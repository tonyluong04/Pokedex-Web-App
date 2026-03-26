"""
Battle API routes for Pokédex v2.0 — Phase 3

Provides endpoint to hydrate both teams with full PokéAPI stats
for client-side battle.
"""

from __future__ import annotations

import random

import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required

from webapp.utils.pokeapi import pokemon_battle_data

battle_bp = Blueprint("battle", __name__)


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
        team_ids_int = [int(i) for i in team_ids]
        if any(i <= 0 for i in team_ids_int):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "All team entries must be positive integers"}), 400

    try:
        # Fetch player team
        player_team = [pokemon_battle_data(pid) for pid in team_ids_int]

        # Generate random opponent
        opp_ids = random.sample(range(1, 899), 5)
        opponent_team = []
        for pid in opp_ids:
            try:
                data = pokemon_battle_data(pid)
                opponent_team.append(data)
            except requests.HTTPError:
                fallback = random.randint(1, 898)
                data = pokemon_battle_data(fallback)
                opponent_team.append(data)

        return jsonify({
            "playerTeam": player_team,
            "opponentTeam": opponent_team,
        })
    except requests.HTTPError as e:
        return jsonify({"error": "Failed to fetch Pokémon data", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500