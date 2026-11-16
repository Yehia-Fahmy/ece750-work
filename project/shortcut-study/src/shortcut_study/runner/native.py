"""Local development loop; real inference requires an owned GPU lease.

CPU tests supply a synthetic transport and GPU probe. They do not qualify a
model, server, chat template, or prompt-token counter for experimental use.
"""

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

from ..adapters.local import ADAPTER_VERSION, HISTORY_POLICY, HTTPResponse, LocalChatActor, NativeAdapterError
from ..config import load_development_config
from ..environment import ToolEnvironment
from ..hashing import sha256_json
from ..runtime import GpuLease, assert_supported_gpu, resolve_canonical_checkout
from ..schemas import validate
from ..tasks.tables import resolve_clarification_fields
from . import (append_event, finish, initial_record, prompt_for, publish_packets,
               read_event_journal, restore_saved_channels, write_new)


def source_fingerprint():
    root = Path(__file__).resolve().parents[1]
    return sha256_json({str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(root.rglob("*.py"))})


def canonical_experiment_checkout():
    return resolve_canonical_checkout(Path(__file__).resolve().parents[5])


def actor_settings(actor):
    return {"adapter_version": ADAPTER_VERSION, "history_policy": HISTORY_POLICY,
            "model": actor.model, "base_url": actor.base_url,
            "temperature": actor.temperature, "top_p": actor.top_p,
            "max_request_bytes": actor.max_request_bytes,
            "max_response_bytes": actor.max_response_bytes}


def native_limits(limits):
    limits = deepcopy(limits) if limits is not None else {
        **load_development_config("budgets")["development"], "technical_transport_retries": 0}
    for key in ("max_model_turns", "max_tool_actions", "max_wall_time_seconds",
                "max_cumulative_generated_tokens", "max_per_turn_output_tokens", "max_context_tokens"):
        if type(limits.get(key)) is not int or limits[key] < 1:
            raise ValueError(f"invalid {key}")
    if limits.get("technical_transport_retries") != 0:
        raise ValueError("native development currently requires zero transport retries")
    return limits


def identity(actor, profile):
    required = {"checkpoint_revision", "checkpoint_sha256", "quantization", "runtime_revision", "template_sha256"}
    if set(profile) != required or any(not isinstance(v, str) or not v for v in profile.values()):
        raise ValueError("explicit checkpoint/runtime/template profile required")
    for key in ("checkpoint_sha256", "template_sha256"):
        if len(profile[key]) != 64 or any(c not in "0123456789abcdef" for c in profile[key]):
            raise ValueError(f"invalid {key}")
    return {"alias": actor.model, "checkpoint_revision": profile["checkpoint_revision"],
            "quantization": profile["quantization"], "runtime": profile["runtime_revision"],
            "template_hash": profile["template_sha256"], "settings_hash": sha256_json(actor_settings(actor))}


def save_http(directory, turn, response):
    write_new(directory / f"turn-{turn:04d}-http.json", {
        "status": response.status, "body_base64": base64.b64encode(response.body).decode("ascii")})


def normalize_response(actor, response, cap):
    try:
        return actor.parse_response(response, max_output_tokens=cap), None
    except NativeAdapterError as exc:
        return {"reasoning": exc.reasoning, "action": None, "usage": exc.usage,
                "parse_error": {"terminal_status": exc.terminal_status, "reason": exc.reason}}, exc


def restore_native_archive(directory, actor, episode):
    """Bind derived captures to saved native bytes, including interrupted turns."""
    for path in sorted(directory.glob("turn-*-http.json")):
        turn = int(path.name.split("-")[1])
        saved = json.loads(path.read_text())
        cap = json.loads((directory / f"turn-{turn:04d}-preflight.json").read_text())["output_cap"]
        parsed, _ = normalize_response(actor, HTTPResponse(saved["status"], base64.b64decode(saved["body_base64"], validate=True)), cap)
        derived = directory / f"turn-{turn:04d}-response.json"
        if derived.exists():
            if json.loads(derived.read_text()) != parsed:
                raise ValueError("native parsed response differs from archived HTTP bytes")
        else:
            write_new(derived, parsed)
    for path in directory.glob("turn-*-response.json"):
        if not path.with_name(path.name.replace("-response.json", "-http.json")).exists():
            raise ValueError("native parsed response has no archived HTTP body")
    request = directory / "turn-0001-request.json"
    if request.exists():
        payload = json.loads(request.read_text())
        episode["references"]["prompts_hash"] = sha256_json(payload)
        episode["references"]["tool_schema_hash"] = sha256_json(payload["tools"])
    events = read_event_journal(directory)
    restore_saved_channels(directory, episode, events)
    return events


