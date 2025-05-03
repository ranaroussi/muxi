# MUXI Framework

> The MUXI Framework is a versatile Python framework for building AI agents and Multi-Agent systems.

MUXI Framework is a powerful platform for building AI agents with memory, MCP server integration, and real-time communication capabilities. It provides a solid foundation for creating advanced AI applications through a unified architecture that integrates multiple interfaces.

> [!WARNING]
> This project is a work in progress and is not yet ready for production use. I'm actively developing the framework and adding new features. Please refer to the [roadmap](docs/roadmap.md) for information about the current state of the project and where it's headed.

## Features

- 🤖 **Multi-Agent Support**: Create and manage multiple AI agents with different capabilities
- 🧠 **Memory Systems**: Short-term and long-term memory for contextual interactions
  - FAISS-backed smart buffer memory with hybrid semantic+recency retrieval
  - Configurable recency bias to balance semantic relevance with temporal proximity
  - Graceful degradation to recency-only search when a model isn't available
  - SQLite with sqlite-vec for local or lightweight deployments
  - PostgreSQL with pgvector for scalable long-term memory
  - Memobase for user-level profile-based memory system
  - Automatic extraction of user information from conversations and storing it in context memory
- 🔌 **MCP Client Integration**: Connect to external services via Model Context Protocol servers
  - Centralized MCPService singleton for thread-safe operations
  - Configurable timeouts at orchestrator, agent, and per-request levels
  - Support for HTTP+SSE transport for web-based MCP servers
  - Support for Command-line transport for local executable servers
  - Robust reconnection mechanism with exponential backoff
  - Comprehensive error handling and diagnostics
  - Cancellation support for long-running operations
- 🌟 **MCP Server Implementation**: Expose your agents as MCP-compatible servers
  - SSE-based server endpoint for MCP host integration
  - Tool discovery from agent capabilities
  - Authentication shared with REST API
  - Bridge package for non-SSE clients
- 🔄 **Agent-to-Agent (A2A) Communication**: Enable structured communication between agents
  - Standardized message format for inter-agent communication
  - Capability registration and discovery
  - Task delegation between specialized agents
  - Context sharing with proper isolation
  - Security and authentication
- 🔒 **A2A Security Layer**: Comprehensive security controls for agent interactions
  - Permission system for controlling which agents can communicate
  - Context isolation preventing unauthorized access to sensitive information
  - Rate limiting to prevent abuse of inter-agent communication
  - Audit logging for security analysis of agent interactions
  - Visualization of agent communication patterns as directed acyclic graphs (DAGs)
- 🎭 **Multi-Modal Capabilities**: Support for various content types and interaction modes
  - Document processing for PDF and Office documents with OCR and summarization
  - Image analysis with vision-capable models for content understanding
  - Audio processing with speech-to-text and text-to-speech capabilities
  - Real-time streaming through WebSocket interfaces
  - Seamless mode switching in conversations
  - Cross-modal memory and retrieval
- 🌐 **Multiple Interfaces**: REST API, WebSockets, CLI, Web UI, etc.
- 🔄 **Intelligent Message Routing**: Automatically direct messages to the most appropriate agent
- 📊 **Multi-User Support**: User-specific memory partitioning for multi-tenant applications
- 📘 **Context Memory**: Store and retrieve structured information to personalize responses
- 🔍 **Agent-Level Knowledge Base**: Provide agents with specialized domain knowledge via lightweight RAG
- 🔄 **Hybrid Communication Protocol**: HTTP for standard requests, SSE for streaming, WebSockets for multi-modal
- 📝 **Declarative Configuration**: Define agents using YAML or JSON files with minimal code
- 🚀 **Modular Architecture**: Use only the components you need
- 🌍 **Language-Specific SDKs** (Coming in v0.5.0): Client libraries for TypeScript/JavaScript, Go, and more

## Architecture

MUXI has a flexible, service-oriented approach:

