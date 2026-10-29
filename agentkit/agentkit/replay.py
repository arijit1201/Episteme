"""Replay recorded responses (CI) and record new ones from a live client."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .client import ModelClient
from .redact import redact
from .types import Message, Response, ToolSpec


class FixtureMissing(Exception):
    pass


def _request(messages: Sequence[Message], tools: Sequence[ToolSpec], system: str, max_output_tokens: int) -> dict:
    return {
        "system": system,
        "messages": list(messages),
        "tools": [asdict(t) for t in tools],
        "max_output_tokens": max_output_tokens,
    }


def request_hash(messages, tools, system: str, max_output_tokens: int) -> str:
    canonical = json.dumps(_request(messages, tools, system, max_output_tokens), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ReplayClient:
    """Serves responses from a JSONL fixture file, matched by request hash.

    Repeated identical requests get their recorded responses in order; the last one repeats.
    """

    name = "replay"

    def __init__(self, fixture_file: str | Path, model: str = "replay"):
        self.model = model
        self.fixture_file = Path(fixture_file)
        self._queues: dict[str, deque[dict]] = defaultdict(deque)
        if self.fixture_file.exists():
            for line in self.fixture_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self._queues[rec["request_hash"]].append(rec["response"])

    def complete(self, messages, tools, *, system="", max_output_tokens) -> Response:
        key = request_hash(messages, tools, system, max_output_tokens)
        queue = self._queues.get(key)
        if not queue:
            raise FixtureMissing(f"no recorded response for request {key[:12]} in {self.fixture_file}")
        data = queue.popleft() if len(queue) > 1 else queue[0]
        return Response.from_dict(data)

    def __repr__(self) -> str:
        return f"ReplayClient({self.fixture_file})"


class RecordingClient:
    """Wraps a live client and appends each request/response pair to a fixture file."""

    def __init__(self, inner: ModelClient, fixture_file: str | Path):
        self._inner = inner
        self.name = inner.name
        self.model = inner.model
        self.fixture_file = Path(fixture_file)

    def complete(self, messages, tools, *, system="", max_output_tokens) -> Response:
        resp = self._inner.complete(messages, tools, system=system, max_output_tokens=max_output_tokens)
        record = {
            "request_hash": request_hash(messages, tools, system, max_output_tokens),
            "request": _request(messages, tools, system, max_output_tokens),
            "response": resp.to_dict(),
        }
        self.fixture_file.parent.mkdir(parents=True, exist_ok=True)
        with self.fixture_file.open("a", encoding="utf-8") as f:
            f.write(redact(json.dumps(record, sort_keys=True)) + "\n")
        return resp

    def __repr__(self) -> str:
        return f"RecordingClient({self.name}:{self.model} -> {self.fixture_file})"
