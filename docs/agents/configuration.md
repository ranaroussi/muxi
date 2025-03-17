---
layout: default
title: Agent Configuration
parent: Building Agents
nav_order: 4
permalink: /agents/configuration/
---

# Agent Configuration

This guide explains how to configure MUXI agents with various settings, tools, and capabilities to meet your specific requirements.

## Configuration Methods

MUXI supports multiple ways to configure agents:

1. **Programmatic Configuration**: Direct configuration via code
2. **Declarative Configuration**: Using JSON or YAML files
3. **Environment Variables**: Setting defaults via environment variables

## Basic Agent Configuration

When creating an agent, you can specify various parameters:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

orchestrator = Orchestrator()

# Create an agent with basic configuration
orchestrator.create_agent(
    agent_id="assistant",                    # Unique identifier for the agent
    model=OpenAIModel(model="gpt-4o"),       # Language model to use
    system_message="You are a helpful assistant that specializes in technology.",  # Personality/role
    temperature=0.7,                         # Creativity level (0.0-1.0)
    max_tokens=1000,                         # Maximum response length
    streaming=True                           # Enable streaming responses
)
```

## Model Configuration

MUXI supports different language model providers:

### OpenAI Models

```python
from muxi.core.models.openai import OpenAIModel

# Configure an OpenAI model
model = OpenAIModel(
    api_key="your_api_key_here",             # API key (or use environment variable)
    model="gpt-4o",                          # Model name
    temperature=0.7,                         # Creativity level
    max_tokens=1000,                         # Max response length
    top_p=0.9,                               # Nucleus sampling parameter
    presence_penalty=0.1,                    # Penalize repeated tokens
    frequency_penalty=0.1,                   # Penalize frequent tokens
    timeout=30,                              # Request timeout in seconds
    retry_attempts=3                         # Number of retries on failure
)
```

### Anthropic Models

```python
from muxi.core.models.anthropic import AnthropicModel

# Configure an Anthropic model
model = AnthropicModel(
    api_key="your_api_key_here",             # API key
    model="claude-3-opus-20240229",          # Model name
    temperature=0.7,                         # Creativity level
    max_tokens=1000                          # Max response length
)
```

### Local Models (Ollama)

```python
from muxi.core.models.ollama import OllamaModel

# Configure a local model via Ollama
model = OllamaModel(
    model="llama3",                          # Model name
    host="http://localhost:11434",           # Ollama host
    temperature=0.7,                         # Creativity level
    max_tokens=1000                          # Max response length
)
```

## Tool Configuration

Equip your agents with tools to perform specific actions:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.tools.web_search import WebSearch
from muxi.core.tools.calculator import Calculator
from muxi.core.tools.weather import WeatherTool

# Create tools with configuration
web_search = WebSearch(
    api_key="your_search_api_key",           # API key for search service
    search_engine="google",                  # Search engine to use
    max_results=5                            # Maximum number of results
)

calculator = Calculator()

weather_tool = WeatherTool(
    api_key="your_weather_api_key",          # Weather service API key
    units="metric"                           # Units for temperature (metric/imperial)
)

# Create an agent with tools
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    tools=[web_search, calculator, weather_tool]
)
```

## Memory Configuration

Configure memory systems to enhance your agent's capabilities:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory

# Configure buffer memory
buffer = BufferMemory(
    max_tokens=4000,                         # Maximum tokens to store
    include_system_messages=True,            # Include system messages in context
    include_tool_calls=True                  # Include tool usage in context
)

# Configure long-term memory
long_term = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/muxidb",
    collection="agent_memories",             # Collection/table name
    embedding_model="text-embedding-3-small", # Embedding model to use
    embedding_dimensions=1536,               # Dimensions of embeddings
    similarity_threshold=0.75                # Minimum similarity for retrieval
)

# Create an agent with configured memory
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=buffer,
    long_term_memory=long_term
)
```

## Declarative Configuration

For easier deployment and management, configure agents using YAML or JSON:

### JSON Configuration Example

```python
import json
from muxi.core.orchestrator import Orchestrator

# Load configuration from a JSON file
with open("agent_config.json", "r") as f:
    config = json.load(f)

# Create orchestrator and load agents
orchestrator = Orchestrator()
for agent_config in config["agents"]:
    orchestrator.create_agent_from_config(agent_config)
```

Example `agent_config.json`:

```json
{
  "agents": [
    {
      "agent_id": "assistant",
      "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "parameters": {
          "temperature": 0.7,
          "max_tokens": 1000
        }
      },
      "system_message": "You are a helpful assistant specializing in technology.",
      "tools": [
        {
          "type": "web_search",
          "config": {
            "api_key": "${SEARCH_API_KEY}",
            "max_results": 5
          }
        },
        {
          "type": "calculator"
        }
      ],
      "memory": {
        "buffer": {
          "max_tokens": 4000
        },
        "long_term": {
          "connection_string": "${DATABASE_URL}",
          "collection": "assistant_memories"
        }
      }
    },
    {
      "agent_id": "coding_assistant",
      "model": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "parameters": {
          "temperature": 0.2,
          "max_tokens": 1500
        }
      },
      "system_message": "You are a specialized coding assistant that helps with programming tasks.",
      "tools": [
        {
          "type": "code_interpreter"
        },
        {
          "type": "repository_search"
        }
      ]
    }
  ]
}
```

### YAML Configuration Example

```python
import yaml
from muxi.core.orchestrator import Orchestrator

