# GPU runbook — G2 held-out qualification (S0)

Audience: Yehia / designated GPU operator on the RTX 3070 Ti host (WSL).  
CPU agents stop here: packaging is already on disk; this document is the handoff packet for inference.

## Preconditions

1. GPU lease free; no other llama.cpp / actor / judge server.
2. Canonical checkout with this packaging commit; original model assets via existing symlinks.
3. Actor capability credible on **development** evidence first:
   - `capability-probe-tab01-v5` passed (complete + incomplete).
   - Prefer a fresh **16-cell** development archive under `qualify-local` (not only the 2-cell probe) before spending the 320-cell held-out budget.
4. CPU packaging accepted for review:
   - `configs/development/g2-held-out.json`
   - `results/qualification/g2-held-out-packaging-v1.json`
   - schedules under the packaging `--out` tree (`schedule-qualification.json`, `schedule-main.json`)
5. Do **not** start WP09 main collection from this runbook.

## What still needs GPU

| Step | Command / action | Why GPU |
| --- | --- | --- |
| A. Fresh 16-cell development archive | `qualify-local --out …` (full slice, not `--capability-probe`) | Confirms tab01-v5 path on all visibility cells before held-out spend |
| B. Held-out actor qualification (320) | Native runner on `schedule-qualification.json` under lease | G2-GPU-2 / G2-GPU-3 gates |
| C. Long-episode pilots | `qualify-local --long-pilot` (10 development hard/extreme complete V00 sc-absent; never qualification/main) | Latency / VRAM for forecast (G2-GPU-6 / WP06) |
| D. Judge held-out fixtures **or** withdraw semantics | Local judge executor on constructed fixtures | G2-GPU-5 |
| E. Fill forecast + choose S0/S1/S4 | Spreadsheet / notes from measured times | Freeze input |
| F. G3 freeze | Commit `configs/frozen/<version>/` after checklist sign-off | Not part of G2 packaging |

Tiny smoke on GPU is optional and only if WSL is free and you want transport confirmation; prefer the CPU smoke schedule + development 16-cell archive over burning held-out IDs.

## Suggested command sequence (operator)

```bash
# 0) Environment
cd /path/to/ece750-work
export PYTHONPATH=project/shortcut-study/src

# 1) Confirm CPU packaging (no GPU)
python3 -m shortcut_study package-g2-held-out \
  --out project/runs/shortcut-study/g2-packaging-smoke \
  --mock-difficulties trivial

# 2) Take GPU lease / start owned local server (existing qualify-local path)
#    Use a free port; release lease on failure.

# 3) Development 16-cell archive (still split=development)
python3 -m shortcut_study qualify-local \
  --out project/runs/shortcut-study/native-dev-16cell-after-v5 \
  --port 18080

# 4) Held-out native run (reserved qualification fingerprints; refuses main)
#    Optional: start with --difficulties trivial for a short authentic subset.
python3 -m shortcut_study qualify-local \
  --held-out \
  --out project/runs/shortcut-study/g2-held-out-<date> \
  --port 18080
# Full S0 held-out = 320 episodes. Prefer finishing development 16-cell first.

# 5) Score + gate table from authentic records; fill templates/G2_HELD_OUT_CHECKLIST.md

# 6) Release GPU; record daily availability
```

## Hard rules

- Zero external inference.
- Preserve unsuccessful runs; never delete a failed qualification denominator to “fix” the gate.
- Do not peek at visibility contrasts to retune prompts between development fix and held-out.
- If actor gates fail: return to development fixes; obtain **fresh** qualification instances afterward.
- If calendar forces it: arm **S4** (honest course fallback) rather than shrinking controls silently.

## After GPU success

1. Attach gate counts + archive hashes to the G2 checklist.
2. Integrator updates `state.json` gates.G2 only with evidence paths.
3. Proceed to `templates/FREEZE_CHECKLIST.md` (G3) with reduced-claims text if S0 ≠ original 3,200 plan.
