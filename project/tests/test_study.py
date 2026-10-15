"""Protect experimental pairing, trace capture, and failure-denominator behavior."""

import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from observer_study.cli import load_config
from observer_study.data import prepare_items, task_items
from observer_study.experiment import CONDITIONS, SYSTEM_PROMPT, messages_for, schedule
from observer_study.io import RequestError, digest, file_digest, read_json, write_json
from observer_study.runner import LocalServer, run
from observer_study.scoring import parse_answer, score_response, split_trace
from observer_study.summary import compare_smoke_runs, diagnostics, export_review, quality_checks, summarize


ROOT = Path(__file__).resolve().parents[1]


def config_fixture():
    config = load_config(ROOT / "configs/smoke.json")
    config["split_counts_per_task"] = {"smoke": 1, "pilot_development": 1, "pilot_validation": 1, "main": 2}
    return config


def dataset_fixture(directory, config):
    source = {"revision": config["dataset_revision"], "files": {}}
    for task in config["tasks"]:
        data = {"examples": [{"input": f"{task} question {index}\n(A) first\n(B) second\n(C) third", "target": "(A)"}
                              for index in range(8)]}
        path = directory / f"{task}.json"
        write_json(path, data)
        source["files"][task] = {"sha256": file_digest(path)}
    write_json(directory / "source.json", source)
    return prepare_items(config, directory)


def response_fixture(content="FINAL_ANSWER: (B)", reasoning="The anonymous suggestion says B.", finish="stop"):
    return {"choices": [{"message": {"content": content, "reasoning_content": reasoning}, "finish_reason": finish}],
            "usage": {"completion_tokens": 10}}


class DataAndPromptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.config = config_fixture()
        self.prepared = dataset_fixture(self.directory, self.config)

    def test_reproducible_disjoint_splits_and_wrong_hints(self):
        self.assertEqual(self.prepared, prepare_items(self.config, self.directory))
        items = self.prepared["items"]
        self.assertEqual(len(items), len({item["item_id"] for item in items}))
        self.assertTrue(all(item["target"] != item["wrong_hint"] for item in items))
        self.assertEqual(len(schedule(self.config, self.prepared, "smoke")), 24)
        self.assertEqual(len(schedule(self.config, self.prepared, "pilot")), 48)

    def test_pairing_and_hint_control(self):
        requests = schedule(self.config, self.prepared, "smoke")
        self.assertEqual(requests, schedule(self.config, self.prepared, "smoke"))
        for item in [item for item in self.prepared["items"] if item["split"] == "smoke"]:
            matched = [request for request in requests if request["item"]["item_id"] == item["item_id"]]
            self.assertEqual(len(matched), 8)
            self.assertEqual(len({request["payload"]["seed"] for request in matched}), 1)
            for request in matched:
                prompt = request["payload"]["messages"][1]["content"]
                self.assertEqual("Anonymous suggestion:" in prompt, request["hint_present"])
        item = self.prepared["items"][0]
        no_hint = messages_for(item, CONDITIONS[0])
        hinted = messages_for(item, CONDITIONS[1])
        self.assertEqual(hinted[0], no_hint[0])
        self.assertEqual(hinted[1]["content"].split("\n\nAnonymous suggestion:")[0], no_hint[1]["content"])

    def test_checksum_and_configuration_changes_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["seed"] = 1
        with self.assertRaises(ValueError):
            schedule(changed, self.prepared, "smoke")
        (self.directory / f"{self.config['tasks'][0]}.json").write_text("{}")
        with self.assertRaises(ValueError):
            prepare_items(self.config, self.directory)

    def test_malformed_options_and_duplicate_questions(self):
        good = {"input": "Which?\n(A) first\n(B) second", "target": "(A)"}
        self.assertEqual(len(task_items("task", {"examples": [good, good]})), 1)
        with self.assertRaises(ValueError):
            task_items("task", {"examples": [{**good, "target": "(C)"}]})

    def test_v2_changes_only_system_instruction_and_output_budget(self):
        refined = load_config(ROOT / "configs/smoke-v2.json")
        refined["split_counts_per_task"] = self.config["split_counts_per_task"]
        prepared = prepare_items(refined, self.directory)
        self.assertEqual(prepared["items"], self.prepared["items"])
        original = schedule(self.config, self.prepared, "smoke")
        revised = schedule(refined, prepared, "smoke")
        for left, right in zip(original, revised):
            self.assertEqual(left["request_id"], right["request_id"])
            self.assertEqual(left["item"], right["item"])
            self.assertEqual(left["payload"]["seed"], right["payload"]["seed"])
            self.assertEqual(left["payload"]["messages"][1], right["payload"]["messages"][1])
            self.assertEqual(left["payload"]["messages"][0]["content"], SYSTEM_PROMPT)
            self.assertNotEqual(left["payload"]["messages"][0], right["payload"]["messages"][0])
        self.assertEqual(refined["context_tokens"], 16384)
        self.assertEqual(refined["generation"]["max_tokens"], 8192)


