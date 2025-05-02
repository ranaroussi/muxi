"""
Version utilities for MUXI Framework.

This module provides utilities for getting and managing version information.
"""

import os
import json
from typing import Optional


def get_version() -> str:
    """
    Get the version of the MUXI Framework.

    Returns:
        The version string
    """
    # Default version
    default_version = "0.1.0"

    try:
        # Try to read from package.json if it exists
        package_path = os.path.join(os.path.dirname(__file__), "..", "..", "package.json")
        if os.path.exists(package_path):
            with open(package_path, "r") as f:
                package_data = json.load(f)
                if "version" in package_data:
                    return package_data["version"]

        # If that fails, try to get from setup.py
        setup_path = os.path.join(os.path.dirname(__file__), "..", "setup.py")
        if os.path.exists(setup_path):
            with open(setup_path, "r") as f:
                content = f.read()
                version_match = next((line for line in content.splitlines() if 'version="' in line), None)
                if version_match:
                    import re
                    match = re.search(r'version="([^"]+)"', version_match)
                    if match:
                        return match.group(1)

        return default_version
    except Exception as e:
        print(f"Error getting version: {e}")
        return default_version
