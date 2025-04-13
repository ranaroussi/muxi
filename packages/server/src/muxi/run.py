"""
Run functionality for the MUXI server.

This module contains the core functionality for running the MUXI server.
"""

import logging
import socket

# Configure logging
logger = logging.getLogger("run")


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def run_server(host="0.0.0.0", port=5050, reload=True, mcp=False):
    """Start the MUXI server with all enabled components (API, WebSockets, MCP)."""
    try:
        # Check if port is already in use
        if is_port_in_use(port):
            msg = f"Port {port} is already in use. MUXI server cannot start."
            logger.error(msg)
            print(f"Error: {msg}")
            print(f"Please stop any other processes using port {port} and try again.")
            return False

        logger.info(f"Starting MUXI server on port {port}...")
        from muxi.server.api.app import start_api

        # Running directly in the main thread - fixes the signal handling issue
        start_api(host=host, port=port, reload=reload, mcp=mcp)
        return True
    except Exception as e:
        logger.error(f"Failed to start MUXI server: {str(e)}")
        print(f"Error: Failed to start MUXI server: {str(e)}")
        return False
