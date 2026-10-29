"""OpenAI Responses API provider (OpenAI recommends it for new projects).

Shapes checked against developers.openai.com docs (function calling, migrate-to-responses) on 2026-10-30.
Runs stateless (store=False): the assistant's raw output items are re-sent verbatim each turn.
"""
from __future__ import annotations

import json
from typing import Any, Sequence

from ..types import Message, Response, ToolCall, ToolSpec, Usage


def _dump(obj: Any) -> dict[str, Any]:
    """SDK objects are pydantic models; tests pass plain dicts."""
    return obj.model_dump(exclude_none=True) if hasattr(obj, "model_dump") else dict(obj)


def to_api_input(messages: Sequence[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in messages:
        role = m["role"]
        if role == "user":
            out.append({"role": "user", "content": m["content"]})
        elif role == "assistant":
            if m.get("provider_items"):
                out.extend(m["provider_items"])
                continue
            if m.get("text"):
                out.append({"role": "assistant", "content": m["text"]})
            for c in m.get("tool_calls", []):
                out.append(
                    {"type": "function_call", "call_id": c["id"], "name": c["name"], "arguments": json.dumps(c["arguments"])}
                )
        elif role == "tool":
            # The Responses API has no error flag on tool output, so mark errors in the text.
            prefix = "Error: " if m.get("is_error") else ""
            out.append({"type": "function_call_output", "call_id": m["tool_call_id"], "output": prefix + m["content"]})
        else:
            raise ValueError(f"unknown message role: {role!r}")
    return out


def from_api_response(resp: Any) -> Response:
    d = _dump(resp)
    items = [_dump(i) for i in d.get("output", [])]
    text_parts: list[str] = []
    calls: list[ToolCall] = []
    for item in items:
        if item.get("type") == "message":
            text_parts += [c["text"] for c in item.get("content", []) if c.get("type") == "output_text"]
        elif item.get("type") == "function_call":
            calls.append(ToolCall(id=item["call_id"], name=item["name"], arguments=json.loads(item["arguments"] or "{}")))
    if d.get("status") == "incomplete":
        reason = (d.get("incomplete_details") or {}).get("reason")
        stop = {"max_output_tokens": "max_tokens", "content_filter": "refusal"}.get(reason, "other")
    elif d.get("status") == "completed":
        stop = "tool_use" if calls else "end_turn"
    else:
        stop = "other"
    u = d.get("usage") or {}
    return Response(
        text="".join(text_parts),
        tool_calls=calls,
        stop_reason=stop,
        usage=Usage(input_tokens=u.get("input_tokens", 0), output_tokens=u.get("output_tokens", 0)),
        provider_items=items,
    )


class OpenAIClient:
    name = "openai"

    def __init__(self, model: str, client: Any = None):
        if client is None:
            import openai  # lazy: replay needs no SDK. Reads OPENAI_API_KEY itself.

            client = openai.OpenAI()
        self.model = model
        self._client = client

    def complete(self, messages, tools: Sequence[ToolSpec], *, system="", max_output_tokens) -> Response:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": to_api_input(messages),
            "max_output_tokens": max_output_tokens,
            "store": False,
        }
        if system:
            kwargs["instructions"] = system
        if tools:
            # strict=False: our schemas are not guaranteed to meet strict mode's rules.
            kwargs["tools"] = [
                {"type": "function", "name": t.name, "description": t.description, "parameters": t.input_schema, "strict": False}
                for t in tools
            ]
        return from_api_response(self._client.responses.create(**kwargs))

    def __repr__(self) -> str:
        return f"OpenAIClient({self.model})"
