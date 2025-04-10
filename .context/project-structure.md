# MUXI Framework Project Structure

```
muxi-framework/
├── .context/                  # Project context and continuity documentation
│   ├── project-brief.md       # Foundation document with core project goals and requirements
│   ├── product-context.md     # Why the project exists and problems it solves
│   ├── system-patterns.md     # System architecture and design patterns
│   ├── tech-context.md        # Technologies used and development setup
│   ├── active-context.md      # Current work focus and next steps
│   ├── progress.md            # What works and what's left to build
│   ├── project-structure.md   # This file - project structure documentation
│   └── scratchpad/            # Work-in-progress documentation and notes
├── .cursor/                   # Cursor editor configuration files
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
│   │   ├── pyproject.toml     # Package configuration
│   │   └── src/muxi/cli/      # CLI package source code
│   ├── core/                  # Core functionality package
│   │   ├── pyproject.toml     # Package configuration
│   │   └── src/muxi/core/     # Core package source code with agents, memory, tools
│   ├── muxi/                  # Meta-package that includes core, server, and CLI
│   │   ├── pyproject.toml     # Package configuration
│   │   └── src/muxi/          # Meta-package source code
│   ├── server/                # Server implementation package
│   │   ├── pyproject.toml     # Package configuration
│   │   └── src/muxi/server/   # Server package with API endpoints and WebSocket
│   └── web/                   # Web application package
│       ├── package.json       # NPM package configuration
│       ├── public/            # Static web assets
│       └── src/               # Web app source code
├── scripts/                   # Utility scripts for project management
├── tests/                     # Test files and directories
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
- `.cursor/` - Contains configuration for the Cursor editor.
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
  - Jekyll configuration for documentation site

### Code and Examples
- `examples/` - Sample code demonstrating how to use the framework:
  - Basic usage examples
  - Configuration-based agent setup
  - Multi-agent orchestration
  - WebSocket client implementation

### Package Structure
- `packages/` - Modular monorepo structure:
  - `core/` - Core functionality including agents, memory systems, tools, and MCP handlers
    - `src/muxi/core/agent.py` - Agent implementation
    - `src/muxi/core/memory.py` - Memory system implementation
    - `src/muxi/core/mcp.py` - Model Context Protocol implementation
    - `src/muxi/core/tools/` - Tool implementations
  - `server/` - Server implementation with API endpoints and WebSocket
    - `src/muxi/server/api/` - REST API implementation
    - `src/muxi/server/ws/` - WebSocket implementation
    - `src/muxi/server/config/` - Server configuration
  - `cli/` - Command-line interface for interacting with agents
    - `src/muxi/cli/commands.py` - CLI commands
    - `src/muxi/cli/app.py` - CLI application
  - `web/` - Web application frontend
    - `src/components/` - React components
    - `src/services/` - API service implementations
  - `muxi/` - Meta-package that installs core, server, and CLI
    - Provides a unified interface to all components

### Supporting Directories
- `migrations/` - Database schema migration scripts.
- `scripts/` - Utility scripts for project management and automation.
- `tests/` - Test files and directories for unit and integration tests.
  - `tests/test_agent.py` - Tests for agent functionality
  - `tests/test_mcp.py` - Tests for Model Context Protocol
  - `tests/test_memory.py` - Tests for memory systems
  - `tests/test_tools.py` - Tests for tools framework
