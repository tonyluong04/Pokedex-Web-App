# A3.py - Domain Logic for Pokédex Web Application
# 
# This module contains core classes and logic for managing Pokémon data.
# It is designed to be used by the Flask web application (app.py).
# 
# Pure domain logic - NO web functions, NO CLI code.

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
        """Initialize all six stats.
        
        Args:
            hp: Hit Points (0-255)
            attack: Physical attack power (0-255)
            defense: Physical defense (0-255)
            sp_atk: Special attack power (0-255)
            sp_def: Special defense (0-255)
            speed: Speed stat (0-255)
            
        Raises:
            ValueError: If any stat is negative
        """
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
        """Set the value of the specified stat.
        
        Args:
            field: Stat name (hp, attack, defense, sp_atk, sp_def, speed)
            value: New stat value (must be non-negative)
            
        Raises:
            ValueError: If value is negative
            AttributeError: If field name is invalid
        """
        v = int(value)
        if v < 0:
            raise ValueError("value must be non-negative.")
        if field == "hp": 
            self.__hp = v
        elif field == "attack": 
            self.__attack = v
        elif field == "defense": 
            self.__defense = v
        elif field == "sp_atk": 
            self.__sp_atk = v
        elif field == "sp_def": 
            self.__sp_def = v
        elif field == "speed": 
            self.__speed = v
        else:
            raise AttributeError(f"Unknown stat '{field}'.")

    def get_stat(self, field):
        """Return the value of the specified stat.
        
        Args:
            field: Stat name (hp, attack, defense, sp_atk, sp_def, speed)
            
        Returns:
            Integer stat value
            
        Raises:
            AttributeError: If field name is invalid
        """
        if field == "hp": 
            return self.__hp
        if field == "attack": 
            return self.__attack
        if field == "defense": 
            return self.__defense
        if field == "sp_atk": 
            return self.__sp_atk
        if field == "sp_def": 
            return self.__sp_def
        if field == "speed": 
            return self.__speed
        raise AttributeError(f"Unknown stat '{field}'.")

    def get_total(self):
        """Return total of all six stats."""
        return (self.__hp + self.__attack + self.__defense +
                self.__sp_atk + self.__sp_def + self.__speed)

    def as_dict(self):
        """Return stats as a dictionary for JSON serialization."""
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
        """Create a Stats object from a dictionary.
        
        Args:
            d: Dictionary with stat keys (missing keys default to 0)
            
        Returns:
            Stats object
        """
        return Stats(
            d.get("hp", 0),
            d.get("attack", 0),
            d.get("defense", 0),
            d.get("sp_atk", 0),
            d.get("sp_def", 0),
            d.get("speed", 0)
        )


# -----------------------
# Abstract Base Classes
# -----------------------

class BasePokemon(ABC):
    """Abstract base class defining shared attributes and methods for all Pokémon."""

    def __init__(self, national_no="0", name="Unknown", species="???",
                 height_m=0.0, weight_kg=0.0, abilities=None, stats=None):
        """Initialize basic Pokémon information and stats.
        
        Args:
            national_no: National Pokédex number (string, e.g., "0004")
            name: Pokémon name
            species: Species classification
            height_m: Height in meters
            weight_kg: Weight in kilograms
            abilities: List of ability names
            stats: Stats object
        """
        self.__national_no = str(national_no)
        self.__name = name
        self.__species = species
        self.__height_m = float(height_m)
        self.__weight_kg = float(weight_kg)
        self.__abilities = abilities if abilities is not None else []
        self.__stats = stats if stats is not None else Stats(0, 0, 0, 0, 0, 0)

    # Getters
    def get_national_no(self): 
        return self.__national_no
    
    def get_name(self): 
        return self.__name
    
    def get_species(self): 
        return self.__species
    
    def get_height(self): 
        return self.__height_m
    
    def get_weight(self): 
        return self.__weight_kg
    
    def get_abilities(self): 
        return self.__abilities
    
    def get_stats(self): 
        return self.__stats

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
        """Display Pokémon information (implemented by subclasses)."""
        pass

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
        """Recreate a Pokémon object from a dictionary.
        
        Args:
            d: Dictionary with Pokémon data
            
        Returns:
            Pokémon object (correct subclass based on type)
        """
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
# Type Classes (Abstract)
# -----------------------

