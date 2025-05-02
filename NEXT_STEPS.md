# Developer Tasks and Implementation Checklist

This document provides a detailed task tracker for developers working on the MUXI Framework. It contains specific implementation tasks, checklists, and tracks completed work. For the high-level strategic vision and roadmap, see the [docs/roadmap.md](docs/roadmap.md) file.

## Completed Work

Core components of the muxi framework now implemented:

1. **Model Context Protocol (MCP)**: Standardized communication with LLMs
   - [x] Fixed message handling to properly use role/content attributes
   - [x] Improved process_message and process_tool_call methods
   - [x] Standardized message structure for compatibility with all LLM providers
   - [x] Implemented centralized MCPService as a singleton pattern
   - [x] Added ToolParser for extracting tool calls from LLM responses
   - [x] Added configurable request timeouts at orchestrator, agent, and per-request levels
   - [x] Implemented thread-safe tool invocation with locks for concurrent access
   - [x] Created comprehensive documentation in `.cursor/rules/mcp_service.mdc`
   - [x] Added proper error handling with consistent patterns throughout MCP interactions
2. **Memory System**:
   - [x] Implemented FAISS-backed smart buffer memory with hybrid semantic+recency retrieval
   - [x] Added configurable recency bias parameter to balance semantic relevance with time
   - [x] Implemented graceful degradation to recency-only search when no model is available
   - [x] Improved metadata filtering capabilities for more targeted memory retrieval
   - [x] Added thread-safe operations for concurrent access to memory systems
   - [x] Created comprehensive documentation in `.cursor/rules/smart_buffer_memory.mdc`
   - [x] Long-term memory using PostgreSQL with pgvector
   - [x] Long-term memory using SQLite with sqlite-vec extension
   - [x] Added proper error handling and fallback mechanisms for vector extensions
   - [x] Memobase system for multi-user support with partitioned memories
   - [x] Domain knowledge system for user-specific structured information
   - [x] Robust database schema with optimized tables and indexes
   - [x] Migration system for schema version control
   - [x] Centralized memory management at orchestrator level
3. **MCP Server Integration**:
   - [x] MCP Handler for communication with external services
   - [x] Centralized MCPService for managing all MCP server communications
   - [x] MCP message processing
   - [x] Example MCP servers (Calculator, Web Search)
   - [x] Implement proper transport abstraction with factory pattern
   - [x] Support for HTTP+SSE transport
   - [x] Support for Command-line transport
   - [x] Implement reconnection with exponential backoff
   - [x] Implement cancellation support for in-progress operations
   - [x] Comprehensive error handling and diagnostics
   - [x] Integration with the official MCP Python SDK
   - [x] Make credentials optional for MCP servers that don't require them
4. **Agent Class**: Main interface combining LLM, memory, and MCP servers
   - [x] Agent-level knowledge base for specialized domain knowledge
   - [x] Dynamic embedding generation using the agent's model
   - [x] File-based knowledge sources with efficient caching
   - [x] Updated agent to use centralized MCPService singleton
   - [x] Removed direct MCP handler dependency in favor of the shared service
   - [x] Agent now delegates to orchestrator for all memory operations
5. **Orchestrator**: For managing multiple agents and their interactions
   - [x] Intelligent message routing with LLM-based agent selection
   - [x] Agent descriptions for specialized capabilities
   - [x] Automatic caching of routing decisions for performance
   - [x] Centralized memory management for all agents
   - [x] Centralized API key handling
   - [x] Enhanced support for multi-user environments
6. **Configuration System**: For loading and managing configuration
   - [x] Support for YAML and JSON configuration files
   - [x] Environment variable substitution in configurations
   - [x] Robust validation of configuration parameters
7. **Example Script**: To demonstrate how to use the framework
8. **Real-Time Communication**:
   - [x] WebSocket server for real-time agent interaction
   - [x] Proper message serialization for MCP messages
   - [x] Shared orchestrator instance between REST API and WebSocket server
   - [x] Resilient connection handling with automatic reconnection
   - [x] Comprehensive error handling
   - [x] Support for multi-user WebSocket connections
9. **API Improvements**:
   - [x] REST API for agent management and interaction
   - [x] Multi-user support endpoints
   - [x] Memory management endpoints including search and clear
   - [x] Comprehensive test coverage
10. **Command Line Interface**:
    - [x] Rich terminal-based interface for agent interaction
    - [x] Commands for chat, one-off messages, and server management
    - [x] Colored output with Markdown support
    - [x] Convenient launcher for API server and web UI
