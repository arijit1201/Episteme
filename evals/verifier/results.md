# Verifier eval results

Run date: 2026-10-30. Cases: `planted_errors.yaml` (20 wrong claims, 10 correct claims).

## Verdict

**The verifier meets the Phase 2 bar.**

| Measure | Result | Bar |
|---|---|---|
| Wrong claims caught (any verdict other than SUPPORTED or OPINION_OK) | 20 of 20 | at least 18 of 20 |
| Wrong claims with the exact expected verdict | 18 of 20 | not required |
| Correct claims wrongly rejected | 0 of 10 | at most 1 of 10 |

`.claude/agents/verifier.md` was not changed.

## Method

- One `verifier` subagent run per case, 30 runs, no retries. Each run saw only the claim and the source id. It never saw the expected verdict or the `evidence` note.
- The verifier found no `.cache/<id>.txt` files, so every run fetched the live source with WebFetch.
- Ground truth for the cases was gathered from the same live sources on the same day by separate research runs, then written into the cases by hand.

## Per-case results

| Case | Expected | Got | Caught or accepted |
|---|---|---|---|
| w-multiagent-tokens | CONTRADICTED | CONTRADICTED | caught |
| w-reflexion-number | CONTRADICTED | CONTRADICTED | caught |
| w-sweagent-numbers | CONTRADICTED | CONTRADICTED | caught |
| w-tools-limit | CONTRADICTED | CONTRADICTED | caught |
| w-subagent-tokens | CONTRADICTED | CONTRADICTED | caught |
| w-bea-date | CONTRADICTED | CONTRADICTED | caught |
| w-autogen-active | CONTRADICTED | CONTRADICTED (2 sub-claims) | caught |
| w-12factor-list | CONTRADICTED | CONTRADICTED | caught |
| w-12factor-order | CONTRADICTED | CONTRADICTED | caught |
| w-weng-components | CONTRADICTED | CONTRADICTED | caught |
| w-passk | CONTRADICTED | CONTRADICTED | caught |
| w-mcp-semver | CONTRADICTED | CONTRADICTED | caught |
| w-12factor-license | CONTRADICTED | CONTRADICTED | caught |
| w-react-finetune | CONTRADICTED | CONTRADICTED | caught |
| w-reflexion-weights | CONTRADICTED | CONTRADICTED | caught |
| w-toolformer-rlhf | CONTRADICTED | CONTRADICTED | caught |
| w-harness-agents | CONTRADICTED | CONTRADICTED | caught |
| u-bea-swebench | UNSUPPORTED | UNSUPPORTED | caught |
| m-react-figure | MISATTRIBUTED | UNSUPPORTED | caught (verdict differs) |
| m-compaction | MISATTRIBUTED | UNSUPPORTED | caught (verdict differs) |
| c-12factor-last | SUPPORTED | SUPPORTED | accepted |
| c-12factor-license | SUPPORTED | SUPPORTED | accepted |
| c-multiagent-tokens | SUPPORTED | SUPPORTED | accepted |
| c-bea-date | SUPPORTED | SUPPORTED | accepted |
| c-react-benchmarks | SUPPORTED | SUPPORTED | accepted |
| c-sweagent-numbers | SUPPORTED | SUPPORTED | accepted |
| c-evals-start | SUPPORTED | SUPPORTED | accepted |
| c-weng-components | SUPPORTED | SUPPORTED | accepted |
| c-tools-limit | SUPPORTED | SUPPORTED | accepted |
| c-harness-testing | SUPPORTED | SUPPORTED | accepted |

## What this does not show

- **Misattribution is weak.** Both misattributed claims came back UNSUPPORTED. The verifier checks the cited source only and does not look for the true source. This is fine as a gate, since the page still fails. A reader should not expect a MISATTRIBUTED verdict from it.
- **The cases are easy.** Most wrong claims change a number, a name or a mechanism. No case tests an omission, an overgeneralization, a claim that is true but stale, a quote over the 15-word limit, or an OPINION_OK judgment.
- **Evidence quality is limited.** WebFetch returns a summary written by a small model, not the raw page. Several verifier reports say so. The ground truth has the same limit.
- **Some context leaked.** Verifiers read `sources.yaml`, so a few cited its `published` and `license` fields as extra support (`c-bea-date`, `w-12factor-license`).
- **Single run, one author.** Each case ran once. The cases and the research behind them came from the same session, not an independent author.
- **Dependence on one source's wording.** `w-mcp-semver` relies on the versioning page under the spec URL, which the verifier found. The overview page alone does not state the rule.

## Before trusting it on pages

Pages will be longer and subtler than these claims. Before the first page merges, add harder cases (omission, overgeneralization, stale facts, quote length, opinion handling) and consider cached source text in `.cache/` so checks do not depend on a summarizing fetch.
