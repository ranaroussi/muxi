#!/usr/bin/env python3
"""
Run both the API server and web UI for the AI Agent Framework.
"""

import threading
import time
import subprocess
import sys
import os


def run_api_server():
    """Start the API server."""
    from src.ui.api.app import start_api
    start_api(host="0.0.0.0", port=8000, reload=True)


def run_web_ui():
    """Start the web UI development server."""
    # Change to the web UI directory
    os.chdir(os.path.join(os.getcwd(), "src", "ui", "web"))

    # Run npm start
    subprocess.run(["npm", "start"], check=True)


if __name__ == "__main__":
    print("Starting AI Agent Framework servers...")

    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api_server)
    api_thread.daemon = True
    api_thread.start()

    # Wait for API server to start
    print("Starting API server...")
    time.sleep(3)
    print("API server running at http://localhost:8000")

    # Start web UI
    print("Starting web UI...")
    try:
        run_web_ui()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)
