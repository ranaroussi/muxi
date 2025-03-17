"""
API module for the MUXI Framework.

This module provides a REST API for interacting with agents.
"""

from muxi.server.api.app import create_app, start_api

__all__ = ["create_app", "start_api"]
