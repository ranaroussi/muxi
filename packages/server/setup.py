from setuptools import setup, find_namespace_packages

setup(
    name="muxi-server",
    version="0.1.0",
    description="MUXI Framework Server Implementation",
    author="MUXI Team",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "muxi-core>=0.1.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "python-multipart>=0.0.6",
        "sqlalchemy>=2.0.0",
    ],
)
