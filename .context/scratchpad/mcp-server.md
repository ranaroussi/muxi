# MCP Server Protocol PRD: Multi-Model Compatibility Protocol for MUXI Framework

## Overview

This document outlines the implementation of an MCP (Multi-Model Compatibility Protocol) server within the MUXI Framework to enable seamless integration with MCP-compatible hosts and clients like Claude, Cursor, and other AI assistants. The MCP server will provide a standardized interface for external tools to communicate with MUXI agents and leverage their capabilities.

## Problem Statement

Currently, the MUXI Framework provides REST API, WebSockets, CLI, and web application interfaces. However, it lacks a standardized way to:

1. Integrate with popular AI assistants that support the MCP protocol
2. Expose agent capabilities as tools for discovery by MCP hosts
3. Enable streaming interactions with MUXI agents through MCP-compatible interfaces
4. Provide a bridge for non-SSE clients to connect to MUXI's MCP server

## Objectives

1. Enable seamless integration between MUXI Framework and MCP-compatible hosts
2. Maintain MUXI's lightweight, modular architecture
3. Expose agent capabilities as discoverable MCP tools
4. Support both request/response and streaming interactions
5. Provide security and authentication consistent with MUXI's existing interfaces

## Feature Requirements

### Core Capabilities

1. **MCP Server**: Server-side implementation of the MCP protocol using Server-Sent Events (SSE)
2. **Tool Discovery**: Expose agent capabilities as MCP tools for discovery
3. **Request Handling**: Process MCP requests and route to appropriate agents
4. **Response Streaming**: Support streaming responses from agents back to MCP clients
5. **Bridge Package**: NPX-based bridge for clients that don't natively support SSE

### Technical Specifications

1. **Protocol Format**: JSON-based message format compatible with MCP standard
2. **Transport Layer**: Server-Sent Events (SSE) for the server, HTTP for the bridge
3. **Authentication**: API key-based authentication shared with the REST API
4. **Tool Definition**: JSON Schema-based tool definitions derived from agent capabilities
5. **Bridge Package**: Lightweight NPM package for non-SSE client integration

## Implementation Approach

The MCP server will be implemented as part of the server module in the API directory, consistent with other communication interfaces like the REST API and WebSockets. The implementation will leverage existing components where possible to maintain consistency and reduce duplication.

### Architecture

```
┌─────────────────────────────────────────────────┐
│                MUXI Framework                   │
│                                                 │
│  ┌─────────┐       ┌─────────────────────────┐  │
│  │ Agent 1 │◄─────┐│                         │  │
│  └─────────┘      ││                         │  │
│                   ││                         │  │
│  ┌─────────┐      ││     Orchestrator        │  │
│  │ Agent 2 │◄─────┘│                         │  │
│  └─────────┘       │                         │  │
│                    │                         │  │
│  ┌─────────┐       │                         │  │
│  │ Agent 3 │◄──────┤                         │  │
│  └─────────┘       └─┬───────────────────────┘  │
│                      │                          │
│    Server Module     │                          │
│  ┌────────────────┐  │                          │
│  │                │  │                          │
│  │  REST API      │◄─┘                          │
│  │                │                             │
│  ├────────────────┤                             │
│  │                │                             │
│  │  WebSockets    │                             │
│  │                │                             │
│  ├────────────────┤                             │
│  │                │                             │
│  │  MCP Server    │                             │
│  │                │                             │
│  └───────┬────────┘                             │
│          │                                      │
└──────────┼──────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐       ┌──────────────────┐
│                     │       │                  │
│  MCP-compatible     │◄─────►│  @muxi/mcp-bridge│
│  hosts (Claude,     │       │  (For non-SSE    │
│  Cursor, etc.)      │       │   clients)       │
│                     │       │                  │
└─────────────────────┘       └──────────────────┘
```

### MCP Server Module

The MCP protocol will be implemented through a new module in the server package:

```
packages/server/src/muxi/api/mcp.py
```

This module will contain:

1. `MCPServer` class that handles the core functionality
2. Tool definition translation from agent capabilities
3. Request/response handling logic
4. SSE endpoint implementation

### Bridge Package

A separate NPM package `@muxi/mcp-bridge` will be created to:
1. Provide a client-side interface for the MCP server
2. Handle SSE connection and reconnection
3. Normalize events for non-SSE clients
4. Manage authentication and request formatting

