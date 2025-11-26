# A3.py
# CSIT121 Assignment 3
# ===== CORE LOGIC (KEEP) =====
from abc import ABC, abstractmethod
import os
import json
import re
import matplotlib.pyplot as plt
import numpy as np

# -----------------------
# Stats
# -----------------------

class Stats:
    """Encapsulates the six main stats of a Pokémon."""
    def __init__(self, hp, attack, defense, sp_atk, sp_def, speed):
        """Initialize all six stats."""
        self.__hp = int(hp)
        self.__attack = int(attack)
        self.__defense = int(defense)
        self.__sp_atk = int(sp_atk)
        self.__sp_def = int(sp_def)
        self.__speed = int(speed)
        for v in (self.__hp, self.__attack, self.__defense,
                  self.__sp_atk, self.__sp_def, self.__speed):
            if v < 0:
                raise ValueError("All stats must be non-negative integers.")

    def set_stat(self, field, value):
        """Set the value of the specified stat."""
        v = int(value)
        if v < 0:
            raise ValueError("value must be non-negative.")
        if field == "hp": self.__hp = v
        elif field == "attack": self.__attack = v
        elif field == "defense": self.__defense = v
        elif field == "sp_atk": self.__sp_atk = v
        elif field == "sp_def": self.__sp_def = v
        elif field == "speed": self.__speed = v
        else:
            raise AttributeError(f"Unknown stat '{field}'.")

    def get_stat(self, field):
        """Return the value of the specified stat."""
        if field == "hp": return self.__hp
        if field == "attack": return self.__attack
        if field == "defense": return self.__defense
        if field == "sp_atk": return self.__sp_atk
        if field == "sp_def": return self.__sp_def
        if field == "speed": return self.__speed
        raise AttributeError(f"Unknown stat '{field}'.")

    def get_total(self):
        """Return total of all six stats."""
        return (self.__hp + self.__attack + self.__defense +
                self.__sp_atk + self.__sp_def + self.__speed)

    def as_dict(self):
        """Return stats as a dictionary."""
        return {
            "hp": self.__hp,
            "attack": self.__attack,
            "defense": self.__defense,
            "sp_atk": self.__sp_atk,
            "sp_def": self.__sp_def,
            "speed": self.__speed,
            "total": self.get_total()
        }
    
    @staticmethod
    def from_dict(d):
        """Create a Stats object from a dictionary, with default value = 0."""
        return Stats(
            d.get("hp", 0),
            d.get("attack", 0),
            d.get("defense", 0),
            d.get("sp_atk", 0),
            d.get("sp_def", 0),
            d.get("speed", 0)
        )



# -----------------------
# «Abstract» BasePokemon
# -----------------------

class BasePokemon(ABC):
    """Abstract base class defining shared attributes and methods for all Pokémon."""

    def __init__(self,
                 national_no="0", name="Unknown", species="???",
                 height_m=0.0, weight_kg=0.0,
                 abilities=None, stats=None):
        """Initialize basic Pokémon information and stats."""
        self.__national_no = str(national_no)
        self.__name = name
        self.__species = species
        self.__height_m = float(height_m)
        self.__weight_kg = float(weight_kg)
        self.__abilities = abilities if abilities is not None else []
        self.__stats = stats if stats is not None else Stats(0, 0, 0, 0, 0, 0)

    # Getters
    def get_national_no(self): return self.__national_no
    def get_name(self): return self.__name
    def get_species(self): return self.__species
    def get_height(self): return self.__height_m
    def get_weight(self): return self.__weight_kg
    def get_abilities(self): return self.__abilities
    def get_stats(self): return self.__stats

    # Basic info setter
    def set_basic_info(self, name, national_no, species, height_m, weight_kg, abilities):
        """Set the basic Pokémon information fields."""
        self.__name = name
        self.__national_no = str(national_no)
        self.__species = species
        self.__height_m = float(height_m)
        self.__weight_kg = float(weight_kg)
        self.__abilities = list(abilities)

    @abstractmethod
    def display(self):
        """Display Pokémon information (to be implemented by subclasses)."""
        pass

    def to_row(self):
        """Convert the Pokémon object into a flat text dictionary for text export."""
        s = self.__stats
        return {
            "national_no": self.__national_no,
            "name": self.__name,
            "type": self.TYPE_NAME,
            "species": self.__species,
            "height_m": str(self.__height_m),
            "weight_kg": str(self.__weight_kg),
            "abilities": ";".join(self.__abilities),
            "hp": str(s.get_stat("hp")),
            "attack": str(s.get_stat("attack")),
            "defense": str(s.get_stat("defense")),
            "sp_atk": str(s.get_stat("sp_atk")),
            "sp_def": str(s.get_stat("sp_def")),
            "speed": str(s.get_stat("speed")),
            "total": str(s.get_total())
        }

    def to_dict(self):
        """Convert the Pokémon object into a nested dictionary for JSON serialization."""
        return {
            "class": self.__class__.__name__,     
            "type": getattr(self.__class__, "TYPE_NAME", ""),
            "national_no": self.__national_no,
            "name": self.__name,
            "species": self.__species,
            "height_m": self.__height_m,
            "weight_kg": self.__weight_kg,
            "abilities": list(self.__abilities),      
            "stats": self.__stats.as_dict()           
        }

    @staticmethod
    def from_dict(d):
        """Recreate a Pokémon object from a dictionary."""
        class_name = d.get("class", "")
        type_name = d.get("type", "").lower()

        class_map = {
            "Charmander": Charmander,
            "Vulpix": Vulpix,
            "Bulbasaur": Bulbasaur,
            "Oddish": Oddish,
            "GenericFirePokemon": GenericFirePokemon,
            "GenericGrassPokemon": GenericGrassPokemon
        }

        klass = class_map.get(class_name)
        # If it's a new Pokémon not in the list, choose by type
        if klass is None:
            if type_name == "fire":
                klass = GenericFirePokemon
            elif type_name == "grass":
                klass = GenericGrassPokemon
            else:
                raise ValueError(f"Unknown Pokémon type: {type_name}")

        return klass(
            national_no=d.get("national_no", "0000"),
            name=d.get("name", "Unknown"),
            species=d.get("species", "???"),
            height_m=float(d.get("height_m", 0.0)),
            weight_kg=float(d.get("weight_kg", 0.0)),
            abilities=d.get("abilities", []),
            stats=Stats.from_dict(d.get("stats", {}))
        )



