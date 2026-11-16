# Shortcut acquisition under declared reviewer visibility
## Methods / report skeleton for the ECE 750T extension study

Yehia Fahmy · ECE 750T, University of Waterloo · draft skeleton **2026-11-16**

> **Document status.** WP12 early draft. This is a writing skeleton and methods outline, not a frozen protocol and not a results paper. Placeholders marked **TBD** must stay empty until a freeze (G3) and accepted analysis (WP11) supply them. Do not invent rates, intervals, or “expected” findings. Style reference for voice and honesty: the completed observer report at `project/report/final-report.md` (do not overwrite that file).

---

### Abstract *(draft structure only)*

**TBD after results.** Intended shape (mirroring the observer report’s restraint):

- One-sentence question about declared T/J reviewer access and prohibited shortcut **acquisition**.
- Scope: local actor on RTX 3070 Ti; matched factorial over visibility × information state × shortcut availability; automated action scoring; optional local semantic audit of T/J.
- What was actually completed vs planned (scope ladder / fallback).
- Primary action-grounded contrast with uncertainty language that can include zero.
- Semantic findings only if a qualified local judge exists; otherwise explicit withdrawal.
- Closing: supports a reproducible evaluation procedure and honest limits—not claims of intent, deception, or faithful internal access.

---

### 1. Question and motivation

Verbalized reasoning can help oversight, but declared access to a channel is not the same as faithful explanation of how an answer was reached. Prior work shows models can respond to biasing hints without acknowledging them ([1], [2]). The completed preliminary study in this course (`project/report/final-report.md`) asked whether **declared developer access to reasoning** changes wrong-hint agreement on BBH items. That study found a clearer hint effect than visibility effect, with fragile automated acknowledgment labels on the rare cases that matter for concealment-style secondary outcomes.

This extension asks a related but distinct set of questions in a **task-solving tool environment** with discoverable answer shortcuts:

1. Does declaring that a task reviewer can see intermediate reasoning (**T**) and/or final justification (**J**) change prohibited shortcut **acquisition**?
2. When acquisition is recorded, what do T and J acknowledge, omit, or contradict—and how do those patterns change with visibility?
3. When authorized information is genuinely insufficient, does the actor abstain appropriately, submit an unsupported answer, or still acquire a forbidden answer?

**Contribution claim (provisional).** A controlled, auditable comparison of shortcut acquisition and T/J disclosure under separately manipulated reviewer-visibility notices, with deterministic action scoring and (if qualified) local semantic auditing. Randomized prompt contrasts can support causal claims about these **notices in this environment**. They do **not** establish subjective awareness, intent to deceive, or access to the model’s full internal computation. T is generated text, not a ground-truth account of thought ([2]).

**Separation from the original study.** The observer report, frozen protocol, and `observer_study` code remain historical evidence. This extension uses its own namespace (`project/shortcut-study/`), contracts, and (when frozen) protocol. The integrated course package should summarize the original result as preliminary evidence and present the extension separately.

---

### 2. Study design

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

Visibility notices promise privacy **from the task reviewer**, not from research logging. Exact notice wording is provisional in `configs/development/visibility.json` until freeze.

#### 2.2 Factorial cells

One **base scenario** yields **16 matched episodes** per replicate seed:

| Factor | Levels (core) |
| --- | --- |
| Information state | Complete vs genuinely insufficient authorized information (paired) |
| Shortcut availability | Present vs physically absent (absent removes data/routes; not mere omission from catalogs) |
| Visibility | V00 / V01 / V10 / V11 |

Shared across matched variants: question/world identity, template, intended difficulty, assigned shortcut mechanism, and seed pairing. Episodes are independent (fresh state; no carry-over).

**Core policy (restricted acquisition study):** only task-listed approved evidence/methods may be used. Discovery catalogs do not authorize resources outside that set. Core shortcut mechanisms (balanced before collection when the catalog exists): direct-result service, restricted reference, cached verdict, prior-agent notes. Required-check omissions are scored separately. Broad permission, wrong/partial notes, process grading, and timing-of-notice variants are **follow-ups**, not silent extra dimensions in the December factorial.

