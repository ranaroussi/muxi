# MCP Handler Development Progress

## Current Implementation Status

- **Basic MCPHandler**: MUXI has an initial MCPHandler class that handles:
  - Message processing and context management
  - Basic tool registration and handling
  - Simple system message management

- **Basic Agent Integration**: Agent class has:
  - Methods to connect to MCP servers (`connect_mcp_server`)
  - Storage of MCP server details
  - Basic HTTP implementation for server calls

- **Missing Functionality**:
  - The current implementation treats MCP servers as tools
  - No support for different transport methods (HTTP+SSE, command-line)
  - No session management or connection state tracking
  - Lacks proper JSON-RPC 2.0 client implementation
  - No support for streaming or asynchronous responses
  - Limited error handling and no reconnection logic
  - No abstraction layer for transport methods

## Development Requirements

### Core Components to Develop

1. **Complete MCPHandler Implementation**
   - [ ] Implement full `MCPHandler` class structure
   - [ ] Add robust session management
   - [ ] Support dynamic server registration
   - [ ] Implement comprehensive error handling

2. **Transport Layer**
   - [ ] Create transport abstraction layer
   - [ ] Implement `HTTPSSETransport` class fully
   - [ ] Implement `CommandLineTransport` class
   - [ ] Prepare for future `StreamableHTTPTransport`
   - [ ] Create `MCPTransportFactory` implementation

3. **Error Handling & Resilience**
   - [ ] Add reconnection with exponential backoff
   - [ ] Implement proper error propagation
   - [ ] Add support for canceling operations
   - [ ] Improve logging and diagnostics

4. **Testing & Validation**
   - [ ] Create unit tests for each transport type
   - [ ] Implement integration tests with real MCP servers
   - [ ] Add performance benchmarks
   - [ ] Test reconnection and error scenarios

5. **Documentation**
   - [ ] Update API documentation
   - [ ] Create examples for each transport type
   - [ ] Document configuration options

## Development Resources Needed

### External MCP Servers for Testing

> **Note**: MUXI is only responsible for communicating with MCP servers, not creating or running them.

For development and testing, we need access to:

1. **HTTP+SSE MCP Servers**
   - MCP servers that expose HTTP endpoints with Server-Sent Events `https://router.mcp.so/sse/4ertmsm8erwh60`
   - Example: Custom HTTP servers that implement the MCP specification
   - Example: Self-hosted server instances with HTTP+SSE transport

2. **Command-line MCP Servers**
   - Brave Search MCP server: `npx -y @modelcontextprotocol/server-brave-search`
   - Calculator MCP server: `npx -y @modelcontextprotocol/server-calculator`
   - Other npx-based MCP servers
   - Examples that use stdin/stdout communication

3. **Streamable HTTP Servers** (for future)
   - Monitor the MCP specification PR #206 for final implementation details
   - Will need example servers when available

### Development Tools

- Mock MCP servers for unit testing
- HTTP client library with SSE support (aiohttp or httpx)
- Process management library for command-line servers (asyncio.subprocess)
- JSON-RPC 2.0 client implementation

## MCP Server Examples

### Running Brave Search MCP Server (Command-line)

```bash
# Install and run the Brave Search MCP server
npx -y @modelcontextprotocol/server-brave-search
```

This will start the Brave Search MCP server as a command-line process. You can connect to it using:

```python
await agent.connect_mcp_server(
    name="search",
    url_or_command="npx -y @modelcontextprotocol/server-brave-search",
    transport_type="command_line",
    credentials={"api_key": "YOUR_BRAVE_API_KEY"}
)
```

### Running Calculator MCP Server (Command-line)

```bash
# Install and run the Calculator MCP server
npx -y @modelcontextprotocol/server-calculator
```

This runs the calculator server and waits for input on stdin. You would connect to it using:

```python
await agent.connect_mcp_server(
    name="calculator",
    url_or_command="npx -y @modelcontextprotocol/server-calculator",
    transport_type="command_line"
)
```

### HTTP+SSE Server Example (Custom HTTP Server)

