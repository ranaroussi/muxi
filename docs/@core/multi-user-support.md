# Multi-User Support in Muxi Core

Muxi Core provides robust support for multi-user applications, enabling personalized agent interactions for each user while efficiently managing shared resources. This document details the multi-user capabilities in Muxi Core.

## Multi-User Architecture

Muxi Core's multi-user architecture combines centralized resource management with user-specific contexts:

```mermaid
graph TD
    subgraph "Muxi Core"
        Orchestrator -->|Manages| Agents
        Orchestrator -->|Manages| Memory
        Orchestrator -->|Manages| Auth

        subgraph "Memory Systems"
            Memory -->|Shared| BufferMemory[Buffer Memory]
            Memory -->|Shared| LongTermMemory[Long-Term Memory]
            Memory -->|User-Specific| Memobase
        end

        subgraph "Authentication"
            Auth --> APIKeys[API Keys]
            Auth --> JWTTokens[JWT Tokens]
            Auth --> Sessions[Sessions]
        end

        subgraph "Agents"
            Agents -->|Shared| SharedAgents[Shared Agents]
            Agents -->|User-Specific| UserAgents[User-Specific Agents]
        end
    end

    User1[User 1] -->|Interacts| Orchestrator
    User2[User 2] -->|Interacts| Orchestrator
    UserN[User N] -->|Interacts| Orchestrator

    Memobase -->|User 1 Context| User1Context[User 1 Context]
    Memobase -->|User 2 Context| User2Context[User 2 Context]
    Memobase -->|User N Context| UserNContext[User N Context]
```

## User Identification

Users are identified by a unique `user_id` that serves as the primary key for user-specific data:

```python
# Example user IDs
user_id = "user_123"        # String-based ID
user_id = 42                # Numeric ID
user_id = "john@email.com"  # Email as ID
```

The user ID is passed to Muxi Core functions that need to operate in a user-specific context:

```python
# Chat with user context
response = await orchestrator.chat(
    message="What's on my schedule today?",
    agent_name="assistant",
    user_id="user_123"  # Identifies the specific user
)
```

## Authentication and Authorization

Muxi Core provides built-in authentication mechanisms:

### API Keys

```python
# Access API keys
user_api_key = orchestrator.user_api_key
admin_api_key = orchestrator.admin_api_key

# Create a new API key
new_key = orchestrator.create_api_key(is_admin=False)

# Validate an API key
is_valid = orchestrator.validate_api_key(
    key="api_key_123",
    require_admin=False
)
```

### JWT Tokens

```python
# Generate a JWT token
token = orchestrator.generate_jwt_token(
    user_id="user_123",
    expiration=3600  # Seconds
)

# Validate a JWT token
payload = orchestrator.validate_jwt_token(token="jwt_token_123")
```

### Example Authentication Flow

```python
from fastapi import HTTPException

# Authenticate a user
async def authenticate_user(api_key):
    if orchestrator.validate_api_key(key=api_key):
        # Extract user_id from key or lookup in database
        user_id = "user_123"  # Usually looked up based on API key
        return user_id
    raise HTTPException(status_code=401, detail="Invalid API key")

# Example API endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, api_key: str):
    user_id = await authenticate_user(api_key)
    response = await orchestrator.chat(
        message=request.message,
        agent_name=request.agent_name,
        user_id=user_id
    )
    return {"response": response}
```

## User-Specific Memory with Memobase

Memobase is the primary system for managing user-specific memory contexts:

### Initializing Memobase

```python
from muxi.core.memory.memobase import Memobase
from muxi.core.models.providers.openai import OpenAIModel

# Create a model for embeddings
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create Memobase
memobase = Memobase(
    mongodb_uri="mongodb://localhost:27017",
    database_name="muxi_memory",
    embedding_provider=embedding_model
)

# Add Memobase to orchestrator
orchestrator = Orchestrator(
    memobase=memobase,
    extraction_model=embedding_model,
    auto_extract_user_info=True
)
```

### User Memory Management

Add and retrieve user-specific memories:

```python
# Add user-specific memory
await memobase.add_user_memory(
    user_id=42,
    message="My favorite color is blue",
    agent_id="assistant",
    importance=0.7
)

# Search user-specific memory
results = await memobase.search_user_memory(
    user_id=42,
    query="What are the user's favorite colors?",
    limit=5
)
```

