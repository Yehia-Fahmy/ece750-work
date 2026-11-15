"""Entry points intentionally limited to CPU development fixtures."""

import argparse
import hashlib
from pathlib import Path

from .adapters.mock import MockActor
from .runner import recover_mock_episode, run_mock_episode, write_new
from .scoring import score_episode
from .tasks.tables import GENERATOR_VERSION, generate_task
from .vertical_slice import enumerate_vertical_slice_assignments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    mock = commands.add_parser("mock-slice", help="Run 16 scripted CPU episodes, never model inference")
    mock.add_argument("--out", type=Path, required=True)
    mock.add_argument("--strategy", choices=("legitimate", "shortcut"), default="legitimate")
    recover = commands.add_parser("recover-mock-episode", help="Seal an interrupted mock episode without replay")
    recover.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "recover-mock-episode":
        episode, _ = recover_mock_episode(args.directory)
        print(f"{episode['episode_id']}: {episode['terminal_status']}; no operations replayed")
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
