"""Pairing must include the actual model and backend, beyond the model alias."""

import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_study import config_fixture, dataset_fixture, response_fixture
from observer_study.data import prepare_items
from observer_study.io import read_json, write_json
from observer_study.runner import LocalServer, run
from observer_study.summary import compare_smoke_runs


class ComparisonIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.before, self.after = self.directory / "before", self.directory / "after"
        self.original = config_fixture()
        dataset_fixture(self.directory, self.original)
        self.make_runs()
        self.manifest = read_json(self.after / "manifest.json")

    def make_runs(self, changed_weights=False):
        refined = copy.deepcopy(self.original)
        refined.update(prompt_version="v2", protocol_version="observer-smoke-v2", context_tokens=16384)
        refined["generation"]["max_tokens"] = 8192
        if changed_weights:
            refined["model"]["sha256"] = "0" * 64
        for path, config in ((self.before, self.original), (self.after, refined)):
            preflight = {"model_sha256": config["model"]["sha256"], "formatted_prompts": {},
                         "properties": {"build_info": "build", "chat_template": "template", "model_path": str(path / "model"),
                                        "default_generation_settings": {"n_ctx": config["context_tokens"],
                                                                        "params": {"dry_multiplier": 0}}}}
            with patch.object(LocalServer, "preflight", return_value=preflight), \
                 patch.object(LocalServer, "request", return_value=(response_fixture(), "body")), \
                 contextlib.redirect_stdout(io.StringIO()):
                run(config, prepare_items(config, self.directory), "smoke", path, "http://127.0.0.1:8080", "unused")

    def test_allowed_profile_changes_and_different_local_paths(self):
        result = compare_smoke_runs(self.before, self.after)
        self.assertEqual(result["matched_requests"], 24)
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["verified_model_and_backend"]["model_sha256"], self.original["model"]["sha256"])
        self.assertEqual(result["verified_model_and_backend"]["runtime_build"], "build")
        self.assertEqual(result["verified_model_and_backend"]["generation_defaults"], {"dry_multiplier": 0})
        self.assertEqual(result["permitted_differences"]["max_output_tokens"], {"before": 4096, "after": 8192})
        self.assertEqual(result["permitted_differences"]["prompt_version"], {"before": "v1", "after": "v2"})

    def test_changed_backend_fields_rejected_individually(self):
        for field, value in (("build_info", "different"), ("chat_template", "different"),
                             ("default_generation_settings", {"params": {"dry_multiplier": 2}})):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["preflight"]["properties"][field] = value
                write_json(self.after / "manifest.json", manifest)
                with self.assertRaisesRegex(ValueError, "Smoke model/backend"):
                    compare_smoke_runs(self.before, self.after)

    def test_changed_weights_under_same_alias_rejected(self):
        # Generate a fresh, internally consistent pair; change weights alone.
        self.before, self.after = self.directory / "weights-before", self.directory / "weights-after"
        self.make_runs(changed_weights=True)
        with self.assertRaisesRegex(ValueError, "model_sha256 differs"):
            compare_smoke_runs(self.before, self.after)

    def test_missing_or_inconsistent_provenance_rejected(self):
        paths = (("preflight",), ("preflight", "model_sha256"), ("preflight", "properties", "build_info"),
                 ("preflight", "properties", "chat_template"),
                 ("preflight", "properties", "default_generation_settings", "params"))
        for path in paths:
            with self.subTest(path=path):
                manifest = copy.deepcopy(self.manifest)
                parent = manifest
                for key in path[:-1]:
                    parent = parent[key]
                del parent[path[-1]]
                write_json(self.after / "manifest.json", manifest)
                with self.assertRaisesRegex(ValueError, "Missing smoke provenance"):
                    compare_smoke_runs(self.before, self.after)
        manifest = copy.deepcopy(self.manifest)
        manifest["preflight"]["model_sha256"] = "0" * 64
        write_json(self.after / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "differs from configured model"):
            compare_smoke_runs(self.before, self.after)
