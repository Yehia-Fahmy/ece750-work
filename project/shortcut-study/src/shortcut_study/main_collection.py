"""Signed-freeze main collection (SW08) on the owned local GPU.

Requires ``configs/frozen/<version>/`` with ``freeze.signed=true`` and matching
component hashes. Uses the frozen schedule denominator (default 320). Never
calls cloud APIs. Behavioral-only scope: prepares audit inputs without judge
inference. ``submission_authorized`` is not flipped here.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import time

from .adapters.local import LocalChatActor
from .adapters.token_counter import LlamaCppTokenCounter
from .config import load_development_config
from .freeze import (
    PROTOCOL_CANDIDATE,
    authorize_main_execution,
    dry_validate_schedule,
    frozen_dir,
    load_json,
)
from .qualification import CounterArchive, episode_metrics, file_hash, source_manifest, tool_operation_counts
from .runner import write_new
from .runner.native import (
    canonical_experiment_checkout,
    native_limits,
    recover_local_episode,
    run_local_episode,
)
from .runtime import GpuLease
from .runtime.server import LocalLlamaServer, inspect_local_assets
from .runtime.telemetry import GpuTelemetry
from .scoring import score_episode
from .tasks.tables import generate_task


def _load_frozen_assignments(freeze_path: Path) -> list[dict]:
    schedule = load_json(freeze_path / "schedule.json")
    if schedule.get("split") != "main":
        raise ValueError("frozen schedule.split must be main")
    if schedule.get("executable") is not True:
        raise ValueError("frozen schedule.executable must be true for main collection")
    assignments = schedule.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        raise ValueError("frozen schedule.assignments missing")
    for row in assignments:
        if row.get("split") != "main":
            raise ValueError(f"assignment {row.get('episode_id')!r} is not split=main")
    return list(assignments)


def _frozen_limits(freeze_path: Path) -> dict:
    budgets = load_json(freeze_path / "budgets.json")
    limits = budgets.get("candidate_limits") or budgets.get("development")
    if not isinstance(limits, dict):
        raise ValueError("frozen budgets.json missing candidate_limits")
    return native_limits(limits)


def _frozen_actor_settings(freeze_path: Path) -> dict:
    profile = load_json(freeze_path / "actor_profile.json")
    primary = profile.get("primary_actor") or {}
    sampling = primary.get("sampling") or {}
    alias = primary.get("model_alias") or "shortcut-qwen3-4b"
    if "temperature" not in sampling or "top_p" not in sampling:
        raise ValueError("frozen actor_profile.primary_actor.sampling incomplete")
    return {
        "model_alias": alias,
        "sampling": {
            "temperature": float(sampling["temperature"]),
            "top_p": float(sampling["top_p"]),
        },
        "server_context_tokens": primary.get("server_context_tokens"),
    }


def summarize_main(assignments, rows, telemetry, *, failure=None, freeze_authority=None):
    """Keep the assigned main denominator, including never-started records."""
    if len({r["episode_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate episode result")
    by_id = {row["episode_id"]: row for row in rows}
    expected = {a["episode_id"] for a in assignments}
    if set(by_id) - expected:
        raise ValueError("result outside assigned schedule")
    outcomes = [
        by_id.get(
            a["episode_id"],
            {
                "episode_id": a["episode_id"],
                "terminal_status": "not_attempted",
                "reason": failure or "Run stopped before this assigned episode.",
                "audit_status": "unresolved_not_attempted",
                "turns": [],
            },
        )
        for a in assignments
    ]
    counts = Counter(row["terminal_status"] for row in outcomes)
    completed = counts["completed"]
    turns = [turn for row in outcomes for turn in row.get("turns", [])]
    elapsed = [row["elapsed_seconds"] for row in outcomes if "elapsed_seconds" in row]
    return {
        "schema_version": "shortcut-main-collection-result-v1",
        "evidence_kind": "local_model_frozen_main_s0_tab_v0",
        "protocol_version": PROTOCOL_CANDIDATE,
        "split": "main",
        "assigned": len(assignments),
        "recorded_episodes": len(rows),
        "terminal_counts": dict(counts),
        "completed": completed,
        "completion_rate": completed / len(assignments) if assignments else None,
        "outcomes": outcomes,
        "failure": failure,
        "telemetry": telemetry,
        "freeze_authority": {
            "directory": None if freeze_authority is None else freeze_authority["directory"],
            "freeze_commit": None if freeze_authority is None else freeze_authority["freeze_commit"],
            "accepting_owner": None if freeze_authority is None else freeze_authority["accepting_owner"],
            "signed": True,
            "g3_status": "accepted",
        },
        "semantic_scope": "withdrawn_behavioral_only",
        "submission_authorized": False,
        "native_slice_capture_passed": bool(assignments)
        and completed == len(assignments)
        and bool(turns)
        and all(
            t["count_matches"] and t["native_reasoning_present"] and t["native_action_present"]
            for t in turns
        )
        and all(
            r.get("recovery_verified") and r.get("audit_status") == "prepared_no_judge"
            for r in outcomes
        ),
        "episode_latency_seconds": {
            "n": len(elapsed),
            "mean": (sum(elapsed) / len(elapsed)) if elapsed else None,
        },
        "limitations": [
            "Frozen S0 TAB-only main collection under signed configs/frozen/s0-tab-v0/.",
            "Behavioral-only: audit inputs prepared; no live semantic judge inference.",
            "submission_authorized remains false; course upload is Yehia-only.",
            "GPU memory is sampled; unsampled peaks may be higher.",
            "Interrupted/unattempted IDs remain in the assigned denominator.",
        ],
    }


def write_progress(directory: Path, *, assigned: int, rows: list, failure=None):
    counts = Counter(row["terminal_status"] for row in rows)
    payload = {
        "schema_version": "shortcut-main-collection-progress-v1",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "assigned": assigned,
        "recorded": len(rows),
        "terminal_counts": dict(counts),
        "failure": failure,
        "last_episode_id": None if not rows else rows[-1]["episode_id"],
        "last_terminal_status": None if not rows else rows[-1]["terminal_status"],
    }
    path = directory / "progress.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def run_main_collection(
    directory,
    *,
    port=18300,
    freeze_path=None,
    protocol_version=PROTOCOL_CANDIDATE,
):
    """Collect the signed frozen main schedule on the local RTX GPU only."""
    from .__main__ import prepare_archive

    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    freeze_path = Path(freeze_path) if freeze_path is not None else frozen_dir(protocol_version)
    freeze_authority = authorize_main_execution(freeze_path)
    dry = dry_validate_schedule(freeze_path)
    if dry.get("assigned") != 320:
        raise ValueError(f"expected 320 frozen main assignments, got {dry.get('assigned')}")
    # Re-check with signature so dry_executable reflects accepted authority.
    signed_authority = authorize_main_execution(freeze_path)
    if not signed_authority.get("executable_main"):
        raise ValueError("freeze authority did not set executable_main")
    if not dry.get("schedule_executable_flag"):
        raise ValueError("frozen schedule.executable is false")

    assignments = _load_frozen_assignments(freeze_path)
    limits = _frozen_limits(freeze_path)
    actor_settings = _frozen_actor_settings(freeze_path)
    # Operational telemetry thresholds stay with the owned local-qualification profile.
    ops_config = load_development_config("local-qualification")
    evidence_kind = "local_model_frozen_main_s0_tab_v0"
    job = "native-frozen-main-collection"
    started = time.monotonic()
    sources = source_manifest()
    write_new(
        directory / "schedule.json",
        {
            "evidence_kind": evidence_kind,
            "split": "main",
            "protocol_version": protocol_version,
            "freeze_directory": str(freeze_path),
            "freeze_commit": freeze_authority["freeze_commit"],
            "accepting_owner": freeze_authority["accepting_owner"],
            "assigned": len(assignments),
            "assignments": assignments,
            "limits": limits,
            "actor_settings": actor_settings,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "submission_authorized": False,
            "semantic_scope": "withdrawn_behavioral_only",
        },
    )
    write_new(directory / "freeze-authority.json", freeze_authority)
    write_new(directory / "source-manifest.json", sources)
    write_new(
        directory / "sampling-note.json",
        {
            "frozen_actor_profile_sampling": actor_settings["sampling"],
            "local_qualification_sampling": ops_config.get("sampling"),
            "authority": "frozen_actor_profile.primary_actor.sampling",
            "note": (
                "Main uses signed freeze actor_profile sampling. If this differs from "
                "local-qualification.json used for G2, that mismatch is disclosed here "
                "rather than silently rewritten."
            ),
        },
    )

    checkout = canonical_experiment_checkout()
    rows, failure, telemetry_summary = [], None, {"status": "not_started"}
    active_directory = active_id = None
    server_gpu = None
    try:
        assets = inspect_local_assets(checkout)
        write_new(directory / "assets.json", assets)
        with GpuLease(checkout, owner="sw08-main-operator", job=job, run_id=directory.name) as lease:
            with GpuTelemetry(
                directory / "telemetry",
                interval_seconds=ops_config["telemetry_interval_seconds"],
            ) as telemetry:
                with LocalLlamaServer(
                    lease,
                    assets=assets,
                    directory=directory / "server",
                    port=port,
                    alias=actor_settings["model_alias"],
                ) as server:
                    write_new(directory / "profile.json", server.profile)
                    server_gpu = server.manifest["gpu"]
                    for assignment in assignments:
                        server.assert_ready()
                        episode_id = assignment["episode_id"]
                        archive = CounterArchive(directory / "token-counts" / episode_id)
                        counter = LlamaCppTokenCounter(
                            server.base_url,
                            expected_props=server.props,
                            evidence_sink=archive,
                        )
                        actor = LocalChatActor(
                            server.base_url,
                            actor_settings["model_alias"],
                            token_counter=counter,
                            **actor_settings["sampling"],
                        )
                        generation_seed = int(assignment.get("generation_seed", 0))
                        task = generate_task(assignment, generation_seed=generation_seed)
                        episode_dir = directory / episode_id
                        active_id, active_directory = episode_id, episode_dir
                        episode, ledger = run_local_episode(
                            task,
                            actor,
                            episode_dir,
                            lease=lease,
                            profile=server.profile,
                            run_id=directory.name,
                            limits=limits,
                            freeze_dir=freeze_path,
                        )
                        ops, approved_reads = tool_operation_counts(
                            ledger,
                            approved_resources=task.public_task["approved_resources"],
                        )
                        first_operations = [
                            event["operation"]
                            for event in ledger["events"]
                            if event.get("event_type") == "tool_call"
                        ]
                        row = {
                            "episode_id": episode_id,
                            "terminal_status": episode["terminal_status"],
                            "reason": episode["terminal_reason"],
                            "elapsed_seconds": episode["timing"]["elapsed_seconds"],
                            "audit_status": "unresolved_incomplete_episode",
                            "turns": [],
                            "recovery_verified": False,
                            "tool_operation_counts": ops,
                            "approved_resources_read": sorted(approved_reads),
                            "first_operations": first_operations,
                        }
                        rows.append(row)
                        row["turns"] = episode_metrics(episode_dir)
                        score = score_episode(task, episode, ledger)
                        row["score"] = {
                            "task_result": score["task_result"],
                            "acquisition": score["acquisition"],
                        }
                        write_new(episode_dir / "scored.json", score)
                        recovered = recover_local_episode(episode_dir, actor)
                        if recovered != (episode, ledger):
                            raise ValueError("native recovery changed a terminal record")
                        row["recovery_verified"] = True
                        if episode["terminal_status"] == "completed":
                            prepare_archive(episode_dir, directory / "audit-inputs" / episode_id)
                            row["audit_status"] = "prepared_no_judge"
                        write_new(episode_dir / "main-collection.json", row)
                        active_id = active_directory = None
                        write_progress(directory, assigned=len(assignments), rows=rows)
                        print(
                            f"{len(rows)}/{len(assignments)} {episode_id}: {episode['terminal_status']}",
                            flush=True,
                        )
                        if episode["terminal_status"] in (
                            "interrupted",
                            "context_limit",
                            "not_attempted",
                            "tool_failure",
                        ):
                            failure = (
                                "Main collection stopped on infrastructure/budget preflight failure: "
                                + episode["terminal_reason"]
                            )
                            break
            telemetry_summary = telemetry.summary
    except (Exception, KeyboardInterrupt) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if active_id is not None and not any(row["episode_id"] == active_id for row in rows):
            terminal = active_directory / "terminal.json"
            status = (
                "interrupted"
                if list(active_directory.glob("turn-*-request.json"))
                else "not_attempted"
            )
            if terminal.exists():
                try:
                    status = json.loads(terminal.read_text())["episode"]["terminal_status"]
                except (ValueError, KeyError, OSError):
                    status = "interrupted"
            rows.append(
                {
                    "episode_id": active_id,
                    "terminal_status": status,
                    "reason": failure,
                    "audit_status": "unresolved_processing_failure",
                    "turns": [],
                    "recovery_verified": False,
                    "artifact_directory": str(active_directory),
                }
            )
        write_new(directory / "failure.json", {"reason": failure, "retry": False})
        if "telemetry" in locals():
            telemetry_summary = telemetry.summary
        write_progress(directory, assigned=len(assignments), rows=rows, failure=failure)

    if source_manifest() != sources:
        failure = "Source/config changed during run; evidence retained but main run integrity flagged."

    summary = summarize_main(
        assignments,
        rows,
        telemetry_summary,
        failure=failure,
        freeze_authority=freeze_authority,
    )
    telemetry_summary = telemetry_summary or {}
    headroom = telemetry_summary.get("minimum_sampled_headroom_mib")
    identities = telemetry_summary.get("observed_gpu_identities")
    summary["sampled_memory_check_passed"] = bool(
        telemetry_summary.get("valid_for_feasibility")
        and identities == [server_gpu]
        and type(headroom) in (int, float)
        and headroom >= ops_config["minimum_sampled_headroom_mib"]
    )
    if failure:
        summary["native_slice_capture_passed"] = False
    summary["local_main_collection_check_passed"] = (
        summary["native_slice_capture_passed"] and summary["sampled_memory_check_passed"]
    )
    summary["wall_seconds_including_startup"] = time.monotonic() - started
    write_progress(directory, assigned=len(assignments), rows=rows, failure=failure)
    write_new(directory / "summary.json", summary)
    write_new(
        directory / "manifest.json",
        {
            "evidence_kind": evidence_kind,
            "source_sha256": sources,
            "freeze_component_sha256": freeze_authority["component_sha256"],
            "artifact_sha256": {
                str(p.relative_to(directory)): file_hash(p)
                for p in sorted(directory.rglob("*"))
                if p.is_file()
            },
        },
    )
    return summary
