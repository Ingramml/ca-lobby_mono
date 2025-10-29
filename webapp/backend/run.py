#!/usr/bin/env python3
"""
CA Lobby API Startup Script

Simple script to run the Flask development server.
For production deployment, use gunicorn with app.py
"""

from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    print(f"🚀 Starting CA Lobby API")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🏥 Health: http://{host}:{port}/health")
    print(f"📊 Status: http://{host}:{port}/api/status")

    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))