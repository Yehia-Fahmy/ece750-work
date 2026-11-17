# Research and implementation review — November 17, 2026

**Verdict: the original observer study reproduces well; the shortcut-study extension is substantial but unfinished and not ready for main collection.** There are confirmed defects beyond the already documented failed capability gates. The evidence reviewed does not support calling the combined research/implementation finished.

Reviewed commit: `3c155baf4af8a2c6bbed8da769f533ecc3847413`. Four reviewers worked in parallel: integration/original-study verification, research design, implementation, and analysis/evidence. All followed the extension's agent guidelines. This review changes only files in this new review directory; it does not repair code, amend protocols, accept gates, rewrite results, or generate model responses.

## What is trustworthy

- **Original study:** 58 tests pass. All 240 original assignments/raw responses check out; 239 completed finals independently parse; 179 judgments remerge; 44 frozen files verify. Both original analyses reproduce, and the newly generated complete evaluation equals the committed evaluation exactly. Its inconclusive visibility finding and exploratory semantic labels are appropriately qualified. See [original-study verification](original-study.md).
- **Preservation:** all 111 protected historical files and the separate design snapshot match their recorded SHA-256 hashes.
- **Extension evidence:** 213 tests pass. All 54,420 manifest-listed artifact hashes and 20 tracked hash anchors checked across four archives match. Counts reproduce: first qualification 238/320 completed; second 239/320; easy legitimate success 11/20 in both; long pilots 9/10; narrow v6 development slice 16/16. Failed outcomes were retained. These checks establish archive consistency, not independent semantic accuracy or physical GPU provenance.
- **Design strengths:** matched visibility conditions; actual removal of absent shortcuts; explicit insufficient-information certificates; separate trace/justification channels; action-grounded acquisition scoring; retained failure denominators; clear prohibition on treating generated reasoning as direct access to internal thought. The main runner still refuses unfrozen main assignments.

The latest qualification's **74.69% completion and 55% easy success** fail the documented 95%/80% requirements. A passing 16-cell development slice cannot replace that broader evidence. G0's limited catalog acceptance is not main-study acceptance.

## Prioritized confirmed findings

P1 means repair before accepting fresh qualification/main reservations. P2 means a substantive defect or reporting gap that must be resolved before relying on the affected output; it does not imply existing main results are invalid, because none exist for the extension.

