"""Guarded freeze authority for main-split execution (SW07-C / G3 prep).

A committed `configs/frozen/<version>/` tree may exist as *provisional
materialization* before Yehia signs. Runners must still refuse `split=main`
until `validate_freeze_authority` accepts a **signed** manifest whose pinned
component hashes match the on-disk files. Unsigned, draft, provisional, or
hash-mismatched trees never authorize main collection. Soft-signing is
forbidden; this module does not write signature fields.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .hashing import sha256_json
from .paths import CONFIGS_DIR
from .tasks.tables import (
    DIFFICULTIES,
    TEMPLATES,
    enumerate_tab_catalog_assignments,
    generate_task,
)

FROZEN_CONFIGS_DIR = CONFIGS_DIR / "frozen"
PROTOCOL_CANDIDATE = "s0-tab-v0"
MANIFEST_NAME = "manifest.json"
SCHEDULE_NAME = "schedule.json"

REQUIRED_COMPONENT_KEYS = (
    "scope",
    "splits_reservation",
    "schedule",
    "budgets",
    "visibility",
    "policy",
    "a_t_j_boundaries",
    "analysis_protocol",
    "actor_profile",
    "scoring_source_of_truth",
    "retry_recovery",
    "reduced_claims",
)

# Status values that never authorize main, even if someone flips signed=true.
_NON_AUTHORIZING_STATUS_MARKERS = (
    "draft",
    "provisional",
    "unsigned",
    "not_frozen",
    "template",
)


class FreezeAuthorityError(ValueError):
    """Raised when a freeze directory cannot authorize main execution."""


def frozen_dir(version: str = PROTOCOL_CANDIDATE) -> Path:
    return FROZEN_CONFIGS_DIR / version


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def component_paths(directory: Path, manifest: dict[str, Any] | None = None) -> dict[str, Path]:
    directory = Path(directory)
    manifest = manifest if manifest is not None else load_json(directory / MANIFEST_NAME)
    components = manifest.get("components") or {}
    paths: dict[str, Path] = {}
    for key in REQUIRED_COMPONENT_KEYS:
        relative = components.get(key)
        if not relative:
            raise FreezeAuthorityError(f"manifest missing components.{key}")
        paths[key] = directory / relative
    return paths


def compute_component_hashes(directory: Path, manifest: dict[str, Any] | None = None) -> dict[str, str]:
    return {
        key: sha256_file(path)
        for key, path in component_paths(directory, manifest).items()
    }


def _status_blocks_authority(status: str | None) -> bool:
    if not status or not isinstance(status, str):
        return True
    lowered = status.lower()
    return any(marker in lowered for marker in _NON_AUTHORIZING_STATUS_MARKERS)


def validate_freeze_authority(
    directory: Path | str,
    *,
    require_signed: bool = True,
) -> dict[str, Any]:
    """Validate a freeze tree.

    When ``require_signed`` is True (runner path), unsigned / provisional /
    mismatched trees raise. Structural dry checks may call with
    ``require_signed=False`` to verify hashes and schedule shape without
    claiming execution authority.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FreezeAuthorityError(f"freeze directory missing: {directory}")
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        raise FreezeAuthorityError(f"freeze manifest missing: {manifest_path}")

    manifest = load_json(manifest_path)
    freeze = manifest.get("freeze")
    if not isinstance(freeze, dict):
        raise FreezeAuthorityError("manifest.freeze must be an object")

    paths = component_paths(directory, manifest)
    for key, path in paths.items():
        if not path.is_file():
            raise FreezeAuthorityError(f"missing freeze component {key}: {path}")

    expected = freeze.get("component_sha256")
    if not isinstance(expected, dict) or set(expected) != set(REQUIRED_COMPONENT_KEYS):
        raise FreezeAuthorityError(
            "manifest.freeze.component_sha256 must pin every required component"
        )
    actual = compute_component_hashes(directory, manifest)
    mismatches = sorted(key for key in REQUIRED_COMPONENT_KEYS if actual[key] != expected[key])
    if mismatches:
        raise FreezeAuthorityError(
            "frozen component hash mismatch: " + ", ".join(mismatches)
        )

    status = manifest.get("status")
    signed = freeze.get("signed") is True
    owner = freeze.get("accepting_owner")
    commit = freeze.get("freeze_commit")
    g3 = freeze.get("g3_status")

    report = {
        "directory": str(directory),
        "protocol_version": manifest.get("protocol_version") or manifest.get("protocol_candidate"),
        "status": status,
        "signed": signed,
        "accepting_owner": owner,
        "freeze_commit": commit,
        "g3_status": g3,
        "component_sha256": actual,
        "executable_main": False,
        "authority": "rejected",
    }

    if require_signed:
        if _status_blocks_authority(status if isinstance(status, str) else None):
            raise FreezeAuthorityError(
                f"freeze status does not authorize main execution: {status!r}"
            )
        if not signed:
            raise FreezeAuthorityError("freeze is unsigned; main execution refused")
        if not isinstance(owner, str) or not owner.strip():
            raise FreezeAuthorityError("freeze accepting_owner is blank; main refused")
        if not isinstance(commit, str) or len(commit.strip()) < 7:
            raise FreezeAuthorityError("freeze_commit missing/invalid; main refused")
        if g3 not in ("accepted", "signed"):
            raise FreezeAuthorityError(
                f"freeze.g3_status={g3!r} does not authorize main (need accepted/signed)"
            )
        report["executable_main"] = True
        report["authority"] = "accepted"
    else:
        report["authority"] = "structural_ok_unsigned_or_unverified"

    return report