# -----------------------
# Type classes (abstract)
# -----------------------

class GrassType(BasePokemon, ABC):
    """Abstract base class for all Grass-type Pokémon. 
    Provides shared information and average-stat calculation."""
    
    TYPE_NAME = "Grass"
    TYPE_INFO = (
        "Grass is one of the three basic elemental types along with Fire and Water, "
        "which constitute the three starter Pokémon. Grass is weak defensively, "
        "with 5 weaknesses and many resistances.\n"
        "In Generations 1-3, all Grass type moves were categorized as Special."
    )

    def display(self):
        """Return Grass-type description (used in type report)."""
        return "[Type: Grass]\n" + GrassType.TYPE_INFO
    

    @classmethod
    def calculate_average(cls, pokemons):
        """Calculate average stats for all Grass-type Pokémon in the Pokédex."""
        grass_pokemon = [
            p for p in pokemons
            if getattr(p.__class__, "TYPE_NAME", "").lower() == "grass"
        ]
        if not grass_pokemon:
            return None

        totals = {k: 0 for k in ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]}
        for p in grass_pokemon:
            s = p.get_stats()
            for k in totals:
                totals[k] += s.get_stat(k)

        count = len(grass_pokemon)
        return {k: round(v / count, 1) for k, v in totals.items()}


class FireType(BasePokemon, ABC):
    """Abstract base class for all Fire-type Pokémon.
    Provides shared information and average-stat calculation."""
    
    TYPE_NAME = "Fire"
    TYPE_INFO = (
        "Fire is one of the three basic elemental types along with Water and Grass. "
        "Fire types are rare in early games, but often powerful.\n"
        "In Generations 1-3, all Fire type moves were categorized as Special."
    )

    def display(self):
        """Return Fire-type description (used in type report)."""
        return "[Type: Fire]\n" + FireType.TYPE_INFO

    @classmethod
    def calculate_average(cls, pokemons):
        """Calculate average stats for all Fire-type Pokémon in the Pokédex."""
        fire_pokemon = [
            p for p in pokemons
            if getattr(p.__class__, "TYPE_NAME", "").lower() == "fire"
        ]
        if not fire_pokemon:
            return None

        totals = {k: 0 for k in ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]}
        for p in fire_pokemon:
            s = p.get_stats()
            for k in totals:
                totals[k] += s.get_stat(k)

        count = len(fire_pokemon)
        return {k: round(v / count, 1) for k, v in totals.items()}



# -----------------------
# Concrete Pokemon
# -----------------------

class Oddish(GrassType):
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"

class Bulbasaur(GrassType):
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"

class Charmander(FireType):
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"

class Vulpix(FireType):
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"

class GenericFirePokemon(FireType):
    """Generic Fire-type Pokémon created by the user."""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"

