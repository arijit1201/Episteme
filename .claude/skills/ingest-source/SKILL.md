---
name: ingest-source
description: Add a new source to sources.yaml or refresh an existing one, then draft and verify the pages that cite it. Use when the user says ingest, add a source, or refresh a source.
---

# Ingest a source

Follow these steps in order. Stop and report if any step fails.

1. **Register.** If the source is new, add an entry to `sources.yaml` with every required field. Use `status: unverified`.
2. **Fetch.** Fetch the URL. If it does not serve the expected document, set `status: dead` and stop.
3. **Hash.** Compute the sha256 of the fetched text. If it equals the stored `content_hash`, report "unchanged" and stop.
4. **Store temporarily.** Save the text to `.cache/<id>.txt`. This folder is git-ignored. Never copy source text anywhere else.
5. **Find affected pages.** Grep `docs/` for `[src:<id>]` and for the id in front matter. A new source may also need a new page from `PLAN.md`.
6. **Draft.** For each affected page, run the `summarizer` subagent.
7. **Verify.** For each drafted page, run the `verifier` subagent in a fresh context. Never let the summarizer verify.
8. **Fix loop.** If the verifier reports FAIL, send the failing claims back to the summarizer. Maximum 2 fix rounds; then stop and report the remaining failures to the user.
9. **Finalize.** On PASS: set the page's `status: verified` and `last_verified` to today. Update the source's `status: verified`, `last_verified` and `content_hash`.
10. **Check.** Run `python scripts/validate.py` and `pytest`.
11. **Clean up.** Move `.cache/<id>.txt` into `.trash/` and tell the user it can be deleted.
12. **Report.** Show the user: pages changed, verifier tables, overlap results, and the diff. Do not commit to `main`.