```
┌───────────────────┐
│      Clients      │
│ (CLI/MCP/Web/SDK) │
└─────────┬─────────┘
          │
          │  (API/SSE/WS)
          │
┌─────────│───────────────────────────────────────────┐
│         │    MUXI Server (Local/Remote)             │
│         │                                           │
│         │        ┌───────────────┐                  │   ┌──────────────────┐
│         └───────>│  Orchestrator │----------------------│ Buffer/LT Memory │
│                  └───────┬───────┘                  │   └──────────────────┘
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  │   ┌──────────────────┐
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │------│ Domain Knowledge │
│  └───┬─────↑───┘  └──────↑──────┘  └───↑─────┬───┘  │   └──────────────────┘
│      │     │             │             │     │      │
│      │     │             ↓             │     │      │
│      │     └─────────> (A2A) <─────────┘     │      │
│      │                                       │      │
│      │            ┌─────────────┐            │      │
│      └───────────>│ MCP Handler │<───────────┘      │
│                   └──────┬──────┘                   │
└──────────────────────────│──────────────────────────┘
                           │
                           │ (gRPC/HTTP/Command)
                           │
┌──────────────────────────▼──────────────────────────┐
│                     MCP Servers                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

For more details, see [Architecture Documentation](docs/intro/architecture.md).

## Installation

### For Development

```bash
# Clone the repository
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework

# Install in development mode
./install_dev.sh
```

### From PyPI (Future)

```bash
pip install muxi
```

## Quick Start

### Configuration-based Approach

The simplest way to get started is with the configuration-based approach:

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with memory configuration at the orchestrator level
app = muxi(
    buffer_size=10,  # Context window size of 10 messages
    buffer_multiplier=10,  # Total buffer capacity will be 10x context window (default: 10)
    long_term="sqlite:///data/memory.db"  # Enable long-term memory with SQLite
    # Alternatively: long_term="postgresql://user:pass@localhost/muxi"
)

# Add an agent from a configuration file
app.add_agent("assistant", "configs/assistant.yaml")

# Chat with the agent
response = await app.chat("Hello, who are you?")
print(response)

# Run the server
# app.run()
```

Example configuration file (`configs/muxi_config.yaml`):

```yaml
# Memory configuration at the top level
memory:
  buffer_size: 10  # Context window size of 10 messages
  buffer_multiplier: 10  # Total buffer capacity will be 10x context window (default: 10)
  long_term: true  # Enable long-term memory using default SQLite in app's root
  # Or specify SQLite: long_term: "sqlite:///data/memory.db"
  # Or specify PostgreSQL: long_term: "postgresql://user:pass@localhost/muxi"

# Agents defined as an array
agents:
  - name: assistant
    system_message: You are a helpful AI assistant.
    model:
      provider: openai
      api_key: "${OPENAI_API_KEY}"
      model: gpt-4o
      temperature: 0.7
    knowledge:
      - path: "knowledge/domain_facts.txt"
        description: "Specialized domain knowledge for this agent"
    mcp_servers:
    - name: web_search
      url: http://localhost:5001
      credentials:
      - id: search_api_key
        param_name: api_key
        required: true
        env_fallback: SEARCH_API_KEY
```

### Programmatic Approach

You can also create agents programmatically using the Orchestrator interface:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.knowledge.base import FileKnowledge

# Create an orchestrator with memory configuration
buffer_memory = BufferMemory(
    max_size=10,                    # Context window size
    buffer_multiplier=10,           # Total capacity = 10 × 10 = 100 messages
    model=OpenAIModel(model="text-embedding-ada-002")
)
long_term_memory = LongTermMemory("postgresql://user:password@localhost:5432/muxi")

orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    long_term_memory=long_term_memory
)

# Create a basic agent (memory is provided by the orchestrator)
agent = orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    system_message="You are a helpful AI assistant.",
    description="General-purpose assistant for answering questions and providing information."
)

# Add domain knowledge to the agent
product_knowledge = FileKnowledge(
    path="knowledge/products.txt",
    description="Product information and specifications"
)
await agent.add_knowledge(product_knowledge)

# Create additional specialized agents
orchestrator.create_agent(
    agent_id="researcher",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    system_message="You are a helpful research assistant.",
    description="Specialized in research tasks, data analysis, and information retrieval."
)

orchestrator.create_agent(
    agent_id="local_assistant",
    model=OpenAIModel(model="gpt-4o", api_key="your_api_key"),
    system_message="You are a helpful personal assistant.",
    description="Personal assistant for tasks, reminders, and general information."
)

# Add MCP server to the agent
await orchestrator.agents["assistant"].connect_mcp_server(
    name="web_search",
    url="http://localhost:5001",
    credentials={"api_key": "your_search_api_key"}
)

# Chat with an agent (automatic routing based on query)
response = await orchestrator.chat("Tell me about quantum physics")
print(response.content)

# Chat with a specific agent
response = await orchestrator.chat("Tell me about quantum physics", agent_name="researcher")
print(response.content)

# Chat with multi-user support
response = await orchestrator.chat("Remember my name is Alice", user_id="user123")
print(response.content)

