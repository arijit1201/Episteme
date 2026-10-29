"""The ModelClient protocol and a wrapper that logs one trace line per call."""
from __future__ import annotations

import logging
import time
from typing import Protocol, Sequence

from .types import Message, Response, ToolSpec

# All agentkit logging goes through this logger: it carries the key-redaction filter.
log = logging.getLogger("agentkit")


class ModelClient(Protocol):
    name: str
    model: str

    def complete(
        self,
        messages: Sequence[Message],
        tools: Sequence[ToolSpec],
        *,
        system: str = "",
        max_output_tokens: int,
    ) -> Response: ...


class TracingClient:
    def __init__(self, inner: ModelClient):
        self._inner = inner
        self.name = inner.name
        self.model = inner.model

    def complete(self, messages, tools, *, system="", max_output_tokens):
        start = time.perf_counter()
        try:
            resp = self._inner.complete(messages, tools, system=system, max_output_tokens=max_output_tokens)
        except Exception as exc:
            log.warning("model call failed provider=%s model=%s error=%s", self.name, self.model, type(exc).__name__)
            raise
        log.info(
            "model call provider=%s model=%s stop=%s in=%d out=%d tool_calls=%d ms=%d",
            self.name, self.model, resp.stop_reason, resp.usage.input_tokens, resp.usage.output_tokens,
            len(resp.tool_calls), (time.perf_counter() - start) * 1000,
        )
        return resp

    def __repr__(self) -> str:
        return f"TracingClient({self.name}:{self.model})"
