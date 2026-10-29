# <starter-name>

<One sentence: what this agent does and for whom.>

## When to use this

- <situation where this design fits>

## When NOT to use this

- <situation where a simpler workflow, a single LLM call, or plain code is better>

## Architecture

<Diagram (Mermaid) and 3–5 sentences: the loop, the tools, where state lives, where a human approves.>

## Run it with your own key (BYOK)

```bash
cd starters/<starter-name>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add the key for the provider you choose
# edit config.yaml: provider, model, limits
python -m src.main "<example task>"
```

Run the tests without any key (uses recorded responses):

```bash
pytest
```

## Build or extend it with your harness

Open this folder in your coding agent and say:

```
Read AGENTS.md and SPEC.md. Implement (or extend) the agent so every acceptance test in SPEC.md passes.
```

## Limits and safety defaults

| Setting | Default | Where |
|---|---|---|
| Max steps per run | <n> | `config.yaml` |
| Max tokens per run | <n> | `config.yaml` |
| Max spend per run (USD) | <n> | `config.yaml` |
| Tools needing human approval | <list> | `config.yaml` |

## Evals

<How to run them, what they measure, current pass rate.>

## Sources

<Links to the knowledge-base pages and primary sources this starter is based on.>