def authorize_main_execution(freeze_dir: Path | str | None) -> dict[str, Any]:
    """Require an explicit signed freeze directory before any main runner work."""
    if freeze_dir is None:
        raise FreezeAuthorityError(
            "split=main requires freeze_dir pointing at a signed configs/frozen/<version>/"
        )
    return validate_freeze_authority(freeze_dir, require_signed=True)


def dry_validate_schedule(directory: Path | str) -> dict[str, Any]:
    """Structurally validate schedule.json (hashes + shape). Does not authorize main."""
    directory = Path(directory)
    # Hash integrity always checked; signature not required for dry structure.
    authority = validate_freeze_authority(directory, require_signed=False)
    schedule = load_json(directory / SCHEDULE_NAME)
    assigned = schedule.get("assignments")
    if not isinstance(assigned, list) or not assigned:
        raise FreezeAuthorityError("schedule.assignments must be a non-empty list")
    denominator = schedule.get("assigned_denominator") or {}
    expected_n = denominator.get("primary_actor_episodes")
    if expected_n != len(assigned):
        raise FreezeAuthorityError(
            f"schedule denominator {expected_n} != len(assignments) {len(assigned)}"
        )
    episode_ids = [row.get("episode_id") for row in assigned]
    if any(not isinstance(eid, str) or not eid for eid in episode_ids):
        raise FreezeAuthorityError("every schedule row needs episode_id")
    if len(set(episode_ids)) != len(episode_ids):
        raise FreezeAuthorityError("schedule episode_id values are not unique")
    if schedule.get("split") != "main":
        raise FreezeAuthorityError("frozen schedule.split must be main")
    # Executable flag must stay false until authority accepts.
    executable = bool(schedule.get("executable")) and authority["executable_main"]
    return {
        **authority,
        "assigned": len(assigned),
        "schedule_executable_flag": bool(schedule.get("executable")),
        "dry_executable": executable,
        "schedule_sha256": authority["component_sha256"]["schedule"],
    }


def build_main_schedule_payload(*, replicate_seed: int = 0) -> dict[str, Any]:
    """Materialize the reserved main factorial schedule (CPU; no inference)."""
    assignments = enumerate_tab_catalog_assignments(
        replicate_seed=replicate_seed, split="main"
    )
    rows = []
    fingerprints = []
    for assignment in assignments:
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        fingerprints.append(task.semantic_fingerprint)
        rows.append({
            **assignment,
            "semantic_fingerprint": task.semantic_fingerprint,
            "terminal_status": "not_attempted",
        })
    if len(set(fingerprints)) != 20:
        raise FreezeAuthorityError(
            f"expected 20 unique main base fingerprints, got {len(set(fingerprints))}"
        )
    return {
        "schema_version": "shortcut-frozen-schedule-v1",
        "protocol_candidate": PROTOCOL_CANDIDATE,
        "status": "provisional_materialization_unsigned",
        "split": "main",
        "replicate_seed": replicate_seed,
        "assigned": len(rows),
        "assigned_denominator": {
            "primary_actor_episodes": 320,
            "base_scenarios": 20,
            "cells_per_base": 16,
            "replicate_seeds": [replicate_seed],
            "templates": list(TEMPLATES),
            "difficulties": list(DIFFICULTIES),
        },
        "executable": False,
        "execution_policy": {
            "condition_balanced_blocks": True,
            "no_parameter_changes_after_outcomes": True,
            "technical_retries_only": True,
            "interrupted_ids_remain_in_denominator": True,
            "unattempted_ids_remain_recoverable": True,
            "replace_attempted_outcomes_forbidden": True,
        },
        "note": (
            "Provisional materialization for SW07-C review. executable=false until Yehia "
            "signs the freeze checklist and g3_status becomes accepted; runners reject "
            "unsigned/mismatched trees."
        ),
        "assignments": rows,
        "fingerprint_summary": {
            "unique_base_fingerprints": len(set(fingerprints)),
            "rows": len(rows),
        },
    }


