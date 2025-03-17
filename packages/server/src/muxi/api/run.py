#!/usr/bin/env python3
"""
Run script for the API server.
"""

import argparse
import logging
import os
import sys

import uvicorn

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Add the project root to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MUXI Framework API Server")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument("--port", type=int, default=5050, help="Port to bind to (default: 5050)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    return parser.parse_args()


if __name__ == "__main__":
    from muxi.server.api.app import create_app

    # Parse command line arguments
    args = parse_args()

    # Create the FastAPI application
    app = create_app()

    # Display startup message
    print(f"Starting API server on {args.host}:{args.port}...")
    if args.reload:
        print("Auto-reload enabled")

    # Run the API server with specified options
    uvicorn.run(app, host=args.host, port=args.port, log_level="debug", reload=args.reload)
