# Research log

## October 12, 2026 — initial implementation

- Work is isolated on branch `codex/research-project-plan` in the research-project worktree.
- Reviewed the proposal/plan and official Qwen, BBH, and llama.cpp documentation for inference capture and sampling.
- Resolved and recorded the official BBH revision and Qwen GGUF revision/checksum.
- Downloaded the three BBH task files, verified their formats, and reserved 135 disjoint items: 3 smoke, 6 pilot-development, 6 pilot-validation, and 120 main.
- Implemented matched prompts, deterministic hint/seed schedules, local server preflight, complete response capture, strict scoring, failure-aware summaries, resumption, and blank human-review export.
- Ten standard-library tests passed, including checksum/configuration guards, pairing, trace capture, ambiguous answers, retries, and unresolved outcomes.
- A real-data dry run produced the expected 24 requests; no model outcomes are inferred from that check.
- Downloaded and checksum-verified the official GGUF, llama.cpp b11574 CUDA 12.8 binary, and CUDA runtime. Startup required Ubuntu's OpenMP library; downloaded and checksum-verified its package and extracted it locally without system installation.
- Corrected the initial preflight assumption that enabled Qwen thinking always prefills `<think>`. The official artifact's template instead leaves the assistant prefix open; enabled/disabled template comparison and output capture now verify the supported behavior. Regression checks cover both supported prefixes.
- Completed the live GPU smoke test: **24/24 responses and nonempty reasoning traces captured; 21/24 complete outputs; 20/21 completed outputs parseable**. Three requests reached the 4,096-token cap with no final answer, and one completed response appended option text to the marker and failed strict parsing. All are retained as unresolved outcomes.
- Request wall time totaled 432.6 seconds (about 7.2 minutes), excluding downloads, server startup, and preflight. A point observation during inference showed 4,316 MiB GPU memory used and 3,702 MiB free; this is not a peak-memory measurement.
- Saved [aggregate smoke diagnostics](results/smoke-summary.json), complete raw evidence under ignored `runs/smoke-001/`, and a blank 24-trace human review sheet at `runs/smoke-001/review.csv`.
- Verified live resume leaves all 24 saved response files unchanged and performs no repeated generations. Audited original response bodies, source-item/ground-truth alignment, and the run's implementation fingerprint.
- Shut down the study server gracefully after validation. Existing coursework edits in the original checkout remain unchanged.

### Next implementation decisions

The smoke configuration misses the proposed completion and parsing gates. Before the disjoint pilot, make the common final-answer instruction explicitly forbid explanations/option text on the answer line, then evaluate a larger generation allowance with a matching context budget in a new configuration/run. Preserve this run and record those changes rather than replacing failed responses. Inspect task solvability on pilot examples, and time acknowledgment coding using the exported rubric. Automated labeling and paired statistical analysis remain subsequent milestones.

AI assistance: Codex generated and checked the implementation and draft protocol. The researcher should inspect the prompts/rubric and review smoke traces before freezing the pilot. No paid labeling API calls were made. No researcher-hour measurements or acknowledgment reliability claims are recorded yet.

## October 13, 2026 — refine and preserve the smoke test

- Created branch `codex/refine-smoke-test` in the existing worktree and committed the original harness/results as `332102e` before refinement.
- Added [smoke-v2.json](configs/smoke-v2.json): explicit final-answer-only prompt version `v2`, 16,384 context tokens, and 8,192 output tokens. Original prompt version `v1` remains available and is the default when no version is specified. Native thinking, parser, model, sampling, questions, hints, item seeds, and schedule remain unchanged.
- Added observed quality-gate evaluation and paired `compare-smoke` diagnostics. Dry or unfinished runs cannot pass. Regression checks cover unchanged paired inputs, unchanged strict parsing, threshold boundaries, and rejection of changed pairs.
- **All 13 tests passed.** A new real-data dry run produced 24 requests before live inference.
- Completed a separate live run in `runs/smoke-002/`: **24/24 responses captured, 24/24 complete, and 24/24 parseable**. All responses stopped normally, with one attempt each. All four original failure cases completed and parsed in v2.
- The observed ≥95% completion and ≥99% parsing targets both pass. Request wall time was 344.6 seconds, with 45,230 reported completion tokens and a longest completion of 4,891 tokens. Timing excludes downloads, startup, and preflight.
- Verified all 31 original artifacts against pre-refinement hashes, including the original configuration, prepared items, raw responses, review sheet, and aggregate summary. They remain byte-for-byte unchanged. Saved new aggregate [summary](results/smoke-v2-summary.json), [comparison](results/smoke-comparison.json), and a separate human-review export under the ignored new run directory.
- Verified live resume did not change any v2 response file or repeat generations. A GPU point observation showed 5,485 MiB used and 2,533 MiB free; this is not a peak measurement. Shut down the server after validation.
- Both instruction and allowance changes were evaluated together on the same three development questions. No independent confirmation or population-level reliability is claimed. Pilot-development, pilot-validation, and main items remain reserved and untouched.

Next: run the disjoint pilot, review task solvability, and develop/validate acknowledgment labels and coding-time estimates before freezing the main protocol.

AI assistance: Codex implemented and tested the refinement, audited preserved evidence, and drafted these notes. No paid labeling API calls were made.

## October 14, 2026 — address PR #5 review findings

- Implemented the [remediation plan](pr-5-remediation-plan.md) in the isolated `pr-5-review` worktree on `codex/pr-5-review-fixes`.
- Corrected competing-marker detection across final text while preserving accepted historical formats and unknown-outcome bounds.
- Kept requests nonterminal during retry delays/execution; tested success, exhaustion, interruption in both phases, and resume without replacement. Summaries and resume also recognize legacy errors with an unfinished latest attempt.
- Captured incomplete HTTP bodies as bounded technical failures, retaining readable partial text, lossless bytes, byte counts, and status. Known HTTP statuses keep their retry eligibility; complete non-JSON responses and model failures retain the existing policy.
- Required matching verified weights, runtime, template, and server generation defaults in smoke comparisons. Added independent negative tests for each invariant and compatibility checks for different local paths and the original/v2 profiles.
- All 24 standard-library tests pass. Added a read-only scoring-audit script and a test that it reports score changes and body mismatches without rewriting evidence.
- Rechecked all 48 retained responses: original raw bodies match saved responses, request fingerprints match, and no score field or aggregate changed. Saved the [audit](results/pr-5-scoring-audit.json) and [strengthened comparison](results/smoke-comparison-reviewed.json) as new artifacts. The original comparison's before/after metrics and quality checks are identical.
- Verified all 31 pre-refinement hashes and all 68 files in the pre-fix historical snapshot. Original configurations, prepared data, raw runs, review files, and aggregate results remain unchanged.
- Preserved the implementation-fingerprint guard: historical runs must be resumed with their original implementation; corrected-code collections use fresh directories. No new GPU inference or labeling API calls were performed. The protocol remains draft and pilot/main samples remain reserved.

AI assistance: Codex implemented the fixes, wrote regression tests, audited retained evidence, and updated the documentation. Researcher review and the disjoint pilot remain the next study milestones.