### Integration Points

1. **Orchestrator**: Enhanced to support MCP request routing
2. **Agent**: Capabilities exposed as MCP tools
3. **API Server**: MCP server integrated as part of the API module
4. **A2A Handler**: Leverage for complex multi-agent interactions

## Message Protocol

### Tool Definition

```json
{
  "name": "financial_analysis",
  "description": "Analyze financial data and provide insights",
  "parameters": {
    "type": "object",
    "properties": {
      "statements": {"type": "array", "items": {"type": "string"}},
      "period": {"type": "string", "enum": ["quarterly", "annual"]}
    },
    "required": ["statements"]
  }
}
```

### MCP Request

```json
{
  "id": "req_12345",
  "method": "run_tool",
  "params": {
    "tool_name": "financial_analysis",
    "tool_params": {
      "statements": ["Q1 2023 Income Statement", "Q1 2023 Balance Sheet"],
      "period": "quarterly"
    }
  }
}
```

### MCP Response (Non-streaming)

```json
{
  "id": "req_12345",
  "result": {
    "analysis": "Company XYZ showed strong growth in Q1 2023...",
    "key_metrics": {
      "revenue_growth": "12.5%",
      "profit_margin": "8.2%",
      "debt_to_equity": "0.45"
    }
  }
}
```

### MCP Response (Streaming)

```json
{
  "id": "req_12345",
  "chunk": {
    "text": "Company XYZ showed strong growth in Q1 2023...",
    "isDelta": true
  }
}
```

### Tool List Response

```json
{
  "id": "req_list_tools",
  "result": {
    "tools": [
      {
        "name": "financial_analysis",
        "description": "Analyze financial data and provide insights",
        "parameters": {
          "type": "object",
          "properties": {
            "statements": {"type": "array", "items": {"type": "string"}},
            "period": {"type": "string", "enum": ["quarterly", "annual"]}
          },
          "required": ["statements"]
        }
      },
      {
        "name": "travel_planning",
        "description": "Plan travel itineraries and suggest destinations",
        "parameters": {
          "type": "object",
          "properties": {
            "destination": {"type": "string"},
            "duration": {"type": "integer"},
            "budget": {"type": "number"}
          },
          "required": ["destination", "duration"]
        }
      }
    ]
  }
}
```

## API Endpoints

### MCP Stream Endpoint

```http
GET /mcp/stream
```

### Tool List Endpoint

```http
GET /mcp/tools
```

### MCP Request Endpoint (for bridge)

```http
POST /mcp/request
```

## Implementation Plan

### Phase 1: Core MCP Server

1. Create `mcp.py` module in the API directory
2. Implement `MCPServer` class
3. Add tool definition translation from agent capabilities
4. Create basic request/response message handling
5. Implement MCP endpoints
6. Add authentication shared with REST API

### Phase 2: Bridge Package

1. Create `@muxi/mcp-bridge` NPM package
2. Implement SSE connection handling
3. Add authentication and reconnection logic
4. Create client-side request/response formatting
5. Publish package to NPM

### Phase 3: Enhanced Features

1. Implement streaming response handling
2. Add support for multi-agent interactions
3. Enable tool-to-tool chaining
4. Support for complex parameter types
5. Add detailed usage analytics

## Integration Example

### Server-Side Integration

MCP server functionality can be enabled in two ways:

1. Using the `mcp` parameter when starting the server:

```python
from muxi.server import run_server

# Start server with MCP enabled
run_server(host="0.0.0.0", port=5050, mcp=True)
```

2. Using the dedicated start function:

```python
from muxi.server.api.mcp import start_mcp

# Start MCP server directly
start_mcp(
    host="0.0.0.0",
    port=5050,
    auth_required=True,
    rate_limit=100,
    log_level="info"
)
```

### Bridge Usage Example

