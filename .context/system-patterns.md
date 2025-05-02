# MUXI Framework System Patterns

This document outlines the core system architecture, design patterns, and component relationships within the MUXI Framework.

## System Architecture

The MUXI Framework follows a modular architecture with several key components:

### High-Level Component Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                      MUXI Framework Components                     │
├───────────────┬───────────────┬───────────────┬────────────────────┤
│   MUXI Core   │    MUXI API   │   MUXI CLI    │   MUXI Web UI      │
│ (Orchestrator,│  (REST, SSE,  │ (Command-line │  (React-based user │
│ Agents, Memory│   MCP, WebRTC)│  interface)   │  interface)        │
└───────┬───────┴───────┬───────┴───────┬───────┴────────┬───────────┘
        │               │               │                │
        ▼               ▼               ▼                ▼
┌────────────────────────────────────────────────────────────────────┐
│                     Shared Libraries & Utilities                   │
├───────────────┬───────────────┬───────────────┬────────────────────┤
│  Vector DBs   │   Language    │  Knowledge    │    Observability   │
│ & Embeddings  │    Models     │  Integration  │    & Telemetry     │
└───────────────┴───────────────┴───────────────┴────────────────────┘
```

### Component Relationships

1. **MUXI Core**: The central orchestration layer for agent management, memory, and core functionality
   - Manages agent lifecycle, configuration, and state
   - Handles memory operations (short-term, long-term, vector storage)
   - Provides knowledge integration and retrieval
   - Manages tool execution and connectivity

2. **MUXI API**: Communication interface between clients and the MUXI Core
   - Exposes REST API endpoints for management and interaction
   - Provides Server-Sent Events (SSE) for streaming responses
   - Implements Model Context Protocol (MCP) for specialized clients
   - Offers WebRTC signaling for peer-to-peer connections

3. **MUXI CLI**: Command-line interface for interacting with MUXI API
   - Provides scriptable access to all MUXI features
   - Supports profile-based configuration management
   - Enables both human-friendly and machine-parsable outputs

4. **MUXI Web UI**: Browser-based interface for interacting with MUXI
   - Provides visual management of agents and configuration
   - Offers chat interface for agent interaction
   - Visualizes memory and knowledge connections

## Key Design Patterns

### Core Design Patterns

1. **Modular Component Architecture**
   - Components are designed with clear boundaries and interfaces
   - Each component can be deployed and scaled independently
   - Interface contracts ensure consistent behavior across components

2. **API-First Design**
   - All functionality is exposed through well-defined APIs
   - Internal components communicate through standardized interfaces
   - External integrations use the same APIs as built-in components

3. **Configuration-Driven Behavior**
   - Components are configurable through environment variables and config files
   - Different deployment scenarios can be achieved through configuration
   - Sensible defaults with progressive customization options

### Communication Patterns

1. **Unified Protocol Support**
   - MUXI API provides multiple protocol options (REST, SSE, MCP, WebRTC)
   - Consistent authentication and authorization across protocols
   - Protocol selection based on client needs and use case

2. **Streaming-First Approach**
   - Streaming responses preferred for real-time user experience
   - Server-sent events (SSE) for incremental content delivery
   - WebSocket/WebRTC for bidirectional communication

3. **Asynchronous Processing**
   - Non-blocking I/O for request handling
   - Background processing for long-running operations
   - Webhook support for completion notifications

### Deployment Patterns

1. **Flexible Deployment Options**
   - Single-machine deployment for development and small installations
   - Network-distributed deployment for scalability and separation of concerns
   - Cross-network deployment for enterprise and secure environments

2. **Component Independence**
   - MUXI Core can run independently for headless operation
   - MUXI API connects to MUXI Core via configurable URI
   - MUXI CLI and Web UI connect to MUXI API via configurable endpoints

3. **Containerization Support**
   - Docker images for all components
   - Docker Compose for development and simple deployments
   - Kubernetes support for production orchestration

## Key Technical Decisions

### 1. Modular Package Structure

The codebase is organized into modular packages for better separation of concerns:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, MCP interface
│   ├── server/        # REST API and WebSocket server
│   ├── cli/           # Command-line interface
│   ├── web/           # Web user interface
│   └── muxi/          # Meta-package that integrates all components
└── tests/             # Test suite for all components
```

This structure allows components to be developed, tested, and deployed independently.

### 2. Hybrid Communication Protocol

The framework implements a hybrid protocol approach:
- **HTTP**: Standard API requests for configuration and management
- **Server-Sent Events (SSE)**: Streaming responses token-by-token
- **WebSockets**: Multi-modal capabilities with bi-directional communication

### 3. Configuration-Driven Development

The framework emphasizes configuration over code, allowing users to define agents and their capabilities through YAML or JSON files, with centralized memory configuration at the orchestrator level.

### 4. LLM Provider Abstraction

The framework abstracts LLM providers behind a common interface, making it easy to switch between different models or providers.

### 5. MCP Integration Strategy

The framework uses a centralized approach for MCP integration through the MCPService:
- **Centralized Service**: Single point of service for all MCP server interactions
- **Transport Abstraction**: Multiple transport methods supported:
  - HTTP+SSE transport for web-based MCP servers
  - Command-line transport for local executable servers
- **Thread-safe Operations**: Locks for concurrent access to MCP servers
- **Unified Error Handling**: Consistent error handling across all MCP interactions
- **Configurable Timeouts**: Timeout configuration at orchestrator, agent, or per-request level

### 6. Memory Architecture

The memory system is centralized at the orchestrator level:
- **Buffer Memory**: Short-term memory for immediate context (using FAISS for vector similarity)
- **Long-Term Memory**: Persistent storage using PostgreSQL with pgvector or SQLite with sqlite-vec
- **Memobase**: Memory partitioning system for multi-user support
- **Shared Access**: All agents access memory through the orchestrator
- **Unified Configuration**: Memory is configured in a single place at initialization

## Design Patterns in Use

### 1. Singleton Pattern

Used for creating single instances of services that should be shared across the application:
- **MCPService**: Singleton service for managing all MCP server connections, ensuring consistent state across all agents

### 2. Factory Pattern

Used for creating implementations of various interfaces:
- **TransportFactory**: Creates the appropriate MCP transport implementation
- **MemoryFactory**: Creates memory systems based on configuration

```python
# Example of factory pattern for MCP transports
class TransportFactory:
    @staticmethod
    def create_transport(transport_type, **kwargs):
        if transport_type == "http":
            return HTTPSSETransport(**kwargs)
        elif transport_type == "command":
            return CommandLineTransport(**kwargs)
        else:
            raise ValueError(f"Unknown transport type: {transport_type}")
```

### 3. Strategy Pattern

Used to encapsulate different algorithms behind a common interface:
- **LLM Provider Strategies**: Different implementation for OpenAI, Anthropic, etc.
- **Memory Storage Strategies**: Different backends for memory storage (PostgreSQL, SQLite)

```python
# Example of strategy pattern for LLM providers
class OpenAIModel(BaseModel):
    def generate(self, messages, **kwargs):
        # OpenAI-specific implementation
        pass

class AnthropicModel(BaseModel):
    def generate(self, messages, **kwargs):
        # Anthropic-specific implementation
        pass
```

### 4. Observer Pattern

Used for event handling:
- **Message Processing Pipeline**: Components observe and react to message events
- **Connection State Changes**: Components react to MCP server connection events

### 5. Facade Pattern

The main `muxi` class provides a simplified facade to the complex underlying system:

```python
# Example of facade pattern
class muxi:
    def __init__(self, buffer_memory=None, long_term_memory=None, **kwargs):
        # Create memory systems
        _buffer_memory = self._create_buffer_memory(buffer_memory)
        _long_term_memory = self._create_long_term_memory(long_term_memory)

        # Initialize orchestrator with memory
        self.orchestrator = Orchestrator(
            buffer_memory=_buffer_memory,
            long_term_memory=_long_term_memory
        )
        # Initialize other components

    async def add_agent(self, name, path=None, **kwargs):
        # Simplified interface to agent creation
        pass

    async def chat(self, message, agent_name=None, user_id=None, **kwargs):
        # Simplified interface to chat functionality
        pass
```

### 6. Repository Pattern

Used for data access abstractions:
- **Memory Repository**: Abstracts database operations for memory storage
- **Knowledge Repository**: Manages knowledge data access

### 7. Command Pattern

Used for operation encapsulation:
- **MCP Tool Calls**: Encapsulates tool execution into command objects
- **API Operations**: API actions are encapsulated as commands

## Component Relationships

### Orchestrator Relationships

- **Owns** multiple Agent instances
- **Routes** messages to appropriate Agents
- **Manages** global configuration
- **Exposes** a public API for client interaction
- **Owns and manages** all memory systems (Buffer and Long-Term Memory)
- **Provides** memory access methods to agents
- **Maintains** centralized memory management
- **Handles** multi-user memory partitioning through Memobase

### Agent Relationships

- **Uses** a Model for LLM interaction
- **Accesses** memory through the Orchestrator
- **Does not own** memory systems directly
- **Connects to** MCP Servers via MCP Service
- **Maintains** a Knowledge Base for domain knowledge
- **Stores** reference to the parent Orchestrator for memory access

### Memory System Relationships

- **Exclusively owned by** the Orchestrator, not individual Agents
- **Initialized during** Orchestrator construction
- **Configured via** the Muxi facade constructor or directly in Orchestrator
- **Buffer Memory provides** immediate context to all Agents via the Orchestrator
- **Long-Term Memory stores** historical context accessed through the Orchestrator
- **Shared efficiently** across all Agents managed by the Orchestrator
- **Partitioned by** user_id for multi-user support via Memobase
- **Memory operations** (add, search, clear) are exposed via Orchestrator methods
- **Agent-specific data** maintained through metadata filtering (using agent_id)

### MCP Service Relationships

- **Connects to** external MCP Servers
- **Translates** Agent requests into MCP protocol
- **Manages** connections and reconnections
- **Handles** asynchronous responses

### Communication Interface Relationships

- **REST API serves** synchronous requests
- **SSE provides** streaming responses
- **WebSockets enable** bidirectional communication
- **CLI offers** terminal-based interaction

## Data Flow

1. **Message Reception**: Client sends message through an interface
2. **Orchestration**: Message is routed to the appropriate agent
3. **Context Enhancement**: Orchestrator's memory systems provide relevant context
4. **Processing**: Agent processes message with LLM and tools
5. **Tool Usage**: External tools are invoked via MCP if needed
6. **Response Generation**: Agent generates a response
7. **Memory Update**: Conversation is stored in orchestrator's memory systems
8. **Response Delivery**: Response is returned to the client

This architecture allows for flexibility, extensibility, and maintainability while providing a powerful foundation for AI agent development.
