---
title: Owning control flow, pause/resume and the stateless reducer
status: verified
sources: [humanlayer-12-factor-agents]
last_verified: 2026-10-30
adapted_from: null
---

# Owning control flow, pause/resume and the stateless reducer

> **In one line:** Keep the agent loop in your own code, keep all state in one serializable thread, and let the loop stop and restart around slow or risky steps.

This page rests on a single source, the 12-Factor Agents repo. It uses factors 3, 5, 6, 7, 8 and 12 and the repo's brief-history-of-software file. In our view: treat it as one practitioner's guidance, not a consensus.

## Why it matters

The source describes an agent as four parts: a prompt, a switch over the model's structured output, accumulated context, and a loop that runs until a terminal step [src:humanlayer-12-factor-agents]. Because the switch and loop are ordinary code, you can hijack them to wait for human input or a long-running task, and you can serialize the context for pause and resume [src:humanlayer-12-factor-agents].

Without that, the author says you must choose among three bad options. You keep the task paused in memory (a `while...sleep`) and restart from scratch if the process dies. Or you limit the agent to low-stakes work such as research and summaries. Or you grant broad powers and hope [src:humanlayer-12-factor-agents].

## Core ideas

- **Own the loop (factor 8).** Write control structures that fit your use case. Some tool calls should break out of the loop to wait for a human or a long job [src:humanlayer-12-factor-agents]. Other custom logic the source lists: summarizing or caching tool results, LLM-as-judge on output, context compaction, logging and tracing, client-side rate limiting, and durable sleep or wait-for-event [src:humanlayer-12-factor-agents].
- **Sync versus async steps.** The source's example handles three intents differently. A clarification request is saved, sent to a human, and the loop breaks. A read-only fetch appends its result to the thread and continues. A high-stakes action (deploying) breaks the loop and waits for human approval [src:humanlayer-12-factor-agents].
- **Pause between selection and execution.** The author's top feature request for frameworks is interrupting an agent between choosing a tool and invoking it. Without that, you cannot review a call before it runs [src:humanlayer-12-factor-agents].
- **Launch, pause, resume via simple APIs (factor 6).** Treat agents as programs. Users, apps, pipelines and other agents should start one through a simple API. Orchestrating code should be able to pause it. External triggers such as webhooks should resume it where it left off, without deep integration with the orchestrator [src:humanlayer-12-factor-agents]. The source notes that orchestrators often allow pause and resume but not in the gap between tool selection and tool execution [src:humanlayer-12-factor-agents].
- **Unify execution and business state (factor 5).** Execution state is things like current step, waiting status and retry counts. Business state is what has happened so far, such as messages and tool results. The source advises merging them where possible, since execution state can often be inferred from the context window [src:humanlayer-12-factor-agents]. Listed benefits include one source of truth, easy serialization, full history in one place, resuming from any point, and forking a thread by copying part of it [src:humanlayer-12-factor-agents]. Some items, such as session ids, may not fit in the context and should be minimized [src:humanlayer-12-factor-agents].
- **Stateless reducer (factor 12).** The source names this factor "Make your agent a stateless reducer" [src:humanlayer-12-factor-agents]. The source's own factor 12 page is brief, with images and a short note but no written definition, so this page does not expand on it [src:humanlayer-12-factor-agents].

## How to apply it

1. Store the whole run as one thread of typed events (model step, tool call, tool result, human request) [src:humanlayer-12-factor-agents].
2. In your loop, branch on the model's structured next step. For read-only steps, append the result and continue [src:humanlayer-12-factor-agents].
3. For clarifications and risky actions, append the event, notify the human, save the thread to a database, and break the loop [src:humanlayer-12-factor-agents].
4. Expose launch and resume endpoints. A webhook that carries the human's reply loads the saved thread, appends the reply and re-enters the loop [src:humanlayer-12-factor-agents].

A runnable starter for this is planned in a later phase.

## Trade-offs and failure modes

- The source itself says separating execution and business state may be worthwhile in some systems, and that you need not unify them [src:humanlayer-12-factor-agents].
- Not everything fits in the thread. Credentials and session ids may stay outside [src:humanlayer-12-factor-agents].
- In our view: hand-written loops cost more up front than a framework default. They pay off when you need approval gates or restarts that survive a crash.
- In our view: breaking the loop only works if saving the thread is reliable. A failed save at the pause point loses the run.

## Further reading

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) (HumanLayer): the full set of factors, including those used here. Licensed CC BY-SA 4.0 [src:humanlayer-12-factor-agents].
