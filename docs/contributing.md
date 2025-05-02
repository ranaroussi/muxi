---
layout: default
title: Contributing to MUXI
parent: Resources
has_children: false
nav_order: 4
permalink: /contributing
---
# Contributing to the MUXI Framework

Thank you for your interest in contributing to the MUXI Framework! This guide will help you start contributing to the project, whether you're fixing bugs, adding new features, improving documentation, or reporting issues.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Guidelines](#coding-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Testing](#testing)
- [Community](#community)
- [Contributor License Agreement](#contributor-license-agreement)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We expect all contributors to be respectful, inclusive, and considerate of others. Harassment or disrespectful behavior of any kind will not be tolerated.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/ranaroussi/muxi.git
   cd muxi
   ```
3. Add the original repository as an upstream remote:

   ```bash
   git remote add upstream https://github.com/ranaroussi/muxi.git
   ```
4. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

1. Install Python 3.9 or later
2. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the framework in development mode:

   ```bash
   pip install -e .
   ```
4. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

### For frontend development:

1. Navigate to the web module directory:

   ```bash
   cd packages/web/src/muxi/web/ui
   ```
2. Install Node.js dependencies:

   ```bash
   npm install
   ```
3. Start the development server:

   ```bash
   npm run dev
   ```

## Project Structure

The MUXI Framework follows a modular monorepo architecture:

```
.context/                  # Project context and continuity documentation
.cursor/                   # Cursor editor configuration and rules
.github/                   # GitHub configuration (workflows, templates)
examples/                  # Example usage
  └─ configs/              # Example configuration files
migrations/                # Database migration scripts
packages/                  # Source code organized into modules
 └─ core/                  # Core components
    └─ muxi/core/          # Core module with agents, memory, MCP, etc.
       ├── agent.py        # Agent implementation
       ├── orchestrator.py # Orchestrator with centralized memory and API keys
       ├── memory/         # Memory systems including FAISS-backed smart buffer
       ├── mcp/            # MCP implementation with centralized service
       ├── models/         # LLM provider interfaces
       └── config/         # Configuration components
 └─ server/                # API and WebSocket server
    └─ muxi/server/        # Server module source code
 └─ cli/                   # Command-line interface
    └─ muxi/cli/           # CLI module source code
 └─ meta/                  # Meta-package for MUXI distribution
    └─ muxi/               # Meta-package source code
 └─ web/                   # Web dashboard
    └─ muxi/web/           # Web app source code
scripts/                   # Utility scripts
tests/                     # Test files
```

Key architectural components:

1. **Core Package**: Contains the essential framework components including Agent, Orchestrator, Memory systems, and MCP implementation. The orchestrator now centralizes memory management and API key handling.

2. **Memory Systems**: Implemented in `packages/core/muxi/core/memory/`:
   - SmartBufferMemory with FAISS-backed vector search (buffer.py)
   - Long-term memory with vector database support (long_term.py)
   - Multi-user memory partitioning (memobase.py)
   - Vector database integrations for SQLite and PostgreSQL

3. **MCP Implementation**: Centralized in `packages/core/muxi/core/mcp/service.py` as a singleton service.

4. **Server Components**: REST API with dual-key authentication and WebSocket support.

5. **Meta Package**: Provides a unified interface to all components.

## Coding Guidelines

### Python Guidelines

- Follow PEP 8 guidelines for code formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (Black default)
- Use Black for code formatting: `black packages tests`
- Use isort for import sorting: `isort packages tests`
- Use flake8 for linting: `flake8 packages tests`
- Use type hints for all function signatures
- Add docstrings in Google format for all functions, classes, and modules

#### Code organization:

- Use descriptive variable names in `snake_case`
- Use `PascalCase` for class names
- Use `UPPER_SNAKE_CASE` for constants
- Use `_leading_underscore` for private attributes/methods

#### Import conventions:

```python
from typing import Dict, List, Optional, Any  # Import specific types
import standard_library                       # Standard library imports first
import third_party_library                    # Third party imports second
from muxi.core.module import local_import     # Local imports last
```

### TypeScript/React Guidelines (Web UI)

- Use TypeScript for all frontend code
- Follow consistent naming conventions:
  - `PascalCase` for React components and interface names
  - `camelCase` for variables, functions, and methods
  - `UPPER_SNAKE_CASE` for constants
- Use functional components with hooks
- Use proper type annotations
- Format code with prettier

### MCP (Model Context Protocol) Guidelines

When working with the Model Context Protocol:

- Follow the official MCP specification
- Implement proper tool call handling
- Properly format messages for different language model providers
- Validate all inputs for security
- Test all tool integrations thoroughly

## Pull Request Process

1. Ensure your code meets the project's coding guidelines
2. Run the tests to make sure your changes don't break existing functionality:

   ```bash
   python -m pytest
   ```
3. Update the documentation if you're changing any user-facing features
4. Make sure your commit messages are clear and follow conventional commit format:

   ```
   type(scope): description

   body

   [optional footer]
   ```
   Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
5. Push your changes to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```
6. Submit a pull request to the main repository
7. Address any feedback from reviewers

Pull requests require at least one approval from a maintainer before being merged.

## Issue Reporting

When reporting issues, please include as much information as possible:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Screenshots (if applicable)
5. Environment details (OS, Python version, etc.)
6. Any relevant logs or error messages

Use the issue templates provided in the repository when available.

## Feature Requests

Feature requests are welcome. To submit a feature request:

1. Check existing issues and pull requests to avoid duplicates
2. Use the feature request template if available
3. Clearly describe the problem your feature would solve
4. Provide examples of how the feature would be used
5. Indicate if you're willing to contribute the implementation

## Documentation

Documentation is critical to the success of the project. When contributing:

- Update relevant documentation for any code changes
- Follow the existing style and formatting
- Use clear language and provide examples where possible
- Document both API usage and implementation details
- Add docstrings for new functions, methods, and classes

## Testing

- Write unit tests for all new functionality
- Use pytest as the testing framework
- Run the existing test suite before submitting a PR:

  ```bash
  python -m pytest
  ```
- Aim for high test coverage, especially for business logic
- Test both happy paths and error cases

## Contributor License Agreement

That we do not have any potential problems later, it is sadly necessary to sign a [Contributor License Agreement](https://github.com/ranaroussi/muxi/blob/main/CONTRIBUTOR_LICENSE_AGREEMENT.md). That can be done literally with the push of a button.

Once a pull request is opened, an automated bot will promptly leave a comment requesting the agreement to be signed. The pull request can only be merged once the signature is obtained.

---

Thank you for contributing to the MUXI Framework! Your efforts help make this project better for everyone.
