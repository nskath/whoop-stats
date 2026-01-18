#!/bin/bash

echo "================================"
echo "Whoop Data Tracker Setup"
echo "================================"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: python whoop_auth.py    (authenticate with Whoop)"
echo "2. Run: python whoop_data.py    (fetch your data)"
echo "3. Run: python generate_viz.py  (create visualizations)"
echo ""
echo "To set up GitHub automation:"
echo "1. Create a new GitHub repository"
echo "2. Add secrets: WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET, WHOOP_REFRESH_TOKEN"
echo "3. Push this code to GitHub"
echo ""
