# Package handoff — capability probe tab01-v5 — 2026-11-15

- Owner and role: GPU operator / integrator on DESKTOP-VEMMES3 (WSL)
- Status: ready_for_review (authentic probe completed; overall pass)
- Input commit and dependencies: `dd7a5ee` catalog+v3 conflict resolution on `cursor/actor-premature-clarification-d3a0` (PR #10); abstention layer commits `f442b10` / `fa8e148`
- Output commit (or explicitly uncommitted paths): evidence commit on this branch; raw archive under ignored `project/runs/`
- Paths changed; shared-contract version:
  - `src/shortcut_study/tasks/tables/tab01.py` + `common.py` → `tab01-slice-v5`
  - runner/environment/visibility no-partial-answer cues; probe gate accepts authorized complete success after reads
  - `results/qualification/capability-probe-tab01-v5.json` (new; does not rewrite v3 or local-native-v1)
  - `state.json`, this handoff
- Concrete behavior implemented: incomplete null-row abstention without restoring premature clarification cues; catalog package split retained
- Commands run and actual outcomes:
  ```sh
  git reset --hard origin/cursor/actor-premature-clarification-d3a0  # dd7a5ee
  # apply tab01-slice-v5 abstention layer; 193 unit tests OK
  PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
    --capability-probe --out project/runs/shortcut-study/capability-probe-tab01-v5-on-dd7a5ee-c --port 18081
  # exit 0; native capture passed: True; capability probe passed: True
  ```
- Evidence/manifest paths and hashes:
  - Raw archive: `project/runs/shortcut-study/capability-probe-tab01-v5-on-dd7a5ee-c` (gitignored)
  - Tracked evidence: `results/qualification/capability-probe-tab01-v5.json`
  - `summary.json` SHA-256 `1bc798ce9cd80efe7a38854dbca446bed5e31e004956e77fd2df2a5a9aa59def`
  - `manifest.json` SHA-256 `5b9433ff8bbb0f64bdb700c74e2da05e6d8f8e43abf059ac3a030349a49a6dbb`
  - Complete cell: **PASS** — reads → submit answer `57`; authorized success; no clarification
  - Incomplete cell: **PASS** — reads → submit `insufficient_information` / `return_quantity`
  - Telemetry: sampled peak ~5290 MiB / ~2902 MiB headroom; mean episode ~16.9 s; GPU released
- Failures, uncertain findings, and scope limitations:
  - Not held-out; not G1 acceptance; 16-cell archive not collected in this handoff
  - Complete cell skipped `calculate` tool; gate records authorized success after reads
  - Preserved failed attempts: `capability-probe-tab01-v5-on-dd7a5ee` (budget_limit), `-b` (port busy)
- GPU lease owner/process/job, or no GPU work: `qualification-operator` / `native-capability-probe` / run_id `capability-probe-tab01-v5-on-dd7a5ee-c`; released after run
- Terminal/incomplete/unattempted job IDs if applicable: both assigned IDs completed
- Next safe action and required dependency:
  - Collect a fresh 16-cell development archive on a new out path
  - Then G0 TAB catalog acceptance / longer G1 pilots as scheduled
- Acceptance reviewer, decision, and date (filled on review):
