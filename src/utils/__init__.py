import os


def get_version():
    """Get the current version of the AI Agent Framework."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    version_file = os.path.join(base_dir, 'src', '.version')
    try:
        with open(version_file, 'r') as f:
            version = f.read().strip()
        return version
    except (FileNotFoundError, IOError):
        return "0.0.0"  # Default version if file not found
