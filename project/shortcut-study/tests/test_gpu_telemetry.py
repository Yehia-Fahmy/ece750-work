"""CPU-only telemetry checks; no GPU probes or inference occur."""

from itertools import chain, repeat
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from shortcut_study.runtime.telemetry import GpuTelemetry, PROBE_TIMEOUT_SECONDS, sample_gpu

GPU = {"name": "NVIDIA GeForce RTX 3070 Ti", "uuid": "GPU-fixture",
       "memory_total_mib": 8192, "memory_used_mib": 500, "utilization_gpu_percent": 10}


def wait_for_records(telemetry, count):
    deadline = time.monotonic() + 2
    while len(telemetry._records) < count and time.monotonic() < deadline:
        time.sleep(.002)
    if len(telemetry._records) < count:
        raise AssertionError("mock telemetry samples did not arrive")


class GpuTelemetryTests(unittest.TestCase):
    def test_probe_uses_fixed_query_bounded_subprocess(self):
        completed = subprocess.CompletedProcess([], 0, "NVIDIA GeForce RTX 3070 Ti, GPU-fixture, 8192, 500, 10\n", "")
        with patch("shortcut_study.runtime.telemetry.shutil.which", return_value="/fixture/nvidia-smi"), \
                patch("shortcut_study.runtime.telemetry.subprocess.run", return_value=completed) as run:
            self.assertEqual(sample_gpu(), GPU)
            self.assertEqual(run.call_args.kwargs["timeout"], PROBE_TIMEOUT_SECONDS)
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertIn("--query-gpu=name,uuid,memory.total,memory.used,utilization.gpu", run.call_args.args[0])

    def test_probe_rejects_invalid_or_multiple_gpu_rows(self):
        for stdout in ("Other GPU, id, 8192, 2, 10\n", "NVIDIA GeForce RTX 3070 Ti, id, 8192, 9000, 10\n",
                       "NVIDIA GeForce RTX 3070 Ti, id, 8192, 2, N/A\n", "one\ntwo\n"):
            with patch("shortcut_study.runtime.telemetry.shutil.which", return_value="/fixture/nvidia-smi"), \
                    patch("shortcut_study.runtime.telemetry.subprocess.run",
                          return_value=subprocess.CompletedProcess([], 0, stdout, "")):
                with self.assertRaises(ValueError):
                    sample_gpu()

    def test_samples_are_durable_and_peak_is_explicitly_sampled(self):
        higher = {**GPU, "memory_used_mib": 7800, "utilization_gpu_percent": 90}
        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", side_effect=chain([GPU], repeat(higher))):
            with GpuTelemetry(directory, interval_seconds=.01) as telemetry:
                wait_for_records(telemetry, 2)
                lines = Path(directory, "gpu-telemetry.jsonl").read_text().splitlines()
                self.assertGreaterEqual(len(lines), 2)
            summary = telemetry.summary
            self.assertTrue(summary["valid_for_feasibility"])
            self.assertTrue(summary["thread_stopped"])
            self.assertEqual(summary["sampled_peak_memory_used_mib"], 7800)
            self.assertEqual(summary["minimum_sampled_headroom_mib"], 392)
            self.assertEqual(summary, json.loads(Path(directory, "gpu-telemetry-summary.json").read_text()))

    def test_probe_errors_are_preserved_and_invalidate_feasibility(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", side_effect=TimeoutError("probe timed out")):
            with GpuTelemetry(directory, interval_seconds=.01) as telemetry:
                wait_for_records(telemetry, 1)
            self.assertFalse(telemetry.summary["valid_for_feasibility"])
            self.assertIsNone(telemetry.summary["sampled_peak_memory_used_mib"])
            self.assertGreater(telemetry.summary["error_count"], 0)
            self.assertIn("timed out", telemetry.summary["errors"][0]["error"])

    def test_uuid_change_is_not_aggregated_as_one_gpu(self):
        other = {**GPU, "uuid": "GPU-other"}
        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", side_effect=chain([GPU], repeat(other))):
            with GpuTelemetry(directory, interval_seconds=.01) as telemetry:
                wait_for_records(telemetry, 2)
            self.assertFalse(telemetry.summary["identity_consistent"])
            self.assertFalse(telemetry.summary["valid_for_feasibility"])
            self.assertEqual(len(telemetry.summary["observed_gpu_identities"]), 2)

    def test_background_storage_error_visible(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", return_value=GPU):
            with patch("shortcut_study.runtime.telemetry.os.fsync", side_effect=[None, OSError("disk full"), None]):
                with GpuTelemetry(directory, interval_seconds=.01) as telemetry:
                    telemetry._thread.join(timeout=1)
                self.assertFalse(telemetry.summary["valid_for_feasibility"])
                self.assertEqual(telemetry.summary["background_failure"]["error_type"], "OSError")

    def test_context_exception_stops_monitor_without_swallowing_error(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", return_value=GPU):
            with self.assertRaisesRegex(RuntimeError, "owned workload failed"):
                with GpuTelemetry(directory) as telemetry:
                    raise RuntimeError("owned workload failed")
            self.assertTrue(telemetry.summary["thread_stopped"])

    def test_failed_bounded_teardown_is_visible_and_late_probe_not_written(self):
        release = threading.Event()
        entered = threading.Event()

        def stalled_probe():
            entered.set()
            release.wait(2)
            return GPU

        with tempfile.TemporaryDirectory() as directory, \
                patch("shortcut_study.runtime.telemetry.sample_gpu", side_effect=stalled_probe):
            telemetry = GpuTelemetry(directory)
            telemetry.__enter__()
            self.assertTrue(entered.wait(1))
            try:
                # Simulate a bounded join returning while an external operation
                # is still blocked; never issue a real GPU probe in this test.
                with patch.object(telemetry._thread, "join", return_value=None):
                    telemetry.__exit__(None, None, None)
                self.assertFalse(telemetry.summary["thread_stopped"])
                self.assertFalse(telemetry.summary["valid_for_feasibility"])
                release.set()
                telemetry._thread.join(timeout=1)
                self.assertEqual(Path(directory, "gpu-telemetry.jsonl").read_text(), "")
            finally:
                release.set()
                telemetry._thread.join(timeout=1)

    def test_refuses_artifact_overwrite_and_invalid_intervals(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "gpu-telemetry.jsonl").write_text("prior evidence")
            with self.assertRaises(FileExistsError):
                with GpuTelemetry(directory):
                    pass
            self.assertEqual(Path(directory, "gpu-telemetry.jsonl").read_text(), "prior evidence")
            for interval in (0, -1, True, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    GpuTelemetry(directory, interval_seconds=interval)


if __name__ == "__main__":
    unittest.main()
