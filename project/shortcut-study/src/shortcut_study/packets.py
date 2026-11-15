"""Pure visibility projections for task-reviewer and research-auditor packets."""

from __future__ import annotations

import copy
import json
from typing import Any, Mapping

from .hashing import sha256_json
from .schemas import validate

# Channel inclusion by visibility cell (A always included).
VISIBILITY_CHANNEL_MAP = {
    "V00": {"A": True, "T": False, "J": False},
    "V01": {"A": True, "T": False, "J": True},
    "V10": {"A": True, "T": True, "J": False},
    "V11": {"A": True, "T": True, "J": True},
}

# Fields that must never appear on a task-reviewer packet.
REVIEWER_FORBIDDEN_TOP_LEVEL = frozenset(
    {
        "events",
        "event_ledger",
        "hidden_truth",
        "hidden_truth_hash",
        "channels",  # raw episode channels object
        "actor_id",
        "raw_requests",
        "raw_responses",
        "T_full",
        "J_full",
        "trace",
        "justification_hidden",
    }
)


def channel_flags(visibility: str) -> dict[str, bool]:
    if visibility not in VISIBILITY_CHANNEL_MAP:
        raise ValueError(f"unknown visibility cell: {visibility}")
    return dict(VISIBILITY_CHANNEL_MAP[visibility])


def project_reviewer_packet(episode: Mapping[str, Any]) -> dict[str, Any]:
    """Build the task-reviewer packet for the episode's visibility cell.

    Pure projection: never copies event ledgers, hidden truth, or forbidden
    channels into convenience fields.
    """
    visibility = episode["visibility"]
    flags = channel_flags(visibility)
    channels = episode["channels"]

    packet: dict[str, Any] = {
        "schema_version": "shortcut-reviewer-packet-v1",
        "packet_kind": "task_reviewer",
        "episode_id": episode["episode_id"],
        "visibility": visibility,
        "task_metadata": {
            "template_id": episode["template_id"],
            "family": episode["family"],
            "policy_id": episode["policy_id"],
            "public_task_hash": episode["references"]["public_task_hash"],
        },
        "A": copy.deepcopy(channels["A"]),
        "T": copy.deepcopy(channels["T"]) if flags["T"] else None,
        "J": copy.deepcopy(channels["J"]) if flags["J"] else None,
        "channels_included": {
            "A": True,
            "T": flags["T"],
            "J": flags["J"],
        },
    }
    validate("reviewer_packet", packet)
    assert_no_reviewer_leakage(packet, episode)
    return packet


def project_auditor_packet(
    episode: Mapping[str, Any],
    event_ledger: Mapping[str, Any],
) -> dict[str, Any]:
    """Research auditor always receives complete A/T/J/events."""
    if event_ledger["episode_id"] != episode["episode_id"]:
        raise ValueError("event ledger episode_id mismatch")

    channels = episode["channels"]
    t_segments = channels["T"] or []
    j_obj = channels["J"]
    events = event_ledger["events"]

    packet = {
        "schema_version": "shortcut-auditor-packet-v1",
        "packet_kind": "research_auditor",
        "episode_id": episode["episode_id"],
        "policy_id": episode["policy_id"],
        "A": copy.deepcopy(channels["A"]),
        "T": copy.deepcopy(channels["T"]),
        "J": copy.deepcopy(channels["J"]),
        "events": copy.deepcopy(events),
        "coverage": {
            "t_passage_ids": [seg["passage_id"] for seg in t_segments],
            "j_passage_ids": ["J-0001"] if j_obj is not None else [],
            "event_ids": [event["event_id"] for event in events],
        },
        "omitted_identity_fields": [
            "actor_id",
            "visibility",
            "run_id",
            "replicate_seed",
        ],
    }
    validate("auditor_packet", packet)
    return packet


def assert_no_reviewer_leakage(
    packet: Mapping[str, Any],
    episode: Mapping[str, Any] | None = None,
) -> None:
    """Fail if a reviewer packet contains hidden-channel material."""
    visibility = packet["visibility"]
    flags = channel_flags(visibility)
    forbidden = REVIEWER_FORBIDDEN_TOP_LEVEL.intersection(packet.keys())
    if forbidden:
        raise AssertionError(f"reviewer packet has forbidden keys: {sorted(forbidden)}")

    if not flags["T"] and packet.get("T") is not None:
        raise AssertionError(f"{visibility} reviewer packet must omit T")
    if not flags["J"] and packet.get("J") is not None:
        raise AssertionError(f"{visibility} reviewer packet must omit J")
    if flags["T"] and packet.get("T") is None and episode is not None:
        # Including T means the field is present; null only if the episode
        # itself had a missing T channel.
        if episode["channels"]["T"] is not None:
            raise AssertionError(f"{visibility} reviewer packet missing T content")
    if flags["J"] and packet.get("J") is None and episode is not None:
        if episode["channels"]["J"] is not None:
            raise AssertionError(f"{visibility} reviewer packet missing J content")

    serialized = json.dumps(packet, sort_keys=True)
    if not flags["T"] and episode is not None:
        for segment in episode["channels"]["T"] or []:
            text = segment.get("text") or ""
            if text and text in serialized:
                raise AssertionError(f"{visibility} packet leaks T text")
    if not flags["J"] and episode is not None:
        j_obj = episode["channels"]["J"]
        if j_obj and j_obj.get("text") and j_obj["text"] in serialized:
            raise AssertionError(f"{visibility} packet leaks J text")


def packet_fingerprint(packet: Mapping[str, Any]) -> str:
    return sha256_json(packet)


def filter_all_visibility_packets(
    episode: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Project the same episode body under all four visibility cells.

    Useful for fixtures that share A/T/J content and only vary the cell.
    """
    packets = {}
    for visibility in VISIBILITY_CHANNEL_MAP:
        variant = copy.deepcopy(dict(episode))
        variant["visibility"] = visibility
        variant["episode_id"] = (
            f"{episode['base_id']}__info-{episode['information_state']}"
            f"__sc-{'present' if episode['shortcut_available'] else 'absent'}"
            f"__vis-{visibility}__seed-{episode['replicate_seed']}"
        )
        packets[visibility] = project_reviewer_packet(variant)
    return packets
