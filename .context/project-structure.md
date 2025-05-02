# MUXI Framework Project Structure

```
muxi-framework/
├── .context/                  # Project context and continuity documentation
│   ├── project-brief.md       # Foundation document with core project goals and requirements
│   ├── product-context.md     # Why the project exists and the problems it solves
│   ├── system-patterns.md     # System architecture and design patterns
│   ├── tech-context.md        # Technologies used and development setup
│   ├── active-context.md      # Current work focus and next steps
│   ├── progress.md            # What works and what's left to build
│   ├── project-structure.md   # This file - project structure documentation
│   └── scratchpad/            # Work-in-progress documentation and notes
├── .cursor/                   # Cursor editor configuration files
│   └── rules/                 # Cursor rules for code patterns and guidelines
│       ├── mcp_service.mdc    # Centralized MCP Service architecture
│       ├── 07_memory_systems_guidelines.mdc # Memory systems guidelines
│       ├── memory_extraction.mdc # Memory extraction guidelines
│       └── [various .mdc files] # Other guidelines and patterns
├── .github/                   # GitHub configuration (actions, templates, etc.)
├── .git/                      # Git repository data
├── .pytest_cache/             # Pytest cache directory
├── docs/                      # Documentation files
│   ├── _includes/             # Jekyll includes for documentation site
│   ├── _site/                 # Generated documentation site
│   ├── .jekyll-cache/         # Jekyll cache
│   ├── assets/                # Documentation assets (images, etc.)
│   └── [various .md files]    # Markdown documentation files
├── examples/                  # Example code for using the framework
│   ├── configs/               # Example configuration files
│   └── [various .py files]    # Example Python scripts
├── migrations/                # Database migration scripts
├── packages/                  # Modular packages structure
│   ├── cli/                   # Command-line interface package
│   │   ├── muxi/
│   │   │   └── cli/           # CLI package source code
│   │   ├── setup.py           # Package configuration
│   │   └── README.md          # CLI documentation
│   ├── core/                  # Core functionality package
│   │   ├── muxi/
│   │   │   └── core/          # Core package source code
│   │   │       ├── agent.py   # Agent implementation
│   │   │       ├── orchestrator.py  # Orchestrator with centralized memory and API keys
│   │   │       ├── mcp/       # Model Context Protocol implementation
│   │   │       │   ├── service.py   # Centralized MCPService singleton
│   │   │       │   ├── handler.py   # MCP Handler
│   │   │       │   └── message.py   # MCP Message structure
│   │   │       ├── memory/    # Memory systems
│   │   │       │   ├── buffer.py    # FAISS-backed buffer memory with context window and buffer multiplier
│   │   │       │   ├── long_term.py # Long-term memory with vector storage
│   │   │       │   ├── memobase.py  # Multi-user memory partitioning
│   │   │       │   ├── sqlite.py    # SQLite vector integration
│   │   │       │   └── extractor.py # User information extraction
│   │   │       ├── models/    # LLM provider implementations
│   │   │       ├── config/    # Configuration components
│   │   │       └── knowledge/ # Knowledge integration
│   │   ├── setup.py           # Package configuration
│   │   └── README.md          # Core documentation
│   ├── meta/                  # Meta-package for installation
│   │   ├── muxi/              # Meta-package source code
│   │   ├── setup.py           # Package configuration
│   │   └── README.md          # Meta-package documentation
│   ├── server/                # Server implementation package
│   │   ├── muxi/
│   │   │   └── server/        # Server package source code
│   │   ├── setup.py           # Package configuration
│   │   └── README.md          # Server documentation
│   └── web/                   # Web application package
│   │   ├── muxi/
│   │   │   └── web/           # Web UI package source code
│   │   ├── setup.py           # Package configuration
│   │   └── README.md          # Web UI documentation
├── scripts/                   # Utility scripts for project management
├── tests/                     # Test files and directories
│   ├── test_agent.py          # Tests for agent functionality
│   ├── test_orchestrator.py   # Tests for orchestrator functionality
│   ├── test_mcp.py            # Tests for MCP functionality
│   ├── test_memory.py         # Tests for memory systems
│   └── [various test files]   # Other tests
├── .cursorignore              # Files to be ignored by Cursor editor
├── .env                       # Environment variables (not in repo)
├── .env.example               # Example environment variables
├── .flake8                    # Flake8 configuration
├── CONTRIBUTOR_LICENSE_AGREEMENT.md # Contributor license agreement
├── env_check.py               # Script to check environment variables
├── install_dev.sh             # Script to install packages in development mode
├── LICENSE.txt                # License information
├── NEXT_STEPS.md              # Development tasks and implementation checklist
├── pyproject.toml             # Python project configuration
├── pytest.ini                 # Pytest configuration
├── README.md                  # Project overview and documentation
├── requirements-dev.txt       # Development dependencies
├── requirements.txt           # Production dependencies
├── run_tests.py               # Script to run tests
└── run_version_tests.sh       # Script to run tests on different Python versions
```

