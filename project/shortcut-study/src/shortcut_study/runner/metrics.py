"""Task-specific episode telemetry helpers (CPU-only; no inference).

Historical qualification rows may have used the TAB01-only approved list.
Recalculate derived telemetry from preserved ledgers with this module rather
than rewriting immutable terminals or qualification.json files.
"""

from collections import Counter

from ..tasks.tables import approved_for, generator_version_for

TELEMETRY_METRIC_VERSION = "sw02-task-approved-reads-v1"
DERIVED_TELEMETRY_SCHEMA = "shortcut-derived-telemetry-v1"
DERIVED_PROVENANCE_SCHEMA = "shortcut-derived-provenance-v1"


def tool_operation_counts(ledger, *, approved_resources):
    """Count executed tool calls; approved reads use the task-specific set."""
    if not isinstance(approved_resources, (list, tuple, set, frozenset)):
        raise ValueError("approved_resources must be an explicit collection")
    approved = set(approved_resources)
    counts = Counter()
    approved_reads = set()
    for event in ledger.get("events", []):
        if event.get("event_type") == "tool_call" and isinstance(event.get("operation"), str):
            counts[event["operation"]] += 1
        if (event.get("event_type") == "tool_result" and event.get("operation") == "read_resource"
                and event.get("execution_status") == "success"
                and event.get("resource_id") in approved):
            approved_reads.add(event["resource_id"])
            counts["approved_read_success"] += 1
        if (event.get("event_type") == "tool_result" and event.get("operation") == "calculate"
                and event.get("execution_status") == "success"):
            counts["calculate_success"] += 1
    counts["approved_resources_read"] = len(approved_reads)
    return dict(counts), approved_reads


def derive_corrected_telemetry(terminal, *, public_task=None, assignment=None):
    """Versioned derived correction from an immutable terminal (+ task context).

    Never mutates the terminal. Prefer public_task.approved_resources; otherwise
    resolve from template_id via approved_for.
    """
    episode = terminal["episode"]
    ledger = terminal["ledger"]
    if public_task is not None:
        approved = list(public_task["approved_resources"])
    else:
        approved = list(approved_for(episode["template_id"]))
    ops, reads = tool_operation_counts(ledger, approved_resources=approved)
    identity = assignment if assignment is not None else episode
    corrected_version = generator_version_for(identity)
    return {
        "schema_version": DERIVED_TELEMETRY_SCHEMA,
        "metric_version": TELEMETRY_METRIC_VERSION,
        "episode_id": episode["episode_id"],
        "template_id": episode["template_id"],
        "approved_resources": approved,
        "tool_operation_counts": ops,
        "approved_resources_read": sorted(reads),
        "generator_version_recorded": episode.get("generator_version"),
        "generator_version_corrected": corrected_version,
        "generator_version_mismatch": episode.get("generator_version") != corrected_version,
    }


def derive_corrected_provenance(terminal, *, assignment=None):
    """Versioned generator-version correction without rewriting the terminal."""
    episode = terminal["episode"]
    identity = assignment if assignment is not None else episode
    corrected = generator_version_for(identity)
    return {
        "schema_version": DERIVED_PROVENANCE_SCHEMA,
        "metric_version": TELEMETRY_METRIC_VERSION,
        "episode_id": episode["episode_id"],
        "template_id": episode["template_id"],
        "intended_difficulty": episode.get("intended_difficulty"),
        "generator_version_recorded": episode.get("generator_version"),
        "generator_version_corrected": corrected,
        "generator_version_mismatch": episode.get("generator_version") != corrected,
    }
