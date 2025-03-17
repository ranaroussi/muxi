# MUXI Framework Architecture Evolution

This document outlines the evolution of the MUXI Framework architecture towards a more flexible, service-oriented approach while maintaining its simplicity and ease of use.

## Vision

The MUXI Framework is evolving to better support:

1. **Unified declarative configuration** for all components
2. **Everything-as-a-service** architecture
3. **Seamless local and remote operation**
4. **Flexible authentication mechanisms**
5. **Decoupled frontend clients**

This evolution preserves the current programmatic API while adding powerful capabilities for distributed deployment.

## Core Architecture Changes

### Current Architecture

```
┌───────────────┐      ┌───────────┐      ┌───────────┐
│  Application  │──────│  Agents   │──────│    LLM    │
└───────┬───────┘      └─────┬─────┘      └───────────┘
        │                    │
        │              ┌─────┴─────┐
        │              │  Memory   │
        │              └─────┬─────┘
┌───────┴───────┐      ┌─────┴─────┐
│  CLI/API/Web  │──────│   Tools   │
└───────────────┘      └───────────┘
```

### Target Architecture

```
┌───────────────┐
┤ Thin Clients  │
│ (CLI/Web/SDK) │
└───────┬───────┘
        │
        │ (API/SSE/WS)
        │
┌───────│─────────────────────────────────────────────┐
│       │      MUXI Server (Local/Remote)             │
│       │                                             │
│       │           ┌──────────────┐                  │
│       └─────────► │ Orchestrator │                  │
│                   └──────┬───────┘                  │
│                          │                          │
│                          ▼                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │  │
│  │ (from YAML) │  │ (from JSON) │  │ (from YAML) │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │         │
│         └────────┬───────┴────────┬───────┘         │
│                  │                │                 │
│           ┌──────┴──────┐  ┌──────┴──────┐          │
│           │ MCP Handler │  │   Memory    │          │
│           └──────┬──────┘  └─────────────┘          │
└──────────────────│──────────────────────────────────┘
                   │
                   │ (gRPC/HTTP)
                   ▼
┌─────────────────────────────────────────────────────┐
│              MCP Servers (via Command/SSE)          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Weather API │  │ Search Tool │  │ Custom Tool │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Packaging Strategy

To support the service-oriented architecture, the MUXI framework will be broken down into modular packages:

### Package Structure

```
muxi/
├── muxi-core/      # Core functionality and shared components
├── muxi-server/    # Server implementation
├── muxi-cli/       # Command-line interface
└── muxi-web/       # Web application
```

### Installation Options

```bash
# Full installation (all components)
pip install muxi

# Minimal CLI for working with remote servers only
pip install muxi-cli

