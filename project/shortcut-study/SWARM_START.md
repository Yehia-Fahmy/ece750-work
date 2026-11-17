# Completion swarm — start here

Updated November 17, 2026. User-selected objective: **“Attempt the new experiment, with a firm S4 fallback cutoff.”** The user also asked that the next swarm independently finish the work. This handoff prepares that execution; it does not claim repairs or new experiments have already happened.

## Outcome to deliver

Repair the confirmed research/implementation defects, attempt a **freshly qualified S0 TAB-only experiment**, and deliver the integrated course report, PDF, final slide deck, speaker notes, reproducible analysis/evidence, and a submission checklist. If qualification/freeze fails the cutoff below, complete **S4** from the original study plus honest extension methods/pilots/failures, without new main factorial claims. Do not stop at code fixes, a Markdown draft, an outline, or a list of work for the researcher.

S0's starting candidate remains 20 content-distinct base scenarios × 16 matched cells × one seed = 320 main actor episodes. It is **not frozen or powered by assertion**. Choose feasible final scope only through the existing pre-main gates and precision evidence. No five-family expansion or extra actors are needed for this completion assignment.

The user authorizes autonomous agent orchestration, ordinary repairs, testing, local qualification/collection after gates, analysis, and artifact construction under the established constraints. Use one RTX 3070 Ti and zero external experimental inference. The current chat prepares and publishes the handoff; the next executing swarm owns this work. Course upload, paid/external compute, changing the hardware constraint, or altering protected original research still require explicit researcher instruction. Do not repeatedly ask to proceed with routine authorized steps.

## First actions: reconcile, assign, execute

1. Read this guide, [AGENTS](AGENTS.md), the current [decisions](DECISIONS.md), [agent coordination guide](AGENT_GUIDE.md), and [state](state.json). Inspect `git status`, your branch/ref, available tools and current date. Do not overwrite another worker's changes or start from an outdated feature branch.
2. Read the [review](reviews/2026-11-17/README.md), the [handoff reconciliation](handoffs/2026-11-17-completion-swarm.md), and [current work packages](SWARM_WORK_PACKAGES.md). Read only the detailed reviewer report and original WP/protocol sections needed for your assignment next. There is no need for every worker to reread every historical handoff.
3. The orchestrator verifies historical/review hashes, records its actual input commit and host, finds local archives/assets, and assigns dependency-ready packages in `state.json.swarm_handoff.packages`. Old owner names in historical WP records do not mean those agents are running. Reconcile actual evidence before accepting any previous “done” status.
4. Start three disjoint CPU lanes: task identity/design (SW01), native/audit provenance (SW02), and statistics/release inputs (SW03). The orchestrator owns shared files and can concurrently maintain the report's claim/evidence ledger. Do not spend a new 320-episode qualification run before the CPU repairs and broader development capability checks are accepted.
5. Require each worker to reproduce its assigned defect independently, implement a targeted fix, add a meaningful regression, and hand off evidence for review by someone other than the author. Integrate reviewed commits in short steps. Use the launch text below for the orchestrator; use the package brief template for workers.

## Firm deadlines and automatic fallback

All deadlines are **America/Toronto**, not the machine's local timezone. Recalculate remaining time at startup. These cutoffs are requirements for the next swarm, not a prediction of success.

| Cutoff | Required outcome / automatic action |
| --- | --- |
| **Nov 22, 2026, 18:00** | Fresh actor qualification accepted, analysis accepted, semantic scope/compute decision recorded, and G3 frozen protocol committed. If any is missing, select S4 automatically; keep repairing/package work, but do not start main collection or extend this deadline without a new user instruction. |
| **Nov 27, 2026, 18:00** | Stop starting new actor blocks. For a started frozen study retain every assigned ID, including incomplete/unattempted outcomes; report partial collection honestly. Never rename attempted main episodes as pilots or shrink the denominator. |
| **Nov 29, 2026, 18:00** | End experimental inference, including semantic audits. Remaining audits become unresolved under the frozen missingness policy. Prioritize final analysis/writing and record any actual technical inability to stop/close owned work safely. |
| **Nov 30** | Complete report draft with generated, checked results or S4 fallback evidence. |
| **Dec 3, 2026, 18:00** | Independently reproduced and visually checked PDF/deck/source/manifest ready for researcher review and submission. |
| **Dec 4, 2026, 23:59** | Repository-recorded course report deadline. Course submission remains researcher-owned. |

If first activated after the freeze cutoff with no accepted freeze, enter S4 immediately. An unsuitable actor, exhausted time budget, unavailable hardware, or inadequate judge is a scientific constraint, not permission to use a cloud fallback, relax gates after seeing results, or fabricate completion. Judge failure may permit a documented behavioral-only S0 before freeze; it cannot support semantic conclusions. Record exact scope decisions and changed claims. S4 completes delivery, not the extension's original scientific question.

## Current reality and authority

