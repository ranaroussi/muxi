from setuptools import setup, find_packages

setup(
    name="muxi-web",
    version="0.1.0",
    description="MUXI Web Component",
    author="Ran Aroussi",
    author_email="ran@aroussi.com",
    packages=find_packages(),
    install_requires=[
        "muxi-core>=0.1.0",
        # Add web-specific dependencies here
    ],
    python_requires=">=3.8",
)
