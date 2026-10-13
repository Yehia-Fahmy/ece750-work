# Smoke-test evidence

Live local run completed October 12, 2026 using the configuration in [smoke.json](../configs/smoke.json), official Qwen3-4B Q4_K_M weights, and llama.cpp build `b11574-8bb3cf0d2` on the RTX 3070 Ti. The [generated summary](smoke-summary.json) comes from the raw run manifest and response records using `observer_study summarize`.

| Diagnostic | Result |
| --- | ---: |
| Distinct smoke questions | 3 (one per task) |
| Assigned/returned requests | 24/24 |
| Captured nonempty reasoning traces | 24/24 |
| Complete reasoning-plus-final outputs | 21/24 (87.5%) |
| Parseable answers among complete outputs | 20/21 (95.2%) |
| Output-cap failures | 3 |
| Completed strict-format parsing failures | 1 |
| Total request wall time | 432.6 seconds |
| Reported completion tokens, including reasoning | 57,155 |

All output-cap failures occurred on the logical-deduction smoke question. The parsing failure included `FINAL_ANSWER: (C) Ambiguous`, which the current exact-line parser rejects. Failures are retained, and their accuracy/hint-agreement outcomes remain unknown. Capture works, but the configuration does **not** meet the plan's provisional ≥95% completion and ≥99% parsing gates. Refine the common format instruction and test a larger output/context allowance before the pilot.

The 24 outputs are paired over just three questions. These are technical diagnostics; they do not establish accuracy across BBH, an observer effect, or acknowledgment-label reliability. Acknowledgment labels and the primary contrast remain pending. The summary reports all-assigned bounds for unresolved answer outcomes.

Raw responses, exact formatted prompts, server properties, hardware point observations, and the human-review sheet are in ignored `project/runs/smoke-001/`. Model/runtime downloads and raw data are also ignored. To reproduce the aggregate from retained evidence, run from the worktree root:

```sh
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/smoke-001 --out project/results/smoke-summary.json
```

For a fresh inference run, follow [the project instructions](../README.md), choose a new run directory, and retain any protocol revisions separately.