class GenericGrassPokemon(GrassType):
    """Generic Grass-type Pokémon created by the user."""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\n" \
               f"Name: {self.get_name()}\n" \
               f"Type: {self.TYPE_NAME}\n" \
               f"Species: {self.get_species()}\n" \
               f"Height: {self.get_height()} m\n" \
               f"Weight: {self.get_weight()} kg\n" \
               f"Abilities: {';'.join(self.get_abilities())}\n" \
               f"Stats:\n" \
               f"  HP: {s.get_stat('hp')}\n" \
               f"  Attack: {s.get_stat('attack')}\n" \
               f"  Defense: {s.get_stat('defense')}\n" \
               f"  Special Attack: {s.get_stat('sp_atk')}\n" \
               f"  Special Defense: {s.get_stat('sp_def')}\n" \
               f"  Speed: {s.get_stat('speed')}\n" \
               f"  Total: {s.get_total()}"



# -----------------------
# Exceptions
# -----------------------

class PokemonNotFoundError(Exception):
    """Raised when a Pokémon cannot be found in the Pokédex."""
    pass



# -----------------------
# Pokedex
# -----------------------

class Pokedex:
    """Singleton class that manages all Pokémon entries."""

    __instance = None     # class-level variable

    def __init__(self):
        """Private constructor — only one instance allowed."""
        if Pokedex.__instance is not None:
            raise Exception("Pokedex is a Singleton class! Use get_instance().")
        self.entries = []
        self.text_path = ""
        self.json_path = ""
        self.dirty = False
        Pokedex.__instance = self

    @classmethod
    def get_instance(cls):
        """Get or create the single Pokedex instance."""
        if cls.__instance is None:
            cls.__instance = Pokedex()
        return cls.__instance

    # Core operations
    def add(self, p):
        """Add a Pokémon object to the Pokédex."""
        self.entries.append(p)
        self.dirty = True

    def get_entries(self):
        """Return all Pokémon entries."""
        return self.entries

    def count(self):
        """Return the number of Pokémon currently in the Pokédex."""
        return len(self.entries)

    # Search operations
    def find_by_name(self, name):
        for p in self.entries:
            if p.get_name().lower() == name.lower():
                return p
        raise PokemonNotFoundError(f"No Pokémon found with name: {name}")

    def find_by_national_no(self, no):
        no_str = str(no)
        for p in self.entries:
            if p.get_national_no() == no_str:
                return p
        raise PokemonNotFoundError(f"No Pokémon found with national number: {no}")

    def find_by_type(self, type_name):
        wanted = str(type_name).lower()
        results = [p for p in self.entries
                   if getattr(p.__class__, "TYPE_NAME", "").lower() == wanted]
        return results

    # Remove operations
    def remove_by_name(self, name):
        try:
            p = self.find_by_name(name)
            self.entries.remove(p)
            self.dirty = True
            return True
        except PokemonNotFoundError:
            return False

    def remove_by_national_no(self, no):
        try:
            p = self.find_by_national_no(no)
            self.entries.remove(p)
            self.dirty = True
            return True
        except PokemonNotFoundError:
            return False

    # Update operations
    def update_by_name(self, name, field, value):
        try:
            p = self.find_by_name(name)
            p.get_stats().set_stat(field, value)
            self.dirty = True
            return True
        except (PokemonNotFoundError, Exception):
            return False

    def update_by_national_no(self, no, field, value):
        try:
            p = self.find_by_national_no(no)
            p.get_stats().set_stat(field, value)
            self.dirty = True
            return True
        except (PokemonNotFoundError, Exception):
            return False

    # File I/O (Text)
    def load(self, filepath):
        """Load Pokémon data from a plain text file."""
        self.entries = []
        self.text_path = filepath
        if not os.path.exists(filepath):
            self.dirty = False
            raise FileNotFoundError(f"File '{filepath}' not found.")

        with open(filepath, "r", encoding="utf-8") as f:
            block, stats = {}, {}
            for line in f:
                line = line.strip()
                if not line:
                    if block:
                        self._create_pokemon_from_block(block, stats)
                        block, stats = {}, {}
                    continue
                if line.startswith("Stats:"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    key, val = key.strip(), val.strip()
                    if key in ["Total", "HP", "Attack", "Defense",
                               "Special Attack", "Special Defense", "Speed"]:
                        stats[key] = int(val.split()[0])
                    else:
                        block[key] = val
            if block:
                self._create_pokemon_from_block(block, stats)
        self.dirty = False
        return len(self.entries)

    def save(self, filepath=""):
        if filepath:
            self.text_path = filepath
        if not self.text_path:
            raise ValueError("No text file path set for saving.")

        with open(self.text_path, "w", encoding="utf-8") as f:
            for p in self.entries:
                row = p.to_row()
                f.write("Name: {}\n".format(row["name"]))
                f.write("National Number: No. {}\n".format(row["national_no"]))
                f.write("Type: {}\n".format(row["type"]))  
                f.write("Species: {}\n".format(row["species"]))
                f.write("Height: {} m\n".format(row["height_m"]))
                f.write("Weight: {} kg\n".format(row["weight_kg"]))
                f.write("Abilities: {}\n".format(row["abilities"]))
                f.write("Stats:\n")
                f.write("  Total: {}\n".format(row["total"]))
                f.write("  HP: {}\n".format(row["hp"]))
                f.write("  Attack: {}\n".format(row["attack"]))
                f.write("  Defense: {}\n".format(row["defense"]))
                f.write("  Special Attack: {}\n".format(row["sp_atk"]))
                f.write("  Special Defense: {}\n".format(row["sp_def"]))
                f.write("  Speed: {}\n".format(row["speed"]))
                f.write("\n")
        self.dirty = False
        return self.text_path

    # Helper to create Pokémon from text block
    def _create_pokemon_from_block(self, block, stats):
        s = Stats(
            stats.get("HP", 0),
            stats.get("Attack", 0),
            stats.get("Defense", 0),
            stats.get("Special Attack", 0),
            stats.get("Special Defense", 0),
            stats.get("Speed", 0)
        )

        name = block.get("Name", "Unknown")
        national_no = str(block.get("National Number", "0000")).replace("No. ", "").zfill(4)
        species = block.get("Species", "???")
        height = float(str(block.get("Height", "0")).split()[0])
        weight = float(str(block.get("Weight", "0")).split()[0])
        abilities = block.get("Abilities", "").split(";")

        type_name = (block.get("Type", "") or "").strip().lower()

        lname = name.lower()
        if lname == "charmander":
            p = Charmander(national_no=national_no, name=name, species=species,
                        height_m=height, weight_kg=weight,
                        abilities=abilities, stats=s)
        elif lname == "vulpix":
            p = Vulpix(national_no=national_no, name=name, species=species,
                    height_m=height, weight_kg=weight,
                    abilities=abilities, stats=s)
        elif lname == "bulbasaur":
            p = Bulbasaur(national_no=national_no, name=name, species=species,
                        height_m=height, weight_kg=weight,
                        abilities=abilities, stats=s)
        elif lname == "oddish":
            p = Oddish(national_no=national_no, name=name, species=species,
                    height_m=height, weight_kg=weight,
                    abilities=abilities, stats=s)
        else:
            if type_name == "fire":
                klass = GenericFirePokemon
            elif type_name == "grass":
                klass = GenericGrassPokemon
            else:
                raise ValueError(f"Unknown Type for '{name}'. Provide 'Type: Fire' or 'Type: Grass'.")
            p = klass(national_no=national_no, name=name, species=species,
                    height_m=height, weight_kg=weight,
                    abilities=abilities, stats=s)
        self.entries.append(p)

    # File I/O (JSON)
    def load_json(self, filepath="pokemon.json"):
        """Load Pokémon data from a JSON file into the Pokédex."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JSON file '{filepath}' not found.")

        self.json_path = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.entries = [BasePokemon.from_dict(d) for d in data]
        self.dirty = False
        return len(self.entries)
        return True
    
    def save_json(self, filepath="pokemon.json"):
        """Save all Pokémon entries to a JSON file."""
        self.json_path = filepath
        data = [p.to_dict() for p in self.entries]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return self.json_path
        return self.json_path    
    
    # Type report export
    def export_type_report(self, typeName, outDir="."):
        """Export a text report summarizing all Pokémon of a given type."""
        wanted = str(typeName).strip().lower()

        if wanted == "fire":
            avgs = FireType.calculate_average(self.entries)
            type_info = FireType.TYPE_INFO
        elif wanted == "grass":
            avgs = GrassType.calculate_average(self.entries)
            type_info = GrassType.TYPE_INFO
        else:
            return None

        selected = [
            p for p in self.entries
            if getattr(p.__class__, "TYPE_NAME", "").lower() == wanted
        ]
        if not selected:
            return None

        filename = f"{wanted}.txt"
        filename = f"{wanted}.txt"
        path = os.path.join(outDir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"[Type: {typeName.capitalize()}]\n")
            f.write(type_info + "\n\n")
            if avgs:
                f.write("Average Stats ({} Pokémon):\n".format(len(selected)))
                f.write(f"  HP {avgs['hp']}, Atk {avgs['attack']}, "
                        f"Def {avgs['defense']}, SpA {avgs['sp_atk']}, "
                        f"SpD {avgs['sp_def']}, Spe {avgs['speed']}\n\n")
            for p in selected:
                f.write(p.display() + "\n\n")
        return path
    


# -----------------------
# Validator
# -----------------------
class Validator:
    """Validates Pokémon input fields (strict: 'No. 0034', '3.6 kg', '1.7 m')."""

    _re_no = re.compile(r"^No\. \d{4}$")                    # exact: No. + space + 4 digits
    _re_height = re.compile(r"^\d+(?:\.\d{1,2})? m$")       # exact one space before 'm'
    _re_weight = re.compile(r"^\d+(?:\.\d{1,2})? kg$")      # exact one space before 'kg'
    _re_name = re.compile(r"^[A-Za-z ]+$")
    _re_abilities = re.compile(r"^[A-Za-z ,;]+$")

    # check methods
    @staticmethod
    def valid_national_no(value: str):
        """Must exactly match 'No. XXXX' (with one space and 4 digits)."""
        return bool(Validator._re_no.fullmatch(value or ""))

    @staticmethod
    def valid_height(value: str):
        """Must include ' m' unit with one space."""
        return bool(Validator._re_height.fullmatch(value or ""))

    @staticmethod
    def valid_weight(value: str):
        """Must include ' kg' unit with one space."""
        return bool(Validator._re_weight.fullmatch(value or ""))

    @staticmethod
    def valid_name(value: str):
        return bool(Validator._re_name.fullmatch(value or ""))

    @staticmethod
    def valid_abilities(value: str):
        return bool(Validator._re_abilities.fullmatch(value or ""))

    # parse methods
    @staticmethod
    def parse_national_no(value: str):
        """Accepts only 'No. XXXX' and returns 'XXXX' (digits only)."""
        if not Validator.valid_national_no(value):
            raise ValueError("National Number must be in format 'No. XXXX' (e.g., 'No. 0034').")
        return value[4:]  # removes 'No. '

    @staticmethod
    def parse_height_m(value: str):
        if not Validator.valid_height(value):
            raise ValueError("Height must include a space and unit, e.g., '1.70 m'.")
        return float(value.split()[0])

    @staticmethod
    def parse_weight_kg(value: str):
        if not Validator.valid_weight(value):
            raise ValueError("Weight must include a space and unit, e.g., '6.90 kg'.")
        return float(value.split()[0])




# ---------------------------
# Visualizer
# ---------------------------

class Visualizer:
    """Matplotlib charts for pokédex stats."""
    # fixed order across all charts
    STAT_ORDER = ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]
    STAT_LABELS = np.array(["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"])

    # Bar chart: one Pokémon’s attributes
    @staticmethod
    def bar_stats_single(pokemon, save_path=None):
        if pokemon is None:
            raise ValueError("pokemon is required for bar chart visualization.")
        s = pokemon.get_stats()
        values = np.array([s.get_stat(k) for k in Visualizer.STAT_ORDER])

        plt.figure()
        plt.bar(Visualizer.STAT_LABELS, values)
        plt.title(f"{pokemon.get_name()} - Attribute Bar Chart")
        plt.xlabel("Attributes")
        plt.ylabel("Value")
        plt.grid(axis="y", linestyle="--", linewidth=0.5)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150)
            plt.close()
            return save_path
        plt.show()
        return None


    # Line chart: Fire vs Grass averages across the same ordered attributes
    @staticmethod
    def line_type_averages(pokemons, save_path=None):
        fire_avg = FireType.calculate_average(pokemons) or {}
        grass_avg = GrassType.calculate_average(pokemons) or {}
        if not fire_avg and not grass_avg:
            raise ValueError("No data to plot for type averages.")

        x = np.arange(len(Visualizer.STAT_ORDER))
        fire_vals = np.array([fire_avg.get(k, 0) for k in Visualizer.STAT_ORDER])
        grass_vals = np.array([grass_avg.get(k, 0) for k in Visualizer.STAT_ORDER])

        plt.figure()
        plt.plot(x, fire_vals, marker="o", label="Fire")
        plt.plot(x, grass_vals, marker="o", label="Grass")
        plt.xticks(x, Visualizer.STAT_LABELS)
        plt.title("Type Averages - Fire vs Grass (Line Chart)")
        plt.xlabel("Attributes")
        plt.ylabel("Average Value")
        plt.grid(True, linestyle="--", linewidth=0.5)
        plt.legend()
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150)
            plt.close()
            return save_path
        plt.show()
        return None


    # Pie chart: one Pokémon’s distribution
    @staticmethod
    def pie_stats(pokemon, save_path=None):
        if pokemon is None:
            raise ValueError("pokemon is required for pie chart visualization.")
        s = pokemon.get_stats()
        values = np.array([s.get_stat(k) for k in Visualizer.STAT_ORDER])

        plt.figure()
        plt.pie(values, labels=Visualizer.STAT_LABELS, autopct="%1.1f%%", startangle=90)
        plt.title(f"{pokemon.get_name()} - Stat Distribution")
        plt.axis("equal")
        if save_path:
            plt.savefig(save_path, dpi=150)
            plt.close()
            return save_path
        plt.show()
        return None


# ===== CONSOLE UI (WILL REPLACE WITH WEB) =====
# ---------------------------
# Menu helpers functions
# ---------------------------

def prompt_nonempty(msg):
    while True:
        s = input(msg).strip()
        if s.lower() in ("x","exit"): return None
        if s: return s
        print("Please enter a non-empty value (or X to cancel).")

def prompt_float(msg):
    while True:
        s = input(msg).strip()
        if s.lower() in ("x","exit"): return None
        try: return float(s)
        except: print("Invalid number. Try again (or X to cancel).")

def prompt_int(msg):
    while True:
        s = input(msg).strip()
        if s.lower() in ("x","exit"): return None
        try: return int(s)
        except: print("Invalid integer. Try again (or X to cancel).")

def detect_and_load(dex, path):
    """Load based on file extension (.txt or .json) and return record count."""
    normalized = path.strip()
    lower = normalized.lower()
    if lower.endswith(".json"):
        return dex.load_json(normalized)
    if lower.endswith(".txt"):
        return dex.load(normalized)
    raise ValueError("Unsupported file type. Use .txt or .json.")

def save_back(dex):
    """Save back to the same file type that was loaded."""
    try:
        if dex.json_path:
            saved_path = dex.save_json(dex.json_path)
            print(f"Pok\u00e9dex data saved to JSON file '{saved_path}'")
        elif dex.text_path:
            saved_path = dex.save(dex.text_path)
            print(f"Pok\u00e9dex saved to '{saved_path}'")
        else:
            print("No file loaded — please use 'S' to specify save file.")
            return
        print("Saved back to original file.")
        dex.dirty = False
    except Exception as e:
        print("Save failed:", e)

def build_pokedex():
    """
    Create a Pokedex instance and load Pokémon data
    WITHOUT asking the user for input.
    This is used by the web app.
    """
    dex = Pokedex.get_instance()

    # Reset basic state so repeated calls don't accumulate weird state.
    dex.entries = []
    dex.text_path = ""
    dex.json_path = ""
    dex.dirty = False

    # Try to auto-load from default files in the project folder.
    # Adjust order if you prefer JSON only / TXT only.
    default_files = ["pokemon.txt", "pokemon.json"]

    for filename in default_files:
        if os.path.exists(filename):
            try:
                detect_and_load(dex, filename)
            except Exception:
                # On web, silently ignore load errors for now
                pass

    return dex

def get_pokemon_list_for_web():
    """
    Build the Pokédex and return a simple list of dictionaries
    for the web app.

    Each dict has keys:
    - number
    - name
    - type
    - hp
    - attack
    - defense
    """
    dex = build_pokedex()
    pokemon_list = []

    for p in dex.get_entries():
        s = p.get_stats()
        pokemon_dict = {
            # national_no is stored as a string like "0001" – we keep it as string
            "number": p.get_national_no(),
            "name": p.get_name(),
            "type": getattr(p.__class__, "TYPE_NAME", "Unknown"),
            "hp": s.get_stat("hp"),
            "attack": s.get_stat("attack"),
            "defense": s.get_stat("defense"),
        }
        pokemon_list.append(pokemon_dict)

    return pokemon_list




# ---------------------------
# Menu system
# ---------------------------
def main():
    dex = Pokedex.get_instance()

    # Initial load
    path = input("Enter file path (.txt or .json) or press Enter to skip: ").strip()
    if path:
        try:
            loaded = detect_and_load(dex, path)
            print(f"Loaded {loaded} Pokémon from '{path}'.")
        except Exception as e:
            print("Load failed:", e)
    else:
        print("Starting with an empty Pokédex.")

    # Main loop
    while True:
        print("\n--- POKEDEX MENU ---")
        print("1) List all Pokémon")
        print("2) Search Pokémon")
        print("3) Update Pokémon stat")
        print("4) Remove Pokémon")
        print("5) Add new Pokémon")
        print("6) Export type report (Fire/Grass)")
        print("7) Visualize stats")
        print("8) Update basic info (No./Height/Weight)")
        print("S) Save")
        print("X) Exit")

        choice = input("Select: ").strip().lower()

        # Exit
        if choice in ("x", "exit"):
            if dex.dirty:
                savep = input("Save changes before exiting? (y/n): ").strip().lower()
                if savep == "y":
                    save_back(dex)
            print("Goodbye!")
            break

        # Option 1: List all pokemons
        elif choice == "1":
            if dex.count() == 0:
                print("Pokédex is empty.")
            else:
                print(f"\n--- Listing {dex.count()} Pokémon ---")
                for p in dex.get_entries():
                    print(p.display())
                    print("-" * 40)

        # Option 2: Search
        elif choice == "2":
            print("Search by:")
            print("  1) Name")
            print("  2) National number (format: No. 0004)")
            print("  3) Type")
            sub = input("Choose option: ").strip()
            try:
                if sub == "1":
                    name = input("Name: ").strip()
                    p = dex.find_by_name(name)
                    print(p.display())
                elif sub == "2":
                    raw_no = input("National Number (format: No. 0004): ").strip()
                    try:
                        no = Validator.parse_national_no(raw_no)
                    except ValueError as e:
                        print(e)
                        continue
                    p = dex.find_by_national_no(no)
                    print(p.display())
                elif sub == "3":
                    t = input("Type (Fire/Grass): ").strip()
                    pokemons = dex.find_by_type(t)
                    if pokemons:
                        for p in pokemons:
                            print(p.display())
                            print("-" * 40)
                    else:
                        print(f"No Pokémon of type {t} found.")
                else:
                    print("Invalid option.")
            except PokemonNotFoundError as e:
                print(e)
            except Exception as e:
                print("Error:", e)

        # Option 3: Update
        elif choice == "3":
            print("Update by: 1) Name  2) National number")
            sub = input("Choose option: ").strip()
            if sub == "1":
                name = input("Name: ").strip()
                field = input("Field (hp/attack/defense/sp_atk/sp_def/speed): ").strip()
                value = input("New value (int): ").strip()
                if dex.update_by_name(name, field, value):
                    save_back(dex)
                    print("Updated and saved.")
                else:
                    print("Update failed.")
            elif sub == "2":
                raw_no = input("National Number (format: No. 0004): ").strip()
                try:
                    no = Validator.parse_national_no(raw_no)
                except ValueError as e:
                    print(e)
                    continue
                field = input("Field (hp/attack/defense/sp_atk/sp_def/speed): ").strip()
                value = input("New value (int): ").strip()
                if dex.update_by_national_no(no, field, value):
                    save_back(dex)
                    print("Updated and saved.")
                else:
                    print("Update failed.")
            else:
                print("Invalid option.")

        # Option 4: Remove
        elif choice == "4":
            print("Remove by: 1) Name  2) National number")
            sub = input("Choose option: ").strip()
            if sub == "1":
                name = input("Name: ").strip()
                if dex.remove_by_name(name):
                    save_back(dex)
                    print("Removed and saved.")
                else:
                    print("Not found.")
            elif sub == "2":
                raw_no = input("National Number (format: No. 0004): ").strip()
                try:
                    no = Validator.parse_national_no(raw_no)
                except ValueError as e:
                    print(e)
                    continue
                if dex.remove_by_national_no(no):
                    save_back(dex)
                    print("Removed and saved.")
                else:
                    print("Not found.")
            else:
                print("Invalid option.")

        # Option 5: Add new pokemon
        elif choice == "5":
            print("Add new Pokémon")
            ptype = input("Type (Fire/Grass): ").strip().lower()
            if ptype not in ("fire", "grass"):
                print("Invalid type! Only Fire or Grass allowed.")
                continue

            # Choose class dynamically
            klass = GenericFirePokemon if ptype == "fire" else GenericGrassPokemon

            # ------- VALIDATED INPUT -------
            raw_no = prompt_nonempty("National Number (format: No. 0025): ")
            try:
                national_no = Validator.parse_national_no(raw_no)
            except ValueError as e:
                print(e)
                continue

            name = prompt_nonempty("Name: ")
            if not Validator.valid_name(name):
                print("Invalid name! Use only letters and spaces.")
                continue

            species = prompt_nonempty("Species: ")
            if not Validator.valid_name(species):
                print("Invalid species name! Use only letters and spaces.")
                continue

            height = prompt_nonempty("Height (e.g., 0.6 m): ")
            try:
                height_val = Validator.parse_height_m(height)
            except ValueError as e:
                print(e); continue

            weight = prompt_nonempty("Weight (e.g., 8.5 kg): ")
            try:
                weight_val = Validator.parse_weight_kg(weight)
            except ValueError as e:
                print(e); continue

            abilities = input("Abilities (separate with ';'): ").strip() or ""
            if not Validator.valid_abilities(abilities):
                print("Invalid abilities format! Use only letters, commas, or semicolons.")
                continue
            abilities_list = [a.strip() for a in abilities.split(";")] if abilities else []

            hp = prompt_int("HP: "); attack = prompt_int("Attack: ")
            defense = prompt_int("Defense: "); sp_attack = prompt_int("Special Attack: ")
            sp_defense = prompt_int("Special Defense: "); speed = prompt_int("Speed: ")

            try:
                s = Stats(hp, attack, defense, sp_attack, sp_defense, speed)
                p = klass(national_no=national_no, name=name, species=species,
                        height_m=height_val, weight_kg=weight_val,
                        abilities=abilities_list, stats=s)
                dex.add(p)
                save_back(dex)
                print(f"{ptype.capitalize()} Pokémon added and saved.")
            except Exception as e:
                print("Add failed:", e)

        # Option 6: Export type report
        elif choice == "6":
            t = input("Type name (Fire/Grass): ").strip()
            try:
                path = dex.export_type_report(t)
                print("Exported:", path)
            except Exception as e:
                print("Export failed:", e)

        # Option 7: Visualize stats
        elif choice == "7":
            if dex.count() == 0:
                print("No Pokémon data to visualize.")
                continue
            print("Choose visualization type:")
            print("  1) Bar chart (single Pokémon’s stats)")
            print("  2) Line chart (Fire vs Grass averages)")
            print("  3) Pie chart (single Pokémon’s stat distribution)")
            sub = input("Select option: ").strip()

            save = input("Save chart to file? (y/n): ").strip().lower()
            save_path = input("Filename (e.g., chart.png): ").strip() if save == "y" else None

            try:
                if sub == "1":
                    name = input("Enter Pokémon name: ").strip()
                    p = dex.find_by_name(name)
                    Visualizer.bar_stats_single(p, save_path)
                elif sub == "2":
                    Visualizer.line_type_averages(dex.get_entries(), save_path)
                elif sub == "3":
                    name = input("Enter Pokémon name: ").strip()
                    p = dex.find_by_name(name)
                    Visualizer.pie_stats(p, save_path)
                else:
                    print("Invalid option.")
            except PokemonNotFoundError as e:
                print(e)
            except Exception as e:
                print("Visualization failed:", e)

         # Option 8: Update basic info (national no, height, weight)
        elif choice == "8":
            print("Update by: 1) Name  2) National number")
            sub = input("Choose option: ").strip()
            try:
                if sub == "1":
                    key = input("Name: ").strip()
                    p = dex.find_by_name(key)
                elif sub == "2":
                    raw_key = input("National Number (format: No. 0004): ").strip()
                    try:
                        key = Validator.parse_national_no(raw_key)
                    except ValueError as e:
                        print(e)
                        continue
                    p = dex.find_by_national_no(key)
                else:
                    print("Invalid option.")
                    continue

                print(f"\nCurrent info for {p.get_name()}:")
                print(f"  National Number: {p.get_national_no()}")
                print(f"  Height: {p.get_height()} m")
                print(f"  Weight: {p.get_weight()} kg")

                field = input("Field (national_no / height_m / weight_kg): ").strip().lower()
                value = input("New value: ").strip()

                cur_name = p.get_name()
                cur_species = p.get_species()
                cur_abilities = p.get_abilities()
                cur_no = p.get_national_no()
                cur_h = p.get_height()
                cur_w = p.get_weight()

                new_no, new_h, new_w = cur_no, cur_h, cur_w

                if field == "national_no":
                    new_no = Validator.parse_national_no(value)
                elif field == "height_m":
                    new_h = Validator.parse_height_m(value)
                elif field == "weight_kg":
                    new_w = Validator.parse_weight_kg(value)
                else:
                    print("Invalid field.")
                    continue

                p.set_basic_info(cur_name, new_no, cur_species, new_h, new_w, cur_abilities)
                dex.dirty = True
                save_back(dex)
                print("Updated and saved.")

            except PokemonNotFoundError as e:
                print(e)
            except ValueError as e:
                print(e)


        # Option S: Save
        elif choice == "s":
            save_back(dex)

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

