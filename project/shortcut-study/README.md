# Shortcut study extension — start here

This is **additional research**, separate from the completed observer-framing study. Status: planning; no extension data collected and no main protocol frozen.

## Read in this order

1. [Context and user decisions](CONTEXT.md): the purpose, scope, and current constraints.
2. [Preserved design V2](../shortcut-study-design-v2.md): the November 14 discussion snapshot. Do not rewrite it to erase earlier proposals.
3. [Decision record](DECISIONS.md): later clarifications and precedence.
4. [Automated evaluation](EVALUATION.md): action scoring, research auditing, validation, and uncertainty.

The context checkpoint was committed and pushed to `main` as `ecb82d3` before the execution plan was developed, following the researcher's requested sequence.

## Execute the next stage

5. [Execution plan](EXECUTION_PLAN.md): December milestones, scope ladder, qualification gates, statistical contrasts, and completion requirements.
6. [Compute plan](COMPUTE.md): measured machine inventory, local model candidates, GPU lease, judge qualification, and full-pipeline forecasting.
7. [Protocol draft](PROTOCOL_DRAFT.md) and [task catalog](TASK_CATALOG.md): intervention, permitted workflow, realistic shortcuts, difficulty, and genuine missing-information cases.
8. [Artifact contracts](ARTIFACT_CONTRACTS.md): new source/data locations, trace/event schemas, scoring provenance, and immutable releases.
9. [Agent guide](AGENT_GUIDE.md), [work packages](WORK_PACKAGES.md), and [state](state.json): ownership, dependencies, handoffs, and the next unstarted work.

The [planning handoff](handoffs/2026-11-15-planning.md) records completed verification and the next safe action.

Recommended target before pilot measurements: 100 base scenarios, 16 matched conditions per seed, two seeds = **3,200 primary-actor episodes**. Judge calls are additional. A smaller 1,600-episode version preserves the controls if local capacity is limited. An optional second actor is conditional on measured capability, audit quality, and remaining compute. No main protocol or model lineup is frozen yet.

## Historical work stays in place

- [Original proposal](../proposal/project-proposal.tex)
- [Original research plan](../research-plan.md)
- [Frozen original main protocol](../main-protocol-v1.md)
- [Completed original report](../report/final-report.md)
- [Original final evaluation](../results/final-automated-evaluation.json)
- [Original reproducibility instructions](../report/README.md)

Those artifacts are evidence, not a backlog for this extension. Historical instructions such as “main collection disabled” apply to their original runbooks. The extension must have its own protocol, source namespace, artifacts, and status. Existing ignored raw evidence and model/runtime links must not be deleted or relocated as cleanup.

The [preservation manifest](preservation-manifest.json) records historical tracked project files at commit `3f17534` and the original V2 snapshot. `project/README.md` is excluded solely to allow a navigation link; scientific artifacts are included.

## Hard constraints

- RTX 3070 Ti, 8 GB VRAM, as the only experiment machine.
- Zero external-compute budget: no paid GPU, hosted inference, hosted judge, or remote generation, even with free credits. Public documentation and free checkpoint downloads are not remote inference.
- Course report due **December 4, 2026**, Toronto time. The date is confirmed in the [course README](../../README.md); 11:59pm follows the general written-work policy. Presentation arrangements and final formatting instructions remain unresolved.
- Automated evaluation; no mandatory human-labeling dependency. Semantic limitations must remain visible.
- Future orchestrators execute the work; this planning pass does not start experiments.

Latest explicit user instructions take precedence. Within this extension, the decision record supersedes conflicting planning suggestions in V2; a future frozen protocol controls a named run and cannot be retroactively changed.