```javascript
// Install bridge package
// npm install @muxi/mcp-bridge

const { MuxiMCPBridge } = require('@muxi/mcp-bridge');

// Create bridge instance
const bridge = new MuxiMCPBridge({
  serverUrl: 'https://my-muxi-server.com',
  apiKey: 'my-api-key',
  reconnect: true,
  maxRetries: 5
});

// Connect to MCP server
bridge.connect()
  .then(() => console.log('Connected to MUXI MCP server'))
  .catch(err => console.error('Connection error:', err));

// Get available tools
bridge.listTools()
  .then(tools => console.log('Available tools:', tools))
  .catch(err => console.error('Error listing tools:', err));

// Run a tool
bridge.runTool({
  tool_name: 'financial_analysis',
  tool_params: {
    statements: ['Q1 2023 Income Statement', 'Q1 2023 Balance Sheet'],
    period: 'quarterly'
  }
})
  .then(result => console.log('Tool result:', result))
  .catch(err => console.error('Error running tool:', err));

// Run a tool with streaming response
bridge.runToolStreaming({
  tool_name: 'financial_analysis',
  tool_params: {
    statements: ['Q1 2023 Income Statement', 'Q1 2023 Balance Sheet'],
    period: 'quarterly'
  }
}, chunk => {
  console.log('Received chunk:', chunk);
})
  .then(() => console.log('Streaming complete'))
  .catch(err => console.error('Streaming error:', err));

// Disconnect when done
bridge.disconnect();
```

## MCP Configuration Options

The MCP server can be configured through parameters passed to either the `run_server` function or the dedicated `start_mcp` function.

### Basic Configuration

```python
# Starting server with MCP enabled
from muxi.server import run_server

# Enable MCP with default settings
run_server(mcp=True)

# Explicitly disable MCP
run_server(mcp=False)
```

### Advanced Configuration

```python
# Using the dedicated start_mcp function with advanced options
from muxi.server.api.mcp import start_mcp

start_mcp(
    # Server configuration
    host="0.0.0.0",
    port=5050,

    # Authentication requirements
    auth_required=True,
    auth_scheme="api_key",  # Options: "api_key", "http"

    # Rate limiting
    rate_limit=100,  # Maximum MCP requests per minute

    # Tool discovery options
    advertise_tools=True,  # Make agent capabilities discoverable as tools

    # Logging level for MCP interactions
    log_level="info"  # Options: "debug", "info", "warning", "error"
)
```

## Security Considerations

### Authentication and Authorization

The MCP server will use the same authentication mechanisms as the REST API to maintain consistency and simplify credential management. The primary authentication method will be API keys.

#### API Key Authentication

```http
GET /mcp/stream
Authorization: Bearer API_KEY_HERE
```

or

```http
GET /mcp/stream
X-API-Key: API_KEY_HERE
```

### API Key Management

1. **Generation**: API keys can be generated automatically or defined by users
2. **Storage**: Keys are securely stored with appropriate hashing
3. **Rotation**: Support for key rotation without service disruption
4. **Revocation**: Immediate revocation of compromised keys

### Additional Security Features

1. **Rate limiting** to prevent abuse
2. **Request validation** to ensure proper formatting
3. **Audit logging** of all MCP interactions
4. **Transport layer security** with TLS 1.3+ for all communications

## Success Metrics

1. Number of successful MCP integrations
2. Tool usage frequency and patterns
3. Error rates and types
4. Response time and performance
5. Developer adoption of the MCP interface

## Future Extensions

1. Support for more complex tool interactions
2. Enhanced error handling and diagnostics
3. Tool versioning and deprecation management
4. Custom tool documentation
5. Interactive tool exploration UI

## Bridge Package Technical Details

### Features

1. **Connection Management**:
   - Automatic reconnection with exponential backoff
   - Connection status monitoring
   - Event-based architecture for connection events

2. **Request Handling**:
   - Synchronous and asynchronous request modes
   - Request timeout management
   - Request batching for efficiency

3. **Authentication**:
   - Multiple authentication methods (API key, custom headers)
   - Credential management and security
   - Token refresh capabilities

4. **Streaming Support**:
   - Chunk processing for streaming responses
   - Backpressure handling
   - Error recovery during streams

### Implementation Details

The bridge package will be implemented as a TypeScript/JavaScript library with minimal dependencies. It will use standard browser APIs where possible and Node.js-specific modules when necessary, with appropriate polyfills for cross-environment compatibility.

