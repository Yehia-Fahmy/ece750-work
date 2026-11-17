# Original observer-study verification

Review date: 2026-11-17 (America/Toronto). Input commit: `3c155ba`.
Reviewer: root/integration reviewer. Review only; no historical files changed.

## Assessment

The original study's reported numerical results reproduce from both committed derived rows and the available local raw evidence. Its report appropriately describes the visibility result as inconclusive and its automated semantic labels as unvalidated and exploratory. This review did not establish semantic accuracy, benchmark cleanliness, or broader generalization; the report already discloses these limitations.

The separate shortcut extension is incomplete. Its failures and unresolved work should not be attributed retroactively to this completed original experiment. Conversely, the original report's completion does not establish completion of the extension.

## Checks and actual outcomes

Commands ran from `/home/yehia/ece750-work` using Python 3 and no model inference:

```sh
PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q
PYTHONPATH=project/src python3 project/verify_final_results.py
PYTHONPATH=project/src:. python3 project/finalize_analysis.py --out /tmp/ece750-review-final-recheck-20261117.json
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
```

- Original suite: **58 tests passed**.
- Extension suite: **213 tests passed**. Passing tests do not resolve the separate scientific and implementation findings in this review.
- Statistical reproduction: **240 derived rows**, primary, secondary, correctness, and control statistics reproduced.
- Raw audit: **240 assignments and raw responses** checked; **239 completed final answers** independently parsed; **179 eligible judgments** remerged; **44 frozen files** verified; no changed scores or technical retries.
- Both original unlabeled and labeled analyses reproduced using the prescribed 10,000-draw bootstrap.
- The newly generated full evaluation JSON equals the committed `project/results/final-automated-evaluation.json` as parsed JSON, with **no differing top-level fields**.
- Independently computed SHA-256 hashes match all **111 historical files** in `preservation-manifest.json`, plus its separately listed original design snapshot.

The original raw archives, benchmark inputs, and retained model symlink are present locally. `nvidia-smi` is unavailable in this review environment; no GPU process was started. GPU qualification was reviewed from archived evidence, not rerun.

## What remains limited

The numerical reproduction is strong evidence of consistency between retained inputs, code, and reported statistics. It does not independently establish the truth of every machine-generated semantic label. The original report explicitly acknowledges lack of natural negative-class validation, five judge/proxy disagreements concentrated among hint-agreeing cases, and label-error sensitivity. Its single-model, single-seed scope and benchmark exposure risk also remain.

The source-only repository supports statistical reproduction from derived rows. Raw authenticity checks additionally require the ignored local archive; it is available here, but is not distributed through Git. The final course formatting requirements and presentation arrangements remain unresolved in the repository. No course submission was performed.
