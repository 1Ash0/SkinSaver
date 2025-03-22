import json
import os

import requests
from app import db
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import login_required, login_user, logout_user, current_user
from models import User
from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get Replit domain for the redirect URL
REPLIT_DOMAIN = os.environ.get("REPLIT_DOMAIN", "")

# Determine if we're in development or production
DEV_REDIRECT_URL = f'https://{REPLIT_DOMAIN}/google_login/callback'

print(f"""Google OAuth configured with:
- Client ID: {'[CONFIGURED]' if GOOGLE_CLIENT_ID else '[MISSING]'}
- Client Secret: {'[CONFIGURED]' if GOOGLE_CLIENT_SECRET else '[MISSING]'}
- Redirect URL: {DEV_REDIRECT_URL}

To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs
""")

# OAuth client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

google_auth = Blueprint("google_auth", __name__)


@google_auth.route("/google_login")
def login():
    # Ensure the Google client is configured
    if not client:
        flash("Google OAuth is not properly configured. Please try regular login.", "warning")
        return redirect(url_for("login"))
        
    # Find out what URL to hit for Google login
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    except Exception as e:
        current_app.logger.error(f"Error getting Google discovery URL: {e}")
        flash("Error connecting to Google. Please try regular login.", "warning")
        return redirect(url_for("login"))

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        # Replacing http:// with https:// is important as the external
        # protocol must be https to match the URI whitelisted
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@google_auth.route("/google_login/callback")
def callback():
    # Ensure the Google client is configured
    if not client:
        flash("Google OAuth is not properly configured", "warning")
        return redirect(url_for("login"))
    
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    if not code:
        flash("Authentication failed. Please try again.", "danger")
        return redirect(url_for("login"))

    try:
        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            # Replacing http:// with https:// is important as the external
            # protocol must be https to match the URI whitelisted
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=request.base_url.replace("http://", "https://"),
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        # Verify email is verified by Google
        userinfo = userinfo_response.json()
        if not userinfo.get("email_verified"):
            flash("Google email not verified", "danger")
            return redirect(url_for("login"))
        
        # Get user info
        users_email = userinfo["email"]
        users_name = userinfo.get("given_name", users_email.split('@')[0])
        
        # Create or update user
        user = User.query.filter_by(email=users_email).first()
        if not user:
            # Create new user
            user = User(
                username=users_name,
                email=users_email,
                has_password=False  # Flag that this user doesn't have a password set
            )
            db.session.add(user)
            db.session.commit()
            flash(f"Welcome {users_name}! Your account has been created.", "success")
        else:
            flash(f"Welcome back, {users_name}!", "success")

        # Log in the user
        login_user(user)
        
        # Redirect to homepage
        return redirect(url_for("index"))
    except Exception as e:
        current_app.logger.error(f"Error in Google callback: {e}")
        flash("Error authenticating with Google. Please try again.", "danger")
        return redirect(url_for("login"))


# We'll use the existing logout route in app.py