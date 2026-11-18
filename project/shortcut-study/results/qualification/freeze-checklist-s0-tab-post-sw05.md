# Main protocol freeze — s0-tab-v0 (SIGNED)

Status: **signed freeze** (ECE-87). Yehia authorized freeze / accept G3; walkthrough 1–5 confirmed **2026-11-17 America/Toronto**.  
Supplements (does not replace) `freeze-checklist-s0-tab-draft.md`.  
`gates.G3=accepted`. Frozen tree: `configs/frozen/s0-tab-v0/`.  
Behavioral-only scope unchanged (SW07-B). `submission_authorized=false`. SW08 GPU **not** started by this booking.

Held-out G2 actor evidence is on main (`#55` / `c3db94e`; ECE-77 books `gates.G2=accepted`).  
Independent freeze review of this signature PR must be someone **other than** the PR author before merge.

## CPU prerequisites

- [x] Catalog/batch identity repairs on main (RD1–3 / #29); fresh batch id `qual-fresh-tab-catalog-v3-001`
- [x] Bound audit prep + task-specific metrics + generator-version stamping fix (#30/#32/#33)
- [x] Analysis estimands / release retention / denominators language (#31); protocol JSON synced
- [x] Integrator wiring + independent SW05 accept (#33); suite 254 OK
- [x] Consumed batches labeled; catalog-v2 marked regression (not fresh)

## Freeze prerequisites

- [x] **Fresh** held-out G2 PASS on content-disjoint batch (SW06) — `qual-fresh-tab-catalog-v5-001` **PASS** (completion 315/320; parse 156/156; easy 20/20); packaged `#55`/`c3db94e`; ECE-77 books `g2_accepted=true` / `gates.G2=accepted`; v3/v4 FAIL archives preserved consumed
- [x] G1 scientific closure recorded with long-pilot + runtime/isolation/scorer evidence (SW07-A / ECE-79) — pack `results/qualification/g1-scientific-closure-sw07a-v1.json`; booked `gates.G1=accepted` on tip `937248b` / `#57`; long-pilot 9/10 disclosed partial
- [x] **Semantic scope XOR closed (SW07-B / ECE-80):** explicit **behavioral-only** S0 + **semantic withdrawal** — judge qualification **not** selected before freeze. Evidence: `handoffs/2026-11-18-sw07-b-semantic-scope.md`, `results/qualification/sw07-b-semantic-scope-v1.json`.
- [x] Pre-freeze analysis simulation at candidate scope (A1–5 tooling) — **behavioral estimands only** under withdrawn semantics — SW07-D / ECE-82: `results/qualification/prefreeze-sim-sw07d-v1/simulation-summary.json`
- [x] Measured actor (+ non-semantic audit-prep) forecast with reserve fitting Nov 27 / Nov 29 cutoffs — **no** live judge GPU budget under this scope — SW07-D / ECE-82: `results/qualification/prefreeze-sim-sw07d-v1/forecast.json` (verdict **FITS**)
- [x] Materialized main schedule + pinned hashes under `configs/frozen/s0-tab-v0/` — signed under ECE-87; component hashes pinned in `manifest.json`
- [x] Guarded executable main path implemented and regression-tested — `shortcut_study.freeze` + `tests/test_frozen_main_path.py`; draft refusal tests retained
- [x] Independent freeze reviewer signature on checklist with actual evidence — **Yehia F** (ECE-87; walkthrough 1–5 confirmed 2026-11-17 America/Toronto). Signature PR still requires independent merge review ≠ PR author.

Freeze commit / timestamp / accepting owner:

`571d88865ee3d2d83ea152275b58436fccacc06c` / `2026-11-17T22:45:00-05:00` / `Yehia F`

Accepted evidence paths for freeze:

_G1+G2 scientific evidence; semantic-scope decision; signed frozen materialization + guarded path; pre-freeze sim + measured forecast; Yehia ECE-87 signature:_

- `results/qualification/g1-scientific-closure-sw07a-v1.json`
- `handoffs/2026-11-18-sw07a-g1-closure.md`
- `results/qualification/g1-long-pilots-20261116.json`
- `results/qualification/local-native-v1.json`
- `results/development/cpu-vertical-slice-v1.json`
- `results/development/wp04-scoring-fixtures-v1.json`
- `results/qualification/qual-fresh-tab-catalog-v5-001.json`
- `handoffs/2026-11-17-sw06-fresh-qual-v5-001.md`
- semantic-scope: `handoffs/2026-11-18-sw07-b-semantic-scope.md`
- semantic-scope: `results/qualification/sw07-b-semantic-scope-v1.json`
- signed frozen: `configs/frozen/s0-tab-v0/`
- guarded path: `handoffs/2026-11-18-sw07c-guarded-frozen-main.md`
- guarded path: `results/qualification/sw07c-guarded-frozen-main-v1.json`
- pre-freeze sim/forecast: `results/qualification/sw07d-prefreeze-sim-forecast-v1.json`
- pre-freeze sim/forecast: `results/qualification/prefreeze-sim-sw07d-v1/`
- pre-freeze sim/forecast: `handoffs/2026-11-18-sw07d-prefreeze-sim-forecast.md`
- signature booking: `handoffs/2026-11-18-ece87-g3-freeze-sign.md`
- signature booking: `results/qualification/ece87-g3-freeze-sign-v1.json`
- prep lineage: `handoffs/2026-11-17-sw07-freeze-prep.md`
- prep lineage: `results/qualification/sw07-freeze-prep-v1.json`
- prior draft: `results/qualification/freeze-checklist-s0-tab-draft.md`
