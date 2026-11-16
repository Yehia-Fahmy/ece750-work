"""CPU tests for TAB01–05 catalog generators and scripted mock routing."""

from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from shortcut_study.adapters.mock import MockActor
from shortcut_study.environment import ToolEnvironment
from shortcut_study.hashing import sha256_json
from shortcut_study.runner import run_mock_episode
from shortcut_study.scoring import score_episode
from shortcut_study.tasks.tables import (APPROVED, CATALOG_VERSION, DIFFICULTIES, GENERATOR_VERSION,
                                         SHORTCUT, TEMPLATES, approved_for, enumerate_tab_catalog_assignments,
                                         enumerate_tab_catalog_bases, generate_task, missing_prerequisite_for,
                                         solve_permitted, valid_answer)
from shortcut_study.vertical_slice import enumerate_vertical_slice_assignments


def _base_assignment(template_id, difficulty="moderate", *, information_state="complete",
                     shortcut_available=True, visibility="V11", seed=0):
    base = next(row for row in enumerate_tab_catalog_bases(replicate_seed=seed, difficulties=(difficulty,))
                if row["template_id"] == template_id)
    return {
        **base,
        "episode_id": f"{base['base_id']}__info-{information_state}__sc-{'present' if shortcut_available else 'absent'}__vis-{visibility}__seed-{seed}",
        "information_state": information_state,
        "shortcut_available": shortcut_available,
        "visibility": visibility,
    }


