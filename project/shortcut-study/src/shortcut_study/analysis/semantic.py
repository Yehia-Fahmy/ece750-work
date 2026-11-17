"""Semantic label diagnostics — separate from behavioral acquisition analysis."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .aggregate import average_contrast_bounds, paired_block_effects
from .metrics import VISIBILITY_ORDER, acquisition_outcome, primary_arm_rows

# Cell coefficients for confirmatory/secondary contrasts on rates.
# T=((r10-r00)+(r11-r01))/2, J=((r01-r00)+(r11-r10))/2, TxJ=r11-r10-r01+r00
CONTRAST_CELL_COEFFICIENTS: dict[str, dict[str, float]] = {
    "T_visibility": {"V00": -0.5, "V01": -0.5, "V10": 0.5, "V11": 0.5},
    "J_visibility": {"V00": -0.5, "V01": 0.5, "V10": -0.5, "V11": 0.5},
    "TxJ_interaction": {"V00": 1.0, "V01": -1.0, "V10": -1.0, "V11": 1.0},
}

CONTRAST_RANGES: dict[str, tuple[float, float]] = {
    "T_visibility": (-1.0, 1.0),
    "J_visibility": (-1.0, 1.0),
    "TxJ_interaction": (-2.0, 2.0),
}


def weighted_review_diagnostics(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Summarize independent-review selection weights and agreement.

    Expects rows with optional keys:
      selection_probability, primary_label, review_label, uncertain
    Missing review labels are counted; weights are used only for reviewed rows.
    """
    assigned = len(rows)
    reviewed = [r for r in rows if r.get("review_label") is not None]
    agree = sum(
        1 for r in reviewed
        if r.get("primary_label") == r.get("review_label")
        and not r.get("uncertain")
    )
    disagree = sum(
        1 for r in reviewed
        if r.get("primary_label") != r.get("review_label")
        and not r.get("uncertain")
    )
    uncertain = sum(1 for r in reviewed if r.get("uncertain"))
    # Horvitz–Thompson style weighted disagreement among reviewed rows with p>0.
    weighted_disagree = 0.0
    weight_sum = 0.0
    for row in reviewed:
        p = row.get("selection_probability")
        if p is None or float(p) <= 0:
            continue
        w = 1.0 / float(p)
        weight_sum += w
        if row.get("primary_label") != row.get("review_label") or row.get("uncertain"):
            weighted_disagree += w
    return {
        "assigned": assigned,
        "reviewed": len(reviewed),
        "agree": agree,
        "disagree": disagree,
        "uncertain": uncertain,
        "raw_disagreement_rate": (disagree / len(reviewed)) if reviewed else None,
        "weighted_disagreement_mass": weighted_disagree,
        "weighted_mass": weight_sum,
        "note": "diagnostic_only_not_semantic_accuracy",
    }


def _outcome_contributions(
    rows: Sequence[Mapping[str, Any]],
    contrast: str,
) -> list[dict[str, Any]]:
    """Per-outcome contribution magnitude for adversarial flip allocation."""
    coeffs = CONTRAST_CELL_COEFFICIENTS[contrast]
    by_cell: dict[str, list[Mapping[str, Any]]] = {cell: [] for cell in VISIBILITY_ORDER}
    for row in primary_arm_rows(rows):
        cell = str(row["visibility"])
        if cell not in by_cell:
            raise ValueError(f"unknown visibility cell: {cell}")
        outcome = acquisition_outcome(row)
        if outcome is None:
            continue
        by_cell[cell].append(row)

    contributions: list[dict[str, Any]] = []
    for cell, cell_rows in by_cell.items():
        n_cell = len(cell_rows)
        if n_cell == 0:
            continue
        coef = coeffs[cell]
        unit = coef / n_cell
        for row in cell_rows:
            outcome = acquisition_outcome(row)
            assert outcome is True or outcome is False
            contributions.append({
                "episode_id": row.get("episode_id"),
                "visibility": cell,
                "outcome": outcome,
                "unit_effect": unit,
                # Flip True→False decreases the cell rate; Flip False→True increases.
                "delta_if_flip": (-unit) if outcome else unit,
            })
    return contributions


