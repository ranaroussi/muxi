---
layout: default
title: Simple Agents
parent: Building Agents
nav_order: 1
permalink: /agents/simple/
---

# Simple Agents

This guide will walk you through creating simple AI agents with the MUXI Framework. A simple agent consists of a language model with optional memory and tool capabilities.

## Prerequisites

Before creating an agent, make sure you have:

1. Installed the MUXI Framework: `pip install muxi`
2. Set up any required API keys (e.g., for OpenAI)

## Creating Your First Agent

The simplest way to create an agent is by using the Orchestrator class, which manages agents and their interactions.

### Basic Agent Example

Here's a minimal example of creating an agent with OpenAI:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create a model (make sure to set your API key)
model = OpenAIModel(
    api_key="your_openai_api_key",  # Set your API key or use an environment variable
    model="gpt-4o",                  # Specify the model to use
)

# Create a simple agent
orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    system_message="You are a helpful assistant that provides clear and concise information."
)

# Chat with the agent
response = orchestrator.chat("assistant", "What can you tell me about the MUXI Framework?")
print(response)
```

### Customizing the System Message

The system message defines the agent's behavior and capabilities. Here are some examples of effective system messages:

```python
# For a general assistant
system_message = "You are a helpful, informative assistant that provides accurate information."

# For a specialized coding assistant
system_message = """You are a Python expert who helps with coding tasks.
Always provide code examples and explain your solutions clearly.
Focus on best practices and readability."""

# For a creative writing assistant
system_message = """You are a creative writing assistant with a talent for
generating engaging stories, poems, and other creative content.
You excel at matching the tone and style requested by the user."""
```

## Using Environment Variables

For security, it's recommended to use environment variables for sensitive information like API keys:

```python
import os
from dotenv import load_dotenv
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Load environment variables from .env file
load_dotenv()

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create a model using environment variable
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create a simple agent
orchestrator.create_agent(
    agent_id="assistant",
    model=model
)
```

## Running Agents from Configuration

MUXI supports creating agents from configuration files, which is useful for deployment:

```python
from muxi.core.orchestrator import Orchestrator

# Initialize the orchestrator
orchestrator = Orchestrator()

# Load agent from configuration
config = {
    "agent_id": "assistant",
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "parameters": {
            "temperature": 0.7
        }
    },
    "system_message": "You are a helpful assistant."
}

# Create agent from config
orchestrator.create_agent_from_config(config)

# Chat with the agent
response = orchestrator.chat("assistant", "How can I create a MUXI agent?")
print(response)
```

## Handling Agent Responses

You can interact with the agent and process its responses:

```python
# Single interaction
response = orchestrator.chat("assistant", "What is the capital of France?")
print(f"Agent: {response}")

# Multi-turn conversation
questions = [
    "What is machine learning?",
    "Can you give an example of a machine learning algorithm?",
    "How is it different from deep learning?"
]

for question in questions:
    print(f"User: {question}")
    response = orchestrator.chat("assistant", question)
    print(f"Agent: {response}")
    print("-" * 50)
```

## Command Line Interface

MUXI also provides a command-line interface for quick interaction with agents:

```bash
# Start a chat session with a default agent
muxi chat

# Start a chat session with a specific model
muxi chat --model gpt-4o

# Start a chat session with a custom system message
muxi chat --system "You are a helpful coding assistant."
```

## Next Steps

Now that you've created a simple agent, you might want to:

- Add memory to your agent for persistent conversations - see [Adding Memory](../memory/)
- Create multiple agents for different purposes - see [Multi-Agent Systems](../multi-agent/)
- Configure your agent with specific tools and capabilities - see [Agent Configuration](../configuration/)

## Troubleshooting

### Common Issues

1. **API Key Issues**: If you receive authentication errors, check that your API key is correct and properly set.

2. **Model Availability**: Ensure you have access to the model you're trying to use (e.g., GPT-4o might require special access).

3. **Rate Limiting**: If you encounter rate limiting, consider adding delays between requests or using a different API key.

### Getting Help

If you run into issues, check the [GitHub Issues](https://github.com/ranaroussi/muxi/issues) or create a new issue with detailed information about your problem.