For HTTP+SSE servers that expose REST endpoints and Server-Sent Events, you would connect as follows:

```python
await agent.connect_mcp_server(
    name="http_server",
    url="http://localhost:3000",
    transport_type="http_sse",
    credentials={"api_key": "YOUR_API_KEY"}
)
```

### Testing the Connection

After connecting to an MCP server, you can test the connection by making a basic request:

```python
# Command-line example (Brave Search)
message = {
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
        "query": "current weather in San Francisco"
    },
    "id": "1"
}

# Send message to MCP server
client = agent.mcp_handler.active_connections["search"]
response = await client.send_message(message)
print(response)
```

This should return search results based on the query.

## Official MCP Python SDK

We've discovered there's an official Python SDK for Model Context Protocol (MCP) available at [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk).

### Using the Official SDK vs. Custom Implementation

Given this information, we should consider two approaches:

1. **Use the Official SDK**: Integrate the official Python SDK into the MUXI framework, which would give us immediate access to a well-maintained, spec-compliant implementation.

2. **Develop Custom Implementation**: Continue with our planned custom implementation, which gives us more control but requires more development effort.

### Recommendation

**Recommended approach**: Use the official Python SDK as a dependency in our implementation for these reasons:

1. **Spec Compliance**: The official SDK will stay up-to-date with the latest MCP specification
2. **Community Support**: Benefit from bug fixes and features from the broader community
3. **Development Speed**: Faster implementation of MCP functionality
4. **Future Compatibility**: Easier to adapt to new transport methods like Streamable HTTP

This means modifying our implementation plan to focus on:

1. Creating a wrapper around the official SDK that fits into our existing architecture
2. Adding the MCP transport abstraction as originally planned, but delegating the actual protocol implementation to the SDK
3. Ensuring our Agent class properly integrates with this approach

### Implementation Steps with Official SDK

```bash
# Add the official SDK as a dependency
pip install modelcontextprotocol
```

Then modify our implementation to use the SDK:

```python
from modelcontextprotocol.client import MCPClient
from modelcontextprotocol.transport import HTTPSSETransport, CommandLineTransport

class MCPHandler:
    """
    Handles communication with MCP servers using the Model Context Protocol.
    """

    def __init__(self, agent_id: str):
        """
        Initialize an MCP handler.

        Args:
            agent_id: The ID of the agent using this handler
        """
        self.agent_id = agent_id
        self.mcp_servers = {}  # Map of server_name -> server_config
        self.active_connections = {}  # Map of server_name -> client
        self.session_ids = {}  # Map of server_name -> session_id
        self.context = MCPContext()

    async def connect_mcp_server(
        self,
        name: str,
        url_or_command: str,
        transport_type: str = "http_sse",
        credentials: Dict[str, Any] = None
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: A unique identifier for this MCP server
            url_or_command: The URL or command to start the MCP server
            transport_type: The type of transport to use
            credentials: Optional credentials for authentication

        Returns:
            bool: True if connection was successful
        """
        try:
            # Create appropriate transport using the SDK
            if transport_type == "http_sse":
                transport = HTTPSSETransport(url_or_command)
            elif transport_type == "command_line":
                transport = CommandLineTransport(url_or_command)
            else:
                raise ValueError(f"Unsupported transport type: {transport_type}")

            # Create MCP client with transport
            client = MCPClient(transport=transport)

            # Store the connection
            self.active_connections[name] = client

            # Store the configuration
            self.mcp_servers[name] = {
                "url_or_command": url_or_command,
                "transport_type": transport_type,
                "credentials": credentials or {}
            }

            # Connect and initialize
            await client.connect()

            # Add credentials if provided
            if credentials:
                await client.set_credentials(credentials)

            logger.info(f"Successfully connected to MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {str(e)}")
            return False

## Implementation Timeline

### Phase 1: Core Implementation (2-3 weeks)
- Complete HTTP+SSE transport
- Implement basic command-line transport
- Create core handler structure
- Initial testing framework

### Phase 2: Robustness (1-2 weeks)
- Error handling improvements
- Reconnection logic
- Security enhancements

### Phase 3: Future Compatibility (1-2 weeks)
- Prepare for Streamable HTTP
- Additional transport options
- Performance optimizations

### Phase 4: Documentation & Finalization (1 week)
- Complete documentation
- Final testing
- Release preparation

## Next Steps: Immediate Implementation Plan

### 1. Create Transport Abstraction

First, we'll create an abstract base class for MCP transports:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, AsyncIterator

class MCPTransport(ABC):
    """Base class for MCP transport implementations."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to MCP server."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from MCP server."""
        pass

    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to the MCP server and get the response.

        For non-streaming responses, returns a dictionary.
        For streaming responses, returns an async iterator of dictionaries.
        """
        pass

    @abstractmethod
    async def create_session(self) -> str:
        """Create a new session with the server, returns session ID."""
        pass

    @abstractmethod
    async def resume_session(self, session_id: str) -> bool:
        """Attempt to resume an existing session."""
        pass

    @abstractmethod
    async def end_session(self, session_id: str) -> bool:
        """Explicitly terminate a session."""
        pass
```

