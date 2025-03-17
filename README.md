# MUXI - AI Agent Framework

MUXI is an extensible framework for building AI agents with real-time communication capabilities, memory persistence, and tool integration.

> [!WARNING]
> This project is a work in progress and is not even close to being ready for production use. I'm actively developing the framework and adding new features. Please refer to the [roadmap](docs/roadmap.md) for detailed information about the current state of the project and where it's headed.

## Features

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with different capabilities
- **Intelligent Message Routing**: Automatically direct messages to the most appropriate agent using LLM-based analysis
- **Standardized LLM Communication**: Model Context Protocol (MCP) for consistent interaction with various LLM providers
- **Memory Systems**: Short-term buffer memory and long-term persistent memory for agents
- **Multi-User Support**: Memobase provides user-specific memory partitioning for multi-tenant applications
- **Domain Knowledge**: Store and retrieve user-specific structured information to personalize agent responses
- **Tool Integration**: Extensible tool system with built-in utilities and custom tool support
- **Real-Time Communication**: WebSocket support for instant messaging and streaming responses
- **REST API**: Comprehensive API for managing agents, tools, and conversations
- **Command Line Interface**: Rich terminal-based interface for creating and interacting with agents
- **Reliable Message Handling**: Robust error handling and automatic reconnection mechanisms
- **Declarative Configuration**: Define agents using YAML or JSON files with minimal code
- **Flexible Deployment**: Run locally or connect to remote MUXI servers
- **Hybrid Communication Protocol**: HTTP for standard requests, SSE for streaming, WebSockets for multi-modal
- **Modular Packaging**: Install only the components you need

## Architecture

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

MUXI is evolving towards a more flexible, service-oriented approach:

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
│         │         ┌──────────────┐                  │
│         └───────> │ Orchestrator │                  │
│                   └──────┬───────┘                  │
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│         ▼                ▼                ▼         │
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

This evolution preserves the current programmatic API while adding powerful capabilities for distributed deployment. For more details, see [ARCHITECTURE_EVOLUTION.md](ARCHITECTURE_EVOLUTION.md).

## Intelligent Message Routing

Automatically route user messages to the most appropriate agent based on their content:

```python
from src import muxi

# Initialize your app with multiple specialized agents
app = muxi()
app.add_agent("configs/weather_agent.yaml")
app.add_agent("configs/finance_agent.json")
app.add_agent("configs/travel_agent.yaml")

# The message will be automatically routed to the most appropriate agent
response = app.chat("What's the weather forecast for Tokyo this weekend?")  # Weather agent
response = app.chat("Should I invest in tech stocks right now?")  # Finance agent
response = app.chat("What are the best attractions in Barcelona?")  # Travel agent
```

Configure the routing system through environment variables:

```
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0
```

For complete configuration options, see the [Configuration Guide](docs/configuration_guide.md).

## Installation

```bash
# Clone the repository
git clone https://github.com/ranaroussi/muxi.git
cd muxi

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Configuration-based Approach (Recommended)

The simplest way to get started is with the configuration-based approach:

```python
from src import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize - database connection will be loaded automatically when needed
app = muxi()

# Add an agent from a configuration file
app.add_agent("my_assistant", "configs/assistant.yaml")

# Chat with a specific agent
response = app.chat("Hello, who are you?", agent_name="my_assistant")
print(response)

# Or let the orchestrator automatically select the appropriate agent
response = app.chat("Hello, can you help me?")
print(response)

# Start the API server and web UI
# app.run()
```

Configuration file (`configs/assistant.yaml`):

```yaml
name: my_assistant
system_message: You are a helpful AI assistant.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
memory:
  buffer: 10  # Buffer window size of 10
  long_term: true  # Enable long-term memory
tools:
- enable_calculator
- enable_web_search
```

### Remote Server Connection (New)

Connect to an existing MUXI server:

```python
from src import muxi

# Connect to a remote MUXI server
app = muxi(
    server_url="http://server-ip:5050",
    api_key="your_api_key"
)

# Use the same API
response = app.chat("Hello, remote assistant!")
print(response)

# Streaming responses via SSE
for chunk in app.chat("Tell me a story", stream=True):
    print(chunk, end="", flush=True)

# Multi-modal capabilities via WebSockets
socket = app.open_socket()
await socket.send_message("Process this image", images=["path/to/image.jpg"])
await socket.close()
```

## Using the Command Line Interface

The framework includes a rich CLI for interacting with agents directly from your terminal:

```bash
# Start the CLI (before package installation)
python -m src.cli

# Start a chat session with an agent
python -m src.cli chat --agent-id assistant

# Send a one-off message to an agent
python -m src.cli send --agent-id assistant "What is the capital of France?"

# Start the API server
python -m src.cli api

