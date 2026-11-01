"""Tool registry for the on-call agent.

A tool is a JSON-schema definition the model sees plus a handler. The agent loop in
`assistant/agent.py` sends `definitions()` to the model, runs `call(name, arguments)`
for each tool call, and returns the handler's string result to the model.
"""

from __future__ import annotations

from typing import Callable

_TOOLS: dict[str, tuple[dict, Callable[[dict], str]]] = {}


def register(definition: dict, handler: Callable[[dict], str]) -> None:
    _TOOLS[definition["name"]] = (definition, handler)


def definitions() -> list[dict]:
    return [definition for definition, _ in _TOOLS.values()]


def call(name: str, arguments: dict) -> str:
    _, handler = _TOOLS[name]
    return handler(arguments)
