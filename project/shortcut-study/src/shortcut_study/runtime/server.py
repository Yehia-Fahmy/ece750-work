"""Owned, offline b11574 server lifecycle. Only the GPU operator may enter it."""

import ctypes
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import threading
import time

from .lease import GpuLease, assert_supported_gpu, resolve_canonical_checkout
from ..runner import write_new


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _environment(library_dirs):
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(("LLAMA_ARG_", "GGML_", "CUDA_"))
                   and key not in ("LD_LIBRARY_PATH", "LD_PRELOAD")}
    environment["LD_LIBRARY_PATH"] = ":".join(library_dirs)
    environment["CUDA_VISIBLE_DEVICES"] = "0"
    return environment


def inspect_local_assets(checkout, *, model_path=None, server_path=None):
    """Read/hash preserved assets and run version/help only; never load a model."""
    checkout = resolve_canonical_checkout(checkout)
    config = json.loads((checkout / "project/configs/main-reduced-v1.json").read_text())
    model_config = config["model"]
    runtime = (checkout / "project/tools/runtime").resolve(strict=True)
    model = Path(model_path or checkout / "project/models" / model_config["filename"]).resolve(strict=True)
    binary = Path(server_path or runtime / "llama-b11574/llama-server").resolve(strict=True)
    if not model.is_file() or not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError("local model and executable server are required")
    if model.stat().st_size != model_config["size_bytes"] or file_hash(model) != model_config["sha256"]:
        raise ValueError("preserved primary model does not match its pinned hash/size")
    libraries = sorted({p.resolve() for p in runtime.rglob("*.so*") if p.is_file()})
    library_dirs = sorted({str(p.parent) for p in runtime.rglob("*.so*") if p.is_file()})
    if Path("/usr/lib/wsl/lib").is_dir():
        library_dirs.append("/usr/lib/wsl/lib")
    environment = _environment(library_dirs)
    probes = {}
    for flag in ("--version", "--help"):
        result = subprocess.run([str(binary), flag], env=environment, capture_output=True,
                                text=True, timeout=20, check=True)
        probes[flag[2:]] = result.stdout + result.stderr
    if "build 11574" not in probes["version"] or "commit 8bb3cf0d2" not in probes["version"]:
        raise ValueError("this launch profile requires the retained b11574 runtime")
    for flag in ("--offline", "--fit", "--no-warmup", "--no-webui", "--no-context-shift",
                 "--reasoning-format", "--reasoning-budget", "--flash-attn", "--verbosity", "--log-colors"):
        if flag not in probes["help"]:
            raise ValueError(f"runtime lacks required flag {flag}")
    return {"schema_version": "shortcut-local-assets-v1", "canonical_checkout": str(checkout),
            "model_path": str(model), "model_sha256": model_config["sha256"],
            "model_size_bytes": model.stat().st_size, "checkpoint_revision": model_config["revision"],
            "quantization": "Q4_K_M", "server_path": str(binary), "library_dirs": library_dirs,
            "runtime_files_sha256": {str(p): file_hash(p) for p in [binary, *libraries]},
            "runtime_revision": "b11574-8bb3cf0d2", **probes}


def _canonical_checkout():
    return resolve_canonical_checkout(Path(__file__).resolve().parents[5])


def _owns_listener(pid, port):
    """Bind readiness to the launched PID, not a competing loopback service."""
    endpoint = f"0100007F:{port:04X}"
    inodes = {line.split()[9] for line in Path("/proc/net/tcp").read_text().splitlines()[1:]
              if line.split()[1] == endpoint and line.split()[3] == "0A"}
    for descriptor in (Path("/proc") / str(pid) / "fd").iterdir():
        try:
            target = os.readlink(descriptor)
        except FileNotFoundError:
            continue
        if target.startswith("socket:[") and target[8:-1] in inodes:
            return True
    return False


