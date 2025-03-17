#!/usr/bin/env python3
"""
Main entry point for the muxi-cli package when run as a module.

This allows running the CLI with:
python -m muxi.cli

This is useful for development, testing, and containerized deployments
where direct module execution is preferred over CLI commands.
"""

import sys

try:
    from muxi.cli.cli import main
except ImportError:
    # Try relative import for development
    from .cli.cli import main


if __name__ == "__main__":
    sys.exit(main())
