---
layout: default
title: Package Structure
parent: Reference
nav_order: 3
permalink: /reference/package/
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
│   │   └── src/muxi/core/
│   │       ├── agent/        # Agent implementation
│   │       ├── memory/       # Memory subsystems
│   │       ├── models/       # LLM provider interfaces
│   │       ├── mcp/          # Model Context Protocol
│   │       ├── orchestrator/ # Multi-agent coordination
│   │       └── tools/        # Built-in tools
│   │
│   ├── server/        # REST API and WebSocket server
│   │   └── src/muxi/server/
│   │       ├── api/          # REST API endpoints
│   │       ├── websocket/    # WebSocket implementation
│   │       ├── auth/         # Authentication
│   │       └── middleware/   # Server middleware
│   │
│   ├── cli/           # Command-line interface
│   │   └── src/muxi/cli/
│   │       ├── commands/     # CLI commands
│   │       ├── terminal/     # Terminal UI
│   │       └── mcp_generator/ # MCP server template generator
│   │
│   ├── web/           # Web user interface
│   │   ├── src/muxi/web/
│   │   │   ├── api/          # Web-specific API
│   │   │   └── server/       # Web server
│   │   └── frontend/         # React-based frontend
│   │
│   └── muxi/          # Meta-package that integrates all components
│       └── src/muxi/
│           ├── __init__.py   # Main entry point
│           └── client.py     # Client implementation
│
├── examples/          # Example scripts and applications
├── docs/              # Documentation
└── tests/             # Test suite for all components
```

## Package Descriptions

### Core Package (`muxi-core`)

The foundation of the MUXI framework, containing all essential components:

- **Agent**: Implements the agent architecture and LLM integration
- **Memory**: Buffer memory, long-term memory, and Memobase implementations
- **Models**: Interfaces to LLM providers like OpenAI, Anthropic, and Ollama
- **MCP**: The Model Context Protocol client implementation
- **Orchestrator**: Multi-agent coordination system
- **Tools**: Built-in tool implementations for common tasks

Key features:
- Minimal dependencies for lightweight usage
- Can be used without the server, CLI, or web UI
- Provides programmatic API for integration into other applications

### Server Package (`muxi-server`)

Implements the server components for exposing MUXI functionality via APIs:

- **API**: REST API endpoints for agent management, chat, memory, etc.
- **WebSocket**: Real-time, bidirectional communication
- **Authentication**: JWT-based auth system
- **Middleware**: Request validation, error handling, rate limiting

Key features:
- FastAPI-based implementation
- WebSocket support for streaming responses
- Server-Sent Events (SSE) for one-way streaming
- Comprehensive API for all MUXI functionality

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

### Web Package (`muxi-web`)

Web-based interface for MUXI:

- **API**: Web-specific API endpoints
- **Server**: Web server implementation
- **Frontend**: React-based UI with streaming support

Key features:
- Modern React-based interface
- Real-time communication via WebSockets
- Agent configuration UI
- Chat history visualization

### Meta Package (`muxi`)

The main package that integrates all components:

- Provides a unified API for the entire framework
- Handles package coordination and initialization
- Simplifies installation and usage

This is the recommended package for most users who want the full MUXI experience.

## Import Structure

MUXI uses a consistent import structure across all packages:

```python
# Core imports
from muxi.core.agent import Agent
from muxi.core.memory import BufferMemory, LongTermMemory
from muxi.core.models.openai import OpenAIModel
from muxi.core.mcp import MCPHandler
from muxi.core.orchestrator import Orchestrator
from muxi.core.tools.weather import WeatherTool

# Server imports
from muxi.server.api import create_app
from muxi.server.websocket import WebSocketManager

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

## Testing Structure

Tests are organized to match the package structure:

```
tests/
├── core/          # Tests for the core package
├── server/        # Tests for the server package
├── cli/           # Tests for the CLI package
├── web/           # Tests for the web package
└── integration/   # Cross-package integration tests
```

Each package has its own test suite that can be run independently:

```bash
# Run core tests
pytest tests/core

# Run all tests
pytest
```

## Related Resources

- [API Documentation](/reference/api) - Detailed API reference
- [Configuration Options](/reference/configuration) - Configuration parameters
- [Codebase Organization](/development/codebase) - Further details on code organization
