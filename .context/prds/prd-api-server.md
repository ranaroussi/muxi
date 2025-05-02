# MUXI API PRD

> ### REST API, SSE, MCP, and WebRTC Integration

> [!NOTE]
> We should place no regards to backwards competability!

## Overview

This document outlines the implementation of the MUXI API, a comprehensive communication layer that unifies multiple protocols into a single server implementation. The server will provide REST API endpoints, Server-Sent Events (SSE) for streaming, MCP (Model Context Protocol) support, and WebRTC for rich media exchange.

## Problem Statement

As MUXI Framework evolves, there's a need for a unified communication layer that can:

1. Serve traditional REST API requests for agent/system management
2. Stream responses in real-time using SSE without waiting for complete responses
3. Support the MCP protocol for integration with MCP-compatible hosts and tools
4. Enable rich media exchange (audio, video) through WebRTC
5. Provide a consistent, secure interface for all these communication methods

Currently, these capabilities exist as separate conceptual components, leading to potential code duplication, inconsistent authentication, and integration challenges.

## Objectives

1. Create a unified MUXI API that combines REST, SSE, MCP, and WebRTC in one process
2. Logically separate endpoints into "user/interface" and "developer/management" categories
3. Implement a consistent authentication mechanism across all protocols
4. Ensure high performance for concurrent connections and streaming responses
5. Provide comprehensive, self-documenting API specification
6. Expose MCP capabilities from connected agents and servers

## Feature Requirements

### Core MUXI API Components

1. **REST API Layer**: Standard HTTP endpoints for agent and system management
   - User/Interface endpoints for agent interaction
   - Developer endpoints for system configuration and management

2. **SSE Streaming**: Real-time streaming responses using Server-Sent Events
   - Stream agent responses without waiting for completion
   - Support incremental updates during processing
   - Provide logging and tracing events in real-time

3. **MCP Integration**: Support for the Model Context Protocol
   - Expose agent capabilities as MCP tools
   - Integrate with MCP-compatible hosts
   - Pass through MCP tool invocations to agents

4. **WebRTC Signaling**: Support for WebRTC multimedia exchange
   - Signaling server for WebRTC connection establishment
   - Media handling for multi-modal agent interactions

### Technical Specifications

1. **Transport Layers**:
   - HTTP/HTTPS for REST endpoints
   - SSE for streaming responses
   - WebSocket/SSE for MCP protocol support
   - WebRTC for audio/video exchange

2. **Authentication**:
   - API key-based authentication leveraging keys set at the MUXI Core level
   - Two key types with explicit access level specification:
     - User/Interface key for client access
     - Administrative key for system management
   - Validation of API keys on all endpoints
   - Access level implemented via decorators or dependency injection
   - Consistent auth mechanism across all protocols

3. **Performance**:
   - Asynchronous request handling
   - Connection pooling for database and external services
   - Efficient resource management for concurrent connections

4. **Documentation**:
   - OpenAPI/Swagger specification
   - Interactive API documentation
   - Automatic endpoint discovery
   - Explicit operation IDs for MCP tool names

## Implementation Approach

The MUXI API will be implemented as a unified module that internally contains logical separations for each protocol while sharing common resources like authentication, logging, and connection management. The implementation will not maintain backward compatibility with existing code, allowing for a clean, optimized design.

**Note:** The new implementation will completely replace the existing API code with no regard for backward compatibility. This allows for a clean, optimized design that follows best practices without legacy constraints.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         MUXI API                            │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │
│  │    REST API   │  │      SSE      │  │      MCP      │    │
│  │   Endpoints   │  │   Streaming   │  │     Server    │    │
│  └───────┬───────┘  └───────┬───────┘  └────────┬──────┘    │
│          │                  │                   │           │
│  ┌───────▼──────────────────▼───────────────────▼──────┐    │
│  │                Shared Core Components               │    │
│  │  (Authentication, Routing, Logging, Rate Limiting)  │    │
│  └───────────────────────────┬─────────────────────────┘    │
│                              │                              │
│  ┌───────────────────────────▼─────────────────────────┐    │
│  │                WebRTC Signaling & Media             │    │
│  └───────────────────────────┬─────────────────────────┘    │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                         MUXI Core                           │
│                              ↓                              │
│                      ┌────────────────┐                     │
│                      │  Orchestrator  │                     │
│                      └───────┬────────┘                     │
│             ┌────────────────┼────────────────┐             │
│      ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐      │
│      │   Agent 1   │  │   Agent 2   │  │   Agent N   │      │
│      └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Authentication System

