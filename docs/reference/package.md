---
layout: default
title: Package Structure
parent: Reference
nav_order: 3
permalink: /reference/package
---

# Package Structure

This page provides a detailed overview of the MUXI Framework's package organization and internal structure.

## Overview

MUXI is organized as a modular monorepo with multiple packages that can be used independently or together. This approach provides several advantages:

- **Separation of Concerns**: Each package has a clear, focused responsibility
- **Independent Versioning**: Packages can evolve at different rates
- **Reduced Dependencies**: Users can install only what they need
- **Clearer Boundaries**: Interfaces between components are well-defined
- **Focused Testing**: Each package can be tested in isolation

## Package Organization

The MUXI framework is structured as follows:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, MCP interface
│   │   ├── muxi/core/
│   │   │   ├── agent.py        # Agent implementation
│   │   │   ├── orchestrator.py # Orchestrator with centralized memory and API keys
│   │   │   ├── memory/         # Memory subsystems
│   │   │   │   ├── buffer.py   # FAISS-backed smart buffer memory
│   │   │   │   ├── long_term.py # Long-term memory with vector storage
│   │   │   │   ├── memobase.py # Multi-user memory partitioning
│   │   │   │   ├── sqlite.py   # SQLite vector integration
│   │   │   │   └── extractor.py # User information extraction
│   │   │   ├── mcp/            # Model Context Protocol
│   │   │   │   ├── service.py  # Centralized MCPService singleton
│   │   │   │   ├── handler.py  # MCP Handler implementation
│   │   │   │   └── message.py  # MCP Message structure
│   │   │   ├── models/         # LLM provider interfaces
│   │   │   ├── config/         # Configuration components
│   │   │   └── knowledge/      # Knowledge integration
│   │   ├── setup.py            # Package configuration
│   │   └── README.md           # Package documentation
│   │
│   ├── server/        # REST API and WebSocket server
│   │   ├── muxi/server/
│   │   │   ├── api/          # REST API endpoints
│   │   │   ├── ws/           # WebSocket implementation
│   │   │   └── config/       # Server configuration
│   │   ├── setup.py          # Package configuration
│   │   └── README.md         # Package documentation
│   │
│   ├── cli/           # Command-line interface
│   │   ├── muxi/cli/
│   │   │   ├── commands/     # CLI commands
│   │   │   ├── terminal/     # Terminal UI
│   │   │   └── mcp_generator/ # MCP server template generator
│   │   ├── setup.py          # Package configuration
│   │   └── README.md         # Package documentation
│   │
│   ├── meta/          # Meta-package for installation
│   │   ├── muxi/           # Meta-package source code
│   │   ├── setup.py        # Package configuration
│   │   └── README.md       # Package documentation
│   │
│   └── web/           # Web user interface
│       ├── src/             # Web app source code
│       └── package.json     # NPM package configuration
│
├── examples/          # Example scripts and applications
├── docs/              # Documentation
└── tests/             # Test suite for all components
```

## Package Descriptions

### Core Package (`muxi-core`)

The foundation of the MUXI framework, containing all essential components:

- **Agent**: Implements the agent architecture with delegation to Orchestrator for memory
- **Orchestrator**:
  - Central manager for multiple agents with shared memory systems
  - Handles API key management with user and admin keys
  - Implements intelligent message routing
- **Memory**:
  - Smart buffer memory with FAISS-backed vector search and recency bias
  - Long-term memory with PostgreSQL and SQLite vector database support
  - Memobase system for multi-user memory partitioning
  - Automatic user information extraction
- **MCP**:
  - Centralized MCPService as a singleton for thread-safe operations
  - Multiple transport types (HTTP+SSE, Command-line)
  - Configurable timeouts at orchestrator, agent, and per-request levels
- **Models**: Interfaces to LLM providers like OpenAI, Anthropic, and others
- **Knowledge**: Domain knowledge integration for agent specialization

Key features:
- Centralized memory architecture at orchestrator level
- Thread-safe MCP server interactions
- Configurable API key system
- Dual database support (PostgreSQL/SQLite)

### Server Package (`muxi-server`)

Implements the server components for exposing MUXI functionality via APIs:

- **API**: REST API endpoints with dual-key authentication (user and admin keys)
- **WebSocket**: Real-time, bidirectional communication
- **SSE**: Server-Sent Events for streaming responses
- **MCP Server**: MCP server implementation for tool hosting

Key features:
- FastAPI-based implementation
- WebSocket support for streaming responses
- Server-Sent Events (SSE) for one-way streaming
- Authentication with API keys

### CLI Package (`muxi-cli`)

Command-line interface for interacting with MUXI:

- **Commands**: Implementation of CLI commands like `chat`, `run`, `mcp`
- **Terminal**: Rich terminal UI for interactive sessions
- **MCP Generator**: Utilities for creating new MCP server templates

Key features:
- Rich terminal UI with syntax highlighting
- Interactive chat mode with history
- Command completion and help documentation
- MCP server scaffolding

### Meta Package (`muxi`)

The main package that integrates all components:

- Provides a unified API for the entire framework
- Handles package coordination and initialization
- Simplifies installation and usage

This is the recommended package for most users who want the full MUXI experience.

### Web Package (`muxi-web`)

Web-based interface for MUXI:

- **Frontend**: React-based UI with streaming support
- **Components**: Reusable UI components
- **Services**: API client services

Key features:
- Modern React-based interface
- Real-time communication via WebSockets
- Agent configuration UI
- Chat history visualization

## Import Structure

MUXI uses a consistent import structure across all packages:

```python
# Core imports
from muxi.core.agent import Agent
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.mcp.service import MCPService
from muxi.core.models.providers.openai import OpenAIModel

