# Worker assignment brief — SW01 task identities / batches — 2026-11-17

## Identity

| Field | Value |
| --- | --- |
| Package | **SW01** |
| Tracker | **ECE-36** |
| Role | task_engineer |
| Owner (to launch) | `sw01_task_engineer` (sibling worker) |
| Independent reviewer | `sw03_analyst` (must ≠ author) |
| Depends on | SW00 assignment (this brief) |
| Input commit | `f82908d62889fbd6ea3ffa79e041ac17ffb6b094` |
| Suggested branch | `cursor/sw01-task-identity-batches-be8a` from input commit (or stack on SW00 PR tip once merged/available) |
| Base for PR | `main` (or stack base required by integrator) |
| CPU-only | **yes** — no GPU / no 320-episode qualification |
| Handoff return path | `project/shortcut-study/handoffs/2026-11-17-sw01-<slug>.md` |

## Findings to close

- **RD1** — semantic split validation conceals actual development/main duplicate (TAB04 trivial)
- **RD2** — qualification batch freshness / consumed-once allocation (preserve old runs; label reused catalog-v2 as post-tuning repeat)
- **RD3** — “optional” non-approved note policy wording → one clear approved-only interpretation without claiming behavioral causation

Reproduce independently first:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/research-design-reproduce.py
```

Do **not** edit dated review JSONs to “pass.” Add new regressions under assigned tests.

## Exact path allowlist (writable)

- `project/shortcut-study/src/shortcut_study/tasks/tables/`
- `project/shortcut-study/src/shortcut_study/ids.py`
- `project/shortcut-study/src/shortcut_study/splits.py`
- `project/shortcut-study/tests/test_ids_splits.py`
- `project/shortcut-study/tests/test_tab_catalog.py`
- `project/shortcut-study/tests/test_task_prompt_review.py`
- `project/shortcut-study/tests/test_sw01_identity_batches.py` (create)
- `project/shortcut-study/handoffs/2026-11-17-sw01-*.md`
- `project/shortcut-study/results/development/sw01-*.json`

## Forbidden (integrator-owned / other lanes)

`state.json`, `schemas/`, `configs/`, `qualification.py`, `held_out.py`, `__main__.py`, `runner/`, `audit/`, `analysis/`, `reviews/`, dependency metadata, protected historical files.

If batch-allocation needs qualification wiring: **propose interface in handoff**; do not edit shared files.

## Interface decisions (agreed before edit)

1. Semantic fingerprints are **content-only** — no split name / split-salted base ID in the fingerprint payload.
2. Paired visibility variants remain under the **same base identity**.
3. Expand low-entropy generators (esp. TAB04) enough for disjoint development / consumed-qual / fresh-qual / main reservations, **or** document a narrower template choice before freeze (integrator records scope).
4. Explicit **batch ID + immutable seed/semantic manifest + consumption record**; new folder/seed ≠ new world.
5. Prior qualification batches remain **consumed**; annotate catalog-v2 run as post-tuning repeat; never delete/rename archives.

## Acceptance / regression targets

- Differently named identical semantic tasks rejected across splits
- Current TAB04 trivial dev/main collision caught
- Materially new worlds pass; paired variants aligned
- Old/consumed batches cannot masquerade as fresh; replay is explicit regression mode
- CPU-only reservation manifest shows disjointness **before any GPU use**
- Targeted tests pass; do not claim full-suite acceptance (integrator runs wave suite)

## Deliverables

1. Fix + meaningful regression tests
2. Handoff using `templates/HANDOFF.md` with commands/results/hashes/commit
3. Interface proposal for qualification batch consumption (if needed)
4. PR against `main` (or stack base); request review from `sw03_analyst`

## Out of scope

GPU qualification, main freeze, report PDF, editing `state.json`, closing G2.
