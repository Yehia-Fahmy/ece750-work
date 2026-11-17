# Analysis and evidence review — 2026-11-17

Reviewed repository baseline: `3c155ba`. Owner: delegated analysis/evidence reviewer. Scope: WP07 statistics, qualification denominators, archived evidence integrity and reproducibility. Read AGENTS, README, DECISIONS, AGENT_GUIDE, EXECUTION_PLAN, WORK_PACKAGES, state, analysis protocol, and relevant WP07/G1/G2 handoffs. No GPU work, inference, source fixes, existing-result changes, or historical-file edits. The root reviewer owns full-suite and historical-preservation checks; the research reviewer owns split leakage and repeated qualification instances.

**Assessment:** the retained qualification counts and hash chains checked here reconcile, and failed qualification is disclosed honestly. The analysis package remains a scaffold with confirmed statistical defects and unimplemented acceptance requirements. It should not yet be accepted as ready for main inference. No final extension result exists to invalidate; the defects below need correction before WP07 acceptance/G3 freeze.

## Confirmed findings

### A1 — P2: complete-block estimate and its interval use different observations

Evidence: `src/shortcut_study/analysis/aggregate.py:157–165` filters individual information-state × seed blocks; `analysis/compare.py:58–68` first averages all blocks for each base and marks the entire base unidentified when any constituent block is unidentified; `analysis/compare.py:119–126` then drops that entire base from complete-only bootstrap. Both outputs are presented together at `analysis/compare.py:196–209` as complete-block sensitivity.

Reproduction: two bases, complete/incomplete variants, four visibility cells each; base A has T effect 1 with one unknown in its incomplete-information block, and base B has T effect 0 with both blocks observed. The displayed complete-block point is **1/3**, but `bootstrap_complete_block.point` is **0** and its 95% interval is **[0, 0]**. Those are different estimands. Equal information-state weighting is also not maintained after uneven block deletion: the observed block mean is 1/3, whereas averaging the complete and incomplete strata separately gives 1/4. Missingness is a realistic concern: latest qualification has 81 non-completed assignments.

Action: define the sensitivity estimand explicitly and make point estimation and bootstrap apply the same inclusion and weighting rule, retaining dependence within base. Add a heterogeneous missingness regression; the existing missingness test only checks that all-assigned bounds widen. Also fix `aggregate.py:175–186`: `blocks_used` counts difficulty strata, not matched blocks (repro reports 1 despite 4 structurally complete blocks).

### A2 — P2: label-error sensitivity is not a conservative bound

Evidence: `src/shortcut_study/analysis/semantic.py:56–81`, especially `:74–76`, describes a conservative ±`flip_rate` envelope for a contrast. In a balanced four-cell design T and J contrast shifts can be twice the fraction of all labels flipped; an interaction can move four times that fraction. The interaction's range is [-2, 2], but this helper clamps every input to [-1, 1].

Reproduction: 40 initially false outcomes, ten per cell. Flipping four V00 labels changes T from 0 to **-0.2**, while the helper's 10% envelope is **[-0.1, 0.1]**. Thus the asserted bound excludes an allowed perturbation. The helper is explicitly a placeholder and is **not called by the current analysis harness**; this is a confirmed implementation defect with no measured semantic conclusion affected.

Action: define whether the error budget is global, per cell, per stratum, or weighted, then derive sharp coefficient-aware bounds over actual labels/weights; use the correct estimand range. Verify adversarial error allocation, including interaction and unequal weights, before using the helper in reports.

### A3 — P2: analysis releases lack the input provenance they advertise

Evidence: `src/shortcut_study/analysis/io.py:123` promises input/output hashes. Its manifest at `:132–145` stores only the caller's input metadata and output report hash. `analysis/harness.py:118–124` passes paths, assignment count, repetitions and seed, without hashes of the schedule, scored rows, source or protocol. Archive loading (`analysis/io.py:30–61`) does not verify a supplied run manifest; final release inputs are not copied into the release.

Consequence: a later reader cannot prove which contents at the named paths generated a report, or reproduce it after those external paths disappear. This is weaker than the qualification runner's archived source/config/artifact hashes and the execution plan's clean-checkout requirement (`EXECUTION_PLAN.md:111`). No release is represented as frozen main evidence, so this is a pre-release blocker rather than evidence of fabricated results.

Action: hash and retain/version the exact schedule and derived scored/audit rows used, attach source/config/protocol identities, and validate raw-manifest linkage when claiming archived provenance. Keep raw authenticity separately documented from statistical reproducibility.

## Conditional risks and gate-definition clarifications

### A4 — P2 before supporting mixed-policy inputs: restricted-only primary analysis does not filter policy

Evidence: `src/shortcut_study/analysis/metrics.py:28–37` calls its output the restricted shortcut-present arm but checks only availability and `acquisition_endpoint`. It never checks `policy_id`. Schedule joining at `analysis/io.py:92–108` does not validate schedule/scorer agreement on policy or split either. The generic JSON-list loader does not schema-validate its rows (`analysis/io.py:34–42`).

Reproduction: a restricted T-only bundle plus a broad-permission J-only bundle produces T=0.5 and J=0.5; the restricted-only T estimand is 1. This risk is **not active in current S0**, whose generator only emits the restricted policy. It matters if the generic archive interface receives mixed policies/versions or a future broad-permission follow-up.

