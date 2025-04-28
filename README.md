# MUXI Framework

> The MUXI Framework is a versatile Python framework for building AI agents and Multi-Agent systems.

MUXI Framework is a powerful platform for building AI agents with memory, MCP server integration, and real-time communication capabilities. It provides a solid foundation for creating advanced AI applications through a unified architecture that integrates multiple interfaces.

> [!TIP]
> This project is a work in progress and is not yet ready for production use. Please read the [whitepaper](WHITEPAPER.md) to learn "everything" about this project.

## Features

- 🤖 **Multi-Agent Support**: Create and manage multiple AI agents with different capabilities
- 🧠 **Memory Systems**: Short-term and long-term memory for contextual interactions
  - FAISS for short-term buffer memory
  - PostgreSQL with pgvector for scalable long-term memory
  - SQLite with sqlite-vec for local or lightweight deployments
- 🔌 **MCP Client Integration**: Connect to external services via Model Context Protocol servers
  - Support for HTTP+SSE transport for web-based MCP servers
  - Support for Command-line transport for local executable servers
  - Robust reconnection mechanism with exponential backoff
  - Comprehensive error handling and diagnostics
  - Cancellation support for long-running operations
- 🌟 **MCP Server Implementation**: Expose your agents as MCP-compatible servers
  - SSE-based server endpoint for MCP host integration
  - Tool discovery from agent capabilities
  - Authentication shared with REST API
  - Bridge package for non-SSE clients
- 🔄 **Agent-to-Agent (A2A) Communication**: Enable structured communication between agents
  - Standardized message format for inter-agent communication
  - Capability registration and discovery
  - Task delegation between specialized agents
  - Context sharing with proper isolation
  - Security and authentication
- 🌐 **Multiple Interfaces**: REST API, WebSockets, CLI, Web UI, etc.
- 🔄 **Intelligent Message Routing**: Automatically direct messages to the most appropriate agent
- 📊 **Multi-User Support**: User-specific memory partitioning for multi-tenant applications
- 📘 **Context Memory**: Store and retrieve structured information to personalize responses
- 🔍 **Agent-Level Knowledge Base**: Provide agents with specialized domain knowledge via lightweight RAG
- 🔄 **Hybrid Communication Protocol**: HTTP for standard requests, SSE for streaming, WebSockets for multi-modal
- 📝 **Declarative Configuration**: Define agents using YAML or JSON files with minimal code
- 🚀 **Modular Architecture**: Use only the components you need
- 🌍 **Language-Specific SDKs** (Coming in v0.5.0): Client libraries for TypeScript/JavaScript, Go, and more

## Architecture

MUXI has a flexible, service-oriented approach:

```
┌───────────────────┐
│      Clients      │
│ (CLI/MCP/Web/SDK) │
└─────────┬─────────┘
          │
          │  (API/SSE/WS)
          │
┌─────────│───────────────────────────────────────────┐
│         │    MUXI Server (Local/Remote)             │
│         │                                           │
│         │        ┌───────────────┐                  │   ┌──────────────────┐
│         └───────>│  Orchestrator │----------------------│ Buffer/LT Memory │
│                  └───────┬───────┘                  │   └──────────────────┘
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  │   ┌──────────────────┐
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │------│ Domain Knowledge │
│  └───┬─────↑───┘  └──────↑──────┘  └───↑─────┬───┘  │   └──────────────────┘
│      │     │             │             │     │      │
│      │     │             ↓             │     │      │
│      │     └─────────> (A2A) <─────────┘     │      │
│      │                                       │      │
│      │            ┌─────────────┐            │      │
│      └───────────>│ MCP Handler │<───────────┘      │
│                   └──────┬──────┘                   │
└──────────────────────────│──────────────────────────┘
                           │
                           │ (gRPC/HTTP/Command)
                           │
┌──────────────────────────▼──────────────────────────┐
│                     MCP Servers                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

For more details, see [Architecture Documentation](docs/intro/architecture.md).

## Technical Details

### Communication Protocols

MUXI implements a hybrid protocol approach for optimal performance and flexibility:

- **HTTP**: For standard API requests like configuration and management
- **Server-Sent Events (SSE)**: For streaming responses token-by-token
- **WebSockets + WebRTC**: For multi-modal capabilities with bi-directional communication

### Package Structure

The MUXI Framework is organized into a modular architecture with the following components:

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

### Language-Specific SDKs

MUXI Framework will provide client libraries for popular programming languages.

**Each SDK will provide:**

- Full REST API client implementation
- WebSocket client for real-time communication
- MCP server protocol implementation
- Consistent developer experience across languages

## License

This project is licensed under a dual licensing model to balance open-source collaboration with sustainable business practices.

### Development Phase (Pre-Version 1.0)

The software is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0)** during the development phase. This license prohibits commercial use, derivative works, and redistribution to ensure the integrity of the development process and to **avoid project fragmentation before it reaches maturity**.

### After Version 1.0 Release

When the project reaches version 1.0, it will switch to a more permissive open-source license that permits unrestricted use for non-commercial use cases and extensive use for commercial use cases.

## Contributing

**Contributions are welcome!** Please read our [Contributing Guide](docs/contributing.md) for details on our code of conduct, development setup, and the process for submitting pull requests.

## Acknowledgements

The many open-source projects that make this framework possible ❤️

