# MUXI Framework Examples

This directory contains example scripts that demonstrate how to use the MUXI Framework with the current package architecture.

## Setup

Before running these examples:

1. Install the MUXI Framework in development mode:
   ```bash
   ./install_dev.sh
   ```

2. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key
   # Add other API keys as needed
   ```

## Available Examples

### 1. Basic Usage

The simplest way to use the MUXI Framework:

```bash
python examples/basic_usage.py
```

This example shows how to create a minimal agent with no tools or special memory systems.

### 2. Simple Agent

Create an agent with memory and tools:

```bash
python examples/simple_agent.py
```

This example demonstrates how to:
- Create an agent with buffer memory
- Add calculator and web search tools
- Process messages and use conversation context

### 3. Configuration-Based Agent

Create agents from YAML/JSON configuration files:

```bash
python examples/config_based_agent.py
```

This example shows how to:
- Create agents from configuration files
- Handle different message types
- Use tools via configuration

### 4. Multi-Agent System

Create multiple specialized agents with automatic message routing:

```bash
python examples/multi_agent.py
```

This example demonstrates:
- Creating multiple specialized agents
- How the orchestrator routes messages to the appropriate agent
- Handling different query types

### 5. WebSocket Client

Connect to the MUXI server via WebSocket:

```bash
# First, start the server
muxi run

# Then, in another terminal, run the WebSocket client
python examples/websocket_client.py
```

This example shows how to:
- Connect to the server via WebSocket
- Subscribe to agents
- Send and receive messages in real-time
- Handle different message types

## Configuration Files

The `configs/` directory contains example configuration files for agents:

- `assistant.yaml`: General-purpose assistant
- `weather_agent.yaml`: Weather specialist
- `finance_agent.json`: Finance specialist
- `travel_agent.yaml`: Travel specialist

These files demonstrate different configuration options for agents, including:
- Model configuration
- Memory settings (buffer_size, buffer_multiplier)
- Tool integration
- MCP server connections
