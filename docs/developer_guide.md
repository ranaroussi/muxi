# MUXI Developer Guide

This guide provides information for developers contributing to the MUXI framework, including how to work with the new modular package structure.

## Setting Up Your Development Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ranaroussi/muxi.git
   cd muxi
   ```

2. **Install Development Dependencies**
   ```bash
   ./install_dev.sh
   ```
   This script installs all packages in development mode, allowing you to modify the code without reinstalling.

3. **Install Additional Development Tools**
   ```bash
   pip install pytest black isort flake8
   ```

## Package Structure

MUXI now follows a modular monorepo structure with these main packages:

- **muxi-core**: Core functionality and shared components
- **muxi-server**: Server implementation
- **muxi-cli**: Command-line interface
- **muxi-web**: Web application
- **muxi**: Meta-package that includes core, server, and CLI

The recommended way to navigate the codebase is:

```
packages/
├── core/        # Core abstractions, models, utils
├── server/      # API, memory, config, tools
├── cli/         # CLI commands and interface
└── web/         # Web interface
```

## Working with Packages

### Making Changes to Core Components

When modifying core components:

1. Navigate to the core package:
   ```bash
   cd packages/core
   ```

2. Make your changes to files in `src/muxi/`

3. Test your changes:
   ```bash
   pytest
   ```

4. See changes immediately thanks to editable mode installation

### Cross-Package Development

When your changes span multiple packages:

1. Use imports from the package perspective:
   ```python
   # In packages/server/src/muxi/server/api/app.py
   from muxi.core.agent import Agent  # Core import
   from muxi.server.config import config  # Server import
   ```

2. Be aware of circular dependencies:
   - core should not import from server, cli, or web
   - server can import from core, but not cli or web
   - cli can import from core, but should avoid importing from server
   - web can import from core, but should avoid importing from server

### Using Symlinks for Development

During development, we use symlinks to handle cross-package imports. The `fix_imports.sh` script has set up these symlinks for you:

```bash
packages/core/src/muxi/server/config -> packages/server/src/muxi/config
packages/core/src/muxi/server/memory -> packages/server/src/muxi/memory
packages/core/src/muxi/server/tools -> packages/server/src/muxi/tools
```

This allows core components to access server components during development. In production, these will be proper package imports.

## Testing

### Running Tests

Run tests for a specific package:

```bash
cd packages/core
pytest
```

Run all tests:

```bash
pytest
```

### Writing Tests

Tests should be organized by package:

```
packages/core/tests/
packages/server/tests/
packages/cli/tests/
packages/web/tests/
```

## Building and Publishing

### Building Packages

Build a specific package:

```bash
cd packages/core
python setup.py sdist bdist_wheel
```

### Publishing to PyPI

Publish a specific package:

```bash
cd packages/core
twine upload dist/*
```

## Common Development Tasks

### Adding a New Tool

1. Create the tool in `packages/server/src/muxi/server/tools/`:
   ```python
   # packages/server/src/muxi/server/tools/my_tool.py
   from muxi.server.tools.base import BaseTool

   class MyTool(BaseTool):
       name = "my_tool"
       description = "My new tool description"

       def execute(self, **kwargs):
           # Implement tool functionality
           return {"result": "Tool output"}
   ```

2. Register the tool in `packages/server/src/muxi/server/tools/__init__.py`:
   ```python
   from muxi.server.tools.my_tool import MyTool

   AVAILABLE_TOOLS = {
       "my_tool": MyTool,
       # Other tools...
   }
   ```

### Adding a New CLI Command

1. Add the command in `packages/cli/src/muxi/cli/commands.py`:
   ```python
   @cli.command()
   @click.option("--option", help="Option description")
   def my_command(option):
       """My command description."""
       # Implement command
       click.echo(f"Running my command with option: {option}")
   ```

### Adding a New Web Component

1. Create the component in `packages/web/src/muxi/web/src/components/`:
   ```javascript
   // packages/web/src/muxi/web/src/components/MyComponent.js
   import React from 'react';

   const MyComponent = () => {
     return (
       <div>
         <h1>My Component</h1>
       </div>
     );
   };

   export default MyComponent;
   ```

## Common Issues and Solutions

### Import Errors

If you encounter import errors:

1. Run the import fixer script:
   ```bash
   ./fix_imports.sh
   ```

2. Check for circular imports:
   - Ensure core doesn't import from server/cli/web
   - Ensure server only imports from core
   - Ensure cli only imports from core

### Missing Packages After Pull

If packages are missing after pulling changes:

1. Re-run the development installation:
   ```bash
   ./install_dev.sh
   ```

## Best Practices

1. **Follow Package Boundaries**: Respect the separation of concerns between packages
2. **Minimize Dependencies**: Keep dependencies minimal, especially in core
3. **Write Tests**: Add tests for new functionality
4. **Document Public APIs**: Document all public methods and classes
5. **Use Type Hints**: Provide type hints for better code quality

## Code Style

Follow these guidelines:

1. Use Black for formatting:
   ```bash
   black packages/
   ```

2. Use isort for import sorting:
   ```bash
   isort packages/
   ```

3. Use flake8 for linting:
   ```bash
   flake8 packages/
   ```

## Contribution Workflow

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes in the appropriate package(s)

3. Run tests:
   ```bash
   pytest
   ```

4. Format your code:
   ```bash
   black packages/
   isort packages/
   ```

5. Create a pull request with a clear description of your changes
