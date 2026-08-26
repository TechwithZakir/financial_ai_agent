from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class RiskLevel(str, Enum):
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"
    PROHIBITED = "Prohibited"


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    function: Callable[..., Any]
    input_schema: dict[str, Any]
    risk: RiskLevel
    roles: tuple[str, ...]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, definition: RegisteredTool) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Tool already registered: {definition.name}")
        self._tools[definition.name] = definition

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def schemas(self, roles: set[str]) -> list[dict[str, Any]]:
        return [
            {"name": item.name, "description": item.description, "parameters": item.input_schema}
            for item in self._tools.values()
            if not item.roles or roles.intersection(item.roles)
        ]


registry = ToolRegistry()


def tool(*, name: str, description: str, schema: dict, risk=RiskLevel.GREEN, roles=()):
    def decorator(function):
        registry.register(RegisteredTool(name, description, function, schema, risk, tuple(roles)))
        return function
    return decorator

