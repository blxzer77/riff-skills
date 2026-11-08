"""Minimal model client used by this service.

`ModelClient.complete` sends one request and returns the model's reply. When `tools`
is given, the reply may contain tool calls the caller must execute and answer.

Production wires a real provider in `make_client()`. Tests pass a fake client.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class Reply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class Message:
    role: str  # "system", "user", "assistant", or "tool"
    content: str
    tool_name: str | None = None


class ModelClient:
    def complete(self, messages: list[Message], tools: list[dict] | None = None,
                 max_tokens: int = 1024) -> Reply:
        raise NotImplementedError


def make_client() -> ModelClient:
    raise RuntimeError("configure a provider in production")
