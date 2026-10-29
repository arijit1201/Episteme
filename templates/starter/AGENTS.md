# AGENTS.md — <starter-name>

Instructions for a coding agent building or extending this starter.

## Task

Implement or extend the agent described in `SPEC.md` until every acceptance test passes.

## Rules

1. Read `SPEC.md` fully before writing code.
2. Call models only through `agentkit` (the shared adapter). Never import a provider SDK in agent code.
3. Never read, print, log or commit API keys. Keys come only from environment variables.
4. Every new behaviour gets a test that runs on recorded responses in `fixtures/`. Record new fixtures with `record` mode only when the user has provided a key and agreed to the cost.
5. Tools with side effects must go through the approval step. Do not add a bypass.
6. Keep the raw loop in `src/` readable: it is a teaching reference. Put framework code in `src/framework/` only.
7. Pin every dependency in `requirements.txt`.

## Commands

```bash
pytest                       # all tests, no key needed
python -m src.main "<task>"  # live run, needs a key in .env
```

## Done means

- `pytest` passes with no API key set.
- `SPEC.md` acceptance tests all pass.
- `README.md` limits table matches `config.yaml`.
