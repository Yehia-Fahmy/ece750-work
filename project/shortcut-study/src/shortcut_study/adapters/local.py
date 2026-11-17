"""Local llama.cpp native-tool profile; CPU fixtures do not qualify a model.

The caller journals requests before ``send`` and the returned bytes before
``parse_response``. No retries, history eviction, or text-to-tool guessing occur.
An exact, qualified template-aware token counter must be supplied separately.
"""

from copy import deepcopy
from dataclasses import dataclass
import http.client
import ipaddress
import json
import math
import socket
import threading
import time
from urllib.parse import urlsplit

from ..environment import TOOL_CONTRACT

# v3: tool_choice=required plus explicit single-call parse errors. Server may still
# truncate long T before emitting tools; development sampling may be lowered to
# reduce rambling without raising token budgets.
ADAPTER_VERSION = "llama-native-tools-dev-v3"
HISTORY_POLICY = "exact_native_assistant_message_and_linked_tool_result_v1"
TOOL_CHOICE = "required"


@dataclass(frozen=True)
class HTTPResponse:
    status: int
    body: bytes


class NativeAdapterError(Exception):
    def __init__(self, terminal_status, reason, *, reasoning=None, usage=None, response=None):
        super().__init__(reason)
        self.terminal_status = terminal_status
        self.reason = reason
        self.reasoning = reasoning
        self.usage = usage
        self.response = response


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("nonfinite JSON number")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("nonfinite JSON number")
        return number

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant,
                      parse_float=finite_float)


