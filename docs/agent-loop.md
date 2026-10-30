---
title: The agent loop, stop conditions, and caps
status: verified
sources: [anthropic-building-effective-agents, openai-practical-guide, anthropic-long-running-harnesses, paper-react]
last_verified: 2026-10-30
adapted_from: null
---

# The agent loop, stop conditions, and caps

> **In one line:** An agent is a model calling tools in a loop, and the loop runs until an exit condition is hit, such as a final output, an error, or a maximum number of turns [src:openai-practical-guide], with stopping conditions like an iteration cap added to keep control [src:anthropic-building-effective-agents].

## Why it matters

Agents are described as LLMs using tools based on environmental feedback in a loop [src:anthropic-building-effective-agents]. The same source warns that their autonomy brings higher costs and the chance of compounding errors [src:anthropic-building-effective-agents]. Long-running loops add a second problem: the agent may declare the job done too early [src:anthropic-long-running-harnesses].

## Core ideas

**The loop shape.** The ReAct paper has the model produce reasoning traces and actions interleaved. Reasoning helps it track and update plans, and actions let it pull in information from outside sources such as knowledge bases or environments [src:paper-react]. Anthropic adds that at each step the agent should get "ground truth" from the environment, such as tool results or code execution, to judge its progress [src:anthropic-building-effective-agents].

**Run = loop until an exit condition.** OpenAI says every orchestration approach needs a "run", usually a loop that continues until an exit condition is hit. Common exit conditions are tool calls, a given structured output, errors, or a maximum number of turns [src:openai-practical-guide]. In the Agents SDK, the run loop ends when a final-output tool is called, or when the model replies with no tool calls [src:openai-practical-guide].

**Natural end plus a safety stop.** Anthropic notes a task often ends on completion, but it is common to add stopping conditions, such as a maximum number of iterations, to keep control [src:anthropic-building-effective-agents]. Agents can also pause for human feedback at checkpoints or on blockers [src:anthropic-building-effective-agents].

**Escalate on failure limits and risk.** OpenAI names two triggers for handing off to a human. One is passing a failure threshold, meaning limits on retries or actions. The other is a high-risk action, such as canceling orders, authorizing large refunds, or making payments [src:openai-practical-guide].

**"Done" must be checked, not claimed.** In long-running work, Anthropic saw a later agent instance see earlier progress and declare the job done [src:anthropic-long-running-harnesses]. It also saw features marked complete without proper end-to-end testing [src:anthropic-long-running-harnesses]. Their fix was a structured feature list, initially all marked failing, so the agent has a clear picture of full completion [src:anthropic-long-running-harnesses]. Agents were told to mark a feature passing only after careful testing [src:anthropic-long-running-harnesses].

**One chunk per session.** Working on one feature at a time countered the tendency to do too much at once. The agent also commits to git and writes a progress note, so a fresh context window can see state quickly [src:anthropic-long-running-harnesses].

## How to apply it

1. In our view: write the loop as call model, run requested tools, append results, repeat. This is our concrete reading of the run loop that OpenAI describes in general terms [src:openai-practical-guide].
2. Define the exit conditions up front: a final-output signal, a reply with no tool calls, an error, and a maximum number of turns [src:openai-practical-guide].
3. Add a cap on iterations [src:anthropic-building-effective-agents] and a retry or action limit that triggers human handoff [src:openai-practical-guide].
4. Gate sensitive or irreversible tools behind human approval [src:openai-practical-guide].
5. For multi-session work, keep a progress file and git history, and a pass/fail feature list the agent can only update by status [src:anthropic-long-running-harnesses].
6. Inference: also cap tokens and spend per run. None of the cited sources gives a number or a spend-cap mechanism, so pick values by measuring your own tasks. TODO(verify): find a primary source for token and spend budgets.

A runnable starter that implements these caps is planned in a later phase.

## Trade-offs and failure modes

- A turn cap is a blunt tool. Inference: a cap set too low cuts off valid work, and one set too high lets a stuck loop burn budget. The sources give no recommended value.
- Anthropic says agents suit open-ended problems where the number of steps cannot be predicted or hardcoded. Simpler solutions may be enough, and agentic systems often trade latency and cost for task performance [src:anthropic-building-effective-agents].
- Compaction alone did not fix long-running failures. Even with compaction, runs across many context windows left half-finished features and lost instructions [src:anthropic-long-running-harnesses].
- In our view: treat the model's own claim that it is finished as a hint, and verify with tests or a checklist before you stop the loop.
- The ReAct results come from specific benchmarks and prompting setups. The abstract does not describe production stop or budget policy [src:paper-react].

## Further reading

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): agent definition, loop, stopping conditions.
- [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): run loop, exit conditions, human handoff triggers.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): multi-session progress, completion checks.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629): the reason-and-act pattern behind the loop.
