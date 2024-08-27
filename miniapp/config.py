# config.py

import os

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Mini App configuration
MINI_APP_URL = 'https://your-mini-app-domain.com'

# Database configuration
MONGODB_URI = os.environ.get('MONGODB_URI')

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Logging configuration
LOG_FOLDER = 'logs'

# Stripe configuration (if using Stripe for payments)
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')