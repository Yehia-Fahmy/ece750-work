"""Qualification accounting tests; never start a server or model."""

import base64
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from shortcut_study.adapters.local import LocalChatActor
from shortcut_study.qualification import (
    CounterArchive, episode_metrics, evaluate_capability_probe, quantile, run_qualification, summarize,
)
from shortcut_study.runner import write_new
import shortcut_study.runner.native as native
from shortcut_study.runtime import GpuLease
from shortcut_study.tasks.tables import APPROVED, generate_task
from shortcut_study.vertical_slice import capability_probe_assignments, enumerate_vertical_slice_assignments


class QualificationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def run_with_fakes(self, name, *, telemetry=None, episode_hook=None, metrics_error=None,
                       capability_probe=False, score=None):
        """Exercise orchestration/accounting with every GPU/inference edge mocked."""
        gpu = {"name": "NVIDIA GeForce RTX 3070 Ti", "uuid": "GPU-fixture", "memory_total_mib": 8192}
        monitor = MagicMock()
        monitor.summary = deepcopy(telemetry if telemetry is not None else {
            "valid_for_feasibility": True, "minimum_sampled_headroom_mib": 1000,
            "observed_gpu_identities": [gpu]})
        server = MagicMock(base_url="http://127.0.0.1:18080", props={}, profile={})
        server.assert_ready = MagicMock()
        server.manifest = {"gpu": gpu}
        results = {}
        default_score = score or {
            "task_result": {"announced_task_score": True, "authorized_success": True,
                            "insufficiency_correct": True},
            "acquisition": {"attempted": False, "successful": False},
        }

        def episode(task, actor, directory, **kwargs):
            directory.mkdir()
            if episode_hook is not None:
                episode_hook(directory)
            events = []
            for index, resource in enumerate(APPROVED, 1):
                events.append({"event_type": "tool_call", "operation": "read_resource",
                               "resource_id": resource, "sequence": len(events) + 1})
                events.append({"event_type": "tool_result", "operation": "read_resource",
                               "resource_id": resource, "execution_status": "success",
                               "sequence": len(events) + 1})
            events.append({"event_type": "tool_call", "operation": "calculate", "sequence": len(events) + 1})
            events.append({"event_type": "tool_result", "operation": "calculate",
                           "execution_status": "success", "sequence": len(events) + 1})
            if task.assignment["information_state"] == "incomplete":
                events.append({"event_type": "tool_call", "operation": "request_clarification",
                               "sequence": len(events) + 1})
                events.append({"event_type": "tool_result", "operation": "request_clarification",
                               "execution_status": "success", "sequence": len(events) + 1})
            result = ({"terminal_status": "completed", "terminal_reason": "fixture",
                       "timing": {"elapsed_seconds": 1}}, {"events": events})
            results[str(directory)] = result
            return result

        turns = [{"count_matches": True, "native_reasoning_present": True,
                  "native_action_present": True, "usage": {"prompt_tokens": 3, "completion_tokens": 4}}]
        with ExitStack() as stack:
            stack.enter_context(patch("shortcut_study.qualification.source_manifest", return_value={"fixture": "hash"}))
            stack.enter_context(patch("shortcut_study.qualification.GpuLease"))
            stack.enter_context(patch("shortcut_study.runtime.server.inspect_local_assets", return_value={}))
            server_class = stack.enter_context(patch("shortcut_study.runtime.server.LocalLlamaServer"))
            server_class.return_value.__enter__.return_value = server
            monitor_class = stack.enter_context(patch("shortcut_study.runtime.telemetry.GpuTelemetry"))
            monitor_class.return_value.__enter__.return_value = monitor
            stack.enter_context(patch("shortcut_study.adapters.token_counter.LlamaCppTokenCounter"))
            stack.enter_context(patch("shortcut_study.qualification.run_local_episode", side_effect=episode))
            stack.enter_context(patch("shortcut_study.qualification.score_episode", return_value=default_score))
            stack.enter_context(patch("shortcut_study.qualification.recover_local_episode",
                                      side_effect=lambda directory, actor: results[str(directory)]))
            stack.enter_context(patch("shortcut_study.__main__.prepare_archive"))
            stack.enter_context(patch("shortcut_study.qualification.episode_metrics", return_value=turns,
                                      side_effect=metrics_error))
            stack.enter_context(patch("builtins.print"))
            return run_qualification(self.root / name, capability_probe=capability_probe)

    def test_failed_start_preserves_all_sixteen_assignments_without_inference(self):
        with patch("shortcut_study.runtime.server.inspect_local_assets", side_effect=RuntimeError("fixture unavailable")), \
                patch("shortcut_study.qualification.run_local_episode", side_effect=AssertionError("no inference")):
            summary = run_qualification(self.root / "run")
        self.assertEqual(summary["assigned"], 16)
        self.assertEqual(summary["terminal_counts"], {"not_attempted": 16})
        self.assertFalse(summary["native_slice_capture_passed"])
        self.assertIn("fixture unavailable", summary["failure"])
        self.assertTrue((self.root / "run/manifest.json").exists())
        with self.assertRaises(FileExistsError):
            run_qualification(self.root / "run")

    def test_capability_probe_uses_two_existing_cells_and_gates_on_reads(self):
        summary = self.run_with_fakes("capability", capability_probe=True)
        self.assertEqual(summary["assigned"], 2)
        self.assertEqual(summary["evidence_kind"], "local_model_capability_probe_not_main")
        self.assertTrue(summary["capability_probe"]["passed"])
        self.assertTrue(summary["capability_check_passed"])
        self.assertTrue(summary["local_development_check_passed"])
        premature = {
            "episode_id": "complete",
            "terminal_status": "completed",
            "score": {"task_result": {"announced_task_score": False, "authorized_success": False,
                                      "insufficiency_correct": False}},
            "tool_operation_counts": {"request_clarification": 1, "submit": 1},
            "approved_resources_read": [],
            "first_operations": ["request_clarification", "submit"],
        }
        probe = evaluate_capability_probe(
            [{"episode_id": "complete", "information_state": "complete"},
             {"episode_id": "incomplete", "information_state": "incomplete"}],
            [premature, {**premature, "episode_id": "incomplete",
                         "score": {"task_result": {"announced_task_score": True, "authorized_success": True,
                                                   "insufficiency_correct": True}}}],
        )
        self.assertFalse(probe["passed"])
        self.assertEqual(len(capability_probe_assignments()), 2)

    def test_result_denominator_keeps_completed_failed_and_unattempted(self):
        assignments = [{"episode_id": name} for name in ("a", "b", "c")]
        rows = [{"episode_id": "a", "terminal_status": "completed", "turns": [], "elapsed_seconds": 2},
                {"episode_id": "b", "terminal_status": "interrupted", "turns": [], "elapsed_seconds": 4}]
        summary = summarize(assignments, rows, {}, failure="stop")
        self.assertEqual(summary["terminal_counts"], {"completed": 1, "interrupted": 1, "not_attempted": 1})
        self.assertEqual(summary["episode_latency_seconds"]["mean"], 3)
        self.assertFalse(summary["main_qualified"])
        self.assertFalse(summary["judge_qualified"])
        self.assertFalse(summary["G1_accepted"])
        for invalid in (rows + [rows[0]], rows + [{"episode_id": "outside"}]):
            with self.assertRaises(ValueError):
                summarize(assignments, invalid, {})

    def test_capture_gate_requires_native_channels_count_agreement_and_audit(self):
        row = {"episode_id": "a", "terminal_status": "completed", "audit_status": "prepared_no_judge",
               "recovery_verified": True, "turns": [{"count_matches": True, "native_reasoning_present": True,
               "native_action_present": True, "usage": {"prompt_tokens": 3, "completion_tokens": 4}}]}
        self.assertTrue(summarize([{"episode_id": "a"}], [row], {})["native_slice_capture_passed"])
        row["turns"][0]["count_matches"] = False
        self.assertFalse(summarize([{"episode_id": "a"}], [row], {})["native_slice_capture_passed"])

    def test_metrics_bind_preflight_to_actual_wire_usage_and_keep_bad_response(self):
        write_new(self.root / "turn-0001-response.json", {"reasoning": "trace", "action": {},
                  "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6}})
        write_new(self.root / "turn-0001-preflight.json", {"prompt_tokens": 5})
        raw = {"timings": {"predicted_ms": 100, "bogus": "not timing"}}
        write_new(self.root / "turn-0001-http.json", {"body_base64": base64.b64encode(json.dumps(raw).encode()).decode()})
        metrics = episode_metrics(self.root)
        self.assertFalse(metrics[0]["count_matches"])
        self.assertEqual(metrics[0]["server_timings"], {"predicted_ms": 100})
        write_new(self.root / "turn-0002-response.json", {"reasoning": None, "action": None, "usage": None})
        write_new(self.root / "turn-0002-preflight.json", {"prompt_tokens": 5})
        write_new(self.root / "turn-0002-http.json", {"body_base64": base64.b64encode(b"partial").decode()})
        self.assertFalse(episode_metrics(self.root)[1]["count_matches"])

    def test_counter_archive_never_overwrites_and_quantiles_are_explicit(self):
        archive = CounterArchive(self.root / "counter")
        archive({"phase": "request"})
        archive({"phase": "response"})
        self.assertEqual(len(list(archive.directory.glob("*.json"))), 2)
        with self.assertRaises(FileExistsError):
            CounterArchive(archive.directory)
        self.assertIsNone(quantile([], .95))
        self.assertEqual(quantile([1, 3], .5), 2)

    def test_memory_gate_requires_valid_matching_gpu_and_minimum_headroom(self):
        gpu = {"name": "NVIDIA GeForce RTX 3070 Ti", "uuid": "GPU-fixture", "memory_total_mib": 8192}
        good = {"valid_for_feasibility": True, "minimum_sampled_headroom_mib": 512,
                "observed_gpu_identities": [gpu]}
        cases = [({}, False), ({**good, "valid_for_feasibility": False}, False),
                 ({**good, "minimum_sampled_headroom_mib": 511}, False),
                 ({**good, "observed_gpu_identities": [{**gpu, "uuid": "GPU-other"}]}, False),
                 (good, True)]
        for index, (telemetry, expected) in enumerate(cases):
            summary = self.run_with_fakes(f"memory-{index}", telemetry=telemetry)
            self.assertTrue(summary["native_slice_capture_passed"])
            self.assertEqual(summary["sampled_memory_check_passed"], expected)
            self.assertEqual(summary["local_development_check_passed"], expected)

    def test_failure_after_saved_request_is_interrupted_not_unattempted(self):
        def interrupted(directory):
            write_new(directory / "turn-0001-request.json", {"fixture": True})
            raise OSError("fixture persistence failure after transport may have begun")

        summary = self.run_with_fakes("interrupted", episode_hook=interrupted)
        self.assertEqual(summary["terminal_counts"], {"interrupted": 1, "not_attempted": 15})
        self.assertEqual(summary["recorded_episodes"], 1)
        self.assertEqual(summary["outcomes"][0]["audit_status"], "unresolved_processing_failure")
        self.assertFalse(summary["local_development_check_passed"])
        artifact = Path(summary["outcomes"][0]["artifact_directory"])
        self.assertTrue((artifact / "turn-0001-request.json").exists())

    def test_failure_after_terminal_retains_completed_outcome(self):
        def after_terminal(directory):
            write_new(directory / "terminal.json", {"episode": {"terminal_status": "completed"}})
            raise OSError("fixture packet persistence failure")

        summary = self.run_with_fakes("terminal", episode_hook=after_terminal)
        self.assertEqual(summary["terminal_counts"], {"completed": 1, "not_attempted": 15})
        self.assertFalse(summary["native_slice_capture_passed"])

    def test_metrics_failure_cannot_erase_returned_terminal_outcome(self):
        summary = self.run_with_fakes("metrics", metrics_error=ValueError("fixture malformed metric"))
        self.assertEqual(summary["terminal_counts"], {"completed": 1, "not_attempted": 15})
        self.assertIn("malformed metric", summary["failure"])
        self.assertFalse(summary["local_development_check_passed"])

    def test_remaining_deadline_reaches_counter_and_expiry_prevents_inference(self):
        clock = [0.0]
        received = []

        class BoundedCounter:
            def __call__(self, payload):
                raise AssertionError("bounded production counter must receive deadline")

            def count(self, payload, *, timeout_seconds):
                received.append(timeout_seconds)
                clock[0] += timeout_seconds + 1
                return 100

        actor = LocalChatActor("http://127.0.0.1:18080", "fixture", token_counter=BoundedCounter())
        task = generate_task(enumerate_vertical_slice_assignments()[0])
        profile = {"checkpoint_revision": "fixture", "checkpoint_sha256": "1" * 64,
                   "quantization": "fixture", "runtime_revision": "fixture", "template_sha256": "2" * 64}
        limits = native.native_limits(None)
        limits["max_wall_time_seconds"] = 3
        with GpuLease(self.root, owner="test", job="cpu", run_id="bounded-counter") as lease, \
                patch.object(native, "canonical_experiment_checkout", return_value=self.root), \
                patch.object(native, "assert_supported_gpu", return_value={"fixture": True}), \
                patch.object(native.time, "monotonic", side_effect=lambda: clock[0]), \
                patch.object(actor, "send", side_effect=AssertionError("expired count must not generate")) as send:
            episode, ledger = native.run_local_episode(task, actor, self.root / "expired", lease=lease,
                                                       profile=profile, limits=limits)
        self.assertEqual(received, [3.0])
        send.assert_not_called()
        self.assertEqual(ledger["events"], [])
        self.assertEqual(episode["terminal_status"], "not_attempted")
        self.assertIn("Wall-time budget reached before transport", episode["terminal_reason"])


if __name__ == "__main__":
    unittest.main()
