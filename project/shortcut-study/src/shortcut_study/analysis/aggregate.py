"""Pairing, weighting, and assigned-denominator missingness helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .metrics import VISIBILITY_ORDER, group_matched_blocks, primary_arm_rows


def missingness_bounds(values: Sequence[bool | None]) -> dict[str, Any]:
    """Sharp [lower, upper] fractions for a binary outcome with unknowns."""
    n = len(values)
    if n == 0:
        return {
            "assigned": 0,
            "positive": 0,
            "unknown": 0,
            "fraction_bounds": None,
        }
    positive = sum(v is True for v in values)
    unknown = sum(v is None for v in values)
    return {
        "assigned": n,
        "positive": positive,
        "unknown": unknown,
        "fraction_bounds": [positive / n, (positive + unknown) / n],
    }


def assigned_denominator(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Account for every primary-arm assignment, including missing outcomes."""
    selected = primary_arm_rows(rows)
    by_status: dict[str, int] = defaultdict(int)
    outcomes: list[bool | None] = []
    for row in selected:
        outcome = row.get("acquisition_successful")
        if outcome is None and "acquisition" in row:
            outcome = row["acquisition"].get("successful")
        outcomes.append(outcome if outcome is True or outcome is False or outcome is None else None)
        terminal = None
        integrity = row.get("integrity") or {}
        if isinstance(integrity, Mapping):
            terminal = integrity.get("terminal_status")
        by_status[str(terminal or "unknown_terminal")] += 1
    bounds = missingness_bounds(outcomes)
    return {
        "assigned": len(selected),
        "by_terminal_status": dict(sorted(by_status.items())),
        "acquisition_bounds": bounds,
        "complete_outcome_fraction": (
            (bounds["assigned"] - bounds["unknown"]) / bounds["assigned"]
            if bounds["assigned"]
            else None
        ),
    }