11. **Code Quality**:
    - [x] Resolved deprecation warnings for SQLAlchemy and FastAPI
    - [x] Standardized line length configuration across linting tools
    - [x] Improved VS Code integration with consistent formatting rules
    - [x] Fixed all test warnings and errors
    - [x] Implemented pytest.ini configuration to filter FAISS-related DeprecationWarnings
12. **Developer Tools**:
    - [x] MCP Server Generator with interactive CLI wizard
    - [x] Template-based code generation system
    - [x] Flattened template structure for simpler maintenance
13. **Architecture Evolution**:
    - [x] Restructured codebase into modular packages
    - [x] Created setup.py for each package with appropriate dependencies
    - [x] Implemented proper monorepo structure
    - [x] Created development installation scripts
    - [x] Fixed cross-package imports
    - [x] Completed migration from src/muxi to direct muxi directories
    - [x] Updated all import paths to reflect the new structure
    - [x] Created meta package for unified installation
    - [x] Updated all documentation to reflect new package structure
14. **Vector Database Support**:
    - [x] SQLite with sqlite-vec integration for local deployments
    - [x] Reorganized extensions directory structure
    - [x] Added proper Python package for easier installation
    - [x] Implemented automatic fallback from package to binary extensions
    - [x] Enhanced compatibility with various platforms and architectures

## Todo List

Things to do next to enhance the framework, ordered by priority:

### 1. Smart Buffer Memory Optimization

Building on the new FAISS-backed smart buffer memory:

- [x] Implement FAISS-backed smart buffer memory with hybrid retrieval
- [ ] Fine-tune recency bias parameters for different use cases
- [ ] Add performance benchmarks for memory operations
- [ ] Optimize vector operations for large context sizes
- [ ] Implement memory compression for improved storage efficiency

### 2. REST API & MCP Server Implementation

Based on the prd-api-server.md specifications, implement the unified MUXI API Server:

- [x] Implement centralized MCPService as a singleton for MCP server interactions
- [ ] Implement unified API Server architecture
  - [ ] Core API server with shared components (auth, logging, rate limiting)
  - [ ] Configuration system with environment variable support
  - [ ] Structured error handling and response format
  - [ ] Consistent response structure across all endpoints
- [ ] Implement REST API endpoints
  - [ ] User/Interface endpoints for agent interaction
    - [ ] Agent chat endpoints (POST /api/v1/agents/{agent_id}/chat)
    - [ ] Orchestrator chat endpoints (POST /api/v1/chat)
    - [ ] Conversation history endpoints (GET /api/v1/conversations)
  - [ ] Developer/Management endpoints
    - [ ] Agent management (GET/POST/PATCH/DELETE /api/v1/agents)
    - [ ] Memory operations (GET/DELETE /api/v1/agents/{agent_id}/memory)
    - [ ] Context memory CRUD operations
    - [ ] MCP server management
    - [ ] Knowledge management
    - [ ] System information and monitoring
- [ ] Implement dual-key authentication system
  - [ ] User/Interface API keys for client access (sk_muxi_user_*)
  - [ ] Administrative API keys for system management (sk_muxi_admin_*)
  - [ ] Automatic key generation mechanism
  - [ ] Secure key storage and validation
- [ ] Add SSE streaming support
  - [ ] Stream agent responses in real-time
  - [ ] Event-based streaming format
  - [ ] Connection recovery mechanism
  - [ ] Tool call event streaming
- [ ] Implement MCP protocol support
  - [ ] Integrate FastMCP or similar library
  - [ ] Tool definition discovery and exposure
  - [ ] Request routing to appropriate agents
  - [ ] Streaming MCP responses
- [ ] Set up WebRTC signaling server (foundation for multi-modal)
  - [ ] Session management endpoints
  - [ ] Signaling protocol implementation
  - [ ] Integration with agent message processing
- [ ] Add security features
  - [ ] CORS configuration
  - [ ] Security headers
  - [ ] Input validation
  - [ ] Rate limiting per endpoint and per key
- [ ] Create OpenAPI/Swagger documentation
  - [ ] Document all endpoints with examples
  - [ ] Create interactive API playground
  - [ ] Include authentication instructions

### 3. WebSocket API Implementation

Building on the api.md specifications, enhance the WebSocket API:

- [ ] Implement WebSocket protocol for real-time communication
- [ ] Add support for multi-modal messages (text, images, audio)
- [ ] Implement proper error handling and recovery
- [ ] Add reconnection logic with exponential backoff
- [ ] Support for attachments as specified in api.md

### 4. CLI Interfaces

- [ ] Enhance CLI interface
  - [ ] Add support for all API operations described in api.md
  - [ ] Improve user experience with better formatting and colors
  - [ ] Add multi-modal interaction support
  - [ ] Implement configuration management commands
