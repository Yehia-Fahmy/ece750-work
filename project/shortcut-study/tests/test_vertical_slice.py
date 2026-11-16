"""16-episode vertical-slice path is enumerable and complete."""

from __future__ import annotations

import unittest

from shortcut_study.fixtures import (
    build_episode_fixture,
    build_event_ledger_fixture,
)
from shortcut_study.packets import project_auditor_packet, project_reviewer_packet
from shortcut_study.vertical_slice import (
    enumerate_vertical_slice_assignments,
    vertical_slice_path_summary,
)


class VerticalSlicePathTests(unittest.TestCase):
    def test_sixteen_assignments(self):
        rows = enumerate_vertical_slice_assignments()
        self.assertEqual(len(rows), 16)
        ids = [row["episode_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        visibilities = {row["visibility"] for row in rows}
        self.assertEqual(visibilities, {"V00", "V01", "V10", "V11"})
        infos = {row["information_state"] for row in rows}
        self.assertEqual(infos, {"complete", "incomplete"})
        availability = {row["shortcut_available"] for row in rows}
        self.assertEqual(availability, {True, False})
        for row in rows:
            self.assertEqual(row["mechanism"], "prior_agent_notes")
            self.assertEqual(row["template_id"], "TAB01")
            self.assertEqual(row["split"], "development")

    def test_path_summary_marks_no_gpu(self):
        summary = vertical_slice_path_summary()
        self.assertEqual(summary["episode_count"], 16)
        self.assertFalse(summary["gpu_run_authorized"])
        self.assertTrue(summary["mock_actor_first"])
        self.assertEqual(len(summary["capability_probe_episode_ids"]), 2)

    def test_fixture_covers_slice_mechanics(self):
        """Contract-level stubs for demonstrations WP02/WP03 must implement."""
        complete_present = build_episode_fixture(
            visibility="V11",
            information_state="complete",
            shortcut_available=True,
        )
        ledger_present = build_event_ledger_fixture(
            complete_present["episode_id"],
            acquire_shortcut=True,
            shortcut_available=True,
        )
        self.assertTrue(
            any(event.get("acquisition_success") for event in ledger_present["events"])
        )

        incomplete_absent = build_episode_fixture(
            visibility="V00",
            information_state="incomplete",
            shortcut_available=False,
            answer_status="insufficient_information",
            result=None,
        )
        ledger_absent = build_event_ledger_fixture(
            incomplete_absent["episode_id"],
            acquire_shortcut=True,
            shortcut_available=False,
        )
        absent_reads = [
            event
            for event in ledger_absent["events"]
            if event.get("acquisition_attempt")
        ]
        self.assertTrue(absent_reads)
        self.assertTrue(all(not event["content_delivered"] for event in absent_reads))
        self.assertTrue(all(not event["acquisition_success"] for event in absent_reads))

        reviewer = project_reviewer_packet(incomplete_absent)
        self.assertIsNone(reviewer["T"])
        self.assertIsNone(reviewer["J"])
        auditor = project_auditor_packet(complete_present, ledger_present)
        self.assertIsNotNone(auditor["T"])
        self.assertIsNotNone(auditor["J"])
        self.assertTrue(auditor["events"])

        interrupted = build_episode_fixture(
            visibility="V10",
            terminal_status="interrupted",
            include_j=False,
        )
        self.assertEqual(interrupted["terminal_status"], "interrupted")
        self.assertIsNone(interrupted["channels"]["J"])


if __name__ == "__main__":
    unittest.main()
