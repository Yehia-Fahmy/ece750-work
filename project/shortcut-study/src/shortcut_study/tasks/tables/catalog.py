"""Development TAB catalog enumeration for S0 (five templates × four difficulties)."""

from ...ids import make_episode_id
from .common import (ALLOWED_MECHANISM, ALLOWED_POLICY, ALLOWED_SPLIT, CATALOG_VERSION, DIFFICULTIES,
                     SHORTCUT, TAB01_SLICE_VERSION, generator_version_for)

TEMPLATES = ("TAB01", "TAB02", "TAB03", "TAB04", "TAB05")

BASE_SCENARIOS = {
    "TAB01": "dev-tab01-net-delivery",
    "TAB02": "dev-tab02-invoice-recon",
    "TAB03": "dev-tab03-stock-balance",
    "TAB04": "dev-tab04-sla-totals",
    "TAB05": "dev-tab05-defect-rate",
}


def enumerate_tab_catalog_bases(*, replicate_seed=0, difficulties=DIFFICULTIES):
    """Return one base-scenario descriptor per template × difficulty (20 for full S0)."""
    rows = []
    for template_id in TEMPLATES:
        for difficulty in difficulties:
            base_id = f"{BASE_SCENARIOS[template_id]}-{difficulty}-001"
            assignment = {
                "base_id": base_id,
                "template_id": template_id,
                "family": "tables",
                "intended_difficulty": difficulty,
                "mechanism": ALLOWED_MECHANISM,
                "shortcut_resource_id": SHORTCUT,
                "policy_id": ALLOWED_POLICY,
                "split": ALLOWED_SPLIT,
                "replicate_seed": replicate_seed,
                "generator_version": (
                    TAB01_SLICE_VERSION if template_id == "TAB01" and difficulty == "moderate"
                    else CATALOG_VERSION),
            }
            rows.append(assignment)
    return rows


def enumerate_tab_catalog_assignments(*, replicate_seed=0, difficulties=DIFFICULTIES,
                                      information_states=("complete", "incomplete"),
                                      shortcut_available=(True, False),
                                      visibility=("V00", "V01", "V10", "V11")):
    """Expand bases into the matched 16-cell factorial used by the vertical slice."""
    rows = []
    for base in enumerate_tab_catalog_bases(replicate_seed=replicate_seed, difficulties=difficulties):
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
