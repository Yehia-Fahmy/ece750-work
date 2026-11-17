# Package handoff — SW06 force-first + reasoning-budget 256 — 2026-11-17

- Owner and role: SW06 GPU operator (`bc-1121d0a4`) on `DESKTOP-VEMMES3`
- Status: ready_for_review (development; **not** qualification; **not** G2)
- Input commit: `2636301` (main after #39/#40)
- Output commits: `86a7426`, `9a4b893` on `cursor/sw06-force-first-list-resources-815d`
- Paths changed:
  - `adapters/local.py` → `llama-native-tools-dev-v4`, empty-history forces `list_resources`, later turns `required`
  - `runner/native.py` records `tool_choice_policy`
  - `runtime/server.py` → uniform `--reasoning-budget 256` (was `-1`)
- Concrete behavior: first turn cannot burn all 3072 tokens on T before a native tool; thinking stays enabled
- Commands / outcomes:
  - 257 unit tests OK
  - Authentic replay: forced tool_choice alone still length@3072 on TAB03 V01; `--reasoning-budget 256` yields tool_calls
  - Rbudget wave: **TAB03 V01/V10 4/4**, **TAB03×8 8/8**, **TAB02×4 vis 4/4**, **TAB02–05 8/8** — all local checks passed
- Evidence: `results/development/sw06-force-first-rbudget-probes-v1.json`
- Failures / limits: fresh qual **not started** in this package (await coordinator greenlight + independent review)
- GPU: exclusive lease; released after probes
- Next: independent review; if greenlighted, allocate `qual-fresh-tab-catalog-v3-001`
- `submission_authorized=false`
