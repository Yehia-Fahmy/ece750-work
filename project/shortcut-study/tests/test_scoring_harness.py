"""WP04 deterministic scoring fixtures and harness (CPU only)."""

from pathlib import Path
import tempfile
import unittest

from shortcut_study.scoring.harness import (
    available_templates,
    load_cases,
    run_case,
    run_fixture_suite,
    write_development_evidence,
)


class ScoringHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.catalog = load_cases()

    def test_case_catalog_covers_acceptance_criteria(self):
        acceptance = {case["acceptance"] for case in self.catalog["cases"]}
        self.assertEqual(
            acceptance,
            {
                "correct_answers_separate_from_compliance",
                "attempts_vs_acquisitions",
                "missing_data_refusal_vs_lucky_guess",
                "genuine_required_check_omissions",
                "no_mental_calculation_inference",
            },
        )
        self.assertIn("TAB01", available_templates())

    def test_each_case_passes_on_tab01(self):
        for case in self.catalog["cases"]:
            with self.subTest(case=case["case_id"]):
                result = run_case(case, self.root / case["case_id"])
                self.assertTrue(result["passed"], result["mismatches"])
                if case["acceptance"] == "no_mental_calculation_inference":
                    self.assertEqual(result["calculate_event_count"], 0)
                    self.assertNotIn("mental", str(result["scored"]).lower())
                    self.assertNotIn("process_claim", result["scored"])

    def test_suite_summary_and_evidence(self):
        summary = run_fixture_suite(self.root / "suite", templates=("TAB01",))
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["passed"], summary["assigned"])
        self.assertFalse(summary["gpu"])
        self.assertFalse(summary["main_collection"])
        evidence = write_development_evidence(summary, self.root / "evidence.json")
        self.assertTrue(evidence.exists())

    def test_unknown_template_is_explicit(self):
        case = self.catalog["cases"][0]
        with self.assertRaisesRegex(ValueError, "unknown template|no assignment"):
            run_case(case, self.root / "missing-template", template_id="TAB99")

    def test_catalog_templates_pass_after_adaptation(self):
        self.assertIn("TAB02", available_templates())
        case = self.catalog["cases"][0]
        adapted = {
            **case,
            "case_id": f"{case['case_id']}__tab02",
            "assignment": {**case["assignment"], "template_id": "TAB02"},
        }
        result = run_case(adapted, self.root / "tab02", template_id="TAB02")
        self.assertTrue(result["passed"], result["mismatches"])
        self.assertEqual(result["template_id"], "TAB02")


if __name__ == "__main__":
    unittest.main()
