> November 7 completion: the [final report](report/final-report.pdf) and [reproduction package](report/README.md) are complete. See the [executed completion plan](completion-plan.md). Automated grading, raw audits, statistical reproduction, and grading-error sensitivity checks are complete. Human adjudication is not required under the user's final reporting decision; acknowledgment accuracy remains unvalidated and its conclusions exploratory. The dated plan below is historical.

# Next steps after PR #5

Reviewed October 29, 2026, against merged commit `cc1bc79`.

## Verified state

- PR #5 is merged. Local `main` matches GitHub, and the working tree was clean before adding this plan. There are no open pull requests.
- The review worktree is clean; its `project/` tree matches merged `main`. The older research worktree remains at `a648e15`, behind its remote branch, with an untracked `AGENTS.md`.
- All **27 standard-library tests pass** on merged `main`; `git diff --check` passes. Older notes describing 24 tests are historical validation records.
- The retained refined smoke run has **24/24 complete, parseable responses**, across three questions. A fresh read-only paired comparison verifies all 24 pairs and the recorded quality gates. This is technical evidence, not evidence of an observer effect or general task reliability.
- Repreparing items from the pinned cached data exactly reproduces the retained v2 manifest: 3 smoke, 6 pilot-development, 6 pilot-validation, and 120 main questions. Both pilot splits successfully dry-run as **48 requests each** using the merged implementation.
- No pilot/main run is present in the inspected research run directory. Label import/validation, automated acknowledgment labeling, and paired statistical analysis are not implemented. The protocol remains draft, and main inference is blocked by that status.
- Weights, runtime, cached data, and raw smoke evidence live under `.worktrees/research-project-plan/project/`. They are absent from the main checkout's default local artifact paths. Preserve that worktree until these files have a verified durable home.

## 1. Prepare the pilot from merged code — October 29–30

- [x] Create a focused branch from merged `main` in the current checkout; avoid collecting with the stale research worktree's implementation.
- [x] Reuse the existing verified weights/runtime through ignored local paths, avoiding another download. Retain original raw run directories and their original implementation fingerprints.
- [x] Add a versioned pilot configuration derived from `configs/smoke-v2.json`, retaining native thinking, v2 prompts, 16,384 context tokens, 8,192 output tokens, sampling, seed, and retry policy. Keep protocol status draft.
- [x] Prepare a new manifest; verify all item IDs, split assignments, hints, and source hashes match the reserved v2 sample. Configuration hashes may change with the new protocol version.
- [x] Document separate development and validation commands with fresh run directories, review exports, and summary paths. Confirm model checksum, full GPU offload, context, and formatted prompts during preflight.

**Done when:** both 48-request schedules dry-run successfully from merged code, disjointness is verified, and every runtime/data/output path is explicit.

Completed October 29 on `codex/prepare-pilot`; see the [pilot runbook](pilot.md) and [preparation evidence](results/pilot-v1-preparation.json). No pilot inference or acknowledgment labeling was performed.

## 2. Run development and establish human labels — October 30–31

- [ ] Collect the six pilot-development questions across all eight conditions, preserving all attempts and failures.
- [ ] Summarize completion, parsing, timing, and memory observations by task/condition. Inspect no-hint correctness and hint-response variation; six questions give only a preliminary suitability check.
- [ ] Have the researcher review rationales with the existing blank review export. Record `yes`, `no`, or `uncertain`, an evidence span, and coding time. Explicit rejection of a suggestion counts as acknowledgment; repeating its answer alone does not.
- [ ] Implement label import and validation: reject duplicate/unknown IDs, invalid labels, and missing required fields; retain absent/uncertain labels as unknown. Join through the saved mapping, and preserve human labels separately from automated predictions.
- [ ] Use these development examples to settle the acknowledgment rubric and choose manual coding or an automated labeler. If automation is used, record its version, exact instructions, usage/cost, and outputs. Do not depend on an unverified service.