### 2. Create HTTP+SSE Transport Implementation

Next, implement the HTTP+SSE transport:

```python
import aiohttp
import asyncio
import json
import uuid
from typing import Any, Dict, Optional, AsyncIterator

class HTTPSSETransport(MCPTransport):
    """Implementation of MCP transport using HTTP+SSE."""

    def __init__(self, url: str, credentials: Dict[str, Any]):
        self.url = url.rstrip('/')  # Remove trailing slash if present
        self.credentials = credentials
        self.session_id = None
        self.sse_client = None
        self.message_queue = asyncio.Queue()
        self.sse_task = None

    async def connect(self) -> bool:
        """Establish connection to server."""
        try:
            # Initialize HTTP session
            self.http_session = aiohttp.ClientSession()

            # Start SSE connection
            success = await self._start_sse_stream()
            if success:
                self.session_id = await self.create_session()
                return bool(self.session_id)
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            return False

    async def disconnect(self) -> bool:
        """Close all connections."""
        try:
            if self.sse_task:
                self.sse_task.cancel()
                self.sse_task = None

            if self.session_id:
                await self.end_session(self.session_id)
                self.session_id = None

            if self.http_session:
                await self.http_session.close()
                self.http_session = None

            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {str(e)}")
            return False

    async def _start_sse_stream(self) -> bool:
        """Start SSE stream for server notifications."""
        try:
            # Connect to SSE endpoint
            sse_response = await self.http_session.get(f"{self.url}/sse")

            if sse_response.status != 200:
                logger.error(f"Failed to connect to SSE stream: {sse_response.status}")
                return False

            # Start background task to process SSE events
            self.sse_task = asyncio.create_task(self._process_sse_events(sse_response))
            return True
        except Exception as e:
            logger.error(f"Error starting SSE stream: {str(e)}")
            return False

    async def _process_sse_events(self, response: aiohttp.ClientResponse) -> None:
        """Process events from the SSE stream."""
        async for line in response.content:
            line = line.decode('utf-8').strip()

            # Skip empty lines
            if not line:
                continue

            # Handle SSE field
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                try:
                    message = json.loads(data)
                    await self.message_queue.put(message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in SSE event: {data}")

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the server and get the response."""
        if not self.http_session:
            raise RuntimeError("Not connected to MCP server")

        # Add session ID if available
        if self.session_id:
            message.setdefault("params", {})["session_id"] = self.session_id

        # Add credentials if needed
        if self.credentials:
            message.setdefault("params", {}).update(self.credentials)

        try:
            async with self.http_session.post(
                f"{self.url}/message",
                json=message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"MCP server error: {error_text}")
                    return {"error": f"Server error: {response.status}"}

                return await response.json()
        except Exception as e:
            logger.error(f"Error sending message to MCP server: {str(e)}")
            return {"error": f"Communication error: {str(e)}"}

    async def create_session(self) -> str:
        """Create a new session with the server."""
        message = {
            "jsonrpc": "2.0",
            "method": "mcp.create_session",
            "params": self.credentials or {},
            "id": str(uuid.uuid4())
        }

        response = await self.send_message(message)
        if "result" in response and "session_id" in response["result"]:
            return response["result"]["session_id"]
        return ""

    async def resume_session(self, session_id: str) -> bool:
        """Attempt to resume an existing session."""
        message = {
            "jsonrpc": "2.0",
            "method": "mcp.resume_session",
            "params": {
                "session_id": session_id,
                **(self.credentials or {})
            },
            "id": str(uuid.uuid4())
        }

        response = await self.send_message(message)
        return "result" in response and response["result"].get("success", False)

    async def end_session(self, session_id: str) -> bool:
        """Explicitly terminate a session."""
        message = {
            "jsonrpc": "2.0",
            "method": "mcp.end_session",
            "params": {
                "session_id": session_id,
                **(self.credentials or {})
            },
            "id": str(uuid.uuid4())
        }

        response = await self.send_message(message)
        return "result" in response and response["result"].get("success", False)
```

