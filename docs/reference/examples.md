---
layout: default
title: Examples Library
parent: Reference
nav_order: 4
permalink: /reference/examples/
---

# Examples Library

This page provides a collection of practical code examples to help you understand how to use the MUXI Framework for common tasks.

## Basic Usage

### Creating a Simple Agent

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel

# Create a simple agent with OpenAI model
agent = Agent(
    name="assistant",
    model=OpenAIModel(
        model="gpt-4o",
        api_key="your-openai-api-key"
    ),
    system_message="You are a helpful assistant that provides concise answers."
)

# Chat with the agent
response = agent.chat("What is the capital of France?")
print(response)  # "The capital of France is Paris."
```

### Using Configuration Files

```python
from muxi import muxi

# Initialize MUXI app
app = muxi()

# Add an agent from a YAML configuration file
app.add_agent("weather", "configs/weather_agent.yaml")

# Chat with the agent
response = app.chat("What's the weather like in New York?", agent_name="weather")
print(response)
```

Example YAML configuration (`configs/weather_agent.yaml`):

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
  buffer_size: 10  # Sets buffer window size to 10
  enable_long_term: true  # Enables long-term memory
mcp_servers:
  - name: weather_api
    url: "http://localhost:5001"
    api_key: "${WEATHER_API_KEY}"
```

## Memory Systems

### Using Buffer Memory

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory

# Create buffer memory with a window size of 5 messages
buffer = BufferMemory(buffer_size=5)

# Create an agent with buffer memory
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant.",
    buffer_memory=buffer
)

# First message
response1 = agent.chat("My name is Alice.")
print(response1)

# Second message (agent will remember the user's name)
response2 = agent.chat("What's my name?")
print(response2)  # Will include "Alice"
```

### Using Long-Term Memory

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.long_term import LongTermMemory

# Create long-term memory with database connection
long_term_memory = LongTermMemory(
    connection_string="postgresql://user:pass@localhost/db"
)

# Create an agent with long-term memory
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant.",
    long_term_memory=long_term_memory
)

# Store important information
response1 = agent.chat("Remember that my favorite color is blue.")
print(response1)

# Later conversation (even after restarting the application)
response2 = agent.chat("What's my favorite color?")
print(response2)  # Will include "blue"
```

### Multi-User Memory with Memobase

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.memobase import Memobase

# Create Memobase for multi-user memory
memobase = Memobase(
    connection_string="postgresql://user:pass@localhost/db"
)

# Create an agent with Memobase
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant.",
    long_term_memory=memobase
)

# Chat with user-specific context
response1 = agent.chat("My name is Alice.", user_id="user1")
response2 = agent.chat("My name is Bob.", user_id="user2")

# Later conversations with separate contexts
response3 = agent.chat("What's my name?", user_id="user1")
print(response3)  # Will include "Alice"

response4 = agent.chat("What's my name?", user_id="user2")
print(response4)  # Will include "Bob"
```

## MCP Servers

### Using an MCP Server

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.mcp import MCPHandler

# Create MCP handler for weather service
weather_mcp = MCPHandler(
    name="weather_api",
    url="http://localhost:5001",
    api_key="your-weather-api-key"
)

# Create an agent with MCP handler
agent = Agent(
    name="weather_assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant that can check the weather.",
    mcp_handlers=[weather_mcp]
)

# Chat with the agent (will use weather MCP when needed)
response = agent.chat("What's the weather like in New York?")
print(response)
```

### Creating a Custom MCP Server

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

class MCPRequest(BaseModel):
    function: str
    parameters: Dict[str, Any]

class MCPResponse(BaseModel):
    result: Dict[str, Any]
    status: str = "success"

@app.post("/")
async def handle_mcp_request(request: MCPRequest):
    if request.function == "getCurrentWeather":
        # Implement weather functionality
        location = request.parameters.get("location", "")
        units = request.parameters.get("units", "metric")

        # In a real implementation, you would call a weather API here
        weather_data = {
            "temperature": 75,
            "conditions": "sunny",
            "humidity": 45,
            "wind_speed": 10
        }

        return MCPResponse(result=weather_data)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown function: {request.function}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
```

## Orchestration

### Multi-Agent System

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel

# Create orchestrator
orchestrator = Orchestrator()

# Add specialized agents
orchestrator.add_agent(
    Agent(
        name="weather_agent",
        model=OpenAIModel("gpt-4o"),
        system_message="You specialize in providing weather information and forecasts."
    )
)

orchestrator.add_agent(
    Agent(
        name="finance_agent",
        model=OpenAIModel("gpt-4o"),
        system_message="You specialize in financial advice and market analysis."
    )
)

# Automatic routing to the appropriate agent
response1 = orchestrator.chat("What's the weather like in New York?")
print(response1)  # Handled by weather_agent

response2 = orchestrator.chat("How are the stock markets doing today?")
print(response2)  # Handled by finance_agent
```

## Domain Knowledge

### Adding Structured Knowledge

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.domain_knowledge import DomainKnowledge

