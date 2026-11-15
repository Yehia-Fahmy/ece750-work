"""Four visibility packet filters and leakage guards."""

from __future__ import annotations

import json
import unittest

from shortcut_study.fixtures import build_episode_fixture, build_event_ledger_fixture
from shortcut_study.packets import (
    VISIBILITY_CHANNEL_MAP,
    assert_no_reviewer_leakage,
    filter_all_visibility_packets,
    project_auditor_packet,
    project_reviewer_packet,
)
from shortcut_study.schemas import validate


class PacketFilterTests(unittest.TestCase):
    def setUp(self):
        self.episode = build_episode_fixture(visibility="V11")
        self.ledger = build_event_ledger_fixture(
            self.episode["episode_id"], acquire_shortcut=True
        )

    def test_all_four_visibility_filters(self):
        packets = filter_all_visibility_packets(self.episode)
        self.assertEqual(set(packets), set(VISIBILITY_CHANNEL_MAP))
        for visibility, packet in packets.items():
            validate("reviewer_packet", packet)
            flags = VISIBILITY_CHANNEL_MAP[visibility]
            self.assertEqual(packet["channels_included"]["T"], flags["T"])
            self.assertEqual(packet["channels_included"]["J"], flags["J"])
            if flags["T"]:
                self.assertIsNotNone(packet["T"])
                self.assertIn("SECRET_T_MARKER_alpha", packet["T"][0]["text"])
            else:
                self.assertIsNone(packet["T"])
            if flags["J"]:
                self.assertIsNotNone(packet["J"])
                self.assertIn("SECRET_J_MARKER_beta", packet["J"]["text"])
            else:
                self.assertIsNone(packet["J"])
            assert_no_reviewer_leakage(packet, self.episode)

    def test_v00_omits_t_and_j_byte_for_byte(self):
        episode = build_episode_fixture(visibility="V00")
        packet = project_reviewer_packet(episode)
        blob = json.dumps(packet)
        self.assertNotIn("SECRET_T_MARKER_alpha", blob)
        self.assertNotIn("SECRET_J_MARKER_beta", blob)
        self.assertNotIn("events", packet)
        self.assertNotIn("actor_id", packet)

    def test_v01_includes_j_only(self):
        episode = build_episode_fixture(visibility="V01")
        packet = project_reviewer_packet(episode)
        self.assertIsNone(packet["T"])
        self.assertIsNotNone(packet["J"])
        blob = json.dumps(packet)
        self.assertNotIn("SECRET_T_MARKER_alpha", blob)
        self.assertIn("SECRET_J_MARKER_beta", blob)

    def test_v10_includes_t_only(self):
        episode = build_episode_fixture(visibility="V10")
        packet = project_reviewer_packet(episode)
        self.assertIsNotNone(packet["T"])
        self.assertIsNone(packet["J"])
        blob = json.dumps(packet)
        self.assertIn("SECRET_T_MARKER_alpha", blob)
        self.assertNotIn("SECRET_J_MARKER_beta", blob)

    def test_auditor_gets_full_record(self):
        packet = project_auditor_packet(self.episode, self.ledger)
        validate("auditor_packet", packet)
        self.assertIsNotNone(packet["T"])
        self.assertIsNotNone(packet["J"])
        self.assertTrue(packet["events"])
        self.assertIn("SECRET_T_MARKER_alpha", packet["T"][0]["text"])
        self.assertIn("SECRET_J_MARKER_beta", packet["J"]["text"])

    def test_leakage_guard_rejects_injected_events(self):
        episode = build_episode_fixture(visibility="V00")
        packet = project_reviewer_packet(episode)
        packet["events"] = self.ledger["events"]
        with self.assertRaises(AssertionError):
            assert_no_reviewer_leakage(packet, episode)


if __name__ == "__main__":
    unittest.main()
