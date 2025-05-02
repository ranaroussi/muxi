from setuptools import setup, find_packages

setup(
    name="muxi-cli",
    version="0.1.0",
    description="MUXI CLI Component",
    author="Ran Aroussi",
    author_email="ran@aroussi.com",
    packages=find_packages(),
    install_requires=[
        "muxi-core>=0.1.0",
        # Add CLI-specific dependencies here
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "muxi=muxi.cli.main:main",
        ],
    },
)
