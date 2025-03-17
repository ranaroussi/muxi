---
layout: default
title: Developer Guide
nav_order: 7
has_children: false
permalink: /developer-guide/
---

# Developer Guide

This guide provides information for developers who want to contribute to the MUXI Framework or build extensions on top of it.

## Project Structure

The MUXI Framework follows a modular architecture with the following directory structure:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, tools, LLM interface
│   ├── server/        # REST API and WebSocket server
│   ├── cli/           # Command-line interface
│   ├── web/           # Web user interface
│   └── muxi/          # Meta-package that integrates all components
├── tests/             # Test suite for all components
├── docs/              # Documentation
├── examples/          # Example usage scenarios
└── scripts/           # Utility scripts
```

### Key Components

1. **Core Package**:
   - `Agent`: The main class representing an AI agent
   - `Memory`: Memory systems for storing conversation history
   - `Tool`: Base class for implementing agent tools
   - `MCPHandler`: Handler for Model Context Protocol communications

2. **Server Package**:
   - `Server`: REST API server for agent interaction
   - `WebSocketServer`: Real-time communication server
   - `Router`: Request routing and middleware

3. **CLI Package**:
   - `MuxiCLI`: Command-line interface for interacting with agents
   - `ChatSession`: Terminal-based chat interface

4. **Web Package**:
   - Frontend user interface built with React
   - WebSocket client for real-time communication

## Setting Up Development Environment

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher (for web development)
- Git

### Installation for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/muxi-framework.git
   cd muxi-framework
   ```

2. Run the development installation script:
   ```bash
   ./install_dev.sh
   ```

   This script installs all packages in development mode, allowing you to make changes without reinstalling.

3. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred text editor to add API keys
   ```

4. Run tests to ensure everything is working:
   ```bash
   python -m pytest
   ```

## Working with the Core Package

The core package contains the foundational components of the MUXI Framework.

### Creating a Custom Agent

```python
from muxi.core import Agent
from muxi.core.memory import BufferMemory
from muxi.core.tools import WebSearch

# Create a custom agent
agent = Agent(
    agent_id="research_assistant",
    system_message="You are a research assistant specialized in scientific topics.",
    memory=BufferMemory(max_tokens=4000),
    tools=[WebSearch()]
)

# Process a message
response = await agent.process_message("Tell me about quantum computing.")
print(response.content)
```

### Implementing a Custom Tool

```python
from muxi.core.tools import Tool
from typing import Dict, Any, Optional

class WeatherTool(Tool):
    name = "weather"
    description = "Get current weather information for a location"
    parameters = {
        "location": {
            "type": "string",
            "description": "The city and country/state"
        }
    }

    async def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params.get("location", "")

        # Implementation to fetch weather data
        # ...

        return {
            "temperature": 72,
            "condition": "Sunny",
            "humidity": 45,
            "location": location
        }
```

### Creating a Custom Memory System

```python
from muxi.core.memory import MemoryBase
from typing import List, Dict, Any, Optional

class CustomMemory(MemoryBase):
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.messages = []

    async def add(self, message: Dict[str, Any]) -> None:
        self.messages.append(message)
        if len(self.messages) > self.capacity:
            self.messages.pop(0)

    async def get(self) -> List[Dict[str, Any]]:
        return self.messages

    async def clear(self) -> None:
        self.messages = []
```

## Working with the Server Package

The server package provides RESTful API and WebSocket interfaces for interacting with agents.

### Creating a Custom API Endpoint

```python
from muxi.server import Server
from muxi.core import AgentManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Create a router
router = APIRouter()

# Define a model for request validation
class CustomRequest(BaseModel):
    agent_id: str
    query: str

# Define a new endpoint
@router.post("/custom-endpoint")
async def custom_endpoint(
    request: CustomRequest,
    agent_manager: AgentManager = Depends(lambda: server.agent_manager)
):
    agent = agent_manager.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    result = await agent.process_message(request.query)
    return {
        "agent_id": request.agent_id,
        "result": result.content
    }

# Create a server and include the router
server = Server()
server.app.include_router(router, prefix="/api/v1")

# Run the server
server.start()
```

### Implementing Custom WebSocket Handlers

```python
from muxi.server.websocket import WebSocketManager
from fastapi import WebSocket