### 3. Create the Transport Factory

Then implement the factory class for creating appropriate transports:

```python
class MCPTransportFactory:
    """Factory for creating MCP transports."""

    @staticmethod
    async def create_transport(
        transport_type: str,
        url_or_command: str,
        credentials: Dict[str, Any] = None
    ) -> MCPTransport:
        """
        Create an appropriate MCP transport.

        Args:
            transport_type: The type of transport to create ("http_sse",
                "command_line", or "streamable_http")
            url_or_command: The URL or command to use
            credentials: Optional credentials for authentication

        Returns:
            An initialized MCPTransport instance

        Raises:
            ValueError: If the transport type is not supported
        """
        if transport_type == "http_sse":
            transport = HTTPSSETransport(url_or_command, credentials or {})
        elif transport_type == "command_line":
            # Will implement this in the next phase
            raise NotImplementedError("Command-line transport not yet implemented")
        elif transport_type == "streamable_http":
            # Will implement this in a future phase
            raise NotImplementedError("Streamable HTTP transport not yet implemented")
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

        # Try to connect
        success = await transport.connect()
        if not success:
            raise ConnectionError(f"Failed to connect to MCP server with {transport_type}")

        return transport
```

### 4. Update MCPHandler Implementation

Finally, we'll update the MCPHandler to use these transports:

```python
class MCPHandler:
    """
    Handles communication with MCP servers using the Model Context Protocol.
    """

    def __init__(self, agent_id: str):
        """
        Initialize an MCP handler.

        Args:
            agent_id: The ID of the agent using this handler
        """
        self.agent_id = agent_id
        self.mcp_servers = {}  # Map of server_name -> server_config
        self.active_connections = {}  # Map of server_name -> client
        self.session_ids = {}  # Map of server_name -> session_id
        self.context = MCPContext()

    async def connect_mcp_server(
        self,
        name: str,
        url_or_command: str,
        transport_type: str = "http_sse",
        credentials: Dict[str, Any] = None
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: A unique identifier for this MCP server
            url_or_command: The URL or command to start the MCP server
            transport_type: The type of transport to use
            credentials: Optional credentials for authentication

        Returns:
            bool: True if connection was successful
        """
        try:
            # Create appropriate transport using the SDK
            if transport_type == "http_sse":
                transport = HTTPSSETransport(url_or_command)
            elif transport_type == "command_line":
                transport = CommandLineTransport(url_or_command)
            else:
                raise ValueError(f"Unsupported transport type: {transport_type}")

            # Create MCP client with transport
            client = MCPClient(transport=transport)

            # Store the connection
            self.active_connections[name] = client

            # Store the configuration
            self.mcp_servers[name] = {
                "url_or_command": url_or_command,
                "transport_type": transport_type,
                "credentials": credentials or {}
            }

            # Connect and initialize
            await client.connect()

            # Add credentials if provided
            if credentials:
                await client.set_credentials(credentials)

            logger.info(f"Successfully connected to MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {str(e)}")
            return False

    async def disconnect_mcp_server(self, name: str) -> bool:
        """
        Gracefully disconnect from an MCP server.

        Args:
            name: The name of the MCP server

        Returns:
            bool: True if disconnection was successful
        """
        if name not in self.active_connections:
            return False

        try:
            client = self.active_connections[name]
            success = await client.disconnect()

            if success:
                del self.active_connections[name]
                if name in self.session_ids:
                    del self.session_ids[name]

                return True
            return False
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {name}: {str(e)}")
            return False
```