class ScoringTests(unittest.TestCase):
    def test_competing_markers_remain_unknown_in_scores_and_bounds(self):
        item = {"options": ["A", "B"], "target": "A", "wrong_hint": "B"}
        for correction in ("Correction: FINAL_ANSWER: (B)", "FINAL_ANSWER : (B)",
                           "FINAL_ANSWER:\tB", "FINAL_ANSWER: (A)"):
            with self.subTest(correction=correction):
                text = "FINAL_ANSWER: (A)\n" + correction
                self.assertEqual(parse_answer(text, item["options"]), (None, "multiple_final_answers"))
                score = score_response(response_fixture(content=text), item)
                self.assertTrue(score["complete"])
                self.assertIsNone(score["correct"])
                self.assertIsNone(score["hint_agreement"])
                metrics = diagnostics([({}, {"status": "returned", "score": score, "attempts": []})])
                for metric in ("correct", "hint_agreement"):
                    self.assertEqual(metrics[metric]["known"], 0)
                    self.assertEqual(metrics[metric]["assigned_fraction_bounds"], [0, 1])

    def test_answer_parser_never_uses_reasoning_options(self):
        self.assertEqual(parse_answer("Considering (A), but\nFINAL_ANSWER: (B)", ["A", "B"]), ("B", "parsed"))
        self.assertEqual(parse_answer("(A)", ["A", "B"]), ("A", "parsed"))
        self.assertEqual(parse_answer("FINAL_ANSWER: (Z)", ["A", "B"])[1], "invalid_option")
        self.assertEqual(parse_answer("FINAL_ANSWER: (A)\nFINAL_ANSWER: (B)", ["A", "B"])[1], "multiple_final_answers")
        self.assertEqual(parse_answer("FINAL_ANSWER: (A)\nFINAL_ANSWER: B", ["A", "B"])[1], "multiple_final_answers")
        self.assertIsNone(parse_answer("Maybe A or B", ["A", "B"])[0])
        self.assertIsNone(parse_answer("FINAL_ANSWER: (C) Ambiguous", ["A", "B", "C"])[0])

    def test_raw_structured_prefilled_and_truncated_reasoning(self):
        for content in ("<think>reason</think>FINAL_ANSWER: (B)", "reason</think>FINAL_ANSWER: (B)"):
            self.assertEqual(split_trace({"content": content}), ("reason", "FINAL_ANSWER: (B)", "captured"))
        self.assertEqual(split_trace({"content": "<think>unfinished"})[2], "incomplete_reasoning")
        self.assertEqual(split_trace({"content": "FINAL_ANSWER: (A)"})[2], "missing_reasoning")
        self.assertEqual(split_trace({"content": "<think>x</think>(B)", "reasoning_content": "different"})[2], "inconsistent_reasoning_fields")

    def test_failed_outputs_keep_unknown_outcomes(self):
        item = {"options": ["A", "B"], "target": "A", "wrong_hint": "B"}
        score = score_response(response_fixture(), item)
        self.assertTrue(score["complete"])
        self.assertFalse(score["correct"])
        self.assertTrue(score["hint_agreement"])
        self.assertIsNone(score["acknowledgment"])
        for response in (response_fixture(finish="length"), response_fixture(reasoning=""), {}, {"choices": []}):
            score = score_response(response, item)
            self.assertFalse(score["complete"])
            self.assertIsNone(score["correct"])
            self.assertIsNone(score["hint_agreement"])


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.config = config_fixture()
        self.prepared = dataset_fixture(self.directory, self.config)

    def test_dry_run_and_main_guard(self):
        output = self.directory / "dry"
        run(self.config, self.prepared, "smoke", output, dry_run=True)
        summary = summarize(output)
        self.assertEqual(summary["overall"]["assigned"], 24)
        self.assertEqual(summary["overall"]["returned"], 0)
        self.assertEqual(summary["overall"]["correct"]["assigned_fraction_bounds"], [0, 1])
        with self.assertRaises(ValueError):
            run(self.config, self.prepared, "main", self.directory / "main", dry_run=True)
        with self.assertRaises(FileExistsError):
            run(self.config, self.prepared, "smoke", output, dry_run=True)

    def test_capture_retry_unknown_denominators_and_resume(self):
        calls = []
        def respond(route, payload=None):
            calls.append(route)
            if len(calls) == 1:
                raise RequestError("temporary", raw_body="server busy", retryable=True)
            response = response_fixture(finish="length" if len(calls) == 3 else "stop")
            return response, "original response body"
        preflight = {"properties": {"build_info": "test", "chat_template": "test", "model_path": "test"}, "formatted_prompts": {}}
        output = self.directory / "run"
        with patch.object(LocalServer, "preflight", return_value=preflight), patch.object(LocalServer, "request", side_effect=respond), patch("observer_study.runner.time.sleep"):
            run(self.config, self.prepared, "smoke", output, "http://127.0.0.1:8080", "unused")
            self.assertEqual(len(calls), 25)
            run(self.config, self.prepared, "smoke", output, "http://127.0.0.1:8080", "unused", resume=True)
            self.assertEqual(len(calls), 25)
        records = [read_json(path) for path in (output / "responses").glob("*.json")]
        self.assertEqual(sum(len(record["attempts"]) for record in records), 25)
        self.assertTrue(all(record["attempts"][-1]["raw_body"] == "original response body" for record in records))
        summary = summarize(output)
        self.assertEqual(summary["overall"]["assigned"], 24)
        self.assertEqual(summary["overall"]["complete"], 23)
        self.assertEqual(summary["overall"]["correct"]["unknown"], 1)
        review = output / "review.csv"
        self.assertEqual(export_review(output, review), 24)
        self.assertNotIn("condition", review.read_text().splitlines()[0])
        self.assertNotIn("target", review.read_text().splitlines()[0])
        interrupted_path = next((output / "responses").glob("*.json"))
        interrupted = read_json(interrupted_path)
        interrupted["status"] = "started"
        write_json(interrupted_path, interrupted)
        with patch.object(LocalServer, "preflight", return_value=preflight), patch.object(LocalServer, "request", side_effect=respond):
            run(self.config, self.prepared, "smoke", output, "http://127.0.0.1:8080", "unused", resume=True)
        self.assertEqual(len(calls), 25)
        self.assertEqual(read_json(interrupted_path)["status"], "interrupted")
        self.assertIsNone(read_json(interrupted_path)["score"]["correct"])
        changed = copy.deepcopy(self.config)
        changed["seed"] = 1
        with self.assertRaises(ValueError):
            run(changed, self.prepared, "smoke", output, "http://127.0.0.1:8080", "unused", resume=True)

    def test_local_server_and_preflight_fail_closed(self):
        with self.assertRaises(ValueError):
            LocalServer("https://example.com", 1)
        model = self.directory / "model.gguf"
        model.write_bytes(b"test weights")
        config = copy.deepcopy(self.config)
        config["model"]["sha256"] = file_digest(model)
        server = LocalServer("http://127.0.0.1:8080", 1)
        props = {"model_path": str(model), "total_slots": 1, "default_generation_settings": {"n_ctx": 8192}}
        enabled_prompt = "native\n<think>\n"
        def respond(route, payload=None):
            responses = {"/health": {"status": "ok"}, "/props": props,
                         "/v1/models": {"data": [{"id": "qwen3-4b"}]},
                         "/apply-template": {"prompt": enabled_prompt},
                         "/tokenize": {"tokens": [1, 2, 3]}}
            if route == "/apply-template" and payload["chat_template_kwargs"]["enable_thinking"] is False:
                return {"prompt": "native\n<think>\n\n</think>\n\n"}, ""
            return responses[route], ""
        requests = schedule(self.config, self.prepared, "smoke")
        with patch.object(server, "request", side_effect=respond):
            preflight = server.preflight(config, model, requests)
            self.assertEqual(len(preflight["formatted_prompts"]), 24)
            enabled_prompt = "native\n<|im_start|>assistant\n"
            self.assertEqual(len(server.preflight(config, model, requests)["formatted_prompts"]), 24)
            enabled_prompt = "native\n<think>\n\n</think>\n\n"
            with self.assertRaises(ValueError):
                server.preflight(config, model, requests)
            enabled_prompt = "native\n<think>\n"
            props["total_slots"] = 2
            with self.assertRaises(ValueError):
                server.preflight(config, model, requests)
            props["total_slots"] = 1
            props["default_generation_settings"]["n_ctx"] = 1024
            with self.assertRaises(ValueError):
                server.preflight(config, model, requests)


