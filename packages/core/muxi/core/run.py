# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Run - Server Startup Functionality
# Description:  Functions for starting and running Muxi servers
# Role:         Provides server initialization capabilities for the Muxi framework
# Usage:        Imported by facade.py and used to start API servers
# Author:       Muxi Framework Team
#
# The run.py file provides the functionality to start and run Muxi servers.
# It includes:
#
# 1. Server Initialization
#    - Starting API servers on specified host and port
#    - Checking port availability before startup
#    - Handling server configuration parameters
#
# 2. Error Handling
#    - Detecting and reporting port conflicts
#    - Managing server startup exceptions
#    - Providing detailed logging and user-friendly error messages
#
# This module is typically used via the Muxi facade:
#
#   app = muxi()
#   app.run(host="0.0.0.0", port=5050)
#
# Or it can be used directly in more advanced scenarios:
#
#   from muxi.core.run import run_server
#   run_server(host="0.0.0.0", port=5050, reload=False, mcp=True)
#
# Note: The current implementation is a placeholder that will be replaced
# with a full server implementation according to the Muxi API specifications.
# =============================================================================

import socket
from loguru import logger


def is_port_in_use(port):
    """
    Check if a port is in use.

    This function attempts to create a socket connection to the specified port
    on localhost to determine if the port is already being used by another process.
    It's used to prevent port conflicts before starting the server.

    Args:
        port (int): The port number to check. Must be a valid port number (1-65535).

    Returns:
        bool: True if the port is in use (unavailable), False if the port is free.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect_ex returns 0 if the connection succeeds (port is in use)
        # and a non-zero value if it fails (port is available)
        return s.connect_ex(("localhost", port)) == 0


def run_server(host="0.0.0.0", port=5050, reload=True, mcp=False):
    """
    Start the MUXI server with all enabled components.

    This function initializes and starts the Muxi API server with the specified
    configuration. It checks for port availability before attempting to start
    and provides appropriate feedback.

    This is currently a placeholder implementation that only logs the attempt to start
    a server. In the future, this will be replaced with proper server implementations
    according to the Muxi API specifications.

    Args:
        host (str): Host address to bind the server to. Defaults to "0.0.0.0" which
            makes the server available on all network interfaces.
        port (int): Port number to bind the server to. Defaults to 5050.
        reload (bool): Whether to enable auto-reload for development mode, which
            automatically restarts the server when code changes. Defaults to True.
        mcp (bool): Whether to enable Model Control Protocol (MCP) support for
            tool calling and external integrations. Defaults to False.

    Returns:
        bool: True if server started successfully, False otherwise. Can be used
            to determine if startup succeeded in programmatic contexts.
    """
    try:
        # Check if port is already in use before attempting to start the server
        if is_port_in_use(port):
            # Construct error message for both logs and user output
            msg = f"Port {port} is already in use. MUXI server cannot start."
            # Log the error to the application logs
            logger.error(msg)
            # Print user-friendly error messages to the console
            print(f"Error: {msg}")
            print(f"Please stop any other processes using port {port} and try again.")
            return False

        # For now, we'll just log that we would have started a server
        # This will be replaced with actual implementation later
        logger.info(
            f"[PLACEHOLDER] Starting MUXI server on {host}:{port} " f"(reload={reload}, mcp={mcp})"
        )
        print(f"[PLACEHOLDER] MUXI server would start on {host}:{port}")
        print("This is a placeholder until the MUXI API server is implemented.")

        return True
    except Exception as e:
        # Catch any unexpected exceptions during server startup
        # Log the error with detailed information for debugging
        logger.error(f"Failed to start MUXI server: {str(e)}")
        # Provide a simplified error message to the user
        print(f"Error: Failed to start MUXI server: {str(e)}")
        return False