class GrassType(BasePokemon, ABC):
    """Abstract base class for all Grass-type Pokémon."""
    
    TYPE_NAME = "Grass"
    TYPE_INFO = (
        "Grass is one of the three basic elemental types along with Fire and Water, "
        "which constitute the three starter Pokémon. Grass is weak defensively, "
        "with 5 weaknesses and many resistances."
    )

    def display(self):
        """Return Grass-type description."""
        return "[Type: Grass]\n" + GrassType.TYPE_INFO
    
    @classmethod
    def calculate_average(cls, pokemons):
        """Calculate average stats for all Grass-type Pokémon.
        
        Args:
            pokemons: List of Pokémon objects
            
        Returns:
            Dictionary with average stats, or None if no Grass Pokémon
        """
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
    """Abstract base class for all Fire-type Pokémon."""
    
    TYPE_NAME = "Fire"
    TYPE_INFO = (
        "Fire is one of the three basic elemental types along with Water and Grass. "
        "Fire types are rare in early games, but often powerful."
    )

    def display(self):
        """Return Fire-type description."""
        return "[Type: Fire]\n" + FireType.TYPE_INFO

    @classmethod
    def calculate_average(cls, pokemons):
        """Calculate average stats for all Fire-type Pokémon.
        
        Args:
            pokemons: List of Pokémon objects
            
        Returns:
            Dictionary with average stats, or None if no Fire Pokémon
        """
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
# Concrete Pokémon Classes
# -----------------------

class Oddish(GrassType):
    """Grass-type Pokémon: Oddish"""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


class Bulbasaur(GrassType):
    """Grass-type Pokémon: Bulbasaur"""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


class Charmander(FireType):
    """Fire-type Pokémon: Charmander"""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


class Vulpix(FireType):
    """Fire-type Pokémon: Vulpix"""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


class GenericFirePokemon(FireType):
    """Generic Fire-type Pokémon created by the user."""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


