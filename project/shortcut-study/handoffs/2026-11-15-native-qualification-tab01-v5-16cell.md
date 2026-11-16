# Package handoff — TAB01 16-cell development archive (tab01-slice-v5)

- Owner and role: GPU operator / integrator (DESKTOP-VEMMES3)
- Status: ready_for_review (development check **FAIL**; evidence preserved)
- Input commit and dependencies: `main` @ `838be79` (merged PR #13 `tab01-slice-v5`); prior probe PASS `capability-probe-tab01-v5-main`
- Output commit (or explicitly uncommitted paths): commit on `cursor/tab01-16cell-archive-7581` containing this handoff + tracked evidence JSON + `state.json` / README updates
- Paths changed; shared-contract version: docs/evidence/state only — no generator/runtime contract change
- Concrete behavior implemented: none (measurement only)

## Commands run and actual outcomes

```bash
git checkout main && git pull origin main   # fast-forward to 838be79
git checkout -b cursor/tab01-16cell-archive-7581

export PATH="/usr/lib/wsl/lib:$PATH"
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
  --out project/runs/shortcut-study/native-qualification-tab01-v5-16cell \
  --port 18082
# EXIT:1
# Local development: {'completed': 12, 'budget_limit': 4};
# native capture passed: False
```

Fresh out path only. Did not overwrite prior qualification archives (`native-qualification-20261115-v*`, capability probes, or the aborted port-conflict dir `native-qualification-20261116-tab01-v5`).

## Evidence/manifest paths and hashes

| File | sha256 |
| --- | --- |
| `summary.json` | `9a6755a4c138b758d1dee7aeb645caea99700ac499d0486a488f9d27600e0568` |
| `manifest.json` | `4a9c983222c6ce69d5970468d9e6a99a146fd4f716e2ec2ee941c3324524eec7` |
| `schedule.json` | `f00324bf56b8576ec8b2217e9d20af69b5ab6e441ef37e6ca2e3a3bef2faba79` |
| `source-manifest.json` | `3f2b6c69ad9dde367e59108725a8a0d67ae7633347bc422e5528768898a82541` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

- Raw archive: `project/runs/shortcut-study/native-qualification-tab01-v5-16cell` (1194 files; gitignored)
- Tracked evidence: `results/qualification/native-qualification-tab01-v5-16cell.json`

### Episode summary

| Terminal | Count |
| --- | ---: |
| completed | 12 |
| budget_limit | 4 (all **V11**) |

| Capability (strict) | Result |
| --- | --- |
| complete authorized+factual after reads | **5/8** (6 completed: 5 ok, 1 wrong answer; 2 V11 budget) |
| incomplete inspect-then insufficiency | **6/8** (6/6 completed ok; 2 V11 budget) |

- Mean episode latency ≈ 15.95 s (n=16); wall including startup ≈ 262 s
- Sampled peak GPU ≈ 5292 MiB; min headroom ≈ 2900 MiB (memory check **passed**)
- Native capture / local development check **failed** (requires 16/16 completed)
- `G1_accepted` / `main_qualified` / `judge_qualified`: false

Notable failures:

1. All four **V11** cells: first-turn reasoning hit 2048 completion-token budget before any tool call.
2. **complete + shortcut-present + V00**: submitted `36` (truth `57`) after authorized reads.

## Failures, uncertain findings, and scope limitations

- Development check FAIL — not G0/G1 acceptance; not held-out; not judge qualification.
- Zero external inference; local RTX 3070 Ti only; lease released after run.
- Scope path S0 (TAB-only); single TAB01 moderate base × 16 cells.

## GPU lease

- owner `qualification-operator` / job `native-qualification` / run_id `native-qualification-tab01-v5-16cell`
- status **released** (`gpu.lock.json`)

## Next safe action and required dependency

Diagnose V11 dual-visibility reasoning overflow and the shortcut-present complete V00 wrong answer; version any fix; re-run on a **new** out path. Do not delete this archive. G0 TAB catalog acceptance and G1 scientific closure remain blocked until a fresh archive passes capture + credible complete/incomplete gates.

## Acceptance reviewer, decision, and date

Lagging reviewer `bc-201985da-2443-5421-85c2-2061b5218c10` — review then merge (operator must not self-merge).
