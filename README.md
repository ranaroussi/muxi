# AI Agent Framework

A powerful, extensible framework for building AI agents with real-time communication capabilities, memory persistence, and tool integration.

## Features

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with different capabilities
- **Standardized LLM Communication**: Modern Control Protocol (MCP) for consistent interaction with various LLM providers
- **Memory Systems**: Short-term buffer memory and long-term persistent memory for agents
- **Multi-User Support**: Memobase provides user-specific memory partitioning for multi-tenant applications
- **Tool Integration**: Extensible tool system with built-in utilities and custom tool support
- **Real-Time Communication**: WebSocket support for instant messaging and streaming responses
- **REST API**: Comprehensive API for managing agents, tools, and conversations
- **Command Line Interface**: Rich terminal-based interface for creating and interacting with agents
- **Reliable Message Handling**: Robust error handling and automatic reconnection mechanisms

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-agent-framework.git
cd ai-agent-framework

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from src.core.orchestrator import Orchestrator
from src.llm.openai import OpenAILLM
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase

# Create an orchestrator to manage agents
orchestrator = Orchestrator()

# Create a basic agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    llm=OpenAILLM(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    system_message="You are a helpful AI assistant."
)

# Create an agent with long-term memory
long_term_memory = LongTermMemory()
orchestrator.create_agent(
    agent_id="researcher",
    llm=OpenAILLM(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=long_term_memory,
    system_message="You are a helpful research assistant."
)

# Create an agent with multi-user support
long_term_memory = LongTermMemory()
memobase = Memobase(long_term_memory=long_term_memory)
orchestrator.create_agent(
    agent_id="multi_user_assistant",
    llm=OpenAILLM(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    memobase=memobase,
    system_message="You are a helpful assistant that supports multiple users."
)

# Chat with a regular agent
response = orchestrator.chat("assistant", "Hello, can you help me with a Python question?")
print(response)

# Chat with a multi-user agent (specify user_id)
response = orchestrator.chat("multi_user_assistant", "Remember that my name is Alice", user_id=123)
print(response)
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

## Architecture

<a href="https://www.mermaidchart.com/raw/12634479-a45c-48c0-bcec-d901cd7d62eb?theme=light&version=v0.1&format=svg"><img src="https://www.mermaidchart.com/raw/12634479-a45c-48c0-bcec-d901cd7d62eb?theme=light&version=v0.1&format=svg" alt="Architecture Diagram" style="width: 100%; height: auto;"></a>

## Using the REST API

Start the API server:

```bash
# Default setup (binds to 0.0.0.0, allowing remote connections)
python -m src.api.run

# Specify custom host and port
python -m src.api.run --host 0.0.0.0 --port 5050
```

> **Note:** The WebSocket server runs on the same port as the API server. When you change the API port, the WebSocket port changes too.

When running the frontend on a different server, update the `REACT_APP_API_URL` in `src/web/.env`:

```
# Replace with your API server's IP or domain name
REACT_APP_API_URL=http://your-server-ip:5050
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

**Client to Server:**
- `subscribe`: Subscribe to an agent
- `chat`: Send a chat message
- `ping`: Keep the connection alive
- `set_user`: Set the user ID for this connection
- `search_memory`: Search agent memory for relevant information
- `clear_memory`: Clear agent memory for a specific user

**Server to Client:**
- `message`: Response from the agent
- `error`: Error message
- `tool_start`: Notification that a tool is being executed
- `tool_end`: Results from a tool execution

## Recent Improvements

- **Multi-User Support**: Added Memobase for user-specific memory partitioning
- **Memory Management**: Added endpoints for memory search and clearing, with support for user-specific operations
- **Shared Orchestrator Instance**: Fixed issue with WebSocket and REST API using different orchestrator instances
- **Enhanced Error Handling**: Improved error handling and reporting in WebSocket connections
- **Message Serialization**: Fixed JSON serialization issues with MCPMessage objects
- **Reliable Connection Management**: Implemented automatic reconnection and subscription recovery
- **Documentation**: Added comprehensive documentation for all components
- **Test Coverage**: Added extensive test coverage for all API endpoints, especially multi-user functionality

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [Agent Guide](docs/agent.md)
- [Orchestrator Documentation](docs/orchestrator.md)
- [Memory Systems](docs/memory.md)
- [Tool System](docs/tools.md)
- [Modern Control Protocol (MCP)](docs/mcp.md)
- [WebSocket Implementation](docs/websocket.md)
- [REST API Documentation](docs/api.md)
- [CLI Documentation](docs/cli.md)
- [Architecture](docs/architecture.md)
- [Agents vs Orchestrators](docs/agents-vs-orchestrators.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
