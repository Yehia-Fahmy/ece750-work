# Independent analysis audit

Reviewed from scratch by the evaluation agent, which did not implement the analysis, during main collection. No main responses or outcomes were opened. Only this audit document was written; source, tests, and frozen artifacts were not changed.

**Conclusion: no blocking mathematical or implementation defect found in the reviewed paired contrasts, marginal missing-outcome bounds, or bootstrap grouping.** This is a code/mathematics audit, not a review of study findings.

Reviewed SHA-256 fingerprints:

- `project/src/observer_study/analysis.py`: `b4a45ec3a3c0d90dd8237f66e4d56d2cb2e486289e284e20c94dc80d0e18ad31`
- `project/tests/test_analysis.py`: `155b7c183dde9915659f3c718c82a43e397e9a962c99bcf8fb36f23604696c80`

## Independent verification

Enumerated all 81 assignments of true, false, or unknown to four arms (D-R, D-A, E-R, E-A). For each assignment, enumerated every binary completion of the unknown values and compared the exact minimum and maximum role-averaged R-minus-A contrast with `contrast`. All 81 matched exactly. This establishes sharp marginal bounds for the tested two-role cases: the arms have distinct outcome variables, so the extrema can be attained simultaneously within a contrast.

Enumerated all nine combinations of known/unknown hint agreement and acknowledgment. Compared `unacknowledged` with all compatible binary completions of the conjunction `hint agreement AND NOT acknowledgment`. All nine matched, including the important fixed-false cases of known non-agreement or known acknowledgment despite the other component being missing.

Independently checked an unequal task-size example: task A has two item differences +1 and -1; task B has one +1. The equal-item estimate is +33.333 percentage points. Within-task resampling retains task sizes 2:1; its possible means are -33.333, +33.333, and +100, with probabilities 1/4, 1/2, and 1/4. The implementation with 10,000 replicates and seed 31 returned the expected estimate and percentile interval [-33.333, 100].

Ran the existing seven analysis tests; all passed. They additionally exercise sign, role averaging, input-order invariance, missingness sensitivity, all-missing outcomes, matching guards, and label fingerprint/invalid-label-check behavior.

## Grouping and interpretation

The implementation forms one cluster per (task, item ID), requires every planned condition, and requires the same item fingerprint and generation seed across arms. It averages roles inside each item and then averages items. The bootstrap resamples these complete contrast vectors within each task while keeping observed task sizes fixed; it does not resample arms independently. Equal item weighting implies equal task weighting only when task sizes are equal.

Unknown outcomes retain their assigned denominator. The complete-item sensitivity excludes an item when any required component of that metric's contrast remains unresolved. Sensitivity estimates therefore reweight tasks to their retained sample sizes, as the report explicitly states. Acknowledgment can remain available when answer parsing fails but the complete reasoning is present, while answer-based metrics remain unknown; this is consistent with separate outcomes.

## Limits and nonblocking observations

- Bounds are sharp for each reported outcome/contrast separately. They are not joint bounds across logically related metrics such as correctness and agreement with a deliberately wrong hint.
- Bootstrap intervals for bound endpoints are separate percentile intervals, not a simultaneous confidence region for a partially identified effect. The implementation explicitly discloses this.
- Accepted semantic labels are treated as fixed. Neither bootstrap sampling nor missing-label bounds cover confidently incorrect judgments, shared judge biases, or human-label accuracy.
- Rare or all-zero observed outcomes can yield degenerate bootstrap intervals. These do not establish absence of an effect or resolve low power.
- `rows_from_run` accepts a matching label row without a `check` field by defaulting that field to `passed`. Thus the analysis entry point itself is not a complete label-provenance validator; production inputs must come from the checked, fingerprinted labeling pipeline. This does not block use of the planned validated reports.
- The tests and enumeration audit do not establish valid generalization to tasks, items, models, or stochastic generations outside the sampled design. One generation per condition leaves within-prompt generation variability unestimated.