# Standalone web app for connecting to remote servers only
pip install muxi-web
```

### Package Contents

1. **muxi-core**
   - Core abstractions and utilities
   - Shared models and schemas
   - Client-side connection management
   - No server dependencies

2. **muxi-server**
   - Complete server implementation
   - Agent management
   - Memory systems
   - LLM integrations
   - API and WebSocket server

3. **muxi-cli**
   - Command-line interface
   - Remote server connections
   - Minimal dependencies
   - Interactive mode

4. **muxi-web**
   - Web application frontend
   - Connection management UI
   - Chat interface
   - Agent configuration
   - Standalone HTML/JS/CSS assets

This modular approach allows users to install only what they need, reducing dependencies and streamlining deployments. It also enables independent evolution of the server and client components.

## Implementation Roadmap

### Phase 1: Core Architecture Refactoring

1. **Unified Server Component**
   - Refactor the application to separate local mode from server mode
   - Ensure programmatic API remains unchanged for backward compatibility
   - Add server authentication framework

2. **Authentication Implementation**
   - Implement flexible API key authentication
   - Support auto-generated keys with one-time display
   - Allow environment variable configuration
   - Add explicit auth configuration options

3. **Client-Server Model**
   - Implement client-side connector for remote servers
   - Create connection management utilities
   - Update facade to seamlessly handle local and remote operation
   - Ensure connection state persistence

### Phase 2: MCP Server Unification

1. **Unified Tool/MCP Server Approach**
   - Refactor tool system to be MCP server based
   - Create adapters for local Python tools to expose as MCP endpoints
   - Update tool registry to handle remote services
   - Implement service discovery

2. **Configuration Schema Updates**
   - Extend YAML/JSON schemas to support the new architecture
   - Create migration utilities for existing configurations
   - Document the new schema format

3. **Deployment Utilities**
   - Add utilities for spinning up MCP servers
   - Create containerization helpers
   - Implement basic service orchestration

### Phase 3: Client Applications

1. **CLI Updates**
   - Update CLI to support server connection
   - Add commands for managing remote servers
   - Implement connection profiles

2. **Web UI Evolution**
   - Convert web UI to standalone SPA
   - Add server connection screen
   - Implement connection state management
   - Create settings for managing multiple servers

3. **SDK Improvements**
   - Update Python SDK for remote operation
   - Create client libraries for other languages
   - Implement WebSocket clients

### Phase 4: Packaging and Distribution

1. **Package Modularization**
   - Restructure codebase for modular packaging
   - Define boundaries between packages
   - Create setup.py with optional dependencies

2. **Package Creation**
   - Implement muxi-core with minimal dependencies
   - Develop muxi-server with full server capabilities
   - Create standalone muxi-cli for remote connections
   - Build standalone muxi-web for browser-based access

3. **Distribution and Documentation**
   - Set up CI/CD for package publishing
   - Create package-specific documentation
   - Develop seamless upgrade paths

## Implementation Strategy and Timeline

### Step 1: Core Architecture (Sprint 1-2)
- Define separation of local and server modes
- Implement auth mechanisms
- Update the facade class to handle connections
- Begin restructuring for modular packaging

### Step 2: MCP Server Evolution (Sprint 3-4)
- Refactor tool system to MCP-based approach
- Update configuration schemas
- Create adapters for existing tools
- Complete core package separation

### Step 3: Client Updates (Sprint 5-6)
- Update CLI interface
- Modify web app for standalone use
- Update documentation
- Create standalone packages

### Step 4: Packaging and Release (Sprint 7-8)
- Finalize package structure
- Set up CI/CD for package publishing
- Create comprehensive tests
- Update examples
- Create migration guides
- Release initial package versions

## Communication Protocol

To optimize for both scalability and real-time streaming capabilities, the MUXI framework will implement a hybrid protocol approach:

### Standard HTTP with SSE Streaming

1. **Default Protocol**: Standard HTTP for all API requests
   - Simple request/response pattern for configuration, management, and non-streaming operations
   - RESTful API design for clear endpoint structure
   - Standard authentication via headers

2. **Streaming with Server-Sent Events (SSE)**
   - When a client sends a chat or generation request, an SSE connection is established
   - The server streams response tokens/chunks in real-time
   - Once the response is complete, the SSE connection automatically closes
   - No persistent connections between requests, improving scalability

3. **Protocol Flow**:

   ```
   Client                                Server
     |                                     |
     |------ HTTP Request (chat) --------->|
     |                                     |
     |<--- HTTP 200 + Content-Type: -------|
     |      text/event-stream              |
     |                                     |
     |<------- SSE chunk 1 ----------------|
     |<------- SSE chunk 2 ----------------|
     |<------- SSE chunk n ----------------|
     |<------- SSE completion signal ------|
     |                                     |
     |-------- Connection Closed --------->|
     |                                     |
   ```

4. **Fallback for Unsupported Clients**
   - For clients that don't support SSE (e.g., CLI in certain environments)
   - Option to use regular HTTP requests with complete responses
   - Parameter to request full response instead of streaming (`stream=false`)
   - Same API endpoints with different response handling

### WebSocket Support for Omni Capabilities

1. **Dual Protocol Support by Default**
   - MUXI servers will start with both HTTP and WebSocket support enabled by default
   - Same port used for both protocols with automatic protocol detection
   - Unified authentication mechanism across both protocols

2. **WebSocket Session Management**
   - Clients can establish persistent WebSocket connections for specific use cases:
     ```python
     # Open a WebSocket connection
     socket = app.open_socket()

     # Use the socket for real-time communication
     await socket.send_message("Hello")

     # Close the connection when done
     socket.close()
     ```

3. **Use Cases for WebSocket Connections**
   - Multi-modal streaming (audio/video input/output)
   - Real-time collaborative features
   - Bi-directional communication for voice conversations
   - Continuous interaction sessions

4. **WebSocket Protocol Flow**:
   ```
   Client                                Server
     |                                     |
     |------ WS Handshake ---------------->|
     |<----- WS Connection Established ----|
     |                                     |
     |------ Auth Message ---------------->|
     |<----- Auth Confirmed --------------|
     |                                     |
     |------ Binary Audio Chunks --------->|
     |<----- Text/Binary Responses --------|
     |                                     |
     |------ Close Connection ------------>|
     |                                     |
   ```

This hybrid approach provides the best of both worlds: SSE for efficient text streaming with automatic connection management and WebSockets for rich, bi-directional communications needed for Omni capabilities. The system will automatically select the most appropriate protocol based on the type of interaction.

## Authentication Implementation Details

### Server-Side Auth

```python
# In MUXI server initialization
def run(self,
        host="0.0.0.0",
        port=5050,
        api_key=None,
        auth_type="api_key",
        auth_disabled=False):
    """Start the MUXI server with authentication."""

    # Handle authentication setup
    if auth_disabled:
        warnings.warn("Running without authentication - NOT RECOMMENDED FOR PRODUCTION")
        self.auth_handler = None
    elif api_key:
        self.auth_handler = ApiKeyAuthHandler(api_key)
    else:
        # Auto-generate a secure key
        generated_key = generate_secure_key()
        self.auth_handler = ApiKeyAuthHandler(generated_key)
        print(f"Server running at http://{host}:{port}")
        print(f"API Key: {generated_key}")

    # Start the server
    self._start_server(host, port)
