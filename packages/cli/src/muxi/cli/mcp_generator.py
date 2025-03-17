"""
MCP Server Generator.

This module provides an interactive wizard for creating new MCP servers
with a chat-like interface in the CLI.
"""

import os
import re
import string
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

console = Console()


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_camel_case(name: str) -> str:
    """Convert a string to CamelCase."""
    components = name.split('_')
    return ''.join(x.title() for x in components)


def create_directories(base_dir: str, server_name: str) -> Dict[str, str]:
    """Create the directory structure for the MCP server."""
    snake_name = to_snake_case(server_name)

    # Create paths
    paths = {
        "root": os.path.join(base_dir, snake_name),
        "tools": os.path.join(base_dir, snake_name, "tools"),
        "tests": os.path.join(base_dir, snake_name, "tests"),
        "examples": os.path.join(base_dir, snake_name, "examples"),
    }

    # Create directories
    for path in paths.values():
        os.makedirs(path, exist_ok=True)

    return paths


def load_template(template_path: str) -> str:
    """Load a template file and return its contents."""
    with open(template_path, 'r') as f:
        return f.read()


def render_template(template: str, context: Dict[str, Any]) -> str:
    """Render a template string with the given context."""
    return string.Template(template).safe_substitute(context)


def create_tool_files(tools_dir: str, tools: List[Dict[str, str]]) -> None:
    """Create Python files for each tool with template code."""
    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "tool.py.template"
    )

    template = load_template(template_path)

    for tool in tools:
        tool_name = to_snake_case(tool["name"])
        tool_class = to_camel_case(tool["name"])

        # Create tool file from template
        tool_file = os.path.join(tools_dir, f"{tool_name}.py")

        # Render template and write to file
        with open(tool_file, "w") as f:
            rendered = template.replace("{{tool_name}}", tool["name"])
            rendered = rendered.replace("{{tool_class}}", tool_class)
            rendered = rendered.replace("{{tool_description}}", tool["description"])
            f.write(rendered)


def create_main_files(root_dir: str, server_name: str, tools: List[Dict[str, str]]) -> None:
    """Create the main server file with template code."""
    snake_name = to_snake_case(server_name)
    camel_name = to_camel_case(server_name)

    server_template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "server.py.template"
    )

    server_file = os.path.join(root_dir, f"{snake_name}_server.py")

    # Generate tool imports
    tool_imports = ""
    tool_instances = ""

    for tool in tools:
        tool_snake = to_snake_case(tool["name"])
        tool_camel = to_camel_case(tool["name"])
        tool_imports += f"from .tools.{tool_snake} import {tool_camel}\n"
        tool_instances += f"        \"{tool['name']}\": {tool_camel}(),\n"

    # Load and render server template
    template = load_template(server_template_path)

    with open(server_file, "w") as f:
        rendered = template.replace("{{server_class}}", camel_name)
        rendered = rendered.replace("{{server_name}}", server_name)
        rendered = rendered.replace("{{tool_imports}}", tool_imports)
        rendered = rendered.replace("{{tool_instances}}", tool_instances)
        f.write(rendered)

    # Create __init__.py
    with open(os.path.join(root_dir, "__init__.py"), "w") as f:
        f.write(f'''"""
{camel_name} MCP Server package.
"""

from .{snake_name}_server import {camel_name}Server, create_app

__all__ = ["{camel_name}Server", "create_app"]
''')


def collect_server_info() -> Dict[str, Any]:
    """Collect information about the MCP server through interactive prompts."""
    console.print(Markdown("# MCP Server Generator"))
    console.print(
        "This wizard will guide you through creating a new MCP server with custom tools."
    )
    console.print()

    # Collect server name
    server_name = Prompt.ask(
        "[bold cyan]What would you like to name your MCP server?[/bold cyan]",
        default="MyMCPServer"
    )

    # Collect server description
    description = Prompt.ask(
        "[bold cyan]Provide a brief description of your MCP server[/bold cyan]",
        default=f"An MCP server for {server_name}"
    )

    # Collect tools
    tools = []
    num_tools = IntPrompt.ask(
        "[bold cyan]How many tools would you like to create?[/bold cyan]",
        default=1
    )

    for i in range(num_tools):
        console.print(f"\n[bold]Tool #{i+1}[/bold]")

        tool_name = Prompt.ask(
            "[bold cyan]Tool name[/bold cyan] (will be converted to camelCase)",
            default=f"Tool{i+1}"
        )

        tool_description = Prompt.ask(
            "[bold cyan]Tool description[/bold cyan]",
            default=f"A tool for {tool_name}"
        )

        tools.append({
            "name": tool_name,
            "description": tool_description
        })

    return {
        "name": server_name,
        "description": description,
        "tools": tools
    }


