# Gunicorn configuration for HealthKart360
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, default 0
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'healthkart360'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for development)
keyfile = None
certfile = None

# Application
wsgi_module = "healthkart360.wsgi:application"
