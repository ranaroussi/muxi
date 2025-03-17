# MUXI Framework User Guide

## Creating Agents

MUXI Framework supports two approaches for creating agents:

### Declarative Approach

The declarative approach uses YAML or JSON configuration files. This is the simplest method and recommended for most use cases:

```python
from muxi import muxi

# Initialize MUXI
app = muxi()

# Add an agent from a configuration file
app.add_agent("assistant", "configs/assistant.yaml")
```

### Programmatic Approach

For more advanced use cases or when you need greater control, you can create agents programmatically using the Orchestrator interface:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory

# Create an orchestrator
orchestrator = Orchestrator()

# Create an agent programmatically
agent = orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    buffer_memory=BufferMemory(),
    system_message="You are a helpful AI assistant.",
    description="General-purpose assistant for answering questions"
)

# Connect to an MCP server
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_search_api_key"}
)
```

> **Note:** Both approaches are fully supported and tested. Choose the one that best fits your use case and development style.
