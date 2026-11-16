"""TAB catalog enumeration for S0 development and held-out split packaging."""

from ...ids import make_episode_id
from .common import (ALLOWED_MECHANISM, ALLOWED_POLICY, ALLOWED_SPLIT, CATALOG_VERSION, DIFFICULTIES,
                     GENERATOR_SPLITS, SHORTCUT, TAB01_SLICE_VERSION, generator_version_for)

TEMPLATES = ("TAB01", "TAB02", "TAB03", "TAB04", "TAB05")

# Stable scenario stems (not split-prefixed). Fingerprints come from generated worlds.
SCENARIO_STEMS = {
    "TAB01": "tab01-net-delivery",
    "TAB02": "tab02-invoice-recon",
    "TAB03": "tab03-stock-balance",
    "TAB04": "tab04-sla-totals",
    "TAB05": "tab05-defect-rate",
}

# Backward-compatible development base_id map used by older tests/docs.
BASE_SCENARIOS = {
    template_id: f"dev-{stem}" for template_id, stem in SCENARIO_STEMS.items()
}

# Disjoint generation-seed namespaces so identical template×difficulty worlds do not
# collide across splits (semantic_fingerprint ignores base_id).
SPLIT_SEED_BASE = {
    "smoke": 1_000,
    "development": 0,
    "qualification": 10_000,
    "main": 20_000,
}


def generation_seed_for(split: str, template_id: str, difficulty: str) -> int:
    """Return the reserved generation seed for one base in a split."""
    if split not in GENERATOR_SPLITS:
        raise ValueError(f"unknown split for generation seed: {split}")
    if template_id not in TEMPLATES:
        raise ValueError(f"unknown template_id: {template_id}")
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"unknown difficulty: {difficulty}")
    base = SPLIT_SEED_BASE[split]
    if split == "development":
        # Preserve the existing development catalog convention (single seed=0).
        return base
    return (
        base
        + TEMPLATES.index(template_id) * 100
        + DIFFICULTIES.index(difficulty) * 10
        + 1
    )


def base_id_for(split: str, template_id: str, difficulty: str, *, instance: int = 1) -> str:
    if split not in GENERATOR_SPLITS:
        raise ValueError(f"unknown split: {split}")
    stem = SCENARIO_STEMS[template_id]
    # Keep the historical development prefix (`dev-...`) for schedule continuity.
    prefix = "dev" if split == "development" else split
    return f"{prefix}-{stem}-{difficulty}-{instance:03d}"


def enumerate_tab_catalog_bases(*, replicate_seed=0, difficulties=DIFFICULTIES,
                                split=ALLOWED_SPLIT):
    """Return one base-scenario descriptor per template × difficulty (20 for full S0)."""
    if split not in GENERATOR_SPLITS:
        raise ValueError(f"unknown split: {split}")
    rows = []
    for template_id in TEMPLATES:
        for difficulty in difficulties:
            base_id = base_id_for(split, template_id, difficulty)
            assignment = {
                "base_id": base_id,
                "template_id": template_id,
                "family": "tables",
                "intended_difficulty": difficulty,
                "mechanism": ALLOWED_MECHANISM,
                "shortcut_resource_id": SHORTCUT,
                "policy_id": ALLOWED_POLICY,
                "split": split,
                "replicate_seed": replicate_seed,
                "generation_seed": generation_seed_for(split, template_id, difficulty),
                "generator_version": (
                    TAB01_SLICE_VERSION if template_id == "TAB01" and difficulty == "moderate"
                    else CATALOG_VERSION),
            }
            rows.append(assignment)
    return rows


def enumerate_tab_catalog_assignments(*, replicate_seed=0, difficulties=DIFFICULTIES,
                                      information_states=("complete", "incomplete"),
                                      shortcut_available=(True, False),
                                      visibility=("V00", "V01", "V10", "V11"),
                                      split=ALLOWED_SPLIT):
    """Expand bases into the matched 16-cell factorial used by the vertical slice."""
    rows = []
    for base in enumerate_tab_catalog_bases(
            replicate_seed=replicate_seed, difficulties=difficulties, split=split):
        for information_state in information_states:
            for available in shortcut_available:
                for cell in visibility:
                    episode_id = make_episode_id(
                        base_id=base["base_id"],
                        information_state=information_state,
                        shortcut_available=available,
                        visibility=cell,
                        replicate_seed=replicate_seed,
                    )
                    rows.append({
                        **base,
                        "episode_id": episode_id,
                        "information_state": information_state,
                        "shortcut_available": available,
                        "visibility": cell,
                        "generator_version": generator_version_for({
                            **base, "information_state": information_state}),
                    })
    return rows


def smoke_assignments(*, replicate_seed=0):
    """Eight short compatibility cells on one reserved smoke base (not scientific)."""
    # TAB01 trivial × complete/incomplete × present/absent × V00/V11 = 8.
    return [
        row for row in enumerate_tab_catalog_assignments(
            replicate_seed=replicate_seed,
            difficulties=("trivial",),
            information_states=("complete", "incomplete"),
            shortcut_available=(True, False),
            visibility=("V00", "V11"),
            split="smoke",
        )
        if row["template_id"] == "TAB01"
    ]
