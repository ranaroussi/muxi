---
layout: default
title: Agent Configuration
parent: Building Agents
nav_order: 3
permalink: /agents/configuration
---

# Agent Configuration

This guide covers the various configuration options available when creating MUXI agents.

## Basic Configuration

<h4>Declarative way</h4>

`configs/basic_agent.json`

```json
{
  "agent_id": "assistant",
  "description": "A general-purpose assistant that can help with a wide range of tasks.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "system_message": "You are a helpful assistant."
}
```

`app.py`

```python
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent from configuration
app.add_agent("configs/basic_agent.json")

# Chat with the agent
response = await app.chat("assistant", "Hello, can you help me?")
print(response)
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create agent
orchestrator.create_agent(
    agent_id="assistant",
    description="A general-purpose assistant that can help with a wide range of tasks.",
    model=model,
    system_message="You are a helpful assistant."
)

# Chat with the agent
response = orchestrator.chat("assistant", "Hello, can you help me?")
print(response)
```

## Required Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `agent_id` | Unique identifier for the agent | `"assistant"` |
| `description` | Description of the agent's purpose and capabilities | `"A helpful assistant for answering questions"` |
| `model` | Model configuration including provider and API key | `{"provider": "openai", "api_key": "${OPENAI_API_KEY}", "model": "gpt-4o"}` |

## Model Configuration

### OpenAI Models

<h4>Declarative way (JSON)</h4>

`configs/openai_model.json`

```json
{
  "agent_id": "openai_assistant",
  "description": "An assistant powered by OpenAI models with custom parameters.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 1000,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0
  }
}
```

<h4>Declarative way (YAML)</h4>

`configs/openai_model.yaml`

```yaml
---
agent_id: openai_assistant
description: An assistant powered by OpenAI models with custom parameters.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.7
  top_p: 0.9
  max_tokens: 1000
  presence_penalty: 0
  frequency_penalty: 0
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create an OpenAI model with custom parameters
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.7,
    top_p=0.9,
    max_tokens=1000,
    presence_penalty=0.0,
    frequency_penalty=0.0
)

# Create an agent with the configured model
orchestrator.create_agent(
    agent_id="openai_assistant",
    description="An assistant powered by OpenAI models with custom parameters.",
    model=model
)

# Chat with the OpenAI-powered agent
response = orchestrator.chat("openai_assistant", "Tell me about machine learning.")
print(response)
```

### Anthropic Models

<h4>Declarative way (JSON)</h4>

`configs/anthropic_model.json`

```json
{
  "agent_id": "claude_assistant",
  "description": "An assistant powered by Anthropic's Claude model.",
  "model": {
    "provider": "anthropic",
    "api_key": "${ANTHROPIC_API_KEY}",
    "model": "claude-3-opus-20240229",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

<h4>Declarative way (YAML)</h4>

`configs/anthropic_model.yaml`

```yaml
---
agent_id: claude_assistant
description: An assistant powered by Anthropic's Claude model.
model:
  provider: anthropic
  api_key: "${ANTHROPIC_API_KEY}"
  model: claude-3-opus-20240229
  temperature: 0.7
  max_tokens: 1000
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.anthropic import AnthropicModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create an Anthropic model
model = AnthropicModel(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-opus-20240229",
    temperature=0.7,
    max_tokens=1000
)

# Create an agent with the Anthropic model
orchestrator.create_agent(
    agent_id="claude_assistant",
    description="An assistant powered by Anthropic's Claude model.",
    model=model
)

