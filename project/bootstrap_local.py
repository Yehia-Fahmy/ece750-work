"""Download pinned official GGUF weights and the Linux CUDA runtime locally."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import urllib.request


ROOT = Path(__file__).resolve().parent


def download(url, path, checksum, size):
    """Verify complete cached artifacts and atomically install new downloads."""
    if path.exists():
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        if path.stat().st_size == size and actual == checksum:
            print(f"Verified cached {path.name}", flush=True)
            return
        raise ValueError(f"Existing artifact failed verification: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    print(f"Downloading {path.name} ({size / 1e6:.0f} MB)", flush=True)
    hasher = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as handle:
        while block := response.read(4 * 1024 * 1024):
            hasher.update(block)
            handle.write(block)
    if temporary.stat().st_size != size or hasher.hexdigest() != checksum:
        raise ValueError(f"Downloaded artifact failed verification: {path}")
    temporary.replace(path)
    print(f"Verified download {path.name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/smoke.json")
    parser.add_argument("--model-only", action="store_true", help="Skip the Linux x86_64 CUDA runtime")
    parser.add_argument("--with-local-libgomp", action="store_true", help="Download/extract Ubuntu libgomp into tools without system installation")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    model = config["model"]
    model_url = f"https://huggingface.co/{model['repository']}/resolve/{model['revision']}/{model['filename']}"
    artifacts = [(model_url, ROOT / "models" / model["filename"], model["sha256"], model["size_bytes"])]
    metadata = {"model": model, "runtime": []}
    if not args.model_only:
        release = config["runtime_release"]
        url = f"https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/{release}"
        with urllib.request.urlopen(url, timeout=60) as response:
            info = json.load(response)
        names = (f"llama-{release}-bin-ubuntu-cuda-12.8-x64.tar.gz",
                 f"cudart-llama-{release}-bin-ubuntu-cuda-12.8-x64.tar.gz")
        for name in names:
            asset = next(item for item in info["assets"] if item["name"] == name)
            checksum = asset.get("digest", "")
            if not checksum.startswith("sha256:"):
                raise ValueError(f"Official release lacks checksum for {name}")
            artifacts.append((asset["browser_download_url"], ROOT / "tools" / name,
                              checksum.removeprefix("sha256:"), asset["size"]))
            metadata["runtime"].append({"release": release, "name": name, "sha256": checksum,
                                        "url": asset["browser_download_url"], "size_bytes": asset["size"]})
    with ThreadPoolExecutor(max_workers=len(artifacts)) as pool:
        futures = [pool.submit(download, *artifact) for artifact in artifacts]
        for future in futures:
            future.result()
    for _, path, _, _ in artifacts[1:]:
        with tarfile.open(path) as archive:
            archive.extractall(ROOT / "tools/runtime", filter="data")
    if args.with_local_libgomp:
        if args.model_only:
            parser.error("--with-local-libgomp requires the Linux runtime")
        listing = subprocess.check_output(["apt-get", "--print-uris", "download", "libgomp1"], text=True)
        match = re.search(r"'([^']+)'\s+(\S+)\s+(\d+)\s+SHA512:([0-9a-f]+)", listing)
        if match is None:
            raise ValueError("Ubuntu package cache lacks a checksum-verified libgomp1 download")
        package_url, name, size, checksum = match.groups()
        path = ROOT / "tools" / name
        if not path.exists():
            with urllib.request.urlopen(package_url.replace("http://", "https://", 1), timeout=60) as response:
                path.write_bytes(response.read())
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha512").hexdigest()
        if path.stat().st_size != int(size) or actual != checksum:
            raise ValueError("Local libgomp1 package failed its Ubuntu checksum")
        subprocess.run(["dpkg-deb", "--extract", str(path), str(ROOT / "tools/runtime/libgomp")], check=True)
        metadata["libgomp"] = {"filename": name, "url": package_url, "sha512": checksum}
    (ROOT / "models/setup.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print("Local model/runtime artifacts are ready. See project/README.md to start the server.", flush=True)


if __name__ == "__main__":
    main()