- [ ] Improve API server based on api.md specifications
  - [ ] Implement all endpoints described in the spec
  - [ ] Add comprehensive test coverage

### 5. Web UI

- [ ] Develop web interface
  - [ ] Create responsive UI for mobile and desktop
  - [ ] Implement real-time updates using WebSocket
  - [ ] Add support for multi-modal interactions
  - [ ] Build user-friendly configuration interface
  - [ ] Create agent management dashboard

### 6. Agent-to-Agent Communication (A2A)

Based on prd-a2a.md specifications:

- [ ] Implement the A2A protocol for inter-agent communication
  - [ ] Capability discovery mechanism
  - [ ] Task delegation between agents
  - [ ] Context sharing with proper isolation
  - [ ] Conversation lifecycle management
  - [ ] External agent integration
  - [ ] Security and authentication
- [ ] Enhance MCP Server Interface
  - [ ] SSE-based MCP server implementation
  - [ ] Automatic tool discovery from agent capabilities
  - [ ] NPX bridge package for non-SSE clients
  - [ ] Streaming response handling
  - [ ] Authentication shared with REST API

### 7. LLM Providers

- [x] Implement OpenAI LLM provider
- [ ] Implement Anthropic LLM provider
- [ ] Implement Gemini LLM provider
- [ ] Implement Grok LLM provider
- [ ] Add support for local models (e.g., Llama, Mistral, DeepSeek)
- [ ] Create a model router for fallback and cost optimization

### 8. Deployment & Package Distribution

- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Cloud deployment guides (AWS, GCP, Azure)
- [ ] Monitoring and logging integration
- [ ] Continuous integration workflow with GitHub Actions or similar tools
- [ ] Automatic version bumping for releases
- [ ] SQLite deployment guides for serverless and edge environments

### 9. Logging and Tracing System

Based on prd-tracing-and-logging.md specifications:

- [ ] Implement comprehensive tracing system
  - [ ] Trace lifecycle management with unique trace IDs
  - [ ] Component-level tracing (user, orchestrator, agent, MCP)
  - [ ] Multiple output formats (stdout, file logs)
  - [ ] External service integration (Papertrail, Kafka)
- [ ] Create CLI tools for trace viewing and analysis
  - [ ] Implement `muxi trace` command
  - [ ] Support filtering by component, operation, and trace ID
  - [ ] Enable log following functionality
- [ ] Implement performance-optimized logging
  - [ ] Minimal impact on response times
  - [ ] Asynchronous logging where appropriate
  - [ ] Sampling in high-traffic environments
- [ ] Add cloud integration for MUXI Cloud deployments
  - [ ] Structured JSON output format
  - [ ] Support for Vector collection agent
  - [ ] ClickHouse integration

### 10. Multi-Modal Capabilities

Transform agents into omni agents capable of handling various media types:

#### Document Processing
- [ ] PDF processing and text extraction
- [ ] Support for Office documents (Word, Excel, etc.)
- [ ] OCR for scanned documents
- [ ] Document summarization tools

#### Image Processing
- [ ] Extend MCPMessage to support image attachments
- [ ] Create image preprocessing pipeline
  - [ ] Resize and optimize images for models
  - [ ] Format conversion utilities
  - [ ] Metadata extraction
- [ ] Integrate with vision-capable models
  - [ ] OpenAI GPT-4V
  - [ ] Anthropic Claude 3
  - [ ] Google Gemini
  - [ ] Local models with vision capabilities
- [ ] Update API endpoints to handle image uploads
- [ ] Add WebSocket support for image sharing

#### Audio Processing
- [ ] Audio file handling and processing
  - [ ] Support various audio formats (MP3, WAV, etc.)
  - [ ] Audio normalization and enhancement
- [ ] Speech-to-text integration
  - [ ] OpenAI Whisper integration
  - [ ] Other speech recognition options
- [ ] Text-to-speech for agent responses
  - [ ] Voice selection options
  - [ ] Emotion/tone control
- [ ] Streaming audio capabilities
  - [ ] Design WebSocket protocol for audio streaming
  - [ ] Implement real-time audio processing

### 11. Language-Specific SDKs

Focus on TypeScript/JavaScript SDK first:

- [ ] TypeScript/JavaScript SDK
  - [ ] REST API client with full endpoint coverage
  - [ ] WebSocket client implementation
  - [ ] MCP server protocol implementation for JavaScript tools
  - [ ] Comprehensive examples and documentation
  - [ ] NPM package distribution

### 12. Memory System Enhancements

