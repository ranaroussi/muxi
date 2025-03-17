---
layout: default
title: Multi-Agent Systems
parent: Building Agents
nav_order: 2
permalink: /agents/multi-agent/
---

# Multi-Agent Systems

This guide explores how to create multi-agent systems with the MUXI Framework, where multiple specialized agents work together to handle complex tasks.

## Why Use Multiple Agents?

Multi-agent systems offer several advantages:

- **Specialization**: Create agents with different expertise and capabilities
- **Division of Labor**: Distribute complex tasks among specialized agents
- **Scalability**: Handle more requests by distributing them across agents
- **Redundancy**: Provide fallback options if one agent cannot handle a task

## Setting Up a Multi-Agent System

### Basic Multi-Agent Setup

The Orchestrator class makes it easy to create and manage multiple agents:

<h4>Declarative way</h4>


```yaml
# configs/general_assistant.yaml
---
agent_id: general_assistant
description: A helpful assistant for general questions about various topics.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-3.5-turbo
system_message: You are a helpful assistant that can answer general questions.
```


```yaml
# configs/code_assistant.yaml
---
agent_id: code_assistant
description: A specialized coding assistant that can help with programming tasks and code examples.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
system_message: You are a specialized coding assistant with expertise in Python, JavaScript, and other popular languages. Provide code examples and explanations.
```

```yaml
# configs/data_science_assistant.yaml
---
agent_id: data_science_assistant
description: A specialized assistant for data science, statistics, and machine learning topics.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
system_message: You are a specialized data science assistant with expertise in statistics, machine learning, and data analysis. Provide detailed technical advice.
```


```python
# app.py
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agents from individual configuration files
app.add_agent("configs/general_assistant.yaml")
app.add_agent("configs/code_assistant.yaml")
app.add_agent("configs/data_science_assistant.yaml")

# Chat with specific agents
general_response = await app.chat("general_assistant", "What is climate change?")
print(f"General Assistant: {general_response}")

code_response = await app.chat("code_assistant", "How do I implement a binary search in Python?")
print(f"Code Assistant: {code_response}")

data_response = await app.chat("data_science_assistant", "Explain the difference between precision and recall.")
print(f"Data Science Assistant: {data_response}")
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create models for different agents
general_model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)
expert_model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create a general assistant
orchestrator.create_agent(
    agent_id="general_assistant",
    description="A helpful assistant for general questions about various topics.",
    model=general_model,
    system_message="You are a helpful assistant that can answer general questions."
)

# Create a coding assistant
orchestrator.create_agent(
    agent_id="code_assistant",
    description="A specialized coding assistant that can help with programming tasks and code examples.",
    model=expert_model,
    system_message="You are a specialized coding assistant with expertise in Python, JavaScript, and other popular languages. Provide code examples and explanations."
)

# Create a data science assistant
orchestrator.create_agent(
    agent_id="data_science_assistant",
    description="A specialized assistant for data science, statistics, and machine learning topics.",
    model=expert_model,
    system_message="You are a specialized data science assistant with expertise in statistics, machine learning, and data analysis. Provide detailed technical advice."
)

# Chat with specific agents
general_response = orchestrator.chat("general_assistant", "What is climate change?")
print(f"General Assistant: {general_response}")

code_response = orchestrator.chat("code_assistant", "How do I implement a binary search in Python?")
print(f"Code Assistant: {code_response}")

data_response = orchestrator.chat("data_science_assistant", "Explain the difference between precision and recall.")
print(f"Data Science Assistant: {data_response}")
```

## Intelligent Message Routing

MUXI provides intelligent routing to direct messages to the most appropriate agent based on content:

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv

...

# The system will automatically route messages to the appropriate agent
response1 = await app.chat("How do I implement binary search in Python?")
print(f"Response (likely from coding agent): {response1}")

response2 = await app.chat("Tell me about the history of Rome.")
print(f"Response (likely from general agent): {response2}")

response3 = await app.chat("Write a short poem about autumn.")
print(f"Response (likely from creative agent): {response3}")
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

...

# The orchestrator will automatically route the message to the most appropriate agent
response1 = orchestrator.chat(message="How do I implement binary search in Python?")
print(f"Response (likely from coding agent): {response1}")

response2 = orchestrator.chat(message="Tell me about the history of Rome.")
print(f"Response (likely from general agent): {response2}")

response3 = orchestrator.chat(message="Write a short poem about autumn.")
print(f"Response (likely from creative agent): {response3}")
```

## Agent Collaboration

You can implement collaboration between agents by passing information between them:

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv

...

# Use the team for a research task
research_response = await app.chat("researcher", "What are the latest developments in renewable energy?")
print(f"Research findings: {research_response}")

# Use the writer to create content based on research
writing_response = await app.chat("writer", f"Create an article about renewable energy based on this research: {research_response}")
print(f"Draft article: {writing_response}")

# Use the critic to review the article
critique_response = await app.chat("critic", f"Review this article for accuracy and quality: {writing_response}")
print(f"Critique: {critique_response}")
```


## Best Practices for Multi-Agent Systems

1. **Clear Specialization**: Define clear roles and expertise for each agent
2. **Consistent System Messages**: Make system messages detailed and non-overlapping
3. **Appropriate Model Selection**: Use more powerful models for complex tasks
4. **Memory Management**: Consider whether agents should share memory or maintain separate contexts
5. **Error Handling**: Implement fallback mechanisms if routing fails
6. **Observability**: Add logging to track which agent handles which messages

## Next Steps

Now that you've set up a multi-agent system, you might want to:

- Add memory to your agents - see [Adding Memory](../memory/)
- Configure your agents with specific settings - see [Agent Configuration](../configuration/)
- Explore how to connect your agents to external services - see [Using MCP Servers](../../extend/using-mcp/)