def weight_plan(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Prespecified equal weights across families and information strata."""
    selected = primary_arm_rows(rows)
    families = sorted({str(r.get("family") or "unspecified_family") for r in selected})
    infos = sorted({str(r["information_state"]) for r in selected})
    family_weight = (1.0 / len(families)) if families else None
    info_weight = (1.0 / len(infos)) if infos else None
    return {
        "families": families,
        "information_states": infos,
        "family_weight": family_weight,
        "information_state_weight": info_weight,
        "rule": "equal_family_and_equal_information_state",
    }


def _block_contrast_bounds(
    cells: Mapping[str, bool | None],
) -> dict[str, tuple[float, float]] | None:
    """Per matched block, contrast bounds using unknown→[0,1] outcome intervals."""
    if any(cell not in cells for cell in VISIBILITY_ORDER):
        return None

    def lo(v: bool | None) -> float:
        return 1.0 if v is True else 0.0

    def hi(v: bool | None) -> float:
        return 0.0 if v is False else 1.0

    r00, r01, r10, r11 = (cells[c] for c in VISIBILITY_ORDER)
    # Difference bounds: lower = lo(a)-hi(b), upper = hi(a)-lo(b).
    t_low = ((lo(r10) - hi(r00)) + (lo(r11) - hi(r01))) / 2.0
    t_high = ((hi(r10) - lo(r00)) + (hi(r11) - lo(r01))) / 2.0
    j_low = ((lo(r01) - hi(r00)) + (lo(r11) - hi(r10))) / 2.0
    j_high = ((hi(r01) - lo(r00)) + (hi(r11) - lo(r10))) / 2.0
    x_low = lo(r11) - hi(r10) - hi(r01) + lo(r00)
    x_high = hi(r11) - lo(r10) - lo(r01) + hi(r00)
    return {
        "T_visibility": (t_low, t_high),
        "J_visibility": (j_low, j_high),
        "TxJ_interaction": (x_low, x_high),
    }


def paired_block_effects(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """
    Build paired block-level contrast bounds, stratified for weighting.

    Incomplete matched blocks (missing a visibility cell) are recorded and
    excluded from contrast means until the schedule is complete.
    """
    blocks = group_matched_blocks(rows)
    strata: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    incomplete = []
    for key, cells in sorted(blocks.items()):
        family, difficulty, base_id, info, seed = key
        contrasts = _block_contrast_bounds(cells)
        if contrasts is None:
            incomplete.append({
                "family": family,
                "intended_difficulty": difficulty,
                "base_id": base_id,
                "information_state": info,
                "replicate_seed": seed,
                "present_cells": sorted(cells),
            })
            continue
        identified = {name: lo == hi for name, (lo, hi) in contrasts.items()}
        strata[(family, difficulty)].append({
            "base_id": base_id,
            "information_state": info,
            "replicate_seed": seed,
            "cells": {c: cells[c] for c in VISIBILITY_ORDER},
            "contrasts": contrasts,
            "identified": identified,
        })
    return {
        "strata": {f"{f}|{d}": items for (f, d), items in sorted(strata.items())},
        "incomplete_blocks": incomplete,
        "complete_blocks": sum(len(v) for v in strata.values()),
    }


def average_contrast_bounds(
    strata_blocks: Mapping[str, Sequence[Mapping[str, Any]]],
    contrast: str,
    *,
    complete_only: bool = False,
) -> dict[str, Any]:
    """
    Equal family weight; within family equal difficulty strata; within stratum
    equal blocks; equal information-state mixing is achieved by including both
    info blocks when present in the simulation/schedule.

    ``complete_only=True`` is retained for block-level diagnostics only. The
    confirmatory complete-base sensitivity estimand (identical point and
    bootstrap inclusion) lives in ``compare.complete_base_contrast``.
    """
    by_family: dict[str, list[tuple[float, float]]] = defaultdict(list)
    blocks_used = 0
    for stratum_key, items in strata_blocks.items():
        family = stratum_key.split("|", 1)[0]
        values = []
        for item in items:
            if complete_only and not item["identified"].get(contrast, False):
                continue
            values.append(item["contrasts"][contrast])
            blocks_used += 1
        if values:
            # Equal weight across difficulty strata keys is applied by caller
            # grouping; here each stratum contributes its block mean.
            mean_lo = sum(v[0] for v in values) / len(values)
            mean_hi = sum(v[1] for v in values) / len(values)
            by_family[family].append((mean_lo, mean_hi))
    if not by_family:
        return {
            "families": 0,
            "blocks_used": 0,
            "bounds": None,
            "point": None,
        }
    family_means = []
    for _family, stratum_means in sorted(by_family.items()):
        family_means.append((
            sum(v[0] for v in stratum_means) / len(stratum_means),
            sum(v[1] for v in stratum_means) / len(stratum_means),
        ))
    lo = sum(v[0] for v in family_means) / len(family_means)
    hi = sum(v[1] for v in family_means) / len(family_means)
    return {
        "families": len(family_means),
        "blocks_used": blocks_used,
        "bounds": [lo, hi],
        "point": lo if lo == hi else None,
    }


def reporting_denominators(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """
    Separate completion / parse / valid-A denominators for gate reporting.

    Does not redefine historical qualification gate counts. Conditional
    parseability among completed episodes is distinct from assigned-denominator
    valid-answer rates.
    """
    rows = list(rows)
    assigned = len(rows)
    complete_info = [r for r in rows if r.get("information_state") == "complete"]

    def _terminal(row: Mapping[str, Any]) -> str:
        integrity = row.get("integrity") or {}
        if isinstance(integrity, Mapping) and integrity.get("terminal_status"):
            return str(integrity["terminal_status"])
        return str(row.get("terminal_status") or "unknown_terminal")

    def _answer_valid(row: Mapping[str, Any]) -> bool | None:
        task = row.get("task_result") or {}
        if isinstance(task, Mapping) and "answer_valid" in task:
            value = task.get("answer_valid")
            if value is True or value is False or value is None:
                return value
        value = row.get("answer_valid")
        if value is True or value is False or value is None:
            return value
        return None

    def _parseable_response(row: Mapping[str, Any]) -> bool | None:
        """Native response parse success when recorded; else fall back to answer_valid."""
        integrity = row.get("integrity") or {}
        if isinstance(integrity, Mapping) and "extraction_failure" in integrity:
            # extraction_failure True → not parseable; False → parseable when completed.
            failed = integrity.get("extraction_failure")
            if failed is True:
                return False
            if failed is False:
                return True
        return _answer_valid(row)

    completed = [r for r in rows if _terminal(r) == "completed"]
    complete_completed = [r for r in complete_info if _terminal(r) == "completed"]
    parseable_complete_completed = [
        r for r in complete_completed if _parseable_response(r) is True
    ]
    valid_assigned = [r for r in rows if _answer_valid(r) is True]
    valid_complete_assigned = [r for r in complete_info if _answer_valid(r) is True]

    def _rate(num: int, den: int) -> float | None:
        return (num / den) if den else None

    return {
        "assigned": assigned,
        "terminal_completion": {
            "numerator": len(completed),
            "denominator": assigned,
            "rate": _rate(len(completed), assigned),
            "definition": "terminal_status=completed / assigned",
        },
        "response_parse_among_complete_completed": {
            "numerator": len(parseable_complete_completed),
            "denominator": len(complete_completed),
            "rate": _rate(len(parseable_complete_completed), len(complete_completed)),
            "definition": (
                "parseable response among complete-information episodes with "
                "terminal_status=completed (conditional; not assigned-denominator)"
            ),
        },
        "valid_answer_among_assigned": {
            "numerator": len(valid_assigned),
            "denominator": assigned,
            "rate": _rate(len(valid_assigned), assigned),
            "definition": "task_result.answer_valid is True / assigned",
        },
        "valid_answer_among_complete_assigned": {
            "numerator": len(valid_complete_assigned),
            "denominator": len(complete_info),
            "rate": _rate(len(valid_complete_assigned), len(complete_info)),
            "definition": (
                "task_result.answer_valid is True among assigned "
                "complete-information episodes"
            ),
        },
        "note": (
            "Reporting definitions only; do not retroactively redefine "
            "historical gate failures that used a selected completed denominator."
        ),
    }
