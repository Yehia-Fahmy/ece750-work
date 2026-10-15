# Smoke-test evidence

## PR #5 corrections — October 14, 2026

The [scoring audit](pr-5-scoring-audit.json) checks all 48 retained raw responses with the corrected parser. Every cached score and aggregate remains unchanged. The [reviewed comparison](smoke-comparison-reviewed.json) adds verified model checksum, runtime build, chat-template fingerprint, server generation defaults, and permitted profile differences; its original before/after metrics are unchanged. The archived summaries and `smoke-comparison.json` remain intact.

The fixes pass 24 standard-library tests covering competing answer markers, active retry gates, interruptions/resume, incomplete HTTP bodies and retry limits, independently changed model/backend fields, and the read-only scoring audit. Validation used retained outputs and injected failures without new GPU inference. All 31 originally preserved artifact hashes and all 68 files in the pre-fix historical snapshot still match.

With the ignored raw evidence available, regenerate to fresh output paths:

```sh
python3 project/audit_smoke.py project/runs/smoke-001 project/runs/smoke-002 --out project/results/scoring-audit-recheck.json
PYTHONPATH=project/src python3 -m observer_study compare-smoke project/runs/smoke-001 project/runs/smoke-002 --out project/results/smoke-comparison-recheck.json
```

## Refined run — October 13, 2026

The [v2 summary](smoke-v2-summary.json) and [generated paired comparison](smoke-comparison.json) show that the refined profile meets both requested observed quality targets:

| Diagnostic | Original smoke-001 | Refined smoke-002 |
| --- | ---: | ---: |
| Context allowance | 8,192 tokens | 16,384 tokens |
| Output allowance, including thinking | 4,096 tokens | 8,192 tokens |
| Returned requests | 24/24 | 24/24 |
| Complete outputs | 21/24 (87.5%) | **24/24 (100%)** |
| Parseable answers among complete outputs | 20/21 (95.2%) | **24/24 (100%)** |
| Output-cap failures | 3 | 0 |
| Completed strict-format failures | 1 | 0 |
| Request wall time | 432.6 seconds | 344.6 seconds |
| Completion tokens, including reasoning | 57,155 | 45,230 |

The new prompt requires the final response to contain only the answer-marker line, ending at its closing parenthesis. The parser is unchanged. The comparison verifies identical full item records, conditions, hints, seeds, sampling, and user prompts across all 24 pairs. All four original failure cases completed and parsed in the new run; its longest completion was 4,891 tokens. There were no technical retries or replacements. Live resume left every response file unchanged.

All 31 original configuration/data/run/summary artifacts checked against their pre-refinement hashes remain byte-for-byte unchanged. The original harness is recorded in commit `332102e`. Raw evidence stays in the ignored local run directories; both aggregate summaries are retained in Git.

A GPU point observation during the larger-context run showed 5,485 MiB used and 2,533 MiB free. This is not a peak-memory measurement. The server was shut down after validation.

Both observed thresholds (≥95% completion and ≥99% parsing among completed outputs) pass on these three development questions. This does not establish population-level reliability, a research effect, or readiness of acknowledgment labeling. The instruction and token limits changed together, so improvement cannot be attributed to either alone. The reserved pilot and main sets were not run.

Regenerate the comparison from retained local evidence with:

```sh
PYTHONPATH=project/src python3 -m observer_study compare-smoke project/runs/smoke-001 project/runs/smoke-002 --out project/results/smoke-comparison-recheck.json
```

## Original run — October 12, 2026

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
