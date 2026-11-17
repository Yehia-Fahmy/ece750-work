"""No inference: controlled endpoint bodies and mocked HTTP/socket objects."""

import base64
from copy import deepcopy
import http.client as http_client
import json
import socket
import unittest
from unittest.mock import Mock, patch

from shortcut_study.adapters.local import HTTPResponse, NativeAdapterError
from shortcut_study.adapters.token_counter import LlamaCppTokenCounter, server_identity
from shortcut_study.hashing import sha256_json, sha256_text


def props():
    return {"model_alias": "qwen-fixture", "model_path": "/retained/model.gguf",
            "build_info": "b11574-8bb3cf0d2", "chat_template": "a native template é",
            "chat_template_tool_use": "a tool template", "bos_token": "", "eos_token": "<eos>",
            "modalities": {"vision": False, "audio": False, "video": False},
            "endpoint_props": False, "is_sleeping": False,
            "default_generation_settings": {"n_ctx": 16384, "params": {"temperature": .6}}}


def payload():
    return {"model": "qwen-fixture", "messages": [
        {"role": "system", "content": "Do the task."},
        {"role": "user", "content": "Question?"},
        {"role": "assistant", "content": None, "reasoning_content": "Prior native reasoning é.",
         "tool_calls": [{"id": "call_1", "type": "function", "function": {
             "name": "read_resource", "arguments": '{"resource_id":"table.json"}'}}]},
        {"role": "tool", "tool_call_id": "call_1", "content": '{"status":"success","content":[7]}'}],
        "tools": [{"type": "function", "function": {"name": "read_resource", "parameters": {
            "type": "object", "properties": {"resource_id": {"type": "string"}}}}}],
        "chat_template_kwargs": {"enable_thinking": True}, "reasoning_format": "deepseek",
        "tool_choice": "required", "parallel_tool_calls": False, "max_tokens": 12, "seed": 42}


def rendered():
    return ('<|im_start|>system\nDo the task.<|im_end|>\n<|im_start|>user\nQuestion?<|im_end|>\n'
            '<|im_start|>assistant\n<think>\nPrior native reasoning é.\n</think>\n\n'
            '<tool_call>\n{"name":"read_resource", "arguments":{"resource_id":"table.json"}}\n</tool_call><|im_end|>\n'
            '<|im_start|>user\n<tool_response>\n' + payload()["messages"][-1]["content"]
            + '\n</tool_response><|im_end|>\n<|im_start|>assistant\n')


def http(value, status=200):
    return HTTPResponse(status, json.dumps(value, ensure_ascii=False).encode())