```

### Client-Side Auth

```python
# Connecting to a remote server
app = muxi(
    server_url="http://server-ip:5050",
    api_key="your_api_key"
)

# Or after initialization
app.connect(server_url="http://server-ip:5050", api_key="your_api_key")
```

### Authentication Flow with SSE

For streaming responses, authentication follows this flow:

1. **Initial Request Authentication**
   - Client includes authentication (API key in header or auth token)
   - Server validates credentials before establishing SSE connection
   - The same credentials used for regular HTTP requests apply to SSE

2. **Per-Request Authentication**
   - Each new chat/generation request requires authentication
   - No persistent authentication state between requests
   - Stateless design improves security and scalability

3. **Implementation**
   ```python
   # Client-side streaming request
   response = app.chat("Tell me a story", stream=True)

   # Internally this does:
   async with httpx.AsyncClient() as client:
       headers = {"Authorization": f"Bearer {api_key}"}
       # Make authenticated request with streaming enabled
       async with client.stream("POST", f"{server_url}/chat",
                                json={"message": "Tell me a story", "stream": True},
                                headers=headers) as response:
           # Process SSE stream
           async for chunk in response.aiter_text():
               # Handle SSE chunk
               yield process_sse_chunk(chunk)
   ```

### Web UI Implementation

The web application will include:

1. **Connection Screen**
   - Server URL input
   - API key input
   - "Connect" button
   - Option to save connection details

2. **Connection Management**
   - Store connection in local storage
   - Handle reconnection
   - Show connection status
   - Multiple connection profiles (optional)

## Usage Examples

### Local Usage (Unchanged)

```python
from src import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize
app = muxi()

# Add an agent from a configuration file
app.add_agent("my_assistant", "configs/assistant.yaml")

# Chat with a specific agent
response = app.chat("Hello, who are you?", agent_name="my_assistant")
print(response)

# Start the server mode (now with auth)
app.run()  # Auto-generates and displays API key
```

### Remote Usage (New)

```python
from src import muxi

# Connect to an existing MUXI server
app = muxi(
    server_url="http://server-ip:5050",
    api_key="sk_muxi_abc123"
)

# Use the same API
app.add_agent("remote_assistant", "configs/assistant.yaml")
response = app.chat("Hello, remote assistant!")
print(response)
```

### Streaming Response Example

```python
from src import muxi

# Connect to a MUXI server
app = muxi(server_url="http://server-ip:5050", api_key="sk_muxi_abc123")

# Non-streaming (default) - returns complete response
full_response = app.chat("Tell me a short story")
print(full_response)

# Streaming - yields chunks as they arrive via SSE
for chunk in app.chat("Tell me a short story", stream=True):
    print(chunk, end="", flush=True)

# Process streaming response programmatically
async def process_stream():
    async for chunk in app.achat("Tell me a short story", stream=True):
        # Do something with each chunk
        process_chunk(chunk)
```

### CLI Usage (Enhanced)

```bash
# Connect to a server
muxi connect --url http://server-ip:5050 --key sk_muxi_abc123

# Use server with the same commands
muxi list agents
muxi chat --agent weather_assistant

# Streaming support in CLI
muxi chat --agent weather_assistant --stream  # Shows progress in real-time
```

## Tasks Breakdown

1. **Server Architecture**
   - [ ] Create AuthHandler interface
   - [ ] Implement ApiKeyAuthHandler
   - [ ] Update server initialization in facade
   - [ ] Add connection management
   - [ ] Implement SSE streaming for chat responses

2. **Configuration**
   - [ ] Update agent schema to support new structure
   - [ ] Create server configuration schema
   - [ ] Implement connection profile storage

3. **MCP Server Unification**
   - [ ] Create adapters for Python tools
   - [ ] Implement service registry
   - [ ] Update orchestrator to handle remote tools

4. **Client Applications**
   - [ ] Update CLI for remote connections
   - [ ] Implement streaming support in clients
   - [ ] Convert web UI to standalone client
   - [ ] Add connection management UI

5. **Packaging and Distribution**
   - [ ] Restructure codebase for modular packaging
   - [ ] Create setup.py with optional dependencies
   - [ ] Implement pyproject.toml structure
   - [ ] Set up CI/CD for package publishing
   - [ ] Create standalone CLI package
   - [ ] Create standalone web package
   - [ ] Update installation documentation

6. **Testing and Documentation**
   - [ ] Create tests for auth mechanisms
   - [ ] Test streaming responses
   - [ ] Test remote connections
   - [ ] Update documentation with examples
   - [ ] Create package-specific documentation

## Conclusion

This evolution maintains the simplicity and ease of use of the MUXI Framework while expanding its capabilities for distributed, service-oriented architectures. The implementation strategy ensures backward compatibility while adding powerful new features for scaling and distribution.

By following this roadmap, we will transition MUXI to a more flexible and powerful framework while maintaining its intuitive API and developer-friendly approach. The use of SSE for streaming responses provides an optimal balance between real-time experiences and server scalability, following industry best practices established by services like OpenAI.
