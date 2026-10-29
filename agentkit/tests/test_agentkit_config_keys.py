import json
import logging

import pytest

from agentkit import (
    ConfigError, RecordingClient, Response, TracingClient, Usage, load_config, make_client, redact, user_message,
)
from agentkit.providers.anthropic import AnthropicClient
from agentkit.providers.openai import OpenAIClient

SECRET_A = "sk-ant-api03-SECRETSECRETSECRET1234"
SECRET_O = "sk-proj-OPENAISECRETVALUE5678"

CONFIG = """
model:
  provider: {provider}
  name: {name}
  price_per_mtok: {{input: 1.0, output: 5.0}}
limits: {{max_steps: 5, max_tokens: 1000, max_spend_usd: 0.1}}
fixtures: {{dir: fixtures, mode: {mode}}}
"""


def write_config(tmp_path, provider="replay", name="null", mode="replay"):
    p = tmp_path / "config.yaml"
    p.write_text(CONFIG.format(provider=provider, name=name, mode=mode), encoding="utf-8")
    return p


class FakeMessages:
    def create(self, **kwargs):
        from types import SimpleNamespace as NS

        return NS(content=[NS(type="text", text=f"echo {kwargs['messages'][0]['content']}")], stop_reason="end_turn",
                  usage=NS(input_tokens=3, output_tokens=2))


def test_provider_swap_is_config_only(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET_A)  # the real SDKs read os.environ
    monkeypatch.setenv("OPENAI_API_KEY", SECRET_O)
    env = {"ANTHROPIC_API_KEY": SECRET_A, "OPENAI_API_KEY": SECRET_O}
    kinds = {}
    for provider in ("replay", "anthropic", "openai"):
        cfg = load_config(write_config(tmp_path, provider=provider, name="some-model"), env={})
        kinds[provider] = make_client(cfg, env=env)
    assert [type(c).__name__ for c in kinds.values()] == ["TracingClient"] * 3
    assert [c.name for c in kinds.values()] == ["replay", "anthropic", "openai"]


def test_env_overrides_provider_and_model(tmp_path):
    cfg = load_config(write_config(tmp_path), env={"AGENTKIT_PROVIDER": "openai", "AGENTKIT_MODEL": "m2"})
    assert (cfg.provider, cfg.model) == ("openai", "m2")


def test_missing_key_error_names_variable_not_value(tmp_path):
    cfg = load_config(write_config(tmp_path, provider="anthropic", name="m"), env={})
    with pytest.raises(ConfigError, match="ANTHROPIC_API_KEY"):
        make_client(cfg, env={})


def test_live_provider_requires_prices(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("model: {provider: openai, name: m}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="price_per_mtok"):
        load_config(p, env={})


def test_record_mode_wraps_live_client(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET_A)
    cfg = load_config(write_config(tmp_path, provider="anthropic", name="m", mode="record"), env={})
    client = make_client(cfg, env={"ANTHROPIC_API_KEY": SECRET_A})
    assert isinstance(client, TracingClient) and isinstance(client._inner, RecordingClient)


def test_keys_never_appear_in_logs_fixtures_errors_or_reprs(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET_A)
    monkeypatch.setenv("OPENAI_API_KEY", SECRET_O)
    cfg = load_config(write_config(tmp_path, provider="anthropic", name="m", mode="record"), env={})
    fixture = cfg.fixtures_dir / "run.jsonl"

    live = AnthropicClient("m", client=type("C", (), {"messages": FakeMessages()})())
    client = TracingClient(RecordingClient(live, fixture))
    with caplog.at_level(logging.DEBUG, logger="agentkit"):
        # A user turn that echoes a key must not reach the fixture or the log.
        resp = client.complete([user_message(f"my key is {SECRET_A}")], [], max_output_tokens=10)
        logging.getLogger("agentkit").info("debug dump: key=%s", SECRET_O)  # even a careless log line is masked

    assert isinstance(resp, Response) and resp.usage == Usage(3, 2)
    blob = "\n".join([caplog.text, fixture.read_text(encoding="utf-8"), repr(cfg), repr(client), repr(live)])
    for secret in (SECRET_A, SECRET_O):
        assert secret not in blob
    assert "[REDACTED]" in caplog.text
    assert json.loads(fixture.read_text(encoding="utf-8").splitlines()[0])["response"]["text"]
    assert "model call provider=anthropic" in caplog.text  # trace line was written

    with pytest.raises(ConfigError) as exc:
        make_client(cfg, env={})
    assert SECRET_A not in str(exc.value)


def test_redact_masks_env_values_and_key_shapes():
    assert redact(f"a {SECRET_A} b", env={"ANTHROPIC_API_KEY": SECRET_A}) == "a [REDACTED] b"
    assert redact("x sk-abcdefghijkl y", env={}) == "x [REDACTED] y"