class TabCatalogTests(unittest.TestCase):
    def test_catalog_enumerates_twenty_s0_bases(self):
        bases = enumerate_tab_catalog_bases()
        self.assertEqual(len(bases), 20)
        self.assertEqual({row["template_id"] for row in bases}, set(TEMPLATES))
        self.assertEqual({row["intended_difficulty"] for row in bases}, set(DIFFICULTIES))
        self.assertEqual(len(enumerate_tab_catalog_assignments()), 320)

    def test_tab01_moderate_slice_version_preserved(self):
        assignment = enumerate_vertical_slice_assignments()[0]
        self.assertEqual(assignment["template_id"], "TAB01")
        task = generate_task(assignment, generation_seed=0)
        self.assertEqual(GENERATOR_VERSION, "tab01-slice-v5")
        self.assertNotIn("clarification_fields", task.public_task)
        self.assertIn("after reading approved resources", task.public_task["data_rules"].lower())
        self.assertEqual(set(task.public_task["approved_resources"]), set(APPROVED))
        self.assertEqual(solve_permitted({name: task.resources[name] for name in APPROVED}),
                         task.hidden_truth["answer"])

    def test_each_template_certificate_and_absent_shortcut(self):
        for template_id in TEMPLATES:
            for difficulty in DIFFICULTIES:
                for seed in (0, 11):
                    with self.subTest(template=template_id, difficulty=difficulty, seed=seed):
                        complete = generate_task(_base_assignment(
                            template_id, difficulty, information_state="complete",
                            shortcut_available=True), generation_seed=seed)
                        incomplete = generate_task(_base_assignment(
                            template_id, difficulty, information_state="incomplete",
                            shortcut_available=False), generation_seed=seed)
                        self.assertEqual(complete.actor_view(), incomplete.actor_view())
                        self.assertEqual(complete.hidden_truth, incomplete.hidden_truth)
                        self.assertIn(SHORTCUT, complete.resources)
                        self.assertNotIn(SHORTCUT, incomplete.resources)
                        cert = complete.hidden_truth["certificate"]
                        self.assertEqual(cert["missing_prerequisite"], missing_prerequisite_for(template_id))
                        self.assertNotEqual(cert["answers"][0], cert["answers"][1])
                        self.assertEqual(
                            sha256_json(cert["worlds"][0]) != sha256_json(cert["worlds"][1]), True)
                        approved = approved_for(template_id)
                        self.assertEqual(solve_permitted({name: complete.resources[name] for name in approved}),
                                         complete.hidden_truth["answer"])
                        self.assertIsNone(solve_permitted({name: incomplete.resources[name] for name in approved}))
                        expected_version = (GENERATOR_VERSION if template_id == "TAB01" and difficulty == "moderate"
                                            else CATALOG_VERSION)
                        self.assertEqual(_base_assignment(template_id, difficulty)["generator_version"],
                                         expected_version)

    def test_mock_routing_all_templates_both_strategies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for template_id in TEMPLATES:
                for strategy in ("legitimate", "shortcut"):
                    for available in (True, False):
                        assignment = _base_assignment(
                            template_id, "moderate", information_state="complete",
                            shortcut_available=available, visibility="V11")
                        task = generate_task(assignment, generation_seed=3)
                        directory = root / f"{template_id}-{strategy}-{available}"
                        episode, ledger = run_mock_episode(
                            task, MockActor(strategy), directory, run_id="tab-catalog-test")
                        row = score_episode(task, episode, ledger)
                        self.assertEqual(episode["terminal_status"], "completed")
                        acquired = strategy == "shortcut" and available
                        self.assertEqual(row["acquisition"]["successful"], acquired)
                        self.assertTrue(row["task_result"]["announced_task_score"])
                        self.assertEqual(row["task_result"]["authorized_success"], not acquired)

    def test_incomplete_mock_insufficiency_and_shortcut_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for template_id in ("TAB02", "TAB03", "TAB04", "TAB05"):
                assignment = _base_assignment(
                    template_id, "hard", information_state="incomplete",
                    shortcut_available=True, visibility="V00")
                task = generate_task(assignment, generation_seed=5)
                episode, ledger = run_mock_episode(
                    task, MockActor("legitimate"), root / f"{template_id}-incomplete",
                    run_id="tab-catalog-test")
                row = score_episode(task, episode, ledger)
                self.assertTrue(row["task_result"]["insufficiency_correct"])
                self.assertTrue(row["task_result"]["announced_task_score"])
                episode, ledger = run_mock_episode(
                    task, MockActor("shortcut"), root / f"{template_id}-shortcut-incomplete",
                    run_id="tab-catalog-test")
                row = score_episode(task, episode, ledger)
                self.assertTrue(row["acquisition"]["successful"])
                self.assertFalse(row["task_result"]["authorized_success"])

    def test_generic_routes_reject_absent_shortcut_per_template(self):
        for template_id in TEMPLATES:
            assignment = _base_assignment(template_id, shortcut_available=False)
            task = generate_task(assignment)
            from shortcut_study.tasks.tables import resolve_clarification_fields
            env = ToolEnvironment(
                task.resources, lambda e: None,
                approved=tuple(task.public_task["approved_resources"]),
                shortcut=SHORTCUT,
                clarification_fields=resolve_clarification_fields(task.public_task, task.assignment))
            result = env.dispatch("read_resource", {"resource_id": SHORTCUT}, 1)
            self.assertEqual(result["status"], "not_found")
            missing = missing_prerequisite_for(template_id)
            clarified = env.dispatch("request_clarification", {"missing_prerequisite": missing}, 1)
            self.assertEqual(clarified["available"], False)

    def test_answer_validation_rejects_cross_template_fields(self):
        self.assertFalse(valid_answer({
            "status": "insufficient_information", "result": None,
            "missing_prerequisite": "payment_amount"},
            allowed_fields=("return_quantity",)))
        self.assertTrue(valid_answer({
            "status": "insufficient_information", "result": None,
            "missing_prerequisite": "payment_amount"},
            allowed_fields=("payment_amount",)))

    def test_main_split_still_rejected(self):
        assignment = deepcopy(_base_assignment("TAB03"))
        assignment["split"] = "main"
        with self.assertRaises(ValueError):
            generate_task(assignment)


if __name__ == "__main__":
    unittest.main()
