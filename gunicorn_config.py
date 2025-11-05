# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# Worker processes
# Calculate workers based on CPU count, but cap at a reasonable maximum
cpu_count = multiprocessing.cpu_count()
# Use 2-4 workers per CPU, but cap at 8 workers maximum for this application
default_workers = min(cpu_count * 2 + 1, 8)
workers = int(os.environ.get('GUNICORN_WORKERS', default_workers))
# Ensure workers is at least 1 and at most 16
workers = max(1, min(workers, 16))
worker_class = 'sync'
worker_connections = 1000
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
keepalive = 2

# Logging
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')  # stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'student_tracker'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

# Preload application (set to False if experiencing issues with database connections)
preload_app = False

# Worker timeouts
graceful_timeout = 30

# Restart workers after this many requests (helpful for memory leaks)
max_requests = 1000
max_requests_jitter = 50

