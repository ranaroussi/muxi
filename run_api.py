#!/usr/bin/env python3
"""
Run the API server for the AI Agent Framework.
"""

from src.api.app import start_api


if __name__ == "__main__":
    print("Starting AI Agent Framework API server...")
    start_api(host="0.0.0.0", port=8000, reload=True)
