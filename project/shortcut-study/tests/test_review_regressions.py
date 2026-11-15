"""Regressions from PR #7 contract review."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import ValidationError

from shortcut_study.fixtures import (
    build_episode_fixture,
    build_event_ledger_fixture,
    load_fixture,
    write_contract_fixtures,
)
from shortcut_study.ids import text_digest
from shortcut_study.hashing import sha256_json
from shortcut_study.packets import (
    assert_no_reviewer_leakage,
    project_auditor_packet,
    project_reviewer_packet,
)
from shortcut_study.schemas import validate


class ReviewRegressionTests(unittest.TestCase):
    def test_missing_submission_survives_record_and_packet_round_trips(self):
        for status in (
            "not_attempted", "interrupted", "model_format_failure",
            "tool_failure", "context_limit", "budget_limit",
        ):
            for visibility in ("V00", "V01", "V10", "V11"):
                with self.subTest(status=status, visibility=visibility):
                    episode = build_episode_fixture(
                        terminal_status=status, visibility=visibility,
                        include_t=False, include_a=False, include_j=False,
                    )
                    validate("episode", json.loads(json.dumps(episode)))
                    ledger = build_event_ledger_fixture(episode["episode_id"])
                    ledger["events"] = []
                    ledger["integrity_sha256"] = sha256_json({
                        "episode_id": episode["episode_id"], "events": [],
                    })
                    validate("events", ledger)
                    self.assertIsNone(project_reviewer_packet(episode)["A"])
                    self.assertIsNone(project_auditor_packet(episode, ledger)["A"])

    def test_completed_episode_still_requires_valid_submission(self):
        for answer in (None, {}, {"status": "answer", "result": 42}):
            with self.subTest(answer=answer):
                episode = build_episode_fixture()
                episode["channels"]["A"] = answer
                with self.assertRaises(ValidationError):
                    validate("episode", episode)

    def test_overlapping_text_in_independent_channels_is_allowed(self):
        for visibility in ("V00", "V01", "V10", "V11"):
            with self.subTest(visibility=visibility):
                episode = build_episode_fixture(visibility=visibility, result="42")
                for channel in (episode["channels"]["T"][0], episode["channels"]["J"]):
                    channel.update(text="42", text_sha256=text_digest("42"))
                validate("episode", episode)
                packet = project_reviewer_packet(episode)
                self.assertEqual(packet["A"], episode["channels"]["A"])
                self.assertEqual(packet["T"], episode["channels"]["T"] if visibility in ("V10", "V11") else None)
                self.assertEqual(packet["J"], episode["channels"]["J"] if visibility in ("V01", "V11") else None)

    def test_hidden_content_cannot_be_injected_into_visible_fields(self):
        episode = build_episode_fixture(visibility="V01")
        original = project_reviewer_packet(episode)
        hidden = episode["channels"]["T"][0]["text"]
        for field in ("A", "J", "task_metadata"):
            with self.subTest(field=field):
                packet = copy.deepcopy(original)
                if field == "A":
                    packet[field]["result"] = hidden
                elif field == "J":
                    packet[field].update(text=hidden, text_sha256=text_digest(hidden))
                else:
                    packet[field]["template_id"] = hidden
                with self.assertRaises(AssertionError):
                    assert_no_reviewer_leakage(packet, episode)

    def test_fixture_score_matches_recorded_restricted_acquisition(self):
        with tempfile.TemporaryDirectory() as directory:
            generated = write_contract_fixtures(Path(directory))
            for source in (load_fixture, lambda name: json.loads(generated[name].read_text())):
                ledger = source("events/complete_present_v11.json")
                scored = source("scored/complete_present_v11.json")
                acquired = next(event for event in ledger["events"] if event.get("acquisition_success"))
                self.assertEqual(ledger["episode_id"], scored["episode_id"])
                self.assertEqual(acquired["policy_classification"], "restricted")
                self.assertTrue(scored["acquisition"]["attempted"])
                self.assertTrue(scored["acquisition"]["successful"])
                self.assertEqual(scored["acquisition"]["first_event_id"], acquired["event_id"])
                self.assertEqual(scored["acquisition"]["resource_id"], acquired["resource_id"])
                self.assertTrue(scored["compliance"]["restricted_access"])
                self.assertFalse(scored["compliance"]["authorized_under_policy"])
                self.assertFalse(scored["task_result"]["authorized_success"])
                self.assertTrue(scored["task_result"]["factual_correct"])


if __name__ == "__main__":
    unittest.main()
