"""Policy × information-state matrix and development configs."""

from __future__ import annotations

import unittest

from shortcut_study.config import load_development_config, policy_matrix_rows
from shortcut_study.packets import VISIBILITY_CHANNEL_MAP


class PolicyMatrixTests(unittest.TestCase):
    def test_visibility_config_matches_packet_map(self):
        visibility = load_development_config("visibility")
        self.assertEqual(set(visibility["cells"]), set(VISIBILITY_CHANNEL_MAP))
        for cell, flags in VISIBILITY_CHANNEL_MAP.items():
            cell_cfg = visibility["cells"][cell]
            self.assertEqual(cell_cfg["include_T"], flags["T"])
            self.assertEqual(cell_cfg["include_J"], flags["J"])
            self.assertTrue(cell_cfg["notice"])

    def test_policy_information_state_matrix(self):
        rows = policy_matrix_rows()
        self.assertEqual(len(rows), 4)
        seen = {
            (row["information_state"], row["shortcut_available"]) for row in rows
        }
        self.assertEqual(
            seen,
            {
                ("complete", True),
                ("complete", False),
                ("incomplete", True),
                ("incomplete", False),
            },
        )
        for row in rows:
            self.assertEqual(row["policy_id"], "restricted_core_v1")
            self.assertFalse(row["expected_absent_routes_recoverable"])

    def test_budgets_and_boundaries_provisional(self):
        budgets = load_development_config("budgets")
        boundaries = load_development_config("a_t_j_boundaries")
        self.assertEqual(budgets["status"], "provisional_until_freeze")
        self.assertEqual(budgets["development"]["max_tool_actions"], 12)
        self.assertEqual(
            boundaries["reviewer_routing"]["T"], ["V10", "V11"]
        )
        self.assertEqual(
            boundaries["research_auditor"]["always_includes"],
            ["A", "T", "J", "events"],
        )


if __name__ == "__main__":
    unittest.main()
