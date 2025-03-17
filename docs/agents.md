---
layout: default
title: Agents
parent: Core Concepts
has_children: false
nav_order: 1
permalink: /agents/
---

# Agents Overview

Agents are the core component of the MUXI Framework. An agent combines a language model, memory systems, and MCP server connections to create an intelligent assistant that can understand and respond to user requests.

## What is an Agent?

An agent is an autonomous entity that:
- Communicates with users via natural language
- Processes requests and generates responses using a language model
- Stores conversation history in memory
- Connects to MCP servers to perform actions or retrieve information
- Can maintain separate memory contexts for different users (with Memobase)

## Creating an Agent

Agents can be created through the Orchestrator, which manages multiple agents and their interactions. Here are several ways to create an agent:

### Via Python Code

```python
import asyncio
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.mcp.handler import MCPHandler
from muxi.core.orchestrator import Orchestrator

async def create_agent():
    # Create language model
    model = OpenAIModel(model="gpt-4o")

    # Create memory systems
    buffer_memory = BufferMemory(max_tokens=4000)
    long_term_memory = LongTermMemory(
        connection_string="postgresql://user:password@localhost:5432/ai_agent_db",
        table_name="agent_memories"
    )

    # For multi-user support, add Memobase
    memobase = Memobase(long_term_memory=long_term_memory)

    # Create MCP handlers
    web_search_mcp = MCPHandler(url="http://localhost:5001", name="web_search")
    calculator_mcp = MCPHandler(url="http://localhost:5002", name="calculator")
    mcp_servers = [web_search_mcp, calculator_mcp]

    # Create orchestrator and agent
    orchestrator = Orchestrator()
    agent_id = "my_agent"

    # Create a standard agent
    orchestrator.create_agent(
        agent_id=agent_id,
        model=model,
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        mcp_servers=mcp_servers,
        system_message="You are a helpful AI assistant.",
        set_as_default=True
    )

    # Create a multi-user agent
    orchestrator.create_agent(
        agent_id="multi_user_agent",
        model=model,
        buffer_memory=BufferMemory(),
        long_term_memory=memobase,  # Pass Memobase as long_term_memory
        mcp_servers=mcp_servers,
        system_message="You are a helpful AI assistant that remembers user preferences."
    )

    return orchestrator, agent_id

# Usage
async def main():
    orchestrator, agent_id = await create_agent()

    # Standard agent usage
    response = await orchestrator.run(agent_id, "What's the weather in New York?")
    print(response)

    # Multi-user agent usage (with user_id)
    response = await orchestrator.run("multi_user_agent", "My name is Alice", user_id=123)
    print(response)

    # Later, the agent will remember Alice
    response = await orchestrator.run("multi_user_agent", "What's my name?", user_id=123)
    print(response)  # Should respond with "Your name is Alice"

if __name__ == "__main__":
    asyncio.run(main())
```

### Via the REST API

You can create an agent by making a POST request to the API:

```bash
# Create a standard agent
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "system_message": "You are a helpful AI assistant.",
    "mcp_servers": [
      {"name": "web_search", "url": "http://localhost:5001"},
      {"name": "calculator", "url": "http://localhost:5002"}
    ]
  }'

# Create a multi-user agent
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "system_message": "You are a helpful AI assistant that remembers user preferences.",
    "mcp_servers": [
      {"name": "web_search", "url": "http://localhost:5001"},
      {"name": "calculator", "url": "http://localhost:5002"}
    ],
    "use_long_term_memory": true,
    "multi_user_support": true
  }'
```

### Via the CLI

The framework provides a CLI command to create agents:

```bash
# Create a standard agent
muxi agent create my_agent --system "You are a helpful AI assistant." --mcp web_search:http://localhost:5001 calculator:http://localhost:5002

# Create a multi-user agent
muxi agent create multi_user_agent --system "You are a helpful AI assistant that remembers user preferences." --mcp web_search:http://localhost:5001 calculator:http://localhost:5002 --multi-user
```

## Agent Parameters

When creating an agent, you can configure various parameters:

