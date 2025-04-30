# MUXI Framework Active Context

## Current Work Focus

The current development focus is on implementing the complete REST API as defined in the `.context/scratchpad/api.md` specification file. This involves standardizing all API endpoints, implementing authentication, error handling, and ensuring proper documentation. This work is considered high priority as it forms the foundation for client applications to interact with the MUXI Framework.

Additionally, we're preparing to implement automatic user information extraction from conversations, a significant enhancement to the context memory system. This feature will allow agents to identify and store important user information without requiring explicit code.

### Primary Areas of Focus

1. **API Implementation**: Implementing the full set of REST endpoints defined in the API specification
2. **Authentication System**: Implementing a robust API key authentication system
3. **Error Handling**: Standardizing error responses across all endpoints
4. **Streaming Support**: Enhancing SSE streaming for chat responses
5. **Documentation**: Creating comprehensive API documentation with Swagger/OpenAPI
6. **SQLite Vector Integration**: Enhancing local deployment capabilities with sqlite-vec extension
7. **Agent-to-Agent Protocol**: Implementing the A2A protocol for inter-agent communication
8. **MCP Server Interface**: Creating an SSE-based MCP server endpoint for MCP host integration
9. **Automatic Information Extraction**: Implementing a system to automatically identify and store important user information from conversations

## Recent Changes

### Major Changes

1. **Package Organization and Import Cleanup**:
   - Moved functionality from `__main__.py` files to dedicated modules
   - Improved import patterns with clean exports from package `__init__.py` files
   - Renamed `run_api_server()` to `run_server()` to reflect multi-purpose nature
   - Added MCP parameter to server startup via `run_server(mcp=True)`
   - Created dedicated `start_mcp()` function for standalone MCP server usage
   - Ensured no direct imports from `__main__.py` files (only through package exports)

2. **Memory Architecture Migration**:
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

3. **SQLite Vector Integration**:
   - Added support for sqlite-vec Python package for vector similarity search
   - Simplified extensions handling by using Python package instead of binary extensions
   - Reorganized extension directory structure to improve clarity and maintainability
   - Updated memory system to work with both PostgreSQL and SQLite databases
   - Improved vector serialization for compatibility with sqlite-vec
   - Enhanced resilience with fallback mechanisms when package is unavailable

4. **Breaking Changes in Version 1.0**:
   - Removed deprecated methods like `_enhance_with_domain_knowledge()` (replaced by `_enhance_with_context_memory()`)
   - Removed `add_user_domain_knowledge()` (replaced by `add_user_context_memory()`)
   - Updated API signatures by removing the `memory` parameter from the `Agent` class (replaced by `buffer_memory`)
   - Removed backward compatibility for user_id=0 handling
   - Renamed all "domain knowledge" terminology to "context memory" throughout the codebase

5. **Test Improvements**:
   - Fixed all test warnings and errors
   - Implemented pytest.ini configuration to filter FAISS-related DeprecationWarnings
   - Improved test coverage across all components
   - Made tests more robust to handle differences in database behaviors

6. **Architectural Evolution**:
   - Restructured codebase into modular packages
   - Created setup.py for each package with appropriate dependencies
   - Implemented proper monorepo structure
   - Created development installation scripts
   - Fixed cross-package imports

7. **MCP Integration**:
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

## Next Steps

Based on the updated priority list, the following tasks have been prioritized:

### Updated Task Priorities

1. **REST API & MCP Server Implementation**:
   - Implement standard REST API endpoints according to api.md spec
   - Implement authentication with API keys
   - Add streaming support for chat endpoints with SSE
   - Implement proper error handling with standardized format
   - Add API versioning support
   - Implement rate limiting and throttling
   - Create API documentation using OpenAPI/Swagger

2. **WebSocket API Implementation**:
   - Implement WebSocket protocol for real-time communication
   - Add support for multi-modal messages (text, images, audio)
   - Implement proper error handling and recovery
   - Add reconnection logic with exponential backoff
   - Support for attachments as specified in api.md

3. **CLI Interfaces**:
   - Enhance CLI interface with support for all API operations
   - Develop web interface with responsive design
   - Implement real-time updates using WebSocket
   - Add support for multi-modal interactions

4. **Web UI**:
   - Create responsive UI for mobile and desktop
   - Implement real-time updates using WebSocket
   - Add support for multi-modal interactions
   - Build user-friendly configuration interface

5. **Agent-to-Agent Communication**:
   - Implement capability discovery mechanism
   - Create task delegation between agents
   - Develop context sharing with proper isolation
   - Implement conversation lifecycle management
   - Add external agent integration
   - Implement security and authentication

6. **A2A Security Layer** (New Priority):
   - Design and implement comprehensive permission system for controlling inter-agent communication
   - Develop context isolation to prevent unauthorized access to user data or sensitive information
   - Implement rate limiting to prevent abuse of inter-agent communication
   - Create audit logging system to record all inter-agent communications for security analysis
   - Develop security controls in line with the whitepaper specifications

7. **Multi-Modal Capabilities** (Raised Priority):
   - Implement document processing with PDF and Office document support
   - Develop image analysis with vision-capable models
   - Create audio processing with speech-to-text and text-to-speech capabilities
   - Implement real-time streaming through WebSocket interfaces
   - Ensure proper handling of multi-modal interactions across all interface types
   - Build comprehensive examples demonstrating multi-modal agent capabilities

8. **Vector Database Enhancements**:
   - Optimize vector operations for improved performance
   - Add support for additional vector databases (e.g., Milvus, Qdrant)
   - Add migration tools for transferring between database types
   - Create performance benchmarks for different vector database options
   - Develop guidance for choosing between SQLite and PostgreSQL
   - Support for vector database clustering and sharding

9. **LLM Providers**:
   - Implement Anthropic LLM provider
   - Implement Gemini LLM provider
   - Implement Grok LLM provider
   - Add support for local models (e.g., Llama, Mistral, DeepSeek)
   - Create a model router for fallback and cost optimization

10. **Testing and Documentation**:
    - Unit tests for all new API endpoints
    - Integration tests for API and WebSocket endpoints
    - Performance benchmarks for API endpoints
    - Complete CLI documentation
    - Expand API documentation beyond api.md with practical examples
    - User guides for advanced use cases
    - Example projects showcasing API usage

11. **Deployment & Package Distribution**:
    - Docker containerization
    - Kubernetes deployment
    - Cloud deployment guides (AWS, GCP, Azure)
    - Monitoring and logging integration
    - Continuous integration workflow with GitHub Actions or similar tools
    - Automatic version bumping for releases
    - SQLite deployment guides for serverless and edge environments

12. **Language-Specific SDKs**:
    - TypeScript/JavaScript SDK
    - Go SDK
    - Java/Kotlin SDK
    - Rust SDK
    - C#/.NET SDK
    - SDK Development Tools

## Active Decisions and Considerations

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

4. **Package Structure**: The modular package structure (core, server, cli, web, muxi) will be maintained for better separation of concerns.

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
