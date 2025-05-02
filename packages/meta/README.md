# MUXI Framework Meta Package

This is the meta package for the MUXI Framework, providing an easy way to install all components together.

## Installation

### Basic Installation

```bash
pip install muxi
```

This installs the meta package with the core functionality.

### With Components

Install with specific components:

```bash
pip install muxi[server]  # Installs with server component
pip install muxi[web]     # Installs with web component
pip install muxi[cli]     # Installs with CLI component
pip install muxi[all]     # Installs with all components
```

## Components

The MUXI Framework consists of the following components:

- **muxi-core**: Core functionality and base classes
- **muxi-server**: Server implementation
- **muxi-web**: Web interface
- **muxi-cli**: Command-line interface

Each component can also be installed individually:

```bash
pip install muxi-core
pip install muxi-server
pip install muxi-web
pip install muxi-cli
```
