"""Local llama.cpp preflight, durable request capture, and safe resumption."""

from datetime import datetime, timezone
from pathlib import Path
import platform
import time
from urllib.parse import urlparse

from .experiment import schedule
from .io import RequestError, digest, file_digest, read_json, request_in_progress, request_json, write_json
from .scoring import score_response, unknown_score


def timestamp():
    """Return timezone-aware UTC timestamps for run and request records."""
    return datetime.now(timezone.utc).isoformat()


def source_hash():
    """Fingerprint the implementation used to generate and score a run."""
    directory = Path(__file__).resolve().parent
    return digest({path.name: file_digest(path) for path in sorted(directory.glob("*.py"))})


class LocalServer:
    """A loopback-only, non-streaming llama.cpp client with raw body capture."""

    def __init__(self, url, timeout):
        parsed = urlparse(url)
        if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1") or parsed.path not in ("", "/"):
            raise ValueError("Use a local server root URL such as http://127.0.0.1:8080")
        self.url = url.rstrip("/")
        self.timeout = timeout

    def request(self, route, payload=None):
        """Send one local JSON request without using an HTTP proxy."""
        return request_json(self.url + route, payload, timeout=self.timeout, local=True)

    def preflight(self, config, model_file, requests):
        """Check model identity, context, native thinking, and every formatted prompt."""
        if file_digest(model_file) != config["model"]["sha256"]:
            raise ValueError("Model checksum differs from the official configured artifact")
        health, _ = self.request("/health")
        if health.get("status") != "ok":
            raise ValueError("Server is not healthy")
        props, _ = self.request("/props")
        models, _ = self.request("/v1/models")
        if config["model"]["alias"] not in {item["id"] for item in models["data"]}:
            raise ValueError("Configured model alias is not served")
        served_path = Path(props["model_path"]).resolve()
        if served_path != Path(model_file).resolve():
            raise ValueError("Server model path differs from the checksum-verified model file")
        if props.get("total_slots") != 1:
            raise ValueError("This draft protocol requires exactly one inference slot")
        context = props["default_generation_settings"]["n_ctx"]
        if context != config["context_tokens"]:
            raise ValueError("Server context differs from the configured allocation")
        prompts = {}
        for request in requests:
            payload = request["payload"]
            rendered, _ = self.request("/apply-template", {
                "messages": payload["messages"],
                "chat_template_kwargs": payload["chat_template_kwargs"],
                "add_generation_prompt": True})
            prompt = rendered["prompt"]
            disabled, _ = self.request("/apply-template", {
                "messages": payload["messages"], "chat_template_kwargs": {"enable_thinking": False},
                "add_generation_prompt": True})
            # Official Qwen3 templates either prefill <think> or leave the assistant
            # prefix open so the model emits it. Disabled mode prefills an empty block.
            enabled_suffix = prompt.rstrip().endswith(("<think>", "<|im_start|>assistant"))
            if not enabled_suffix or disabled["prompt"] == prompt or not disabled["prompt"].rstrip().endswith("</think>"):
                raise ValueError("Chat template does not distinguish native thinking from disabled mode")
            tokenized, _ = self.request("/tokenize", {"content": prompt, "add_special": False, "parse_special": True})
            token_count = len(tokenized["tokens"])
            if token_count + config["generation"]["max_tokens"] > config["context_tokens"]:
                raise ValueError(f"Prompt/output exceed configured context: {request['request_id']}")
            prompts[request["request_id"]] = {"formatted_prompt": prompt, "input_token_count": token_count,
                                              "disabled_thinking_prompt": disabled["prompt"]}
        return {"properties": props, "models": models, "formatted_prompts": prompts,
                "model_sha256": config["model"]["sha256"]}


def run(config, prepared, split, output, url=None, model_file=None, dry_run=False, resume=False):
    """Capture each attempt; resume only unattempted requests under identical settings."""
    if split == "main" and config.get("protocol_status") != "frozen":
        raise ValueError("Main collection requires a frozen protocol; this configuration is draft")
    requests = schedule(config, prepared, split)
    output = Path(output)
    identity = {"config": config, "prepared_sha256": digest(prepared), "source_sha256": source_hash(),
                "requests_sha256": digest(requests), "split": split, "dry_run": dry_run, "server_url": url}
    existing = read_json(output / "manifest.json") if resume else None
    if existing is not None and existing["identity"] != identity:
        raise ValueError("Cannot resume: code, inputs, settings, split, or endpoint changed")
    server = None
    preflight = None
    if not dry_run:
        if not url or model_file is None:
            raise ValueError("Real inference requires --server and --model-file")
        server = LocalServer(url, config["request_timeout_seconds"])
        preflight = server.preflight(config, model_file, requests)
        if existing is not None:
            old = existing["preflight"]
            for field in ("build_info", "chat_template", "model_path"):
                if old["properties"].get(field) != preflight["properties"].get(field):
                    raise ValueError(f"Cannot resume: server {field} changed")
            if old["properties"].get("default_generation_settings", {}).get("params") != preflight["properties"].get("default_generation_settings", {}).get("params"):
                raise ValueError("Cannot resume: server generation defaults changed")
            if old["formatted_prompts"] != preflight["formatted_prompts"]:
                raise ValueError("Cannot resume: formatted prompts changed")
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
        write_json(output / "manifest.json", {"schema_version": 1, "created_at": timestamp(),
                   "identity": identity, "python": platform.python_version(), "platform": platform.platform(),
                   "preflight": preflight, "requests": requests})
        (output / "responses").mkdir()
    if dry_run:
        print(f"Prepared {len(requests)} requests without inference: {output}", flush=True)
        return
    for index, request in enumerate(requests, 1):
        path = output / "responses" / f"{request['request_id']}.json"
        if path.exists():
            previous = read_json(path)
            if request_in_progress(previous):
                previous.update(status="interrupted", score=unknown_score())
                write_json(path, previous)
            continue
        record = {"request_id": request["request_id"], "status": "started", "attempts": [], "score": unknown_score()}
        write_json(path, record)
        for attempt_number in range(config["technical_retries"] + 1):
            record["status"] = "started"
            attempt = {"number": attempt_number + 1, "started_at": timestamp()}
            record["attempts"].append(attempt)
            write_json(path, record)
            started = time.monotonic()
            try:
                response, raw = server.request("/v1/chat/completions", request["payload"])
                attempt.update(raw_body=raw, response=response, elapsed_seconds=time.monotonic() - started,
                               finished_at=timestamp())
                record.update(status="returned", score=score_response(response, request["item"]))
                write_json(path, record)
                break
            except RequestError as exc:
                attempt.update(error=str(exc), raw_body=exc.raw_body, retryable=exc.retryable,
                               elapsed_seconds=time.monotonic() - started, finished_at=timestamp())
                terminal = not exc.retryable or attempt_number == config["technical_retries"]
                record["status"] = "technical_error" if terminal else "started"
                write_json(path, record)
                if terminal:
                    break
                time.sleep(1)
        score = record["score"]
        print(f"[{index}/{len(requests)}] {request['request_id']} {record['status']} "
              f"finish={score['finish_reason']} trace={score['trace_status']} answer={score['answer']}", flush=True)
