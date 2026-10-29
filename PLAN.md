# PLAN.md — phased build plan

Work one phase at a time. Each phase lists deliverables and acceptance criteria.
A phase is done only when every acceptance criterion passes. Stop after each phase for review.

---

## Phase 1 — Skeleton

**Goal:** the repo checks itself, sources are real, and starters have a provider-neutral way to call models.

### Deliverables

1. **Source check.** Visit every `url` in `sources.yaml`. Fix wrong URLs. Set `status: verified` and `last_verified` for each one that resolves to the expected document. Remove nothing; mark dead sources `status: dead`.
2. **License.** `LICENSE` already holds the full Apache License 2.0 text. Add a copyright line to `README.md` with your name and year.
3. **CI green.** Push to a GitHub repo and confirm `.github/workflows/checks.yml` passes.
4. **Model adapter** in `agentkit/` (a small Python package shared by all starters):
   - `ModelClient` protocol: one method that takes messages, tool definitions and limits, and returns a normalized response (text, tool calls, stop reason, token usage).
   - Providers: `anthropic`, `openai`, and `replay` (reads recorded responses from `fixtures/`, used in CI).
   - `record` mode: wraps a real provider and saves responses to `fixtures/` so they can be replayed.
   - `Budget`: tracks steps, tokens and estimated spend; raises when a limit is hit.
   - Provider and model come from `config.yaml` plus environment variables. Keys only from the environment.
   - Check the current SDK docs for each provider before writing provider code. Do not rely on memory for API shapes.
5. **Docs site.** Pick a static site generator (see `DECISIONS.md`) and render `docs/`.

### Acceptance criteria

- [ ] Every source in `sources.yaml` has `status` of `verified` or `dead`.
- [ ] `pytest` passes, including `agentkit` tests that run only on the `replay` provider.
- [ ] Swapping provider requires changing `config.yaml` only.
- [ ] A test proves `Budget` stops a run at the step limit and at the spend limit.
- [ ] A test proves API keys never appear in logs or trace output.
- [ ] CI is green on GitHub.

---

## Phase 2 — Verifier first, then the first 10 pages

**Goal:** trust the verifier before trusting any page it approves.

### Deliverables

1. **Verifier eval.** Extend `evals/verifier/planted_errors.yaml` to at least 20 planted errors and 10 correct claims. Run the `verifier` subagent on each case and record results in `evals/verifier/results.md`.
2. **First 10 pages**, in this order, each from `templates/page.md` via the `/ingest-source` workflow:
   1. `what-is-an-agent.md` — workflows vs agents; when not to build an agent
   2. `agent-loop.md` — the loop, stop conditions, step and budget caps
   3. `tool-design.md` — tool schemas, naming, token-efficient results, error messages
   4. `context-engineering.md` — context as a budget, compaction, note-taking, sub-agents
   5. `control-flow.md` — owning control flow, pause/resume, stateless reducer
   6. `human-in-the-loop.md` — approval as a tool call, escalation triggers
   7. `evals.md` — tasks, trials, graders, error analysis, regression vs capability evals
   8. `multi-agent.md` — orchestrator-workers, handoffs, token cost trade-off
   9. `mcp.md` — what MCP is, current revision, servers and clients
   10. `security.md` — prompt injection, least privilege, guardrail layers

### Acceptance criteria

- [ ] Verifier catches at least 18 of 20 planted errors.
- [ ] Verifier wrongly rejects at most 1 of 10 correct claims.
- [ ] Each page passes `scripts/validate.py` and has a verifier report attached to its PR.
- [ ] Each page passes `scripts/check_overlap.py` against every source it cites.

If the verifier misses the thresholds, improve `.claude/agents/verifier.md` and rerun. Do not write pages until it passes.

---

## Phase 3 — First starter: `tool-agent`

**Goal:** one complete starter that sets the pattern for all others.

### Deliverables

Create `starters/tool-agent/` with the `/new-starter` skill. Example task: an operations agent that reads a ticket, looks up records with read-only tools, drafts an action, and requests human approval before any write tool runs.

- `src/` — raw loop on `agentkit` (no framework).
- `src/framework/` — the same agent in one framework (choice recorded in `DECISIONS.md`).
- `SPEC.md`, `AGENTS.md`, `README.md`, `.env.example`, `config.yaml`.
- `evals/` — at least 5 cases with graders.
- `fixtures/` — recorded responses for every test.
- Tracing set up with OpenTelemetry.

### Acceptance criteria

- [ ] `pytest starters/tool-agent` passes with no API key set.
- [ ] Both `src/` and `src/framework/` pass the same eval cases.
- [ ] A write tool cannot run without an approval step (tested).
- [ ] A new user can follow `README.md` from clone to first live run in under 15 minutes (test it once by hand).
- [ ] A coding agent given only `SPEC.md` + `AGENTS.md` can reproduce a passing implementation (test it once).

---

## Phase 4 — Two more starters

`starters/rag-agent/` (document Q&A with citations) and `starters/research-agent/` (search, read, report with sources). Same acceptance criteria as Phase 3.

Later candidates, one at a time, only after these pass: `coding-agent`, `browser-agent`, `multi-agent`, `voice-agent`.

---

## Phase 5 — Keep it fresh

1. **Weekly ingest.** A scheduled job re-fetches each source, compares its `content_hash`, and opens a PR that re-ingests changed sources. Never commits to `main`.
2. **Nightly live smoke test.** Runs each starter once against one cheap model with a hard spend cap. Uses a GitHub Actions secret. Must not run on pull requests from forks.
3. **Spend caps.** Set a monthly budget on the API key in the provider console, and a per-run cap in code.

### Acceptance criteria

- [ ] A changed source produces a PR, not a commit.
- [ ] The nightly job fails visibly when a provider change breaks a starter.
- [ ] Monthly API spend stays under the cap you set in `DECISIONS.md`.

---

## Topic backlog (after Phase 2)

memory, retrieval and agentic RAG, observability and tracing, cost and latency, deployment and state.
