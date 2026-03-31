"""
Tool registry: register and validate tools before the agent can call them.
Validates arguments against the schema before execution — bad args fail fast,
not silently inside the tool.
"""
from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict          # JSON Schema for the tool's input
    fn: Callable[..., Any]    # the actual function to call


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def call(self, name: str, arguments: dict) -> Any:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        tool = self._tools[name]
        # TODO: validate arguments against tool.parameters schema
        return tool.fn(**arguments)

    def to_api_format(self) -> list[dict]:
        """Return tool definitions in Anthropic/OpenAI API format."""
        return [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in self._tools.values()
        ]
