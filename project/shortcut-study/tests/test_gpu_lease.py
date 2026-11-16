"""CPU/process-only lease checks; no GPU workload or server is started."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from shortcut_study.runtime import GpuLease, LeaseBusyError, assert_supported_gpu, resolve_canonical_checkout


class GpuLeaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def lease(self, root=None):
        return GpuLease(root or self.root, owner="test-owner", job="cpu-fixture", run_id="test-run")

    def child(self, code, *arguments):
        return subprocess.run([sys.executable, "-c", code, str(self.root), *arguments],
                              capture_output=True, text=True, timeout=10, check=False)

    def test_context_metadata_heartbeat_and_release(self):
        lease = self.lease()
        with self.assertRaises(RuntimeError):
            lease.assert_held()
        with lease:
            lease.assert_held()
            metadata = lease.heartbeat()
            self.assertEqual(metadata["pid"], os.getpid())
            self.assertEqual(metadata["owner"], "test-owner")
            self.assertEqual(metadata["job"], "cpu-fixture")
            self.assertEqual(metadata["run_id"], "test-run")
            self.assertTrue(metadata["host"])
            self.assertGreaterEqual(metadata["heartbeat_at"], metadata["acquired_at"])
            self.assertEqual(json.loads(lease.metadata_path.read_text()), metadata)
            inode = lease.lock_path.stat().st_ino
        self.assertEqual(json.loads(lease.metadata_path.read_text())["status"], "released")
        with self.assertRaises(RuntimeError):
            lease.heartbeat()
        with self.lease() as next_lease:
            self.assertEqual(next_lease.lock_path.stat().st_ino, inode)

    def test_stale_heartbeat_never_overrides_process_lock(self):
        with self.lease() as lease:
            metadata = json.loads(lease.metadata_path.read_text())
            metadata["heartbeat_at"] = "1970-01-01T00:00:00+00:00"
            lease.metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(LeaseBusyError):
                with self.lease():
                    self.fail("second lease acquired")
            result = self.child("""
import sys
from shortcut_study.runtime import GpuLease, LeaseBusyError
try:
    with GpuLease(sys.argv[1], owner='child', job='fixture', run_id='child'):
        sys.exit(3)
except LeaseBusyError:
    sys.exit(0)
""")
            self.assertEqual(result.returncode, 0, result.stderr)
            lease.assert_held()

    def test_abrupt_process_exit_releases_kernel_lease(self):
        result = self.child("""