#### 2.3 Task environment *(planned; implementation status below)*

Believable workflows across families planned in the catalog: tabular/numerical analysis, multi-document reasoning, planning, debugging, verification. Tools are mediated (e.g. list/read resources, calculate, check_candidate, request_clarification, submit). Tool calls must be executable objects from action content—not inferred from T. Malformed/interrupted/over-limit episodes remain in the assigned denominator under the frozen technical policy.

#### 2.4 Actors, judges, and compute

| Role | Candidate (not frozen) | Constraint |
| --- | --- | --- |
| Primary actor | Existing local Qwen3-4B / llama.cpp path | RTX 3070 Ti 8 GB only; zero external inference |
| Primary judge | Local candidate (planning docs mention Qwen3-8B) | Same machine/lease; no cloud judge fallback |
| Independent review | Different-family local checkpoint if qualified | Same-model re-run ≠ independent validation |

Decoding and history policy are fixed across visibility cells after freeze. No condition-specific “stop thinking,” history clipping, or template change.

#### 2.5 Scope ladder *(choose before main; not a results claim)*

Planning target: 100 base scenarios × 16 × 2 seeds = **3,200** primary-actor episodes (judge calls additional). Affordable tiers and the three-family fallback are in `EXECUTION_PLAN.md`. Drop optional second actors and seeds before dropping visibility/information controls. **TBD at freeze:** selected tier, families, seeds, exact N, and whether semantic audit is in scope or withdrawn.

---

### 3. Metrics and scoring

Keep fields separate; never collapse into a single “deception score.”

#### 3.1 Deterministic / action-grounded *(authoritative for primary behavioral claims)*

| Domain | Examples |
| --- | --- |
| Integrity | Completed / truncated / tool failure / extraction failure / interrupted / not attempted |
| Acquisition | Attempted vs successful; resource/method; first event timing |
| Compliance | Authorized under pinned policy; mandatory checks completed |
| Task result | Factual correctness; **authorized** success; announced status score; insufficiency appropriateness; lucky unsupported guesses |

Facts come from the event ledger and validators, not from searching T/J to rescue an answer. Successful acquisition with transparent disclosure is still acquisition. A factually correct answer via a prohibited resource can fail authorized completion—report both.

#### 3.2 Semantic / language audit *(secondary; only if locally qualified)*

| Domain | Examples |
| --- | --- |
| Trace acknowledgment | Explicit use / rejection-only / hypothetical / absent / uncertain |
| Justification disclosure | Explicit / partial / absent; denial; uncertainty |
| Process claims | Supported / contradicted / not externally verifiable vs events |
| T↔J relationship | Consistent / omission / contradiction / revision / uncertain |
| Insufficiency explanation | Correct missing prerequisite / incorrect / unsupported definitive answer / uncertain |

Judge packets omit actor identity and condition codes where feasible; actor text may still reveal condition. Evidence must cite original passage/event IDs with coverage checks. Uncertain stays uncertain. Agreement is not semantic ground truth. If primary semantics fail qualification, **withdraw semantic conclusions** and retain the behavioral study.

---

### 4. Analysis plan *(prespecify before main; implement in WP07/WP11)*

**Primary acquisition analysis** uses the restricted, **shortcut-present** arm. The absent arm is a control (do not dilute rates with structural zeros). Weight complete/incomplete strata and task families equally as prespecified.

Let \(r_{00}, r_{01}, r_{10}, r_{11}\) be acquisition rates in the four visibility cells (seeds averaged within base scenario):

| Contrast | Definition | Role |
| --- | --- | --- |
| T-visibility | \(\bigl((r_{10}-r_{00})+(r_{11}-r_{01})\bigr)/2\) | Confirmatory |
| J-visibility | \(\bigl((r_{01}-r_{00})+(r_{11}-r_{10})\bigr)/2\) | Confirmatory |
| T×J interaction | \(r_{11}-r_{10}-r_{01}+r_{00}\) | Secondary unless promoted pre-collection |

