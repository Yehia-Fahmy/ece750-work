# Completion work packages

Read [SWARM_START](SWARM_START.md) first. This is the current dependency/acceptance plan over the original [WP00–WP13](WORK_PACKAGES.md); it does not erase them. **Statuses, owners, reviewers, branches, and evidence live only in `state.json.swarm_handoff.packages`.** All paths below are relative to this extension. A worker may write only the paths explicitly assigned by the orchestrator; requests to change shared interfaces go through the integrator.

The dated reviews contain exact source locations and reproduction scripts. Independently establish the current behavior before fixing it. Preserve the dated review and old output JSONs unchanged; new tests/evidence belong under tests and newly versioned results/handoffs. A review report is evidence to evaluate, not authority to blindly edit code.

## Ownership and dependency map

| ID | Role / permitted area to assign | Dependencies | Original work / findings |
| --- | --- | --- | --- |
| SW00 | Orchestrator: state, contracts, shared CLI/config/dependencies, integration and scope | None | Current baseline and all handoffs |
| SW01 | Task engineer: `src/shortcut_study/tasks/tables/`, `src/shortcut_study/ids.py`, `src/shortcut_study/splits.py`, assigned files in `tests/` | SW00 assignment | WP01/02/08; RD1–3 |
| SW02 | Runtime/evaluation engineer: `src/shortcut_study/runner/`, `src/shortcut_study/audit/`, assigned files in `tests/` | SW00 assignment | WP03–06; IMPL-1–3 |
| SW03 | Analyst: `src/shortcut_study/analysis/`, `tests/test_analysis.py`, `fixtures/analysis/`, `ANALYSIS_PROTOCOL.md` | SW00 assignment | WP07; A1–5 |
| SW04 | Report/evidence author: `report/`, source/claim ledger; small derived evidence exports | SW00 assignment; final narrative follows later evidence | WP12; RD2/RD4/literature |
| SW05 | Independent CPU reviewer + integrator | SW01–03 | Integrated acceptance before new qualification |
| SW06 | Single GPU operator + independent qualification reviewer | SW05; credible development capability | WP05/06/08; new actor/judge/forecast evidence |
| SW07 | Integrator + analyst + independent freeze reviewer | SW06 and all required analysis/contracts | WP08; executable frozen main path |
| SW08 | GPU operator, audit engineer, analyst | SW07 | WP09–11; main collection, optional qualified semantics, analysis |
| SW09 | Report/build author + independent reproduction reviewer | SW04 and SW08 **or** dated S4 fallback | WP12/13; PDF/deck/notes/reproduction/delivery |

**Shared-file rule:** `src/shortcut_study/qualification.py`, `src/shortcut_study/held_out.py`, `src/shortcut_study/__main__.py`, files under `configs/` and `schemas/`, dependency metadata, and `state.json` remain integrator-owned. SW01 supplies a batch-allocation interface proposal; SW02 supplies provenance/telemetry and judge interface proposals; the integrator integrates their shared wiring sequentially. Do not have two workers edit qualification or CLI wiring at once. New helper modules can be assigned exclusively to a worker after agreement.

Suggested waves: SW01/02/03 concurrently; orchestrator handles SW00 and lightweight SW04 reconciliation. Then rotate one completed author into report work and use a different worker to review their changes. After SW05, one GPU owner runs SW06 while CPU analysis/report work continues. SW07 integrates the accepted freeze and executable path. During SW08, CPU workers verify closed batches and prepare outputs without leaking main contrasts to prompt developers. SW09 runs for either S0 or S4; it is never canceled because science failed.

## SW00 — establish the execution baseline and contracts

Record actual commit/branch, current Toronto date, available CPU/RAM/GPU, local archive paths, and any active lease/process before assigning work. Verify preservation and dated review manifests. Record unresolved findings with source IDs, including RD4's **partial supersession** by later report work. Adopt package statuses `not_started`, `in_progress`, `blocked`, `ready_for_review`, `accepted`, or `deferred`; use `deferred` only with reason/scope consequence. Claims about gate acceptance still require gate evidence.

Agree before edits on semantic identity fields, new batch IDs/consumption records, audit source validation API, task-specific telemetry inputs, and analysis row/input-manifest contracts. Version scientific changes. Reserve raw/release paths and define independent reviewers. Reconcile current top-level docs/state after every scope decision; the old S4 checklist does not prohibit agent-authored PDFs or authorize ignoring new defects.

Acceptance: one actionable assignment per worker, disjoint paths, documented interfaces, current date/cutoffs, known evidence availability, preserved original hashes. Do not claim the historical G0 acceptance clears newly discovered identity defects.

## SW01 — task identities, fresh qualification, and clear policy

Reproduce [RD1–3](reviews/2026-11-17/research-design.md). Remove split/base-ID salt from semantic identities and exclude incidental text changes as a substitute for new task semantics. Preserve paired variants under the same base identity. Expand low-entropy generators enough to support genuinely distinct development, consumed qualification, fresh qualification and main reservations, or explicitly document a defensible narrower template choice before freeze. Trivial TAB04 currently offers only two worlds; reseeding alone is insufficient.

