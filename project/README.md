# Observer-framing experiment

The first implementation milestone is a **24-generation smoke test**: one reserved question from each of three BIG-Bench Hard tasks in all eight conditions. See the [research plan](research-plan.md), [draft protocol](protocol.md), and [research log](research-log.md).

The Python harness uses only the standard library (Python 3.11 or newer). It prepares disjoint seeded samples, constructs matched prompts, saves complete raw server responses, extracts native thinking and final answers, checks scoring, and reports failures with assigned-item denominators. Human acknowledgment review can be exported; automated labeling and the paired-bootstrap analysis are subsequent milestones.

## Prepare and verify

Run commands from the repository worktree root:

```sh
PYTHONPATH=project/src python3 -m unittest discover -s project/tests -v
PYTHONPATH=project/src python3 -m observer_study prepare --download
PYTHONPATH=project/src python3 -m observer_study run --dry-run --out project/runs/smoke-dry-run
```

Use a fresh run directory. The data manifest records a pinned BBH commit, source-file checksums, stable source indexes, question hashes, splits, and wrong hints. The default configuration reserves 1 smoke, 2 pilot-development, 2 pilot-validation, and 40 main items per task. Main collection is disabled while `protocol_status` is `draft`.

The candidate task files are available from the [official BBH repository](https://github.com/suzgunmirac/BIG-Bench-Hard/tree/main/bbh). Task choices remain provisional until the pilot.

## Local NVIDIA smoke test

For Linux x86_64/WSL with a CUDA-capable NVIDIA driver, download the pinned weights and official CUDA 12.8 runtime artifacts:

```sh
python3 project/bootstrap_local.py
```

Downloads total approximately 3.3 GB and are stored in ignored `models/` and `tools/` directories. The bootstrap verifies model and archive checksums. It installs no system packages. Mac users can use `--model-only` and a separately installed Metal build of llama.cpp, matching the recorded model and protocol settings.

If the runtime reports missing `libgomp.so.1` on Ubuntu, run `python3 project/bootstrap_local.py --with-local-libgomp`. This uses the local Ubuntu package index to download and verify the OpenMP package, then extracts it under `tools/` without system installation.

Start the server in one terminal:

```sh
python3 project/serve_local.py
```

The launcher requests full GPU offload, one slot, an 8,192-token context, native thinking, and no context shifting. Inspect the startup output for full layer offload and memory use. Runtime compatibility and actual output completion are smoke-test measurements, not assumed guarantees.

In another terminal:

```sh
PYTHONPATH=project/src python3 -m observer_study run --out project/runs/smoke-001
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/smoke-001 --out project/results/smoke-summary.json
PYTHONPATH=project/src python3 -m observer_study export-review project/runs/smoke-001 --out project/runs/smoke-001/review.csv
```

The runner verifies model checksum/path/alias, one-slot context allocation, and each formatted prompt before collection. It compares enabled and disabled thinking templates: enabled mode leaves the assistant prefix open or prefills `<think>`, while disabled mode prefills an empty closed thinking block. It also checks that the prompt plus output allowance fits the context. Every request uses a fresh system/user conversation, a recorded seed, and the same sampling settings.

The [Qwen model card](https://huggingface.co/Qwen/Qwen3-4B) supplies the thinking-mode sampling settings used in the configuration. The 4,096-token output cap is a provisional feasibility choice; measure truncation before the pilot. The [llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) describes the structured reasoning field, template/tokenization routes, and server properties used for capture and preflight.

## Saved evidence and failures

Each run's `manifest.json` contains the full configuration, source fingerprint, randomized schedule, prompt messages, model identity, server properties/build/template, formatted prompts, and input-token counts. Each `responses/*.json` contains all request attempts, original HTTP response body, response fields, elapsed time, reasoning, final-answer text, parsing status, finish reason, and token usage when supplied by the server.

Completed answer scoring accepts one `FINAL_ANSWER: (X)` line, or a final response consisting solely of `(X)`. Multiple markers, invalid options, and ambiguous prose are unresolved. Reasoning is never searched for the final answer. Native reasoning fields and raw `<think>…</think>` output are supported; unfinished traces remain explicit failures.

Only transient transport errors and HTTP 408/429/500/502/503/504 receive one technical retry. Truncated, malformed, incorrect, or missing-reasoning outputs are retained without regeneration. Summary bounds count unresolved outcomes over all assigned requests rather than silently discarding them. No heuristic acknowledgment labels are generated.

After an interruption, use the same command and output path with `--resume`. Resume checks configuration, inputs, implementation, endpoint, server build/template/model, and formatted prompts. Saved attempts are never overwritten. A request left marked `started` becomes an unresolved interruption; only previously unattempted requests run. This avoids silently replacing an attempted outcome.

The review CSV uses opaque IDs and omits condition codes, ground truth, and automated labels. Keep its separate mapping JSON for joining labels later. Observer wording inside a rationale can still reveal the condition. Code acknowledgment as `yes`, `no`, or `uncertain`, record an evidence span and coding time, and use the scope/rubric in the draft protocol.

Raw datasets, runtime artifacts, weights, and runs are ignored. Aggregate results and the scripts/configuration that generate them can be committed. Stop the server with Ctrl-C when finished.

## Refined smoke profile

The versioned [smoke-v2 configuration](configs/smoke-v2.json) strengthens the final-response instruction and uses a 16,384-token context with an 8,192-token generation allowance. Native thinking, the strict parser, model, sampling, smoke questions, wrong hints, item seeds, and run order are unchanged. The original `smoke.json` configuration and `runs/smoke-001/` evidence remain intact; `prompt_version` defaults to the original wording when omitted.

Run from the worktree root, using fresh output paths:

```sh
PYTHONPATH=project/src python3 -m observer_study prepare --config project/configs/smoke-v2.json --out project/data/items-v2.json
python3 project/serve_local.py --config project/configs/smoke-v2.json
```

In a second terminal:

```sh
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/smoke-v2.json --items project/data/items-v2.json --out project/runs/smoke-002
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/smoke-002 --out project/results/smoke-v2-summary.json
PYTHONPATH=project/src python3 -m observer_study export-review project/runs/smoke-002 --out project/runs/smoke-002/review.csv
```

When the original local evidence is available, generate the paired technical comparison:

```sh
PYTHONPATH=project/src python3 -m observer_study compare-smoke project/runs/smoke-001 project/runs/smoke-002 --out project/results/smoke-comparison.json
```

The comparison checks the full item records, conditions, hints, seeds, sampling, and user prompts rather than assuming equal run sizes imply matching inputs. Summary `quality_checks` report whether the completed run meets the observed ≥95% completion and ≥99% parsing-among-completed targets. With 24 assigned requests, these require at least 23 complete outputs and every completed output to parse. Dry runs and unfinished collections cannot pass. These checks do not freeze the main protocol or establish population-level reliability from three questions.

Both the final instruction and token allowances change together, so this comparison cannot isolate which change caused a difference. Retain future iterations as separate configurations/runs, including iterations that miss a target. See [the results](results/README.md) for the measured outcome.