The MUXI API will use a dual-key authentication system based on the keys set at the MUXI Core level:

1. **User/Interface Key**: Limited to chat interactions and user-facing features
   - Used for client applications, chat interfaces
   - Restricted from management operations
   - Format: `sk_muxi_user_YOUR_KEY` (when auto-generated)

2. **Administrative Key**: Full access to all endpoints and operations
   - Used for system management, agent configuration
   - Required for sensitive operations
   - Format: `sk_muxi_admin_YOUR_KEY` (when auto-generated)

The MUXI API will validate each incoming request against these keys and enforce the appropriate access level. Access levels will be specified using decorators:

```python
@app.get("/endpoint", operation_id="get_some_resource")
@requires_user_key  # or @requires_admin_key
async def get_resource():
    # Implementation
```

At initialization, the MUXI Core (Orchestrator) and declarative API (muxi) will accept API keys as parameters:

```python
# For the Orchestrator approach
orchestrator = Orchestrator(user_api_key="your_user_key", admin_api_key="your_admin_key")

# For the declarative approach
app = muxi(user_api_key="your_user_key", admin_api_key="your_admin_key")
```

Upon running, the MUXI API will display the following information:

```
╭──────────────────────────────────────╮
│  ███╗   ███╗ ██╗   ██╗ ██╗  ██╗ ██╗  │
│  ████╗ ████║ ██║   ██║ ╚██╗██╔╝ ██║  │
│  ██╔████╔██║ ██║   ██║  ╚███╔╝  ██║  │
│  ██║╚██╔╝██║ ██║   ██║  ██╔██╗  ██║  │
│  ██║ ╚═╝ ██║ ╚██████╔╝ ██╔╝ ██╗ ██║  │
│  ╚═╝     ╚═╝  ╚═════╝  ╚═╝  ╚═╝ ╚═╝  │
│───────────────┬──────────────────────│
│  * MUXI Core  │  Version: 1.2.0      │
│───────────────┴──────────────────────│
│                                      │
│  Running on:                         │
│  http://0.0.0.0:8000                 │
│                                      │
╰──────────────────────────────────────╯
```

If keys are not provided during initialization, temporary keys will be auto-generated and the startup message will include the generated API keys:

```
╭──────────────────────────────────────╮
│  ███╗   ███╗ ██╗   ██╗ ██╗  ██╗ ██╗  │
│  ████╗ ████║ ██║   ██║ ╚██╗██╔╝ ██║  │
│  ██╔████╔██║ ██║   ██║  ╚███╔╝  ██║  │
│  ██║╚██╔╝██║ ██║   ██║  ██╔██╗  ██║  │
│  ██║ ╚═╝ ██║ ╚██████╔╝ ██╔╝ ██╗ ██║  │
│  ╚═╝     ╚═╝  ╚═════╝  ╚═╝  ╚═╝ ╚═╝  │
│───────────────┬──────────────────────│
│  * MUXI Core  │  Version: 1.2.0      │
│───────────────┴──────────────────────│
│                                      │
│  Running on:                         │
│  http://0.0.0.0:8000                 │
│                                      │
╰─────────────┬────────────────────────╯
              │
╭─────────────┴────────────────────────────────────────────────────────╮
│                                                                      │
│  API Keys (auto-generated):                                          │
│                                                                      │
│   — User:  sk_muxi_user_xxxxxxxxxxxxxxxxxxxxx                        │
│   — Admin: sk_muxi_admin_xxxxxxxxxxxxxxxxxxxxx                       │
│                                                                      │
│  ⚡ Auto-generating API keys should only be used during development.  │
│  We recommend to explicitly set your own API keys.                   │
│                                                                      │
╰──────────────────────────────────────────────────────────────────────╯
```

API keys are stored in memory during runtime, with no persistent storage or complex key management infrastructure. This places responsibility for key management on developers, which is appropriate for most use cases. For production environments, developers should set their own keys rather than relying on auto-generated ones.

NOTES:

1. All endpoints must have at least `@requires_user_key` applied. If no decorator is specified, `@requires_user_key` should be applied automatically.
2. Admin keys grant access to all endpoints, including those marked with `@requires_user_key`.

### Endpoint Categories

The MUXI API will logically separate endpoints into two categories:

#### User/Interface Endpoints

Accessible with User/Interface key or Administrative key:

