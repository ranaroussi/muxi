#!/usr/bin/env python3
"""
Run script for the API server.
"""

import os
import sys
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Add the project root to the path so we can import from src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
))

if __name__ == "__main__":
    from src.ui.api.app import create_app

    # Create the FastAPI application
    app = create_app()

    # Run the API server with debug mode
    uvicorn.run(app, host="127.0.0.1", port=5050, log_level="debug")
