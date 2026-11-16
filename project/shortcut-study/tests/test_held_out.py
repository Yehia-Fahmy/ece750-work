"""CPU tests for S0 G2 held-out packaging (no GPU)."""

from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from shortcut_study.adapters.mock import MockActor
from shortcut_study.held_out import (build_split_reservations, evaluate_cpu_g2_structural_gates,
                                    package_g2_held_out, run_mock_held_out, s0_schedule)
from shortcut_study.runner import run_mock_episode
from shortcut_study.splits import check_split_disjointness
from shortcut_study.tasks.tables import (enumerate_tab_catalog_assignments, generate_task,
                                         smoke_assignments)


class HeldOutPackagingTests(unittest.TestCase):
    def test_smoke_schedule_is_eight_cells(self):
        rows = smoke_assignments()
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["split"] == "smoke" for row in rows))

    def test_s0_qualification_and_main_counts(self):
        self.assertEqual(len(s0_schedule("qualification")), 320)
        self.assertEqual(len(s0_schedule("main")), 320)
        self.assertEqual(len(s0_schedule("development")), 320)

    def test_split_fingerprints_are_disjoint(self):
        reservations = build_split_reservations()
        self.assertTrue(reservations["disjointness_checked"])
        self.assertEqual(reservations["episode_counts"]["qualification"], 320)
        self.assertEqual(reservations["fingerprint_counts"]["qualification"], 20)
        self.assertEqual(reservations["fingerprint_counts"]["main"], 20)
        # Cross-check helper still agrees when flattening base fingerprints as synthetic rows.
        flat = []
        for split, bases in reservations["bases_by_split"].items():
            for index, base in enumerate(bases):
                flat.append({
                    "episode_id": f"{base['base_id']}__probe-{index}",
                    "split": split,
                    "semantic_fingerprint": base["semantic_fingerprint"],
                    "base_id": base["base_id"],
                })
        check_split_disjointness(flat)

    def test_cpu_structural_gates_pass_without_accepting_g2(self):
        reservations = build_split_reservations()
        gates = evaluate_cpu_g2_structural_gates(reservations)
        self.assertTrue(gates["cpu_structural_passed"])
        self.assertFalse(gates["g2_accepted"])
        pending = [g for g in gates["gates"] if g["gpu_required"]]
        self.assertEqual(len(pending), 4)
        self.assertTrue(all(g["status"] == "pending_gpu" for g in pending))

    def test_mock_held_out_trivial_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = run_mock_held_out(
                Path(tmp) / "mock", strategy="legitimate", difficulties=("trivial",))
            self.assertEqual(summary["assigned"], 80)  # 5 templates × 1 difficulty × 16
            self.assertEqual(summary["completed"], 80)
            self.assertEqual(summary["evidence_kind"], "scripted_mock_not_model_observation")

    def test_main_generates_but_mock_runner_refuses(self):
        assignment = enumerate_tab_catalog_assignments(split="main", difficulties=("trivial",))[0]
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        self.assertEqual(task.assignment["split"], "main")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                run_mock_episode(task, MockActor("legitimate"), Path(tmp) / "main-ep",
                                 run_id="held-out-test")

    def test_package_g2_writes_schedules_and_refuses_main_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pkg"
            evidence = package_g2_held_out(
                out, mock_strategy="legitimate", mock_difficulties=("trivial",))
            self.assertTrue(evidence["cpu_gates"]["cpu_structural_passed"])
            self.assertFalse(evidence["g2_accepted"])
            main = (out / "schedules" / "schedule-main.json").read_text()
            self.assertIn('"executable": false', main)
            self.assertTrue((out / "split-reservations.json").exists())
            self.assertTrue((out / "g2-gate-evaluation.json").exists())

    def test_qualification_seed_differs_from_development(self):
        dev = enumerate_tab_catalog_assignments(split="development", difficulties=("moderate",))
        qual = enumerate_tab_catalog_assignments(split="qualification", difficulties=("moderate",))
        self.assertNotEqual(dev[0]["generation_seed"], qual[0]["generation_seed"])
        self.assertNotEqual(dev[0]["base_id"], qual[0]["base_id"])
        t_dev = generate_task(dev[0], generation_seed=dev[0]["generation_seed"])
        t_qual = generate_task(qual[0], generation_seed=qual[0]["generation_seed"])
        # Same template+difficulty across splits must not share fingerprints.
        same_template = [
            (a, b) for a in [t_dev] for b in [t_qual]
            if a.assignment["template_id"] == b.assignment["template_id"]
            and a.assignment["intended_difficulty"] == b.assignment["intended_difficulty"]
        ]
        self.assertEqual(len(same_template), 1)
        self.assertNotEqual(same_template[0][0].semantic_fingerprint,
                            same_template[0][1].semantic_fingerprint)


if __name__ == "__main__":
    unittest.main()