def run_local_episode(task, actor, directory, *, lease, profile, run_id="local-development", limits=None):
    """Execute one development episode, without retries or history clipping.

    The operator must qualify the pinned server/profile and exact token counter
    before using this for model measurements. There is intentionally no main-run
    CLI. Merely supplying a profile is provenance, not runtime qualification.
    """
    if not isinstance(actor, LocalChatActor) or task.assignment["split"] != "development":
        raise ValueError("only local development actors/assignments are supported")
    if not isinstance(lease, GpuLease):
        raise ValueError("an OS-held canonical GPU lease is required")
    if lease.canonical_checkout != canonical_experiment_checkout():
        raise ValueError("GPU lease must belong to this repository's canonical checkout")
    lease.assert_held()
    gpu = assert_supported_gpu()
    limits = native_limits(limits)
    actor_id = identity(actor, profile)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    episode = initial_record(task, run_id, "native", limits)
    episode.update(actor_id=actor_id, terminal_reason="Assigned local development episode; no generation attempted.")
    validate("episode", episode)
    write_new(directory / "assignment.json", episode)
    write_new(directory / "inputs.json", {
        "prompt": prompt_for(task), "resources": task.resources, "hidden_truth": task.hidden_truth,
        "profile": profile, "actor_settings": actor_settings(actor), "gpu": gpu,
        "source_fingerprint": source_fingerprint(), "limits": limits,
        "qualification_status": "unqualified_development", "history_policy": HISTORY_POLICY})
    environment = ToolEnvironment(
        task.resources, lambda event: append_event(directory / "events.jsonl", event),
        approved=tuple(task.public_task["approved_resources"]),
        shortcut=task.assignment["shortcut_resource_id"],
        clarification_fields=resolve_clarification_fields(task.public_task, task.assignment))
    history = []
    used_tokens = actions = 0
    generation_started = False
    start = time.monotonic()
    status, reason = "budget_limit", "Maximum model turns reached."
    try:
        for turn in range(1, limits["max_model_turns"] + 1):
            remaining_seconds = limits["max_wall_time_seconds"] - (time.monotonic() - start)
            if actions >= limits["max_tool_actions"] or remaining_seconds <= 0:
                status, reason = "budget_limit", "Action or wall-time budget reached."
                break
            remaining_tokens = limits["max_cumulative_generated_tokens"] - used_tokens
            if remaining_tokens <= 0:
                status, reason = "budget_limit", "Cumulative generated-token budget reached."
                break
            cap = min(limits["max_per_turn_output_tokens"], remaining_tokens)
            payload = actor.build_request(prompt_for(task), history, max_output_tokens=cap,
                                          seed=task.assignment["replicate_seed"])
            remaining_seconds = limits["max_wall_time_seconds"] - (time.monotonic() - start)
            if remaining_seconds <= 0:
                status, reason = "budget_limit", "Wall-time budget reached before prompt counting."
                break
            count = actor.count_prompt_tokens(payload, timeout_seconds=remaining_seconds)
            if type(count) is not int or count < 0:
                raise NativeAdapterError("context_limit", "Invalid exact prompt-token count.")
            if count + cap > limits["max_context_tokens"]:
                status, reason = "context_limit", "Full prompt plus reserved output exceeds context; no clipping."
                break
            write_new(directory / f"turn-{turn:04d}-request.json", payload)
            write_new(directory / f"turn-{turn:04d}-preflight.json", {
                "prompt_tokens": count, "output_cap": cap, "cumulative_generated_before": used_tokens})
            if turn == 1:
                episode["references"]["prompts_hash"] = sha256_json(payload)
                episode["references"]["tool_schema_hash"] = sha256_json(payload["tools"])
            lease.assert_held()
            lease.heartbeat()
            remaining_seconds = limits["max_wall_time_seconds"] - (time.monotonic() - start)
            if remaining_seconds <= 0:
                status, reason = "budget_limit", "Wall-time budget reached before transport."
                break
            try:
                generation_started = True
                transport_started = time.monotonic()
                response = actor.send(payload, timeout_seconds=remaining_seconds)
                save_http(directory, turn, response)
            except NativeAdapterError as exc:
                if exc.response is not None:
                    save_http(directory, turn, exc.response)
                write_new(directory / f"turn-{turn:04d}-transport-error.json", {
                    "terminal_status": exc.terminal_status, "reason": exc.reason})
                raise
            finally:
                write_new(directory / f"turn-{turn:04d}-timing.json", {
                    "transport_wall_seconds": time.monotonic() - transport_started})
            parsed, error = normalize_response(actor, response, cap)
            write_new(directory / f"turn-{turn:04d}-response.json", parsed)
            restore_saved_channels(directory, episode, read_event_journal(directory))
            write_new(directory / f"turn-{turn:04d}-capture.json", episode)
            usage = parsed.get("usage")
            if usage is not None:
                used_tokens += usage["completion_tokens"]
            if error is not None:
                raise error
            if usage["prompt_tokens"] != count:
                status, reason = "context_limit", "Server usage differs from exact preflight count; no action executed."
                break
            if used_tokens > limits["max_cumulative_generated_tokens"]:
                status, reason = "budget_limit", "Server output exceeded cumulative token budget."
                break
            if time.monotonic() - start >= limits["max_wall_time_seconds"]:
                status, reason = "budget_limit", "Response exceeded episode wall-time budget."
                break
            call_id = parsed["assistant_message"]["tool_calls"][0]["id"]
            if any(previous["tool_calls"][0]["id"] == call_id for previous in history[::2]):
                status, reason = "model_format_failure", "Reused native tool-call ID; no action executed."
                break
            action = parsed["action"]
            result = environment.dispatch(action["operation"], action["arguments"], turn)
            actions += 1
            write_new(directory / f"turn-{turn:04d}-result.json", result)
            if result["status"] == "malformed":
                status, reason = "model_format_failure", "Invalid tool arguments; no regeneration."
                break
            if environment.submission is not None:
                status, reason = "completed", "Local development submission accepted."
                break
            history = actor.extend_history(history, parsed, result)
    except NativeAdapterError as exc:
        status, reason = exc.terminal_status, exc.reason
    except (KeyboardInterrupt, InterruptedError):
        status, reason = "interrupted", "Local operation interrupted; no retry or replay."
    except Exception as exc:
        if isinstance(exc, OSError):
            raise  # storage errors leave durable artifacts for explicit recovery
        status, reason = "tool_failure", f"Local runtime failure: {type(exc).__name__}"
    if not generation_started:
        status, reason = "not_attempted", f"No generation started: {status}: {reason}"
    episode.update(terminal_status=status, terminal_reason=reason,
                   timing={"elapsed_seconds": time.monotonic() - start,
                           "accounted_completion_tokens": used_tokens})
    events = restore_native_archive(directory, actor, episode)
    return finish(directory, episode, events)