- Reviewed scientific code baseline: `3c155ba`. Handoff base: `7c4aed7` on fetched `origin/main` (includes later S4 report/packaging). No source/test/result changes occurred between these baselines; the reviewed code defects remain open.
- Original study: 58 tests and complete raw/statistical reproduction passed in the review. Extension: 213 tests passed at the review baseline; fresh handoff checks are recorded in the handoff file. Passing tests do not cover the newly reproduced defects.
- Latest actor qualification: 239/320 completed; 11/20 easy successes. G2 is **failed/not accepted**, and the second run reused the first run's worlds. There is no qualified semantic judge and no frozen main protocol.
- `#26/#27` already added S4 report and delivery drafts. The review's stale-report finding is partly superseded; the code/design findings are not. The user's latest instruction reopens an S0 attempt with the cutoff above. Preserve the S4 artifacts as the fallback, rather than deleting or pretending they were main results.
- Current `state.json.swarm_handoff` owns new package assignments/acceptance. Existing `packages`, `gates`, and historical handoffs retain scientific lineage and must be reconciled by the integrator as packages close. Evidence and actual files outrank stale prose; new dated user decisions outrank old planning-only or canceled-work instructions. Frozen run rules cannot be retroactively changed.

## Efficient coordination

Use one orchestrator and up to three simultaneous workers initially; match actual host capacity. More agents do not increase one GPU's throughput. Use platform subagents for subtasks, not user-owned chats, unless the user asks for separate chats. Do not infer authorization to message unrelated chats or people.

Each package has one writer, an explicit path allowlist, a named independent reviewer, and an input commit. Workers do not edit `state.json`, shared configs/schemas, dependency files, or shared CLI wiring without a documented ownership transfer. The orchestrator integrates those changes from agreed interface proposals. Do not assign two workers the same file simply because they address different functions. Use separate supported worktrees when useful; resolve all GPU ownership to the canonical lease and retain asset-dependent old worktrees. For shared-checkout work, use strict path ownership.

Workers run targeted tests. The integrator runs the full extension suite once per meaningful integrated wave and the historical/preservation checks at release boundaries. Reuse unchanged validation evidence with its commit/hash; rerun when relevant inputs change. Test output from fixtures is not actor evidence. Preserve dated review outputs; add new fix evidence rather than rewriting the review to pass. `analyze-dry` currently regenerates tracked fixtures: inspect it before claiming a read-only reproduction, and fix its side effects in SW03.

Changes after an acceptance boundary require review and checks of the affected interfaces before the next experiment; a previous SW05 pass does not automatically cover later judge/runtime changes. Freeze source/config identities only after the executable main path is integrated. Never rely on acceptance from a different code version without verifying compatibility.

Every handoff uses [the template](templates/HANDOFF.md), plus package ID, assigned paths, expected regression, reviewer, next runnable action, and blockers. The orchestrator updates state after acceptance, not on worker confidence alone. If blocked, work on independent CPU/report tasks rather than polling the GPU. Maintain durable progress during long runs; stop only owned processes.

## Completion means concrete artifacts

The final acceptance reviewer must be different from the relevant author and inspect the exact integrated commit. Require:

- All in-scope confirmed defects repaired with regression evidence; conditional/out-of-scope items explicitly resolved, rejected with evidence, or deferred with justified limits. No silent closure of an open finding.
- Either accepted frozen S0 with complete assigned accounting and reproducible analysis, or a dated S4 decision and an explicit record that the extension question remains unanswered. Preserve all failed/pre-main/main records and distinguish reused qualification from fresh evidence.
- Integrated report source plus readable PDF; final presentation deck plus speaker notes; checked citations, measured numbers, AI disclosure, and calibrated claims. Use a four-page core plus references/appendices provisionally while official formatting remains unavailable; keep that assumption visible and adjustable.
- Derived analysis/evidence rows and source/config/input/output hashes; CPU reproduction from a clean checkout; separate instructions for raw authenticity checks that need ignored local archives; visual PDF/deck inspection.
- Delivery manifest/checklist and reconciled state with unresolved researcher-only logistics clearly named. The swarm builds the PDF/deck and checks available archives itself; missing templates are routine implementation choices. Only actual course logistics/approval/upload remain researcher actions.

## Pasteable launch instruction

> Execute the completion swarm from `project/shortcut-study/SWARM_START.md` on the branch/ref containing this handoff. Independently validate and repair the review findings, assign disjoint work packages with separate reviewers, and carry the work through to a completed report/PDF/deck/notes/reproducibility package. Attempt a fresh qualified S0 study on the local RTX 3070 Ti only. If qualification and committed freeze are not complete by November 22, 2026 at 18:00 America/Toronto, select S4 automatically and finish the honest fallback deliverables. Preserve the original research, all failed archives, and frozen denominators. Follow the actor/inference cutoffs and update `state.json` with actual evidence. Routine authorized work does not need repeated confirmation; leave course submission to me.
