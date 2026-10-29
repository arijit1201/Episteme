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

## Open

| Decision | Options | Notes |
|---|---|---|
| Repo visibility | Public / private | Public: GitHub Actions on standard runners is free with no minute cap. Private (Free plan): 2,000 minutes/month included. |
| Docs site generator | MkDocs (Material), Zensical, Docusaurus, Astro Starlight | TODO(verify): check each project's maintenance status before choosing. |
| Model adapter | Own thin adapter / LiteLLM / provider SDKs only | Own adapter keeps the loop visible for learners; LiteLLM covers more providers. |
| Framework for `src/framework/` per starter | OpenAI Agents SDK, Claude Agent SDK, LangGraph, PydanticAI, Google ADK | Pick per starter; verify current version in official docs first. |
| Ingest scheduler | GitHub Actions cron / Claude Code scheduled task | Actions cron keeps it in the repo and needs an API key secret. |
| Monthly API spend cap | e.g. $10 / $25 / $50 | Set in the provider console and in code. |
| Nightly smoke-test model | One cheap model per provider | Check current pricing pages before choosing. |
