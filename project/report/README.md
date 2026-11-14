# Final report

**Submission deadline: December 4, 2026** (11:59pm ET under the general written-work policy), confirmed by the instructor in course discussion question #16. The project presentation date remains **TBD**. See the [course deadline table](../../README.md#deliverables-and-due-dates).

[Read the final report (PDF)](final-report.pdf) · [Readable Markdown](final-report.md)

Completed November 7, 2026. Four pages of main text plus one page of references
and reproducibility notes. The report uses automated answer-key scoring and
separate machine-generated acknowledgment labels. Human adjudication is not a
completion requirement. It does not claim that the semantic judge's accuracy has
been established. This final reporting decision supersedes the human-review
requirement in historical plans, without altering the frozen protocol.

The main finding is inconclusive for developer visibility: wrong-hint agreement
is 3.33–5.00 percentage points lower in the observed sample, but bootstrap
uncertainty spans zero. Adding the hint increases wrong-option agreement by
11.67 points. Secondary acknowledgment findings are sensitive to grading errors.

## Reproduce the statistics

Run from the repository root. Python's standard library is sufficient:

```sh
PYTHONPATH=project/src:. python3 -m unittest discover -s project/tests -q
PYTHONPATH=project/src python3 project/verify_final_results.py
```

The second command uses the 240 derived rows included in
[`final-automated-evaluation.json`](../results/final-automated-evaluation.json).
It reproduces the original 10,000-draw paired bootstrap without model calls,
downloads, or human labels. It checks statistical reproducibility, not raw-data
authenticity or semantic accuracy.

For the complete raw-source audit and postcollection robustness analyses, the
original local `project/runs/` and `project/data/` directories must be available:

```sh
PYTHONPATH=project/src:. python3 project/finalize_analysis.py --out /tmp/ece750-final-recheck.json
```

Use a fresh output path. This rechecks the pinned benchmark files, all 240 raw
responses and 44 frozen files, independently parses all 239 completed finals,
remerges the 179 numbered judgments, reproduces both original analyses, and
computes the postcollection robustness checks. No generations are performed.
All current source files must still match the original freeze for this audit.

## Rebuild the document

Use an isolated Python environment with the packages in `requirements.txt`:

```sh
python3 -m venv /tmp/ece750-report-build
/tmp/ece750-report-build/bin/pip install -r project/report/requirements.txt
/tmp/ece750-report-build/bin/python project/report/build_report.py --out /tmp/ece750-report-rebuilt
```

The default input is the final evaluation JSON. Editable prose lives in
[`report-template.md`](report-template.md); numeric placeholders and tables are
filled from the JSON. The builder creates Markdown, PDF, and PNG/PDF figure files,
and checks that the intended sections occupy five pages. Main text uses 10.5-point
embedded serif type, with 14-point leading and separate pages for methods,
results, and interpretation. The PDF was rendered and visually checked.

The completion environment lacked `venv`'s pip bootstrap, so the initial build
used a temporary environment with the official pip bootstrap installed separately.
No system packages or project runtime dependencies were changed. The repository
does not depend on that temporary environment; requirements are recorded here.

## Evidence and limitations

- [Completion plan and final reporting policy](../completion-plan.md)
- [Frozen protocol](../main-protocol-v1.md)
- [Original collected results](../results/main-reduced-v1-001-report.md)
- [Existing automated judging record](../results/main-reduced-v1-001-judging-report.md)
- [Final evaluation, provenance, robustness checks, and derived rows](../results/final-automated-evaluation.json)

The original protocol and historical reports are preserved, including their earlier
human-review language. Added label-error, phrase-proxy, abstention, and task-level
checks are explicitly postcollection. They do not retroactively validate the
judge or establish a new confirmatory finding. The report's course-specific
format has not been checked against a final handout, which is absent from this
repository; the four-page main-text target follows the proposal handout.
