# Package handoff — WP03/WP06 exact prompt counting, November 15, 2026

- Owner: `native_adapter` worker.
- Status: ready_for_review; 23 CPU fixture tests pass, live equivalence unmeasured by this worker.
- Input commit: `cf742c0` (reviewed native/audit integration).
- Output commit: uncommitted; root owns integration.
- Changed paths: `src/shortcut_study/adapters/token_counter.py`, `tests/test_token_counter.py`, this handoff.

`LlamaCppTokenCounter(base_url, expected_props=..., evidence_sink=...)` is callable for the native actor adapter. `count(payload, timeout_seconds=...)` can lower its configured total deadline to the remaining episode budget. The sink receives JSON-serializable request, raw response, final count and error records. No count is returned without successful evidence writes. Raw byte bodies use base64; the final count includes request, rendered-prompt, token-array and server-identity hashes. `last_evidence` is cleared before each attempt.

The counter checks the pinned server identity before and after template application/tokenization. Identity includes alias/path/build, default and optional tool-use template hashes, special-token strings, text-only modalities and context/default-settings hash. Mutable property updates must be disabled. The operator separately verifies executable/checkpoint files and owns the GPU lease; `/props` is not file attestation.

Only local IP-literal origins and three fixed routes are reachable: GET `/props`, POST `/apply-template`, POST `/tokenize`. The complete chat payload—including tools, thinking settings and all native history—reaches template application unchanged. Media input arrays are rejected before transport. The returned text prompt is tokenized with `add_special=true`, `parse_special=true`, `with_pieces=false`. Every socket operation shares a total deadline; byte caps, partial-body preservation, strict JSON checks, no redirects/proxies/retries and fail-closed errors mirror the native transport profile.

Source verification used the official immutable [server routes](https://github.com/ggml-org/llama.cpp/blob/8bb3cf0d2/tools/server/server-context.cpp) and [tokenization helpers](https://github.com/ggml-org/llama.cpp/blob/8bb3cf0d2/tools/server/server-common.cpp). At this revision, chat and template application share `oaicompat_chat_params_parse`; text completion passes both special-token flags as true to the same tokenizer used by `/tokenize`. Only nonempty string template output is supported by this profile.

The actual rendered prompt must contain each nonempty prior native reasoning and tool-result text in order. Their hashes/positions and retained segment counts are recorded. This conservative substring check detects omission/reordering; it does not prove semantic use or exact tool-result role placement. Templates that reformat those strings fail closed until separately qualified. No generated summaries, manual reasoning reinsertion or history eviction occur.

Historical assistant actions receive an additional Qwen-specific check: each closed assistant frame must retain its native reasoning prefix and ordered tool calls, with function names and strict JSON arguments semantically identical to the native history. JSON whitespace/key ordering may change; missing, changed or extra calls fail closed. A JSON decoder determines argument boundaries, including strings containing closing-tag text. Tool-call examples inside reasoning cannot satisfy this action check. The exact layout was verified by reading the protected `project/runs/pilot-v1-preflight.json` template (UTF-8 SHA256 `57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361`); that historical file was not modified. Other role layouts are unsupported and fail closed. This check demonstrates rendered retention, not model attention or semantic use.

Validation:

- `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -p test_token_counter.py -q` — 23 tests passed using mocked HTTP/socket objects and controlled endpoint bodies.
- `git diff --check` — passed before handoff.
- Source SHA256: `e55fa315d4b408dfe391dc4c17ea5f3f8c2e72eb437b39c4772994f8e02f5b82`.
- Test SHA256: `8a8a16a97254ab6d383dca587e8afeca46fc949714f97cfc364334a45f6d93eb`.

No servers, inference, GPU jobs, downloads or Git mutations were run by this worker. The orchestrator must independently review these changes, then verify counts against actual `usage.prompt_tokens` on every live turn using the owned, pinned server. Memory/runtime/model capability and full WP03/WP06 acceptance remain pending. There are no worker-owned experiment IDs or GPU processes.

- Next safe action: independent review followed by the root-owned local qualification run.
- Acceptance reviewer/decision/date: pending.
