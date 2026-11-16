# Package handoff — G1 long-episode pilots (WP06 notes) — 2026-11-16

- Owner and role: GPU operator on DESKTOP-VEMMES3.
- Status: ready_for_review — telemetry **recorded**; does **not** alone accept G1.
- Input: after G2 held-out run `g2-held-out-20261116` released the lease; development-split only.
- Output: `--long-pilot` CLI path + evidence/handoff on `cursor/g2-held-out-gpu-b591`.

## Why development split

Pilots must not consume or peek at qualification/main fingerprints. Schedule is fixed: TAB01–05 × {hard, extreme} × complete × shortcut absent × V00 → **10** episodes.

## Command and outcome

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
export PYTHONPATH=project/shortcut-study/src
python3 -m shortcut_study qualify-local \
  --long-pilot \
  --out project/runs/shortcut-study/g1-long-pilots-20261116 \
  --port 18087
# EXIT 1 — native capture requires all terminals completed (9/10 completed)
```

| Metric | Value |
| --- | --- |
| Assigned | 10 |
| Terminal | completed 9 / model_format_failure 1 (TAB02 hard) |
| Mean / p95 episode latency | 31.86 s / 43.14 s |
| Sampled peak / headroom | 5271 / 2921 MiB |
| Split | development |
| `g1_accepted` | false |

## Evidence

- Raw: `project/runs/shortcut-study/g1-long-pilots-20261116`
- Tracked: `results/qualification/g1-long-pilots-20261116.json`
- Companion held-out FAIL: `results/qualification/g2-held-out-20261116.json`

## Next safe action

Integrator may use these notes plus held-out hard/extreme latencies for WP06 forecast drafts. G1 still needs isolation/scorer completeness notes and independent acceptance. Do not self-merge; do not start main.

## GPU lease

Released (`qualification-operator` / `native-long-pilot-development` / `g1-long-pilots-20261116`).
