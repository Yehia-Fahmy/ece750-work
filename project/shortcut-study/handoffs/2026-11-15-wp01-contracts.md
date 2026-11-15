# Package handoff — WP01 Shared contracts — 2026-11-15

- Owner and role: integrator (contracts)
- Status: accepted
- Input commit and dependencies: WP00 accepted (`ecb82d3`); planning baseline on `main` at handoff start; Yehia authorized WP01 implementation
- Output commit (or explicitly uncommitted paths): see Git commit on branch `cursor/shortcut-wp01-1ebb`
- Paths changed; shared-contract version:
  - `schemas/` — episode, events, reviewer/auditor packets, scored row, semantic audit (`*-v1`)
  - `configs/development/` — visibility, policy matrix, budgets, A/T/J boundaries, splits, scoring SoT, vertical_slice
  - `src/shortcut_study/` — validation, packet filters, IDs/splits, fixtures, vertical-slice enumeration
  - `fixtures/` — contract fixtures + 16-episode assignment list
  - `tests/` — 21 contract tests
  - `requirements.txt` — `jsonschema` for schema validation
  - `state.json` — WP01 claimed/completed evidence
- Concrete behavior implemented:
  - Versioned JSON Schema contracts with round-trip fixtures
  - Pure task-reviewer projections for V00/V01/V10/V11 with leakage guards
  - Full research-auditor packet projection (A/T/J/events)
  - Policy × information-state × availability matrix config
  - Stable `episode_id` / `base_id` / semantic fingerprint helpers and split disjointness rules
  - Source-of-truth mapping for deterministic scoring vs semantic labels vs budgets
  - Enumerated 16-episode vertical-slice path (TAB01 × complete/incomplete × present/absent × four visibility × seed 0); mock-first; no GPU
- Commands run and actual outcomes:
  - `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q` → 21 tests OK
  - `PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q` → 58 tests OK (historical suite)
  - Preservation manifest historical hashes checked → 0 mismatches
- Evidence/manifest paths and hashes:
  - Fixture materialization under `fixtures/` (see Git)
  - Vertical-slice assignments: `fixtures/vertical_slice/assignments.json` (16 episodes)
- Failures, uncertain findings, and scope limitations:
  - Configs and notices remain **provisional until freeze**
  - No authentic actor/judge inference; fixtures are mock/contract only
  - WP02 generators and WP03 environment not started; vertical slice is path/contracts only
  - G0 still requires WP02 catalog/specification acceptance
- GPU lease owner/process/job, or no GPU work: **no GPU work**
- Terminal/incomplete/unattempted job IDs if applicable: none
- Next safe action and required dependency:
  - Integrator acceptance of WP01 on evidence above
  - Start WP02 (TAB vertical-slice generator) and WP03 (mock-actor runner) against these contracts; WP12 background may proceed in parallel
- Acceptance reviewer, decision, and date (filled on review): integrator; accepted 2026-11-15 on passing contract tests and preservation check; G0 still needs WP02 catalog/specification

## PR #7 review remediation — November 15, 2026

Yehia authorized fixing the review findings and merging the PR. Input revision:
`c9af4241f89ebda3ff3286cbe5765b475b3c9a65`. Output: the commit containing this
handoff update on `cursor/shortcut-wp01-1ebb`.

- Episode and both packet schemas now allow missing A as null. Completed episodes
  still require a valid submission. The interrupted fixture now has no A or J.
- Reviewer leakage checks compare routed channels and metadata to their sources.
  Repeated text across independently captured channels is allowed; injected or
  altered content, forbidden fields, and incorrect channel flags are rejected.
- The scored fixture now records the restricted acquisition in its event ledger,
  including resource/event references and unsuccessful authorized completion,
  while preserving factual correctness. This remains mock data, not a WP04 scorer.
- Added five regression tests, including all six non-completed statuses across
  all four visibility cells, completed-answer validation, overlapping text,
  injected content, and committed/generated fixture consistency. Before the fix,
  the regression suite reproduced failures; afterward all tests passed.

Validation on the corrected implementation:

- `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q` — 26 passed.
- `PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q` — 58 passed.
- `Draft202012Validator.check_schema` on all seven schema files — passed.
- SHA-256 verification against `preservation-manifest.json` — all 111 historical
  files and the design snapshot match.
- `git diff --check` — passed.

Changed fixture SHA-256 hashes:

- `fixtures/episodes/interrupted_v00.json`: `d66717f5137f7e932456daafa47adfa052936f2ef71588fd7eacabfd9b00b194`
- `fixtures/scored/complete_present_v11.json`: `905cb925c4c280fd339b152208f0248924fd7d1cd6f88038f688e7a1d468b8a7`

No GPU work or experimental inference. No remaining issue from this review;
the provisional-contract and unimplemented-consumer limitations above still apply.