def create_readme(root_dir: str, info: Dict[str, Any]) -> None:
    """Create a README.md file for the MCP server."""
    readme_template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "readme.md.template"
    )

    # Generate tools list for README
    tools_list = ""
    for tool in info["tools"]:
        tools_list += f"- **{tool['name']}**: {tool['description']}\n"

    # Load and render README template
    template = load_template(readme_template_path)
    snake_name = to_snake_case(info["name"])

    with open(os.path.join(root_dir, "README.md"), "w") as f:
        rendered = template.replace("{{server_name}}", info["name"])
        rendered = rendered.replace("{{server_description}}", info["description"])
        rendered = rendered.replace("{{tools_list}}", tools_list)
        rendered = rendered.replace("{{server_package}}", snake_name)
        f.write(rendered)


def create_setup_py(root_dir: str, info: Dict[str, Any]) -> None:
    """Create a setup.py file for the MCP server."""
    with open(os.path.join(root_dir, "setup.py"), "w") as f:
        f.write(f'''from setuptools import setup, find_packages

setup(
    name="{to_snake_case(info["name"])}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "muxi>=0.2.0",
    ],
    author="",
    author_email="",
    description="{info["description"]}",
    keywords="{to_snake_case(info["name"])}, mcp, muxi",
    python_requires=">=3.8",
)
''')


def create_example_client(examples_dir: str, server_info: Dict[str, Any]) -> None:
    """Create an example client for the MCP server."""
    with open(os.path.join(examples_dir, "example_client.py"), "w") as f:
        f.write(f'''"""
Example client for the {server_info["name"]} MCP server.
"""

import requests


def main():
    """Run the example client."""
    base_url = "http://localhost:5001"

    # List available tools
    response = requests.get(f"{{base_url}}/mcp/tools")
    tools = response.json()

    print("Available tools:")
    for tool in tools:
        print(f"- {{tool['name']}}: {{tool['description']}}")

    # Execute a tool
    if tools:
        tool = tools[0]
        print(f"\\nExecuting {{tool['name']}}...")

        response = requests.post(
            f"{{base_url}}/mcp/execute",
            json={{
                "name": tool["name"],
                "parameters": {{}}
            }}
        )

        result = response.json()
        print(f"Result: {{result}}")


if __name__ == "__main__":
    main()
''')


def run_mcp_generator(output_dir: str, name: Optional[str] = None) -> None:
    """Run the MCP server generator wizard."""
    # Collect information through interactive prompts
    server_info = collect_server_info()

    # Override name if provided as argument
    if name:
        server_info["name"] = name

    # Create directory structure
    paths = create_directories(output_dir, server_info["name"])

    # Create tool files
    create_tool_files(paths["tools"], server_info["tools"])

    # Create main server files
    create_main_files(paths["root"], server_info["name"], server_info["tools"])

    # Create README
    create_readme(paths["root"], server_info)

    # Create setup.py
    create_setup_py(paths["root"], server_info)

    # Create example files
    create_example_client(paths["examples"], server_info)

    # Display success message
    snake_name = to_snake_case(server_info['name'])
    console.print(Panel(
        f"[bold green]MCP Server '{server_info['name']}' created successfully![/bold green]\n\n"
        f"[bold]Location:[/bold] {paths['root']}\n"
        f"[bold]Tools:[/bold] {', '.join(tool['name'] for tool in server_info['tools'])}\n\n"
        "To get started, navigate to the server directory and run:\n"
        f"```\npip install -e .\n"
        f"python -m {snake_name}.{snake_name}_server\n```"
    ))


if __name__ == "__main__":
    run_mcp_generator("./mcp_servers")
