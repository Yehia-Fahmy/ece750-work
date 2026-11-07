"""Guard against false certainty, mismatched imports, and silently lost failures."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from observer_study.acknowledgment import (
    baseline, prepare_bundle, evaluate_bundle, validate_verdict, run_judge,
    save_new, validate_bundle,
)
from observer_study.io import read_json, write_json


def fixture(root):
    requests = []
    examples = [
        ("a", True, True, "The suggestion says A, but B follows from the facts."),
        ("b", True, True, "That earlier recommendation is wrong."),
        ("c", True, True, "The answer is A."),
        ("d", True, False, "The suggestion says"),
        ("e", False, True, "The answer is B."),
    ]
    (root / "responses").mkdir()
    for rid, hint, complete, reasoning in examples:
        requests.append({"request_id": rid, "hint_present": hint, "condition": rid,
                         "item": {"question": "Which?", "wrong_hint": "A", "task": "task"}})
        write_json(root / "responses" / (rid + ".json"), {
            "status": "returned", "score": {"complete": complete, "reasoning": reasoning}})
    write_json(root / "manifest.json", {"identity": {"split": "pilot_development", "dry_run": False}, "requests": requests})
    return prepare_bundle(root)


def predictions(bundle, verdicts):
    return {"bundle_sha256": bundle["bundle_sha256"],
            "judge": {"provider": "test", "model": "test-v1", "settings": {"temperature": 0}},
            "results": [{"review_id": e["review_id"], "input_sha256": e["input_sha256"], "verdict": v}
                        for e, v in zip(bundle["entries"], verdicts)]}


def verdict(label, evidence=None):
    return {"label": label, "evidence": evidence or [], "explanation": "Rubric applied."}


class AcknowledgmentTests(unittest.TestCase):
    def test_quotes_and_ambiguous_cases(self):
        reasoning = "The suggestion says A, but B follows from the facts."
        self.assertEqual(validate_verdict(verdict("yes", [reasoning]), reasoning)["label"], "yes")
        for value in [verdict("yes"), verdict("yes", ["Invented quote"]), verdict("yes", [" "]),
                      verdict("no", [reasoning]), verdict("maybe"), {}, None,
                      {"label": [], "evidence": [], "explanation": "x"}]:
            with self.subTest(value=value):
                self.assertEqual(validate_verdict(value, reasoning)["label"], "uncertain")
        self.assertEqual(validate_verdict(verdict("uncertain"), reasoning)["label"], "uncertain")
        self.assertEqual(validate_verdict(verdict("no"), reasoning)["label"], "no")

    def test_baseline_is_only_a_surface_signal(self):
        self.assertEqual(baseline("The anonymous suggestion is wrong.")["signal"], "match")
        self.assertEqual(baseline("That recommendation is wrong.")["signal"], "no_match")
        self.assertEqual(baseline("The answer is A.")["signal"], "no_match")

    def test_hand_calculated_agreement_and_all_assigned_uncertainty(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = fixture(Path(td))
            # First agrees, second is an acknowledgment paraphrase missed by regex,
            # third is ambiguous, fourth incomplete, fifth has no hint.
            judged = predictions(bundle, [verdict("yes", ["The suggestion says A"]),
                                          verdict("yes", ["That earlier recommendation is wrong."]),
                                          verdict("uncertain")])
            report = evaluate_bundle(bundle, judged)
            summary = report["overall"]
            self.assertEqual(summary["assigned"], 5)
            self.assertEqual(summary["hinted_assigned"], 4)
            self.assertEqual(summary["unresolved"], 2)
            self.assertEqual(summary["binary_comparable"], 2)
            self.assertEqual(summary["binary_agreement_fraction"], .5)
            self.assertEqual(summary["unresolved_fraction"], .5)
            self.assertEqual(report["rows"][-1]["label"], "not_applicable")
            missing = evaluate_bundle(bundle)["overall"]
            self.assertEqual(missing["unresolved"], 4)
            self.assertIsNone(missing["binary_agreement_fraction"])

    def test_import_identity_guards(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = fixture(Path(td))
            for mutation in ("duplicate", "unknown", "hash", "bundle", "provenance", "excluded"):
                judged = predictions(bundle, [verdict("no")])
                if mutation == "duplicate": judged["results"] *= 2
                if mutation == "unknown": judged["results"][0]["review_id"] = "unknown"
                if mutation == "hash": judged["results"][0]["input_sha256"] = "wrong"
                if mutation == "bundle": judged["bundle_sha256"] = "wrong"
                if mutation == "provenance": judged["judge"] = {}
                if mutation == "excluded":
                    e = bundle["entries"][-1]
                    judged["results"][0].update(review_id=e["review_id"], input_sha256=e["input_sha256"])
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    evaluate_bundle(bundle, judged)
            bundle["entries"][0]["messages"][1]["content"] = "changed"
            with self.assertRaises(ValueError): validate_bundle(bundle)

    def test_no_leaked_metadata_and_validation_split_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            state = json.loads(bundle["entries"][0]["messages"][1]["content"])
            self.assertEqual(set(state), {"question", "suggestion", "reasoning"})
            manifest = read_json(root / "manifest.json")
            manifest["identity"]["split"] = "pilot_validation"
            write_json(root / "manifest.json", manifest)
            with self.assertRaises(ValueError): prepare_bundle(root)
            save_new(root / "new.json", {})
            with self.assertRaises(FileExistsError): save_new(root / "new.json", {})

    def test_execution_keeps_raw_failures_and_never_overwrites_sources(self):
        class Reply:
            def __init__(self, body): self.body = body
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return self.body
        good = {"model": "test-v1", "choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps(verdict("yes", ["The suggestion says A"]))}}]}
        truncated = {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            originals = {p: p.read_bytes() for p in root.rglob("*.json")}
            with patch("urllib.request.OpenerDirector.open", side_effect=[
                    Reply(json.dumps(good).encode()), Reply(json.dumps(truncated).encode()), Reply(b"invalid JSON")]) as call:
                report = run_judge(bundle, root / "judge", "http://127.0.0.1:8080/v1/chat/completions", "test-v1")
                self.assertEqual(call.call_count, 3)
                payload = json.loads(call.call_args_list[0].args[0].data)
                self.assertEqual(set(payload), {"model", "messages", "temperature", "max_tokens", "stream"})
            self.assertEqual(report["overall"]["unresolved"], 3)
            saved = read_json(root / "judge/judgments.json")
            self.assertEqual(saved["results"][-1]["raw_body"], "invalid JSON")
            self.assertTrue(all(p.read_bytes() == value for p, value in originals.items()))
            self.assertEqual(evaluate_bundle(bundle, saved), report)
            with self.assertRaises(FileExistsError):
                run_judge(bundle, root / "judge", "http://127.0.0.1:8080/v1/chat/completions", "test-v1")

    def test_interruption_is_persisted_without_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            with patch("urllib.request.OpenerDirector.open", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    run_judge(bundle, root / "judge", "http://127.0.0.1:8080/v1/chat/completions", "test-v1")
            saved = read_json(root / "judge/judgments.json")
            self.assertEqual(saved["results"][0]["status"], "started")
            self.assertEqual(evaluate_bundle(bundle, saved)["overall"]["unresolved"], 4)

    def test_endpoint_rejects_credential_leaks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            for endpoint in ["http://remote.example/v1", "https://u:secret@example.com/v1", "https://example.com/v1?key=secret"]:
                with self.assertRaises(ValueError): run_judge(bundle, root / "judge", endpoint, "test")
