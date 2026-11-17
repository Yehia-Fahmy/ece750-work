# Guide for future orchestrators and workers

**Current execution entry:** [SWARM_START](SWARM_START.md), [completion packages](SWARM_WORK_PACKAGES.md), and `state.json.swarm_handoff`. The November 17 user-selected target is an S0 attempt with automatic S4 fallback if qualification and committed freeze are missing at **November 22, 18:00 America/Toronto**. This supersedes the prior S4-only completion target and the old planning-only restriction for the next executing swarm; all scientific gates, local-compute and preservation constraints remain. The older wave descriptions below are architectural background, not a request to restart completed work.

Status: execution guide. On November 15 the researcher explicitly authorized continued implementation with multiple agents, review, and code merging. Assignments and handoffs are recorded in `state.json`; this guide does not independently authorize a model run, external messages, or course submission.

## Starting an execution session

1. Read [SWARM_START](SWARM_START.md), [DECISIONS](DECISIONS.md), [completion packages](SWARM_WORK_PACKAGES.md), and [state](state.json), then assigned sections of [EXECUTION_PLAN](EXECUTION_PLAN.md) and [original work packages](WORK_PACKAGES.md). Read the latest handoff reconciliation and inspect the actual Git working tree; status files can be stale.
2. Verify the historical hashes. Preserve uncommitted user work. Locate the canonical checkout, original model symlink, and existing raw archives without moving them.
3. Record current date, remaining course time, actual GPU availability, and active processes. Select the next dependency-ready package. A past calendar target is not permission to skip qualification.
4. Assign one owner per package and one integration owner. Agree on the shared contracts before parallel implementation. Record assignment, input commit, and output paths in state; use a short commit boundary for each accepted package.
5. Treat all future CLI names in planning documents as deliverable requirements, not currently installed commands. Inspect implementation before invoking anything.

