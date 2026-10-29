"""Small standard-library helpers for durable research artifacts."""

import base64
import hashlib
import http.client
import json
from pathlib import Path
import urllib.error
import urllib.request


def digest(value):
    """Hash a JSON-compatible value independently of dictionary ordering."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_digest(path):
    """Hash a file without loading model weights into memory."""
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path):
    """Read a UTF-8 JSON artifact."""
    return json.loads(Path(path).read_text())


def write_json(path, value):
    """Replace an artifact atomically after writing its complete contents."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def request_in_progress(record):
    """Recognize active requests, including legacy errors with an unfinished retry."""
    if record["status"] == "started":
        return True
    attempts = record.get("attempts", [])
    return bool(record["status"] == "technical_error" and attempts
                and attempts[-1].get("started_at") and not attempts[-1].get("finished_at"))


class RequestError(Exception):
    """HTTP/transport failures, retaining error body and retry eligibility."""

    def __init__(self, message, raw_body=None, retryable=False, details=None):
        super().__init__(message)
        self.raw_body = raw_body
        self.retryable = retryable
        self.details = details


def _read_response_body(response, *, retryable=True, http_status=None):
    """Retain truncated bytes even when the connection splits a UTF-8 character."""
    try:
        return response.read()
    except http.client.IncompleteRead as exc:
        details = {"kind": "incomplete_http_body", "http_status": http_status,
                   "received_bytes": len(exc.partial), "missing_bytes": exc.expected,
                   "partial_body_base64": base64.b64encode(exc.partial).decode("ascii")}
        raise RequestError("Incomplete HTTP response body", exc.partial.decode("utf-8", errors="replace"),
                           retryable=retryable, details=details) from exc


def _decode_response_body(body, *, retryable=False, http_status=None):
    """Retain malformed UTF-8 losslessly without treating it as model output."""
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError as exc:
        details = {"kind": "invalid_utf8", "http_status": http_status,
                   "received_bytes": len(body), "body_base64": base64.b64encode(body).decode("ascii")}
        raise RequestError("Response is not UTF-8", body.decode("utf-8", errors="replace"),
                           retryable=retryable, details=details) from exc


def request_json(url, payload=None, timeout=30, local=False):
    """Fetch JSON and retain the original response body for trace auditing."""
    headers = {"User-Agent": "ece750-observer-study/1", "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=body, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if local else urllib.request.build_opener()
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = _decode_response_body(_read_response_body(response))
    except urllib.error.HTTPError as exc:
        retryable = exc.code in (408, 429, 500, 502, 503, 504)
        with exc:
            raw = _read_response_body(exc, retryable=retryable, http_status=exc.code)
        text = _decode_response_body(raw, retryable=retryable, http_status=exc.code)
        raise RequestError(f"HTTP {exc.code}", text, retryable) from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise RequestError(str(exc), retryable=True) from exc
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError as exc:
        raise RequestError("Response is not JSON", raw_body=raw) from exc
