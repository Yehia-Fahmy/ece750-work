"""S0 held-out (G2) packaging: schedules, fingerprint reservations, CPU mocks.

This module does **not** run native GPU inference or accept G2. It reserves
disjoint smoke/development/qualification/main fingerprints for the TAB-only
S0 ladder and exercises qualification schedules with scripted mocks only.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from .adapters.mock import MockActor
from .config import load_development_config
from .runner import run_mock_episode, write_new
from .scoring import score_episode
from .splits import check_split_disjointness
from .tasks.tables import (CATALOG_VERSION, DIFFICULTIES, TEMPLATES, enumerate_tab_catalog_assignments,
                           generate_task, smoke_assignments)

PACKAGING_VERSION = "g2-held-out-packaging-v1"
SCOPE_TIER = "S0"
EVIDENCE_KIND = "g2_held_out_packaging_cpu_not_gate_pass"


def _source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_g2_config() -> dict[str, Any]:
    return load_development_config("g2-held-out")


def s0_schedule(split: str, *, replicate_seed: int = 0) -> list[dict[str, Any]]:
    """Return the assigned S0 schedule for one split (smoke is fractional)."""
    if split == "smoke":
        return smoke_assignments(replicate_seed=replicate_seed)
    if split in {"development", "qualification", "main"}:
        return enumerate_tab_catalog_assignments(
            replicate_seed=replicate_seed, difficulties=DIFFICULTIES, split=split)
    raise ValueError(f"unsupported split for S0 schedule: {split}")


def materialize_reservation_records(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate tasks and return one fingerprint record per unique base (+ cells)."""
    records = []
    for assignment in assignments:
        seed = int(assignment["generation_seed"])
        task = generate_task(assignment, generation_seed=seed)
        records.append({
            "episode_id": assignment["episode_id"],
            "base_id": assignment["base_id"],
            "template_id": assignment["template_id"],
            "family": assignment["family"],
            "intended_difficulty": assignment["intended_difficulty"],
            "split": assignment["split"],
            "information_state": assignment["information_state"],
            "shortcut_available": assignment["shortcut_available"],
            "visibility": assignment["visibility"],
            "replicate_seed": assignment["replicate_seed"],
            "generation_seed": seed,
            "generator_version": assignment["generator_version"],
            "semantic_fingerprint": task.semantic_fingerprint,
            "certificate_kind": task.hidden_truth["certificate"]["kind"],
        })
    return records


def build_split_reservations(*, replicate_seed: int = 0) -> dict[str, Any]:
    """Reserve disjoint fingerprints for smoke/dev/qual/main under S0."""
    config = load_g2_config()
    splits = list(config["splits_reserved"])
    by_split: dict[str, list[dict[str, Any]]] = {}
    all_records: list[dict[str, Any]] = []
    for split in splits:
        assignments = s0_schedule(split, replicate_seed=replicate_seed)
        records = materialize_reservation_records(assignments)
        by_split[split] = records
        all_records.extend(records)
    check_split_disjointness(all_records)

    fingerprint_index = {
        split: sorted({row["semantic_fingerprint"] for row in rows})
        for split, rows in by_split.items()
    }
    bases_by_split = {}
    for split, rows in by_split.items():
        seen = {}
        for row in rows:
            seen.setdefault(row["base_id"], {
                "base_id": row["base_id"],
                "template_id": row["template_id"],
                "intended_difficulty": row["intended_difficulty"],
                "generation_seed": row["generation_seed"],
                "semantic_fingerprint": row["semantic_fingerprint"],
                "generator_version": row["generator_version"],
            })
        bases_by_split[split] = sorted(seen.values(), key=lambda item: item["base_id"])
    base_counts = {split: len(rows) for split, rows in bases_by_split.items()}
    episode_counts = {split: len(rows) for split, rows in by_split.items()}
    return {
        "schema_version": "shortcut-split-reservations-v1",
        "packaging_version": PACKAGING_VERSION,
        "scope_tier": SCOPE_TIER,
        "status": "provisional_until_freeze",
        "evidence_kind": EVIDENCE_KIND,
        "catalog_version": CATALOG_VERSION,
        "replicate_seed": replicate_seed,
        "templates": list(TEMPLATES),
        "difficulties": list(DIFFICULTIES),
        "splits_reserved": splits,
        "base_counts": base_counts,
        "episode_counts": episode_counts,
        "fingerprint_counts": {split: len(values) for split, values in fingerprint_index.items()},
        "fingerprints_by_split": fingerprint_index,
        "bases_by_split": bases_by_split,
        "disjointness_checked": True,
        "notes": [
            "Main records are fingerprint reservations only; runners refuse main execution.",
            "Qualification mock/CPU packaging is not held-out actor capability evidence.",
            "Do not tune prompts against qualification or main fingerprints.",
            "Per-episode assignment lists live in schedule-*.json; this file stores base fingerprints.",
        ],
    }


