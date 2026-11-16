"""Read-only sampled GPU telemetry; sampled maxima are not true peak memory."""

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time

PROBE_TIMEOUT_SECONDS = 5
FIELDS = "name,uuid,memory.total,memory.used,utilization.gpu"


def sample_gpu():
    """Query only the fixed NVIDIA CLI, with no shell or inference operation."""
    executable = shutil.which("nvidia-smi")
    if executable is None:
        fallback = Path("/usr/lib/wsl/lib/nvidia-smi")
        if not fallback.is_file() or not os.access(fallback, os.X_OK):
            raise FileNotFoundError("nvidia-smi unavailable")
        executable = str(fallback)
    result = subprocess.run(
        [executable, "--query-gpu=" + FIELDS, "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=PROBE_TIMEOUT_SECONDS, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"nvidia-smi exit {result.returncode}: {result.stderr.strip()}")
    rows = [line.split(",") for line in result.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0]) != 5:
        raise ValueError("expected exactly one GPU telemetry row")
    name, uuid, total, used, utilization = (part.strip() for part in rows[0])
    total, used, utilization = int(total), int(used), int(utilization)
    if (name != "NVIDIA GeForce RTX 3070 Ti" or not uuid or not 8000 <= total <= 8192
            or not 0 <= used <= total or not 0 <= utilization <= 100):
        raise ValueError("invalid or unsupported GPU telemetry")
    return {"name": name, "uuid": uuid, "memory_total_mib": total,
            "memory_used_mib": used, "utilization_gpu_percent": utilization}


class GpuTelemetry:
    """Continuously journal readings and errors across startup and episodes.

    The caller holds the GPU lease and owns any inference process. This class
    only launches bounded read-only nvidia-smi queries. Inspect ``summary`` after
    exit: any error, identity change, missing samples, or failed teardown makes
    ``valid_for_feasibility`` false. Polling can miss brief memory peaks.
    """

    def __init__(self, directory, *, interval_seconds=1.0):
        if (type(interval_seconds) not in (int, float) or not math.isfinite(interval_seconds)
                or interval_seconds <= 0):
            raise ValueError("interval_seconds must be finite and positive")
        self.directory = Path(directory)
        self.interval_seconds = interval_seconds
        self.samples_path = self.directory / "gpu-telemetry.jsonl"
        self.summary = None
        self._stop = threading.Event()
        self._abandon = threading.Event()
        self._thread = None
        self._records = []
        self._background_failure = None
        self._started = None

    def __enter__(self):
        if self._thread is not None:
            raise RuntimeError("telemetry context is single use")
        self.directory.mkdir(parents=True, exist_ok=True)
        with self.samples_path.open("x", encoding="utf-8") as handle:
            handle.flush()
            os.fsync(handle.fileno())
        self._started = time.monotonic()
        self._thread = threading.Thread(target=self._collect, name="gpu-telemetry", daemon=True)
        self._thread.start()
        return self

    def _collect(self):
        try:
            while True:
                record = {"observed_at_utc": datetime.now(timezone.utc).isoformat(),
                          "elapsed_seconds": time.monotonic() - self._started}
                try:
                    record.update(status="ok", gpu=sample_gpu())
                except Exception as exc:
                    record.update(status="error", error_type=type(exc).__name__, error=str(exc))
                if self._abandon.is_set():
                    break  # never append a late probe after failed bounded teardown
                with self.samples_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                self._records.append(record)
                if self._stop.wait(self.interval_seconds):
                    break
        except BaseException as exc:
            # Includes storage failures. A failed thread must never look like a
            # successful monitor merely because some earlier readings exist.
            self._background_failure = {"error_type": type(exc).__name__, "error": str(exc)}

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop.set()
        self._thread.join(timeout=PROBE_TIMEOUT_SECONDS + 1)
        thread_stopped = not self._thread.is_alive()
        if not thread_stopped:
            self._abandon.set()
        records = list(self._records)
        samples = [r["gpu"] for r in records if r["status"] == "ok"]
        errors = [r for r in records if r["status"] == "error"]
        identities = {(g["name"], g["uuid"], g["memory_total_mib"]) for g in samples}
        identity_consistent = bool(samples) and len(identities) == 1
        elapsed = time.monotonic() - self._started
        self.summary = {
            "schema_version": "shortcut-gpu-telemetry-v1", "measurement_kind": "sampled_read_only_gpu_inventory",
            "interval_seconds": self.interval_seconds, "elapsed_seconds": elapsed,
            "sample_count": len(samples), "error_count": len(errors), "errors": errors,
            "thread_stopped": thread_stopped, "background_failure": self._background_failure,
            "identity_consistent": identity_consistent,
            "observed_gpu_identities": [{"name": n, "uuid": u, "memory_total_mib": m}
                                        for n, u, m in sorted(identities)],
            "sampled_peak_memory_used_mib": max((g["memory_used_mib"] for g in samples), default=None),
            "minimum_sampled_headroom_mib": min((g["memory_total_mib"] - g["memory_used_mib"]
                                                for g in samples), default=None),
            "sampled_peak_utilization_percent": max((g["utilization_gpu_percent"] for g in samples), default=None),
            "valid_for_feasibility": bool(samples) and not errors and identity_consistent
                                     and thread_stopped and self._background_failure is None,
            "limitations": ["Polling can miss brief peaks; these are sampled values, not true peak allocation.",
                            "Includes display and other GPU memory users; does not establish full offload or model qualification."],
        }
        with (self.directory / "gpu-telemetry-summary.json").open("x", encoding="utf-8") as handle:
            json.dump(self.summary, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        return False
