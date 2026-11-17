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

- [ ] **Fresh** held-out G2 PASS on content-disjoint batch (SW06) — `qual-fresh-tab-catalog-v3-001` **FAIL** (consumed); ECE-59 #48 merged (`430c86b`, TAB05 extreme 16/16); root-greenlit **ECE-63** collecting a **new** batch id (`g2_accepted=false` until finish)
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
