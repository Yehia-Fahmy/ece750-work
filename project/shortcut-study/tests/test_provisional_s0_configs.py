"""Guards for WP08/G3 provisional S0 drafts — must stay unsigned draft configs.

SW07-C may commit an unsigned ``configs/frozen/<version>/`` materialization.
These draft invariants still apply to ``configs/provisional/``; frozen-path
authority is covered by ``test_frozen_main_path.py``.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from shortcut_study.paths import CONFIGS_DIR, PACKAGE_ROOT

PROVISIONAL_DIR = CONFIGS_DIR / "provisional" / "s0-tab-only"
CHECKLIST = PACKAGE_ROOT / "results" / "qualification" / "freeze-checklist-s0-tab-draft.md"
EVIDENCE = PACKAGE_ROOT / "results" / "qualification" / "wp08-freeze-draft-v1.json"
FROZEN_DIR = CONFIGS_DIR / "frozen"


def _load(name: str) -> dict:
    with (PROVISIONAL_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


class ProvisionalS0ConfigTests(unittest.TestCase):
    def test_provisional_tree_exists_and_stays_draft(self):
        self.assertTrue(PROVISIONAL_DIR.is_dir())
        self.assertTrue((PROVISIONAL_DIR / "manifest.json").is_file())
        # If a frozen tree exists, it must not be soft-signed via the provisional path.
        if FROZEN_DIR.exists():
            for manifest_path in FROZEN_DIR.glob("*/manifest.json"):
                frozen = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertFalse(
                    frozen.get("freeze", {}).get("signed") is True,
                    f"{manifest_path} must remain unsigned until Yehia signs",
                )

    def test_manifest_unsigned(self):
        manifest = _load("manifest.json")
        self.assertEqual(manifest["status"], "draft_not_frozen")
        self.assertEqual(manifest["protocol_candidate"], "s0-tab-v0")
        self.assertFalse(manifest["freeze"]["signed"])
        self.assertIsNone(manifest["freeze"]["frozen_directory"])
        self.assertIsNone(manifest["freeze"]["freeze_commit"])

    def test_scope_is_s0_tab_320(self):
        scope = _load("scope.json")
        self.assertEqual(scope["tier"], "S0")
        self.assertEqual(scope["families"], ["tables"])
        self.assertEqual(scope["base_scenarios"], 20)
        self.assertEqual(scope["primary_actor_episodes"], 320)
        self.assertEqual(scope["replicate_seeds"], [0])
        self.assertFalse(scope["optional_second_actor"])

    def test_split_reservations_disjoint(self):
        splits = _load("splits_reservation.json")
        ranges = {
            name: tuple(cfg["generation_seed_inclusive_range"])
            for name, cfg in splits["reservations"].items()
        }
        self.assertEqual(set(ranges), {"smoke", "development", "qualification", "main"})
        ordered = sorted(ranges.items(), key=lambda item: item[1][0])
        for (_, left), (_, right) in zip(ordered, ordered[1:]):
            self.assertLess(left[1], right[0], "generation_seed ranges must not overlap")
        self.assertEqual(
            splits["reservations"]["development"]["grandfathered"]["generation_seed"],
            0,
        )
        self.assertEqual(
            splits["reservations"]["main"]["provisional_generation_seed"],
            2000,
        )

    def test_schedule_not_materialized(self):
        schedule = _load("schedule_plan.json")
        self.assertFalse(schedule["materialization"]["done"])
        self.assertEqual(schedule["assigned_denominator"]["primary_actor_episodes"], 320)

    def test_checklist_all_unchecked(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("DRAFT", text)
        self.assertNotIn("- [x]", text)
        self.assertGreaterEqual(text.count("- [ ]"), 17)
        self.assertIn("deliberately blank", text.lower())

    def test_evidence_marker(self):
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "draft_not_frozen")
        self.assertFalse(evidence["signed"])
        self.assertFalse(evidence["frozen_directory_created"])
        self.assertEqual(evidence["checklist_items_checked"], 0)

    def test_required_component_files(self):
        manifest = _load("manifest.json")
        for relative in manifest["components"].values():
            path = PROVISIONAL_DIR / relative
            self.assertTrue(path.is_file(), relative)
            doc = json.loads(path.read_text(encoding="utf-8"))
            status = doc.get("status") or doc.get("protocol_status")
            self.assertIsNotNone(status)
            self.assertTrue(
                ("draft" in status)
                or status == "provisional_reservation_not_frozen",
                status,
            )


if __name__ == "__main__":
    unittest.main()
