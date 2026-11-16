# Local native qualification stage — November 15, 2026

Owner: root integrator and sole GPU operator. The researcher authorized implementation of the next stage after local runtime qualification and an authentic 16-condition development slice were described; earlier multi-agent, review, merge and destination publication instructions remain in the session.

## Outcome

The local runtime/recording path works with the preserved Qwen3-4B Q4_K_M checkpoint and llama.cpp b11574 on the RTX 3070 Ti. The actor is **not ready for main collection**: in both completed development runs it requested clarification and submitted insufficient information in all 16 cases, scoring 0/8 on complete-information cases and 8/8 on incomplete cases. These are deterministic scorer results, not language-judge labels. No resource reads, calculations, or shortcut acquisitions occurred in the authentic runs.

No scientific gate is accepted by this milestone. G0/G1 remain open; the judge, held-out actor capability, representative long-case performance, and full study budget remain unqualified. No main data or semantic model judgments were produced. Historical work remains unchanged.

## Implementation and ownership

- `native_adapter`: exact pinned-runtime token counter, lossless request/response evidence, Qwen rendered reasoning/tool-result/tool-call retention checks; later neutral task-metadata correction and regressions.
- `review_cpu`: pinned local asset inspection, owned offline server lifecycle, canonical lease enforcement, listening-process identity, full GPU-offload verification, bounded readiness/cleanup, and parent-death protection.
- `audit_pipeline`: sampled GPU telemetry, independent root integration review/regressions, and independent reproduction of both completed archives/audit preparations.
- Root: qualification CLI, schedule/denominator preservation, native timing/deadline integration, immutable manifests, integration tests, GPU operation, final evidence/state/docs and Git integration.

The counter/server workers cross-reviewed one another. Telemetry was independently reviewed by `review_cpu`; root orchestration was independently reviewed by `audit_pipeline`; the prompt correction was independently reviewed by `review_cpu`. All workers respected source ownership; only root started model servers or mutated Git.

The new command is:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local --out project/runs/shortcut-study/NEW_RUN --port 18080
```

It assigns 16 development cases before loading the model; starts the owned offline single-slot 16k server under the shared lease; captures exact native T/tool/A/J; checks prompt/token/history identity; scores, verifies recovery, prepares full audit input; preserves failed/unattempted assignments; and stops the owned server before releasing the GPU. No retries or main-run CLI are supplied. Success means native capture plus sampled-memory checks, not actor task or judge qualification.

## Actual execution and immutable lineage

| Run | Exact source | Observed result |
| --- | --- | --- |
| `native-qualification-20261115-v1` | Pre-logging-fix source hashes retained | Startup rejected: default verbosity omitted full-offload diagnostics. All 16 assignments unattempted; no actor generation. Owned server exited cleanly. |
| `native-qualification-20261115-v2` | `859fd45` (all 44 source/config/schema hashes matched) | 16 completed, 32 native turns/count matches, 16 verified audit inputs; 20,284 completion tokens. Mean episode 10.46s, p95 17.27s. Sampled peak 5,280 MiB, minimum sampled headroom 2,912 MiB. |
| `native-qualification-20261115-v3` | `60aa979` (all 44 source/config/schema hashes matched) | 16 completed, 32 native turns/count matches, 16 verified audit inputs; 15,536 completion tokens. Mean episode 8.07s, p95 9.67s. Sampled peak 5,278 MiB, minimum sampled headroom 2,914 MiB. |

Each completed run has 701 hashed archive files. All 32 native turns per run contained nonempty observable reasoning. The actual rendered histories retained prior reasoning, tool results, and structured tool names/arguments; the raw response bytes and token-ID arrays were independently checked. The server reported all 37/37 layers offloaded. Telemetry had zero errors (166 samples in v2; 129 in v3). Sampling may miss brief peaks; these figures are not true peak allocation or forecasts for longer tasks/audits.

V2 exposed an incorrect public field: `missing_prerequisites: [return_quantity]` appeared even when all authorized data was complete. The reviewed generator-v2 change renames it to neutral `clarification_fields` while preserving identical public tasks across information states, resources, policy, hidden worlds, seeds and scoring. This factual metadata correction is separately committed and versioned; it did not resolve the observed actor behavior. V2 was not overwritten or relabeled. These repeated development records are not independent main observations or a held-out capability test.

The initial startup failure was corrected by explicitly enabling diagnostic logging; the strict full-offload requirement was retained. The failed initial attempt remains available. No external inference, remote GPU, paid service, or download was used. Original model/runtime symlinks and files remain in place.

## Review findings resolved and verification

Review found and fixed: attempted generations could be mislabeled unattempted after processing/storage errors; memory-telemetry failure/headroom was not part of command success; counter calls did not receive the remaining episode deadline; metadata transport could exceed its total deadline or accept a truncated body; and rendered native actions needed explicit retention checking. Regression tests cover these failures. Raw HTTP is saved before auxiliary timing evidence.

Commands and actual results:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
# 168 passed
PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q
# 58 passed
git diff --check
# passed
```

All 111 historical tracked files and the design snapshot match their preservation manifest. Review independently rehashed all artifacts, runtime libraries/executable, and the 2,497,280,256-byte model. Completed audit requests/messages and deterministic scores were reconstructed exactly without further inference. See the separate [independent review](2026-11-15-local-qualification-review.md).

After v3, the host PID query confirmed the owned server process was absent; GPU memory returned to 303 MiB with 0% utilization, and the canonical lease was released. The read-only host observation is recorded in `results/qualification/hardware/post-run-20261115.json`. No GPU job remains active.

## Evidence and next action

Raw evidence is retained under the three ignored `project/runs/shortcut-study/native-qualification-20261115-v*` directories. The committed `results/qualification/local-native-v1.json` contains run manifests/summary hashes, lineage, real metrics, test outcomes and review references. Its SHA-256 is 8d17a940b81feb6a1caa66256df14c6eb308ea2d11cda3475c5231241035322b.

Next diagnose the actor's premature clarification using development tool-use capability fixtures, including real authorized reading/calculation and representative long histories. Preserve unsuccessful development data and version any changes before a fresh run. Then complete local semantic judge execution/validation, broader generator/scorer capability, analysis and measured capacity before freezing or collecting main data. Do not infer task capability from passing transport tests or use the short clarification-only latency as a full-study forecast.

Output: the commit containing this handoff, for reviewed integration after `859fd45` and `60aa979`. Final merge/publication status is reported by the root after Git verification.
