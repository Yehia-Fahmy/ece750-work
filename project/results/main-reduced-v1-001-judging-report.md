# Main acknowledgment judging — November 7, 2026

The single-pass workflow returned **179/179 eligible judgments**: **177 yes**, **2 no**, and **0 uncertain**. There were 0 evidence-check failures and 0 missing eligible records. The 60 no-hint controls were not applicable; the one incomplete hinted response remains unresolved. Automated judgments are not human validation.

Each complete hinted trace received one fresh independent `gpt-6-luna` context at low reasoning effort, with at most three workers concurrently. Workers received only the fixed guide and one blinded packet, with no condition metadata, final answers, correctness, baseline predictions, or earlier judgments. All 179 packet identities and selected passages were validated against the original inputs. No worker tool calls were observed. The first worker used the default CLI tool configuration; subsequent workers also disabled apps, plugins, shell and skill-search features. The rubric was identical throughout. The initial six-million-token cap admitted 151 workers; a separately recorded continuation finished the 28 unstarted packets under a combined 7.5-million-token cap. No packet received a second judgment. Raw prompts, responses, runtime events, launch plan and ledger are preserved under `runs/main-reduced-v1-001/numbered-judging-v1/execution/`; merged trace-level labels are in `agents-merged-v1/`.

The phrase baseline agrees on **174/179** definite labels. Among all 180 hinted assignments, 1 remains unresolved (0.56%), including the excluded incomplete trace. Agreement and exact evidence do not establish semantic accuracy.

| Condition | Assigned | Yes | No | Uncertain | Not applicable |
| --- | ---: | ---: | ---: | ---: | ---: |
| C0 | 60 | 0 | 0 | 0 | 60 |
| C1 | 60 | 60 | 0 | 0 | 0 |
| D-A | 60 | 58 | 1 | 1 | 0 |
| D-R | 60 | 59 | 1 | 0 | 0 |

The separate [labeled analysis](main-reduced-v1-001-labeled-analysis.json) retains the frozen developer contrast, 10,000 task-stratified paired bootstrap draws, and seed 750. The primary wrong-hint-agreement results and correctness/control comparisons exactly match the initial analysis. Conditional on accepted automated labels, the secondary unacknowledged-agreement D-R minus D-A contrast has all-assigned bounds **-1.67 to 0.00 percentage points**. These are identification bounds, not confidence limits; endpoint intervals and complete-item sensitivity are retained in the analysis. They do not account for semantic labeling error.

The read-only audit again verified all 240 raw responses, unchanged scores, and all 44 frozen files. All 56 workflow tests passed. The researcher review CSV and initial reports were preserved. Reported judging usage was 6,595,121 input tokens (1,661,184 reported cached) and 43,023 output tokens; billing cost, exact model snapshot and sampling parameters were unavailable.

See the [aggregate judging results](main-reduced-v1-001-acknowledgment.json) for fingerprints, baseline counts, uncertainty, condition counts, and provenance. Human validation across conditions and predicted classes remains outstanding before strong secondary claims.
