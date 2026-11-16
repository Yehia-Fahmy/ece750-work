# Package handoff — actor premature-clarification prompt fix — 2026-11-15

- Owner and role: integrator / environment+task prompt owner for WP02/WP03 capability unblock
- Status: ready_for_review (CPU/prompt verified; authentic GPU probe blocked on this Mac host)
- Input commit and dependencies: `76d6db3` (reviewed local runtime qualification stage)
- Output commit (or explicitly uncommitted paths): branch `cursor/actor-premature-clarification-d3a0` (this handoff lands with the fix commit)
- Paths changed; shared-contract version:
  - `src/shortcut_study/tasks/tables/__init__.py` → generator `tab01-slice-v3`
  - `src/shortcut_study/environment/__init__.py` (tool-contract purpose text)
  - `src/shortcut_study/runner/__init__.py` (inspect-before-abstain channel instructions)
  - `configs/development/visibility.json` (scoring statement)
  - `src/shortcut_study/qualification.py`, `__main__.py`, `vertical_slice.py` (`--capability-probe`)
  - tests/README/`state.json` updates
- Concrete behavior implemented:
  1. Diagnosed premature clarification as prompt/tool affordance bias, not budgets, policy blocks, or judge.
  2. Removed public `clarification_fields`; reframed data rules; require authorized reads before clarification/insufficiency.
  3. Added smallest existing-slice GPU probe: complete+incomplete V00, shortcut absent.
- Commands run and actual outcomes:
  ```sh
  PYTHONPATH=project/shortcut-study/src python3 -m unittest \
    tests.test_task_prompt_review tests.test_qualification.QualificationTests.test_capability_probe_uses_two_existing_cells_and_gates_on_reads \
    tests.test_slice_execution tests.test_vertical_slice tests.test_local_adapter \
    tests.test_cpu_merge_review tests.test_packets tests.test_schemas tests.test_policy_matrix tests.test_ids_splits
  # 69 passed (focused suite excluding Mac /var vs /private/var lease path failures)
  PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice \
    --strategy legitimate --out project/runs/shortcut-study/cpu-capability-prompt-v3-legitimate
  # Scripted mock only: 16/16 completed
  PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
    --capability-probe --out project/runs/shortcut-study/capability-probe-v3-attempt
  # exit 1; summary.failure = FileNotFoundError for project/tools; assigned=2 not_attempted
  ```
- Evidence/manifest paths and hashes:
  - Internal diagnosis: agent-store `internal/actor-premature-clarification-diagnosis.md`
  - Prior immutable qualification evidence unchanged: `results/qualification/local-native-v1.json`
  - Fresh mock run (ignored raw archive): `project/runs/shortcut-study/cpu-capability-prompt-v3-legitimate`
  - Failed Mac probe archives (ignored): `project/runs/shortcut-study/capability-probe-v3-attempt*`
- Failures, uncertain findings, and scope limitations:
  - Authentic Qwen3-4B proof not executed here (RTX 3070 Ti assets absent on Mac; `project/tools` / `project/models` missing).
  - Full unittest discover still hits pre-existing macOS `/private/var` vs `/var` canonical-lease resolution failures unrelated to this prompt change.
  - Prompt fix may be necessary but is not yet proven sufficient until the RTX capability probe passes.
- GPU lease owner/process/job, or no GPU work: no GPU work on this host
- Terminal/incomplete/unattempted job IDs if applicable: none
- Next safe action and required dependency:
  - On the RTX experiment checkout (with `project/models` + `project/tools/runtime`), run:
    `PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local --capability-probe --out project/runs/shortcut-study/capability-probe-tab01-v3 --port 18080`
  - If complete cell reads/calculates and scores success, re-run full 16-cell development archive under a new versioned out path; then resume G0/G1/WP02 catalog decisions.
- Acceptance reviewer, decision, and date (filled on review):
