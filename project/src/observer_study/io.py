"""Small standard-library helpers for durable research artifacts."""

import hashlib
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


class RequestError(Exception):
    """HTTP/transport failures, retaining error body and retry eligibility."""

    def __init__(self, message, raw_body=None, retryable=False):
        super().__init__(message)
        self.raw_body = raw_body
        self.retryable = retryable


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
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RequestError(f"HTTP {exc.code}", exc.read().decode("utf-8", errors="replace"), exc.code in (408, 429, 500, 502, 503, 504)) from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise RequestError(str(exc), retryable=True) from exc
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError as exc:
        raise RequestError("Response is not JSON", raw_body=raw) from exc
