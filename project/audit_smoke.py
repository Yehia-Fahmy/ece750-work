"""Re-score retained smoke responses without changing their cached evidence."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from observer_study.io import digest, file_digest, write_json
from observer_study.runner import source_hash
from observer_study.scoring import score_response
from observer_study.summary import diagnostics, run_records


def audit_run(directory):
    """Compare every returned raw response with its saved body and cached score."""
    manifest, records = run_records(directory)
    if manifest["identity"]["dry_run"] or manifest["identity"]["split"] != "smoke":
        raise ValueError("Audit requires a real smoke run")
    if digest(manifest["requests"]) != manifest["identity"]["requests_sha256"]:
        raise ValueError("Saved request schedule differs from its fingerprint")
    rescored, changes = [], []
    for request, record in records:
        if record["status"] != "returned" or not record["attempts"]:
            raise ValueError(f"Missing returned response: {request['request_id']}")
        attempt = record["attempts"][-1]
        if json.loads(attempt["raw_body"]) != attempt["response"]:
            raise ValueError(f"Raw body differs from saved response: {request['request_id']}")
        score = score_response(attempt["response"], request["item"])
        fields = {field: {"cached": record["score"].get(field), "rescored": score.get(field)}
                  for field in sorted(record["score"].keys() | score.keys())
                  if record["score"].get(field) != score.get(field)}
        if fields:
            changes.append({"request_id": request["request_id"], "fields": fields})
        rescored.append((request, {**record, "score": score}))
    current = diagnostics(rescored)
    return {"run": Path(directory).name, "collection_source_sha256": manifest["identity"]["source_sha256"],
            "assigned": len(records), "audited_responses": len(rescored), "changed_scores": changes,
            "cached_overall_matches_rescored": diagnostics(records) == current, "rescored_overall": current}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True, help="Fresh audit output path")
    args = parser.parse_args()
    try:
        if args.out.exists():
            raise FileExistsError("Audit output exists; choose a new path")
        report = {"schema_version": 1, "scoring_source_sha256": source_hash(),
                  "audit_script_sha256": file_digest(__file__), "runs": [audit_run(path) for path in args.runs]}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.out, report)
        print(f"Audited {sum(run['audited_responses'] for run in report['runs'])} responses: {args.out}")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
