"""Anthropic Messages API provider.

Shapes checked against platform.claude.com docs (tool use, stop reasons, prompt caching) on 2026-10-30.
No forced tool_choice: current models reject `any` and `tool`.
"""
from __future__ import annotations

from typing import Any, Sequence

from ..types import Message, Response, ToolCall, ToolSpec, Usage

_STOP = {
    "end_turn": "end_turn",
    "stop_sequence": "end_turn",
    "tool_use": "tool_use",
    "max_tokens": "max_tokens",
    "refusal": "refusal",
}


def to_api_messages(messages: Sequence[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    def flush() -> None:
        if results:  # tool_result blocks must be one user message, right after the tool_use message
            out.append({"role": "user", "content": list(results)})
            results.clear()

    for m in messages:
        role = m["role"]
        if role == "tool":
            block: dict[str, Any] = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}
            if m.get("is_error"):
                block["is_error"] = True
            results.append(block)
            continue
        flush()
        if role == "user":
            out.append({"role": "user", "content": m["content"]})
        elif role == "assistant":
            blocks: list[dict[str, Any]] = []
            if m.get("text"):
                blocks.append({"type": "text", "text": m["text"]})
            for c in m.get("tool_calls", []):
                blocks.append({"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["arguments"]})
            out.append({"role": "assistant", "content": blocks})
        else:
            raise ValueError(f"unknown message role: {role!r}")
    flush()
    return out


def from_api_response(resp: Any) -> Response:
    text_parts: list[str] = []
    calls: list[ToolCall] = []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            calls.append(ToolCall(id=block.id, name=block.name, arguments=dict(block.input)))
    u = resp.usage
    # input_tokens excludes cached tokens, so add them back for the real total.
    input_total = (u.input_tokens or 0) + (getattr(u, "cache_read_input_tokens", 0) or 0) + (
        getattr(u, "cache_creation_input_tokens", 0) or 0
    )
    return Response(
        text="".join(text_parts),
        tool_calls=calls,
        stop_reason=_STOP.get(resp.stop_reason, "other"),
        usage=Usage(input_tokens=input_total, output_tokens=u.output_tokens or 0),
    )


class AnthropicClient:
    name = "anthropic"

    def __init__(self, model: str, client: Any = None):
        if client is None:
            import anthropic  # lazy: replay needs no SDK. Reads ANTHROPIC_API_KEY itself.

            client = anthropic.Anthropic()
        self.model = model
        self._client = client

    def complete(self, messages, tools: Sequence[ToolSpec], *, system="", max_output_tokens) -> Response:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_output_tokens,
            "messages": to_api_messages(messages),
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools
            ]
        return from_api_response(self._client.messages.create(**kwargs))

    def __repr__(self) -> str:
        return f"AnthropicClient({self.model})"
