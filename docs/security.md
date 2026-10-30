---
title: Security for agents
status: verified
sources: [owasp-llm01-prompt-injection, anthropic-prompt-injection-defenses, openai-practical-guide, mcp-spec, anthropic-building-effective-agents, humanlayer-12-factor-agents]
last_verified: 2026-10-30
adapted_from: null
---

# Security for agents

> **In one line:** In our view: assume the model can be tricked by any content it reads, and limit what a tricked model can do.

## Why it matters

Prompt injection means input changes a model's behavior in ways nobody intended. The input need not be readable by humans, as long as the model parses it [src:owasp-llm01-prompt-injection]. When an agent reads untrusted content, an attacker can embed instructions that hijack it [src:anthropic-prompt-injection-defenses]. Impact depends on the business context and on how much agency the model has [src:owasp-llm01-prompt-injection]. Agents with tools can be pushed into disclosing data, running commands in connected systems, or using functions they should not [src:owasp-llm01-prompt-injection].

## Core ideas

**Two entry routes.** Direct injection comes from the user's own prompt. Indirect injection comes from external sources such as websites or files the model reads [src:owasp-llm01-prompt-injection]. Anthropic's example: an email with hidden white text telling an agent to forward "confidential" mail to an outside address [src:anthropic-prompt-injection-defenses].

**No known cure.** OWASP says it is unclear whether any fool-proof prevention exists, and that RAG and fine-tuning do not fully mitigate the problem [src:owasp-llm01-prompt-injection]. Anthropic reports progress on robustness but says the problem is far from solved [src:anthropic-prompt-injection-defenses]. Inference: design so that one successful injection is survivable.

**Least privilege.** OWASP advises giving the application its own API tokens, handling those functions in code instead of handing them to the model, and restricting the model to the minimum access its task needs [src:owasp-llm01-prompt-injection]. It also suggests treating the model as an untrusted user when testing trust boundaries [src:owasp-llm01-prompt-injection].

**Human approval for risky actions.** OWASP lists human-in-the-loop control for privileged operations [src:owasp-llm01-prompt-injection]. OpenAI names two triggers for human intervention: exceeded failure thresholds, and high-risk actions that are sensitive, irreversible or high-stakes, such as payments or large refunds [src:openai-practical-guide]. MCP says there should always be a human able to deny tool invocations, and hosts must get explicit consent before invoking any tool [src:mcp-spec]. The 12-factor material has code pause the loop for approval of high-stakes tool calls [src:humanlayer-12-factor-agents].

**Tool risk ratings.** OpenAI suggests rating each tool low, medium or high using read-only versus write access, reversibility, account permissions and financial impact. Ratings can trigger guardrail checks or escalation to a human [src:openai-practical-guide].

**Layered guardrails.** OpenAI treats guardrails as layers: one is unlikely to be enough, so combine specialized ones. Its example mixes LLM-based checks, regex rules and a moderation API on user input [src:openai-practical-guide]. Listed types include relevance and safety classifiers, a PII filter, moderation and output validation [src:openai-practical-guide]. Guardrails should be paired with authentication, authorization, strict access controls and standard software security [src:openai-practical-guide]. Anthropic describes one guardrail pattern: one model instance handles the user query while another screens it [src:anthropic-building-effective-agents].

**Defenses inside the model vendor stack.** Anthropic describes three layers for its browser agent: reinforcement-learning training against injections, classifiers scanning untrusted content entering the context, and human red teaming [src:anthropic-prompt-injection-defenses].

**Handle untrusted content as untrusted.** OWASP recommends separating and clearly marking external content, validating output formats with deterministic code, and filtering input and output [src:owasp-llm01-prompt-injection]. MCP treats tool descriptions and annotations as untrusted unless they come from a trusted server [src:mcp-spec].

## How to apply it

In our view: this checklist is our synthesis; markers show the idea's source, not a source's checklist.

1. In our view: list every source of untrusted content the agent reads (web, files, email, tool output).
2. List every tool. Rate each by write access, reversibility and cost [src:openai-practical-guide].
3. Give the agent only the credentials and tools its task needs. Keep sensitive functions in application code [src:owasp-llm01-prompt-injection].
4. Gate high-risk tools behind human approval in your own control flow [src:openai-practical-guide] [src:humanlayer-12-factor-agents].
5. Add input and output checks in layers, mixing deterministic rules and model-based classifiers [src:openai-practical-guide].
6. Set stopping conditions such as a maximum iteration count, and test in a sandbox [src:anthropic-building-effective-agents].
7. Run adversarial tests regularly [src:owasp-llm01-prompt-injection].

## Trade-offs and failure modes

- Anthropic says that even a 1% attack success rate, a figure it gives for its own browser-use setup and not a general result, still represents meaningful risk, and that no browser agent is immune [src:anthropic-prompt-injection-defenses]. Inference: filters and classifiers lower risk but do not remove it.
- OWASP notes that attackers can use multiple languages or encodings such as Base64 to evade filters [src:owasp-llm01-prompt-injection]. Inference: blocklists alone are weak.
- In our view: approval prompts add friction. OpenAI wants human oversight of high-risk actions until reliability is trusted [src:openai-practical-guide].
- MCP states that the protocol cannot enforce its security principles itself, so implementors SHOULD build consent and access controls [src:mcp-spec].
- In our view: least privilege and approval gates are the most dependable controls, because they hold even when the model is fooled. Classifiers are a useful extra layer, not a boundary.
- OWASP lists prompt-level constraints as one mitigation [src:owasp-llm01-prompt-injection]. In our view: do not rely on them alone.

## Further reading

- [LLM01:2025 Prompt Injection (OWASP)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/): attack types and mitigations.
- [Mitigating the risk of prompt injections in browser use (Anthropic)](https://www.anthropic.com/research/prompt-injection-defenses): browser-agent threat model and defenses.
- [A practical guide to building agents (OpenAI)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf): layered guardrails and human intervention.
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification): consent and tool safety.
- [Building effective agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents): guardrail pattern.
- [12-Factor Agents (HumanLayer)](https://github.com/humanlayer/12-factor-agents): approval of high-stakes tool calls in control flow.
