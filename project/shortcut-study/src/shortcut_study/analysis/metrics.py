"""Per-cell acquisition metrics and null/zero-event diagnostics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

VISIBILITY_ORDER = ("V00", "V01", "V10", "V11")


def acquisition_outcome(row: Mapping[str, Any]) -> bool | None:
    """Return True/False/None for acquisition success; None is unknown, not negative."""
    value = row.get("acquisition_successful")
    if value is None and "acquisition" in row:
        value = row["acquisition"].get("successful")
    if value is True or value is False or value is None:
        return value
    raise TypeError(f"acquisition_successful must be bool|None, got {type(value)!r}")


def _eligible(row: Mapping[str, Any]) -> bool:
    eligibility = row.get("eligibility") or {}
    if isinstance(eligibility, Mapping):
        return bool(eligibility.get("acquisition_endpoint", True))
    return True


def primary_arm_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Restricted shortcut-present arm used for primary acquisition contrasts."""
    selected = []
    for row in rows:
        if row.get("shortcut_available") is not True:
            continue
        if not _eligible(row):
            continue
        selected.append(dict(row))
    return selected


def cell_rates(
    rows: Iterable[Mapping[str, Any]],
    *,
    information_state: str | None = None,
) -> dict[str, dict[str, float | int | None]]:
    """Assigned-denominator rates per visibility cell (unknowns counted in denominator)."""
    buckets: dict[str, list[bool | None]] = {cell: [] for cell in VISIBILITY_ORDER}
    for row in primary_arm_rows(rows):
        if information_state is not None and row.get("information_state") != information_state:
            continue
        cell = row["visibility"]
        if cell not in buckets:
            raise ValueError(f"unknown visibility cell: {cell}")
        buckets[cell].append(acquisition_outcome(row))
    out: dict[str, dict[str, float | int | None]] = {}
    for cell, values in buckets.items():
        n = len(values)
        positives = sum(v is True for v in values)
        unknowns = sum(v is None for v in values)
        out[cell] = {
            "assigned": n,
            "positive": positives,
            "unknown": unknowns,
            "rate_lower": (positives / n) if n else None,
            "rate_upper": ((positives + unknowns) / n) if n else None,
            "rate_if_complete": (positives / n) if n and unknowns == 0 else None,
        }
    return out


def zero_event_warnings(rates: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Emit finite-sample warnings when cells or the whole arm have zero events."""
    warnings: list[str] = []
    assigned = sum(int(rates[c]["assigned"] or 0) for c in VISIBILITY_ORDER if c in rates)
    positives = sum(int(rates[c]["positive"] or 0) for c in VISIBILITY_ORDER if c in rates)
    unknowns = sum(int(rates[c]["unknown"] or 0) for c in VISIBILITY_ORDER if c in rates)
    if assigned == 0:
        warnings.append("no_assigned_primary_arm_rows")
        return warnings
    if positives == 0 and unknowns == 0:
        warnings.append(
            "zero_observed_acquisitions: do_not_report_degenerate_zero_width_bootstrap_as_zero_risk"
        )
    if positives == 0 and unknowns > 0:
        warnings.append("zero_known_acquisitions_with_missing_outcomes")
    for cell in VISIBILITY_ORDER:
        if cell not in rates:
            warnings.append(f"missing_cell_{cell}")
            continue
        if int(rates[cell]["assigned"] or 0) == 0:
            warnings.append(f"empty_cell_{cell}")
    return warnings


def cluster_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
    """Bootstrap cluster: base scenario within family × difficulty."""
    family = str(row.get("family") or "unspecified_family")
    difficulty = str(row.get("intended_difficulty") or "unspecified_difficulty")
    base_id = str(row["base_id"])
    return family, difficulty, base_id


def group_matched_blocks(
    rows: Iterable[Mapping[str, Any]],
) -> dict[tuple[str, str, str, str, int], dict[str, bool | None]]:
    """
    Group primary-arm rows into matched visibility blocks.

    Key: (family, difficulty, base_id, information_state, replicate_seed)
    Value: visibility → acquisition outcome
    """
    blocks: dict[tuple[str, str, str, str, int], dict[str, bool | None]] = defaultdict(dict)
    for row in primary_arm_rows(rows):
        family, difficulty, base_id = cluster_key(row)
        info = str(row["information_state"])
        seed = int(row.get("replicate_seed", 0))
        key = (family, difficulty, base_id, info, seed)
        cell = row["visibility"]
        if cell in blocks[key]:
            raise ValueError(f"duplicate visibility cell in block {key}: {cell}")
        blocks[key][cell] = acquisition_outcome(row)
    return dict(blocks)
