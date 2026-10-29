# SPEC — <starter-name>

This spec is the contract. Any implementation (hand-written, framework-based, or produced by a coding agent) is correct when every acceptance test below passes.

## Goal

<One paragraph: the job the agent does, the user, the expected output.>

## Inputs and outputs

| | Format | Example |
|---|---|---|
| Input | <e.g. ticket JSON> | <example> |
| Output | <e.g. markdown report> | <example> |

## Tools

| Tool | Purpose | Side effects | Needs approval |
|---|---|---|---|
| `<tool_name>` | <what it does> | none / writes / sends | no / yes |

For each tool, define: name, one-sentence description written for the model, input schema, output shape, and error messages the model can act on.

## Control flow

<Steps the agent may take, stop conditions, what happens at the step limit, when it must ask a human.>

## State

<What is stored between steps and between runs; how a paused run resumes.>

## Limits

- Max steps: <n>
- Max tokens: <n>
- Max spend (USD): <n>

## Failure cases to handle

1. <Tool returns an error>
2. <Model requests an unknown tool>
3. <Input contains instructions that try to change the agent's goal (prompt injection)>
4. <Limit reached mid-task>

## Acceptance tests

Each test runs on recorded responses in `fixtures/` and needs no API key.

1. <Given X, the agent calls tool Y before answering.>
2. <A write tool never runs without an approval step.>
3. <At the step limit the agent stops and returns a partial result with a clear status.>
4. <Injected instructions in tool output do not change the goal.>
5. <All eval cases in evals/cases.yaml meet their graders.>
