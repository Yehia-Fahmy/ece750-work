"""SW07-D / ECE-82: pre-freeze sim + forecast evidence; freeze stays unsigned."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from shortcut_study.analysis.compare import analyze_acquisition
from shortcut_study.analysis.harness import recovery_ok, run_dry
from shortcut_study.analysis.simulate import build_stochastic_bundle
from shortcut_study.freeze import (
    FreezeAuthorityError,
    compute_component_hashes,
    frozen_dir,
    load_json,
    validate_freeze_authority,
)
from shortcut_study.paths import CONFIGS_DIR, PACKAGE_ROOT

EVIDENCE = PACKAGE_ROOT / "results" / "qualification" / "sw07d-prefreeze-sim-forecast-v1.json"
SIM_DIR = PACKAGE_ROOT / "results" / "qualification" / "prefreeze-sim-sw07d-v1"
FORECAST = SIM_DIR / "forecast.json"
CHECKLIST = (
    PACKAGE_ROOT / "results" / "qualification" / "freeze-checklist-s0-tab-post-sw05.md"
)
STATE = PACKAGE_ROOT / "state.json"


class SW07DPrefreezeSimForecastTests(unittest.TestCase):
    def test_evidence_index_and_forecast_fit(self):
        self.assertTrue(EVIDENCE.is_file())
        index = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(index["package"], "SW07-D")
        self.assertFalse(index["signed"])
        self.assertFalse(index["g3_set"])
        self.assertFalse(index["submission_authorized"])
        self.assertTrue(index["cpu_only"])
        self.assertFalse(index["gpu_used"])
        self.assertEqual(index["results"]["forecast_verdict"], "FITS")
        self.assertTrue(index["results"]["fits_nov27"])
        self.assertTrue(index["results"]["fits_nov29"])
        self.assertTrue(index["results"]["deterministic_all_recovered"])

        forecast = json.loads(FORECAST.read_text(encoding="utf-8"))
        self.assertEqual(forecast["fit"]["verdict"], "FITS")
        self.assertLess(
            forecast["pipeline"]["required_gpu_hours_with_reserve"],
            forecast["windows"]["actor_gpu_hours_available_provisional"],
        )
        self.assertEqual(forecast["scope"]["live_judge_gpu_episodes"], 0)
        self.assertGreaterEqual(forecast["assumptions"]["reserve_fraction"], 0.25)
        # Conservative planning must not use clarification-only ~8s.
        self.assertGreater(forecast["assumptions"]["planning_actor_seconds_per_episode"], 20.0)

    def test_frozen_budgets_and_protocol_updated_but_unsigned(self):
        directory = frozen_dir()
        manifest = load_json(directory / "manifest.json")
        budgets = load_json(directory / "budgets.json")
        protocol = load_json(directory / "analysis_protocol.json")

        self.assertFalse(manifest["freeze"]["signed"])
        self.assertIsNone(manifest["freeze"]["accepting_owner"])
        self.assertIsNone(manifest["freeze"]["freeze_commit"])
        self.assertEqual(manifest["freeze"]["g3_status"], "not_started")
        self.assertFalse(manifest["submission_authorized"])
        self.assertEqual(budgets["forecast"]["status"], "measured_forecast_provisional_unsigned")
        self.assertEqual(budgets["forecast"]["verdict"], "FITS")
        self.assertTrue(protocol["simulation_before_freeze"]["done"])
        self.assertEqual(
            protocol["semantic"]["scope_decision"], "withdrawn_behavioral_only"
        )

        actual = compute_component_hashes(directory, manifest)
        self.assertEqual(manifest["freeze"]["component_sha256"], actual)

        report = validate_freeze_authority(directory, require_signed=False)
        self.assertFalse(report["signed"])
        with self.assertRaises(FreezeAuthorityError):
            validate_freeze_authority(directory, require_signed=True)

    def test_checklist_sim_forecast_checked_signature_blank(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("[x] Pre-freeze analysis simulation", text)
        self.assertIn("[x] Measured actor", text)
        self.assertIn("prefreeze-sim-sw07d-v1", text)
        self.assertIn("deliberately blank", text.lower())
        self.assertIn("_None — deliberately blank", text)
        self.assertIn("Independent freeze reviewer signature", text)
        # Remaining blocker must stay unchecked
        self.assertRegex(text, r"- \[ \] Independent freeze reviewer signature")

    def test_state_g3_untouched(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["gates"]["G3"], "not_started")
        self.assertFalse(state["constraints"]["submission_authorized"])

    def test_deterministic_recovery_smoke(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            report = run_dry(Path(tmp) / "dry", effect="T_only", replicates=40, seed=3)
            self.assertTrue(recovery_ok(report))

    def test_stochastic_candidate_scope_publishes_widths(self):
        bundle = build_stochastic_bundle(
            bases=20,
            baseline=0.05,
            t_effect=0.25,
            j_effect=0.0,
            seed=20261117,
            difficulties=("trivial", "moderate", "hard", "extreme"),
        )
        self.assertEqual(bundle["design"]["bases"], 20)
        report = analyze_acquisition(bundle["rows"], replicates=300, seed=20261116)
        p95 = report["contrasts"]["T_visibility"]["bootstrap"]["percentile_95"]
        self.assertIsNotNone(p95)
        self.assertGreater(p95[1] - p95[0], 0.05)

    def test_provisional_budgets_mirrored(self):
        path = CONFIGS_DIR / "provisional" / "s0-tab-only" / "budgets.json"
        budgets = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(budgets["status"], "draft_not_frozen")
        self.assertEqual(
            budgets["forecast"]["status"], "measured_forecast_provisional_unsigned"
        )


if __name__ == "__main__":
    unittest.main()
