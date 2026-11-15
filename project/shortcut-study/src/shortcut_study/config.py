"""Load provisional development configs."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from .paths import DEVELOPMENT_CONFIGS_DIR

CONFIG_FILES = {
    "visibility": "visibility.json",
    "policy": "policy.json",
    "budgets": "budgets.json",
    "a_t_j_boundaries": "a_t_j_boundaries.json",
    "splits": "splits.json",
    "scoring_source_of_truth": "scoring_source_of_truth.json",
    "vertical_slice": "vertical_slice.json",
}


@lru_cache(maxsize=None)
def load_development_config(name: str) -> dict[str, Any]:
    if name not in CONFIG_FILES:
        raise KeyError(f"unknown development config: {name}")
    path = DEVELOPMENT_CONFIGS_DIR / CONFIG_FILES[name]
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def policy_matrix_rows() -> list[dict[str, Any]]:
    return list(load_development_config("policy")["policy_information_state_matrix"]["rows"])
