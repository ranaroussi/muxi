# MCP Client-Server Communication Explained


## Client / Server Communication

The communication between an MCP (Model Context Protocol) client and server is primarily **asynchronous**, though it incorporates both synchronous and asynchronous elements depending on the specific interaction.

### Current Transport: HTTP+SSE

In the current implementation, MCP uses a hybrid approach:

1. **Client → Server**: Synchronous HTTP POST requests to the `/message` endpoint
   - Client sends JSON-RPC 2.0 messages in the request body
   - Server responds synchronously to these messages
2. **Server → Client**: Asynchronous communication via Server-Sent Events (SSE)
   - Client establishes a persistent SSE connection via the `/sse` endpoint
   - Server can push notifications, requests, or updates to the client at any time
   - This creates a long-lived, one-way communication channel from server to client

This hybrid approach allows for bi-directional communication where:

- Clients can make requests and receive immediate responses
- Servers can independently push messages to clients without a specific request

### Upcoming "Streamable HTTP" Transport

The proposed new transport method (in [PR #206](https://github.com/modelcontextprotocol/specification/pull/206)) simplifies this by:

1. Using a single `/message` endpoint for all communication
2. Allowing any client request to be upgraded to an SSE stream
3. Supporting both stateless and stateful operation through server-managed session IDs

This still maintains the asynchronous nature of MCP while improving flexibility.

### Key Aspects of MCP Communication

1. **Stateful Sessions**: MCP maintains state across requests, making it inherently asynchronous in nature
2. **Tool Execution**: When a client requests a tool execution, the operation runs asynchronously:
   - Client makes request
   - Server executes tool (potentially long-running)
   - Server sends progress notifications asynchronously
   - Server sends final result when complete
3. **Event-Driven**: The protocol is fundamentally event-driven, with both sides able to initiate communication
4. **JSON-RPC**: Uses JSON-RPC 2.0 message format which supports both request-response patterns and notifications

This asynchronous design is critical for AI agents that need to perform potentially long-running operations while maintaining interactive responsiveness with users.


## Client / Command-Line Server Communication

When an MCP client interacts with a command-line based MCP server (like `npx -y @modelcontextprotocol/server-brave-search`), the communication model differs from HTTP+SSE but maintains the same asynchronous principles:

### Command-line MCP Server Communication Flow

1. **Initialization**:
   - The MCP client spawns the server process using the command-line instruction
   - The process starts and initializes the MCP server implementation
2. **Bidirectional Communication**:
   - Communication happens through standard input/output (stdin/stdout) of the spawned process
   - The client writes JSON-RPC messages to the process's stdin
   - The server reads from stdin, processes the requests, and writes responses to stdout
   - The client reads the server's responses from the process's stdout
3. **Asynchronous Messaging**:
   - The server can still send notifications to the client asynchronously
   - Long-running operations work the same way as in HTTP+SSE transport
   - The client needs to continuously monitor stdout for server messages
4. **Session Management**:
   - The session is naturally maintained as long as the process is running
   - If the process terminates, the session ends
   - Reconnection requires respawning the process

This approach is particularly useful for local development, testing, and scenarios where running a separate HTTP server would be overkill. It maintains the same JSON-RPC message structure and protocol semantics while using a different transport mechanism.

Both communication models (HTTP+SSE and command-line) support the asynchronous nature of MCP, just through different underlying transport mechanisms.