# Run the server
# orchestrator.run()
```

### Using the CLI

```bash
# Start a chat session with the default agent
muxi chat

# Send a one-off message
muxi send "What is the capital of France?"

# Run the server
muxi run
```

### Using the Server (API w/ Websockets + MCP Server)

Start the server:

```bash
muxi run
```

Then, in another terminal or from your application:

```bash
# Send a message to an agent
curl -X POST http://localhost:5050/agents/assistant/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the capital of France?"}'
```

### Using the Web UI

The web UI requires installing the web module first:

```bash
# Install the web UI module
pip install muxi-web

# Start the server with web UI support
muxi run
```

Then open your browser and navigate to:

```
http://localhost:5050
```

Alternatively, you can run the web UI separately if you already have a MUXI server running elsewhere:

```bash
# Start just the web UI, connecting to a server
muxi-web --server-url http://your-server-address:5050
```

## Core Capabilities

### Working with MCP Servers

The framework provides a powerful interface for working with Model Context Protocol (MCP) servers:

```python
from muxi import muxi

# Initialize MUXI with memory configuration
app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term=True  # Use default SQLite database
)

# Add an agent with MCP server capabilities
app.add_agent("assistant", "configs/assistant.yaml")

# Get centralized MCPService instance
mcp_service = await app.get_mcp_service()

# Connect to an HTTP-based MCP server with credentials
await app.get_agent("assistant").connect_mcp_server(
    name="weather",
    url="http://localhost:5001",  # For HTTP+SSE transport
    credentials={"api_key": "your_weather_api_key"}  # Optional: can be omitted if no authentication is needed
)

# Connect to a command-line based MCP server without credentials
await app.get_agent("assistant").connect_mcp_server(
    name="calculator",
    command="npx -y @modelcontextprotocol/server-calculator",
    # No credentials parameter needed for servers that don't require authentication
)

# Chat with the agent using MCP server capabilities
response = await app.chat(
    "What's the weather in New York? Also, what's 123 * 456?",
    user_id="user123"
)
print(response.content)  # Agent will use both MCP servers to answer
```

Example MCP server configuration in YAML:

```yaml
# Memory configuration at the top level
memory:
  buffer_size: 10
  buffer_multiplier: 10
  long_term: true  # Use default SQLite database

# Agents configuration
agents:
  - name: assistant
    system_message: You are a helpful AI assistant.
    model:
      provider: openai
      model: gpt-4o
    mcp_servers:
    - name: web_search
      url: http://localhost:5001
      credentials:  # Optional: can be omitted if no authentication is required
      - id: search_api_key
        param_name: api_key
        required: true
        env_fallback: SEARCH_API_KEY
    - name: calculator
      command: npx -y @modelcontextprotocol/server-calculator
      # No credentials section needed for servers that don't require authentication
```

### MCP Server Implementation

MUXI can not only connect to MCP servers but also expose your agents as MCP-compatible servers:

```python
from muxi import muxi

# Initialize MUXI with memory configuration
app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term="sqlite:///data/memory.db"
)

# Add an agent from configuration
app.add_agent("assistant", "configs/assistant.yaml")

# Start both API and MCP server on different ports
app.run_server(
    port=5050,
    mcp=True,
    mcp_port=5051
)

# Or start just the MCP server
app.start_mcp(port=5051)
```

This allows other MCP clients (like Claude, Cursor, or other AI assistants) to connect to your MUXI agents and use their capabilities.

### Working with Smart Buffer Memory

The FAISS-backed smart buffer memory system provides powerful semantic search capabilities:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create embedding model for vector search
embedding_model = OpenAIModel(model="text-embedding-ada-002", api_key="your_api_key")

# Create a buffer memory with semantic search capabilities
buffer = BufferMemory(
    max_size=10,                  # Context window size (recent messages)
    buffer_multiplier=10,         # Total capacity = 10 × 10 = 100 messages
    model=embedding_model,        # Model for generating embeddings
    vector_dimension=1536,        # Dimension for OpenAI embeddings
    recency_bias=0.3              # Balance between semantic (0.7) and recency (0.3)
)

# Create orchestrator with the smart buffer memory
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=LongTermMemory(connection_string="postgresql://user:pass@localhost/muxi")
)

# Add a message to the buffer
await orchestrator.add_to_buffer_memory(
    "Important information about quantum computing algorithms",
    metadata={"topic": "quantum computing", "importance": "high"}
)

# Search the memory (semantically similar content)
results = await orchestrator.search_memory(
    "Tell me about quantum algorithms",
    k=5
)

# Search with metadata filtering
results = await orchestrator.search_memory(
    "Tell me about important concepts",
    filter_metadata={"importance": "high"},
    k=5
)

# Adjust recency bias for different use cases
# For human conversations (favor recent)
results = await orchestrator.search_memory(
    "What did I just talk about?",
    recency_bias=0.7,             # Higher value favors recency
    k=5
)

# For factual queries (favor semantic)
results = await orchestrator.search_memory(
    "Tell me about quantum entanglement",
    recency_bias=0.1,             # Lower value favors semantic relevance
    k=5
)
```

