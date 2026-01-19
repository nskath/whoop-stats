#!/usr/bin/env python3
"""
Whoop Data Fetching Script
Fetches sleep, strain, recovery, and other health data from Whoop API
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('WHOOP_CLIENT_ID')
CLIENT_SECRET = os.getenv('WHOOP_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Whoop API base URL (using v2)
API_BASE = 'https://api.prod.whoop.com/developer/v2'
TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token'


class WhoopClient:
    """Client for interacting with Whoop API"""

    def __init__(self, tokens_file='tokens.json'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()
        self.access_token = self.tokens.get('access_token')

    def load_tokens(self):
        """Load tokens from file"""
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception("Tokens file not found. Run whoop_auth.py first to authenticate.")

    def save_tokens(self):
        """Save updated tokens to file"""
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI
        }

        response = requests.post(TOKEN_URL, data=data)

        if response.status_code == 200:
            new_tokens = response.json()
            self.tokens.update(new_tokens)
            self.access_token = new_tokens['access_token']
            self.save_tokens()
            print("✓ Access token refreshed")
        else:
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")

    def make_request(self, endpoint, params=None):
        """Make authenticated request to Whoop API"""
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        url = f"{API_BASE}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)

        # If unauthorized, try refreshing token
        if response.status_code == 401:
            print("Access token expired, refreshing...")
            self.refresh_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    def get_user_profile(self):
        """Get user profile information"""
        return self.make_request('user/profile/basic')

    def get_cycles(self, limit=25):
        """Get physiological cycles (daily summaries)"""
        params = {'limit': limit}
        return self.make_request('cycle', params=params)

    def get_recovery(self, limit=25):
        """Get recovery data"""
        params = {'limit': limit}
        return self.make_request('recovery', params=params)

    def get_sleep(self, limit=25):
        """Get sleep data"""
        params = {'limit': limit}
        return self.make_request('activity/sleep', params=params)

    def get_workouts(self, limit=25):
        """Get workout data"""
        params = {'limit': limit}
        return self.make_request('activity/workout', params=params)


def save_data(data, filename):
    """Save data to JSON file"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved {filename}")


def main():
    """Main data fetching flow"""
    print("=" * 60)
    print("WHOOP Data Fetcher")
    print("=" * 60)

    # Initialize client
    client = WhoopClient()

    print(f"\nFetching most recent data (up to 25 records per category)...")
    print()

    # Fetch user profile
    print("1. Fetching user profile...")
    profile = client.get_user_profile()
    save_data(profile, 'profile.json')

    # Fetch cycles
    print("2. Fetching cycles...")
    cycles = client.get_cycles()
    save_data(cycles, 'cycles.json')

    # Fetch recovery
    print("3. Fetching recovery data...")
    recovery = client.get_recovery()
    save_data(recovery, 'recovery.json')

    # Fetch sleep
    print("4. Fetching sleep data...")
    sleep = client.get_sleep()
    save_data(sleep, 'sleep.json')

    # Fetch workouts
    print("5. Fetching workout data...")
    workouts = client.get_workouts()
    save_data(workouts, 'workouts.json')

    print("\n" + "=" * 60)
    print("Data fetch complete! Check the data/ directory.")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  User: {profile.get('user_id', 'Unknown')}")
    print(f"  Cycles: {len(cycles.get('records', []))} records")
    print(f"  Recovery: {len(recovery.get('records', []))} records")
    print(f"  Sleep: {len(sleep.get('records', []))} records")
    print(f"  Workouts: {len(workouts.get('records', []))} records")


if __name__ == '__main__':
    main()
