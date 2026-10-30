---
title: Multi-agent systems
status: verified
sources: [anthropic-multi-agent-research, anthropic-building-effective-agents, openai-practical-guide]
last_verified: 2026-10-30
adapted_from: null
---

# Multi-agent systems

> **In one line:** Add agents only when one agent with tools fails, and budget for a much larger token bill when you do.

## Why it matters

One agent can hit limits: prompts with too many branches, or tools it confuses with each other. Splitting work across agents can help with these [src:openai-practical-guide]. Anthropic adds that tasks with information beyond a single context window suit multi-agent setups [src:anthropic-multi-agent-research]. But coordination adds complexity and overhead, and Anthropic's data shows a large token cost [src:openai-practical-guide][src:anthropic-multi-agent-research].

## Core ideas

**Orchestrator-workers.** A central LLM breaks a task down at run time, hands pieces to worker LLMs, and merges their results [src:anthropic-building-effective-agents]. It looks like parallelization, but subtasks are not fixed in advance: the orchestrator picks them from the input [src:anthropic-building-effective-agents]. Anthropic's Research system uses this pattern. A lead agent delegates to subagents that run in parallel [src:anthropic-multi-agent-research].

**Manager pattern (OpenAI's term).** A central manager agent calls specialist agents as tools. It suits workflows where one agent should control execution and talk to the user [src:openai-practical-guide].

**Handoffs (decentralized pattern).** A handoff is a one-way transfer of control. In the OpenAI Agents SDK it is a kind of tool call. The new agent starts at once and receives the latest conversation state [src:openai-practical-guide]. It fits triage, or cases where a specialist should fully take over without the first agent staying involved. A handoff back to the original agent is optional [src:openai-practical-guide].

**Why tokens matter.** Anthropic reports that token usage alone explained 80% of performance variance on BrowseComp. Tool calls and model choice were the other two factors, and together the three explained 95% [src:anthropic-multi-agent-research]. Subagents with separate context windows add capacity for parallel reasoning [src:anthropic-multi-agent-research].

## How to apply it

1. Start with a single agent and maximize what it can do. Move to several agents only when needed [src:openai-practical-guide].
2. Split when prompts have many conditional branches, or when tools stay confused after you improve names, parameters and descriptions [src:openai-practical-guide].
3. If delegating, give each subagent an objective, an output format, guidance on tools and sources, and clear task boundaries. Vague instructions led to duplicated work and gaps [src:anthropic-multi-agent-research].
4. Put effort rules in the lead prompt. Anthropic used: simple fact-finding, 1 agent with 3-10 tool calls; direct comparisons, 2-4 subagents with 10-15 calls each; complex research, more than 10 subagents [src:anthropic-multi-agent-research].
5. To cut the "game of telephone", let subagents write large outputs to external storage and pass back lightweight references. This also reduces tokens copied through conversation history [src:anthropic-multi-agent-research].

A runnable starter is planned in a later phase.

## Trade-offs and failure modes

**Token cost, exact figures.** In Anthropic's data, agents typically use about 4x more tokens than chat interactions. Multi-agent systems use about 15x more than chats [src:anthropic-multi-agent-research]. The 15x figure is against chat, not against a single agent. Inference: against a single agent, the multiple would be smaller than 15x, but the source gives no direct figure. TODO(verify): single-agent versus multi-agent token ratio.

**Economics.** Anthropic says multi-agent systems need tasks valuable enough to pay for the extra cost [src:anthropic-multi-agent-research].

**Poor fits.** Domains where all agents must share context, or with many dependencies between agents, fit badly. Most coding tasks have fewer parallelizable parts than research. Anthropic notes that LLM agents are not yet good at real-time coordination and delegation [src:anthropic-multi-agent-research]. Good fits are valuable tasks with heavy parallelization, information beyond one context window, and many complex tools [src:anthropic-multi-agent-research].

**Failure modes seen early.** Spawning 50 subagents for simple queries, endless searching for nonexistent sources, and agents distracting each other with excess updates [src:anthropic-multi-agent-research]. Small changes to the lead agent can unpredictably change subagent behavior [src:anthropic-multi-agent-research].

**Tool overload is not just a count.** Some setups handle more than 15 distinct tools while others struggle with under 10 overlapping ones [src:openai-practical-guide].

In our view: choose manager/orchestrator when you need one point of control and synthesis, and handoffs when the specialist should own the conversation. Both are supported by the sources, but the choice rule is our synthesis. Also in our view: measure token spend per run from day one, given the multiples above.

## Further reading

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): production orchestrator-workers, token data, prompting lessons.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): orchestrator-workers as one workflow among several, and the advice to start simple.
- [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): manager and decentralized patterns, and when to split agents.
