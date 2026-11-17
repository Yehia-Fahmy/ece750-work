"""Confirmatory T/J contrasts, paired bootstrap, and multiplicity scaffolding."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Mapping, Sequence

from .aggregate import average_contrast_bounds, paired_block_effects, reporting_denominators
from .metrics import cell_rates, rule_of_three_upper, zero_event_warnings
from .protocol import (
    BONFERRONI_INDIVIDUAL,
    CONFIRMATORY_CONTRASTS,
    DEFAULT_BOOTSTRAP_REPLICATES,
    DEFAULT_BOOTSTRAP_SEED,
    INDIVIDUAL_INTERVAL,
    SECONDARY_CONTRASTS,
)


def confirmatory_contrasts() -> tuple[str, ...]:
    return CONFIRMATORY_CONTRASTS


def _quantile(ordered: Sequence[float], p: float) -> float:
    if not ordered:
        raise ValueError("empty sample")
    index = (len(ordered) - 1) * p
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def percentile_interval(values: Sequence[float], level: float) -> list[float] | None:
    """Linear-interpolated empirical percentile interval; not an exact test."""
    if not values:
        return None
    alpha = 1.0 - level
    ordered = sorted(values)
    return [_quantile(ordered, alpha / 2.0), _quantile(ordered, 1.0 - alpha / 2.0)]


def _base_level_effects(
    strata_blocks: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Collapse matched blocks to base scenarios within family|difficulty.

    Information states and replicate seeds for the same base are averaged with
    equal weight (prespecified). A base is identified for a contrast only when
    every constituent matched block is identified for that contrast.
    """
    out: dict[str, list[dict[str, Any]]] = {}
    for stratum_key, items in strata_blocks.items():
        by_base: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for item in items:
            by_base[str(item["base_id"])].append(item)
        bases = []
        for base_id, group in sorted(by_base.items()):
            contrasts: dict[str, tuple[float, float]] = {}
            identified: dict[str, bool] = {}
            names = set()
            for item in group:
                names.update(item["contrasts"])
            for name in sorted(names):
                lo = sum(item["contrasts"][name][0] for item in group) / len(group)
                hi = sum(item["contrasts"][name][1] for item in group) / len(group)
                contrasts[name] = (lo, hi)
                identified[name] = all(item["identified"][name] for item in group) and lo == hi
            bases.append({
                "base_id": base_id,
                "contrasts": contrasts,
                "identified": identified,
                "block_count": len(group),
            })
        out[stratum_key] = bases
    return out


def _mean_point(
    strata_bases: Mapping[str, Sequence[Mapping[str, Any]]],
    contrast: str,
    *,
    complete_only: bool = False,
    use_upper: bool = False,
) -> float | None:
    by_family: dict[str, list[float]] = defaultdict(list)
    for stratum_key, bases in strata_bases.items():
        family = stratum_key.split("|", 1)[0]
        values = []
        for base in bases:
            if complete_only and not base["identified"].get(contrast, False):
                continue
            lo, hi = base["contrasts"][contrast]
            values.append(hi if use_upper else lo)
        if values:
            by_family[family].append(sum(values) / len(values))
    if not by_family:
        return None
    family_means = [sum(v) / len(v) for _, v in sorted(by_family.items())]
    return sum(family_means) / len(family_means)


def _filter_complete_bases(
    strata_bases: Mapping[str, Sequence[Mapping[str, Any]]],
    contrast: str,
) -> dict[str, list[Mapping[str, Any]]]:
    usable: dict[str, list[Mapping[str, Any]]] = {}
    for key, bases in strata_bases.items():
        kept = [b for b in bases if b["identified"].get(contrast, False)]
        if kept:
            usable[key] = kept
    return usable


def complete_base_contrast(
    strata_bases: Mapping[str, Sequence[Mapping[str, Any]]],
    contrast: str,
) -> dict[str, Any]:
    """
    Complete-base sensitivity estimand.

    Include a base only when every matched information-state block for that base
    is identified for ``contrast``. Average included bases with the same family /
    difficulty weighting as the confirmatory analysis. Point estimation and the
    complete-base cluster bootstrap must use this same inclusion set.
    """
    usable = _filter_complete_bases(strata_bases, contrast)
    bases_used = sum(len(v) for v in usable.values())
    blocks_used = sum(int(b["block_count"]) for bases in usable.values() for b in bases)
    point_lo = _mean_point(usable, contrast, complete_only=False, use_upper=False)
    point_hi = _mean_point(usable, contrast, complete_only=False, use_upper=True)
    identified = point_lo is not None and point_lo == point_hi
    return {
        "estimand": "complete_base_sensitivity",
        "families": len({k.split("|", 1)[0] for k in usable}),
        "bases_used": bases_used,
        "blocks_used": blocks_used,
        "bounds": [point_lo, point_hi] if point_lo is not None and point_hi is not None else None,
        "point": point_lo if identified else None,
        "note": (
            "Includes a base only when all matched information-state blocks are "
            "identified; identical inclusion for point and bootstrap."
        ),
    }