### User Context Memory

Store structured information about users:

```python
# Add to user context memory
await memobase.add_user_context_memory(
    user_id=42,
    knowledge={
        "name": "John Doe",
        "preferences": {
            "theme": "dark",
            "language": "English"
        },
        "location": "New York"
    },
    source="manual_input",
    importance=0.9
)

# Get user context memory
user_context = await memobase.get_user_context_memory(user_id=42)
print(user_context)

# Update user context memory
await memobase.update_user_context_memory(
    user_id=42,
    path="preferences.notifications",
    value="enabled"
)
```

### Automatic Information Extraction

Memobase can automatically extract user information from conversations:

```python
# Enable automatic extraction
orchestrator = Orchestrator(
    memobase=memobase,
    auto_extract_user_info=True,
    extraction_model=extraction_model
)

# Extraction happens automatically during conversations
# But can also be triggered manually:
await memobase.extract_user_information(
    user_message="I live in Toronto and I'm allergic to cats.",
    agent_response="I'll remember that you live in Toronto and have a cat allergy.",
    user_id=42,
    agent_id="assistant"
)
```

## User-Specific Agents

Create dedicated agents for specific users:

```python
# Create user-specific agents
user1_agent = orchestrator.create_agent(
    agent_id="user1_assistant",
    model=model,
    system_message="You are assisting User 1 (John). He prefers concise answers.",
    user_id="user_1"  # Associate agent with specific user
)

user2_agent = orchestrator.create_agent(
    agent_id="user2_assistant",
    model=model,
    system_message="You are assisting User 2 (Sarah). She prefers detailed explanations.",
    user_id="user_2"
)
```

### User-Specific Agent Management

```python
# Get agents for a specific user
user_agents = orchestrator.get_user_agents(user_id="user_1")

# Set default agent for a user
orchestrator.set_user_default_agent(
    user_id="user_1",
    agent_id="user1_assistant"
)
```

## Filtering Memory by User

When working with shared memory systems, filter by user ID:

```python
# Filter buffer memory by user ID
buffer_results = await orchestrator.search_memory(
    query="my preferences",
    agent_id="assistant",
    filter_metadata={"user_id": "user_123"}
)

# Filter long-term memory by user ID
long_term_results = await orchestrator.search_memory(
    query="user preferences",
    use_long_term=True,
    filter_metadata={"user_id": "user_123"}
)
```

## Session Management

Track user sessions for continuous interactions:

```python
# Create a user session
session_id = orchestrator.create_user_session(
    user_id="user_123",
    metadata={"source": "web", "device": "desktop"}
)

# Use session ID in conversations
response = await orchestrator.chat(
    message="Continue our discussion",
    agent_name="assistant",
    user_id="user_123",
    session_id=session_id
)

# End a session
orchestrator.end_user_session(session_id=session_id)
```

## Multi-User API Endpoints

Example of multi-user API endpoints:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

class ChatRequest(BaseModel):
    message: str
    agent_name: str = None

async def get_user_id(api_key: str = Depends(api_key_header)):
    if orchestrator.validate_api_key(key=api_key):
        # In a real application, lookup user_id based on API key
        return "user_123"
    raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_user_id)
):
    response = await orchestrator.chat(
        message=request.message,
        agent_name=request.agent_name,
        user_id=user_id
    )
    return {"response": response}

@app.get("/user/context")
async def get_user_context(user_id: str = Depends(get_user_id)):
    context = await orchestrator.get_user_context_memory(user_id=user_id)
    return {"user_context": context}
```

## Multi-User Conversation Management

Managing conversations for multiple users:

```python
# Clear memory for a specific user
orchestrator.clear_memory(
    agent_id="assistant",
    user_id="user_123"
)

# Add user-specific conversation memory
await orchestrator.add_to_buffer_memory(
    message="I prefer dark mode.",
    metadata={
        "role": "user",
        "agent_id": "assistant",
        "user_id": "user_123",
        "conversation_id": "conv_456"
    }
)