- **agent_id** (required): A unique identifier for the agent
- **model** (required): The language model provider to use (e.g., OpenAIModel, AnthropicModel)
- **buffer_memory**: Short-term memory for the current conversation
- **long_term_memory**: Persistent memory for storing information across sessions. Can be a LongTermMemory or Memobase instance for multi-user support.
- **mcp_servers**: A list of MCP servers the agent can connect to
- **system_message**: Instructions that define the agent's behavior
- **description**: A concise description of the agent's capabilities and purpose, used for intelligent message routing (critical for multi-agent systems)
- **set_as_default**: Whether to set this as the default agent for the orchestrator
- **multi_user_support**: Whether to enable user-specific memory via Memobase

## Intelligent Message Routing

The MUXI framework includes an intelligent message routing system that can automatically direct user messages to the most appropriate agent based on their content and the agents' descriptions.

### How It Works

1. When a user sends a message without specifying an agent, the routing system analyzes the message.
2. The system compares the message content against each agent's description.
3. Using a dedicated LLM (configurable via environment variables), it selects the most appropriate agent.
4. The message is then sent to the selected agent for processing.

### Configuring Agent Descriptions

For effective routing, provide clear and specific descriptions for each agent:

```python
# Create a weather-focused agent
orchestrator.create_agent(
    agent_id="weather_assistant",
    model=OpenAIModel(model="gpt-4o"),
    description="Specialized in providing weather forecasts, answering questions about climate and weather phenomena, and reporting current conditions in various locations.",
    # ... other parameters
)

# Create a finance-focused agent
orchestrator.create_agent(
    agent_id="finance_assistant",
    model=OpenAIModel(model="gpt-4o"),
    description="Expert in financial analysis, investment strategies, market trends, stock recommendations, and personal finance advice.",
    # ... other parameters
)
```

### Configuration via YAML/JSON

You can also specify descriptions in configuration files:

```yaml
name: travel_assistant
description: "Specialized in travel recommendations, flight and hotel bookings, tourist attractions, and travel planning."
system_message: "You are a helpful travel assistant."
# ... other configuration
```

### Routing Configuration

The routing system can be configured through environment variables:

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

## Interacting with an Agent

Once you've created an agent, you can interact with it in several ways:

### Via Python Code with Configuration-based Approach (Recommended)

```python
from muxi import muxi

# Initialize MUXI
mx = muxi()

# Add agents from configuration files
mx.add_agent("assistant", "configs/general_assistant.yaml")
mx.add_agent("weather", "configs/weather_agent.yaml")
mx.add_agent("finance", "configs/finance_agent.yaml")

# Let the orchestrator automatically select the appropriate agent (recommended)
response = mx.chat("What's the weather in New York?")
print(response)  # Will likely be handled by the weather agent

# Or chat with a specific agent if needed (optional)
response = mx.chat("Tell me about investment strategies", agent_name="finance")
print(response)

# With user-specific context
response = mx.chat("What's my favorite color?", user_id=123)
print(response)  # Will use the user's context if available
```

### Via Python Code with Traditional Approach

```python
# Continue from previous example

# Standard agent interaction
response = await orchestrator.chat(message="What's the population of Tokyo?")
print(response)  # Orchestrator will select the appropriate agent

# Explicitly specifying an agent
response = await orchestrator.chat(message="Tell me about quantum computing", agent_id=agent_id)
print(response)

# Multi-user agent interaction
response = await orchestrator.chat(message="My favorite color is blue", user_id=123)
print(response)

# The multi-user agent will remember user-specific information
response = await orchestrator.chat(message="What's my favorite color?", user_id=123)
print(response)  # Should respond with "Your favorite color is blue"
```

### Via the REST API

```bash
# Chat with a specific agent
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "message": "What is the capital of France?"
  }'

# Chat with a multi-user agent (specify user_id)
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "message": "What is the capital of France?",
    "user_id": 123
  }'

# Search memory for a multi-user agent
curl -X POST http://localhost:5050/agents/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "query": "favorite color",
    "user_id": 123
  }'
```

### Via WebSocket

```python
import asyncio
import json
import websockets

async def chat_with_agent():
    uri = "ws://localhost:5050/ws"
    async with websockets.connect(uri) as websocket:
        # Set user ID for multi-user agents
        await websocket.send(json.dumps({
            "type": "set_user",
            "user_id": 123
        }))

        # Subscribe to an agent (optional - if you want messages from a specific agent)
        await websocket.send(json.dumps({
            "type": "subscribe",
            "agent_id": "multi_user_agent"
        }))

        # Wait for subscription confirmation
        response = await websocket.recv()
        print(f"Subscription response: {response}")

        # Send a message without specifying an agent (automatic selection)
        await websocket.send(json.dumps({
            "type": "chat",
            "message": "What is the capital of France?"
        }))

        # Or send a message to a specific agent
        await websocket.send(json.dumps({
            "type": "chat",
            "message": "What's the weather forecast?",
            "agent_id": "weather_agent"
        }))

        # Receive response
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data}")

            if data["type"] == "agent_done":
                break

asyncio.run(chat_with_agent())
```

