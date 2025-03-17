#!/usr/bin/env python3
"""
Main entry point for the muxi-web package when run as a module.

This allows running the web UI with:
python -m muxi.web

This is useful for development, testing, and containerized deployments
where direct module execution is preferred over CLI commands.
"""

import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("run")


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
    """Run the web UI."""
    print("Starting MUXI Web UI...")
    logger.info("Starting MUXI Web UI")

    # Run web UI in the main thread
    run_web_ui()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down web UI...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting web UI: {str(e)}")
        import traceback

        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Ensure you have Node.js and npm installed for the web UI")
        print("2. Make sure all dependencies are installed:")
        print("   - pip install muxi-web")
        print("   - cd web && npm install")
        sys.exit(1)
