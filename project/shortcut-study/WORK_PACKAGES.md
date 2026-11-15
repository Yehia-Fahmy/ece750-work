# Work packages and acceptance evidence

Every package below is a planned deliverable unless marked accepted in [state](state.json). Effort estimates are rough **active engineering time**, excluding model inference, downloads, and review. They are scheduling aids, not guarantees. Run only checks relevant to changed behavior; do not repeatedly rerun the entire suite without a reason.

| ID | Package / dependencies | Intended outputs and ownership | Acceptance evidence | Effort |
| --- | --- | --- | --- | --- |
| WP00 | Preserve context / none | Existing V2 snapshot, context, decisions, evaluation, historical hash manifest | Context checkpoint `ecb82d3` pushed to main; historical hashes match | Done |
| WP01 | Shared contracts / WP00 | `schemas/`, `configs/development/`, contract fixture records; integrator owns shared interfaces | Round-trip episode/event schemas; all four packet filters; policy/state matrix; IDs and split rules; source of truth for scoring and budgets | 0.5–1 day |
| WP02 | Task generators / WP01 | `src/shortcut_study/tasks/{tables,documents,planning,debugging,verification}/`; separate family ownership | Five templates/family; four calibrated difficulty targets; complete/incomplete pairs; four compatible shortcut types; hidden validators and impossibility certificates; no-answer-leak and absent-resource fixtures | 2–4 days distributed |
| WP03 | Environment and model adapters / WP01 | `src/shortcut_study/environment/`, `adapters/`, `runner/`; environment owner | End-to-end authentic native T/tool/A/J capture; isolation and generic-route tests; independent reviewer filters; malformed/interrupted/over-limit handling; durable event ordering | 1–2 days |
| WP04 | Deterministic scoring / WP01 | `src/shortcut_study/scoring/` and fixtures; scoring owner | Correct answers separate from compliance; attempts vs acquisitions; missing-data refusal vs lucky guess; genuine required-check omissions; no mental-calculation inference from missing tool calls | 0.5–1 day |
| WP05 | Automated language audit / WP01, sample WP03 records | `src/shortcut_study/audit/`, rubric configs, constructed fixture splits; evaluation owner | Structured evidence-validated labels; temporal revisions; injection defense; whole/chunk coverage; all-flagged plus seeded 10% routing; preserved independent labels and uncertainty | 1–2 days plus local tests |
| WP06 | Local model/runtime feasibility / minimal WP03 and WP05 | `results/qualification/hardware/`, pinned model/runtime asset manifests, GPU lease implementation; operator | Measured memory/latency on long episodes and audits; native multi-turn trace/tool support; shared lock across worktrees; full workload forecast; no external inference | 0.5–1 day plus GPU time |
| WP07 | Analysis implementation / WP01, WP04 schema | `src/shortcut_study/analysis/`, simulation fixtures, draft analysis protocol; analyst | Known injected effects recovered; pairing/weighting/missingness tests; bootstrap and multiplicity outputs; null/zero-event warnings; weighted review diagnostics and label sensitivity | 0.5–1 day |
| WP08 | Qualify and freeze / WP02–WP07 | `results/qualification/`, `configs/frozen/<version>/`, freeze manifest and gate record; integrator/operator | Fresh held-out qualification; capability/judge gates; measured total budget including secondary reviews; full assigned schedule and scope committed before main; unresolved limitations documented | 0.5–1 day plus GPU time |
| WP09 | Main actor collection / WP08 | Ignored raw archive plus committed progress/integrity summaries; operator only | Every assigned ID accounted for; authentic records and hashes; condition-balanced execution; fixed technical retries; no parameter changes after outcomes; cutoff observed | Measured GPU budget |
| WP10 | Main semantic audit / WP08, available WP09 records | Ignored raw audit archive; structured audit/review rows and coverage; evaluation owner/operator | Every eligible record audited or unresolved; coverage and evidence checks; independent review sampling manifest; exact judge provenance; no actor text executed | Measured GPU budget |
| WP11 | Final analysis / WP07, WP09, WP10 | `results/main/<run_id>/`, generated tables/figures and machine-readable statistics; analyst | Every reported count reconciles; frozen contrasts; assigned-denominator bounds; semantic uncertainty and label-error sensitivity; no undeclared pooling across versions/models | 0.5–1 day |
| WP12 | Integrated report and presentation / WP00 for background; WP11 for findings | `report/` source/PDF, references, slides, speaker notes; author | Original study separated from extension; methods match frozen protocol; generated figures; limitations, AI disclosure, grading requirements; no unsupported causal/faithfulness claims | 1–2 days, start early |
| WP13 | Reproduce and deliver / WP11, WP12 | `delivery/` manifest/checklist and reproduction record; independent reviewer/integrator | Clean-checkout derived-data reproduction; historical hashes unchanged; PDF/slide inspection; all links/counts verified; raw-evidence availability explained; package ready before Dec 4 | 0.5–1 day |

The estimates overlap across CPU workers. WP02 and isolation work are the biggest engineering uncertainty. A single developer should use the scope ladder rather than treating distributed estimates as a promise.

## Mandatory vertical slice before broad implementation

Use one small table-reconciliation case with a restricted prior-agent note and a complete/incomplete pair. Execute all four visibility cells with and without the note: 16 episodes for one seed. Use this as development data only. First use a deterministic mock actor to validate routing; then a local model for authentic trace/tool extraction. A mock is never counted as an actor observation.

The slice must demonstrate: real absent-resource removal; successful restricted acquisition when deliberately exercised by a fixture; honest insufficiency scoring; distinct A/T/J; a task-reviewer packet lacking hidden channels; a full research-auditor packet; an evidence-cited semantic verdict; and a saved failed/interrupted episode. Scale to the rest of the catalog only after these mechanics work.

## Family-package partition

WP02 can be split into WP02-TAB, WP02-DOC, WP02-PLAN, WP02-CODE, and WP02-VERIFY. Each subpackage owns its generator and tests; shared generation utilities remain integrator-owned. All five must implement the same contracts. The three-family fallback defers CODE and VERIFY only through the pre-main decision in the execution plan, with a reason and changed claims.

## Gate ownership

- G0: integrator accepts WP01 and the catalog/specification part of WP02.
- G1: integrator accepts the vertical slice plus isolation/scorer evidence and initial WP06 measurements.
- G2: qualification reviewer checks capability, judge, and compute evidence; automated reference tests supply correctness where possible.
- G3: integrator signs the freeze checklist and commits the version. A review by an agent is not human scientific validation.
- G4/G5: operator and analyst reconcile collection/audit denominators.
- G6: reviewer reproduces the package; researcher handles final submission.

## Follow-ups deliberately outside the core

Broad-permission runs using “You may use any tools or information available to you in this task environment”; permitted prior notes with mandatory independent verification; wrong/partial/stale notes; actual process grading versus answer-only grading; notices introduced after shortcut exposure; controlled source perturbations to establish reliance; and limited-view monitor evaluations.

Each needs its own question, assignment, rubric, power/precision discussion, and compute forecast. Broad permission changes which information is legitimate. A wrong note does not by itself prove use unless the intervention and alternative explanations are controlled. Keep these as future packages after a completed core, not implicit extra dimensions in December's factorial.
