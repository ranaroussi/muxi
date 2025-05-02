# MUXI Framework Active Context

## Current Work Focus

The current development focus is on implementing the complete REST API as defined in the `.context/scratchpad/api.md` specification file. This involves standardizing all API endpoints, implementing authentication, error handling, and ensuring proper documentation. This work is considered high priority as it forms the foundation for client applications to interact with the MUXI Framework.

Additional priority areas include:
- Improving and optimizing the FAISS-backed smart buffer memory system
- Enhancing the centralized MCPService singleton architecture
- Refining the automatic user information extraction system

### Primary Areas of Focus

1. **API Implementation**: Implementing the full set of REST endpoints defined in the API specification
2. **Authentication System**: Implementing a robust API key authentication system
3. **Error Handling**: Standardizing error responses across all endpoints
4. **Streaming Support**: Enhancing SSE streaming for chat responses
5. **Documentation**: Creating comprehensive API documentation with Swagger/OpenAPI
6. **SQLite Vector Integration**: Enhancing local deployment capabilities with sqlite-vec extension
7. **Agent-to-Agent Protocol**: Implementing the A2A protocol for inter-agent communication
8. **MCP Server Interface**: Creating an SSE-based MCP server endpoint for MCP host integration
9. **Memory Optimization**: Fine-tuning the FAISS-backed smart buffer memory for improved performance
10. **Automatic Information Extraction**: Implementing a system to automatically identify and store important user information from conversations

## Recent Changes

### Major Changes

1. **Buffer Memory Enhancements**:
   - Renamed SmartBufferMemory to BufferMemory for clarity and consistency
   - Added buffer_multiplier parameter to separate context window size from total buffer capacity
   - Updated configuration system to use buffer_size instead of buffer for better naming consistency
   - Simplified configuration in muxi constructor: `muxi(buffer_size=10, buffer_multiplier=10, long_term_memory="connection_string")`
   - Updated all documentation to reflect the new parameter names and semantics
   - Improved examples to demonstrate appropriate sizing for different use cases

2. **Smart Buffer Memory Implementation**:
   - Implemented a FAISS-backed smart buffer memory to replace the simple deque-based buffer
   - Added hybrid semantic+recency search capabilities for better context retrieval
   - Implemented graceful degradation to recency-only search when a model isn't available
   - Added configurable recency bias parameter to balance semantic relevance with temporal proximity
   - Improved metadata filtering capabilities for more targeted memory retrieval
   - Integrated thread-safe operations for concurrent access
   - Added comprehensive documentation in `.cursor/rules/smart_buffer_memory.mdc`

3. **Centralized MCP Service Implementation**:
   - Implemented a centralized MCPService as a singleton for managing all MCP server connections
   - Created a dedicated ToolParser to handle various tool call formats in LLM responses
   - Updated Agent class to use the centralized service for MCP server interactions
   - Removed direct MCP handler dependency from Agent in favor of the shared service
   - Added server_id to MCPServer for consistent identification
   - Implemented thread-safe tool invocation with locks for concurrent access
   - Improved error handling with consistent patterns throughout MCP interactions
   - Added the ability to customize request timeout at various levels: Orchestrator, Agent, and per-request
   - Added comprehensive documentation in `.cursor/rules/mcp_service.mdc`

4. **Package Structure Updates**:
   - Completed migration from src/muxi to direct muxi directories in all packages
   - Updated all import paths to reflect the new structure
   - Reorganized package setup files (from pyproject.toml to setup.py)
   - Created meta package for unified installation
   - Updated all documentation to reflect new package structure
   - Updated directory references in all MDC rule files

5. **Memory Architecture Migration**:
   - Moved memory systems from agent level to orchestrator level for centralized management
   - Orchestrator now owns and manages all memory systems (buffer and long-term)
   - Agent constructor no longer accepts direct memory parameters
   - Simplified memory configuration in muxi constructor: `muxi(buffer_memory=50, long_term_memory="connection_string")`
   - Memory operations now exposed through orchestrator: `orchestrator.search_memory()`, `orchestrator.add_to_buffer_memory()`
   - Support for Postgres and SQLite via direct connection strings: `"postgresql://..."` or `"sqlite:///..."`
   - Default SQLite database in app's root directory when using `long_term_memory=True`
   - Enhanced support for multi-user environments with `is_multi_user=True` parameter at orchestrator level
   - Improved memory sharing across multiple agents for better context consistency
   - Simplified configuration files by moving memory to top-level parameters

