"""
Gunicorn Configuration
Production WSGI server settings - Optimized for Render deployment
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - Optimized for Render's Starter plan (512MB RAM)
# Default to 2 workers (each uses ~50-100MB RAM)
# Can override with WEB_CONCURRENCY environment variable
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Threads per worker (for better concurrency without memory overhead)
threads = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Process naming
proc_name = "kaluwala_csr"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Preload app for better performance
preload_app = True

# Restart workers periodically to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Graceful timeout for worker shutdown
graceful_timeout = 30

def on_starting(server):
    """Called just before the master process is initialized"""
    print("Starting Kaluwala CSR Libraries...")
    print(f"Workers: {workers}, Threads per worker: {threads}")

def on_reload(server):
    """Called to recycle workers during a reload"""
    print("Reloading Kaluwala CSR Libraries...")

def when_ready(server):
    """Called just after the server is started"""
    print("Kaluwala CSR Libraries is ready. Listening on:", bind)

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    print(f"Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal"""
    print(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal"""
    print(f"Worker received SIGABRT signal (pid: {worker.pid})")
