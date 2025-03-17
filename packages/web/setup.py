from setuptools import setup, find_namespace_packages

setup(
    name="muxi-web",
    version="0.1.0",
    description="MUXI Framework Web Interface",
    author="MUXI Team",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "muxi-core>=0.1.0",
        "flask>=2.2.0",
        "jinja2>=3.1.0",
        "werkzeug>=2.2.0",
    ],
    include_package_data=True,
)
