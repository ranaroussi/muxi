# MUXI Framework Active Context

## Current Work Focus

The current development focus is on implementing the complete REST API as defined in the `.context/scratchpad/api.md` specification file. This involves standardizing all API endpoints, implementing authentication, error handling, and ensuring proper documentation. This work is considered high priority as it forms the foundation for client applications to interact with the MUXI Framework.

Additionally, we're refining the automatic user information extraction system in MUXI by centralizing the extraction logic at the Orchestrator level rather than handling it in the Agent.

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

1. **Centralized MCP Service Implementation**:
   - Implemented a centralized MCPService as a singleton for managing all MCP server connections
   - Created a dedicated ToolParser to handle various tool call formats in LLM responses
   - Updated Agent class to use the centralized service for MCP server interactions
   - Removed direct MCP handler dependency from Agent in favor of the shared service
   - Added server_id to MCPServer for consistent identification
   - Implemented thread-safe tool invocation with locks for concurrent access
   - Improved error handling with consistent patterns throughout MCP interactions
   - Added the ability to customize request timeout at various levels: Orchestrator, Agent, and per-request

2. **Package Organization and Import Cleanup**:
   - Moved functionality from `__main__.py` files to dedicated modules
   - Improved import patterns with clean exports from package `__init__.py` files
   - Renamed `run_api_server()` to `run_server()` to reflect multi-purpose nature
   - Added MCP parameter to server startup via `run_server(mcp=True)`
   - Created dedicated `start_mcp()` function for standalone MCP server usage
   - Ensured no direct imports from `__main__.py` files (only through package exports)

3. **Memory Architecture Migration**:
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

4. **SQLite Vector Integration**:
   - Added support for sqlite-vec Python package for vector similarity search
   - Simplified extensions handling by using Python package instead of binary extensions
   - Reorganized extension directory structure to improve clarity and maintainability
   - Updated memory system to work with both PostgreSQL and SQLite databases
   - Improved vector serialization for compatibility with sqlite-vec
   - Enhanced resilience with fallback mechanisms when package is unavailable

5. **Breaking Changes in Version 1.0**:
   - Removed deprecated methods like `_enhance_with_domain_knowledge()` (replaced by `_enhance_with_context_memory()`)
   - Removed `add_user_domain_knowledge()` (replaced by `add_user_context_memory()`)
   - Updated API signatures by removing the `memory` parameter from the `Agent` class (replaced by `buffer_memory`)
   - Removed backward compatibility for user_id=0 handling
   - Renamed all "domain knowledge" terminology to "context memory" throughout the codebase

6. **Test Improvements**:
   - Fixed all test warnings and errors
   - Implemented pytest.ini configuration to filter FAISS-related DeprecationWarnings
   - Improved test coverage across all components
   - Made tests more robust to handle differences in database behaviors

7. **Architectural Evolution**:
   - Restructured codebase into modular packages
   - Created setup.py for each package with appropriate dependencies
   - Implemented proper monorepo structure
   - Created development installation scripts
   - Fixed cross-package imports

8. **MCP Integration**:
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
   - ✅ Implement centralized MCP service for Agent-to-MCP server communications
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
   - Support attachments for files and media

3. **CLI Interfaces**:
   - Enhance CLI interface with support for all API operations
   - Improve user experience with better formatting and colors
   - Add multi-modal interaction support
   - Implement configuration management commands

4. **Web UI**:
   - Create responsive UI for mobile and desktop
   - Implement real-time updates using WebSocket
   - Add support for multi-modal interactions
   - Build user-friendly configuration interface
   - Create agent management dashboard

5. **Agent-to-Agent Communication (A2A)**:
   - Implement the A2A protocol for inter-agent communication
   - Create capability discovery mechanism
   - Develop task delegation between agents
   - Implement context sharing with proper isolation
   - Add conversation lifecycle management
   - Support external agent integration
   - Implement security and authentication

6. **LLM Providers**:
   - Implement Anthropic LLM provider
   - Implement Gemini LLM provider
   - Implement Grok LLM provider
   - Add support for local models (e.g., Llama, Mistral, DeepSeek)
   - Create a model router for fallback and cost optimization

