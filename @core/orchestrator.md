# Orchestrator in Muxi Core

The Orchestrator is the central component of Muxi Core, coordinating agents, memory systems, and external integrations. It serves as the primary entry point for applications built with Muxi Core.

## Orchestrator Architecture

The Orchestrator manages the following components:

```mermaid
graph TD
    subgraph "Orchestrator"
        Agents[Agent Management]
        Memory[Memory Systems]
        Routing[Message Routing]
        MCP[Tool Integration]
        Auth[Authentication]
        API[API Services]
    end

    Memory --> BufferMemory[Buffer Memory]
    Memory --> LongTermMemory[Long-Term Memory]
    Memory --> Memobase[Memobase]

    Agents --> Agent1[Agent 1]
    Agents --> Agent2[Agent 2]
    Agents --> AgentN[Agent N]

    MCP --> Server1[MCP Server 1]
    MCP --> Server2[MCP Server 2]

    External[External Client] --> API
    API --> Routing
    Routing --> Agents
    Agents --> Memory
    Agents --> MCP
```

## Core Responsibilities

The Orchestrator has several primary responsibilities:

1. **Agent Management**: Create, configure, and coordinate multiple agents
2. **Memory Coordination**: Centralize access to different memory systems
3. **Message Routing**: Direct messages to the appropriate agent based on content
4. **Tool Integration**: Manage connections to external tools via MCP
5. **Authentication**: Handle API keys and user authentication
6. **API Services**: Provide HTTP endpoints for client applications

## Creating an Orchestrator

### Basic Initialization

```python
from muxi.core.orchestrator import Orchestrator

# Create a basic orchestrator
orchestrator = Orchestrator()

# Run the orchestrator's API server
if __name__ == "__main__":
    orchestrator.run(
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### With Memory Systems

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create models
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memory systems
buffer_memory = BufferMemory(
    max_size=10,
    buffer_multiplier=10,
    model=embedding_model
)

long_term_memory = LongTermMemory(
    connection_string="postgresql://user:pass@localhost/muxi",
    embedding_provider=embedding_model
)

# Create orchestrator with memory systems
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    long_term_memory=long_term_memory,
    extraction_model=embedding_model
)
```

### Full Configuration

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.config.app import AppConfig

# Create models
chat_model = OpenAIModel(model="gpt-4o")
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memory systems
buffer_memory = BufferMemory(
    max_size=10,
    buffer_multiplier=10,
    model=embedding_model
)

long_term_memory = LongTermMemory(
    connection_string="postgresql://user:pass@localhost/muxi",
    embedding_provider=embedding_model
)

memobase = Memobase(
    mongodb_uri="mongodb://localhost:27017",
    embedding_provider=embedding_model
)

# Create configuration
config = AppConfig(
    name="My Muxi App",
    debug=True,
    cors_origins="*",
    secret_key="supersecretkey",
    system_message="You are a helpful AI assistant."
)

# Create orchestrator with full configuration
orchestrator = Orchestrator(
    config=config,
    buffer_memory=buffer_memory,
    long_term_memory=long_term_memory,
    memobase=memobase,
    extraction_model=embedding_model,
    auto_extract_user_info=True
)
```

## Agent Management

The Orchestrator manages the lifecycle of agents:

### Creating Agents

```python
# Create a default agent
default_agent = orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    system_message="You are a helpful assistant.",
    set_as_default=True
)

# Create a specialized agent
code_agent = orchestrator.create_agent(
    agent_id="code",
    model=OpenAIModel(model="gpt-4o"),
    system_message="You are a coding expert.",
    description="Expert in programming and software development"
)
```

### Managing Agents

```python
# List all agents
agents = orchestrator.list_agents()
print(agents)

# Get a specific agent
assistant = orchestrator.get_agent("assistant")

# Set the default agent
orchestrator.set_default_agent("assistant")

# Remove an agent
orchestrator.remove_agent("deprecated_agent")
```

## Message Routing

The Orchestrator can intelligently route messages to the appropriate agent using an LLM:

```python
# Initialize routing model
orchestrator._initialize_routing_model()

# Select the best agent for a message
agent_id = await orchestrator.select_agent_for_message(
    "What's the best way to implement quicksort in Python?"
)
# Returns "code" based on message content