# Load configuration from a YAML file
with open("agent_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create orchestrator and load agents
orchestrator = Orchestrator()
for agent_config in config["agents"]:
    orchestrator.create_agent_from_config(agent_config)
```

Example `agent_config.yaml`:

```yaml
agents:
  - agent_id: assistant
    model:
      provider: openai
      model: gpt-4o
      parameters:
        temperature: 0.7
        max_tokens: 1000
    system_message: You are a helpful assistant specializing in technology.
    tools:
      - type: web_search
        config:
          api_key: ${SEARCH_API_KEY}
          max_results: 5
      - type: calculator
    memory:
      buffer:
        max_tokens: 4000
      long_term:
        connection_string: ${DATABASE_URL}
        collection: assistant_memories

  - agent_id: coding_assistant
    model:
      provider: anthropic
      model: claude-3-opus-20240229
      parameters:
        temperature: 0.2
        max_tokens: 1500
    system_message: You are a specialized coding assistant that helps with programming tasks.
    tools:
      - type: code_interpreter
      - type: repository_search
```

## Environment Variables

Configure MUXI with environment variables for secure deployment:

```bash
# Model API keys
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"

# Database configuration
export MUXI_DATABASE_URL="postgresql://username:password@localhost:5432/muxidb"

# Tool API keys
export MUXI_SEARCH_API_KEY="your_search_key"
export MUXI_WEATHER_API_KEY="your_weather_key"

# Default configuration
export MUXI_DEFAULT_MODEL="gpt-4o"
export MUXI_ENABLE_TOOLS="true"
export MUXI_USE_LONG_TERM_MEMORY="true"
```

You can then load these variables in your code:

```python
import os
from dotenv import load_dotenv
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Load environment variables from .env file if present
load_dotenv()

# Create model using environment variables
model = OpenAIModel(
    # API key will be automatically loaded from OPENAI_API_KEY
    model=os.getenv("MUXI_DEFAULT_MODEL", "gpt-4o")
)

# Create orchestrator
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="assistant",
    model=model
)
```

## Advanced Configuration

### Streaming Configuration

Configure how responses are streamed to clients:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Configure streaming behavior
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="streaming_agent",
    model=OpenAIModel(model="gpt-4o"),
    streaming=True,                          # Enable streaming
    stream_chunk_size=20,                    # Characters per chunk
    stream_delay=0.02                        # Delay between chunks (seconds)
)

# Use with a streaming handler
def stream_handler(chunk):
    print(chunk, end="", flush=True)

# Get streaming response
orchestrator.chat(
    "streaming_agent",
    "Write a short story about a robot.",
    stream_handler=stream_handler
)
```

### Rate Limiting Configuration

Configure rate limiting to manage API usage:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.rate_limiter import RateLimiter

# Configure rate limiting
rate_limiter = RateLimiter(
    requests_per_minute=60,                 # Maximum requests per minute
    tokens_per_minute=100000,               # Maximum tokens per minute
    max_retries=3,                          # Retries on rate limit errors
    retry_delay=5.0                         # Seconds between retries
)

# Create model with rate limiter
model = OpenAIModel(
    model="gpt-4o",
    rate_limiter=rate_limiter
)

# Create agent with rate-limited model
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="rate_limited_agent",
    model=model
)
```

### Multi-Modal Configuration

Configure agents to handle images and other media:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Create multi-modal agent
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="vision_agent",
    model=OpenAIModel(
        model="gpt-4o",                     # Model that supports vision
        vision_enabled=True,                # Enable vision capabilities
        max_image_size=4096,                # Maximum image dimension in pixels
        image_detail="high"                 # Image detail level (low/medium/high)
    )
)

# Use the agent with an image
response = orchestrator.chat(
    "vision_agent",
    "What's in this image?",
    image_paths=["path/to/image.jpg"]       # Local image path
)

# Or with a URL
response = orchestrator.chat(
    "vision_agent",
    "What's in this image?",
    image_urls=["https://example.com/image.jpg"]  # Remote image URL
)
```

## Configuration Best Practices

1. **Use Environment Variables for Secrets**: Never hardcode API keys or credentials

2. **Declarative Configuration for Production**: Use YAML/JSON configs for deployment environments

3. **Appropriate Tool Selection**: Only include tools that agents actually need

4. **Memory Optimization**: Configure memory systems according to your use case

5. **Model Selection**: Choose the right model for your task complexity

6. **Environment-Specific Configs**: Create different configs for development, testing, and production

7. **Centralized Configuration**: Store common settings in shared config files

8. **Version Control**: Keep configuration files in version control with secrets redacted

## Troubleshooting Configuration Issues

### Common Issues and Solutions

1. **Missing API Keys**: Ensure API keys are correctly set in environment variables

2. **Model Compatibility**: Verify that the selected model supports the required capabilities (e.g., vision, tool use)

3. **Database Connection**: Check that database credentials and connection strings are correct

4. **Tool Configuration**: Ensure tools have the necessary parameters and API keys

5. **Rate Limiting**: If experiencing rate limiting errors, adjust rate limiter settings

### Debugging Configuration

To debug configuration issues, you can print the configuration:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
import json

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(model="gpt-4o")

# Create an agent
orchestrator.create_agent(
    agent_id="assistant",
    model=model
)

# Get agent configuration (with sensitive data masked)
config = orchestrator.get_agent_config("assistant", mask_secrets=True)
print(json.dumps(config, indent=2))
```

## Next Steps

Now that you've learned how to configure agents, you might want to:

- Learn about multi-agent systems - see [Multi-Agent Systems](../multi-agent/)
- Add memory to your agents - see [Adding Memory](../memory/)
- Explore how to connect your agents to external services - see [Using MCP Servers](../../extend/using-mcp/)