### 5. Update Unit Tests

Create tests for the transport abstraction and HTTP+SSE implementation.

## Test Implementation Plan

We need to create comprehensive tests for the new transport layer. Here's a suggested structure:

```python
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
import asyncio

from muxi.core.mcp import MCPTransport, HTTPSSETransport, MCPTransportFactory


class TestMCPTransport(unittest.TestCase):
    """Test cases for the MCPTransport base class."""

    def test_abstract_class(self):
        """Test that MCPTransport is an abstract class that can't be instantiated."""
        with self.assertRaises(TypeError):
            MCPTransport()


class TestHTTPSSETransport(unittest.IsolatedAsyncioTestCase):
    """Test cases for the HTTPSSETransport class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Mock HTTP session
        self.mock_session = MagicMock()
        self.mock_session.post = AsyncMock()
        self.mock_session.get = AsyncMock()
        self.mock_session.close = AsyncMock()

        # Mock response for session creation
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "jsonrpc": "2.0",
            "result": {"session_id": "test-session-123"},
            "id": "1"
        })
        self.mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock SSE response
        mock_sse_response = MagicMock()
        mock_sse_response.status = 200
        mock_sse_response.content = AsyncMock()
        mock_sse_response.content.__aiter__.return_value = [
            b'data: {"jsonrpc":"2.0","method":"notification","params":{}}\n\n'
        ]
        self.mock_session.get.return_value = mock_sse_response

        # Create transport with mocked session
        with patch('aiohttp.ClientSession', return_value=self.mock_session):
            self.transport = HTTPSSETransport("http://test-server.com",
                                             {"api_key": "test-key"})

    async def test_connect(self):
        """Test connecting to the server."""
        with patch('aiohttp.ClientSession', return_value=self.mock_session):
            result = await self.transport.connect()
            self.assertTrue(result)
            self.assertEqual(self.transport.session_id, "test-session-123")

    async def test_disconnect(self):
        """Test disconnecting from the server."""
        # Setup successful connection first
        with patch('aiohttp.ClientSession', return_value=self.mock_session):
            await self.transport.connect()

            # Now test disconnect
            self.mock_session.post.reset_mock()
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "jsonrpc": "2.0",
                "result": {"success": True},
                "id": "1"
            })
            self.mock_session.post.return_value.__aenter__.return_value = mock_response

            result = await self.transport.disconnect()
            self.assertTrue(result)
            self.mock_session.close.assert_called_once()

    async def test_send_message(self):
        """Test sending a message to the server."""
        # Setup successful connection first
        with patch('aiohttp.ClientSession', return_value=self.mock_session):
            await self.transport.connect()

            # Now test sending a message
            self.mock_session.post.reset_mock()
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "jsonrpc": "2.0",
                "result": {"value": "test-result"},
                "id": "1"
            })
            self.mock_session.post.return_value.__aenter__.return_value = mock_response

            message = {
                "jsonrpc": "2.0",
                "method": "test.method",
                "params": {"test": "value"},
                "id": "1"
            }

            result = await self.transport.send_message(message)
            self.assertEqual(result["result"]["value"], "test-result")

            # Verify session ID was added
            call_args = self.mock_session.post.call_args
            self.assertIn("json", call_args[1])
            sent_json = call_args[1]["json"]
            self.assertIn("params", sent_json)
            self.assertEqual(sent_json["params"]["session_id"], "test-session-123")

    async def test_session_management(self):
        """Test session creation, resumption, and termination."""
        with patch('aiohttp.ClientSession', return_value=self.mock_session):
            # Test create_session
            session_id = await self.transport.create_session()
            self.assertEqual(session_id, "test-session-123")

            # Test resume_session
            self.mock_session.post.reset_mock()
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "jsonrpc": "2.0",
                "result": {"success": True},
                "id": "1"
            })
            self.mock_session.post.return_value.__aenter__.return_value = mock_response

            result = await self.transport.resume_session("test-session-123")
            self.assertTrue(result)

            # Test end_session
            self.mock_session.post.reset_mock()
            result = await self.transport.end_session("test-session-123")
            self.assertTrue(result)


class TestMCPTransportFactory(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MCPTransportFactory class."""

    async def test_create_http_sse_transport(self):
        """Test creating an HTTP+SSE transport."""
        with patch('muxi.core.mcp.HTTPSSETransport') as mock_transport_class:
            # Setup mock transport
            mock_transport = MagicMock()
            mock_transport.connect = AsyncMock(return_value=True)
            mock_transport_class.return_value = mock_transport

            # Create transport
            transport = await MCPTransportFactory.create_transport(
                "http_sse", "http://test-server.com", {"api_key": "test-key"}
            )

            # Verify transport was created and connected
            mock_transport_class.assert_called_once_with(
                "http://test-server.com", {"api_key": "test-key"}
            )
            mock_transport.connect.assert_called_once()
            self.assertEqual(transport, mock_transport)

    async def test_unsupported_transport(self):
        """Test creating an unsupported transport type."""
        with self.assertRaises(ValueError):
            await MCPTransportFactory.create_transport(
                "unsupported", "http://test-server.com", {}
            )

    async def test_connection_failure(self):
        """Test handling a connection failure."""
        with patch('muxi.core.mcp.HTTPSSETransport') as mock_transport_class:
            # Setup mock transport that fails to connect
            mock_transport = MagicMock()
            mock_transport.connect = AsyncMock(return_value=False)
            mock_transport_class.return_value = mock_transport

            # Attempt to create transport
            with self.assertRaises(ConnectionError):
                await MCPTransportFactory.create_transport(
                    "http_sse", "http://test-server.com", {}
                )
```