def _sharp_flip_delta(
    contributions: Sequence[Mapping[str, Any]],
    *,
    flip_budget: int,
    direction: str,
) -> float:
    """Largest absolute contrast move from at most flip_budget adversarial flips."""
    if flip_budget <= 0 or not contributions:
        return 0.0
    signed = []
    for item in contributions:
        delta = float(item["delta_if_flip"])
        if direction == "increase" and delta > 0:
            signed.append(delta)
        elif direction == "decrease" and delta < 0:
            signed.append(delta)
    if direction == "increase":
        signed.sort(reverse=True)
        return float(sum(signed[:flip_budget]))
    signed.sort()  # most negative first
    return float(sum(signed[:flip_budget]))


def label_error_sensitivity(
    rows_or_points: Sequence[Mapping[str, Any]] | Mapping[str, float | None],
    *,
    flip_rate: float = 0.1,
    contrasts: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Coefficient-aware label-error envelopes under a global flip-rate budget.

    Error budget: floor(flip_rate * N) adversarial flips among observed primary-arm
    labels (global fraction). Sharp bounds allocate those flips to the largest
    |cell coefficient / n_cell| contributions. Interaction uses range [-2, 2];
    T/J use [-1, 1].

    Passing a bare point mapping without rows is rejected: a ±flip_rate envelope
    is not conservative for these contrasts.
    """
    if not 0.0 <= flip_rate <= 1.0:
        raise ValueError("flip_rate must be in [0, 1]")
    if isinstance(rows_or_points, Mapping) and not isinstance(rows_or_points, list):
        # Mapping of contrast → point without outcomes cannot yield sharp bounds.
        raise ValueError(
            "label_error_sensitivity requires scored/analysis rows with outcomes; "
            "a bare point mapping cannot produce conservative contrast envelopes "
            "(T/J can move by ~2×flip_rate and interaction by ~4×flip_rate under "
            "adversarial allocation)"
        )

    rows = list(rows_or_points)
    names = list(contrasts) if contrasts is not None else list(CONTRAST_CELL_COEFFICIENTS)
    primary = primary_arm_rows(rows)
    observed = [r for r in primary if acquisition_outcome(r) is not None]
    n_obs = len(observed)
    flip_budget = int(flip_rate * n_obs)  # floor; explicit global fraction budget

    paired = paired_block_effects(rows)
    envelopes: dict[str, Any] = {}
    for name in names:
        if name not in CONTRAST_CELL_COEFFICIENTS:
            raise KeyError(f"unknown contrast for label sensitivity: {name}")
        point = average_contrast_bounds(paired["strata"], name, complete_only=False)["point"]
        if point is None:
            envelopes[name] = {
                "point": None,
                "flip_rate": flip_rate,
                "flip_budget": flip_budget,
                "envelope": None,
                "note": "unidentified_point_no_envelope",
            }
            continue
        contributions = _outcome_contributions(rows, name)
        up = _sharp_flip_delta(contributions, flip_budget=flip_budget, direction="increase")
        down = _sharp_flip_delta(contributions, flip_budget=flip_budget, direction="decrease")
        range_lo, range_hi = CONTRAST_RANGES[name]
        lo = max(range_lo, float(point) + down)
        hi = min(range_hi, float(point) + up)
        envelopes[name] = {
            "point": point,
            "flip_rate": flip_rate,
            "flip_budget": flip_budget,
            "observed_labels": n_obs,
            "max_increase": up,
            "max_decrease": down,
            "envelope": [lo, hi],
            "contrast_range": [range_lo, range_hi],
            "error_budget": "global_fraction_of_observed_primary_arm_labels",
        }
    return {
        "flip_rate": flip_rate,
        "flip_budget": flip_budget,
        "observed_labels": n_obs,
        "envelopes": envelopes,
        "note": "sharp_coefficient_aware_sensitivity_not_a_confidence_interval",
    }


def group_labels_by_field(
    findings: Iterable[Mapping[str, Any]],
) -> dict[str, list[str]]:
    """Collect label strings per semantic field for separate aggregation."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        grouped[str(finding["field"])].append(str(finding["label"]))
    return {key: values for key, values in sorted(grouped.items())}
