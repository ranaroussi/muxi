from setuptools import setup, find_namespace_packages

setup(
    name="muxi-core",
    version="0.1.0",
    description="MUXI Framework Core Components",
    author="MUXI Team",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies only
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
    ],
)
