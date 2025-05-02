# MUXI CLI Client PRD

> ### Command-line Interface for MUXI API Server

## Overview

This document outlines the implementation of the MUXI Command Line Interface (CLI), a comprehensive client for interacting with the MUXI API Server. The CLI will provide terminal-based access to all API Server features, supporting both interactive and scripting workflows while maintaining consistent authentication and configuration patterns.

## Problem Statement

As the MUXI Framework evolves, users need a powerful command-line interface that can:

1. Provide scriptable access to all MUXI features via the API Server
2. Support multiple environments and configurations through profiles
3. Enable quick testing and interaction without requiring a GUI
4. Support automation and CI/CD integration
5. Offer a consistent user experience across different systems

## Objectives

1. Create a comprehensive CLI client for the MUXI API Server
2. Implement profile-based configuration management
3. Support command-line authentication and server specification
4. Provide shell completion and help documentation
5. Enable both human-friendly and machine-parsable outputs
6. Support all API Server features through logical command grouping

## Feature Requirements

### Core CLI Architecture

1. **Command Structure**:
   - Root command: `muxi`
   - Grouped subcommands by domain (agents, chat, memory, etc.)
   - Consistent flag patterns across all commands
   - Support for global flags that apply to all commands

2. **Configuration Management**:
   - Profile-based configuration stored in `~/.muxi/config` (or OS-appropriate location)
   - Environment variable support for all settings
   - Command-line flag overrides for all settings
   - Auto-creation of config file structure on first use

3. **Authentication**:
   - Support for API keys with profile-based storage
   - Environment variable fallback for CI/CD integrations use-case
   - Secure handling and masking of sensitive information
   - Clear error messaging for authentication failures

4. **Output Formats**:
   - Human-friendly formatted output by default
   - JSON output option for all commands
   - YAML output option for configuration viewing
   - Quiet mode for scripting without output
   - Support for colored output with disabling option

### Configuration System

The CLI will use an INI-style configuration file similar to AWS CLI and MySQL clients, stored at `~/.muxi/config` (or `~/.config/muxi/config` on Linux, `%APPDATA%\muxi\config` on Windows) with the following structure:

```ini
[default]
output_format = text
color = true
default_profile = local

[profile local]
host = http://localhost:8000
api_key_user = sk_muxi_user_abc123
api_key_admin = sk_muxi_admin_abc123
timeout = 30
ssl_verify = true

[profile production]
host = https://api.example.com
api_key_user = sk_muxi_user_xyz789
api_key_admin = sk_muxi_admin_xyz789
timeout = 60
ssl_verify = true
```

This approach is immediately familiar to users of other command-line tools and allows for easy editing in any text editor.

> **Note on API Keys**: Profiles can be created with only one API key type (either user or admin key). When users with only a user key attempt to access admin-restricted commands, they will receive a user-friendly message explaining that the command is restricted to developers/administrators. This prevents unnecessary confusion while maintaining proper access control.

The CLI will support the following configuration management commands:

```bash
# Create or update a profile
muxi profiles create [-n|--name NAME] [-h|--host URL] [-k|--key KEY] [--timeout SECONDS] [--ssl-verify BOOL] [--default]

# List available profiles
muxi profiles list

# Show profile details
muxi profiles show [-n|--name NAME]

# Delete a profile
muxi profiles delete [-n|--name NAME]

# Set default profile
muxi profiles set-default [-n|--name NAME]
```

During interactive profile creation, the CLI will ask users if the profile should be set as the default profile:

```
$ muxi profiles create
Profile name: production
Host URL: https://api.example.com
User API Key: ************
Admin API Key: ************
Set as default profile? [y/N]: y
Profile "production" created and set as default.
```

The default profile will be used when no specific profile is provided via the `--profile` option.

### Command-line Options

All commands will support the following global options:

```bash
# Profile selection
-p, --profile STRING       Use specific profile from config file

# Direct connection options (override profile settings)
-h, --host URL             API Server URL
-k, --key STRING|$VAR      API key for authentication
--timeout SECONDS          Request timeout
--no-ssl-verify            Disable SSL certificate verification

# Output formatting
-o, --output FORMAT        Output format: text, json, yaml
-q, --quiet                Suppress all output except errors
--no-color                 Disable colored output

# Misc
-v, --verbose              Enable verbose output
--help                     Show help for command
--version                  Show CLI version
```

### Supported Command Groups

#### 1. Agent Management