def _read_provisional_component(name: str) -> dict[str, Any]:
    path = CONFIGS_DIR / "provisional" / "s0-tab-only" / name
    return load_json(path)


def _stamp_provisional(doc: dict[str, Any], *, status_key: str = "status") -> dict[str, Any]:
    out = deepcopy(doc)
    if status_key in out:
        out[status_key] = "provisional_materialization_unsigned"
    elif "protocol_status" in out:
        out["protocol_status"] = "provisional_materialization_unsigned"
    out["freeze_note"] = (
        "Copied into configs/frozen/s0-tab-v0/ as unsigned provisional materialization. "
        "Not G3. Not soft-signed. Not submission authority."
    )
    return out


def build_frozen_splits_reservation() -> dict[str, Any]:
    """Pin split seed namespaces to the executable catalog (not the older draft ranges)."""
    return {
        "status": "provisional_materialization_unsigned",
        "schema_version": "shortcut-splits-reservation-v1",
        "protocol_candidate": PROTOCOL_CANDIDATE,
        "rules": {
            "disjoint_by": ["semantic_fingerprint", "episode_id"],
            "shared_base_across_conditions_within_split": True,
            "notes": [
                "Pinned to catalog SPLIT_SEED_BASE namespaces used by generate_task.",
                "Main generation seeds are 20000+ (not the older provisional 2000 draft range).",
            ],
        },
        "reservations": {
            "smoke": {
                "generation_seed_inclusive_range": [1000, 1999],
                "instance_key_prefix": "smoke-",
                "catalog_seed_base": 1000,
            },
            "development": {
                "generation_seed_inclusive_range": [0, 0],
                "instance_key_prefix": "dev-",
                "catalog_seed_base": 0,
                "grandfathered_generation_seed": 0,
            },
            "qualification": {
                "generation_seed_inclusive_range": [10000, 19999],
                "instance_key_prefix": "qual-",
                "catalog_seed_base": 10000,
                "note": "Historical consumed namespaces may differ; fresh batches allocate via batch API.",
            },
            "main": {
                "generation_seed_inclusive_range": [20000, 29999],
                "instance_key_prefix": "main-",
                "catalog_seed_base": 20000,
                "planned_primary_actor_episodes": 320,
            },
        },
        "freeze_note": (
            "Unsigned provisional freeze pin. Rejected for main execution until signature."
        ),
    }


def build_frozen_scope() -> dict[str, Any]:
    scope = _stamp_provisional(_read_provisional_component("scope.json"))
    # G2 is accepted on main tip; keep S0 candidate alive but do not claim freeze/G3.
    # Preserve SW07-B behavioral-only XOR fields from provisional scope when present.
    scope["s4_fallback"] = {
        "tier": "S4",
        "primary_actor_episodes": 0,
        "when": "freeze_or_collection_misses_cutoffs",
        "selected": False,
        "automatic_if_no_g3_by": "2026-11-22T18:00:00 America/Toronto",
        "reason": (
            "G2 PASS on qual-fresh-tab-catalog-v5-001 reopened S0 freeze prep; S4 remains "
            "automatic fallback if G3 is unsigned by the SWARM_START cutoff."
        ),
    }
    scope["withdrawn_relative_to_original_plan"] = {
        "original_course_core_episodes": 3200,
        "original_families": 5,
        "original_replicate_seeds": 2,
        "reason": (
            "Course-core 3200 remains withdrawn. S0 320 is the freeze candidate after G2 "
            "accept; this tree is unsigned provisional materialization only."
        ),
    }
    claims = scope.get("semantic_claims")
    if not isinstance(claims, dict) or claims.get("default") != "withdrawn_behavioral_only":
        scope["semantic_claims"] = {
            "default": "withdrawn_behavioral_only",
            "decision": "behavioral_only_plus_semantic_withdrawal",
            "xor_rejected_alternative": "qualify_local_semantic_judge_before_freeze",
            "decided_at": "2026-11-18",
            "decision_ref": "handoffs/2026-11-18-sw07-b-semantic-scope.md",
            "evidence_ref": "results/qualification/sw07-b-semantic-scope-v1.json",
            "condition": (
                "SW07-B/ECE-80 selected behavioral-only before freeze; live local judge "
                "not qualified; no cloud judge; semantic conclusions withdrawn"
            ),
        }
    return scope


