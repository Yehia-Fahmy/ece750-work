"""Enumerate the mandatory 16-episode vertical-slice assignment path."""

from __future__ import annotations

import json
from typing import Any

from .ids import make_episode_id
from .paths import DEVELOPMENT_CONFIGS_DIR


def load_vertical_slice_config() -> dict[str, Any]:
    path = DEVELOPMENT_CONFIGS_DIR / "vertical_slice.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def enumerate_vertical_slice_assignments(
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return 16 matched condition rows for one base scenario and one seed."""
    config = config or load_vertical_slice_config()
    base = config["base_scenario"]
    factorial = config["factorial"]
    rows: list[dict[str, Any]] = []
    for information_state in factorial["information_states"]:
        for shortcut_available in factorial["shortcut_available"]:
            for visibility in factorial["visibility"]:
                episode_id = make_episode_id(
                    base_id=base["base_id"],
                    information_state=information_state,
                    shortcut_available=shortcut_available,
                    visibility=visibility,
                    replicate_seed=base["replicate_seed"],
                )
                rows.append(
                    {
                        "episode_id": episode_id,
                        "base_id": base["base_id"],
                        "template_id": base["template_id"],
                        "family": base["family"],
                        "intended_difficulty": base["intended_difficulty"],
                        "mechanism": base["mechanism"],
                        "shortcut_resource_id": base["shortcut_resource_id"],
                        "policy_id": base["policy_id"],
                        "split": base["split"],
                        "generator_version": base["generator_version"],
                        "information_state": information_state,
                        "shortcut_available": shortcut_available,
                        "visibility": visibility,
                        "replicate_seed": base["replicate_seed"],
                    }
                )
    expected = config.get("episode_count", 16)
    if len(rows) != expected:
        raise AssertionError(
            f"vertical slice expected {expected} episodes, got {len(rows)}"
        )
    return rows


def vertical_slice_path_summary() -> dict[str, Any]:
    config = load_vertical_slice_config()
    assignments = enumerate_vertical_slice_assignments(config)
    return {
        "base_id": config["base_scenario"]["base_id"],
        "episode_count": len(assignments),
        "episode_ids": [row["episode_id"] for row in assignments],
        "required_demonstrations": config["required_demonstrations"],
        "consumer_packages": config["consumer_packages"],
        "mock_actor_first": True,
        "gpu_run_authorized": False,
    }
