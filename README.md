# Agentic Engineering Knowledge Base — Starter Pack

This pack is the seed for a verified, hands-on knowledge base about agentic engineering.
It is designed to be built out with a local coding agent (Claude Code, or any harness that reads `AGENTS.md`).

It has three parts:

1. **Knowledge pages** (`docs/`): short, cited pages on core topics, written in our own words from primary sources.
2. **Starters** (`starters/`): detailed, runnable project templates for common agent types. Each starter works two ways:
   - **BYOK** (bring your own key): run the code with your own provider key.
   - **Harness**: point your coding agent at the starter's `SPEC.md` and `AGENTS.md` and let it build or extend the project.
3. **Ingest engine** (`.claude/`, `scripts/`, `sources.yaml`): a summarizer and a separate verifier that keep pages accurate, plus free CI checks.

## Quick start (with Claude Code)

```bash
unzip agentic-kb-starter.zip
cd agentic-kb-starter
git init && git add . && git commit -m "chore: starter pack"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest                      # checks for the scripts themselves
python scripts/validate.py  # validates sources.yaml and docs/
claude                      # start Claude Code in this folder
```

Then, in Claude Code:

```
Read PLAN.md and DECISIONS.md. Start Phase 1. Stop at the end of the phase and show me what changed.
```

Work one phase at a time. Each phase in `PLAN.md` has acceptance criteria; a phase is done only when they pass.

## What is in this pack

| Path | Purpose |
|---|---|
| `AGENTS.md` | Rules for any coding agent working in this repo. `CLAUDE.md` imports it. |
| `PLAN.md` | Phased build plan with acceptance criteria. |
| `DECISIONS.md` | Decisions already made, and open decisions you still need to make. |
| `sources.yaml` | Registry of primary sources. Every page cites sources by `id` from here. |
| `docs/` | Knowledge pages. Starts with an index only. |
| `starters/` | Empty. Phase 3 creates the first starter from `templates/starter/`. |
| `templates/` | Page template and starter template. |
| `.claude/agents/` | `summarizer` and `verifier` subagents for the ingest workflow. |
| `.claude/skills/` | `ingest-source` and `new-starter` skills. |
| `agentkit/` | Shared model adapter (anthropic, openai, replay), budgets, key redaction. |
| `zensical.toml` | Docs site config. `zensical build --strict` runs in CI. |
| `scripts/` | `validate.py`, `check_versions.py`, `check_overlap.py`. |
| `tests/` | Tests for the scripts. |
| `evals/verifier/` | Planted-error cases used to measure the verifier before trusting it. |
| `.github/workflows/checks.yml` | Free CI: tests, validation, link check, secret scan, version check. |

## Licensing

Copyright 2026 Arijit Bhattacharjee.

- Code: Apache License 2.0 (`LICENSE`).
- Written content in `docs/`: CC BY-SA 4.0 (`LICENSE-CONTENT.md`).

This split exists because some sources we may adapt (for example HumanLayer's 12-Factor Agents) are CC BY-SA 4.0, which requires adaptations to carry the same license.
