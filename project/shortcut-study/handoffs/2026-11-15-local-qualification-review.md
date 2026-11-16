# Local qualification independent review — November 15, 2026

- Owner: `audit_pipeline`, independent archive reviewer and telemetry implementer.
- Status: ready for integrator acceptance of development capture integrity only.
- Input: shared `codex/shortcut-native-audit` implementation following the locally merged native/audit stage. The exact measured source is the run's 44-file source/config/schema manifest, not an assumed commit.
- Output: this uncommitted handoff only. No experimental archive or source was edited during review. Root owned all local GPU execution; this reviewer made no GPU queries, network requests, actor inference, or semantic judgments.

## Completed archive checks

Archive: `project/runs/shortcut-study/native-qualification-20261115-v2`.

The read-only verification command was `PYTHONPATH=project/shortcut-study/src python3 /tmp/shortcut-qualification-review.py`, exit 0. The temporary review script's SHA-256 was `4776c0f004062021b71cd41d37ff2f3a0ca2a2ea6f66791118c26d964644f6dc`. It used only saved files and pure parsing, hashing, projection, scoring, and audit-preparation functions. Before the subsequent generator change, it verified:

- All 701 artifact hashes and all 44 frozen source/config/schema hashes; current source manifest exactly equaled the archived manifest at review time.
- The full expected 16 unique development assignments, unchanged assignment fields, 16 completed terminal records, and all saved per-episode metrics. Every assigned episode remained in the summary denominator.
- All 32 native responses reparsed identically from raw HTTP bytes; each had nonempty native T and a native action. All 32 preflight counts equaled both the saved token-array length and the native server's prompt-token usage.
- All 288 token-counter evidence records, including raw request/response body hashes, original request binding, rendered-prompt hashes, token-array hashes, and pure retained-history/tool-call validation against actual saved rendered prompts. This is evidence for the retained runtime/template and these requests.
- All 16 reviewer packets equaled their visibility projections. All 16 deterministic score rows exactly reproduced from the corresponding generated task and terminal ledger.
- All 16 audit inputs and judge-message payloads exactly reproduced from full saved A/T/J/events/results and the task/tool definitions. Their input/output manifests matched, and the condition-encoding local episode identifier was absent from judge messages. No judge was invoked.
- The summary's denominator, status counts, token totals, latency aggregates, and capture fields exactly reproduced from saved per-episode records.
- All 166 telemetry records were successful, with one GPU UUID. Recomputed sampled peak memory was 5,280 MiB and minimum sampled headroom was 2,912 MiB. The saved server readiness evidence records 37/37 layers offloaded; its stop record has exit code 0. Root separately owns host-level shutdown/lease verification.

The summary accounts for 42,640 prompt tokens and 20,284 completion tokens. Mean episode elapsed time is 10.463897 seconds; recorded total wall time including startup is 174.492984 seconds. Wall time is a saved operator measurement, not independently reconstructed from the per-episode durations.

Archive manifest SHA-256: `2bd47ab2ad5ed00fdcc123e75ab50d05c0573e7ebf4017737670b638671bda0e`.

Summary SHA-256: `677da5f42c596a116f97c7923eb3c34ba1096f3ebec794c92bcc7854ce0955d8`.

## Failed attempt and limited behavior retained

The same command verified `native-qualification-20261115-v1` retains all 16 assignments as `not_attempted`, zero saved actor requests, and zero turns. Its recorded failure is `ValueError: full GPU offload is not established by startup logs`. Missing diagnostic logging was corrected for v2 without weakening the full-offload gate; no model inference is recorded for v1.

A separate read-only Python tally of saved action operations, A statuses, and deterministic scorer fields found 16 `request_clarification` actions, 16 `submit` actions, and 16 `insufficient_information` submissions. The deterministic announced score is false for all eight complete cases and true for all eight incomplete cases. These are mechanical labels and counts, not a semantic interpretation of T/J.

Root identified a public-task prompt defect: `missing_prerequisites` was populated even for complete cases. Root assigned a neutral clarification-field rename and generator-version bump to `native_adapter`, with independent review by `review_cpu`. A fresh v3 development archive is planned; v2 must remain intact. This review does not establish that the prompt wording caused the observed behavior. The source freeze was lifted only after the v2 source/hash check; changed generator files must be evaluated against their own future run manifest.

## Review scope and next action

