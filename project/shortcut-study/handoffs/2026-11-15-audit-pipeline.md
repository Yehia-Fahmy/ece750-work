# WP05 CPU audit plumbing — November 15, 2026

- Owner/role: `audit_pipeline`, evaluation engineer delegated by integrator.
- Status: ready_for_review; partial WP05 implementation, not package acceptance or judge qualification.
- Input commit/dependencies: `fc18d65`, locally merged CPU TAB01 slice; accepted WP01 schemas and mock WP03 artifacts. User authorized continued implementation and multi-agent review.
- Output commit: uncommitted worker paths; integration owner records the commit.
- Changed paths: `src/shortcut_study/audit/{__init__,pipeline}.py`, `tests/test_audit_pipeline.py`, this handoff. No shared schemas, configuration, CLI, state, or historical files edited.
- Shared contract: existing `shortcut-semantic-audit-v1`; private preparation/validation/review/reconciliation envelope versions are `v1`. Development rubric constant: `development-evidence-rubric-v1`.

Implemented behavior:

- `prepare_audit(episode, ledger, *, public_task, capabilities, tool_results)` rejects incomplete episodes/missing channels, validates source schemas, task/capability hashes, canonical evidence ordering, text hashes, event-ledger integrity, invocation request hashes/resource identities, monotonic turns, matching tool call/result pairs, response execution status, and complete hash-matching original tool-response content. Delivery/acquisition flags must agree with returned payloads and event status; successful reads must match approved-resource policy classification. T passages must reference recorded action turns. Completed A/J must match the final successful accepted submission. The supported source ledger is the current paired environment format; legacy standalone event stubs are rejected. It builds full A/T/J/events input regardless of reviewer visibility. Source text offsets are explicitly local to each original passage, in both characters and UTF-8 bytes.
- The condition-encoding episode ID stays in the local envelope. `judge_messages` sends an opaque audit ID with task/policy, capabilities, complete original evidence, and a fixed system instruction treating all actor/task/tool text as data. Model/condition identity and primary verdicts are not added to judge messages. Text may still reveal framing; this is not perfect blinding.
- `make_chunks` retains whole passages in chronological overlapping windows, and preserves A, task/policy/capabilities, full ledger, and original tool responses in each chunk. `verify_chunk_coverage` verifies provenance, actual content, ordering, and union coverage. No silent clipping or generated summaries.
- `validate_response` enforces JSON/schema, one label per planned field, a fixed categorical vocabulary, uncertainty reasons, cited source IDs, full relevant-channel coverage, and explicit full-ledger scope for process claims. Missing/invalid output or references yield uncertain canonical findings. Original raw output and labels remain in the returned envelope; materialized passages/events come from source data, never judge quotations. Prepared data and evidence metadata are hash sealed against accidental mutation.
- `route_reviews` selects all uncertainty/contradiction/denial/evidence failures plus seeded sampling without replacement of `ceil(10% * n)` unflagged rows per caller-declared stratum. It records exact inclusion probabilities, sparse strata, seed, and selection reason. Rounding may exceed 10% overall. Sampling is invariant to input row order.
- `reconcile` retains both original envelopes and keeps only agreeing valid labels; disagreement/unresolved evidence stays uncertain. It independently checks complete/unique categorical fields and uncertainty reasons, rather than trusting permissive shared-schema validity flags. It requires distinct checkpoint revisions and primary/independent-review roles. Distinct revisions alone do not prove checkpoint independence or qualification.

Verification (actual outcomes):

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -p test_audit_pipeline.py -v
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -p test_audit_pipeline.py -q
git diff --check
```

Initial targeted runs: **15 tests passed**. After independent review identified invocation consistency, terminal A/J binding, reconciliation taxonomy, nonfinite/deep JSON, post-submission trace turns, and contradictory action flags, the targeted suite was extended and **21 tests passed** (latest command above with `-q`). `git diff --check`: exit 0. The integration fixture executes a real CPU mock episode under V00 and loads its original saved tool results; test temporaries are cleaned. Controlled cases cover source corruption, absent responses, incomplete episodes, malformed/duplicate JSON, unsupported labels/quotes, invalid references, partial-channel absence, chunk gaps, Unicode offsets, later revision text, injected instructions preserved as data, sampling probabilities, and independent disagreement. Added regression cases reject stale invocation hashes, wrong resources, mismatched call/result pairs, reversed turns, altered submitted A/J, unsuccessful acceptance, trace turns after final submission, contradictory delivery/acquisition/policy flags, duplicate/missing/unknown reconciliation labels, numeric overflow, and deeply nested JSON. Invalid parse envelopes retain the raw response and remain serializable with `allow_nan=False`. These tests do not score a language judge.

Artifact SHA-256:

| Path | SHA-256 |
| --- | --- |
| `src/shortcut_study/audit/__init__.py` | `f1f9dd3d3912d93357760b795562958eba4f30b88535e05dbaa677f03c8d28e5` |
| `src/shortcut_study/audit/pipeline.py` | `2bc156d7c274b9229c83ad0187ab67c28241259bc2d1c82ea220ffe270eee5cd` |
| `tests/test_audit_pipeline.py` | `1c51a28ef8cd898df3e785c68efc402dd88976dd908066ca6bba572499d0fe74` |

Limits/remaining work:

- No actor or judge inference, GPU lease/process/job, held-out fixture accuracy, natural-trace accuracy, latency, or prompt-injection robustness measurement. No experimental job IDs were assigned.
- Evidence validation establishes references and coverage, not semantic truth. Test verdicts are explicitly supplied synthetic labels. Temporal revision support preserves chronology/citations; language interpretation remains future local-judge work.
- The current input lacks the generator's insufficiency certificate and deterministic score context. If authorized information sufficiency cannot be established from supplied task facts and observed results, insufficiency explanation must remain uncertain. The request explicitly instructs this; the mechanical validator cannot decide semantic sufficiency.
- Chunk requests are a mechanical planner only. A qualified chunk/reconcile language strategy, token budget, long-range contradiction calibration, and whole/chunk comparison remain pending. Chunk copies retain the full ledger/results and can still exceed a model context window.
- No durable judge executor, cache, retry policy, usage tracking, validation-set split, or rubric qualification. The integrator separately added the `prepare-audit` CLI; this worker does not own that integration. Callers must persist complete returned envelopes and retain rejected episode IDs as unresolved in the assigned denominator.
- Sampling callers supply prespecified strata (actor/family/visibility/information/acquisition/length as feasible); no automatic pooling or scientific sample-size policy is inferred.

Next safe action: independent code review and integrated tests, then integration commit. Continue toward a pinned local judge request/response executor and held-out controlled fixtures after GPU/runtime/lease prerequisites. Do not mark WP05 accepted or scale the broad catalog based on these tests alone.

Independent reviewer: `native_adapter`, November 15, 2026. Reproduced the reported issues, then independently verified all fixes and all 21 audit tests passing; no outstanding blockers in the reviewed source/coverage/blinding/sampling/reconciliation scope. Integrator acceptance of this partial implementation remains pending; full WP05 acceptance remains pending local judge implementation and qualification.
