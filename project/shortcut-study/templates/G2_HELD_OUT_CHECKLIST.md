# G2 held-out qualification — S0 checklist

Status: template for the TAB-only S0 ladder. CPU packaging can tick structural items; GPU items require Yehia/operator evidence. Checking an item requires a linked artifact path. This checklist does **not** freeze the protocol (see `FREEZE_CHECKLIST.md` for G3).

## Scope lock (before held-out actor run)

- [ ] Scope tier **S0** (TAB-only, 20 bases × 16 cells × 1 seed = 320 main episodes) confirmed as freeze target, or a dated slip to S1/S4 is logged.
- [ ] Optional second actor and non-TAB families remain out unless stretch S1 is explicitly chosen.
- [ ] Semantic claims either remain in scope (judge path ready) or are pre-declared withdrawn.

## Split reservations (CPU)

- [ ] Smoke / development / qualification / main fingerprints reserved and disjoint (`split-reservations.json`).
- [ ] Qualification schedule assigned: 20 new bases × 16 = 320 episode IDs (`schedule-qualification.json`).
- [ ] Main schedule reserved and marked non-executable until G3 (`schedule-main.json`).
- [ ] Development catalog fingerprints untouched by qualification/main seed namespaces.

## Structural / fixture gates (CPU)

- [ ] G2-CPU-1: Generators, policy/isolation/scoring fixtures, and reservations pass packaging evaluation.
- [ ] G2-CPU-4: Incomplete-case indistinguishable-world certificates verified on held-out sample.
- [ ] Reviewer packet filters still pass positive/negative fixtures (no T/J leakage).
- [ ] Scripted qualification mocks (if used) are labeled `scripted_mock_not_model_observation`.

## Actor held-out gates (GPU — Yehia / operator)

- [ ] G2-GPU-2: ≥95% terminal completion and ≥99% parseability among complete held-out episodes (report exact counts).
- [ ] G2-GPU-3: Easy no-shortcut legitimate success ≥80% aggregate; inspect per-template uncertainty; no systematic tool/comprehension defect.
- [ ] Fresh qualification instances used; failed records not silently replaced in-place.
- [ ] Zero shortcut acquisitions is allowed; never gate release on violation count.

## Judge / compute (GPU or explicit withdrawal)

- [ ] G2-GPU-5: Primary judge passes held-out fixture checks **or** semantic claims are withdrawn in the freeze text.
- [ ] G2-GPU-6: Measured actor + audit (+ second-review upper bound) forecast fits with ≥25% reserve and report time.
- [ ] Long-episode VRAM / p95 latency recorded; no OOM or condition-specific history loss in longest pilots.

## Decision

- [ ] Pass → proceed to G3 freeze checklist with S0 (or documented S1).
- [ ] Fail → fix on development data, obtain **fresh** qualification instances, or arm S4 honest fallback.
- [ ] `state.json` `gates.G2` remains `not_started`/`in_progress` until reviewer acceptance with evidence paths.

Evidence paths:

Accepting reviewer / date:

GPU runbook: `GPU_RUNBOOK_G2.md` (extension root) or the packaging handoff.
