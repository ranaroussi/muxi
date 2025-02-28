#!/usr/bin/env python
"""
API server entry point for the AI Agent Framework.

This script provides an HTTP API for interacting with
agents created with the AI Agent Framework.
"""

import argparse
from src.api import start_api


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Agent Framework API Server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Starting API server on {args.host}:{args.port}...")
    if args.reload:
        print("Auto-reload enabled")
    start_api(host=args.host, port=args.port, reload=args.reload)
