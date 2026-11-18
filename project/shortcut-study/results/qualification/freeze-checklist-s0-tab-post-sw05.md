# Main protocol freeze — s0-tab candidate (POST-SW05 PREP)

Status: **unsigned prep checklist** after SW05 CPU acceptance (`91baf90`).  
Supplements (does not replace) `freeze-checklist-s0-tab-draft.md`.  
**Do not sign.** G3 = `not_started`. Provisional `configs/frozen/s0-tab-v0/` may exist for SW07-C review but is **not** a signed freeze.

Held-out G2 actor evidence is on main (`#55` / `c3db94e`; ECE-77 books `gates.G2=accepted`).  
Freeze **signature** remains blank pending Yehia/root process — **do not soft-sign**.  
This document does not authorize a second GPU worker or a v6 fresh batch.

## CPU prerequisites now available (still not a freeze)

- [x] Catalog/batch identity repairs on main (RD1–3 / #29); fresh batch id `qual-fresh-tab-catalog-v3-001`
- [x] Bound audit prep + task-specific metrics + generator-version stamping fix (#30/#32/#33)
- [x] Analysis estimands / release retention / denominators language (#31); protocol JSON synced
- [x] Integrator wiring + independent SW05 accept (#33); suite 254 OK
- [x] Consumed batches labeled; catalog-v2 marked regression (not fresh)

## Still blocked before any real freeze signature

- [x] **Fresh** held-out G2 PASS on content-disjoint batch (SW06) — `qual-fresh-tab-catalog-v5-001` **PASS** (completion 315/320; parse 156/156; easy 20/20); packaged `#55`/`c3db94e`; ECE-77 books `g2_accepted=true` / `gates.G2=accepted`; v3/v4 FAIL archives preserved consumed
- [x] G1 scientific closure recorded with long-pilot + runtime/isolation/scorer evidence (SW07-A / ECE-79) — pack `results/qualification/g1-scientific-closure-sw07a-v1.json`; booked `gates.G1=accepted` on tip `937248b` / `#57`; long-pilot 9/10 disclosed partial; **not** freeze
- [x] **Semantic scope XOR closed (SW07-B / ECE-80):** explicit **behavioral-only** S0 + **semantic withdrawal** — judge qualification **not** selected before freeze. Evidence: `handoffs/2026-11-18-sw07-b-semantic-scope.md`, `results/qualification/sw07-b-semantic-scope-v1.json`. Independent review ≠ author still required before merge/use as freeze input.
- [ ] Pre-freeze analysis simulation at candidate scope (A1–5 tooling ready; simulation not a freeze) — **behavioral estimands only** under withdrawn semantics
- [ ] Measured actor (+ non-semantic audit-prep if any) forecast with reserve fitting cutoffs — **no** live judge GPU budget under this scope
- [x] Materialized main schedule + pinned hashes under `configs/frozen/<version>/` — **provisional unsigned** `configs/frozen/s0-tab-v0/` (SW07-C / ECE-81); runners still reject until signature
- [x] Guarded executable main path implemented and regression-tested (do not merely delete refusal) — `shortcut_study.freeze` + `tests/test_frozen_main_path.py`; draft refusal tests retained
- [ ] Independent freeze reviewer signature on checklist with actual evidence (Yehia/root — **not** soft-signed by orchestrator; SW07-C author ≠ freeze signer)

Freeze commit / timestamp / accepting owner:

_None — deliberately blank. G1/G2 evidence + SW07-B semantic withdrawal + SW07-C provisional frozen path ≠ freeze signature. Do not soft-sign._

Accepted evidence paths for freeze:

_G1+G2 scientific evidence recorded; semantic-scope decision recorded; provisional frozen materialization + guarded path (unsigned); freeze signature still pending:_

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
- provisional frozen: `configs/frozen/s0-tab-v0/`
- guarded path: `handoffs/2026-11-18-sw07c-guarded-frozen-main.md`
- guarded path: `results/qualification/sw07c-guarded-frozen-main-v1.json`
- prep-only: `handoffs/2026-11-17-sw07-freeze-prep.md`
- prep-only: `results/qualification/sw07-freeze-prep-v1.json`
- prior draft: `results/qualification/freeze-checklist-s0-tab-draft.md`