# Chat with the Claude-powered agent
response = orchestrator.chat("claude_assistant", "Tell me about the history of AI.")
print(response)
```

### Google Models

<h4>Declarative way</h4>

`configs/google_model.json`

```json
{
  "agent_id": "gemini_assistant",
  "description": "An assistant powered by Google's Gemini model.",
  "model": {
    "provider": "google",
    "api_key": "${GOOGLE_API_KEY}",
    "model": "gemini-1.5-pro",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.google import GoogleModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create a Google model
model = GoogleModel(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=1000
)

# Create an agent with the Google model
orchestrator.create_agent(
    agent_id="gemini_assistant",
    description="An assistant powered by Google's Gemini model.",
    model=model
)

# Chat with the Gemini-powered agent
response = orchestrator.chat("gemini_assistant", "Tell me about quantum computing.")
print(response)
```

### Azure OpenAI Models

<h4>Declarative way</h4>

`configs/azure_model.json`

```json
{
  "agent_id": "azure_assistant",
  "description": "An assistant powered by Azure-hosted OpenAI models.",
  "model": {
    "provider": "azure_openai",
    "api_key": "${AZURE_OPENAI_API_KEY}",
    "api_base": "${AZURE_OPENAI_ENDPOINT}",
    "api_version": "2023-12-01-preview",
    "deployment_name": "gpt-4"
  }
}
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.azure_openai import AzureOpenAIModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create an Azure OpenAI model
model = AzureOpenAIModel(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2023-12-01-preview",
    deployment_name="gpt-4"
)

# Create an agent with the Azure model
orchestrator.create_agent(
    agent_id="azure_assistant",
    description="An assistant powered by Azure-hosted OpenAI models.",
    model=model
)

# Chat with the Azure-powered agent
response = orchestrator.chat("azure_assistant", "What are the benefits of cloud computing?")
print(response)
```

### Local Models

<h4>Declarative way</h4>

`configs/local_model.json`

```json
{
  "agent_id": "local_assistant",
  "description": "An assistant powered by a locally-hosted model.",
  "model": {
    "provider": "local",
    "model_path": "/path/to/model",
    "model_type": "llama2"
  }
}
```

<h4>Programmatic way</h4>

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.local import LocalModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create a local model
model = LocalModel(
    model_path="/path/to/model",
    model_type="llama2"
)

# Create an agent with the local model
orchestrator.create_agent(
    agent_id="local_assistant",
    description="An assistant powered by a locally-hosted model.",
    model=model
)

# Chat with the locally-hosted agent
response = orchestrator.chat("local_assistant", "Tell me about open-source AI.")
print(response)
```

## System Message Configuration

The system message provides instructions to the AI about its role and behavior.

<h4>Declarative way</h4>

`configs/system_message.json`

```json
{
  "agent_id": "science_assistant",
  "description": "A specialized assistant for science and technology topics.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "system_message": "You are a helpful assistant specialized in answering questions about science and technology. Keep your answers concise but informative."
}
```


<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create a model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create an agent with specialized system message
orchestrator.create_agent(
    agent_id="science_assistant",
    description="A specialized assistant for science and technology topics.",
    model=model,
    system_message="You are a helpful assistant specialized in answering questions about science and technology. Keep your answers concise but informative."
)

# Chat with the specialized agent
response = orchestrator.chat("science_assistant", "Explain how nuclear fusion works.")
print(response)
```

### Multi-line System Messages

<h4>Declarative way</h4>

`configs/multiline_system_message.json`

```json
{
  "agent_id": "python_assistant",
  "description": "A specialized assistant for Python programming.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "system_message": "You are a Python coding assistant.\n\nYour role is to help users with Python programming questions.\n\nAlways provide explanations along with code examples.\n\nFocus on best practices and readability."
}
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize orchestrator
orchestrator = Orchestrator()

# Create a model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Define a multi-line system message
system_message = """You are a Python coding assistant.

Your role is to help users with Python programming questions.

Always provide explanations along with code examples.

Focus on best practices and readability."""

# Create an agent with the multi-line system message
orchestrator.create_agent(
    agent_id="python_assistant",
    description="A specialized assistant for Python programming.",
    model=model,
    system_message=system_message
)

# Chat with the specialized coding agent
response = orchestrator.chat("python_assistant", "How do I read a CSV file in Python?")
print(response)
```

## Memory Configuration

### Buffer Memory

<h4>Declarative way</h4>

`configs/buffer_memory.json`

```json
{
  "agent_id": "assistant",
  "description": "An assistant with buffer memory for maintaining conversation context.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "buffer_memory": {
    "type": "buffer",
    "max_tokens": 2000,
    "include_system_messages": true
  }
}
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create buffer memory with custom settings
buffer = BufferMemory(
    max_tokens=2000,
    include_system_messages=True
)

# Create an agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    description="An assistant with buffer memory for maintaining conversation context.",
    model=model,
    buffer_memory=buffer
)

# Have a conversation that requires context
orchestrator.chat("assistant", "My name is Sam.")
response = orchestrator.chat("assistant", "Do you remember my name?")
print(response)  # Should mention "Sam"
```

### Long-Term Memory

<h4>Declarative way</h4>

`configs/long_term_memory.json`

```json
{
  "agent_id": "assistant",
  "description": "An assistant with long-term memory capabilities.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "long_term_memory": {
    "type": "long_term",
    "connection_string": "${DATABASE_URL}",
    "collection": "agent_memories"
  }
}
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.long_term import LongTermMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Configure long-term memory
long_term = LongTermMemory(
    connection_string=os.getenv("DATABASE_URL"),
    collection="agent_memories"
)

# Create an agent with long-term memory
orchestrator.create_agent(
    agent_id="assistant",
    description="An assistant with long-term memory capabilities.",
    model=model,
    long_term_memory=long_term
)

# Store information in long-term memory
orchestrator.chat("assistant", "Remember that I like to travel to Japan.")

