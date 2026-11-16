"""Exact text-chat preflight for the retained llama.cpp b11574 server.

Only /props, /apply-template, and /tokenize are reachable. The latter two
follow the same template and tokenizer path as text chat completion in commit
8bb3cf0d2, using add_special=True and parse_special=True. No inference occurs.
Server ownership/checkpoint hashing remain the operator's responsibility.
"""

import base64
from copy import deepcopy
import http.client
import json
import math
import re
import socket
import threading
import time

from .local import HTTPResponse, LocalChatActor, NativeAdapterError, _json_bytes, _strict_json
from ..hashing import sha256_bytes, sha256_json, sha256_text

COUNTER_VERSION = "llama-b11574-template-counter-v1"
SOURCE_REVISION = "8bb3cf0d2"
SOURCE_URLS = [
    f"https://github.com/ggml-org/llama.cpp/blob/{SOURCE_REVISION}/tools/server/server-context.cpp",
    f"https://github.com/ggml-org/llama.cpp/blob/{SOURCE_REVISION}/tools/server/server-common.cpp",
]
_ROUTES = {("GET", "/props"), ("POST", "/apply-template"), ("POST", "/tokenize")}


def server_identity(props):
    """Bind the pinned text-only model/template identity reported by /props.

    This is an integrity identity, not remote attestation or a checkpoint hash.
    The owner must separately verify the loaded files and executable.
    """
    if not isinstance(props, dict):
        raise ValueError("server properties must be an object")
    for key in ("model_alias", "model_path", "build_info", "chat_template"):
        if not isinstance(props.get(key), str) or not props[key].strip():
            raise ValueError(f"missing server identity field: {key}")
    if (not re.search(r"(?<!\d)11574(?!\d)", props["build_info"])
            or SOURCE_REVISION not in props["build_info"]):
        raise ValueError("counter supports only verified llama.cpp b11574 / 8bb3cf0d2")
    modalities = props.get("modalities")
    if (not isinstance(modalities, dict)
            or any(modalities.get(key) is not False for key in ("vision", "audio", "video"))):
        raise ValueError("counter supports only a text-only server")
    if props.get("endpoint_props") is not False:
        raise ValueError("mutable server properties must be disabled")
    for key in ("bos_token", "eos_token"):
        if not isinstance(props.get(key), str):
            raise ValueError(f"missing special-token identity: {key}")
    tool_template = props.get("chat_template_tool_use")
    if tool_template is not None and not isinstance(tool_template, str):
        raise ValueError("invalid tool-use template")
    defaults = props.get("default_generation_settings")
    if (not isinstance(defaults, dict) or type(defaults.get("n_ctx")) is not int
            or defaults["n_ctx"] < 1 or not isinstance(defaults.get("params"), dict)):
        raise ValueError("missing server context/default settings")
    # Reject non-JSON values before hashing operator-supplied properties.
    _json_bytes(defaults)
    return {
        "model_alias": props["model_alias"], "model_path": props["model_path"],
        "build_info": props["build_info"],
        "chat_template_sha256": sha256_text(props["chat_template"]),
        "chat_template_tool_use_sha256": sha256_text(tool_template) if tool_template is not None else None,
        "bos_token": props["bos_token"], "eos_token": props["eos_token"],
        "modalities": deepcopy(modalities), "endpoint_props": False,
        "default_generation_settings_sha256": sha256_json(defaults),
        "context_tokens": defaults["n_ctx"],
    }


