#!/usr/bin/env python3
"""
Startup script that initializes database and starts Gunicorn server.
This ensures the database is created before the application starts.
"""
import os
import sys

def main():
    """Initialize database and start Gunicorn"""
    print("🔧 Initializing database...")
    
    # Initialize database
    try:
        from app import app, init_db
        with app.app_context():
            init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    
    # Start Gunicorn
    print("🚀 Starting Gunicorn server...")
    
    # Use exec to replace current process with Gunicorn
    try:
        # Check if gunicorn_config.py exists, otherwise use defaults
        if os.path.exists('gunicorn_config.py'):
            os.execvp('gunicorn', ['gunicorn', '-c', 'gunicorn_config.py', 'app:app'])
        else:
            # Fallback to default configuration
            os.execvp('gunicorn', [
                'gunicorn',
                '--bind', '0.0.0.0:5000',
                '--workers', '4',
                '--timeout', '120',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'app:app'
            ])
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install with: pip install gunicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

