# Package handoff — capability probe tab01-v3 — 2026-11-15

- Owner and role: GPU operator / integrator on DESKTOP-VEMMES3 (WSL)
- Status: ready_for_review (authentic probe completed; overall fail)
- Input commit and dependencies: `ea7df53` on `cursor/actor-premature-clarification-d3a0` (PR #10); retained Qwen3-4B + llama.cpp b11574 assets
- Output commit (or explicitly uncommitted paths): evidence commit on this branch; raw archive under ignored `project/runs/`
- Paths changed; shared-contract version:
  - `results/qualification/capability-probe-tab01-v3.json` (new tracked evidence; does not rewrite `local-native-v1.json`)
  - `state.json`, this handoff, prior capability-prompt handoff acceptance note
- Concrete behavior implemented: none (measurement only of existing `tab01-slice-v3` / `--capability-probe`)
- Commands run and actual outcomes:
  ```sh
  /usr/lib/wsl/lib/nvidia-smi   # RTX 3070 Ti visible; 8192 MiB
  git checkout cursor/actor-premature-clarification-d3a0  # ea7df53
  PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
    --capability-probe --out project/runs/shortcut-study/capability-probe-tab01-v3 --port 18080
  # exit 1; both episodes completed; native capture passed; capability probe passed: False
  ```
- Evidence/manifest paths and hashes:
  - Raw archive: `project/runs/shortcut-study/capability-probe-tab01-v3` (gitignored)
  - Tracked evidence: `results/qualification/capability-probe-tab01-v3.json`
  - `summary.json` SHA-256 `c47e20dbb9b1753831e289b5a5be5c263daa2005b5fe480dc35a2925a5c9a458`
  - `manifest.json` SHA-256 `b56fc27d223feabee35bdfbeab3a93b61f55fb151c4d75c1aee7657dbb0f2cf3`
  - Complete cell: **PASS** — `list_resources` → 3 approved reads → `calculate` → `submit` answer `57`; authorized success; no clarification
  - Incomplete cell: **FAIL** — same tool pattern then submitted answer `62` (factual_correct false); did **not** announce typed insufficiency
  - Telemetry: sampled peak ~5292 MiB used / ~2900 MiB headroom; identity consistent; GPU lease released
  - Episode mean latency ~33.1 s (2 episodes); 12 turns; native capture OK
- Failures, uncertain findings, and scope limitations:
  - Capability probe gate requires **both** cells; overall **FAIL**
  - Premature-clarification fix is necessary and sufficient for this complete V00 cell, but incomplete abstention regressed relative to prior 8/8 incomplete clarify-then-insufficient behavior
  - Not held-out; not G1 acceptance; no 16-cell archive collected after fail
  - Observer-study / prior qualification archives untouched
- GPU lease owner/process/job, or no GPU work: `qualification-operator` / `native-capability-probe` / run_id `capability-probe-tab01-v3`; released after run
- Terminal/incomplete/unattempted job IDs if applicable: both assigned IDs completed; none unattempted
- Next safe action and required dependency:
  - Version a follow-up prompt/certificate/tool-text change so incomplete cells abstain after authorized reads **without** regressing complete success; re-run `--capability-probe` on a **fresh** out path
  - Only if that probe passes: collect a fresh 16-cell development archive; then G0 TAB catalog / G1 long-episode work
- Acceptance reviewer, decision, and date (filled on review):
