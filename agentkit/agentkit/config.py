"""Load a starter's config.yaml and build the model client from it.

Provider and model come from config.yaml; AGENTKIT_PROVIDER and AGENTKIT_MODEL override them.
Keys are never in config: the SDKs read ANTHROPIC_API_KEY / OPENAI_API_KEY from the environment.

fixtures.mode only matters for live providers: `record` also saves each response to
<fixtures.dir>/<fixture>.jsonl. Provider `replay` always replays from that file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml

from .client import ModelClient, TracingClient
from .replay import RecordingClient, ReplayClient

PROVIDERS = ("replay", "anthropic", "openai")
KEY_VARS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    provider: str
    model: str | None
    max_steps: int
    max_tokens: int
    max_spend_usd: float
    input_price_per_mtok: float | None
    output_price_per_mtok: float | None
    fixtures_dir: Path
    fixtures_mode: str


def load_config(path: str | Path, env: Mapping[str, str] | None = None) -> Config:
    env = os.environ if env is None else env
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    model = data.get("model") or {}
    limits = data.get("limits") or {}
    price = model.get("price_per_mtok") or {}
    fixtures = data.get("fixtures") or {}

    provider = env.get("AGENTKIT_PROVIDER") or model.get("provider") or "replay"
    if provider not in PROVIDERS:
        raise ConfigError(f"provider {provider!r} is not one of {PROVIDERS}")
    mode = fixtures.get("mode", "replay")
    if mode not in ("replay", "record"):
        raise ConfigError(f"fixtures.mode {mode!r} is not 'replay' or 'record'")
    if provider != "replay" and (price.get("input") is None or price.get("output") is None):
        raise ConfigError("model.price_per_mtok.input and .output are required for live providers (spend cap needs them)")

    return Config(
        provider=provider,
        model=env.get("AGENTKIT_MODEL") or model.get("name"),
        max_steps=int(limits.get("max_steps", 15)),
        max_tokens=int(limits.get("max_tokens", 50000)),
        max_spend_usd=float(limits.get("max_spend_usd", 0.50)),
        input_price_per_mtok=price.get("input"),
        output_price_per_mtok=price.get("output"),
        fixtures_dir=path.parent / fixtures.get("dir", "fixtures"),
        fixtures_mode=mode,
    )


def make_client(config: Config, *, fixture: str = "default", env: Mapping[str, str] | None = None) -> ModelClient:
    env = os.environ if env is None else env
    fixture_file = config.fixtures_dir / f"{fixture}.jsonl"

    if config.provider == "replay":
        return TracingClient(ReplayClient(fixture_file, model=config.model or "replay"))

    if not config.model:
        raise ConfigError("model.name (or AGENTKIT_MODEL) is required for live providers")
    key_var = KEY_VARS[config.provider]
    if not env.get(key_var):
        raise ConfigError(f"{key_var} is not set; export it or put it in .env")

    if config.provider == "anthropic":
        from .providers.anthropic import AnthropicClient

        client: ModelClient = AnthropicClient(config.model)
    else:
        from .providers.openai import OpenAIClient

        client = OpenAIClient(config.model)
    if config.fixtures_mode == "record":
        client = RecordingClient(client, fixture_file)
    return TracingClient(client)
