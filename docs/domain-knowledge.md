---
layout: default
title: Domain Knowledge
parent: Concepts
has_children: false
nav_order: 4
permalink: /domain-knowledge/
---

# Domain Knowledge

Domain knowledge is a feature that allows agents to store and retrieve user-specific structured information. This enables agents to personalize their responses based on what they know about each user.

## Overview

The domain knowledge system extends the Memobase memory system to store structured information about users. This information can include:

- Personal details (name, age, location)
- Preferences and interests
- Family information
- Work details
- Any other structured data relevant to the user

When a user interacts with an agent, the agent can automatically enhance the user's message with relevant domain knowledge, providing more personalized and contextually appropriate responses.

## Key Features

- **Structured Storage**: Store information in a structured format (dictionaries, lists, nested objects)
- **User-Specific**: Each user has their own domain knowledge store
- **Automatic Enhancement**: Messages are automatically enhanced with relevant domain knowledge
- **Flexible Retrieval**: Retrieve all knowledge or specific keys
- **Bulk Import**: Import knowledge from dictionaries or JSON files
- **Metadata Support**: Track source and importance of knowledge

## Usage

### Adding Domain Knowledge

```python
from src.memory.memobase import Memobase
from src.memory.long_term import LongTermMemory

# Create a Memobase instance
memobase = Memobase(long_term_memory=LongTermMemory())

# Add domain knowledge for a user
user_id = 123
knowledge = {
    "name": "Alice",
    "age": 30,
    "location": {"city": "New York", "country": "USA"},
    "interests": ["AI", "programming", "music"],
    "family": {"spouse": "Bob", "children": ["Charlie", "Diana"]}
}

# Add the knowledge to the user's domain knowledge store
await memobase.add_user_domain_knowledge(
    user_id=user_id,
    knowledge=knowledge,
    source="user_profile",  # Optional: track the source of this information
    importance=0.8  # Optional: set importance level (0.0 to 1.0)
)
```

### Retrieving Domain Knowledge

```python
# Get all domain knowledge for a user
all_knowledge = await memobase.get_user_domain_knowledge(user_id=123)

# Get specific keys
specific_knowledge = await memobase.get_user_domain_knowledge(
    user_id=123,
    keys=["name", "interests"]
)
```

### Importing Domain Knowledge

```python
# Import from a dictionary
data = {
    "name": "Bob",
    "preferences": {
        "theme": "dark",
        "notifications": "enabled"
    }
}
await memobase.import_user_domain_knowledge(
    data_source=data,
    user_id=456,
    format="dict",
    source="settings_import"
)

# Import from a JSON file
await memobase.import_user_domain_knowledge(
    data_source="user_data.json",
    user_id=789,
    format="json",
    source="file_import"
)
```

### Clearing Domain Knowledge

```python
# Clear specific keys
await memobase.clear_user_domain_knowledge(
    user_id=123,
    keys=["preferences", "temporary_data"]
)

# Clear all domain knowledge for a user
await memobase.clear_user_domain_knowledge(user_id=123)
```

## Automatic Message Enhancement

When using an agent with Memobase as its long-term memory, messages are automatically enhanced with relevant domain knowledge:

```python
from src.core.orchestrator import Orchestrator
from src.models.openai import OpenAIModel
from src.memory.buffer import BufferMemory

# Create an orchestrator
orchestrator = Orchestrator()

# Create an agent with Memobase
orchestrator.create_agent(
    agent_id="personal_assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    long_term_memory=memobase,
    system_message="You are a helpful personal assistant."
)

# Chat with the agent (domain knowledge is automatically included)
response = orchestrator.chat(
    agent_id="personal_assistant",
    message="What music should I listen to today?",
    user_id=123
)
# The agent will know the user's interests include music
```

## Implementation Details

The domain knowledge feature is implemented in the following components:

1. **Memobase**: Provides methods for adding, retrieving, and clearing domain knowledge
2. **Agent**: Enhances user messages with domain knowledge before processing
3. **Orchestrator**: Passes user IDs to agents for multi-user support

Domain knowledge is stored in a separate collection in the vector database, with metadata to track the key, value, source, and importance of each piece of information.

## Best Practices

- Store only relevant information that will enhance the agent's ability to assist the user
- Use clear, descriptive keys for domain knowledge
- Consider privacy implications when storing personal information
- Regularly update domain knowledge to keep it current
- Use the importance parameter to prioritize critical information

## Future Enhancements

- Automatic knowledge extraction from conversations
- Time-based knowledge expiration
- Knowledge conflict resolution
- Enhanced privacy controls
- Knowledge sharing between users (with permissions)