**Done when:** a development summary, timed human labels, operational rubric, and measured labeling workload exist. No held-out validation examples have been used to tune the rubric or labeler.

## 3. Validate and choose the study size — October 31–November 1

- [ ] Freeze the development rubric/labeler, then collect the six held-out pilot-validation questions across all eight conditions.
- [ ] Review held-out labels without exposing automated predictions. Report class counts, uncertain cases, positive-class precision/recall where estimable, and uncertainty. A provisional target is about 0.90 precision and recall; a small or rare-positive sample may be inconclusive.
- [ ] Check observed completion ≥95% and parsing among completed outputs ≥99%, retaining all assigned requests in denominators. Inspect task suitability and estimate main inference/review time from pilot measurements.
- [ ] If validation prompts a rubric/model change, record the change and obtain new held-out evidence rather than continuing to describe the same validation examples as untouched.
- [ ] Choose the planned **120 questions × 8 conditions = 960 generations**, or the documented fallback of **60 questions × 4 conditions = 240 generations**, using one observer selected before main results. Record any sample/split changes explicitly.

**Done when:** a dated go/no-go decision justifies task selection, labeling reliability, study size, and available time. November 1 is a planning target; unresolved validation moves main collection later or reduces scope.

## 4. Finish analysis tooling and freeze methods — before main inference

- [ ] Implement the primary outcome: wrong-hint agreement without acknowledgment, retaining genuinely unresolved outcomes as unknown.
- [ ] Implement the rationale-visible minus answer-only contrast averaged across observer roles, task-stratified paired bootstrap intervals, and all-assigned missing-outcome bounds. Keep every condition for a question together when resampling.
- [ ] Add per-condition accuracy, hint agreement, acknowledgment, completion, and failure tables; mark role-specific comparisons exploratory and complete-pair analysis as sensitivity analysis.
- [ ] Validate analysis using small hand-calculated examples, including missing labels/answers, matched grouping, sign of the contrast, and reproducible bootstrap draws. Do this before inspecting main outcomes.
- [ ] Update `protocol.md` with exact prompts, tasks/items, acknowledgment scope, runtime/model, output limits, retries, uncertainty handling, analysis settings, and pilot decisions. Create a frozen main configuration and regenerate/verify its manifest without changing reserved IDs unintentionally.
- [ ] Commit the collection/analysis implementation before inference so source fingerprints stay stable during collection and resume.

**Done when:** the frozen methods and executable analysis agree, tests pass, and main preflight succeeds under the recorded configuration.

## 5. Collect, validate, and write

| Target | Deliverable |
| --- | --- |
| November 2–8, conditional on the gates above | Main inference and labeling, complete manifests/counts, preserved failed/interrupted requests, and aggregate capture diagnostics. |
| November 9–15 | Human validation across conditions/predicted classes, uncertain-case review, paired estimates/intervals, missing-outcome bounds, and checked figures/tables. Expand validation if positive examples are too rare for useful reliability estimates. |
| November 16–22 | Complete report draft with methods, results, limitations, reproducibility instructions, citations, and AI-assistance disclosure. Freeze experiments by November 22. |
| November 23 onward | Revise report, prepare/rehearse slides, and submit under confirmed course instructions. Keep the November 27 micro-survey in the schedule. |

Check LEARN now for proposal feedback and authoritative final-report/presentation requirements. The instructor has confirmed the report deadline as December 4, 2026; the presentation date remains TBD. Report page limits still conflict in the available materials. Maintain a four-page core as a working layout until the final instructions are confirmed.

Keep additional models, extra seeds, and paraphrase studies optional until the core study is validated and the report draft exists. Clean up old branches/worktrees only after ignored evidence and runtime assets are preserved; squash merging means commit ancestry alone does not establish that a branch's contents are unmerged.

## Immediate next unit of work

Prepare the pilot configuration and explicit local artifact paths, add validated human-label import, and collect the **48-request development pilot**. Deliver its aggregate diagnostics and blank researcher review sheet before using the held-out validation split.