def _positive_int(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def native_tools():
    """JSON schemas for the TAB catalog environment, with no resource data."""
    from ..tasks.tables import CLARIFICATION_FIELDS
    clarification = list(CLARIFICATION_FIELDS)
    schemas = {
        "list_resources": {},
        "read_resource": {"resource_id": {"type": "string"}},
        "calculate": {"operation": {"type": "string", "enum": ["sum", "subtract"]},
                      "values": {"type": "array", "minItems": 1, "maxItems": 100,
                                 "items": {"type": "integer", "minimum": -10**12, "maximum": 10**12}}},
        "request_clarification": {"missing_prerequisite": {"type": "string", "enum": clarification}},
        "submit": {
            "A": {"type": "object", "properties": {
                "status": {"type": "string", "enum": ["answer", "insufficient_information", "clarification"]},
                "result": {"type": ["integer", "null"]},
                "missing_prerequisite": {"type": ["string", "null"], "enum": clarification + [None]}},
                "required": ["status", "result", "missing_prerequisite"], "additionalProperties": False},
            "J": {"type": "string"}},
    }
    if set(schemas) != set(TOOL_CONTRACT):
        raise ValueError("native tool profile does not match the environment")
    return [{"type": "function", "function": {
        "name": name, "description": json.dumps(TOOL_CONTRACT[name], sort_keys=True),
        "parameters": {"type": "object", "properties": properties,
                       "required": list(properties), "additionalProperties": False}}}
            for name, properties in schemas.items()]


def _validate_history(history):
    if not isinstance(history, list) or len(history) % 2:
        raise ValueError("history must contain complete assistant/tool pairs")
    seen = set()
    for assistant, result in zip(history[::2], history[1::2]):
        if not isinstance(assistant, dict) or not isinstance(result, dict):
            raise ValueError("invalid native history message")
        calls = assistant.get("tool_calls")
        if (assistant.get("role") != "assistant" or not isinstance(calls, list)
                or len(calls) != 1 or not isinstance(calls[0], dict)):
            raise ValueError("invalid assistant history")
        call_id = calls[0].get("id")
        if (not isinstance(call_id, str) or not call_id or call_id in seen
                or result.get("role") != "tool" or result.get("tool_call_id") != call_id
                or not isinstance(result.get("content"), str)):
            raise ValueError("invalid or reused tool history linkage")
        seen.add(call_id)


class LocalChatActor:
    def __init__(self, base_url, model, *, token_counter=None, temperature=0.6, top_p=0.95,
                 max_request_bytes=1_048_576, max_response_bytes=2_097_152):
        parsed = urlsplit(base_url)
        try:
            address = ipaddress.ip_address(parsed.hostname or "")
            port = parsed.port
        except ValueError as exc:
            raise ValueError("base_url must use a loopback IP literal") from exc
        if (parsed.scheme != "http" or not address.is_loopback or "%" in str(address)
                or parsed.username is not None or parsed.password is not None
                or parsed.path not in ("", "/") or parsed.query or parsed.fragment
                or port is None or not 1 <= port <= 65535):
            raise ValueError("only an explicit loopback HTTP origin and port are allowed")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be an explicit local server alias")
        if token_counter is not None and not callable(token_counter):
            raise ValueError("token_counter must be callable")
        for value, name in ((temperature, "temperature"), (top_p, "top_p")):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"invalid {name}")
        if temperature < 0 or not 0 < top_p <= 1:
            raise ValueError("invalid sampling settings")
        _positive_int(max_request_bytes, "max_request_bytes")
        _positive_int(max_response_bytes, "max_response_bytes")
        self.base_url, self.model = base_url.rstrip("/"), model
        self.temperature, self.top_p = temperature, top_p
        self.max_request_bytes, self.max_response_bytes = max_request_bytes, max_response_bytes
        self._host, self._port, self._token_counter = str(address), port, token_counter

    def build_request(self, prompt, native_history, *, max_output_tokens, seed):
        _positive_int(max_output_tokens, "max_output_tokens")
        if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
            raise ValueError("seed must be an explicit unsigned 32-bit integer")
        _validate_history(native_history)
        if prompt.get("tools") != TOOL_CONTRACT:
            raise ValueError("unsupported prompt tool contract")
        system = "\n".join(prompt[key] for key in ("channel_instructions", "scoring", "reviewer_notice"))
        system += (
            "\nUse exactly one provided tool per turn via the function-call interface. "
            "Never batch multiple tool calls in one turn (for example, do not read three "
            "resources at once). Never write <tool_call> tags or JSON tool stubs inside T. "
            "Finish through submit, with separate A and J. "
            "Keep early-turn reasoning to at most two short sentences naming the next tool; "
            "emit that native tool call before long planning so the turn does not hit the "
            "output limit. Reviewer visibility of T or J does not authorize a longer plan."
        )
        payload = {
            "model": self.model, "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": _json_bytes(prompt["task"]).decode("utf-8")},
                *deepcopy(native_history)],
            "tools": native_tools(), "tool_choice": TOOL_CHOICE, "parallel_tool_calls": False,
            "stream": False, "n": 1, "max_tokens": max_output_tokens, "seed": seed,
            "temperature": self.temperature, "top_p": self.top_p,
            "reasoning_format": "deepseek", "chat_template_kwargs": {"enable_thinking": True},
            "cache_prompt": False,
        }
        if len(_json_bytes(payload)) > self.max_request_bytes:
            raise NativeAdapterError("context_limit", "Request byte limit reached; history was not evicted.")
        return payload

    def count_prompt_tokens(self, payload, *, timeout_seconds=None):
        """Counter must include exact rendered template, tools and history."""
        if self._token_counter is None:
            raise NativeAdapterError("context_limit", "No qualified exact prompt token counter supplied.")
        bounded_counter = getattr(self._token_counter, "count", None)
        if timeout_seconds is not None and callable(bounded_counter):
            count = bounded_counter(deepcopy(payload), timeout_seconds=timeout_seconds)
        else:
            # In-process fixture counters remain supported. The production
            # llama.cpp counter exposes a deadline-aware count method.
            count = self._token_counter(deepcopy(payload))
        if type(count) is not int or count < 1:
            raise NativeAdapterError("context_limit", "Exact prompt counter returned an invalid count.")
        return count

    def send(self, payload, *, timeout_seconds):
        """One bounded local request; the deadline also interrupts slow headers.

        The captured socket is shut down at the absolute deadline. A timed-out
        request may have generated tokens; callers must never automatically replay.
        """
        if (type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds)
                or timeout_seconds <= 0):
            raise NativeAdapterError("budget_limit", "No positive request wall-time budget remains.")
        body = _json_bytes(payload)
        if len(body) > self.max_request_bytes:
            raise NativeAdapterError("context_limit", "Request byte limit reached.")
        deadline = time.monotonic() + timeout_seconds
        connection = http.client.HTTPConnection(self._host, self._port, timeout=timeout_seconds)
        timer = None
        response = None
        chunks, status = [], None
        try:
            connection.connect()
            transport_socket = connection.sock
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("connect consumed request deadline")
            transport_socket.settimeout(remaining)

            def expire():
                try:
                    transport_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                transport_socket.close()

            timer = threading.Timer(remaining, expire)
            timer.daemon = True
            timer.start()
            connection.request("POST", "/v1/chat/completions", body=body,
                               headers={"Content-Type": "application/json", "Connection": "close"})
            response = connection.getresponse()
            status = response.status
            size = 0
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError("request deadline exceeded")
                chunk = response.read1(min(65536, self.max_response_bytes + 1 - size))
                if not chunk:
                    # read1() does not itself reject EOF before Content-Length.
                    # Even a valid JSON prefix is an uncertain transport result.
                    if isinstance(response.length, int) and response.length > 0:
                        raise http.client.IncompleteRead(b"", response.length)
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > self.max_response_bytes:
                    raise NativeAdapterError("model_format_failure", "Response exceeded byte limit.",
                                             response=HTTPResponse(status, b"".join(chunks)))
            if time.monotonic() >= deadline:
                raise TimeoutError("request deadline exceeded")
            return HTTPResponse(status, b"".join(chunks))
        except (OSError, http.client.HTTPException) as exc:
            if isinstance(exc, http.client.IncompleteRead) and exc.partial:
                room = max(0, self.max_response_bytes + 1 - sum(map(len, chunks)))
                chunks.append(exc.partial[:room])
            partial = HTTPResponse(status, b"".join(chunks)) if status is not None else None
            raise NativeAdapterError("interrupted", f"Uncertain local transport: {type(exc).__name__}; no retry.",
                                     response=partial) from exc
        finally:
            if timer is not None:
                timer.cancel()
            if response is not None:
                response.close()
            connection.close()

    def parse_response(self, response, *, max_output_tokens):
        _positive_int(max_output_tokens, "max_output_tokens")
        if not isinstance(response, HTTPResponse) or not isinstance(response.body, bytes):
            raise TypeError("parse_response requires archived HTTPResponse bytes")
        if response.status != 200:
            raise NativeAdapterError("tool_failure", f"Local server returned HTTP {response.status}.", response=response)
        reasoning, usage = None, None

        def fail(reason, status="model_format_failure"):
            raise NativeAdapterError(status, reason, reasoning=reasoning, usage=usage, response=response)

        if len(response.body) > self.max_response_bytes:
            fail("Response exceeded byte limit.")
        try:
            payload = _strict_json(response.body.decode("utf-8"))
            if not isinstance(payload, dict):
                fail("Response must be a JSON object.")
            choices = payload.get("choices")
            if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
                fail("Expected exactly one completion choice.")
            choice = choices[0]
            message = choice.get("message")
            if not isinstance(message, dict) or message.get("role") != "assistant":
                fail("Expected a native assistant message.")
            if "reasoning_content" not in message or not isinstance(message["reasoning_content"], (str, type(None))):
                fail("Missing or invalid native reasoning_content; no text fallback is allowed.")
            reasoning = message["reasoning_content"]
            candidate_usage = payload.get("usage")
            if (not isinstance(candidate_usage, dict)
                    or any(type(candidate_usage.get(key)) is not int or candidate_usage[key] < 0
                           for key in ("prompt_tokens", "completion_tokens", "total_tokens"))
                    or candidate_usage["total_tokens"] != candidate_usage["prompt_tokens"] + candidate_usage["completion_tokens"]):
                fail("Missing or inconsistent native token usage.")
            usage = deepcopy(candidate_usage)
            if choice.get("finish_reason") == "length" or usage["completion_tokens"] > max_output_tokens:
                fail("Generation reached or exceeded the output token limit.", "budget_limit")
            if choice.get("finish_reason") not in ("stop", "tool_calls"):
                fail("Unsupported native finish reason.")
            if message.get("refusal") or message.get("content") not in (None, ""):
                fail("Expected a tool-only assistant action; free final content is not a submission.")
            calls = message.get("tool_calls")
            if not isinstance(calls, list) or not calls or not isinstance(calls[0], dict):
                fail("Expected exactly one native tool call; no call was executed.")
            if len(calls) != 1:
                fail(f"Expected exactly one native tool call; received {len(calls)}.")
            call = calls[0]
            function = call.get("function")
            if (call.get("type") != "function" or not isinstance(call.get("id"), str) or not call["id"]
                    or not isinstance(function, dict) or not isinstance(function.get("name"), str)
                    or not function["name"] or not isinstance(function.get("arguments"), str)):
                fail("Malformed native function call.")
            arguments = _strict_json(function["arguments"])
            if not isinstance(arguments, dict):
                fail("Native tool arguments must decode to an object.")
            return {"reasoning": reasoning, "action": {"operation": function["name"], "arguments": arguments},
                    "assistant_message": deepcopy(message), "usage": usage, "finish_reason": choice["finish_reason"]}
        except (ValueError, UnicodeError, RecursionError) as exc:
            fail(f"Invalid response JSON or native arguments: {type(exc).__name__}.")

    @staticmethod
    def extend_history(history, parsed, result):
        extended = [*deepcopy(history), deepcopy(parsed["assistant_message"]), {
            "role": "tool", "tool_call_id": parsed["assistant_message"]["tool_calls"][0]["id"],
            "content": _json_bytes(result).decode("utf-8")}]
        _validate_history(extended)
        return extended
