#!/usr/bin/env python3
"""
Environment Setup Utility

This module provides functions for ensuring environment variables are properly
loaded from the .env file, even when testing.
"""

import os
from dotenv import load_dotenv


def load_api_keys():
    """
    Load API keys from .env file and ensure they're correctly set in the environment.

    This function:
    1. Loads variables from .env with override=True
    2. Forces the OPENAI_API_KEY to be loaded directly from the .env file
    """
    # Load environment variables with override
    load_dotenv(override=True)

    # Force load the API key from .env file
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.readlines()
        for line in env_content:
            if line.strip().startswith("OPENAI_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["OPENAI_API_KEY"] = key
                break
            # Also load other API keys if needed
            elif line.strip().startswith("ANTHROPIC_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["ANTHROPIC_API_KEY"] = key
            elif line.strip().startswith("MISTRAL_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["MISTRAL_API_KEY"] = key
