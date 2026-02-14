#!/usr/bin/env python3
"""
Simple runner for async app without command-line argument conflicts.
"""
import os
import asyncio

# Set environment variables for configuration
os.environ['AVR_HOST'] = '192.168.1.100'
os.environ['AVR_PORT'] = '60128'
os.environ['DEBUG'] = 'true'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = '8080'

# Now import and run the app
from async_app import app

if __name__ == '__main__':
    import sys
    # Clear sys.argv to prevent argument parsing
    sys.argv = ['run_async.py']

    print("=" * 60)
    print("DiscoAVR Async Server Starting...")
    print("=" * 60)
    print(f"Web Interface: http://localhost:8080")
    print(f"Debug Mode: ENABLED (no receiver required)")
    print(f"WebSocket: ws://localhost:8080/ws/state")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=8080, debug=True)
