---
title: Human in the loop
status: verified
sources: [humanlayer-12-factor-agents, openai-practical-guide, openai-agents-sdk-docs]
last_verified: 2026-10-30
adapted_from: null
---

# Human in the loop

> **In one line:** Treat asking a human as just another tool call, and decide in advance which situations force that call.

## Why it matters

Early in a deployment, human intervention lets you find failures and edge cases without hurting the user experience, and it feeds a sturdier evaluation cycle [src:openai-practical-guide]. A human-intervention mechanism lets the agent gracefully transfer control when it cannot complete a task [src:openai-practical-guide]. Inference: without such a mechanism, a stuck agent has no clean way to give control back. Sensitive or irreversible actions are the other risk: examples given are canceling orders, authorizing large refunds and making payments [src:openai-practical-guide].

## Core ideas

**Approval as a tool call.** HumanLayer's factor 7 suggests you might get better results by having the model always emit structured output and name its intent. A human request such as `request_human_input` is one possible intent, next to `done_for_now` and ordinary tools [src:humanlayer-12-factor-agents]. Their sketch gives that request a question, context and options (urgency, answer format, choices) [src:humanlayer-12-factor-agents]. The authors say this may not improve performance and should be tested [src:humanlayer-12-factor-agents].

**Pause, persist, resume.** In the sketch, the loop records a `human_input_requested` event, saves state under a thread id, notifies the person and exits. A later webhook loads that thread, appends the human's response and continues the loop [src:humanlayer-12-factor-agents]. The same project says many orchestrators can pause and resume, but not between choosing a tool and running it [src:humanlayer-12-factor-agents].

**Framework-level approval (OpenAI Agents SDK).** A tool declares `needs_approval`, either `True` or an async function that decides per call [src:openai-agents-sdk-docs]. When a call needs approval and no stored decision exists, the run pauses and `RunResult.interruptions` lists the pending items [src:openai-agents-sdk-docs]. You convert the result to a `RunState`, call `approve` or `reject`, and resume with the original top-level agent [src:openai-agents-sdk-docs]. Interruptions from handoffs and nested `Agent.as_tool()` runs surface on the outer run [src:openai-agents-sdk-docs]. Rules that cannot safely inspect the arguments (missing, malformed or non-object JSON) fail closed and require manual approval [src:openai-agents-sdk-docs].

**Escalation triggers.** OpenAI's guide names two main ones [src:openai-practical-guide]:

1. Exceeding failure thresholds: limits on retries or actions, for example repeatedly failing to understand customer intent [src:openai-practical-guide].
2. High-risk actions: sensitive, irreversible or high-stakes actions, until the agent has proven reliable [src:openai-practical-guide].

HumanLayer adds a concrete case: a consecutive-error threshold is a good place to escalate, either by model decision or by deterministic takeover of control flow [src:humanlayer-12-factor-agents].

## How to apply it

1. List your tools and mark the irreversible or high-stakes ones. In our view: start with approval required on all of them and relax later, which fits the guide's idea of keeping oversight on high-risk actions while reliability is unproven [src:openai-practical-guide].
2. In our view: put a retry or error counter in your own loop and hand off to a human when it crosses the limit. Both sources name failure thresholds as an escalation point [src:openai-practical-guide][src:humanlayer-12-factor-agents].
3. In our view: make the approval request carry the tool name and arguments so the reviewer sees what will run. The SDK exposes agent name, tool name and arguments on each pending item [src:openai-agents-sdk-docs].
4. Store paused state on the server. The SDK warns that `RunState.from_json()` and `from_string()` do not authenticate snapshots, so deserialize only trusted data and take reviewer identity from your auth layer, not the request body [src:openai-agents-sdk-docs].
5. In our view: give rejections a clear message. The SDK supports a per-call `rejection_message` and a run-wide `tool_error_formatter` [src:openai-agents-sdk-docs].
6. In our view: make approved actions idempotent. Approval does not guarantee exactly-once execution, so the SDK docs advise a stable idempotency key per logical action for consequential side effects [src:openai-agents-sdk-docs].

A runnable starter for this pattern is planned in a later phase.

## Trade-offs and failure modes

- Sticky decisions (`always_approve`) can leak. For local shell and apply-patch tools they match tool type and name rather than the owning agent, so one approval can apply to another agent's tool after a handoff [src:openai-agents-sdk-docs]. Use per-call decisions when permissions differ [src:openai-agents-sdk-docs].
- For local shell and apply-patch tools, approval is opt-in: `needs_approval` defaults to `False`, and an `on_approval` callback alone does not enable it [src:openai-agents-sdk-docs].
- Callbacks that decide in code let the run continue without a human pause [src:openai-agents-sdk-docs]. Inference: that removes the human check, so use them only where a code policy is an acceptable substitute.
- In our view: too many approval prompts will train reviewers to click through, so tier by risk instead of gating everything permanently. The sources do not test this.
- Hosted shell environments do not support `needs_approval` or `on_approval` [src:openai-agents-sdk-docs].

## Further reading

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents): factor 7 on human contact as a tool call, plus pause/resume and error handling.
- [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): the two escalation triggers and guardrails context.
- [OpenAI Agents SDK (Python) documentation](https://openai.github.io/openai-agents-python/): the human-in-the-loop page covers approval flow, `RunState` and long-running approvals.
