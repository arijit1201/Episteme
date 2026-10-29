# DECISIONS.md

Record each decision with the date and the reason. Revisit a decision only when new evidence appears.

## Made

| Date | Decision | Reason |
|---|---|---|
| 2026-10-29 | Start a fresh repo; do not fork `ankurkumarz/agentic-ai-knowledge-base`. | Its content is LLM-ingested without a verification gate; spot checks found factual errors. Auditing 600+ commits costs more than starting clean. Individual pages may be copied later with attribution after verification (it is Apache-2.0). |
| 2026-10-29 | Python first for starters and scripts. | Widest SDK and framework coverage. TypeScript versions can follow. |
| 2026-10-29 | Code under Apache-2.0; content under CC BY-SA 4.0. | Allows adapting CC BY-SA sources such as 12-Factor Agents. |
| 2026-10-29 | Primary sources first; secondary only when no primary exists. | The main failure of existing knowledge bases is drift from primary sources. |
| 2026-10-29 | Summarizer and verifier are separate agents. | A model checking its own draft shares its blind spots. |
| 2026-10-29 | CI uses recorded responses; no API key in PR checks. | Free, deterministic, and safe for public PRs. |
| 2026-10-29 | No standalone labs for now; starters carry the runnable code. | Scope control. Starters are tested in CI instead. |
| 2026-10-30 | Repo is public (github.com/arijit1201/Episteme). | Free unlimited GitHub Actions minutes on standard runners. |
| 2026-10-30 | Own thin model adapter (`agentkit/`), official `anthropic` and `openai` SDKs only. | Keeps the loop and provider shapes visible for learners; avoids a large dependency. LiteLLM stays an option if provider coverage becomes a need. |
| 2026-10-30 | Docs site: Zensical, strict build in CI only; `.readthedocs.yaml` included but hosting not connected. | MkDocs 1.x is unmaintained and Material for MkDocs is in maintenance mode (EOL 2027-05-05, per squidfunk's posts). Zensical is its Python successor, MIT, alpha (0.0.73): acceptable because `docs/` is plain Markdown and a switch is cheap. Read the Docs hosts a build, it is not a generator. |

## Open

| Decision | Options | Notes |
|---|---|---|
| Framework for `src/framework/` per starter | OpenAI Agents SDK, Claude Agent SDK, LangGraph, PydanticAI, Google ADK | Pick per starter; verify current version in official docs first. |
| Ingest scheduler | GitHub Actions cron / Claude Code scheduled task | Actions cron keeps it in the repo and needs an API key secret. |
| Monthly API spend cap | e.g. $10 / $25 / $50 | Set in the provider console and in code. |
| Nightly smoke-test model | One cheap model per provider | Check current pricing pages before choosing. |
