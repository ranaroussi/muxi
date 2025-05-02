from setuptools import setup, find_packages

setup(
    name="muxi-server",
    version="0.1.0",
    description="MUXI Server Component",
    author="Ran Aroussi",
    author_email="ran@aroussi.com",
    packages=find_packages(),
    install_requires=[
        "muxi-core>=0.1.0",
        # Add server-specific dependencies here
    ],
    python_requires=">=3.8",
)
