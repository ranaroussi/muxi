from setuptools import setup, find_packages

setup(
    name="muxi-core",
    version="0.1.0",
    description="MUXI Core Framework",
    author="Ran Aroussi",
    author_email="ran@aroussi.com",
    packages=find_packages(),
    install_requires=[
        "loguru",
        "pydantic",
        "openai>=1.0.0",
        "faiss-cpu",
        "numpy>=1.20.0",
    ],
    python_requires=">=3.8",
)
