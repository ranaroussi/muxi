# MUXI Framework System Patterns

## System Architecture

The MUXI Framework follows a service-oriented architecture with clear separation of concerns and modular components. The high-level architecture is as follows:

```
┌───────────────────┐
│      Clients      │
│   (CLI/Web/SDK)   │
└─────────┬─────────┘
          │
          │ (API/SSE/WS)
          │
┌─────────│───────────────────────────────────────────┐
│         │    MUXI Server (Local/Remote)             │
│         │                                           │
│         │        ┌───────────────┐                  │
│         └───────>│  Orchestrator │                  │
│                  └───────┬───────┘                  │
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│         ▼                ▼                ▼         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    ┌───────────┐
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │-------│ Knowledge │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │    └───────────┘
│         ↓                ↓                ↓         │
│         └────────┬───────┴────────┬───────┘         │
│                  ↓                :                 │
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
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Components

1. **Orchestrator**: Central component that manages agents and routes messages
2. **Agent**: Core entity that processes messages with specific capabilities
3. **Memory System**: Stores conversation history and contextual information
4. **MCP Handler**: Manages communications with external MCP servers
5. **Knowledge Base**: Stores and retrieves domain-specific knowledge
6. **Communication Interfaces**: HTTP API, SSE, WebSockets for interaction

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

The framework emphasizes configuration over code, allowing users to define agents and their capabilities through YAML or JSON files.

### 4. LLM Provider Abstraction

The framework abstracts LLM providers behind a common interface, making it easy to switch between different models or providers.

### 5. MCP Integration Strategy

External tool integration follows the Model Context Protocol (MCP) standard, with support for:
- HTTP+SSE transport for web-based MCP servers
- Command-line transport for local executable servers

### 6. Memory Architecture

The memory system is split into:
- **Buffer Memory**: Short-term memory for immediate context (using FAISS for vector similarity)
- **Long-Term Memory**: Persistent storage using PostgreSQL with pgvector or SQLite with sqlite-vec
- **User Partitioning**: Memory segregation for multi-user support

## Design Patterns in Use

### 1. Factory Pattern

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

### 2. Strategy Pattern

Used to encapsulate different algorithms behind a common interface:
- **LLM Provider Strategies**: Different implementation for OpenAI, Anthropic, etc.
- **Memory Storage Strategies**: Different backends for memory storage

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

### 3. Observer Pattern

Used for event handling:
- **Message Processing Pipeline**: Components observe and react to message events
- **Connection State Changes**: Components react to MCP server connection events

### 4. Facade Pattern

The main `muxi` class provides a simplified facade to the complex underlying system:

```python
# Example of facade pattern
class muxi:
    def __init__(self, **kwargs):
        self.orchestrator = Orchestrator()
        # Initialize other components

    async def add_agent(self, agent_id, config_path=None, **kwargs):
        # Simplified interface to agent creation
        pass

    async def chat(self, message, agent_name=None, user_id=None, **kwargs):
        # Simplified interface to chat functionality
        pass
```

### 5. Repository Pattern

Used for data access abstractions:
- **Memory Repository**: Abstracts database operations for memory storage
- **Knowledge Repository**: Manages knowledge data access

### 6. Command Pattern

Used for operation encapsulation:
- **MCP Tool Calls**: Encapsulates tool execution into command objects
- **API Operations**: API actions are encapsulated as commands

## Component Relationships

### Orchestrator Relationships

- **Owns** multiple Agent instances
- **Routes** messages to appropriate Agents
- **Manages** global configuration
- **Exposes** a public API for client interaction
- **Owns and manages** memory systems (Buffer and Long-Term Memory)
- **Provides** memory access methods to agents
- **Maintains** centralized memory management
- **Handles** multi-user memory partitioning

### Agent Relationships

- **Uses** a Model for LLM interaction
- **Accesses** memory through the Orchestrator
- **Does not own** memory systems directly
- **Connects to** MCP Servers via MCP Handler
- **Maintains** a Knowledge Base for domain knowledge

### Memory System Relationships

- **Owned by** the Orchestrator, not individual Agents
- **Buffer Memory provides** immediate context to Agents through the Orchestrator
- **Long-Term Memory stores** historical context that Agents access via Orchestrator
- **Memory is configured** at the Orchestrator level
- **Memory is shared** across multiple Agents when appropriate
- **Memory is partitioned by** user_id for multi-user support
- **Memory operations** (add, search, clear) are exposed via the Orchestrator

### MCP Handler Relationships

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
3. **Context Enhancement**: Memory systems provide relevant context
4. **Processing**: Agent processes message with LLM and tools
5. **Tool Usage**: External tools are invoked via MCP if needed
6. **Response Generation**: Agent generates a response
7. **Memory Update**: Conversation is stored in memory
8. **Response Delivery**: Response is returned to the client

This architecture allows for flexibility, extensibility, and maintainability while providing a powerful foundation for AI agent development.
