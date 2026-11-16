"""Load analysis inputs from schedules and scored archives; write releases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..hashing import sha256_bytes
from ..schemas import validate


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schedule(path: Path) -> list[dict[str, Any]]:
    doc = _read_json(path)
    if isinstance(doc, list):
        assignments = doc
    elif isinstance(doc, Mapping) and "assignments" in doc:
        assignments = list(doc["assignments"])
    else:
        raise ValueError(f"schedule must be a list or object with assignments: {path}")
    if not assignments:
        raise ValueError(f"schedule is empty: {path}")
    return assignments


def load_scored_rows(path: Path) -> list[dict[str, Any]]:
    """Load scored rows from a JSON list/object or a directory of scored.json files."""
    path = Path(path)
    rows: list[dict[str, Any]] = []
    if path.is_file():
        doc = _read_json(path)
        if isinstance(doc, list):
            rows = list(doc)
        elif isinstance(doc, Mapping) and "rows" in doc:
            rows = list(doc["rows"])
        else:
            validate("scored_row", doc)
            rows = [dict(doc)]
    elif path.is_dir():
        scored_files = sorted(path.rglob("scored.json"))
        if not scored_files:
            # Also accept analysis_rows.json at the root of a dry bundle.
            alt = path / "analysis_rows.json"
            if alt.is_file():
                return load_scored_rows(alt)
            raise FileNotFoundError(
                f"no scored.json files under {path}; real archives TBD"
            )
        for file_path in scored_files:
            row = _read_json(file_path)
            validate("scored_row", row)
            rows.append(row)
    else:
        raise FileNotFoundError(path)
    if not rows:
        raise ValueError(f"no scored rows loaded from {path}")
    return rows


def join_rows_with_schedule(
    scored_rows: list[Mapping[str, Any]],
    assignments: list[Mapping[str, Any]],
    *,
    evidence_kind: str = "scored_archive_with_schedule",
) -> list[dict[str, Any]]:
    """Attach family/difficulty/seed strata from the assignment schedule."""
    by_id = {row["episode_id"]: dict(row) for row in scored_rows}
    if len(by_id) != len(scored_rows):
        raise ValueError("duplicate episode_id in scored rows")
    assigned_ids = [a["episode_id"] for a in assignments]
    if len(set(assigned_ids)) != len(assigned_ids):
        raise ValueError("duplicate episode_id in schedule")
    missing = [eid for eid in assigned_ids if eid not in by_id]
    extra = sorted(set(by_id) - set(assigned_ids))
    if missing:
        raise ValueError(
            f"{len(missing)} scheduled episode_ids lack scored rows "
            f"(examples: {missing[:3]}); archives incomplete or TBD"
        )
    if extra:
        raise ValueError(
            f"{len(extra)} scored rows are not on the schedule (examples: {extra[:3]})"
        )
    joined = []
    for assignment in assignments:
        row = by_id[assignment["episode_id"]]
        # Prefer schedule strata; scored schema does not carry family/difficulty.
        for key in (
            "family",
            "intended_difficulty",
            "template_id",
            "mechanism",
            "replicate_seed",
            "base_id",
            "visibility",
            "information_state",
            "shortcut_available",
        ):
            if key in assignment:
                if key in row and row[key] != assignment[key]:
                    raise ValueError(
                        f"schedule/scored mismatch for {assignment['episode_id']}: {key}"
                    )
                row[key] = assignment[key]
        if "acquisition_successful" not in row:
            row["acquisition_successful"] = row["acquisition"]["successful"]
        row["evidence_kind"] = evidence_kind
        joined.append(row)
    return joined


def write_analysis_release(
    output_directory: Path,
    report: Mapping[str, Any],
    *,
    inputs: Mapping[str, Any],
    command: str,
) -> dict[str, str]:
    """Write a derived analysis release with input/output hashes. Refuses overwrite."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=False)
    report_path = output_directory / "analysis_report.json"
    manifest_path = output_directory / "analysis_manifest.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_hash = sha256_bytes(report_path.read_bytes())
    manifest = {
        "evidence_kind": report.get("evidence_kind", "unspecified"),
        "command": command,
        "inputs": dict(inputs),
        "protocol_status": "draft_not_frozen",
        "frozen_main_results": False,
        "output_sha256": {
            "analysis_report.json": report_hash,
        },
        "note": (
            "Scaffolding/dry outputs are not main scientific findings. "
            "Main contrasts remain TBD until real closed archives exist."
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "analysis_report.json": report_hash,
        "analysis_manifest.json": sha256_bytes(manifest_path.read_bytes()),
    }
