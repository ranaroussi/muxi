---
layout: default
title: Automatic User Information Extraction
parent: Memory Systems
grand_parent: Technical Details
nav_order: 3
permalink: /technical/memory/user-extraction
---

# Automatic User Information Extraction

MUXI includes a powerful automatic user information extraction system that can identify and store important information about users from conversations. This guide explains how the extraction system works and how to configure it in your MUXI applications.

{: .note }
> User information extraction is designed with privacy in mind. All extraction is opt-in, anonymous users are excluded by default, and safeguards are in place to protect sensitive information.

## Overview

The automatic user information extraction system analyzes conversations between users and agents to identify key facts, preferences, and characteristics. It then stores this information in the user's context memory, making it available for future interactions.

### Key Features

- **Zero-effort personalization**: Remembers important user information without explicit programming
- **Importance scoring**: Prioritizes information based on relevance and significance
- **Confidence assessment**: Evaluates certainty before storing information
- **Conflict resolution**: Handles updates when new information contradicts existing data
- **Privacy controls**: Protects user privacy with opt-out mechanisms and anonymous user exclusion

## Architecture

The extraction system follows a centralized architecture:

1. **MemoryExtractor**: Core class that analyzes conversations and extracts information
2. **Orchestrator**: Manages the extraction process and coordinates with agents
3. **Agent**: Delegates extraction to its parent Orchestrator

When a user interacts with an agent, the conversation is processed asynchronously to extract important information without impacting response times.

### Implementation Details

The extraction process works as follows:

1. User sends a message to an agent
2. Agent processes and responds to the message
3. Agent delegates extraction to the Orchestrator
4. Orchestrator processes the conversation asynchronously
5. MemoryExtractor analyzes the content to identify key information
6. Extracted information is scored for importance and confidence
7. Valid information is stored in the user's context memory
8. Future conversations include this information in the agent's context

## Configuration

### Basic Setup

Automatic user information extraction is enabled by default in the Orchestrator. You can explicitly configure it as follows:

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI with extraction enabled
app = muxi(
    buffer_memory=15,
    long_term_memory="postgresql://user:pass@localhost/db",
    auto_extract_user_info=True,  # Enable automatic extraction
    config_file="configs/muxi_config.yaml"
)
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory

# Initialize components
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
buffer = BufferMemory(15)
long_term_memory = LongTermMemory(connection_string="postgresql://user:pass@localhost/db")

# Initialize orchestrator with extraction enabled
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=long_term_memory,
    auto_extract_user_info=True,  # Enable automatic extraction
)

# Create an agent that will use the orchestrator's extraction
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant that remembers important user information.",
    model=model
)
```

### Advanced Configuration

For more control over the extraction process, you can configure additional parameters:

```python
from muxi.models.providers.openai import OpenAIModel

# Create a specialized model for extraction
extraction_model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",  # Using a capable model for extraction
    temperature=0.0  # Lower temperature for more deterministic extraction
)

# Initialize orchestrator with advanced extraction options
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=long_term_memory,
    auto_extract_user_info=True,
    extraction_model=extraction_model,  # Specify a dedicated model for extraction
    extraction_interval=3  # Process extraction every 3 messages (default is 1)
)
```

### Extraction Parameters

The following parameters can be configured:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `auto_extract_user_info` | Enable/disable automatic extraction | `True` |
| `extraction_model` | Model used for extraction | Same as agent model |
| `extraction_interval` | Process extraction every N messages | `1` |
| `confidence_threshold` | Minimum confidence score (0.0-1.0) | `0.7` |
| `importance_threshold` | Minimum importance score (0.0-1.0) | `0.5` |

## Privacy Controls

### Automatic Privacy Features

The extraction system includes several built-in privacy features:

1. **Anonymous User Exclusion**: Users with `user_id=0` are automatically excluded from extraction
2. **Configurable Thresholds**: Only information with sufficient confidence is stored
3. **PII Detection**: Basic detection of sensitive personal information
4. **Asynchronous Processing**: Extraction runs separately from conversation flow

### User Opt-Out

You can explicitly exclude users from extraction:

```python
# Exclude a user from extraction
await orchestrator.opt_out_user(user_id="user_123", opt_out=True)

# Re-enable extraction for a user
await orchestrator.opt_out_user(user_id="user_123", opt_out=False)
```

### Data Purging

You can purge all extracted information for a user:

```python
# Remove all extracted information for a user
await orchestrator.purge_user_data(user_id="user_123")
```

## Accessing Extracted Information

Information extracted by the system is automatically included in the agent's context for future conversations. You can also access it directly:

```python
# Get all context memory for a user
user_context = await orchestrator.get_user_context_memory(user_id="user_123")

# Check specific extracted information
if "preferred_language" in user_context:
    preferred_language = user_context["preferred_language"]["value"]
    print(f"User prefers programming in {preferred_language}")
```

## Example: Extraction in Action

Here's an example of automatic extraction in a conversation:

```python
# User interacts with the agent
user_message = "I live in Berlin and I'm learning Python. I prefer visual explanations over text."
agent_response = await app.chat(
    message=user_message,
    agent_name="assistant",
    user_id="user_123"
)

# Behind the scenes, the system extracts:
# - Location: Berlin
# - Learning: Python
# - Preference: Visual explanations

# In a future conversation, the agent can use this information
later_response = await app.chat(
    message="Can you help me understand dictionaries?",
    agent_name="assistant",
    user_id="user_123"
)
# The agent might respond with a visual explanation of Python dictionaries,
# since it remembers the user's location, learning interests, and preferences
```

## Best Practices

1. **Set an appropriate extraction interval** - Balance between comprehensive extraction and performance. For chatbots, every message (interval=1) works well; for applications with frequent messages, consider a higher interval.

2. **Consider using a specialized extraction model** - For high-accuracy extraction, consider using a more capable model for extraction than your main conversation model.

3. **Adjust confidence thresholds** - Tune the confidence threshold based on your needs. Higher thresholds (e.g., 0.8) will reduce false positives but might miss some information.

4. **Respect privacy preferences** - Always provide clear opt-out mechanisms and process opt-out requests promptly.

5. **Review extracted information periodically** - Audit the quality and accuracy of extracted information to fine-tune your system.

6. **Implement retention policies** - Define how long extracted information should be stored and implement automatic aging or purging.

## Limitations and Considerations

- Extraction is only as good as the underlying model. More capable models generally provide better extraction results.
- Complex or nuanced information may not be extracted correctly. Consider supplementing with explicit storage where needed.
- Extraction runs asynchronously and may not be immediate. Don't rely on instant availability of newly extracted information.
- Balance between extraction frequency and API costs, especially with third-party models that charge per token.

## What's Next

Now that you understand automatic user information extraction, you might want to:

- Learn about [Context Memory Namespaces](../namespaces/) for organizing extracted information
- Explore [Memory Optimization](../optimization/) for improving performance
- Consider implementing [Interface-Level User ID Generation](../user-id/) for consistent user identification
