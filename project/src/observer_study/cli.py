"""Command-line entry points for preparing and running the local smoke test."""

import argparse
import json
from pathlib import Path

from .data import download_tasks, prepare_items
from .io import RequestError, read_json, write_json
from .runner import run
from .summary import export_review, summarize


ROOT = Path(__file__).resolve().parents[2]


def load_config(path):
    """Check protocol settings before sampling or inference."""
    config = read_json(path)
    generation = config["generation"]
    if generation.get("chat_template_kwargs", {}).get("enable_thinking") is not True:
        raise ValueError("The study requires native thinking")
    if generation.get("stream") is not False:
        raise ValueError("The capture client requires non-streaming responses")
    if generation.get("reasoning_format") != "deepseek":
        raise ValueError("The capture client expects the deepseek reasoning format")
    if generation.get("max_tokens", 0) <= 0 or generation["max_tokens"] >= config["context_tokens"]:
        raise ValueError("Output allowance must be positive and smaller than the context")
    if "stop" in generation or "response_format" in generation:
        raise ValueError("Do not stop/constrain the reasoning stream")
    if type(config["seed"]) is not int or type(config["technical_retries"]) is not int or config["technical_retries"] < 0:
        raise ValueError("Seed and technical retry limit must be integers")
    if not config["tasks"] or len(config["tasks"]) != len(set(config["tasks"])):
        raise ValueError("Task names must be nonempty and unique")
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare", help="Validate pinned data and reserve disjoint items")
    prepare.add_argument("--config", type=Path, default=ROOT / "configs/smoke.json")
    prepare.add_argument("--data-dir", type=Path, default=ROOT / "data/bbh")
    prepare.add_argument("--out", type=Path, default=ROOT / "data/items.json")
    prepare.add_argument("--download", action="store_true", help="Download missing pinned official task files")
    execute = subparsers.add_parser("run", help="Prepare requests or execute local inference")
    execute.add_argument("--config", type=Path, default=ROOT / "configs/smoke.json")
    execute.add_argument("--items", type=Path, default=ROOT / "data/items.json")
    execute.add_argument("--split", choices=("smoke", "pilot", "pilot_development", "pilot_validation", "main"), default="smoke")
    execute.add_argument("--out", type=Path, required=True)
    execute.add_argument("--server", default="http://127.0.0.1:8080")
    execute.add_argument("--model-file", type=Path, default=ROOT / "models/Qwen3-4B-Q4_K_M.gguf")
    execute.add_argument("--dry-run", action="store_true")
    execute.add_argument("--resume", action="store_true")
    summary = subparsers.add_parser("summarize", help="Report capture/scoring and unknown-outcome bounds")
    summary.add_argument("run", type=Path)
    summary.add_argument("--out", type=Path)
    review = subparsers.add_parser("export-review", help="Create a blank human acknowledgment review sheet")
    review.add_argument("run", type=Path)
    review.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            config = load_config(args.config)
            if args.download:
                download_tasks(config, args.data_dir)
            prepared = prepare_items(config, args.data_dir)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            if args.out.exists() and read_json(args.out) != prepared:
                raise ValueError("Existing item manifest differs; choose a new output path")
            write_json(args.out, prepared)
            print(f"Prepared {len(prepared['items'])} disjoint items: {args.out}")
            print(json.dumps(prepared["eligibility"], indent=2))
        elif args.command == "run":
            run(load_config(args.config), read_json(args.items), args.split, args.out,
                args.server, args.model_file, args.dry_run, args.resume)
        elif args.command == "summarize":
            result = summarize(args.run)
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                write_json(args.out, result)
            print(json.dumps(result["overall"], indent=2))
        else:
            count = export_review(args.run, args.out)
            print(f"Exported {count} traces: {args.out}")
    except (ValueError, KeyError, OSError, RequestError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
