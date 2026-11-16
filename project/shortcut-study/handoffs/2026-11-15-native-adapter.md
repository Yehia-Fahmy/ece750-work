# Package handoff — WP03 native local adapter, November 15, 2026

- Owner and role: `native_adapter` worker, local model adapter implementation.
- Status: ready_for_review; CPU fixture validation only.
- Input commit and dependencies: `fc18d65`, merged CPU vertical slice; existing TOOL_CONTRACT and episode status vocabulary.
- Output commit: uncommitted worker changes; integrator owns integration and Git operations.
- Paths changed: `src/shortcut_study/adapters/local.py`, `tests/test_local_adapter.py`, and this handoff. No shared schema changes.

Implemented `LocalChatActor` with request construction, explicit seed/sampling profile, native tool schemas for the existing TAB01 environment, native `reasoning_content` capture, exactly one executable tool call, and exact assistant/tool history linkage. Tool names mentioned in reasoning never execute. Nonempty free final content, missing native reasoning fields, malformed/duplicate JSON keys, nonfinite values, ambiguous multiple calls, invalid usage and output truncation fail explicitly. Parse failures retain captured native reasoning and known usage. Unknown native operation names remain attempts for the environment to log and reject.

The transport accepts only numeric loopback HTTP origins with explicit ports. It uses a fixed chat route without proxies, redirects, DNS lookup of hostnames, or retries. A total deadline closes the captured socket even during slow header/body reads. Byte limits bound request and response storage; incomplete declared bodies and partial chunks remain uncertain interrupted outcomes with received bytes retained. The caller must durably archive requests before sending and raw byte responses before parsing, including error responses.

The adapter requires an injected exact template-aware prompt token counter. An absent or invalid counter fails closed before inference when the runner uses the preflight API. No tokenizer approximation is presented as exact. Request construction does not evict history or manually splice reasoning into content; the native assistant message, including its reasoning field, is returned to the server unchanged. How a particular model template treats that field remains a qualification requirement.

Commands and actual outcomes:

- `PYTHONPATH=project/shortcut-study/src python3 -m unittest discover -s project/shortcut-study/tests -p test_local_adapter.py -q` — 20 tests passed. Fixtures replace HTTP connections, sockets and deadline timers; no server was started and no network inference occurred.
- `git diff --check` — passed before handoff.
- `sha256sum project/shortcut-study/src/shortcut_study/adapters/local.py project/shortcut-study/tests/test_local_adapter.py` — source `431ed0ceb96dc6bdbee6f48a0fac5517f139f3d13cbf360ea50361bc0d797a70`; tests `9e30d33504dc097a429999bc3d49c447546df2fafd353292ac6a46d848930d41`.

Documentation evidence: the retained b11574 directory contains runtime binaries rather than server source/documentation. The official [b11574 server README](https://github.com/ggml-org/llama.cpp/blob/b11574/tools/server/README.md) documents native reasoning, usage, template application and tokenization. This establishes API intent, not checkpoint compatibility or exact template/token counter equivalence. No runtime/model was modified or loaded.

Limitations: this is a development adapter profile, not WP03 acceptance or G1 qualification. Exact tokenization, template behavior over multiple turns, server/model provenance, GPU ownership, runtime request compatibility and actual native tool/trace generation remain unmeasured. The caller owns total episode budgets, durable archives and preservation of failed operations. HTTP errors are conservatively technical failures; transport uncertainty is interrupted and never automatically retried. No main-run entry point is supplied here.

- GPU lease owner/process/job: none; no GPU work or server processes.
- Terminal/incomplete/unattempted experiment IDs: none; synthetic unit tests only.
- Next safe action: integrate the development runner, independently review error/archive paths, and qualify an exact local template/token counter before any authorized local model collection.
- Acceptance reviewer/decision/date: pending integrator review.