## Advanced Agent Features

### Custom System Messages

You can customize your agent's behavior by providing a detailed system message:

```python
system_message = """
You are an AI assistant specialized in helping with scientific research.
- Always cite your sources
- When uncertain, acknowledge the limits of your knowledge
- Provide step-by-step explanations for complex topics
- Use LaTeX formatting for mathematical equations
"""

orchestrator.create_agent(
    agent_id="science_agent",
    model=model,
    system_message=system_message,
    # Other parameters...
)
```

### Specialized Agents

You can create specialized agents for specific tasks:

```python
# Create a programming assistant
orchestrator.create_agent(
    agent_id="code_assistant",
    model=OpenAIModel(model="gpt-4o"),
    mcp_servers=[calculator_mcp],
    system_message="You are an expert coding assistant. Provide clean, efficient code examples and explain your reasoning.",
)

# Create a customer service agent
orchestrator.create_agent(
    agent_id="customer_service",
    model=AnthropicModel(model="claude-3-opus"),
    mcp_servers=[web_search_mcp],
    system_message="You are a friendly customer service representative. Help users with their questions in a polite and helpful manner.",
)
```

### Multi-User Support

You can create agents that support multiple users with separate memory contexts:

```python
from muxi.core.memory.memobase import Memobase
from muxi.core.memory.long_term import LongTermMemory

# Create a multi-user agent
# Memobase extends LongTermMemory with multi-user capabilities
memobase = Memobase(long_term_memory=LongTermMemory())

orchestrator.create_agent(
    agent_id="customer_service",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=memobase,  # Pass Memobase as long_term_memory
    mcp_servers=[web_search_mcp, calculator_mcp],
    system_message="""
    You are a customer service assistant that helps different customers.
    Maintain a personalized conversation with each user.
    Remember their preferences and previous interactions.
    """
)

# Different users interact with the same agent
user1_response = await orchestrator.chat("customer_service", "My name is John and I need help with my order #12345", user_id=1001)
user2_response = await orchestrator.chat("customer_service", "I'm Sarah and I have a question about your return policy", user_id=1002)

# Later interactions - the agent remembers each user
user1_followup = await orchestrator.chat("customer_service", "Any updates on my order?", user_id=1001)
# Agent will remember John and order #12345

user2_followup = await orchestrator.chat("customer_service", "Thanks for the information yesterday", user_id=1002)
# Agent will remember Sarah and the return policy discussion
```

## Best Practices

1. **Choose the right language model**: Different tasks require different language models. For complex reasoning, use advanced models like GPT-4 or Claude 3.

2. **Craft effective system messages**: Be specific about the agent's role, tone, and constraints.

3. **Select relevant MCP servers**: Only connect the agent to MCP servers it needs for its specific purpose.

4. **Memory management**: For long conversations, ensure your buffer size is adequate. For persistent knowledge, use long-term memory.

5. **Error handling**: Implement proper error handling for MCP server communication failures.

6. **Regular testing**: Test your agents with diverse inputs to ensure they behave as expected.

7. **User ID management**: For multi-user agents, ensure user IDs are consistently applied across interactions.

8. **Memory partitioning**: Use Memobase for applications where user data isolation is important.

## Troubleshooting

### Agent Not Responding

- Check if the language model API key is valid
- Ensure the agent ID is correct
- Verify that the WebSocket connection is established

### Agent Not Using MCP Servers Correctly

- Check if MCP servers are properly connected and running
- Review the system message for clear instructions
- Ensure MCP server credentials are correctly configured

### Memory Issues

- Verify database connection for long-term memory
- Check buffer memory size for token limits
- Ensure memory systems are properly initialized

## Next Steps

After creating your agent, you might want to:

- Add [custom MCP servers](./mcp-servers) to extend its capabilities
- Configure [memory systems](./memory) for better recall
- Implement [multi-agent collaboration](./orchestrator) for complex tasks
- Connect to the [WebSocket server](./websocket) for real-time interaction
