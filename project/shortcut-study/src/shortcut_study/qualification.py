"""Owned local runtime qualification and a fixed development-only slice.

All inference is performed by the retained local GPU server. These records
establish engineering compatibility, not held-out capability or judge quality.
"""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

from .adapters.local import LocalChatActor
from .config import load_development_config
from .runner import write_new
from .runner.native import canonical_experiment_checkout, native_limits, recover_local_episode, run_local_episode
from .runtime import GpuLease
from .scoring import score_episode
from .ids import make_episode_id
from .runner.metrics import tool_operation_counts as task_tool_operation_counts
from .tasks.tables import (
    APPROVED,
    DIFFICULTIES,
    SHORTCUT,
    DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
    DEFAULT_FRESH_QUALIFICATION_NAMESPACE,
    BATCH_SEED_NAMESPACES,
    allocate_qualification_batch,
    enumerate_tab_catalog_assignments,
    generate_task,
    generator_version_for,
    is_consumed_batch,
    mark_batch_consumed,
)
from .vertical_slice import capability_probe_assignments, enumerate_vertical_slice_assignments

LONG_PILOT_TEMPLATES = ("TAB01", "TAB02", "TAB03", "TAB04", "TAB05")
LONG_PILOT_DIFFICULTIES = ("hard", "extreme")
VISIBILITY_CELLS = ("V00", "V01", "V10", "V11")
INFORMATION_STATES = ("complete", "incomplete")
SHORTCUT_AVAILABLE = (True, False)


def long_pilot_assignments():
    """Representative development hard/extreme complete episodes for WP06 notes.

    Uses split=development only (never qualification/main) so pilots cannot
    contaminate held-out fingerprints. Fixed: V00, shortcut absent, complete.
    """
    selected = []
    catalog = list(enumerate_tab_catalog_assignments(
        difficulties=LONG_PILOT_DIFFICULTIES, split="development"))
    for template_id in LONG_PILOT_TEMPLATES:
        for difficulty in LONG_PILOT_DIFFICULTIES:
            matches = [
                row for row in catalog
                if row["template_id"] == template_id
                and row["intended_difficulty"] == difficulty
                and row["information_state"] == "complete"
                and row["shortcut_available"] is False
                and row["visibility"] == "V00"
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"expected one long-pilot cell for {template_id}/{difficulty}, got {len(matches)}")
            selected.append(matches[0])
    if len(selected) != 10:
        raise ValueError("long pilot schedule must be exactly 10 development episodes")
    return selected


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_manifest():
    root = Path(__file__).resolve().parents[2]
    return {str(path.relative_to(root)): file_hash(path)
            for area in ("src", "schemas", "configs/development")
            for path in sorted((root / area).rglob("*"))
            if path.is_file() and path.suffix in (".py", ".json")}


