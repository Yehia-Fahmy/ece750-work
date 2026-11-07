# Main freeze audit

Audit completed November 6, 2026 (America/Toronto), during collection and before inspecting main response contents or outcome summaries. This is a separate agent review of the coordinator's freeze and preparation. The reviewing agent authored the analysis module, so the analysis checks are author verification rather than an independent implementation review. No generation, scoring, analysis source, frozen document, or frozen input was changed.

**Result: no blocking discrepancy found.**

## Provenance and sample checks

- Recomputed SHA-256 for all 44 files in `main-reduced-v1-freeze.json`; every current file matches its frozen hash.
- Checked `source-inputs.tar.gz` against its archive hash and every archived member against the recorded individual hash. All match.
- Recomputed the package source fingerprint; it equals both freeze record and active main manifest fingerprint. Configuration and prepared-item content hashes agree with the freeze and main-run identity. The run's full configuration equals the frozen configuration.
- Freeze timestamp is `2026-11-07T04:33:40.921837+00:00`; main manifest creation is `2026-11-07T04:33:56.572293+00:00`. The recorded freeze precedes the run's manifest. This establishes local recorded ordering, not externally certified preregistration.
- Main manifest contains exactly the first 20 previously reserved main items per task in their original reservation order: 60 items total. Selected item dictionaries are unchanged, including targets, question hashes and wrong hints. The reduced manifest's original-reservation hash also matches.
- Rebuilt both original eight-condition main schedule and reduced schedule. Every selected request, including its full prompt, decoding payload and generation seed, exactly matches the corresponding originally reserved request. The active run's complete 240-request schedule matches the rebuilt reduced schedule. Each of C0, C1, D-R and D-A has 60 assignments.
- Main IDs and question hashes are disjoint from all original non-main reserved items. Fresh natural-validation IDs and question hashes are disjoint from every original reserved item, including both selected and unused main items.

## Protocol and implementation agreement

The frozen protocol and configuration transparently identify wrong-hint agreement as primary, with D-R minus D-A over all assigned matched items. They retain the original unacknowledged endpoint as secondary. The change is motivated by pilot outcome prevalence and labeling feasibility; the documents do not select a role or endpoint according to the pilot visibility contrast. This review cannot independently establish private decision motives, but the explicit recorded rationale and before-main ordering are consistent.

The analysis computes within-item role differences and averages all assigned items. For this one-role balanced design, this is precisely the frozen contrast and equal weighting of the three task means. Bootstrap resampling retains complete item clusters, fixed sample sizes within each task, and all paired arms. The linear percentile interpolation, 10,000 replicates and configured seed 750 are supported.

For unknown outcomes, the implemented paired bounds subtract opposing lower/upper endpoints and retain every assigned item. Secondary conjunction logic follows the frozen protocol: known non-hint agreement or accepted acknowledgment=yes establishes zero; agreement=yes and acknowledgment=no establishes one; otherwise it is unknown. Incomplete traces cannot provide accepted labels. Missing and failed-check labels remain unknown. Label input fingerprints, duplicate/foreign labels, mismatched item identity/seed, and missing scheduled conditions are checked. Complete-item sensitivity is disclosed separately with retained task counts. Bounds do not account for semantic label errors, and bound-endpoint intervals are not claimed as joint confidence regions.

**Operational requirement:** the generic CLI defaults differ from this particular frozen protocol. Execute main analysis with explicit `--roles D --seed 750 --replicates 10000`. The generic CLI does not automatically enforce the configuration's analysis settings; preserving the executed command and output metadata is necessary. No source change is needed during collection.

The acknowledgment-reliability gate departure is explicit. Fresh checks contain three natural positive cases and constructed negative/ambiguous cases; this does not establish natural negative/ambiguous accuracy or human validation. Primary answer scoring is independent of these acknowledgment judgments. Strong secondary acknowledgment claims must await the researcher checks already required by the frozen protocol. The reduced design supports only the developer role and offers no guaranteed power for the rare secondary endpoint.

## Tests

Ran `PYTHONPATH=project/src python3 -m unittest discover -s project/tests -v`: **56 tests passed**. These include seven analysis tests covering hand-calculated contrasts, bootstrap stratum support and row-order reproducibility, role averaging and sign, unknown bounds, all-missing cases, complete-item counts, matching rejection, and label provenance. Other tests cover answer parsing, failures, conditions, evidence extraction, and fresh selection. Tests use fixtures and temporary directories; no main responses were read or regenerated.
