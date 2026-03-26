"""
Pokémon-related database models for Pokédex v2.0

Phase 1: store a user's personal selection (My Pokéball).
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy.dialects.postgresql import UUID

from webapp.extensions import db
from webapp.utils.db_helpers import get_or_create


class UserPokemon(db.Model):
    """
    UserPokemon model - represents a Pokémon in a user's personal Pokédex.
    
    References PokéAPI data by pokemon_id (not a copy).
    """
    
    __tablename__ = 'user_pokemon'
    
    # Primary Key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # PokéAPI Reference
    pokemon_id = db.Column(db.Integer, nullable=False)
    pokemon_name = db.Column(db.String(255), nullable=False)
    pokemon_number = db.Column(db.Integer, nullable=False)
    
    # Metadata (timezone-aware UTC)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'pokemon_id', name='uq_user_pokemon'),
    )
    
    def __repr__(self):
        return f"<UserPokemon {self.pokemon_name}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'id': str(self.id),
            'pokemon_id': self.pokemon_id,
            'pokemon_name': self.pokemon_name,
            'pokemon_number': self.pokemon_number,
            'added_at': self.added_at.isoformat(),
        }
    
    @staticmethod
    def add_to_pokedex(user_id, pokemon_id, pokemon_name, pokemon_number):
        """
        Add a Pokémon to user's Pokédex.
        
        Returns:
            UserPokemon object or None if duplicate
        """
        instance, created = get_or_create(
            UserPokemon,
            filter_by={"user_id": user_id, "pokemon_id": pokemon_id},
            defaults={
                "pokemon_name": pokemon_name,
                "pokemon_number": pokemon_number,
            }
        )

        if not created:
            return None  # Already in Pokédex

        db.session.commit()
        return instance
