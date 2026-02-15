"""
WSGI Entry Point for Gunicorn
Production server entry point
"""

import os
from app import create_app

# Create Flask application
app = create_app('production')

if __name__ == "__main__":
    app.run()
