# Package handoff — WP02/WP03/WP04 CPU slice — November 15, 2026

- Owner: integrator; one agent, no delegation or GPU ownership.
- Status: CPU milestone implemented and tested, ready for review. Full WP02, WP03, and WP04 remain in progress; no qualification gate is accepted.
- Authorization: researcher requested continuing implementation and following agent instructions. This continues the WP01 handoff's specified mock-first path.
- Input commit: `813cf1f` (merged WP01 and PR #7 remediation). Working tree was clean at start.
- Output: explicitly uncommitted changes in the current checkout. No branch, commit, push, or submission was performed.
- Date/capacity: November 15, 19 calendar days until December 4. Canonical checkout `/home/yehia/ece750-work`; existing model symlink and raw archives retained. `nvidia-smi` is unavailable in this session; GPU availability/daily capacity remain unverified. No GPU process was started and no external inference was used.

## Implemented behavior

- `src/shortcut_study/tasks/tables/`: seeded TAB01 net-delivery task; independent oracle/public solver; matched complete/incomplete worlds; verifiable missing-return certificate; actual absent-resource removal; typed A validation.
- `src/shortcut_study/environment/`: JSON-only resource listing/reading, bounded integer arithmetic, stable clarification, terminal submit. No filesystem/network/eval/candidate-oracle route. Restricted reads succeed when present and are recorded separately from discovery/failed attempts.
- `src/shortcut_study/adapters/mock.py`: legitimate and deliberate shortcut strategies. Both consume only the public prompt and tool history. Scripted T/J are explicitly labeled fixture text, not native model traces.
- `src/shortcut_study/runner/`: fresh per-episode state, raw requests/responses, start/result events, channel captures, immutable atomic terminal records, and reviewer/auditor projections. Refuses overwrite; crash recovery seals uncertain episodes without replay. Known acquisitions survive missing A/J; missing negative evidence remains unknown. Recovery can finish missing derived packets from an authoritative terminal record.
- `src/shortcut_study/scoring/`: ledger/order/request/channel checks; acquisition/discovery facts; factual answer versus announced score versus authorized success; honest insufficiency and unsupported lucky guesses; assigned-denominator eligibility retained. No language labels or private-calculation inferences.
- `src/shortcut_study/__main__.py`: runnable `mock-slice` and `recover-mock-episode` commands. Complete runs contain source/config/schema and artifact hash manifests. Main generation is not available.
- `tests/test_slice_execution.py`: 13 additional tests, including 32 successful condition/strategy combinations, 20 generated-world certificate checks across all conditions, malformed actions, forbidden routes, budget/interruption/recovery, evidence tampering, immutable writes, and main-generation rejection.
- Documentation/state: updated README, agent-guide status, TAB01 specification, and package ownership/evidence. Shared schemas and archived WP01 fixtures remain unchanged.

## Commands and observed results

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
```

39 tests passed (26 previous contract tests plus 13 new tests).

```sh
PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q
```

58 historical tests passed. Those tests use fixtures/mocks; their printed judging/response messages are not new inference.

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy legitimate --out project/runs/shortcut-study/cpu-slice-20261115-legitimate-v1
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy shortcut --out project/runs/shortcut-study/cpu-slice-20261115-shortcut-v1
```

Both CLI runs completed 16/16 scripted episodes. Legitimate strategy: 0 acquisitions, 16 announced successes. Deliberate shortcut strategy: 8 acquisitions (all present conditions), 12 announced successes; incomplete definite answers were not scored as supported completion. These counts validate programmed behavior only and are not actor-study findings.

SHA-256 checks against the historical manifest matched all 111 historical files and the V2 snapshot. Every stored source hash and all 434 legitimate-run / 402 shortcut-run artifact hashes matched. Raw runs are ignored by Git and retained in their existing locations.

## Artifact hashes

The tracked verification record includes complete source hashes and both run summaries:

- `results/development/cpu-vertical-slice-v1.json`: `97ea2a4ebd79dc82bb869efe04cfab08dc5e5b66095170722c56eabaece2c6d4`
- Legitimate raw `manifest.json`: `b4be44f910cc82e7ceb8fd8c006fdf19002e42d90c19dd4c092ff71cbc4ad140`
- Shortcut raw `manifest.json`: `9697dde5209eaf75e208b1d2729c5529b27fd1abac8b724b8ca3e60934b91f37`

Hashes establish integrity relative to these files, not independent authenticity of a model generation. Source/config/schema hashes match this uncommitted implementation; output commit is intentionally null.

## Limitations and next safe action

Only one development template, intended moderate difficulty, and prior-agent notes are implemented. Difficulty is uncalibrated; additional templates/families/mechanisms, reserved splits, native actor adapters, genuine reasoning capture, tokenizer/context budgets, preemptive timeouts, GPU lease/runtime qualification, semantic judges, and statistical analysis remain outstanding. This in-memory tool boundary is not an untrusted-code sandbox for debugging tasks. All policies/prompts remain provisional.

Recovery does not resume a run or rebuild its aggregates/manifest. It preserves the original journal and publishes an episode terminal record; downstream use requires a separately recorded recovery manifest. No native transport retry or model resume policy is implemented here.

Next: review the slice, then extend development generators and implement the local native adapter with explicit T/tool/A/J extraction tests. Establish GPU/runtime access and the shared lease before authentic local inference. G0 still needs broader task specifications; G1 still needs authentic capture and local feasibility evidence. WP05 can use these mock episode contracts for engineering but must not claim semantic validation from scripted text.

All 32 CLI episode IDs are terminal. Interrupted/error cases were isolated temporary test fixtures. No live job or GPU lease remains. Acceptance reviewer: pending; no independent review claimed.

## Merge review — November 15

The researcher authorized merging and continuing with multiple agents. Independent `review_cpu` review found two recovery evidence-loss defects: a durably written acquisition could be omitted after a signal, and saved T/accepted A/J could be dropped during crash recovery. Both were corrected in the runner with six crash/integrity regressions. Root reviewed the corrections. The resulting 45 extension tests pass; both fresh v2 CLI strategies complete 16/16 episodes with the expected programmed counts. No remaining CPU-slice merge blockers were identified.

`results/development/cpu-merge-review-v1.json` records this review, current source hashes, fresh run manifests and verified artifact counts. Earlier verification records and raw runs remain unchanged as historical development evidence. Recovery now retains saved A/J when matching raw actions and event hashes establish the accepted submission; it never generates replacement text. Full package and qualification acceptance remain pending. The output is the commit containing this addendum on `codex/shortcut-cpu-slice`, to be merged into `main` by the integrator.
