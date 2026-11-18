"""SW07-D / ECE-82: pre-freeze sim + forecast evidence; ECE-87 may sign freeze later."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from shortcut_study.analysis.compare import analyze_acquisition
from shortcut_study.analysis.harness import recovery_ok, run_dry
from shortcut_study.analysis.simulate import build_stochastic_bundle
from shortcut_study.freeze import (
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
        # Historical SW07-D evidence package itself remains an unsigned prep artifact.
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

    def test_frozen_budgets_and_protocol_retain_forecast_under_signed_freeze(self):
        directory = frozen_dir()
        manifest = load_json(directory / "manifest.json")
        budgets = load_json(directory / "budgets.json")
        protocol = load_json(directory / "analysis_protocol.json")

        # ECE-87 signs the freeze; SW07-D forecast verdict and behavioral scope remain.
        self.assertTrue(manifest["freeze"]["signed"])
        self.assertEqual(manifest["freeze"]["accepting_owner"], "Yehia F")
        self.assertEqual(manifest["freeze"]["g3_status"], "accepted")
        self.assertFalse(manifest["submission_authorized"])
        self.assertEqual(budgets["forecast"]["verdict"], "FITS")
        self.assertIn(budgets["forecast"]["status"], {
            "measured_forecast_provisional_unsigned",
            "measured_forecast_frozen_signed",
        })
        self.assertTrue(protocol["simulation_before_freeze"]["done"])
        self.assertEqual(
            protocol["semantic"]["scope_decision"], "withdrawn_behavioral_only"
        )

        actual = compute_component_hashes(directory, manifest)
        self.assertEqual(manifest["freeze"]["component_sha256"], actual)

        report = validate_freeze_authority(directory, require_signed=True)
        self.assertTrue(report["signed"])
        self.assertEqual(report["authority"], "accepted")

    def test_checklist_sim_forecast_and_signature_filled(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("[x] Pre-freeze analysis simulation", text)
        self.assertIn("[x] Measured actor", text)
        self.assertIn("prefreeze-sim-sw07d-v1", text)
        self.assertIn("Independent freeze reviewer signature", text)
        self.assertRegex(text, r"- \[x\] Independent freeze reviewer signature")
        self.assertIn("Yehia F", text)
        self.assertIn("571d88865ee3d2d83ea152275b58436fccacc06c", text)
        self.assertIn("2026-11-17T22:45:00-05:00", text)
        self.assertNotIn("_None — deliberately blank", text)

    def test_state_g3_accepted_submission_false(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["gates"]["G3"], "accepted")
        self.assertFalse(state["constraints"]["submission_authorized"])
        self.assertEqual(state["frozen_protocol"], "s0-tab-v0")

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
