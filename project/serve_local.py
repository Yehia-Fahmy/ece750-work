"""Start the pinned local llama.cpp server with the draft smoke-test settings."""

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/smoke.json")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    runtime = ROOT / "tools/runtime"
    binaries = list(runtime.rglob("llama-server"))
    if len(binaries) != 1:
        parser.error("Expected one llama-server binary; run bootstrap_local.py first")
    binary = binaries[0].resolve()
    model = ROOT / "models" / config["model"]["filename"]
    if not model.exists():
        parser.error("Model weights are absent; run bootstrap_local.py first")
    library_dirs = {str(path.parent) for path in runtime.rglob("*.so*")}
    environment = dict(os.environ)
    environment["LD_LIBRARY_PATH"] = ":".join(sorted(library_dirs)) + ":" + environment.get("LD_LIBRARY_PATH", "")
    command = [str(binary), "--model", str(model), "--alias", config["model"]["alias"],
               "--ctx-size", str(config["context_tokens"]), "--n-gpu-layers", "99",
               "--parallel", "1", "--jinja", "--reasoning", "on", "--reasoning-format", "deepseek",
               "--reasoning-budget", "-1", "--flash-attn", "on", "--no-context-shift",
               "--host", "127.0.0.1", "--port", str(args.port)]
    print("Starting local server:", json.dumps(command), flush=True)
    os.execve(binary, command, environment)


if __name__ == "__main__":
    main()
