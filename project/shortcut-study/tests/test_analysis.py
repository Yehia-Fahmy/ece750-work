"""WP07 analysis scaffolding: injected effects, missingness, null warnings."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from shortcut_study.analysis.aggregate import assigned_denominator, missingness_bounds
from shortcut_study.analysis.compare import analyze_acquisition, confirmatory_contrasts
from shortcut_study.analysis.harness import recovery_ok, run_analyze, run_dry
from shortcut_study.analysis.metrics import cell_rates, zero_event_warnings
from shortcut_study.analysis.semantic import (
    label_error_sensitivity,
    weighted_review_diagnostics,
)
from shortcut_study.analysis.simulate import (
    INJECTED_EFFECTS,
    build_simulation_bundle,
    write_simulation_fixtures,
)


class AnalysisScaffoldTests(unittest.TestCase):
    def test_confirmatory_pair(self):
        self.assertEqual(confirmatory_contrasts(), ("T_visibility", "J_visibility"))

    def test_injected_T_only_recovered(self):
        bundle = build_simulation_bundle("T_only")
        report = analyze_acquisition(bundle["rows"], replicates=50, seed=1)
        for name, expected in bundle["expected_contrasts"].items():
            point = report["contrasts"][name]["all_assigned"]["point"]
            self.assertEqual(point, expected, name)

    def test_injected_J_and_both_recovered(self):
        for effect in ("J_only", "both"):
            bundle = build_simulation_bundle(effect)
            report = analyze_acquisition(bundle["rows"], replicates=50, seed=2)
            for name, expected in bundle["expected_contrasts"].items():
                self.assertEqual(
                    report["contrasts"][name]["all_assigned"]["point"],
                    expected,
                    f"{effect}:{name}",
                )

    def test_null_zero_event_warning(self):
        bundle = build_simulation_bundle("null")
        rates = cell_rates(bundle["rows"])
        warnings = zero_event_warnings(rates)
        self.assertIn(
            "zero_observed_acquisitions: do_not_report_degenerate_zero_width_bootstrap_as_zero_risk",
            warnings,
        )
        report = analyze_acquisition(bundle["rows"], replicates=30, seed=3)
        self.assertEqual(report["contrasts"]["T_visibility"]["all_assigned"]["point"], 0.0)
        self.assertTrue(any("zero_observed_acquisitions" in w for w in report["warnings"]))

    def test_missingness_bounds_widen(self):
        known = missingness_bounds([True, False, False, True])
        self.assertEqual(known["fraction_bounds"], [0.5, 0.5])
        missing = missingness_bounds([True, False, None, True])
        self.assertEqual(missing["fraction_bounds"], [0.5, 0.75])
        bundle = build_simulation_bundle(
            "T_only",
            missing_block=("sim-tab-eas-000", "complete", "V10"),
        )
        report = analyze_acquisition(bundle["rows"], replicates=40, seed=4)
        bounds = report["contrasts"]["T_visibility"]["all_assigned"]["bounds"]
        self.assertIsNotNone(bounds)
        self.assertLess(bounds[0], bounds[1])
        self.assertIsNone(report["contrasts"]["T_visibility"]["all_assigned"]["point"])
        denom = assigned_denominator(bundle["rows"])
        self.assertGreater(denom["acquisition_bounds"]["unknown"], 0)

    def test_absent_controls_not_in_primary_rates(self):
        bundle = build_simulation_bundle("T_only", include_absent_controls=True)
        rates = cell_rates(bundle["rows"])
        # 1 family × 2 difficulties × 4 bases × 2 info states = 16 per cell
        self.assertEqual(rates["V00"]["assigned"], 16)
        self.assertEqual(rates["V10"]["positive"], 16)

    def test_dry_harness_writes_release_and_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dry"
            report = run_dry(out, effect="T_only", replicates=40, seed=5)
            self.assertTrue(recovery_ok(report))
            self.assertTrue((out / "analysis_report.json").is_file())
            self.assertTrue((out / "analysis_manifest.json").is_file())
            manifest = json.loads((out / "analysis_manifest.json").read_text())
            self.assertFalse(manifest["frozen_main_results"])
            self.assertEqual(
                manifest["evidence_kind"],
                "synthetic_injected_effect_not_actor_observation",
            )

    def test_analyze_on_materialized_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fixtures"
            write_simulation_fixtures(root)
            out = Path(tmp) / "from-fixtures"
            report = run_analyze(
                root / "J_only" / "analysis_rows.json",
                root / "J_only" / "schedule.json",
                out,
                replicates=40,
                seed=6,
            )
            expected = INJECTED_EFFECTS["J_only"]["expected"]
            self.assertEqual(
                report["contrasts"]["J_visibility"]["all_assigned"]["point"],
                expected["J_visibility"],
            )
            self.assertEqual(
                report["contrasts"]["T_visibility"]["all_assigned"]["point"],
                expected["T_visibility"],
            )

    def test_analyze_refuses_missing_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing"
            with self.assertRaises(FileNotFoundError) as ctx:
                run_analyze(
                    Path(tmp) / "no-scored",
                    Path(tmp) / "no-schedule",
                    out,
                    replicates=10,
                    seed=7,
                )
            self.assertIn("TBD", str(ctx.exception))

    def test_weighted_review_and_label_sensitivity(self):
        rows = [
            {
                "primary_label": "disclosed",
                "review_label": "disclosed",
                "selection_probability": 0.1,
                "uncertain": False,
            },
            {
                "primary_label": "omitted",
                "review_label": "disclosed",
                "selection_probability": 1.0,
                "uncertain": False,
            },
            {"primary_label": "omitted", "review_label": None},
        ]
        diag = weighted_review_diagnostics(rows)
        self.assertEqual(diag["reviewed"], 2)
        self.assertEqual(diag["disagree"], 1)
        self.assertGreater(diag["weighted_disagreement_mass"], 0)
        sens = label_error_sensitivity({"T_visibility": 0.5}, flip_rate=0.1)
        self.assertEqual(sens["envelopes"]["T_visibility"]["envelope"], [0.4, 0.6])


if __name__ == "__main__":
    unittest.main()