def recover_local_episode(directory, actor):
    """Re-extract already saved HTTP bodies; never call transport or execute tools."""
    directory = Path(directory)
    inputs = json.loads((directory / "inputs.json").read_text())
    if inputs["actor_settings"] != actor_settings(actor) or inputs["source_fingerprint"] != source_fingerprint():
        raise ValueError("native recovery implementation/settings mismatch")
    terminal = directory / "terminal.json"
    if terminal.exists():
        saved = json.loads(terminal.read_text())
        validate("episode", saved["episode"])
        validate("events", saved["ledger"])
        if saved["ledger"]["integrity_sha256"] != sha256_json(saved["ledger"]["events"]):
            raise ValueError("terminal event integrity mismatch")
        reconstructed = deepcopy(saved["episode"])
        events = restore_native_archive(directory, actor, reconstructed)
        if reconstructed != saved["episode"] or events != saved["ledger"]["events"]:
            raise ValueError("terminal record differs from native archive")
        publish_packets(directory, saved["episode"], saved["ledger"])
        return saved["episode"], saved["ledger"]
    episode = json.loads((directory / "assignment.json").read_text())
    request = directory / "turn-0001-request.json"
    events = restore_native_archive(directory, actor, episode)
    episode.update(terminal_status="interrupted" if request.exists() else "not_attempted",
                   terminal_reason="Recovered native archive without transport or action replay.")
    return finish(directory, episode, events)