class TokenCounterTests(unittest.TestCase):
    def setUp(self):
        self.records = []
        self.counter = LlamaCppTokenCounter("http://127.0.0.1:8080", expected_props=props(), evidence_sink=self.records.append)
        self.counter._transport = Mock(side_effect=[http(props()), http({"prompt": rendered()}),
                                                   http({"tokens": [151644, 1, 2, 151645]}), http(props())])

    def test_counts_exact_special_tokens_with_full_unchanged_template_request(self):
        request = payload()
        original = deepcopy(request)
        self.assertEqual(self.counter(request), 4)
        self.assertEqual(request, original)
        calls = self.counter._transport.call_args_list
        self.assertEqual([(c.args[0], c.args[1]) for c in calls], [
            ("GET", "/props"), ("POST", "/apply-template"), ("POST", "/tokenize"), ("GET", "/props")])
        self.assertEqual(json.loads(calls[1].args[2]), request)
        self.assertEqual(json.loads(calls[2].args[2]), {
            "content": rendered(), "add_special": True, "parse_special": True, "with_pieces": False})
        self.assertEqual(len({c.args[3] for c in calls}), 1, "all endpoints share one deadline")

    def test_durable_evidence_contains_exact_raw_responses_and_template_identity(self):
        self.counter(payload())
        self.assertEqual([r["phase"] for r in self.records], ["request", "response"] * 4 + ["count"])
        response = self.records[3]
        self.assertEqual(json.loads(base64.b64decode(response["body_base64"])), {"prompt": rendered()})
        final = self.counter.last_evidence
        self.assertEqual(final["prompt_tokens"], 4)
        self.assertEqual(final["identity"]["chat_template_sha256"], sha256_text(props()["chat_template"]))
        self.assertEqual(final["rendered_prompt_sha256"], sha256_text(rendered()))
        self.assertEqual(final["token_ids_sha256"], sha256_json([151644, 1, 2, 151645]))
        self.assertEqual(final["retained_reasoning_segments"], 1)
        self.assertEqual(final["retained_tool_results"], 1)
        self.assertEqual(final["retained_tool_calls"], 1)
        json.dumps(self.records, allow_nan=False)

    def test_request_must_be_saved_before_transport(self):
        def transport(method, path, body, deadline):
            self.assertEqual(self.records[-1]["phase"], "request")
            return http(props()) if path == "/props" else http(
                {"prompt": rendered()} if path == "/apply-template" else {"tokens": [1]})
        self.counter._transport.side_effect = transport
        self.assertEqual(self.counter(payload()), 1)

    def test_missing_or_reformatted_native_trace_fails_before_tokenize(self):
        for text in ("<assistant>No previous history.", rendered().replace("Prior native reasoning é.", "summarized trace")):
            with self.subTest(text=text):
                self.counter._transport.side_effect = [http(props()), http({"prompt": text})]
                with self.assertRaisesRegex(NativeAdapterError, "omitted or reordered reasoning"):
                    self.counter(payload())
                self.assertIsNone(self.counter.last_evidence)

    def test_missing_tool_result_or_reordered_history_rejected(self):
        for text in ("Prior native reasoning é.", payload()["messages"][-1]["content"] + "Prior native reasoning é."):
            self.counter._transport.side_effect = [http(props()), http({"prompt": text})]
            with self.assertRaisesRegex(NativeAdapterError, "tool_result"):
                self.counter(payload())

    def test_empty_trace_is_explicitly_counted_as_zero_retained_segments(self):
        request = payload()
        request["messages"][2]["reasoning_content"] = "  "
        self.counter._transport.side_effect = [http(props()), http({"prompt": rendered().replace(
            "Prior native reasoning é.", "  ")}), http({"tokens": [1]}), http(props())]
        self.counter(request)
        self.assertEqual(self.counter.last_evidence["retained_reasoning_segments"], 0)

    def test_missing_changed_or_extra_rendered_tool_calls_are_rejected(self):
        for text in (rendered().replace('"name":"read_resource"', '"name":"wrong"'),
                     rendered().replace('"resource_id":"table.json"', '"resource_id":"other.json"'),
                     rendered().replace('<tool_call>\n{"name":"read_resource", "arguments":{"resource_id":"table.json"}}\n</tool_call>', ''),
                     rendered().replace('</tool_call><|im_end|>', '</tool_call><tool_call>{}</tool_call><|im_end|>')):
            self.counter._transport.side_effect = [http(props()), http({"prompt": text})]
            with self.assertRaises(NativeAdapterError):
                self.counter(payload())

    def test_tool_examples_or_thought_mentions_cannot_replace_real_history(self):
        envelope = '<tool_call>\n{"name":"read_resource", "arguments":{"resource_id":"table.json"}}\n</tool_call>'
        request = payload()
        request["messages"][2]["reasoning_content"] += envelope
        text = rendered().replace("Prior native reasoning é.", request["messages"][2]["reasoning_content"])
        text = text.replace('\n</think>\n\n' + envelope, '\n</think>\n\n')
        self.counter._transport.side_effect = [http(props()), http({"prompt": text})]
        with self.assertRaisesRegex(NativeAdapterError, "omitted a native tool call"):
            self.counter(request)

    def test_tool_argument_json_reformatting_and_tag_strings_are_lossless(self):
        request = payload()
        request["messages"][2]["tool_calls"][0]["function"]["arguments"] = '{"second":2,"first":"</tool_call>"}'
        text = rendered().replace('{"resource_id":"table.json"}', '{ "first": "</tool_call>", "second": 2 }')
        self.counter._transport.side_effect = [http(props()), http({"prompt": text}), http({"tokens": [1]}), http(props())]
        self.assertEqual(self.counter(request), 1)
        self.assertEqual(self.counter.last_evidence["retained_tool_calls"], 1)

    def test_identity_changes_before_or_after_count_fail_closed(self):
        for stage in (0, 3):
            values = [http(props()), http({"prompt": rendered()}), http({"tokens": [1]}), http(props())]
            changed = props()
            changed["chat_template_tool_use"] += " changed"
            values[stage] = http(changed)
            self.counter._transport.side_effect = values
            with self.subTest(stage=stage), self.assertRaisesRegex(NativeAdapterError, "identity changed"):
                self.counter(payload())
            self.assertIsNone(self.counter.last_evidence)

    def test_identity_requires_pinned_runtime_and_text_only_immutable_props(self):
        for key, value in (("build_info", "b11575-8bb3cf0d2"), ("build_info", "b11574-other"),
                           ("modalities", {"vision": True, "audio": False, "video": False}),
                           ("endpoint_props", True), ("model_path", ""), ("chat_template", None),
                           ("default_generation_settings", {})):
            changed = props()
            changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                server_identity(changed)
        identity = self.counter.expected_identity
        identity["model_path"] = "altered"
        self.assertNotEqual(self.counter.expected_identity, identity)

    def test_count_refuses_media_and_alias_change_before_any_request(self):
        for mutate in (lambda p: p.update(model="other"),
                       lambda p: p["messages"][1].update(content=[{"type": "image_url", "image_url": {"url": "https://invalid.example/image"}}])):
            request = payload()
            mutate(request)
            with self.assertRaises(NativeAdapterError):
                self.counter(request)
        self.counter._transport.assert_not_called()

    def test_invalid_template_or_token_shapes_fail_closed(self):
        for value in (None, "", [1, 2]):
            self.counter._transport.side_effect = [http(props()), http({"prompt": value})]
            with self.assertRaises(NativeAdapterError):
                self.counter(payload())
        for value in (None, [], [True], [-1], [2**31], [1.0], [{"id": 1, "piece": "a"}]):
            self.counter._transport.side_effect = [http(props()), http({"prompt": rendered()}), http({"tokens": value})]
            with self.assertRaises(NativeAdapterError):
                self.counter(payload())

    def test_raw_failures_preserved_before_parsing_with_no_retry(self):
        for raw in (b"\xff", b"not-json", b'{"x":1e999}', b'{"tokens":[],"tokens":[1]}'):
            self.counter._transport.side_effect = [HTTPResponse(200, raw)]
            with self.assertRaises(NativeAdapterError):
                self.counter(payload())
            response = self.records[-2]
            self.assertEqual(response["phase"], "response")
            self.assertEqual(base64.b64decode(response["body_base64"]), raw)

    def test_partial_transport_body_is_archived(self):
        self.counter._transport.side_effect = NativeAdapterError(
            "context_limit", "test interrupted count", response=HTTPResponse(200, b"partial\xff"))
        with self.assertRaises(NativeAdapterError):
            self.counter(payload())
        self.assertFalse(self.records[-2]["complete"])
        self.assertEqual(base64.b64decode(self.records[-2]["body_base64"]), b"partial\xff")

    def test_no_evidence_sink_no_valid_origin_no_counter(self):
        with self.assertRaises(ValueError):
            LlamaCppTokenCounter("http://127.0.0.1:8080", expected_props=props(), evidence_sink=None)
        for origin in ("http://example.com:8080", "http://localhost:8080", "http://127.0.0.1:8080/v1"):
            with self.assertRaises(ValueError):
                LlamaCppTokenCounter(origin, expected_props=props(), evidence_sink=self.records.append)

    def test_durable_sink_failure_prevents_endpoint_call(self):
        def broken_sink(record):
            raise OSError("fixture disk failure")
        self.counter._sink = broken_sink
        with self.assertRaises(OSError):
            self.counter(payload())
        self.counter._transport.assert_not_called()

    def test_per_count_deadline_is_capped_and_invalid_deadline_rejected(self):
        with patch("shortcut_study.adapters.token_counter.time.monotonic", return_value=100):
            self.counter.count(payload(), timeout_seconds=2)
        self.assertEqual(self.counter._transport.call_args_list[0].args[3], 102)
        for seconds in (0, -1, True, float("inf")):
            with self.assertRaises(ValueError):
                self.counter.count(payload(), timeout_seconds=seconds)

    def test_counter_deadline_overrun_returns_no_count(self):
        with patch("shortcut_study.adapters.token_counter.time.monotonic", side_effect=[0, 11]):
            with self.assertRaisesRegex(NativeAdapterError, "total deadline"):
                self.counter(payload())
        self.assertIsNone(self.counter.last_evidence)

    def test_request_byte_limit_does_not_evict_history(self):
        self.counter.max_request_bytes = 1
        with self.assertRaisesRegex(NativeAdapterError, "request byte limit"):
            self.counter(payload())
        self.assertEqual(self.counter._transport.call_count, 1, "only /props was sent")

    @patch("shortcut_study.adapters.token_counter.threading.Timer")
    @patch("shortcut_study.adapters.token_counter.http.client.HTTPConnection")
    def test_real_transport_fixed_local_routes_with_deadline(self, connection_class, timer_class):
        counter = LlamaCppTokenCounter("http://127.0.0.1:8080", expected_props=props(), evidence_sink=self.records.append)
        conn = connection_class.return_value
        reply = conn.getresponse.return_value
        reply.status, reply.length = 200, 0
        reply.read1.side_effect = [b'{}', b'']
        with patch("shortcut_study.adapters.token_counter.time.monotonic", return_value=1):
            self.assertEqual(counter._transport("GET", "/props", None, 3), HTTPResponse(200, b'{}'))
        connection_class.assert_called_once_with("127.0.0.1", 8080, timeout=2)
        self.assertEqual(conn.request.call_args.args[:2], ("GET", "/props"))
        timer_class.assert_called_once()
        timer_class.return_value.cancel.assert_called_once()
        with self.assertRaises(ValueError):
            counter._transport("POST", "/v1/chat/completions", b'{}', 3)

    @patch("shortcut_study.adapters.token_counter.threading.Timer")
    @patch("shortcut_study.adapters.token_counter.http.client.HTTPConnection")
    def test_transport_rejects_truncated_body_even_when_json_prefix_valid(self, connection_class, timer_class):
        counter = LlamaCppTokenCounter("http://127.0.0.1:8080", expected_props=props(), evidence_sink=self.records.append)
        reply = connection_class.return_value.getresponse.return_value
        reply.status, reply.length = 200, 5
        reply.read1.side_effect = [b'{}', b'']
        with patch("shortcut_study.adapters.token_counter.time.monotonic", return_value=1):
            with self.assertRaises(NativeAdapterError) as caught:
                counter._transport("GET", "/props", None, 3)
        self.assertEqual(caught.exception.response.body, b'{}')

    @patch("shortcut_study.adapters.token_counter.threading.Timer")
    @patch("shortcut_study.adapters.token_counter.http.client.HTTPConnection")
    def test_transport_interrupts_headers_and_preserves_partial_chunks(self, connection_class, timer_class):
        counter = LlamaCppTokenCounter("http://127.0.0.1:8080", expected_props=props(), evidence_sink=self.records.append)
        conn = connection_class.return_value
        def late_headers():
            timer_class.call_args.args[1]()
            raise socket.timeout("fixture header timeout")
        conn.getresponse.side_effect = late_headers
        with patch("shortcut_study.adapters.token_counter.time.monotonic", return_value=1):
            with self.assertRaises(NativeAdapterError):
                counter._transport("GET", "/props", None, 3)
        conn.sock.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        conn.getresponse.side_effect = None
        reply = conn.getresponse.return_value
        reply.status = 200
        reply.read1.side_effect = [b"first", http_client.IncompleteRead(b"last", 2)]
        with patch("shortcut_study.adapters.token_counter.time.monotonic", return_value=1):
            with self.assertRaises(NativeAdapterError) as caught:
                counter._transport("GET", "/props", None, 3)
        self.assertEqual(caught.exception.response.body, b"firstlast")


if __name__ == "__main__":
    unittest.main()