The smart buffer memory automatically falls back to recency-based search when no embedding model is available or when semantic search fails, ensuring robustness in all scenarios.

### Intelligent Message Routing

Automatically route user messages to the most appropriate agent based on their content:

```python
from muxi import muxi

# Initialize MUXI with memory and multiple specialized agents
app = muxi(
    buffer_size=10,
    buffer_multiplier=10,  # Optional: default is 10
    long_term="postgresql://user:pass@localhost/muxi"
)

# Add multiple specialized agents
await app.add_agent("weather", "configs/weather_agent.yaml")
await app.add_agent("finance", "configs/finance_agent.json")
await app.add_agent("travel", "configs/travel_agent.yaml")

# The message will be automatically routed to the most appropriate agent
response = await app.chat("What's the weather forecast for Tokyo this weekend?")  # Weather agent
response = await app.chat("Should I invest in tech stocks right now?")  # Finance agent
response = await app.chat("What are the best attractions in Barcelona?")  # Travel agent
```

The orchestrator analyzes the content of each message and intelligently routes it to the most suitable agent based on their specializations and descriptions. This means you don't need to specify which agent should handle each request - the system figures it out automatically.

Configure the routing system through environment variables:

```
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0
```

### Agent-to-Agent (A2A) Communication

Enable collaboration between specialized agents:

```python
from muxi import muxi

# Initialize MUXI with memory and multiple specialized agents
app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term="sqlite:///data/memory.db"
)

# Add multiple specialized agents
await app.add_agent("researcher", "configs/researcher_agent.yaml")
await app.add_agent("writer", "configs/writer_agent.yaml")
await app.add_agent("fact_checker", "configs/fact_checker_agent.yaml")

# Enable A2A communication (enabled by default, but can be configured)
app.configure_a2a(enabled=True, scope="internal")

# Process a complex query that requires multiple agents
response = await app.chat(
    "Research quantum computing advancements in 2025 and write a summary report",
    user_id="user123"
)

# Behind the scenes:
# 1. The message is routed to the researcher agent
# 2. Researcher agent gathers information
# 3. Researcher delegates to the writer agent to create the summary
# 4. Writer creates draft and delegates to fact_checker for verification
# 5. Final verified response returned to the user
```

A2A communication allows agents to collaborate seamlessly, creating more powerful workflows than any single agent could accomplish alone.

### Working with Memory and Context Memory

```python
from muxi import muxi

# Initialize MUXI with memory configuration
app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term="postgresql://user:pass@localhost/muxi"
)

# Add multiple agents from configuration files
await app.add_agent("weather", "configs/weather_agent.yaml")
await app.add_agent("assistant", "configs/assistant.yaml")

# Add context memory for a specific user
user_id = "user123"
knowledge = {
    "name": "Alice",
    "location": {"city": "New York", "country": "USA"},
    "preferences": {"language": "English", "units": "metric"}
}
await app.add_user_context_memory(user_id, knowledge)

# Chat with personalized context
# Note: No need to specify agent_id - the orchestrator will select the appropriate agent
response = await app.chat(
    "What's the weather like in my city?",
    user_id=user_id
)
print(response.content)  # Uses Alice's location data from context memory

# For memory operations that are specific to an agent, you can specify agent_id
memory_results = await app.search_memory(
    "What did the user ask about the weather?",
    agent_id="weather",  # Specify when you need to target a specific agent's memory
    user_id=user_id,
    limit=5
)
print("Related memories:", memory_results)
```

### Vector Database Support

MUXI supports multiple vector database backends for long-term memory:

#### Using SQLite with `sqlite-vec`

Ideal for local development, small-scale deployments, or edge environments:

```python
# In your environment variables (.env file)
USE_LONG_TERM_MEMORY=sqlite:///data/memory.db
# Or for default SQLite database in app's root directory
USE_LONG_TERM_MEMORY=true

# Or in your configuration file (YAML)
memory:
  buffer_size: 10
  buffer_multiplier: 10
  long_term: "sqlite:///data/memory.db"
  # Or for default SQLite database in app's root directory
  # long_term: true

# Or programmatically
from muxi import muxi

app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term="sqlite:///data/memory.db"
)
```

