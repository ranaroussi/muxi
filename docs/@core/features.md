# Muxi Core Features

Muxi Core offers a comprehensive set of features for building AI-powered applications. This document outlines the key features currently available in the core package.

## Agent System

### Multi-Agent Management

- **Agent Creation and Registration**: Create and register multiple agents with the orchestrator
- **Flexible Agent Configuration**: Configure agents with different models, system messages, and capabilities
- **Agent Lifecycle Management**: Control the lifecycle of agents (create, activate, deactivate, remove)
- **Default Agent Designation**: Specify a default agent for handling general requests

```python
# Creating and registering multiple agents
openai_model = OpenAIModel(model="gpt-4o")
anthropic_model = AnthropicModel(model="claude-3-opus-20240229")

agent1 = orchestrator.create_agent(
    agent_id="general",
    model=openai_model,
    system_message="You are a helpful assistant.",
    set_as_default=True
)

agent2 = orchestrator.create_agent(
    agent_id="code",
    model=anthropic_model,
    system_message="You are a coding expert.",
    description="Expert in programming and software development"
)
```

### Intelligent Message Routing

- **Automatic Agent Selection**: Route messages to the most appropriate agent based on content
- **LLM-Based Routing Logic**: Utilize language models to understand message intent and select the best agent
- **Routing Rules Configuration**: Set custom routing rules and preferences
- **Routing Cache**: Cache frequently seen message patterns for faster routing

```python
# Automatic routing to the appropriate agent
response = await orchestrator.chat(
    message="How do I implement a binary search tree in Python?",
    # No agent_id specified - will use intelligent routing
)
```

## Memory Systems

### Buffer Memory

- **Smart Buffer with Vector Search**: Combines recency with semantic search using FAISS
- **Configurable Buffer Size**: Set the context window size and total buffer capacity
- **Hybrid Retrieval**: Balance between semantic relevance and recency with recency bias
- **Metadata Filtering**: Filter memory items based on metadata attributes
- **Graceful Fallback**: Automatically falls back to recency-based retrieval when needed

```python
# Initialize buffer memory with semantic search
buffer = BufferMemory(
    max_size=10,               # Context window size
    buffer_multiplier=10,      # Buffer capacity multiplier
    model=embedding_model      # For vector embeddings
)

# Add to buffer with metadata
await buffer.add(
    "The user prefers dark mode",
    metadata={"category": "preferences", "importance": "high"}
)

# Semantic search with recency bias
results = await buffer.search(
    query="What UI settings does the user prefer?",
    limit=5,
    recency_bias=0.3  # Balance between semantic (0.0) and recency (1.0)
)
```

### Long-Term Memory

- **Persistent Vector Storage**: Store embeddings and content in PostgreSQL with pgvector
- **Collection-Based Organization**: Organize memories into collections for better retrieval
- **Vector Similarity Search**: Find semantically similar content based on embedding distance
- **Metadata Filtering**: Filter search results based on metadata attributes
- **Transaction Support**: Ensure database consistency with proper transaction handling

```python
# Initialize long-term memory
long_term = LongTermMemory(
    connection_string="postgresql://user:pass@localhost/muxi",
    embedding_provider=embedding_model
)

# Add to long-term memory
memory_id = await long_term.add(
    content="Jane is allergic to peanuts",
    metadata={"user_id": 42, "category": "health", "importance": 0.9}
)

# Search long-term memory
results = await long_term.search(
    query="User dietary restrictions",
    limit=5,
    filter_metadata={"user_id": 42}
)
```

### Memobase for Multi-User Systems

- **Multi-User Memory Management**: Store and retrieve user-specific information
- **MongoDB Integration**: Scale to millions of users with MongoDB storage
- **User Context Memory**: Track persistent user attributes and preferences
- **Automatic Information Extraction**: Extract and organize user information from conversations
- **Tiered Memory Structure**: Organize information by importance and recency

```python
# Initialize Memobase for multi-user support
memobase = Memobase(
    mongodb_uri="mongodb://localhost:27017",
    embedding_provider=embedding_model
)

# Add user-specific memory
await memobase.add_user_memory(
    user_id=42,
    message="My favorite color is blue",
    agent_id="assistant"
)

# Retrieve user-specific context
user_context = await memobase.get_user_context(
    user_id=42,
    agent_id="assistant"
)
```

## Model Integration

### Provider Abstractions

