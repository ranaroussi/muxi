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
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

### For frontend development:

1. Navigate to the web directory:

   ```bash
   cd src/web
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

The MUXI Framework follows a modular structure:

```
.github/                  # GitHub configuration (workflows, templates)
docs/                     # Documentation files
src/                      # Source code
 └─ core/                 # Core components (Agent, Orchestrator)
 └─ models/               # Language model implementations
 └─ memory/               # Memory systems
 └─ tools/                # Tool system
 └─ api/                  # API server
 └─ web/                  # Web dashboard
 └─ utils/                # Utility functions
tests/                    # Test files
examples/                 # Example usage
scripts/                  # Utility scripts
```

## Coding Guidelines

### Python Guidelines

- Follow PEP 8 guidelines for code formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (Black default)
- Use Black for code formatting: `black src tests`
- Use isort for import sorting: `isort src tests`
- Use flake8 for linting: `flake8 src tests`
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
from src.module import local_import           # Local imports last
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

### MCP (Modern Control Protocol) Guidelines

When working with the Modern Control Protocol:

- Follow the official MCP specification
- Implement proper tool call handling
- Properly format messages for different language model providers
- Validate all inputs for security
- Test all tool integrations thoroughly

## Pull Request Process

1. Ensure your code meets the project's coding guidelines
2. Run the tests to make sure your changes don't break existing functionality:

   ```bash
   python run_tests.py
   ```
3. Update the documentation if you're changing any user-facing features
4. Make sure your commit messages are clear and follow conventional commit format:

   ```
   type(scope): description

   body

   [optional footer]
   ```
   Types include: feat, fix, docs, style, refactor, test, chore
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
  python run_tests.py
  ```
- Aim for high test coverage, especially for business logic
- Test both happy paths and error cases

## Community

Join our community channels to get help, discuss features, or connect with other contributors:

- [GitHub Discussions](https://github.com/ranaroussi/muxi/discussions)
- [Discord Server](#) (if applicable)
- [Community Forum](#) (if applicable)

---

Thank you for contributing to the MUXI Framework! Your efforts help make this project better for everyone.
