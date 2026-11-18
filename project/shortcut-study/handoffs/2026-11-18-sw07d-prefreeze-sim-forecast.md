# Package handoff — SW07-D / ECE-82 pre-freeze sim + forecast — 2026-11-18

- Owner and role: CPU analyst worker (`bc-cf0d6ec3…`); **not** freeze signer
- Status: ready_for_review — pre-freeze analysis simulation + measured actor forecast recorded; **G3 remains not_started**; freeze signature blank
- Tracker: ECE-82 / SW07-D
- Input commit: `8251978` (`origin/main` tip after #59 SW07-C)
- Output paths:
  - `results/qualification/prefreeze-sim-sw07d-v1/` (simulation releases + stochastic panels + forecast)
  - `results/qualification/sw07d-prefreeze-sim-forecast-v1.json` (index)
  - `configs/frozen/s0-tab-v0/{budgets,analysis_protocol,manifest}.json` (forecast/sim refs; hashes re-pinned; **still unsigned**)
  - `configs/provisional/s0-tab-only/{budgets,analysis_protocol}.json` (mirrored draft status)
  - `results/qualification/freeze-checklist-s0-tab-post-sw05.md` (sim + forecast checked; signature blank)
  - `results/qualification/freeze-checklist-s0-tab-draft.md` (evidence text only; items remain unchecked on draft)
  - `results/qualification/sw07-freeze-prep-v1.json` (blocker text)
  - `tests/test_sw07d_prefreeze_sim_forecast.py`
  - this handoff

## What was run (CPU only)

1. **Deterministic injected-effect recovery** (`T_only`, `J_only`, `both`, `null`) via `analyze-dry` — all contrasts recovered; releases retain hashed inputs.
2. **Missingness / complete-base coherence** — one forced-unknown primary cell; complete-base point matches bootstrap inclusion (A1).
3. **Stochastic Bernoulli panel at candidate S0** (20 base clusters, 10k bootstrap, seed `20261116`) — published expected interval widths / detection diagnostics. Semantics withdrawn; no label-error freeze claims (A2 out of scope).
4. **Measured forecast** from long-pilot hard/extreme p95 (`43.14s`), +15% overhead, ≥25% reserve, provisional 8 GPU-h/day, **no live judge GPU** (SW07-B behavioral-only). Assumed collection start = Nov 22 18:00 America/Toronto if G3 signed.

## Forecast vs cutoffs

| Cutoff | Window / capacity | Required (S0 320 + reserve) | Fit? |
| --- | --- | --- | --- |
| Nov 27 18:00 stop starting actor blocks | 5 d × 8 h = **40** GPU-h provisional | **~5.51** GPU-h | **FITS** (slack ~34.5 h) |
| Nov 29 18:00 end experimental inference | live judge = 0 under behavioral-only | **0** additional GPU-h | **FITS** |

Clarification-only / mixed held-out wall means (~8 s) were **not** used for multi-tool planning (`COMPUTE.md`).

## Explicit non-actions

- Freeze signature fields stay `_None — deliberately blank._`
- Do **not** set `gates.G3=accepted`
- Do **not** flip `submission_authorized`
- Do **not** claim executable main / soft-sign `freeze.signed`
- Do **not** start SW08 from this PR
- Do **not** treat synthetic sim numbers as actor findings or main contrasts

## Commands / outcomes

```bash
PYTHONPATH=project/shortcut-study/src python3 -m unittest \
  project.shortcut-study.tests.test_sw07d_prefreeze_sim_forecast \
  project.shortcut-study.tests.test_frozen_main_path -v
```

(Exact invoke from package root documented in evidence JSON / PR body.)

## Next safe action

- Independent reviewer **≠** this author verifies sim/forecast artifacts, unsigned freeze pins, G3 untouched, and cutoff arithmetic
- Yehia/root may then consider freeze signature only after independent review + remaining human process
- Hold SW08 until signed G3

## Acceptance reviewer, decision, and date (filled on review)

_