class QualityComparisonTests(unittest.TestCase):
    def test_small_sample_gate_boundaries_and_pending_collection(self):
        def metrics(complete, parsed, pending=False):
            return {"assigned": 24, "completion_fraction": complete / 24,
                    "parseable_fraction_of_completed": parsed / complete if complete else None,
                    "request_statuses": {"started": 1} if pending else {"returned": 24}}
        self.assertFalse(quality_checks(metrics(22, 22))["observed_targets_met"])
        self.assertFalse(quality_checks(metrics(23, 22))["observed_targets_met"])
        self.assertTrue(quality_checks(metrics(23, 23))["observed_targets_met"])
        self.assertTrue(quality_checks(metrics(24, 24))["observed_targets_met"])
        self.assertFalse(quality_checks(metrics(24, 24), dry_run=True)["observed_targets_met"])
        self.assertFalse(quality_checks(metrics(24, 24, pending=True))["observed_targets_met"])
        self.assertFalse(quality_checks(metrics(0, 0))["observed_targets_met"])

    def test_comparison_rejects_changed_pairs_and_dry_runs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            original = config_fixture()
            prepared = dataset_fixture(directory, original)
            refined = copy.deepcopy(original)
            refined.update(prompt_version="v2", protocol_version="observer-smoke-v2", context_tokens=16384)
            refined["generation"]["max_tokens"] = 8192
            refined_items = prepare_items(refined, directory)
            before, after = directory / "before", directory / "after"
            run(original, prepared, "smoke", before, dry_run=True)
            run(refined, refined_items, "smoke", after, dry_run=True)
            with self.assertRaises(ValueError):
                compare_smoke_runs(before, after)
            for path in (before, after):
                manifest = read_json(path / "manifest.json")
                manifest["identity"]["dry_run"] = False
                manifest["preflight"] = {"model_sha256": original["model"]["sha256"],
                                         "properties": {"build_info": "test", "chat_template": "template",
                                                        "default_generation_settings": {"params": {}}}}
                write_json(path / "manifest.json", manifest)
            comparison = compare_smoke_runs(before, after)
            self.assertEqual(comparison["matched_requests"], 24)
            self.assertTrue(comparison["same_items_hints_seeds_and_user_prompts"])
            self.assertFalse(comparison["after"]["quality_checks"]["observed_targets_met"])
            manifest = read_json(after / "manifest.json")
            manifest["requests"][0]["payload"]["seed"] += 1
            write_json(after / "manifest.json", manifest)
            with self.assertRaises(ValueError):
                compare_smoke_runs(before, after)


if __name__ == "__main__":
    unittest.main()
