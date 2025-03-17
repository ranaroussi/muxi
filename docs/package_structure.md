# MUXI Package Structure

This document outlines the modular package structure of the MUXI framework and explains how the different components interact.

## Overview

MUXI follows a modular monorepo structure with these main packages:

```
muxi-framework/
├── packages/
│   ├── core/      # Core functionality: agents, memory, tools, LLM interface
│   ├── server/    # Server implementation with API endpoints and WebSocket
│   ├── cli/       # Command-line interface
│   ├── web/       # Web application
│   └── muxi/      # Meta-package that integrates all components
├── examples/      # Cross-package examples
├── docs/          # Unified documentation
├── scripts/       # Build and release scripts
└── tests/         # Integration tests across packages
```

## Installation Options

There are several installation options for MUXI:

### 1. muxi (Complete Framework)

The full framework including all components needed to run MUXI locally.

**Key components:**
- Core functionality and shared components
- Complete server implementation with API and WebSocket
- Agent management and orchestration
- Memory systems and LLM integrations
- Command-line interface

**Installed by:**
```bash
pip install muxi
```

### 2. Development Installation

For development, install all packages in editable mode:

```bash
./install_dev.sh
```

This script installs all packages in development mode, allowing you to modify the code without reinstalling.

## Package Structure Details

Each package has a standard structure:

```
packages/core/
├── pyproject.toml     # Package configuration
└── src/
    └── muxi/
        └── core/      # Core package code
            ├── __init__.py
            ├── agent.py
            ├── memory.py
            ├── mcp.py
            └── tools/
                ├── __init__.py
                ├── base.py
                └── ...
```

The dependencies follow this pattern:

```
core <-- server
 ^       ^
 |       |
 |       |
 +--- cli
 |
 |
 +--- web
```

The meta-package `muxi` installs core, server, and cli packages together.

## Import Structure

When developing within the MUXI framework, use the following import patterns:

### Core Components
```python
from muxi.core.agent import Agent
from muxi.core.memory import MemorySystem
from muxi.core.mcp import MCPMessage
from muxi.core.tools import Calculator, WebSearch
```

### Server Components
```python
from muxi.server.config import config
from muxi.server.api.app import start_api
from muxi.server.ws import WebSocketManager
```

### CLI Components
```python
from muxi.cli.commands import chat, run, send
```

### Web Components
```python
from muxi.web.app import create_app
```

## Adding New Packages

To add a new package to the MUXI framework:

1. Create a new directory under `packages/`
2. Create the standard Python package structure:
   ```
   packages/new-package/
   ├── pyproject.toml
   ├── README.md
   ├── src/
   │   └── muxi/
   │       └── new_module/
   │           └── __init__.py
   ```
3. Define appropriate dependencies in `pyproject.toml`
4. Update the installation scripts

## Building and Publishing

Each package can be built and published to PyPI:

```bash
# Build a specific package
cd packages/core
python -m build

# Build all packages
# Use a script that iterates through all packages
```

## Package Contents

### Core Package
The core package contains the foundational components:
- `Agent`: Base class for AI agents
- `MemorySystem`: Short-term and long-term memory implementations
- `MCPHandler`: Model Context Protocol implementation
- `Tool`: Base class for tool implementations

### Server Package
The server package provides:
- REST API implementation
- WebSocket server for real-time communication
- Configuration management
- Database connections

### CLI Package
The CLI package includes:
- Interactive terminal-based chat interface
- Command-line tools for managing agents
- Server management commands

### Web Package
The web package contains:
- React-based user interface
- WebSocket client implementation
- Configuration UI for agents and tools

### Meta Package
The `muxi` meta-package:
- Provides a unified API
- Handles dependencies across packages
- Simplifies installation
