# MUXI Framework Project Structure

```
muxi/
├── .cursor/                   # Cursor editor configuration files
├── .github/                   # GitHub configuration (actions, templates, etc.)
├── .git/                      # Git repository data
├── .pytest_cache/             # Pytest cache directory
├── brainstorm/                # Development ideas and brainstorming documents
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
│   ├── core/                  # Core functionality package
│   ├── muxi/                  # Meta-package that includes core, server, and CLI
│   ├── server/                # Server implementation package
│   └── web/                   # Web application package
├── scripts/                   # Utility scripts for project management
├── tests/                     # Test files and directories
├── .cursorignore              # Files to be ignored by Cursor editor
├── .env                       # Environment variables (not in repo)
├── .env.example               # Example environment variables
├── .flake8                    # Flake8 configuration
├── cleanup.sh                 # Script to remove old src/ directory after migration
├── CONTRIBUTOR_LICENSE_AGREEMENT.md # Contributor license agreement
├── env_check.py               # Script to check environment variables
├── fix_imports.sh             # Script to fix imports after package restructuring
├── install_dev.sh             # Script to install packages in development mode
├── LICENSE.txt                # License information
├── NEXT_STEPS.md              # Development tasks and implementation checklist
├── PROJECT_STRUCTURE.md       # This file
├── pyproject.toml             # Python project configuration
├── pytest.ini                 # Pytest configuration
├── README.md                  # Project overview and documentation
├── requirements-dev.txt       # Development dependencies
├── requirements.txt           # Production dependencies
├── run_tests.py               # Script to run tests
├── run_version_tests.sh       # Script to run tests on different Python versions
└── update_imports.sh          # Script to update imports
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

### Utility Scripts
- `cleanup.sh` - Script to remove the old src/ directory after successful migration to packages structure.
- `env_check.py` - Validates environment variables and their configuration.
- `fix_imports.sh` - Fixes import references for the new package structure and creates symlinks for development.
- `install_dev.sh` - Installs all MUXI packages in development mode for easier modification.
- `run_tests.py` - Script to run the project's test suite.
- `run_version_tests.sh` - Tests compatibility with different Python versions.
- `update_imports.sh` - Updates import statements throughout the codebase.

## Directories Explanation

### Development and CI/CD
- `.cursor/` - Contains configuration for the Cursor editor.
- `.github/` - GitHub-specific files for actions, workflows, and issue templates.
- `.git/` - Git repository data.
- `.pytest_cache/` - Cache directory for pytest.

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
  - `core/` - Core functionality and shared components
  - `server/` - Server implementation with API endpoints and WebSocket
  - `cli/` - Command-line interface for interacting with agents
  - `web/` - Web application frontend
  - `muxi/` - Meta-package that installs core, server, and CLI

### Supporting Directories
- `brainstorm/` - Contains early-stage ideas and development notes.
- `migrations/` - Database schema migration scripts.
- `scripts/` - Utility scripts for project management and automation.
- `tests/` - Test files and directories for unit and integration tests.