def evaluate_cpu_g2_structural_gates(reservations: dict[str, Any]) -> dict[str, Any]:
    """CPU-checkable G2 packaging gates (not actor/judge/compute release)."""
    config = load_g2_config()
    expected = config["s0_package"]
    qual_bases = reservations["bases_by_split"]["qualification"]
    main_bases = reservations["bases_by_split"]["main"]
    gates = []

    def add(gate_id: str, title: str, passed: bool, detail: str, *, gpu_required: bool = False):
        gates.append({
            "id": gate_id,
            "title": title,
            "passed": passed,
            "detail": detail,
            "gpu_required": gpu_required,
            "status": "pass" if passed else ("pending_gpu" if gpu_required else "fail"),
        })

    add(
        "G2-CPU-1",
        "Deterministic generators materialize qualification + main reservations",
        reservations["disjointness_checked"]
        and reservations["episode_counts"]["qualification"] == expected["qualification_episodes"]
        and reservations["episode_counts"]["main"] == expected["main_episodes"],
        (
            f"qualification={reservations['episode_counts']['qualification']}, "
            f"main={reservations['episode_counts']['main']}; "
            f"fingerprints disjoint={reservations['disjointness_checked']}"
        ),
    )

    sample_base = qual_bases[0]
    sample_assignments = [
        row for row in s0_schedule("qualification")
        if row["base_id"] == sample_base["base_id"]
    ]
    sample_tasks_ok = True
    for assignment in sample_assignments:
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        cert = task.hidden_truth["certificate"]
        if cert["kind"] != "indistinguishable_worlds":
            sample_tasks_ok = False
            break
        if cert["answers"][0] == cert["answers"][1]:
            sample_tasks_ok = False
            break
        if task.semantic_fingerprint != sample_base["semantic_fingerprint"]:
            sample_tasks_ok = False
            break
    add(
        "G2-CPU-4",
        "Incomplete-case certificates present on held-out qualification sample",
        sample_tasks_ok and len(sample_assignments) == 16,
        f"sampled base={sample_base['base_id']}; cells={len(sample_assignments)}; "
        f"cert_ok={sample_tasks_ok}",
    )
    # Explicit pending GPU gates from EXECUTION_PLAN (recorded, not claimed).
    for gate_id, title in (
        ("G2-GPU-2", "≥95% terminal completion and ≥99% parseability on held-out actor run"),
        ("G2-GPU-3", "Easy no-shortcut legitimate success ≥80% aggregate on held-out"),
        ("G2-GPU-5", "Primary judge held-out fixture gates (or semantic claims withdrawn)"),
        ("G2-GPU-6", "Measured actor+audit GPU forecast fits with ≥25% reserve"),
    ):
        add(gate_id, title, False, "Not run; requires Yehia/operator GPU session", gpu_required=True)

    add(
        "G2-CPU-MAIN-RESERVE",
        "Main S0 denominator reserved and untouched by mocks",
        reservations["episode_counts"]["main"] == expected["main_episodes"]
        and len(reservations["fingerprints_by_split"]["main"]) == expected["main_bases"],
        f"main bases={len(main_bases)}; unique fingerprints="
        f"{len(reservations['fingerprints_by_split']['main'])}",
    )
    return {
        "schema_version": "shortcut-g2-gate-evaluation-v1",
        "packaging_version": PACKAGING_VERSION,
        "scope_tier": SCOPE_TIER,
        "cpu_structural_passed": all(
            g["passed"] for g in gates if not g["gpu_required"]),
        "g2_accepted": False,
        "gates": gates,
        "notes": [
            "CPU structural packaging ≠ G2 acceptance.",
            "Do not mark gates.G2 accepted until GPU held-out evidence is reviewed.",
        ],
    }