```bash
# List agents
muxi agents list

# Get agent details
muxi agents get [agent_id]

# Create agent
muxi agents create --name NAME [--description DESC] [--system-prompt PROMPT] [--model MODEL]
# or muxi agents create → interactive mode

# Update agent
muxi agents update [agent_id] [--name NAME] [--description DESC] [--system-prompt PROMPT] [--model MODEL]
# or muxi agents update [agent_id] → interactive mode

# Delete agent
muxi agents delete [agent_id]

# Import agent from file
muxi agents import [--file PATH]
```

#### 2. Chat/Conversation

```bash
# Chat with orchestrator
muxi chat [--message "Your message"] [--user-id USER] [--file FILE] [--stream]
# or muxi chat → interactive mode

# Chat with specific agent
muxi chat [agent_id] [--message "Your message"] [--user-id USER] [--file FILE] [--stream]
# or muxi chat [agent_id] → interactive mode

# List conversations
muxi conversations list [--user-id USER]

# Get conversation history
muxi conversations get [conversation_id]
```

#### 3. Memory Management

```bash
# Search agent memory
muxi memory search [agent_id] [--query "search term"] [--limit NUMBER]

# Clear agent memory
muxi memory clear [agent_id]
```

#### 4. Knowledge Management

```bash
# List knowledge sources
muxi knowledge list [agent_id]

# Add knowledge
muxi knowledge add [agent_id] [--file PATH] [--url URL] [--text "Content"]

# Remove knowledge
muxi knowledge remove [agent_id] [knowledge_id]

# Search knowledge
muxi knowledge search [agent_id] [--query "search term"]
```

#### 5. System Information

```bash
# Get system status
muxi system status

# Get system usage statistics
muxi system usage
```

#### 6. MCP Functionality

```bash
# List available tools
muxi tools list [agent_id]

# Invoke tool
muxi tools invoke [tool_name] [--params JSON] [--agent-id AGENT]
```

### Interactive Features

The CLI will support several interactive features:

1. **Interactive Chat Mode**:

   ```bash
   # Start interactive chat session
   muxi chat interactive [agent_id]
   ```
   This will provide a REPL-like interface for chatting with agents.

2. **Shell Completion**:

   ```bash
   # Install shell completion
   muxi completion install [--shell bash|zsh|fish]
   ```

3. **Interactive Configuration**:

   ```bash
   # Interactive profile creation wizard
   muxi profiles create --interactive
   ```

### Output Handling

The CLI will provide consistent output handling across all commands:

1. **Text Output (Default)**:
   Human-readable formatted output optimized for terminal viewing.

2. **JSON Output**:

   ```bash
   muxi agents list --output json
   ```
   Machine-parsable JSON output for scripting and automation.

3. **YAML Output**:

   ```bash
   muxi profiles show --output yaml
   ```
   Structured but readable output for configuration viewing.

4. **Streaming Output**:
   For commands that support streaming (e.g., chat), the CLI will provide real-time updates as they arrive from the API Server.

## Example Flows

### Profile Setup and Agent Creation

```bash
# Create a profile
muxi profiles create --name production --host https://api.example.com --key sk_muxi_admin_xyz789

# Set as default
muxi profiles set-default --name production

# Create a new agent
muxi agents create --name "Research Assistant" --description "Helps with research tasks" --model "gpt-4"
```

### Multi-environment Testing

```bash
# Check agents on staging
muxi agents list --profile staging

# Compare with production
muxi agents list --profile production

# Create new agent on staging only
muxi agents create --profile staging --name "Test Agent" --description "Testing only"
```

### Interactive Chat

```bash
# Start interactive chat with default agent through orchestrator
muxi chat interactive

# Start interactive chat with specific agent
muxi chat interactive agent_123abc

# Exit interactive mode with /exit or Ctrl+D
```

### Scripting Integration

```bash
# Create agent and capture ID in script
AGENT_ID=$(muxi agents create --name "Script Agent" --output json | jq -r '.id')

# Use agent in further operations
muxi chat $AGENT_ID --message "Hello, I was created by a script" --output json > response.json
```

## Implementation Approach

### Technology Stack

1. **Core CLI Framework**:
   - Modern CLI framework with subcommand support (e.g., Click, Commander.js)
   - HTTP client library for API communication
   - Structured error handling

2. **Configuration Management**:
   - YAML/JSON parsing libraries
   - Secure credential storage integration
   - OS-specific path management