The original planning handoff contained documentation only. As of November 15, WP01 contracts are accepted and the CPU TAB01 slice is reviewed and locally merged. Native adapter/runner, lease, exact counter, owned server and audit plumbing now have authentic development runtime evidence; consult `state.json` and the latest qualification handoff. As of November 16, the TAB01–05 development catalog and scripted mocks exist (`handoffs/2026-11-16-tab-catalog-expansion.md`); `tab01-slice-v5` capability probe PASSed, but the follow-up 16-cell development archive FAILed (PR #16). `tab01-slice-v6` probe + 16-cell archive **passed** on DESKTOP-VEMMES3 (`handoffs/2026-11-15-native-qualification-tab01-v6-16cell.md` / PR #20); prior v5 FAIL preserved. Integrator **accepted TAB-only G0** for S0 (`handoffs/2026-11-16-g0-tab-accepted.md`) on WP01 + TAB catalog/spec + the v6 PASS archive—not from catalog mocks alone, and not as five-family G0. **G1/G2/G3 remain open** (not accepted). No extension model is main-qualified, no main protocol is frozen, and synthetic records are not a collected model dataset.

## Roles and boundaries

| Role | Owns | Can run in parallel with |
| --- | --- | --- |
| Integrator / orchestrator | Contracts, state, integration commits, gate records, final scope | CPU workers; avoids modifying their owned files |
| Task engineers | Assigned family generators and fixtures | Other family engineers after contracts stabilize |
| Environment engineer | Tool dispatch, isolation, event capture, model adapters | Task and scoring engineers using fixtures |
| Scoring engineer | Deterministic validators and derived records | Environment and task engineers |
| Evaluation engineer | Judge rubric, evidence coverage, review routing | CPU work; GPU tests only through operator |
| GPU operator | Lease, pinned runtimes, servers, pilot/main/audit jobs | CPU workers within measured RAM limits |
| Analyst | Frozen contrasts, simulations, analysis scripts, tables | Collection using schema fixtures; does not inspect main contrasts early |
| Report author | Literature, methods, original-study integration, report/slides | Implementation; adds measured claims only after accepted results |
| Reproduction reviewer | Independent checks against committed evidence | After relevant package completion; no unlogged result edits |

These are responsibilities, not a requirement for nine simultaneous agents. One agent may hold several roles. Four concurrent workers can cover integration, task generation, environment/scoring, and evaluation/report work. More agents do not increase the single GPU's capacity.

Suggested parallel waves:

- **Wave 1:** integrator owns WP01; report author starts WP12 background; independent worker inspects existing reusable components. No competing schema edits.
- **Wave 2:** after WP01, task engineers take separate WP02 family directories; environment engineer takes WP03; scorer takes WP04. All use shared fixture contracts.
- **Wave 3:** WP05 audit implementation and WP06 hardware qualification use the GPU sequentially; analyst completes WP07 on synthetic fixtures. Other workers finish generators.
- **Wave 4:** integrator executes WP08 qualification/freeze. Reviewer checks gate evidence. Failures return to the owning development package.
- **Wave 5:** operator handles WP09 actor collection then WP10 local audit; CPU workers check integrity and prepare report/reproduction scripts. Do not show effect estimates to prompt developers before collection closes.
- **Wave 6:** analyst completes WP11; author finishes WP12; reviewer completes WP13 and integrator packages the delivery.

## Source ownership and integration

All new scientific code belongs under `project/shortcut-study/src/shortcut_study/`. Use a separate import namespace and test directory. New scripts/configs/results/report belong beneath this extension. Asset and raw-run locations are described in [ARTIFACT_CONTRACTS](ARTIFACT_CONTRACTS.md).

Parallel workers own disjoint modules, tests, and fixtures. The integrator owns contracts, shared configuration, dependency metadata, state, and the top-level test runner. Workers request a contract change through a handoff entry before changing a shared schema. Interfaces are versioned; affected producers and consumers must pass integration checks together.

Use isolated branches/worktrees when the executing environment supports them; prefer `codex/shortcut-<package>` names. Do not delete existing worktrees: the original model directory currently depends on one. Every worktree resolves the GPU lease to the same canonical checkout. A single coordinator handles commits/pushes to main according to the execution session's authorization. Do not assume a worker's ability to edit a shared checkout authorizes staging another worker's files.

## Status and handoff protocol

Package states are `not_started`, `in_progress`, `blocked`, `ready_for_review`, `accepted`, or `deferred`. State changes require evidence and an owner. A blocked package names a concrete dependency or failed check; useful independent work can continue. “Accepted” means its acceptance evidence exists, not merely that a worker reported success.

Use [the handoff template](templates/HANDOFF.md) for every package boundary or interruption. Include the input/output commit, touched paths, commands and real results, artifact manifest, unresolved issues, next safe action, and GPU ownership. The accepting integrator records the handoff path in `state.json` and checks dependencies. Never record a nonexistent commit or predicted passing test as completed.

Long-running jobs write durable episode records and periodic status files. On recovery, identify which episode IDs are terminal, incomplete, or never attempted. Follow the frozen retry policy; an interrupted bad result is not a fresh scientific opportunity. Stop only owned processes. Preserve unsuccessful runs and audit failures.

## Escalation and decision rules

Routine implementation choices within the accepted contracts do not need repeated researcher approval. Record material scientific changes before freeze. Escalate only decisions that change the user's constraints or require missing user information: external compute, spending, removal of historical artifacts, unavailable submission requirements, or actual course submission. Do not add cloud inference as a convenience fallback.

Insufficient local hardware or failed judge qualification leads to the documented reduced scope or limitation. A zero measured effect is a finding. No desired finding, grade, or publication aspiration authorizes changing a denominator or hiding an unsuccessful run.

## Suggested launch instruction for the researcher

Use the current pasteable launch instruction in [SWARM_START](SWARM_START.md#pasteable-launch-instruction). The earlier example below predates the review and is retained for context.

> Execute the shortcut-study extension from `project/shortcut-study/README.md`. Follow the state and work-package dependencies; preserve the original study. You may delegate independent packages to agents. Use only the local RTX 3070 Ti, with one GPU owner and zero external inference. Start with contracts and the vertical slice, then qualify and freeze a feasible scope before main collection. Keep durable handoffs, finish the report and reproduction package by the documented December deadline, and leave course submission to me.

This is a suggested future instruction, not evidence it has already been given.
