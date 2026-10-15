"""Smoke-test diagnostics without inventing unvalidated acknowledgment labels."""

from collections import Counter
import csv
from pathlib import Path

from .io import digest, read_json, request_in_progress, write_json
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
              "request_statuses": dict(Counter("started" if request_in_progress(record) else record["status"]
                                               for _, record in records)),
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


def quality_checks(overall, dry_run=False, targets=None):
    """Evaluate observed smoke gates without treating a small sample as certification."""
    targets = targets or {"minimum_completion_fraction": 0.95,
                          "minimum_parseable_fraction_of_completed": 0.99}
    terminal = {"returned", "technical_error", "interrupted"}
    finished = (overall["assigned"] > 0 and not dry_run
                and set(overall["request_statuses"]).issubset(terminal))
    completion = overall["completion_fraction"]
    parsing = overall["parseable_fraction_of_completed"]
    completion_met = completion is not None and completion >= targets["minimum_completion_fraction"]
    parsing_met = parsing is not None and parsing >= targets["minimum_parseable_fraction_of_completed"]
    return {"targets": targets, "collection_finished": finished,
            "completion_target_met": completion_met, "parsing_target_met": parsing_met,
            "observed_targets_met": finished and completion_met and parsing_met}


def summarize(directory):
    """Summarize capture and scoring; acknowledgment analysis remains pending."""
    manifest, records = run_records(directory)
    overall = diagnostics(records)
    return {"schema_version": 1, "split": manifest["identity"]["split"],
            "dry_run": manifest["identity"]["dry_run"], "config": manifest["identity"]["config"],
            "source_sha256": manifest["identity"]["source_sha256"],
            "overall": overall,
            "quality_checks": quality_checks(overall, manifest["identity"]["dry_run"],
                                              manifest["identity"]["config"].get("quality_targets")),
            "by_condition": {code: diagnostics([(request, record) for request, record in records if request["condition"] == code])
                             for code in sorted({request["condition"] for request, _ in records})},
            "by_task": {task: diagnostics([(request, record) for request, record in records if request["item"]["task"] == task])
                        for task in sorted({request["item"]["task"] for request, _ in records})},
            "acknowledgment_analysis": {"status": "pending_human_or_validated_automated_labels",
                                        "primary_contrast": None}}


def compare_smoke_runs(before_directory, after_directory):
    """Verify the same paired requests and compare capture quality across versions."""
    before_manifest, _ = run_records(before_directory)
    after_manifest, _ = run_records(after_directory)
    for manifest in (before_manifest, after_manifest):
        if manifest["identity"]["dry_run"] or manifest["identity"]["split"] != "smoke":
            raise ValueError("Comparison requires two real smoke runs")
    before_requests = {request["request_id"]: request for request in before_manifest["requests"]}
    after_requests = {request["request_id"]: request for request in after_manifest["requests"]}
    if not before_requests or before_requests.keys() != after_requests.keys():
        raise ValueError("Smoke schedules differ")
    for request_id, left in before_requests.items():
        right = after_requests[request_id]
        for field in ("item", "condition", "observer", "access", "hint_present"):
            if left[field] != right[field]:
                raise ValueError(f"Paired smoke {field} differs: {request_id}")
        def normalized_payload(request):
            payload = dict(request["payload"])
            payload.pop("max_tokens")
            messages = payload.pop("messages")
            if len(messages) != 2 or messages[0]["role"] != "system" or messages[1]["role"] != "user":
                raise ValueError("Expected a fresh system/user conversation")
            return payload, messages[1]
        if normalized_payload(left) != normalized_payload(right):
            raise ValueError(f"Sampling, seed, or user prompt differs: {request_id}")
    result = {"matched_requests": len(before_requests), "same_items_hints_seeds_and_user_prompts": True}
    for name, directory, manifest in (("before", before_directory, before_manifest),
                                      ("after", after_directory, after_manifest)):
        summary = summarize(directory)
        config = manifest["identity"]["config"]
        result[name] = {"protocol_version": config["protocol_version"],
                        "prompt_version": config.get("prompt_version", "v1"),
                        "context_tokens": config["context_tokens"],
                        "max_output_tokens": config["generation"]["max_tokens"],
                        "overall": summary["overall"], "quality_checks": summary["quality_checks"]}
    return result


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
