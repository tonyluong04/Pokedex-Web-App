"""
Battle API routes for Pokédex v2.0 — Phase 3

Provides endpoints to generate a random opponent team and
hydrate both teams with full PokéAPI stats for client-side battle.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

battle_bp = Blueprint("battle", __name__)

# PokéAPI helper (duplicated intentionally to keep blueprint self-contained)

_POKEAPI_BASE = "https://pokeapi.co/api/v2"


def _fetch_pokemon_battle_data(pokemon_id: int) -> Dict[str, Any]:
    """Fetch the fields needed for battle from PokéAPI."""
    url = f"{_POKEAPI_BASE}/pokemon/{pokemon_id}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    p = resp.json()

    # Extract stats by name
    stat_map: Dict[str, int] = {}
    for s in p.get("stats", []):
        name = (s.get("stat") or {}).get("name", "")
        stat_map[name] = s.get("base_stat", 0)

    # Extract types
    types: List[str] = []
    for t in p.get("types", []):
        type_name = (t.get("type") or {}).get("name")
        if type_name:
            types.append(type_name)

    # Sprite
    sprites = p.get("sprites") or {}
    other = sprites.get("other") or {}
    sprite = (other.get("official-artwork") or {}).get("front_default") or sprites.get("front_default")

    return {
        "pokemon_id": p.get("id"),
        "name": p.get("name"),
        "sprite": sprite,
        "types": types,
        "hp": stat_map.get("hp", 1),
        "attack": stat_map.get("attack", 1),
        "defense": stat_map.get("defense", 1),
        "speed": stat_map.get("speed", 1),
    }


@battle_bp.get("/battle/opponent")
def generate_opponent():
    """Generate 5 random Pokémon as the opponent team."""
    try:
        ids = random.sample(range(1, 899), 5)
        team = []
        for pid in ids:
            try:
                data = _fetch_pokemon_battle_data(pid)
                team.append(data)
            except requests.HTTPError:
                # If a random ID fails, pick another
                fallback = random.randint(1, 898)
                try:
                    data = _fetch_pokemon_battle_data(fallback)
                    team.append(data)
                except Exception:
                    continue
        return jsonify({"opponentTeam": team})
    except Exception as e:
        return jsonify({"error": "Failed to generate opponent", "detail": str(e)}), 500


@battle_bp.post("/battle/start")
@login_required
def start_battle():
    """
    Accept the player's team of 5 pokemon_ids, fetch full stats for both
    teams, return hydrated data for client-side battle.
    """
    body = request.get_json(silent=True) or {}
    team_ids = body.get("team")

    if not team_ids or not isinstance(team_ids, list) or len(team_ids) != 5:
        return jsonify({"error": "team must be a list of exactly 5 pokemon_ids"}), 400

    try:
        # Validate all are positive ints
        team_ids_int = [int(i) for i in team_ids]
        if any(i <= 0 for i in team_ids_int):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "All team entries must be positive integers"}), 400

    try:
        # Fetch player team
        player_team = []
        for pid in team_ids_int:
            data = _fetch_pokemon_battle_data(pid)
            player_team.append(data)

        # Generate random opponent
        opp_ids = random.sample(range(1, 899), 5)
        opponent_team = []
        for pid in opp_ids:
            try:
                data = _fetch_pokemon_battle_data(pid)
                opponent_team.append(data)
            except requests.HTTPError:
                fallback = random.randint(1, 898)
                data = _fetch_pokemon_battle_data(fallback)
                opponent_team.append(data)

        return jsonify({
            "playerTeam": player_team,
            "opponentTeam": opponent_team,
        })
    except requests.HTTPError as e:
        return jsonify({"error": "Failed to fetch Pokémon data", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500