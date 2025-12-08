import os
import sys
from io import BytesIO
import base64
from flask import Flask, render_template, request, jsonify

# Adjust path to import A3.py from parent directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from A3 import (
    Pokedex, Stats, GenericFirePokemon, GenericGrassPokemon,
    Validator, Visualizer, PokemonNotFoundError
)

app = Flask(__name__)

# ===== HELPER FUNCTIONS =====

def _ensure_dex_loaded():
    """Ensure Pokedex is loaded from pokemon.json."""
    dex = Pokedex.get_instance()
    if not dex.get_entries():
        json_path = os.path.join(PARENT_DIR, "pokemon.json")
        try:
            dex.load_json(json_path)
        except FileNotFoundError:
            pass  # Empty Pokédex is okay for now
    return dex

def _pokemon_to_dict(pokemon_obj):
    """Convert a Pokémon object to a full detail dict."""
    s = pokemon_obj.get_stats()
    return {
        "number": pokemon_obj.get_national_no(),
        "name": pokemon_obj.get_name(),
        "type": getattr(pokemon_obj.__class__, "TYPE_NAME", "Unknown"),
        "species": pokemon_obj.get_species(),
        "height_m": pokemon_obj.get_height(),
        "weight_kg": pokemon_obj.get_weight(),
        "abilities": pokemon_obj.get_abilities(),
        "stats": {
            "hp": s.get_stat("hp"),
            "attack": s.get_stat("attack"),
            "defense": s.get_stat("defense"),
            "sp_atk": s.get_stat("sp_atk"),
            "sp_def": s.get_stat("sp_def"),
            "speed": s.get_stat("speed"),
            "total": s.get_total()
        }
    }

def get_pokemon_list_for_web():
    """Build the Pokédex and return a simple list of dictionaries for the web app.
    
    This function initializes the Pokedex singleton, loads from pokemon.json,
    and returns a list of Pokémon with basic information for displaying on the web.
    
    Returns:
        List of dictionaries, each containing:
        - number: National Pokédex number (string, e.g., "0004")
        - name: Pokémon name
        - type: Type name (Fire or Grass)
        - hp: HP stat
        - attack: Attack stat
        - defense: Defense stat
        
    Example:
        >>> pokemon_list = get_pokemon_list_for_web()
        >>> print(pokemon_list[0])
        {'number': '0004', 'name': 'Charmander', 'type': 'Fire', 'hp': 100, ...}
    """
    dex = _ensure_dex_loaded()
    pokemon_list = []
    
    for p in dex.get_entries():
        s = p.get_stats()
        pokemon_dict = {
            "number": p.get_national_no(),
            "name": p.get_name(),
            "type": getattr(p.__class__, "TYPE_NAME", "Unknown"),
            "hp": s.get_stat("hp"),
            "attack": s.get_stat("attack"),
            "defense": s.get_stat("defense"),
        }
        pokemon_list.append(pokemon_dict)
    
    return pokemon_list

# ===== SPA SHELL =====

@app.route("/")
def index():
    """Serve the SPA shell."""
    return render_template("index.html")

# ===== REST API ENDPOINTS =====

@app.route("/api/pokemon", methods=["GET"])
def api_list_pokemon():
    """
    GET /api/pokemon?type=Fire&q=charma
    Returns array of pokemon summary.
    """
    dex = _ensure_dex_loaded()
    
    q = request.args.get("q", "").strip().lower()
    type_filter = request.args.get("type", "").strip()
    
    pokemon_list = []
    for p in dex.get_entries():
        pokemon_dict = {
            "number": p.get_national_no(),
            "name": p.get_name(),
            "type": getattr(p.__class__, "TYPE_NAME", "Unknown"),
            "hp": p.get_stats().get_stat("hp"),
            "attack": p.get_stats().get_stat("attack"),
            "defense": p.get_stats().get_stat("defense"),
        }
        
        # Apply filters
        if type_filter and pokemon_dict["type"].lower() != type_filter.lower():
            continue
        
        if q:
            name_match = q in pokemon_dict["name"].lower()
            number_match = str(pokemon_dict["number"]).lstrip("0") == q.lstrip("0")
            if not (name_match or number_match):
                continue
        
        pokemon_list.append(pokemon_dict)
    
    return jsonify(pokemon_list)

@app.route("/api/pokemon/<number>", methods=["GET"])
def api_get_pokemon(number):
    """
    GET /api/pokemon/0004
    Returns full Pokémon detail.
    """
    dex = _ensure_dex_loaded()
    try:
        p = dex.find_by_national_no(number)
        return jsonify(_pokemon_to_dict(p))
    except PokemonNotFoundError:
        return jsonify({"error": f"Pokémon #{number} not found"}), 404

@app.route("/api/types", methods=["GET"])
def api_get_types():
    """
    GET /api/types
    Returns list of available types.
    """
    dex = _ensure_dex_loaded()
    types = sorted({getattr(p.__class__, "TYPE_NAME", "Unknown") for p in dex.get_entries()})
    return jsonify(types)

