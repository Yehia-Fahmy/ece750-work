# Shortcut study extension — start here

This is **additional research**, separate from the completed observer-framing study. Status: the local native runtime is validated; `tab01-slice-v5` capability probe on the RTX host **passed** both complete and incomplete V00 cells (fresh probe on main after #10). Prior failed v3 probe evidence is preserved; no main protocol is frozen. See the [qualification handoff](handoffs/2026-11-15-local-qualification.md), [v5 capability probe handoff](handoffs/2026-11-15-capability-probe-tab01-v5.md), and [v5 evidence](results/qualification/capability-probe-tab01-v5.json).

## Native adapter and audit development

The CPU slice was independently reviewed, corrected for interruption evidence loss, and merged locally at `fc18d65`. The [next-stage handoff](handoffs/2026-11-15-native-audit-integration.md) records the subsequent multi-agent implementation and review.

- `adapters/local.py` accepts native `reasoning_content` and one native function call per turn. It uses a fixed loopback HTTP endpoint, preserves raw bytes, refuses redirects/proxies/retries, and bounds request time and response size. It never extracts executable calls from T or free-form final text.
- `runner/native.py` records exact requests, native HTTP bodies, parsed T, tools, and A/J; checks cumulative token, context, action, turn and wall budgets; and recovers saved evidence without replay. Reused tool IDs are rejected before execution. Only development assignments are supported.
- `runtime/` provides an OS-held lock shared across Git worktrees, owner/heartbeat metadata, process-exit release, and a read-only RTX 3070 Ti identity check. The native runner requires this repository's canonical lock.
- `audit/` prepares complete A/T/J/events and verified tool results, materializes original evidence, checks coverage, keeps invalid judgments uncertain, samples all flagged plus a seeded stratified 10% of unflagged records, and preserves independent disagreement. Chunk planning is implemented; chunk-judge equivalence is unqualified.

Prepare an audit request from a **completed episode directory**, without invoking a judge:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study prepare-audit --episode PATH_TO_EPISODE_DIRECTORY --out NEW_OUTPUT_DIRECTORY
```

This writes `prepared.json`, `messages.json`, and a hash manifest. Rejected/incomplete episode IDs must remain in the assigned audit denominator. The prepared request excludes direct actor/condition identifiers; actor text may still reveal its condition. Evidence checking proves reference and coverage integrity, not the truth of a semantic judgment. Without generator sufficiency context, some insufficiency-explanation judgments must remain uncertain.

The original native integration tests use synthetic HTTP bodies, a test GPU probe, and fixture token counts. The new local qualification command owns the retained Qwen3-4B/b11574 server, hashes its assets, verifies the listening process and full GPU offload, and counts the actual rendered chat template through the pinned runtime. Caller-supplied profiles alone remain declarations; use the owned qualification path for measured runtime evidence. Native development permits zero transport retries; uncertain requests are never replayed. Full WP03/WP05/WP06 and G1 acceptance remain pending.

Run the fixed 16-condition **local model development slice** from the repository root, in an environment with access to the RTX 3070 Ti:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local --out project/runs/shortcut-study/NEW_RUN --port 18080
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local --capability-probe --out project/runs/shortcut-study/NEW_CAPABILITY_PROBE --port 18080
```

These commands perform real local GPU inference. They require a fresh output directory, acquire the canonical GPU lease, use only the preserved local checkpoint/runtime, and stop their own server before releasing the lease. The server is offline, bound to loopback, fully offloaded, and configured for one 16k context slot with no history clipping. They preserve the assigned schedule, requests, responses, exact count evidence, native T/tool/A/J, scoring, recovery checks, audit inputs, and sampled GPU memory. They create no semantic judgments and do not collect main-study data. Incomplete records remain in the assigned denominator. Read `summary.json` and `manifest.json`; a successful development check does not qualify the judge, broad task capability, or full study budget. The CLI returns failure when capture checks or the sampled 512 MiB memory-headroom check fail. `--capability-probe` runs only the two existing vertical-slice cells (complete + incomplete, V00, shortcut absent) and requires authorized reads then correct answer on the complete cell plus inspect-then-abstain on the incomplete cell.

## Measured development result

The corrected generator (`tab01-slice-v2`, source commit `60aa979`) completed all 16 development episodes with 32 exact token-count matches and verified native history/recovery/audit inputs. Mean episode latency was 8.07 seconds; sampled peak GPU usage was 5,278 MiB, leaving 2,914 MiB sampled headroom. These short episodes do not establish long-task or whole-study throughput.

**Development capability on TAB01 is now probe-gated:** early v2/v3 16-cell runs clarified without reading (0/8 complete). `tab01-slice-v3` removed public `clarification_fields` and required inspect-before-abstain; the v3 RTX probe (merged in #10) still failed incomplete abstention. `tab01-slice-v5` adds no-partial-answer cues on the catalog package ports; a fresh RTX probe on main passed both cells. Prior archives remain preserved. Semantic judging and held-out G2 remain unqualified. See [v5 probe evidence](results/qualification/capability-probe-tab01-v5.json) and [local-native-v1](results/qualification/local-native-v1.json).

## Implemented CPU vertical slice

The [implementation handoff](handoffs/2026-11-15-cpu-vertical-slice.md) records a real synthetic TAB01 generator, complete/incomplete certificates, mediated tools, durable mock episodes, deterministic scoring, and the existing reviewer/auditor projections. This is a partial implementation of WP02–WP04, not full package acceptance or G1 qualification.

Run from the repository root, using a fresh output directory each time:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -q
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy legitimate --out project/runs/shortcut-study/my-legitimate-slice
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-slice --strategy shortcut --out project/runs/shortcut-study/my-shortcut-slice
```

Each command assigns all 16 conditions. The shortcut strategy deliberately attempts the prior-agent note, then falls back to approved tables when it is absent. The generated T/J are explicitly scripted test text; none of these records measure model behavior or validate a language judge. `summary.json` identifies this evidence type. `manifest.json` hashes the actual source/config/schema files and saved artifacts. Raw records remain under the ignored run directory; the small [verification record](results/development/cpu-vertical-slice-v1.json) is tracked.

WP07 analysis scaffolding (CPU, synthetic only) recovers known injected visibility effects and refuses missing archives. It does not invent frozen main results; scientific contrasts remain TBD until closed scored archives exist. See [ANALYSIS_PROTOCOL.md](ANALYSIS_PROTOCOL.md).

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study analyze-dry --effect T_only --replicates 200 --out /tmp/shortcut-wp07-dry
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study analyze --scored PATH --schedule PATH --out PATH
```

The JSON tool boundary has no filesystem, network, Python execution, hidden-answer lookup, or candidate-check route. It is not a sandbox for untrusted Python plugins. Authorized resource reads and restricted note reads return copies of the episode's resource map; absence physically removes the note. TAB01 accepts an integer answer or a typed insufficiency/clarification status, keeping explanations in J.

For an interrupted **mock episode directory** (a child of a run directory), seal it without replay:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study recover-mock-episode PATH_TO_EPISODE_DIRECTORY
```

Recovery preserves the journal, retains known events and saved T/A/J, and marks uncertain execution interrupted. Already-saved submissions are reconstructed only from matching raw actions and hashed events. It does not resume collection, generate new A/J, or rebuild the run summary/manifest. A fully written terminal record remains authoritative; missing derived reviewer/auditor packets can be recreated from it. Keep the original manifest when adding recovered artifacts and record a separate recovery manifest before downstream use.

The TAB development catalog now covers TAB01–05 × four intended difficulties (20 bases / 320 matched cells) with scripted mocks; see [catalog expansion handoff](handoffs/2026-11-16-tab-catalog-expansion.md) and [verification record](results/development/tab-catalog-expansion-v1.json). Difficulties are uncalibrated; only prior-agent notes are implemented; DOC/PLAN/CODE/VERIFY remain pending. Run a fresh catalog mock directory with:

```sh
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study mock-tab-catalog --strategy legitimate --out project/runs/shortcut-study/my-tab-catalog-legitimate
```

The original mock runner checks turn/action/wall limits; the separate native development loop adds token/context checks and bounded transport. Authentic local development inference has now run. Semantic judge qualification, held-out capability/main generation, and non-TAB families remain pending. Main task generation is explicitly rejected.

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
