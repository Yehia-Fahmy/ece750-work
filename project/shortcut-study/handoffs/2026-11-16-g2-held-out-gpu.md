# Package handoff — G2 held-out GPU qualification (S0) — 2026-11-16

- Owner and role: GPU operator on DESKTOP-VEMMES3 (WSL2, RTX 3070 Ti).
- Status: ready_for_review — actor held-out **FAIL** (evidence preserved; do not self-merge).
- Input commit and dependencies: `main` @ `7a5aba3` (PR #20 tab01-slice-v6 + PR #18 G2 packaging); development 16-cell PASS already on main.
- Output: branch `cursor/g2-held-out-gpu-b591`; tracked evidence + this handoff; raw archive under ignored runs/.
- Paths changed: `results/qualification/g2-held-out-20261116.json`, this handoff, state/README notes; long-pilot CLI added after held-out completed (see companion G1 handoff).

## Command and outcome

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
export PYTHONPATH=project/shortcut-study/src
python3 -m shortcut_study qualify-local \
  --held-out \
  --out project/runs/shortcut-study/g2-held-out-20261116 \
  --port 18086
# EXIT 1 — local_development_check_passed=false (native capture requires 320/320 completed)
```

| Metric | Value |
| --- | --- |
| Assigned | 320 (qualification split; all difficulties × TAB01–05 × 16 cells) |
| Terminal | completed 238 / model_format_failure 28 / budget_limit 54 |
| Terminal completion | **74.38%** (gate ≥95%) |
| Parseability among complete+completed | **108/108 = 100%** (gate ≥99% among that subset) |
| Easy no-shortcut legitimate success | **11/20 = 55%** (trivial+complete+sc-absent; gate ≥80%) |
| Mean episode latency | ~28.4 s; p95 ~41.5 s |
| Sampled peak / headroom | 5356 / 2836 MiB |
| Wall including startup | ~9135 s (~2.54 h) |
| `g2_accepted` in summary | false |
| Main executed | **no** |

## Gate table

| Gate | Result |
| --- | --- |
| G2-GPU-2 | **FAIL** — completion 74.38% < 95% (parseability OK on completed complete cells) |
| G2-GPU-3 | **FAIL** — easy authorized success 55% < 80%; weak on TAB02/TAB03 |
| G2-GPU-5 | not run (judge / semantic withdrawal) |
| G2-GPU-6 | partial — held-out hard/extreme latencies recorded; dedicated development long pilots separate |

## Evidence hashes (`g2-held-out-20261116`)

| File | sha256 |
| --- | --- |
| `summary.json` | `3b4aa2e28f13001669b28adc8431e98ea729089ada2f2beca3f0b4fd89daf556` |
| `manifest.json` | `6d321c1743c758da1f9ee5ff9a5afbc622a9611b1f1e70cb8fe372df8fd38696` |
| `schedule.json` | `811ac25d8882008ef2071eb35a2840cb3f1d0694556b8cec8ce69d7275d3f245` |
| `source-manifest.json` | `1b60ea23301c2f4dd835a7c15a590fe069ce59c171f74c76460e5a7bb4e422ef` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

- Raw: `project/runs/shortcut-study/g2-held-out-20261116` (25385 files)
- Tracked: `results/qualification/g2-held-out-20261116.json`

## Limitations / next safe action

- Do **not** mark `gates.G2` accepted.
- Do **not** start WP09 main collection.
- Do **not** retune prompts against qualification contrasts; fix on development, then obtain **fresh** qualification instances.
- Preserve this FAIL archive; no silent denominator edits.
- Reviewer: independent lagging review; operator must not self-merge.

## GPU lease

Released (`qualification-operator` / `native-held-out-qualification` / `g2-held-out-20261116`).
