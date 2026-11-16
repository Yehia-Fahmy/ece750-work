# Package handoff — TAB02–05 v6 public-task port (`tab-catalog-v2`) — 2026-11-16

- Owner and role: CPU catalog worker (ECE-29); no GPU ownership.
- Status: ready_for_review
- Input commit and dependencies: `origin/main` including PR #23 (G2 held-out FAIL packaging); diagnosis `docs/g2-held-out-diagnosis.md`.
- Output branch: `cursor/tab02-05-v6-public-task-2eaa` (this handoff's commit).
- Paths changed: `src/shortcut_study/tasks/tables/{common,tab02,tab03,tab04,tab05}.py`, `adapters/mock.py`, `tests/test_tab_catalog.py`, `tests/test_task_prompt_review.py`, `configs/development/tab_catalog.json`, `TASK_CATALOG.md`, fresh evidence under `results/development/tab-catalog-v2-public-task-port.json`. Raw mocks under gitignored `project/runs/shortcut-study/tab-catalog-v2-*`.
- Concrete behavior implemented:
  1. Omit public `clarification_fields` on TAB02–05 (typed ids remain in tool/submit schemas + `data_rules`).
  2. Inspect-first `data_rules` (“After reading approved resources… typed missing_prerequisite id is …”).
  3. Template-specific multi-row inclusion + prefer-`calculate` / tool-before-long-speculation cues aligned with `tab01-slice-v6`.
  4. Bump catalog generator version `tab-catalog-v1` → `tab-catalog-v2` (TAB01 moderate stays `tab01-slice-v6`).
  5. **Not** done: budget raises as primary lever; rewrite of v5 FAIL or G2 FAIL evidence; GPU held-out re-run.
- Commands run and actual outcomes:
  - `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q` → **213 passed**.
  - `mock-tab-catalog --strategy legitimate|shortcut` → **320/320 completed** each (`tab-catalog-v2`); legitimate acquired 0 / announced 320; shortcut acquired 160 / announced 240 (scripted fixture behavior only).
- Evidence/manifest paths and hashes: `results/development/tab-catalog-v2-public-task-port.json` (artifact counts verified against run manifests).
- Failures, uncertain findings, and scope limitations: CPU/mocks only. Does **not** accept `gates.G2`. Prior `g2-held-out-20261116` FAIL and `tab01-slice-v5` FAIL archives preserved unchanged. Authentic development GPU probe + fresh held-out 320 remain for WSL worker after merge.
- GPU lease owner/process/job, or no GPU work: **no GPU work**.
- Next safe action and required dependency: lagging reviewer merges this PR; separate WSL GPU worker re-qualifies held-out after merge. Do not start main / 3200 collection.
- Acceptance reviewer, decision, and date (filled on review):

Do not mark G2 accepted from mocks. Preserve unsuccessful outputs and distinguish fixture behavior from measured model behavior.