# Process with selected agent
response = await orchestrator.run_agent(
    input_text="What's the best way to implement quicksort in Python?",
    agent_id=agent_id
)
```

### Smart Routing Architecture

The Orchestrator uses an LLM-based approach to intelligently route messages to the most appropriate agent:

1. **Routing Model Initialization**:
   - The routing model is initialized during Orchestrator creation via `_initialize_routing_model()`
   - Settings come from `config.routing` (defined in `routing.py`)
   - By default, it uses OpenAI's "gpt-4o-mini" with temperature=0.0 for precise routing
   - Can be customized through environment variables:

     ```
     ROUTING_LLM=openai
     ROUTING_LLM_MODEL=gpt-4o-mini
     ROUTING_LLM_TEMPERATURE=0.0
     ROUTING_LLM_MAX_TOKENS=256
     ```

2. **Routing Process Flow**:
   - For each incoming message, the Orchestrator:
     1. Checks if there's only one agent (automatic selection)
     2. Checks routing cache for previously seen messages
     3. Creates a prompt with all agent descriptions and capabilities
     4. Sends the prompt to the routing model
     5. Parses the response to extract the selected agent ID
     6. Falls back to the default agent if routing fails

3. **Routing Prompt Construction**:
   - The prompt includes descriptions of all available agents
   - Each agent's ID and description are included
   - The user's message is included for context
   - The prompt asks for just the agent ID as a response

4. **Response Parsing**:
   - Uses multiple strategies to extract the agent ID:
     - Exact matching with known agent IDs
     - Looking for formatted responses (e.g., "Agent ID: xyz")
     - Checking for agent ID mentions in the response text

5. **Caching and Optimization**:
   - Routing decisions are cached to improve performance
   - Automatic fallback to default agent when necessary

### Automatic Routing

```python
# Chat with automatic agent selection
response = await orchestrator.chat(
    message="How do I calculate the area of a circle?",
    # No agent_name specified, so routing will be used
)
```

## Memory Integration

The Orchestrator provides a unified interface to memory systems:

```python
# Adding to buffer memory
await orchestrator.add_to_buffer_memory(
    message="I prefer dark mode.",
    metadata={"role": "user", "agent_id": "assistant"}
)

# Adding to long-term memory
await orchestrator.add_to_long_term_memory(
    content="User John Doe prefers dark mode.",
    metadata={"user_id": 42, "category": "preferences"}
)

# Searching memory
results = await orchestrator.search_memory(
    query="What are the user's theme preferences?",
    agent_id="assistant",
    k=5,
    use_long_term=True
)

# Working with user context
await orchestrator.add_user_context_memory(
    user_id=42,
    knowledge={"preferences": {"theme": "dark"}},
    importance=0.8
)

user_context = await orchestrator.get_user_context_memory(user_id=42)
```

## MCP Tool Integration

The Orchestrator manages MCP servers for tool integration:

```python
# Register an MCP server
server_id = await orchestrator.register_mcp_server(
    server_id="github",
    url="https://mcp-server.example.com/github"
)

# Get the MCP service
mcp_service = orchestrator.get_mcp_service()

# Execute a tool
result = await mcp_service.execute_tool(
    server_id="github",
    tool_name="create_issue",
    parameters={
        "repo": "user/repo",
        "title": "Bug report",
        "body": "Found a bug in the login system"
    }
)

# List available tools
tools = await orchestrator.list_mcp_tools()
print(tools)
```

## Conversation Management

The Orchestrator manages conversations between users and agents:

```python
# Process a message
response = await orchestrator.run_agent(
    input_text="What is the capital of France?",
    agent_id="assistant"
)

# High-level chat interface
response = await orchestrator.chat(
    message="What is the capital of France?",
    agent_name="assistant",
    user_id=42
)

# Clear conversation context
orchestrator.clear_memory(agent_id="assistant")
```

## Authentication and Authorization

The Orchestrator handles authentication and API keys:

```python
# Access API keys
user_api_key = orchestrator.user_api_key
admin_api_key = orchestrator.admin_api_key

# Create a new API key
new_key = orchestrator.create_api_key(is_admin=False)

