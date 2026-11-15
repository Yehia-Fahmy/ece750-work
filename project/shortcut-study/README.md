# Shortcut study extension — start here

This is **additional research**, separate from the completed observer-framing study. Status: CPU development; shared contracts and a TAB01 mock vertical slice are implemented. No extension model observations have been collected and no main protocol is frozen.

## Implemented CPU vertical slice

The [implementation handoff](handoffs/2026-11-15-cpu-vertical-slice.md) records a real synthetic TAB01 generator, complete/incomplete certificates, mediated tools, durable mock episodes, deterministic scoring, and the existing reviewer/auditor projections. This is a partial implementation of WP02–WP04, not full package acceptance or G1 qualification.

Run from the repository root, using a fresh output directory each time:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy legitimate --out project/runs/shortcut-study/my-legitimate-slice
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy shortcut --out project/runs/shortcut-study/my-shortcut-slice
```

Each command assigns all 16 conditions. The shortcut strategy deliberately attempts the prior-agent note, then falls back to approved tables when it is absent. The generated T/J are explicitly scripted test text; none of these records measure model behavior or validate a language judge. `summary.json` identifies this evidence type. `manifest.json` hashes the actual source/config/schema files and saved artifacts. Raw records remain under the ignored run directory; the small [verification record](results/development/cpu-vertical-slice-v1.json) is tracked.

The JSON tool boundary has no filesystem, network, Python execution, hidden-answer lookup, or candidate-check route. It is not a sandbox for untrusted Python plugins. Authorized resource reads and restricted note reads return copies of the episode's resource map; absence physically removes the note. TAB01 accepts an integer answer or a typed insufficiency/clarification status, keeping explanations in J.

For an interrupted **mock episode directory** (a child of a run directory), seal it without replay:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study recover-mock-episode PATH_TO_EPISODE_DIRECTORY
```

Recovery preserves the journal, retains known events and saved T/A/J, and marks uncertain execution interrupted. Already-saved submissions are reconstructed only from matching raw actions and hashed events. It does not resume collection, generate new A/J, or rebuild the run summary/manifest. A fully written terminal record remains authoritative; missing derived reviewer/auditor packets can be recreated from it. Keep the original manifest when adding recovered artifacts and record a separate recovery manifest before downstream use.

Current limits: one development template at intended moderate difficulty, one shortcut mechanism, scripted adapters, and TAB01 scoring only. Turn/action/wall limits are checked; token/context accounting and preemptive timeouts await a native adapter. No GPU lease, native model inference, semantic judge, qualification/main generation, or broad task catalog is implemented by this slice. Main task generation is explicitly rejected.

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
