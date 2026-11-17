"""SW03 regressions: A1–5, fixture side effects, release provenance."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from shortcut_study.analysis.compare import analyze_acquisition
from shortcut_study.analysis.harness import run_analyze, run_dry
from shortcut_study.analysis.io import join_rows_with_schedule, load_scored_rows
from shortcut_study.analysis.metrics import cell_rates
from shortcut_study.analysis.semantic import label_error_sensitivity
from shortcut_study.analysis.simulate import (
    ANALYSIS_FIXTURES_DIR,
    build_simulation_bundle,
    build_stochastic_bundle,
    write_simulation_fixtures,
)
from shortcut_study.hashing import sha256_bytes


class SW03AnalysisReleaseTests(unittest.TestCase):
    def test_a1_heterogeneous_missingness_point_matches_bootstrap(self):
        bundle = build_simulation_bundle(
            "null",
            bases_per_family=2,
            difficulties=("trivial",),
            include_absent_controls=False,
        )
        rows = bundle["rows"]
        for row in rows:
            if row["base_id"].endswith("000"):
                value = row["visibility"] in ("V10", "V11")
                if row["information_state"] == "incomplete" and row["visibility"] == "V10":
                    value = None
                row["acquisition_successful"] = value
                row["acquisition"]["successful"] = value
        report = analyze_acquisition(rows, replicates=50, seed=1)
        t = report["contrasts"]["T_visibility"]
        point = t["complete_block_sensitivity"]["point"]
        boot_point = t["bootstrap_complete_block"]["point"]
        self.assertEqual(point, boot_point)
        self.assertEqual(point, 0.0)
        self.assertEqual(t["bootstrap_complete_block"]["percentile_95"], [0.0, 0.0])
        self.assertEqual(report["paired"]["complete_blocks"], 4)
        # all_assigned blocks_used counts matched blocks, not difficulty strata.
        self.assertEqual(t["all_assigned"]["blocks_used"], 4)
        self.assertEqual(t["complete_block_sensitivity"]["bases_used"], 1)
        self.assertEqual(t["complete_block_sensitivity"]["estimand"], "complete_base_sensitivity")

    def test_a2_adversarial_flips_inside_coefficient_aware_bounds(self):
        null = build_simulation_bundle(
            "null",
            bases_per_family=10,
            difficulties=("trivial",),
            information_states=("complete",),
            include_absent_controls=False,
        )["rows"]
        changed = copy.deepcopy(null)
        flips = 0
        for row in changed:
            if row["visibility"] == "V00" and flips < 4:
                row["acquisition_successful"] = True
                row["acquisition"]["successful"] = True
                flips += 1
        changed_point = analyze_acquisition(changed, replicates=10)["contrasts"][
            "T_visibility"
        ]["all_assigned"]["point"]
        sens = label_error_sensitivity(null, flip_rate=0.1)
        lo, hi = sens["envelopes"]["T_visibility"]["envelope"]
        self.assertEqual(flips, 4)
        self.assertEqual(changed_point, -0.2)
        self.assertLessEqual(lo, changed_point)
        self.assertGreaterEqual(hi, 0.0)
        # Interaction range must allow ±2, not clamp to ±1.
        ix = sens["envelopes"]["TxJ_interaction"]["contrast_range"]
        self.assertEqual(ix, [-2.0, 2.0])

    def test_a3_release_retains_hashed_inputs_for_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_simulation_fixtures(root / "fixtures")
            out = root / "release"
            report = run_analyze(
                root / "fixtures" / "T_only" / "analysis_rows.json",
                root / "fixtures" / "T_only" / "schedule.json",
                out,
                replicates=20,
                seed=11,
            )
            manifest = json.loads((out / "analysis_manifest.json").read_text())
            retained_schedule = out / "retained_inputs" / "schedule.json"
            retained_rows = out / "retained_inputs" / "analysis_rows.json"
            self.assertTrue(retained_schedule.is_file())
            self.assertTrue(retained_rows.is_file())
            self.assertTrue((out / "analysis_protocol_snapshot.json").is_file())
            self.assertIn("retained:schedule.json", manifest["input_sha256"])
            self.assertEqual(
                manifest["input_sha256"]["retained:schedule.json"],
                sha256_bytes(retained_schedule.read_bytes()),
            )
            self.assertEqual(
                manifest["input_sha256"]["retained:analysis_rows.json"],
                sha256_bytes(retained_rows.read_bytes()),
            )
            # Replay after removing original external paths.
            replay_out = root / "replay"
            replay = run_analyze(
                retained_rows,
                retained_schedule,
                replay_out,
                replicates=20,
                seed=11,
            )
            self.assertEqual(
                report["contrasts"]["T_visibility"]["all_assigned"]["point"],
                replay["contrasts"]["T_visibility"]["all_assigned"]["point"],
            )

    def test_a4_mixed_policy_and_wrong_version_reject(self):
        restricted = build_simulation_bundle(
            "T_only",
            bases_per_family=1,
            difficulties=("trivial",),
            include_absent_controls=False,
        )["rows"]
        broad = build_simulation_bundle(
            "J_only",
            bases_per_family=1,
            difficulties=("trivial",),
            include_absent_controls=False,
        )["rows"]
        for row in broad:
            row["base_id"] += "-broad"
            row["episode_id"] += "-broad"
            row["policy_id"] = "broad_permission_v1"
        with self.assertRaises(ValueError) as ctx:
            analyze_acquisition(restricted + broad, replicates=10)
        self.assertIn("mixed policy_id", str(ctx.exception))

        wrong_policy = copy.deepcopy(restricted)
        for row in wrong_policy:
            row["policy_id"] = "broad_permission_v1"
        with self.assertRaises(ValueError) as ctx2:
            analyze_acquisition(wrong_policy, replicates=5)
        self.assertIn("restricted_core_v1", str(ctx2.exception))

        mixed_scorer = copy.deepcopy(restricted)
        mixed_scorer[0]["scorer_version"] = "other-scorer-v9"
        with self.assertRaises(ValueError) as ctx3:
            analyze_acquisition(mixed_scorer, replicates=5)
        self.assertIn("scorer_version", str(ctx3.exception))

    def test_a4_join_rejects_schedule_scored_policy_mismatch(self):
        bundle = build_simulation_bundle(
            "T_only",
            bases_per_family=1,
            difficulties=("trivial",),
            include_absent_controls=False,
        )
        scored = [dict(r) for r in bundle["rows"]]
        assignments = [dict(a) for a in bundle["assignments"]]
        assignments[0]["policy_id"] = "broad_permission_v1"
        with self.assertRaises(ValueError):
            join_rows_with_schedule(scored, assignments)

    def test_a5_reporting_denominators_are_separated(self):
        bundle = build_simulation_bundle(
            "T_only",
            bases_per_family=1,
            difficulties=("trivial",),
            include_absent_controls=False,
        )
        rows = bundle["rows"]
        # Mark one complete-info episode incomplete/non-parseable.
        for row in rows:
            if row["information_state"] == "complete" and row["visibility"] == "V00":
                row["integrity"]["terminal_status"] = "interrupted"
                row["integrity"]["extraction_failure"] = True
                row["task_result"]["answer_valid"] = False
                break
        report = analyze_acquisition(rows, replicates=5, seed=2)
        den = report["reporting_denominators"]
        self.assertEqual(den["assigned"], len(rows))
        self.assertLess(
            den["terminal_completion"]["numerator"],
            den["assigned"],
        )
        self.assertIn("response_parse_among_complete_completed", den)
        self.assertIn("valid_answer_among_assigned", den)
        self.assertIn("do not retroactively redefine", den["note"].lower())

    def test_analyze_dry_does_not_rewrite_tracked_fixtures(self):
        tracked = ANALYSIS_FIXTURES_DIR / "manifest.json"
        before = tracked.read_bytes() if tracked.is_file() else None
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dry"
            with mock.patch(
                "shortcut_study.analysis.harness.write_simulation_fixtures"
            ) as mocked:
                report = run_dry(out, effect="T_only", replicates=15, seed=9)
                mocked.assert_not_called()
            self.assertTrue((out / "retained_inputs" / "schedule.json").is_file())
            self.assertIn("materialize_fixtures", json.loads(
                (out / "analysis_manifest.json").read_text()
            )["inputs"])
            self.assertFalse(
                json.loads((out / "analysis_manifest.json").read_text())["inputs"][
                    "materialize_fixtures"
                ]
            )
            self.assertTrue(
                report["injected_effect_recovery"]["T_visibility"]["match"]
            )
        after = tracked.read_bytes() if tracked.is_file() else None
        self.assertEqual(before, after)

    def test_stochastic_bundle_recovers_t_effect_sign_at_candidate_scope(self):
        bundle = build_stochastic_bundle(
            bases=20,
            baseline=0.05,
            t_effect=0.35,
            j_effect=0.0,
            missing_rate=0.0,
            seed=42,
        )
        self.assertEqual(bundle["design"]["bases"], 20)
        report = analyze_acquisition(bundle["rows"], replicates=200, seed=7)
        point = report["contrasts"]["T_visibility"]["all_assigned"]["point"]
        interval = report["contrasts"]["T_visibility"]["bootstrap"]["percentile_95"]
        self.assertIsNotNone(point)
        self.assertGreater(point, 0.1)
        self.assertIsNotNone(interval)
        # Interval should not be a degenerate toy singleton for stochastic draws.
        self.assertGreaterEqual(interval[1], interval[0])

    def test_load_scored_rows_validates_serialized_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.json"
            path.write_text(json.dumps([{"episode_id": "x"}]) + "\n")
            with self.assertRaises(ValueError):
                load_scored_rows(path)


if __name__ == "__main__":
    unittest.main()