@app.route("/api/pokemon", methods=["POST"])
def api_create_pokemon():
    """
    POST /api/pokemon
    Create new Pokémon. Auto-saves to JSON.
    """
    dex = _ensure_dex_loaded()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        ptype = (data.get("type") or "").strip().lower()
        if ptype not in ("fire", "grass"):
            return jsonify({"error": "Type must be 'Fire' or 'Grass'"}), 400
        
        # Validate inputs
        name = (data.get("name") or "").strip()
        if not Validator.valid_name(name):
            return jsonify({"error": "Name must contain only letters and spaces"}), 400
        
        species = (data.get("species") or "").strip()
        if not Validator.valid_name(species):
            return jsonify({"error": "Species must contain only letters and spaces"}), 400
        
        try:
            height_m = float(data.get("height_m", 0.0))
            weight_kg = float(data.get("weight_kg", 0.0))
            if height_m < 0 or weight_kg < 0:
                return jsonify({"error": "Height and weight must be non-negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Height and weight must be numbers"}), 400
        
        # Create stats
        stats_data = data.get("stats", {})
        try:
            stats = Stats(
                stats_data.get("hp", 0),
                stats_data.get("attack", 0),
                stats_data.get("defense", 0),
                stats_data.get("sp_atk", 0),
                stats_data.get("sp_def", 0),
                stats_data.get("speed", 0)
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Create Pokémon
        klass = GenericFirePokemon if ptype == "fire" else GenericGrassPokemon
        national_no = str(data.get("national_no", "0000")).zfill(4)
        abilities = data.get("abilities", [])
        
        p = klass(
            national_no=national_no,
            name=name,
            species=species,
            height_m=height_m,
            weight_kg=weight_kg,
            abilities=abilities,
            stats=stats
        )
        
        dex.add(p)  # Auto-saves to JSON
        return jsonify(_pokemon_to_dict(p)), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pokemon/<number>", methods=["PUT"])
def api_update_pokemon(number):
    """
    PUT /api/pokemon/0004
    Replace entire Pokémon entry. Auto-saves to JSON.
    """
    dex = _ensure_dex_loaded()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        p = dex.find_by_national_no(number)
        
        # Update stats if provided
        if "stats" in data:
            stats_data = data["stats"]
            s = p.get_stats()
            for field in ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]:
                if field in stats_data:
                    try:
                        s.set_stat(field, stats_data[field])
                    except ValueError as e:
                        return jsonify({"error": f"Invalid {field}: {e}"}), 400
        
        dex.save_json()  # Persist changes
        return jsonify(_pokemon_to_dict(p))
    
    except PokemonNotFoundError:
        return jsonify({"error": f"Pokémon #{number} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pokemon/<number>/stats", methods=["PATCH"])
def api_patch_pokemon_stats(number):
    """
    PATCH /api/pokemon/0004/stats
    Update only specific stats.
    """
    dex = _ensure_dex_loaded()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        p = dex.find_by_national_no(number)
        s = p.get_stats()
        
        for field, value in data.items():
            if field in ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]:
                try:
                    s.set_stat(field, value)
                except ValueError as e:
                    return jsonify({"error": f"Invalid {field}: {e}"}), 400
        
        dex.save_json()
        return jsonify(_pokemon_to_dict(p))
    
    except PokemonNotFoundError:
        return jsonify({"error": f"Pokémon #{number} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pokemon/<number>", methods=["DELETE"])
def api_delete_pokemon(number):
    """
    DELETE /api/pokemon/0004
    Delete Pokémon. Auto-saves to JSON.
    """
    dex = _ensure_dex_loaded()
    try:
        success = dex.remove_by_national_no(number)  # Auto-saves
        if success:
            return jsonify({"message": f"Pokémon #{number} deleted"})
        else:
            return jsonify({"error": f"Pokémon #{number} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/stats/chart", methods=["GET"])
def api_stats_chart():
    """
    GET /api/stats/chart?type=single&number=0004
    or
    GET /api/stats/chart?type=averages
    Returns PNG image as base64 data URL.
    """
    dex = _ensure_dex_loaded()
    chart_type = request.args.get("type", "single").lower()
    
    try:
        if chart_type == "single":
            number = request.args.get("number")
            if not number:
                return jsonify({"error": "number parameter required"}), 400
            p = dex.find_by_national_no(number)
            
            # Generate chart to BytesIO
            img_bytes = BytesIO()
            Visualizer.bar_stats_single(p, save_path=None)
            # Capture the figure directly
            import matplotlib.pyplot as plt
            plt.savefig(img_bytes, format="png", dpi=150, bbox_inches="tight")
            plt.close()
            img_bytes.seek(0)
            
            # Encode to base64 data URL
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
            return jsonify({"image": f"data:image/png;base64,{img_base64}"})
        
        elif chart_type == "averages":
            img_bytes = BytesIO()
            Visualizer.line_type_averages(dex.get_entries(), save_path=None)
            import matplotlib.pyplot as plt
            plt.savefig(img_bytes, format="png", dpi=150, bbox_inches="tight")
            plt.close()
            img_bytes.seek(0)
            
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
            return jsonify({"image": f"data:image/png;base64,{img_base64}"})
        
        else:
            return jsonify({"error": "type must be 'single' or 'averages'"}), 400
    
    except PokemonNotFoundError:
        return jsonify({"error": "Pokémon not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
