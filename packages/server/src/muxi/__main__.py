#!/usr/bin/env python3
"""
Main entry point for the muxi-server package when run as a module.

This allows running the MUXI server with:
python -m muxi.server

This is useful for development, testing, and containerized deployments
where direct module execution is preferred over CLI commands.
"""

import logging
import sys
from muxi.server import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("run")


def main():
    """Run the MUXI server."""
    print("Starting MUXI Server...")
    logger.info("Starting MUXI Server")

    # Run server in the main thread
    # This will block until the server stops
    run_server()


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
