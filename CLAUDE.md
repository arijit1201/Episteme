@AGENTS.md

## Claude Code specifics

- Use the `summarizer` subagent to draft pages and the `verifier` subagent to check them. Never let the summarizer verify its own draft.
- Use the `/ingest-source` skill to add or refresh a source. Use the `/new-starter` skill to create a starter.
- Use plan mode for anything that touches more than 3 files.
