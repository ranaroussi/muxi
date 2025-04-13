# SQLite Vector Extensions

This directory contains pre-compiled SQLite vector extension binaries (`sqlite-vec`) for different platforms and architectures. These extensions enable vector similarity search capabilities in SQLite databases, which is used by Muxi for local-first vector storage and semantic search.

## Directory Structure

The binaries are organized by architecture and operating system:

```
extensions/
├── x86_64-darwin/    # macOS (Intel)
│   └── sqlite-vec.dylib
├── arm64-darwin/     # macOS (Apple Silicon)
│   └── sqlite-vec.dylib
├── x86_64-linux/     # Linux (x86_64)
│   └── sqlite-vec.so
├── arm64-linux/      # Linux (ARM64)
│   └── sqlite-vec.so
└── x86_64-windows/   # Windows (x86_64)
    └── sqlite-vec.dll
```

## Supported Platforms

The following platforms are currently supported:

- **macOS**: Intel (x86_64) and Apple Silicon (arm64)
- **Linux**: x86_64 and arm64
- **Windows**: x86_64

## Usage

The Muxi framework automatically detects the current operating system and architecture, and loads the appropriate extension binary at runtime.

## Adding Custom Binaries

If you need to add support for a new platform or update an existing binary:

1. Compile the SQLite vector extension for your target platform
2. Place the compiled binary in the appropriate directory (or create a new one if needed)
3. Update the `load_sqlite_vec_extension` function in `packages/server/src/muxi/memory/sqlite.py` if necessary

## Building from Source

Instructions for building the SQLite vector extension from source can be found at:
[sqlite-vec GitHub repository](https://github.com/asg017/sqlite-vec)

## License

The SQLite vector extension is distributed under the MIT license.
