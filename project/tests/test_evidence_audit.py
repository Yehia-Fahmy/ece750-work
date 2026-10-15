"""Ensure the archived-output audit detects differences without rewriting evidence."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from project.audit_smoke import audit_run
from test_study import config_fixture, dataset_fixture, response_fixture
from observer_study.io import file_digest, read_json, write_json
from observer_study.runner import LocalServer, run


class EvidenceAuditTests(unittest.TestCase):
    def test_rescoring_reports_differences_and_preserves_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            config = config_fixture()
            prepared = dataset_fixture(directory, config)
            output = directory / "run"
            response = response_fixture()
            with patch.object(LocalServer, "preflight", return_value={"properties": {}, "formatted_prompts": {}}), \
                 patch.object(LocalServer, "request", return_value=(response, json.dumps(response))), \
                 contextlib.redirect_stdout(io.StringIO()):
                run(config, prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
            self.assertEqual(audit_run(output)["changed_scores"], [])
            path = next((output / "responses").glob("*.json"))
            record = read_json(path)
            record["score"]["correct"] = not record["score"]["correct"]
            write_json(path, record)
            hashes = {p: file_digest(p) for p in output.rglob("*.json")}
            report = audit_run(output)
            self.assertEqual(len(report["changed_scores"]), 1)
            self.assertIn("correct", report["changed_scores"][0]["fields"])
            self.assertFalse(report["cached_overall_matches_rescored"])
            self.assertEqual(hashes, {p: file_digest(p) for p in output.rglob("*.json")})
            record["attempts"][-1]["raw_body"] = "{}"
            write_json(path, record)
            with self.assertRaisesRegex(ValueError, "Raw body differs"):
                audit_run(output)
