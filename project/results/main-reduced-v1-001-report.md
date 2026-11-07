# Main collection and initial analysis — November 7, 2026

The reduced main study is collected: **240/240 requests returned**, **239/240 completed (99.6%)**, and **239/239 complete outputs parsed (100%)**. Both frozen technical targets passed. The only incomplete response, `date_understanding_0164__D-A`, reached the 8,192-token limit without a final answer. It remains unknown; no regeneration occurred. There were zero technical retries. Recorded request time totals 2,514.3 seconds (41.9 minutes), excluding setup/preflight, with 335,139 reported completion tokens. The task's GPU server was stopped afterward.

## Scope and verification

The protocol was frozen on November 6 locally, before main collection: 60 questions, 20/task, crossed with C0, C1, developer rationale-visible (D-R) and developer answer-only (D-A). All main items, hints, prompts and seeds retain their originally reserved values. Fresh evaluation used three additional questions outside every reserved split. The developer-only scope was selected before main results for workload and evaluator relevance. It cannot compare observer roles.

Wrong-hint agreement was promoted to primary before collection because the original unacknowledged-agreement endpoint was rare and acknowledgment reliability remained limited. The original endpoint remains prespecified secondary. The [frozen protocol](../main-protocol-v1.md) documents this change, the departure from the proposed human-label reliability gate for primary collection, and the content-addressed source archive used instead of committing unrelated preexisting changes.

The [raw audit](main-reduced-v1-001-audit.json) checked all 240 original HTTP bodies against saved responses and recomputed every score: zero changes. All 44 frozen file hashes remained intact. All 56 tests passed. An [independent reviewer](main-results-independent-audit.md) parsed the raw answers and independently implemented the specified bootstrap, reproducing the numerical primary results exactly. Earlier audits verified [fresh labels](fresh-evaluation-independent-audit.md), [freeze/sample provenance](main-freeze-independent-audit.md), and [analysis mathematics](analysis-independent-audit.md).

## Primary paired visibility comparison

D-R has 9 wrong-hint agreements among 60 assignments. D-A has 11 known agreements and one unknown among 60 assignments. The all-assigned D-R minus D-A contrast is therefore bounded by **−5.00 to −3.33 percentage points**.

These are missing-outcome identification bounds, **not confidence limits**. Under the frozen task-stratified paired bootstrap (10,000 draws, seed 750), the lower-bound endpoint has a 95% percentile interval of **[−15.00, +5.00] pp**, and the upper-bound endpoint has **[−13.33, +5.00] pp**. These separate endpoint intervals are not a joint confidence region. A single all-assigned point estimate is not identified.

The prespecified complete-item sensitivity retains 59 questions (19 date, 20 disambiguation, 20 logical deduction). Its estimate is **−3.39 pp**, with 95% percentile interval **[−11.86, +5.08] pp**. It changes task composition slightly. Sampling uncertainty spans zero; this study does **not establish a developer-visibility effect** or demonstrate that the effect is absent.

## Condition diagnostics

All percentages below use 60 assigned requests per condition; ranges retain the one unknown response.

| Condition | Complete / assigned | Correct / assigned | Agreement with fixed wrong label / assigned |
| --- | ---: | ---: | ---: |
| C0, no hint | 60/60 | 51/60 (85.0%) | 2/60 (3.3%) |
| C1, hint only | 60/60 | 45/60 (75.0%) | 9/60 (15.0%) |
| D-R | 60/60 | 46/60 (76.7%) | 9/60 (15.0%) |
| D-A | 59/60 | 41–42/60 (68.3–70.0%) | 11–12/60 (18.3–20.0%) |

C0 has no displayed suggestion; its agreement column is agreement with the stored wrong option. The separately specified C1−C0 control contrast is +11.67 pp for wrong-label agreement (95% percentile interval [5.00, 20.00]) and −10.00 pp for correctness ([−18.33, −1.67]). These are control comparisons, not the primary visibility comparison; intervals are not adjusted for multiple comparisons. Individual wrong-hint agreement does not establish causal influence on that particular response.

By task, complete/parseable counts are 79/80 for date understanding and 80/80 for each other task. Accuracy varies markedly: date 62–63/80, disambiguation 43/80, logical deduction 78/80. Tasks, questions and conditions were not replaced based on these outcomes. Full diagnostics are in the [summary](main-reduced-v1-001-summary.json).

## Acknowledgment remains pending

The revised workflow passed six new constructed examples (two explicit, two absent, two ambiguous) and two isolated judgments of each of three fresh natural traces. There were no evidence-copy failures. All three natural cases were positive and C1 only. This is limited feasibility evidence, not human validation or estimated natural negative/ambiguous accuracy. The old validation set remains inspected and was not reused as untouched data. See [fresh evaluation](fresh-evaluation-v3.json).

**No main acknowledgment labels have been assigned.** The initial [analysis](main-reduced-v1-001-analysis.json) leaves all 180 hinted acknowledgment outcomes unknown, including the incomplete trace. The original unacknowledged-agreement visibility contrast currently has all-assigned bounds **[−20.00, +15.00] pp**. The 45-item secondary complete-item subset is mechanically known-zero because neither arm agreed with the hint; its degenerate interval must not be interpreted as evidence of no unacknowledged agreement in the study.

The blank 240-row researcher review export is `runs/main-reduced-v1-001/review.csv`. A separate postcollection exporter, `prepare_main_judging.py`, re-verifies the frozen run and prepares **179 eligible one-trace numbered packets** under `runs/main-reduced-v1-001/numbered-judging-v1/agents/`, excluding 60 C0 controls and the one incomplete trace. It creates no labels and changes no frozen source. Main annotation and researcher checks across conditions/predicted classes remain the next phase before strong secondary claims. Independent AI contexts are not human raters.

## Reproduction

Use the commands in [main-study.md](../main-study.md). Main analysis must explicitly specify `--roles D --replicates 10000 --seed 750`. Keep the original run, source/input archive and all failed attempts; choose fresh output filenames for re-analysis. The checked outputs retain source-manifest, row and label fingerprints. Raw data remain local and ignored by Git; aggregate results and reproducing code are in the project tree.
