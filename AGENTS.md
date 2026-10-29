# AGENTS.md — rules for coding agents in this repo

This repo is a verified knowledge base and a set of starter templates for agentic engineering.
Correctness beats breadth. A short page that is right is worth more than a long page that is mostly right.

## Ground rules

1. **Work one phase at a time** from `PLAN.md`. Stop at the end of each phase and report what changed.
2. **Never commit secrets.** Keys live only in `.env` (git-ignored). Use `.env.example` to document variable names, never values.
3. **Never push to `main` directly.** Work on a branch; open a PR or show a diff for review.
4. **Ask before deleting files.** Move unwanted files into a `.trash/` folder next to them instead, and say why.
5. **Do not invent facts, versions, URLs or numbers.** If you cannot verify something, write `TODO(verify): ...` and move on.

## Content rules (docs/)

1. Every page starts from `templates/page.md` and has valid front matter.
2. Every factual claim ends with a source marker like `[src:anthropic-building-effective-agents]`. The id must exist in `sources.yaml`.
3. Write in your own words. Quotes must be under 15 words, in quotation marks, and at most one quote per source per page.
4. Never store the full text of a copyrighted source in the repo. Fetched source text goes in `.cache/` (git-ignored) and is deleted after the ingest run.
5. Prefer primary sources (tier `primary`). Secondary sources may support a claim only when no primary source exists, and the page must say so.
6. Mark judgment and inference explicitly: "In our view…" or "Inference:". Never present opinion as a sourced fact.
7. Every page must pass the `verifier` subagent before it is merged. The verifier must not be the same agent run that wrote the page.
8. Set `last_verified` to the date the verifier passed. Pages older than 120 days are flagged stale by `scripts/validate.py`.

## Starter rules (starters/)

1. Every starter is created from `templates/starter/` with the `new-starter` skill.
2. Every starter has both paths: BYOK code in `src/` and harness instructions in `AGENTS.md` + `SPEC.md`.
3. Provider choice goes through the model adapter (see `PLAN.md` Phase 1). Agent code never imports a provider SDK directly.
4. Every starter ships: max steps, max tokens and max spend per run; tracing; at least 5 eval cases; human approval for irreversible tools.
5. Tests in CI use recorded responses in `fixtures/`. CI must never need a real API key.
6. Pin dependency versions. `scripts/check_versions.py` flags pins that fall behind.

## Commands

```bash
pytest                              # tests (scripts + starters)
python scripts/validate.py          # sources.yaml + docs/ front matter + source ids + staleness
python scripts/check_versions.py    # outdated pins in starters/ (needs network)
python scripts/check_overlap.py PAGE SOURCE_TEXT   # paraphrase check during ingest
```

## Definition of done

- `pytest` passes.
- `python scripts/validate.py` passes.
- New pages have a passing verifier report in the PR description.
- No new file contains a secret, a full copyrighted text, or an unverified claim without `TODO(verify)`.
