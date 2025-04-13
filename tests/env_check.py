#!/usr/bin/env python3
"""
Environment Check Script

This script checks the OpenAI API key that's being used by the framework.
"""

import os
from dotenv import load_dotenv
import openai


def check_env_keys():
    """Check environment variables and OpenAI client key."""
    print("=== Environment Variables Check ===\n")

    # Check environment variables before loading
    openai_key_before = os.environ.get("OPENAI_API_KEY", "Not found")
    print(
        f"OPENAI_API_KEY before loading: "
        f"{openai_key_before[:10]}..."
        f"{openai_key_before[-5:] if len(openai_key_before) > 15 else ''}"
    )

    # Load environment variables with override
    load_dotenv(override=True)

    # Force load the API key from .env file
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_content = f.readlines()
        for line in env_content:
            if line.strip().startswith("OPENAI_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["OPENAI_API_KEY"] = key
                break

    # Check environment variables after loading
    openai_key = os.environ.get("OPENAI_API_KEY", "Not found")
    print(
        f"OPENAI_API_KEY after loading: "
        f"{openai_key[:10]}..."
        f"{openai_key[-5:] if len(openai_key) > 15 else ''}"
    )

    # Check OpenAI client
    client = openai.Client(api_key=openai_key)
    client_key = client.api_key
    print(
        f"OpenAI client API key: "
        f"{client_key[:10]}..."
        f"{client_key[-5:] if len(client_key) > 15 else ''}"
    )

    # Check if .env file exists
    env_path = os.path.join(os.getcwd(), ".env")
    print(f".env file exists: {os.path.exists(env_path)}")

    # Check .env file content
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_content = f.readlines()
        for line in env_content:
            if line.strip().startswith("OPENAI_API_KEY="):
                key = line.strip().split("=", 1)[1]
                print(
                    f"OPENAI_API_KEY in .env file: "
                    f"{key[:10]}..."
                    f"{key[-5:] if len(key) > 15 else ''}"
                )
                break


if __name__ == "__main__":
    check_env_keys()
