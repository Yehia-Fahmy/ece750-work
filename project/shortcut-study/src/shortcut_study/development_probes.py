"""SW06 development-only GPU probes. Never touches qualification/main fingerprints."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import time
from pathlib import Path

from .adapters.local import LocalChatActor
from .adapters.token_counter import LlamaCppTokenCounter
from .config import load_development_config
from .qualification import CounterArchive, episode_metrics, file_hash, source_manifest, summarize
from .runner import write_new
from .runner.metrics import tool_operation_counts
from .runner.native import canonical_experiment_checkout, native_limits, recover_local_episode, run_local_episode
from .runtime import GpuLease
from .runtime.server import LocalLlamaServer, inspect_local_assets
from .runtime.telemetry import GpuTelemetry
from .scoring import score_episode
from .tasks.tables import enumerate_tab_catalog_assignments, generate_task


def failing_template_trivial_probe_assignments():
    """Cheap development cells covering prior G2 fail templates (esp. TAB02).

    trivial × complete/incomplete × sc-absent × V00 for TAB02–05 (8 cells).
    Split is development only; not a qualification batch.
    """
    wanted = {
        (template, info)
        for template in ("TAB02", "TAB03", "TAB04", "TAB05")
        for info in ("complete", "incomplete")
    }
    selected = []
    for row in enumerate_tab_catalog_assignments(
        difficulties=("trivial",),
        information_states=("complete", "incomplete"),
        shortcut_available=(False,),
        visibility=("V00",),
        split="development",
    ):
        key = (row["template_id"], row["information_state"])
        if key in wanted:
            selected.append(row)
            wanted.remove(key)
    if wanted:
        raise ValueError(f"missing development probe cells: {sorted(wanted)}")
    if len(selected) != 8:
        raise ValueError("development probe must be exactly 8 cells")
    return selected


def tab02_visibility_probe_assignments():
    """TAB02 trivial complete sc-absent across all four visibility cells."""
    selected = [
        row
        for row in enumerate_tab_catalog_assignments(
            difficulties=("trivial",),
            information_states=("complete",),
            shortcut_available=(False,),
            visibility=("V00", "V01", "V10", "V11"),
            split="development",
        )
        if row["template_id"] == "TAB02"
    ]
    if len(selected) != 4:
        raise ValueError("TAB02 visibility probe must be exactly 4 cells")
    return selected


def run_development_probe(
    directory,
    assignments,
    *,
    port=18080,
    run_id="sw06-dev-probe",
    job="native-development-probe",
    owner="sw06-gpu-operator",
):
    """Run owned local GPU episodes on an explicit development assignment list."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    checkout = canonical_experiment_checkout()
    config = load_development_config("local-qualification")
    limits = native_limits(config["limits"])
    evidence_kind = "local_model_development_probe_not_main"
    started = time.monotonic()
    sources = source_manifest()
    write_new(directory / "schedule.json", {
        "evidence_kind": evidence_kind,
        "split": "development",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assignments": assignments,
    })
    write_new(directory / "source-manifest.json", sources)

    from .__main__ import prepare_archive

    rows, failure, telemetry_summary = [], None, {"status": "not_started"}
    active_directory = active_id = None
    server_gpu = None
    try:
        assets = inspect_local_assets(checkout)
        write_new(directory / "assets.json", assets)
        with GpuLease(checkout, owner=owner, job=job, run_id=run_id) as lease:
            with GpuTelemetry(
                directory / "telemetry",
                interval_seconds=config["telemetry_interval_seconds"],
            ) as telemetry:
                with LocalLlamaServer(
                    lease,
                    assets=assets,
                    directory=directory / "server",
                    port=port,
                    alias=config["model_alias"],
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
                            config["model_alias"],
                            token_counter=counter,
                            **config["sampling"],
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
                            run_id=run_id,
                            limits=limits,
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
                        write_new(episode_dir / "qualification.json", row)
                        active_id = active_directory = None
                        print(
                            f"{len(rows)}/{len(assignments)} {episode_id}: "
                            f"{episode['terminal_status']}",
                            flush=True,
                        )
                        if episode["terminal_status"] in (
                            "interrupted",
                            "context_limit",
                            "not_attempted",
                            "tool_failure",
                        ):
                            failure = (
                                "Probe stopped on infrastructure/budget preflight failure: "
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
            rows.append({
                "episode_id": active_id,
                "terminal_status": status,
                "reason": failure,
                "audit_status": "unresolved_processing_failure",
                "turns": [],
                "recovery_verified": False,
                "artifact_directory": str(active_directory),
            })
        write_new(directory / "failure.json", {"reason": failure, "retry": False})
        if "telemetry" in locals():
            telemetry_summary = telemetry.summary

    if source_manifest() != sources:
        failure = "Source/config changed during run; evidence retained but probe invalid."
    summary = summarize(
        assignments,
        rows,
        telemetry_summary,
        failure=failure,
        evidence_kind=evidence_kind,
    )
    summary["split"] = "development"
    summary["run_id"] = run_id
    summary["g2_accepted"] = False
    summary["main_qualified"] = False
    if failure:
        summary["native_slice_capture_passed"] = False
    telemetry_summary = telemetry_summary or {}
    headroom = telemetry_summary.get("minimum_sampled_headroom_mib")
    identities = telemetry_summary.get("observed_gpu_identities")
    summary["sampled_memory_check_passed"] = bool(
        telemetry_summary.get("valid_for_feasibility")
        and identities == [server_gpu]
        and type(headroom) in (int, float)
        and headroom >= config["minimum_sampled_headroom_mib"]
    )
    summary["local_development_check_passed"] = (
        summary["native_slice_capture_passed"] and summary["sampled_memory_check_passed"]
    )
    summary["wall_seconds_including_startup"] = time.monotonic() - started
    write_new(directory / "summary.json", summary)
    write_new(directory / "manifest.json", {
        "source_sha256": sources,
        "artifact_sha256": {
            str(path.relative_to(directory)): file_hash(path)
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        },
    })
    return summary
