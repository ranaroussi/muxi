---
layout: default
title: Quick Start
nav_order: 2
permalink: /quick-start/
---

# Quick Start Guide

This guide will help you quickly get started with the MUXI Framework using a simplified configuration-based approach.

## Installation

Install the MUXI Framework from GitHub:

```bash
git clone https://github.com/your-organization/muxi.git
cd muxi
pip install -e .
```

## Set Up Environment Variables

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your-openai-key
DATABASE_URL=your-database-connection-string
```

## Create Agent Configuration Files

### YAML Configuration Example

Create a file `agents/weather_agent.yaml`:

```yaml
name: weather_assistant
system_message: You are a helpful assistant that can check the weather.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
memory:
  buffer: 10  # Sets buffer window size to 10
  long_term: true  # Enables long-term memory
tools:
- enable_calculator
- enable_web_search
```

### JSON Configuration Example

Alternatively, create `agents/finance_agent.json`:

```json
{
    "name": "finance_assistant",
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
    "tools": [
        "enable_calculator"
    ]
}
```

## Create Your Application

Create a new Python file with minimal code:

```python
from dotenv import load_dotenv
from src import muxi

# Load environment variables
load_dotenv()

# Initialize MUXI - no connection string needed
# It will be loaded from DATABASE_URL when required
mx = muxi()

# Add agents from configuration files
mx.add_agent("weather", "agents/weather_agent.yaml")
mx.add_agent("finance", "agents/finance_agent.json")

# Option 1: Interactive usage
# Chat with a specific agent
response = mx.chat("What's the weather in New York?", agent_name="weather")
print(response)

# Let the orchestrator automatically select the appropriate agent
response = mx.chat("What's the current stock market trend?")
print(response)  # Will likely be handled by the finance agent

# Chat with user-specific context
response = mx.chat("What's the weather in my city?", user_id=123)
print(response)  # Will use Alice's location data

# Option 2: Start server and web UI
mx.run()
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
mx.add_user_domain_knowledge(user_id, knowledge)

# Chat with user-specific context
response = mx.chat("weather", "What's the weather in my city?", user_id=user_id)
print(response)  # Will use Alice's location data
```

## Using MCP Servers

To integrate external Model Context Protocol servers:

```yaml
mcp_servers:
- name: weather_api
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    required: true
```

For credentials, the framework will:
1. First look for user-specific credentials in the database
2. Then look for system-wide credentials in the database
3. Finally, fall back to environment variables

## Advanced Usage

See the [Configuration Guide](/configuration-guide/) for advanced options and [API Reference](/api-reference/) for the complete API.
