"""SW02 regressions for IMPL-1–3 (CPU fixtures; no authentic archives required)."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from shortcut_study.adapters.local import HTTPResponse, LocalChatActor
from shortcut_study.adapters.mock import MockActor
from shortcut_study.audit import prepare_audit, prepare_audit_from_episode_directory
from shortcut_study.environment import TOOL_CONTRACT
from shortcut_study.hashing import sha256_text
from shortcut_study.qualification import tool_operation_counts as legacy_tool_operation_counts
from shortcut_study.runtime import GpuLease
import shortcut_study.runner.native as native
from shortcut_study.runner import initial_record, run_mock_episode
from shortcut_study.runner.metrics import (
    TELEMETRY_METRIC_VERSION,
    derive_corrected_provenance,
    derive_corrected_telemetry,
    tool_operation_counts,
)
from shortcut_study.tasks.tables import (
    APPROVED,
    CATALOG_VERSION,
    TEMPLATES,
    approved_for,
    enumerate_tab_catalog_assignments,
    generate_task,
    generator_version_for,
)
from shortcut_study.vertical_slice import enumerate_vertical_slice_assignments

PROFILE = {
    "checkpoint_revision": "fixture-not-model",
    "checkpoint_sha256": "1" * 64,
    "quantization": "fixture",
    "runtime_revision": "fixture-not-runtime",
    "template_sha256": "2" * 64,
}


class SyntheticActor(LocalChatActor):
    def __init__(self, strategy="legitimate", **kwargs):
        super().__init__(
            "http://127.0.0.1:18080", "synthetic-native",
            token_counter=lambda _p: 100, **kwargs)
        self.strategy = strategy
        self.requests = []

    def send(self, payload, *, timeout_seconds):
        self.requests.append(deepcopy(payload))
        history = []
        messages = payload["messages"][2:]
        for assistant, tool in zip(messages[::2], messages[1::2]):
            call = assistant["tool_calls"][0]["function"]
            history.append({
                "action": {
                    "operation": call["name"],
                    "arguments": json.loads(call["arguments"]),
                },
                "result": json.loads(tool["content"]),
            })
        task = json.loads(payload["messages"][1]["content"])
        scripted = MockActor(self.strategy).respond({"task": task, "history": history})
        action = scripted["action"]
        response = {
            "choices": [{
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "reasoning_content": "Synthetic native-format trace; no inference.",
                    "tool_calls": [{
                        "id": f"call-{len(history) + 1}",
                        "type": "function",
                        "function": {
                            "name": action["operation"],
                            "arguments": json.dumps(action["arguments"]),
                        },
                    }],
                },
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        }
        return HTTPResponse(200, json.dumps(response).encode())


def _catalog_cell(template_id, *, difficulty="moderate"):
    return next(
        row for row in enumerate_tab_catalog_assignments(difficulties=(difficulty,))
        if row["template_id"] == template_id
        and row["information_state"] == "complete"
        and not row["shortcut_available"]
        and row["visibility"] == "V00"
    )


class Impl2GeneratorVersionTests(unittest.TestCase):
    def test_all_five_templates_record_derived_generator_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for template_id in TEMPLATES:
                assignment = _catalog_cell(template_id)
                task = generate_task(assignment, generation_seed=assignment["generation_seed"])
                expected = generator_version_for(assignment)
                self.assertEqual(expected, assignment["generator_version"])
                if template_id == "TAB01" and assignment["intended_difficulty"] == "moderate":
                    self.assertEqual(expected, "tab01-slice-v7")
                else:
                    self.assertEqual(expected, CATALOG_VERSION)
                episode, _ = run_mock_episode(
                    task, MockActor("legitimate"), root / template_id, run_id="sw02")
                self.assertEqual(episode["generator_version"], expected)
                record = initial_record(
                    task, "sw02", "mock",
                    {"max_model_turns": 8, "max_tool_actions": 16, "max_wall_time_seconds": 30})
                self.assertEqual(record["generator_version"], expected)

    def test_assignment_generator_mismatch_rejected(self):
        assignment = _catalog_cell("TAB02")
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        task.assignment = {**task.assignment, "generator_version": "tab01-slice-v6"}
        with self.assertRaisesRegex(ValueError, "generator_version"):
            initial_record(
                task, "sw02", "mock",
                {"max_model_turns": 8, "max_tool_actions": 16, "max_wall_time_seconds": 30})

    def test_derived_provenance_corrects_without_rewriting_terminal(self):
        assignment = _catalog_cell("TAB03")
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        with tempfile.TemporaryDirectory() as tmp:
            episode, ledger = run_mock_episode(
                task, MockActor("legitimate"), Path(tmp) / "ep", run_id="sw02")
            terminal = {"episode": deepcopy(episode), "ledger": ledger}
            # Simulate a historical wrong stamp without mutating the on-disk terminal.
            terminal["episode"]["generator_version"] = "tab01-slice-v6"
            derived = derive_corrected_provenance(terminal, assignment=assignment)
            self.assertTrue(derived["generator_version_mismatch"])
            self.assertEqual(derived["generator_version_corrected"], CATALOG_VERSION)
            self.assertEqual(episode["generator_version"], CATALOG_VERSION)


class Impl3ApprovedReadTelemetryTests(unittest.TestCase):
    def test_task_specific_reads_for_all_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for template_id in TEMPLATES:
                assignment = _catalog_cell(template_id)
                task = generate_task(assignment, generation_seed=assignment["generation_seed"])
                episode, ledger = run_mock_episode(
                    task, MockActor("legitimate"), root / template_id, run_id="sw02")
                self.assertEqual(episode["terminal_status"], "completed")
                approved = list(task.public_task["approved_resources"])
                self.assertEqual(set(approved), set(approved_for(template_id)))
                ops, reads = tool_operation_counts(ledger, approved_resources=approved)
                self.assertEqual(reads, set(approved))
                self.assertEqual(ops["approved_resources_read"], len(approved))
                self.assertGreaterEqual(ops.get("approved_read_success", 0), len(approved))
                if template_id != "TAB01":
                    legacy_ops, legacy_reads = legacy_tool_operation_counts(ledger)
                    self.assertEqual(legacy_reads, set())
                    self.assertEqual(legacy_ops.get("approved_resources_read", 0), 0)
                    derived = derive_corrected_telemetry(
                        {"episode": episode, "ledger": ledger},
                        public_task=task.public_task)
                    self.assertEqual(derived["metric_version"], TELEMETRY_METRIC_VERSION)
                    self.assertEqual(set(derived["approved_resources_read"]), set(approved))


class Impl1NativeAuditBindingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lease = GpuLease(self.root, owner="test", job="sw02", run_id="test")
        self.lease.__enter__()
        self.addCleanup(self.lease.__exit__, None, None, None)
        probe = patch.object(
            native, "assert_supported_gpu",
            return_value={"gpu_name": "synthetic-probe-not-hardware"})
        probe.start()
        self.addCleanup(probe.stop)
        canonical = patch.object(native, "canonical_experiment_checkout", return_value=self.root)
        canonical.start()
        self.addCleanup(canonical.stop)

    def _run_native(self):
        assignment = next(
            a for a in enumerate_vertical_slice_assignments()
            if a["information_state"] == "complete"
            and not a["shortcut_available"]
            and a["visibility"] == "V00")
        task = generate_task(assignment)
        actor = SyntheticActor("legitimate")
        directory = self.root / "native-ep"
        episode, ledger = native.run_local_episode(
            task, actor, directory, lease=self.lease, profile=PROFILE)
        return task, actor, directory, episode, ledger

    def test_valid_native_prepares_with_http_provenance(self):
        _, actor, directory, episode, ledger = self._run_native()
        http_sha = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.glob("turn-*-http.json"))
        }
        bundle = prepare_audit_from_episode_directory(directory, actor=actor)
        prepared = bundle["prepared"]
        self.assertEqual(prepared["data"]["T"], episode["channels"]["T"])
        self.assertEqual(prepared["data"]["events"], ledger["events"])
        self.assertEqual(bundle["binding"]["kind"], "native")
        self.assertEqual(bundle["binding"]["native_http_sha256"], http_sha)
        self.assertEqual(prepared["native_binding"]["native_http_sha256"], http_sha)
        # HTTP bytes unchanged by preparation.
        self.assertEqual(
            {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(directory.glob("turn-*-http.json"))},
            http_sha)

    def test_altered_terminal_t_rejected_http_unchanged(self):
        _, actor, directory, episode, _ = self._run_native()
        http_path = directory / "turn-0001-http.json"
        http_before = hashlib.sha256(http_path.read_bytes()).hexdigest()
        terminal_path = directory / "terminal.json"
        terminal = json.loads(terminal_path.read_text())
        original = terminal["episode"]["channels"]["T"][0]["text"]
        replacement = "REVIEW FIXTURE: I deliberately acquired the prohibited previous attempt."
        terminal["episode"]["channels"]["T"][0].update(
            text=replacement, text_sha256=sha256_text(replacement))
        terminal_path.write_text(json.dumps(terminal))
        with self.assertRaisesRegex(ValueError, "terminal record differs from native archive"):
            prepare_audit_from_episode_directory(directory, actor=actor)
        with self.assertRaisesRegex(ValueError, "terminal record differs from native archive"):
            native.verify_terminal_matches_native(directory, actor)
        self.assertEqual(hashlib.sha256(http_path.read_bytes()).hexdigest(), http_before)
        self.assertEqual(original, episode["channels"]["T"][0]["text"])
        self.assertNotEqual(original, replacement)

    def test_prepare_audit_rejects_native_without_binding(self):
        task, _, directory, episode, ledger = self._run_native()
        results = {
            event["event_id"]: json.loads(
                (directory / f"turn-{event['turn_id']:04d}-result.json").read_text())
            for event in ledger["events"] if event["response_sha256"] is not None
        }
        capabilities = json.loads((directory / "turn-0001-request.json").read_text())["tools"]
        with self.assertRaisesRegex(ValueError, "native_binding"):
            prepare_audit(
                episode, ledger, public_task=task.public_task,
                capabilities=capabilities, tool_results=results)

    def test_missing_http_source_fails_clearly(self):
        _, actor, directory, _, _ = self._run_native()
        for path in directory.glob("turn-*-http.json"):
            path.unlink()
        with self.assertRaisesRegex(ValueError, "HTTP source"):
            prepare_audit_from_episode_directory(directory, actor=actor)

    def test_interrupted_without_terminal_stays_unprepared(self):
        directory = self.root / "interrupted"
        directory.mkdir()
        (directory / "inputs.json").write_text(json.dumps({
            "prompt": {"task": {"approved_resources": list(APPROVED)}, "tools": TOOL_CONTRACT},
            "actor_settings": {
                "adapter_version": "x", "history_policy": "y",
                "model": "synthetic-native", "base_url": "http://127.0.0.1:18080",
                "temperature": 0.6, "top_p": 0.95,
                "max_request_bytes": 1_048_576, "max_response_bytes": 2_097_152,
            },
        }))
        with self.assertRaisesRegex(ValueError, "interrupted records remain unprepared"):
            prepare_audit_from_episode_directory(directory)


if __name__ == "__main__":
    unittest.main()