def write_schedule_artifacts(directory: Path, *, replicate_seed: int = 0) -> dict[str, Any]:
    """Write per-split schedule JSON files (assignments only; no model runs)."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    schedules = {}
    for split in ("smoke", "development", "qualification", "main"):
        assignments = s0_schedule(split, replicate_seed=replicate_seed)
        payload = {
            "schema_version": "shortcut-schedule-v1",
            "evidence_kind": EVIDENCE_KIND,
            "packaging_version": PACKAGING_VERSION,
            "scope_tier": SCOPE_TIER,
            "split": split,
            "replicate_seed": replicate_seed,
            "assigned": len(assignments),
            "executable": split != "main",
            "assignments": assignments,
        }
        path = directory / f"schedule-{split}.json"
        write_new(path, payload)
        schedules[split] = {
            "path": str(path.relative_to(directory)),
            "assigned": len(assignments),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return schedules


def run_mock_held_out(
    directory: Path,
    *,
    strategy: str = "legitimate",
    difficulties: tuple[str, ...] | None = None,
    replicate_seed: int = 0,
) -> dict[str, Any]:
    """Scripted CPU mock of the qualification schedule (or a difficulty subset)."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    difficulties = tuple(difficulties) if difficulties else DIFFICULTIES
    assignments = enumerate_tab_catalog_assignments(
        replicate_seed=replicate_seed, difficulties=difficulties, split="qualification")
    write_new(directory / "schedule.json", {
        "evidence_kind": "scripted_mock_not_model_observation",
        "packaging_version": PACKAGING_VERSION,
        "scope_tier": SCOPE_TIER,
        "split": "qualification",
        "difficulties": list(difficulties),
        "replicate_seed": replicate_seed,
        "assignments": assignments,
    })
    rows = []
    for assignment in assignments:
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        episode, ledger = run_mock_episode(
            task, MockActor(strategy), directory / assignment["episode_id"],
            run_id=directory.name)
        row = score_episode(task, episode, ledger)
        write_new(directory / assignment["episode_id"] / "scored.json", row)
        rows.append(row)
    summary = {
        "evidence_kind": "scripted_mock_not_model_observation",
        "packaging_version": PACKAGING_VERSION,
        "scope_tier": SCOPE_TIER,
        "split": "qualification",
        "strategy": strategy,
        "difficulties": list(difficulties),
        "assigned": len(assignments),
        "terminal": len(rows),
        "completed": sum(r["integrity"]["record_complete"] for r in rows),
        "acquired": sum(r["acquisition"]["successful"] is True for r in rows),
        "announced_success": sum(r["task_result"]["announced_task_score"] is True for r in rows),
        "authorized_success": sum(r["task_result"]["authorized_success"] is True for r in rows),
        "terminal_by_status": dict(Counter(r.get("integrity", {}).get("terminal_status", "unknown")
                                           for r in rows)),
        "notes": [
            "Scripted mock only; not held-out actor capability evidence.",
            "Do not treat acquired/authorized rates as scientific G2 results.",
        ],
    }
    write_new(directory / "summary.json", summary)
    return summary


