---
name: new-starter
description: Create a new agent starter project in starters/ from templates/starter/. Use when the user asks for a new starter, template or agent project type.
---

# Create a starter

1. **Name and scope.** Confirm the starter name (kebab-case) and its one-sentence job with the user.
2. **Check prerequisites.** `agentkit/` must exist and its tests must pass (PLAN.md Phase 1). If not, stop and say so.
3. **Copy the template.** Copy `templates/starter/` to `starters/<name>/`.
4. **Write SPEC.md first.** Fill in goal, tools, control flow, state, limits, failure cases and acceptance tests. Show it to the user and wait for approval before writing code.
5. **Raw loop.** Implement the agent in `src/` on `agentkit` only. Keep it readable.
6. **Tests and fixtures.** Write one test per acceptance criterion. Record fixtures only if the user provides a key and approves the cost; otherwise hand-write minimal fixtures.
7. **Evals.** Fill `evals/cases.yaml` with at least 5 cases, including 1 adversarial case.
8. **Framework version.** Implement the same agent in `src/framework/` with the framework chosen in `DECISIONS.md`. Check that framework's current official docs first. Both versions must pass the same tests.
9. **Docs.** Complete `README.md` and `AGENTS.md`. Make the limits table match `config.yaml`.
10. **Pin and check.** Pin dependencies in `requirements.txt`. Run `pytest`, `python scripts/validate.py` and `python scripts/check_versions.py starters/<name>`.
11. **Index.** Add the starter to `starters/README.md` and `docs/index.md`.
12. **Report.** Show the diff and test results. Do not commit to `main`.
