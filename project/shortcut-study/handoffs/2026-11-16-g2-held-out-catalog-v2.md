# Package handoff — G2 held-out after tab-catalog-v2 (S0) — FAIL

- Owner and role: GPU operator on DESKTOP-VEMMES3 (WSL2, RTX 3070 Ti).
- Status: ready_for_review — actor held-out **FAIL** (evidence preserved; do not self-merge).
- Input commit and dependencies: `main` @ `18f2b9f` (PR #24 tab-catalog-v2 public-task port).
- Output: branch `cursor/g2-held-out-catalog-v2-2c86`; tracked evidence + this handoff; raw archive under ignored runs/.
- Paths changed: `results/qualification/g2-held-out-20261116-catalog-v2.json`, this handoff, state/README notes.
- Prior FAIL preserved untouched: `g2-held-out-20261116` / [PR #23](https://github.com/Yehia-Fahmy/ece750-work/pull/23).

## Command and outcome

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
export PYTHONPATH=project/shortcut-study/src
python3 -m shortcut_study qualify-local \
  --held-out \
  --out project/runs/shortcut-study/g2-held-out-20261116-catalog-v2 \
  --port 18089
# EXIT 1 — local_development_check_passed=false (native capture requires 320/320 completed)
```

| Metric | Value |
| --- | --- |
| Assigned | 320 (qualification split; all difficulties × TAB01–05 × 16 cells) |
| Terminal | completed 239 / model_format_failure 27 / budget_limit 54 |
| Terminal completion | **74.69%** (gate ≥95%) |
| Parseability among complete+completed | **111/111 = 100%** (gate ≥99% among that subset) |
| Easy no-shortcut legitimate success | **11/20 = 55%** (trivial+complete+sc-absent; gate ≥80%) |
| Easy per template | TAB01 4/4; TAB02 **0/4**; TAB03 2/4; TAB04 3/4; TAB05 2/4 |
| Mean episode latency | ~30.3 s; p95 ~48.6 s |
| Sampled peak / headroom | 5371 / 2821 MiB |
| Wall including startup | ~9755 s (~2.71 h) |
| `g2_accepted` in summary | false |
| Main executed | **no** |

Pre-held-out cheap development smoke (TAB02–05 trivial V00 sc-absent, 8 eps): completed 5 / budget_limit 2 / model_format_failure 1 — archived under `project/runs/shortcut-study/dev-smoke-tab02-05-catalog-v2` (not scientific).

## Gate table

| Gate | Result |
| --- | --- |
| G2-GPU-2 | **FAIL** — completion 74.69% < 95% (parseability OK on completed complete cells) |
| G2-GPU-3 | **FAIL** — easy authorized success 55% < 80%; TAB02 easy 0/4 (format failures) |
| G2-GPU-5 | not run (judge / semantic withdrawal) |
| G2-GPU-6 | partial — held-out latencies recorded; prior G1 long pilots unchanged |

## Comparison to prior FAIL (#23)

| | #23 `g2-held-out-20261116` | this `…-catalog-v2` |
| --- | ---: | ---: |
| completed | 238/320 (74.38%) | 239/320 (74.69%) |
| budget_limit | 54 | 54 |
| model_format_failure | 28 | 27 |
| easy success | 11/20 (55%) | 11/20 (55%) |

Catalog-v2 did **not** clear G2. Do not soft-wash.

## Evidence hashes (`g2-held-out-20261116-catalog-v2`)

| File | sha256 |
| --- | --- |
| `summary.json` | `9b1793bfebca51255ce61e61940d78f7d5548033573f126c765e67fdb038b00d` |
| `manifest.json` | `4388671cd30fc77576a7155a08e27084fe91fabeeb579448bf5fbddf90e8d153` |
| `schedule.json` | `7a27bcdf5945e07b5e9d7d6a1d853b997d025e3daf7b7793e0f5da70d75ee23f` |
| `source-manifest.json` | `6a3c01dea08d8e47f2d7ca4f3362de515d8806a1519345af7420b96273e1b3e0` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

- Raw: `project/runs/shortcut-study/g2-held-out-20261116-catalog-v2` (26472 files)
- Tracked: `results/qualification/g2-held-out-20261116-catalog-v2.json`

## Limitations / next safe action

- Do **not** mark `gates.G2` accepted.
- Do **not** start WP09 main collection.
- Do **not** retune prompts against qualification contrasts.
- Preserve both FAIL archives; no silent denominator edits.
- Honest next lever discussion: arm S4 or a new development-only fix — not a second soft re-held-out without a real lever.
- Reviewer: independent lagging review; operator must not self-merge.

## GPU lease

Released (`qualification-operator` / `native-held-out-qualification` / `g2-held-out-20261116-catalog-v2`).
