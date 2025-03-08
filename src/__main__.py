#!/usr/bin/env python3
"""
Main entry point for the src package when run as a module.

This allows running both the API server and web UI with:
python -m src

This is useful for development, testing, and containerized deployments
where direct module execution is preferred over CLI commands.
"""

import logging
import os
import socket
import subprocess
import sys
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("run")


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def run_api_server():
    """Start the API server."""
    try:
        # Check if port is already in use
        if is_port_in_use(5050):
            msg = "Port 5050 is already in use. API server cannot start."
            logger.error(msg)
            print(f"Error: {msg}")
            print("Please stop any other processes using port 5050 " "and try again.")
            return False

        logger.info("Starting API server on port 5050...")
        from src.api.app import start_api

        # Running directly in the main thread - fixes the signal handling issue
        start_api(host="0.0.0.0", port=5050, reload=True)
        return True
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        print(f"Error: Failed to start API server: {str(e)}")
        return False


def run_web_ui():
    """Start the web UI development server."""
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Change to the web UI directory
        web_dir = os.path.join(current_dir, "web")

        if not os.path.exists(web_dir):
            logger.error(f"Web UI directory not found at {web_dir}")
            print(f"Error: Web UI directory not found at {web_dir}")
            return False

        logger.info(f"Changing directory to {web_dir}")
        os.chdir(web_dir)

        # Check if node_modules exists
        node_modules = os.path.join(web_dir, "node_modules")
        if not os.path.exists(node_modules):
            logger.warning("node_modules not found, running npm install...")
            print("node_modules not found. Running npm install...")
            result = subprocess.run(["npm", "install"], check=False)
            if result.returncode != 0:
                logger.error("npm install failed. Please run it manually.")
                print("Error: npm install failed. Please run it manually.")
                return False

        # Run npm start
        logger.info("Starting web UI with npm start...")
        subprocess.run(["npm", "start"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start web UI: {str(e)}")
        print(f"Error: Failed to start web UI: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in run_web_ui: {str(e)}")
        print(f"Error in run_web_ui: {str(e)}")
        return False


def main():
    """Run both the API server and web UI."""
    print("Starting MUXI Framework...")
    logger.info("Starting MUXI Framework")

    # Modified approach: Start web UI in a thread, API server in main thread

    # Start Web UI in a separate thread
    web_thread = threading.Thread(target=run_web_ui)
    web_thread.daemon = True
    web_thread.start()

    print("Web UI starting in background...")
    print("Starting API server...")

    # Run API server in the main thread (this should resolve the signal issue)
    # This will block until the API server stops
    run_api_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting servers: {str(e)}")
        import traceback

        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Check if port 5050 is already in use by another process")
        print("2. Ensure you have Node.js and npm installed for the web UI")
        print("3. Make sure all dependencies are installed:")
        print("   - For Python: pip install -r requirements.txt")
        print("   - For Web UI: cd src/web && npm install")
        sys.exit(1)
