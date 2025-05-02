from setuptools import setup, find_packages

setup(
    name="muxi",
    version="0.1.0",
    description="MUXI Framework (Meta Package)",
    author="Ran Aroussi",
    author_email="ran@aroussi.com",
    packages=find_packages(),
    install_requires=[
        "muxi-core>=0.1.0",
    ],
    extras_require={
        "server": ["muxi-server>=0.1.0"],
        "web": ["muxi-web>=0.1.0"],
        "cli": ["muxi-cli>=0.1.0"],
        "all": [
            "muxi-server>=0.1.0",
            "muxi-web>=0.1.0",
            "muxi-cli>=0.1.0",
        ]
    },
    python_requires=">=3.8",
)
