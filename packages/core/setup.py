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
        "anyio>=3.7.0",
        "python-dotenv>=1.0.0",
        "websockets>=11.0.3",
        "httpx-sse>=0.4.0",
        "rich>=13.6.0",
        "colorama>=0.4.6",
        "mcp>=1.4.1",
    ],
    extras_require={
        "server": [
            "fastapi>=0.104.0",
            "uvicorn>=0.23.1",
            "starlette>=0.27.0",
        ],
        "vector": [
            "faiss-cpu>=1.10.0",
            "pgvector>=0.3.6",
            "numpy>=1.24.0",
        ],
        "database": [
            "aiosqlite>=0.19.0",
            "psycopg2-binary>=2.9.9",
            "SQLAlchemy>=2.0.17",
        ],
        "providers": [
            "openai>=0.27.8",
            "anthropic>=0.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
        ],
        "all": [
            "fastapi>=0.104.0",
            "uvicorn>=0.23.1",
            "starlette>=0.27.0",
            "faiss-cpu>=1.10.0",
            "pgvector>=0.3.6",
            "numpy>=1.24.0",
            "aiosqlite>=0.19.0",
            "psycopg2-binary>=2.9.9",
            "SQLAlchemy>=2.0.17",
            "openai>=0.27.8",
            "anthropic>=0.5.0",
            "pytest>=7.0.0",
        ],
    },
)
