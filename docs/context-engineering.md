---
title: Context engineering
status: verified
sources: [anthropic-context-engineering, anthropic-long-running-harnesses, humanlayer-12-factor-agents]
last_verified: 2026-10-30
adapted_from: null
---

# Context engineering

> **In one line:** Treat the context window as a limited budget, and spend it only on the smallest set of tokens that raises the odds of the outcome you want [src:anthropic-context-engineering].

## Why it matters

Models lose recall accuracy as the token count in the window grows, an effect Anthropic calls context rot [src:anthropic-context-engineering]. The decline is gradual rather than a cliff, but it shows up in every model tested [src:anthropic-context-engineering]. Agents that run in a loop keep producing data, so something must decide on each turn what goes into the window [src:anthropic-context-engineering]. Long tasks also cross window boundaries, and each new session starts with no memory of the last [src:anthropic-long-running-harnesses].

## Core ideas

- **Context is more than the prompt.** It covers instructions, retrieved documents, past tool calls and results, memory from other conversations, and output-format instructions [src:humanlayer-12-factor-agents]. Each model call can be seen as handing the model a summary of what has already happened and asking it to pick the next step [src:humanlayer-12-factor-agents].
- **Budget, not bucket.** Anthropic describes an "attention budget" that each added token draws down [src:anthropic-context-engineering]. Larger windows are not expected to remove pollution and relevance problems soon [src:anthropic-context-engineering].
- **Keep every part tight.** System prompts should sit at the right altitude: not brittle if-else logic, not vague guidance [src:anthropic-context-engineering]. Tool sets should be small and unambiguous, and few-shot examples should be a few diverse canonical ones, not a list of edge cases [src:anthropic-context-engineering].
- **Load just in time.** Agents can hold lightweight references such as file paths or stored queries and pull data in with tools at runtime, instead of loading everything first [src:anthropic-context-engineering]. A hybrid is also possible: some data up front, the rest by exploration [src:anthropic-context-engineering].
- **Compaction.** Summarize a conversation near the limit and start a new window from the summary [src:anthropic-context-engineering]. Tune the compaction prompt on real traces: first maximize recall, then trim for precision [src:anthropic-context-engineering]. Clearing old tool results is described as a safe, light form [src:anthropic-context-engineering].
- **Structured note-taking.** The agent writes notes (a to-do list, a NOTES.md) outside the window and reads them back later [src:anthropic-context-engineering].
- **Sub-agents.** Focused sub-agents work in clean windows and return a condensed summary, often 1,000-2,000 tokens, to a coordinating agent [src:anthropic-context-engineering].
- **Own the format.** You need not use the standard message list; you can pack the whole history into one custom-formatted message to be more token- and attention-efficient [src:humanlayer-12-factor-agents].
- **Compact errors.** Feed a failed tool call's error back into the context so the model can self-correct [src:humanlayer-12-factor-agents]. You can restructure the error or remove earlier events rather than append it raw [src:humanlayer-12-factor-agents].

## How to apply it

1. Start with a minimal system prompt on the best model, then add instructions and examples only for failures you observe [src:anthropic-context-engineering].
2. Pick the long-task technique by task shape: compaction for long back-and-forth, note-taking for iterative work with milestones, multi-agent for parallel research [src:anthropic-context-engineering].
3. Compaction alone was not enough in Anthropic's long-running tests. Their fix was an initializer session that creates an init.sh script, a progress file and a first git commit; later sessions each do one feature and leave a clean state [src:anthropic-long-running-harnesses].
4. Keep a feature list as JSON with a passes field. The authors found the model less likely to overwrite JSON than Markdown [src:anthropic-long-running-harnesses].
5. At session start, have the agent read the progress file, the git log and the feature list, then run a basic end-to-end check before new work [src:anthropic-long-running-harnesses].
6. Wrap tool calls in a try/catch that appends the error to the thread, and count consecutive errors. After about three, stop, reset parts of the context, or escalate to a human [src:humanlayer-12-factor-agents].

A runnable starter for these patterns is planned in a later phase.

## Trade-offs and failure modes

- Over-aggressive compaction can drop subtle details whose value shows up later [src:anthropic-context-engineering].
- Just-in-time exploration is slower than precomputed retrieval, and agents without good tool guidance can chase dead ends [src:anthropic-context-engineering].
- Compaction may not hand the next session clear instructions; one observed result was a half-built feature left undocumented [src:anthropic-long-running-harnesses].
- Too many error retries can make an agent repeat the same mistake [src:humanlayer-12-factor-agents].
- Anthropic leaves open whether specialized multi-agent setups beat one general agent for long-running coding [src:anthropic-long-running-harnesses].
- The Anthropic posts are vendor sources on Claude-based setups. In our view: the techniques transfer, but the specific numbers and tool names may not.

## Further reading

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): the budget framing, compaction, notes, sub-agents.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): initializer plus coding-agent pattern across sessions.
- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents): factor 3 (own your context window) and factor 9 (compact errors).
