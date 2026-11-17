# Package handoff — SW02 native provenance / audit / telemetry — 2026-11-17

- Owner and role: `sw02_runtime_audit` / runtime_audit_engineer (ECE-37)
- Status: ready_for_review
- Input commit and dependencies: `3f77a18475097fad9f7754b038cefaa6457af065` on `cursor/sw00-completion-baseline-be8a` (SW00 tip; assignment also named `f82908d`)
- Output commit (or explicitly uncommitted paths): see PR branch `cursor/sw02-audit-provenance-f2fa` (filled after push)
- Paths changed; shared-contract version:
  - `src/shortcut_study/runner/__init__.py` — episode generator version from assignment/`generator_version_for`
  - `src/shortcut_study/runner/native.py` — `verify_terminal_matches_native`, verification actor, HTTP digests
  - `src/shortcut_study/runner/metrics.py` — **new** task-specific `tool_operation_counts` + derived corrections
  - `src/shortcut_study/audit/pipeline.py` + `__init__.py` — `prepare_audit_from_episode_directory`; native prep requires binding
  - `tests/test_sw02_provenance_telemetry.py` — **new** IMPL-1–3 regressions
  - `tests/test_native_runner.py`, `tests/test_audit_pipeline.py`
  - `results/development/sw02-provenance-telemetry-v1.json`
  - Shared-contract proposals below (integrator-owned files untouched)
- Concrete behavior implemented:
  - **IMPL-1:** Bound audit prep verifies terminal channels against immutable native HTTP re-extraction (same fail-closed predicate as recovery). Altered T rejected; HTTP bytes unchanged. Mock prep unchanged. Valid native prep attaches `native_binding` digests.
  - **IMPL-2:** `initial_record` records `resolve_episode_generator_version` (catalog matches `generator_version_for`; retains historical `vertical-slice-stub-v0`; rejects wrong TAB01-slice stamps on other templates).
  - **IMPL-3:** New `runner.metrics.tool_operation_counts(ledger, approved_resources=...)` uses task-specific authorized sets for all five templates; versioned derived telemetry helpers for historical ledgers without rewriting terminals.
- Commands run and actual outcomes:
  - `PYTHONPATH=project/shortcut-study/src python3 -m unittest project.shortcut-study.tests.test_sw02_provenance_telemetry project.shortcut-study.tests.test_native_runner project.shortcut-study.tests.test_audit_pipeline` → **OK**
  - Broader: `test_qualification`, `test_held_out`, `test_tab_catalog`, `test_slice_execution`, `test_cpu_merge_review` → **OK**
  - Authentic reproducer `reviews/2026-11-17/implementation-reproduce.py`: **not runnable here** (`project/runs/` absent; missing deps initially then no archive root)
- Evidence/manifest paths and hashes:
  - `project/shortcut-study/results/development/sw02-provenance-telemetry-v1.json`
  - sha256 `b250b2f37a044e6192964bf90fb168d2efbad1147324009b6119753289513898`
  - Review citation (not re-measured): `reviews/2026-11-17/implementation-results.json` (304 / 208 / prepare_archive accepted altered T)
- Failures, uncertain findings, and scope limitations:
  - **No WSL/authentic held-out archives on this cloud host.** Fixture/temp-copy reproduction only; do not treat fixture runs as raw authenticity of G2 archive bytes.
  - Live semantic judge executor / qualification: **out of scope** (no judge success claimed).
  - `__main__.prepare_archive` still calls bare `prepare_audit` without binding → **now fails closed on native** until integrator rewires (intentional).
  - `qualification.tool_operation_counts` still TAB01-only until integrator migrates callers to `runner.metrics`.
  - Qualification/held_out paths that stamp every row with `GENERATOR_VERSION` will fail closed on non-matching templates at `initial_record` until schedule stamping is fixed.
- GPU lease owner/process/job, or no GPU work: **no GPU work**
- Terminal/incomplete/unattempted job IDs if applicable: none
- Next safe action and required dependency:
  1. **Integrator (SW00/SW05):** apply interface proposals below; re-run full extension suite; do not start new 320-ep qualification until SW05 accepts.
  2. **Independent reviewer `sw01_task_engineer`:** review this PR (author ≠ reviewer). Brief below.
- Acceptance reviewer, decision, and date (filled on review): pending `sw01_task_engineer`

## Integrator interface proposals (do not invent in SW02 paths)

### A. `__main__.prepare_archive` (IMPL-1 CLI wire-up)

Replace body with bound prep (preserve output filenames):

```python
def prepare_archive(episode_directory, output_directory):
    from .audit import judge_messages, prepare_audit_from_episode_directory
    episode_directory, output_directory = Path(episode_directory), Path(output_directory)
    bundle = prepare_audit_from_episode_directory(episode_directory)
    prepared = bundle["prepared"]
    messages = judge_messages(prepared)
    output_directory.mkdir(parents=True, exist_ok=False)
    write_new(output_directory / "prepared.json", prepared)
    write_new(output_directory / "messages.json", messages)
    write_new(output_directory / "manifest.json", {
        "status": "prepared_only_no_judge_inference",
        "episode_id": prepared["episode_id"],
        "binding": bundle["binding"],
        "input_sha256": bundle["binding"]["input_sha256"],
        "output_sha256": {
            name: hashlib.sha256((output_directory / name).read_bytes()).hexdigest()
            for name in ("prepared.json", "messages.json")
        },
    })
    return prepared
```

### B. `qualification.tool_operation_counts` (IMPL-3)

- Prefer importing `shortcut_study.runner.metrics.tool_operation_counts`.
- Call sites must pass `approved_resources=task.public_task["approved_resources"]` (or `approved_for(template_id)`).
- Publish derived corrections via `derive_corrected_telemetry` / `derive_corrected_provenance`; never rewrite historical `terminal.json` / `qualification.json`.
- Capability probe TAB01-only gate can keep TAB01 `APPROVED` explicitly, but catalog telemetry must not.

### C. Schedule stamping (`qualification.py` / `__main__.py` / `held_out.py`)

- Stop overwriting catalog rows with global `GENERATOR_VERSION`.
- Keep each assignment's `generator_version` from `generator_version_for` / catalog enumeration.
- Vertical-slice stub `vertical-slice-stub-v0` remains an explicit historical schedule label.

## Review brief for `sw01_task_engineer` (independent; must ≠ author)

Please verify:

1. **IMPL-1:** `tests/test_sw02_provenance_telemetry.py` + `test_native_runner.test_bound_audit_rejects_terminal_t_disagreeing_with_http` — altered T rejected; HTTP digests stable; valid native prep succeeds with `native_binding`.
2. **IMPL-2:** all five templates' mock episodes record matching `generator_version`; mismatch assignment fails closed; stub vertical-slice still runs.
3. **IMPL-3:** corrected metrics report task-specific approved reads; legacy `qualification.tool_operation_counts` still undercounts TAB02–05 (expected until integrator migrates).
4. Path allowlist respected; no edits to `state.json`, schemas, configs, `__main__.py`, `qualification.py`, course submission.
5. Evidence JSON limitations about missing archives are honest.
6. Integrator proposals are sufficient and do not require SW02 to own shared files.

Do not mark acceptance on predicted GPU/judge results. Preserve dated `reviews/2026-11-17/` outputs.

Do not mark acceptance based on predicted results. Preserve unsuccessful outputs and distinguish fixture behavior from measured model behavior.