def build_frozen_reduced_claims() -> dict[str, Any]:
    return {
        "status": "provisional_materialization_unsigned",
        "schema_version": "shortcut-reduced-claims-v1",
        "protocol_candidate": PROTOCOL_CANDIDATE,
        "compared_to": {
            "original_plan_label": "course_core_3200",
            "original_primary_actor_episodes": 3200,
            "original_families": 5,
            "original_replicate_seeds": 2,
        },
        "selected_candidate": {
            "tier": "S0",
            "base_scenarios": 20,
            "families": 1,
            "family_ids": ["tables"],
            "replicate_seeds": 1,
            "primary_actor_episodes": 320,
            "note": (
                "Candidate after G2 accept. Freeze signature blank; G3 not_started; "
                "submission_authorized=false."
            ),
        },
        "explicit_reductions": [
            "No soft-signed G3 / frozen-protocol claim from this materialization alone.",
            "No main collection authorization while freeze.signed is false.",
            "No five-family breadth claim; DOC/PLAN/CODE/VERIFY out.",
            "No optional second-actor replication.",
            "Independent semantic-validation claims withdrawn (SW07-B/ECE-80 XOR: "
            "behavioral-only selected; judge path not qualified before freeze; no cloud judge).",
        ],
        "semantic_scope": {
            "decision": "behavioral_only_plus_semantic_withdrawal",
            "decision_ref": "results/qualification/sw07-b-semantic-scope-v1.json",
            "live_judge_in_freeze_scope": False,
        },
        "freeze_note": "Unsigned provisional freeze pin. Not submission authority.",
    }