Action: reject incompatible policy/split/scorer versions by default, or require explicit separate analyses. Validate serialized rows and field consistency; avoid trusting optional flattened aliases over their scored source fields.

### A5 — parseability is reported on a selected denominator

Evidence: `results/qualification/g2-held-out-20261116-catalog-v2.json:60–76` labels the gate “99% parseability among complete held-out episodes” but reports `parseability_among_complete_completed`, excluding complete-information assignments that did not complete. Source archives reproduce **111/111** for that selected subset, versus **111/160 = 69.375%** valid answer artifacts across all assigned complete-information episodes. Prior run is **108/108** selected, versus **108/160 = 67.5%** assigned.

The denominator is named explicitly in the evidence, and overall G2 already FAILs. This is therefore a gate-definition/reporting clarification, not a hidden successful qualification. Parsing a completed artifact measures a different thing from producing a valid artifact on assignment; the 99% criterion is weak if “completed” already requires valid parsing.

Action: freeze separate denominators for transport/native-response parsing, parseable submitted A, and terminal completion; show assigned-denominator valid-output rate as well as the conditional rate. Do not retroactively redefine the recorded failures.

## Evidence reconciliation and strengths

Read-only checks covered four retained local archives. All **54,420 manifest-listed artifacts** matched their expected SHA-256 digests, as did all **20 tracked top-level hash anchors** checked against the four tracked evidence JSONs. Every assigned ID in these schedules has a scored row. Hash agreement shows internal consistency of retained evidence; it is not independent proof of the physical inference provenance or semantic truth.

| Archive | Assigned | Completed | Format failure | Budget limit | Easy authorized success |
| --- | ---: | ---: | ---: | ---: | ---: |
| `g2-held-out-20261116` | 320 | 238 | 28 | 54 | 11/20 |
| `g2-held-out-20261116-catalog-v2` | 320 | 239 | 27 | 54 | 11/20 |
| `g1-long-pilots-20261116` | 10 | 9 | 1 | 0 | Not an easy-task run |
| `native-qualification-tab01-v6-16cell` | 16 | 16 | 0 | 0 | Not an easy-task run |

Manifest entry counts, in the same order: 25,384; 26,471; 984; 1,581. Both held-out runs retain unsuccessful outcomes in the 320-assignment completion denominator and easy failures in the 20-assignment easy denominator. The 16-cell development pass has not been substituted for the failed broader qualification.

The primary T/J/interaction algebra and unknown-outcome endpoint bounds are correct for balanced, eligible, complete matched schedules. Absent controls are excluded, bootstrap draws retain base-scenario dependence, Bonferroni interval levels are labeled, and zero-event warnings explicitly prohibit zero-population-risk claims. Synthetic fixture provenance and unfrozen status are clearly distinguished from model findings. The archive loader rejects absent/extra IDs and duplicate IDs rather than silently shrinking the schedule.

Raw evidence is present on this machine, so these counts were actually recomputed. The raw runs remain ignored local artifacts; a Git checkout alone does not contain these scored episode rows. A future reproducibility package should include committed/released derived rows and a separate available raw-evidence package, as the plan already requires.

## Acknowledged unfinished acceptance work

These are gaps, not evidence that completed results were misrepresented:

- The synthetic “simulations” use deterministic T-only/J-only/alternating/all-zero cell patterns (`analysis/simulate.py:22–43`). They test algebra, not confidence-interval coverage, false-positive behavior, power or useful precision at S0's **20 base clusters / five templates**. The execution plan specifically requires plausible baseline/effect simulations and expected interval widths/detection rates before freeze (`EXECUTION_PLAN.md:94–96`). No such outputs were found.
- Zero-event handling emits warnings but no independent-base finite-sample upper bound. Template sensitivity is absent. Both are required in the plan at `:94–96`.
- Semantic helper functions are not wired to archived audit rows or the CLI. There is no implemented primary-versus-reconciled analysis, acquisition-conditioned disclosure analysis, or validated bounded-error analysis, despite draft commitments at `EXECUTION_PLAN.md:98` and `ANALYSIS_PROTOCOL.md:31`.
- G2 capability remains failed; primary judge qualification and full actor-plus-audit forecast remain open; G3 is not frozen. The long pilot's ten V00 complete/absent actor tasks do not establish long-audit feasibility or a complete pipeline budget. These omissions are already disclosed by the current state and handoffs.
- The `run_dry` default rewrites tracked simulation fixtures (`analysis/harness.py:38–39`) even if output is under `/tmp`. Review probes below intentionally avoid it. Future read-only reproduction should make fixture regeneration explicit and preserve released inputs.

## Commands and durable evidence

Run from `/home/yehia/ece750-work`:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-repro.py
python3 project/shortcut-study/reviews/2026-11-17/analysis-evidence-archives.py
```

Both commands completed with exit status 0. Exact observed outputs are retained in `analysis-evidence-repro.json` and `analysis-evidence-archives.json` beside this report. The scripts perform CPU-only inspection/probes; they write only stdout. No full-suite rerun was performed by this reviewer, avoiding duplication of the root review. No source defect was repaired during this review.
