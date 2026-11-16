"""Native protocol integration with synthetic HTTP bodies, never inference."""

import base64
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from shortcut_study.adapters.local import HTTPResponse, LocalChatActor, NativeAdapterError
from shortcut_study.adapters.mock import MockActor
from shortcut_study.__main__ import prepare_archive
from shortcut_study.hashing import sha256_json
from shortcut_study.runtime import GpuLease
import shortcut_study.runner.native as native
from shortcut_study.scoring import score_episode
from shortcut_study.tasks.tables import generate_task
from shortcut_study.vertical_slice import enumerate_vertical_slice_assignments

PROFILE = {"checkpoint_revision": "fixture-not-model", "checkpoint_sha256": "1" * 64,
           "quantization": "fixture", "runtime_revision": "fixture-not-runtime", "template_sha256": "2" * 64}


class SyntheticActor(LocalChatActor):
    """The scripted strategy emits the wire shape expected from a native server."""
    def __init__(self, strategy="legitimate", **kwargs):
        super().__init__("http://127.0.0.1:18080", "synthetic-native", token_counter=lambda p: 100, **kwargs)
        self.strategy = strategy
        self.requests = []

    def send(self, payload, *, timeout_seconds):
        self.requests.append(deepcopy(payload))
        history = []
        messages = payload["messages"][2:]
        for assistant, tool in zip(messages[::2], messages[1::2]):
            call = assistant["tool_calls"][0]["function"]
            history.append({"action": {"operation": call["name"], "arguments": json.loads(call["arguments"])},
                            "result": json.loads(tool["content"])})
        scripted = MockActor(self.strategy).respond({"history": history})
        action = scripted["action"]
        response = {"choices": [{"finish_reason": "tool_calls", "message": {
            "role": "assistant", "content": None, "reasoning_content": "Synthetic native-format trace; no inference.",
            "tool_calls": [{"id": f"call-{len(history) + 1}", "type": "function", "function": {
                "name": action["operation"], "arguments": json.dumps(action["arguments"])}}]}}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}}
        return HTTPResponse(200, json.dumps(response).encode())


class NativeRunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lease = GpuLease(self.root, owner="test", job="synthetic", run_id="test")
        self.lease.__enter__()
        self.addCleanup(self.lease.__exit__, None, None, None)
        probe = patch.object(native, "assert_supported_gpu", return_value={"gpu_name": "synthetic-probe-not-hardware"})
        probe.start()
        self.addCleanup(probe.stop)
        canonical = patch.object(native, "canonical_experiment_checkout", return_value=self.root)
        canonical.start()
        self.addCleanup(canonical.stop)
        self.assignments = enumerate_vertical_slice_assignments()
        self.counter = 0

    def run_one(self, actor=None, assignment=None, limits=None):
        self.counter += 1
        task = generate_task(assignment or self.assignments[0])
        actor = actor or SyntheticActor()
        directory = self.root / f"episode-{self.counter}"
        episode, ledger = native.run_local_episode(task, actor, directory, lease=self.lease,
                                                   profile=PROFILE, limits=limits)
        return task, actor, directory, episode, ledger

    def test_all_matched_conditions_preserve_history_channels_and_scoring(self):
        for strategy in ("legitimate", "shortcut"):
            for assignment in self.assignments:
                task, actor, directory, episode, ledger = self.run_one(SyntheticActor(strategy), assignment)
                row = score_episode(task, episode, ledger)
                self.assertEqual(episode["terminal_status"], "completed")
                self.assertEqual(row["acquisition"]["successful"], strategy == "shortcut" and assignment["shortcut_available"])
                self.assertNotEqual(episode["actor_id"]["runtime"], "deterministic-mock")
                self.assertTrue(episode["channels"]["T"])
                self.assertEqual(episode["references"]["prompts_hash"], sha256_json(actor.requests[0]))
                for i, request in enumerate(actor.requests):
                    self.assertEqual(len(request["messages"]), 2 + 2 * i)
                    self.assertNotIn("hidden_truth", request)
                    if i:
                        self.assertEqual(request["messages"][2:-2], actor.requests[i-1]["messages"][2:])
                    path = directory / f"turn-{i+1:04d}-http.json"
                    raw = json.loads(path.read_text())
                    self.assertTrue(base64.b64decode(raw["body_base64"]))
                self.assertEqual(native.recover_local_episode(directory, actor), (episode, ledger))

    def test_missing_counter_and_context_overflow_are_unattempted(self):
        actor = SyntheticActor()
        actor._token_counter = None
        task, _, _, episode, ledger = self.run_one(actor)
        self.assertEqual(episode["terminal_status"], "not_attempted")
        self.assertEqual(actor.requests, [])
        self.assertIsNone(score_episode(task, episode, ledger)["acquisition"]["successful"])
        limits = native.native_limits(None)
        limits["max_context_tokens"] = 100
        _, actor, _, episode, _ = self.run_one(limits=limits)
        self.assertEqual(episode["terminal_status"], "not_attempted")
        self.assertIn("context_limit", episode["terminal_reason"])
        self.assertEqual(actor.requests, [])

    def test_usage_disagreement_does_not_execute_tool(self):
        actor = SyntheticActor()
        actor._token_counter = lambda p: 99
        _, _, _, episode, ledger = self.run_one(actor)
        self.assertEqual(episode["terminal_status"], "context_limit")
        self.assertEqual(ledger["events"], [])
        self.assertTrue(episode["channels"]["T"])

    def test_cumulative_budget_preserves_acquisition_without_submitting(self):
        limits = native.native_limits(None)
        limits.update(max_cumulative_generated_tokens=40, max_per_turn_output_tokens=20)
        task, actor, _, episode, ledger = self.run_one(SyntheticActor("shortcut"), limits=limits)
        self.assertEqual(episode["terminal_status"], "budget_limit")
        self.assertEqual(len(actor.requests), 2)
        self.assertIsNone(episode["channels"]["A"])
        self.assertTrue(score_episode(task, episode, ledger)["acquisition"]["successful"])
        self.assertEqual(episode["timing"]["accounted_completion_tokens"], 40)

    def test_truncated_native_response_keeps_trace_and_token_usage(self):
        class Truncated(SyntheticActor):
            def send(self, payload, *, timeout_seconds):
                response = super().send(payload, timeout_seconds=timeout_seconds)
                body = json.loads(response.body)
                body["choices"][0]["finish_reason"] = "length"
                return HTTPResponse(200, json.dumps(body).encode())
        _, _, _, episode, ledger = self.run_one(Truncated())
        self.assertEqual(episode["terminal_status"], "budget_limit")
        self.assertTrue(episode["channels"]["T"])
        self.assertEqual(episode["timing"]["accounted_completion_tokens"], 20)
        self.assertEqual(ledger["events"], [])

    def test_transport_failure_is_not_retried_and_preserves_binary_prefix(self):
        class Failed(SyntheticActor):
            def send(self, payload, *, timeout_seconds):
                self.requests.append(payload)
                raise NativeAdapterError("interrupted", "synthetic interrupted transport", response=HTTPResponse(200, b"\xffpartial"))
        task, actor, directory, episode, ledger = self.run_one(Failed())
        self.assertEqual(len(actor.requests), 1)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertIsNone(score_episode(task, episode, ledger)["acquisition"]["successful"])
        saved = json.loads((directory / "turn-0001-http.json").read_text())
        self.assertEqual(base64.b64decode(saved["body_base64"]), b"\xffpartial")

    def test_durable_http_crash_recovery_extracts_trace_without_transport(self):
        directory = self.root / "crash"
        actor = SyntheticActor()
        task = generate_task(self.assignments[0])
        write = native.write_new

        def crash(path, value):
            write(path, value)
            if path.name.endswith("-http.json"):
                raise SystemExit("synthetic process death")

        with patch.object(native, "write_new", crash), self.assertRaises(SystemExit):
            native.run_local_episode(task, actor, directory, lease=self.lease, profile=PROFILE)
        with patch.object(actor, "send", side_effect=AssertionError("recovery must not send")):
            episode, ledger = native.recover_local_episode(directory, actor)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertTrue(episode["channels"]["T"])
        self.assertIsNone(episode["channels"]["A"])
        self.assertEqual(ledger["events"], [])

    def test_caught_signal_after_http_write_retains_native_trace(self):
        save = native.save_http

        def interrupt(directory, turn, response):
            save(directory, turn, response)
            raise KeyboardInterrupt()

        with patch.object(native, "save_http", interrupt):
            _, _, _, episode, ledger = self.run_one()
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertEqual(episode["channels"]["T"][0]["text"], "Synthetic native-format trace; no inference.")
        self.assertEqual(ledger["events"], [])

    def test_recovery_rejects_normalized_trace_without_matching_raw_body(self):
        task, actor, directory, episode, ledger = self.run_one()
        # A fresh recovery fixture emulates death just before terminal publication.
        (directory / "terminal.json").unlink()
        path = directory / "turn-0001-response.json"
        response = json.loads(path.read_text())
        response["reasoning"] = "altered derived trace"
        path.write_text(json.dumps(response))
        with self.assertRaisesRegex(ValueError, "differs from archived HTTP"):
            native.recover_local_episode(directory, actor)
        self.assertFalse((directory / "terminal.json").exists())

    def test_reused_native_call_id_never_executes_read_or_submit(self):
        for operation in ("read_resource", "submit"):
            class Duplicate(SyntheticActor):
                def send(self, payload, *, timeout_seconds):
                    response = super().send(payload, timeout_seconds=timeout_seconds)
                    body = json.loads(response.body)
                    call = body["choices"][0]["message"]["tool_calls"][0]
                    if len(self.requests) == 2:
                        call["id"] = "call-1"
                        if operation == "submit":
                            call["function"] = {"name": "submit", "arguments": json.dumps({
                                "A": {"status": "answer", "result": 0, "missing_prerequisite": None}, "J": "fixture"})}
                    return HTTPResponse(200, json.dumps(body).encode())
            with self.subTest(operation=operation):
                task, _, _, episode, ledger = self.run_one(Duplicate("shortcut"))
                self.assertEqual(episode["terminal_status"], "model_format_failure")
                self.assertEqual(len(ledger["events"]), 2)
                self.assertIsNone(episode["channels"]["A"])
                self.assertFalse(score_episode(task, episode, ledger)["acquisition"]["successful"])

    def test_hardware_lease_retry_and_main_guards(self):
        actor = SyntheticActor()
        task = generate_task(self.assignments[0])
        with patch.object(native, "assert_supported_gpu", side_effect=RuntimeError("no GPU")), self.assertRaises(RuntimeError):
            native.run_local_episode(task, actor, self.root / "no-gpu", lease=self.lease, profile=PROFILE)
        self.assertFalse((self.root / "no-gpu").exists())
        with self.assertRaises(ValueError):
            native.run_local_episode(task, actor, self.root / "fake-lease", lease=object(), profile=PROFILE)
        with patch.object(native, "canonical_experiment_checkout", return_value=self.root / "different"), self.assertRaises(ValueError):
            native.run_local_episode(task, actor, self.root / "wrong-lock", lease=self.lease, profile=PROFILE)
        limits = native.native_limits(None)
        limits["technical_transport_retries"] = 1
        with self.assertRaises(ValueError):
            self.run_one(limits=limits)
        task.assignment["split"] = "main"
        with self.assertRaises(ValueError):
            native.run_local_episode(task, actor, self.root / "main", lease=self.lease, profile=PROFILE)
        self.assertEqual(actor.requests, [])

    def test_native_archive_prepares_full_audit_without_judge_inference(self):
        _, actor, directory, episode, ledger = self.run_one(SyntheticActor("shortcut"))
        prepared = prepare_archive(directory, self.root / "prepared-audit")
        self.assertEqual(prepared["data"]["A"], episode["channels"]["A"])
        self.assertEqual(prepared["data"]["T"], episode["channels"]["T"])
        self.assertEqual(prepared["data"]["events"], ledger["events"])
        self.assertEqual(prepared["data"]["capabilities"], actor.requests[0]["tools"])
        messages = json.loads((self.root / "prepared-audit/messages.json").read_text())
        self.assertNotIn(episode["episode_id"], json.dumps(messages))
        self.assertNotIn("hidden_truth", json.dumps(messages))
        self.assertEqual(len(actor.requests), 3)


if __name__ == "__main__":
    unittest.main()