Implement explicit qualification-batch allocation/consumption and immutable seed/semantic manifests. A new output folder or actor sampling seed does not make a new world. Prior qualification batches remain consumed. Keep all old runs and annotate the catalog-v2 run as a post-tuning repeat, without renaming/deleting its archive. Resolve “optional non-approved notes” versus approved-only policy while retaining ordinary discovery. Prove incomplete-world certificates, absence controls, and no-answer-leak properties still hold after changes.

Acceptance: differently named identical semantic tasks are rejected across splits; current dev/main collision is caught; materially new worlds pass; paired variants remain aligned; old/consumed batches cannot masquerade as fresh; batch replay is explicit regression mode; changed generators/policy have new versions. A CPU-only reservation manifest demonstrates disjointness before any GPU use.

## SW02 — native provenance, audit source verification, and telemetry

Reproduce [IMPL-1–3](reviews/2026-11-17/implementation.md). Bind standalone audit preparation to immutable native request/response evidence and validated extraction; merely recomputing self-hashes is insufficient. Reuse strong recovery verification without replaying inference or mutating evidence. Retain mock/native provenance distinctions. Use actual assignment/generator version and task-specific approved resources in episode/qualification metrics. Publish versioned derived corrections from original archives; never rewrite historical terminals or their manifests.

Acceptance: source-inconsistent T is rejected while valid records prepare successfully; original HTTP bytes remain unchanged; all five templates report correct generator versions and authorized-read sets; missing/corrupted native sources fail clearly; interrupted records remain accounted for; no new retries, remote endpoints or lease bypasses. Coordinate shared CLI/qualification changes through SW00.

After initial acceptance, this lane can implement the missing local semantic judge executor/qualification fixtures under a separate assignment. Record exact local checkpoint/runtime/rubric/coverage/cost. Qualify absence, denial, revision, insufficiency, long-trace and prompt-injection cases; retain uncertainty and independent-review probabilities. Existing audit plumbing is not a qualified judge. No judge success is assumed in the initial CPU handoff.

## SW03 — valid statistics, precision, and reproducible releases

Reproduce [A1–5](reviews/2026-11-17/analysis-evidence.md). Define one complete-block/base sensitivity estimand and implement identical inclusion/weighting in the point estimator and cluster bootstrap. Correct diagnostic block counts. Derive label-error bounds from actual contrast coefficients/weights and an explicit error budget, including the interaction range; do not claim a placeholder is conservative. Reject mixed policies/splits/versions by default and validate serialized inputs and matching schedule fields.

Retain/hash exact derived inputs, schedule, analysis configuration, source version and output artifacts so a clean checkout can reproduce a release. Distinguish statistical reproduction from native authenticity. Make fixture regeneration explicit rather than a side effect of read-only analysis commands. Define completion, response parsing and valid-A denominators separately; do not retroactively change old gate counts.

Before main freeze, simulate plausible paired baseline/effect/missingness patterns at the actual candidate scope and report interval widths, coverage/false-positive behavior and detection limitations. Implement justified zero-event bounds on a stated independent-base event, template sensitivity, and relevant semantic aggregation/sensitivity if semantics survive qualification. Twenty base clusters are not 320 independent observations. Do not inspect main effects to choose sample size or prompts.

Acceptance: heterogeneous-missingness example yields coherent point/interval outputs; allowed adversarial flips fall inside bounds; wrong-policy/version inputs reject; release inputs can be verified/replayed after original external paths are unavailable; expected behavior is recovered on stochastic rather than only deterministic toy simulations; weighting, missingness, zero-event and multiplicity outputs match the documented estimands. Semantic-only functionality may be explicitly deferred if final scope withdraws all dependent claims.

## SW04 — current evidence, related work, and report continuity

The S4 draft on `7c4aed7` already includes both qualification failures and a slide outline. Do not recreate those as if missing. Add the review's qualification-reuse caveat, distinguish still-unfixed versus repaired code, and avoid presenting the two runs as two independent held-out confirmations. Maintain a claim/evidence table keyed to tracked rows and hashes. Reconcile overstated “validated” descriptions with what was actually tested. Keep original study findings separate from extension results.

Verify key primary papers and close the related-work comparison: intervention, shortcut opportunity, acquisition versus causal use, T/J disclosure, actual monitorability, and judge limitations. No unsupported novelty/deception/internal-thought claim. Update prose as real qualification/main outcomes arrive; keep S4 fallback content ready throughout. No invented main effects or exploratory pilot effect estimates presented as confirmation.

Acceptance: every quantitative claim has an artifact source and denominator; consumed qualification is identified; draft scope/gates match current state; original-study numbers reproduce; references support their statements. SW04 can start early and must not block independent CPU repairs.

## SW05 — independent integrated CPU acceptance

A reviewer other than each fix author reruns the relevant defect reproduction and new regression tests against the integrated commit. Review canonical identity/batch manifests, raw-to-derived binding, statistics, and provenance as a connected pipeline. Run the full extension suite once for the integrated wave, original tests/preservation at this boundary, and verify review artifacts remain intact. Record source hashes, tests and unresolved limitations in dated handoffs.

