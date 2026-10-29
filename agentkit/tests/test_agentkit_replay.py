import json

import pytest

from agentkit import (
    FixtureMissing, RecordingClient, ReplayClient, Response, ToolCall, ToolSpec, Usage,
    assistant_message, tool_message, user_message,
)

TOOLS = [ToolSpec("lookup", "Look up a record.", {"type": "object", "properties": {"id": {"type": "string"}}})]
SYSTEM = "You are terse."


class Scripted:
    """A live-client stand-in that returns queued responses."""

    name, model = "scripted", "m1"

    def __init__(self, *responses):
        self.responses = list(responses)

    def complete(self, messages, tools, *, system="", max_output_tokens):
        return self.responses.pop(0)


def _tool_turn():
    return Response("", [ToolCall("c1", "lookup", {"id": "7"})], "tool_use", Usage(10, 5))


def _final_turn():
    return Response("Record 7 is open.", [], "end_turn", Usage(20, 6))


def test_record_then_replay_round_trip(tmp_path):
    fixture = tmp_path / "fixtures" / "run.jsonl"
    rec = RecordingClient(Scripted(_tool_turn(), _final_turn()), fixture)

    msgs = [user_message("status of 7?")]
    first = rec.complete(msgs, TOOLS, system=SYSTEM, max_output_tokens=200)
    msgs += [assistant_message(first), tool_message("c1", "status=open")]
    second = rec.complete(msgs, TOOLS, system=SYSTEM, max_output_tokens=200)

    replay = ReplayClient(fixture)
    msgs2 = [user_message("status of 7?")]
    r1 = replay.complete(msgs2, TOOLS, system=SYSTEM, max_output_tokens=200)
    assert r1 == first
    msgs2 += [assistant_message(r1), tool_message("c1", "status=open")]
    assert replay.complete(msgs2, TOOLS, system=SYSTEM, max_output_tokens=200) == second


def test_replay_miss_names_the_fixture(tmp_path):
    replay = ReplayClient(tmp_path / "none.jsonl")
    with pytest.raises(FixtureMissing, match="none.jsonl"):
        replay.complete([user_message("hi")], [], max_output_tokens=10)


def test_replay_repeats_last_response(tmp_path):
    fixture = tmp_path / "r.jsonl"
    rec = RecordingClient(Scripted(_final_turn()), fixture)
    rec.complete([user_message("hi")], [], max_output_tokens=10)
    replay = ReplayClient(fixture)
    assert replay.complete([user_message("hi")], [], max_output_tokens=10).text == "Record 7 is open."
    assert replay.complete([user_message("hi")], [], max_output_tokens=10).text == "Record 7 is open."


def test_fixture_lines_are_valid_json(tmp_path):
    fixture = tmp_path / "r.jsonl"
    RecordingClient(Scripted(_final_turn()), fixture).complete([user_message("hi")], [], max_output_tokens=10)
    rec = json.loads(fixture.read_text(encoding="utf-8").splitlines()[0])
    assert set(rec) == {"request_hash", "request", "response"}
