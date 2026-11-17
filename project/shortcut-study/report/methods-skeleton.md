# Shortcut acquisition under declared reviewer visibility
## Course report draft (S4 honest fallback) — ECE 750T extension

Yehia Fahmy · ECE 750T, University of Waterloo · draft advanced **2026-11-17** (S4 declared after G2 held-out FAIL twice: [#23](https://github.com/Yehia-Fahmy/ece750-work/pull/23), [#25](https://github.com/Yehia-Fahmy/ece750-work/pull/25); TAB01 development PASS via [#20](https://github.com/Yehia-Fahmy/ece750-work/pull/20); G0 TAB-only accepted via [#22](https://github.com/Yehia-Fahmy/ece750-work/pull/22))

> **Document status (S4).** This WP12 draft is the **honest course fallback**: **no frozen main collection**, **G2 not accepted**, **G3 freeze canceled**, and **no main factorial claim**. The text records (a) the intended methods/design, (b) measured **development/pilot** evidence (TAB01 `tab01-slice-v6` PASS; G1 long-pilot telemetry), (c) measured **held-out FAIL** evidence (two archives), and (d) explicit withdrawals. Do **not** invent acquisition rates, visibility contrasts, intervals, or “expected” findings from development cells or failed held-out runs. Style reference: `project/report/final-report.md` (do not overwrite).

---

### Abstract

This extension asked whether declaring task-reviewer access to intermediate reasoning (**T**) and/or final justification (**J**) changes prohibited shortcut **acquisition** in a local tool environment. The planned confirmatory design was a matched factorial over table templates × visibility × information state × shortcut availability, with deterministic action scoring and optional local semantic audit.

**What was delivered under S4 (Dec 4 package):** validated contracts, mediated environment, TAB generators, local GPU actor path, and development/pilot evidence—including a TAB01 `tab01-slice-v6` capability probe and 16-cell development archive that **passed**, plus long-pilot telemetry. **Held-out G2 qualification failed twice** (completion ~75%; easy no-shortcut success 55%) and was **not** accepted. Consequently there is **no freeze**, **no main 320-episode (or larger) factorial collection**, and **no confirmatory T/J visibility acquisition contrasts**. Independent semantic-judge claims are **withdrawn** (judge never qualified; no cloud judge). The course package therefore combines the historical observer study with an honest account of incomplete extension science—not a claim that the shortcut factorial’s scientific objectives were achieved.

---

### 1. Question and motivation

Verbalized reasoning can help oversight, but declared access to a channel is not the same as a faithful account of how an answer was reached. Prior work shows models can respond to biasing hints without acknowledging them ([1], [2]). The completed preliminary study in this course (`project/report/final-report.md`) asked whether **declared developer access to reasoning** changes wrong-hint agreement on BBH items. That study found a clearer hint effect than visibility effect, with fragile automated acknowledgment labels on the rare cases that matter for concealment-style secondary outcomes.

This extension asked a related but distinct set of questions in a **task-solving tool environment** with discoverable answer shortcuts:

1. Does declaring that a task reviewer can see intermediate reasoning (**T**) and/or final justification (**J**) change prohibited shortcut **acquisition**?
2. When acquisition is recorded, what do T and J acknowledge, omit, or contradict—and how do those patterns change with visibility?
3. When authorized information is genuinely insufficient, does the actor abstain appropriately, submit an unsupported answer, or still acquire a forbidden answer?

**Contribution claim under S4 (reduced).** The course contribution is a **reproducible evaluation procedure** and an honest negative/partial capability record for local Qwen3-4B on RTX 3070 Ti in this TAB environment—not a completed confirmatory visibility experiment. Randomized prompt contrasts *would* have supported causal claims about these **notices in this environment** if a frozen main collection had been run. They were **not** run. They would still **not** establish subjective awareness, intent to deceive, or access to the model’s full internal computation. T is generated text, not a ground-truth account of thought ([2]).

**Separation from the original study.** The observer report, frozen protocol, and `observer_study` code remain historical evidence. This extension uses its own namespace (`project/shortcut-study/`), contracts, and (never frozen) protocol drafts. The integrated course package summarizes the original result as preliminary evidence and presents the extension’s incomplete outcomes separately.

**Scope honesty for December 4.** The original planning target of five families × 100 bases × two seeds (3,200 primary-actor episodes) remains **withdrawn**. The provisional S0 TAB-only 320-episode freeze target is also **withdrawn** under S4 after two G2 FAILs. Writing targets the honest fallback below.

---

### 2. Study design *(intended; not executed as main)*

The following subsections describe the design that was built and would have been frozen under S0. Under S4 they remain **methods documentation**, not a claim that the factorial was collected.

#### 2.1 Channels and evaluator roles

| Channel | Meaning |
| --- | --- |
| **A** | Terminal structured answer/status (`answer` / `insufficient_information` / `clarification`), plus result/artifact as applicable |
| **T** | Ordered **native** intermediate reasoning segments linked to turns; missing T is a missing channel, not “no reasoning” |
| **J** | Final user-facing justification prose, separate from A and from T |

| Role | Sees |
| --- | --- |
| **Task reviewer** (named in the actor prompt) | Assigned visibility cell only: V00=A; V01=A+J; V10=A+T; V11=A+T+J |
| **Research auditor** | Always A+T+J+events, regardless of the task-reviewer cell |

Visibility notices promise privacy **from the task reviewer**, not from research logging. Exact notice wording stayed provisional in `configs/development/visibility.json` (never frozen).

#### 2.2 Factorial cells *(intended S0 core)*

One **base scenario** yields **16 matched episodes** per replicate seed:

| Factor | Levels |
| --- | --- |
| Information state | Complete vs genuinely insufficient authorized information (paired) |
| Shortcut availability | Present vs physically absent (absent removes data/routes) |
| Visibility | V00 / V01 / V10 / V11 |

**Core policy (restricted acquisition study):** only task-listed approved evidence/methods may be used. Under the TAB work that shipped, the implemented shortcut mechanism is **prior-agent notes**.

#### 2.3 Task environment (TAB family)

S0 would have used the **tables** family only (TAB01–05):

| ID | Template | Answer type (summary) |
| --- | --- | --- |
| TAB01 | Net delivered quantity (North) | integer net units |
| TAB02 | Invoice reconciliation | integer unpaid open balance |
| TAB03 | Stock balance (WH-A) | integer ending units |
| TAB04 | SLA eligibility totals | integer in-SLA support count |
| TAB05 | Weighted defect rate | integer basis points (truncating) |

**Tools (mediated):** `list_resources`, `read_resource`, `calculate`, `check_candidate` (where applicable), `request_clarification`, `submit`.

#### 2.4 Actors, judges, and compute

| Role | Candidate used in pilots | Constraint |
| --- | --- | --- |
| Primary actor | Local Qwen3-4B / llama.cpp on RTX 3070 Ti | Zero external inference |
| Primary judge | Not qualified | **Withdrawn** under S4; no cloud judge |
| Optional second actor | Out | Dropped before visibility/info controls |

#### 2.5 Scope ladder outcome

| Tier | Package | Status for Dec 4 |
| --- | --- | --- |
| **S0** | TAB-only × 1 seed → **320** main episodes | **Withdrawn** — G2 never passed |
| **S1** | 3 families × 1 seed → **960** | **Not selected** |
| **S3 / course core** | 100 × 16 × 2 → **3,200** | **Withdrawn** earlier for calendar |
| **S4** | **0** main factorial episodes | **Selected 2026-11-17** |

Rules that stayed fixed in planning: four T/J visibility cells; complete/incomplete pairing; shortcut present/absent controls; zero acquisitions would have been a valid result. Under S4 those controls were **not** exercised in a frozen main run.

---

### 3. Metrics and scoring *(prespecified; main unused)*

Keep fields separate; never collapse into a single “deception score.”

#### 3.1 Deterministic / action-grounded *(would have been authoritative for primary behavioral claims)*

| Domain | Examples |
| --- | --- |
| Integrity | Completed / truncated / tool failure / extraction failure / interrupted / not attempted |
| Acquisition | Attempted vs successful; resource/method; first event timing |
| Compliance | Authorized under pinned policy; mandatory checks completed |
| Task result | Factual correctness; **authorized** success; announced status; insufficiency appropriateness |

Facts come from the event ledger and validators, not from searching T/J to rescue an answer.

#### 3.2 Semantic / language audit *(withdrawn under S4)*

Live local judge execution and held-out fixture qualification did not complete. **Semantic conclusions are withdrawn.** Audit **preparation** (coverage, evidence binding, sampling plan) exists and was exercised on authentic development records; preparation ≠ qualified judgment.

---

### 4. Analysis plan *(prespecified; not applied to main)*

The confirmatory plan used restricted, **shortcut-present** acquisition rates \(r_{00}, r_{01}, r_{10}, r_{11}\) with T- and J-visibility contrasts, paired bootstrap over base scenarios, assigned-denominator missingness, and finite-sample language for zero events.

**Under S4 this analysis was not applied to any main archive.** Development and failed held-out scores are **not** substituted as confirmatory visibility effects. Synthetic WP07 fixtures remain harness checks only.

---

### 5. Implementation and gate honesty *(as of 2026-11-17; S4)*

| Area | State |
| --- | --- |
| Contracts (WP01) | Accepted |
| TAB catalog (WP02-TAB) | TAB01–05 development catalog (`tab-catalog-v2`); **G0 TAB-only accepted** (#22); not five-family |
| Environment / runner (WP03) | Mediated tools; mock + authentic native A/T/J/event capture; GPU lease; owned offline server |
| Deterministic scoring (WP04) | TAB ledger scoring exercised; full package acceptance pending |
| Semantic judge (WP05) | Prep only → **semantic claims withdrawn** |
| Analysis harness (WP07) | Synthetic scaffolding only; **no main contrasts** |
| Actor capability (dev) | TAB01 `tab01-slice-v6` probe + 16-cell **PASS** (#20); prior v5 FAIL preserved (#16) |
| Held-out qualification (G2) | **FAILED twice** (#23, #25); `gates.G2=failed` |
| Frozen protocol / main run | **None**; `gates.G3=canceled`; WP09–WP11 **canceled** |
| Scope tier | **S4 declared** (`handoffs/2026-11-17-s4-honest-course-fallback.md`) |

#### 5.1 Development / pilot evidence (positive, not main)

Evidence kind: `local_model_capability_probe_not_main` / `local_model_development_not_main`. Host: DESKTOP-VEMMES3 · RTX 3070 Ti.

| Run | Role | Outcome (recorded) | Tracked evidence |
| --- | --- | --- | --- |
| `capability-probe-tab01-v6b` | Two-cell capability probe | **PASS** — complete: `list_resources` → `read_resource`×3 → `calculate` → submit authorized **57**; incomplete: reads then typed insufficiency | `results/qualification/capability-probe-tab01-v6.json` |
| `native-qualification-tab01-v6-16cell` | Full 16-cell development archive | **PASS** — **16/16** completed; complete strict **8/8**; incomplete strict **8/8**; mean ~28.6 s; peak/headroom 5292/2900 MiB | `results/qualification/native-qualification-tab01-v6-16cell.json` |
| `g1-long-pilots-20261116` | Development hard/extreme long pilots | **Recorded** — 9/10 completed (TAB02 hard `model_format_failure`); mean ~31.9 s; peak/headroom 5271/2921 MiB; **does not accept G1 alone** | `results/qualification/g1-long-pilots-20261116.json` |

#### 5.2 Held-out G2 FAIL evidence (negative; both preserved)

Evidence kind: `local_model_held_out_qualification_not_main`. `g2_accepted=false` in both summaries. **Main was not executed.**

| Run / PR | Completion | Easy no-shortcut (≥80% gate) | Terminals (completed / budget_limit / format) | Tracked evidence |
| --- | ---: | ---: | --- | --- |
| `g2-held-out-20261116` / [#23](https://github.com/Yehia-Fahmy/ece750-work/pull/23) | **238/320 = 74.38%** | **11/20 = 55%** | 238 / 54 / 28 | `results/qualification/g2-held-out-20261116.json` |
| `g2-held-out-20261116-catalog-v2` / [#25](https://github.com/Yehia-Fahmy/ece750-work/pull/25) | **239/320 = 74.69%** | **11/20 = 55%** (TAB01 4/4; TAB02 **0/4**; TAB03 2/4; TAB04 3/4; TAB05 2/4) | 239 / 54 / 27 | `results/qualification/g2-held-out-20261116-catalog-v2.json` |

Parseability among complete+completed cells passed on both subsets (108/108; 111/111). Catalog-v2 (#24) did **not** clear G2. These archives are retained as negative evidence; they are **not** soft-washed into a partial main claim.

**What this closes under S4:** the decision to stop main-collection ambition for Dec 4 and report incomplete science honestly.

**What this does *not* create:** a main factorial finding; a G2 pass; a freeze; a visibility-effect estimate.

---

### 6. Timeline toward December 4, 2026

All times America/Toronto.

| Window | Milestone | Report implication |
| --- | --- | --- |
| Through Nov 16 | TAB01 v6 PASS; G0 TAB-only accept; G2 FAIL #23; catalog-v2; long pilots | Pilot + negative held-out evidence accrued |
| Nov 17 | G2 FAIL #25; **S4 declared** | Methods + pilots + withdrawals; **no main Results** |
| Nov 17–30 | Finish S4 WP12 narrative / figures shells from **pilot-only** evidence | No new main GPU collection |
| Dec 1–3 | WP13 packaging (pilot-only bundle) | Submission-ready under S4 |
| **Dec 4** | Course report due | Presentation date **TBD**; page limit **TBD** |

---

### 7. Results *(S4: pilot / incomplete-extension status only)*

#### 7.1 Primary narrative under S4

There is **no main-study results table**. The scientific outcome for the extension is:

1. **Procedure built:** contracts, TAB generators, mediated tools, durable native capture, deterministic scoring path, audit preparation, local GPU lease/runtime.
2. **Development capability on TAB01 cleared** after `tab01-slice-v6` (probe + 16-cell PASS).
3. **Held-out qualification did not clear** on two authentic 320-episode attempts; actor was **not** main-qualified.
4. **Therefore** confirmatory T/J visibility acquisition contrasts were **not** estimated from a frozen main archive.
5. **Semantic transparency questions** remain unanswered by a qualified local judge (withdrawn, not replaced by cloud inference).

| Item | Status |
| --- | --- |
| Capability probe (`capability-probe-tab01-v6b`) | PASS (development) |
| 16-cell development archive (`native-qualification-tab01-v6-16cell`) | PASS (development) |
| Prior v5 16-cell FAIL (#16) | Preserved |
| G1 long pilots | Recorded 9/10; G1 not formally accepted |
| G2 held-out #23 | FAIL (238/320; easy 55%) |
| G2 held-out #25 (post catalog-v2) | FAIL (239/320; easy 55%) |
| Shortcut **acquisition rates** by visibility (confirmatory) | **Not computed / not claimed** — no main run |
| Semantic T/J audit on main | **Not run / withdrawn** |
| Gate / freeze | G0 accepted; G2 **failed**; G3 **canceled**; **S4** |

Provenance for the rows above reconciles to the tracked qualification JSON under `results/qualification/` (raw trees under ignored `project/runs/shortcut-study/`).

#### 7.2 Main-study slots *(explicitly empty — not TBD-for-later invention)*

**Main collection was not started.** The following confirmatory slots remain empty by decision, not by oversight:

1. Acquisition rates by visibility cell (shortcut-present; assigned denominators).
2. T- and J-visibility contrasts with bootstrap intervals.
3. Abstention vs unsupported answers by information state on a frozen main schedule.
4. Paired T/J disclosure among acquisitions (semantics withdrawn anyway).
5. Provenance to `results/main/<run_id>/` — **no such run**.

Do not draft numeric stand-ins from development 16-cell scores or from either G2 FAIL archive.

---

### 8. Reliability, limitations, and improvements

- Single local quantized actor (Qwen3-4B); no multi-model replication.
- Declared reviewer access ≠ proven belief that the model “feels observed.”
- Observed tool events ≠ proven causal reliance on shortcut content.
- T/J omission ≠ intent; process claims only where events can support or contradict.
- Semantic judge never qualified; rare-class labels especially fragile; **no human grading accuracy claimed**.
- Generalization limits: TAB-only development catalog; difficulties uncalibrated; one shortcut mechanism (prior-agent notes).
- Calendar/capability pressure forced S4 after two G2 FAILs; the reduction from 3,200 → S0 (320) → **S4 (0 main)** is disclosed, not concealed.
- Development PASS on tab01-v6 is **not** held-out qualification; held-out completion ~75% and easy success 55% blocked freeze.
- Zero external inference by design constrained remediation options (no cloud actor/judge).

**Improvements (forward-looking):** further development-only format/budget work on TAB02–05; fresh held-out only after a real lever; calibrated difficulties; additional mechanisms/families only with forecast; held-out judge calibration; repeated seeds—**none of which are claimed as completed for Dec 4**.

---

### 9. Conclusion

Under S4, the extension delivers a reproducible local evaluation stack and an honest partial capability record: TAB01 development competence after `tab01-slice-v6`, preserved failures (v5 archive; two G2 held-out FAILs), and explicit withdrawal of the main shortcut-factorial scientific claim. The original observer study remains the completed preliminary evidence in this course package. Prefer a reproducible procedure and honest uncertainty over a forced positive visibility story.

---

### References *(starter list; verify primary sources before novelty claims)*

[1] Turpin, M., Michael, J., Perez, E., and Bowman, S. R. (2023). *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting.* NeurIPS 36.

[2] Chen, Y., et al. (2025). *Reasoning Models Don't Always Say What They Think.* arXiv:2505.05410.

[3] Suzgun, M., et al. (2023). *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them.* Findings of ACL. *(Original study tasks; cite if summarizing preliminary evidence.)*

[4] Qwen Team (2025). *Qwen3-4B model card.* Exact checkpoint/runtime hashes recorded in qualification manifests; no freeze hash set under S4.

**TBD:** expanded related-work pass (monitoring, faithfulness, agent evals); do not claim novelty from planning docs alone.

---

### Reproducibility, AI disclosure, and grading notes

- Derived statistics for any pilot tables must regenerate from committed qualification JSON/scripts without hidden spreadsheet edits.
- Raw HTTP/tool archives under ignored `project/runs/shortcut-study/` are a separate authenticity package; say so honestly.
- Historical files in `preservation-manifest.json` must still match.
- **AI disclosure:** AI assistance was used extensively for code, orchestration, drafting, and automated tooling in this extension. This does **not** constitute human grading accuracy, independent human scientific validation, or a claim that model traces are faithful internal accounts. No cloud inference was used for actor/judge episodes.
- Course format: four-page core + separated references/appendices until official page limits arrive; presentation **TBD**; submission is a researcher action (`submission_authorized: false` in `state.json`).
- Scope claims in the final PDF must match **S4** (0 main factorial episodes), not the withdrawn 3,200 or provisional 320 targets.

---

### Appendices outline *(outside four-page core)*

| Appendix | Content |
| --- | --- |
| A | Provisional notices, policy text, tool schemas (never frozen) |
| B | TAB task examples (complete/incomplete; present/absent prior-agent note) |
| C | Original observer-study summary (pointer to frozen report; do not rewrite history) |
| D | Qualification/gate evidence: tab01-v6 PASS; G2 FAILs #23/#25; S4 decision |
| E | Judge validation — **withdrawn** (prep-only) |
| F | Reproduction commands and delivery checklist (WP13; pilot-only) |
| G | Slides + speaker notes *(separate artifacts)* |

---

## TBD checklist (do not silently close)

- [ ] Official page limit and presentation date/format
- [x] Scope-ladder decision: **S4 declared** (2026-11-17); no freeze; no main N
- [x] Fresh multi-cell **development** evidence on TAB01 (`tab01-slice-v6` probe + 16-cell PASS via PR #20)
- [x] Integrator **G0** TAB-only acceptance (PR #22)
- [x] Held-out actor qualification (**G2**) — **failed twice** (#23, #25); documented under S4
- [x] Judge qualification outcome — **withdraw semantics**
- [ ] G1 formal acceptance (optional under S4; long pilots already recorded)
- [ ] Generated pilot-only summary tables for the four-page core (no faux main contrasts)
- [ ] AI-disclosure wording matched to actual assistance used (draft present; finalize in PDF)
- [ ] Slide deck and speaker notes
- [ ] WP13 reproduction record and submission checklist