Acceptance: no unresolved defect can invalidate planned qualification or main outputs. Gate definitions/denominators are prespecified. Documentation and actual CLI match. Existing main-refusal safeguards remain until SW07 introduces the properly guarded frozen path. A mock pass does not qualify the actor.

## SW06 — bounded development repair and fresh qualification

Only the designated GPU operator acquires the canonical lease; CPU workers keep progressing. Start with targeted **development** cases across the failing templates and visibility/length conditions, especially TAB02; a two-cell TAB01 probe is inadequate catalog evidence. Diagnose comprehension/tool-format/budget failures from preserved traces, version repairs, and verify them on development data. Record attempt/time budgets and actual daily availability; do not consume new qualification samples as a tuning loop.

Once credible, run a new content-disjoint qualification batch under predeclared gates: at least 95% completion and 99% conditional parseability with exact defined denominators, at least 80% easy no-shortcut legitimate success, and no systematic family/template tool defect; inspect uncertainty. Require actual long actor/audit cost, memory and context evidence. Qualify the local judge/independent review path if feasible; otherwise decide behavioral-only scope before freeze and withdraw the semantic question. Independent machine agreement is not semantic accuracy.

Acceptance: reviewer reconciles every assigned ID, sources and failures; confirms batch freshness and definitions were fixed before collection; integrator records G1 acceptance only with its underlying runtime/isolation/scorer/long-pilot evidence, and accepts or rejects G2 explicitly; full actor/audit/review forecast fits all cutoffs and reserves. Gate failure returns to development only while time remains and a new batch is available. At **Nov 22 18:00** without accepted qualification **and freeze**, enter S4. No user confirmation is needed to honor this fallback.

## SW07 — freeze and implement the guarded main execution path

Current native/mock runners reject main; this is intentional, not a configuration switch to bypass. Build the executable main path and regression-test it before collecting anything. It must require an accepted versioned freeze, exact source/config/checkpoint/template/policy/schedule hashes, disjoint main instances, planned denominator, paired/counterbalanced order, technical retry/recovery rules, analysis and semantic-scope decisions. Reject unsigned/provisional/mismatched inputs. Do not simply remove the main guard.

Acceptance: independent reviewer signs the checklist with actual evidence; committed `configs/frozen/<version>/` and exact source support a dry validated schedule; altered/unsigned manifests reject; interrupted and unattempted IDs remain recoverable without replacing attempted outcomes. Only then update G3 and permit SW08. Do not reinterpret existing draft tests as a permanent ban on legitimate future freeze; preserve their draft invariants and add separate frozen-path tests.

## SW08 — collection, audits and final analysis

Run only frozen assignments, with one GPU owner and durable progress. Keep the paired denominator intact. Verify closed batches without revealing main contrasts to prompt developers or changing parameters after outcomes. Run all eligible semantic audits or preserve explicit unresolved status only if that scope was qualified/frozen. Do not improvise a remote judge or silently skip inconvenient records.

Acceptance: all planned IDs accounted for; raw/input/version integrity verified; actor and audit failures retained; derived rows released; actual frozen contrasts/intervals/sensitivities generated and independently reconciled; semantic uncertainty and selection effects disclosed. At actor/inference cutoffs close the remaining assigned accounting honestly. An incomplete main run remains an incomplete main run in the report, even if the delivery narrative falls back to the original study and methods.

## SW09 — complete artifacts and independent delivery acceptance

Produce the final integrated course report/source/PDF, generated tables/figures, final slide deck, speaker notes, source bibliography, reproducible build commands/dependencies, and submission-ready delivery manifest. Choose a simple maintainable document/deck toolchain using available project dependencies; no missing template is a reason to leave this to the researcher. Do not modify the protected original report/build assets; adapt into new extension-owned files.

Use genuine S0 results if accepted, or explicitly selected S4 content. Include research limitations, qualification reuse, failures, AI assistance, missing official format assumptions, and whether semantic conclusions were withdrawn. From a clean checkout, reproduce reported numbers without hidden local paths; separately verify available raw archives or explicitly name what cannot be checked. Render and visually inspect every PDF/deck page for clipping, illegibility, correct figures and links.

Acceptance: a non-author reviewer verifies the exact final commit, hashes/counts, artifact existence/content, clean-checkout reproduction and visual inspection. Update WP12/WP13/G6 only when these outcomes exist. Leave only actual researcher logistics and course submission pending. Preserve the new experiment's unanswered status if S4; delivery completion is not scientific-success certification.

## Worker assignment brief

The orchestrator supplies: package ID; concrete objective and review finding IDs; exact input commit; assigned paths; dependencies/interface decisions; regression/acceptance examples above; output/handoff path; independent reviewer; whether CPU-only or designated GPU operator. Workers return: what changed and why; actual commands/results; source/artifact hashes; limitations; commit or uncommitted-file list; next dependency-ready action. Never claim a run/test/commit that has not occurred.
