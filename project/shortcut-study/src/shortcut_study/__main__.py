"""Development tools, including an owned local GPU qualification run."""

import argparse
import hashlib
import json
from pathlib import Path

from .adapters.mock import MockActor
from .runner import recover_mock_episode, run_mock_episode, write_new
from .scoring import score_episode
from .tasks.tables import GENERATOR_VERSION, generate_task
from .vertical_slice import enumerate_vertical_slice_assignments


def prepare_archive(episode_directory, output_directory):
    """Prepare local judge input from verified saved evidence; never call a judge."""
    from .audit import judge_messages, prepare_audit

    episode_directory, output_directory = Path(episode_directory), Path(output_directory)
    terminal_path = episode_directory / "terminal.json"
    inputs_path = episode_directory / "inputs.json"
    terminal = json.loads(terminal_path.read_text())
    inputs = json.loads(inputs_path.read_text())
    episode, ledger = terminal["episode"], terminal["ledger"]
    input_paths = [terminal_path, inputs_path]
    if episode["actor_id"]["runtime"] == "deterministic-mock":
        capabilities = inputs["prompt"]["tools"]
    else:
        request_path = episode_directory / "turn-0001-request.json"
        capabilities = json.loads(request_path.read_text())["tools"]
        input_paths.append(request_path)
    results = {}
    for event in ledger["events"]:
        if event["response_sha256"] is not None:
            path = episode_directory / f"turn-{event['turn_id']:04d}-result.json"
            results[event["event_id"]] = json.loads(path.read_text())
            input_paths.append(path)
    prepared = prepare_audit(episode, ledger, public_task=inputs["prompt"]["task"],
                             capabilities=capabilities, tool_results=results)
    messages = judge_messages(prepared)
    output_directory.mkdir(parents=True, exist_ok=False)
    write_new(output_directory / "prepared.json", prepared)
    write_new(output_directory / "messages.json", messages)
    write_new(output_directory / "manifest.json", {
        "status": "prepared_only_no_judge_inference", "episode_id": episode["episode_id"],
        "input_sha256": {str(p.relative_to(episode_directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(set(input_paths))},
        "output_sha256": {name: hashlib.sha256((output_directory / name).read_bytes()).hexdigest()
                          for name in ("prepared.json", "messages.json")}})
    return prepared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    mock = commands.add_parser("mock-slice", help="Run 16 scripted CPU episodes, never model inference")
    mock.add_argument("--out", type=Path, required=True)
    mock.add_argument("--strategy", choices=("legitimate", "shortcut"), default="legitimate")
    recover = commands.add_parser("recover-mock-episode", help="Seal an interrupted mock episode without replay")
    recover.add_argument("directory", type=Path)
    audit = commands.add_parser("prepare-audit", help="Prepare verified local judge input without inference")
    audit.add_argument("--episode", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    qualify = commands.add_parser("qualify-local", help="Qualify the retained local runtime on 16 development assignments")
    qualify.add_argument("--out", type=Path, required=True)
    qualify.add_argument("--port", type=int, default=18080)
    qualify.add_argument("--capability-probe", action="store_true",
                         help="Run the smallest existing-slice GPU probe (complete+incomplete V00, shortcut absent)")
    args = parser.parse_args()
    if args.command == "qualify-local":
        from .qualification import run_qualification
        summary = run_qualification(args.out, port=args.port, capability_probe=args.capability_probe)
        capability = summary.get("capability_probe")
        capability_note = ""
        if capability is not None:
            capability_note = f"; capability probe passed: {capability['passed']}"
        print(f"Local development: {summary['terminal_counts']}; native capture passed: "
              f"{summary['native_slice_capture_passed']}{capability_note}; output: {args.out}")
        if not summary["local_development_check_passed"]:
            raise SystemExit(1)
        return
    if args.command == "recover-mock-episode":
        episode, _ = recover_mock_episode(args.directory)
        print(f"{episode['episode_id']}: {episode['terminal_status']}; no operations replayed")
        return
    if args.command == "prepare-audit":
        prepared = prepare_archive(args.episode, args.out)
        print(f"Prepared audit for {prepared['episode_id']}; no judge inference; output: {args.out}")
        return
    args.out.mkdir(parents=True, exist_ok=False)
    assignments = [{**row, "generator_version": GENERATOR_VERSION}
                   for row in enumerate_vertical_slice_assignments()]
    write_new(args.out / "schedule.json", {"evidence_kind": "scripted_mock_not_model_observation", "assignments": assignments})
    rows = []
    for assignment in assignments:
        task = generate_task(assignment)
        episode, ledger = run_mock_episode(task, MockActor(args.strategy), args.out / assignment["episode_id"], run_id=args.out.name)
        row = score_episode(task, episode, ledger)
        write_new(args.out / assignment["episode_id"] / "scored.json", row)
        rows.append(row)
    summary = {"evidence_kind": "scripted_mock_not_model_observation", "strategy": args.strategy,
               "assigned": len(assignments), "terminal": len(rows),
               "completed": sum(r["integrity"]["record_complete"] for r in rows),
               "acquired": sum(r["acquisition"]["successful"] is True for r in rows),
               "announced_success": sum(r["task_result"]["announced_task_score"] is True for r in rows)}
    write_new(args.out / "summary.json", summary)
    source_root = Path(__file__).resolve().parents[2]
    source_files = sorted(path for area in ("src", "schemas", "configs/development")
                          for path in (source_root / area).rglob("*")
                          if path.is_file() and path.suffix in (".py", ".json"))
    write_new(args.out / "manifest.json", {
        "evidence_kind": "scripted_mock_not_model_observation",
        "source_sha256": {str(p.relative_to(source_root)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in source_files},
        "artifact_sha256": {str(p.relative_to(args.out)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(args.out.rglob("*")) if p.is_file()},
    })
    print(f"Scripted mock only: {summary['completed']}/{len(assignments)} completed; output: {args.out}")


if __name__ == "__main__":
    main()
