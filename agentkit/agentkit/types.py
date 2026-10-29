"""Provider-neutral data types. Messages are plain dicts so they serialize to fixtures unchanged."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

StopReason = Literal["end_turn", "tool_use", "max_tokens", "refusal", "other"]


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class Response:
    text: str
    tool_calls: list[ToolCall]
    stop_reason: StopReason
    usage: Usage
    # Raw provider output items, re-sent verbatim on the next turn when the provider needs them.
    provider_items: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Response":
        return cls(
            text=d["text"],
            tool_calls=[ToolCall(**c) for c in d["tool_calls"]],
            stop_reason=d["stop_reason"],
            usage=Usage(**d["usage"]),
            provider_items=d.get("provider_items", []),
        )


Message = dict[str, Any]


def user_message(text: str) -> Message:
    return {"role": "user", "content": text}


def assistant_message(resp: Response) -> Message:
    return {
        "role": "assistant",
        "text": resp.text,
        "tool_calls": [asdict(c) for c in resp.tool_calls],
        "provider_items": resp.provider_items,
    }


def tool_message(call_id: str, content: str, is_error: bool = False) -> Message:
    return {"role": "tool", "tool_call_id": call_id, "content": content, "is_error": is_error}