3. **Output Formatting**:
   - Terminal UI libraries for interactive features
   - Table formatting for data presentation
   - Color handling with ANSI/VT100 support

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       MUXI CLI Client                       │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │
│  │  Command      │  │  Config       │  │  Output       │    │
│  │  Processor    │  │  Manager      │  │  Formatter    │    │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘    │
│          │                  │                  │            │
│  ┌───────▼──────────────────▼──────────────────▼──────┐     │
│  │                   HTTP Client                      │     │
│  └───────────────────────────┬────────────────────────┘     │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       MUXI API Server                        │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Phases

#### Phase 1: Core Infrastructure (Highest Priority)

1. Implement command-line parsing and routing
2. Create configuration management system
3. Implement authentication handling
4. Develop output formatting system
5. Set up error handling and logging

#### Phase 2: Basic API Commands (High Priority)

1. Implement agent management commands
2. Add basic chat functionality
3. Implement profile management commands
4. Add system information commands
5. Create basic documentation and help system

#### Phase 3: Advanced Features (Medium Priority)

1. Add interactive chat mode
2. Implement streaming support
3. Implement memory and knowledge commands
4. Add MCP tool functionality
5. Implement environment variable support for all options

#### Phase 4: Polish and Documentation (Medium Priority)

1. Refine help and usage documentation
2. Add examples for all commands
3. Implement cross-platform testing
4. Create installation packages
5. Develop comprehensive user guide

#### Phase 5: Enhanced User Experience (Lower Priority)

1. Add shell completion
2. Implement command aliases and shortcuts
3. Create an interactive terminal UI mode
4. Add scripting helpers and automation features
5. Implement configuration wizards for complex operations

#### Phase 6: Advanced Integration (Lowest Priority)

1. Add plugin system for custom commands
2. Implement integration with common CI/CD platforms
3. Create Docker-based CLI version
4. Add advanced telemetry and analytics capabilities
5. Implement synchronization between multiple CLI instances

## Security Considerations

1. **API Key Handling**:
   - Store API keys with appropriate file permissions (600)
   - Support environment variables to avoid storing keys in config
   - Mask keys in all output and logs
   - Clear keys from memory when possible

2. **TLS/SSL Verification**:
   - Enable SSL verification by default
   - Provide clear warnings when disabled
   - Support custom CA certificates

3. **Sensitive Data**:
   - Avoid logging sensitive information
   - Clear terminal history in interactive mode
   - Provide secure input for sensitive information

## Monitoring and Telemetry (TBD)

Optionally, the CLI can include anonymous usage telemetry to help improve the tool:

1. **Usage Statistics**:
   - Command frequency
   - Error rates
   - Performance metrics

2. **User Preferences**:
   - Opt-out option during installation
   - Environment variable to disable (MUXI_TELEMETRY=off)
   - Clear disclosure of collected data

## Installation Options

1. **Package Managers**:
   - npm/yarn (global install)
   - pip for Python implementation
   - Homebrew for macOS
   - apt/yum for Linux distributions

2. **Standalone Binaries**:
   - Single-file executables for major platforms
   - Docker container option

3. **Installation Script**:
   - Curl-based installer
   - Configuration wizard option

## Success Metrics

1. **User Adoption**:
   - CLI installation count
   - Command usage frequency
   - Error rates

2. **Feature Coverage**:
   - Percentage of API features available via CLI
   - Command discoverability (help usage)

3. **Performance**:
   - Command execution time
   - Resource utilization

## Conclusion

The MUXI CLI client will provide a powerful, flexible interface to the MUXI API Server, enabling users to interact with the system through the terminal or automated scripts. With comprehensive profile management, consistent command structure, and support for all API features, the CLI will be an essential tool for both development and production use of the MUXI Framework.

### User Experience Considerations

1. **Permission-Based Command Handling**:
   - When a user with only a user API key attempts to access an admin-restricted command, provide a clear message:

     ```
     $ muxi agents create --name "New Agent"
     Error: This command requires administrator privileges.

     To use this command, you need an admin API key. Your current profile
     'personal' has a user API key which can only access user/interface commands.

     Please create a profile with admin privileges or update your current profile.
     ```

   - Include helpful suggestions for obtaining the proper permissions
   - Avoid technical jargon in error messages
   - Provide links to documentation for more information

2. **Command Discovery and Help**:
   - Clearly mark commands that require admin privileges in help text
   - Include information about required permissions in command documentation
   - Provide examples of both user and admin workflows