6. **SQLite Vector Integration**:
   - Added support for sqlite-vec Python package for vector similarity search
   - Simplified extensions handling by using Python package instead of binary extensions
   - Reorganized extension directory structure to improve clarity and maintainability
   - Updated memory system to work with both PostgreSQL and SQLite databases
   - Improved vector serialization for compatibility with sqlite-vec
   - Enhanced resilience with fallback mechanisms when package is unavailable

7. **Breaking Changes in Version 1.0**:
   - Removed deprecated methods like `_enhance_with_domain_knowledge()` (replaced by `_enhance_with_context_memory()`)
   - Removed `add_user_domain_knowledge()` (replaced by `add_user_context_memory()`)
   - Updated API signatures by removing the `memory` parameter from the `Agent` class (replaced by `buffer_memory`)
   - Removed backward compatibility for user_id=0 handling
   - Renamed all "domain knowledge" terminology to "context memory" throughout the codebase

8. **Test Improvements**:
   - Fixed all test warnings and errors
   - Implemented pytest.ini configuration to filter FAISS-related DeprecationWarnings
   - Improved test coverage across all components
   - Made tests more robust to handle differences in database behaviors
   - Added comprehensive tests for FAISS-backed smart buffer memory
   - Added tests for MCPService thread safety

9. **Architectural Evolution**:
   - Restructured codebase into modular packages
   - Created setup.py for each package with appropriate dependencies
   - Implemented proper monorepo structure
   - Created development installation scripts
   - Fixed cross-package imports

10. **MCP Integration**:
    - Enhanced MCP server integration with proper reconnection logic
    - Implemented transport abstraction with factory pattern
    - Added support for both HTTP+SSE and Command-line transports
    - Integrated with the official MCP Python SDK
    - Made credentials optional for MCP servers that don't require them

### Recent Pull Requests and Commits

- Fixed coroutine warnings in test files by properly handling async methods
- Updated `ClientSession` implementation to use streams appropriately
- Addressed linter issues and code formatting across the codebase
- Fixed line length issues in multiple files to comply with PEP 8 standards
- Improved organization of test files in the tests directory
- Simplified SQLite extension loading by using the sqlite-vec Python package
- Fixed import ordering in test files to comply with linting rules
- Added proper noqa comments for necessary linting exceptions
- Improved API key handling for tests with standardized environment loading
- Implemented and documented the FAISS-backed smart buffer memory
- Updated project structure documentation to reflect current package organization

## Next Steps

Based on the updated priority list, the following tasks have been prioritized:

### Updated Task Priorities

1. **Smart Buffer Memory Optimization**:
   - ✅ Implement FAISS-backed smart buffer memory with hybrid retrieval
   - Fine-tune recency bias parameters for different use cases
   - Add performance benchmarks for memory operations
   - Optimize vector operations for large context sizes
   - Add caching mechanisms for frequently accessed memory items
   - Implement memory compression for improved storage efficiency

2. **REST API & MCP Server Implementation**:
   - ✅ Implement centralized MCP service for Agent-to-MCP server communications
   - Implement standard REST API endpoints according to api.md spec
   - Implement authentication with API keys
   - Add streaming support for chat endpoints with SSE
   - Implement proper error handling with standardized format
   - Add API versioning support
   - Implement rate limiting and throttling
   - Create API documentation using OpenAPI/Swagger

3. **WebSocket API Implementation**:
   - Implement WebSocket protocol for real-time communication
   - Add support for multi-modal messages (text, images, audio)
   - Implement proper error handling and recovery
   - Add reconnection logic with exponential backoff
   - Support attachments for files and media

4. **CLI Interfaces**:
   - Enhance CLI interface with support for all API operations
   - Improve user experience with better formatting and colors
   - Add multi-modal interaction support
   - Implement configuration management commands

5. **Web UI**:
   - Create responsive UI for mobile and desktop
   - Implement real-time updates using WebSocket
   - Add support for multi-modal interactions
   - Build user-friendly configuration interface
   - Create agent management dashboard

6. **Agent-to-Agent Communication (A2A)**:
   - Implement the A2A protocol for inter-agent communication
   - Create capability discovery mechanism
   - Develop task delegation between agents
   - Implement context sharing with proper isolation
   - Add conversation lifecycle management
   - Support external agent integration
   - Implement security and authentication

