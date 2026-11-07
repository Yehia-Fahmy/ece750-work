# Pilot v1 runbook

Prepared October 29, 2026 from merged PR #5. Configuration: [`configs/pilot-v1.json`](configs/pilot-v1.json). The protocol remains **draft**; this preparation does not enable main collection.

## Prepared design

Pilot v1 changes only `protocol_version` from smoke v2. It retains Qwen3-4B Q4_K_M, native thinking, prompt v2, 16,384 context tokens, 8,192 output tokens, sampling, technical retries, and seed 0.

| Split | Questions per task | Total questions | Conditions | Requests |
| --- | ---: | ---: | ---: | ---: |
| `pilot_development` | 2 | 6 | 8 | 48 |
| `pilot_validation` | 2 | 6 | 8 | 48 |

Tasks are logical deduction with three objects, date understanding, and disambiguation QA. All 135 reserved items, including the three smoke and 120 main items, retain their original IDs, splits, hints, and source hashes. Pilot requests retain the original prompts, seeds, and split-specific execution order. Development and validation are disjoint from each other and from smoke/main.

Use development outputs to refine the acknowledgment rubric and any automated labeler. Freeze those choices before collecting/reviewing held-out validation. The researcher supplies human labels and evidence spans; preparation produces no labels or model answers.

## Local files in this checkout

Run commands from the repository root with Python 3.11 or newer.

| Path | Contents |
| --- | --- |
| `project/data/bbh/` | Copied pinned BBH source files and checksum manifest. |
| `project/data/items-pilot-v1.json` | Newly prepared manifest bound to the pilot configuration. |
| `project/models/` | Relative symlink to the existing research worktree's verified weights. |
| `project/tools/` | Relative symlink to the existing research worktree's runtime. |
| `project/runs/pilot-v1-development-dry-run/` | 48 scheduled requests, no responses. |
| `project/runs/pilot-v1-validation-dry-run/` | Separate 48 scheduled requests, no responses. |
| `project/runs/pilot-v1-preflight.json` | Local model/backend checks and formatted prompts, without generations. |
| `project/runs/pilot-v1-preflight-server.log` | GPU startup and preflight server log. |
| `project/runs/pilot-v1-gpu-startup.log` | Verbose startup evidence of all 37 layers offloaded to the GPU. |

Data, models, tools, and runs are ignored by Git. The model/runtime links target `.worktrees/research-project-plan/project/`; preserve that worktree while these links are used. Original smoke manifests/responses remain there unchanged. New collection uses this checkout's merged implementation and fresh output directories.

The preparation summary is [`results/pilot-v1-preparation.json`](results/pilot-v1-preparation.json). Model SHA-256 and size, both cached runtime archive checksums, item preservation, disjointness, schedules, and the draft main-collection guard were checked. Live preflight checks both pilot schedules against the actual runtime without calling the generation endpoint. Recheck GPU/server conditions when starting collection.

To regenerate the same manifest from the local cache:

```sh
PYTHONPATH=project/src python3 -m observer_study prepare --config project/configs/pilot-v1.json --out project/data/items-pilot-v1.json
```

To repeat a dry run, use a **new** output directory. Existing dry-run directories cannot be converted into live runs or resumed as live runs.

```sh
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/pilot-v1.json --items project/data/items-pilot-v1.json --split pilot_development --out project/runs/pilot-v1-development-dry-run-002 --dry-run
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/pilot-v1.json --items project/data/items-pilot-v1.json --split pilot_validation --out project/runs/pilot-v1-validation-dry-run-002 --dry-run
```

## Collect development first

In one terminal, start the local server:

```sh
LLAMA_ARG_LOG_VERBOSITY=4 python3 project/serve_local.py --config project/configs/pilot-v1.json
```

Check full GPU layer offload in startup output. The runner checks model identity, native thinking template, context allocation, and every formatted prompt before generating answers. In another terminal:

```sh
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/pilot-v1.json --items project/data/items-pilot-v1.json --split pilot_development --out project/runs/pilot-v1-development-001
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/pilot-v1-development-001 --out project/results/pilot-v1-development-001-summary.json
PYTHONPATH=project/src python3 -m observer_study export-review project/runs/pilot-v1-development-001 --out project/runs/pilot-v1-development-001/review.csv
```

Inspect the summary for unfinished requests and failures before interpreting it. Fill the review CSV using the [acknowledgment rubric](protocol.md#acknowledgment-rubric-for-pilot-development): `yes`, `no`, or `uncertain`, with evidence, review time, and notes. Preserve its adjacent mapping JSON. Condition text inside rationales limits blinding.

To continue an interrupted collection, repeat its exact `run` command with `--resume`. Keep code/configuration, endpoint, model, and runtime fixed. Resume preserves attempted outcomes and runs only previously unattempted requests; it does not replace failed or interrupted generations. A changed implementation requires a fresh run, with any additional collection and its rationale documented.

## Collect validation after development choices are fixed

Use the same server/configuration after recording the development rubric and labeler settings:

```sh
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/pilot-v1.json --items project/data/items-pilot-v1.json --split pilot_validation --out project/runs/pilot-v1-validation-001
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/pilot-v1-validation-001 --out project/results/pilot-v1-validation-001-summary.json
PYTHONPATH=project/src python3 -m observer_study export-review project/runs/pilot-v1-validation-001 --out project/runs/pilot-v1-validation-001/review.csv
```

Stop the server with Ctrl-C after collection. Keep validation human decisions separate from automated predictions. Label import/reliability analysis remains subsequent work; the existing summary intentionally leaves acknowledgment outcomes pending.

## Pilot decision

Report completion ≥95% and parsing among completed outputs ≥99% with actual counts, by task and condition as well as overall. For each 48-request split, those thresholds require at least 46 complete outputs and every completed output to parse. Retain unresolved outcomes over all assigned requests; no regeneration for formatting, correctness, truncation, or rationale content.

Also inspect no-hint task suitability, hint-response variation, acknowledgment class counts/reliability, coding time, runtime, and available resources. Six questions per split provide preliminary evidence and may be insufficient for rare-positive label validation. Record a full/reduced-scope decision before freezing the main protocol. See [the next-steps plan](next-steps.md) for the remaining analysis and reporting work.