# Search with conversation and user filters
results = await orchestrator.search_memory(
    query="theme preferences",
    agent_id="assistant",
    filter_metadata={
        "user_id": "user_123",
        "conversation_id": "conv_456"
    }
)
```

## Data Isolation and Privacy

Ensuring proper data isolation between users:

```python
# 1. Always include user_id in metadata
await orchestrator.add_to_buffer_memory(
    message="My address is 123 Main St.",
    metadata={"user_id": "user_123", "role": "user"}
)

# 2. Always filter by user_id when retrieving
results = await orchestrator.search_memory(
    query="address",
    filter_metadata={"user_id": "user_123"}
)

# 3. Use user-specific agents when possible
user_agent = orchestrator.create_agent(
    agent_id="user123_assistant",
    model=model,
    system_message="You are a private assistant for User 123.",
    user_id="user_123"
)

# 4. Implement data retention policies
async def cleanup_old_user_data(user_id, days=90):
    # Clean up old data for compliance purposes
    cutoff_date = datetime.now() - timedelta(days=days)
    await orchestrator.delete_user_data(
        user_id=user_id,
        before_date=cutoff_date
    )
```

## User Preferences Management

Managing user preferences:

```python
# Store user preferences
await orchestrator.add_user_context_memory(
    user_id="user_123",
    knowledge={
        "preferences": {
            "theme": "dark",
            "language": "English",
            "notifications": "enabled",
            "timezone": "America/New_York"
        }
    },
    importance=0.8
)

# Get user preferences
user_context = await orchestrator.get_user_context_memory(
    user_id="user_123"
)
theme = user_context.get("preferences", {}).get("theme", "light")

# Update a specific preference
await orchestrator.update_user_context_memory(
    user_id="user_123",
    path="preferences.theme",
    value="light"
)
```

## Best Practices for Multi-User Applications

1. **Always Use User IDs**: Include user_id in all operations involving user data
2. **Implement Proper Authentication**: Use API keys or JWT tokens for authentication
3. **Filter Memory by User**: Always filter memory results by user_id
4. **Consistent Metadata**: Establish consistent metadata schemas for user data
5. **User Privacy**: Implement proper data isolation and retention policies
6. **Error Handling**: Implement robust error handling for user operations
7. **Scalability**: Design for scalability with growing user bases

## Example: Complete Multi-User Chat Application

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.models.providers.openai import OpenAIModel
import os

# Set up models
chat_model = OpenAIModel(model="gpt-4o")
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Set up memory systems
buffer_memory = BufferMemory(
    max_size=10,
    buffer_multiplier=10,
    model=embedding_model
)

memobase = Memobase(
    mongodb_uri=os.getenv("MONGODB_URI"),
    embedding_provider=embedding_model
)

# Create orchestrator
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    memobase=memobase,
    extraction_model=embedding_model,
    auto_extract_user_info=True
)

# Create a shared agent
general_agent = orchestrator.create_agent(
    agent_id="general",
    model=chat_model,
    system_message="You are a helpful assistant.",
    set_as_default=True
)

# Define API endpoints (using FastAPI)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

class ChatRequest(BaseModel):
    message: str
    agent_name: str = None

# Authentication dependency
async def get_current_user(api_key: str = Depends(api_key_header)):
    if not orchestrator.validate_api_key(key=api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    # In a real app, look up user_id based on API key
    # For this example, I extract it from the key itself
    user_id = api_key.split("_")[1]  # Assumes format like "apikey_user123"
    return user_id

# Chat endpoint
@app.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        response = await orchestrator.chat(
            message=request.message,
            agent_name=request.agent_name,
            user_id=user_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User context endpoint
@app.get("/user/context")
async def get_user_context(user_id: str = Depends(get_current_user)):
    try:
        context = await orchestrator.get_user_context_memory(user_id=user_id)
        return {"user_context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clear user conversation endpoint
@app.post("/user/clear-conversation")
async def clear_conversation(user_id: str = Depends(get_current_user)):
    try:
        orchestrator.clear_memory(user_id=user_id)
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Coming Soon Features

- **Enhanced User Management**: Advanced user management with roles and permissions
- **Team Contexts**: Shared contexts for teams of users
- **User Analytics**: Track and analyze user interactions
- **Multi-Modal User Context**: Support for images and other media in user context
- **User Feedback Systems**: Incorporate user feedback into the memory systems
