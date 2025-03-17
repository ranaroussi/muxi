# MUXI Package Structure

This document outlines the modular package structure of the MUXI framework and explains how the different components interact.

## Overview

MUXI follows a modular monorepo structure internally, with three main installation options for users:

```
muxi/
├── packages/
│   ├── core/      # Core functionality and shared components
│   ├── server/    # Server implementation
│   ├── cli/       # Command-line interface
│   └── web/       # Web application
├── examples/      # Cross-package examples
├── docs/          # Unified documentation
├── scripts/       # Build and release scripts
└── tests/         # Integration tests across packages
```

## Installation Options

There are three main installation options for MUXI:

### 1. muxi (Base Framework)

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

### 2. muxi-cli (CLI Client Only)

A lightweight client for connecting to remote MUXI servers via command line.

**Key components:**
- Command-line interface
- Remote server connections
- Minimal dependencies
- Interactive mode

**Installed by:**
```bash
pip install muxi-cli
```

### 3. muxi-web (Web Client Only)

The standalone web client for connecting to MUXI servers.

**Key components:**
- Web application frontend
- Connection management UI
- Chat interface
- Agent configuration

**Installed by:**
```bash
pip install muxi-web
```

## Development Setup

For development, install all packages in editable mode:

```bash
./install_dev.sh
```

This script installs all packages in development mode, allowing you to modify the code without reinstalling.

## Internal Package Structure

Internally, the MUXI framework consists of these packages:

- **core**: Foundation package with abstractions, models, and client code
- **server**: Server implementation with API, memory, and agent orchestration
- **cli**: Command-line interface for interacting with MUXI
- **web**: Web application for interacting with MUXI

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
from muxi.models.base import BaseModel
from muxi.utils.id_generator import generate_id
```

### Server Components
```python
from muxi.server.config import config
from muxi.server.memory import LongTermMemory
from muxi.server.api.app import start_api
from muxi.server.tools.calculator import Calculator
```

### CLI Components
```python
from muxi.cli.commands import run_chat
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
   ├── setup.py
   ├── README.md
   ├── src/
   │   └── muxi/
   │       └── new_module/
   │           └── __init__.py
   ```
3. Define appropriate dependencies in `setup.py`
4. Update the installation scripts

## Building and Publishing

Each package can be built and published to PyPI:

```bash
# Build all packages
./scripts/build_all.sh
```
