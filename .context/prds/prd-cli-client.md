# MUXI CLI PRD

## Overview

The MUXI CLI provides a command-line interface for interacting with the MUXI API. It enables users to manage agents, handle conversations, configure the system, and utilize the full range of MUXI capabilities directly from the terminal.

## Problem Statement

As the MUXI Framework grows, a robust CLI tool is needed to:

1. Provide easy terminal access to all MUXI features without requiring web UI
2. Enable scripting and automation of MUXI interactions
3. Offer a consistent interface for both casual and power users
4. Support both interactive and scripted operational modes
5. Allow configuration management through profiles for different environments

## Objectives

1. Create a feature-complete MUXI CLI for terminal-based interaction
2. Implement a profile-based configuration system for multiple environments
3. Support multiple output formats for both human reading and machine parsing
4. Provide useful command documentation and help text
5. Ensure secure handling of API keys and sensitive configuration

## Feature Requirements

### Core Components

1. **Profile-based Configuration**:
   - INI-style configuration format (similar to AWS CLI)
   - Support for multiple profiles with different settings
   - Secure storage of API keys
   - Default profile selection mechanism

2. **Command Structure**:
   - Hierarchical command organization
   - Global options for all commands
   - Consistent naming and parameter conventions
   - Help documentation for all commands

3. **Authentication**:
   - Support for both user and admin API keys
   - Secure handling of credentials
   - Clear permission indicators for admin-only commands
   - Friendly error messages for permission-denied operations

4. **Output Formats**:
   - Text (default, human-readable)
   - JSON (for programmatic consumption)
   - YAML (for configuration and structured data)
   - Custom formatters for specific data types

5. **Interactive Features**:
   - Chat mode for conversational interaction
   - Configuration wizards for complex operations
   - Confirmation prompts for destructive actions

### Command Groups

The MUXI CLI will implement the following command groups:

1. **Agent Management**:
   - Create, list, update, delete agents
   - Configure agent properties and capabilities
   - Manage agent relationships and teams

2. **Chat/Conversation**:
   - Initiate and manage conversations
   - Send messages to specific agents
   - Record and retrieve conversation history

3. **Memory Management**:
   - Configure memory systems
   - Manage long-term and buffer memory
   - Import and export memory data

4. **Knowledge Management**:
   - Add, update, delete knowledge entries
   - Configure knowledge bases
   - Import/export knowledge

5. **Profiles**:
   - Create, update, delete configuration profiles
   - Set default profile
   - View current configuration

6. **System**:
   - View system status and statistics
   - Configure global settings
   - Manage API keys
   - Handle logging and debugging

7. **MCP**:
   - List available MCP tools
   - Configure MCP servers
   - Test MCP tool invocations

### Authentication and Permissions

The MUXI CLI will support the dual API key system:

1. **User API Key**:
   - Access to chat and basic features
   - Limited management capabilities
   - Used by most end-users

2. **Admin API Key**:
   - Full access to all commands
   - System configuration and management
   - Sensitive operations

Commands will be clearly marked in help text regarding their permission requirements. When using a user API key on admin-restricted commands, a user-friendly error message will be displayed instead of a generic permission error.

## Implementation Approach

The MUXI CLI will be implemented in Python, consistent with the rest of the MUXI Framework. It will leverage the Click library for command structure and argument parsing.

### Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                          MUXI CLI                             │
│                                                               │
│   ┌───────────────┐  ┌────────────────┐  ┌────────────────┐   │
│   │   Commands    │  │  Config Mgmt   │  │  API Client    │   │
│   │   (Click)     │  │  (Profiles)    │  │   (HTTPX)      │   │
│   └───────┬───────┘  └────────┬───────┘  └────────┬───────┘   │
│           │                   │                   │           │
│   ┌───────▼───────────────────▼───────────────────▼───────┐   │
│   │                   Shared Utilities                     │   │
│   │ (Formatting, Error Handling, Authentication, Helpers)  │   │
│   └─────────────────────────────┬───────────────────────┘     │
│                                 │                             │
└─────────────────────────────────┼─────────────────────────────┘
                                  │
                                  │ HTTP/HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                         MUXI API                            │
└─────────────────────────────────────────────────────────────┘
```

### Configuration System

The MUXI CLI will use an INI-style configuration format, stored in:

- `~/.config/muxi/config` (Linux/macOS)
- `%USERPROFILE%\.muxi\config` (Windows)

Example configuration file:

```ini
[default]
profile = production

[profile production]
host = https://api.muxi.example.com
api_key = sk_muxi_user_XXXXXXXXXXXX
output_format = text
color = true

[profile development]
host = http://localhost:8000
api_key = sk_muxi_admin_XXXXXXXXXXXX
output_format = json
ssl_verify = false
timeout = 60
```

### Configuration Options

Each profile can include the following settings:

1. **host**: URL of the MUXI API server
2. **api_key**: Authentication key (user or admin)
3. **output_format**: Default format (text, json, yaml)
4. **ssl_verify**: Whether to verify SSL certificates
5. **color**: Whether to use colored output
6. **timeout**: Request timeout in seconds

### Global Command Options

All commands will support the following options:

1. **--profile**: Select a specific profile
2. **--output**: Output format (text, json, yaml)
3. **--color/--no-color**: Whether to use colored output
4. **--verbose**: Increase output verbosity
5. **--help**: Display help information

### Implementation Phases

The implementation will proceed in the following phases:

1. **Phase 1: Core Infrastructure** (Highest Priority)
   - Configuration management system
   - API client implementation
   - Authentication handling
   - Base command structure
   - Output formatting utilities

2. **Phase 2: Basic API Commands** (Highest Priority)
   - Profile management commands
   - Basic agent management
   - Simple chat interface
   - System status commands

3. **Phase 3: Advanced Features** (Medium Priority)
   - Complete agent management
   - Memory operations
   - Knowledge management
   - Advanced chat features
   - MCP tool integration

4. **Phase 4: Polish and Documentation** (Medium Priority)
   - Comprehensive help documentation
   - Error handling improvements
   - Consistent output formatting
   - Performance optimizations

5. **Phase 5: Enhanced User Experience** (Lower Priority)
   - Interactive chat mode
   - Configuration wizards
   - Shell completion
   - Command aliases

6. **Phase 6: Advanced Integration** (Lower Priority)
   - Plugin system
   - CI/CD platform integration
   - Docker-based CLI
   - Advanced telemetry

### Command-Line Interface

#### Examples

```bash
# Configure a new profile
muxi profiles create --name development --host http://localhost:8000 --key sk_muxi_admin_XXXXXXXXXXXX

# List available agents
muxi agents list

# Create a new agent
muxi agents create --name "Research Assistant" --description "Helps with research tasks"

# Chat with a specific agent
muxi chat --agent "Research Assistant"

# Get system status
muxi system status

# Configure memory settings
muxi memory configure --buffer-size 10 --long-term-store postgres
```

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
   - Variable to disable in config file (telemetry = 0)
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
