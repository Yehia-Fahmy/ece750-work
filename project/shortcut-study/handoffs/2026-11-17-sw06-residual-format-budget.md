# Package handoff — SW06 residual format/budget repair — 2026-11-17

- Owner: SW06 GPU operator (`bc-1121d0a4`) on `DESKTOP-VEMMES3`
- Status: ready_for_review (development; **not** qualification; **not** G2)
- Input: main `640eec7` after v3-001 FAIL packaging path
- Branch: `cursor/sw06-residual-format-budget-815d`
- Changes:
  - Adapter `llama-native-tools-dev-v5`: later turns `enable_thinking=false` + accept omitted `reasoning_content`
  - First turn still thinks + forces `list_resources`
  - `max_tool_actions` 8→12, `max_model_turns` 12→16 (token budgets unchanged)
  - temperature 0.2
- Probe outcomes:
  - Format residual cells (TAB01 V01 / TAB03 hard-extreme / TAB04 V10): **24/24 completed**
  - TAB05 extreme budget wave: **15/16 completed** (1 remaining action-budget calculate loop on incomplete V10 sc-absent)
  - TAB02×4 vis: 4/4 completed+auth; TAB03×8 vis: 8/8 completed; TAB02–05 V00: 8/8 completed
- Evidence: `results/development/sw06-residual-format-budget-probes-v1.json`
- Explicit: no new fresh 320; `qual-fresh-tab-catalog-v3-001` remains consumed; `submission_authorized=false`
- Next: independent review; coordinator greenlight for **new** fresh batch id only if completion credibility accepted
