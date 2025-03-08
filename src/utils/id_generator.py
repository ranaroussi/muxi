"""
ID generation utilities for the AI Agent Framework.

This module provides functions for generating Nano IDs consistently
across the application.
"""

from nanoid import generate


def generate_nanoid(size: int = 21) -> str:
    """
    Generate a Nano ID of the specified size.

    Args:
        size: Length of the ID to generate. Default is 21 characters.

    Returns:
        A new Nano ID string.
    """
    alphabet = "_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return generate(alphabet, size)


def get_default_nanoid() -> str:
    """
    Get a default Nano ID with standard size.
    Used for SQLAlchemy default values.

    Returns:
        A new Nano ID string of standard length.
    """
    return generate_nanoid()
