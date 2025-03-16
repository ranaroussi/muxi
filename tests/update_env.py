#!/usr/bin/env python3
"""
Environment Variable Update Script

This script checks if the OpenAI API key in the .env file is valid
and updates it to use the text string 'dummy_key' for testing if necessary.
"""

import os
import re
from dotenv import load_dotenv


def update_api_key():
    """Update the OpenAI API key in the .env file for testing."""
    print("Checking OpenAI API key...")

    # Load current environment variables
    load_dotenv()

    # Get the current API key
    current_key = os.getenv("OPENAI_API_KEY", "")

    # Check if it contains 'your_' or similar placeholder text
    if "your_" in current_key.lower() or "xxx" in current_key.lower():
        print("Found placeholder API key. Updating for testing...")

        # Read the .env file
        env_path = os.path.join(os.getcwd(), '.env')
        with open(env_path, 'r') as file:
            env_content = file.read()

        # Replace the OpenAI API key with a dummy key for testing
        updated_content = re.sub(
            r'OPENAI_API_KEY=.*',
            'OPENAI_API_KEY=dummy_key_for_testing',
            env_content
        )

        # Write the updated content back to the .env file
        with open(env_path, 'w') as file:
            file.write(updated_content)

        print("Updated .env file with dummy API key for testing.")

        # Reload environment variables
        load_dotenv()
    else:
        print("API key appears to be set. No changes needed.")


if __name__ == "__main__":
    update_api_key()
