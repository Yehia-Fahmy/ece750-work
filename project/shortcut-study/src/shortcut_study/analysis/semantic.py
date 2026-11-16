"""Semantic label diagnostics — separate from behavioral acquisition analysis."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence


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


def label_error_sensitivity(
    behavioral_points: Mapping[str, float | None],
    *,
    flip_rate: float = 0.1,
) -> dict[str, Any]:
    """
    Bound how a fraction of label flips could move reported points.

    This is a placeholder sensitivity envelope for semantic endpoints once audit
    rows exist. It does not invent audit labels.
    """
    if not 0.0 <= flip_rate <= 1.0:
        raise ValueError("flip_rate must be in [0, 1]")
    envelopes = {}
    for name, point in behavioral_points.items():
        if point is None:
            envelopes[name] = None
            continue
        # Conservative ±flip_rate shift on a [−1, 1]-scaled contrast.
        lo = max(-1.0, float(point) - flip_rate)
        hi = min(1.0, float(point) + flip_rate)
        envelopes[name] = {"point": point, "flip_rate": flip_rate, "envelope": [lo, hi]}
    return {
        "flip_rate": flip_rate,
        "envelopes": envelopes,
        "note": "bounded_sensitivity_not_a_confidence_interval",
    }


def group_labels_by_field(
    findings: Iterable[Mapping[str, Any]],
) -> dict[str, list[str]]:
    """Collect label strings per semantic field for separate aggregation."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        grouped[str(finding["field"])].append(str(finding["label"]))
    return {key: values for key, values in sorted(grouped.items())}
