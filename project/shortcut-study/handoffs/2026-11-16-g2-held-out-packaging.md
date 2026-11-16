# Package handoff — WP08 G2 held-out packaging (S0) — 2026-11-16

- Owner and role: integrator / CPU packaging worker; no GPU ownership.
- Status: ready_for_review
- Input commit and dependencies: `main` post-#17 (`0400696`; G0 blocked after #16 FAIL; WP08 provisional draft on main); TAB catalog + WP01 contracts; scope path S0.
- Output commit: branch `cursor/g2-held-out-packaging-a32b` (this handoff's commit).
- Paths changed; shared-contract version: `src/shortcut_study/held_out.py`, catalog split namespaces, mock/native qualification split support, `configs/development/g2-held-out.json`, budgets/splits notes, `templates/G2_HELD_OUT_CHECKLIST.md`, `GPU_RUNBOOK_G2.md`, CLI `package-g2-held-out` / `mock-held-out` / `qualify-local --held-out`. No episode/event schema version bump. Fresh evidence only under `results/qualification/g2-held-out-packaging-v1.json` and ignored raw `project/runs/shortcut-study/g2-held-out-packaging-v1/`.
- Concrete behavior implemented:
  - S0 schedules: smoke 8 / development 320 / qualification 320 / main 320 with disjoint generation-seed namespaces and fingerprint reservations.
  - CPU structural G2 gate evaluation (generators + certificates + main reserve); GPU gates recorded as `pending_gpu`.
  - Scripted qualification mocks allowed; main execution refused by mock and native runners.
  - Native `qualify-local --held-out` entrypoint for operator GPU (not run in this packaging session).
- Commands run and actual outcomes:
  - `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q` → 201 passed.
  - `PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study package-g2-held-out --out project/runs/shortcut-study/g2-held-out-packaging-v1 --mock-difficulties trivial` → `cpu_structural_passed=True`, `g2_accepted=False`.
- Evidence/manifest paths and hashes: `results/qualification/g2-held-out-packaging-v1.json` (see file for schedule/reservation sha256s).
- Failures, uncertain findings, and scope limitations: G2 not accepted; no authentic held-out actor run; no judge qualification; no measured forecast; TAB-only / prior-note only; difficulties uncalibrated; actor 16-cell development archive still recommended before spending the 320-cell held-out budget.
- GPU lease owner/process/job, or no GPU work: no GPU work.
- Terminal/incomplete/unattempted job IDs if applicable: scripted mock trivial qualification subset completed under packaging out; main schedule non-executable.
- Next safe action and required dependency: Yehia/operator follows `GPU_RUNBOOK_G2.md` when WSL/GPU is free (prefer fresh 16-cell development archive, then `--held-out`); fill `templates/G2_HELD_OUT_CHECKLIST.md`. Do not mark `gates.G2` accepted or start WP09 from this PR alone.
- Acceptance reviewer, decision, and date (filled on review):

Do not mark acceptance based on predicted results. Preserve unsuccessful outputs and distinguish fixture behavior from measured model behavior.
