#!/usr/bin/env python3
"""
Whoop OAuth Authentication Script
Handles the OAuth 2.0 flow to get access and refresh tokens
"""

import os
import json
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('WHOOP_CLIENT_ID')
CLIENT_SECRET = os.getenv('WHOOP_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Whoop OAuth endpoints
AUTH_URL = 'https://api.prod.whoop.com/oauth/oauth2/auth'
TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token'

# Scopes - request access to all available data
SCOPES = [
    'read:recovery',
    'read:cycles',
    'read:sleep',
    'read:workout',
    'read:profile',
    'read:body_measurement',
    'offline'  # Enables refresh token
]

# Global variables to store OAuth state and authorization code
oauth_state = None
auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""

    def do_GET(self):
        global auth_code, oauth_state

        # Parse the callback URL
        query = urlparse(self.path).query
        params = parse_qs(query)

        # Validate state parameter
        received_state = params.get('state', [None])[0]
        if received_state != oauth_state:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Error: Invalid State</h1>
                    <p>State validation failed. This may be a CSRF attack.</p>
                </body>
                </html>
            """)
            return

        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params.get('error', ['Unknown error'])[0]
            error_desc = params.get('error_description', [''])[0]
            self.wfile.write(f"<html><body><h1>Error: {error}</h1><p>{error_desc}</p></body></html>".encode())

    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


def get_authorization_url():
    """Generate the OAuth authorization URL"""
    global oauth_state

    # Generate a random state for CSRF protection (minimum 8 characters required)
    oauth_state = secrets.token_urlsafe(32)

    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'state': oauth_state
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code):
    """Exchange authorization code for access and refresh tokens"""
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")


def save_tokens(tokens):
    """Save tokens to a local file"""
    with open('tokens.json', 'w') as f:
        json.dump(tokens, f, indent=2)
    print("✓ Tokens saved to tokens.json")


def main():
    """Main authentication flow"""
    print("=" * 60)
    print("WHOOP API Authentication")
    print("=" * 60)

    # Generate authorization URL
    auth_url = get_authorization_url()

    print("\n1. Opening browser for authentication...")
    print(f"\nIf the browser doesn't open automatically, visit:\n{auth_url}\n")

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("2. Waiting for authorization callback...")
    server = HTTPServer(('localhost', 8080), CallbackHandler)

    # Wait for one request (the callback)
    server.handle_request()

    if auth_code:
        print("3. Authorization code received!")
        print("4. Exchanging code for access token...")

        # Exchange code for tokens
        tokens = exchange_code_for_tokens(auth_code)

        print("\n✓ Authentication successful!")
        print(f"  Access Token: {tokens['access_token'][:20]}...")
        print(f"  Refresh Token: {tokens['refresh_token'][:20]}...")
        print(f"  Expires in: {tokens['expires_in']} seconds")

        # Save tokens
        save_tokens(tokens)

        print("\n" + "=" * 60)
        print("You're all set! Run whoop_data.py to fetch your data.")
        print("=" * 60)
    else:
        print("\n✗ Authentication failed - no authorization code received")


if __name__ == '__main__':
    main()
