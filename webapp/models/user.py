"""
User model for Pokédex v2.0
Stores user authentication and profile information from Google OAuth.
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid

from webapp.extensions import db
from webapp.utils.db_helpers import get_or_create


class User(UserMixin, db.Model):
    """User model for storing Google OAuth authenticated users."""
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Google OAuth Fields
    google_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(512))
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps (timezone-aware UTC)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses."""
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
    
    @staticmethod
    def from_google_oauth(google_id, email, name, picture=None):
        """
        Create or update user from Google OAuth credentials.
        
        Args:
            google_id: Google account ID (from OAuth token 'sub')
            email: User's email address
            name: User's display name
            picture: Profile picture URL
            
        Returns:
            User object (created or updated)
        """
        user, created = get_or_create(
            User,
            filter_by={"google_id": google_id},
            defaults={
                "email": email,
                "name": name,
                "picture": picture,
                "is_active": True,
                "last_login": datetime.now(timezone.utc),
            }
        )

        if not created:
            # Update existing user's fields
            user.email = email
            user.name = name
            if picture:
                user.picture = picture
            user.last_login = datetime.now(timezone.utc)

        db.session.commit()
        return user