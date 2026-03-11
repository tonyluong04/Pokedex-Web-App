"""
Pokémon API routes for Pokédex v2.0

Phase 1: PokéAPI browsing + personal collection (My Pokéball)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required, current_user

from webapp.extensions import db
from webapp.models.pokemon import UserPokemon


pokemon_bp = Blueprint("pokemon", __name__)


def _pokeapi_get_json(path: str, *, params: Optional[dict] = None) -> Dict[str, Any]:
    base = current_app.config.get("POKEAPI_BASE_URL", "https://pokeapi.co/api/v2").rstrip("/")
    url = f"{base}{path}"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _sprite_from_pokemon(payload: Dict[str, Any]) -> Optional[str]:
    sprites = payload.get("sprites") or {}
    other = sprites.get("other") or {}
    official = (other.get("official-artwork") or {}).get("front_default")
    return official or sprites.get("front_default")


def _pokemon_detail_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    stats = []
    for s in payload.get("stats", []):
        stat_name = (s.get("stat") or {}).get("name")
        base_stat = s.get("base_stat")
        if stat_name is not None and base_stat is not None:
            stats.append({"name": stat_name, "base": base_stat})

    types = []
    for t in payload.get("types", []):
        type_name = (t.get("type") or {}).get("name")
        if type_name:
            types.append(type_name)

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "number": payload.get("id"),
        "sprite": _sprite_from_pokemon(payload),
        "types": types,
        "stats": stats,
        "height": payload.get("height"),
        "weight": payload.get("weight"),
        "base_experience": payload.get("base_experience"),
    }


@pokemon_bp.get("/pokemon/default")
def pokemon_default():
    """
    Return a small default set of Pokémon (ordered by National Dex id).
    Used when no search query is entered.
    """
    try:
        limit = int(request.args.get("limit", 12))
        limit = max(1, min(limit, 24))
    except ValueError:
        limit = 12

    try:
        listing = _pokeapi_get_json("/pokemon", params={"limit": limit, "offset": 0})
        results = listing.get("results", [])

        summaries: List[Dict[str, Any]] = []
        for item in results:
            name = item.get("name")
            if not name:
                continue
            detail = _pokeapi_get_json(f"/pokemon/{name}")
            d = _pokemon_detail_from_payload(detail)
            summaries.append({"id": d["id"], "name": d["name"], "number": d["number"], "sprite": d["sprite"]})

        summaries.sort(key=lambda x: (x.get("number") or 0))
        return jsonify({"results": summaries})
    except requests.HTTPError as e:
        return jsonify({"error": "PokéAPI request failed", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


@pokemon_bp.get("/pokemon/search")
def pokemon_search():
    """
    Search Pokémon by name or ID.
    If query is empty, clients should use /pokemon/default.
    """
    query = (request.args.get("query") or "").strip().lower()
    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        payload = _pokeapi_get_json(f"/pokemon/{query}")
        d = _pokemon_detail_from_payload(payload)
        return jsonify({"results": [{"id": d["id"], "name": d["name"], "number": d["number"], "sprite": d["sprite"]}]})
    except requests.HTTPError:
        return jsonify({"results": []})
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


@pokemon_bp.get("/pokemon/<id_or_name>")
def pokemon_detail(id_or_name: str):
    """Get Pokémon detail by id or name."""
    q = (id_or_name or "").strip().lower()
    if not q:
        return jsonify({"error": "Missing id_or_name"}), 400

    try:
        payload = _pokeapi_get_json(f"/pokemon/{q}")
        return jsonify(_pokemon_detail_from_payload(payload))
    except requests.HTTPError as e:
        return jsonify({"error": "Pokémon not found", "detail": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


# ===== Personal collection: "My Pokéball" (max 5) =====


@pokemon_bp.get("/me/pokeball")
@login_required
def my_pokeball_list():
    items = (
        UserPokemon.query.filter_by(user_id=current_user.id)
        .order_by(UserPokemon.added_at.asc())
        .all()
    )
    return jsonify({"results": [i.to_dict() for i in items]})


@pokemon_bp.post("/me/pokeball")
@login_required
def my_pokeball_add():
    data = request.get_json(silent=True) or {}
    pokemon_id = data.get("pokemon_id")
    if pokemon_id is None:
        return jsonify({"error": "pokemon_id is required"}), 400

    try:
        pokemon_id_int = int(pokemon_id)
        if pokemon_id_int <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "pokemon_id must be a positive integer"}), 400

    # Enforce max 5 Pokémon in Pokéball
    count = UserPokemon.query.filter_by(user_id=current_user.id).count()
    if count >= 5:
        return jsonify({"error": "Pokéball is full (max 5)"}), 409

    try:
        payload = _pokeapi_get_json(f"/pokemon/{pokemon_id_int}")
        d = _pokemon_detail_from_payload(payload)
        if not d.get("id") or not d.get("name"):
            return jsonify({"error": "Invalid Pokémon data from PokéAPI"}), 502

        created = UserPokemon.add_to_pokedex(
            current_user.id,
            int(d["id"]),
            str(d["name"]),
            int(d["number"] or d["id"]),
        )
        if created is None:
            return jsonify({"error": "Already in Pokéball"}), 409

        return jsonify(created.to_dict()), 201
    except requests.HTTPError as e:
        return jsonify({"error": "Pokémon not found", "detail": str(e)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


@pokemon_bp.delete("/me/pokeball/<int:pokemon_id>")
@login_required
def my_pokeball_delete(pokemon_id: int):
    item = UserPokemon.query.filter_by(user_id=current_user.id, pokemon_id=pokemon_id).first()
    if not item:
        return jsonify({"error": "Not in Pokéball"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"deleted": True, "pokemon_id": pokemon_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500
