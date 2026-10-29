"""Provider mapping tests. They use fake SDK clients shaped like the documented responses; no network."""
from types import SimpleNamespace as NS

from agentkit import Response, ToolCall, ToolSpec, Usage, assistant_message, tool_message, user_message
from agentkit.providers.anthropic import AnthropicClient
from agentkit.providers.openai import OpenAIClient

TOOLS = [ToolSpec("lookup", "Look up a record.", {"type": "object", "properties": {"id": {"type": "string"}}})]


class FakeAnthropic:
    def __init__(self, response):
        self.calls = []
        self.messages = NS(create=self._create)
        self._response = response

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


class FakeOpenAI:
    def __init__(self, response):
        self.calls = []
        self.responses = NS(create=self._create)
        self._response = response

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


def test_anthropic_request_and_response_mapping():
    api_response = NS(
        content=[NS(type="text", text="Checking."), NS(type="tool_use", id="tu_1", name="lookup", input={"id": "7"})],
        stop_reason="tool_use",
        usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=100, cache_creation_input_tokens=None),
    )
    fake = FakeAnthropic(api_response)
    client = AnthropicClient("claude-haiku-5-5", client=fake)

    prior = Response("Checking.", [ToolCall("tu_0", "lookup", {"id": "6"})], "tool_use", Usage())
    msgs = [
        user_message("status?"),
        assistant_message(prior),
        tool_message("tu_0", "boom", is_error=True),
        tool_message("tu_x", "ok"),
    ]
    resp = client.complete(msgs, TOOLS, system="Be terse.", max_output_tokens=300)

    sent = fake.calls[0]
    assert sent["model"] == "claude-haiku-5-5" and sent["max_tokens"] == 300 and sent["system"] == "Be terse."
    assert sent["tools"] == [{"name": "lookup", "description": "Look up a record.", "input_schema": TOOLS[0].input_schema}]
    assert "tool_choice" not in sent
    # Two tool results are grouped into one user message.
    assert sent["messages"][2] == {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "tu_0", "content": "boom", "is_error": True},
            {"type": "tool_result", "tool_use_id": "tu_x", "content": "ok"},
        ],
    }
    assert sent["messages"][1]["content"][1] == {"type": "tool_use", "id": "tu_0", "name": "lookup", "input": {"id": "6"}}

    assert resp.text == "Checking."
    assert resp.tool_calls == [ToolCall("tu_1", "lookup", {"id": "7"})]
    assert resp.stop_reason == "tool_use"
    assert resp.usage == Usage(input_tokens=110, output_tokens=5)  # cached tokens are added back


def test_anthropic_stop_reasons():
    for api, expected in [("end_turn", "end_turn"), ("max_tokens", "max_tokens"), ("refusal", "refusal"), ("pause_turn", "other")]:
        r = NS(content=[NS(type="text", text="x")], stop_reason=api, usage=NS(input_tokens=1, output_tokens=1))
        got = AnthropicClient("m", client=FakeAnthropic(r)).complete([user_message("hi")], [], max_output_tokens=5)
        assert got.stop_reason == expected


def test_openai_request_and_response_mapping():
    api_response = {
        "status": "completed",
        "output": [
            {"type": "reasoning", "id": "rs_1", "summary": []},
            {"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "lookup", "arguments": '{"id": "7"}'},
        ],
        "usage": {"input_tokens": 12, "output_tokens": 8},
    }
    fake = FakeOpenAI(api_response)
    client = OpenAIClient("gpt-6-luna", client=fake)
    resp = client.complete([user_message("status?")], TOOLS, system="Be terse.", max_output_tokens=300)

    sent = fake.calls[0]
    assert sent["model"] == "gpt-6-luna" and sent["instructions"] == "Be terse."
    assert sent["max_output_tokens"] == 300 and sent["store"] is False
    assert sent["input"] == [{"role": "user", "content": "status?"}]
    assert sent["tools"] == [
        {"type": "function", "name": "lookup", "description": "Look up a record.", "parameters": TOOLS[0].input_schema, "strict": False}
    ]
    assert resp.tool_calls == [ToolCall("call_1", "lookup", {"id": "7"})]
    assert resp.stop_reason == "tool_use"
    assert resp.usage == Usage(12, 8)
    assert len(resp.provider_items) == 2

    # Next turn: the raw output items go back verbatim, then the tool output.
    follow = FakeOpenAI({"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": "Open."}]}], "usage": {}})
    client2 = OpenAIClient("gpt-6-luna", client=follow)
    final = client2.complete([user_message("status?"), assistant_message(resp), tool_message("call_1", "status=open")], TOOLS, max_output_tokens=300)
    assert follow.calls[0]["input"][1:] == resp.provider_items + [
        {"type": "function_call_output", "call_id": "call_1", "output": "status=open"}
    ]
    assert final.text == "Open." and final.stop_reason == "end_turn"


def test_openai_incomplete_status():
    r = {"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "output": [], "usage": {}}
    got = OpenAIClient("m", client=FakeOpenAI(r)).complete([user_message("hi")], [], max_output_tokens=5)
    assert got.stop_reason == "max_tokens"
