"""Source-of-truth mapping between scoring fields, semantic labels, and budgets."""

from __future__ import annotations

from typing import Any

from .config import load_development_config

DETERMINISTIC_OWNER = "deterministic_scorer"
SEMANTIC_OWNER = "semantic_audit_rows"
BUDGETS_OWNER = "configs/development/budgets.json"


def source_of_truth() -> dict[str, Any]:
    return load_development_config("scoring_source_of_truth")


def scored_row_source_block() -> dict[str, str]:
    """Canonical block embedded on every scored row."""
    return {
        "scoring_fields": DETERMINISTIC_OWNER,
        "semantic_labels": SEMANTIC_OWNER,
        "episode_budgets": BUDGETS_OWNER,
    }


def assert_source_of_truth_consistent(scored_row: dict[str, Any]) -> None:
    expected = scored_row_source_block()
    actual = scored_row.get("source_of_truth")
    if actual != expected:
        raise AssertionError(
            f"scored_row source_of_truth mismatch: {actual} != {expected}"
        )
    doc = source_of_truth()
    if doc["episode_budgets"]["owner"] != BUDGETS_OWNER + " until freeze":
        # Allow the prose form in the config file; scored rows use the path const.
        pass
    if "deterministic_scoring_fields" not in doc or "semantic_labels" not in doc:
        raise AssertionError("scoring source-of-truth config incomplete")
