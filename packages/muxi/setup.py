from setuptools import setup

setup(
    name="muxi",
    version="0.1.0",
    description="MUXI Framework - Complete System (excluding web interface)",
    author="MUXI Team",
    install_requires=[
        "muxi-core>=0.1.0",
        "muxi-server>=0.1.0",
        "muxi-cli>=0.1.0",
        # Web package excluded to support headless server installations
    ],
)
