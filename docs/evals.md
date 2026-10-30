---
title: Evals for agents
status: verified
sources: [anthropic-demystifying-evals, anthropic-multi-agent-research]
last_verified: 2026-10-30
adapted_from: null
---

# Evals for agents

> **In one line:** Start small with real failures, grade outcomes rather than exact steps, and read the transcripts to learn whether the agent or the eval is wrong.

## Why it matters

Without evals, teams react to complaints, reproduce bugs by hand, and hope a fix did not break something else. They also cannot tell a real regression from noise [src:anthropic-demystifying-evals]. Agents make this harder: they act over many turns and change state, so one mistake can compound [src:anthropic-demystifying-evals]. Their paths also vary, so checking a fixed sequence of steps usually fails [src:anthropic-multi-agent-research].

## Core ideas

**Vocabulary.** The source defines these terms [src:anthropic-demystifying-evals]:
- A task is a single test: fixed inputs plus success criteria.
- A trial is one try at a task. Outputs vary between runs, so you run several.
- A grader scores some aspect of performance. A task can have several graders, each with several checks.
- A transcript is the full record of a trial: outputs, tool calls, reasoning, intermediate results.
- The outcome is the final environment state. A "booked" message is not the outcome. A reservation row in the database is.
- A suite groups tasks with a shared goal.

**Three grader types.** Code-based graders (string match, tests, static analysis, tool-call checks) are fast, cheap and reproducible, but brittle against valid variation. Model-based graders (rubrics, pairwise comparison) handle open-ended output but are non-deterministic, cost more, and need calibration against humans. Human graders are the gold standard but slow and expensive [src:anthropic-demystifying-evals]. Per-task scoring can be weighted, binary, or hybrid [src:anthropic-demystifying-evals].

**Grade the outcome, not the path.** Requiring one exact tool-call sequence gives brittle tests, because agents find valid approaches the designer did not foresee [src:anthropic-demystifying-evals]. The multi-agent research team reached the same conclusion and judged outcomes plus a reasonable process [src:anthropic-multi-agent-research]. The first source also advises partial credit for multi-part tasks [src:anthropic-demystifying-evals].

**Capability vs regression evals.** Capability evals ask what the agent can do well. They should start at a low pass rate and give the team something to climb. Regression evals ask whether the agent still handles what it used to. They should sit near 100%, and a drop signals breakage. A capability eval with a high pass rate can graduate into the regression suite [src:anthropic-demystifying-evals].

**Non-determinism.** pass@k is the chance of at least one success in k tries. It rises with k. pass^k is the chance that all k trials succeed. It falls with k. The source ties pass^k to customer-facing agents that must be reliable every time. Its example: 75% per-trial success over 3 trials gives about 42% for all three [src:anthropic-demystifying-evals].

**Error analysis.** Grader quality is only visible by reading many trial transcripts with their grades. A failed transcript shows whether the agent erred or the grader rejected a valid answer. Failures should feel fair [src:anthropic-demystifying-evals]. Eval bugs it reports include rigid numeric matching, ambiguous specs, and tasks that cannot be reproduced exactly. A CORE-Bench score rose 42% to 95% after bug fixes and a less constrained scaffold [src:anthropic-demystifying-evals]. Human testers also found a source-selection bias that automated evals missed: early research agents preferred SEO content farms over authoritative sources [src:anthropic-multi-agent-research].

## How to apply it

1. Start with 20-50 simple tasks drawn from real failures. Early changes have large effects, so small samples suffice [src:anthropic-demystifying-evals]. The research team began with about 20 queries [src:anthropic-multi-agent-research].
2. Seed tasks from manual checks, bug trackers and support queues [src:anthropic-demystifying-evals].
3. Write unambiguous tasks that two domain experts would grade alike. Add a reference solution that passes every grader. A 0% pass rate over many trials usually means a broken task [src:anthropic-demystifying-evals].
4. Test both directions of a behavior (should search, should not) to avoid one-sided optimization [src:anthropic-demystifying-evals].
5. Run each trial from a clean environment. Shared state causes correlated failures and can inflate scores [src:anthropic-demystifying-evals].
6. Prefer deterministic graders, add LLM graders where needed, use humans sparingly [src:anthropic-demystifying-evals].
7. For LLM judges, allow an "Unknown" answer and calibrate against human experts [src:anthropic-demystifying-evals].
8. Watch for saturation: a suite at 100% shows no room to improve [src:anthropic-demystifying-evals].

A runnable starter for this is planned in a later phase.

## Trade-offs and failure modes

- Code graders are brittle and model graders are noisy and costly [src:anthropic-demystifying-evals].
- The two sources differ on judge design. The first suggests one isolated judge per rubric dimension [src:anthropic-demystifying-evals]. The second found one LLM call with one prompt, scoring 0.0-1.0 plus pass/fail, most consistent and closest to human judgment [src:anthropic-multi-agent-research]. In our view: try both on your own task and compare each against human labels.
- Automated evals can give false confidence if they do not match real usage, and need upkeep as the product and models change [src:anthropic-demystifying-evals]. The source pairs them with production monitoring, A/B tests, feedback and human review [src:anthropic-demystifying-evals].
- Graders can be cheated, so passing should require a real solution [src:anthropic-demystifying-evals].
- In our view: begin with a handful of cases and grow the set from observed failures. Do not wait for a large suite.

## Further reading

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): definitions, grader types, capability vs regression, pass@k and pass^k, and a step-by-step roadmap.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): a worked case of small-sample evals, an LLM judge rubric, and human testing for a research agent.