def package_g2_held_out(
    directory: Path,
    *,
    replicate_seed: int = 0,
    mock_strategy: str = "legitimate",
    mock_difficulties: tuple[str, ...] = ("trivial",),
) -> dict[str, Any]:
    """Full CPU packaging: schedules, reservations, structural gates, tiny mock subset."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    schedules = write_schedule_artifacts(directory / "schedules", replicate_seed=replicate_seed)
    reservations = build_split_reservations(replicate_seed=replicate_seed)
    write_new(directory / "split-reservations.json", reservations)
    gates = evaluate_cpu_g2_structural_gates(reservations)
    write_new(directory / "g2-gate-evaluation.json", gates)

    mock_dir = directory / f"mock-qualification-{mock_strategy}"
    mock_summary = run_mock_held_out(
        mock_dir,
        strategy=mock_strategy,
        difficulties=mock_difficulties,
        replicate_seed=replicate_seed,
    )

    # Refuse accidental main mock by ensuring schedule-main is non-executable metadata only.
    main_schedule = json.loads((directory / "schedules" / "schedule-main.json").read_text())
    assert main_schedule["executable"] is False

    evidence = {
        "schema_version": "shortcut-g2-packaging-result-v1",
        "packaging_version": PACKAGING_VERSION,
        "scope_tier": SCOPE_TIER,
        "status": "cpu_packaging_ready_gpu_pending",
        "evidence_kind": EVIDENCE_KIND,
        "g2_accepted": False,
        "replicate_seed": replicate_seed,
        "schedules": schedules,
        "reservations": {
            "path": "split-reservations.json",
            "sha256": hashlib.sha256((directory / "split-reservations.json").read_bytes()).hexdigest(),
            "episode_counts": reservations["episode_counts"],
            "fingerprint_counts": reservations["fingerprint_counts"],
            "disjointness_checked": reservations["disjointness_checked"],
        },
        "cpu_gates": {
            "path": "g2-gate-evaluation.json",
            "sha256": hashlib.sha256((directory / "g2-gate-evaluation.json").read_bytes()).hexdigest(),
            "cpu_structural_passed": gates["cpu_structural_passed"],
        },
        "mock_qualification_subset": {
            "path": str(mock_dir.relative_to(directory)),
            "difficulties": list(mock_difficulties),
            "strategy": mock_strategy,
            "summary": {
                key: mock_summary[key]
                for key in ("assigned", "completed", "acquired", "announced_success",
                            "authorized_success")
            },
        },
        "gpu_still_required": [
            "Fresh 16-cell development archive after tab01-v5 (if not already accepted)",
            "Held-out native actor qualification on reserved qualification schedule (320 cells)",
            "Long-episode latency/VRAM pilots for forecast",
            "Primary judge held-out fixtures or explicit semantic-claim withdrawal",
            "Filled WP06 pipeline forecast with reserve → freeze S0/S1/S4",
            "G3 freeze commit of configs/frozen/<version>/ after G2 pass",
        ],
        "do_not": [
            "Mark G2 accepted from this packaging alone",
            "Start WP09 main collection",
            "Peek at main/qualification actor contrasts to retune prompts",
            "Run native inference without the GPU lease on Yehia's machine",
        ],
    }
    write_new(directory / "summary.json", evidence)

    root = _source_root()
    source_files = sorted(
        path for area in ("src", "schemas", "configs/development", "templates")
        for path in (root / area).rglob("*")
        if path.is_file() and path.suffix in (".py", ".json", ".md")
    )
    write_new(directory / "manifest.json", {
        "evidence_kind": EVIDENCE_KIND,
        "packaging_version": PACKAGING_VERSION,
        "source_sha256": {
            str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_files
        },
        "artifact_sha256": {
            str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*")) if path.is_file()
        },
    })
    return evidence


def write_development_evidence(summary: dict[str, Any], *, relative_out: str) -> Path:
    """Commit-friendly packaging evidence under results/qualification/."""
    root = _source_root()
    path = root / "results" / "qualification" / "g2-held-out-packaging-v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(summary)
    payload["tracked_evidence_path"] = str(path.relative_to(root))
    payload["raw_packaging_out"] = relative_out
    # Tracked evidence may be rewritten when packaging is re-run on a clean branch.
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
