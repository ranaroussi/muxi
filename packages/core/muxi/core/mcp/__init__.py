# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        MCP - Model Control Protocol Package
# Description:  Framework for integrating with external tools and models
# Role:         Enables agent interactions with tools and external services
# Usage:        Used by agents to perform actions beyond conversation
# Author:       Muxi Framework Team
#
# The MCP (Model Control Protocol) package provides the infrastructure for
# agents to interact with external tools, services, and models. It includes:
#
# 1. Connection Management
#    - Establishes and maintains connections to MCP servers
#    - Handles authentication and credential management
#    - Provides reconnection logic for resilient operation
#
# 2. Message Formatting
#    - Standardizes message structure between agents and tools
#    - Handles tool call parsing and formatting
#    - Manages request/response cycle for tool invocations
#
# 3. Tool Integration
#    - Provides unified interface for tool discovery and usage
#    - Supports synchronous and asynchronous tool execution
#    - Handles error conditions and timeouts gracefully
#
# The MCP protocol enables agents to perform a wide range of actions beyond
# simple text generation, such as retrieving information, manipulating data,
# or interacting with external APIs and services.
#
# Example usage:
#
#   # Create MCP service
#   service = MCPService.get_instance()
#
#   # Connect to an MCP server
#   service.register_server("my_tools", "http://localhost:8080")
#
#   # Invoke a tool
#   result = await service.invoke_tool(
#       server_id="my_tools",
#       tool_name="search_database",
#       parameters={"query": "customer records"}
#   )
#
# The MCP package forms the backbone of the Muxi framework's tool integration
# capabilities, enabling AI agents to interact with the external world in a
# controlled and secure manner.
# =============================================================================

# Re-export key classes
from muxi.core.mcp.handler import (
    MCPHandler, MCPConnectionError, MCPRequestError, MCPTimeoutError
)
from muxi.core.mcp.reconnect_handler import ReconnectingMCPHandler
from muxi.core.mcp.service import MCPService
from muxi.core.mcp.message import MCPMessage, MCPToolCall
from muxi.core.mcp.parser import ToolParser, ToolCall

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
