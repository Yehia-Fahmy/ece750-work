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
from .tasks.tables import GENERATOR_VERSION, generate_task
from .vertical_slice import enumerate_vertical_slice_assignments


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


def summarize(assignments, rows, telemetry, *, failure=None):
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
        "evidence_kind": "local_model_development_not_main",
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
        "limitations": ["One TAB01 development scenario; no held-out capability evidence.",
                        "No semantic judge inference or complete pipeline capacity forecast.",
                        "GPU memory is sampled; unsampled peaks may be higher.",
                        "Task correctness and policy compliance are separate from native capture compatibility."]}
    return result


def run_qualification(directory, *, port=18080):
    from .adapters.token_counter import LlamaCppTokenCounter
    from .runtime.server import LocalLlamaServer, inspect_local_assets
    from .runtime.telemetry import GpuTelemetry
    from .__main__ import prepare_archive

    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    config = load_development_config("local-qualification")
    limits = native_limits(config["limits"])
    assignments = [{**row, "generator_version": GENERATOR_VERSION}
                   for row in enumerate_vertical_slice_assignments()]
    started = time.monotonic()
    sources = source_manifest()
    write_new(directory / "schedule.json", {"evidence_kind": "local_model_development_not_main",
                                           "assignments": assignments, "config": config,
                                           "created_at": datetime.now(timezone.utc).isoformat()})
    write_new(directory / "source-manifest.json", sources)
    checkout = canonical_experiment_checkout()
    rows, failure, telemetry_summary = [], None, {"status": "not_started"}
    active_directory = active_id = None
    server_gpu = None
    try:
        assets = inspect_local_assets(checkout)
        write_new(directory / "assets.json", assets)
        with GpuLease(checkout, owner="qualification-operator", job="native-development-slice",
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
                        task = generate_task(assignment)
                        episode_dir = directory / episode_id
                        active_id, active_directory = episode_id, episode_dir
                        episode, ledger = run_local_episode(task, actor, episode_dir, lease=lease,
                                                             profile=server.profile, run_id=directory.name,
                                                             limits=limits)
                        row = {"episode_id": episode_id, "terminal_status": episode["terminal_status"],
                               "reason": episode["terminal_reason"],
                               "elapsed_seconds": episode["timing"]["elapsed_seconds"],
                               "audit_status": "unresolved_incomplete_episode",
                               "turns": [], "recovery_verified": False}
                        # Register the terminal outcome before downstream validation
                        # so a scoring/audit error never erases an actual generation.
                        rows.append(row)
                        row["turns"] = episode_metrics(episode_dir)
                        score = score_episode(task, episode, ledger)
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
    summary = summarize(assignments, rows, telemetry_summary, failure=failure)
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
    summary["wall_seconds_including_startup"] = time.monotonic() - started
    write_new(directory / "summary.json", summary)
    write_new(directory / "manifest.json", {
        "source_sha256": sources,
        "artifact_sha256": {str(p.relative_to(directory)): file_hash(p)
                            for p in sorted(directory.rglob("*")) if p.is_file()}})
    return summary
