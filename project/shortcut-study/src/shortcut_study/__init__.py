"""Shortcut-study extension package (separate from observer_study)."""

__all__ = [
    "SCHEMA_VERSIONS",
    "VISIBILITY_CELLS",
]

SCHEMA_VERSIONS = {
    "episode": "shortcut-episode-v1",
    "events": "shortcut-events-v1",
    "reviewer_packet": "shortcut-reviewer-packet-v1",
    "auditor_packet": "shortcut-auditor-packet-v1",
    "scored_row": "shortcut-scored-row-v1",
    "semantic_audit": "shortcut-semantic-audit-v1",
}

VISIBILITY_CELLS = ("V00", "V01", "V10", "V11")
