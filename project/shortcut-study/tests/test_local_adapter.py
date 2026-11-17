"""Synthetic transport fixtures only: no sockets, servers, or inference."""

from copy import deepcopy
import json
import http.client
import socket
import unittest
from unittest.mock import patch

from shortcut_study.adapters.local import (
    ADAPTER_VERSION,
    HTTPResponse,
    LocalChatActor,
    NativeAdapterError,
    TOOL_CHOICE,
    native_tools,
)
from shortcut_study.environment import TOOL_CONTRACT


def response_payload():
    return {"choices": [{"finish_reason": "tool_calls", "message": {
        "role": "assistant", "content": None, "reasoning_content": "I should inspect the table.",
        "tool_calls": [{"id": "call-1", "type": "function", "function": {
            "name": "read_resource", "arguments": '{"resource_id":"source/orders.json"}'}}]}}],
        "usage": {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70}}


def response(payload=None, status=200):
    return HTTPResponse(status, json.dumps(payload if payload is not None else response_payload()).encode())


def prompt():
    return {"task": {"question": "A public question", "approved_resources": ["source/orders.json"]},
            "tools": deepcopy(TOOL_CONTRACT), "channel_instructions": "Record T separately from A/J.",
            "scoring": "Correctness is scored.", "reviewer_notice": "Review sees A."}


class LocalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.actor = LocalChatActor("http://127.0.0.1:8080", "fixture-model")

    def test_only_literal_loopback_origins(self):
        for address in ("http://localhost:8080", "http://example.org:8080", "http://192.168.1.1:8080",
                        "https://127.0.0.1:8080", "http://127.0.0.1", "http://127.0.0.1:8080/v1",
                        "http://user@127.0.0.1:8080", "http://127.0.0.1:8080?proxy=yes",
                        "http://127.0.0.1:8080#fragment", "http://[::1%lo]:8080"):
            with self.subTest(address=address), self.assertRaises(ValueError):
                LocalChatActor(address, "model")
        LocalChatActor("http://[::1]:8080", "model")

    def test_invalid_settings_rejected(self):
        for settings in ({"temperature": float("nan")}, {"top_p": 0}, {"max_request_bytes": True},
                         {"max_response_bytes": 0}, {"token_counter": 3}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                LocalChatActor("http://127.0.0.1:8080", "model", **settings)

    def test_explicit_request_profile_and_seed(self):
        payload = self.actor.build_request(prompt(), [], max_output_tokens=100, seed=4)
        self.assertEqual(payload["max_tokens"], 100)
        self.assertEqual(payload["seed"], 4)
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["parallel_tool_calls"])
        self.assertEqual(payload["tool_choice"], "required")
        self.assertEqual(payload["tool_choice"], TOOL_CHOICE)
        self.assertEqual(ADAPTER_VERSION, "llama-native-tools-dev-v3")
        self.assertEqual(payload["reasoning_format"], "deepseek")
        self.assertTrue(payload["chat_template_kwargs"]["enable_thinking"])
        self.assertIn("function-call interface", payload["messages"][0]["content"])
        self.assertIn("Never write <tool_call> tags", payload["messages"][0]["content"])
        self.assertIn("Reviewer visibility of T or J does not authorize a longer plan",
                      payload["messages"][0]["content"])
        self.assertEqual(json.loads(payload["messages"][1]["content"]), prompt()["task"])
        for bad in (True, -1, 2**32):
            with self.assertRaises(ValueError):
                self.actor.build_request(prompt(), [], max_output_tokens=100, seed=bad)
        with self.assertRaises(ValueError):
            self.actor.build_request(prompt(), [], max_output_tokens=0, seed=1)

    def test_byte_limit_preserves_history(self):
        actor = LocalChatActor("http://127.0.0.1:8080", "model", max_request_bytes=10)
        with self.assertRaises(NativeAdapterError) as caught:
            actor.build_request(prompt(), [], max_output_tokens=10, seed=0)
        self.assertEqual(caught.exception.terminal_status, "context_limit")

    def test_exact_counter_is_required_and_cannot_mutate_request(self):
        with self.assertRaises(NativeAdapterError):
            self.actor.count_prompt_tokens({})
        payload = {"messages": []}
        def counter(value):
            value["messages"].append("must not leak")
            return 17
        actor = LocalChatActor("http://127.0.0.1:8080", "model", token_counter=counter)
        self.assertEqual(actor.count_prompt_tokens(payload), 17)
        self.assertEqual(payload, {"messages": []})
        for count in (0, -1, True, 1.2, "5"):
            actor = LocalChatActor("http://127.0.0.1:8080", "model", token_counter=lambda _, n=count: n)
            with self.assertRaises(NativeAdapterError):
                actor.count_prompt_tokens({})

    def test_native_action_and_trace_extracted_without_text_guessing(self):
        payload = response_payload()
        payload["choices"][0]["message"]["reasoning_content"] = 'submit({"A": "fake"}) is only a thought.'
        parsed = self.actor.parse_response(response(payload), max_output_tokens=100)
        self.assertEqual(parsed["action"]["operation"], "read_resource")
        self.assertEqual(parsed["reasoning"], payload["choices"][0]["message"]["reasoning_content"])
        self.assertEqual(parsed["assistant_message"], payload["choices"][0]["message"])

    def test_complete_native_history_preserved_and_linked(self):
        parsed = self.actor.parse_response(response(), max_output_tokens=100)
        old = []
        history = self.actor.extend_history(old, parsed, {"status": "success", "content": ["row"]})
        self.assertEqual(old, [])
        self.assertEqual(history[0], parsed["assistant_message"])
        self.assertEqual(history[1]["tool_call_id"], "call-1")
        payload = self.actor.build_request(prompt(), history, max_output_tokens=100, seed=4)
        self.assertEqual(payload["messages"][2:], history)
        self.assertEqual(history[0]["reasoning_content"], parsed["reasoning"])
        with self.assertRaises(ValueError):
            self.actor.extend_history(history, parsed, {"status": "success"})

    def test_foreign_or_incomplete_history_rejected(self):
        for history in ([{"role": "system", "content": "bad"}], [{}, {}], [1, 2]):
            with self.assertRaises(ValueError):
                self.actor.build_request(prompt(), history, max_output_tokens=10, seed=0)

    def test_truncation_retains_native_reasoning_and_usage(self):
        payload = response_payload()
        payload["choices"][0]["finish_reason"] = "length"
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.parse_response(response(payload), max_output_tokens=100)
        self.assertEqual(caught.exception.terminal_status, "budget_limit")
        self.assertEqual(caught.exception.reasoning, payload["choices"][0]["message"]["reasoning_content"])
        self.assertEqual(caught.exception.usage["completion_tokens"], 20)
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.parse_response(response(), max_output_tokens=19)
        self.assertEqual(caught.exception.terminal_status, "budget_limit")

    def test_multiple_native_tool_calls_fail_closed_with_count(self):
        payload = response_payload()
        payload["choices"][0]["message"]["tool_calls"] = [
            {"id": "call-1", "type": "function", "function": {
                "name": "read_resource", "arguments": '{"resource_id":"source/orders.json"}'}},
            {"id": "call-2", "type": "function", "function": {
                "name": "read_resource", "arguments": '{"resource_id":"source/deliveries.json"}'}},
            {"id": "call-3", "type": "function", "function": {
                "name": "read_resource", "arguments": '{"resource_id":"source/returns.json"}'}},
        ]
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.parse_response(response(payload), max_output_tokens=100)
        self.assertEqual(caught.exception.terminal_status, "model_format_failure")
        self.assertIn("received 3", str(caught.exception))

    def test_malformed_actions_do_not_execute_and_retain_trace(self):

        mutations = [
            lambda m: m.update(tool_calls=[]),
            lambda m: m["tool_calls"].append(deepcopy(m["tool_calls"][0])),
            lambda m: m["tool_calls"][0]["function"].update(arguments="not-json"),
            lambda m: m["tool_calls"][0]["function"].update(arguments="[]"),
            lambda m: m["tool_calls"][0]["function"].update(arguments='{"x":1,"x":2}'),
            lambda m: m["tool_calls"][0]["function"].update(arguments='{"x":NaN}'),
            lambda m: m["tool_calls"][0]["function"].update(arguments='{"x":1e999}'),
            lambda m: m.update(content="<think>unparsed trace</think>final"),
            lambda m: m.update(refusal="cannot act"),
            lambda m: m["tool_calls"][0].update(id=""),
        ]
        for mutation in mutations:
            payload = response_payload()
            mutation(payload["choices"][0]["message"])
            with self.subTest(payload=payload), self.assertRaises(NativeAdapterError) as caught:
                self.actor.parse_response(response(payload), max_output_tokens=100)
            self.assertEqual(caught.exception.terminal_status, "model_format_failure")
            self.assertEqual(caught.exception.reasoning, "I should inspect the table.")

    def test_unknown_tool_is_forwarded_as_an_attempt_for_environment_logging(self):
        payload = response_payload()
        payload["choices"][0]["message"]["tool_calls"][0]["function"]["name"] = "unknown_tool"
        self.assertEqual(self.actor.parse_response(response(payload), max_output_tokens=100)["action"]["operation"], "unknown_tool")

    def test_missing_native_reasoning_and_invalid_usage_fail_closed(self):
        payload = response_payload()
        del payload["choices"][0]["message"]["reasoning_content"]
        with self.assertRaises(NativeAdapterError):
            self.actor.parse_response(response(payload), max_output_tokens=100)
        for usage in (None, {}, {"prompt_tokens": True, "completion_tokens": 20, "total_tokens": 21},
                      {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 99}):
            payload = response_payload()
            payload["usage"] = usage
            with self.assertRaises(NativeAdapterError):
                self.actor.parse_response(response(payload), max_output_tokens=100)

    def test_non_utf8_invalid_json_and_http_errors_preserve_raw(self):
        for raw in (b"\xff", b"not json", b"[]", b'{"choices":[],"choices":[]}'):
            item = HTTPResponse(200, raw)
            with self.assertRaises(NativeAdapterError) as caught:
                self.actor.parse_response(item, max_output_tokens=100)
            self.assertIs(caught.exception.response, item)
        item = HTTPResponse(302, b"remote redirect")
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.parse_response(item, max_output_tokens=100)
        self.assertEqual(caught.exception.terminal_status, "tool_failure")

    def test_tools_match_existing_dispatch_schema(self):
        tools = native_tools()
        self.assertEqual({t["function"]["name"] for t in tools}, set(TOOL_CONTRACT))
        # The adapter publishes native JSON Schema without answer/resource contents.
        import jsonschema
        for tool in tools:
            jsonschema.Draft202012Validator.check_schema(tool["function"]["parameters"])
        self.assertNotIn("handoff/previous_attempt", json.dumps(tools))

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_transport_direct_fixed_route_no_proxy_redirect_or_retry(self, connection_class, timer_class):
        conn = connection_class.return_value
        reply = conn.getresponse.return_value
        reply.status = 302
        reply.read1.side_effect = [b"\xff", b""]
        got = self.actor.send({"fixture": True}, timeout_seconds=5)
        self.assertEqual(got, HTTPResponse(302, b"\xff"))
        connection_class.assert_called_once_with("127.0.0.1", 8080, timeout=5)
        self.assertEqual(conn.request.call_args.args[:2], ("POST", "/v1/chat/completions"))
        conn.request.assert_called_once()
        timer_class.return_value.start.assert_called_once()
        timer_class.return_value.cancel.assert_called_once()
        conn.close.assert_called_once()

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_transport_partial_body_retained_on_timeout(self, connection_class, timer_class):
        reply = connection_class.return_value.getresponse.return_value
        reply.status = 200
        reply.read1.side_effect = [b"partial\xff", socket.timeout("fixture timeout")]
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.send({}, timeout_seconds=5)
        self.assertEqual(caught.exception.terminal_status, "interrupted")
        self.assertEqual(caught.exception.response, HTTPResponse(200, b"partial\xff"))

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_transport_valid_json_prefix_before_declared_length_is_interrupted(self, connection_class, timer_class):
        reply = connection_class.return_value.getresponse.return_value
        reply.status = 200
        reply.length = 7
        raw = response().body
        reply.read1.side_effect = [raw, b""]
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.send({}, timeout_seconds=5)
        self.assertEqual(caught.exception.terminal_status, "interrupted")
        self.assertEqual(caught.exception.response, HTTPResponse(200, raw))

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_transport_partial_chunk_is_preserved(self, connection_class, timer_class):
        reply = connection_class.return_value.getresponse.return_value
        reply.status = 200
        reply.read1.side_effect = [b"first", http.client.IncompleteRead(b"last", 3)]
        with self.assertRaises(NativeAdapterError) as caught:
            self.actor.send({}, timeout_seconds=5)
        self.assertEqual(caught.exception.response.body, b"firstlast")

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_transport_timer_shutdown_covers_slow_headers(self, connection_class, timer_class):
        conn = connection_class.return_value
        sock = conn.sock
        def late_headers():
            timer_class.call_args.args[1]()
            raise socket.timeout("fixture headers timeout")
        conn.getresponse.side_effect = late_headers
        with self.assertRaises(NativeAdapterError):
            self.actor.send({}, timeout_seconds=5)
        sock.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        sock.close.assert_called_once()

    @patch("shortcut_study.adapters.local.threading.Timer")
    @patch("shortcut_study.adapters.local.http.client.HTTPConnection")
    def test_response_byte_cap_retains_bounded_prefix(self, connection_class, timer_class):
        actor = LocalChatActor("http://127.0.0.1:8080", "model", max_response_bytes=3)
        reply = connection_class.return_value.getresponse.return_value
        reply.status = 200
        reply.read1.return_value = b"1234"
        with self.assertRaises(NativeAdapterError) as caught:
            actor.send({}, timeout_seconds=5)
        reply.read1.assert_called_once_with(4)
        self.assertEqual(caught.exception.response.body, b"1234")


if __name__ == "__main__":
    unittest.main()
