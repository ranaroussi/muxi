"""
MUXI Framework - AI agents and tools for building powerful applications.
"""

from importlib import metadata

try:
    __version__ = metadata.version("muxi")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0-dev"
