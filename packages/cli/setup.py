from setuptools import setup, find_namespace_packages

setup(
    name="muxi-cli",
    version="0.1.0",
    description="MUXI Framework Command Line Interface",
    author="MUXI Team",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "muxi-core>=0.1.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "muxi=muxi.cli.main:cli",
        ],
    },
)
