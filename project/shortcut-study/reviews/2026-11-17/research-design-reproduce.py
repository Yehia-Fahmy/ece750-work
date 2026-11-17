"""Read-only CPU review probes. Run from the repository root with study PYTHONPATH.

No model calls, raw-archive changes, or experimental execution. Output is JSON
on stdout; generated main tasks are inspected as reservations only.
"""

from pathlib import Path
import hashlib
import json
import subprocess

from shortcut_study.hashing import sha256_json
from shortcut_study.splits import check_split_disjointness
from shortcut_study.tasks.tables import enumerate_tab_catalog_assignments, generate_task


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    records, seen, collisions = [], {}, []
    for split in ("development", "qualification", "main"):
        for assignment in enumerate_tab_catalog_assignments(split=split):
            if (assignment["information_state"] != "complete"
                    or assignment["shortcut_available"]
                    or assignment["visibility"] != "V00"):
                continue
            task = generate_task(assignment, generation_seed=assignment["generation_seed"])
            content_hash = sha256_json({"public": task.public_task, "world": task.hidden_truth["world"]})
            descriptor = {"split": split, "base_id": assignment["base_id"],
                          "semantic_fingerprint": task.semantic_fingerprint}
            if content_hash in seen:
                collisions.append({"same_public_and_world_hash": content_hash,
                                   "first": seen[content_hash], "second": descriptor})
            seen[content_hash] = descriptor
            records.append(dict(assignment, semantic_fingerprint=task.semantic_fingerprint))
    check_split_disjointness(records)

    names = ("g2-held-out-20261116", "g2-held-out-20261116-catalog-v2")
    roots = [root / "project/runs/shortcut-study" / name for name in names]
    archive_check = {"runs": list(names)}
    if all((p / "schedule.json").exists() for p in roots):
        schedules = [json.loads((p / "schedule.json").read_text())["assignments"] for p in roots]
        first, second = schedules
        archive_check["schedule_sha256"] = {n: sha256(p / "schedule.json") for n, p in zip(names, roots)}
        archive_check["same_episode_ids_in_order"] = [a["episode_id"] for a in first] == [a["episode_id"] for a in second]
        archive_check["same_assignments_except_generator_version"] = all(
            {k: v for k, v in a.items() if k != "generator_version"}
            == {k: v for k, v in b.items() if k != "generator_version"}
            for a, b in zip(first, second)) and len(first) == len(second)
        counts = {k: 0 for k in ("hidden_truth", "resources", "prompt")}
        input_hashes = {n: {} for n in names}
        for assignment in first:
            episode_id = assignment["episode_id"]
            paths = [p / episode_id / "inputs.json" for p in roots]
            inputs = [json.loads(p.read_text()) for p in paths]
            for key in counts:
                counts[key] += inputs[0][key] == inputs[1][key]
            for name, path in zip(names, paths):
                input_hashes[name][episode_id] = sha256(path)
        archive_check.update({"episodes_compared": len(first), "equal_input_field_counts": counts,
                              "input_hash_manifest_digests": {n: sha256_json(v) for n, v in input_hashes.items()}})
    else:
        archive_check["status"] = "raw archives unavailable; cannot reproduce input comparison"

    source_paths = ["src/shortcut_study/tasks/tables/common.py", "src/shortcut_study/tasks/tables/catalog.py",
                    "src/shortcut_study/tasks/tables/tab04.py", "src/shortcut_study/qualification.py",
                    "src/shortcut_study/ids.py", "src/shortcut_study/splits.py"]
    result = {
        "review_kind": "read_only_cpu_research_design_review",
        "input_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_sha256": {p: sha256(root / "project/shortcut-study" / p) for p in source_paths},
        "reserved_bases_checked": len(records),
        "existing_split_disjointness_check": "passed",
        "content_duplicate_pairs_across_splits": collisions,
        "qualification_reuse": archive_check,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
