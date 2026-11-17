"""SW05 integrator wiring regressions (CPU-only; no GPU / no qualification run)."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shortcut_study.analysis.protocol import (
    DEFAULT_PRIMARY_POLICY_ID,
    DENOMINATORS,
    MISSINGNESS,
    SEMANTIC,
    ZERO_EVENT_POLICY,
)
from shortcut_study.ids import make_episode_id
from shortcut_study.qualification import (
    allocate_held_out_schedule,
    tool_operation_counts,
)
from shortcut_study.runner.metrics import tool_operation_counts as metrics_counts
from shortcut_study.tasks.tables import (
    APPROVED,
    CATALOG_VERSION,
    DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
    TAB01_SLICE_VERSION,
    TEMPLATES,
    approved_for,
    generate_task,
    is_consumed_batch,
)
from shortcut_study.vertical_slice import (
    capability_probe_assignments,
    enumerate_vertical_slice_assignments,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs" / "development"


class TabCatalogConfigTests(unittest.TestCase):
    def test_development_catalog_matches_code_versions(self):
        catalog = json.loads((CONFIGS / "tab_catalog.json").read_text())
        self.assertEqual(catalog["catalog_version"], "tab-catalog-v4")
        self.assertEqual(catalog["catalog_version"], CATALOG_VERSION)
        self.assertEqual(catalog["tab01_moderate_generator_version"], TAB01_SLICE_VERSION)
        self.assertEqual(catalog["other_generator_version"], CATALOG_VERSION)
        self.assertEqual(
            catalog["fresh_qualification_batch_id"], DEFAULT_FRESH_QUALIFICATION_BATCH_ID)
        self.assertIn("Treat a new output directory as a fresh held-out world set", catalog["do_not"])


class AnalysisProtocolConfigTests(unittest.TestCase):
    def test_development_protocol_mirrors_protocol_module(self):
        protocol = json.loads((CONFIGS / "analysis_protocol.json").read_text())
        self.assertEqual(protocol["primary_arm"]["policy_id"], DEFAULT_PRIMARY_POLICY_ID)
        self.assertTrue(protocol["primary_arm"]["reject_mixed_policy_split_scorer"])
        self.assertEqual(protocol["missingness"]["complete_base_sensitivity"],
                         MISSINGNESS["complete_base_sensitivity"])
        self.assertEqual(protocol["denominators"], DENOMINATORS)
        self.assertEqual(protocol["zero_event_policy"]["independent_base_rule_of_three"],
                         ZERO_EVENT_POLICY["independent_base_rule_of_three"])
        self.assertIn("coefficient_aware", protocol["semantic"]["label_sensitivity"])
        self.assertEqual(protocol["semantic"]["withdraw_if_judge_unqualified"],
                         SEMANTIC["withdraw_if_judge_unqualified"])


class HeldOutBatchWiringTests(unittest.TestCase):
    def test_fresh_batch_expands_to_full_factorial_without_historical_catalog(self):
        manifest, assignments = allocate_held_out_schedule(
            batch_id=DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
            batch_mode="fresh",
            difficulties=("trivial",),
        )
        self.assertEqual(manifest["batch_id"], DEFAULT_FRESH_QUALIFICATION_BATCH_ID)
        self.assertTrue(manifest["fresh_held_out"])
        self.assertEqual(manifest["base_count"], 5)  # 5 templates × trivial
        self.assertEqual(len(assignments), 80)  # 5 × 16
        self.assertTrue(all(row["batch_id"] == DEFAULT_FRESH_QUALIFICATION_BATCH_ID for row in assignments))
        self.assertTrue(all(row["split"] == "qualification" for row in assignments))
        versions = {row["generator_version"] for row in assignments}
        self.assertIn(CATALOG_VERSION, versions)
        # No global GENERATOR_VERSION overwrite: TAB01 moderate not in trivial subset.
        self.assertNotIn("tab01-slice-v6", versions)
        for row in assignments:
            expected = make_episode_id(
                base_id=row["base_id"],
                information_state=row["information_state"],
                shortcut_available=row["shortcut_available"],
                visibility=row["visibility"],
                replicate_seed=row["replicate_seed"],
            )
            self.assertEqual(row["episode_id"], expected)
            task = generate_task(row, generation_seed=row["generation_seed"])
            self.assertEqual(task.assignment["generator_version"], row["generator_version"])

    def test_consumed_batch_cannot_allocate_as_fresh(self):
        with self.assertRaises(AssertionError):
            allocate_held_out_schedule(
                batch_id="g2-held-out-20261116",
                batch_mode="fresh",
            )

    def test_regression_replay_of_consumed_batch_is_explicit(self):
        manifest, assignments = allocate_held_out_schedule(
            batch_id="g2-held-out-20261116-catalog-v2",
            batch_mode="regression",
            difficulties=("trivial",),
        )
        self.assertFalse(manifest["fresh_held_out"])
        self.assertEqual(manifest["mode"], "regression")
        self.assertEqual(len(assignments), 80)
        self.assertTrue(is_consumed_batch(manifest["batch_id"]))


class GeneratorVersionStampTests(unittest.TestCase):
    def test_vertical_slice_and_capability_probe_keep_declared_versions(self):
        for row in enumerate_vertical_slice_assignments():
            self.assertEqual(row["generator_version"], "vertical-slice-stub-v0")
        for row in capability_probe_assignments():
            self.assertEqual(row["generator_version"], "vertical-slice-stub-v0")


class MetricsWiringTests(unittest.TestCase):
    def test_qualification_helper_uses_task_specific_approved_set(self):
        for template_id in TEMPLATES:
            approved = list(approved_for(template_id))
            ledger = {"events": []}
            for resource in approved:
                ledger["events"].append({
                    "event_type": "tool_call", "operation": "read_resource",
                    "resource_id": resource,
                })
                ledger["events"].append({
                    "event_type": "tool_result", "operation": "read_resource",
                    "resource_id": resource, "execution_status": "success",
                })
            ops, reads = tool_operation_counts(ledger, approved_resources=approved)
            expected_ops, expected_reads = metrics_counts(ledger, approved_resources=approved)
            self.assertEqual(ops, expected_ops)
            self.assertEqual(reads, expected_reads)
            self.assertEqual(reads, set(approved))
            if template_id != "TAB01":
                legacy_ops, legacy_reads = tool_operation_counts(ledger)
                self.assertEqual(legacy_reads, set(APPROVED) & set(approved))
                self.assertLess(legacy_ops.get("approved_resources_read", 0), len(approved))


class PrepareArchiveWiringTests(unittest.TestCase):
    def test_prepare_archive_delegates_to_bound_episode_prep(self):
        from shortcut_study.__main__ import prepare_archive

        with tempfile.TemporaryDirectory() as tmp:
            episode_dir = Path(tmp) / "episode"
            out_dir = Path(tmp) / "out"
            episode_dir.mkdir()
            fake_prepared = {
                "episode_id": "fixture-ep",
                "schema_version": "fixture",
            }
            fake_binding = {
                "input_sha256": {"terminal.json": "abc"},
                "runtime": "deterministic-mock",
            }
            with patch(
                "shortcut_study.audit.prepare_audit_from_episode_directory",
                return_value={"prepared": fake_prepared, "binding": fake_binding},
            ) as prep, patch(
                "shortcut_study.audit.judge_messages",
                return_value=[{"role": "user", "content": "fixture"}],
            ):
                prepared = prepare_archive(episode_dir, out_dir)
            prep.assert_called_once_with(episode_dir)
            self.assertEqual(prepared["episode_id"], "fixture-ep")
            manifest = json.loads((out_dir / "manifest.json").read_text())
            self.assertEqual(manifest["binding"], fake_binding)
            self.assertEqual(manifest["input_sha256"], fake_binding["input_sha256"])
            self.assertIn("prepared.json", manifest["output_sha256"])
            self.assertEqual(
                manifest["output_sha256"]["prepared.json"],
                hashlib.sha256((out_dir / "prepared.json").read_bytes()).hexdigest(),
            )


class AnalyzeDryCliFlagTests(unittest.TestCase):
    def test_materialize_fixtures_flag_defaults_off_and_forwards(self):
        from shortcut_study.__main__ import main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dry"
            with patch("shortcut_study.__main__.run_dry") as run_dry, patch(
                "shortcut_study.__main__.recovery_ok", return_value=True
            ), patch("sys.argv", ["shortcut_study", "analyze-dry", "--out", str(out)]):
                run_dry.return_value = {"warnings": []}
                main()
            self.assertFalse(run_dry.call_args.kwargs["materialize_fixtures"])

            with patch("shortcut_study.__main__.run_dry") as run_dry, patch(
                "shortcut_study.__main__.recovery_ok", return_value=True
            ), patch(
                "sys.argv",
                ["shortcut_study", "analyze-dry", "--out", str(out), "--materialize-fixtures"],
            ):
                run_dry.return_value = {"warnings": []}
                main()
            self.assertTrue(run_dry.call_args.kwargs["materialize_fixtures"])


if __name__ == "__main__":
    unittest.main()
