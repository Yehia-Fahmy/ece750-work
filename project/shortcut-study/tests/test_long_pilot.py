"""CPU tests for development-split long-pilot schedule (no GPU)."""

import unittest

from shortcut_study.qualification import long_pilot_assignments


class LongPilotScheduleTests(unittest.TestCase):
    def test_long_pilot_assignments_are_ten_development_cells(self):
        rows = long_pilot_assignments()
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["episode_id"] for row in rows}), 10)
        for row in rows:
            self.assertEqual(row["split"], "development")
            self.assertEqual(row["information_state"], "complete")
            self.assertIs(row["shortcut_available"], False)
            self.assertEqual(row["visibility"], "V00")
            self.assertIn(row["intended_difficulty"], ("hard", "extreme"))
            self.assertNotEqual(row["split"], "qualification")
            self.assertNotEqual(row["split"], "main")


if __name__ == "__main__":
    unittest.main()
