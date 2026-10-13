"""Smoke-test diagnostics without inventing unvalidated acknowledgment labels."""

from collections import Counter
import csv
from pathlib import Path

from .io import digest, read_json, write_json
from .scoring import unknown_score


def run_records(directory):
    """Join saved responses to the full assigned schedule, retaining absent requests."""
    directory = Path(directory)
    manifest = read_json(directory / "manifest.json")
    records = []
    for request in manifest["requests"]:
        path = directory / "responses" / f"{request['request_id']}.json"
        response = read_json(path) if path.exists() else {"status": "not_attempted", "score": unknown_score(), "attempts": []}
        records.append((request, response))
    return manifest, records


def diagnostics(records):
    """Use assigned-item denominators and bound unknown answer outcomes."""
    assigned = len(records)
    complete = sum(record["score"]["complete"] for _, record in records)
    parseable_complete = sum(record["score"]["complete"] and record["score"]["answer"] is not None for _, record in records)
    result = {"assigned": assigned, "returned": sum(record["status"] == "returned" for _, record in records),
              "complete": complete, "parseable_complete": parseable_complete,
              "completion_fraction": complete / assigned if assigned else None,
              "parseable_fraction_of_completed": parseable_complete / complete if complete else None,
              "request_statuses": dict(Counter(record["status"] for _, record in records)),
              "trace_statuses": dict(Counter(record["score"]["trace_status"] for _, record in records)),
              "finish_reasons": dict(Counter(str(record["score"]["finish_reason"]) for _, record in records))}
    for metric in ("correct", "hint_agreement"):
        values = [record["score"][metric] for _, record in records]
        positives = sum(value is True for value in values)
        unknown = sum(value is None for value in values)
        result[metric] = {"positive": positives, "known": assigned - unknown, "unknown": unknown,
                          "assigned_fraction_bounds": [positives / assigned, (positives + unknown) / assigned] if assigned else [None, None]}
    result["total_wall_seconds"] = sum(attempt.get("elapsed_seconds", 0) for _, record in records for attempt in record["attempts"])
    tokens = [record["score"]["usage"].get("completion_tokens") for _, record in records if isinstance(record["score"]["usage"], dict)]
    result["reported_completion_tokens"] = sum(value for value in tokens if isinstance(value, int))
    return result


def summarize(directory):
    """Summarize capture and scoring; acknowledgment analysis remains pending."""
    manifest, records = run_records(directory)
    return {"schema_version": 1, "split": manifest["identity"]["split"],
            "dry_run": manifest["identity"]["dry_run"], "config": manifest["identity"]["config"],
            "source_sha256": manifest["identity"]["source_sha256"],
            "overall": diagnostics(records),
            "by_condition": {code: diagnostics([(request, record) for request, record in records if request["condition"] == code])
                             for code in sorted({request["condition"] for request, _ in records})},
            "by_task": {task: diagnostics([(request, record) for request, record in records if request["item"]["task"] == task])
                        for task in sorted({request["item"]["task"] for request, _ in records})},
            "acknowledgment_analysis": {"status": "pending_human_or_validated_automated_labels",
                                        "primary_contrast": None}}


def export_review(directory, output):
    """Export blinded blank human labels with a separate request-ID mapping."""
    _, records = run_records(directory)
    output = Path(output)
    mapping = {}
    with output.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["review_id", "question", "suggestion", "reasoning", "final_answer", "acknowledgment", "evidence", "review_seconds", "notes"])
        writer.writeheader()
        for request, record in records:
            if record["status"] != "returned":
                continue
            review_id = digest(request["request_id"])[:16]
            mapping[review_id] = request["request_id"]
            score = record["score"]
            writer.writerow({"review_id": review_id, "question": request["item"]["question"],
                             "suggestion": f"({request['item']['wrong_hint']})" if request["hint_present"] else "absent",
                             "reasoning": score["reasoning"], "final_answer": score["final_answer_text"]})
    write_json(output.with_suffix(".mapping.json"), mapping)
    return len(mapping)
