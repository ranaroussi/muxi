# MUXI Framework MCP Handler PRD

## 1. Introduction

This PRD defines the requirements and design for the MCP (Model Context Protocol) handler component of the MUXI Framework. The MCP handler will enable MUXI agents to connect to and interact with MCP servers, providing access to specialized capabilities such as web search, file operations, or other tools without requiring direct implementation within MUXI itself.

### 1.1 Background

MCP is a standardized protocol that allows AI applications to:
- [x] Share contextual information with language models
- [x] Expose tools and capabilities to AI systems
- [x] Build composable integrations and workflows

The MUXI framework has transitioned from using internal tools to exclusively leveraging MCP servers for specialized capabilities, necessitating a robust MCP handler implementation.

## 2. Goals and Objectives

### 2.1 Primary Goals

- [x] Create a unified MCP handler in MUXI that can connect to various MCP servers regardless of transport method
- [x] Support current MCP server implementations (HTTP+SSE and command-line based)
- [ ] Design with forward compatibility for the upcoming Streamable HTTP transport
- [x] Provide a clean, consistent API that abstracts transport details from the agent implementation

### 2.2 Success Metrics

- [ ] Successful integration with at least 3 major MCP server types
- [ ] Minimal latency overhead (< 50ms added by handler layer)
- [x] Graceful handling of connection failures and reconnections
- [ ] 100% conformance with MCP specification

## 3. Current MCP Architecture

### 3.1 Transport Methods

MCP currently operates with two primary transport methods:

#### 3.1.1 HTTP+SSE Transport
- [x] Client → Server messages go through HTTP POST to `/message` endpoint
- [x] Server → Client messages go through Server-Sent Events (SSE) via `/sse` endpoint
- [ ] Requires maintaining long-lived connections
- [ ] Limited resumability support

#### 3.1.2 Command-line Based Transport
- [x] Servers are started via command-line (e.g., `npx -y @modelcontextprotocol/server-brave-search`)
- [ ] Communication typically happens via standard input/output or a local port
- [ ] Generally more suited for local development and testing

### 3.2 Protocol Details

- [x] Uses JSON-RPC 2.0 message format
- [x] Stateful connections between client and server
- [x] Server and client capability negotiation
- [x] Features include Resources, Prompts, and Tools

## 4. Future MCP Transport (Streamable HTTP)

