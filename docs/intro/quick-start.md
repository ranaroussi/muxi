---
layout: default
title: Quick Start Guide
parent: Introduction
nav_order: 3
permalink: /intro/quick-start
---

# Quick Start Guide

## What You'll Learn
- How to install MUXI
- How to create agents using configuration files
- How to build a simple multi-agent application
- How to interact with agents and MCP servers
- How to support multiple users

## Prerequisites
- Python 3.10 or later
- An OpenAI API key (for the examples in this guide)
- Basic Python knowledge

## Installation

Install the MUXI Framework using pip:

```bash
pip install muxi
```

For development installations, you can clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework
./install_dev.sh
```

## Set Up Environment Variables

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your-openai-key
POSTGRES_DATABASE_URL=your-database-connection-string
WEATHER_API_KEY=your-weather-api-key
```

## Creating Your First Agent

The easiest way to get started with MUXI is to use declarative configuration files. These can be in YAML or JSON format.

### YAML Configuration Example

Create a file `configs/muxi_config.yaml`:

```yaml
agents:
  - agent_id: weather_assistant
    description: "Specialized in providing weather forecasts and current conditions."
    system_message: You are a helpful assistant that can check the weather.
    model:
      provider: openai
      api_key: "${OPENAI_API_KEY}"
      model: gpt-4o
      temperature: 0.7
    mcp_servers:
      - name: weather_api
        url: http://localhost:5001
        api_key: "${WEATHER_API_KEY}"
  - agent_id: finance_assistant
    description: "Expert in financial analysis, investments, and market trends."
    system_message: You are a helpful finance assistant.
    model:
      provider: openai
      api_key: "${OPENAI_API_KEY}"
      model: gpt-4o
      temperature: 0.2
    mcp_servers:
      - name: finance_api
        url: http://localhost:5002
        api_key: "${FINANCE_API_KEY}"
```

### JSON Configuration Example

Alternatively, create `configs/muxi_config.json`:

```json
{
  "agents": [
    {
      "agent_id": "weather_assistant",
      "description": "Specialized in providing weather forecasts and current conditions.",
      "system_message": "You are a helpful assistant that can check the weather.",
      "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o",
        "temperature": 0.7
      },
      "mcp_servers": [
        {
          "name": "weather_api",
          "url": "http://localhost:5001",
          "api_key": "${WEATHER_API_KEY}"
        }
      ]
    },
    {
      "agent_id": "finance_assistant",
      "description": "Expert in financial analysis, investments, and market trends.",
      "system_message": "You are a helpful finance assistant.",
      "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o",
        "temperature": 0.2
      },
      "mcp_servers": [
        {
          "name": "finance_api",
          "url": "http://localhost:5002",
          "api_key": "${FINANCE_API_KEY}"
        }
      ]
    }
  ]
}
```

## Create a Multi-Agent Application

Create a new Python file with minimal code:

```python
from dotenv import load_dotenv
from muxi import muxi

# Load environment variables
load_dotenv()

# Initialize MUXI with memory configuration
app = muxi(
  buffer_memory=10,  # Sets buffer window size to 10
  long_term_memory="postgresql://user:pass@localhost/db",  # Enables long-term memory
  config_file="configs/muxi_config.yaml"  # Load agent configurations from file
)

# Chat with a specific agent
response = app.chat("What's the weather in New York?", agent_name="weather_assistant")
print(response)

# Let the orchestrator automatically select the appropriate agent
response = app.chat("What's the current stock market trend?")
print(response)  # Will be handled by the finance_assistant

# Start the server
app.run()
```

## Automatic Agent Selection

When you add multiple agents to your application, MUXI will automatically route messages to the most appropriate agent based on their descriptions:

```python
# Let the orchestrator automatically select the appropriate agent
response = app.chat("What's the current stock market trend?")
print(response)  # Will likely be handled by the finance_assistant

response = app.chat("What's the weather in New York?")
print(response)  # Will likely be handled by the weather_assistant
```

The routing system uses an LLM to analyze the message content and agent descriptions to determine the best match.

## Adding Context Memory

You can enhance your agents with context memory:

```python
# Add context knowledge for the agent
app.add_context_knowledge("geography.txt", agent_id="weather_assistant")

# Add user-specific context memory
app.add_user_context_memory(
    user_id="user123",
    knowledge={"name": "John", "location": "New York"}
)
```

## Multi-User Support

For multi-user applications:

```python
# Initialize MUXI with multi-user memory support
app = muxi(
    buffer_memory=10,
    long_term_memory="postgresql://user:pass@localhost/db",  # PostgreSQL recommended for multi-user
    config_file="configs/muxi_config.yaml"
)

# Chat with user-specific context
response = app.chat(
    "What's the weather in my city?",
    agent_name="weather_assistant",
    user_id="user123"
)
print(response)  # Will use user123's location data

# Another user with different context
response = app.chat(
    "What's the weather in my city?",
    agent_name="weather_assistant",
    user_id="user456"
)
print(response)  # Will use user456's location data if available
```

## Using the CLI

MUXI provides a convenient command-line interface:

```bash
# Start a chat session with the default agent
muxi chat

# Send a one-off message
muxi send "What is the capital of France?"

# Run the server
muxi run
```

## Using the REST API

After starting the server:

```bash
muxi run
```

You can interact with the API:

```bash
# Send a message to an agent
curl -X POST http://localhost:5050/agents/weather_assistant/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the capital of France?"}'
```

## Using WebSockets

For real-time applications, you can use the WebSocket interface:

```python
import asyncio
import websockets
import json

async def chat_with_agent():
    async with websockets.connect("ws://localhost:5050/ws") as websocket:
        # Send a message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "Tell me about the weather in Paris",
            "agent": "weather_assistant"
        }))

        # Receive streaming response
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data["type"] == "chunk":
                # Process streaming chunk
                print(response_data["content"], end="")
            elif response_data["type"] == "done":
                # Response complete
                break

asyncio.run(chat_with_agent())
```

## Using MCP Servers

MCP servers extend agent capabilities by providing specialized functionality. To use them:

1. Add them to your agent configuration as shown in the examples above
2. The agent will automatically use the appropriate server based on the query

### Creating Your Own MCP Server

You can create your own MCP server to extend agent capabilities:

```bash
# Generate a new MCP server template
muxi mcp create my_custom_server
cd my_custom_server

# Install dependencies and start the server
pip install -r requirements.txt
python server.py
```

Once your MCP server is running, add it to your agent configuration:

```yaml
mcp_servers:
  - name: custom_server
    url: http://localhost:5010
    api_key: "${CUSTOM_API_KEY}"
```

## Advanced Topics

For more detailed information:

- [Creating MCP Servers](/extend/custom-mcp)
- [Multi-Agent Systems](/agents/multi-agent)
- [Memory Systems](/technical/memory/buffer)

## What's Next

- [Architecture](/intro/architecture) - Understand the framework's architecture
- [Simple Agents](/agents/simple) - Learn more about creating agents
- [Server Deployment](/clients/server) - Deploy your application as a server