def _get_json(port, route, timeout):
    if route not in ("/health", "/props"):
        raise ValueError("only fixed read-only readiness routes are supported")
    deadline = time.monotonic() + timeout
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    timer = response = None
    try:
        connection.connect()
        sock = connection.sock
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("readiness connect exceeded deadline")
        sock.settimeout(remaining)

        def expire():
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

        timer = threading.Timer(remaining, expire)
        timer.daemon = True
        timer.start()
        connection.request("GET", route, headers={"Connection": "close"})
        response = connection.getresponse()
        chunks, size = [], 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("readiness response exceeded deadline")
            chunk = response.read1(min(65536, 2_097_153 - size))
            if not chunk:
                if isinstance(response.length, int) and response.length > 0:
                    raise http.client.IncompleteRead(b"".join(chunks), response.length)
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > 2_097_152:
                raise ValueError("server metadata exceeds byte limit")
        if time.monotonic() >= deadline:
            raise TimeoutError("readiness response exceeded deadline")
        body = b"".join(chunks)
        return response.status, json.loads(body)
    finally:
        if timer is not None:
            timer.cancel()
        if response is not None:
            response.close()
        connection.close()


class LocalLlamaServer:
    def __init__(self, lease, *, assets, directory, port=18080, alias="shortcut-qwen3-4b", startup_timeout=120):
        if type(port) is not int or not 1024 <= port <= 65535:
            raise ValueError("an explicit unprivileged loopback port is required")
        if not isinstance(alias, str) or re.fullmatch(r"[A-Za-z0-9_.-]+", alias) is None:
            raise ValueError("invalid local model alias")
        if type(startup_timeout) not in (int, float) or not 0 < startup_timeout <= 600:
            raise ValueError("startup timeout must be within 0..600 seconds")
        self.lease, self.assets, self.directory = lease, json.loads(json.dumps(assets)), Path(directory)
        self.port, self.alias, self.startup_timeout = port, alias, startup_timeout
        self.base_url = f"http://127.0.0.1:{port}"
        self.process = self._log = None
        self.props = self.profile = self.manifest = None

    def command(self):
        return [self.assets["server_path"], "--model", self.assets["model_path"], "--alias", self.alias,
                "--host", "127.0.0.1", "--port", str(self.port), "--ctx-size", "16384",
                "--n-gpu-layers", "999", "--device", "CUDA0", "--parallel", "1", "--jinja",
                "--reasoning", "on", "--reasoning-format", "deepseek", "--reasoning-budget", "-1",
                "--flash-attn", "on", "--no-context-shift", "--fit", "off", "--offline",
                "--no-webui", "--no-warmup", "--verbosity", "5", "--log-colors", "off",
                "--temp", "0.6", "--top-p", "0.95",
                "--top-k", "20", "--min-p", "0.0", "--repeat-penalty", "1.0",
                "--presence-penalty", "0.0", "--frequency-penalty", "0.0"]

    def __enter__(self):
        if self.process is not None:
            raise RuntimeError("server context cannot be entered twice")
        if not isinstance(self.lease, GpuLease) or self.lease.canonical_checkout != _canonical_checkout():
            raise ValueError("server requires this repository's canonical GPU lease")
        self.lease.assert_held()
        if Path(self.assets["canonical_checkout"]) != self.lease.canonical_checkout:
            raise ValueError("asset manifest belongs to another checkout")
        for path, expected in self.assets["runtime_files_sha256"].items():
            if file_hash(path) != expected:
                raise ValueError("runtime asset changed after inspection")
        if file_hash(self.assets["model_path"]) != self.assets["model_sha256"]:
            raise ValueError("model asset changed after inspection")
        gpu = assert_supported_gpu()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", self.port))  # refuse any preexisting listener
        self.directory.mkdir(parents=True, exist_ok=False)
        environment = _environment(self.assets["library_dirs"])
        environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
        command = self.command()
        self.manifest = {"schema_version": "shortcut-owned-server-v1", "assets": self.assets,
                         "command": command, "gpu": gpu, "parent_pid": os.getpid(),
                         "environment": {k: environment[k] for k in ("LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES", "PYTHONPATH")},
                         "parent_death_policy": "Linux PR_SET_PDEATHSIG SIGKILL before exec"}
        write_new(self.directory / "launch.json", self.manifest)
        self._log = (self.directory / "server.log").open("xb", buffering=0)
        try:
            # A fresh Python child sets parent-death protection before exec,
            # avoiding preexec_fn in a potentially multithreaded orchestrator.
            self.process = subprocess.Popen(
                [sys.executable, "-m", "shortcut_study.runtime.server", "--owned-child", str(os.getpid()), *command],
                env=environment, stdin=subprocess.DEVNULL, stdout=self._log, stderr=subprocess.STDOUT,
                close_fds=True, start_new_session=True,
            )
            write_new(self.directory / "process.json", {"pid": self.process.pid})
            deadline = time.monotonic() + self.startup_timeout
            while time.monotonic() < deadline:
                self.lease.heartbeat()
                if self.process.poll() is not None:
                    raise RuntimeError("owned server exited before readiness; inspect server.log")
                try:
                    if _owns_listener(self.process.pid, self.port):
                        status, health = _get_json(self.port, "/health", min(2, max(.01, deadline - time.monotonic())))
                        if status == 200 and health.get("status") == "ok":
                            status, self.props = _get_json(self.port, "/props", min(2, max(.01, deadline - time.monotonic())))
                            if status != 200:
                                raise ValueError("owned server props unavailable")
                            break
                except (ConnectionError, TimeoutError, FileNotFoundError):
                    pass
                time.sleep(.1)
            else:
                raise TimeoutError("owned server readiness deadline exceeded")
            self.assert_ready()
            write_new(self.directory / "props.json", self.props)
            template = self.props.get("chat_template")
            if (self.props.get("model_alias") != self.alias
                    or Path(self.props.get("model_path", "")).resolve() != Path(self.assets["model_path"])
                    or not isinstance(template, str) or not template):
                raise ValueError("server props do not match the launched model/template")
            defaults = self.props.get("default_generation_settings", {})
            if defaults.get("n_ctx") != 16384 or self.props.get("total_slots") != 1:
                raise ValueError("server did not retain single-slot 16k context")
            log = (self.directory / "server.log").read_text(errors="replace")
            offloads = re.findall(r"offloaded (\d+)/(\d+) layers to GPU", log)
            if not offloads or any(int(a) != int(b) or int(b) < 1 for a, b in offloads):
                raise ValueError("full GPU offload is not established by startup logs")
            tool_template = self.props.get("chat_template_tool_use")
            if tool_template is not None and not isinstance(tool_template, str):
                raise ValueError("invalid server tool template")
            selected_template = tool_template or template
            self.profile = {"checkpoint_revision": self.assets["checkpoint_revision"],
                            "checkpoint_sha256": self.assets["model_sha256"], "quantization": self.assets["quantization"],
                            "runtime_revision": self.assets["runtime_revision"],
                            "template_sha256": hashlib.sha256(selected_template.encode("utf-8")).hexdigest()}
            write_new(self.directory / "ready.json", {"pid": self.process.pid, "profile": self.profile,
                                                      "full_offload_layers": offloads,
                                                      "selected_template": "chat_template_tool_use" if tool_template else "chat_template",
                                                      "base_template_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
                                                      "tool_template_sha256": hashlib.sha256(tool_template.encode("utf-8")).hexdigest() if tool_template else None})
            return self
        except BaseException:
            self.close()
            raise

    def assert_ready(self):
        self.lease.assert_held()
        if self.process is None or self.process.poll() is not None or not _owns_listener(self.process.pid, self.port):
            raise RuntimeError("owned server is not alive and listening on its assigned port")

    def close(self):
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=10)
                path = self.directory / "stopped.json"
                if not path.exists():
                    write_new(path, {"pid": self.process.pid, "returncode": self.process.poll()})
        finally:
            if self._log is not None:
                self._log.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


def _owned_child(parent_pid, command):
    # Linux-only, fail closed. Parent death between Popen and prctl is detected
    # by the second getppid check. exec preserves the configured death signal.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "cannot establish parent-death protection")
    if os.getppid() != parent_pid:
        raise RuntimeError("owning parent exited before server launch")
    os.execve(command[0], command, os.environ)


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] != "--owned-child":
        raise SystemExit("internal owned-child launcher only")
    _owned_child(int(sys.argv[2]), sys.argv[3:])