A new "Streamable HTTP" transport is being developed (RFC in [PR #206](https://github.com/modelcontextprotocol/specification/pull/206)) that will replace the current HTTP+SSE approach:

### 4.1 Key Changes

- [ ] Removes the `/sse` endpoint
- [ ] All client → server messages go through the `/message` endpoint
- [ ] Server responses can be upgraded to SSE for streaming
- [ ] Servers can establish session IDs to maintain state
- [ ] Clients can initiate SSE streams with empty GET requests to `/message`
- [ ] Supports stateless server implementations

### 4.2 Benefits

- [ ] Enables stateless servers, eliminating the requirement for high availability long-lived connections
- [ ] Uses plain HTTP implementation, improving compatibility with middleware and infrastructure
- [ ] Provides a flexible upgrade path with SSE used only when needed
- [ ] Maintains backward compatibility with incremental evolution

## 5. MUXI MCP Handler Requirements

### 5.1 Functional Requirements

1. **Connection Management**
   - [x] Establish connections to MCP servers via HTTP+SSE
   - [ ] Support command-line based MCP servers
   - [ ] Prepare for Streamable HTTP when released
   - [x] Handle server session IDs and authentication
   - [x] Manage connection lifecycle (initialization, maintenance, termination)

2. **Message Handling**
   - [x] Implement JSON-RPC 2.0 client
   - [x] Support for all MCP message types
   - [x] Process server responses and notifications
   - [ ] Handle streaming responses appropriately

3. **Tool Execution**
   - [x] Register available tools from MCP servers
   - [x] Execute tool calls based on agent requests
   - [x] Process tool results and return to agent

4. **Error Handling**
   - [x] Graceful handling of connection failures
   - [x] Automatic reconnection with exponential backoff
   - [x] Clear error reporting to agent layer
   - [ ] Support for cancellation of in-progress operations

5. **Configuration**
   - [x] Flexible configuration options for different MCP server types
   - [x] Support for authentication credentials
   - [ ] Environment variable integration

### 5.2 Non-Functional Requirements

1. **Performance**
   - [ ] Minimal latency overhead
   - [x] Efficient message processing
   - [ ] Optimization for streaming responses

2. **Security**
   - [x] Secure handling of authentication credentials
   - [x] Proper validation of all server responses
   - [ ] Protection against potential vulnerabilities

3. **Reliability**
   - [x] Graceful degradation when servers are unavailable
   - [ ] Automatic recovery from temporary failures
   - [x] Proper logging for diagnostic purposes

4. **Extensibility**
   - [x] Modular design to support new transport methods
   - [x] Abstracted interfaces to simplify future updates
   - [x] Clean API boundaries

## 6. Implementation Details

### 6.1 MCP Handler Class Structure

```python
class MCPHandler:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.mcp_servers = {}  # Map of server_name -> server_config
        self.active_connections = {}  # Map of server_name -> connection
        self.session_ids = {}  # Map of server_name -> session_id

    async def connect_mcp_server(self, name: str, url: str, credentials: Dict[str, Any]) -> bool:
        """Connect to an MCP server and initialize session."""
        # Implementation

    async def disconnect_mcp_server(self, name: str) -> bool:
        """Gracefully disconnect from an MCP server."""
        # Implementation

    async def process_message(self, message: MCPMessage) -> MCPMessage:
        """Process an incoming message that may contain tool calls."""
        # Implementation

    async def _handle_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call on the appropriate MCP server."""
        # Implementation

    async def _create_session(self, server_name: str) -> str:
        """Create a new session with the MCP server."""
        # Implementation

    async def _resume_session(self, server_name: str, session_id: str) -> bool:
        """Attempt to resume an existing session."""
        # Implementation

    async def _end_session(self, server_name: str) -> bool:
        """Explicitly terminate a session."""
        # Implementation
```

### 6.2 Transport Implementations

#### 6.2.1 HTTP+SSE Transport

```python
class HTTPSSETransport:
    def __init__(self, url: str, credentials: Dict[str, Any]):
        self.url = url
        self.credentials = credentials
        self.sse_client = None

    async def connect(self) -> bool:
        """Establish connection to server."""
        # Implementation

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the server and get the response."""
        # Implementation

    async def start_sse_stream(self) -> bool:
        """Start SSE stream for server notifications."""
        # Implementation

    async def disconnect(self) -> bool:
        """Close all connections."""
        # Implementation
```

#### 6.2.2 CommandLine Transport

```python
class CommandLineTransport:
    def __init__(self, command: str, credentials: Dict[str, Any]):
        self.command = command
        self.credentials = credentials
        self.process = None

    async def connect(self) -> bool:
        """Start the server process."""
        # Implementation

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the server and get the response."""
        # Implementation

    async def disconnect(self) -> bool:
        """Terminate the server process."""
        # Implementation
```

#### 6.2.3 Streamable HTTP Transport

```python
class StreamableHTTPTransport:
    def __init__(self, url: str, credentials: Dict[str, Any]):
        self.url = url
        self.credentials = credentials
        self.session_id = None
        self.stream_client = None

    async def connect(self) -> bool:
        """Establish connection and get session ID."""
        # Implementation

    async def send_message(self, message: Dict[str, Any]) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Send a message to the server and get response (potentially streaming)."""
        # Implementation

    async def start_stream(self) -> bool:
        """Start a stream for server-initiated messages."""
        # Implementation

    async def end_session(self) -> bool:
        """Explicitly terminate the session."""
        # Implementation

    async def disconnect(self) -> bool:
        """Close all connections."""
        # Implementation
```

### 6.3 Transport Factory

```python
class MCPTransportFactory:
    @staticmethod
    async def create_transport(server_type: str, url_or_command: str, credentials: Dict[str, Any]) -> MCPTransport:
        """Create the appropriate transport based on server type."""
        if server_type == "http_sse":
            return HTTPSSETransport(url_or_command, credentials)
        elif server_type == "command_line":
            return CommandLineTransport(url_or_command, credentials)
        elif server_type == "streamable_http":
            return StreamableHTTPTransport(url_or_command, credentials)
        else:
            raise ValueError(f"Unsupported server type: {server_type}")
```

## 7. API Design

### 7.1 Agent-Facing API

```python
# Example agent method for connecting to an MCP server
async def connect_mcp_server(self, name: str, url: str, credentials: Dict[str, Any] = None) -> bool:
    """
    Connect to an MCP server.

    Args:
        name: A unique identifier for this MCP server
        url: The URL or command to start the MCP server
        credentials: Optional credentials for authentication

    Returns:
        bool: True if connection was successful
    """
    if self.mcp_handler is None:
        self.mcp_handler = MCPHandler(self.agent_id)

    return await self.mcp_handler.connect_mcp_server(name, url, credentials or {})

# Example agent method for handling messages with potential tool calls
async def process_message(self, message: str) -> MCPMessage:
    """
    Process a user message, potentially executing MCP tool calls.

    Args:
        message: The user's message

    Returns:
        MCPMessage: The response after processing
    """
    # Get LLM response
    llm_response = await self.model.chat([{"role": "user", "content": message}])

    # If the response contains tool calls, process them
    if "tool_calls" in llm_response:
        response = MCPMessage.from_dict(llm_response)
        return await self.mcp_handler.process_message(response)

    # If no tool calls, just return the response
    return MCPMessage(role="assistant", content=llm_response["content"])
```

### 7.2 Configuration API

```yaml
# Example YAML configuration for an agent with MCP servers
name: assistant
description: "General-purpose AI assistant with MCP capabilities."
system_message: You are a helpful AI assistant.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
mcp_servers:
- name: web_search
  type: http_sse  # or "command_line" or "streamable_http"
  url: http://localhost:5001
  credentials:
  - id: search_api_key
    param_name: api_key
    required: true
    env_fallback: SEARCH_API_KEY
- name: calculator
  type: command_line
  command: npx -y @modelcontextprotocol/server-calculator
  credentials: []
```

## 8. Security Considerations

### 8.1 Authentication

- [x] All MCP server connections should require authentication if specified
- [x] Authentication credentials should be securely stored
- [ ] Support for environment variable-based credential management
- [x] Authentication tokens included with every request as per MCP spec

### 8.2 Data Protection

- [x] Sensitive data should not be logged
- [x] Proper sanitization of inputs and outputs
- [x] Secure handling of session IDs

### 8.3 Server Validation

- [x] Validate server responses against expected schemas
- [x] Implement proper error handling for malformed responses
- [ ] Protect against server-side attacks

## 9. Testing Requirements

### 9.1 Unit Tests

- [x] Test each transport implementation independently
- [x] Mock server responses for predictable testing
- [x] Test error handling and edge cases

### 9.2 Integration Tests

- [ ] Test with actual MCP servers
- [ ] Verify end-to-end functionality
- [ ] Test session management and reconnection

### 9.3 Performance Tests

- [ ] Benchmark latency overhead
- [ ] Test under high load
- [ ] Evaluate streaming performance

## 10. Deployment and Scalability

### 10.1 Logging

- [x] Comprehensive logging for diagnostic purposes
- [x] Log all connection events and errors
- [ ] Configurable log levels

### 10.2 Monitoring

- [ ] Health checks for MCP server connections
- [ ] Performance metrics collection
- [ ] Error rate tracking

### 10.3 Scalability

- [x] Support for multiple concurrent MCP server connections
- [x] Efficient resource management
- [ ] Connection pooling when applicable

## 11. Future Considerations

### 11.1 WebSocket Support

While not currently part of the MCP specification, we should design the handler to potentially accommodate WebSocket transport in the future if it becomes part of the standard.

### 11.2 Multi-Modal Support

As MCP evolves to support image, audio, and other modalities, the handler should be extensible to these new capabilities.

### 11.3 Automatic Discovery

Future versions may include automatic discovery and registration of MCP servers.

## 12. Timeline and Priorities

### 12.1 Phase 1: Basic Implementation

- [x] Implement HTTP+SSE transport
- [x] Develop core MCPHandler class
- [x] Basic session management
- [x] Initial integration with Agent class

### 12.2 Phase 2: Command-Line Support

- [x] Implement CommandLineTransport
- [ ] Process management
- [ ] Integration with existing command-line MCP servers

### 12.3 Phase 3: Streamable HTTP Support

- [ ] Implement StreamableHTTPTransport
- [ ] Support for session management
- [ ] Handling of streaming responses

### 12.4 Phase 4: Testing and Refinement

- [x] Comprehensive testing
- [ ] Performance optimization
- [x] Documentation

## 13. Conclusion

The MCP Handler will provide MUXI agents with a standardized way to interact with external capabilities through MCP servers. By supporting both current transport methods and preparing for the upcoming Streamable HTTP transport, we ensure that MUXI remains compatible with the evolving MCP ecosystem. This implementation will enable a wide range of specialized capabilities without requiring direct implementation within the MUXI framework itself.
