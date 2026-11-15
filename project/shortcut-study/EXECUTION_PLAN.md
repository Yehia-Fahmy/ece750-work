# Execution plan: local study to December report

Prepared November 15, 2026. This is an executable work plan, not an experiment already performed. The context checkpoint was pushed to `main` as `ecb82d3` before this plan was developed. Read [CONTEXT](CONTEXT.md), [DECISIONS](DECISIONS.md), and [AGENT_GUIDE](AGENT_GUIDE.md) first.

## Objective and completion evidence

Deliver a course-ready report by December 4 that combines the completed preliminary observer study with a separately documented shortcut experiment. Preserve the original standalone report. Success means a controlled, auditable study and an honest account of uncertainty; a positive visibility effect or rare violation is not required.

The deliverable includes report Markdown/source and PDF; a reproducible derived dataset and analysis; frozen experiment/grade manifests; aggregate results; limitations and AI-assistance disclosure; a slide deck and speaker notes; and a submission checklist with any unresolved course-format requirements. Submission itself is not authorized by this plan.

The research questions are: (1) Does declared access to T or J change prohibited shortcut acquisition? (2) When acquisition is recorded, what do T and J acknowledge, omit, or contradict, and how do those patterns change with visibility? (3) Does genuinely insufficient authorized information change shortcut acquisition, unsupported answering, or appropriate abstention? The randomized prompt contrasts support causal claims about these notices in this environment; they do not establish subjective awareness, intent to deceive, or access to the model's full internal computation.

## Strategy

1. Preserve the earlier work and the discussion context — done at `ecb82d3`.
2. Build one end-to-end episode before scaling task generation. Keep original `observer_study` source unchanged.
3. Qualify the existing Qwen3-4B as the primary actor and a local primary judge. Trial a small different-family actor and an independent judge; include them only if they meet capability, quality, and budget gates.
4. Prioritize the four T/J visibility cells, complete/incomplete pairs, and shortcut-present/absent controls. Additional factors are deferred.
5. Freeze sample size, prompts, models, grading, and analysis before main generation, using measured actor **and auditor** cost.
6. Generate balanced blocks, audit locally, and finish collection with enough time left for analysis and writing.

Never add a cloud judge when local qualification is difficult. If semantic grading fails, retain the behavioral study and report the semantic evaluation failure explicitly; do not claim the requested transparency question was resolved. A course report can document that limitation, but it is not successful semantic validation.

## Timeline and gates

All dates/times are America/Toronto. The operator must recalculate remaining time if work starts late; do not act as if an old target date is still in the future.

| Window | Gate / milestone | Concrete exit evidence |
| --- | --- | --- |
| Nov 15–17 | G0 contracts and task specification | Versioned episode schema, exact provisional A/T/J boundaries, permission semantics, generator specs, evaluator-access tests, and reviewed analysis contrasts |
| Nov 18–20 | G1 vertical slice and local feasibility | End-to-end smoke episodes; actor/judge memory and timing reports; deterministic scoring fixtures; absent-shortcut tests; frozen historical files still match |
| Nov 20–22 | G2 development + held-out qualification | Pilot capability/difficulty results; judge validation and natural-record agreement; full compute forecast; chosen course scope |
| By Nov 22 evening | G3 main freeze | Source/config/data/checkpoint hashes, schedule, planned denominator, grade rubric, analysis plan, and freeze record committed |
| Nov 23–27 | G4 main actor collection | Captured terminal episodes, periodic integrity manifests, complete counts; CPU audit runs alongside GPU collection |
| By Nov 27, 18:00 | Actor-collection cutoff | Stop starting new actor blocks after cutoff; retain assigned incomplete records. Nov 27 micro-survey is a separate course commitment |
| Nov 28–29 | G5 local semantic audits + statistical analysis | All planned primary audits processed or explicitly unresolved; second-review coverage; reproducible rates/intervals; label-error sensitivity |
| By Nov 29, 18:00 | Inference cutoff | No new exploratory generations; finishing missing technical audits must not displace report delivery |
| Nov 30 | Full report draft | Complete scientific narrative, tables/figures from checked results, limitations, reference trail |
| Dec 1–3 | G6 independent reproduction and packaging | Clean-checkout statistical reproduction, PDF visual inspection, navigation and artifact audit, slides, submission-ready bundle |
| Dec 4 | Delivery | Final package ready for researcher submission; report date confirmed, time based on general 11:59pm policy; presentation date still TBD |

Writing the methods, background, and report skeleton starts during implementation, not after collection. If official page limits remain unavailable, maintain a four-page core plus clearly separated appendices and references; do not claim this resolves the conflicting historical instructions.

