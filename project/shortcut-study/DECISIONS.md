# Decision record

Recorded November 15, 2026. IDs are stable for work-package references.

| ID | Decision | Status / basis |
| --- | --- | --- |
| D01 | Preserve all original proposals, plans, source, frozen records, and reports; add the extension separately | Explicit user requirement |
| D02 | Focus on shortcut acquisition and disclosure, not evidence tampering | Explicit user correction |
| D03 | Keep T (intermediate trace) distinct from J (final justification) | Explicit user clarification |
| D04 | Scientific research auditor always gets A+T+J+events; task reviewer gets the assigned view | Resolves the user's concern about detecting discrepancies in hidden-channel conditions |
| D05 | Include prior-agent notes, graded difficulty, and insufficient-information pairs | Explicit user additions |
| D06 | Broad permission does not name a shortcut; absent shortcuts are actually removed | Explicit user wording/control requirements |
| D07 | Use logs and reference validators for primary facts; evidence-backed model judgments for language | Discussed evaluation recommendation; detailed rubric still unfrozen |
| D08 | No required manual labeling; automatic judge agreement is not semantic ground truth | Preserves automated workflow and stated quality limitations |
| D09 | Only RTX 3070 Ti 8 GB; no MacBook, rented compute, hosted actor, hosted judge, or free remote inference | Latest explicit user constraint |
| D10 | Deliver course report by December 4; do not optimize this phase for a large publication study | Latest user target plus confirmed repository deadline |
| D11 | Keep V2 as a dated design snapshot; add current constraints and execution decisions here | Additive organization |
| D12 | No new experimental generations in this planning pass | User assigned planning and future orchestration |

## Superseded suggestions

- Renting 24–48 GB GPUs or paying hosted judges: excluded by D09.
- Treating December 4 as provisional: superseded by the instructor clarification recorded in course discussion #16 and repository commit `3f17534`. Final page limit is still unresolved.
- Passing only the experimental reviewer view to the research auditor: incorrect; D04 requires the full record.
- Treating reading prior notes as necessarily prohibited: depends on policy. Core access-restricted and reuse-with-required-verification experiments must stay distinct.
- Automatically expanding to every factor, three actors, and all seeds: not a commitment; choose scope using pilot cost and precision, before main outcomes.

## Proposed defaults pending pilot freeze

Core visibility uses V00/V01/V10/V11 with fixed answer/status scoring. Broad-permission, note-quality, grading-pressure, and visibility-timing studies are separate follow-ups. The core note condition uses access restriction; reuse-with-verification is a separately labeled extension. Correct complete notes are the core reference variant, with wrong/partial notes in an explicit robustness panel.

Record future decisions as dated entries with evidence, affected artifact/version, and whether they occurred before or after main data collection. Never silently rewrite a frozen decision or rename a failed main run as a pilot.

### November 15 — execution-planning defaults

The context checkpoint `ecb82d3` was committed and pushed before the execution plan. The proposed course core is 100 base scenarios × 16 matched conditions × two seeds = 3,200 episodes on one primary actor. Scope may decrease before main collection using the documented budget/capability gates. These counts are a planning recommendation, not a powered-study guarantee or a frozen protocol.

Proposed candidates are the existing Qwen3-4B actor, Qwen3-8B local primary judge, and a qualified small different-family alternative for independent review/optional replication. None is newly qualified by this documentation. A failed independent judge is a disclosed limitation; it does not permit external compute. Main actor collection targets November 27, audits November 29, full report November 30, and final packaging December 1–3.
