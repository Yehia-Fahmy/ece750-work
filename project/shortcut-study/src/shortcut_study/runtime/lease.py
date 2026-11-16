"""One OS-held GPU lease shared by the primary checkout and its worktrees."""

from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import weakref


class LeaseBusyError(RuntimeError):
    """Another process holds the lease; stale metadata never permits takeover."""


def resolve_canonical_checkout(checkout):
    """Resolve standard Git worktrees to their common primary checkout.

    Non-Git paths support explicitly shared roots and CPU test fixtures. A
    nonstandard Git common directory is rejected rather than guessing a root.
    """
    checkout = Path(checkout).resolve(strict=True)
    if not checkout.is_dir():
        raise ValueError("checkout must be a directory")
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, text=True, timeout=10, check=False,
    )
    if result.returncode:
        if "not a git repository" in result.stderr:
            return checkout
        raise RuntimeError("cannot resolve canonical Git checkout: " + result.stderr.strip())
    common = Path(result.stdout.strip()).resolve(strict=True)
    if common.name != ".git":
        raise ValueError("unsupported Git common directory; use the canonical standard checkout")
    return common.parent


def assert_supported_gpu():
    """Read GPU identity only; never starts a server or allocates GPU memory."""
    try:
        executable = shutil.which("nvidia-smi")
        if executable is None:
            fallback = Path("/usr/lib/wsl/lib/nvidia-smi")
            if not fallback.is_file() or not os.access(fallback, os.X_OK):
                raise FileNotFoundError("nvidia-smi is unavailable on PATH and at the fixed WSL location")
            executable = str(fallback)
        result = subprocess.run(
            [executable, "--query-gpu=name,uuid,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("local RTX 3070 Ti availability could not be verified") from exc
    rows = [line.strip().split(",") for line in result.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0]) != 3:
        raise RuntimeError("exactly one local RTX 3070 Ti must be visible")
    name, uuid, memory = (field.strip() for field in rows[0])
    try:
        memory_mib = int(memory)
    except ValueError as exc:
        raise RuntimeError("invalid GPU memory report") from exc
    if name != "NVIDIA GeForce RTX 3070 Ti" or not uuid or not 8000 <= memory_mib <= 8192:
        raise RuntimeError("unsupported GPU; this study permits only the 8 GB RTX 3070 Ti")
    return {"name": name, "uuid": uuid, "memory_total_mib": memory_mib}


_leases = weakref.WeakSet()


def _close_inherited_descriptors():
    # flock is tied to an open-file description. A forked child must not retain
    # its parent's lease or explicitly unlock that shared description.
    for lease in list(_leases):
        if lease._fd is not None:
            os.close(lease._fd)
            lease._fd = None
            lease._pid = None


os.register_at_fork(after_in_child=_close_inherited_descriptors)


class GpuLease:
    """Nonblocking exclusive lease; callers own starting/stopping their jobs.

    ``gpu.lock`` is never replaced or deleted. Metadata is independently atomic
    in ``gpu.lock.json`` and is diagnostic only; the kernel lock grants ownership.
    """

    def __init__(self, canonical_checkout, *, owner, job, run_id):
        for label, value in (("owner", owner), ("job", job), ("run_id", run_id)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} must be a nonempty string")
        self.canonical_checkout = resolve_canonical_checkout(canonical_checkout)
        self.lock_path = self.canonical_checkout / "project/runs/shortcut-study/gpu.lock"
        self.metadata_path = self.lock_path.with_suffix(".lock.json")
        self.owner, self.job, self.run_id = owner, job, run_id
        self._fd = None
        self._pid = None
        self._metadata = None
        _leases.add(self)

    def __enter__(self):
        if self._fd is not None:
            raise RuntimeError("lease is already entered")
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o600)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise LeaseBusyError(f"GPU lease is held: {self.lock_path}; inspect {self.metadata_path}") from exc
            self._fd, self._pid = descriptor, os.getpid()
            timestamp = datetime.now(timezone.utc).isoformat()
            self._metadata = {
                "schema_version": "shortcut-gpu-lease-v1", "owner": self.owner,
                "pid": self._pid, "host": socket.gethostname(), "job": self.job,
                "run_id": self.run_id, "canonical_checkout": str(self.canonical_checkout),
                "lock_path": str(self.lock_path), "acquired_at": timestamp,
                "heartbeat_at": timestamp, "status": "held",
            }
            self.heartbeat()
        except BaseException:
            os.close(descriptor)
            self._fd, self._pid = None, None
            raise
        return self

    def assert_held(self):
        if self._fd is None or self._pid != os.getpid():
            raise RuntimeError("GPU lease is not held by this process")
        current = self.lock_path.stat()
        held = os.fstat(self._fd)
        if (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino):
            raise RuntimeError("GPU lock file was replaced while held")

    def _save_metadata(self):
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.lock_path.parent,
                                             prefix=".gpu-metadata-", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(self._metadata, stream, sort_keys=True, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.metadata_path)
            directory_fd = os.open(self.lock_path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def heartbeat(self):
        self.assert_held()
        self._metadata["heartbeat_at"] = datetime.now(timezone.utc).isoformat()
        self._save_metadata()
        return dict(self._metadata)

    def __exit__(self, exc_type, exc_value, traceback):
        if self._fd is None:
            return False
        descriptor = self._fd
        try:
            if self._pid == os.getpid():
                self.assert_held()
                self._metadata["status"] = "released"
                self._metadata["released_at"] = datetime.now(timezone.utc).isoformat()
                self._save_metadata()
        finally:
            self._fd, self._pid = None, None
            # Closing releases this process's kernel lease. Never unlink the
            # stable lock inode, signal another PID, or use heartbeat age.
            os.close(descriptor)
        return False
