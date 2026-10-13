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
