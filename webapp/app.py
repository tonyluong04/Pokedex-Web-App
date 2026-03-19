"""
Pokédex Web App v2.0 - Flask Backend
Personal project with PokéAPI integration, PostgreSQL, and Google OAuth.
"""
import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_login import current_user

# Add parent directory to path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

from config import get_config
from webapp.extensions import db, login_manager

def create_app(config=None):
    """
    Application factory function.
    
    Args:
        config: Configuration object (uses get_config() if None)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Configure login manager
    # Redirect unauthenticated users to SPA shell at '/'
    login_manager.login_view = 'index'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from webapp.models.user import User
        # SQLAlchemy 2.x: prefer Session.get over Query.get
        return db.session.get(User, user_id)
    
    # Create app context and database tables
    with app.app_context():
        # Ensure all models are imported so db.create_all() sees them.
        # Without these imports, new tables (e.g. user_pokemon) won't be created.
        import webapp.models.user  # noqa: F401
        import webapp.models.pokemon  # noqa: F401
        db.create_all()
    
    # Register blueprints
    from webapp.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Pokémon + collection API (Phase 1)
    from webapp.routes.pokemon import pokemon_bp
    app.register_blueprint(pokemon_bp, url_prefix="/api")
    
    # Battle API (Phase 3)
    from webapp.routes.battle import battle_bp
    app.register_blueprint(battle_bp, url_prefix="/api")

    # ===== Routes (Phase 0) =====
    
    @app.route('/')
    def index():
        """Serve SPA shell."""
        return render_template('index.html')
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'environment': app.config['FLASK_ENV'],
            'authenticated': current_user.is_authenticated
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='localhost', port=5000)
