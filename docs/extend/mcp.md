---
layout: default
title: MCP Server Integration
nav_order: 2
parent: Extending Capabilities
permalink: /extend/mcp
---

# MCP Server Integration

{: .fs-5 .fw-600 }
Model Context Protocol (MCP) is a standardized protocol that allows AI applications to access specialized capabilities, share context with language models, and expose tools to AI systems. This guide explains how to integrate external MCP servers with your MUXI agents.

## Introduction to MCP

MCP enables your agents to leverage external tools and capabilities through a standardized interface. The MCP handler in MUXI manages the connections to MCP servers, abstracting the complexities of the transport layer from your application code.

Key features of the MUXI MCP implementation include:

- Support for multiple transport types (HTTP+SSE and Command-line)
- Robust reconnection with exponential backoff
- Cancellation support for long-running operations
- Comprehensive error handling and diagnostic information
- Integration with the official MCP Python SDK

## Connecting to MCP Servers

There are two ways to connect your agents to MCP servers:

### 1. Using Configuration Files

The simplest approach is to define MCP servers in your agent configuration:

```yaml
name: my_assistant
system_message: You are a helpful assistant with access to external tools.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
mcp_servers:
- name: web_search
  url: http://localhost:5001
  credentials:
  - id: search_api_key
    param_name: api_key
    required: true
    env_fallback: SEARCH_API_KEY
- name: calculator
  command: npx -y @modelcontextprotocol/server-calculator
```

### 2. Programmatically

You can also connect to MCP servers programmatically:

```python
from muxi import muxi

# Initialize MUXI
app = muxi()

# Add an agent
await app.add_agent("assistant", "configs/assistant.yaml")

# Connect to an HTTP-based MCP server
await app.get_agent("assistant").connect_mcp_server(
    name="weather",
    url="http://localhost:5001",
    credentials={"api_key": "your_weather_api_key"}
)

# Connect to a command-line MCP server
await app.get_agent("assistant").connect_mcp_server(
    name="calculator",
    command="npx -y @modelcontextprotocol/server-calculator"
)
```

## Transport Types

MUXI supports two transport types for MCP servers, automatically selected based on the parameters you provide:

### HTTP+SSE Transport

This transport type is used for web-based MCP servers that follow the HTTP+SSE protocol. It's automatically selected when you provide a `url` parameter:

- Client → Server messages go through HTTP POST requests
- Server → Client messages go through Server-Sent Events (SSE)
- Requires maintaining long-lived connections

```python
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_api_key"}
)
```

### Command-line Transport

This transport type is used for local MCP servers that run as executable processes. It's automatically selected when you provide a `command` parameter:

- Servers are started via command-line
- Communication happens via standard input/output
- Suitable for local development and testing

```python
await agent.connect_mcp_server(
    name="calculator",
    command="npx -y @modelcontextprotocol/server-calculator",
    credentials={"api_key": "your_api_key"}
)
```

## MCP Server Credentials

MCP servers may require credentials for authentication, though many servers don't need any authentication. Credentials are completely optional:

```yaml
mcp_servers:
- name: web_search
  url: http://localhost:5001
  credentials:  # Optional: can be omitted if no authentication is required
  - id: search_api_key
    param_name: api_key
    required: true
    env_fallback: SEARCH_API_KEY
```

Or programmatically:

```python
# With credentials
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_api_key"}
)

# Without credentials (passing None or omitting the parameter are both valid)
await agent.connect_mcp_server(
    name="calculator",
    url="http://localhost:5002"
)
```

## Using MCP Servers in Agents

Once an MCP server is connected to an agent, the agent can automatically use it when needed. The LLM will receive information about available tools from MCP servers and can call them as needed.

```python
# Agent will automatically use connected MCP servers when appropriate
response = await app.chat(
    "What's the weather in New York? Also, what's 123 * 456?"
)
print(response.content)
```

## Handling Disconnections

The MCP handler automatically manages reconnections using an exponential backoff strategy, but you can also manually disconnect and reconnect:

```python
# Disconnect from an MCP server
await agent.disconnect_mcp_server("web_search")

# Reconnect to the MCP server
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_api_key"}
)
```

## Cancellation Support

You can cancel long-running MCP operations if needed:

```python
from muxi.core.mcp_handler import CancellationToken

# Create a cancellation token
token = CancellationToken()

# Execute a potentially long-running operation
task = agent.execute_tool("web_search", {"query": "complex research topic"}, token)

# Cancel the operation if needed
token.cancel()
```

## Error Handling

The MCP handler provides comprehensive error handling with specific exception types:

- `MCPError`: Base exception for all MCP-related errors
- `MCPConnectionError`: For connection-related errors
- `MCPRequestError`: For errors when making requests
- `MCPTimeoutError`: For timeout errors
- `MCPCancelledError`: For canceled operations

```python
from muxi.core.mcp_handler import MCPError, MCPConnectionError

try:
    await agent.connect_mcp_server(
        name="web_search",
        url="http://non-existent-server.com",
        credentials={}
    )
except MCPConnectionError as e:
    print(f"Failed to connect: {e}")
except MCPError as e:
    print(f"General MCP error: {e}")
```

## Diagnostics

You can get detailed diagnostic information about MCP server connections:

```python
# Get connection statistics for all MCP servers
stats = agent.mcp_handler.get_connection_stats()
print(stats)

# Output example:
# {
#     "active_connections": 2,
#     "registered_tools": 5,
#     "active_operations": 0,
#     "current_time": "2023-07-15T10:30:45.123456",
#     "connections": {
#         "web_search": {
#             "connected": true,
#             "url": "http://localhost:5001",
#             "command": null,
#             "session_id": "abc123",
#             "connect_time": "2023-07-15T10:25:30.123456",
#             "connection_age_s": 315.0,
#             "last_activity": "2023-07-15T10:28:45.123456",
#             "idle_time_s": 120.0
#         },
#         "calculator": {
#             "connected": true,
#             "url": null,
#             "command": "npx -y @modelcontextprotocol/server-calculator",
#             "pid": 12345
#         }
#     }
# }
```

## Best Practices

1. **Use Standard MCP Servers**: Prefer well-tested, community-maintained MCP servers when possible
2. **Handle Credentials Securely**: Use environment variables for sensitive credentials
3. **Implement Proper Error Handling**: Catch and handle MCP-related exceptions appropriately
4. **Monitor Connection Health**: Periodically check connection statistics for potential issues
5. **Set Appropriate Timeouts**: Configure request timeouts based on expected operation duration

## Available MCP Servers

While MUXI doesn't include built-in MCP servers, it has been tested with the following external MCP servers:

1. **Web Search**: MCP servers that provide web search capabilities
2. **Weather**: MCP servers for weather information
3. **Calculator**: Basic calculator functionality
4. **Brave Search**: Integration with Brave search engine

To use these servers, you'll need to install and configure them separately according to their documentation.

## Advanced Configuration

For advanced scenarios, you can configure additional parameters:

```python
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_api_key"},
    request_timeout=120  # Timeout in seconds
)
```

## Conclusion

MCP server integration enables your MUXI agents to leverage external capabilities through a standardized protocol. By following this guide, you can connect your agents to various MCP servers and enhance their capabilities.