7. **Deployment & Package Distribution**:
   - Implement Docker containerization
   - Create Kubernetes deployment configurations
   - Develop cloud deployment guides (AWS, GCP, Azure)
   - Add monitoring and logging integration
   - Set up continuous integration with GitHub Actions
   - Create automatic version bumping for releases
   - Develop SQLite deployment guides for serverless environments

8. **Logging and Tracing System**:
   - Implement comprehensive tracing system with unique trace IDs
   - Add component-level tracing (user, orchestrator, agent, MCP)
   - Support multiple output formats (stdout, file logs)
   - Enable integration with external services (Papertrail, Kafka)
   - Create CLI tools for trace viewing and analysis
   - Implement performance-optimized logging
   - Add cloud integration for MUXI Cloud deployments

9. **Multi-Modal Capabilities**:
   - Implement document processing with PDF and Office document support
   - Develop image analysis with vision-capable models
   - Create audio processing with speech-to-text and text-to-speech capabilities
   - Implement real-time streaming through WebSocket interfaces
   - Ensure proper handling of multi-modal interactions across all interface types
   - Build comprehensive examples demonstrating multi-modal agent capabilities

10. **TypeScript/JavaScript SDK**:
    - Create REST API client with full endpoint coverage
    - Implement WebSocket client for real-time communication
    - Develop MCP server protocol implementation for JavaScript tools
    - Build comprehensive examples and documentation
    - Package and publish to NPM

11. **Memory System Enhancements**:
    - Implement context memory templates for common use cases
    - Add improved context merging capabilities
    - Implement context memory namespaces
    - Optimize vector operations for improved performance
    - Complete automatic user information extraction implementation
    - Develop interface-level user ID generation
    - Add advanced vector database features for scalability

12. **Testing and Documentation**:
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

3. **Asynchronous Processing**:
   - Extraction runs in background tasks to avoid blocking conversation flow
   - Proper error handling to prevent extraction failures from affecting core functionality

4. **Privacy Enhancements**:
   - Anonymous users (user_id=0) are explicitly excluded from extraction
   - Consistent handling of anonymous users across all memory operations
   - Added testing to verify privacy controls

## Recent Decisions

- **Centralization of Memory Logic**: Memory operations are now primarily handled by the Orchestrator
- **User ID Treatment**: Anonymous users (user_id=0) are consistently handled with early returns
- **Error Isolation**: Extraction errors are caught and logged but don't disrupt core functionality
- **Testing Approach**: Created comprehensive tests for both MemoryExtractor and Orchestrator functionality

## Current Implementation State

The automatic user information extraction system is now functional and centralized:

1. MemoryExtractor class in packages/server/src/muxi/memory/extractor.py handles actual extraction
2. Orchestrator in packages/core/src/muxi/core/orchestrator.py manages the extraction process
3. Agent in packages/core/src/muxi/core/agent.py delegates extraction to Orchestrator
4. Tests in tests/test_extractor.py verify functionality

## Documentation Updates

Documentation in .cursor/rules/ has been updated:
- memory_extraction.mdc: Explains the centralized extraction architecture
- memory_user_id.mdc: Documents anonymous user handling across memory operations

## Next Steps

1. **Performance Testing**: Evaluate extraction performance with high message volume
2. **Enhanced Filtering**: Add more sophisticated filtering for extracted information
3. **User Control**: Implement user-facing controls for extraction preferences
4. **Integration**: Connect extraction with other components of the MUXI framework

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
     - `muxi`: Meta-package that installs everything

2. **Authentication Flow**:
   - Implementing the dual API key system (user and admin keys) at the MUXI Core level
   - MUXI API will validate keys against MUXI Core for permission checking
   - MUXI CLI will store and manage keys in profile configurations

3. **Deployment Configuration**:
   - MUXI API needs to be configured with the URI of MUXI Core (defaults to localhost:3000)
   - Documentation for deploying each component independently with appropriate configuration
