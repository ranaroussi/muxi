---
layout: default
title: Agents
parent: Core Concepts
has_children: false
nav_order: 1
permalink: /agents/
---

# Agents Overview

Agents are the core component of the MUXI Framework. An agent combines a language model, memory systems, and tools to create an intelligent assistant that can understand and respond to user requests.

## What is an Agent?

An agent is an autonomous entity that:
- Communicates with users via natural language
- Processes requests and generates responses using a language model
- Stores conversation history in memory
- Executes tools to perform actions or retrieve information
- Can maintain separate memory contexts for different users (with Memobase)

## Creating an Agent

Agents can be created through the Orchestrator, which manages multiple agents and their interactions. Here are several ways to create an agent:

### Via Python Code

```python
import asyncio
from src.models import OpenAIModel
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase
from src.tools.web_search import WebSearchTool
from src.tools.calculator import CalculatorTool
from src.core.orchestrator import Orchestrator

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

    # Create tools
    tools = [WebSearchTool(), CalculatorTool()]

    # Create orchestrator and agent
    orchestrator = Orchestrator()
    agent_id = "my_agent"

    # Create a standard agent
    orchestrator.create_agent(
        agent_id=agent_id,
        model=model,
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        tools=tools,
        system_message="You are a helpful AI assistant.",
        set_as_default=True
    )

    # Create a multi-user agent
    orchestrator.create_agent(
        agent_id="multi_user_agent",
        model=model,
        buffer_memory=BufferMemory(),
        long_term_memory=memobase,  # Pass Memobase as long_term_memory
        tools=tools,
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
    "tools": ["web_search", "calculator"]
  }'

# Create a multi-user agent
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "system_message": "You are a helpful AI assistant that remembers user preferences.",
    "tools": ["web_search", "calculator"],
    "use_long_term_memory": true,
    "multi_user_support": true
  }'
```

### Via the CLI

The framework provides a CLI command to create agents:

```bash
# Create a standard agent
python -m src.cli.agent create my_agent --system "You are a helpful AI assistant." --tools web_search calculator

# Create a multi-user agent
python -m src.cli.agent create multi_user_agent --system "You are a helpful AI assistant that remembers user preferences." --tools web_search calculator --multi-user
```

## Agent Parameters

When creating an agent, you can configure various parameters:

- **agent_id** (required): A unique identifier for the agent
- **model** (required): The language model provider to use (e.g., OpenAIModel, AnthropicModel)
- **buffer_memory**: Short-term memory for the current conversation
- **long_term_memory**: Persistent memory for storing information across sessions. Can be a LongTermMemory or Memobase instance for multi-user support.
- **tools**: A list of tools the agent can use
- **system_message**: Instructions that define the agent's behavior
- **set_as_default**: Whether to set this as the default agent for the orchestrator
- **multi_user_support**: Whether to enable user-specific memory via Memobase

## Interacting with an Agent

Once you've created an agent, you can interact with it in several ways:

### Via Python Code

```python
# Continue from previous example

# Standard agent interaction
response = await orchestrator.run(agent_id, "What's the population of Tokyo?")
print(response)

# Using the default agent
response = await orchestrator.run("Tell me about quantum computing")
print(response)

# Multi-user agent interaction
response = await orchestrator.run("multi_user_agent", "My favorite color is blue", user_id=123)
print(response)

# The multi-user agent will remember user-specific information
response = await orchestrator.run("multi_user_agent", "What's my favorite color?", user_id=123)
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

        # Subscribe to an agent
        await websocket.send(json.dumps({
            "type": "subscribe",
            "agent_id": "multi_user_agent"
        }))

        # Wait for subscription confirmation
        response = await websocket.recv()
        print(f"Subscription response: {response}")

        # Send a message
        await websocket.send(json.dumps({
            "type": "chat",
            "agent_id": "multi_user_agent",
            "message": "What is the capital of France?"
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
    tools=[CalculatorTool()],
    system_message="You are an expert coding assistant. Provide clean, efficient code examples and explain your reasoning.",
)

# Create a customer service agent
orchestrator.create_agent(
    agent_id="customer_service",
    model=AnthropicModel(model="claude-3-opus"),
    tools=[WebSearchTool()],
    system_message="You are a friendly customer service representative. Help users with their questions in a polite and helpful manner.",
)
```

### Multi-User Support

You can create agents that support multiple users with separate memory contexts:

```python
from src.memory.memobase import Memobase
from src.memory.long_term import LongTermMemory

# Create a multi-user agent
# Memobase extends LongTermMemory with multi-user capabilities
memobase = Memobase(long_term_memory=LongTermMemory())

orchestrator.create_agent(
    agent_id="customer_service",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=memobase,  # Pass Memobase as long_term_memory
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

3. **Provide relevant tools**: Only give the agent tools it needs for its specific purpose.

4. **Memory management**: For long conversations, ensure your buffer size is adequate. For persistent knowledge, use long-term memory.

5. **Error handling**: Implement proper error handling for tool execution failures.

6. **Regular testing**: Test your agents with diverse inputs to ensure they behave as expected.

7. **User ID management**: For multi-user agents, ensure user IDs are consistently applied across interactions.

8. **Memory partitioning**: Use Memobase for applications where user data isolation is important.

## Troubleshooting

### Agent Not Responding

- Check if the language model API key is valid
- Ensure the agent ID is correct
- Verify that the WebSocket connection is established

### Agent Not Using Tools Correctly

- Check if tools are properly registered
- Review the system message for clear instructions
- Ensure tool parameters are correctly defined

### Memory Issues

- Verify database connection for long-term memory
- Check buffer memory size for token limits
- Ensure memory systems are properly initialized

## Next Steps

After creating your agent, you might want to:

- Add [custom tools](./tools) to extend its capabilities
- Configure [memory systems](./memory) for better recall
- Implement [multi-agent collaboration](./orchestrator) for complex tasks
- Connect to the [WebSocket server](./websocket) for real-time interaction
