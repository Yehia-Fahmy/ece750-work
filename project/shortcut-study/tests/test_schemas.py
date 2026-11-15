"""Round-trip episode/event and derived-row schema validation."""

from __future__ import annotations

import unittest

from shortcut_study.fixtures import (
    build_episode_fixture,
    build_event_ledger_fixture,
    build_scored_row_fixture,
    build_semantic_audit_fixture,
    write_contract_fixtures,
)
from shortcut_study.schemas import SCHEMA_FILES, load_schema, validate
from shortcut_study.scoring_fields import assert_source_of_truth_consistent


class SchemaRoundTripTests(unittest.TestCase):
    def test_all_schema_files_load(self):
        for name in SCHEMA_FILES:
            schema = load_schema(name)
            self.assertIn("$schema", schema)
            self.assertIn("title", schema)

    def test_episode_and_event_round_trip(self):
        episode = build_episode_fixture()
        validate("episode", episode)
        ledger = build_event_ledger_fixture(episode["episode_id"], acquire_shortcut=True)
        validate("events", ledger)
        self.assertEqual(ledger["episode_id"], episode["episode_id"])

    def test_scored_and_audit_round_trip(self):
        episode = build_episode_fixture(visibility="V10")
        scored = build_scored_row_fixture(episode)
        audit = build_semantic_audit_fixture(episode)
        validate("scored_row", scored)
        validate("semantic_audit", audit)
        assert_source_of_truth_consistent(scored)

    def test_write_fixtures_validate(self):
        paths = write_contract_fixtures()
        self.assertIn("episodes/complete_present_v11.json", paths)
        self.assertIn("vertical_slice/assignments.json", paths)
        for relative in (
            "episodes/complete_present_v11.json",
            "events/complete_present_v11.json",
            "scored/complete_present_v11.json",
            "audit/complete_present_v11.json",
        ):
            self.assertTrue(paths[relative].is_file())


if __name__ == "__main__":
    unittest.main()
