"""
Authentication routes for Google OAuth.
Handles login, logout, callback, and session management.
"""
import os
from flask import Blueprint, redirect, url_for, session, jsonify, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token

from webapp.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ===== GOOGLE OAUTH SETUP =====

def get_google_flow():
    """
    Create and return a Google OAuth flow instance.
    
    Returns:
        Flow object configured with Google OAuth credentials
    """
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',  # Will create this in setup instructions
        scopes=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ],
        redirect_uri=current_app.config['GOOGLE_REDIRECT_URI']
    )
    return flow


# ===== AUTH ROUTES =====

@auth_bp.route('/google')
def google_login():
    """
    Initiate Google OAuth login flow.
    Redirects user to Google Sign-In.
    """
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store state in session for CSRF protection
    session['oauth_state'] = state
    
    return redirect(authorization_url)


@auth_bp.route('/google/callback')
def google_callback():
    """
    Google OAuth callback handler.
    Processes OAuth response and creates/updates user session.
    
    Returns:
        Redirect to dashboard on success, login page on failure
    """
    # Verify state for CSRF protection
    state = session.get('oauth_state')
    if not state:
        return redirect(url_for('auth.login_page'))
    
    try:
        # Get authorization code from URL
        code = request.args.get('code')
        if not code:
            return redirect(url_for('auth.login_page'))
        
        # Exchange code for credentials
        flow = get_google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from ID token
        id_token = credentials.id_token
        user_info = verify_oauth2_token(id_token, Request(), current_app.config['GOOGLE_CLIENT_ID'])
        
        # Extract user data
        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', email)
        picture = user_info.get('picture')
        
        # Create or update user in database
        user = User.from_google_oauth(google_id, email, name, picture)
        
        # Log user in
        login_user(user)
        
        # After successful login, send user to SPA shell at '/'
        return redirect(url_for('index'))
    
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return redirect(url_for('auth.login_page'))


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user and clear session.
    
    Returns:
        Redirect to login page
    """
    logout_user()
    session.clear()
    # After logout, return to SPA shell; frontend will show login view
    return redirect(url_for('index'))


# ===== STATUS & INFO ENDPOINTS =====

@auth_bp.route('/status')
def status():
    """
    Get current authentication status.
    
    Returns:
        JSON with user info if logged in, empty object if not
    """
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    else:
        return jsonify({'authenticated': False})


@auth_bp.route('/profile')
@login_required
def profile():
    """
    Get current user's profile information.
    
    Returns:
        JSON with user profile data
    """
    return jsonify(current_user.to_dict())


# ===== UI ROUTES (for development) =====

@auth_bp.route('/login')
def login_page():
    """
    Serve login page (development).
    In production, frontend handles this.
    """
    # SPA at '/' handles login UI; keep this route only as a fallback
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Legacy development dashboard.
    For SPA, the main UI lives at '/' and uses /auth/status.
    """
    return redirect(url_for('index'))
