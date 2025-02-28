# Agent

Agents are the core component of the AI Agent Framework. An agent combines a Large Language Model (LLM), memory systems, and tools to create an intelligent assistant that can understand and respond to user requests.

## What is an Agent?

An agent is an autonomous entity that:
- Communicates with users via natural language
- Processes requests and generates responses using an LLM
- Stores conversation history in memory
- Executes tools to perform actions or retrieve information

## Creating an Agent

Agents can be created through the Orchestrator, which manages multiple agents and their interactions. Here are several ways to create an agent:

### Via Python Code

```python
import asyncio
from src.llm import OpenAILLM
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.tools.web_search import WebSearchTool
from src.tools.calculator import CalculatorTool
from src.core.orchestrator import Orchestrator

async def create_agent():
    # Create LLM
    llm = OpenAILLM(model="gpt-4o")

    # Create memory systems
    buffer_memory = BufferMemory(max_tokens=4000)
    long_term_memory = LongTermMemory(
        connection_string="postgresql://user:password@localhost:5432/ai_agent_db",
        table_name="agent_memories"
    )

    # Create tools
    tools = [WebSearchTool(), CalculatorTool()]

    # Create orchestrator and agent
    orchestrator = Orchestrator()
    agent_id = "my_agent"

    orchestrator.create_agent(
        agent_id=agent_id,
        llm=llm,
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        tools=tools,
        system_message="You are a helpful AI assistant.",
        set_as_default=True
    )

    return orchestrator, agent_id

# Usage
async def main():
    orchestrator, agent_id = await create_agent()
    response = await orchestrator.run(agent_id, "What's the weather in New York?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Via the REST API

You can create an agent by making a POST request to the API:

```bash
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "system_message": "You are a helpful AI assistant.",
    "tools": ["web_search", "calculator"]
  }'
```

### Via the CLI

The framework provides a CLI command to create agents:

```bash
python -m src.cli.agent create my_agent --system "You are a helpful AI assistant." --tools web_search calculator
```

## Agent Parameters

When creating an agent, you can configure various parameters:

- **agent_id** (required): A unique identifier for the agent
- **llm** (required): The LLM provider to use (e.g., OpenAILLM, AnthropicLLM)
- **buffer_memory**: Short-term memory for the current conversation
- **long_term_memory**: Persistent memory for storing information across sessions
- **tools**: A list of tools the agent can use
- **system_message**: Instructions that define the agent's behavior
- **set_as_default**: Whether to set this as the default agent for the orchestrator

## Interacting with an Agent

Once you've created an agent, you can interact with it in several ways:

### Via Python Code

```python
# Continue from previous example
response = await orchestrator.run(agent_id, "What's the population of Tokyo?")
print(response)

# Using the default agent
response = await orchestrator.run("Tell me about quantum computing")
print(response)
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

# Chat with the default agent
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?"
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
        # Subscribe to an agent
        await websocket.send(json.dumps({
            "type": "subscribe",
            "agent_id": "my_agent"
        }))

        # Wait for subscription confirmation
        response = await websocket.recv()
        print(f"Subscription response: {response}")

        # Send a message
        await websocket.send(json.dumps({
            "type": "chat",
            "agent_id": "my_agent",
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
    llm=llm,
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
    llm=OpenAILLM(model="gpt-4o"),
    tools=[CalculatorTool()],
    system_message="You are an expert coding assistant. Provide clean, efficient code examples and explain your reasoning.",
)

# Create a customer service agent
orchestrator.create_agent(
    agent_id="customer_service",
    llm=AnthropicLLM(model="claude-3-opus"),
    tools=[WebSearchTool()],
    system_message="You are a friendly customer service representative. Help users with their questions in a polite and helpful manner.",
)
```

## Best Practices

1. **Choose the right LLM**: Different tasks require different language models. For complex reasoning, use advanced models like GPT-4 or Claude 3.

2. **Craft effective system messages**: Be specific about the agent's role, tone, and constraints.

3. **Provide relevant tools**: Only give the agent tools it needs for its specific purpose.

4. **Memory management**: For long conversations, ensure your buffer size is adequate. For persistent knowledge, use long-term memory.

5. **Error handling**: Implement proper error handling for tool execution failures.

6. **Regular testing**: Test your agents with diverse inputs to ensure they behave as expected.

## Troubleshooting

### Agent Not Responding

- Check if the LLM API key is valid
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

- Add [custom tools](./tools.md) to extend its capabilities
- Configure [memory systems](./memory.md) for better recall
- Implement [multi-agent collaboration](./orchestrator.md) for complex tasks
- Connect to the [WebSocket server](./websocket.md) for real-time interaction