#### Using PostgreSQL with `pgvector`

Recommended for production deployments or multi-user environments:

```python
# In your environment variables (.env file)
POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/muxi

# Or in your configuration file (YAML)
memory:
  buffer_size: 10
  buffer_multiplier: 10
  long_term: "postgresql://user:password@localhost:5432/muxi"

# Or programmatically
from muxi import muxi

app = muxi(
    buffer_size=10,
    buffer_multiplier=10,
    long_term="postgresql://user:password@localhost:5432/muxi"
)
```

## Technical Details

### Communication Protocols

MUXI implements a hybrid protocol approach for optimal performance and flexibility:

- **HTTP**: For standard API requests like configuration and management
- **Server-Sent Events (SSE)**: For streaming responses token-by-token
- **WebSockets**: For multi-modal capabilities with bi-directional communication

### Package Structure

The MUXI Framework is organized into a modular architecture with the following components:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, MCP interface
│   │   ├── muxi/core/
│   │   │   ├── agent.py        # Agent implementation
│   │   │   ├── orchestrator.py # Orchestrator with centralized memory
│   │   │   ├── memory/         # Memory subsystems
│   │   │   │   ├── buffer.py   # FAISS-backed smart buffer memory
│   │   │   │   └── long_term.py # Vector storage with PostgreSQL/SQLite
│   │   │   ├── mcp/            # Model Context Protocol
│   │   │   │   └── service.py  # Centralized MCPService singleton
│   │   │   └── models/         # LLM provider implementations
│   ├── server/        # REST API and WebSocket server
│   ├── cli/           # Command-line interface
│   ├── web/           # Web user interface
│   └── meta/          # Meta-package that integrates all components
└── tests/             # Test suite for all components
```

### Language-Specific SDKs (Coming in v0.5.0)

MUXI Framework will provide client libraries for popular programming languages:

- **TypeScript/JavaScript SDK**: For web and Node.js applications
- **Go SDK**: For backend integrations
- **Other Planned SDKs**: Java/Kotlin, Rust, C#/.NET, PHP, Ruby

**Each SDK will provide:**

- Full REST API client implementation
- WebSocket client for real-time communication
- MCP server protocol implementation
- Consistent developer experience across languages

## Development Roadmap

The MUXI Framework development is focused on the following priorities:

1. **Smart Buffer Memory Optimization** - ✅ Implemented FAISS-backed memory with hybrid retrieval; ongoing optimization
2. **REST API & MCP Server Implementation** - ✅ Implemented centralized MCP service; in progress: REST API endpoints
3. **WebSocket API Implementation** - Enhancing real-time communication with multi-modal message support
4. **CLI Interfaces** - Improving command-line interface with support for all API operations
5. **Web UI** - Developing a responsive web interface with real-time updates
6. **Agent-to-Agent Communication** - Implementing the A2A protocol for inter-agent communication
7. **Vector Database Enhancements** - Optimizing vector operations and supporting additional databases
8. **LLM Providers** - Expanding support for various LLM providers (Anthropic, Gemini, Grok, local models)
9. **Testing and Documentation** - Comprehensive testing and documentation for all components
10. **Deployment & Package Distribution** - Docker containerization, Kubernetes deployment, and CI/CD pipelines
11. **Language-Specific SDKs** - Developing client libraries for TypeScript, Go, Java/Kotlin, Rust, and C#/.NET
12. **Multi-Modal Capabilities** - Adding support for document, image, and audio processing
13. **Security Enhancements** - Implementing advanced security features for enterprise-grade deployments

The [roadmap](docs/roadmap.md) file provides more detailed information about the project roadmap.

## License

This project is licensed under a dual licensing model to balance open-source collaboration with sustainable business practices.

### Development Phase (Pre-Version 1.0)

The software is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0)** during the development phase. This license prohibits commercial use, derivative works, and redistribution to ensure the integrity of the development process and to **avoid project fragmentation before it reaches maturity**.

### After Version 1.0 Release

When the project reaches version 1.0, it will switch to a more permissive open-source license that permits unrestricted use for non-commercial use cases and extensive use for commercial use cases.

## Contributing

**Contributions are welcome!** Please read my [Contributing Guide](docs/contributing.md) for details on the code of conduct, development setup, and the process for submitting pull requests.

## Acknowledgements

The many open-source projects that make this framework possible ❤️

