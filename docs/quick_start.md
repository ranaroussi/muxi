---
layout: default
title: Quick Start
nav_order: 2
permalink: /quick-start/
---

# Quick Start Guide

This guide will help you quickly get started with the MUXI Framework using a simplified configuration-based approach. For more detailed configuration options, see the [Configuration Guide](/configuration-guide/).

## Installation

Install the MUXI Framework using pip:

```bash
pip install muxi
```

For development, you can clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework
./install_dev.sh
```

## Set Up Environment Variables

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your-openai-key
DATABASE_URL=your-database-connection-string
WEATHER_API_KEY=your-weather-api-key
```

## Create Agent Configuration Files

### YAML Configuration Example

Create a file `agents/weather_agent.yaml`:

```yaml
name: weather_assistant
description: "Specialized in providing weather forecasts and current conditions."
system_message: You are a helpful assistant that can check the weather.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
memory:
  buffer: 10  # Sets buffer window size to 10
  long_term: true  # Enables long-term memory
mcp_servers:
- name: weather_api
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    value: "${WEATHER_API_KEY}"
    required: true
```

### JSON Configuration Example

Alternatively, create `agents/finance_agent.json`:

```json
{
    "name": "finance_assistant",
    "description": "Expert in financial analysis, investments, and market trends.",
    "system_message": "You are a helpful finance assistant.",
    "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "memory": {
        "buffer": 5,
        "long_term": false
    },
    "mcp_servers": [
        {
            "name": "finance_api",
            "url": "http://localhost:5002",
            "credentials": [
                {
                    "id": "finance_api_key",
                    "param_name": "api_key",
                    "value": "${FINANCE_API_KEY}",
                    "required": true
                }
            ]
        }
    ]
}
```

## Automatic Agent Selection

When you add multiple agents to your application, MUXI will automatically route messages to the most appropriate agent based on their descriptions:

```python
from muxi import muxi

# Create a new MUXI instance
app = muxi()

# Add multiple agents with different specializations
app.add_agent("weather", "agents/weather_agent.yaml")
app.add_agent("finance", "agents/finance_agent.json")

# Let the orchestrator automatically select the appropriate agent
response = app.chat("What's the current stock market trend?")
print(response)  # Will likely be handled by the finance agent

response = app.chat("What's the weather in New York?")
print(response)  # Will likely be handled by the weather agent
```

The routing system uses a dedicated LLM to analyze the message content and agent descriptions to determine the best match. You can configure this behavior with environment variables:

```
# Routing LLM configuration
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0
ROUTING_USE_CACHING=true
```

## Create Your Application

Create a new Python file with minimal code:

```python
from dotenv import load_dotenv
from muxi import muxi

# Load environment variables
load_dotenv()

# Initialize MUXI - no connection string needed
# It will be loaded from DATABASE_URL when required
app = muxi()

# Add agents from configuration files
app.add_agent("weather", "agents/weather_agent.yaml")
app.add_agent("finance", "agents/finance_agent.json")

# Option 1: Interactive usage
# Chat with a specific agent
response = app.chat("What's the weather in New York?", agent_name="weather")
print(response)

# Let the orchestrator automatically select the appropriate agent
response = app.chat("What's the current stock market trend?")
print(response)  # Will likely be handled by the finance agent

# Chat with user-specific context
response = app.chat("What's the weather in my city?")
print(response)  # Will use Alice's location data

# Option 2: Start the server
app.run()
```

## Multi-User Support

For multi-user applications:

```python
user_id = 123

# Add domain knowledge for a specific user (if not already added in the past)
knowledge = {
    "name": "Alice",
    "location": {"city": "New York"}
}
app.add_user_domain_knowledge(user_id, knowledge)

# Chat with user-specific context
response = app.chat("What's the weather in my city?", user_id=user_id)
print(response)  # Will use Alice's location data
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

## Using the API

After starting the server:

```bash
muxi run
```

You can interact with the API:

```bash
# Send a message to an agent
curl -X POST http://localhost:5050/agents/assistant/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the capital of France?"}'
```

## Using MCP Servers

To integrate external Model Context Protocol servers, add them to the agent configuration file as shown in the examples above. MCP servers extend agent capabilities by providing specialized functionality like weather data, financial information, web search, etc.

For MCP server credentials, the framework will:

1. First look for user-specific credentials in the database
2. Then look for system-wide credentials in the database
3. Finally, fall back to environment variables

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
  credentials:
  - id: custom_api_key
    param_name: api_key
    value: "${CUSTOM_API_KEY}"
    required: true
```

## Advanced Usage

See the [Configuration Guide](/configuration-guide/) for advanced options and [API Reference](/api-reference/) for the complete API.
