# Package handoff — TAB01 16-cell development archive (tab01-slice-v6)

- Owner and role: GPU operator / integrator (DESKTOP-VEMMES3)
- Status: ready_for_review (development check **PASS**)
- Input commit and dependencies: follow-up after PR #16 FAIL; new branch (does not amend #16); `tab01-slice-v6`
- Exact sources at GPU run: `80bf93a`; branch later rebased onto `origin/main` @ `916dd8b` (#18) for PR cleanliness
- Output: evidence JSON + handoffs + state/README on `cursor/tab01-slice-v6-fix-7581`
- Paths changed: prompt/budget cues + docs/evidence (no silent rewrite of prior archives)

## Fixes vs v5 16-cell FAIL

1. **V11 first-turn overflow:** tool-first / brief-T cues + development/local `max_per_turn_output_tokens` **3072**
2. **complete+sc-present+V00 wrong 36:** explicit multi-row same-order inclusion + calculate-before-numeric cues (root cause was dropping second O1 delivery)

Soft probe gate unchanged. Unit tests: 209 OK after rebase.

## Commands and outcomes

```bash
# probe (PASS)
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
  --capability-probe --out project/runs/shortcut-study/capability-probe-tab01-v6b --port 18084
# EXIT 0

# 16-cell (PASS)
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
  --out project/runs/shortcut-study/native-qualification-tab01-v6-16cell --port 18085
# EXIT 0; Local development: {'completed': 16}; native capture passed: True
```

## Episode summary

| Metric | Value |
| --- | --- |
| Terminal | **16/16 completed** (0 budget_limit) |
| Complete strict | **8/8** |
| Incomplete strict | **8/8** |
| Prior-fail cells | V11 all completed; complete+sc-present+V00 authorized+factual with calculate |
| Mean episode latency | ~28.6 s |
| Sampled peak / headroom | 5292 / 2900 MiB |
| Capture / local check | **passed** |
| Wall including startup | ~465 s |

## Evidence hashes (`native-qualification-tab01-v6-16cell`)

| File | sha256 |
| --- | --- |
| `summary.json` | `75ec76f19d6fe2fe3740a061d8ec99feac56881b6cba3334b036b49314be5c9a` |
| `manifest.json` | `10a19a4ff1c418c24b79c319fb6f18a469e8917b01821d13e1f9c93bcc330fd9` |
| `schedule.json` | `222f043d6bd0d8ea19112e6f67cc9421321a0f9c1fc47a9ae9d91e06f7f942a8` |
| `source-manifest.json` | `7f808a24d7c64e3de5078e5e0c2db15de7757edef393bde3f177051c702bdfa6` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

- Raw: `project/runs/shortcut-study/native-qualification-tab01-v6-16cell` (1582 files)
- Tracked: `results/qualification/native-qualification-tab01-v6-16cell.json`
- Probe: `results/qualification/capability-probe-tab01-v6.json`

## Limitations / unlocks

- Not held-out; not judge qualification; not G3 freeze; not main collection.
- **G0:** prior `blocked_not_accepted` can be re-evaluated by integrator (PASS archive now exists).
- **G1:** development capture+capability cleared on TAB01 slice; long-episode WP06 pilots still required before acceptance.
- Prior v5 FAIL archive (`native-qualification-tab01-v5-16cell` / #16) preserved.

## GPU lease

Released (`qualification-operator` / `native-qualification-tab01-v6-16cell`).

## Next safe action

Lagging reviewer `bc-201985da-2443-5421-85c2-2061b5218c10` reviews/merges (do not self-merge). Then integrator G0 re-evaluation + long-episode pilots.