import os, sys
from shortcut_study.runtime import GpuLease
lease = GpuLease(sys.argv[1], owner='child', job='fixture', run_id='child')
lease.__enter__()
os._exit(0)
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        lease = self.lease()
        self.assertEqual(json.loads(lease.metadata_path.read_text())["status"], "held")
        with lease:
            lease.assert_held()

    def test_exception_releases_and_metadata_failure_does_not_leak_lock(self):
        lease = self.lease()
        with self.assertRaisesRegex(ValueError, "fixture"):
            with lease:
                raise ValueError("fixture")
        broken = self.lease()
        with patch.object(broken, "_save_metadata", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                broken.__enter__()
        with self.lease() as next_lease:
            next_lease.assert_held()

    @unittest.skipUnless(hasattr(os, "fork"), "requires Linux fork")
    def test_fork_does_not_inherit_lease_authority_or_release_parent(self):
        with self.lease() as lease:
            child_pid = os.fork()
            if child_pid == 0:
                try:
                    lease.assert_held()
                except RuntimeError:
                    os._exit(0)
                os._exit(3)
            _, status = os.waitpid(child_pid, 0)
            self.assertEqual(os.waitstatus_to_exitcode(status), 0)
            lease.assert_held()
            with self.assertRaises(LeaseBusyError):
                with self.lease():
                    self.fail("fork released parent's lock")

    def test_real_git_common_dir_resolution_shares_primary_lock(self):
        # Minimal valid Git metadata, without committing or touching the project
        # repository. Exercise actual rev-parse for a linked worktree.
        primary, linked = self.root / "primary", self.root / "linked"
        common = primary / ".git"
        (common / "objects").mkdir(parents=True)
        (common / "refs").mkdir()
        (common / "HEAD").write_text("ref: refs/heads/main\n")
        (common / "config").write_text("[core]\nrepositoryformatversion = 0\nbare = false\n")
        linked.mkdir()
        administrative = common / "worktrees/linked"
        administrative.mkdir(parents=True)
        (administrative / "HEAD").write_text("ref: refs/heads/linked\n")
        (administrative / "commondir").write_text("../..\n")
        (administrative / "gitdir").write_text(str(linked / ".git") + "\n")
        (linked / ".git").write_text("gitdir: " + str(administrative) + "\n")
        self.assertEqual(resolve_canonical_checkout(linked), primary)
        self.assertEqual(resolve_canonical_checkout(primary), primary)
        with self.lease(primary) as lease:
            linked_lease = self.lease(linked)
            self.assertEqual(linked_lease.lock_path, lease.lock_path)
            with self.assertRaises(LeaseBusyError):
                with linked_lease:
                    self.fail("linked worktree acquired duplicate lock")

    @patch("shortcut_study.runtime.lease.shutil.which", return_value="/usr/bin/nvidia-smi")
    def test_gpu_query_rejects_missing_wrong_and_multiple_devices(self, which):
        with patch("shortcut_study.runtime.lease.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaises(RuntimeError):
                assert_supported_gpu()
        for output in ("", "NVIDIA A100, GPU-1, 40960\n",
                       "NVIDIA GeForce RTX 3070 Ti, GPU-1, 4096\n",
                       "NVIDIA GeForce RTX 3070 Ti, GPU-1, 8192\n" * 2):
            with self.subTest(output=output), patch("shortcut_study.runtime.lease.subprocess.run",
                                                   return_value=subprocess.CompletedProcess([], 0, output)):
                with self.assertRaises(RuntimeError):
                    assert_supported_gpu()

    @patch("shortcut_study.runtime.lease.shutil.which", return_value="/usr/bin/nvidia-smi")
    def test_gpu_query_returns_supported_identity_without_starting_workload(self, which):
        result = subprocess.CompletedProcess([], 0, "NVIDIA GeForce RTX 3070 Ti, GPU-fixture, 8192\n")
        with patch("shortcut_study.runtime.lease.subprocess.run", return_value=result) as query:
            self.assertEqual(assert_supported_gpu(), {"name": "NVIDIA GeForce RTX 3070 Ti",
                                                      "uuid": "GPU-fixture", "memory_total_mib": 8192})
        which.assert_called_once_with("nvidia-smi")
        self.assertEqual(query.call_args.args[0], ["/usr/bin/nvidia-smi", "--query-gpu=name,uuid,memory.total",
                                                 "--format=csv,noheader,nounits"])

    @patch("shortcut_study.runtime.lease.shutil.which", return_value=None)
    def test_gpu_query_uses_only_executable_fixed_wsl_fallback(self, which):
        result = subprocess.CompletedProcess([], 0, "NVIDIA GeForce RTX 3070 Ti, GPU-fixture, 8192\n")
        for is_file, executable in ((True, True), (False, True), (True, False)):
            with self.subTest(is_file=is_file, executable=executable), \
                    patch("shortcut_study.runtime.lease.Path.is_file", return_value=is_file), \
                    patch("shortcut_study.runtime.lease.os.access", return_value=executable) as access, \
                    patch("shortcut_study.runtime.lease.subprocess.run", return_value=result) as query:
                if is_file and executable:
                    self.assertEqual(assert_supported_gpu()["uuid"], "GPU-fixture")
                    self.assertEqual(query.call_args.args[0][0], "/usr/lib/wsl/lib/nvidia-smi")
                    access.assert_called_once_with(Path("/usr/lib/wsl/lib/nvidia-smi"), os.X_OK)
                else:
                    with self.assertRaises(RuntimeError):
                        assert_supported_gpu()
                    query.assert_not_called()


if __name__ == "__main__":
    unittest.main()