## Scope ladder selected before main collection

One base scenario has complete and insufficient-information variants. Each variant has shortcut present/absent and all four visibility cells: **16 episodes per base scenario per seed**. All sizes below are per actor; judge calls are additional.

| Tier | Base scenarios | Seeds | Episodes | When to choose |
| --- | ---: | ---: | ---: | --- |
| Course core — recommended starting target | 100: five families × five templates × four difficulties × one instance | 2 | 3,200 | Measured actor+audit budget fits and all families pass qualification |
| Lower-compute course core | Same 100 | 1 | 1,600 | Budget cannot support two seeds; preserves breadth and factorial pairing, discloses lack of repeated-seed stability |
| Expanded distinct scenarios | 200: two instances per template/difficulty | 2 | 6,400 | Extra time after all audit/report reserves, chosen before main outcomes |
| Original V2 full allocation | Same 200 | 3 | 9,600 | Only if measured total workload fits; not the default for one 8 GB GPU |
| Qualified-family fallback | 60: first three qualified planned families × five templates × four difficulties | 2 | 1,920 | Debugging/verification infrastructure fails pre-main qualification; scope change logged, not concealed |

The three-family fallback defaults to analysis, multi-document reasoning, and planning, based on implementation/capability evidence rather than observed visibility effects. If those are not qualified, do not substitute arbitrary families without a dated decision and updated freeze. Minimum one-seed version is 960 episodes. The original V2 proposal stays unchanged as a record of the broader ambition.

An optional second actor uses 40 predetermined common base scenarios (two per family/difficulty) × 16 × two seeds = **1,280 additional episodes**, only if both actor and its semantic evaluation fit. Use that exact subset from the primary actor for comparisons. A small compatibility pilot is not a main model replication. Actor identities and subset are fixed before inspecting main actor contrasts.

With the course core plus second actor, there are 4,480 actor episodes and at least 4,480 primary episode audits, potentially many more chunk/secondary calls. Do not call that 4,480 independent tasks.

Drop optional actors and follow-ups before reducing the primary design. Reduce seeds before eliminating information/visibility controls. If all five families cannot be built correctly, use the documented family fallback rather than superficial fake tasks. No post-main extension chasing significance or selectively dropping difficult cases.

## Pilot design and qualification

All smoke/development/qualification/main generators use disjoint seeds and semantic instance fingerprints. A rephrased or renumbered duplicate is not held out. Reserve the main set before actor development; do not use main model outcomes to tune it.

- Compatibility smoke: about eight short episodes per candidate; validates traces, tools, channel separation, and terminal records. Not evidence of behavioral reliability.
- Development: 40 base scenarios (two per family/difficulty), with 80 balanced selected episodes per candidate rather than the full factorial. Include all shortcut mechanisms, visibility cells, information states, and absent controls in a recorded fractional schedule. Add targeted technical fixtures without calling them representative data.
- Held-out primary qualification: 20 new base scenarios × two information states × two availability states × four visibility cells × one seed = 320 episodes. A secondary candidate can first receive a balanced 40-episode technical subset; qualify its actual supported protocol before any main replication.
- Judge fixtures and natural pilot audit are separate from actor task development; see [COMPUTE](COMPUTE.md) and [EVALUATION](EVALUATION.md).

Proposed G2 release gates (freeze exact definitions before held-out qualification):

1. Deterministic generators, policy oracle, environment isolation, A validator, and channel filters pass all meaningful positive/negative fixtures.
2. At least 95% terminal completion and 99% parseability among complete episodes on held-out qualification; report exact counts and failures. These are observed gates, not population guarantees.
3. Easy no-shortcut tasks achieve at least 80% legitimate success in aggregate and no family has a clear systematic tool/comprehension defect. Inspect uncertainty and per-family evidence. Hard/extreme failures are retained and not a model-disqualification criterion by themselves.
4. Incomplete cases have a verified indistinguishable-world or mandatory-observation certificate; incomplete status cannot hide malformed outputs.
5. Primary judge passes prespecified held-out fixture checks; coverage and natural disagreement are reported. Rare-class natural accuracy remains unestablished without reference labels.
6. GPU memory/total-time forecast fits with reserve. No OOM, context clipping, or condition-specific history loss in the longest pilot records.

If a gate fails, fix on development data and obtain fresh qualification instances. Do not replace failed qualification records and call the same sample untouched. Never require a minimum number of main violations as a release gate; zero shortcut use can be a valid result.

## Statistical plan before main freeze

