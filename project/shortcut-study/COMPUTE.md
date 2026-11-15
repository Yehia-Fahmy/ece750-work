# Local compute, model trials, and scheduling

Planning date: November 15, 2026. No new model was loaded or benchmarked in this planning pass.

## Observed baseline

- Read-only GPU query: NVIDIA GeForce RTX 3070 Ti, 8,192 MiB VRAM, 303 MiB used at the observation, driver 591.86. A point observation is not peak workload memory.
- Host reports about 19 GiB RAM, 5 GiB swap, and 946 GiB available workspace storage. Avoid swap-dependent inference.
- Existing Qwen3-4B Q4_K_M artifact: 2,497,280,256 bytes; configured checksum in `project/configs/main-reduced-v1.json`.
- `project/models` is a symlink to `../.worktrees/research-project-plan/project/models`. Do not delete that worktree, replace the symlink, or overwrite its model. Resolve and record actual paths before use.
- Original llama.cpp runtime is b11574, retained under `project/tools/runtime`. Its compatibility is established for the original one-turn study, not the new tool loop or other model templates.
- Historical main run: 240 one-turn requests, 2,514.31 seconds and 335,139 completion tokens. These are provenance facts, not a forecast for multi-turn agents or semantic judges.

## Candidate order

| Candidate | Proposed role | Reason / qualification requirement |
| --- | --- | --- |
| Existing Qwen3-4B Q4_K_M | Primary actor | Continuity, already available; must qualify native T and tool-loop capture anew |
| Qwen3-8B Q4_K_M | Primary local semantic judge candidate | Official artifact approximately 5.03 GB; must pass fixture/natural pilot checks and full-record/chunk memory tests |
| SmolLM3-3B, pinned documented quantization | Different-family actor and independent-review candidate | Official card documents extended thinking and tool calling; adapter, conversion provenance, and actual task/judge capability remain untested |
| Qwen3-1.7B, pinned quantization | Optional inexpensive scaling/technical fallback | Same-family comparison only; not an independent-family semantic judge and may fail harder tasks |

Trial only enough candidates to choose a qualified primary actor and grader. Model size does not certify judging quality. A candidate acting as a model under study cannot be its own sole semantic judge. If Qwen3-8B becomes an actor, require an independently qualified auditor for its semantic conclusions; otherwise keep it as a judge. Shared-family biases between Qwen actors and judge must be disclosed.

If SmolLM3 is both an actor candidate and a review candidate, it must not serve as the independent reviewer of its own actor episodes. Use another qualified checkpoint for that panel and disclose any shared-lineage limitation, or mark the panel as lacking independent semantic validation. Changing roles is not free: include the additional qualification and review cost before choosing the optional actor.

Official references checked November 15:

- [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B) and [official GGUF listing](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/main).
- [SmolLM3-3B model card](https://huggingface.co/HuggingFaceTB/SmolLM3-3B) and its linked [quantization collection](https://huggingface.co/collections/HuggingFaceTB/smollm3-686d33c1fdffe8e635317e23). Do not assume an official `SmolLM3-3B-GGUF` repository exists; resolve a supported artifact or document a local conversion.
- [Qwen3-1.7B official GGUF listing](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main).
- [llama.cpp tool-calling documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md). Current docs do not prove the retained b11574 has the same features.

Resolve immutable revision, checksum, license, template, and conversion provenance before downloading. Free downloads are allowed by the plan; hosted inference is not. Download to a new ignored extension asset directory, never overwrite an original artifact. If a runtime update is necessary, install a separate pinned runtime for the extension. Do not update old runtime files in place.

## Memory and execution policy

- Exactly one model server/GPU workload at a time. Actors, primary judge, and independent judge run in phases; multiple coding agents do not create extra GPU capacity.
- Start the 4B actor at the known 16k context as a candidate. Start the 8B judge around 8k, then measure. The 5.03 GB weight file alone is not peak memory; KV cache, tool histories, buffers, and display allocations also consume VRAM.
- Record peak GPU allocation, prompt and output token counts, full-offload status, throughput, and p50/p95 episode latency on realistic long cases. Target at least 0.5 GiB observed headroom and no OOM in stress fixtures; this is a heuristic guard, not a capacity guarantee.
- Cache quantization, offloading, decoding changes, and forced thought termination are experimental choices. Pilot and freeze them; do not vary them by visibility condition or silently enable them after OOM.
- Do not silently evict early tool history or T to fit. Either choose a protocol that fits before freeze, use a validated adapter/history representation, or record a context-limit failure. Context budgets include input and output.
- Judge generation need not use the actor's decoding mode. Qualify the exact judge mode/settings. Deterministic request settings do not guarantee hardware-level reproducibility.

## GPU lease and recovery

Use one host-wide lock at the canonical primary checkout's ignored `project/runs/shortcut-study/gpu.lock` (absolute path resolved once by the orchestrator). All worktrees must use that same lock, not their own relative copy. Implement an OS-held exclusive lock, plus owner, PID, host, job, run ID, and heartbeat metadata. Lock release follows process exit; stale heartbeat alone does not authorize killing another process. Inspect the owner and job status before recovery.

The GPU operator is the only role that starts/stops servers or changes the active checkpoint. CPU workers can build fixtures, write code, analyze saved rows, and draft the report concurrently. They should not run memory-heavy jobs that starve the inference process. Stop only owned processes; never use broad process-name kills.

## Forecast the complete pipeline

For each qualified actor/profile, estimate from representative pilot records:

`total seconds = N_actor × mean actor episode seconds + N_audit × mean primary audit seconds + N_second × mean second-review seconds + loading/preflight/recovery overhead`.

Audit latency includes all chunks, reconciliation, and retries under the frozen policy. Judge outputs may themselves include internal reasoning; count all billed-equivalent local tokens and wall time. Record input, generated tokens, and stored bytes separately. Estimate second-review load from flagged prevalence plus the unflagged 10% sample; include an upper-bound scenario where every episode needs review. Use upper uncertainty estimates of means or a conservative pilot forecast, not medians alone for total time.

Illustration only: 3,200 episodes at 30 seconds each take 26.7 GPU-hours. A primary audit averaging 15 seconds adds 13.3 hours. Reviewing 20% again at 15 seconds adds 2.7 hours: **42.7 hours before overhead**. At 90 seconds per actor episode, the same plan exceeds 96 hours before overhead. These numbers are sensitivity examples, not measured new-study speed.

Do not assume 24/7 availability. Until the operator records a schedule, use an explicitly provisional eight GPU-hours/day for planning, never as evidence of reliable unattended capacity. Compute remaining usable hours to the inference cutoff, subtract existing bookings, and reserve at least 25% for failures and variance. Choose the largest scientific tier whose full forecast fits. Preserve report-writing time independently of GPU utilization. If no tier fits, record a scope limitation instead of renting compute.

Batch actor generation by checkpoint and balanced scenario blocks. Run deterministic checks while generating. Schedule enough early primary auditing to detect schema/coverage defects without unblinding effect estimates; checkpoint switches should not be so frequent that loading dominates. No main-run prompt adjustment in response to observed behavior.

## Judge qualification proposal

Use development fixtures to tune, then at least 200 held-out constructed cases covering supported claims, contradictions/denials, hypothetical/revised reasoning, and ambiguous cases (roughly 50 each). Critical fixture labels should derive from deliberately controlled event/text constructions rather than a reference judge's unexplained opinion. Proposed release targets: at least 99% schema/evidence validity, at least 95% precision and 90% recall for critical contradiction/denial labels on the labeled fixtures, and no systematic failure on negatives, revisions, or injection cases. Report counts and confidence intervals; small validation classes cannot establish a very low natural false-positive rate.

Independently audit at least 80 balanced natural development/qualification records where available. This supplies disagreement and coverage diagnostics, not semantic ground truth. Validate longer traces with deliberate cross-chunk revisions. If targets fail, revise on development data and obtain fresh held-out cases. Exact targets and routing are fixed before the held-out judge test.

No free remote endpoint, university GPU, or external judge is an escape hatch. Future orchestrators may coordinate implementation as the researcher configures them, but cannot supply unrecorded actor generations, task-answer observations, or semantic grades using their own cloud inference. Future approval must explicitly change D09 before external experiment compute can be introduced.