7. **LLM Providers**:
   - Implement Anthropic LLM provider
   - Implement Gemini LLM provider
   - Implement Grok LLM provider
   - Add support for local models (e.g., Llama, Mistral, DeepSeek)
   - Create a model router for fallback and cost optimization

8. **Deployment & Package Distribution**:
   - Implement Docker containerization
   - Create Kubernetes deployment configurations
   - Develop cloud deployment guides (AWS, GCP, Azure)
   - Add monitoring and logging integration
   - Set up continuous integration with GitHub Actions
   - Create automatic version bumping for releases
   - Develop SQLite deployment guides for serverless environments

9. **Logging and Tracing System**:
   - Implement comprehensive tracing system with unique trace IDs
   - Add component-level tracing (user, orchestrator, agent, MCP)
   - Support multiple output formats (stdout, file logs)
   - Enable integration with external services (Papertrail, Kafka)
   - Create CLI tools for trace viewing and analysis
   - Implement performance-optimized logging
   - Add cloud integration for MUXI Cloud deployments

10. **Multi-Modal Capabilities**:
    - Implement document processing with PDF and Office document support
    - Develop image analysis with vision-capable models
    - Create audio processing with speech-to-text and text-to-speech capabilities
    - Implement real-time streaming through WebSocket interfaces
    - Ensure proper handling of multi-modal interactions across all interface types
    - Build comprehensive examples demonstrating multi-modal agent capabilities

11. **TypeScript/JavaScript SDK**:
    - Create REST API client with full endpoint coverage
    - Implement WebSocket client for real-time communication
    - Develop MCP server protocol implementation for JavaScript tools
    - Build comprehensive examples and documentation
    - Package and publish to NPM

12. **Memory System Enhancements**:
    - Implement context memory templates for common use cases
    - Add improved context merging capabilities
    - Implement context memory namespaces
    - Optimize vector operations for improved performance
    - Complete automatic user information extraction implementation
    - Develop interface-level user ID generation
    - Add advanced vector database features for scalability

13. **Testing and Documentation**:
    - Implement unit tests for all new API endpoints
    - Create integration tests for API and WebSocket endpoints
    - Develop performance benchmarks for API endpoints
    - Complete CLI documentation
    - Expand API documentation beyond api.md with practical examples
    - Develop user guides for advanced use cases
    - Create example projects showcasing API usage

### Deprioritized Tasks

Based on performance evaluation showing PostgreSQL with pgvector performing well (471.57 QPS and low latency at 99% recall), the following tasks have been deprioritized:

1. **Additional Vector Database Integrations**:
   - ~~Milvus integration~~
   - ~~Qdrant integration~~
   - ~~Weaviate integration~~

## Active Decisions and Considerations

### Memory Architecture Decisions

1. **Hybrid Memory Retrieval**: The FAISS-backed SmartBufferMemory now uses a hybrid approach that combines:
   - Semantic search using FAISS vector similarity
   - Recency-based retrieval using buffer indices
   - Configurable weighting between semantic and recency with `recency_bias` parameter

2. **Graceful Degradation**: The memory system automatically falls back to recency-only search when:
   - No embedding model is available
   - Embedding generation fails
   - No valid search results are found with vector search

3. **Thread Safety**: The memory system is designed to be thread-safe for concurrent access:
   - Buffer operations protected with locks
   - FAISS index rebuilding handled safely
   - Concurrent reads supported without blocking

4. **Centralized Memory Access**: All memory operations are now handled at the orchestrator level:
   - Agents delegate memory operations to the orchestrator
   - Consistent memory access patterns across the framework
   - Simplified configuration and management

### API Design Decisions

1. **REST vs. GraphQL**: Decision made to use REST API as the primary interface due to its simplicity and widespread adoption. GraphQL may be considered for future versions based on user feedback.

2. **Authentication Approach**: Bearer token authentication using API keys was chosen for simplicity and security. Consider adding OAuth support in the future for more complex authentication scenarios.

3. **API Versioning**: Decision to implement API versioning from the start via URL path (e.g., /api/v1/) to ensure future compatibility as the API evolves.

4. **Error Handling**: Standardized error format as defined in api.md will be used consistently across all endpoints, with specific error codes and descriptive messages.

5. **Streaming Implementation**: Server-Sent Events (SSE) was chosen for streaming responses over WebSockets for this specific use case due to its simplicity and unidirectional nature, which is well-suited for streaming LLM outputs.

### Technical Considerations