class CustomWebSocketManager(WebSocketManager):
    async def handle_custom_message(self, websocket: WebSocket, data: dict):
        # Custom message handling logic
        agent_id = data.get("agent_id")
        message = data.get("message")

        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            await websocket.send_json({"error": "Agent not found"})
            return

        response = await agent.process_message(message)
        await websocket.send_json({
            "type": "custom_response",
            "content": response.content
        })

    async def handle_message(self, websocket: WebSocket, data: dict):
        message_type = data.get("type")

        if message_type == "custom":
            await self.handle_custom_message(websocket, data)
        else:
            await super().handle_message(websocket, data)
```

## Working with the CLI Package

The CLI package provides a command-line interface for interacting with agents.

### Extending the CLI

```python
import click
from muxi.cli.app import cli

@cli.command()
@click.argument("agent_id")
@click.argument("file_path")
def process_file(agent_id, file_path):
    """Process a file with a specific agent."""
    click.echo(f"Processing {file_path} with agent {agent_id}")

    # Implementation to read the file and process it
    with open(file_path, "r") as f:
        content = f.read()

    # Process the file content with the agent
    # ...

    click.echo("File processed successfully.")

# Register the command
if __name__ == "__main__":
    cli()
```

## Working with the Web Package

The web package provides a web-based user interface for interacting with agents.

### Customizing the Web UI

1. Navigate to the web package directory:
   ```bash
   cd packages/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Modify the source files in the `src` directory.

4. Run the development server:
   ```bash
   npm run dev
   ```

## Testing

The MUXI Framework uses pytest for testing. To run tests:

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_agent.py

# Run with coverage
python -m pytest --cov=muxi
```

### Writing Tests

1. Create a new test file in the `tests` directory.
2. Write tests using pytest conventions.
3. Use fixtures for common setup.

Example:

```python
import pytest
from muxi.core import Agent
from muxi.core.mcp import MCPMessage

@pytest.fixture
def test_agent():
    return Agent(
        agent_id="test_agent",
        system_message="You are a test agent."
    )

def test_agent_process_message(test_agent):
    # Mock the LLM response
    test_agent.llm_handler.generate = lambda messages, **kwargs: MCPMessage(
        role="assistant",
        content="This is a test response."
    )

    # Test processing a message
    response = await test_agent.process_message("Hello")
    assert response.content == "This is a test response."
    assert response.role == "assistant"
```

## Documentation

The MUXI Framework uses Jekyll with Just the Docs theme for documentation.

### Building the Documentation

1. Install Ruby and Jekyll:
   ```bash
   gem install jekyll bundler
   ```

2. Navigate to the docs directory:
   ```bash
   cd docs
   ```

3. Install dependencies:
   ```bash
   bundle install
   ```

4. Build and serve the documentation:
   ```bash
   bundle exec jekyll serve
   ```

5. View the documentation at http://localhost:4000

### Adding Documentation

1. Create a new Markdown file in the `docs` directory.
2. Add front matter with appropriate metadata.
3. Write the content using Markdown.

Example:

```markdown
---
layout: default
title: Custom Module
parent: Developer Guide
nav_order: 3
---

# Custom Module

Documentation for the custom module...
```

## Continuous Integration

The MUXI Framework uses GitHub Actions for continuous integration.

### CI Workflow

The CI workflow includes:

1. Running tests on multiple Python versions
2. Checking code style with flake8
3. Building and testing the documentation
4. Publishing packages to PyPI on release

### Local Pre-commit Checks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will run checks before each commit to ensure code quality.

## Versioning and Releases

The MUXI Framework follows semantic versioning (SemVer):

- MAJOR version for incompatible API changes
- MINOR version for adding functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

### Creating a Release

1. Update version numbers in relevant files:
   - `packages/core/pyproject.toml`
   - `packages/server/pyproject.toml`
   - `packages/cli/pyproject.toml`
   - `packages/web/package.json`
   - `packages/muxi/pyproject.toml`

2. Update the CHANGELOG.md file with details of the changes.

3. Create a tag for the release:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

4. The CI pipeline will build and publish the packages.

## Contributing

Contributions to the MUXI Framework are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Support and Community

- GitHub Issues: For bug reports and feature requests
- Discussions: For questions and community support
- Discord: For real-time communication with the community
