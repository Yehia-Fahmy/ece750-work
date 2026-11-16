"""CLI harnesses: synthetic dry-run and archive analysis (when rows exist)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .compare import analyze_acquisition
from .io import (
    join_rows_with_schedule,
    load_schedule,
    load_scored_rows,
    write_analysis_release,
)
from .protocol import (
    DEFAULT_BOOTSTRAP_REPLICATES,
    DEFAULT_BOOTSTRAP_SEED,
    DRAFT_SUMMARY,
)
from .simulate import build_simulation_bundle, write_simulation_fixtures


def run_dry(
    output_directory: Path,
    *,
    effect: str = "T_only",
    replicates: int = 200,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
    materialize_fixtures: bool = True,
) -> dict[str, Any]:
    """
    CPU-only dry run on synthetic injected-effect rows.

    Default bootstrap replicates are reduced for a fast smoke; pass 10000 to
    match the draft protocol default.
    """
    if materialize_fixtures:
        write_simulation_fixtures()
    bundle = build_simulation_bundle(effect)
    report = analyze_acquisition(
        bundle["rows"], replicates=replicates, seed=seed
    )
    report["evidence_kind"] = bundle["evidence_kind"]
    report["simulation"] = {
        "effect": effect,
        "expected_contrasts": bundle["expected_contrasts"],
        "description": bundle["description"],
        "row_count": bundle["row_count"],
    }
    report["draft_protocol"] = DRAFT_SUMMARY
    recovered = {}
    for name, expected in bundle["expected_contrasts"].items():
        point = report["contrasts"][name]["all_assigned"]["point"]
        recovered[name] = {
            "expected": expected,
            "recovered_point": point,
            "match": point == expected,
        }
    report["injected_effect_recovery"] = recovered
    inputs = {
        "source": "synthetic_build_simulation_bundle",
        "effect": effect,
        "replicates": replicates,
        "seed": seed,
    }
    hashes = write_analysis_release(
        output_directory,
        report,
        inputs=inputs,
        command=(
            f"python -m shortcut_study analyze-dry --effect {effect} "
            f"--replicates {replicates} --seed {seed} --out {output_directory}"
        ),
    )
    report["output_sha256"] = hashes
    return report


def run_analyze(
    scored: Path,
    schedule: Path,
    output_directory: Path,
    *,
    replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """
    Analyze real scored archives against an assignment schedule.

    Refuses empty inputs and does not invent rows. Main scientific claims remain
    TBD until closed actor/audit archives are supplied.
    """
    scored_path = Path(scored)
    schedule_path = Path(schedule)
    if not scored_path.exists():
        raise FileNotFoundError(
            f"scored archive not found: {scored_path} (TBD until real archives exist)"
        )
    if not schedule_path.exists():
        raise FileNotFoundError(
            f"schedule not found: {schedule_path} (TBD until real archives exist)"
        )
    assignments = load_schedule(schedule_path)
    scored_rows = load_scored_rows(scored_path)
    rows = join_rows_with_schedule(
        scored_rows,
        assignments,
        evidence_kind="scored_archive_with_schedule",
    )
    report = analyze_acquisition(rows, replicates=replicates, seed=seed)
    report["evidence_kind"] = "scored_archive_with_schedule"
    report["draft_protocol"] = DRAFT_SUMMARY
    report["status"] = {
        "frozen_main_results": False,
        "note": "Estimates reflect provided inputs only; not a frozen WP11 release.",
    }
    inputs = {
        "scored": str(scored_path),
        "schedule": str(schedule_path),
        "assigned": len(assignments),
        "replicates": replicates,
        "seed": seed,
    }
    hashes = write_analysis_release(
        output_directory,
        report,
        inputs=inputs,
        command=(
            f"python -m shortcut_study analyze --scored {scored_path} "
            f"--schedule {schedule_path} --replicates {replicates} "
            f"--seed {seed} --out {output_directory}"
        ),
    )
    report["output_sha256"] = hashes
    return report


def recovery_ok(report: dict[str, Any]) -> bool:
    recovery = report.get("injected_effect_recovery") or {}
    if not recovery:
        return False
    return all(item.get("match") for item in recovery.values())