## Files Explanation

### Configuration Files
- `.cursorignore` - Specifies files for the Cursor editor to ignore.
- `.env` - Contains environment variables for development.
- `.env.example` - Example environment variable file for reference.
- `.flake8` - Configuration for the Flake8 linter.
- `pyproject.toml` - Python project configuration for tools like Black and isort.
- `pytest.ini` - Configuration for pytest testing framework.

### Documentation Files
- `README.md` - Main project documentation with overview, features, architecture, and usage examples.
- `CONTRIBUTOR_LICENSE_AGREEMENT.md` - Legal agreement for contributors.
- `LICENSE.txt` - Project license information.
- `NEXT_STEPS.md` - Detailed task tracker for developers with completed work and todo items.

### Context Files
- `.context/project-brief.md` - Foundation document defining core requirements and project scope.
- `.context/product-context.md` - Explains why the project exists and what problems it solves.
- `.context/system-patterns.md` - Documents system architecture, design patterns, and component relationships.
- `.context/tech-context.md` - Details technologies used, development setup, and technical constraints.
- `.context/active-context.md` - Tracks current work focus, recent changes, and next steps.
- `.context/progress.md` - Documents what works, what's left to build, and current status.
- `.context/project-structure.md` - This file - documents the project structure.
- `.context/scratchpad/api.md` - API specification for REST endpoints and WebSocket communication.

### Utility Scripts
- `env_check.py` - Validates environment variables and their configuration.
- `install_dev.sh` - Installs all MUXI packages in development mode for easier modification.
- `run_tests.py` - Script to run the project's test suite.
- `run_version_tests.sh` - Tests compatibility with different Python versions.

## Directories Explanation

### Development and CI/CD
- `.cursor/` - Contains configuration for the Cursor editor and development guidelines:
	- `rules/` directory contains MDC files with coding patterns and best practices
	- Rules document important architectural patterns like the centralized MCP service
	- Memory system guidelines explain the orchestrator-level memory architecture
	- Detailed guidelines for different components of the framework
- `.github/` - GitHub-specific files for actions, workflows, and issue templates.
- `.git/` - Git repository data.
- `.pytest_cache/` - Cache directory for pytest.

### Project Context
- `.context/` - Structured documentation for project continuity and context:
	- Core context files in a clear hierarchy (from project-brief to progress)
	- Project structure documentation (this file)
	- Scratchpad for works-in-progress like API specifications
	- Serves as the comprehensive knowledge repository for the project
	- Maintains continuity and shared understanding across development

### Documentation
- `docs/` - Contains all project documentation in Markdown format, including:
	- Architecture documentation
	- User guides
	- API references
	- Configuration guides
	- Development guidelines
	- Jekyll configuration for the documentation site

### Code and Examples
- `examples/` - Sample code demonstrating how to use the framework:
	- Basic usage examples
	- Configuration-based agent setup
	- Multi-agent orchestration
	- WebSocket client implementation

### Package Structure
- `packages/` - Modular monorepo structure:
  	- `core/` - Core functionality including:
		- Orchestrator with centralized memory management and API key handling
		- Agent implementation that delegates to the orchestrator for memory access
		- Centralized MCPService as a singleton for thread-safe MCP server interaction
		- FAISS-backed smart buffer memory with hybrid semantic+recency retrieval
		- Memory systems with PostgreSQL and SQLite vector database support
		- Multi-user support through Memobase memory partitioning
		- Configurable timeout settings at orchestrator, agent, and per-request levels
		- LLM provider implementations with standardized interfaces
		- Knowledge integration components
  	- `server/` - Server implementation with API endpoints and WebSocket:
	    - REST API with dual-key authentication (user and admin keys)
	    - SSE streaming for real-time responses
	    - MCP server implementation for tool hosting
	    - Error handling and response standardization
  	- `cli/` - Command-line interface for interacting with agents:
	    - Commands for chat and message sending
	    - Server management functionality
	    - Configuration management
  	- `web/` - Web application frontend:
	    - React-based chat interface
	    - WebSocket integration for real-time updates
	    - Configuration management UI
  	- `meta/` - Meta-package that installs core, server, and CLI:
	    - Simplified import paths
	    - Unified installation
	    - Top-level API exposing core functionality

### Supporting Directories
- `migrations/` - Database schema migration scripts for vector databases.
- `scripts/` - Utility scripts for project management and automation.
- `tests/` - Test files and directories for unit and integration tests:
	  - Tests for agent functionality
	  - Tests for orchestrator with centralized memory
	  - Tests for MCPService and tool invocation
	  - Tests for FAISS-backed buffer memory
	  - Tests for SQLite and PostgreSQL vector database integrations
	  - Tests for API key authentication and validation
