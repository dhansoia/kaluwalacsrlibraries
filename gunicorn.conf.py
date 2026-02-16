"""
Gunicorn Configuration
Production WSGI server settings - Ultra-optimized for Render Starter (512MB RAM)
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - Minimal for Render Starter plan (512MB RAM)
# Using 1 worker with multiple threads is more memory efficient
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
worker_class = "gthread"  # Use threaded workers instead of sync
worker_connections = 1000
timeout = 120
keepalive = 2

# Threads per worker (handles concurrent requests efficiently)
threads = 4

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

# Preload app for better performance and memory sharing
preload_app = True

# Restart workers periodically to prevent memory leaks
max_requests = 500  # Reduced from 1000
max_requests_jitter = 50

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Memory optimization - limit worker memory
worker_tmp_dir = "/dev/shm"  # Use shared memory for tmp files

def on_starting(server):
    """Called just before the master process is initialized"""
    print("Starting Kaluwala CSR Libraries (Memory-Optimized)...")
    print(f"Workers: {workers}, Threads per worker: {threads}")
    print(f"Worker class: gthread (memory efficient)")

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
