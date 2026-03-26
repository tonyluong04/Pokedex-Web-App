"""
Shared PokéAPI helper functions.
Used by both pokemon and battle route blueprints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from flask import current_app


_POKEAPI_BASE = "https://pokeapi.co/api/v2"


def _get_base_url() -> str:
    """Get PokéAPI base URL from app config or default."""
    try:
        return current_app.config.get("POKEAPI_BASE_URL", _POKEAPI_BASE).rstrip("/")
    except RuntimeError:
        return _POKEAPI_BASE


def pokeapi_get_json(path: str, *, params: Optional[dict] = None) -> Dict[str, Any]:
    """Fetch JSON from PokéAPI."""
    url = f"{_get_base_url()}{path}"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def extract_sprite(payload: Dict[str, Any]) -> Optional[str]:
    """Extract the best available sprite URL from a PokéAPI pokemon payload."""
    sprites = payload.get("sprites") or {}
    other = sprites.get("other") or {}
    official = (other.get("official-artwork") or {}).get("front_default")
    return official or sprites.get("front_default")


def extract_types(payload: Dict[str, Any]) -> List[str]:
    """Extract type names from a PokéAPI pokemon payload."""
    types = []
    for t in payload.get("types", []):
        type_name = (t.get("type") or {}).get("name")
        if type_name:
            types.append(type_name)
    return types


def extract_stats(payload: Dict[str, Any]) -> Dict[str, int]:
    """Extract base stats as a name→value dict from a PokéAPI pokemon payload."""
    stat_map = {}
    for s in payload.get("stats", []):
        name = (s.get("stat") or {}).get("name", "")
        stat_map[name] = s.get("base_stat", 0)
    return stat_map


def pokemon_detail(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Full detail dict used by the Pokédex views."""
    stats = []
    for s in payload.get("stats", []):
        stat_name = (s.get("stat") or {}).get("name")
        base_stat = s.get("base_stat")
        if stat_name is not None and base_stat is not None:
            stats.append({"name": stat_name, "base": base_stat})

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "number": payload.get("id"),
        "sprite": extract_sprite(payload),
        "types": extract_types(payload),
        "stats": stats,
        "height": payload.get("height"),
        "weight": payload.get("weight"),
        "base_experience": payload.get("base_experience"),
    }


def pokemon_battle_data(pokemon_id: int) -> Dict[str, Any]:
    """Fetch and return battle-relevant fields for a single Pokémon."""
    payload = pokeapi_get_json(f"/pokemon/{pokemon_id}")
    stat_map = extract_stats(payload)

    return {
        "pokemon_id": payload.get("id"),
        "name": payload.get("name"),
        "sprite": extract_sprite(payload),
        "types": extract_types(payload),
        "hp": stat_map.get("hp", 1),
        "attack": stat_map.get("attack", 1),
        "defense": stat_map.get("defense", 1),
        "speed": stat_map.get("speed", 1),
    }