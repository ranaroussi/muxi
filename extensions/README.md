# MUXI Framework Extensions

This directory contains extension modules for the MUXI Framework, organized by extension type. Each subdirectory contains a different type of extension.

## Current Extensions

### sqlite-vec

The `sqlite-vec` directory contains pre-compiled SQLite extensions for vector similarity search across different platforms and architectures. These extensions enable vector search capabilities in the MUXI Framework's long-term memory system.

See the `sqlite-vec/README.md` for specific details about the SQLite vector extension.

## Adding New Extensions

To add a new extension:

1. Create a new subdirectory under `/extensions` with a descriptive name for your extension
2. Include all necessary binaries, libraries, or source files in that directory
3. Update the appropriate loader function in the codebase to use your extension
4. Document the extension in a README.md file within your extension directory

This organization allows for clean separation between different types of extensions while maintaining a consistent structure for the framework.
