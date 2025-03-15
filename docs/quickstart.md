---
layout: default
title: Quickstart Guide
parent: Getting Started
has_children: false
nav_order: 2
permalink: /quickstart/
---
# Quick Start Guide

This guide will help you quickly set up and start using MUXI for building AI agents.

## Installation

```bash
# Clone the repository
git clone https://github.com/ranaroussi/muxi.git
cd muxi

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### Creating Agents with Python

```python
from src.core.orchestrator import Orchestrator
from src.models.openai import OpenAIModel
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase

# Create an orchestrator to manage agents
orchestrator = Orchestrator()

# Create a basic agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    system_message="You are a helpful AI assistant."
)

# Send a message to the agent
response = orchestrator.chat("assistant", "Hello, can you help me with a Python question?")
print(response)
```

### Working with Advanced Memory Systems

```python
# Create an agent with long-term memory
long_term_memory = LongTermMemory()
orchestrator.create_agent(
    agent_id="researcher",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=long_term_memory,
    system_message="You are a helpful research assistant."
)

# Create an agent with multi-user support
long_term_memory = LongTermMemory()
memobase = Memobase(long_term_memory=long_term_memory)
orchestrator.create_agent(
    agent_id="multi_user_assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=memobase,
    system_message="You are a helpful assistant that supports multiple users."
)

# Chat with a multi-user agent (specify user_id)
response = orchestrator.chat("multi_user_assistant", "Remember that my name is Alice", user_id=123)
print(response)
```

## Using the Command Line Interface

MUXI comes with a rich command-line interface for interacting with agents:

```bash
# Start the CLI
python -m src.cli

# Start a chat session with an agent
python -m src.cli chat --agent-id assistant

# Send a one-off message to an agent
python -m src.cli send --agent-id assistant "What is the capital of France?"
```

## Starting the API Server

To use the REST API and WebSocket server:

```bash
# Start the API server
python -m src.cli api

# Start both API server and web UI
python -m src.cli run
# or simply
python -m src
```

## Using the WebSocket Interface

Connect to the WebSocket server from JavaScript:

```javascript
// Browser WebSocket client example
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

## Using the REST API

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

## Next Steps

Now that you've set up MUXI and created your first agents, check out these resources to learn more:

- [Architecture Overview](architecture) to understand how MUXI components fit together
- [Agent Guide](agent) for details on agent capabilities and configuration
- [Memory Systems](memory) to learn about different memory options
- [Tools Overview](tools) to extend your agents with additional capabilities
