# Completion plan — November 7, 2026

The existing study has 240 main responses and 179 eligible automated acknowledgment
judgments. The remaining deliverable is a reproducible synthesis and final report.
The user has requested automated grading without human adjudication. This changes
the final reporting policy, not the frozen experiment or its prespecified endpoints.

1. **Audit existing evidence.** Run the workflow tests, verify the frozen source and
   all raw responses, independently check final-answer extraction, and reproduce
   the paired analysis and numbered-evidence validation.
2. **Strengthen automated evaluation.** Retain answer-key matching for correctness
   and exact wrong-option matching for the primary endpoint. Evaluate secondary
   conclusions under the existing semantic judge, phrase baseline, disagreement
   abstention, and complete removal of semantic labels. Add a bounded label-error
   sensitivity analysis and task-level diagnostics. These are postcollection
   robustness checks, not new confirmatory endpoints or accuracy validation.
3. **Write a readable final report.** Target four pages of main text, with references
   separate. Include the research question, related work, methods, principal results,
   limitations, and practical improvements. Generate figures/tables from verified
   results. Provide editable text, PDF, and reproduction commands.
4. **Verify and close.** Check the PDF layout, report numbers, source links, tests,
   and Git diff. Update the project entry points and record what was completed.

No new main responses will replace observed failures. Original raw evidence,
frozen protocol, historical reports, and preexisting uncommitted work are retained.
Semantic labels will remain explicitly machine-generated and unvalidated for
natural-language accuracy; human review is not a completion requirement for this
report. Course-specific final formatting instructions are absent from the repository,
so the proposal handout's four-page main-text guidance is the working format.

## Execution record

- Initial inspection: main collection and semantic annotation already complete;
  all 56 existing workflow tests pass. Historical documentation still refers to
  outstanding human review and needs a current reporting-policy addendum.
- **Step 1 complete:** audited all 240 raw responses and reference-key assignments,
  verified all 44 frozen files, independently parsed 239 complete finals, remerged
  all 179 eligible judgments, and exactly reproduced both saved analyses.
- **Step 2 complete:** added phrase-proxy, disagreement-abstention, no-label, and
  bounded label-error checks plus task diagnostics. All five judge–phrase
  disagreements concern wrong-hint agreements; one possible label error already
  allows either direction for the secondary effect. Added exhaustive small-case
  tests for the label-error bounds. All 58 workflow tests pass.
- **Step 3 complete:** generated the four-page main report, separate reference page,
  editable Markdown/template, and standalone figure. Bibliographic sources were
  verified against primary publications and the model card. No new model calls
  or human grading were used in this completion pass.
- **Step 4 complete:** rebuilt and rendered the five-page PDF, checked layout and
  page sections, and provided a portable statistics verifier using 240 exported
  derived rows. Current entry points now identify the completed report and
  distinguish the final reporting policy from historical plans.

The final report and methods are complete for the available frozen study. Future
replication, broader semantic calibration, and repeated-seed experiments are
research extensions, not unfinished work hidden behind a claim of completion.
Submission to the course and a separate presentation are outside this request.
