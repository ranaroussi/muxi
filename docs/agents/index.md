---
layout: default
title: Building Agents
has_children: true
nav_order: 3
permalink: /agents/
---

# Building Agents with MUXI

This section explains how to build AI agents using the MUXI Framework. Agents are the fundamental building blocks of MUXI applications, providing natural language capabilities powered by large language models.

## What is an Agent?

In MUXI, an agent is an AI entity that:

- Is powered by a language model (like OpenAI's GPT-4, Anthropic's Claude, etc.)
- Can understand and generate natural language
- Has optional memory capabilities to remember conversations
- Can be configured with a specific personality and knowledge domain
- Can be customized to suit different tasks

## Creating Your First Agent

<h4>Declarative way</h4>

```yaml
# configs/assistant.yaml

---
agent_id: assistant
description: "A helpful general-purpose assistant that can answer questions and provide information."
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
system_message: "You are a helpful AI assistant that provides clear and accurate information."

```

```python
# app.py

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
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize components
orchestrator = Orchestrator()

# Create a model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create an agent
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful general-purpose assistant that can answer questions and provide information.",
    model=model,
    system_message="You are a helpful AI assistant that provides clear and accurate information."
)

# Chat with the agent
response = orchestrator.chat("assistant", "Hello, what can you help me with?")
print(response)
```

## Agent Capabilities

MUXI agents support a wide range of capabilities:

- **Natural Language Conversation**: Engage in human-like dialogue
- **Memory Systems**: Remember previous interactions and important information
- **Multi-Modal Inputs**: Process text, images, and other data types
- **Personality Customization**: Tailor the agent's tone, style, and behavior
- **Domain Knowledge**: Specialize in particular topics or knowledge areas
- **Multi-Agent Collaboration**: Work together with other agents for complex tasks

## Agent Configuration Options

Agents can be configured with various options:

- **Model Selection**: Choose from multiple LLM providers and models
- **System Messages**: Define the agent's role and behavior
- **Memory Settings**: Configure short-term and long-term memory
- **Temperature Control**: Adjust creativity vs. determinism
- **Response Length**: Control maximum output length
- **Domain-Specific Knowledge**: Add specialized information

## Guides in this Section

Each guide focuses on a specific aspect of building agents:

- [Simple Agent](simple/): Create a basic agent and understand fundamental concepts
- [Agent Configuration](configuration/): Learn about all available configuration options
- [Adding Memory](memory/): Enhance agents with memory capabilities
- [Multi-Agent Systems](multi-agent/): Build systems with multiple collaborating agents

## Example: Creating a Specialized Agent

<h4>Declarative way</h4>

`configs/science_tutor.json`

```json
{
  "agent_id": "science_tutor",
  "description": "A specialized science tutor that can explain concepts clearly and answer related questions.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 1000
  },
  "system_message": "You are a helpful science tutor. Your goal is to explain scientific concepts clearly and accurately, using examples and analogies when appropriate. You should be patient and encouraging, and adapt your explanations to different levels of understanding."
}
```


```python
# app.py

from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add an agent from a configuration file
app.add_agent("science_tutor", "configs/science_tutor.json")

# Chat with the agent
response = await app.chat("Hello, who are you?")
print(response)
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize components
orchestrator = Orchestrator()

# Create a model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.3,
    max_tokens=1000
)

# Create a specialized science tutor agent
orchestrator.create_agent(
    agent_id="science_tutor",
    description="A specialized science tutor that can explain concepts clearly and answer related questions.",
    model=model,
    system_message="You are a helpful science tutor. Your goal is to explain scientific concepts clearly and accurately, using examples and analogies when appropriate. You should be patient and encouraging, and adapt your explanations to different levels of understanding."
)

# Chat with the tutor
response = orchestrator.chat("science_tutor", "Can you explain photosynthesis in simple terms?")
print(response)
```

Ready to build your own agent? Start with the [Simple Agent](simple/) guide.
