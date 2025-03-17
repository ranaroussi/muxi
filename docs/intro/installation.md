---
layout: default
title: Installation
parent: Introduction
nav_order: 5
permalink: /intro/installation/
---

# Installation

## What You'll Learn
- How to install MUXI using different methods
- How to set up your development environment
- How to configure MUXI with environment variables
- Different installation options for various usage scenarios

## Prerequisites
- Python 3.10 or later
- pip (Python package manager)
- A basic understanding of Python environments (recommended)

## Installation Options

MUXI provides several installation options depending on your needs.

### Standard Installation

For most users, the standard installation includes everything you need to get started:

```bash
pip install muxi
```

This installs the main `muxi` package, which includes:
- Core functionality (agents, memory, MCP)
- Server components (API, WebSocket)
- Command-line interface

### Minimal Installation

If you only need the core functionality without the server or CLI:

```bash
pip install muxi-core
```

### Web UI Installation

To use the web interface:

```bash
pip install muxi-web
```

### Development Installation

For contributors or developers who want to modify the framework:

```bash
git clone https://github.com/yourusername/muxi-framework.git
cd muxi-framework
./install_dev.sh
```

The development installation:
- Installs all packages in editable mode
- Sets up pre-commit hooks
- Prepares the development environment

## Environment Setup

### Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Required for most functionality
OPENAI_API_KEY=your-openai-api-key

# Optional but recommended for persistence
DATABASE_URL=postgresql://user:password@localhost:5432/muxi

# Optional for specific MCP servers
WEATHER_API_KEY=your-weather-api-key
SERPER_API_KEY=your-serper-api-key

# Server configuration (optional)
MUXI_HOST=0.0.0.0
MUXI_PORT=5050
MUXI_API_KEY=your-custom-api-key

# Memory configuration (optional)
MUXI_BUFFER_SIZE=10
MUXI_ENABLE_LONG_TERM=true
```

### Loading Environment Variables

In your Python code:

```python
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Now you can use MUXI
from muxi import muxi
app = muxi()
```

## Database Setup

For long-term memory functionality, MUXI requires a PostgreSQL database with the pgvector extension.

### Local PostgreSQL Setup

1. Install PostgreSQL (version 14 or higher recommended)

2. Install the pgvector extension:

```bash
# On Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# On macOS with Homebrew
brew install pgvector
```

3. Create a database and enable the extension:

```sql
CREATE DATABASE muxi;
CREATE EXTENSION IF NOT EXISTS pgvector;
```

4. Set the DATABASE_URL environment variable:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/muxi
```

### Using Docker

You can also use Docker to run PostgreSQL with pgvector:

```bash
docker run -d \
  --name muxi-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=user \
  -e POSTGRES_DB=muxi \
  -p 5432:5432 \
  pgvector/pgvector:pg14
```

Then set your DATABASE_URL:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/muxi
```

## Verifying Installation

To verify that MUXI was installed correctly:

```bash
# Check the installed version
muxi --version

# Start the interactive CLI
muxi chat

# Run a simple test
muxi send "Hello, world!"
```

## Package Structure

After installation, the MUXI framework will have the following structure:

```
muxi/
├── core/          # Core components
├── server/        # Server implementation
├── cli/           # Command-line interface
└── __init__.py    # Main entry point
```

## Troubleshooting

### Common Issues

**Missing API Key**:
```
Error: OpenAI API key not found
```
Solution: Set the OPENAI_API_KEY environment variable.

**Database Connection Error**:
```
Error: Could not connect to database
```
Solution: Verify your DATABASE_URL and ensure PostgreSQL is running.

**Port Already in Use**:
```
Error: Address already in use
```
Solution: Change the port using MUXI_PORT environment variable or the `port` parameter in `app.run()`.

### Getting Help

If you encounter issues not covered here:
- Check the [GitHub Issues](https://github.com/yourusername/muxi-framework/issues) for known problems
- Join the [Discord community](https://discord.gg/muxi) for real-time help
- Visit the [Troubleshooting Guide](/reference/troubleshooting) for detailed solutions

## Advanced Installation

### Installing Specific Versions

```bash
pip install muxi==0.1.0
```

### Installing from Source

```bash
pip install git+https://github.com/yourusername/muxi-framework.git
```

### Virtual Environments

It's recommended to use virtual environments:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install muxi
```

## What's Next

- [Quick Start Guide](/intro/quick-start) - Build your first MUXI application
- [Simple Agents](/agents/simple) - Learn how to create agents
- [Using MCP Servers](/extend/using-mcp) - Extend your agents with external capabilities