# Start both API server and web UI
python -m src.cli run
# or simply
python -m src
```

After installing the package, you can use the `muxi` command instead:

```bash
muxi chat --agent-id assistant
```

## Communication Protocols

MUXI implements a hybrid protocol approach for optimal performance and flexibility:

### Standard HTTP
- Used for all API requests like configuration and management
- RESTful API design with clear endpoint structure
- Standard authentication via headers

### Server-Sent Events (SSE)
- Used for streaming responses during chat/generation
- Real-time token-by-token streaming
- Connection automatically closes after response completion
- Higher scalability than persistent WebSocket connections

### WebSockets
- Used for multi-modal capabilities (Omni features)
- Bi-directional communication for audio/video
- Persistent connections for continuous interaction
- Available through the `app.open_socket()` API

## Using the REST API

Start the API server:

```bash
# Default setup (binds to 0.0.0.0, allowing remote connections)
python -m src.api.run

# Specify custom host and port
python -m src.api.run --host 0.0.0.0 --port 5050
```

> **Note:** The WebSocket server runs on the same port as the API server. When you change the API port, the WebSocket port changes too.

When running the frontend on a different server, update the `BACKEND_API_URL` in `src/web/.env`:

```
# Replace with your API server's IP or domain name
BACKEND_API_URL=http://your-server-ip:5050
```

Create a new agent:

```bash
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent",
    "system_message": "You are a helpful AI assistant."
  }'
```

Send a message to the agent:

```bash
curl -X POST http://localhost:5050/chat/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with today?"
  }'
```

## Using WebSockets

To use the WebSocket feature, run the server and connect using a WebSocket client:

```javascript
// Browser WebSocket client example
// Note: The WebSocket server runs on the same port as the API server
const socket = new WebSocket('ws://localhost:5050/ws');

socket.onopen = () => {
  console.log('Connected to WebSocket server');

  // Set user ID (for multi-user agents)
  socket.send(JSON.stringify({
    type: 'set_user',
    user_id: 123
  }));

  // Subscribe to an agent
  socket.send(JSON.stringify({
    type: 'subscribe',
    agent_id: 'agent'
  }));

  // Send a message
  socket.send(JSON.stringify({
    type: 'chat',
    message: 'Tell me about artificial intelligence'
  }));
};

socket.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Received:', response);
};
```

### WebSocket Message Types

#### Client to Server:

- `subscribe`: Subscribe to an agent
- `chat`: Send a chat message
- `ping`: Keep the connection alive
- `set_user`: Set the user ID for this connection
- `search_memory`: Search agent memory for relevant information
- `clear_memory`: Clear agent memory for a specific user

#### Server to Client:

- `message`: Response from the agent
- `error`: Error message
- `tool_start`: Notification that a tool is being executed
- `tool_end`: Results from a tool execution

## Recent Improvements

- **Multi-User Support**: Added Memobase for user-specific memory partitioned memory
- **Memory Management**: Added endpoints for memory search and clearing, with support for user-specific operations
- **Shared Orchestrator Instance**: Fixed issue with WebSocket and REST API using different orchestrator instances
- **Enhanced Error Handling**: Improved error handling and reporting in WebSocket connections
- **Message Serialization**: Fixed JSON serialization issues with MCPMessage objects
- **Reliable Connection Management**: Implemented automatic reconnection and subscription recovery
- **MCP Message Structure**: Improved message handling with standardized role/content attributes for better compatibility with various LLM providers
- **Testing Environment**: Added utilities for consistent API key handling in tests
- **Documentation**: Added comprehensive documentation for all components
- **Test Coverage**: Added extensive test coverage for all API endpoints, especially multi-user functionality

## Documentation

Comprehensive documentation is available in the `docs` directory:

### Overview
- [Framework Overview](docs/overview.md)
- [Architecture](docs/architecture.md)
- [Agent Guide](docs/agent.md)
- [Orchestrator Documentation](docs/orchestrator.md)
- [Memory Systems](docs/memory.md)
- [Domain Knowledge](docs/domain_knowledge.md)
- [Tool System](docs/tools.md)
- [Model Context Protocol (MCP)](docs/mcp.md)

### Concepts
- [Agents vs Tools](docs/agents_vs_tools.md)
- [Tools vs MCP](docs/tools_vs_mcp.md)

### Setup and Configuration
- [Quick Start Guide](docs/quick_start.md)
- [Configuration Guide](docs/configuration_guide.md)
- [Testing Guide](docs/testing.md)

### Interfaces
- [CLI Documentation](docs/cli.md)
- [Webapp Documentation](docs/webapp.md)
- [REST API Documentation](docs/api.md)
- [WebSocket Implementation](docs/websocket.md)


## License

This project is licensed under a dual licensing model to balance open-source collaboration with sustainable business practices.

### Development Phase (Pre-Version 1.0)

During the development phase, the software is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0)** license. This license prohibits commercial use, derivative works, and redistribution to ensure the integrity of the development process and to avoid fragmentation of the project before it reaches maturity.

### After Version 1.0 Release

When the project reaches version 1.0, it will adopt a more permissive open-source license that permits free use for non-commercial and internal commercial purposes, with the possibility of a commercial license for specific use cases.

## Contributing

**Contributions are welcome!** Please read our [Contributing Guide](docs/contributing.md) for details on our code of conduct, development setup, and the process for submitting pull requests.