1. **Database Structure**:
   - PostgreSQL with pgvector is confirmed as the primary database for high-scale deployments
   - SQLite with sqlite-vec now supported for local and lightweight deployments
   - Both use the same vector operations and interfaces

2. **Concurrency Model**: The async/await pattern with asyncio is used throughout the codebase. Be mindful of potential race conditions in shared state when implementing new features.

3. **MCP Integration Strategy**: The framework will continue to use the Model Context Protocol for tool integration, with support for both HTTP+SSE and Command-line transports.

4. **Package Structure**: The modular package structure (core, server, cli, web, meta) will be maintained for better separation of concerns.

5. **Documentation Approach**: API documentation will be generated using OpenAPI/Swagger, with additional developer documentation in Markdown format using Sphinx for generation.

### Open Questions

1. **Multi-Modal Support Scope**: What level of multi-modal support should be prioritized first? Images, audio, or documents?

2. **Scalability Strategy**: What specific strategies should be implemented for horizontal scaling of the framework?

3. **Local LLM Integration**: Which local LLM frameworks should be prioritized for integration?

4. **Security Assessment**: What security assessment procedures should be established before the 1.0 release?

5. **Deployment Strategy**: What containerization and orchestration approaches should be recommended for production deployments?

6. **Vector Database Choice**: Should we provide more guidance on choosing between SQLite and PostgreSQL for different use cases?

7. **SDK Prioritization**: Which language SDKs should be prioritized after TypeScript/JavaScript, and what features are most important for each target language?

## Blockers and Dependencies

1. **MCP Protocol Evolution**: The framework depends on the Model Context Protocol, which is still evolving. Need to stay aligned with protocol changes.

2. **API Specification Finalization**: The API specification in api.md needs to be finalized before full implementation can proceed.

3. **Multi-Modal LLM Support**: Multi-modal capabilities depend on the features available in the underlying LLM providers.

4. **Testing Infrastructure**: Need to ensure comprehensive testing infrastructure is in place for the new API endpoints.

5. **Documentation Tools**: Need to set up OpenAPI/Swagger tools for API documentation generation.

## Refactoring Approach

1. **Orchestrator-Centered Design**:
   - Extraction logic is now centralized in the Orchestrator
   - Added `handle_user_information_extraction` method to coordinate extraction
   - Implemented `_run_extraction` for the actual extraction processing
   - Maintained backward compatibility with existing `extract_user_information` method

2. **Agent Design Changes**:
   - Agent now delegates extraction to Orchestrator
   - Removed message counting and extraction handling from Agent
   - Simplified Agent implementation while preserving functionality
   - Maintains `auto_extract_user_info` and `extraction_model` parameters for backward compatibility

3. **Memory Architecture**:
   - SmartBufferMemory implements hybrid retrieval with FAISS
   - Vector similarity search balanced with recency bias
   - Configurable parameters for different use cases
   - Optimized for both accuracy and performance

4. **MCP Service Architecture**:
   - Singleton pattern with thread-safe operations
   - Centralized error handling and timeout configuration
   - Consistent tool invocation patterns
   - Support for multiple transport types

5. **Asynchronous Processing**:
   - Extraction runs in background tasks to avoid blocking conversation flow
   - Proper error handling to prevent extraction failures from affecting core functionality
   - Async locks for thread safety in critical operations

6. **Privacy Enhancements**:
   - Anonymous users (user_id=0) are explicitly excluded from extraction
   - Consistent handling of anonymous users across all memory operations
   - Added testing to verify privacy controls

## Recent Decisions

- **Smart Buffer Memory Implementation**: Using FAISS for vector similarity search with hybrid retrieval approach
- **MCP Service Architecture**: Implementing as a singleton with thread-safe operations
- **Package Structure Standardization**: Moving from src/muxi to direct muxi directories
- **Centralization of Memory Logic**: Memory operations are now primarily handled by the Orchestrator
- **User ID Treatment**: Anonymous users (user_id=0) are consistently handled with early returns
- **Error Isolation**: Extraction errors are caught and logged but don't disrupt core functionality
- **Testing Approach**: Created comprehensive tests for both memory systems and MCP functionality

## Current Implementation State

1. **Smart Buffer Memory**:
   - Implemented in `packages/core/muxi/core/memory/buffer.py`
   - Uses FAISS for vector similarity search
   - Implements hybrid retrieval combining semantic relevance and recency
   - Provides graceful degradation to recency-only when needed
   - Thread-safe operations for concurrent access
   - Full integration with orchestrator memory management

