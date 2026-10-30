---
title: What is an agent? Workflows vs agents, and when not to build one
status: verified
sources: [anthropic-building-effective-agents, openai-practical-guide]
last_verified: 2026-10-30
adapted_from: null
---

# What is an agent? Workflows vs agents, and when not to build one

> **In one line:** In our view: an agent is a system where the model steers the process and picks the tools; if fixed code paths or a single well-prepared LLM call can do the job, build that instead.

## Why it matters

People use "agent" for very different things, from fully autonomous systems to scripted pipelines [src:anthropic-building-effective-agents]. Agentic systems often pay for better task results with extra latency and cost [src:anthropic-building-effective-agents]. Anthropic notes the simplest answer may involve no agentic system at all [src:anthropic-building-effective-agents]. The article itself carries a note that much of the tooling it describes has changed since December 2024 [src:anthropic-building-effective-agents].

## Core ideas

**Workflow vs agent.** Anthropic calls both kinds "agentic systems" but separates them architecturally. In a workflow, predefined code paths orchestrate the LLMs and tools. In an agent, the LLM directs its own process and tool use and keeps control of how the task gets done [src:anthropic-building-effective-agents].

**Agents are loops.** Anthropic describes agents as typically just LLMs using tools, guided by feedback from the environment, in a loop [src:anthropic-building-effective-agents]. OpenAI's definition matches: a system that independently completes tasks for the user. It names two traits: an LLM manages workflow execution and decisions, and the system has tools it selects dynamically within defined guardrails [src:openai-practical-guide].

**What is not an agent.** OpenAI excludes applications that use an LLM without letting it control workflow execution. Its examples are simple chatbots, single-turn LLMs and sentiment classifiers [src:openai-practical-guide].

**Note on terms.** OpenAI uses "workflow" for the sequence of steps needed to reach a user's goal [src:openai-practical-guide]. Anthropic uses "workflow" for systems orchestrated through predefined code paths [src:anthropic-building-effective-agents]. Inference: these are different senses of the word, so check which one a source uses.

**When workflows fit.** Workflows give predictability and consistency on well-defined tasks. Agents suit cases that need flexibility and model-driven decisions at scale [src:anthropic-building-effective-agents]. Anthropic's catalogue of workflow patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer [src:anthropic-building-effective-agents].

**When agents fit.** Anthropic points to open-ended problems where the number of steps is hard or impossible to predict and no fixed path can be hardcoded. You must also have some trust in the model's decisions [src:anthropic-building-effective-agents]. OpenAI points to workflows that resisted rule-based automation, with three signals: complex decision-making (such as refund approval), rulesets too unwieldy to maintain (such as vendor security reviews), and heavy reliance on unstructured data (such as home insurance claims) [src:openai-practical-guide].

**When not to build an agent.**
- A single LLM call, improved with retrieval and in-context examples, is usually enough for many applications [src:anthropic-building-effective-agents].
- OpenAI advises validating that the use case clearly meets its agent criteria; otherwise a deterministic solution may suffice [src:openai-practical-guide].
- Agents bring higher cost and the risk of compounding errors [src:anthropic-building-effective-agents].

## How to apply it

1. Anthropic recommends finding the simplest solution possible and increasing complexity only when needed [src:anthropic-building-effective-agents].
2. OpenAI's three signals for an agent use case are complex decision-making, unwieldy rulesets and heavy reliance on unstructured data [src:openai-practical-guide]. In our view: if a simple solution falls short, check the task against these signals next.
3. Anthropic says workflows suit well-defined tasks and agents suit cases needing flexibility and model-driven decisions at scale [src:anthropic-building-effective-agents]. In our view: use a workflow when the steps are known in advance.
4. OpenAI reports that customers typically do better with an incremental approach than with an immediate fully autonomous build [src:openai-practical-guide].
5. For an agent, test extensively in sandboxes and add guardrails [src:anthropic-building-effective-agents]. Stopping conditions such as a maximum number of iterations help keep control [src:anthropic-building-effective-agents].
6. Add complexity only when it demonstrably improves outcomes [src:anthropic-building-effective-agents].

A runnable starter that demonstrates this is planned in a later phase.

## Trade-offs and failure modes

- Cost and latency rise with autonomy, and errors can compound across many steps [src:anthropic-building-effective-agents].
- Frameworks can hide prompts and responses and make debugging harder. They can also tempt you to add complexity. Anthropic suggests starting with direct LLM API calls [src:anthropic-building-effective-agents].
- Anthropic's best-fit examples (customer support, coding) share clear success criteria, feedback loops and human oversight [src:anthropic-building-effective-agents].
- In our view: the two sources agree on direction (start simple, justify autonomy) but frame the decision differently. Anthropic frames it as fixed path vs model-chosen path; OpenAI frames it as rules vs judgment. Use both tests.
- In our view: "do I need an agent?" is best answered by an eval. If a simpler design meets your accuracy target, stop there.

## Further reading

- [Building effective agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents): the workflow/agent distinction, five workflow patterns, and guidance on when to stay simple.
- [A practical guide to building agents (OpenAI)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): a definition of agents, criteria for choosing use cases, and design foundations.
