"""Fixed data split and preprocessing supplied by the instructor."""
from pathlib import Path
import hashlib
import numpy as np

DATA = Path(__file__).resolve().parent / "data"
SHA256 = {
    "adult_headers.txt": "7dbc74c3f61661803197d4c3fa5e25b1a402648f1fc8390b2e1bd5bcf330214e",
    "adult_train.npz": "80f337f7c8398521f43c043d51e7648f58a6d9fa03368ac401ca88570912d38b",
    "adult_test.npz": "f6d9b03c308a2383d1a48a0ee8f81c8783f0cdccc008ce23685b5bb5300977de",
}


def read_original(filename):
    path = DATA / filename
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256[filename]:
        raise ValueError(f"Unexpected data file: {path}")
    with np.load(path, allow_pickle=False) as d:
        x, y, a = d["x"], d["y"].ravel(), d["a"].ravel()
    header_path = DATA / "adult_headers.txt"
    if hashlib.sha256(header_path.read_bytes()).hexdigest() != SHA256["adult_headers.txt"]:
        raise ValueError("Unexpected feature header file")
    names = header_path.read_text().splitlines()
    assert len(names) == x.shape[1] + 1 and names[-1] == "income"
    names = np.asarray(names[:-1])
    assert np.array_equal(a, x[:, np.flatnonzero(names == "sex_Male")[0]])
    assert np.array_equal(1 - a, x[:, np.flatnonzero(names == "sex_Female")[0]])
    assert set(np.unique(y)) <= {0, 1} and set(np.unique(a)) <= {0, 1}
    keep = ~np.isin(names, ["sex_Female", "sex_Male"])
    return x[:, keep], y, a, names[keep]


def load_data(include_test=True):
    """Return the original train/test splits and training-only preprocessing.

    Each split contains x, raw_x, y, a, and original row ids. Set include_test
    to False to load training data only.
    """
    x, y, a, names = read_original("adult_train.npz")
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1

    def pack(raw, labels, groups):
        return dict(x=((raw - mean) / scale).astype(np.float32), raw_x=raw,
                    y=labels.astype(np.float32), a=groups.astype(np.int64),
                    ids=np.arange(len(labels)))

    splits = {"train": pack(x, y, a)}
    if include_test:
        tx, ty, ta, tn = read_original("adult_test.npz")
        assert np.array_equal(names, tn)
        splits["test"] = pack(tx, ty, ta)
    return splits, dict(names=names, mean=mean, scale=scale)


if __name__ == "__main__":
    splits, prep = load_data()
    print(f"Model features: {len(prep['names'])}; A=0: Female; A=1: Male")
    for name, split in splits.items():
        print(name, len(split["y"]), "rows")
