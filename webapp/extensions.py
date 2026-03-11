from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Shared Flask extensions for the application.
# Import these in models and blueprints instead of importing from app.py

db = SQLAlchemy()
login_manager = LoginManager()

