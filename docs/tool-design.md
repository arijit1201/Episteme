---
title: Tool design for agents
status: verified
sources: [anthropic-writing-tools, anthropic-building-effective-agents, openai-practical-guide]
last_verified: 2026-10-30
adapted_from: null
---

# Tool design for agents

> **In one line:** In our view: design each tool for a model with a limited context window, not for a human developer: few distinct tools, clear names, compact results, and errors that say how to fix the call.

## Why it matters

A tool is a contract between deterministic code and a non-deterministic agent. The agent may call it wrongly, skip it, or misread its output [src:anthropic-writing-tools]. Wrapping existing API endpoints without thought wastes limited agent context [src:anthropic-writing-tools]. Anthropic reports that, building its SWE-bench agent, it spent more time optimizing tools than the overall prompt [src:anthropic-building-effective-agents]. That article carries a note that much of its tooling landscape has changed since December 2024 [src:anthropic-building-effective-agents].

## Core ideas

**Pick tools for workflows, not endpoints.**
- Prefer a `search_contacts` tool over `list_contacts`, because dumping everything burns context [src:anthropic-writing-tools].
- A tool may merge several chained operations. Examples given: `schedule_event` instead of separate list and create tools, and `search_logs` instead of `read_logs` [src:anthropic-writing-tools].
- Each tool needs a clear, distinct purpose. Too many or overlapping tools distract the agent [src:anthropic-writing-tools].
- OpenAI says the problem is similarity, not count. Some systems handle more than 15 distinct tools, while others struggle with fewer than 10 overlapping ones [src:openai-practical-guide].

**Name for clear boundaries.**
- Group related tools under shared prefixes, by service (`asana_search`, `jira_search`) or by resource [src:anthropic-writing-tools].
- Prefix versus suffix naming changed eval results, and the effect varied by model. Test your own scheme [src:anthropic-writing-tools].
- Name parameters unambiguously: `user_id`, not `user` [src:anthropic-writing-tools].
- OpenAI's advice when tools get confused: improve names, parameters and descriptions first. Split into multiple agents only if that fails [src:openai-practical-guide].

**Write the schema and description like documentation for a new hire.**
- Make implicit context explicit: query formats, niche terms, relationships between resources [src:anthropic-writing-tools].
- A good definition can include example usage, edge cases, input format rules and boundaries from other tools [src:anthropic-building-effective-agents].
- Make mistakes harder. Anthropic's example: the model erred with relative file paths after changing directory, so the tool began requiring absolute paths, and the model then used it flawlessly [src:anthropic-building-effective-agents]. The source calls this "Poka-yoke your tools" [src:anthropic-building-effective-agents].
- Pick formats the model writes easily. Diffs need line counts up front, and code inside JSON needs escaping. Keep formats close to text the model has seen naturally, and avoid counting or escaping overhead [src:anthropic-building-effective-agents].

**Return high-signal, token-efficient results.**
- Return meaningful fields (`name`, `file_type`) over low-level identifiers (`uuid`, `mime_type`) [src:anthropic-writing-tools].
- Replacing opaque alphanumeric IDs with readable names, or a 0-indexed scheme, improved Claude's retrieval precision by reducing hallucinations [src:anthropic-writing-tools].
- Offer a `response_format` enum (`concise` or `detailed`). In Anthropic's Slack example, concise used 72 tokens against 206 for detailed. Detailed output carries the IDs that later calls need [src:anthropic-writing-tools].
- For large outputs, use pagination, range selection, filtering or truncation, with sensible defaults. Claude Code caps tool responses at 25,000 tokens by default [src:anthropic-writing-tools].
- When truncating, tell the agent what to do next, for example to run narrower searches [src:anthropic-writing-tools].

**Write errors the agent can act on.**
- Return specific, actionable guidance on input errors, not opaque codes or tracebacks [src:anthropic-writing-tools].

## How to apply it

1. In our view: list the few workflows your agent must complete. Build one tool per task-level workflow, consolidating chained steps.
2. In our view: prefix names by service or resource. Name every parameter so it cannot be confused with another.
3. In our view: write each description with purpose, input format, an example, and what the tool is not for.
4. In our view: add `response_format`, a default page size and a limit on result size.
5. In our view: make validation errors state what was wrong and show a valid example.
6. Build a prototype and run realistic multi-call eval tasks. Track tool errors, call counts, runtime and token use. Many redundant calls suggest resizing pagination or token limits. Many invalid-parameter errors suggest clearer descriptions or examples [src:anthropic-writing-tools].
7. Read raw transcripts, not only the agent's stated reasoning, because agents do not always say what they mean [src:anthropic-writing-tools].

A runnable starter for this page is planned in a later phase.

## Trade-offs and failure modes

- In our view: consolidated tools cut round trips but may be harder to describe, and a vague multi-purpose tool can hurt. Start narrow and merge only where evals show chained calls.
- Concise output saves tokens but can hide IDs that the next call needs. The `response_format` switch exists for this reason [src:anthropic-writing-tools].
- Naming and format advice varies by model, so treat it as hypotheses to test [src:anthropic-writing-tools].
- Inference: the OpenAI guide gives no result-size or error-message guidance in the cached text, so those points rest on Anthropic's experience alone.
- TODO(verify): whether tool-annotation and dynamic-loading advice from the Anthropic post applies to non-Claude providers.

## Further reading

- [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents): the main source for namespacing, result design, token limits and error messages.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): Appendix 2 covers tool formats and agent-computer interface design.
- [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): tool types (data, action, orchestration) and the tool overload point.
