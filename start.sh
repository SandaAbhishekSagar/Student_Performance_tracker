#!/bin/bash
# Startup script that initializes database and starts Gunicorn

set -e

echo "🔧 Initializing database..."

# Initialize database
python -c "
from app import app, init_db
with app.app_context():
    init_db()
    print('✅ Database initialized successfully')
"

echo "🚀 Starting Gunicorn server..."

# Start Gunicorn
exec gunicorn -c gunicorn_config.py app:app

