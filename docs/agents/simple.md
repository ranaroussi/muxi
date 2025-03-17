---
layout: default
title: Simple Agent
parent: Building Agents
nav_order: 1
permalink: /agents/simple/
---

# Creating a Simple Agent

This guide walks you through creating a basic agent using the MUXI Framework.

## Basic Agent Creation

<h4>Declarative way</h4>

```yaml
# configs/assistant.yaml

---
agent_id: assistant
description: A helpful assistant that answers questions and performs tasks.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
system_message: You are a helpful AI assistant.

```


```python
# app.py

from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add an agent from a configuration file
app.add_agent("assistant", "configs/assistant.yaml")

# Chat with the agent
response = await app.chat("Hello, who are you?")
print(response)
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create an OpenAI model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create an agent
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant that answers questions and performs tasks.",
    model=model,
    system_message="You are a helpful AI assistant."
)

# Chat with the agent
response = orchestrator.chat("Hello, who are you?")
print(response)
```

## Customizing Agent Settings

<h4>Declarative way</h4>

```yaml
---
agent_id: creative_writer
description: A creative assistant that can help with writing and generating creative
  content.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
  temperature: 0.8
  top_p: 0.9
  max_tokens: 1000
system_message: You are a creative assistant specializing in fiction writing. Help
  users craft stories, characters, and engaging narratives.
```

<h4>Programmatic way</h4>

```python
# ...

# Create a model with custom parameters
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.8,
    top_p=0.9,
    max_tokens=1000
)

# Create a creative agent
orchestrator.create_agent(
    agent_id="creative_writer",
    description="...",
    model=model,
    system_message="..."
)

# ...
```

## Using Different Model Providers

MUXI supports multiple model providers including OpenAI, Anthropic, Google, and more.

### Anthropic Agent Example

<h4>Declarative way</h4>

```yaml
---
agent_id: claude
description: An intelligent assistant powered by Claude.
model:
  provider: anthropic
  api_key: "${ANTHROPIC_API_KEY}"
  model: claude-3-opus-20240229
system_message: You are Claude, a helpful AI assistant created by Anthropic.

```

<h4>Programmatic way</h4>

```python
# Create an Anthropic model
model = AnthropicModel(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-opus-20240229"
)

# Create a Claude agent
orchestrator.create_agent(
    agent_id="claude",
    description="...",
    model=model,
    system_message="..."
)
```

### Google Agent Example

<h4>Declarative way</h4>

```yaml
---
agent_id: gemini
description: An intelligent assistant powered by Google's Gemini model.
model:
  provider: google
  api_key: "${GOOGLE_API_KEY}"
  model: gemini-1.5-pro
system_message: You are Gemini, a helpful AI assistant created by Google.
```

<h4>Programmatic way</h4>

```python
# Create a Google model
model = GoogleModel(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-pro"
)

# Create a Gemini agent
orchestrator.create_agent(
    agent_id="gemini",
    description="...",
    model=model,
    system_message="..."
)
```

## Azure OpenAI Support

MUXI also supports Azure OpenAI services:

<h4>Declarative way</h4>

```yaml
---
agent_id: azure_assistant
description: A helpful assistant using Azure-hosted OpenAI models.
model:
  provider: azure_openai
  api_key: "${AZURE_OPENAI_API_KEY}"
  api_version: 2023-12-01-preview
  api_base: "${AZURE_OPENAI_ENDPOINT}"
  deployment_name: gpt-4
system_message: You are a helpful AI assistant running on Azure infrastructure.
```

<h4>Programmatic way</h4>

```python
# Create an Azure OpenAI model
model = AzureOpenAIModel(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name="gpt-4"
)

# Create an Azure agent
orchestrator.create_agent(
    agent_id="azure_assistant",
    description="...",
    model=model,
    system_message="..."
)
```

## Local Models

MUXI supports running models locally using the local provider:

<h4>Declarative way</h4>

```yaml
---
agent_id: local_assistant
description: A locally-hosted AI assistant running on your own hardware.
model:
  provider: local
  model_path: "/path/to/local/model"
  model_type: llama2
  context_window: 4096
system_message: You are a locally-hosted AI assistant.
```

<h4>Programmatic way</h4>

```python
# Create a local model
model = LocalModel(
    model_path="/path/to/local/model",
    model_type="llama2",
    context_window=4096
)

# Create a local agent
orchestrator.create_agent(
    agent_id="local_assistant",
    description="...",
    model=model,
    system_message="..."
)
```

## Next Steps

Now that you've created a simple agent, you can:

- Learn how to configure agent settings in detail - see [Agent Configuration](../configuration/)
- Add memory capabilities to your agent - see [Adding Memory](../memory/)
- Create multi-agent systems - see [Multi-Agent Systems](../multi-agent/)

## Troubleshooting

### Common Issues

1. **API Key Issues**: If you receive authentication errors, check that your API key is correct and properly set.
2. **Model Availability**: Ensure you have access to the model you're trying to use (e.g., GPT-4o might require special access).
3. **Rate Limiting**: If you encounter rate limiting, consider adding delays between requests or using a different API key.

### Getting Help

If you run into issues, check the [GitHub Issues](https://github.com/ranaroussi/muxi/issues) or create a new issue with detailed information about your problem.
