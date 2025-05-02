"""
Tool Parser for handling LLM responses.

This module provides functionality to parse LLM responses and extract tool calls.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple

from loguru import logger


class ToolCall:
    """Represents a parsed tool call from an LLM response."""

    def __init__(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        full_text: str,
        start_pos: int,
        end_pos: int
    ):
        """
        Initialize a tool call.

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            full_text: The complete text of the tool call
            start_pos: Start position in the original text
            end_pos: End position in the original text
        """
        self.tool_name = tool_name
        self.parameters = parameters
        self.full_text = full_text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.result: Optional[Dict[str, Any]] = None

    def set_result(self, result: Dict[str, Any]) -> None:
        """
        Set the result of the tool call.

        Args:
            result: The result to set
        """
        self.result = result

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool call to a dictionary.

        Returns:
            A dictionary representation of the tool call
        """
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "full_text": self.full_text,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "result": self.result
        }


class ToolParser:
    """Parser for extracting tool calls from LLM responses."""

    # Regex patterns for different tool call formats
    _JSON_PATTERN = r'```json\s*({[\s\S]*?})\s*```'
    _FUNCTION_PATTERN = r'([a-zA-Z0-9_]+)\(([^)]*)\)'
    _TOOL_CALL_PATTERN = r'<tool:([a-zA-Z0-9_]+)>\s*({[\s\S]*?})\s*</tool>'

    @classmethod
    def parse(cls, text: str) -> Tuple[str, List[ToolCall]]:
        """
        Parse text to extract tool calls.

        Args:
            text: The text to parse

        Returns:
            A tuple of (cleaned_text, tool_calls)
        """
        tool_calls = []

        # Try to find JSON blocks
        json_calls = cls._parse_json_blocks(text)
        tool_calls.extend(json_calls)

        # Try to find function-style calls
        function_calls = cls._parse_function_calls(text)
        tool_calls.extend(function_calls)

        # Try to find explicit tool calls
        explicit_calls = cls._parse_explicit_tool_calls(text)
        tool_calls.extend(explicit_calls)

        # Sort tool calls by position
        tool_calls.sort(key=lambda x: x.start_pos)

        # Remove tool calls from text
        cleaned_text = cls._remove_tool_calls(text, tool_calls)

        return cleaned_text, tool_calls

    @classmethod
    def _parse_json_blocks(cls, text: str) -> List[ToolCall]:
        """
        Parse JSON blocks from text.

        Args:
            text: The text to parse

        Returns:
            A list of ToolCall objects
        """
        tool_calls = []

        for match in re.finditer(cls._JSON_PATTERN, text):
            try:
                json_str = match.group(1)
                data = json.loads(json_str)

                # Check if this looks like a tool call
                if "tool" in data and "parameters" in data:
                    tool_calls.append(ToolCall(
                        tool_name=data["tool"],
                        parameters=data["parameters"],
                        full_text=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end()
                    ))
                elif "function" in data and "arguments" in data:
                    # OpenAI-style function call
                    arguments = data["arguments"]
                    if isinstance(arguments, str):
                        try:
                            parameters = json.loads(arguments)
                        except json.JSONDecodeError:
                            parameters = {"text": arguments}
                    else:
                        parameters = arguments

                    tool_calls.append(ToolCall(
                        tool_name=data["function"],
                        parameters=parameters,
                        full_text=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end()
                    ))
            except Exception as e:
                logger.warning(f"Failed to parse JSON block: {e}")

        return tool_calls

    @classmethod
    def _parse_function_calls(cls, text: str) -> List[ToolCall]:
        """
        Parse function-style calls from text.

        Args:
            text: The text to parse

        Returns:
            A list of ToolCall objects
        """
        tool_calls = []

        for match in re.finditer(cls._FUNCTION_PATTERN, text):
            try:
                function_name = match.group(1)
                args_str = match.group(2).strip()

                # Try to parse arguments
                params = {}
                if args_str:
                    # Check if args are JSON
                    if args_str.startswith('{') and args_str.endswith('}'):
                        try:
                            params = json.loads(args_str)
                        except json.JSONDecodeError:
                            # Not valid JSON, try to parse as key=value pairs
                            pass

                    # If not JSON or JSON parsing failed, try key=value format
                    if not params and '=' in args_str:
                        # Parse as key=value pairs
                        for arg in args_str.split(','):
                            arg = arg.strip()
                            if '=' in arg:
                                key, value = arg.split('=', 1)
                                key = key.strip()
                                value = value.strip()

                                # Remove quotes if present
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]

                                params[key] = cls._parse_value(value)
                    elif not params:
                        # Simple comma-separated values
                        args = [arg.strip() for arg in args_str.split(',')]
                        for i, arg in enumerate(args):
                            params[f"arg{i+1}"] = cls._parse_value(arg)

                tool_calls.append(ToolCall(
                    tool_name=function_name,
                    parameters=params,
                    full_text=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
            except Exception as e:
                logger.warning(f"Failed to parse function call: {e}")

        return tool_calls

    @classmethod
    def _parse_explicit_tool_calls(cls, text: str) -> List[ToolCall]:
        """
        Parse explicit tool calls from text.

        Args:
            text: The text to parse

        Returns:
            A list of ToolCall objects
        """
        tool_calls = []

        for match in re.finditer(cls._TOOL_CALL_PATTERN, text):
            try:
                tool_name = match.group(1)
                params_str = match.group(2)

                # Parse parameters
                params = {}
                try:
                    params = json.loads(params_str)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse parameters for tool {tool_name}")

                tool_calls.append(ToolCall(
                    tool_name=tool_name,
                    parameters=params,
                    full_text=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
            except Exception as e:
                logger.warning(f"Failed to parse explicit tool call: {e}")

        return tool_calls

    @classmethod
    def _parse_value(cls, value: str) -> Any:
        """
        Parse a string value into an appropriate type.

        Args:
            value: The string value to parse

        Returns:
            The parsed value
        """
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Try to parse as boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        if value.lower() == 'null' or value.lower() == 'none':
            return None

        # Return as string
        return value

    @classmethod
    def _remove_tool_calls(cls, text: str, tool_calls: List[ToolCall]) -> str:
        """
        Remove tool calls from text.

        Args:
            text: The original text
            tool_calls: The tool calls to remove

        Returns:
            The text with tool calls removed
        """
        # Sort tool calls in reverse order to avoid position changes
        sorted_calls = sorted(tool_calls, key=lambda x: x.start_pos, reverse=True)

        result = text
        for call in sorted_calls:
            result = result[:call.start_pos] + result[call.end_pos:]

        return result.strip()

    @classmethod
    def replace_tool_calls_with_results(cls, text: str, tool_calls: List[ToolCall]) -> str:
        """
        Replace tool calls in text with their results.

        Args:
            text: The original text
            tool_calls: The tool calls with results

        Returns:
            The text with tool calls replaced by results
        """
        # Sort tool calls in reverse order to avoid position changes
        sorted_calls = sorted(tool_calls, key=lambda x: x.start_pos, reverse=True)

        result = text
        for call in sorted_calls:
            if call.result:
                result_text = f"**Result from {call.tool_name}:** "
                result_text += f"{json.dumps(call.result, indent=2)}"
                result = result[:call.start_pos] + result_text + result[call.end_pos:]

        return result
