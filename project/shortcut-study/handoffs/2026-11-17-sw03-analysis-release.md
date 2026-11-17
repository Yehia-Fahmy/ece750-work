# Package handoff — SW03 statistics / release inputs — 2026-11-17

- Owner and role: `sw03_analyst` (worker bc-1a2b628e-1c8d-5000-b76b-bdf1c33ec6c4); analyst
- Status: ready_for_review
- Input commit and dependencies: `3f77a18` on `cursor/sw00-completion-baseline-be8a` (SW00 tip); tracker ECE-38; findings A1–5
- Output commit (or explicitly uncommitted paths): see branch `cursor/sw03-analysis-release-c6c4` (filled after push)
- Paths changed; shared-contract version: analysis package + tests + protocol draft only (allowlist). No `state.json` / schemas / configs / `__main__.py` edits. Proposed shared-contract bumps listed below for integrator.
- Concrete behavior implemented:
  - **A1:** Complete-base sensitivity estimand — a base is included only when all matched information-state blocks are identified; point and complete-base bootstrap share inclusion/weighting. Fixed `blocks_used` to count matched blocks.
  - **A2:** Coefficient-aware label-error envelopes under a global flip-rate budget; interaction range [-2, 2]; bare point±flip_rate API rejected.
  - **A3:** Releases retain hashed schedule/rows/protocol under `retained_inputs/` + protocol snapshot; statistical replay without external paths.
  - **A4:** Primary arm rejects mixed/wrong `policy_id`, mixed `split`, mixed/missing `scorer_version`; join validates schedule/scored agreement; JSON-list rows schema-validated (analysis strata stripped for projection).
  - **A5:** Separate reporting denominators for terminal completion, conditional parse-among-complete-completed, valid-A among assigned / complete-assigned (no historical gate rewrite).
  - **Fixture side effect:** `run_dry(..., materialize_fixtures=False)` default; CLI analyze-dry no longer rewrites tracked fixtures.
  - Stochastic Bernoulli probe helper at candidate 20-base scope; rule-of-three independent-base zero-event bound.
- Commands run and actual outcomes:
  - `PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-repro.py` — pre-fix: A1 mismatch (1/3 vs 0), A2 underbound (−0.2 outside ±0.1), A4 pooled mixed policies (T=J=0.5).
  - Post-fix probes: complete-base point=bootstrap=0; adversarial T=−0.2 inside [−0.2, 0.2]; mixed policy raises; analyze-dry fixture manifest SHA unchanged.
  - `unittest discover -p 'test_analysis.py'` → 10 OK; `-p 'test_sw03*.py'` → 9 OK.
- Evidence/manifest paths and hashes:
  - `project/shortcut-study/results/development/sw03-analysis-repair-v1.json` (source file hashes + dry release hashes)
  - Agent notes: `/cursor/stores/bc-01a1e142-d0b9-750b-a619-ea79245ffebc/internal/sw03-analysis-release.md`
- Failures, uncertain findings, and scope limitations:
  - Semantic helper still not wired to archived audit rows / CLI (deferred if semantics withdraw; placeholder wiring remains out of SW03 GPU/judge scope).
  - Stochastic precision probe is a minimal Bernoulli check at candidate scope — not a full coverage/power study; expand before G3 freeze.
  - Zero-event rule-of-three is diagnostic for independent-base events only; nonzero-event Clopper–Pearson not implemented.
  - `configs/development/analysis_protocol.json` and CLI `--materialize-fixtures` not updated (forbidden paths); see integrator proposals.
  - No new 320-episode qualification; no GPU; course submission untouched.
- GPU lease owner/process/job, or no GPU work: no GPU work
- Terminal/incomplete/unattempted job IDs if applicable: n/a
- Next safe action and required dependency:
  1. **Independent reviewer `sw02_runtime_audit`** (must ≠ author): reproduce A1–5 regressions on this PR tip; run the two unittest modules; confirm analyze-dry does not dirty `fixtures/analysis/`; spot-check a release `retained_inputs/` replay.
  2. **Integrator:** merge after SW02 review; sync `configs/development/analysis_protocol.json` to protocol.py; optional `__main__.py --materialize-fixtures`; consider analysis-row schema allowlist for flattened strata if desired.
- Acceptance reviewer, decision, and date (filled on review): `sw02_runtime_audit` — pending

## Review brief for `sw02_runtime_audit`

Please independently verify (do not trust author confidence):

1. Re-run review repro logic / `tests/test_sw03_analysis_release.py` on the PR commit.
2. Confirm A1: heterogeneous missingness yields identical complete-base point and bootstrap point.
3. Confirm A2: 4/40 adversarial V00 flips → T=−0.2 falls inside coefficient-aware envelope; interaction range is [-2,2].
4. Confirm A3: `run_analyze` writes `retained_inputs/` + hashes; deleting originals still allows replay from retained copies.
5. Confirm A4: mixed policy / wrong policy / mixed scorer_version raise.
6. Confirm A5: reporting_denominators keys exist and note forbids retroactive gate redefinition.
7. Confirm `python -m shortcut_study analyze-dry ...` leaves `fixtures/analysis/manifest.json` hash unchanged.
8. Record any disagreement with the complete-base estimand definition or release manifest shape in your review handoff.

## Integrator contract proposals (do not apply in SW03)

| Contract | Proposal |
| --- | --- |
| `configs/development/analysis_protocol.json` | Mirror `protocol.py` DENOMINATORS, DEFAULT_PRIMARY_POLICY_ID, complete_base_sensitivity, label-error budget language |
| `__main__.py` | Add `--materialize-fixtures` flag forwarding to `run_dry(..., materialize_fixtures=...)` |
| `schemas/` / analysis row | Optional: documented allowlist for flattened schedule strata on analysis bundles vs scored_row-only archives |
| `state.json` | Mark SW03 ready_for_review → accepted after SW02 sign-off |

Do not mark acceptance based on predicted results. Preserve unsuccessful outputs and distinguish fixture behavior from measured model behavior.
