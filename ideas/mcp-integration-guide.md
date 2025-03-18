# MCP Handler Integration Guide

This guide provides instructions for integrating our successful HTTP+SSE transport implementation with the main `MCPHandler` class.

## Overview

The Model Context Protocol (MCP) requires specific handling for HTTP+SSE connections, different from what we initially expected. This guide explains how to update the existing codebase based on our successful tests with the mcpify.ai server.

## Dependencies

The MCP Python SDK is now available on PyPI and can be installed with:

```bash
pip install mcp>=1.4.1
```

The package provides:
- Full implementation of the Model Context Protocol specification
- Support for building both MCP clients and servers
- HTTP+SSE transport capabilities
- JSON-RPC request/response handling
- Tools and resource management

Optional extras are available:
- `cli`: Command-line interface for MCP servers
- `rich`: Rich text formatting support
- `ws`: WebSocket support (for future transport methods)

Install with extras using:
```bash
pip install "mcp[cli,rich]>=1.4.1"
```

We've updated our `requirements.txt` file to use the PyPI package instead of installing directly from GitHub.

## Key Components to Modify

1. **HTTPSSETransport Class**: Replace the current implementation with our working version
2. **MCPHandler Class**: Update to handle asynchronous request/response patterns
3. **Request/Response Handling**: Implement proper event handling for the SSE stream

## Implementation Steps

### 1. Update HTTPSSETransport

Replace the existing `HTTPSSETransport` class in `packages/core/src/muxi/core/mcp_handler.py` with the working implementation from `tests/mcp_updated_transport.py`. Key differences include:

- **Connection Handling**: Use proper async context managers for the SSE stream
- **Endpoint Discovery**: Extract the message URL from the SSE stream events
- **Session Management**: Use the server-provided session ID from the message URL
- **Request Processing**: Handle 202 Accepted responses and track requests by ID

```python
class HTTPSSETransport:
    """HTTP+SSE transport for MCP servers."""

    def __init__(self, url: str):
        """Initialize with server URL."""
        self.base_url = url
        self.sse_url = url if '/sse' in url else f"{url.rstrip('/')}/sse"
        self.message_url = None
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for SSE
        self.sse_connection = None
        self.connected = False
        self.pending_requests = {}  # Track requests by ID

    async def connect(self) -> bool:
        """Connect to the MCP server."""
        # Implementation from mcp_updated_transport.py
        # ...
```

### 2. Update MCPHandler Integration

Modify the `MCPHandler` class to work with the new transport implementation:

```python
class MCPHandler:
    # ... existing code ...

    async def connect_mcp_server(self, name: str, url: str, credentials: Dict[str, Any]) -> bool:
        """Connect to an MCP server and initialize session."""
        try:
            # Create transport
            transport = HTTPSSETransport(url)

            # Connect to server
            connected = await transport.connect()
            if not connected:
                logger.error(f"Failed to connect to MCP server: {name}")
                return False

            # Store the transport
            self.active_connections[name] = transport

            # Start listening for SSE events in a background task
            asyncio.create_task(self._listen_for_events(name, transport))

            return True

        except Exception as e:
            logger.error(f"Error connecting to MCP server {name}: {str(e)}")
            return False

    async def _listen_for_events(self, server_name: str, transport: HTTPSSETransport) -> None:
        """Listen for SSE events from the MCP server."""
        try:
            async for event in transport.listen_for_events():
                # Process events (responses to our requests)
                await self._process_sse_event(server_name, event)
        except Exception as e:
            logger.error(f"Error listening for events from {server_name}: {str(e)}")

    async def _process_sse_event(self, server_name: str, event: str) -> None:
        """Process an SSE event from the MCP server."""
        # Parse the event and match to pending requests
        # ...
```

### 3. Implement Request Tracking

To handle the asynchronous nature of MCP servers, implement request tracking:

```python
async def send_request(self, server_name: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Send a request to an MCP server and wait for the response."""
    if server_name not in self.active_connections:
        raise ValueError(f"Not connected to MCP server: {server_name}")

    transport = self.active_connections[server_name]

    # Create a request ID
    request_id = str(uuid.uuid4())

    # Create a future to wait for the response
    response_future = asyncio.Future()
    self.pending_requests[request_id] = response_future

    # Create JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }

    # Send the request
    await transport.send_request(request)

    # Wait for the response with timeout
    try:
        return await asyncio.wait_for(response_future, timeout=30.0)
    except asyncio.TimeoutError:
        self.pending_requests.pop(request_id, None)
        raise TimeoutError(f"Request timed out: {method}")
```

### 4. Process SSE Events

Handle incoming SSE events to complete the request/response cycle:

```python
async def _process_sse_event(self, server_name: str, event: str) -> None:
    """Process an SSE event from the MCP server."""
    try:
        # Check if this is a data event
        if event.startswith("data: "):
            data_str = event[6:].strip()
            data = json.loads(data_str)

            # Check if this is a response to a request
            if "id" in data and data["id"] in self.pending_requests:
                # Get the future for this request
                future = self.pending_requests.pop(data["id"])

                # Set the result
                if not future.done():
                    future.set_result(data)
    except Exception as e:
        logger.error(f"Error processing SSE event: {str(e)}")
```

## Testing the Integration

After implementing these changes, test the integration with the following steps:

1. **Connection Test**: Verify that connecting to the MCP server works
2. **Ping Test**: Send a ping request and ensure you get a response
3. **Tool Call Test**: Test calling an actual tool function like `get_current_weather`
4. **Error Handling**: Test reconnection and error handling

## Common Issues and Solutions

1. **Timeout Errors**: If you encounter timeouts, increase the timeout value in the transport
2. **SSE Connection Issues**: Ensure you're using the correct headers for SSE connections
3. **Event Parsing**: Make sure you're properly parsing the SSE events to extract responses
4. **Session Handling**: The session ID is provided by the server, don't try to create your own

## Resources

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [SSE Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Reference Implementation](tests/mcp_updated_transport.py)
- [Progress Documentation](ideas/mcp-progress.md)