# Clear buffer memory to simulate a new session
agent = orchestrator.get_agent("assistant")
agent.buffer_memory.clear()

# The agent should still remember the information
response = orchestrator.chat("assistant", "Where do I like to travel?")
print(response)  # Should mention "Japan"
```

## MCP Server Configuration

Agents can connect to MCP (Model Context Protocol) servers to access external tools and capabilities:

```yaml
mcp_servers:
- name: web_search
  url: http://localhost:5001
  credentials:  # Credentials are optional and can be omitted if not needed
  - id: search_api_key
    param_name: api_key
    required: false
    env_fallback: SEARCH_API_KEY
- name: calculator
  command: npx -y @modelcontextprotocol/server-calculator
  # No credentials needed for this server, so the credentials section is omitted
```

MCP servers can use either:
- HTTP transport (specified with `url` parameter)
- Command-line transport (specified with `command` parameter)

Each MCP server can have optional credentials for authentication, though many servers don't require any credentials at all.

## Complete Configuration Example

<h4>Declarative way</h4>

`configs/complete_configuration.yaml`

```json
{
  "agent_id": "expert_assistant",
  "description": "A comprehensive AI assistant with multiple capabilities.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "system_message": "You are an expert assistant with broad knowledge and capabilities. You can help with research, writing, problem-solving, and many other tasks. Always be helpful, accurate, and concise.",
  "buffer_memory": {
    "type": "buffer",
    "max_tokens": 4000
  },
  "long_term_memory": {
    "type": "long_term",
    "connection_string": "${DATABASE_URL}"
  },
  "mcp_servers": [
    {
      "name": "web_search",
      "url": "http://localhost:5001",
      "credentials": [
        {
          "id": "search_api_key",
          "param_name": "api_key",
          "required": true,
          "env_fallback": "SEARCH_API_KEY"
        }
      ]
    },
    {
      "name": "calculator",
      "url": "http://localhost:5002"
    },
    {
      "name": "weather",
      "url": "http://localhost:5003",
      "credentials": [
        {
          "id": "weather_api_key",
          "param_name": "api_key",
          "required": true,
          "env_fallback": "WEATHER_API_KEY"
        }
      ]
    }
  ]
}
```

`app.py`

```python
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add fully-configured agent
app.add_agent("configs/complete_configuration.yaml")

# Chat with the comprehensive agent
response = await app.chat("expert_assistant", "Tell me about recent advances in AI.")
print(response)
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.domain_knowledge import DomainKnowledge

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1000
)

# Configure memory
buffer = BufferMemory(max_tokens=4000)
long_term = LongTermMemory(connection_string=os.getenv("DATABASE_URL"))

# Create a fully-configured agent
agent = orchestrator.create_agent(
    agent_id="expert_assistant",
    description="A comprehensive AI assistant with multiple capabilities.",
    model=model,
    system_message="You are an expert assistant with broad knowledge and capabilities. You can help with research, writing, problem-solving, and many other tasks. Always be helpful, accurate, and concise.",
    buffer_memory=buffer,
    long_term_memory=long_term,
)

# Connect to MCP servers
await agent.connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": os.getenv("SEARCH_API_KEY")}
)

await agent.connect_mcp_server(
    name="calculator",
    url="http://localhost:5002"
)

await agent.connect_mcp_server(
    name="weather",
    url="http://localhost:5003",
    credentials={"api_key": os.getenv("WEATHER_API_KEY")}
)

# Chat with the agent
response = await orchestrator.chat("expert_assistant", "Tell me about recent advances in AI.")
print(response)
```

## Configuration Best Practices

1. **Use Environment Variables for API Keys**
   - Always use environment variables for sensitive information like API keys
   - Example: `"api_key": "${OPENAI_API_KEY}"`
2. **Set Appropriate Temperature**
   - Use lower values (0.0-0.3) for factual tasks
   - Use moderate values (0.3-0.7) for balanced responses
   - Use higher values (0.7-1.0) for creative tasks
3. **Craft Detailed System Messages**
   - Be specific about the agent's role, capabilities, and limitations
   - Include examples of desired behavior when possible
   - Structure long system messages with clear sections

4. **Balance Memory Configuration**
   - Set appropriate token limits for buffer memory based on your model's context window
   - Use long-term memory for important information that needs to persist
   - Use domain knowledge for static information that doesn't change
5. **Use Descriptive Agent IDs**
   - Choose agent IDs that clearly reflect their purpose
   - Follow a consistent naming convention

## Next Steps

Now that you've learned about agent configuration, you can:

- Add memory capabilities to your agent - see [Adding Memory](../memory/)
- Create multi-agent systems - see [Multi-Agent Systems](../multi-agent/)
- Learn about advanced agent capabilities - see [Advanced Features](../../advanced-features/)