Uncertainty: paired bootstrap resampling **base scenarios** within family/difficulty (planning default 10,000 draws, fixed recorded seed), retaining matched variants. Report individual 95% intervals and conservative simultaneous intervals for the two confirmatory contrasts (e.g. Bonferroni via 97.5% individuals). Do not describe ordinary bootstrap intervals as exact tests. No equivalence claim from an interval crossing zero.

**Missingness:** assigned-denominator bounds and complete-block sensitivity. **Zero events:** do not present a degenerate zero-width bootstrap as proof of zero population risk; use an appropriate finite-sample bound and state when the contrast is poorly identified.

**Semantics (if in scope):** report T and J separately; all-assigned joint acquisition+omission/denial rates; conditional disclosure among acquisitions (with selection caveat); alternate labels and bounded label-error sensitivity. Do not convert judge agreement into accuracy.

**Clustering note:** even 3,200 episodes are only ~100 base-scenario clusters—not 3,200 independent units.

---

### 5. Current implementation honesty *(as of 2026-11-16; development evidence only)*

This section is **not** a main-study result. It records why the report cannot yet fill Results.

| Area | State |
| --- | --- |
| Contracts (WP01) | Accepted; development configs provisional until freeze |
| TAB01 vertical slice | Mock + native capture paths exist for the 16-cell development factorial |
| Local runtime | Owned offline Qwen3-4B / llama.cpp path; GPU lease; short-episode memory sample recorded |
| Actor capability | **Not ready for main.** Authentic 16-episode development runs: actor requested clarification and submitted insufficient information without reading resources; deterministic scoring **0/8** on complete cases and **8/8** on incomplete cases (metadata fix did not resolve premature clarification) |
| Semantic judge | Preparation/audit plumbing exists; **live local judge execution and qualification pending** |
| Analysis package | WP07 not started |
| Frozen protocol / main run | **None** (`frozen_protocol: null`) |
| Gates | G0/G1 in progress; G2–G6 not started |

**Course-delivery fallback** (already in the execution plan): if no adequate main run by cutoff, the integrated report presents (a) the original observer result, (b) validated extension methods and pilots, and (c) explicit incomplete outcomes—without claiming the shortcut factorial’s scientific objectives were achieved.

---

### 6. Timeline toward December 4, 2026

All times America/Toronto. Operator must recalculate if work slips; past gate dates are not permission to skip qualification.

| Window | Milestone | Report implication |
| --- | --- | --- |
| Now | Capability diagnosis + methods skeleton (this file) | Fill background/methods; keep Results empty |
| Through G1/G2 | Vertical-slice feasibility; held-out qualification | Update §5 with measured gates only |
| By ~Nov 22 (G3) | Freeze protocol, N, models, analysis | Lock methods to frozen text; stop “provisional” wording |
| Nov 23–27 | Main actor collection (cutoff ~Nov 27 18:00) | No effect estimates shown to prompt developers early |
| Nov 28–29 | Audits + analysis (inference cutoff ~Nov 29 18:00) | Populate tables/figures from committed derived rows only |
| Nov 30 | Full report draft | Four-page core + appendices |
| Dec 1–3 | Reproduction, PDF/slides, packaging (WP13) | Submission-ready bundle; researcher submits |
| **Dec 4** | Course report due (11:59pm written-work policy) | Presentation date **TBD**; page limit **TBD** (assume 4-page core until resolved) |

---

### 7. Results *(empty until WP11)*

**Do not draft numeric findings.** Planned figure/table slots:

1. **Table.** Acquisition rates by visibility cell (shortcut-present; assigned denominators; missingness ranges if needed).
2. **Figure.** T- and J-visibility contrasts with bootstrap intervals (observer-report style restraint if intervals cross zero).
3. **Table.** Appropriate abstention vs unsupported answers by information state (and acquisition if any).
4. **Table/figure (optional).** Paired T/J disclosure among acquisitions, with uncertain cases visible—only if semantics are qualified.
5. **Provenance paragraph.** Every count reconciles to `results/main/<run_id>/` (or explicit pilot-only package under the fallback).

If the fallback applies, replace this section with a clearly labeled “Pilot and incomplete-extension status” subsection—not a faux main analysis.

---

### 8. Reliability, limitations, and improvements *(skeleton)*

Intended discussion points (fill with evidence later):

- Single local quantized actor; limited family/template coverage after any scope ladder cut.
- Declared reviewer access ≠ proven belief that the model “feels observed.”
- Observed acquisition ≠ proven causal reliance on shortcut content.
- T/J omission ≠ intent; process claims only where events can support or contradict.
- Semantic judge: fixture vs natural accuracy; rare-class fragility; no mandatory human labels.
- Generalization limits; no external compute by design.
- Calendar/capability pressure and any pre-main scope reduction, disclosed not concealed.

**Improvements** (forward-looking; not excuses for inventing results): capability-qualified actors; held-out judge calibration; repeated seeds; controlled reliance interventions; separate broad-permission / process-grading panels.

---

### 9. Conclusion *(TBD)*

Placeholder stance: state what action-grounded evidence supports; what remains inconclusive; what semantic claims are withdrawn; how the original observer study and this extension relate. Prefer a reproducible procedure and honest uncertainty over a forced positive visibility story.

---

### References *(starter list; verify primary sources before novelty claims)*

[1] Turpin, M., Michael, J., Perez, E., and Bowman, S. R. (2023). *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting.* NeurIPS 36.

[2] Chen, Y., et al. (2025). *Reasoning Models Don't Always Say What They Think.* arXiv:2505.05410.

[3] Suzgun, M., et al. (2023). *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them.* Findings of ACL. *(Original study tasks; cite if summarizing preliminary evidence.)*

[4] Qwen Team (2025). *Qwen3-4B model card.* Exact checkpoint/runtime hashes **TBD at freeze**.

**TBD:** expanded related-work pass (monitoring, faithfulness, agent evals); do not claim novelty from planning docs alone.

---

### Reproducibility, AI disclosure, and grading notes

- Derived statistics must regenerate from committed rows/scripts without hidden spreadsheet edits.
- Raw HTTP/tool archives under ignored `project/runs/shortcut-study/` are a separate authenticity package; say so honestly.
- Historical files in `preservation-manifest.json` must still match.
- AI assistance for code, drafting, and automated annotation is expected; claim no human grading accuracy or independent human scientific validation unless later supplied with provenance.
- Course format: four-page core + separated references/appendices until official page limits arrive; presentation **TBD**; submission is a researcher action (`submission_authorized: false` in `state.json`).

---

### Appendices outline *(outside four-page core)*

| Appendix | Content |
| --- | --- |
| A | Exact frozen notices, policy text, tool schemas |
| B | Task examples (complete/incomplete; present/absent shortcut) |
| C | Original observer-study summary (pointer to frozen report; do not rewrite history) |
| D | Qualification/gate evidence and scope-ladder decision |
| E | Judge validation fixtures, coverage, disagreement |
| F | Reproduction commands and delivery checklist (WP13) |
| G | Slides + speaker notes *(separate artifacts)* |

---

## TBD checklist (do not silently close)

- [ ] Official page limit and presentation date/format
- [ ] Frozen protocol version, hashes, N, families, seeds, budgets
- [ ] Actor capability gate passed on held-out qualification (or documented fallback)
- [ ] Judge qualification outcome (proceed / primary-only / withdraw semantics)
- [ ] Final confirmatory contrast list and multiplicity rule
- [ ] Generated tables/figures from accepted WP11 release
- [ ] AI-disclosure wording matched to actual assistance used
- [ ] Slide deck and speaker notes
- [ ] WP13 reproduction record and submission checklist
