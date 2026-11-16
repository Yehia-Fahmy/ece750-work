# Package handoff — WP06 owned local server — November 15, 2026

- Owner: `review_cpu`, delegated lifecycle engineer; root is the sole GPU operator and integrator.
- Status: ready for review; CPU lifecycle implementation and read-only asset inspection only.
- Input commit: `cf742c02a7d72f0ac245046651d214d78395043e`.
- Output: uncommitted `src/shortcut_study/runtime/server.py`, `tests/test_local_server.py`, and this handoff. No shared schemas, existing runtime/model assets, or historical records changed.
- Dependencies read: extension AGENTS, README, DECISIONS, AGENT_GUIDE, COMPUTE, WORK_PACKAGES/WP06, and artifact/handoff instructions.

## API and behavior

`inspect_local_assets(checkout, *, model_path=None, server_path=None)` resolves retained assets, verifies the primary model against its historical SHA-256/size, hashes the executable and runtime shared libraries, and captures `--version`/`--help` without loading a model. It requires b11574/commit `8bb3cf0d2` and the launch profile's supported flags.

`LocalLlamaServer(lease, *, assets, directory, port=18080, alias="shortcut-qwen3-4b", startup_timeout=120)` is a context manager for the operator. It exposes `base_url`, `props`, `profile`, `manifest`, `process`, and `assert_ready()`. It validates this repository's canonical OS-held lease and rechecks file hashes before startup. It refuses an occupied port and verifies the new listening socket belongs to its owned PID through `/proc`, so a competing service cannot satisfy readiness.

Launch arguments pin loopback/CUDA0, 16,384 context tokens, one slot, full GPU layers, Jinja, thinking on, deepseek reasoning format, unrestricted reasoning budget, flash attention on, no context shift, fit off, offline operation, no web UI, no automatic warmup, and explicit sampling defaults. The environment removes inherited LLAMA_ARG/GGML/CUDA overrides and LD_PRELOAD, and pins library/Python paths. The server must report the requested model/context/slot count and startup logs must establish full GPU offload. Readiness uses only fixed GET routes with an absolute socket-shutdown deadline and rejects premature EOF even when the saved prefix is valid JSON.

Artifacts are `launch.json`, `process.json`, `server.log`, `props.json`, `ready.json`, and `stopped.json`. The native profile's `template_sha256` is SHA-256 of the exact UTF-8 tool-use template when nonempty, otherwise the base template; every native request contains tools. `ready.json` records the selected field plus both base and optional tool-template hashes. Full props remain available to the independently reviewed exact token counter, which binds both templates and runtime defaults.

Only the launched process is terminated. Graceful termination waits ten seconds, then SIGKILL waits another ten seconds; cleanup precedes release of the caller's lease. A separate Python child sets Linux `PR_SET_PDEATHSIG(SIGKILL)` before exec and detects an already-dead parent, avoiding a threaded-parent `preexec_fn`. The operator must nest this context inside the GPU lease and stop on uncertain generation; root owns that orchestration. No broad process-name killing, downloads, or external inference is implemented.

## Checks and observations

```sh
PYTHONPATH=project/shortcut-study/src:project/shortcut-study/tests python3 -m unittest test_local_server test_token_counter test_gpu_telemetry -q
```

44 tests passed: 15 server tests, 20 token-counter tests, and nine telemetry tests. Server coverage includes pinned arguments/assets, canonical lease, occupied-port rejection, PID/socket association using `/proc` fixtures, failed startup retention, wrong props/partial offload rejection, effective-template identity, owned cleanup escalation, sanitized environment, bounded readiness headers/incomplete-body rejection, and a real **CPU Python child** killed after its parent exits. No model/server inference occurred. An initial real-socket fixture encountered sandbox EPERM; it was replaced with deterministic `/proc` snapshots rather than requiring host-network permission.

Read-only `inspect_local_assets('.')` succeeded after supplying retained library directories. An initial bare `llama-server --help` failed because `libgomp.so.1` was not on the loader path; this motivated explicit preserved dependency paths. Inspection observed:

- Model resolved to `.worktrees/research-project-plan/project/models/Qwen3-4B-Q4_K_M.gguf`; 2,497,280,256 bytes; SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`, matching the historical pinned configuration.
- Runtime resolved to `.worktrees/research-project-plan/project/tools/runtime/llama-b11574/llama-server`.
- Version: `0.6.0-dev (build 11574, commit 8bb3cf0d2)`, GNU 13.3.0, Linux x86_64.
- 34 runtime executable/shared-library files hashed. Preserved llama, CUDA runtime, libgomp directories plus the fixed WSL driver directory supply library lookup.

This proves local asset integrity and inspected flags, not native tool compatibility, exact live token agreement, or measured GPU capacity.

## Artifact hashes and review

- `src/shortcut_study/runtime/server.py`: `9c774c85d9cf32c102d12e2950a213396a4181d1ed03a27f1d0e75f7d36f9c13`
- `tests/test_local_server.py`: `f6d2f41b989d29d1c7702d45bed406b6aa42362e8cf26527cd2fbad0777dc432`

Independent token-counter review found no merge blockers: fixed local non-generation routes, one absolute deadline, immutable props/template/runtime identity checks, complete template and special-token flags, evidence-before-return, and failure without estimated counts. Its twenty tests passed in the combined command above. Source/API semantics still require the root operator's actual server compatibility observation.

The counter agent reviewed lifecycle code and identified a readiness transport deadline/truncated-body gap; both were fixed with regression tests before live use. The audit reviewer checked lifecycle ownership/offload/environment boundaries and prompted explicit effective-tool-template provenance. This worker also reviewed telemetry source/tests: read-only fixed queries, durable readings/errors, identity checks, bounded teardown and clearly sampled maxima; no blocker found. Polling remains unable to establish true peak allocation.

GPU owner/process/job from this worker: none. No GPU server, model load, inference, or download was started. Next safe action: independent root/counter-agent review, then root freezes the source snapshot before owned local qualification. WP06 full capacity and qualification acceptance remain pending.
