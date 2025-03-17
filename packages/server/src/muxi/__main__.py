#!/usr/bin/env python3
"""
Main entry point for the muxi-server package when run as a module.

This allows running both the API server and web UI with:
python -m muxi.server

This is useful for development, testing, and containerized deployments
where direct module execution is preferred over CLI commands.
"""

import logging
import socket
import sys

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
        from muxi.server.api.app import start_api

        # Running directly in the main thread - fixes the signal handling issue
        start_api(host="0.0.0.0", port=5050, reload=True)
        return True
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        print(f"Error: Failed to start API server: {str(e)}")
        return False


def main():
    """Run the API server."""
    print("Starting MUXI Server...")
    logger.info("Starting MUXI Server")

    # Run API server in the main thread (this should resolve the signal issue)
    # This will block until the API server stops
    run_api_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        import traceback

        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Check if port 5050 is already in use by another process")
        print("2. Make sure all dependencies are installed:")
        print("   - pip install muxi-server")
        sys.exit(1)