class CounterArchive:
    """Immutable, ordered transport evidence independent of episode creation."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.index = 0

    def __call__(self, record):
        self.index += 1
        write_new(self.directory / f"record-{self.index:05d}.json", record)


def quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def episode_metrics(directory):
    """Derive count equivalence and native server timings from saved bytes."""
    import base64

    directory = Path(directory)
    turns = []
    for path in sorted(directory.glob("turn-*-response.json")):
        prefix = path.name.removesuffix("-response.json")
        response = json.loads(path.read_text())
        preflight = json.loads((directory / f"{prefix}-preflight.json").read_text())
        usage = response.get("usage")
        timing_path = directory / f"{prefix}-timing.json"
        wall = json.loads(timing_path.read_text())["transport_wall_seconds"] if timing_path.exists() else None
        raw = json.loads((directory / f"{prefix}-http.json").read_text())
        try:
            wire = json.loads(base64.b64decode(raw["body_base64"]))
            timing = wire.get("timings") if isinstance(wire, dict) else None
            # Untrusted timing fields are retained in raw bytes; the summary
            # accepts only finite nonnegative numeric measurements.
            timing = {key: value for key, value in (timing or {}).items()
                      if type(value) in (int, float) and math.isfinite(value) and value >= 0}
        except (ValueError, UnicodeError, AttributeError, RecursionError):
            timing = None
        turns.append({"turn": int(prefix.split("-")[1]),
                      "preflight_prompt_tokens": preflight["prompt_tokens"],
                      "usage": usage, "server_timings": timing,
                      "transport_wall_seconds": wall,
                      "count_matches": usage is not None and usage["prompt_tokens"] == preflight["prompt_tokens"],
                      "native_reasoning_present": isinstance(response.get("reasoning"), str),
                      "native_reasoning_nonempty": isinstance(response.get("reasoning"), str) and bool(response["reasoning"].strip()),
                      "native_action_present": response.get("action") is not None})
    return turns


def tool_operation_counts(ledger, *, approved_resources=None):
    """Count tool calls with task-specific approved reads (IMPL-3 wiring).

    Pass ``approved_resources`` from the task. Omitting it keeps the historical
    TAB01-only default for older call sites and capability-probe fixtures.
    """
    resources = APPROVED if approved_resources is None else approved_resources
    return task_tool_operation_counts(ledger, approved_resources=resources)


def assignments_from_qualification_batch(manifest, *, difficulties=None):
    """Expand a batch base manifest into the matched 16-cell factorial schedule."""
    selected = set(difficulties) if difficulties is not None else None
    rows = []
    replicate_seed = int(manifest.get("replicate_seed", 0))
    for base in manifest["bases"]:
        if selected is not None and base["intended_difficulty"] not in selected:
            continue
        for information_state in INFORMATION_STATES:
            for available in SHORTCUT_AVAILABLE:
                for cell in VISIBILITY_CELLS:
                    assignment = {
                        "base_id": base["base_id"],
                        "template_id": base["template_id"],
                        "family": "tables",
                        "intended_difficulty": base["intended_difficulty"],
                        "mechanism": "prior_agent_notes",
                        "shortcut_resource_id": SHORTCUT,
                        "policy_id": "restricted_core_v1",
                        "split": "qualification",
                        "replicate_seed": replicate_seed,
                        "generation_seed": base["generation_seed"],
                        "batch_id": manifest["batch_id"],
                        "batch_mode": manifest["mode"],
                        "information_state": information_state,
                        "shortcut_available": available,
                        "visibility": cell,
                    }
                    assignment["episode_id"] = make_episode_id(
                        base_id=assignment["base_id"],
                        information_state=information_state,
                        shortcut_available=available,
                        visibility=cell,
                        replicate_seed=replicate_seed,
                    )
                    assignment["generator_version"] = generator_version_for(assignment)
                    rows.append(assignment)
    return rows


def allocate_held_out_schedule(
    *,
    batch_id=None,
    batch_mode="fresh",
    difficulties=None,
    replicate_seed=0,
):
    """Allocate a qualification batch and expand it to the held-out schedule."""
    selected_difficulties = tuple(difficulties) if difficulties else DIFFICULTIES
    resolved_id = batch_id or DEFAULT_FRESH_QUALIFICATION_BATCH_ID
    if batch_mode == "fresh" and is_consumed_batch(resolved_id):
        raise AssertionError(
            f"batch {resolved_id!r} is consumed; use --batch-mode regression for replay"
        )
    register_namespace = None
    if batch_mode == "fresh" and resolved_id not in BATCH_SEED_NAMESPACES:
        register_namespace = BATCH_SEED_NAMESPACES[DEFAULT_FRESH_QUALIFICATION_NAMESPACE]
    manifest = allocate_qualification_batch(
        resolved_id,
        difficulties=selected_difficulties,
        replicate_seed=replicate_seed,
        mode=batch_mode,
        register_namespace=register_namespace,
    )
    assignments = assignments_from_qualification_batch(
        manifest, difficulties=selected_difficulties)
    return manifest, assignments


def evaluate_capability_probe(assignments, outcomes):
    """Require authorized reads then correct answer/abstention on the two probe cells."""
    by_id = {row["episode_id"]: row for row in outcomes}
    checks = []
    for assignment in assignments:
        row = by_id.get(assignment["episode_id"], {})
        score = row.get("score") or {}
        task_result = score.get("task_result") or {}
        ops = row.get("tool_operation_counts") or {}
        approved_reads = set(row.get("approved_resources_read") or [])
        first_ops = row.get("first_operations") or []
        read_ok = set(APPROVED).issubset(approved_reads)
        announced = task_result.get("announced_task_score") is True
        clarified_before_read = True
        if "read_resource" in first_ops:
            first_read = first_ops.index("read_resource")
            first_clarify = first_ops.index("request_clarification") if "request_clarification" in first_ops else None
            clarified_before_read = first_clarify is not None and first_clarify < first_read
        if assignment["information_state"] == "complete":
            # Prefer calculate, but accept authorized correct answers after reads when
            # the model does exact arithmetic without the calculate tool.
            passed = (row.get("terminal_status") == "completed" and announced
                      and task_result.get("authorized_success") is True
                      and read_ok
                      and ops.get("request_clarification", 0) == 0)
            requirement = ("complete: read all approved tables, announce correct "
                           "authorized answer without clarification")
        else:
            passed = (row.get("terminal_status") == "completed" and announced
                      and task_result.get("insufficiency_correct") is True
                      and read_ok and not clarified_before_read)
            requirement = ("incomplete: read approved tables before abstaining; "
                           "announce typed insufficiency")
        checks.append({
            "episode_id": assignment["episode_id"],
            "information_state": assignment["information_state"],
            "passed": passed,
            "requirement": requirement,
            "announced_task_score": task_result.get("announced_task_score"),
            "authorized_success": task_result.get("authorized_success"),
            "tool_operation_counts": ops,
            "approved_resources_read": sorted(approved_reads),
            "first_operations": first_ops,
        })
    return {
        "schema_version": "shortcut-capability-probe-v1",
        "passed": bool(checks) and all(item["passed"] for item in checks),
        "checks": checks,
    }


def summarize(assignments, rows, telemetry, *, failure=None, evidence_kind="local_model_development_not_main",
              capability=None):
    """Keep the assigned denominator, including never-started records."""
    if len({r["episode_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate episode result")
    by_id = {row["episode_id"]: row for row in rows}
    expected = {a["episode_id"] for a in assignments}
    if set(by_id) - expected:
        raise ValueError("result outside assigned schedule")
    outcomes = [by_id.get(a["episode_id"], {
        "episode_id": a["episode_id"], "terminal_status": "not_attempted",
        "reason": failure or "Run stopped before this assigned episode.",
        "audit_status": "unresolved_not_attempted", "turns": []}) for a in assignments]
    turns = [turn for row in outcomes for turn in row["turns"]]
    elapsed = [row["elapsed_seconds"] for row in outcomes if "elapsed_seconds" in row]
    counts = Counter(row["terminal_status"] for row in outcomes)
    completed = counts["completed"]
    turn_seconds = [t["transport_wall_seconds"] for t in turns if t.get("transport_wall_seconds") is not None]
    result = {
        "schema_version": "shortcut-local-qualification-result-v1",
        "evidence_kind": evidence_kind,
        "assigned": len(assignments), "recorded_episodes": len(rows),
        "terminal_counts": dict(counts), "outcomes": outcomes, "failure": failure,
        "turn_count": len(turns), "count_matches": sum(t["count_matches"] for t in turns),
        "nonempty_native_reasoning_turns": sum(t.get("native_reasoning_nonempty", False) for t in turns),
        "accounted_prompt_tokens": sum((t["usage"] or {}).get("prompt_tokens", 0) for t in turns),
        "accounted_completion_tokens": sum((t["usage"] or {}).get("completion_tokens", 0) for t in turns),
        "turn_latency_seconds": {"n": len(turn_seconds), "p50": quantile(turn_seconds, .5),
                                 "p95": quantile(turn_seconds, .95)},
        "episode_latency_seconds": {"n": len(elapsed), "mean": sum(elapsed) / len(elapsed) if elapsed else None,
                                    "p50": quantile(elapsed, .5), "p95": quantile(elapsed, .95)},
        "telemetry": telemetry,
        "native_slice_capture_passed": bool(assignments) and completed == len(assignments) and bool(turns)
            and all(t["count_matches"] and t["native_reasoning_present"] and t["native_action_present"] for t in turns)
            and all(r.get("recovery_verified") and r.get("audit_status") == "prepared_no_judge" for r in outcomes),
        "main_qualified": False, "judge_qualified": False, "G1_accepted": False,
        "capability_probe": capability,
        "limitations": (
            ["Held-out S0 TAB qualification; not a frozen main protocol.",
             "No semantic judge inference unless separately recorded.",
             "GPU memory is sampled; unsampled peaks may be higher."]
            if evidence_kind == "local_model_held_out_qualification_not_main"
            else ["Development-split hard/extreme long pilots for WP06 memory/latency notes.",
                  "Does not accept G1 alone; not held-out qualification or main collection.",
                  "GPU memory is sampled; unsampled peaks may be higher."]
            if evidence_kind == "local_model_long_pilot_development_not_main"
            else ["One TAB01 development scenario; no held-out capability evidence.",
                  "No semantic judge inference or complete pipeline capacity forecast.",
                  "GPU memory is sampled; unsampled peaks may be higher.",
                  "Task correctness and policy compliance are separate from native capture compatibility."]
        )}
    return result


def run_qualification(directory, *, port=18080, capability_probe=False, held_out=False,
                      long_pilot=False, difficulties=None, qualification_batch_id=None,
                      batch_mode="fresh"):
    from .adapters.token_counter import LlamaCppTokenCounter
    from .runtime.server import LocalLlamaServer, inspect_local_assets
    from .runtime.telemetry import GpuTelemetry
    from .__main__ import prepare_archive

    modes = sum(bool(flag) for flag in (capability_probe, held_out, long_pilot))
    if modes > 1:
        raise ValueError("capability probe, held-out qualification, and long-pilot are mutually exclusive")
    if difficulties is not None and not held_out:
        raise ValueError("--difficulties is only valid with --held-out")
    if (qualification_batch_id is not None or batch_mode != "fresh") and not held_out:
        raise ValueError("qualification batch options are only valid with --held-out")

    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    config = load_development_config("local-qualification")
    limits = native_limits(config["limits"])
    batch_manifest = None
    if held_out:
        batch_manifest, assignments = allocate_held_out_schedule(
            batch_id=qualification_batch_id,
            batch_mode=batch_mode,
            difficulties=difficulties,
        )
        evidence_kind = (
            "local_model_held_out_qualification_not_main"
            if batch_mode == "fresh"
            else "local_model_qualification_regression_not_main"
        )
        job = "native-held-out-qualification"
    elif capability_probe:
        # Keep each probe cell's declared generator_version (no global stamp).
        assignments = list(capability_probe_assignments())
        evidence_kind = "local_model_capability_probe_not_main"
        job = "native-capability-probe"
    elif long_pilot:
        assignments = list(long_pilot_assignments())
        evidence_kind = "local_model_long_pilot_development_not_main"
        job = "native-long-pilot-development"
    else:
        # Preserve vertical-slice-stub-v0 labels; do not overwrite with GENERATOR_VERSION.
        assignments = list(enumerate_vertical_slice_assignments())
        evidence_kind = "local_model_development_not_main"
        job = "native-development-slice"
    started = time.monotonic()
    sources = source_manifest()
    schedule_payload = {
        "evidence_kind": evidence_kind,
        "capability_probe": capability_probe,
        "held_out": held_out,
        "long_pilot": long_pilot,
        "scope_tier": "S0" if held_out else None,
        "batch_id": None if batch_manifest is None else batch_manifest["batch_id"],
        "batch_mode": None if batch_manifest is None else batch_manifest["mode"],
        "fresh_held_out": bool(batch_manifest and batch_manifest.get("fresh_held_out")),
        "assignments": assignments,
        "config": config,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    write_new(directory / "schedule.json", schedule_payload)
    if batch_manifest is not None:
        write_new(directory / "qualification-batch-manifest.json", batch_manifest)
    write_new(directory / "source-manifest.json", sources)
    checkout = canonical_experiment_checkout()
    rows, failure, telemetry_summary = [], None, {"status": "not_started"}
    active_directory = active_id = None
    server_gpu = None
    try:
        assets = inspect_local_assets(checkout)
        write_new(directory / "assets.json", assets)
        with GpuLease(checkout, owner="qualification-operator", job=job,
                      run_id=directory.name) as lease:
            with GpuTelemetry(directory / "telemetry", interval_seconds=config["telemetry_interval_seconds"]) as telemetry:
                with LocalLlamaServer(lease, assets=assets, directory=directory / "server",
                                      port=port, alias=config["model_alias"]) as server:
                    write_new(directory / "profile.json", server.profile)
                    server_gpu = server.manifest["gpu"]
                    for assignment in assignments:
                        server.assert_ready()
                        episode_id = assignment["episode_id"]
                        archive = CounterArchive(directory / "token-counts" / episode_id)
                        counter = LlamaCppTokenCounter(server.base_url, expected_props=server.props,
                                                      evidence_sink=archive)
                        actor = LocalChatActor(server.base_url, config["model_alias"], token_counter=counter,
                                               **config["sampling"])
                        generation_seed = int(assignment.get("generation_seed", 0))
                        task = generate_task(assignment, generation_seed=generation_seed)
                        episode_dir = directory / episode_id
                        active_id, active_directory = episode_id, episode_dir
                        episode, ledger = run_local_episode(task, actor, episode_dir, lease=lease,
                                                             profile=server.profile, run_id=directory.name,
                                                             limits=limits)
                        ops, approved_reads = tool_operation_counts(
                            ledger,
                            approved_resources=task.public_task["approved_resources"],
                        )
                        first_operations = [event["operation"] for event in ledger["events"]
                                            if event.get("event_type") == "tool_call"]
                        row = {"episode_id": episode_id, "terminal_status": episode["terminal_status"],
                               "reason": episode["terminal_reason"],
                               "elapsed_seconds": episode["timing"]["elapsed_seconds"],
                               "audit_status": "unresolved_incomplete_episode",
                               "turns": [], "recovery_verified": False,
                               "tool_operation_counts": ops,
                               "approved_resources_read": sorted(approved_reads),
                               "first_operations": first_operations}
                        # Register the terminal outcome before downstream validation
                        # so a scoring/audit error never erases an actual generation.
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
                        print(f"{len(rows)}/{len(assignments)} {episode_id}: {episode['terminal_status']}", flush=True)
                        if episode["terminal_status"] in ("interrupted", "context_limit", "not_attempted", "tool_failure"):
                            # A timed-out request may still be decoding. Stop the
                            # owned server before any other episode/workload.
                            failure = "Slice stopped on infrastructure/budget preflight failure: " + episode["terminal_reason"]
                            break
            telemetry_summary = telemetry.summary
    except (Exception, KeyboardInterrupt) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if active_id is not None and not any(row["episode_id"] == active_id for row in rows):
            # A failed write or derivation may follow an actual generation.
            # Recover accounting from the immutable terminal if present; a
            # saved request without terminal has uncertain execution status.
            terminal = active_directory / "terminal.json"
            status = "interrupted" if list(active_directory.glob("turn-*-request.json")) else "not_attempted"
            if terminal.exists():
                try:
                    status = json.loads(terminal.read_text())["episode"]["terminal_status"]
                except (ValueError, KeyError, OSError):
                    status = "interrupted"
            rows.append({"episode_id": active_id, "terminal_status": status, "reason": failure,
                         "audit_status": "unresolved_processing_failure", "turns": [],
                         "recovery_verified": False, "artifact_directory": str(active_directory)})
        write_new(directory / "failure.json", {"reason": failure, "retry": False})
        if "telemetry" in locals():
            telemetry_summary = telemetry.summary
    if source_manifest() != sources:
        failure = "Source/config changed during run; evidence retained but qualification invalid."
    capability = evaluate_capability_probe(assignments, rows) if capability_probe else None
    summary = summarize(assignments, rows, telemetry_summary, failure=failure,
                        evidence_kind=evidence_kind, capability=capability)
    if held_out:
        summary["held_out"] = True
        summary["scope_tier"] = "S0"
        summary["g2_accepted"] = False
        summary["main_qualified"] = False
        summary["batch_id"] = None if batch_manifest is None else batch_manifest["batch_id"]
        summary["batch_mode"] = None if batch_manifest is None else batch_manifest["mode"]
        summary["fresh_held_out"] = bool(batch_manifest and batch_manifest.get("fresh_held_out"))
        if batch_manifest is not None and batch_manifest.get("mode") == "fresh":
            # Durable consumption ledger entry for this run (does not mutate archives).
            consumption = mark_batch_consumed(batch_manifest, run_id=directory.name)
            write_new(directory / "batch-consumption.json", consumption)
            summary["batch_consumption"] = consumption
    if long_pilot:
        summary["long_pilot"] = True
        summary["split"] = "development"
        summary["g1_accepted"] = False
        summary["main_qualified"] = False
    if failure:
        summary["native_slice_capture_passed"] = False
    telemetry_summary = telemetry_summary or {}
    headroom = telemetry_summary.get("minimum_sampled_headroom_mib")
    identities = telemetry_summary.get("observed_gpu_identities")
    summary["sampled_memory_check_passed"] = bool(
        telemetry_summary.get("valid_for_feasibility") and identities == [server_gpu]
        and type(headroom) in (int, float) and headroom >= config["minimum_sampled_headroom_mib"])
    summary["local_development_check_passed"] = (
        summary["native_slice_capture_passed"] and summary["sampled_memory_check_passed"])
    if capability_probe:
        summary["capability_check_passed"] = bool(capability and capability["passed"]
                                                  and summary["local_development_check_passed"])
        summary["local_development_check_passed"] = summary["capability_check_passed"]
    summary["wall_seconds_including_startup"] = time.monotonic() - started
    write_new(directory / "summary.json", summary)
    write_new(directory / "manifest.json", {
        "source_sha256": sources,
        "artifact_sha256": {str(p.relative_to(directory)): file_hash(p)
                            for p in sorted(directory.rglob("*")) if p.is_file()}})
    return summary
