"""
Pokémon API routes for Pokédex v2.0

Phase 1: PokéAPI browsing + personal collection (My Pokéball)
"""

from __future__ import annotations

from typing import Any, Dict, List

import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from webapp.extensions import db
from webapp.models.pokemon import UserPokemon
from webapp.utils.pokeapi import pokeapi_get_json, pokemon_detail


pokemon_bp = Blueprint("pokemon", __name__)


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
        listing = pokeapi_get_json("/pokemon", params={"limit": limit, "offset": 0})
        results = listing.get("results", [])

        summaries: List[Dict[str, Any]] = []
        for item in results:
            name = item.get("name")
            if not name:
                continue
            detail_payload = pokeapi_get_json(f"/pokemon/{name}")
            d = pokemon_detail(detail_payload)
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
        payload = pokeapi_get_json(f"/pokemon/{query}")
        d = pokemon_detail(payload)
        return jsonify({"results": [{"id": d["id"], "name": d["name"], "number": d["number"], "sprite": d["sprite"]}]})
    except requests.HTTPError:
        return jsonify({"results": []})
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


@pokemon_bp.get("/pokemon/<id_or_name>")
def pokemon_detail_route(id_or_name: str):
    """Get Pokémon detail by id or name."""
    q = (id_or_name or "").strip().lower()
    if not q:
        return jsonify({"error": "Missing id_or_name"}), 400

    try:
        payload = pokeapi_get_json(f"/pokemon/{q}")
        return jsonify(pokemon_detail(payload))
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
        payload = pokeapi_get_json(f"/pokemon/{pokemon_id_int}")
        d = pokemon_detail(payload)
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
