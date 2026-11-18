# Main protocol freeze — s0-tab candidate (POST-SW05 PREP)

Status: **unsigned prep checklist** after SW05 CPU acceptance (`91baf90`).  
Supplements (does not replace) `freeze-checklist-s0-tab-draft.md`.  
**Do not sign. Do not create `configs/frozen/`.** G3 = `not_started`.

Parallel: SW06 fresh qualification is running on user WSL (ECE-42). This document does not authorize GPU work.

## CPU prerequisites now available (still not a freeze)

- [x] Catalog/batch identity repairs on main (RD1–3 / #29); fresh batch id `qual-fresh-tab-catalog-v3-001`
- [x] Bound audit prep + task-specific metrics + generator-version stamping fix (#30/#32/#33)
- [x] Analysis estimands / release retention / denominators language (#31); protocol JSON synced
- [x] Integrator wiring + independent SW05 accept (#33); suite 254 OK
- [x] Consumed batches labeled; catalog-v2 marked regression (not fresh)

## Still blocked before any real freeze signature

- [x] **Fresh** held-out G2 PASS on content-disjoint batch (SW06) — `qual-fresh-tab-catalog-v5-001` **PASS** (completion 315/320; parse 156/156; easy 20/20); v3/v4 FAIL archives preserved consumed; `g2_accepted=true` on v5 evidence; freeze signature still required
- [ ] G1 scientific closure recorded with long-pilot + runtime evidence as required by gates
- [ ] Judge qualification **or** explicit behavioral-only scope + semantic withdrawal before freeze
- [ ] Pre-freeze analysis simulation at candidate scope (A1–5 tooling ready; simulation not a freeze)
- [ ] Measured actor+audit forecast with reserve fitting cutoffs
- [ ] Materialized main schedule + pinned hashes under `configs/frozen/<version>/`
- [ ] Guarded executable main path implemented and regression-tested (do not merely delete refusal)
- [ ] Independent freeze reviewer signature on checklist with actual evidence

Freeze commit / timestamp / accepting owner:

_None — deliberately blank._

Accepted evidence paths for freeze:

_None. Prep-only paths:_

- `handoffs/2026-11-17-sw07-freeze-prep.md`
- `results/qualification/sw07-freeze-prep-v1.json`
- prior draft: `results/qualification/freeze-checklist-s0-tab-draft.md`
