---
layout: default
title: Building Agents
nav_order: 3
has_children: true
permalink: /agents/
---

# Building Agents

This section provides comprehensive guides on building AI agents with the MUXI Framework.

## What Are MUXI Agents?

MUXI agents are AI assistants powered by language models that can:

- Have natural conversations with users
- Remember past interactions through memory systems
- Use specialized tools to perform tasks
- Collaborate with other agents in multi-agent systems

## In This Section

Start with the basics and then explore more advanced features:

- [Simple Agents](./simple/): Learn how to create basic agents and interact with them
- [Multi-Agent Systems](./multi-agent/): Set up multiple specialized agents that work together
- [Adding Memory](./memory/): Enhance your agents with short-term and long-term memory capabilities
- [Agent Configuration](./configuration/): Configure agents with various settings and capabilities

## Key Components of a MUXI Agent

Every MUXI agent consists of several key components:

### 1. Language Model

The core intelligence of an agent comes from its language model (LLM), which can be:
- OpenAI models like GPT-4o
- Anthropic models like Claude
- Local models via Ollama

### 2. Memory Systems

Agents use different types of memory:
- **Buffer Memory**: Short-term memory for recent conversations
- **Long-Term Memory**: Persistent storage for important information
- **Memobase**: Multi-user memory management

### 3. Tools

Agents can use tools to perform specific tasks:
- Web search
- Calculator
- Weather information
- And many others you can define

### 4. System Message

The system message defines the agent's personality, capabilities, and constraints.

## Getting Started

If you're new to the MUXI Framework, we recommend starting with the [Simple Agents](./simple/) guide to learn the basics before moving on to more advanced topics.

## Example: Creating a Basic Agent

Here's a quick example of creating a simple agent:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create a model
model = OpenAIModel(model="gpt-4o")

# Create a simple agent
orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    system_message="You are a helpful assistant."
)

# Chat with the agent
response = orchestrator.chat("assistant", "Hello, how can you help me?")
print(response)
```

## Prerequisites

Before diving into this section, we recommend:
- Completing the [Introduction](/intro/) section
- Having MUXI installed (see [Installation](/intro/installation))
- Understanding the basic concepts of the framework (see [Overview](/intro/overview))

## Next Steps After Building Agents

Once you've mastered building agents, you can:
- [Extend agent capabilities](/extend/) with MCP servers and domain knowledge
- [Deploy your agents](/clients/server) as a server
- [Explore advanced techniques](/technical/agents/fundamentals) in the Technical Deep Dives section
