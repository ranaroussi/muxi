---
layout: default
title: Configuration Guide
nav_order: 3
permalink: /configuration-guide/
---

# Configuration Guide

This guide explains how to configure the MUXI framework, covering everything from basic setup to advanced features like intelligent message routing and credential management.

## Basic Configuration

MUXI supports configuration through YAML or JSON files, making it easy to define agents without writing code.

### Environment Variables

MUXI uses environment variables for sensitive information and global settings:

```
# LLM API keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database connection
DATABASE_URL=postgresql://user:password@localhost:5432/muxi

# Debug and logging
DEBUG=false
LOG_LEVEL=info

# Routing LLM configuration
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0
ROUTING_USE_CACHING=true
ROUTING_CACHE_TTL=3600
```

You can load these variables from a `.env` file using:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Agent Configuration Files

MUXI supports both YAML and JSON formats for agent configuration:

#### YAML Example (weather_agent.yaml)

```yaml
name: weather_assistant
description: "Specialized in providing weather forecasts, answering questions about climate and weather phenomena, and reporting current conditions in various locations worldwide."
system_message: You are a helpful assistant that can check the weather. Use the Weather
  tool when asked about weather conditions.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
memory:
  buffer: 10
  long_term: true
tools:
- enable_calculator
- enable_web_search
mcp_servers:
- name: weather
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    required: true
    env_fallback: WEATHER_API_KEY
```

#### JSON Example (finance_agent.json)

```json
{
    "name": "finance_assistant",
    "description": "Expert in financial analysis, investment strategies, market trends, stock recommendations, and personal finance advice. Can perform calculations and analyze financial data.",
    "system_message": "You are a helpful assistant specialized in finance and investments. Use the Calculator tool for financial calculations.",
    "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "memory": {
        "buffer": 15,
        "long_term": true
    },
    "tools": [
        "enable_calculator"
    ],
    "mcp_servers": [
        {
            "name": "stock_data",
            "url": "http://localhost:5002",
            "credentials": [
                {
                    "id": "alpha_vantage_api_key",
                    "param_name": "api_key",
                    "required": true
                },
                {
                    "id": "alpha_vantage_account_id",
                    "param_name": "account_id",
                    "required": false
                }
            ]
        }
    ]
}
```

## Intelligent Message Routing

MUXI can automatically route messages to the most appropriate agent based on their content and agent descriptions.

### Configuration Parameters

The routing system is configured through environment variables:

```
# Routing LLM provider (defaults to "openai")
ROUTING_LLM=openai

# Model to use for routing (defaults to "gpt-4o-mini")
ROUTING_LLM_MODEL=gpt-4o-mini

# Temperature for routing decisions (defaults to 0.0)
ROUTING_LLM_TEMPERATURE=0.0

# Whether to cache routing decisions (defaults to true)
ROUTING_USE_CACHING=true

# Time in seconds to cache routing decisions (defaults to 3600)
ROUTING_CACHE_TTL=3600
```

### Agent Descriptions

For effective routing, provide clear and specific descriptions for each agent:

```yaml
# Weather agent
name: weather_assistant
description: "Specialized in providing weather forecasts, answering questions about climate and weather phenomena, and reporting current conditions in various locations worldwide."
```

```yaml
# Finance agent
name: finance_assistant
description: "Expert in financial analysis, investment strategies, market trends, stock recommendations, and personal finance advice. Can perform calculations and analyze financial data."
```

### How Routing Works

1. When a user sends a message without specifying an agent, the routing system analyzes the message.
2. The system compares the message content against each agent's description.
3. Using a dedicated LLM, it selects the most appropriate agent.
4. The message is then sent to the selected agent for processing.
5. If routing fails or no appropriate agent is found, the system falls back to the default agent or the first available agent.

## Credential Management

MUXI supports flexible credential management for MCP servers and external services.

### Credential Configuration

Credentials are defined in the agent configuration file:

```yaml
mcp_servers:
- name: weather_api
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    required: true
    env_fallback: WEATHER_API_KEY
```

### Multiple Credentials

For services requiring multiple credentials:

```yaml
mcp_servers:
- name: twitter
  url: http://localhost:5003
  credentials:
  - id: twitter_api_key
    param_name: api_key
    required: true
  - id: twitter_api_secret
    param_name: api_secret
    required: true
```

### Credential Resolution Process

When resolving credentials, the system:

1. First checks for user-specific credentials in the database
2. If not found, looks for system-wide credentials in the database
3. Finally, falls back to environment variables if specified

## Memory Configuration

Configure memory storage for your agents:

```yaml
memory:
  # Short-term memory (number of messages to keep in context)
  buffer: 10

  # Enable long-term memory for persistent storage
  long_term: true

  # Enable multi-user support
  multi_user: true
```

## Tool Configuration

Enable built-in tools or add custom tools:

```yaml
tools:
# Built-in tools
- enable_calculator
- enable_web_search

# Custom tools
- name: custom_tool
  module: src.tools.custom
  class: CustomTool
  config:
    param1: value1
    param2: value2
```

## MCP Server Configuration

Connect to Model Context Protocol servers:

```yaml
mcp_servers:
- name: weather
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    required: true

- name: news
  url: http://localhost:5002
  credentials:
  - id: news_api_key
    param_name: api_key
    required: true
```

## Advanced Configuration

### Using Environment Variables in Configuration

Use `${ENV_VAR}` syntax to reference environment variables:

```yaml
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: "${LLM_MODEL:-gpt-4o}"  # Use default if not set
```

### Configuration Validation

MUXI validates your configuration files and provides helpful error messages:

```
ValueError: Missing required field: model.provider
ValueError: Invalid field: memory must be an object
ValueError: Invalid field: description must be a string
```
