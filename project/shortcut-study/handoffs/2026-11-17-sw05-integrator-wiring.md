# Package handoff — SW05 integrator wiring / CPU acceptance tip — 2026-11-17

- Owner and role: orchestrator / integrator (`bc-ece62cad-b32b-5b8f-b2e7-56b9dbc6be8a`); shared-path wiring after SW01–03 merges
- Status: ready_for_review
- Input commit and dependencies: `0a71981` on `main` (SW01 #29, SW02 #30, SW03 #31, compat #32)
- Output commit: (this PR tip on `cursor/sw05-integrator-wiring-be8a`)
- Paths changed; shared-contract version:
  - `src/shortcut_study/qualification.py` — held-out batch allocation, metrics migration, stop `GENERATOR_VERSION` stamps
  - `src/shortcut_study/__main__.py` — bound `prepare_archive`, batch CLI flags, `--materialize-fixtures`
  - `src/shortcut_study/tasks/tables/__init__.py` — export `DEFAULT_FRESH_QUALIFICATION_NAMESPACE`
  - `configs/development/tab_catalog.json` → `tab-catalog-v3` / `tab01-slice-v7`
  - `configs/development/analysis_protocol.json` — mirrors `analysis/protocol.py` (A1–5 language)
  - `fixtures/episodes/*.json` — semantic fingerprints regenerated for content-only RD1 algorithm
  - `tests/test_sw05_integrator_wiring.py`, `results/development/sw05-integrator-wiring-v1.json`
- Concrete behavior implemented:
  1. **SW01:** `allocate_held_out_schedule` calls `allocate_qualification_batch`; expands bases to 16-cell factorial; rejects consumed batches as fresh; writes batch manifest + consumption ledger on fresh held-out close.
  2. **SW02:** `prepare_archive` → `prepare_audit_from_episode_directory`; `tool_operation_counts(..., approved_resources=task.public_task["approved_resources"])`; vertical-slice / capability-probe / long-pilot keep declared `generator_version`.
  3. **SW03:** development `analysis_protocol.json` synced; `analyze-dry --materialize-fixtures` opt-in (default off).
- Commands run and actual outcomes:
  - `PYTHONPATH=src python3 -m unittest tests.test_sw05_integrator_wiring` → **9 OK**
  - `PYTHONPATH=src python3 -m unittest discover -s tests` → **254 OK**
- Evidence/manifest paths and hashes: `results/development/sw05-integrator-wiring-v1.json`
- Failures, uncertain findings, and scope limitations:
  - No GPU / no 320-episode qualification in this PR.
  - `submission_authorized` remains false.
  - Historical `reviews/2026-11-17/` bytes untouched (dated evidence preserved).
  - `test_schemas.test_write_fixtures_validate` still rewrites episode fixtures as a side effect; fingerprints now match RD1.
- GPU lease owner/process/job, or no GPU work: **no GPU work**
- Next safe action and required dependency:
  1. **Independent SW05 reviewer** (must ≠ SW01/SW02/SW03 authors and ≠ this integrator): run checklist below on this PR tip.
  2. After SW05 accept only: follow `handoffs/2026-11-17-sw06-gpu-plan.md` on user WSL RTX 3070 Ti — do not start qualification without that plan.

## SW05 acceptance checklist (independent reviewer)

- [ ] RD1–3, IMPL-1–3, A1–5 regressions green on integrated tip
- [ ] Fresh held-out path uses `qual-fresh-tab-catalog-v3-001` (or registered batch), not historical catalog alone
- [ ] Consumed `g2-held-out-20261116*` cannot allocate as fresh
- [ ] Bound audit prep path wired; metrics use task-specific approved sets when callers pass them
- [ ] No schedule stamp with global `GENERATOR_VERSION` on vertical-slice / capability-probe
- [ ] `analysis_protocol.json` mirrors protocol denominators / complete-base / label-error language
- [ ] Full extension suite OK; `reviews/2026-11-17/` unchanged
- [ ] Main-refusal / `submission_authorized=false` still present
- [ ] Exact PR commit recorded; author ≠ reviewer

Do not mark acceptance based on predicted GPU results. Preserve unsuccessful outputs.