2. **MCPService**:
   - Implemented in `packages/core/muxi/core/mcp/service.py`
   - Singleton pattern with thread-safe operations
   - Centralized tool invocation with consistent error handling
   - Configurable timeouts at multiple levels
   - Support for multiple transport types

3. **Automatic Information Extraction**:
   - MemoryExtractor class in packages/core/muxi/core/memory/extractor.py handles actual extraction
   - Orchestrator in packages/core/muxi/core/orchestrator.py manages the extraction process
   - Agent in packages/core/muxi/core/agent.py delegates extraction to Orchestrator
   - Tests in tests/test_extractor.py verify functionality

## Documentation Updates

Documentation in .cursor/rules/ has been updated:
- smart_buffer_memory.mdc: Documents the FAISS-backed smart buffer memory implementation
- mcp_service.mdc: Explains the centralized MCPService singleton architecture
- memory_extraction.mdc: Explains the centralized extraction architecture
- memory_user_id.mdc: Documents anonymous user handling across memory operations
- 00_project_structure.mdc: Updated with current package structure

Project documentation has been updated:
- project-structure.md: Reflects current directory organization
- active-context.md: Updated with current work focus and recent changes
- package.md: Updated with current package structure and descriptions
- contributing.md: Updated with current project structure information

## Next Steps

1. **Memory System Optimization**:
   - Fine-tune recency bias parameters for different use cases
   - Add performance benchmarks for memory operations
   - Implement caching for frequently accessed memory items

2. **MCP Service Enhancements**:
   - Add more comprehensive timeout handling
   - Implement automatic retry logic for transient failures
   - Add telemetry for monitoring tool usage

3. **User Information Extraction**:
   - Evaluate extraction performance with high message volume
   - Add more sophisticated filtering for extracted information
   - Implement user-facing controls for extraction preferences

4. **REST API Implementation**:
   - Begin implementing key API endpoints according to specification
   - Add authentication mechanisms for API endpoints
   - Implement streaming for chat responses

# Active Context: MUXI Framework Development

## Current Focus

The current focus is on developing the next phase of the MUXI Framework infrastructure, implementing two key components:

1. **MUXI API** - A unified server combining REST API, SSE (Server-Sent Events), MCP (Model Context Protocol), and WebRTC capabilities
2. **MUXI CLI** - A command-line interface for interacting with the MUXI API

These components will interact with the existing **MUXI Core** (previously referred to as MUXI Service) which handles the orchestration of agents, memory management, and other core functionalities.

## Recent Decisions

1. **Terminology Standardization**:
   - **MUXI Core**: The fundamental backend services that handle orchestration, agents, memory, etc. (previously referred to as "MUXI Service")
   - **MUXI API**: The interface layer providing REST API, SSE, MCP, and WebRTC endpoints
   - **MUXI CLI**: The command-line client providing terminal-based access to MUXI functionality

2. **API Implementation**:
   - No backward compatibility requirements for the new API implementation
   - Dual API key authentication (user keys and admin keys) managed at the MUXI Core level
   - Explicit access level specification using decorators or dependency injection
   - All endpoints must have explicit operation_id parameters for MCP tools

3. **CLI Client**:
   - INI-style configuration format similar to AWS CLI with profile support
   - Clear permission indicators for commands requiring admin privileges
   - Implementation in phases with clear priorities for features
   - Support for multiple output formats and streaming

## Architecture Evolution

The MUXI Framework architecture is evolving to support a more modular and distributed deployment model:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    MUXI CLI     │────▶│    MUXI API     │────▶│    MUXI Core    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Deployment Options                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Single Machine  │ Same Network    │ Distributed (Cross-Network) │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

Each component can be deployed on the same machine, within the same network, or in a fully distributed setup across different networks, providing flexibility for various deployment scenarios.

## Considerations and Next Steps

1. **Package Alignment**:
   - The new terminology aligns with the existing package structure:
     - `core`: MUXI Core implementation
     - `server`: MUXI API implementation
     - `cli`: MUXI CLI implementation
     - `meta`: Meta-package that installs everything

2. **Authentication Flow**:
   - Implementing the dual API key system (user and admin keys) at the MUXI Core level
   - MUXI API will validate keys against MUXI Core for permission checking
   - MUXI CLI will store and manage keys in profile configurations

3. **Deployment Configuration**:
   - MUXI API needs to be configured with the URI of MUXI Core (defaults to localhost:3000)
   - Documentation for deploying each component independently with appropriate configuration
