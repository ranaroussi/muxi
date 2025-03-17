# MUXI Framework

MUXI (Multi-agent User eXperience Interface) Framework is a powerful platform for building AI agents with memory, tools, and real-time communication capabilities. It provides a solid foundation for creating advanced AI applications through a unified architecture that integrates multiple interfaces.

## Features

- 🤖 **Multi-Agent Support**: Create and manage multiple AI agents with different capabilities
- 🧠 **Memory Systems**: Short-term and long-term memory for contextual interactions
- 🛠️ **Tool Integration**: Extensible tool system with built-in web search, calculator, and more
- 🌐 **Multiple Interfaces**: REST API, WebSockets, CLI, Web UI, etc.
- 🔌 **Plugin System**: Extend functionality with custom plugins
- 🔒 **Security**: Built-in authentication and authorization

## Installation

### From PyPI (Recommended)

```bash
pip install muxi
```

### For Development

```bash
# Clone the repository
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework

# Install in development mode
./install_dev.sh
```

## Quick Start

### Using the CLI

```bash
# Start a chat session with the default agent
muxi chat

# Send a one-off message
muxi send "What is the capital of France?"

# Run the server
muxi run
```

### Using the API

Start the server:

```bash
muxi run
```

Then, in another terminal or from your application:

```bash
# Send a message to an agent
curl -X POST http://localhost:5050/agents/assistant/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the capital of France?"}'
```

### Using the Web UI

Start the server and web UI:

```bash
muxi run
```

Then open your browser and navigate to:

```
http://localhost:5050
```

## Documentation

For more detailed documentation, see:

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [API Reference](docs/api_reference.md)
- [CLI Reference](docs/cli.md)
- [Web UI Guide](docs/web_ui.md)
- [Configuration](docs/configuration.md)
- [Package Structure](docs/package_structure.md)

## Architecture

The MUXI Framework is organized into a modular architecture with the following main components:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, tools, LLM interface
│   ├── server/        # REST API and WebSocket server
│   ├── cli/           # Command-line interface
│   ├── web/           # Web user interface
│   └── muxi/          # Meta-package that integrates all components
└── tests/             # Test suite for all components
```

## Examples

### Creating a Custom Agent

```python
from muxi.core import Agent, MemorySystem
from muxi.core.tools import Calculator, WebSearch

# Create a new agent with custom tools and memory
agent = Agent(
    agent_id="math_helper",
    system_message="You are a helpful math assistant.",
    tools=[Calculator(), WebSearch()],
    memory=MemorySystem()
)

# Send a message to the agent
response = await agent.process_message("What is the square root of 16?")
print(response.content)  # Output: 4
```

### Building a Multi-Agent System

```python
from muxi.core import AgentManager
from muxi.server import Server

# Create and register multiple agents
manager = AgentManager()
manager.create_agent("researcher", "You are a research assistant...")
manager.create_agent("coder", "You are a coding assistant...")

# Start the server with these agents
server = Server(agent_manager=manager)
server.start()
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for their LLM technologies
- The many open-source projects that make this framework possible

