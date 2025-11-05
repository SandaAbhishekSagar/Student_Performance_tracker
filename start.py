#!/usr/bin/env python3
"""
Startup script that initializes database and starts Gunicorn server.
This ensures the database is created before the application starts.
"""
import os
import sys

def main():
    """Initialize database and start Gunicorn"""
    sys.stdout.flush()
    sys.stderr.flush()
    
    print("🔧 Initializing database...", flush=True)
    sys.stdout.flush()
    
    # Initialize database
    try:
        from app import app, init_db, logger
        with app.app_context():
            logger.info("Starting database initialization...")
            init_db()
            logger.info("Database initialization completed successfully")
        print("✅ Database initialized successfully", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Error initializing database: {e}", flush=True, file=sys.stderr)
        sys.stderr.flush()
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        # Try to log the error
        try:
            from app import logger
            logger.error(f"Database initialization failed: {e}", exc_info=True)
        except:
            pass
        sys.exit(1)
    
    # Start Gunicorn
    print("🚀 Starting Gunicorn server...", flush=True)
    sys.stdout.flush()
    
    # Use exec to replace current process with Gunicorn
    try:
        # Check if gunicorn_config.py exists, otherwise use defaults
        if os.path.exists('gunicorn_config.py'):
            os.execvp('gunicorn', ['gunicorn', '-c', 'gunicorn_config.py', 'app:app'])
        else:
            # Fallback to default configuration
            port = os.environ.get('PORT', '5000')
            os.execvp('gunicorn', [
                'gunicorn',
                '--bind', f'0.0.0.0:{port}',
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

