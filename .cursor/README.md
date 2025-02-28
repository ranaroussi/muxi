# Cursor IDE Configuration

This directory contains configuration files for the Cursor IDE to enhance the development experience for the AI Agent Framework.

## Available Configurations

- **settings.json**: Contains IDE-wide settings optimized for Python development
- **keybindings.json**: Custom keyboard shortcuts for common operations
- **snippets/python.json**: Code snippets specific to this AI Agent Framework

## Keyboard Shortcuts

| Shortcut | Description |
|----------|-------------|
| Ctrl+Alt+T | Execute Python file in terminal |
| Ctrl+Alt+R | Run current Python file |
| Ctrl+Shift+T | Create a new Python terminal |
| Alt+Shift+F | Run linting on the current file |
| Ctrl+Shift+D | Debug current Python file in terminal |
| Ctrl+Shift+B | Format document |
| Ctrl+Shift+I | Sort imports |

## Code Snippets

| Prefix | Description |
|--------|-------------|
| `aiagent` | Initialize an AI Agent with memory |
| `aitool` | Create a custom tool for the AI Agent Framework |
| `aiws` | Setup a WebSocket handler for the AI Agent Framework |
| `aiapitest` | Create a test for an API endpoint |

## Usage

These configurations are automatically applied when the project is opened in Cursor IDE. To use a snippet, type the prefix (e.g., `aiagent`) and press Tab to expand it.
