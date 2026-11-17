# Worker assignment brief — SW02 native provenance / audit / telemetry — 2026-11-17

## Identity

| Field | Value |
| --- | --- |
| Package | **SW02** |
| Tracker | **ECE-37** |
| Role | runtime_audit_engineer |
| Owner (to launch) | `sw02_runtime_audit` (sibling worker) |
| Independent reviewer | `sw01_task_engineer` (must ≠ author) |
| Depends on | SW00 assignment (this brief) |
| Input commit | `f82908d62889fbd6ea3ffa79e041ac17ffb6b094` |
| Suggested branch | `cursor/sw02-audit-provenance-be8a` |
| Base for PR | `main` (or stack base) |
| CPU-only | **yes** — no GPU / no live judge qualification in this package |
| Handoff return path | `project/shortcut-study/handoffs/2026-11-17-sw02-<slug>.md` |

## Findings to close

- **IMPL-1** — standalone audit preparation does not bind terminal T to native request/response bytes
- **IMPL-2** — generator version provenance wrong across templates
- **IMPL-3** — approved-read telemetry not task-specific

Reproduce independently:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/implementation-reproduce.py
```

If `project/runs/` is missing (cloud hosts), build **fixture/temp-copy** regressions that deliberately alter T while keeping native bytes, and cite dated `implementation-results.json`. Do **not** rewrite authentic archives or claim raw authenticity without archives.

## Exact path allowlist (writable)

- `project/shortcut-study/src/shortcut_study/runner/`
- `project/shortcut-study/src/shortcut_study/audit/`
- `project/shortcut-study/tests/test_audit_pipeline.py`
- `project/shortcut-study/tests/test_native_runner.py`
- `project/shortcut-study/tests/test_sw02_provenance_telemetry.py` (create)
- `project/shortcut-study/handoffs/2026-11-17-sw02-*.md`
- `project/shortcut-study/results/development/sw02-*.json`

## Forbidden

`state.json`, `schemas/`, `configs/`, `qualification.py`, `held_out.py`, `__main__.py`, `tasks/`, `ids.py`, `splits.py`, `analysis/`, `reviews/`, historical terminals under `project/runs/` (read-only if present).

## Interface decisions

1. Standalone audit prep must verify T against **immutable native** evidence + validated extraction; recomputing self-hashes alone is insufficient.
2. Reuse strong recovery verification without replaying inference or mutating evidence.
3. Episode/qualification metrics use **actual assignment/generator version** and **task-specific** approved resources for all five TAB templates.
4. Versioned **derived corrections** only; never overwrite historical terminals/manifests.
5. Shared CLI/schema/qualification field changes: **propose → integrator applies**.

## Acceptance / regression targets

- Source-inconsistent T rejected; valid records still prepare
- Original HTTP bytes unchanged in tests
- All five templates report correct generator versions + authorized-read sets
- Missing/corrupted native sources fail clearly; interrupted records accounted for
- No new retries, remote endpoints, or lease bypasses
- Live semantic judge executor is **out of scope** for this first SW02 CPU handoff (separate later assignment)

## Deliverables

Fix + regressions + handoff + PR; request review from `sw01_task_engineer`.
