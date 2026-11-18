# Package handoff — SW07-B / ECE-80 semantic scope (2026-11-18)

- Owner and role: CPU analyst (`bc-9e07f3b8-08a5-565b-8555-d4c5610d848f`); **not** freeze signer
- Status: ready_for_review — **XOR decision recorded**; freeze remains **unsigned**; G3 remains `not_started`
- Tracker: ECE-80 / SW07-B
- Input commit: `212631a` (`origin/main` tip; G2 booked accepted)
- Output paths:
  - `results/qualification/sw07-b-semantic-scope-v1.json`
  - `results/qualification/freeze-checklist-s0-tab-post-sw05.md` (semantic item closed; signature still blank)
  - `results/qualification/freeze-checklist-s0-tab-draft.md` (judge items marked withdrawn for this candidate)
  - `configs/provisional/s0-tab-only/{scope,reduced_claims,scoring_source_of_truth,analysis_protocol,README,manifest}.json|.md`
  - `DECISIONS.md` (D16)
  - `report/claim-evidence-ledger.md` (C-SEM)
  - `results/qualification/sw07-freeze-prep-v1.json` (blocker text)
  - this handoff
- Shared-contract note: provisional configs stay `draft_not_frozen`; this PR does **not** create `configs/frozen/`

## XOR choice (exactly one)

| Option | Selected? |
| --- | --- |
| Qualify local semantic judge before freeze | **No** |
| Explicit **behavioral-only** S0 scope + **semantic withdrawal** | **Yes** |

## Why behavioral-only (evidence, not preference)

1. **No live judge.** `src/shortcut_study/audit/` prepares A/T/J/events and validates envelopes; `prepare-audit` is explicitly `prepared_only_no_judge_inference`. Chunk planning is not a qualified chunk-and-reconcile judge.
2. **Still unqualified.** `state.json` has `judge_qualified: false`. The 2026-11-17 review and WP05 handoff require held-out rubric gates, natural-record diagnostics, long-trace/chunk equivalence, and a complete actor+audit forecast before semantic claims.
3. **CPU-only package / single GPU.** Judge qualification needs local RTX 3070 Ti inference. This package must not take GPU. Post-G3 actor collection already owns that scarce lease; a late judge campaign before Nov 22 freeze is not feasible without crowding out the behavioral main path.
4. **Protocol already permits this XOR.** `SWARM_START.md`, `EXECUTION_PLAN.md`, and provisional `withdraw_if_judge_unqualified` authorize withdrawing semantics rather than inventing labels or using a cloud judge (D09).

## Scientific consequences locked for freeze candidate

**In scope (behavioral):** shortcut acquisition / visibility contrasts under deterministic scoring; incomplete-task abstention or clarification behavior in the TAB environment; assigned-denominator accounting.

**Withdrawn:** any independent semantic validation of T/J; primary or independent judge labels as confirmatory findings; main conclusions that require a qualified semantic auditor. SW08 must **not** run live semantic judge episodes under this freeze candidate unless a later dated decision **supersedes this XOR before signature** (not this PR).

## Explicit non-actions

- Freeze signature fields stay `_None — deliberately blank._`
- Do **not** set `gates.G3=accepted`
- `submission_authorized=false`
- No GPU work; no soft-sign; no `configs/frozen/` materialization from this package alone

## Commands / checks

- Inspected tip `212631a`, freeze checklist, provisional scope, audit source, `state.json` judge flag, SWARM/EXECUTION/DECISIONS language — CPU document work only; no test suite mutation required for this decision package.

## Next safe action

Independent reviewer **≠** this author verifies the XOR is exclusive, evidence paths exist, checklist signature is still blank, G3 untouched, and provisional files say **withdrawn** rather than “pending judge.” Integrator may then proceed with remaining SW07 freeze prep (G1 package, forecast/sim, guarded main path) under **behavioral-only** scope.

- Acceptance reviewer, decision, and date: _pending independent review_
