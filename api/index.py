"""
Vercel entry point for CA Lobby API
Imports the main Flask application from webapp/backend/app.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webapp', 'backend'))

from app import create_app

app = create_app()

# This is the handler that Vercel will call
def handler(request, response):
    return app(request, response)

if __name__ == '__main__':
    app.run()