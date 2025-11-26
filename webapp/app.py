import os
import sys
from flask import Flask, render_template, request

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from A3 import get_pokemon_list_for_web

app = Flask(__name__)


@app.route("/")
def index():
    return pokemon_list()


@app.route("/pokemon")
def pokemon_list():
    """
    Show table of all Pokémon.
    Supports:
      - q  : search query (name)
      - type : type filter (e.g., Fire, Grass); empty = all
    """
    all_pokemon = get_pokemon_list_for_web()

    # get unique types for the filter dropdown
    types = sorted({p["type"] for p in all_pokemon if p.get("type")})

    # read query params
    q = request.args.get("q", "").strip().lower()
    type_filter = request.args.get("type", "").strip()

    # filter by type
    if type_filter:
        filtered = [p for p in all_pokemon if p.get("type", "").lower() == type_filter.lower()]
    else:
        filtered = all_pokemon

    # filter by search query (name or number)
    if q:
        def matches(p):
            if q.isdigit():
                return str(p["number"]).lstrip("0") == q.lstrip("0") or str(p["number"]) == q
            return q in p["name"].lower()
        filtered = [p for p in filtered if matches(p)]

    return render_template(
        "pokemon_list.html",
        pokemon_list=filtered,
        types=types,
        selected_type=type_filter,
        search_q=request.args.get("q", "")
    )


@app.route("/pokemon/<number>")
def pokemon_detail(number):
    """
    Show detailed information for a single Pokémon by national number.
    """
    all_pokemon = get_pokemon_list_for_web()
    
    # Find the Pokémon by number
    pokemon = None
    for p in all_pokemon:
        if p["number"] == number:
            pokemon = p
            break
    
    if pokemon is None:
        return f"Pokémon with number {number} not found", 404
    
    # Enrich the pokemon dict with full stats and other details
    from A3 import Pokedex
    dex = Pokedex.get_instance()
    
    # Find the actual object to get all details
    pokemon_obj = None
    for entry in dex.get_entries():
        if entry.get_national_no() == number:
            pokemon_obj = entry
            break
    
    if pokemon_obj is None:
        return f"Pokémon with number {number} not found", 404
    
    # Build enriched dict with all stats and metadata
    stats = pokemon_obj.get_stats()
    pokemon_detail = {
        "number": pokemon_obj.get_national_no(),
        "name": pokemon_obj.get_name(),
        "type": getattr(pokemon_obj.__class__, "TYPE_NAME", "Unknown"),
        "species": pokemon_obj.get_species(),
        "height_m": pokemon_obj.get_height(),
        "weight_kg": pokemon_obj.get_weight(),
        "abilities": pokemon_obj.get_abilities(),
        "stats": {
            "hp": stats.get_stat("hp"),
            "attack": stats.get_stat("attack"),
            "defense": stats.get_stat("defense"),
            "sp_atk": stats.get_stat("sp_atk"),
            "sp_def": stats.get_stat("sp_def"),
            "speed": stats.get_stat("speed"),
            "total": stats.get_total()
        }
    }
    
    return render_template("pokemon_detail.html", pokemon=pokemon_detail)


if __name__ == "__main__":
    app.run(debug=True)