def materialize_provisional_frozen_tree(
    destination: Path | str | None = None,
    *,
    replicate_seed: int = 0,
) -> dict[str, Any]:
    """Write an unsigned configs/frozen/<version>/ tree for review (no soft-sign)."""
    destination = Path(destination) if destination is not None else frozen_dir()
    if destination.exists():
        raise FreezeAuthorityError(f"refusing to overwrite existing freeze tree: {destination}")
    destination.mkdir(parents=True, exist_ok=False)

    components: dict[str, Any] = {
        "scope": build_frozen_scope(),
        "splits_reservation": build_frozen_splits_reservation(),
        "schedule": build_main_schedule_payload(replicate_seed=replicate_seed),
        "budgets": _stamp_provisional(_read_provisional_component("budgets.json")),
        "visibility": _stamp_provisional(_read_provisional_component("visibility.json")),
        "policy": _stamp_provisional(_read_provisional_component("policy.json")),
        "a_t_j_boundaries": _stamp_provisional(
            _read_provisional_component("a_t_j_boundaries.json")
        ),
        "analysis_protocol": _stamp_provisional(
            _read_provisional_component("analysis_protocol.json"),
            status_key="protocol_status",
        ),
        "actor_profile": _stamp_provisional(_read_provisional_component("actor_profile.json")),
        "scoring_source_of_truth": _stamp_provisional(
            _read_provisional_component("scoring_source_of_truth.json")
        ),
        "retry_recovery": _stamp_provisional(_read_provisional_component("retry_recovery.json")),
        "reduced_claims": build_frozen_reduced_claims(),
    }
    # Point scoring SoT at this frozen tree once hashes exist.
    components["scoring_source_of_truth"]["episode_budgets"] = {
        "owner": "configs/frozen/s0-tab-v0/budgets.json (unsigned provisional)",
        "frozen_location": "configs/frozen/s0-tab-v0/",
    }
    if "freeze" in components["analysis_protocol"]:
        components["analysis_protocol"]["freeze"] = "provisional_materialization_unsigned"

    relative_names = {
        "scope": "scope.json",
        "splits_reservation": "splits_reservation.json",
        "schedule": SCHEDULE_NAME,
        "budgets": "budgets.json",
        "visibility": "visibility.json",
        "policy": "policy.json",
        "a_t_j_boundaries": "a_t_j_boundaries.json",
        "analysis_protocol": "analysis_protocol.json",
        "actor_profile": "actor_profile.json",
        "scoring_source_of_truth": "scoring_source_of_truth.json",
        "retry_recovery": "retry_recovery.json",
        "reduced_claims": "reduced_claims.json",
    }
    for key, relative in relative_names.items():
        write_json(destination / relative, components[key])

    hashes = {key: sha256_file(destination / relative) for key, relative in relative_names.items()}
    manifest = {
        "status": "provisional_materialization_unsigned",
        "schema_version": "shortcut-freeze-manifest-v1",
        "protocol_version": PROTOCOL_CANDIDATE,
        "protocol_candidate": PROTOCOL_CANDIDATE,
        "tier": "S0",
        "created_for": "SW07-C / ECE-81 provisional frozen materialization",
        "timezone": "America/Toronto",
        "freeze": {
            "signed": False,
            "g3_status": "not_started",
            "frozen_directory": f"configs/frozen/{PROTOCOL_CANDIDATE}/",
            "accepting_owner": None,
            "freeze_commit": None,
            "freeze_timestamp": None,
            "component_sha256": hashes,
            "note": (
                "Deliberately unsigned. Yehia/root must sign the freeze checklist before "
                "g3_status may become accepted. Agents must not soft-sign."
            ),
        },
        "components": relative_names,
        "source_provisional": "configs/provisional/s0-tab-only/",
        "gate_prerequisites": {
            "G0": "accepted",
            "G2": "accepted (qual-fresh-tab-catalog-v5-001)",
            "G1": "still open scientific closure",
            "G3": "requires Yehia signature — not_started",
        },
        "blocked_actions_until_signed": [
            "WP09 / SW08 main actor collection",
            "Setting gates.G3=accepted",
            "Flipping submission_authorized",
            "Treating this tree as immutable scientific freeze authority",
        ],
        "submission_authorized": False,
    }
    write_json(destination / MANIFEST_NAME, manifest)
    # Recompute schedule/manifest hashes after manifest write is unnecessary for
    # components; manifest is not part of component_sha256 pins.
    readme = (
        "# Provisional frozen tree — `s0-tab-v0`\n\n"
        "**Status:** `provisional_materialization_unsigned` — not G3.\n\n"
        "- `freeze.signed` is **false**; signature fields are deliberately blank.\n"
        "- Runners **reject** `split=main` against this tree until Yehia signs.\n"
        "- Hash mismatches also reject, even after a future signature.\n"
        "- `submission_authorized` remains **false**.\n"
        "- Independent freeze review must be someone other than the SW07-C author.\n"
    )
    (destination / "README.md").write_text(readme, encoding="utf-8")

    structural = dry_validate_schedule(destination)
    return {
        "directory": str(destination),
        "manifest_sha256": sha256_file(destination / MANIFEST_NAME),
        "component_sha256": hashes,
        "signed": False,
        "submission_authorized": False,
        "dry_validate": structural,
        "schedule_rows": components["schedule"]["assigned"],
        "content_fingerprint": sha256_json(
            {"components": hashes, "protocol": PROTOCOL_CANDIDATE, "signed": False}
        ),
    }


def sign_freeze_manifest_for_tests(
    directory: Path | str,
    *,
    accepting_owner: str,
    freeze_commit: str,
    g3_status: str = "accepted",
) -> dict[str, Any]:
    """Test-only helper: rewrite signature fields on a *copy* freeze tree.

    Production agents must not call this against the committed provisional tree.
    """
    directory = Path(directory)
    manifest = load_json(directory / MANIFEST_NAME)
    # Signed authority requires a non-provisional status marker.
    manifest["status"] = "frozen_signed_for_tests_only"
    freeze = dict(manifest["freeze"])
    freeze.update({
        "signed": True,
        "g3_status": g3_status,
        "accepting_owner": accepting_owner,
        "freeze_commit": freeze_commit,
        "freeze_timestamp": "2099-01-01T00:00:00+00:00",
        "note": "TEST-ONLY signature. Never copy into the committed provisional tree.",
    })
    # Keep component hashes in sync with on-disk files.
    freeze["component_sha256"] = compute_component_hashes(directory, manifest)
    manifest["freeze"] = freeze
    # Executable schedule flag may be true only under test signature.
    schedule = load_json(directory / SCHEDULE_NAME)
    schedule["executable"] = True
    schedule["status"] = "frozen_signed_for_tests_only"
    write_json(directory / SCHEDULE_NAME, schedule)
    manifest["freeze"]["component_sha256"] = compute_component_hashes(directory, manifest)
    write_json(directory / MANIFEST_NAME, manifest)
    return validate_freeze_authority(directory, require_signed=True)