# Create an agent
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant."
)

# Add domain knowledge
agent.add_domain_knowledge({
    "company": {
        "name": "Acme Corp",
        "founded": 1985,
        "products": ["widgets", "gadgets", "tools"],
        "headquarters": "New York"
    },
    "contact": {
        "email": "info@acmecorp.example",
        "phone": "555-123-4567"
    }
})

# Agent can use this knowledge
response = agent.chat("What products does the company sell?")
print(response)  # Will include widgets, gadgets, and tools
```

### Adding Document Knowledge

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel

# Create an agent
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant."
)

# Add domain knowledge from a text file
agent.add_domain_knowledge_from_file("company_profile.txt")

# Agent can use this knowledge
response = agent.chat("What is the company's mission statement?")
print(response)  # Will include information from the document
```

## Communication Interfaces

### REST API Server

```python
from muxi import muxi

# Initialize MUXI app
app = muxi()

# Add agents
app.add_agent("assistant", "configs/assistant.yaml")
app.add_agent("coder", "configs/coder.yaml")

# Start the server
app.run(host="0.0.0.0", port=5050)
```

### WebSocket Client

```python
import asyncio
import websockets
import json

async def chat_with_agent():
    async with websockets.connect("ws://localhost:5050/ws") as websocket:
        # Send a message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "What is the capital of France?",
            "agent": "assistant",
            "user_id": "user123"
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

## CLI Applications

### Interactive CLI

```python
from muxi.cli import cli

if __name__ == "__main__":
    # Start the CLI with interactive mode
    cli()
```

### Programmatic CLI

```python
from muxi.cli.commands import chat_command

if __name__ == "__main__":
    # Send a message and print the response
    response = chat_command(
        message="What is the capital of France?",
        agent="assistant",
        user_id="user123"
    )
    print(response)
```

## Advanced Examples

### Streaming Responses

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel

# Create an agent
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful assistant."
)

# Stream response chunks
for chunk in agent.chat_stream("Tell me a short story about a robot."):
    print(chunk, end="", flush=True)
print()  # Final newline
```

### Custom Tools

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.tools import BaseTool

# Define a custom tool
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform mathematical calculations"

    def execute(self, expression: str) -> str:
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

# Create an agent with the custom tool
agent = Agent(
    name="math_assistant",
    model=OpenAIModel("gpt-4o"),
    system_message="You are a helpful math assistant.",
    tools=[CalculatorTool()]
)

# Agent can use the calculator tool
response = agent.chat("What is 123 * 456?")
print(response)  # Will include correct calculation
```

### Fine-Tuned Models

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel

# Create an agent with a fine-tuned model
agent = Agent(
    name="specialized_assistant",
    model=OpenAIModel(
        model="ft:gpt-3.5-turbo-0613:my-org:my-custom-model:1234",
        api_key="your-openai-api-key"
    ),
    system_message="You are a specialized assistant."
)

# Chat with the agent
response = agent.chat("Can you help me with my query?")
print(response)
```

## Complete Applications

### Q&A System with Web Search

```python
from muxi import muxi
from muxi.core.mcp import MCPHandler

# Initialize MUXI app
app = muxi()

# Create a web search MCP handler
web_search_mcp = MCPHandler(
    name="web_search",
    url="http://localhost:5002",
    api_key="your-search-api-key"
)

# Create a research agent with web search capability
app.add_agent(
    name="researcher",
    system_message="""You are a research assistant that can search the web for information.
    Always use the web_search tool when asked about current events or facts you're uncertain about.""",
    model="gpt-4o",
    mcp_handlers=[web_search_mcp]
)

# Start the CLI
print("Research Assistant (type 'exit' to quit)")
print("----------------------------------------")

while True:
    query = input("\nQuestion: ")
    if query.lower() == "exit":
        break

    response = app.chat(query, agent_name="researcher")
    print(f"\nAnswer: {response}")
```

### Customer Support Bot

```python
from muxi import muxi
from muxi.core.memory.memobase import Memobase

# Initialize MUXI app
app = muxi()

# Create multi-user memory
memobase = Memobase(
    connection_string="postgresql://user:pass@localhost/db"
)

# Create a customer support agent
app.add_agent(
    name="support",
    system_message="""You are a customer support agent for Acme Corp.
    Be polite, helpful, and concise in your responses.
    Reference customer information when available.""",
    model="gpt-4o",
    long_term_memory=memobase
)

# Add company knowledge base
app.add_domain_knowledge_from_file("company_faq.txt")
app.add_domain_knowledge_from_file("product_information.txt")
app.add_domain_knowledge_from_file("return_policy.txt")

# Start server
app.run(host="0.0.0.0", port=5050)
```

## Related Topics

- [Simple Agents](../agents/simple) - Learn more about creating basic agents
- [Multi-Agent Systems](../agents/multi-agent) - Explore multi-agent orchestration
- [Adding Memory](../agents/memory) - Understand memory systems in depth
- [Using MCP Servers](../extend/using-mcp) - Connect agents to external services
