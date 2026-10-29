# agentkit

Small model adapter shared by every starter. Agent code talks to `ModelClient`; it never imports a provider SDK.

- Providers: `anthropic` (Messages API), `openai` (Responses API), `replay` (recorded responses, used in CI).
- `RecordingClient` wraps a live provider and saves responses to `fixtures/*.jsonl` for later replay.
- `Budget` stops a run at the step, token or spend limit.
- Provider and model come from the starter's `config.yaml`; `AGENTKIT_PROVIDER` and `AGENTKIT_MODEL` override them. Keys come only from `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`.

```python
from agentkit import load_config, make_client, Budget, user_message

config = load_config("config.yaml")
client = make_client(config, fixture="my-test")
budget = Budget.from_config(config)

budget.start_step()
resp = client.complete([user_message("hi")], [], system="Be brief.", max_output_tokens=500)
budget.charge(resp.usage)
```

Notes:

- `temperature` in `config.yaml` is not forwarded yet: some current models may reject it. TODO(verify).
- OpenAI calls use the Responses API with `store=False`. Reasoning models in stateless mode may need `include=["reasoning.encrypted_content"]`. TODO(verify) before using one.
