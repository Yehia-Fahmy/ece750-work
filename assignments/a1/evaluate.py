"""Compute the assignment's three metrics from a run's saved test predictions."""
import argparse
import json
from pathlib import Path
import numpy as np
import student


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    with np.load(args.run / "test.npz", allow_pickle=False) as d:
        result = student.metrics(d["y"], d["score"], d["a"])
    text = json.dumps(result, indent=2, allow_nan=False)
    (args.run / "test-metrics.json").write_text(text + "\n")
    print(text)
