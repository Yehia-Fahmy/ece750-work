# Native/audit development integration — November 15, 2026

- Owner: root integrator. The researcher explicitly authorized merging, continued implementation, multiple agents, and review.
- Input: reviewed CPU slice merged locally as `fc18d65` (implementation `5a48821`). Its 45 tests and two repaired evidence-loss defects are recorded separately.
- Output: the commit containing this handoff on `codex/shortcut-native-audit`, for reviewed local integration into `main`. No remote publication is claimed.
- Status: CPU implementation milestone reviewed. WP03/WP05/WP06 remain in progress; no model qualification or scientific gate is accepted.
- Historical protection: all 111 historical files and the design snapshot still match the preservation manifest. Existing model/runtime assets, symlinks, and raw archives remain in place.

## Ownership and independent review

| Owner | Work | Review |
| --- | --- | --- |
| `native_adapter` | `adapters/local.py`, adapter tests/handoff | `review_cpu` inspected transport and native channel boundaries; root integrated |
| `audit_pipeline` | `audit/`, audit tests/handoff | `native_adapter` independently reproduced findings and verified fixes |
| `review_cpu` | `runtime/`, GPU lease tests/handoff | Root inspected locking/worktree/WSL behavior and integration guards |
| root | `runner/native.py`, integration tests, `prepare-audit` CLI, state and evidence | `review_cpu` reviewed native recording/recovery and action validation; root checked final integration |

Workers used disjoint owned paths in the shared implementation branch. Only the integrator performed Git mutations. No worker started a model, server, or GPU workload.

## Concrete behavior

The native adapter uses literal loopback HTTP, a fixed chat-completion route, native `reasoning_content`, and exactly one function call. It preserves response bytes including partial/error bodies, rejects malformed/ambiguous actions, keeps exact linked tool history, and never guesses executable actions from reasoning. Requests have byte caps and a total deadline; redirects, proxies, and automatic retries are absent.

The native development loop requires the canonical repository GPU lease and a successful read-only GPU identity check. It records exact requests, HTTP bytes, parsed reasoning, actions, tool results, and final A/J. It enforces turn/action/wall and token/context budgets without clipping history. An exact template-aware prompt counter is mandatory; without one, generation stays unattempted. Server token counts must match preflight before an action executes. Caller-supplied model/template hashes are recorded declarations, not live identity verification.

Recovery re-extracts saved HTTP and verifies derived responses against the original bytes. Known reasoning and accepted submissions survive interruptions; uncertain operations are never retried or replayed. Duplicate native tool-call IDs are rejected before either resource reads or submission.

The GPU lease uses a stable OS-locked file at the canonical checkout, durable owner/PID/host/job/run/heartbeat metadata, process-exit release, and fork handling. Worktrees resolve to the same lock. Heartbeat age does not grant takeover or authorize killing another process. GPU probing uses PATH or the fixed executable WSL fallback, without a shell.

Audit preparation binds public task/capabilities, paired event requests and responses, action chronology, returned content, acquisition flags, and terminal A/J. It provides full A/T/J/events and necessary tool contents while omitting direct treatment/model identifiers from judge messages. Strict output/evidence validation preserves uncertainty and source passages, all-flagged plus seeded stratified 10% review records exact inclusion probabilities, and reconciliation preserves both original judgments. This validates references and coverage, not semantic truth.

`prepare-audit` builds immutable local requests and manifests from completed episode archives without invoking a judge. Whole-record and overlapping passage chunk preparation are implemented; semantic equivalence of chunked judging remains unqualified. Some insufficiency judgments remain uncertain without additional generator-derived sufficiency context.

## Review findings resolved

- Native HTTP could be saved just before an interruption while T was omitted from the terminal record. Normal sealing and recovery now share raw-to-derived re-extraction and reject altered normalized responses.
- Native duplicate tool IDs were checked only after execution. The check now precedes every action, including submit.
- Audit preparation accepted inconsistent request hashes, event pairing/turns, terminal A/J, delivery/acquisition flags, and trace turns beyond the terminal action. Source validation and regression fixtures now reject those cases.
- Reconciliation accepted unknown/duplicate taxonomy labels; it now validates the exact planned field set and categories.
- Judge JSON with overflowing floats or excessive nesting could prevent durable recording of invalid output. It now retains raw output and returns serializable unresolved findings.

Independent reviewers rechecked their reproductions after the fixes and reported no remaining blockers in the reviewed scope.

## Validation and evidence

Commands run from the repository root:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q
git diff --check
```

Observed results: 107 extension tests passed, 58 historical tests passed, whitespace checks passed, and preservation hashes matched. The extension count is 45 prior CPU/review tests + 20 adapter + 12 native integration + 9 lease + 21 audit tests. Native integration includes all 16 conditions for each of two scripted strategies. HTTP, token counts, and GPU probes in these tests are synthetic; no model inference occurred.

The CLI command below succeeded on an existing mock record and wrote prepared evidence/messages plus a manifest:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study prepare-audit --episode project/runs/shortcut-study/cpu-slice-20261115-shortcut-v2/vs-tab01-reconciliation-001__info-complete__sc-present__vis-V11__seed-0 --out project/runs/shortcut-study/cpu-audit-preparation-20261115-v1
```

- `results/development/native-audit-integration-v1.json` contains source/test/config hashes, test counts, reviewer assignments, and artifact references. SHA-256: `a61a4030a8801eb8f4693849ad042c7e5a875cc9f441915ba0be8c3292151f5f`.
- `results/qualification/hardware/inventory-20261115.json` records a real read-only host query: RTX 3070 Ti, 8192 MiB total, 303 MiB used at observation. SHA-256: `df614b5535bd5edb982e360cfd5d1bf9f7c409659acc077785b8a1c269eb8af1`.
- The initial Python subprocess query in the restricted sandbox returned exit 255 with NVML GPU-access-blocked output. An approved host query succeeded. This distinction is recorded; it is not evidence that inference can run inside the restricted sandbox.

The GPU inventory is a point observation, not a peak-memory, throughput, or capacity qualification. Daily machine availability remains unverified. No active inference job or GPU lease remains.

## Remaining work and next action

Qualify the pinned local server/checkpoint/template and implement/validate exact native prompt token counting, then run the authentic 16-condition development slice under the canonical lease in an environment with GPU access. Do not count synthetic tests as model observations. Complete local semantic judge execution and held-out validation, broader task/scoring families and split reservations, statistical analysis, scope freeze, main collection, and report packaging through the existing work packages. G0/G1 remain open.

The local CPU merge succeeded. Automatic approval review rejected `git push origin main`, stating that publishing to the external default branch required explicit destination approval. That approval was requested and remained pending at this handoff; no alternative publication route was attempted. Continue local authorized work and publish only after explicit approval.
