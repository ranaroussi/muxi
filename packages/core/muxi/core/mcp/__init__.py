"""
MCP (Model Control Protocol) Package

This package contains all components related to the MCP protocol for interacting
with hosted models and services.
"""

# Re-export key classes
from packages.core.mcp.handler import (
    MCPHandler, MCPConnectionError, MCPRequestError, MCPTimeoutError
)
from packages.core.mcp.reconnect_handler import ReconnectingMCPHandler
from packages.core.mcp.service import MCPService
from packages.core.mcp.message import MCPMessage, MCPToolCall
from packages.core.mcp.parser import ToolParser, ToolCall

__all__ = [
    'MCPHandler',
    'MCPConnectionError',
    'MCPRequestError',
    'MCPTimeoutError',
    'ReconnectingMCPHandler',
    'MCPService',
    'MCPMessage',
    'MCPToolCall',
    'ToolParser',
    'ToolCall',
]