```typescript
// Core bridge interface definition
interface MuxiMCPBridgeOptions {
  serverUrl: string;
  apiKey?: string;
  customHeaders?: Record<string, string>;
  reconnect?: boolean;
  maxRetries?: number;
  retryBackoff?: number;
  timeout?: number;
}

class MuxiMCPBridge {
  constructor(options: MuxiMCPBridgeOptions);

  // Connection management
  connect(): Promise<void>;
  disconnect(): void;
  isConnected(): boolean;
  onConnectionStateChange(callback: (state: ConnectionState) => void): void;

  // Tool management
  listTools(): Promise<Tool[]>;

  // Request handling
  runTool(params: ToolRunParams): Promise<ToolResult>;
  runToolStreaming(params: ToolRunParams, onChunk: (chunk: ToolChunk) => void): Promise<void>;

  // Advanced usage
  setCustomHeaders(headers: Record<string, string>): void;
  setTimeout(milliseconds: number): void;
}
```

## Code Structure

The implementation will follow this structure:

```
packages/server/src/muxi/
├── __init__.py          # Re-exports run_server function
├── api/
│   ├── __init__.py
│   ├── app.py           # Enhanced to integrate MCP server
│   ├── mcp.py           # New file for MCP server implementation
│   ├── run.py
│   └── websocket.py
└── ...
```

The `mcp.py` file will contain:

```python
from typing import Optional
import logging
from fastapi import FastAPI, Request, Response
from sse_starlette.sse import EventSourceResponse

from muxi.core.orchestrator import Orchestrator

# Configure logging
logger = logging.getLogger("mcp")

class MCPServer:
    """MCP Server implementation using SSE."""

    def __init__(self, app: FastAPI, orchestrator: Orchestrator, **options):
        self.app = app
        self.orchestrator = orchestrator
        self.options = options
        self.register_routes()

    def register_routes(self):
        """Register MCP-related routes on the FastAPI app."""
        self.app.add_api_route("/mcp/stream", self.stream_endpoint, methods=["GET"])
        self.app.add_api_route("/mcp/tools", self.tools_endpoint, methods=["GET"])
        self.app.add_api_route("/mcp/request", self.request_endpoint, methods=["POST"])

    async def stream_endpoint(self, request: Request):
        """SSE endpoint for MCP streaming."""
        # Implementation

    async def tools_endpoint(self, request: Request):
        """Endpoint for listing available tools."""
        # Implementation

    async def request_endpoint(self, request: Request):
        """Endpoint for non-streaming requests."""
        # Implementation


def start_mcp(
    host: str = "0.0.0.0",
    port: int = 5050,
    auth_required: bool = True,
    auth_scheme: str = "api_key",
    rate_limit: int = 100,
    advertise_tools: bool = True,
    log_level: str = "info",
) -> None:
    """Start the MCP server."""
    from muxi.server.api.app import create_app
    from muxi.server import orchestrator

    # Create FastAPI app
    app = create_app()

    # Initialize MCP server
    mcp_server = MCPServer(
        app=app,
        orchestrator=orchestrator,
        auth_required=auth_required,
        auth_scheme=auth_scheme,
        rate_limit=rate_limit,
        advertise_tools=advertise_tools,
        log_level=log_level,
    )

    # Start the server
    import uvicorn
    uvicorn.run(app, host=host, port=port)
```

The `__main__.py` file will be enhanced with an MCP parameter, but we'll also expose the function directly from the package for cleaner imports:

```python
def run_server(
    host: str = "0.0.0.0",
    port: int = 5050,
    reload: bool = True,
    mcp: bool = False
):
    """Start the MUXI server with all enabled components (API, WebSockets, MCP)."""
    try:
        # Check if port is already in use
        if is_port_in_use(port):
            msg = f"Port {port} is already in use. Server cannot start."
            logger.error(msg)
            print(f"Error: {msg}")
            print(f"Please stop any other processes using port {port} and try again.")
            return False

        logger.info(f"Starting MUXI server on port {port}...")
        from muxi.server.api.app import start_api

        # Running directly in the main thread with MCP parameter
        start_api(host=host, port=port, reload=reload, mcp=mcp)
        return True
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"Error: Failed to start server: {str(e)}")
        return False
```

In the package's `__init__.py`:

```python
from muxi.server.run import run_server

__all__ = ["run_server"]
```

## Conclusion

The MCP server implementation for MUXI Framework will provide a powerful interface for integration with MCP-compatible hosts and clients. By implementing the server as part of the API module alongside existing communication interfaces, we maintain a consistent architecture while providing a clean, intuitive API for enabling MCP functionality.

The bridge package will ensure compatibility with clients that don't natively support SSE, expanding the potential user base and making integration as seamless as possible. Together, these components will position MUXI as a flexible and developer-friendly framework for building sophisticated AI applications.
