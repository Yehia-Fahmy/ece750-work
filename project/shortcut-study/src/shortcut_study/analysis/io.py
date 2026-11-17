"""Load analysis inputs from schedules and scored archives; write releases."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from ..hashing import sha256_bytes, sha256_json
from ..schemas import validate
from .protocol import DEFAULT_PRIMARY_POLICY_ID, DRAFT_SUMMARY, PROTOCOL_ID


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


# Analysis strata may be flattened onto scored rows in dry bundles; strip before
# schema validation. Do not trust these aliases over schedule/source fields.
_ANALYSIS_ONLY_KEYS = frozenset({
    "family",
    "intended_difficulty",
    "template_id",
    "mechanism",
    "replicate_seed",
    "acquisition_successful",
    "evidence_kind",
})


def _validate_scored_row(row: Mapping[str, Any], *, index: int | None = None) -> None:
    projection = {k: v for k, v in row.items() if k not in _ANALYSIS_ONLY_KEYS}
    try:
        validate("scored_row", projection)
    except Exception as exc:  # noqa: BLE001 — attach index for list loads
        where = f"scored row {index}" if index is not None else "scored row"
        raise ValueError(f"{where} failed schema validation: {exc}") from exc


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
        for index, row in enumerate(rows):
            _validate_scored_row(row, index=index)
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
            _validate_scored_row(row)
            rows.append(row)
    else:
        raise FileNotFoundError(path)
    if not rows:
        raise ValueError(f"no scored rows loaded from {path}")
    return rows


def _require_match(
    assignment: Mapping[str, Any],
    row: Mapping[str, Any],
    key: str,
) -> None:
    if key not in assignment:
        return
    if key in row and row[key] != assignment[key]:
        raise ValueError(
            f"schedule/scored mismatch for {assignment['episode_id']}: {key}"
        )


def join_rows_with_schedule(
    scored_rows: list[Mapping[str, Any]],
    assignments: list[Mapping[str, Any]],
    *,
    evidence_kind: str = "scored_archive_with_schedule",
    expected_policy_id: str = DEFAULT_PRIMARY_POLICY_ID,
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

    schedule_policies = {a.get("policy_id") for a in assignments}
    schedule_splits = {a.get("split") for a in assignments}
    if len(schedule_policies) > 1:
        raise ValueError(
            f"schedule has mixed policy_id values: "
            f"{sorted(str(p) for p in schedule_policies)}"
        )
    if len(schedule_splits) > 1:
        raise ValueError(
            f"schedule has mixed split values: "
            f"{sorted(str(s) for s in schedule_splits)}"
        )

    joined = []
    for assignment in assignments:
        row = by_id[assignment["episode_id"]]
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
            "policy_id",
            "split",
        ):
            _require_match(assignment, row, key)
            if key in assignment:
                row[key] = assignment[key]
        if "policy_id" in assignment and "policy_id" in row:
            _require_match(assignment, row, "policy_id")
        if "scorer_version" in assignment and "scorer_version" in row:
            _require_match(assignment, row, "scorer_version")
        if "acquisition_successful" not in row:
            row["acquisition_successful"] = row["acquisition"]["successful"]
        row["evidence_kind"] = evidence_kind
        joined.append(row)

    # Primary-arm homogeneity (restricted policy / single split / scorer).
    from .metrics import assert_homogeneous_primary_inputs

    assert_homogeneous_primary_inputs(joined, expected_policy_id=expected_policy_id)
    return joined


def _copy_retained(path: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return sha256_bytes(destination.read_bytes())


def write_analysis_release(
    output_directory: Path,
    report: Mapping[str, Any],
    *,
    inputs: Mapping[str, Any],
    command: str,
    retain_paths: Mapping[str, Path] | None = None,
    protocol: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """
    Write a derived analysis release with retained inputs and hashes.

    Copies exact schedule/scored/protocol artifacts into the release when
    ``retain_paths`` is provided so statistical reproduction does not depend on
    external paths remaining available. Refuses overwrite.
    """
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=False)
    report_path = output_directory / "analysis_report.json"
    manifest_path = output_directory / "analysis_manifest.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_hash = sha256_bytes(report_path.read_bytes())

    retained_dir = output_directory / "retained_inputs"
    retained_hashes: dict[str, str] = {}
    retained_relpaths: dict[str, str] = {}
    source_paths: dict[str, str] = {}
    if retain_paths:
        retained_dir.mkdir(parents=True, exist_ok=True)
        for name, path in sorted(retain_paths.items()):
            path = Path(path)
            if not path.is_file():
                raise FileNotFoundError(f"cannot retain missing input: {path}")
            dest = retained_dir / name
            retained_hashes[name] = _copy_retained(path, dest)
            retained_relpaths[name] = str(Path("retained_inputs") / name)
            source_paths[name] = str(path)

    protocol_doc = dict(protocol) if protocol is not None else dict(DRAFT_SUMMARY)
    protocol_path = output_directory / "analysis_protocol_snapshot.json"
    protocol_path.write_text(
        json.dumps(protocol_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    protocol_hash = sha256_bytes(protocol_path.read_bytes())

    input_content_hashes = {
        key: value
        for key, value in dict(inputs).items()
        if key.endswith("_sha256") or key == "content_sha256"
    }

    manifest = {
        "evidence_kind": report.get("evidence_kind", "unspecified"),
        "command": command,
        "protocol_id": PROTOCOL_ID,
        "protocol_status": "draft_not_frozen",
        "frozen_main_results": False,
        "inputs": dict(inputs),
        "input_source_paths": source_paths,
        "retained_inputs": retained_relpaths,
        "input_sha256": {
            **input_content_hashes,
            **{f"retained:{name}": digest for name, digest in retained_hashes.items()},
            "analysis_protocol_snapshot.json": protocol_hash,
        },
        "protocol_sha256": protocol_hash,
        "output_sha256": {
            "analysis_report.json": report_hash,
            "analysis_protocol_snapshot.json": protocol_hash,
        },
        "reproduction": {
            "statistical": (
                "Replay from retained_inputs/ plus this protocol snapshot; "
                "does not prove native inference authenticity."
            ),
            "native_authenticity": (
                "Separate raw-archive package and SW02 provenance checks; "
                "not claimed by this analysis release alone."
            ),
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
        "analysis_protocol_snapshot.json": protocol_hash,
        **{f"retained_inputs/{name}": digest for name, digest in retained_hashes.items()},
    }


def hash_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def hash_json_value(value: Any) -> str:
    return sha256_json(value)