- `/api/v1/chat` - Send messages to the orchestrator
- `/api/v1/chat/stream` - Stream chat with the orchestrator (SSE)
- `/api/v1/agents/{agent_id}/chat` - Send messages to a specific agent
- `/api/v1/agents/{agent_id}/chat/stream` - Stream chat with a specific agent (SSE)

#### Developer/Management Endpoints

Requires Administrative key:

- Agent management (CRUD operations)
- Memory operations
- System configuration
- MCP server management
- Knowledge management
- User context management
- System statistics and monitoring

### Protocol Implementation

#### REST API

Standard RESTful interface following OpenAPI specifications:

- JSON request/response format
- Standard HTTP methods (GET, POST, PATCH, DELETE)
- Consistent error handling
- Rate limiting and throttling
- Resource-based URL structure
- Explicit operation IDs for MCP tool names

#### Server-Sent Events (SSE)

Streaming implementation for real-time updates:

- Event-based format for incremental content delivery
- Support for connection recovery
- Automatic reconnection handling
- Event types for different message components (content, tool calls)
- Logging and tracing events for monitoring

#### MCP Protocol

Model Context Protocol support:

- Tool definition and discovery
- Request/response message format
- Support for streaming tool responses
- Integration with agent capabilities
- Operation IDs matching FastAPI endpoint operation_id parameters

#### WebRTC

Media exchange capabilities for multi-modal interactions:

- Signaling server for connection establishment
- STUN/TURN server integration
- Media track handling
- Support for audio/video/screen sharing
- Integration with MCP protocol for multi-modal tool invocations

## Detailed API Specifications

### REST API Endpoints

The REST API will follow the specifications outlined in the API specification document, with clear separation between user/interface and developer endpoints, and explicit operation IDs for MCP tool names.

#### User/Interface Endpoints

```
# Chat with orchestrator
POST /api/v1/chat
POST /api/v1/chat/stream (SSE)

# Chat with specific agent
POST /api/v1/agents/{agent_id}/chat
POST /api/v1/agents/{agent_id}/chat/stream (SSE)

# Get conversation history
GET /api/v1/conversations/{user_id}
```

#### Developer/Management Endpoints

```
# Agent management
GET /api/v1/agents
POST /api/v1/agents
GET /api/v1/agents/{agent_id}
PATCH /api/v1/agents/{agent_id}
DELETE /api/v1/agents/{agent_id}
POST /api/v1/agents/import

# Memory operations
GET /api/v1/agents/{agent_id}/memory/search
DELETE /api/v1/agents/{agent_id}/memory

# User and context management
GET /api/v1/users
POST /api/v1/users/{user_id}/context
GET /api/v1/users/{user_id}/context
PATCH /api/v1/users/{user_id}/context
DELETE /api/v1/users/{user_id}/context

# MCP server management
GET /api/v1/agents/{agent_id}/mcp_servers
POST /api/v1/agents/{agent_id}/mcp_servers
DELETE /api/v1/agents/{agent_id}/mcp_servers/{server_name}
GET /api/v1/agents/{agent_id}/mcp_servers/{server_name}

# Knowledge management
GET /api/v1/agents/{agent_id}/knowledge
POST /api/v1/agents/{agent_id}/knowledge
DELETE /api/v1/agents/{agent_id}/knowledge/{knowledge_id}
GET /api/v1/agents/{agent_id}/knowledge/search

# System information
GET /api/v1/system/status
GET /api/v1/system/usage
```

### MCP Protocol Endpoints

```
# MCP streaming endpoint
GET /api/v1/mcp/stream (SSE)

# Tool discovery
GET /api/v1/mcp/tools

# Bridge endpoint for non-SSE clients
POST /api/v1/mcp/request
```

### WebRTC Endpoints

```
# WebRTC signaling
POST /api/v1/rtc/offer
POST /api/v1/rtc/answer
POST /api/v1/rtc/ice-candidate

# Media session management
POST /api/v1/rtc/sessions
GET /api/v1/rtc/sessions/{session_id}
DELETE /api/v1/rtc/sessions/{session_id}
```

### Logging and Tracing Endpoints

```
# Real-time trace log streaming
GET /api/v1/logs/trace/stream (SSE)

# Real-time application log streaming
GET /api/v1/logs/app/stream (SSE)

# Filtered trace log retrieval
GET /api/v1/logs/trace

# Trace log search
POST /api/v1/logs/trace/search
```

## Example Flows

### Agent Chat with Streaming Response