# Server imports
from muxi.server.api import create_app
from muxi.server.ws import WebSocketManager

# CLI imports
from muxi.cli.commands import chat_command

# Meta-package imports (includes all of the above)
from muxi import muxi  # Main entry point
```

## Dependency Graph

The packages have the following dependency relationships:

```
muxi (meta-package)
 ├── muxi-core     # No external package dependencies
 ├── muxi-server   # Depends on muxi-core
 ├── muxi-cli      # Depends on muxi-core
 └── muxi-web      # Depends on muxi-core and muxi-server
```

This structure ensures that:
1. `muxi-core` can be used independently without installing server, CLI, or web components
2. Each higher-level package only depends on what it needs

## Installation Options

Users can install packages based on their needs:

```bash
# Full installation (recommended)
pip install muxi

# Core functionality only
pip install muxi-core

# Server functionality
pip install muxi-server

# CLI functionality
pip install muxi-cli

# Web UI
pip install muxi-web

# Development installation
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework
./install_dev.sh
```

## Development Guidelines

When contributing to MUXI, consider these package-related guidelines:

1. **Respect Package Boundaries**: Don't create circular dependencies between packages
2. **Minimize Dependencies**: Each package should only depend on what it absolutely needs
3. **Consistent Interfaces**: Public APIs should be consistent across packages
4. **Proper Re-exporting**: The meta-package should re-export all important interfaces
5. **Version Compatibility**: Be mindful of version compatibility between packages
6. **Memory Architecture**: Remember that memory is now centralized at the orchestrator level
7. **MCP Access**: Always use the MCPService singleton for MCP server interactions

## Testing Structure

Tests are organized to match the package structure:

```
tests/
├── test_agent.py           # Tests for agent functionality
├── test_orchestrator.py    # Tests for orchestrator functionality
├── test_mcp.py             # Tests for MCP functionality
├── test_memory.py          # Tests for memory systems
└── [various test files]    # Other tests
```

Each component has its own test suite that can be run independently:

```bash
# Run agent tests
pytest tests/test_agent.py

# Run all tests
pytest
```

## Related Resources

- [API Documentation](/reference/api) - Detailed API reference
- [Configuration Options](/reference/configuration) - Configuration parameters
- [Codebase Organization](/development/codebase) - Further details on code organization