# Validate an API key
is_valid = orchestrator.validate_api_key(key="api_key_123", require_admin=False)

# Generate a JWT token
token = orchestrator.generate_jwt_token(user_id="user_42")

# Validate a JWT token
payload = orchestrator.validate_jwt_token(token="jwt_token_123")
```

## Running the API Server

The Orchestrator provides a complete API server:

```python
# Run the API server
if __name__ == "__main__":
    orchestrator.run(
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## API Endpoints

The Orchestrator creates several API endpoints:

- **POST /chat**: Send a message and get a response
- **POST /chat/{agent_name}**: Send a message to a specific agent
- **GET /agents**: List all available agents
- **POST /agents**: Create a new agent
- **GET /agents/{agent_id}**: Get information about a specific agent
- **DELETE /agents/{agent_id}**: Remove an agent
- **GET /health**: Check if the API is running
- **POST /auth/token**: Generate a JWT token
- **GET /docs**: Swagger UI documentation

## Advanced Usage

### Event Hooks

```python
# Add a pre-processing hook
@orchestrator.register_hook("before_process_message")
async def my_pre_process_hook(message, agent_id, user_id=None):
    print(f"Processing message: {message} for agent {agent_id}")
    return {"modified_message": message}

# Add a post-processing hook
@orchestrator.register_hook("after_process_message")
async def my_post_process_hook(response, agent_id, user_id=None):
    print(f"Response generated by {agent_id}: {response}")
    return {"modified_response": response}
```

### Multi-User Support

```python
# Create user-specific agents
user1_agent = orchestrator.create_agent(
    agent_id="user1_assistant",
    model=model,
    system_message="You are assisting User 1.",
    user_id="user_1"
)

user2_agent = orchestrator.create_agent(
    agent_id="user2_assistant",
    model=model,
    system_message="You are assisting User 2.",
    user_id="user_2"
)

# Chat with user context
response1 = await orchestrator.chat(
    message="What's on my schedule today?",
    agent_name="assistant",
    user_id="user_1"
)

response2 = await orchestrator.chat(
    message="What's on my schedule today?",
    agent_name="assistant",
    user_id="user_2"
)
```

### Custom Model Integration

```python
from muxi.core.models.base import BaseModel

# Implement a custom model
class MyCustomModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Custom initialization

    async def chat(self, messages, **kwargs):
        # Custom chat implementation
        pass

    async def embed(self, text, **kwargs):
        # Custom embedding implementation
        pass

# Use the custom model with the orchestrator
orchestrator.create_agent(
    agent_id="custom",
    model=MyCustomModel(),
    system_message="You are powered by a custom model."
)
```

## Performance Optimization

### Memory Usage

Optimize memory usage based on your application needs:

```python
# For applications with limited recent context needs
buffer_memory = BufferMemory(
    max_size=5,              # Smaller context window
    buffer_multiplier=5,     # Smaller total capacity (25 items)
    model=embedding_model
)

# For applications with extensive context needs
buffer_memory = BufferMemory(
    max_size=20,             # Larger context window
    buffer_multiplier=15,    # Larger total capacity (300 items)
    model=embedding_model
)
```

### Caching

```python
# Configure with caching
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    enable_routing_cache=True,     # Cache routing decisions
    routing_cache_size=100,        # Size of the routing cache
    enable_model_cache=True,       # Cache model responses
    model_cache_size=50            # Size of the model cache
)
```

## Best Practices

1. **Centralize Configuration**: Use the AppConfig class to centralize configuration
2. **Memory Management**: Choose appropriate memory systems for your use case
3. **Agent Specialization**: Create specialized agents for different tasks
4. **Authentication**: Always use API keys or JWT tokens in production
5. **Error Handling**: Implement proper error handling for production use
6. **Metadata Consistency**: Establish consistent metadata conventions
7. **User Identification**: Always include user_id in multi-user applications

## Coming Soon Features

- **Agent Teams**: Organize agents into teams for complex workflows
- **Workflow Orchestration**: Define and execute multi-step workflows
- **Agent-to-Agent Communication**: Enable communication between agents
- **Enhanced Routing**: More sophisticated message routing algorithms
- **Performance Monitoring**: Built-in performance tracking and optimization
