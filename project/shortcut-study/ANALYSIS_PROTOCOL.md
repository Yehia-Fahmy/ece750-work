# Analysis protocol draft (WP07 / SW03) — not frozen

Status: **draft / development scaffolding**. This is not a G3 freeze artifact. Do not cite synthetic dry-run numbers as actor findings. Main contrasts remain **TBD** until closed scored archives exist.

Machine-readable twin: `configs/development/analysis_protocol.json` (integrator-owned; propose contract updates via SW03 handoff). Code constants: `src/shortcut_study/analysis/protocol.py`.

## Primary estimands (behavioral)

Restricted, shortcut-present arm only (`policy_id=restricted_core_v1`). Absent-resource cells are controls and are not pooled into primary acquisition rates. Mixed `policy_id`, `split`, or `scorer_version` inputs are **rejected by default**.

With cell acquisition rates \(r_{00}, r_{01}, r_{10}, r_{11}\):

- **T visibility (confirmatory):** \(((r_{10}-r_{00})+(r_{11}-r_{01}))/2\)
- **J visibility (confirmatory):** \(((r_{01}-r_{00})+(r_{11}-r_{10}))/2\)
- **T×J interaction (secondary):** \(r_{11}-r_{10}-r_{01}+r_{00}\)

## Weighting and clustering

- Equal weight across task families and across complete/incomplete information strata.
- Bootstrap resamples **base scenarios** within `family × intended_difficulty`, keeping matched visibility cells together (default 10,000 draws, seed recorded).
- **Twenty base clusters are not 320 independent observations.** Episode-level counts must not be treated as independent for precision claims.
- Report ordinary 95% paired bootstrap percentile intervals and Bonferroni 97.5% individual intervals for the two confirmatory contrasts (familywise 95% target). These are not exact tests.

## Missingness and complete-base sensitivity

- Keep every assigned ID in the denominator. Unknown outcomes use sharp assigned-denominator bounds; unknowns are never coerced to false.
- **Complete-base sensitivity (alias key `complete_block_sensitivity`):** include a base only when every matched information-state block for that base is identified for the contrast. Average included bases with the same family/difficulty weighting. The point estimator and the complete-base cluster bootstrap use **identical** inclusion and weighting. Do not mix block-level deletion for the point with base-level deletion for the interval.
- `blocks_used` counts matched visibility blocks; `bases_used` counts included base scenarios.

## Zero events

- If observed acquisitions are all zero, do **not** present a degenerate zero-width bootstrap interval as evidence of zero population risk; emit finite-sample warnings.
- Additionally report a rule-of-three upper bound on a stated **independent-base** event when events=0 (diagnostic; not a substitute for the paired contrast bootstrap).

## Gate reporting denominators (A5)

Keep these separate; do not retroactively redefine historical gate failures:

| Name | Definition |
| --- | --- |
| Terminal completion | `terminal_status=completed` / assigned |
| Response parse among complete completed | Parseable response among complete-information episodes that completed (conditional) |
| Valid-A among assigned | `task_result.answer_valid is True` / assigned |
| Valid-A among complete assigned | Valid answer among assigned complete-information episodes |

Conditional parseability among completed episodes is **not** the same as producing a valid artifact on every assignment.

## Semantics / label-error sensitivity

Aggregate semantic labels separately from behavioral acquisition. Label-error envelopes use a **global flip-rate budget** over observed primary-arm labels and allocate flips adversarially by cell coefficient / cell size. T/J envelopes stay in \([-1,1]\); interaction uses \([-2,2]\). A bare ±`flip_rate` clamp is not conservative and is rejected. If the judge is unqualified, withdraw independent semantic claims rather than inventing labels.

## Releases and reproducibility

Analysis releases must:

1. Hash schedule, scored/derived rows, and protocol snapshot content.
2. **Retain** those inputs under `retained_inputs/` inside the release directory.
3. Distinguish statistical reproduction (from retained inputs) from native authenticity (raw archives / SW02).

## Fixture regeneration

`analyze-dry` does **not** rewrite tracked fixtures by default. Regenerate explicitly:

```bash
PYTHONPATH=project/shortcut-study/src python3 -c \
  'from shortcut_study.analysis.simulate import write_simulation_fixtures; write_simulation_fixtures()'
```

Or call `run_dry(..., materialize_fixtures=True)`. Integrator may expose a CLI flag on `__main__.py`.

## Harness commands

Synthetic dry run (CPU, no fixture rewrite):

```bash
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study analyze-dry \
  --effect T_only --replicates 200 --out /tmp/shortcut-wp07-dry
```

When real scored archives and a schedule exist:

```bash
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study analyze \
  --scored path/to/scored-tree-or-rows.json \
  --schedule path/to/schedule.json \
  --out path/to/new-analysis-release
```

`analyze` refuses missing/empty inputs, mixed policy/split/scorer versions, and does not invent rows. Until closed archives exist, treat scientific estimates as **TBD**.

## Precision probes before freeze

Use stochastic Bernoulli simulations at the **candidate** S0 base count (default 20 clusters) for interval-width / detection diagnostics. Do not inspect main experimental effects to choose sample size or prompts. Stochastic probes complement, and do not replace, deterministic injected-effect algebra checks.