- **Unified Model Interface**: Consistent interface across different model providers
- **Support for Multiple Providers**: OpenAI, Anthropic, and others through a common API
- **Flexible Configuration**: Configure model parameters like temperature and max tokens
- **Error Handling**: Standardized error handling and retry mechanisms
- **Streaming Support**: Stream responses to improve user experience

```python
# Create models from different providers with a consistent interface
openai_model = OpenAIModel(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1000
)

anthropic_model = AnthropicModel(
    model="claude-3-opus-20240229",
    temperature=0.5,
    max_tokens=2000
)

# Both models expose the same methods
response = await model.chat(messages)
embedding = await model.embed(text)
```

### Embedding Utilities

- **Standardized Embedding Generation**: Generate embeddings for semantic search
- **Dimension Standardization**: Handle different embedding dimensions across models
- **Batched Processing**: Process multiple texts efficiently in batches
- **Caching Support**: Optional caching for frequently embedded content

```python
# Generate embeddings for semantic search
embedding = await model.embed("This is some text to embed")

# Use embedding with memory systems
await buffer_memory.add(
    content="Important information about the project",
    embedding=embedding
)
```

## MCP Integration (Model Context Protocol)

### Tool Calling Framework

- **MCP Standard Compliance**: Support for the Model Context Protocol standard
- **Multiple Transport Options**: HTTP+SSE and command-line transports
- **Tool Registration and Discovery**: Register and discover available tools
- **Structured Parameter Validation**: Validate tool parameters against schemas
- **Result Processing**: Process and handle tool execution results

```python
# Register an MCP server for tool access
server_id = await orchestrator.register_mcp_server(
    server_id="github",
    url="https://mcp-server.example.com/github"
)

# Execute a tool through MCP
result = await orchestrator.get_mcp_service().execute_tool(
    server_id="github",
    tool_name="create_issue",
    parameters={
        "repo": "user/repo",
        "title": "Bug report",
        "body": "Found a bug in the login system"
    }
)
```

### External Tool Integration

- **HTTP API Integration**: Connect to external HTTP APIs
- **Command-Line Tool Integration**: Run and interact with command-line tools
- **Authentication Support**: Handle API keys and other authentication methods
- **Timeout and Error Handling**: Robust handling of timeouts and errors
- **Streaming Tool Results**: Support for streaming results from long-running tools

```python
# Command-line tool integration
await orchestrator.register_mcp_server(
    server_id="local_tools",
    command="python local_tool_server.py"
)
```

## Multi-User Support

### Authentication and Authorization

- **API Key Authentication**: Support for user and admin API keys
- **JWT Token Support**: Generate and validate JWT tokens for secure sessions
- **Role-Based Access Control**: Differentiate between user and admin capabilities
- **Session Management**: Track and manage user sessions

```python
# Generate API keys
user_api_key = orchestrator.user_api_key
admin_api_key = orchestrator.admin_api_key

# Use API keys for authentication
headers = {"Authorization": f"Bearer {user_api_key}"}
```

### User Context Management

- **Per-User Memory Context**: Store and retrieve user-specific information
- **Automatic Information Extraction**: Extract user information from conversations
- **Persistent User Attributes**: Track user preferences and important information
- **User Session Tracking**: Associate conversations with specific users

```python
# Add user context memory
await orchestrator.add_user_context_memory(
    user_id=42,
    knowledge={
        "preferences": {
            "theme": "dark",
            "notifications": "enabled"
        }
    },
    importance=0.8
)

# Retrieve user context memory
user_context = await orchestrator.get_user_context_memory(
    user_id=42
)
```

## API and Integration

### FastAPI Integration

- **Ready-to-Use API Endpoints**: Pre-built API endpoints for common operations
- **Swagger Documentation**: Automatic API documentation with Swagger UI
- **CORS Support**: Cross-Origin Resource Sharing configuration
- **Health Checks**: API health check endpoints

```python
# Start the API server
orchestrator.run(
    host="0.0.0.0",
    port=8000,
    reload=True
)
```

### Webhooks and Events

- **Event System**: Subscribe to internal system events
- **Webhook Integration**: Send notifications to external systems
- **Event Filtering**: Filter events by type and source
- **Retry Mechanisms**: Automatic retries for failed webhook deliveries

## Coming Soon Features

- **Agent-to-Agent (A2A) Communication**: Enable direct communication between specialized agents
- **Multi-Model Support**: Use different models for different tasks within the same agent
- **Advanced Planning Capabilities**: Structured planning and reasoning frameworks
- **Memory Optimization**: Automatic summarization and pruning of memory contents
- **Workflow Orchestration**: Define and execute complex workflows involving multiple agents and tools
