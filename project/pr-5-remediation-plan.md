# PR #5 remediation plan

Prepared against PR head `a648e15`. Implement and validate in the isolated review worktree, using a new fix branch before committing. This plan covers the four review findings; acknowledgment automation, the pilot, and statistical analysis remain later milestones in the research plan.

## Constraints

- Preserve existing configurations, prepared items, manifests, responses, review sheets, and aggregate evidence. Use fresh paths for any new run or corrected analysis.
- Keep the matched items, hints, seeds, condition wording, sampling settings, and assigned-item denominators fixed. These fixes should not introduce a new experiment.
- Keep unknown outcomes unknown. Never regenerate an answer to improve correctness, parsing, or rationale content.
- Retain the existing code-fingerprint guard on resume. Historical runs belong to their original implementation; use that revision to resume them, or create a fresh run with the corrected harness.

## 1. Make contradictory answer markers unresolved

Files: `src/observer_study/scoring.py`, `tests/test_study.py`.

- Separate detection of competing marker occurrences from validation of the accepted answer line. Search the entire final-answer text for competing `FINAL_ANSWER` markers, including embedded markers and malformed spacing around the colon.
- Keep the accepted label grammar strict: one valid marker line or a response consisting solely of a valid option. Preserve compatibility with the original profile's explanatory text around a single marker; never search the reasoning field for an answer or infer a label from prose.
- Return an unresolved parse result for competing markers, including repeated identical markers. Keep accuracy and hint agreement unknown when parsing is unresolved.
- Add cases for an embedded correction, a second malformed marker, duplicate identical markers, invalid options, the standalone-option fallback, and valid historical explanatory responses. Test the resulting score and summary bounds as well as the parser result.

Acceptance: `FINAL_ANSWER: (A)\nCorrection: FINAL_ANSWER: (B)` cannot become a known A outcome. Existing valid single-marker and standalone answers retain their scores.

## 2. Make retry lifecycle states accurate

Files: `src/observer_study/runner.py`, `src/observer_study/summary.py` if needed, `tests/test_study.py`.

- Keep the request nonterminal throughout an allowed retry, including the delay between attempts. Persist the active state before sending each attempt.
- Set `technical_error` only for a nonretryable failure or an exhausted retry budget. Preserve every attempt's body, error, timestamps, and elapsed time.
- Keep interrupted active requests unresolved on resume and do not issue another generation for them. Handle legacy records whose status is `technical_error` but whose latest attempt has no finish timestamp as interrupted rather than completed failures.
- Test summaries during retry backoff and during the retry itself, successful retry completion, exhausted retries, and interruption followed by resume. Verify that resume preserves attempts and makes no replacement request.

Acceptance: with 23 completed requests and the last request awaiting or executing a retry, both `collection_finished` and `observed_targets_met` are false. Terminal failures still contribute unknown outcomes over all assigned requests.

## 3. Capture incomplete HTTP responses as technical failures

Files: `src/observer_study/io.py`, `tests/test_study.py`; extend error-record fields only if needed to retain partial-response evidence.

- Catch `http.client.IncompleteRead` at the HTTP boundary and convert it into a retryable `RequestError`.
- Retain the partial body and truncation metadata. Preserve bytes losslessly when the interruption splits a UTF-8 character, with a readable representation for inspection.
- Apply the same handling when reading an HTTP error body; an incomplete error response must not escape the technical-failure path.
- Reuse the existing retry limit. Keep complete non-JSON responses nonretryable and retain existing HTTP retry eligibility.
- Test the client exception conversion and runner integration: partial body followed by success, repeated truncation exhausting the budget, an incomplete HTTP error body, and continuation to subsequent scheduled requests.

Acceptance: truncation produces a saved technical attempt rather than an uncaught exception; the retry limit is respected, and exhausted requests remain unknown without stopping collection of later requests.

## 4. Verify model and backend invariants in smoke comparisons

Files: `src/observer_study/summary.py`, `tests/test_study.py`.

- Require agreement on the verified model checksum, runtime build, chat template, and server generation defaults, in addition to the existing item, hint, condition, seed, and request-sampling checks. Reject missing identity evidence with a specific error.
- Permit the documented changes to prompt version, context allocation, and output allowance. Implementation fingerprints may differ between versions. Compare weight checksums rather than requiring identical local model paths.
- Include the checked model/backend identity and the permitted differences in newly generated comparison output so the result records what was verified.
- Test each invariant independently, with one changed field per case. Include missing provenance, the same weights at different local paths, and the legitimate original-to-v2 comparison.

Acceptance: changing weights under the same model alias, changing runtime/template, or changing a server sampling default rejects comparison. The retained original and v2 runs still qualify as paired inputs.

## Validation and evidence update

1. Promote the four review reproductions into repository regression tests and implement the targeted cases above. Keep fixtures small and inference-free.
2. Run `PYTHONPATH=project/src python3 -m unittest discover -s project/tests -v` and `git diff --check`.
3. Audit all 48 retained smoke responses with the corrected parser without rewriting cached scores. Report any changed classifications explicitly; save corrected aggregates under new filenames if required.
4. Regenerate the strengthened comparison to a new output path. Verify that any differences from the archived comparison are explained by added provenance checks or documented scoring corrections.
5. Recheck all 31 preserved artifact hashes. Record the fix validation, scoring audit, and historical-resume instructions in the README/protocol/research log.

No new GPU run is required to establish these four fixes. Use recorded evidence and deterministic failure injection; undertake a fresh smoke run only if validation reveals a generation-path change that those checks cannot resolve.

Deliver the changes as four focused fixes with their regression tests, followed by the evidence/documentation update. Completion requires all tests passing, each reproduced defect covered, historical artifacts preserved, and no unexplained scoring changes.

## Implementation status — October 14, 2026

All four fixes are implemented in separate commits. All 24 tests pass, including a read-only audit regression test. The [48-response audit](results/pr-5-scoring-audit.json) found no changed scores, and the [strengthened comparison](results/smoke-comparison-reviewed.json) preserves every original metric. All 31 original preservation hashes and the 68-file pre-fix historical snapshot match. See the [research log](research-log.md) for validation details and the README for reproduction and historical-resume instructions.
