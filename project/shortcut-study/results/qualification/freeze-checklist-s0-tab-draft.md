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
- [x] Held-out actor gates pass; measured family/difficulty limitations are recorded. Evidence: G2 accepted on tip `212631a` / `#56` after v5-001 (`#55`); family/difficulty residuals disclosed in SW06 handoffs
- [x] **Semantic scope XOR:** primary judge path **not** qualified; **behavioral-only** S0 with **explicit semantic withdrawal** (SW07-B / ECE-80). Evidence: `handoffs/2026-11-18-sw07-b-semantic-scope.md`, `results/qualification/sw07-b-semantic-scope-v1.json`. Do not treat audit prep as a qualified judge.
- [x] Evidence validation / chunk / sampling / reconciliation rules retained for prepare-only audit plumbing; **live judge episodes out of freeze scope** under withdrawn semantics. Evidence: `src/shortcut_study/audit/pipeline.py`; SW07-B decision JSON
- [ ] Paired contrasts, weighting, multiplicity, missingness, rare-event and label-error analyses are frozen and simulation-tested. Evidence: SW07-D pre-freeze sim recorded at `results/qualification/prefreeze-sim-sw07d-v1/` (behavioral-only; **not** freeze signature)
- [ ] GPU schedule and conservative actor+audit forecast fit, including reserve and report time. Evidence: SW07-D measured forecast **FITS** Nov 27/29 with reserve (`results/qualification/prefreeze-sim-sw07d-v1/forecast.json`); budgets filled provisional — **not** freeze signature
- [ ] Source/config/data/model hashes and randomized episode schedule are committed. Evidence: provisional unsigned `configs/frozen/s0-tab-v0/` exists (SW07-C); still unsigned / not executable main
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
