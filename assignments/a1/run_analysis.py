"""Reproduce the Assignment 1 tables and plots from the fixed data and runs."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from data import load_data
from student import correlations, metrics
import train


RESULTS = Path(__file__).resolve().parent / "results"


def ranked(corr, names, k):
    valid = [i for i, value in enumerate(corr) if np.isfinite(value)]
    order = sorted(valid, key=lambda i: (-abs(float(corr[i])), i))
    return [
        {"feature": str(names[i]), "correlation": float(corr[i]), "index": int(i)}
        for i in order[:k]
    ]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def question_11():
    splits, prep = load_data(include_test=False)
    train_split = splits["train"]
    names = prep["names"]
    return {
        "y": ranked(correlations(train_split["raw_x"], train_split["y"]), names, 10),
        "a": ranked(correlations(train_split["raw_x"], train_split["a"]), names, 10),
    }


def question_13(run):
    splits, prep = load_data()
    test = splits["test"]
    with np.load(Path(run) / "test.npz", allow_pickle=False) as saved:
        if not np.array_equal(saved["ids"], test["ids"]):
            raise ValueError("Saved predictions are not aligned with the test split")
        prediction = (saved["score"] >= 0.5).astype(np.float64)
        groups = saved["a"]
    names = prep["names"]
    raw_x = test["raw_x"]
    return {
        "all": ranked(correlations(raw_x, prediction), names, 3),
        "a0": ranked(correlations(raw_x[groups == 0], prediction[groups == 0]), names, 3),
        "a1": ranked(correlations(raw_x[groups == 1], prediction[groups == 1]), names, 3),
    }


def training_metrics(run):
    """Score the training split with a saved model. This does not read test labels."""
    splits, prep = load_data(include_test=False)
    train_split = splits["train"]
    state = torch.load(Path(run) / "model.pt", map_location="cpu", weights_only=True)
    model = train.model_for(train_split["x"].shape[1])
    model.load_state_dict(state)
    score = train.predict(model, train_split["x"])
    result = metrics(train_split["y"], score, train_split["a"])
    result["alpha"] = json.loads((Path(run) / "config.json").read_text())["alpha"]
    return result


def test_metrics(runs):
    rows = []
    for run in runs:
        path = Path(run)
        result = json.loads((path / "test-metrics.json").read_text())
        result["alpha"] = json.loads((path / "config.json").read_text())["alpha"]
        rows.append(result)
    return sorted(rows, key=lambda row: row["alpha"])


def plot_metrics(rows):
    import matplotlib.pyplot as plt

    RESULTS.mkdir(parents=True, exist_ok=True)
    alpha = [row["alpha"] for row in rows]
    series = (
        ("accuracy", "Test accuracy", "q14_accuracy.png"),
        ("rw_accuracy", "Test reweighted accuracy", "q14_rw_accuracy.png"),
        ("dp_gap", r"Test $\Delta_{DP}$", "q14_dp_gap.png"),
    )
    for key, title, filename in series:
        figure, axis = plt.subplots(figsize=(5, 3.2))
        axis.plot(alpha, [row[key] for row in rows], marker="o")
        axis.set_xlabel(r"$\alpha$")
        axis.set_ylabel(title)
        axis.set_title(title)
        axis.grid(True, alpha=0.3)
        figure.tight_layout()
        figure.savefig(RESULTS / filename, dpi=200)
        plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q11", action="store_true")
    parser.add_argument("--q13", type=Path)
    parser.add_argument("--train-metrics", type=Path)
    parser.add_argument("--q14", nargs="+", type=Path)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.q11:
        value = question_11()
        write_json(RESULTS / "q11_correlations.json", value)
        print(json.dumps(value, indent=2))
    if args.q13:
        value = question_13(args.q13)
        write_json(RESULTS / "q13_correlations.json", value)
        print(json.dumps(value, indent=2))
    if args.train_metrics:
        print(json.dumps(training_metrics(args.train_metrics), indent=2))
    if args.q14:
        rows = test_metrics(args.q14)
        write_json(RESULTS / "q14_metrics.json", rows)
        plot_metrics(rows)
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
