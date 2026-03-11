"""
Initialize database tables for Pokédex v2.0
Run once to create all tables.
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webapp.app import create_app, db

def init_database():
    """Create all database tables."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tables created: {tables}")

if __name__ == '__main__':
    init_database()