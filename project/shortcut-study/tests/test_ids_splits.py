"""Stable IDs, fingerprints, and split disjointness."""

from __future__ import annotations

import unittest

from shortcut_study.fixtures import build_episode_fixture
from shortcut_study.ids import make_episode_id, semantic_fingerprint
from shortcut_study.splits import check_split_disjointness


class IdAndSplitTests(unittest.TestCase):
    def test_episode_id_stable(self):
        episode_id = make_episode_id(
            base_id="vs-tab01-reconciliation-001",
            information_state="complete",
            shortcut_available=True,
            visibility="V00",
            replicate_seed=0,
        )
        self.assertEqual(
            episode_id,
            "vs-tab01-reconciliation-001__info-complete__sc-present__vis-V00__seed-0",
        )

    def test_semantic_fingerprint_stable(self):
        payload = {
            "template_id": "TAB01",
            "family": "tables",
            "intended_difficulty": "moderate",
            "mechanism": "prior_agent_notes",
            "public_task": {"question": "q"},
            "hidden_world": {"answer": 1},
        }
        self.assertEqual(semantic_fingerprint(payload), semantic_fingerprint(payload))

    def test_split_disjointness_ok_within_split(self):
        records = [
            build_episode_fixture(visibility="V00", split="development"),
            build_episode_fixture(visibility="V01", split="development"),
        ]
        # Same fingerprint across matched cells in one split is allowed.
        check_split_disjointness(records)

    def test_split_disjointness_rejects_cross_split_fingerprint(self):
        a = build_episode_fixture(visibility="V00", split="development")
        b = build_episode_fixture(visibility="V00", split="main")
        # Force identical fingerprint with different episode ids via visibility
        # already differs episode_id; change split only.
        b["semantic_fingerprint"] = a["semantic_fingerprint"]
        b["episode_id"] = a["episode_id"] + "-main"
        with self.assertRaises(AssertionError):
            check_split_disjointness([a, b])

    def test_duplicate_episode_id_rejected(self):
        a = build_episode_fixture(visibility="V11")
        b = build_episode_fixture(visibility="V11")
        with self.assertRaises(AssertionError):
            check_split_disjointness([a, b])


if __name__ == "__main__":
    unittest.main()