| Priority | Finding | Evidence and consequence |
| --- | --- | --- |
| **P1** | **An actual development/main duplicate passes split validation.** | The trivial TAB04 development and reserved-main tasks have identical public content and hidden worlds. Non-development fingerprints incorporate the split-specific base ID, hiding the collision. The trivial generator has only two underlying resolution-time possibilities, so merely changing random seeds cannot guarantee three distinct split instances. [RD1](research-design.md#rd1--p1-confirmed-semantic-split-validation-conceals-an-actual-developmentmain-duplicate) |
| **P1** | **The second qualification was not fresh after tuning.** | All 320 hidden worlds and resource sets were reused; 256 prompts changed after the first failure. This is useful regression evidence but violates the plan's fresh-instance requirement. Both failures remain preserved and honestly labeled FAIL. [RD2](research-design.md#rd2--p1-confirmed-the-second-held-out-qualification-reused-all-previously-inspected-worlds) |
| **P2** | **A sensitivity estimate and its confidence interval use different subsets.** | A small missingness example produces a complete-block effect of **1/3**, while its associated bootstrap point and 95% interval are **0 and [0,0]**. One path drops individual information-state blocks; the other drops entire bases. [A1](analysis-evidence.md#a1--p2-complete-block-estimate-and-its-interval-use-different-observations) |
| **P2** | **Standalone audit preparation does not verify trace text against native responses.** | A deliberately altered temporary copy of terminal T is accepted into a judge packet even though native response bytes disagree. Native recovery correctly rejects the same copy, but standalone preparation bypasses that check. This is a reproduced validation defect, **not a finding that authentic archives were altered**. [IMPL-1](implementation.md#impl-1--p2-standalone-audit-preparation-does-not-bind-terminal-t-to-native-source-bytes) |
| **P2** | **Catalog provenance and read telemetry are wrong in existing records.** | 304/320 latest terminal records use the TAB01 generator version instead of the schedule's catalog version. Approved-read telemetry disagrees with task-specific resource lists in 208/320 records because it recognizes only TAB01 resources. Preserved schedules/source manifests and ledgers allow versioned derived corrections without new inference. [IMPL-2/3](implementation.md) |
| **P2** | **Analysis releases lack exact input provenance.** | Their manifests record input paths and output hashes, but not hashes or retained copies of the actual schedule/scored data and source/protocol used. This does not satisfy the planned reproducible final release. [A3](analysis-evidence.md#a3--p2-analysis-releases-lack-the-input-provenance-they-advertise) |
| **P2** | **The label-error sensitivity helper is not conservative.** | Flipping 10% of balanced outcomes permits a T effect of −0.2 outside its claimed [−0.1,+0.1] envelope. It also uses the wrong range for interactions. This helper is currently unused by the main analysis harness; no measured semantic conclusion is affected. [A2](analysis-evidence.md#a2--p2-label-error-sensitivity-is-not-a-conservative-bound) |
| **P2** | **Policy wording and the report draft need reconciliation.** | Calling non-approved notes “optional” weakens the intended prohibition; its behavioral impact is unmeasured. The report draft emphasizes the development pass and omits both later qualification failures, although the top-level README/state record them. The draft is explicitly unfinished, so this is stale reporting rather than a false final result. [RD3/4](research-design.md) |

The integration reviewer reran all three focused defect reproduction scripts and obtained the same outputs (excluding temporary-directory names). These findings are not inferred solely from agent summaries or test coverage.

## Unfinished scientific work and claim limits

These are accepted-plan gaps, distinct from the defects above:

1. **Actor qualification has failed.** A new run needs development repairs and genuinely new, content-disjoint qualification instances. Repeating the same cases until they pass cannot establish held-out readiness.
2. **Semantic evaluation is not qualified.** Audit preparation exists, but a local judge, held-out rubric validation, natural-record agreement, long-trace/chunk validation, and complete actor-plus-audit compute forecast remain missing. A behavioral-only fallback must explicitly withdraw semantic conclusions. Automated agreement would still not establish semantic ground truth.
3. **Analysis is scaffolding.** Deterministic injected effects check algebra; they do not measure interval coverage, false positives, or useful precision at S0's 20 base scenarios. Prescribed precision simulations, template sensitivity, a justified finite-sample zero-event bound, and integration with real semantic audit rows remain absent.
4. **No main freeze or main results exist.** There is no accepted G3 protocol/schedule or WP09–WP11 main collection/audit/analysis. Main execution still requires implementation and gate integration. The extension report is a methods/pilot draft; its final PDF, slides, and delivery/reproduction package are not complete.
5. **Related work is relevant but incomplete.** The research reviewer verified the central primary sources. A novelty comparison with tool shortcut/reward-hacking work and literature distinguishing trace faithfulness from monitorability is still needed. The defensible claim is about **declared reviewer access and recorded acquisition/disclosure in this environment**, not subjective awareness, deception, causal reliance on a note, or actual monitor effectiveness. See the [source-by-source assessment](research-design.md#literature-grounding).

S0 means one actor, five table templates, one shortcut mechanism, one seed, and **20 base clusters**, not 320 independent tasks. Structural difficulty labels are not calibrated difficulty measurements. Explicit missing-field instructions also make the abstention task narrower than general discovery of insufficiency.

Two additional conditional issues should be handled before expanding scope: the generic analysis selector silently pools broad-permission rows into its supposedly restricted-only endpoint, and conditional parseability must not be confused with producing valid outputs over all assignments. Current S0 only generates restricted-policy rows; neither issue changes the current FAIL verdict. Details are in [analysis/evidence review](analysis-evidence.md).

## Recommended repair sequence and acceptance evidence

| Order | Work | Concrete acceptance evidence |
| --- | --- | --- |
| 1 | Repair semantic identities and task pools; resolve common policy wording. Preserve consumed qualification batches as regression evidence. | Identical task semantics with different IDs are rejected; development/qualification/main reservations are demonstrably content-disjoint; low-entropy templates have enough distinct worlds; policy wording has one clear interpretation. |
| 2 | Repair the reproduced CPU defects before another large model run. | The missingness example has a consistent point/interval estimand; source-inconsistent audit T is rejected; all five templates report correct versions/reads; analysis releases retain exact input identities; error bounds contain adversarial allowed flips. |
| 3 | Decide feasible scientific scope using development evidence, then qualify on one fresh batch. | Prespecified gates, fresh batch manifest, complete failure accounting, actual actor capability evidence, and either qualified semantics plus full cost forecast or an explicit narrower behavioral-only scope. |
| 4 | Complete precision checks and freeze the exact feasible protocol before main collection. | Accepted G1/G2 decisions, accepted analysis package, pinned model/settings/scorers, content-disjoint main reservation, counterbalanced schedule, fixed denominators, missingness/zero-event policy, and versioned G3 artifacts. |
| 5 | Update the report concurrently and prepare the fallback. | Both failed qualifications and long pilots appear in the evidence table; fresh versus reused data are distinguished; claims match actual results; reproducible derived rows, PDF/slides and delivery checks are completed. |

There are 17 calendar days from this review date to the repository's December 4 report deadline. Its existing S4 fallback—original results plus extension methods/pilots with no new main factorial claim—is scientifically preferable to bypassing failed gates. This review does not select S4 or authorize new experimental collection; it identifies the decision and evidence needed.

## Review artifacts and reproducibility

- [Original study verification](original-study.md)
- [Research design, literature and split evidence](research-design.md)
- [Implementation and audit provenance](implementation.md)
- [Statistics, qualification evidence and remaining analysis work](analysis-evidence.md)
- [Verification record](verification.json), [review state](state.json), and [artifact hashes](manifest.json)

Focused CPU reproductions, from the repository root:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/research-design-reproduce.py
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/implementation-reproduce.py
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-repro.py
python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-archives.py
```

The adjacent JSON files preserve observed outputs. Raw-archive checks require the ignored local `project/runs/` evidence; it was available during this review. The audit mutation reproducer changes only a fresh temporary copy. No GPU or external inference was used, and no live GPU requalification was attempted. This is a substantive, scoped review, not a proof that every remaining path is defect-free.
