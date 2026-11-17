# Package handoff — SW06 ECE-59 TAB05 extreme residual — 2026-11-17

- Owner: SW06 GPU operator (`bc-1121d0a4`) on `DESKTOP-VEMMES3`
- Status: ready_for_review (development; **not** qualification; **not** G2)
- Input: main `49ed0c4` (#47) after #46 merge (do **not** push to #46)
- Branch: `cursor/sw06-tab05-extreme-residual-815d`
- Changes:
  - Adapter `llama-native-tools-dev-v6`: anti-repeat cue + identical_tool_call_already_executed recovery guidance
  - Runner: identical successful (op,args) fingerprints return error tool result; **do not burn** `max_tool_actions`
  - Probe-only `configs/development/local-development-probes.json` with `max_model_turns` **20** (used by `development_probes.py` only)
  - Live path `configs/development/local-qualification.json` stays `max_model_turns` **16** (what `qualification.py` / held-out reads)
  - `budgets.json` → `qualification` stays 16; `budgets.json` → `development` is 20 for CPU/native_limits defaults only
  - Token budgets unchanged
- Probe outcomes:
  - Wave A (`…antidupe-20261117`): 15/16 — cleared prior incomplete V10 sc-absent; new fail incomplete V10 sc-present (anti-dupe fired but action budget still burned)
  - Wave B (`…antidupe-20261117b`): **16/16 completed** after action-budget skip + turns 20 (ran under then-live local-qual 20; post-ECE-62 fix that 20 lives only in local-development-probes)
- Evidence: `results/development/sw06-tab05-extreme-residual-clearance-v1.json`
- Explicit: no new fresh 320; `qual-fresh-tab-catalog-v3-001` remains consumed; `submission_authorized=false`
- Next: re-review after ECE-62 budget-claim fix; coordinator/root greenlight for **new** fresh batch id only if credibility accepted