def _positive_seconds(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError("timeout_seconds must be positive and finite")
    return value


def _retained_history(payload, rendered):
    """Check nonempty native T/tool text occurs in order in the actual prompt.

    This is a conservative substring check. A template that reformats or drops
    these fields must be separately qualified; it is never silently accepted.
    """
    cursor, traces, results = 0, 0, 0
    spans = []
    for number, message in enumerate(payload["messages"]):
        kind, text = None, None
        if message.get("role") == "assistant" and message.get("reasoning_content"):
            kind, text = "reasoning", message["reasoning_content"].strip()
        elif message.get("role") == "tool" and message.get("content"):
            kind, text = "tool_result", message["content"].strip()
        if not text:
            continue
        start = rendered.find(text, cursor)
        if start < 0:
            raise NativeAdapterError("context_limit", f"Rendered prompt omitted or reordered {kind} history at message {number}.")
        cursor = start + len(text)
        traces += kind == "reasoning"
        results += kind == "tool_result"
        spans.append({"message_index": number, "kind": kind, "text_sha256": sha256_text(text),
                      "text_start": start, "text_end": cursor})
    return {"retained_reasoning_segments": traces, "retained_tool_results": results,
            "history_spans": spans, "check": "ordered_nonempty_text_substrings"}


def _retained_tool_calls(payload, rendered):
    """Check Qwen's rendered assistant frames, excluding tools examples and T.

    The retained Qwen3 template emits one closed assistant frame per historical
    assistant message and JSON name/arguments envelopes within tool_call tags.
    JSON is decoded before looking for the closing tag, so tag-like strings in
    argument values cannot truncate a call. Other layouts fail closed.
    """
    assistants = [m for m in payload["messages"] if m["role"] == "assistant"]
    frames = list(re.finditer(r"<\|im_start\|>assistant\n(.*?)<\|im_end\|>", rendered, re.DOTALL))
    if len(frames) != len(assistants):
        raise NativeAdapterError("context_limit", "Rendered Qwen assistant history frame count differs from native history.")
    checked = []
    for number, (message, frame) in enumerate(zip(assistants, frames)):
        body = frame.group(1)
        reasoning = message.get("reasoning_content") or ""
        if reasoning:
            prefix = "<think>\n" + reasoning.strip("\n") + "\n</think>\n\n"
            if not body.startswith(prefix):
                raise NativeAdapterError("context_limit", "Rendered Qwen frame does not preserve its native reasoning prefix.")
            body = body[len(prefix):]
        if message.get("content") not in (None, ""):
            raise NativeAdapterError("context_limit", "Tool-history check supports only native tool-only assistant actions.")
        calls = message.get("tool_calls")
        if not isinstance(calls, list) or not calls:
            raise NativeAdapterError("context_limit", "Historical assistant has no native tool calls.")
        for call in calls:
            if (not isinstance(call, dict) or not isinstance(call.get("function"), dict)
                    or not isinstance(call["function"].get("name"), str)
                    or not isinstance(call["function"].get("arguments"), str)):
                raise NativeAdapterError("context_limit", "Invalid native tool-call history.")
            function = call["function"]
            expected = {"name": function["name"], "arguments": _strict_json(function["arguments"])}
            body = body.lstrip()
            if not body.startswith("<tool_call>"):
                raise NativeAdapterError("context_limit", "Rendered Qwen history omitted a native tool call.")
            body = body[len("<tool_call>"):].lstrip()
            _, end = json.JSONDecoder().raw_decode(body)
            actual = _strict_json(body[:end])
            if sha256_json(actual) != sha256_json(expected):
                raise NativeAdapterError("context_limit", "Rendered Qwen history changed native tool name or arguments.")
            body = body[end:].lstrip()
            if not body.startswith("</tool_call>"):
                raise NativeAdapterError("context_limit", "Rendered Qwen tool call lacks its closing tag.")
            body = body[len("</tool_call>"):]
            checked.append({"assistant_index": number, "function": function["name"],
                            "arguments_sha256": sha256_json(expected["arguments"]),
                            "frame_text_start": frame.start(), "frame_text_end": frame.end()})
        if body.strip():
            raise NativeAdapterError("context_limit", "Rendered Qwen frame contains unmatched tool action content.")
    return {"retained_tool_calls": len(checked), "tool_call_checks": checked,
            "tool_call_check": "qwen_assistant_frame_strict_json_arguments_v1"}


class LlamaCppTokenCounter:
    def __init__(self, base_url, *, expected_props, evidence_sink, timeout_seconds=10,
                 max_request_bytes=1_048_576, max_response_bytes=2_097_152):
        self._identity = server_identity(deepcopy(expected_props))
        if not callable(evidence_sink):
            raise ValueError("a durable evidence_sink(record) callback is required")
        origin = LocalChatActor(base_url, self._identity["model_alias"],
                                max_request_bytes=max_request_bytes, max_response_bytes=max_response_bytes)
        self.base_url = origin.base_url
        self._host, self._port = origin._host, origin._port
        self.max_request_bytes, self.max_response_bytes = max_request_bytes, max_response_bytes
        self.timeout_seconds = _positive_seconds(timeout_seconds)
        self._sink = evidence_sink
        self._call_index = 0
        self._lock = threading.Lock()
        self.last_evidence = None

    @property
    def expected_identity(self):
        return deepcopy(self._identity)

    def _record(self, call_index, phase, **fields):
        self._sink({"schema_version": "shortcut-token-counter-evidence-v1",
                    "counter_version": COUNTER_VERSION, "call_index": call_index,
                    "phase": phase, **deepcopy(fields)})

    def _transport(self, method, path, body, deadline):
        """Bound all socket operations by the count's single absolute deadline."""
        if (method, path) not in _ROUTES:
            raise ValueError("counter endpoint is not read-only")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise NativeAdapterError("context_limit", "Token-counter deadline expired before request.")
        connection = http.client.HTTPConnection(self._host, self._port, timeout=remaining)
        response, timer, status = None, None, None
        chunks, size = [], 0
        try:
            connection.connect()
            sock = connection.sock
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("counter connect deadline")
            sock.settimeout(remaining)

            def expire():
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()

            timer = threading.Timer(remaining, expire)
            timer.daemon = True
            timer.start()
            connection.request(method, path, body=body,
                               headers={"Content-Type": "application/json", "Connection": "close"})
            response = connection.getresponse()
            status = response.status
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError("counter response deadline")
                chunk = response.read1(min(65536, self.max_response_bytes + 1 - size))
                if not chunk:
                    if isinstance(response.length, int) and response.length > 0:
                        raise http.client.IncompleteRead(b"", response.length)
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > self.max_response_bytes:
                    raise NativeAdapterError("context_limit", "Counter response byte limit reached.",
                                             response=HTTPResponse(status, b"".join(chunks)))
            if time.monotonic() >= deadline:
                raise TimeoutError("counter response deadline")
            return HTTPResponse(status, b"".join(chunks))
        except (OSError, http.client.HTTPException) as exc:
            if isinstance(exc, http.client.IncompleteRead) and exc.partial:
                room = max(0, self.max_response_bytes + 1 - size)
                chunks.append(exc.partial[:room])
            partial = HTTPResponse(status, b"".join(chunks)) if status is not None else None
            raise NativeAdapterError("context_limit", f"Token-counter transport failed: {type(exc).__name__}; no retry.",
                                     response=partial) from exc
        finally:
            if timer is not None:
                timer.cancel()
            if response is not None:
                response.close()
            connection.close()

    def _request(self, call_index, request_index, method, path, payload, deadline):
        body = _json_bytes(payload) if payload is not None else None
        if body is not None and len(body) > self.max_request_bytes:
            raise NativeAdapterError("context_limit", "Counter request byte limit reached.")
        self._record(call_index, "request", request_index=request_index, method=method, path=path,
                     payload=payload, body_sha256=sha256_bytes(body or b""),
                     body_base64=base64.b64encode(body or b"").decode("ascii"))
        try:
            response = self._transport(method, path, body, deadline)
        except NativeAdapterError as exc:
            response = exc.response
            if response is not None:
                self._record(call_index, "response", request_index=request_index,
                             status=response.status, complete=False,
                             body_base64=base64.b64encode(response.body).decode("ascii"),
                             body_sha256=sha256_bytes(response.body))
            raise
        self._record(call_index, "response", request_index=request_index,
                     status=response.status, complete=True,
                     body_base64=base64.b64encode(response.body).decode("ascii"),
                     body_sha256=sha256_bytes(response.body))
        if response.status != 200 or len(response.body) > self.max_response_bytes:
            raise NativeAdapterError("context_limit", f"Counter endpoint {path} returned invalid HTTP response.", response=response)
        try:
            parsed = _strict_json(response.body.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise NativeAdapterError("context_limit", f"Counter endpoint {path} returned invalid JSON.", response=response) from exc
        if not isinstance(parsed, dict):
            raise NativeAdapterError("context_limit", f"Counter endpoint {path} must return an object.", response=response)
        return parsed

    def __call__(self, payload):
        return self.count(payload)

    def count(self, payload, *, timeout_seconds=None):
        """Return exact token count only after recording all successful evidence.

        A caller may lower the configured deadline to its remaining episode
        wall budget. Counter failures never fall back to estimated token counts.
        """
        timeout = self.timeout_seconds if timeout_seconds is None else min(
            self.timeout_seconds, _positive_seconds(timeout_seconds))
        if not self._lock.acquire(blocking=False):
            raise NativeAdapterError("context_limit", "Concurrent token counting is not supported.")
        self.last_evidence = None
        self._call_index += 1
        call_index = self._call_index
        deadline = time.monotonic() + timeout
        try:
            payload = deepcopy(payload)
            if not isinstance(payload, dict) or payload.get("model") != self._identity["model_alias"]:
                raise NativeAdapterError("context_limit", "Chat model alias does not match pinned counter identity.")
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                raise NativeAdapterError("context_limit", "Counter requires nonempty text chat messages.")
            for message in messages:
                if (not isinstance(message, dict) or message.get("role") not in ("system", "user", "assistant", "tool")
                        or not isinstance(message.get("content"), (str, type(None)))
                        or not isinstance(message.get("reasoning_content"), (str, type(None)))):
                    raise NativeAdapterError("context_limit", "Only native text messages are supported; media fetching is forbidden.")
            before = self._request(call_index, 1, "GET", "/props", None, deadline)
            if server_identity(before) != self._identity:
                raise NativeAdapterError("context_limit", "Server identity changed before token counting.")
            rendered = self._request(call_index, 2, "POST", "/apply-template", payload, deadline).get("prompt")
            if not isinstance(rendered, str) or not rendered:
                raise NativeAdapterError("context_limit", "Pinned text profile requires a nonempty rendered prompt string.")
            retention = _retained_history(payload, rendered)
            retention.update(_retained_tool_calls(payload, rendered))
            token_request = {"content": rendered, "add_special": True, "parse_special": True, "with_pieces": False}
            tokens = self._request(call_index, 3, "POST", "/tokenize", token_request, deadline).get("tokens")
            if (not isinstance(tokens, list) or not tokens
                    or any(type(token) is not int or not 0 <= token <= 2**31 - 1 for token in tokens)):
                raise NativeAdapterError("context_limit", "Tokenizer must return a nonempty integer token-ID array.")
            after = self._request(call_index, 4, "GET", "/props", None, deadline)
            if server_identity(after) != self._identity:
                raise NativeAdapterError("context_limit", "Server identity changed during token counting.")
            evidence = {"identity": deepcopy(self._identity), "identity_sha256": sha256_json(self._identity),
                        "request_sha256": sha256_json(payload), "rendered_prompt_sha256": sha256_text(rendered),
                        "token_ids_sha256": sha256_json(tokens), "prompt_tokens": len(tokens),
                        "add_special": True, "parse_special": True, "source_revision": SOURCE_REVISION,
                        **retention}
            if time.monotonic() >= deadline:
                raise NativeAdapterError("context_limit", "Token-counter total deadline expired.")
            self._record(call_index, "count", **evidence)
            if time.monotonic() >= deadline:
                raise NativeAdapterError("context_limit", "Token-counter evidence exceeded total deadline.")
            self.last_evidence = deepcopy(evidence)
            return len(tokens)
        except (NativeAdapterError, ValueError, TypeError, RecursionError) as exc:
            error = exc if isinstance(exc, NativeAdapterError) else NativeAdapterError(
                "context_limit", f"Invalid token-count evidence: {type(exc).__name__}.")
            self._record(call_index, "error", reason=error.reason, terminal_status=error.terminal_status)
            raise error from (None if error is exc else exc)
        finally:
            self._lock.release()
