# MUXI Framework

MUXI Framework is a powerful platform for building AI agents with memory, MCP server integration, and real-time communication capabilities. It provides a solid foundation for creating advanced AI applications through a unified architecture that integrates multiple interfaces.

> [!WARNING]
> This project is a work in progress and is not yet ready for production use. We're actively developing the framework and adding new features. Please refer to the [roadmap](docs/roadmap.md) for information about the current state of the project and where it's headed.

## Features

- 🤖 **Multi-Agent Support**: Create and manage multiple AI agents with different capabilities
- 🧠 **Memory Systems**: Short-term and long-term memory for contextual interactions
- 🔌 **MCP Server Integration**: Connect to external services via Model Context Protocol servers
- 🌐 **Multiple Interfaces**: REST API, WebSockets, CLI, Web UI, etc.
- 🔄 **Intelligent Message Routing**: Automatically direct messages to the most appropriate agent
- 📊 **Multi-User Support**: User-specific memory partitioning for multi-tenant applications
- 📘 **Domain Knowledge**: Store and retrieve structured information to personalize responses
- 🔄 **Hybrid Communication Protocol**: HTTP for standard requests, SSE for streaming, WebSockets for multi-modal
- 📝 **Declarative Configuration**: Define agents using YAML or JSON files with minimal code
- 🚀 **Modular Architecture**: Use only the components you need

## Architecture

MUXI has a flexible, service-oriented approach:

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
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │  │
│  │    (YAML)   │  │    (JSON)   │  │    (YAML)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
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

For more details, see [Architecture Documentation](docs/architecture.md).

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

### Configuration-based Approach

The simplest way to get started is with the configuration-based approach:

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add an agent from a configuration file
app.add_agent("assistant", "configs/assistant.yaml")

# Chat with the agent
response = await app.chat("Hello, who are you?")
print(response)

# Run the server
# app.run()
```

Example configuration file (`configs/assistant.yaml`):

```yaml
name: assistant
system_message: You are a helpful AI assistant.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
memory:
  buffer: 10  # Buffer window size of 10
  long_term: true  # Enable long-term memory
mcp_servers:
- name: web_search
  url: http://localhost:5001
  credentials:
  - id: search_api_key
    param_name: api_key
    required: true
    env_fallback: SEARCH_API_KEY
```

### Programmatic Approach

You can also create agents programmatically using the Orchestrator interface:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory

# Create an orchestrator to manage agents
orchestrator = Orchestrator()

# Create a basic agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    buffer_memory=BufferMemory(),
    system_message="You are a helpful AI assistant.",
    description="General-purpose assistant for answering questions and providing information."
)

# Create an agent with long-term memory
orchestrator.create_agent(
    agent_id="researcher",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    buffer_memory=BufferMemory(),
    long_term_memory=LongTermMemory(connection_string="your_db_connection"),
    system_message="You are a helpful research assistant.",
    description="Specialized in research tasks, data analysis, and information retrieval."
)

# Add MCP server to the agent
await orchestrator.agents["assistant"].connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_search_api_key"}
)

# Chat with an agent (automatic routing based on query)
response = await orchestrator.chat("Tell me about quantum physics")
print(response.content)

# Chat with a specific agent
response = await orchestrator.chat("Tell me about quantum physics", agent_name="researcher")
print(response.content)

# Chat with multi-user support
response = await orchestrator.chat("Remember my name is Alice", user_id="user123")
print(response.content)
```

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

The web UI requires installing the web module first:

```bash
# Install the web UI module
pip install muxi-web

# Start the server with web UI support
muxi run
```

Then open your browser and navigate to:

```
http://localhost:5050
```

Alternatively, you can run the web UI separately if you already have a MUXI server running elsewhere:

```bash
# Start just the web UI, connecting to a server
muxi-web --server-url http://your-server-address:5050
```

## Intelligent Message Routing

Automatically route user messages to the most appropriate agent based on their content:

```python
from muxi import muxi

# Initialize your app with multiple specialized agents
app = muxi()
await app.add_agent("weather", "configs/weather_agent.yaml")
await app.add_agent("finance", "configs/finance_agent.json")
await app.add_agent("travel", "configs/travel_agent.yaml")

# The message will be automatically routed to the most appropriate agent
response = await app.chat("What's the weather forecast for Tokyo this weekend?")  # Weather agent
response = await app.chat("Should I invest in tech stocks right now?")  # Finance agent
response = await app.chat("What are the best attractions in Barcelona?")  # Travel agent
```

The orchestrator analyzes the content of each message and intelligently routes it to the most suitable agent based on their specializations and descriptions. This means you don't need to specify which agent should handle each request - the system figures it out automatically.

Configure the routing system through environment variables:

```
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0
```

## Package Structure

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

## Communication Protocols

MUXI implements a hybrid protocol approach for optimal performance and flexibility:

- **HTTP**: For standard API requests like configuration and management
- **Server-Sent Events (SSE)**: For streaming responses token-by-token
- **WebSockets**: For multi-modal capabilities with bi-directional communication

## Working with Memory and Domain Knowledge

```python
from muxi import muxi

# Initialize MUXI
app = muxi()

# Add multiple agents from configuration files
await app.add_agent("weather", "configs/weather_agent.yaml")
await app.add_agent("assistant", "configs/assistant.yaml")

# Add domain knowledge for a specific user
user_id = "user123"
knowledge = {
    "name": "Alice",
    "location": {"city": "New York", "country": "USA"},
    "preferences": {"language": "English", "units": "metric"}
}
await app.add_user_domain_knowledge(user_id, knowledge)

# Chat with personalized context
# Note: No need to specify agent_id - the orchestrator will select the appropriate agent
response = await app.chat(
    "What's the weather like in my city?",
    user_id=user_id
)
print(response.content)  # Uses Alice's location data from domain knowledge

# For memory operations that are specific to an agent, you can specify agent_id
memory_results = await app.search_memory(
    "What did the user ask about the weather?",
    agent_id="weather",  # Specify when you need to target a specific agent's memory
    user_id=user_id,
    limit=5
)
print("Related memories:", memory_results)
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

## License

This project is licensed under a dual licensing model to balance open-source collaboration with sustainable business practices.

### Development Phase (Pre-Version 1.0)

During the development phase, the software is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0)** license. This license prohibits commercial use, derivative works, and redistribution to ensure the integrity of the development process and to avoid fragmentation of the project before it reaches maturity.

### After Version 1.0 Release

When the project reaches version 1.0, it will adopt a more permissive open-source license that permits free use for non-commercial and internal commercial purposes, with the possibility of a commercial license for specific use cases.

## Contributing

**Contributions are welcome!** Please read our [Contributing Guide](docs/contributing.md) for details on our code of conduct, development setup, and the process for submitting pull requests.

## Acknowledgements

- OpenAI for their LLM technologies
- The many open-source projects that make this framework possible