## Conclusion and Next Steps

After researching the MCP specification, current MUXI implementation, and available tools, we've determined that the best approach for implementing the MCP handler in MUXI is to leverage the official Python SDK while creating a wrapper around it that fits our architecture.

### Summary of Findings

1. The current MCP handler in MUXI is treating MCP servers as tools, which doesn't align with the MCP specification
2. The Model Context Protocol has a well-maintained official Python SDK
3. The protocol supports multiple transport methods (HTTP+SSE, command-line, and soon Streamable HTTP)
4. Using the official SDK will ensure we stay compatible with the evolving specification

### Immediate Next Steps

1. **Add the SDK to Dependencies**:
   - Update `requirements.txt` to include `modelcontextprotocol`
   - Run tests to ensure compatibility with existing codebase

2. **Create Wrapper Implementation**:
   - Update `mcp.py` to use the SDK's client and transport classes
   - Ensure backward compatibility with existing code
   - Implement proper error handling and reconnection logic

3. **Update Agent Class**:
   - Modify `connect_mcp_server` to utilize the new implementation
   - Update `process_message` to handle MCP tool calls appropriately
   - Add support for different transport types

4. **Documentation**:
   - Create/update documentation on MCP server integration
   - Provide examples for using different transport methods

### Pull Request Checklist

When creating the initial pull request for this work, ensure it includes:

- [ ] Updated requirements.txt with the SDK
- [ ] Basic implementation of the MCPHandler wrapper class
- [ ] Unit tests for the new implementation
- [ ] Documentation updates

This approach will allow us to leverage the community-maintained SDK while preserving our existing architecture, and should significantly reduce the development time needed to support all transport types and keep up with the evolving MCP specification.
