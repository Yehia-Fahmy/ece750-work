"""Regression checks for request lifecycle and transport evidence."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_study import config_fixture, dataset_fixture, response_fixture
from observer_study.io import RequestError, read_json, write_json
from observer_study.runner import LocalServer, run
from observer_study.scoring import unknown_score
from observer_study.summary import summarize


class RetryLifecycleTests(unittest.TestCase):
    def test_gate_stays_pending_during_backoff_and_retry(self):
        for outcome in ("success", "exhausted", "interrupt_backoff", "interrupt_retry"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                config = config_fixture()
                prepared = dataset_fixture(directory, config)
                output = directory / "run"
                calls, snapshots = [], []
                preflight = {"properties": {}, "formatted_prompts": {}}

                def respond(route, payload=None):
                    calls.append(payload)
                    if len(calls) == 24:
                        raise RequestError("busy", raw_body="busy", retryable=True)
                    if len(calls) == 25:
                        snapshots.append(summarize(output))
                        if outcome == "interrupt_retry":
                            raise KeyboardInterrupt()
                        if outcome == "exhausted":
                            raise RequestError("busy again", retryable=True)
                    return response_fixture(), "body"

                def backoff(seconds):
                    snapshots.append(summarize(output))
                    if outcome == "interrupt_backoff":
                        raise KeyboardInterrupt()

                with patch.object(LocalServer, "preflight", return_value=preflight), \
                     patch.object(LocalServer, "request", side_effect=respond), \
                     patch("observer_study.runner.time.sleep", side_effect=backoff), \
                     contextlib.redirect_stdout(io.StringIO()):
                    if outcome.startswith("interrupt"):
                        with self.assertRaises(KeyboardInterrupt):
                            run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
                    else:
                        run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
                    self.assertTrue(snapshots)
                    for snapshot in snapshots:
                        self.assertEqual(snapshot["overall"]["complete"], 23)
                        self.assertFalse(snapshot["quality_checks"]["collection_finished"])
                        self.assertFalse(snapshot["quality_checks"]["observed_targets_met"])
                    attempts = {p.name: read_json(p)["attempts"] for p in (output / "responses").glob("*.json")}
                    count = len(calls)
                    run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused", resume=True)
                self.assertEqual(len(calls), count)
                self.assertEqual(attempts, {p.name: read_json(p)["attempts"] for p in (output / "responses").glob("*.json")})
                summary = summarize(output)
                self.assertTrue(summary["quality_checks"]["collection_finished"])
                self.assertEqual(summary["overall"]["correct"]["unknown"], 0 if outcome == "success" else 1)
                terminal = "returned" if outcome == "success" else "technical_error" if outcome == "exhausted" else "interrupted"
                self.assertIn(terminal, summary["overall"]["request_statuses"])

    def test_legacy_unfinished_retry_is_pending_then_interrupted_on_resume(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            config = config_fixture()
            prepared = dataset_fixture(directory, config)
            output = directory / "run"
            preflight = {"properties": {}, "formatted_prompts": {}}
            with patch.object(LocalServer, "preflight", return_value=preflight), \
                 patch.object(LocalServer, "request", return_value=(response_fixture(), "body")) as request, \
                 contextlib.redirect_stdout(io.StringIO()):
                run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
                path = next((output / "responses").glob("*.json"))
                record = read_json(path)
                record.update(status="technical_error", score=unknown_score())
                record["attempts"].append({"number": 2, "started_at": "2026-10-14T00:00:00Z"})
                write_json(path, record)
                self.assertFalse(summarize(output)["quality_checks"]["observed_targets_met"])
                run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused", resume=True)
            self.assertEqual(request.call_count, 24)
            resumed = read_json(path)
            self.assertEqual(resumed["status"], "interrupted")
            self.assertEqual(resumed["attempts"], record["attempts"])
            self.assertIsNone(resumed["score"]["correct"])
