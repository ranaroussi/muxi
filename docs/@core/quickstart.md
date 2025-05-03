# Muxi Core Quick Start Guide

This guide will help you quickly get started with Muxi Core for building AI-powered applications.

## Installation

Install the Muxi Core package using pip:

```bash
pip install muxi-core
```

## Basic Usage

### Creating a Simple Agent

Here's how to create a simple agent with Muxi Core:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create a model
model = OpenAIModel(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1000
)

# Create an orchestrator
orchestrator = Orchestrator()

# Create an agent
agent = orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    system_message="You are a helpful assistant.",
    set_as_default=True
)

# Run the agent
async def main():
    response = await orchestrator.run_agent(
        input_text="What is the capital of France?",
        agent_id="assistant"
    )
    print(response)

# Run the async function
import asyncio
asyncio.run(main())
```

### Using Memory Systems

To use memory systems for better conversation context:

```python
import asyncio
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create models
chat_model = OpenAIModel(model="gpt-4o")
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memory systems
buffer_memory = BufferMemory(
    max_size=10,  # Context window size
    buffer_multiplier=10,  # Buffer capacity multiplier
    model=embedding_model
)

# Create orchestrator with memory
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    extraction_model=embedding_model
)

# Create an agent
agent = orchestrator.create_agent(
    agent_id="assistant",
    model=chat_model,
    system_message="You are a helpful assistant with memory.",
    set_as_default=True
)

# Example conversation with memory
async def conversation():
    # First message
    response1 = await orchestrator.run_agent(
        input_text="My name is Alice.",
        agent_id="assistant"
    )
    print(f"Agent: {response1}")

    # Second message (agent should remember the name)
    response2 = await orchestrator.run_agent(
        input_text="What's my name?",
        agent_id="assistant"
    )
    print(f"Agent: {response2}")

# Run the async function
asyncio.run(conversation())
```

### Adding Tool Capabilities with MCP

To give your agent the ability to use tools:

```python
import asyncio
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.agent import MCPServer
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create a model with tool calling capabilities
model = OpenAIModel(
    model="gpt-4o",
    temperature=0.5
)

# Create an orchestrator
orchestrator = Orchestrator()

# Configure an MCP server (example with command-line tools)
mcp_server = MCPServer(
    name="weather",
    url="https://mcp-server.example.com/weather"
)

# Register the MCP server with the orchestrator
async def setup():
    server_id = await orchestrator.register_mcp_server(
        server_id="weather",
        url="https://mcp-server.example.com/weather"
    )

    # Create an agent with tool capabilities
    agent = orchestrator.create_agent(
        agent_id="assistant",
        model=model,
        system_message=(
            "You are an assistant that can check the weather. "
            "Use the weather tool when asked about weather conditions."
        ),
        mcp_server=mcp_server,
        set_as_default=True
    )

    # Example of using the agent with a tool
    response = await orchestrator.run_agent(
        input_text="What's the weather like in New York today?",
        agent_id="assistant"
    )
    print(f"Agent: {response}")

# Run the async function
asyncio.run(setup())
```

## Running a Web API

Create a file named `app.py`:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create a model
model = OpenAIModel(model="gpt-4o")

# Create an orchestrator
orchestrator = Orchestrator()

# Create an agent
agent = orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    system_message="You are a helpful assistant.",
    set_as_default=True
)

# Run the web API
if __name__ == "__main__":
    orchestrator.run(
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

Run the application:

```bash
python app.py
```

Access the API documentation at http://localhost:8000/docs

## Multi-Agent System

Create a more complex system with multiple specialized agents:

```python
import asyncio
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create models
model = OpenAIModel(model="gpt-4o")
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memory
buffer_memory = BufferMemory(
    max_size=10,
    buffer_multiplier=10,
    model=embedding_model
)

# Create orchestrator with memory and routing
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    extraction_model=embedding_model
)

# Initialize the routing model (for intelligent message routing)
orchestrator._initialize_routing_model()

async def setup_agents():
    # Create specialized agents
    general_agent = orchestrator.create_agent(
        agent_id="general",
        model=model,
        system_message="You are a helpful general assistant.",
        description="General-purpose assistant for everyday questions and conversation",
        set_as_default=True
    )

    code_agent = orchestrator.create_agent(
        agent_id="code",
        model=model,
        system_message="You are a coding expert specializing in software development.",
        description="Expert in programming, algorithms, and software engineering"
    )

    math_agent = orchestrator.create_agent(
        agent_id="math",
        model=model,
        system_message="You are a mathematics expert.",
        description="Expert in mathematics, statistics, and numerical problem-solving"
    )

    # Test the routing system
    questions = [
        "How's the weather today?",
        "What's the best way to implement quicksort in Python?",
        "Solve the equation 3x^2 + 2x - 5 = 0"
    ]

    for question in questions:
        # Let the orchestrator choose the best agent
        selected_agent_id = await orchestrator.select_agent_for_message(question)
        print(f"Question: {question}")
        print(f"Selected agent: {selected_agent_id}")

        # Process with the selected agent
        response = await orchestrator.run_agent(
            input_text=question,
            agent_id=selected_agent_id
        )
        print(f"Response: {response}\n")

# Run the async function
asyncio.run(setup_agents())
```

## Next Steps

After getting started, explore these topics:

1. **Long-Term Memory**: Add persistent vector storage for extensive knowledge retention
2. **Multi-User Support**: Set up Memobase for user-specific memory contexts
3. **Custom Model Providers**: Implement your own model provider for specialized models
4. **Advanced Tool Integration**: Develop complex tools using the MCP protocol
5. **Custom Agents**: Create specialized agents with domain-specific knowledge

For more detailed information, refer to the other documentation sections on specific features and components.

## Common Patterns

### Environment Configuration

Use environment variables for configuration:

```bash
# Configure your environment
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@localhost/muxi"
export MONGODB_URI="mongodb://localhost:27017"
```

### Request-Response Flow

The typical flow for processing requests:

1. User sends a message to the orchestrator
2. Orchestrator selects the appropriate agent
3. Agent processes the message, possibly using tools
4. Agent response is returned to the orchestrator
5. Orchestrator updates memory systems
6. Response is returned to the user

### Error Handling

Implement proper error handling for production applications:

```python
try:
    response = await orchestrator.run_agent(input_text="What is the capital of France?")
except Exception as e:
    print(f"Error: {str(e)}")
    response = "I'm sorry, I encountered an error processing your request."
```
