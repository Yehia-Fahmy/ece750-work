"""SW08 / ECE-89: CPU regressions for signed-freeze main collection helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from shortcut_study.freeze import PROTOCOL_CANDIDATE, frozen_dir
from shortcut_study.main_collection import (
    _frozen_actor_settings,
    _frozen_limits,
    _load_frozen_assignments,
    summarize_main,
    write_progress,
)


FROZEN = frozen_dir(PROTOCOL_CANDIDATE)


class MainCollectionHelpersTests(unittest.TestCase):
    def test_load_signed_freeze_schedule_has_320_main_rows(self):
        assignments = _load_frozen_assignments(FROZEN)
        self.assertEqual(len(assignments), 320)
        self.assertTrue(all(row["split"] == "main" for row in assignments))
        limits = _frozen_limits(FROZEN)
        self.assertEqual(limits["max_model_turns"], 16)
        self.assertEqual(limits["max_tool_actions"], 12)
        settings = _frozen_actor_settings(FROZEN)
        self.assertEqual(settings["model_alias"], "shortcut-qwen3-4b")
        # ECE-90 errata: signed freeze sampling matches G2 qual (T=0.2).
        self.assertEqual(settings["sampling"]["temperature"], 0.2)
        self.assertEqual(settings["sampling"]["top_p"], 0.95)

    def test_summarize_retains_unattempted_denominator(self):
        assignments = _load_frozen_assignments(FROZEN)[:3]
        rows = [
            {
                "episode_id": assignments[0]["episode_id"],
                "terminal_status": "completed",
                "turns": [
                    {
                        "count_matches": True,
                        "native_reasoning_present": True,
                        "native_action_present": True,
                    }
                ],
                "recovery_verified": True,
                "audit_status": "prepared_no_judge",
                "elapsed_seconds": 1.0,
            }
        ]
        summary = summarize_main(
            assignments,
            rows,
            {"status": "ok"},
            failure="stopped",
            freeze_authority={
                "directory": str(FROZEN),
                "freeze_commit": "571d88865ee3d2d83ea152275b58436fccacc06c",
                "accepting_owner": "Yehia F",
            },
        )
        self.assertEqual(summary["assigned"], 3)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["terminal_counts"]["completed"], 1)
        self.assertEqual(summary["terminal_counts"]["not_attempted"], 2)
        self.assertFalse(summary["submission_authorized"])
        self.assertEqual(summary["semantic_scope"], "withdrawn_behavioral_only")

    def test_write_progress_is_durable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_progress(
                root,
                assigned=320,
                rows=[
                    {
                        "episode_id": "ep-1",
                        "terminal_status": "completed",
                    }
                ],
            )
            payload = json.loads((root / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["assigned"], 320)
            self.assertEqual(payload["recorded"], 1)
            self.assertEqual(payload["last_episode_id"], "ep-1")


if __name__ == "__main__":
    unittest.main()