1. Client connects to `/api/v1/agents/assistant/chat/stream`
2. Client sends API key in header `Authorization: Bearer sk_muxi_user_YOUR_KEY`
3. Server validates API key and permission level
4. Client sends message: "Tell me about renewable energy"
5. Server initiates SSE stream
6. Server sends incremental response chunks as they're generated
7. Server includes tool call events if agent uses tools
8. Client receives and renders incremental updates
9. Server sends completion event when response is finished

### MCP Tool Invocation

1. MCP-compatible host connects to `/api/v1/mcp/stream`
2. Host provides API key in header `Authorization: Bearer sk_muxi_user_YOUR_KEY`
3. Server validates API key and permission level
4. Host requests available tools
5. Server returns tool definitions with names matching operation_ids
6. Host invokes tool with parameters
7. Server routes tool request to appropriate agent
8. Agent processes request and returns result
9. Server streams result back to host

### WebRTC Multi-modal Exchange

1. Client initiates WebRTC session via `/api/v1/rtc/sessions`
2. Client provides API key in header `Authorization: Bearer sk_muxi_user_YOUR_KEY`
3. Server validates API key and permission level
4. Client and server exchange signaling via dedicated endpoints
5. Media connection is established
6. Client sends audio/video stream
7. Server processes media in real-time
8. Agent responds via text or media stream
9. Session is terminated when interaction completes

### Log/Trace Monitoring

1. Admin connects to `/api/v1/logs/trace/stream`
2. Admin provides API key in header `Authorization: Bearer sk_muxi_admin_YOUR_KEY`
3. Server validates API key and admin permissions
4. Server initiates SSE stream
5. Server sends trace events in real-time as they occur
6. Admin receives structured trace data
7. Admin can filter or search traces
8. Connection remains open for continuous monitoring

## Implementation Plan

### Phase 1: Core REST API & SSE Integration

1. Implement REST API framework with FastAPI
2. Add authentication system using MUXI Core-level API keys
3. Implement core agent and chat endpoints
4. Add SSE streaming capabilities
5. Deploy with proper CORS and security headers

### Phase 2: MCP Protocol Integration

1. Integrate FastAPI_MCP library for MCP support
2. Implement tool definition discovery
3. Connect MCP tools to agent capabilities
4. Add MCP request routing
5. Test with common MCP-compatible hosts (Claude, Cursor)

### Phase 3: WebRTC Implementation

1. Add WebRTC signaling server capabilities
2. Implement media session management
3. Connect media processing to agent inputs
4. Support multi-modal agent responses
5. Test with audio/video communication

### Phase 4: Logging and Tracing Integration

1. Implement trace event generation
2. Add SSE endpoints for real-time trace streaming
3. Implement trace search and filtering
4. Connect with core MUXI tracing system
5. Add trace visualization utilities

### Phase 5: Performance Optimization & Documentation

1. Optimize for concurrent connections
2. Implement proper connection pooling
3. Add comprehensive logging and monitoring
4. Create OpenAPI documentation
5. Develop interactive API playground

## Authentication Implementation

The MUXI API will leverage the API keys set at the MUXI Core level. These keys will be:

1. Cryptographically secure random strings
2. When auto-generated, prefixed with `sk_muxi_user_` or `sk_muxi_admin_` to indicate scope
3. Validated on every request across all protocols
4. Accessible to the MUXI API through the MUXI orchestrator

### API Key Header Format

```
Authorization: Bearer <USER_KEY>
```

or

```
Authorization: Bearer <ADMIN_KEY>
```

### API Key Validation

The MUXI API will validate each request by:

1. Extracting the API key from the Authorization header
2. Checking the key prefix to determine the access level (user or admin)
3. Validating the key against the keys managed by the MUXI Core
4. Enforcing endpoint access restrictions based on the key type

### Access Level Decoration

Every endpoint will explicitly specify the required access level using either decorator pattern or dependency injection:

```python
# Decorator method
@app.post("/api/v1/chat", operation_id="chat_with_orchestrator")
@app.verify_user_key  # or @app.verify_admin_key
async def chat():
    # Implementation
```

**NOTES:**

1. `verify_admin_key` should automatically be applied to all endpoints that do not have `verify_user_key` applied.
2. admins should be able to access all endpoints, so they should not have any endpoints that do not have `verify_admin_key` applied.

## Security Considerations

1. **Transport Security**:
   - Require HTTPS in production
   - Implement proper CORS configuration
   - Add security headers (CSP, HSTS, etc.)