class GenericGrassPokemon(GrassType):
    """Generic Grass-type Pokémon created by the user."""
    def display(self):
        s = self.get_stats()
        return f"\nNational Number: {self.get_national_no()}\nName: {self.get_name()}\nType: {self.TYPE_NAME}\nSpecies: {self.get_species()}\nHeight: {self.get_height()} m\nWeight: {self.get_weight()} kg\nAbilities: {';'.join(self.get_abilities())}\nStats:\n  HP: {s.get_stat('hp')}\n  Attack: {s.get_stat('attack')}\n  Defense: {s.get_stat('defense')}\n  Special Attack: {s.get_stat('sp_atk')}\n  Special Defense: {s.get_stat('sp_def')}\n  Speed: {s.get_stat('speed')}\n  Total: {s.get_total()}"


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
    """Singleton class that manages all Pokémon entries.
    
    Pokemon.json is the single source-of-truth for persistence.
    Used by Flask web application to manage Pokémon data.
    """

    __instance = None

    def __init__(self):
        """Initialize Pokedex (private - use get_instance())."""
        if Pokedex.__instance is not None:
            raise Exception("Pokedex is a Singleton class! Use get_instance().")
        self.entries = []
        self.json_path = "pokemon.json"
        Pokedex.__instance = self

    @classmethod
    def get_instance(cls):
        """Get or create the singleton Pokedex instance."""
        if cls.__instance is None:
            cls.__instance = Pokedex()
        return cls.__instance

    # ===== Core Operations =====

    def add(self, p):
        """Add a Pokémon and persist to JSON immediately.
        
        Args:
            p: Pokémon object
        """
        self.entries.append(p)
        self.save_json()

    def get_entries(self):
        """Get list of all Pokémon entries."""
        return self.entries

    def count(self):
        """Get total number of Pokémon."""
        return len(self.entries)

    # ===== Search Operations =====

    def find_by_name(self, name):
        """Find Pokémon by name (case-insensitive).
        
        Args:
            name: Pokémon name
            
        Returns:
            Pokémon object
            
        Raises:
            PokemonNotFoundError: If not found
        """
        for p in self.entries:
            if p.get_name().lower() == name.lower():
                return p
        raise PokemonNotFoundError(f"No Pokémon found with name: {name}")

    def find_by_national_no(self, no):
        """Find Pokémon by national number.
        
        Args:
            no: National number (string or int)
            
        Returns:
            Pokémon object
            
        Raises:
            PokemonNotFoundError: If not found
        """
        no_str = str(no)
        for p in self.entries:
            if p.get_national_no() == no_str:
                return p
        raise PokemonNotFoundError(f"No Pokémon found with national number: {no}")

    def find_by_type(self, type_name):
        """Find all Pokémon by type.
        
        Args:
            type_name: Type name (Fire, Grass, etc.)
            
        Returns:
            List of Pokémon objects matching type
        """
        wanted = str(type_name).lower()
        results = [p for p in self.entries
                   if getattr(p.__class__, "TYPE_NAME", "").lower() == wanted]
        return results

    # ===== Remove Operations =====

    def remove_by_name(self, name):
        """Remove Pokémon by name and persist to JSON.
        
        Args:
            name: Pokémon name
            
        Returns:
            True if removed, False if not found
        """
        try:
            p = self.find_by_name(name)
            self.entries.remove(p)
            self.save_json()
            return True
        except PokemonNotFoundError:
            return False

    def remove_by_national_no(self, no):
        """Remove Pokémon by national number and persist to JSON.
        
        Args:
            no: National number
            
        Returns:
            True if removed, False if not found
        """
        try:
            p = self.find_by_national_no(no)
            self.entries.remove(p)
            self.save_json()
            return True
        except PokemonNotFoundError:
            return False

    # ===== Update Operations =====

    def update_by_name(self, name, field, value):
        """Update a stat by Pokémon name and persist to JSON.
        
        Args:
            name: Pokémon name
            field: Stat field name (hp, attack, defense, etc.)
            value: New value
            
        Returns:
            True if updated, False if error
        """
        try:
            p = self.find_by_name(name)
            p.get_stats().set_stat(field, value)
            self.save_json()
            return True
        except (PokemonNotFoundError, Exception):
            return False

    def update_by_national_no(self, no, field, value):
        """Update a stat by national number and persist to JSON.
        
        Args:
            no: National number
            field: Stat field name (hp, attack, defense, etc.)
            value: New value
            
        Returns:
            True if updated, False if error
        """
        try:
            p = self.find_by_national_no(no)
            p.get_stats().set_stat(field, value)
            self.save_json()
            return True
        except (PokemonNotFoundError, Exception):
            return False

    # ===== JSON File I/O =====

    def load_json(self, filepath="pokemon.json"):
        """Load Pokémon data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Number of Pokémon loaded
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JSON file '{filepath}' not found.")

        self.json_path = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.entries = [BasePokemon.from_dict(d) for d in data]
        return len(self.entries)

    def save_json(self, filepath=None):
        """Save all entries to JSON file.
        
        Auto-called by add/remove/update operations.
        
        Args:
            filepath: Optional new filepath to save to
            
        Returns:
            Path to saved file
        """
        if filepath:
            self.json_path = filepath
        data = [p.to_dict() for p in self.entries]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return self.json_path


# -----------------------
# Validator
# -----------------------

class Validator:
    """Validates Pokémon input fields for web forms."""

    _re_name = re.compile(r"^[A-Za-z ]+$")
    _re_abilities = re.compile(r"^[A-Za-z ,;]+$")

    @staticmethod
    def valid_name(value: str):
        """Validate name field (letters and spaces only).
        
        Args:
            value: String to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(Validator._re_name.fullmatch(value or ""))

    @staticmethod
    def valid_abilities(value: str):
        """Validate abilities field (letters, commas, semicolons).
        
        Args:
            value: String to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(Validator._re_abilities.fullmatch(value or ""))


# -----------------------
# Visualizer
# -----------------------

class Visualizer:
    """Matplotlib charts for Pokédex stats visualization.
    
    Generates PNG charts that can be embedded in web app.
    """
    
    STAT_ORDER = ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]
    STAT_LABELS = np.array(["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"])

    @staticmethod
    def bar_stats_single(pokemon, save_path=None):
        """Generate bar chart for single Pokémon's stats.
        
        Args:
            pokemon: Pokémon object
            save_path: Optional path to save PNG file
            
        Returns:
            Path to saved file (or None if not saved)
            
        Raises:
            ValueError: If pokemon is None
        """
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

    @staticmethod
    def line_type_averages(pokemons, save_path=None):
        """Generate line chart comparing Fire vs Grass type averages.
        
        Args:
            pokemons: List of Pokémon objects
            save_path: Optional path to save PNG file
            
        Returns:
            Path to saved file (or None if not saved)
            
        Raises:
            ValueError: If no data to plot
        """
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

    @staticmethod
    def pie_stats(pokemon, save_path=None):
        """Generate pie chart for Pokémon stat distribution.
        
        Args:
            pokemon: Pokémon object
            save_path: Optional path to save PNG file
            
        Returns:
            Path to saved file (or None if not saved)
            
        Raises:
            ValueError: If pokemon is None
        """
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