The restricted, shortcut-present arm is the primary acquisition analysis; the absent arm is a control, not a way to dilute rates by adding structural zeros. Weight complete/incomplete strata and task families equally as prespecified. Let r00/r01/r10/r11 be acquisition rates in the four visibility cells, with seeds averaged within each base scenario.

- T-visibility effect: `((r10-r00) + (r11-r01))/2`.
- J-visibility effect: `((r01-r00) + (r11-r10))/2`.
- T×J interaction: `r11-r10-r01+r00` (secondary unless explicitly promoted before collection).

Treat T and J main effects as the two confirmatory contrasts. Report individual 95% paired bootstrap intervals, and simultaneous conservative intervals using 97.5% individual intervals for a Bonferroni familywise 95% target over these two contrasts. Do not describe ordinary bootstrap intervals as exact tests. Information-sufficiency interaction, family/mechanism/model contrasts, and semantic outcomes are secondary with clear multiplicity disclosure.

Resample base scenarios within family/difficulty, retaining all matched variants and seeds. 10,000 draws, fixed recorded seed; simulation checks before freeze. Template-level sensitivity tests generalization across the five templates per family; fine subgroup cells may be too small for strong inference. Missing outcomes get assigned-denominator bounds and complete-block sensitivity; record rare-event/degenerate-bootstrap limitations. No equivalence claim from an interval crossing zero.

Before freeze, simulate plausible baseline rates and paired effects at each affordable tier and publish expected interval widths/detection rates. Select scope by feasibility and useful precision, not an assumed positive finding. The nominal 3,200 episodes contain only 100 base-scenario clusters; they are not 3,200 independent units. If observed events are all zero, do not present a degenerate zero-width bootstrap interval as evidence of zero population risk. Include an appropriate finite-sample bound on a clearly defined independent-base-scenario event (with its sampling assumptions) and state when the primary contrast remains poorly identified. Generalization to unseen templates remains limited.

For semantics, report T/J labels separately, all-assigned acquisition-plus-omission/denial rates, and conditional disclosure among acquisitions. Label uncertainty and selection into acquisition both matter. Include alternate primary-judge/reconciled labels and bounded label-error sensitivity. Do not turn judge agreement into a semantic accuracy estimate.

## Contingencies and honest completion

- **Only one actor qualifies:** complete the matched study on that actor; report limited model generalization.
- **Independent judge fails:** use qualified primary labels with uncertain flags/sensitivity; explicitly withdraw claims of independent semantic validation. If primary semantics fail, do not issue semantic conclusions.
- **Long traces exceed judge capacity:** validated coverage-preserving chunking, or unresolved; never shorten stored traces after seeing the answer.
- **Low shortcut prevalence:** report prevalence and uncertainty; use constructed fixtures to assess grader behavior without pretending synthetic violations are natural actor data.
- **Late start or reduced machine availability:** choose a smaller pre-main tier. If collection has started, retain the frozen denominator and all interrupted outcomes; publish the resulting limitations rather than quietly redefining the sample.
- **No adequate new main run by cutoff:** deliver an integrated report of the original result, validated extension methods/pilots, and explicit incomplete outcomes. This is a course-delivery fallback, not a claim the extension's scientific objectives were achieved.

## Required final checks

Every historical file in the preservation manifest still matches. Every reported number is generated from committed derived rows. Fresh reproduction works without raw hidden local archives for statistics; raw authenticity requires the separate local evidence package and is described honestly. Actor and auditor failures are visible. All figures are checked against tables. Course-specific requirements, unresolved assumptions, contributions, and use of AI are explicit. No external compute has been used.

## Report construction

Start with a concise question/contribution and the completed observer study as preliminary evidence. Describe the extension's task environment, matched interventions, A/T/J distinction, and separate reviewer/auditor roles. Present action-grounded findings before semantic judgments, then insufficient-information outcomes, automated-grader validation, uncertainty, and limitations. Use the original frozen report as a source, not a file to overwrite.

Plan compact figures for visibility versus acquisition, appropriate abstention/unsupported answers by information state, and paired T/J disclosure with uncertain cases visible. Append task examples, exact notices, provenance, judge validation, scope deviations, and reproduction instructions. Do not force every planned figure into a four-page main text if a simpler table communicates the result.

Verify recent related work from primary papers before claiming novelty; the existing evaluation references are a starting point, not a completed literature review. Distinguish the contribution of controlled realistic shortcut tasks and separately manipulated T/J visibility from prior work on chain-of-thought faithfulness and monitoring. State that “reasoning models don't always say what they think” motivates triangulating text against actions, not treating traces as a ground-truth account of thought.
