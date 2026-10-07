"""Supplied CPU training loop. This runs at alpha=0 before completing student.py."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from data import load_data
import student


def model_for(n_features):
    return nn.Sequential(nn.Linear(n_features, 64), nn.ReLU(), nn.Linear(64, 1))


def predict(model, x):
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(torch.from_numpy(x)).squeeze(1)).numpy()


def save_predictions(path, model, split):
    np.savez_compressed(path, score=predict(model, split["x"]),
                        y=split["y"], a=split["a"], ids=split["ids"])


def run(alpha, seed, out):
    if not np.isfinite(alpha) or alpha < 0:
        raise ValueError("alpha must be finite and nonnegative")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    splits, prep = load_data()
    d = splits["train"]
    x = torch.from_numpy(d["x"])
    y = torch.from_numpy(d["y"])
    a = torch.from_numpy(d["a"])
    model = model_for(x.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    generator = torch.Generator().manual_seed(seed)
    start = time.perf_counter()
    history = []
    skipped = 0
    for epoch in range(10):
        model.train()
        loss_sum = 0.
        for ids in torch.randperm(len(y), generator=generator).split(256):
            logits = model(x[ids]).squeeze(1)
            loss = nn.functional.binary_cross_entropy_with_logits(logits, y[ids])
            if alpha > 0:
                if torch.unique(a[ids]).numel() == 2:
                    penalty = student.dp_penalty(torch.sigmoid(logits), a[ids])
                    if penalty.ndim != 0 or not torch.isfinite(penalty):
                        raise ValueError("Penalty must be a finite scalar")
                    loss = loss + alpha * penalty
                else:
                    skipped += 1  # Use classification loss alone for this batch.
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite training loss")
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_sum += loss.item() * len(ids)
        history.append(dict(epoch=epoch + 1, objective=loss_sum / len(y)))
    elapsed = time.perf_counter() - start
    torch.save(model.state_dict(), out / "model.pt")
    np.savez_compressed(out / "preprocessing.npz", **prep)
    save_predictions(out / "test.npz", model, splits["test"])
    config = dict(alpha=alpha, seed=seed, epochs=10, batch_size=256, lr=1e-3,
                  weight_decay=1e-5, hidden_units=64,
                  threshold=0.5, seconds=elapsed, skipped_penalty_batches=skipped,
                  numpy=np.__version__, torch=torch.__version__)
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (out / "history.json").write_text(json.dumps(history, indent=2) + "\n")
    print(f"Saved {out}: {elapsed:.2f}s; skipped penalty batches: {skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=0.)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run(args.alpha, args.seed, args.out)
