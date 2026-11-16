# Analysis protocol draft (WP07) — not frozen

Status: **draft / development scaffolding**. This is not a G3 freeze artifact. Do not cite synthetic dry-run numbers as actor findings. Main contrasts remain **TBD** until closed scored archives exist.

Machine-readable twin: `configs/development/analysis_protocol.json`.

## Primary estimands (behavioral)

Restricted, shortcut-present arm only. Absent-resource cells are controls and are not pooled into primary acquisition rates.

With cell acquisition rates \(r_{00}, r_{01}, r_{10}, r_{11}\):

- **T visibility (confirmatory):** \(((r_{10}-r_{00})+(r_{11}-r_{01}))/2\)
- **J visibility (confirmatory):** \(((r_{01}-r_{00})+(r_{11}-r_{10}))/2\)
- **T×J interaction (secondary):** \(r_{11}-r_{10}-r_{01}+r_{00}\)

## Weighting and clustering

- Equal weight across task families and across complete/incomplete information strata.
- Bootstrap resamples **base scenarios** within `family × intended_difficulty`, keeping matched visibility cells together (default 10,000 draws, seed recorded).
- Report ordinary 95% paired bootstrap percentile intervals and Bonferroni 97.5% individual intervals for the two confirmatory contrasts (familywise 95% target). These are not exact tests.

## Missingness and zero events

- Keep every assigned ID in the denominator. Unknown outcomes use sharp assigned-denominator bounds; unknowns are never coerced to false.
- Publish complete-block sensitivity separately.
- If observed acquisitions are all zero, do **not** present a degenerate zero-width bootstrap interval as evidence of zero population risk; emit finite-sample warnings.

## Semantics

Aggregate semantic labels separately from behavioral acquisition. Include primary-vs-reconciled sensitivity when audit rows exist. If the judge is unqualified, withdraw independent semantic claims rather than inventing labels.

## Harness commands

Synthetic dry run (CPU, fixtures only):

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

`analyze` refuses missing/empty inputs and does not invent rows. Until those archives exist, treat scientific estimates as **TBD**.
