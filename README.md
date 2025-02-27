# AI Agent Framework

A powerful and flexible framework for building AI agents with memory, tools, and modern LLM integration.

## Features

- **Modern Control Protocol (MCP)**: Implements the [Model Context Protocol](https://modelcontextprotocol.io/) for standardized communication with LLMs
- **Memory System**: Both short-term (buffer) and long-term (PostgreSQL with pgvector) memory
- **Tool Integration**: Easily add custom tools for your agents
- **Multi-Agent Support**: Create and manage multiple agents with different capabilities
- **Asynchronous API**: Built with asyncio for efficient concurrent operations
- **Real-Time Communication**: WebSocket support for real-time interaction with agents

## Architecture

The framework consists of several key components:

- **Agent**: The main interface for users, combining LLM, memory, and tools
- **Orchestrator**: Manages multiple agents and coordinates their interactions
- **MCP Handler**: Handles communication with LLMs using the Modern Control Protocol
- **Memory**: Buffer memory (FAISS) and long-term memory (PostgreSQL with pgvector)
- **Tools**: Extensible tool system for adding capabilities to agents

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension (for long-term memory)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-agent-framework.git
   cd ai-agent-framework
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://user:password@localhost:5432/ai_agent_db
   ```

## Usage

### Simple Example

```python
import asyncio
from dotenv import load_dotenv

from src.llm import OpenAILLM
from src.memory.buffer import BufferMemory
from src.tools.web_search import WebSearchTool
from src.core.orchestrator import Orchestrator

async def main():
    # Load environment variables
    load_dotenv()

    # Create LLM
    llm = OpenAILLM(model="gpt-4o")

    # Create memory
    memory = BufferMemory()

    # Create tools
    tools = [WebSearchTool()]

    # Create orchestrator and agent
    orchestrator = Orchestrator()
    orchestrator.create_agent(
        agent_id="my_agent",
        llm=llm,
        buffer_memory=memory,
        tools=tools,
        set_as_default=True
    )

    # Run the agent
    response = await orchestrator.run("What's the weather in New York?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Example

```bash
python examples/simple_agent.py
```

### Using the CLI

The framework comes with a rich command-line interface for interacting with agents:

```bash
# Run with default settings
python cli.py

# Run with a custom agent ID
python cli.py --agent-id custom_agent

# Get help
python cli.py --help
```

The CLI provides the following commands:
- `/exit`, `/quit`, `/bye` - Exit the chat
- `/help` - Show help message
- `/clear` - Clear the screen
- `/memory <query>` - Search the agent's memory
- `/tools` - List available tools

### Using the API

The framework includes a REST API server for programmatic interaction with agents:

```bash
# Start the API server
python api.py

# Start on a custom port
python api.py --port 8080

# Enable auto-reload for development
python api.py --reload
```

The API provides the following endpoints:

- `GET /` - Health check
- `POST /agents` - Create a new agent
- `GET /agents` - List all agents
- `DELETE /agents/{agent_id}` - Delete an agent
- `POST /agents/chat` - Chat with an agent
- `POST /agents/memory/search` - Search an agent's memory
- `GET /tools` - List available tools
- `WS /ws` - WebSocket endpoint for real-time communication

The API includes Swagger documentation which can be accessed at `http://localhost:8000/docs` when the server is running.

### Using WebSockets

The framework supports real-time communication with agents using WebSockets:

```bash
# Run the WebSocket client example
python examples/websocket_client.py

# Connect to a specific agent
python examples/websocket_client.py --agent custom_agent

# Connect to a different server
python examples/websocket_client.py --url ws://example.com:8000
```

The WebSocket protocol supports the following message types:

**Client to Server:**
- `subscribe` - Subscribe to an agent's messages
- `chat` - Send a message to an agent

**Server to Client:**
- `response` - A response from an agent
- `agent_thinking` - Indicates the agent is processing
- `agent_done` - Indicates the agent has finished processing
- `error` - An error message

Example WebSocket client code:

```python
import asyncio
import json
import websockets

async def main():
    # Connect to WebSocket
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to an agent
        await websocket.send(json.dumps({
            "type": "subscribe",
            "agent_id": "my_agent"
        }))

        # Send a message
        await websocket.send(json.dumps({
            "type": "chat",
            "message": "Hello, agent!"
        }))

        # Receive responses
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data}")

asyncio.run(main())
```

## Creating Custom Tools

You can create custom tools by inheriting from the `BaseTool` class:

```python
from src.tools.base import BaseTool

class MyCustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Description of what my tool does"

    @property
    def parameters(self) -> dict:
        return {
            "param1": {
                "type": "string",
                "description": "Description of parameter 1"
            }
        }

    @property
    def required_parameters(self) -> list:
        return ["param1"]

    async def execute(self, **kwargs) -> any:
        # Implement your tool logic here
        param1 = kwargs.get("param1")
        return f"Result: {param1}"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
