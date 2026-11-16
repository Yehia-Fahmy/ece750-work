"""Owned-server CPU fixtures. No model or GPU server is launched."""

import hashlib
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from shortcut_study.runtime import GpuLease
import shortcut_study.runtime.server as server


class LocalServerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.binary, self.model = self.root / "server", self.root / "model.gguf"
        self.binary.write_bytes(b"synthetic executable")
        self.binary.chmod(0o700)
        self.model.write_bytes(b"synthetic model")
        self.assets = {"canonical_checkout": str(self.root), "server_path": str(self.binary),
                       "model_path": str(self.model), "model_sha256": server.file_hash(self.model),
                       "runtime_files_sha256": {str(self.binary): server.file_hash(self.binary)},
                       "checkpoint_revision": "fixture", "quantization": "fixture",
                       "runtime_revision": "fixture", "library_dirs": [str(self.root)]}
        self.lease = GpuLease(self.root, owner="test", job="cpu", run_id="test")
        self.lease.__enter__()
        self.addCleanup(self.lease.__exit__, None, None, None)
        self.owns_listener = server._owns_listener
        for name, value in (("_canonical_checkout", self.root), ("assert_supported_gpu", {"fixture": True}),
                            ("_owns_listener", True)):
            item = patch.object(server, name, return_value=value)
            item.start()
            self.addCleanup(item.stop)
        self.props = {"model_alias": "shortcut-qwen3-4b", "model_path": str(self.model),
                      "chat_template": "fixture template", "default_generation_settings": {"n_ctx": 16384},
                      "total_slots": 1}
        self.process = MagicMock(pid=1234)
        self.process.poll.return_value = None
        self.process.wait.side_effect = lambda **kwargs: setattr(self.process.poll, "return_value", -15)

    def launch(self, directory="run"):
        return server.LocalLlamaServer(self.lease, assets=self.assets, directory=self.root / directory)

    def fake_popen(self, command, **kwargs):
        kwargs["stdout"].write(b"llama_model_load: offloaded 37/37 layers to GPU\n")
        return self.process

    def patches(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch.object(server.socket, "socket"))
        stack.enter_context(patch.object(server.subprocess, "Popen", side_effect=self.fake_popen))
        stack.enter_context(patch.object(server, "_get_json", side_effect=[(200, {"status": "ok"}), (200, self.props)]))
        return stack

    def test_fixed_launch_identity_log_props_and_owned_cleanup(self):
        with self.patches(), self.launch() as owned:
            owned.assert_ready()
            self.assertEqual(owned.profile["checkpoint_sha256"], self.assets["model_sha256"])
            self.assertEqual(owned.profile["template_sha256"], hashlib.sha256(b"fixture template").hexdigest())
            self.assertEqual(owned.props, self.props)
            command = owned.command()
            for flag in ("--offline", "--no-warmup", "--no-context-shift", "--no-webui"):
                self.assertIn(flag, command)
            for flag, value in (("--ctx-size", "16384"), ("--parallel", "1"), ("--n-gpu-layers", "999"),
                                ("--host", "127.0.0.1"), ("--fit", "off"), ("--device", "CUDA0"),
                                ("--verbosity", "5"), ("--log-colors", "off")):
                self.assertEqual(command[command.index(flag)+1], value)
            self.assertTrue((owned.directory / "ready.json").is_file())
        self.process.terminate.assert_called_once()
        self.process.kill.assert_not_called()
        self.assertEqual(json.loads((self.root / "run/stopped.json").read_text())["returncode"], -15)
        self.lease.assert_held()

    def test_asset_mutation_and_foreign_lease_refused_before_spawn(self):
        self.model.write_bytes(b"changed")
        with patch.object(server.subprocess, "Popen") as spawn, self.assertRaisesRegex(ValueError, "model asset"):
            self.launch().__enter__()
        spawn.assert_not_called()
        self.assertFalse((self.root / "run").exists())
        with patch.object(server, "_canonical_checkout", return_value=self.root / "elsewhere"), self.assertRaises(ValueError):
            self.launch().__enter__()

    def test_existing_port_refused_and_never_signalled(self):
        with patch.object(server.socket, "socket") as socket_class, patch.object(server.subprocess, "Popen") as spawn:
            socket_class.return_value.__enter__.return_value.bind.side_effect = OSError("occupied")
            with self.assertRaises(OSError):
                self.launch().__enter__()
            spawn.assert_not_called()
        self.process.terminate.assert_not_called()

    def test_wrong_props_stops_only_owned_process(self):
        self.props["total_slots"] = 2
        with self.patches(), self.assertRaisesRegex(ValueError, "single-slot"):
            self.launch().__enter__()
        self.process.terminate.assert_called_once()

    def test_partial_offload_is_rejected_and_owned_process_stopped(self):
        def partial(command, **kwargs):
            kwargs["stdout"].write(b"llama_model_load: offloaded 12/37 layers to GPU\n")
            return self.process
        with self.patches(), patch.object(server.subprocess, "Popen", side_effect=partial), \
                self.assertRaisesRegex(ValueError, "full GPU offload"):
            self.launch().__enter__()
        self.process.terminate.assert_called_once()

    def test_readiness_without_offload_diagnostics_remains_unverified(self):
        def quiet(command, **kwargs):
            kwargs["stdout"].write(b"verbosity = 3\nmodel loaded\nlistening on http://127.0.0.1:18080\n")
            return self.process
        with self.patches(), patch.object(server.subprocess, "Popen", side_effect=quiet), \
                self.assertRaisesRegex(ValueError, "full GPU offload is not established"):
            self.launch().__enter__()
        self.process.terminate.assert_called_once()
        self.assertTrue((self.root / "run/props.json").exists())
        self.assertFalse((self.root / "run/ready.json").exists())

    def test_profile_binds_effective_tool_template(self):
        self.props["chat_template_tool_use"] = "specific tool template"
        with self.patches(), self.launch() as owned:
            self.assertEqual(owned.profile["template_sha256"], hashlib.sha256(b"specific tool template").hexdigest())
            ready = json.loads((owned.directory / "ready.json").read_text())
            self.assertEqual(ready["selected_template"], "chat_template_tool_use")
            self.assertEqual(ready["base_template_sha256"], hashlib.sha256(b"fixture template").hexdigest())

    def test_listener_inode_belongs_to_current_process(self):
        # The sandbox disallows creating sockets; exercise /proc snapshots.
        snapshot = "header\n0: 0100007F:46A0 00000000:0000 0A 0 0 0 0 0 123456 0\n"
        with patch.object(server.Path, "read_text", return_value=snapshot), \
                patch.object(server.Path, "iterdir", return_value=iter([Path("/proc/1234/fd/3")])), \
                patch.object(server.os, "readlink", return_value="socket:[123456]"):
            self.assertTrue(self.owns_listener(1234, 18080))
        with patch.object(server.Path, "read_text", return_value=snapshot), \
                patch.object(server.Path, "iterdir", return_value=iter([Path("/proc/1234/fd/3")])), \
                patch.object(server.os, "readlink", return_value="socket:[999999]"):
            self.assertFalse(self.owns_listener(1234, 18080))

    def test_startup_exit_retains_failure_logs_without_signalling_dead_pid(self):
        self.process.poll.return_value = 2
        with self.patches(), self.assertRaisesRegex(RuntimeError, "exited before readiness"):
            self.launch().__enter__()
        self.process.terminate.assert_not_called()
        self.assertTrue((self.root / "run/server.log").exists())

    def test_slow_owned_shutdown_escalates_only_its_process(self):
        def wait(**kwargs):
            if self.process.wait.call_count == 1:
                raise subprocess.TimeoutExpired("fixture", 10)
            self.process.poll.return_value = -9
        self.process.wait.side_effect = wait
        with self.patches(), self.launch():
            pass
        self.process.terminate.assert_called_once()
        self.process.kill.assert_called_once()
        self.assertEqual(self.process.wait.call_count, 2)

    def test_launch_environment_cannot_inherit_model_or_sampling_overrides(self):
        with patch.dict(os.environ, {"LLAMA_ARG_MODEL_URL": "remote", "LD_PRELOAD": "unwanted",
                                     "GGML_CUDA_FORCE_MMQ": "1", "CUDA_VISIBLE_DEVICES": "3"}):
            environment = server._environment(["/fixed/libs"])
        self.assertNotIn("LLAMA_ARG_MODEL_URL", environment)
        self.assertNotIn("LD_PRELOAD", environment)
        self.assertNotIn("GGML_CUDA_FORCE_MMQ", environment)
        self.assertEqual(environment["CUDA_VISIBLE_DEVICES"], "0")
        self.assertEqual(environment["LD_LIBRARY_PATH"], "/fixed/libs")

    def test_inspection_hashes_assets_and_uses_only_version_help(self):
        runtime = self.root / "project/tools/runtime"
        runtime.mkdir(parents=True)
        config = self.root / "project/configs/main-reduced-v1.json"
        config.parent.mkdir()
        config.write_text(json.dumps({"model": {"filename": "fixture", "sha256": server.file_hash(self.model),
                                                "size_bytes": self.model.stat().st_size, "revision": "fixture"}}))
        help_text = "--offline --fit --no-warmup --no-webui --no-context-shift --reasoning-format --reasoning-budget --flash-attn --verbosity --log-colors"
        with patch.object(server.subprocess, "run", side_effect=[
                subprocess.CompletedProcess([], 0, "build 11574, commit 8bb3cf0d2", ""),
                subprocess.CompletedProcess([], 0, help_text, "")]) as probe, \
                patch.object(server, "resolve_canonical_checkout", return_value=self.root):
            assets = server.inspect_local_assets(self.root, model_path=self.model, server_path=self.binary)
        self.assertEqual(assets["model_sha256"], server.file_hash(self.model))
        self.assertEqual([call.args[0][1] for call in probe.call_args_list], ["--version", "--help"])

    def test_parent_death_protection_applies_before_exec_and_rejects_lost_parent(self):
        libc = MagicMock()
        libc.prctl.return_value = 0
        with patch.object(server.ctypes, "CDLL", return_value=libc), \
                patch.object(server.os, "getppid", return_value=99), patch.object(server.os, "execve") as execute:
            server._owned_child(99, ["/fixture/server", "--offline"])
            libc.prctl.assert_called_once_with(1, server.signal.SIGKILL, 0, 0, 0)
            execute.assert_called_once()
            execute.reset_mock()
            with self.assertRaises(RuntimeError):
                server._owned_child(98, ["/fixture/server"])
            execute.assert_not_called()

    def test_parent_death_stops_cpu_child_after_exec(self):
        marker = self.root / "cpu-child-ready"
        child = "from pathlib import Path; import sys,time; Path(sys.argv[1]).write_text('ready'); time.sleep(4)"
        parent = """
import os, pathlib, subprocess, sys, time
marker = pathlib.Path(sys.argv[1])
p = subprocess.Popen([sys.executable, '-m', 'shortcut_study.runtime.server', '--owned-child', str(os.getpid()), sys.executable, '-c', sys.argv[2], str(marker)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
deadline = time.monotonic() + 3
while not marker.exists() and p.poll() is None and time.monotonic() < deadline:
    time.sleep(.01)
print(p.pid, flush=True)
os._exit(0 if marker.exists() else 1)
"""
        result = subprocess.run([sys.executable, "-c", parent, str(marker), child],
                                capture_output=True, text=True, timeout=5, check=True)
        child_pid = int(result.stdout.strip())
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            status = Path(f"/proc/{child_pid}/stat")
            if not status.exists() or status.read_text().split()[2] == "Z":
                break
            time.sleep(.01)
        else:
            self.fail("CPU child remained alive after owner exit")

    @patch("shortcut_study.runtime.server.threading.Timer")
    @patch("shortcut_study.runtime.server.http.client.HTTPConnection")
    def test_readiness_rejects_incomplete_body_even_if_json_prefix_valid(self, connection, timer):
        reply = connection.return_value.getresponse.return_value
        reply.status, reply.length = 200, 5
        reply.read1.side_effect = [b'{"status":"ok"}', b'']
        with self.assertRaises(http.client.IncompleteRead):
            server._get_json(18080, "/health", 2)
        timer.return_value.cancel.assert_called_once()
        connection.return_value.close.assert_called_once()

    @patch("shortcut_study.runtime.server.threading.Timer")
    @patch("shortcut_study.runtime.server.http.client.HTTPConnection")
    def test_readiness_absolute_deadline_interrupts_slow_headers(self, connection, timer):
        def delayed_headers():
            timer.call_args.args[1]()
            raise TimeoutError("fixture deadline")
        connection.return_value.getresponse.side_effect = delayed_headers
        with self.assertRaises(TimeoutError):
            server._get_json(18080, "/props", 2)
        connection.return_value.sock.shutdown.assert_called_once_with(server.socket.SHUT_RDWR)
        connection.return_value.sock.close.assert_called_once()
        with self.assertRaises(ValueError):
            server._get_json(18080, "/v1/chat/completions", 2)


if __name__ == "__main__":
    unittest.main()
