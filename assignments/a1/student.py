"""Complete these three functions. See the handout for definitions."""
import numpy as np
import torch


def correlations(x: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Return signed Pearson correlations, one per column of x.

    x has shape (n, d); target has shape (n,). Return shape (d,).
    Return np.nan for a constant feature or constant target. Rank by absolute
    correlation outside this function, breaking ties by feature-column index.
    """
    x = np.asarray(x, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64).reshape(-1)
    x_c = x - x.mean(axis=0)
    t_c = target - target.mean()
    x_norm = np.sqrt(np.sum(x_c * x_c, axis=0))
    t_norm = np.sqrt(np.sum(t_c * t_c))
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = (x_c.T @ t_c) / (x_norm * t_norm)
    corr[~np.isfinite(corr)] = np.nan
    return corr


def _mean_or_none(values):
    if len(values) == 0:
        return None
    return float(np.mean(values))


def metrics(y: np.ndarray, score: np.ndarray, a: np.ndarray) -> dict:
    """Compute metrics over a complete split, using prediction = score >= 0.5.

    All inputs have shape (n,). Return a JSON-serializable dictionary:
      accuracy, rw_accuracy, dp_gap,
      groups: {'0': {n, accuracy, positive_rate},
               '1': {n, accuracy, positive_rate}}.
    Use None for undefined rates and any gap or average depending on one.
    Counts must be Python ints; defined rates must be Python floats.
    Do not average batch-level metrics.
    """
    y = np.asarray(y).reshape(-1)
    score = np.asarray(score).reshape(-1)
    a = np.asarray(a).reshape(-1)
    pred = score >= 0.5
    correct = pred == y

    groups = {}
    accs, rates = [], []
    for g in (0, 1):
        mask = a == g
        n = int(np.sum(mask))
        acc = _mean_or_none(correct[mask])
        rate = _mean_or_none(pred[mask])
        groups[str(g)] = {"n": n, "accuracy": acc, "positive_rate": rate}
        accs.append(acc)
        rates.append(rate)

    return {
        "accuracy": _mean_or_none(correct),
        "rw_accuracy": None if None in accs else float(0.5 * (accs[0] + accs[1])),
        "dp_gap": None if None in rates else float(abs(rates[0] - rates[1])),
        "groups": groups,
    }


def dp_penalty(score: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    """Return a differentiable scalar penalty; score and a have shape (batch,).

    score contains sigmoid probabilities, not logits or thresholded labels.
    Choose and explain your penalty in Question 1.4. The caller handles batches
    missing a group; you may assume both groups are present here.
    """
    score = score.reshape(-1)
    a = a.reshape(-1)
    return (score[a == 0].mean() - score[a == 1].mean()).square()
