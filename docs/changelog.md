---
title: Changelog
nav_order: 11
---

# Changelog

All notable changes to the MUXI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2023-09-10

### Added
- **Memory Architecture Migration**: Migrated memory management from agent level to orchestrator level [Breaking Change]
  - Orchestrator-level memory management for centralized control
  - Memory sharing between agents for improved collaboration
  - Simplified configuration via constructor parameters
  - Updated documentation and examples
- **Knowledge Base**: Enhanced agent-level knowledge storage and retrieval capabilities
  - Vector database support for semantic search
  - Efficient document indexing and retrieval
  - Support for multiple knowledge sources
- **Long-term Memory**: Added persistent memory solutions
  - PostgreSQL with pgvector integration
  - SQLite with sqlite-vec support
  - Configurable retention policies
- **Multi-user Memory Support**: Separated memory contexts for multiple users
  - User-specific knowledge and conversation history
  - Enhanced privacy and context management
- **User Context Memory**: Added support for storing user-specific information
  - Profile data and preferences
  - Session state management
- **MCP Server Capabilities**:
  - SSE-based server endpoint for MCP host integration
  - Tool discovery from agent capabilities
  - Authentication shared with REST API

### Changed
- **Configuration Format**: Updated YAML/JSON configuration to support orchestrator-level memory
- **API Signatures**: Modified initialization procedures to use constructor parameters instead of setup methods
- **Examples**: Revamped all code examples to demonstrate the new memory architecture
- **Documentation**: Comprehensive update of all memory-related documentation

### Fixed
- Memory isolation issues in multi-agent environments
- Inefficient memory access patterns
- Inconsistent user context handling

### Removed
- Agent-level memory configuration
- `Agent.setup_memory()` method (replaced with constructor parameters in Orchestrator)
- Deprecated memory access patterns

## [0.2.0] - 2023-08-15

### Added
- Modular package structure for better organization
- Enhanced CLI with interactive mode
- Improved error handling and logging

### Changed
- Restructured import paths for better clarity
- Refactored core components for better maintainability

### Fixed
- Various stability issues
- Performance bottlenecks in message routing

## [0.1.0] - 2023-07-01

### Added
- Initial release of MUXI Framework
- Core agent system
- Basic memory systems (short-term buffer)
- OpenAI integration
- Command line interface
- MCP Client integration (HTTP+SSE)
- MCP Client integration (Command)