def bootstrap_contrasts(
    strata_bases: Mapping[str, Sequence[Mapping[str, Any]]],
    contrast: str,
    *,
    replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
    complete_only: bool = False,
) -> dict[str, Any]:
    """
    Resample base scenarios within each family|difficulty stratum.

    Ordinary percentile intervals are diagnostic scaffolding, not exact tests.
    When outcomes are unidentified, bootstrap the bound endpoints separately.
    When complete_only=True, resample the complete-base inclusion set only.
    """
    if replicates < 1:
        raise ValueError("replicates must be >= 1")
    if complete_only:
        usable = _filter_complete_bases(strata_bases, contrast)
    else:
        usable = {key: list(bases) for key, bases in strata_bases.items() if bases}
    if not usable:
        return {
            "replicates": replicates,
            "seed": seed,
            "samples": 0,
            "point": None,
            "percentile_95": None,
            "bonferroni_975": None,
            "bound_endpoint_percentile_95": {"lower": None, "upper": None},
            "warnings": ["no_bases_for_bootstrap"],
            "estimand": "complete_base_sensitivity" if complete_only else "all_assigned",
        }

    point_lo = _mean_point(usable, contrast, complete_only=False, use_upper=False)
    point_hi = _mean_point(usable, contrast, complete_only=False, use_upper=True)
    identified = point_lo is not None and point_lo == point_hi

    rng = random.Random(seed)
    lower_draws: list[float] = []
    upper_draws: list[float] = []
    for _ in range(replicates):
        resampled: dict[str, list[Mapping[str, Any]]] = {}
        for key, bases in usable.items():
            resampled[key] = [rng.choice(bases) for _ in bases]
        lo = _mean_point(resampled, contrast, complete_only=False, use_upper=False)
        hi = _mean_point(resampled, contrast, complete_only=False, use_upper=True)
        if lo is None or hi is None:
            continue
        lower_draws.append(lo)
        upper_draws.append(hi)

    warnings = []
    if identified and point_lo == 0.0 and all(v == 0.0 for v in lower_draws):
        warnings.append(
            "degenerate_zero_bootstrap: use_finite_sample_language_not_zero_risk_claim"
        )

    return {
        "replicates": replicates,
        "seed": seed,
        "samples": len(lower_draws),
        "point": point_lo if identified else None,
        "all_assigned_bounds": [point_lo, point_hi],
        "percentile_95": percentile_interval(lower_draws, INDIVIDUAL_INTERVAL) if identified else None,
        "bonferroni_975": (
            percentile_interval(lower_draws, BONFERRONI_INDIVIDUAL) if identified else None
        ),
        "bound_endpoint_percentile_95": {
            "lower": percentile_interval(lower_draws, INDIVIDUAL_INTERVAL),
            "upper": percentile_interval(upper_draws, INDIVIDUAL_INTERVAL),
        },
        "warnings": warnings,
        "note": "percentile_intervals_are_not_exact_tests",
        "estimand": "complete_base_sensitivity" if complete_only else "all_assigned",
        "bases_used": sum(len(v) for v in usable.values()),
    }


def analyze_acquisition(
    rows: Sequence[Mapping[str, Any]],
    *,
    replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run primary acquisition metrics, contrasts, bootstrap, and warnings."""
    rates = cell_rates(rows)
    warnings = zero_event_warnings(rates)
    paired = paired_block_effects(rows)
    strata_bases = _base_level_effects(paired["strata"])
    independent_bases = sum(len(v) for v in strata_bases.values())
    positives = sum(int(rates[c]["positive"] or 0) for c in rates)
    zero_bound = rule_of_three_upper(
        events=positives,
        independent_units=independent_bases,
    )

    contrasts: dict[str, Any] = {}
    for name in list(CONFIRMATORY_CONTRASTS) + list(SECONDARY_CONTRASTS):
        assigned = average_contrast_bounds(paired["strata"], name, complete_only=False)
        complete = complete_base_contrast(strata_bases, name)
        boot = bootstrap_contrasts(
            strata_bases, name, replicates=replicates, seed=seed, complete_only=False
        )
        boot_complete = bootstrap_contrasts(
            strata_bases, name, replicates=replicates, seed=seed, complete_only=True
        )
        # Coherence check: complete-base point must match bootstrap inclusion point.
        if (
            complete["point"] is not None
            and boot_complete["point"] is not None
            and complete["point"] != boot_complete["point"]
        ):
            warnings.append(f"{name}:complete_base_point_bootstrap_mismatch")
        contrasts[name] = {
            "role": "confirmatory" if name in CONFIRMATORY_CONTRASTS else "secondary",
            "all_assigned": assigned,
            "complete_block_sensitivity": complete,
            "bootstrap": boot,
            "bootstrap_complete_block": boot_complete,
        }
        warnings.extend(f"{name}:{w}" for w in boot["warnings"])
        warnings.extend(f"{name}:complete:{w}" for w in boot_complete["warnings"])

    return {
        "evidence_kind": rows[0].get("evidence_kind", "unspecified") if rows else "empty",
        "cell_rates": rates,
        "paired": {
            "complete_blocks": paired["complete_blocks"],
            "incomplete_blocks": paired["incomplete_blocks"],
            "strata_base_counts": {k: len(v) for k, v in strata_bases.items()},
            "independent_bases": independent_bases,
        },
        "reporting_denominators": reporting_denominators(rows),
        "zero_event_independent_base_bound": zero_bound,
        "contrasts": contrasts,
        "warnings": sorted(set(warnings)),
        "multiplicity": {
            "confirmatory": list(CONFIRMATORY_CONTRASTS),
            "individual_interval": INDIVIDUAL_INTERVAL,
            "bonferroni_individual_interval": BONFERRONI_INDIVIDUAL,
            "familywise_target": 0.95,
        },
        "estimands": {
            "all_assigned": "assigned_denominator_contrast_bounds",
            "complete_block_sensitivity": "complete_base_sensitivity",
        },
    }
