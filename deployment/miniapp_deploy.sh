#!/bin/bash

# Deploy the Mini App

# Pull the latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
# python manage.py db upgrade

# Restart the Flask server
sudo systemctl restart wattz-car-rental-miniapp