Building on the new FAISS-backed smart buffer memory:

- [ ] Implement context memory templates for common use cases
- [ ] Add context memory namespaces for better organization
- [ ] Complete memory-related REST API endpoints
- [ ] Optimize vector operations for improved performance
- [ ] Develop data migration tools between database backends
- [ ] Enhance multi-modal content support in memory systems
- [ ] Complete automatic user information extraction implementation
- [ ] Implement interface-level user ID generation
- [ ] Add advanced vector database features for scalability

### 13. Testing and Documentation

- [ ] Unit tests for all new API endpoints
- [ ] Integration tests for API and WebSocket endpoints
- [ ] Create e2e tests for the framework
- [ ] Performance benchmarks for API endpoints
- [ ] Complete CLI documentation
- [ ] Expand API documentation beyond api.md with practical examples
- [ ] User guides for advanced use cases
- [ ] Example projects showcasing API usage
- [ ] Generate API documentation with Fumadocs

### 14. Additional Language SDKs

After completing TypeScript/JavaScript SDK:

- [ ] Go SDK
  - [ ] API client library
  - [ ] MCP server implementation helpers
  - [ ] Utilities for agent configuration

- [ ] Other Language SDKs
  - [ ] Java/Kotlin SDK
  - [ ] Rust SDK
  - [ ] C#/.NET SDK
  - [ ] PHP SDK
  - [ ] Ruby SDK (optional)

- [ ] SDK Development Tools
  - [ ] API client generators from OpenAPI spec
  - [ ] Shared test suite for SDK validations
  - [ ] Consistent interface definitions across languages
  - [ ] Version syncing mechanisms with core framework

### 15. Security Enhancements

- [ ] Enhance API security
  - [ ] Rate limiting and throttling
  - [ ] Input validation and sanitization
  - [ ] IP-based restrictions
- [ ] Implement advanced authentication methods
  - [ ] OAuth and OpenID Connect integration
  - [ ] Role-based access control
  - [ ] Multi-factor authentication options
- [ ] Add data protection features
  - [ ] Encryption at rest and in transit
  - [ ] Privacy controls
  - [ ] Compliance with security standards
- [ ] Implement security auditing
  - [ ] Vulnerability scanning
  - [ ] Security logging
  - [ ] Access monitoring

### 16. Stability and Performance

- [x] Comprehensive error monitoring
- [x] Database schema optimization and indexing
- [x] Improved API key handling for tests
- [x] Standardized environment variable loading
- [ ] Load testing for concurrent connections
- [ ] Benchmarking WebSocket message throughput
- [ ] Connection pooling for database access

## Implementation Roadmap

Based on api.md roadmap and current progress:

### Phase 1: Core API (v0.3.0) - In Progress
- [x] Smart buffer memory with FAISS-backed vector similarity
- [x] Centralized MCPService as singleton pattern
- [x] Authentication system
- [x] Agent management endpoints (basic)
- [x] Basic conversation endpoints
- [x] Memory search and management
- [x] SQLite vector integration
- [ ] Complete API as outlined in api.md

### Phase 2: Advanced Features (v0.4.0)
- [ ] Complete MCP server management endpoints
- [ ] Knowledge management endpoints
- [ ] WebSocket support for real-time communication
- [ ] Streaming responses
- [ ] Basic MCP server interface implementation
- [ ] Initial Agent-to-Agent (A2A) communication protocol

### Phase 3: Scaling & Monitoring (v0.5.0)
- [ ] System status and monitoring
- [ ] API usage statistics
- [ ] Rate limiting and quotas
- [ ] Multi-modal content support
- [ ] Advanced A2A communication with capability discovery
- [ ] Full MCP Server interface with streaming response support
- [ ] Language-specific SDKs (TypeScript, Go, others)

## Contribution Guidelines

Guidelines for contributing to the framework:

1. **Code Style**: Follow PEP 8 guidelines
2. **Documentation**: Document all public functions, classes, and methods
3. **Testing**: Write tests for all new features
4. **Pull Requests**: Create a pull request with a clear description of changes
5. **Issues**: Use GitHub issues for bug reports and feature requests

## Example Scenarios

### Simple Agent with Configuration Files

This scenario demonstrates a complete workflow from installation to running an agent using the new configuration-based approach:

1. **Install the Framework**

   ```bash
   # Clone the repository
   git clone https://github.com/your-org/muxi.git
   cd muxi

   # Install dependencies
   pip install -e .
   ```

