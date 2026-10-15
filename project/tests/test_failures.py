"""Regression checks for request lifecycle and transport evidence."""

import base64
import contextlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from test_study import config_fixture, dataset_fixture, response_fixture
from observer_study.io import RequestError, read_json, request_json, write_json
from observer_study.runner import LocalServer, run
from observer_study.scoring import unknown_score
from observer_study.summary import summarize


def http_response(body=b"{}", truncated=False):
    response = MagicMock()
    response.closed = False
    response.__enter__.return_value = response
    if truncated:
        response.read.side_effect = http.client.IncompleteRead(body, 10)
    else:
        response.read.return_value = body
    return response


class TransportTests(unittest.TestCase):
    def test_incomplete_success_and_error_bodies_retain_bytes_and_retry_policy(self):
        partial = b'{"message":"\xe2\x82'
        for status, retryable in ((None, True), (500, True), (400, False)):
            with self.subTest(status=status):
                opener = MagicMock()
                response = http_response(partial, truncated=True)
                if status is None:
                    opener.open.return_value = response
                else:
                    opener.open.side_effect = urllib.error.HTTPError("http://localhost", status, "error", {}, response)
                with patch("urllib.request.build_opener", return_value=opener):
                    with self.assertRaises(RequestError) as caught:
                        request_json("http://127.0.0.1:8080", {}, local=True)
                error = caught.exception
                self.assertEqual(error.retryable, retryable)
                self.assertEqual(error.raw_body, partial.decode("utf-8", errors="replace"))
                self.assertEqual(base64.b64decode(error.details["partial_body_base64"]), partial)
                self.assertEqual(error.details["received_bytes"], len(partial))
                self.assertEqual(error.details["missing_bytes"], 10)
                self.assertEqual(error.details["http_status"], status)

    def test_complete_non_json_and_http_errors_keep_existing_retry_policy(self):
        for status in (None, 400, 408, 429, 500, 502, 503, 504):
            with self.subTest(status=status):
                opener = MagicMock()
                response = http_response(b"not JSON")
                if status is None:
                    opener.open.return_value = response
                else:
                    opener.open.side_effect = urllib.error.HTTPError("http://localhost", status, "error", {}, response)
                with patch("urllib.request.build_opener", return_value=opener):
                    with self.assertRaises(RequestError) as caught:
                        request_json("http://127.0.0.1:8080", {}, local=True)
                self.assertEqual(caught.exception.retryable, status is not None and status != 400)
                self.assertEqual(caught.exception.raw_body, "not JSON")

    def test_truncation_retries_are_saved_and_collection_continues(self):
        for exhausted in (False, True):
            with self.subTest(exhausted=exhausted), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                config = config_fixture()
                prepared = dataset_fixture(directory, config)
                output = directory / "run"
                body = json.dumps(response_fixture()).encode()
                partial = b'{"choices": [\xe2\x82'
                opener = MagicMock()
                replies = [http_response(partial, truncated=True),
                           http_response(partial if exhausted else body, truncated=exhausted)]
                replies.extend(http_response(body) for _ in range(23))
                opener.open.side_effect = replies
                with patch.object(LocalServer, "preflight", return_value={"properties": {}, "formatted_prompts": {}}), \
                     patch("urllib.request.build_opener", return_value=opener), \
                     patch("observer_study.runner.time.sleep"), \
                     contextlib.redirect_stdout(io.StringIO()):
                    run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
                self.assertEqual(opener.open.call_count, 25)
                manifest = read_json(output / "manifest.json")
                first = read_json(output / "responses" / (manifest["requests"][0]["request_id"] + ".json"))
                self.assertEqual(len(first["attempts"]), 2)
                failed = first["attempts"][0]
                self.assertEqual(base64.b64decode(failed["error_details"]["partial_body_base64"]), partial)
                self.assertTrue(failed["finished_at"])
                self.assertEqual(first["status"], "technical_error" if exhausted else "returned")
                summary = summarize(output)
                self.assertEqual(summary["overall"]["assigned"], 24)
                self.assertEqual(summary["overall"]["returned"], 23 if exhausted else 24)
                self.assertEqual(summary["overall"]["correct"]["unknown"], 1 if exhausted else 0)


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