Earlier CPU review established the bounded, durable telemetry implementation (9 mocked tests) and qualification regression checks (10 tests). The separate reviewer found no telemetry blockers. This reviewer also checked the v2 logging-only server correction with the valid-launch, missing-diagnostics rejection, and partial-offload rejection tests: all 3 passed. No additional source tests were necessary to reinterpret the immutable archive.

No blocking integrity finding remains for v2. This is one development scenario, two turns per episode, and a narrow observed action path. It does not validate long/context-boundary episodes, broad task capability, natural resource-reading behavior, semantic audit accuracy, chunk equivalence, an independent judge, a full workload forecast, or G1/G2/main acceptance. Polling can miss memory peaks. Audit inputs lack hidden generator sufficiency certificates, so some insufficiency explanations remain unevaluable from the supplied evidence alone.

Next safe action: accept the archive-integrity review separately from task capability, finish the versioned prompt correction and independent tests, and let the designated GPU operator collect a fresh development archive. Preserve v1/v2 and their original assigned denominators. Integrator records acceptance and future-run provenance in state.

- Acceptance reviewer / decision: pending root integration.

## V3 independent follow-up review

Root completed `project/runs/shortcut-study/native-qualification-20261115-v3` using commit `60aa97922bb7308787fe80dd4cde7add5aa5de77`, including the reviewed neutral clarification-field change and generator v2. No further prompt changes are planned in this stage. V1 and v2 remain preserved.

Command: `PYTHONPATH=project/shortcut-study/src python3 /tmp/shortcut-qualification-v3-review.py`, exit 0. The temporary script's SHA-256 is `87ab302c79fde031dbcf6d821a011540f35778b25736be725ddd877a1b9f005b`. It repeated the full v2 integrity procedure against v3, comparing the telemetry aggregates to its actual samples rather than the earlier run's numeric values.

Actual results:

- 701 artifact hashes and 44 current source/config/schema hashes matched the archived manifests. The complete expected schedule remained 16 unique assignments, with 16 completed terminal records and no reassignment or missing outcome.
- All 32 saved native responses reparsed exactly from raw HTTP bytes. All 32 contained nonempty native T and a native action, with exact preflight/native-usage/token-array prompt-count agreement. All 288 counter evidence records passed the byte/hash checks; retained history and action checks passed against every saved rendered prompt.
- All 16 reviewer projections, deterministic scorer rows, prepared audit inputs, and judge-message payloads exactly reproduced. Audit input/output manifests matched and the local condition-encoding episode IDs remained absent from judge messages. No semantic judge ran.
- The complete per-episode metrics and aggregate summary reproduced: 38,072 prompt tokens, 15,536 completion tokens, mean episode elapsed time 8.070746 seconds, episode p95 9.668974 seconds, turn p95 6.289203 seconds. Recorded wall time including startup is 135.912855 seconds.
- All 129 telemetry samples were successful with one GPU UUID. Sampled peak memory was 5,278 MiB, minimum sampled headroom 2,914 MiB. The saved readiness record establishes 37/37 layers offloaded and the owned server stop record reports PID 62942 exited with code 0. These are sampled memory values, not true peaks; host cleanup is root's separate responsibility.

Archive manifest SHA-256: `c409907c8e55bf846c6d90cff0b32fd557cb6a84a5ed2d0629cf7822e5e462df`.

Summary SHA-256: `bc9c47cc424c9addda96629a85d6a5297ed0bbea0e5745ec58b8163a0289575c`.

A separate deterministic tally again found 16 clarification requests followed by 16 submissions, all with `insufficient_information` status. Announced task score was 0/8 for complete cases and 8/8 for incomplete cases. All 16 scorer records show no shortcut attempt and no acquisition. The real actor did not exercise resource reading, calculation, or acquisition in this run. No language interpretation or causal explanation is inferred from these counts.

V3 therefore passes the reviewed native capture/count/audit-preparation and sampled-memory compatibility checks, while the observed actor behavior remains insufficient for complete-case task capability. No integrity blocker was found. Broad capability, real read/calculate/acquisition paths, long-context operation, language-judge quality, full workload forecasting, G1/G2 acceptance, and main-study readiness remain pending. The saved summary correctly leaves `G1_accepted`, `main_qualified`, and `judge_qualified` false. Preserve this result and its denominator; any future capability work requires its own versioned development evidence.
