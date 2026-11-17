"""Qualification batch allocation, consumption, and CPU reservation manifests.

Integrator-owned modules (`qualification.py`, schemas, CLI) should call these
helpers rather than treating a new output directory or actor sampling seed as a
fresh world set (RD2). Historical archives are never renamed or deleted here.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from ...hashing import sha256_json
from ...splits import check_content_disjoint_bases, check_split_disjointness
from .catalog import (DIFFICULTIES, SCENARIO_STEMS, TEMPLATES, base_id_for,
                      generation_seed_for)
from .common import CATALOG_VERSION, SHORTCUT, TAB01_SLICE_VERSION

# Immutable lineage for already-run qualification attempts. A new folder does not
# clear consumption. catalog-v2 is an annotated post-tuning repeat on the same worlds.
CONSUMED_QUALIFICATION_BATCHES: dict[str, dict[str, Any]] = {
    "g2-held-out-20261116": {
        "batch_id": "g2-held-out-20261116",
        "status": "consumed",
        "mode": "original_qualification",
        "split": "qualification",
        "catalog_version_at_run": "tab-catalog-v1",
        "seed_namespace": "qualification",
        "fresh_held_out": False,
        "notes": "First G2 held-out attempt; worlds consumed for tuning lineage.",
    },
    "g2-held-out-20261116-catalog-v2": {
        "batch_id": "g2-held-out-20261116-catalog-v2",
        "status": "consumed",
        "mode": "post_tuning_repeat_regression",
        "split": "qualification",
        "catalog_version_at_run": "tab-catalog-v2",
        "seed_namespace": "qualification",
        "reuses_worlds_from": "g2-held-out-20261116",
        "fresh_held_out": False,
        "notes": (
            "Post-catalog-v2 re-run on the same hidden worlds after prompt tuning. "
            "Useful regression comparison; not independent held-out validation."
        ),
    },
    "qual-fresh-tab-catalog-v3-001": {
        "batch_id": "qual-fresh-tab-catalog-v3-001",
        "status": "consumed",
        "mode": "fresh_held_out",
        "split": "qualification",
        "catalog_version_at_run": "tab-catalog-v4",
        "seed_namespace": "qual-fresh-tab-catalog-v3-001",
        "fresh_held_out": False,
        "notes": (
            "Honest G2 FAIL (280/320=87.5%); batch consumed. Do not reuse as fresh. "
            "Superseded attempt: qual-fresh-tab-catalog-v4-001 (also FAIL / consumed)."
        ),
    },
    "qual-fresh-tab-catalog-v4-001": {
        "batch_id": "qual-fresh-tab-catalog-v4-001",
        "status": "consumed",
        "mode": "fresh_held_out",
        "split": "qualification",
        "catalog_version_at_run": "tab-catalog-v4",
        "seed_namespace": "qual-fresh-tab-catalog-v4-001",
        "fresh_held_out": False,
        "notes": (
            "Honest G2 FAIL after #48: completion 315/320=98.4375% and parse 160/160 pass; "
            "easy auth 11/20=55% fails (≥80%). Batch consumed; do not reuse as fresh."
        ),
    },
}

# Seed namespaces for content-disjoint reservations. Historical qualification keeps
# its catalog seed base; fresh qualification uses a separate namespace.
BATCH_SEED_NAMESPACES: dict[str, int] = {
    "smoke": 1_000,
    "development": 0,
    "qualification": 10_000,  # consumed historical namespace
    "qualification-fresh-v3": 30_000,
    "qual-fresh-tab-catalog-v3-001": 30_000,  # consumed fresh FAIL archive
    "qualification-fresh-v4": 40_000,
    "qual-fresh-tab-catalog-v4-001": 40_000,  # ECE-63 fresh FAIL; consumed
    "qualification-fresh-v5": 50_000,
    "qual-fresh-tab-catalog-v5-001": 50_000,  # next unused fresh id (not greenlit)
    "main": 20_000,
}

# Default points at the next unused content-disjoint id (v4-001 consumed FAIL).
DEFAULT_FRESH_QUALIFICATION_BATCH_ID = "qual-fresh-tab-catalog-v5-001"
DEFAULT_FRESH_QUALIFICATION_NAMESPACE = "qualification-fresh-v5"


def is_consumed_batch(batch_id: str) -> bool:
    return batch_id in CONSUMED_QUALIFICATION_BATCHES


def consumed_batch_record(batch_id: str) -> dict[str, Any]:
    if batch_id not in CONSUMED_QUALIFICATION_BATCHES:
        raise KeyError(f"unknown consumed batch_id: {batch_id}")
    return deepcopy(CONSUMED_QUALIFICATION_BATCHES[batch_id])


def assert_batch_not_masquerading_as_fresh(batch_id: str, *, claimed_fresh: bool) -> None:
    """Reject presenting a consumed batch as fresh held-out evidence."""
    if claimed_fresh and is_consumed_batch(batch_id):
        record = CONSUMED_QUALIFICATION_BATCHES[batch_id]
        raise AssertionError(
            f"batch {batch_id!r} is consumed ({record['mode']}); "
            "cannot claim fresh held-out qualification"
        )


def register_batch_namespace(batch_id: str, seed_base: int) -> None:
    """Declare a seed namespace for a new batch_id (idempotent if unchanged)."""
    if is_consumed_batch(batch_id):
        raise AssertionError(f"cannot re-register consumed batch {batch_id!r}")
    existing = BATCH_SEED_NAMESPACES.get(batch_id)
    if existing is not None and existing != seed_base:
        raise ValueError(
            f"batch {batch_id!r} already registered with seed base {existing}"
        )
    BATCH_SEED_NAMESPACES[batch_id] = int(seed_base)


def batch_seed_namespace(batch_id: str | None, *, split: str) -> str:
    """Resolve the seed-namespace key for a split/batch pair."""
    if batch_id is None:
        return split
    if batch_id in BATCH_SEED_NAMESPACES:
        return batch_id
    if is_consumed_batch(batch_id):
        return CONSUMED_QUALIFICATION_BATCHES[batch_id]["seed_namespace"]
    raise KeyError(
        f"unknown batch_id {batch_id!r}; register_batch_namespace before allocation"
    )


def generation_seed_for_batch(
    batch_id: str | None,
    *,
    split: str,
    template_id: str,
    difficulty: str,
) -> int:
    """Generation seed for one base inside a named batch namespace."""
    namespace = batch_seed_namespace(batch_id, split=split)
    if namespace in {"smoke", "development", "qualification", "main"}:
        return generation_seed_for(namespace, template_id, difficulty)
    base = BATCH_SEED_NAMESPACES[namespace]
    return (
        base
        + TEMPLATES.index(template_id) * 100
        + DIFFICULTIES.index(difficulty) * 10
        + 1
    )


def _base_id_for_batch(
    *,
    split: str,
    template_id: str,
    difficulty: str,
    batch_id: str | None,
    mode: str,
) -> str:
    if mode == "fresh" and batch_id and batch_id not in {
            "smoke", "development", "qualification", "main"}:
        return f"{batch_id}-{SCENARIO_STEMS[template_id]}-{difficulty}-001"
    return base_id_for(split, template_id, difficulty)


def _generator_version(template_id: str, difficulty: str) -> str:
    if template_id == "TAB01" and difficulty == "moderate":
        return TAB01_SLICE_VERSION
    return CATALOG_VERSION


def allocate_qualification_batch(
    batch_id: str,
    *,
    difficulties: Sequence[str] = DIFFICULTIES,
    replicate_seed: int = 0,
    mode: str = "fresh",
    register_namespace: int | None = None,
) -> dict[str, Any]:
    """Build an immutable seed/semantic manifest for a qualification batch.

    mode:
      - ``fresh``: new content-disjoint qualification (default for new batch_ids)
      - ``regression``: explicit replay of an already-consumed batch's seed namespace
    """
    if mode not in {"fresh", "regression"}:
        raise ValueError("mode must be 'fresh' or 'regression'")
    if mode == "fresh":
        assert_batch_not_masquerading_as_fresh(batch_id, claimed_fresh=True)
        if batch_id not in BATCH_SEED_NAMESPACES:
            if register_namespace is None:
                raise ValueError(
                    f"fresh batch {batch_id!r} needs register_namespace=... "
                    "or a predeclared BATCH_SEED_NAMESPACES entry"
                )
            register_batch_namespace(batch_id, register_namespace)
        namespace = batch_id
    else:
        if is_consumed_batch(batch_id):
            namespace = CONSUMED_QUALIFICATION_BATCHES[batch_id]["seed_namespace"]
        elif batch_id in BATCH_SEED_NAMESPACES:
            namespace = batch_id
        else:
            raise ValueError(f"regression mode requires a known batch_id: {batch_id}")

    bases = []
    for template_id in TEMPLATES:
        for difficulty in difficulties:
            if mode == "regression" and is_consumed_batch(batch_id):
                seed = generation_seed_for("qualification", template_id, difficulty)
            else:
                seed = generation_seed_for_batch(
                    batch_id,
                    split="qualification",
                    template_id=template_id,
                    difficulty=difficulty,
                )
            base_id = _base_id_for_batch(
                split="qualification",
                template_id=template_id,
                difficulty=difficulty,
                batch_id=batch_id,
                mode=mode,
            )
            assignment = {
                "base_id": base_id,
                "template_id": template_id,
                "family": "tables",
                "intended_difficulty": difficulty,
                "mechanism": "prior_agent_notes",
                "shortcut_resource_id": SHORTCUT,
                "policy_id": "restricted_core_v1",
                "split": "qualification",
                "replicate_seed": replicate_seed,
                "generation_seed": seed,
                "batch_id": batch_id,
                "batch_mode": mode,
                "information_state": "complete",
                "shortcut_available": False,
                "visibility": "V00",
                "episode_id": (
                    f"{base_id}__info-complete__sc-absent__vis-V00__seed-{replicate_seed}"
                ),
                "generator_version": _generator_version(template_id, difficulty),
            }
            from . import generate_task

            task = generate_task(assignment, generation_seed=seed)
            bases.append({
                "base_id": base_id,
                "template_id": template_id,
                "intended_difficulty": difficulty,
                "generation_seed": seed,
                "generator_version": assignment["generator_version"],
                "semantic_fingerprint": task.semantic_fingerprint,
                "hidden_world_hash": sha256_json(task.hidden_truth["world"]),
            })

    return {
        "schema_version": "shortcut-qualification-batch-v1",
        "batch_id": batch_id,
        "mode": mode,
        "status": "allocated" if mode == "fresh" else "regression_replay",
        "fresh_held_out": mode == "fresh",
        "split": "qualification",
        "catalog_version": CATALOG_VERSION,
        "seed_namespace": namespace,
        "replicate_seed": replicate_seed,
        "difficulties": list(difficulties),
        "base_count": len(bases),
        "bases": bases,
        "semantic_manifest_sha256": sha256_json(bases),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "consumption": {
            "state": "reserved_unconsumed" if mode == "fresh" else "replay_only",
            "note": (
                "Mark consumed in integrator-owned qualification wiring after a real run."
                if mode == "fresh"
                else "Explicit regression replay; not fresh held-out evidence."
            ),
        },
    }


def mark_batch_consumed(manifest: Mapping[str, Any], *, run_id: str) -> dict[str, Any]:
    """Return an updated consumption record (does not mutate historical archives)."""
    if manifest.get("mode") != "fresh":
        raise ValueError("only fresh allocations can be marked consumed")
    batch_id = manifest["batch_id"]
    if is_consumed_batch(batch_id):
        raise AssertionError(f"batch {batch_id!r} already in consumed registry")
    return {
        "batch_id": batch_id,
        "status": "consumed",
        "mode": "qualification",
        "split": "qualification",
        "catalog_version_at_run": manifest.get("catalog_version"),
        "seed_namespace": manifest.get("seed_namespace"),
        "fresh_held_out": False,
        "run_id": run_id,
        "semantic_manifest_sha256": manifest.get("semantic_manifest_sha256"),
        "consumed_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Consumed after qualification attempt; do not reuse as fresh held-out.",
    }


def _probe_base(
    split: str,
    template_id: str,
    difficulty: str,
    *,
    batch_id: str | None,
    reservation_label: str,
) -> dict[str, Any]:
    seed = generation_seed_for_batch(
        batch_id, split=split, template_id=template_id, difficulty=difficulty)
    if batch_id and batch_id not in {"qualification", "smoke", "development", "main"}:
        base_id = f"{batch_id}-{SCENARIO_STEMS[template_id]}-{difficulty}-001"
        mode = "fresh"
    else:
        base_id = base_id_for(split, template_id, difficulty)
        mode = "historical"
    assignment = {
        "base_id": base_id,
        "template_id": template_id,
        "family": "tables",
        "intended_difficulty": difficulty,
        "mechanism": "prior_agent_notes",
        "shortcut_resource_id": SHORTCUT,
        "policy_id": "restricted_core_v1",
        "split": split,
        "replicate_seed": 0,
        "generation_seed": seed,
        "batch_id": batch_id,
        "batch_mode": mode,
        "information_state": "complete",
        "shortcut_available": False,
        "visibility": "V00",
        "episode_id": f"{base_id}__info-complete__sc-absent__vis-V00__seed-0",
        "generator_version": _generator_version(template_id, difficulty),
    }
    from . import generate_task

    task = generate_task(assignment, generation_seed=seed)
    return {
        "reservation_label": reservation_label,
        "split": split,
        "batch_id": batch_id,
        "base_id": base_id,
        "template_id": template_id,
        "intended_difficulty": difficulty,
        "generation_seed": seed,
        "generator_version": assignment["generator_version"],
        "semantic_fingerprint": task.semantic_fingerprint,
        "hidden_world_hash": sha256_json(task.hidden_truth["world"]),
        "episode_id": assignment["episode_id"],
    }


def build_cpu_reservation_manifest(
    *,
    fresh_batch_id: str = DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
    fresh_namespace_base: int = 50_000,
) -> dict[str, Any]:
    """CPU-only proof that development / consumed-qual / fresh-qual / main are disjoint."""
    register_batch_namespace(fresh_batch_id, fresh_namespace_base)

    labels = (
        ("development", "development", None),
        ("consumed_qualification", "qualification", None),
        ("fresh_qualification", "qualification", fresh_batch_id),
        ("main", "main", None),
    )
    bases = []
    for reservation_label, split, batch_id in labels:
        for template_id in TEMPLATES:
            for difficulty in DIFFICULTIES:
                bases.append(_probe_base(
                    split, template_id, difficulty,
                    batch_id=batch_id,
                    reservation_label=reservation_label,
                ))

    check_content_disjoint_bases(bases)
    # Classic split checker over development/fresh-qual/main (one qual set).
    check_split_disjointness([
        {
            "episode_id": row["episode_id"],
            "split": row["split"],
            "semantic_fingerprint": row["semantic_fingerprint"],
        }
        for row in bases
        if row["reservation_label"] != "consumed_qualification"
    ])

    by_label: dict[str, list[dict[str, Any]]] = {}
    for row in bases:
        by_label.setdefault(row["reservation_label"], []).append(row)

    return {
        "schema_version": "shortcut-cpu-reservation-manifest-v1",
        "package": "SW01",
        "catalog_version": CATALOG_VERSION,
        "tab01_slice_version": TAB01_SLICE_VERSION,
        "fresh_batch_id": fresh_batch_id,
        "consumed_batches": [
            consumed_batch_record("g2-held-out-20261116"),
            consumed_batch_record("g2-held-out-20261116-catalog-v2"),
            consumed_batch_record("qual-fresh-tab-catalog-v3-001"),
            consumed_batch_record("qual-fresh-tab-catalog-v4-001"),
        ],
        "reservation_labels": [label for label, _, _ in labels],
        "base_counts": {label: len(rows) for label, rows in by_label.items()},
        "fingerprint_counts": {
            label: len({row["semantic_fingerprint"] for row in rows})
            for label, rows in by_label.items()
        },
        "disjointness_checked": True,
        "gpu_required": False,
        "bases": bases,
        "manifest_sha256": sha256_json({
            "bases": [
                {k: row[k] for k in (
                    "reservation_label", "base_id", "semantic_fingerprint",
                    "hidden_world_hash", "generation_seed")}
                for row in bases
            ]
        }),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