2. **Authentication & Authorization**:
   - Validate API keys on every request
   - Implement scope-based authorization
   - Rate limit authentication attempts

3. **Input Validation**:
   - Validate all request parameters
   - Sanitize user inputs
   - Implement request size limits

4. **Rate Limiting**:
   - Per-key rate limits
   - Graduated response (warn, then block)
   - Configurable limits per endpoint

5. **Logging & Monitoring**:
   - Audit logging for security events
   - Performance monitoring
   - Anomaly detection

## Monitoring and Observability

The MUXI API will include comprehensive monitoring and observability features:

1. **Request Logging**:
   - Structured logs for all requests
   - Performance metrics (timing, size)
   - Error tracking

2. **Health Checks**:
   - Internal status endpoint
   - Component health reporting
   - Dependency status

3. **Metrics**:
   - Request count by endpoint
   - Response times
   - Error rates
   - Connection counts

4. **Tracing**:
   - Request tracing across components
   - Correlation IDs
   - Span collection for performance analysis
   - Real-time trace streaming via SSE

## Deployment Considerations

### Initialization and Configuration

The MUXI API must be initialized with configuration parameters that define its operational environment:

1. **MUXI Core Connection**:
   - Configurable URI for the MUXI Core (defaults to `localhost:3000`)
   - Allows for distributed installation where MUXI API and MUXI Core run on different hosts
   - Connection parameters (timeout, retry policy, etc.)
   - TLS/SSL certificate configuration for secure communication

2. **Server Configuration**:
   - Host and port bindings
   - SSL/TLS certificate paths
   - Worker process count
   - Connection limits and timeouts
   - Maximum request size
   - CORS configuration

3. **Environment-specific Settings**:
   - Development vs. production mode
   - Debug logging toggle
   - Performance profiling options

### Production Deployment Best Practices

For production deployments, the following best practices are recommended:

1. **Reverse Proxy Integration**:
   - Deploy behind Caddy, Traefik, Nginx, or other reverse proxy
   - Offload TLS termination to the reverse proxy
   - Configure appropriate headers (X-Forwarded-For, etc.)
   - Implement path-based routing if needed
   - Enable HTTP/2 for improved performance

2. **Load Balancing**:
   - Utilize multiple MUXI API instances behind a load balancer
   - Configure sticky sessions for WebRTC and SSE connections
   - Implement health checks for automatic instance replacement
   - Use Redis or similar for session state sharing

3. **Security Enhancement**:
   - Rate limiting at reverse proxy level
   - Web Application Firewall (WAF) integration
   - DDoS protection
   - IP filtering for admin endpoints
   - Regular security audits

4. **Monitoring Integration**:
   - Prometheus metrics exposure
   - Grafana dashboard templates
   - Log aggregation (ELK, Datadog, etc.)
   - Distributed tracing with OpenTelemetry

5. **High Availability**:
   - Multi-region deployment
   - Automatic failover
   - Backup and recovery procedures
   - Blue-green deployment support

A comprehensive deployment guide will be provided in the documentation site, including specific configuration examples for Caddy, Traefik, and other popular reverse proxies.

## Future Extensions

1. **API Key Management**:
   - Key rotation
   - Expiration policies
   - Usage analytics

2. **Advanced Authentication**:
   - OAuth 2.0 support
   - OIDC integration
   - SAML for enterprise

3. **Enhanced WebRTC**:
   - Screen sharing
   - Recording capabilities
   - Group sessions

4. **Federation**:
   - Inter-server communication
   - Federated agent discovery
   - Cross-instance authentication

## Success Metrics

1. Request throughput and latency
2. Concurrent connection capacity
3. Stream stability and reconnection rates
4. Tool invocation success rate
5. WebRTC connection stability
6. Developer adoption (measured by API usage)

## Dependencies

1. FastAPI for REST API implementation
2. SSE implementation (either FastAPI extension or custom)
3. FastAPI_MCP for MCP protocol support
4. WebRTC libraries for signaling and media handling
5. Authentication and security libraries
6. Monitoring and logging infrastructure

## Conclusion

The unified MUXI API will provide a comprehensive communication layer for the MUXI Framework, combining REST API, SSE streaming, MCP protocol support, and WebRTC capabilities in a single, cohesive implementation. This approach reduces code duplication, ensures consistent authentication and security, and simplifies integration for developers and users. By leveraging FastAPI's capabilities and explicitly specifying operation IDs for MCP tool names, the MUXI API will provide a clean, modern, and developer-friendly interface to the MUXI Framework.
