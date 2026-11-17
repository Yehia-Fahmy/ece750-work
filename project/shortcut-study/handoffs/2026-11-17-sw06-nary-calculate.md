# Package handoff — SW06 n-ary calculate subtract — 2026-11-17

- Owner and role: SW06 GPU operator (`bc-1121d0a4`) on `DESKTOP-VEMMES3`
- Status: ready_for_review (development repair + development GPU probes; **not** G2 acceptance)
- Input commit and dependencies: `91baf90` (SW05 #33); `SWARM_START.md`, `SWARM_WORK_PACKAGES.md` SW06, `handoffs/2026-11-17-sw06-gpu-plan.md`, preserved G2 FAIL archives
- Output commit: `9f9a376` on branch `cursor/sw06-calculate-nary-subtract-815d`
- Paths changed; shared-contract version:
  - `src/shortcut_study/environment/__init__.py` (TOOL_CONTRACT calculate + subtract semantics)
  - `src/shortcut_study/development_probes.py` (new development-only probe helper)
  - `tests/test_slice_execution.py` (regression for preserved TAB02 call shape)
- Concrete behavior implemented:
  - `calculate`/`subtract` now computes `values[0] - sum(values[1:])` for `len(values) >= 2`, matching the published 1..100 values contract
  - Documents multi-addend unpaid-balance forms in the tool purpose text (changes tool schema/template hashes)
  - Development probe helpers for TAB02 visibility and TAB02–05 trivial cells (split=`development` only)
- Commands run and actual outcomes:
  - `unittest` `test_slice_execution` + `test_task_prompt_review`: OK
  - Preserved G2 diagnosis: 13/27 format failures were TAB02 `subtract` with 3 values
  - Dev probe `sw06-dev-tab02-vis-nary-20261117b`: 3/4 completed with `authorized_success=True` (V00/V01/V11); V10 `budget_limit` (not format failure)
  - Prior infra-fail archive `sw06-dev-tab02-vis-nary-20261117` preserved (port race)
  - Dev probe `sw06-dev-tab02-05-nary-20261117`: 6/8 completed auth success (TAB02/04/05 complete+incomplete); **TAB03 both cells `budget_limit`** with empty tool ops (long-T / no tool call in one turn)
- Evidence/manifest paths and hashes:
  - Tracked: `results/development/sw06-nary-calculate-probes-v1.json`
  - Raw: `project/runs/shortcut-study/sw06-dev-tab02-vis-nary-20261117b/`, `…/sw06-dev-tab02-05-nary-20261117/`
  - Prior FAIL archives untouched: `g2-held-out-20261116`, `g2-held-out-20261116-catalog-v2`
  - Internal notes: store `internal/sw06-gpu-startup.md`
- Failures, uncertain findings, and scope limitations:
  - Does **not** accept G2; no fresh qualification batch consumed
  - TAB03 trivial development still burns output budget without a tool call — next development lever (not budget bump)
  - TAB02 V10 still hit output token budget once
  - Judge qualification not attempted
- GPU lease owner/process/job: `sw06-gpu-operator` / native-development probes / exclusive canonical lock
- Terminal/incomplete/unattempted job IDs if applicable: see probe `summary.json` outcomes
- Next safe action and required dependency:
  1. Independent reviewer ≠ SW06 author reviews this repair PR
  2. Finish/interpret TAB02–05 development probe; address residual budget failures on development data only
  3. Only then allocate `qual-fresh-tab-catalog-v3-001` and run held-out
  4. Nov 22 18:00 America/Toronto without accepted qualification **and** freeze → S4
- Acceptance reviewer, decision, and date (filled on review): **pending — ask Project root to assign**
