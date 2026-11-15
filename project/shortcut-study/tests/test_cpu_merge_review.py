"""Review regressions for signals between durable writes and memory updates."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from shortcut_study.adapters.mock import MockActor
import shortcut_study.runner as runner
from shortcut_study.scoring import score_episode
from shortcut_study.tasks.tables import generate_task
from shortcut_study.vertical_slice import enumerate_vertical_slice_assignments


class DurableBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "episode"
        self.task = generate_task(next(a for a in enumerate_vertical_slice_assignments()
                                       if a["shortcut_available"]))

    def test_signal_after_acquisition_fsync_preserves_known_fact(self):
        append = runner.append_event

        def interrupt_after_durable_result(path, event):
            append(path, event)
            if event["acquisition_success"]:
                raise KeyboardInterrupt()

        with patch.object(runner, "append_event", interrupt_after_durable_result):
            episode, ledger = runner.run_mock_episode(self.task, MockActor("shortcut"), self.directory)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertEqual(ledger["events"], runner.read_event_journal(self.directory))
        self.assertEqual(len(ledger["events"]), 4)
        self.assertTrue(score_episode(self.task, episode, ledger)["acquisition"]["successful"])
        self.assertEqual(runner.recover_mock_episode(self.directory), (episode, ledger))

    def crash_after_write(self, predicate, exception=SystemExit):
        write = runner.write_new

        def crash(path, value):
            write(path, value)
            if predicate(path, value):
                raise exception()

        with patch.object(runner, "write_new", crash):
            with self.assertRaises(exception):
                runner.run_mock_episode(self.task, MockActor("shortcut"), self.directory)

    def test_recovery_keeps_response_trace_before_capture(self):
        self.crash_after_write(lambda path, value: path.name == "turn-0001-response.json")
        episode, ledger = runner.recover_mock_episode(self.directory)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertEqual(episode["channels"]["T"][0]["text"],
                         "Scripted test step; not native model reasoning.")
        self.assertEqual(ledger["events"], [])
        self.assertIsNone(episode["channels"]["A"])

    def test_caught_signal_keeps_response_trace_before_capture(self):
        write = runner.write_new

        def interrupt(path, value):
            write(path, value)
            if path.name == "turn-0001-response.json":
                raise KeyboardInterrupt()

        with patch.object(runner, "write_new", interrupt):
            episode, _ = runner.run_mock_episode(self.task, MockActor(), self.directory)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertEqual(len(episode["channels"]["T"]), 1)

    def test_recovery_keeps_accepted_submission_without_replay(self):
        self.crash_after_write(lambda path, value: value == {"status": "success", "accepted": True})
        journal_before = (self.directory / "events.jsonl").read_bytes()
        episode, ledger = runner.recover_mock_episode(self.directory)
        self.assertEqual(episode["terminal_status"], "interrupted")
        self.assertEqual(episode["channels"]["A"], ledger["events"][-1]["arguments"]["A"])
        self.assertEqual(episode["channels"]["J"]["text"], "I used the prior-agent note.")
        self.assertEqual((self.directory / "events.jsonl").read_bytes(), journal_before)
        self.assertTrue(score_episode(self.task, episode, ledger)["acquisition"]["successful"])

    def test_submission_reconstruction_rejects_hash_or_raw_response_mismatch(self):
        self.crash_after_write(lambda path, value: value == {"status": "success", "accepted": True})
        events = runner.read_event_journal(self.directory)
        assignment = json.loads((self.directory / "assignment.json").read_text())
        for key in ("request_sha256", "response_sha256"):
            tampered = deepcopy(events)
            tampered[-1][key] = "0" * 64
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.restore_saved_channels(self.directory, deepcopy(assignment), tampered)
        response_path = self.directory / "turn-0003-response.json"
        response = json.loads(response_path.read_text())
        response["action"]["arguments"]["J"] = "changed"
        response_path.write_text(json.dumps(response))
        with self.assertRaises(ValueError):
            runner.recover_mock_episode(self.directory)
        self.assertFalse((self.directory / "terminal.json").exists())

    def test_partial_journal_tail_is_preserved_and_interior_corruption_rejected(self):
        self.directory.mkdir()
        journal = self.directory / "events.jsonl"
        contents = b'{"known": true}\n{"partial":'
        journal.write_bytes(contents)
        self.assertEqual(runner.read_event_journal(self.directory), [{"known": True}])
        self.assertEqual(journal.read_bytes(), contents)
        journal.write_bytes(contents + b'\n{"later": true}\n')
        with self.assertRaises(json.JSONDecodeError):
            runner.read_event_journal(self.directory)


if __name__ == "__main__":
    unittest.main()