2. **Create a Configuration File**

   Create a file `configs/my_agent.yaml`:

   ```yaml
   name: my_assistant
   system_message: You are a helpful assistant with weather capabilities.
   model:
     provider: openai
     api_key: "${OPENAI_API_KEY}"
     model: gpt-4o
     temperature: 0.7
   memory:
     buffer: 10  # Buffer window size of 10
     long_term: true  # Enable long-term memory with default SQLite in app's root
     # Or use SQLite explicitly: long_term: "sqlite:///data/memory.db"
     # Or PostgreSQL: long_term: "postgresql://user:password@localhost:5432/muxi"
   knowledge:
   - path: "knowledge/weather_facts.txt"
     description: "Facts about weather patterns and climate"
   - path: "knowledge/geography.txt"
     description: "Information about global geography"
   mcp_servers:
   - name: calculator
     url: http://localhost:5000
     credentials: []
   - name: weather
     url: http://localhost:5001
     credentials:
     - id: weather_api_key
       param_name: api_key
       required: true
       env_fallback: WEATHER_API_KEY
   - name: web_search
     url: http://localhost:5002
     credentials:
     - id: search_api_key
       param_name: api_key
       required: true
       env_fallback: SEARCH_API_KEY
   ```

3. **Set Up Environment Variables**

   Create a `.env` file:

   ```
   OPENAI_API_KEY=your_openai_key_here
   # PostgreSQL connection
   POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/muxi
   # Or SQLite connection
   # USE_LONG_TERM_MEMORY=sqlite:///data/memory.db
   # Or just enable default SQLite in app's root directory
   # USE_LONG_TERM_MEMORY=true
   WEATHER_API_KEY=your_weather_api_key
   SEARCH_API_KEY=your_search_api_key
   ```

4. **Create a Simple Application**

   Create a file `app.py`:

   ```python
   from dotenv import load_dotenv
   from muxi import muxi

   # Load environment variables
   load_dotenv()

   # Initialize MUXI - the database connection will be loaded
   # automatically from POSTGRES_DATABASE_URL when needed
   mx = muxi()

   # Add agent from configuration
   mx.add_agent("assistant", "configs/my_agent.yaml")

   # Interactive mode - explicitly specify the agent (optional)
   response = mx.chat("What's the weather like in London?", agent_name="assistant")
   print(f"Response: {response}")

   # Let the orchestrator automatically select the appropriate agent (recommended)
   response = mx.chat("What's the weather like in New York?")
   print(f"Response: {response}")

   # Add knowledge programmatically
   from muxi.knowledge.base import FileKnowledge
   new_knowledge = FileKnowledge(path="knowledge/climate_data.txt", description="Climate data for major cities")
   mx.get_agent("assistant").add_knowledge(new_knowledge)

   # Or start a server
   # mx.start_server(port=5050)
   ```

5. **Run the Application**

   ```bash
   python app.py
   ```

### Working with Smart Buffer Memory

Demonstrates how to use the FAISS-backed smart buffer memory:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import SmartBufferMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create embedding model for vector search
embedding_model = OpenAIModel(model="text-embedding-ada-002", api_key="your_api_key")

# Create a buffer memory with semantic search capabilities
buffer = SmartBufferMemory(
    max_size=100,                 # Store up to 100 messages
    model=embedding_model,        # Model for generating embeddings
    vector_dimension=1536,        # Dimension for OpenAI embeddings
    recency_bias=0.3              # Balance between semantic (0.7) and recency (0.3)
)

# Create orchestrator with the smart buffer memory
orchestrator = Orchestrator(buffer_memory=buffer)

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
```

### RESTful API Server

According to the api.md specification, starting a MUXI API server:

```python
from muxi import muxi

app = muxi()

# Load agents from configurations
app.add_agent("assistant", "configs/assistant.yaml")
app.add_agent("weather_expert", "configs/weather_agent.yaml")
app.add_agent("finance_expert", "configs/finance_agent.yaml")

# Start the server with authentication
app.run_server(
    port=5050,
    api_key=True,  # Auto-generate an API key and display it once
    # Or provide a specific key: api_key="sk_muxi_your_custom_key"
)
```

### Client-Server Connection
This scenario demonstrates connecting to a remote MUXI server:

1. **Install the Client Library**

   ```bash
   # Install just the client component
   pip install muxi-cli
   ```

2. **Connect to a Remote Server**

   ```python
   from muxi import muxi

   # Connect to an existing MUXI server
   app = muxi(
       server_url="http://server-ip:5050",
       api_key="sk_muxi_abc123"
   )

   # Use the same API as with local mode
   app.add_agent("remote_assistant", "configs/assistant.yaml")
   response = app.chat("Hello, remote assistant!")
   print(response)
   ```

