"""Pinned BIG-Bench Hard downloads and disjoint, seeded item manifests."""

import hashlib
import random
import re
from pathlib import Path
import urllib.request

from .io import digest, file_digest, read_json, write_json


def seeded_rng(seed, namespace):
    """Keep random choices stable when unrelated tasks or arms are added."""
    return random.Random(int(digest([seed, namespace])[:16], 16))


def download_tasks(config, directory):
    """Cache official task files and their source revision and checksums."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    revision = config["dataset_revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Dataset revision must be a full commit hash")
    manifest_path = directory / "source.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {"revision": revision, "files": {}}
    if manifest["revision"] != revision:
        raise ValueError("Cached dataset revision differs; choose a fresh data directory")
    for task in config["tasks"]:
        if not re.fullmatch(r"[a-z0-9_]+", task):
            raise ValueError(f"Invalid task name: {task}")
        path = directory / f"{task}.json"
        if path.exists():
            expected = manifest["files"].get(task, {}).get("sha256")
            if expected is None or file_digest(path) != expected:
                raise ValueError(f"Unverified or modified cached data: {path}")
            continue
        url = f"https://raw.githubusercontent.com/suzgunmirac/BIG-Bench-Hard/{revision}/bbh/{task}.json"
        with urllib.request.urlopen(url, timeout=60) as response:
            raw = response.read()
        # Validate JSON and options before trusting a downloaded artifact.
        import json
        task_items(task, json.loads(raw))
        temporary = path.with_suffix(".json.tmp")
        temporary.write_bytes(raw)
        temporary.replace(path)
        manifest["files"][task] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest()}
        write_json(manifest_path, manifest)
    return manifest


def task_items(task, data):
    """Validate multiple-choice items and keep source indexes as stable IDs."""
    items = []
    seen = set()
    for index, example in enumerate(data["examples"]):
        question = example["input"]
        options = re.findall(r"^\(([A-Z])\)\s+", question, flags=re.MULTILINE)
        target = re.fullmatch(r"\(([A-Z])\)", example["target"].strip())
        if len(options) < 2 or len(set(options)) != len(options) or target is None or target[1] not in options:
            raise ValueError(f"Unsupported answer format: {task}:{index}")
        question_hash = digest(question)
        if question_hash in seen:
            continue
        seen.add(question_hash)
        items.append({"item_id": f"{task}:{index:04d}", "task": task, "source_index": index,
                      "question": question, "question_sha256": question_hash,
                      "options": options, "target": target[1]})
    return items


def prepare_items(config, directory):
    """Reserve smoke, pilot-development, pilot-validation, and main samples."""
    directory = Path(directory)
    source = read_json(directory / "source.json")
    if source["revision"] != config["dataset_revision"]:
        raise ValueError("Dataset revision differs from configuration")
    counts = config["split_counts_per_task"]
    if set(counts) != {"smoke", "pilot_development", "pilot_validation", "main"}:
        raise ValueError("Expected four named, disjoint data splits")
    if any(type(count) is not int or count < 1 for count in counts.values()):
        raise ValueError("Split counts must be positive integers")
    selected, audit = [], {}
    for task in config["tasks"]:
        path = directory / f"{task}.json"
        if file_digest(path) != source["files"][task]["sha256"]:
            raise ValueError(f"Dataset checksum mismatch: {task}")
        raw = read_json(path)
        eligible = task_items(task, raw)
        if len(eligible) < sum(counts.values()):
            raise ValueError(f"Not enough disjoint items in {task}")
        audit[task] = {"source_items": len(raw["examples"]), "eligible_unique_items": len(eligible)}
        seeded_rng(config["seed"], f"items:{task}").shuffle(eligible)
        offset = 0
        for split in ("smoke", "pilot_development", "pilot_validation", "main"):
            for item in eligible[offset:offset + counts[split]]:
                wrong = [option for option in item["options"] if option != item["target"]]
                item["wrong_hint"] = seeded_rng(config["seed"], f"hint:{item['item_id']}").choice(wrong)
                item["split"] = split
                selected.append(item)
            offset += counts[split]
    return {"schema_version": 1, "config_sha256": digest(config), "source": source,
            "eligibility": audit, "items": selected}
