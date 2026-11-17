# Worker assignment brief — SW03 statistics / release inputs — 2026-11-17

## Identity

| Field | Value |
| --- | --- |
| Package | **SW03** |
| Tracker | **ECE-38** |
| Role | analyst |
| Owner (to launch) | `sw03_analyst` (sibling worker) |
| Independent reviewer | `sw02_runtime_audit` (must ≠ author) |
| Depends on | SW00 assignment (this brief) |
| Input commit | `f82908d62889fbd6ea3ffa79e041ac17ffb6b094` |
| Suggested branch | `cursor/sw03-analysis-release-be8a` |
| Base for PR | `main` (or stack base) |
| CPU-only | **yes** |
| Handoff return path | `project/shortcut-study/handoffs/2026-11-17-sw03-<slug>.md` |

## Findings to close

- **A1** — complete-block point vs bootstrap interval use different populations
- **A2** — label-error sensitivity not conservative (wrong interaction range)
- **A3** — analysis releases lack hashed/retained exact inputs
- **A4** — mixed policy/eligibility pooling risk (conditional)
- **A5** — parseability / valid-A denominator definitions

Reproduce independently:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-repro.py
```

Orchestrator already reconfirmed A1/A2/A4 mismatch on this host at the input commit.

## Exact path allowlist (writable)

- `project/shortcut-study/src/shortcut_study/analysis/`
- `project/shortcut-study/tests/test_analysis.py`
- `project/shortcut-study/tests/test_sw03_analysis_release.py` (create)
- `project/shortcut-study/fixtures/analysis/`
- `project/shortcut-study/ANALYSIS_PROTOCOL.md`
- `project/shortcut-study/handoffs/2026-11-17-sw03-*.md`
- `project/shortcut-study/results/development/sw03-*.json`

## Forbidden

`state.json`, shared configs/schemas (propose changes), `qualification.py`, `held_out.py`, `__main__.py`, `tasks/`, `runner/`, `audit/`, `reviews/`.

**Note:** `analyze-dry` currently regenerates tracked fixtures — fix side effects so read-only reproduction does not rewrite fixtures unless an explicit regen command is used.

## Interface decisions

1. One documented **complete-block/base sensitivity estimand**; identical inclusion/weighting in point estimator and cluster bootstrap.
2. Label-error bounds from actual contrast coefficients/weights + explicit error budget; correct interaction range.
3. Reject mixed policies/splits/versions by default; validate serialized inputs and matching schedule fields.
4. Release manifests **hash and retain** schedule, scored data, source/protocol, and outputs for clean-checkout statistical reproduction.
5. Distinguish completion / response-parse / valid-A denominators; do not retroactively change old gate counts.
6. Precision / zero-event / template sensitivity simulations at candidate S0 scope before freeze (CPU); semantic-only pieces may be deferred if scope withdraws semantics.

## Acceptance / regression targets

- Heterogeneous-missingness example → coherent point/interval
- Allowed adversarial flips fall inside bounds
- Wrong-policy/version inputs reject
- Release inputs verifiable/replayable after external paths unavailable
- Weighting/missingness/zero-event/multiplicity match documented estimands

## Deliverables

Fix + regressions + updated protocol notes + handoff + PR; request review from `sw02_runtime_audit`.
