# Main protocol freeze — s0-tab-v0 (DRAFT)

Status: **draft checklist only — not an approved freeze.** Every item below is intentionally unchecked. Do not sign. Do not create `configs/frozen/s0-tab-v0/`. Agent review is not human scientific validation (G3).

Scope candidate: **S0 TAB-only**, 20 bases × 16 cells × 1 seed = **320** primary actor episodes. Machine twin: `configs/provisional/s0-tab-only/`.

- [ ] Historical preservation hashes match. Evidence: _pending re-check at real freeze_
- [ ] Scope tier, actor(s), supported families, base scenarios, seeds, assigned denominator, and optional subset are fixed. Evidence: `configs/provisional/s0-tab-only/scope.json` (provisional only)
- [ ] Development/qualification/main instances are disjoint and fingerprints checked. Evidence: `configs/provisional/s0-tab-only/splits_reservation.json` (ranges reserved; fingerprints not yet materialized/verified)
- [ ] Complete-case legitimate solvers and incomplete-case certificates pass. Evidence: _G1/G2 pending; TAB01 v5 probe is not held-out qualification_
- [ ] Shortcut presence/absence, discovery, policy, and sandbox tests pass. Evidence: _partial CPU fixtures; full gate pending_
- [ ] Native T extraction, tool dispatch, A/J separation, and all reviewer filters pass. Evidence: development runtime yes; main-qualified no
- [ ] Exact observation notices, announced scoring, and policy wording are recorded. Evidence: provisional copies under `configs/provisional/s0-tab-only/`
- [ ] Model checkpoint, quantization, runtime/template, context/decoding/history policy, and tool/episode budgets are pinned. Evidence: _hashes TBD at freeze; actor_profile.json is unqualified_
- [ ] Terminal failure, retry, recovery, and stop rules are fixed. Evidence: draft `retry_recovery.json` only
- [ ] Held-out actor gates pass; measured family/difficulty limitations are recorded. Evidence: **G2 not started**
- [ ] Primary judge and any independent reviewer pass recorded fixture gates; natural agreement and rare-class limitations are disclosed. Evidence: **judge unqualified**; default S0 withdraws semantic claims
- [ ] Evidence validation, chunk coverage, review sampling, reconciliation, and uncertainty rules are fixed. Evidence: audit prep exists; live judge pending
- [ ] Paired contrasts, weighting, multiplicity, missingness, rare-event and label-error analyses are frozen and simulation-tested. Evidence: WP07 scaffold + draft analysis_protocol; pre-freeze simulation **not done**
- [ ] GPU schedule and conservative actor+audit forecast fit, including reserve and report time. Evidence: **placeholders only** in budgets.json
- [ ] Source/config/data/model hashes and randomized episode schedule are committed. Evidence: **blocked** — schedule_plan IDs not materialized; no `configs/frozen/`
- [ ] Main effect estimates have not been used to select this configuration. Evidence: no main archive; selection is pre-outcome scope ladder
- [ ] Deviations and unmet gates are recorded; any reduced claims are explicit. Evidence: draft `reduced_claims.json` (unsigned)

Freeze commit / timestamp / accepting owner:

_None — deliberately blank. G3 remains `not_started`._

Accepted evidence paths:

_None accepted for freeze. Draft paths only:_

- `configs/provisional/s0-tab-only/`
- `results/qualification/wp08-freeze-draft-v1.json`
- `handoffs/2026-11-16-wp08-freeze-draft.md`

Any later real freeze creates a new version under `configs/frozen/<version>/` and a deviation record. Do not silently reuse the same main-run identifier with changed scientific settings.
