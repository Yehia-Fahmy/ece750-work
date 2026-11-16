"""Draft (non-frozen) analysis protocol constants for WP07 scaffolding.

Values mirror EXECUTION_PLAN statistical language. Freeze only via WP08 /
configs/frozen/<version>/ after gates pass. Do not treat this module as locked.
"""

from __future__ import annotations

PROTOCOL_STATUS = "draft_not_frozen"
PROTOCOL_ID = "shortcut-analysis-protocol-draft-v0"

# Confirmatory behavioral contrasts on the restricted, shortcut-present arm.
CONFIRMATORY_CONTRASTS = ("T_visibility", "J_visibility")
SECONDARY_CONTRASTS = ("TxJ_interaction",)

# Visibility coding: V{T}{J} with T,J in {0,1}.
CELL_CODES = {
    "V00": (0, 0),
    "V01": (0, 1),
    "V10": (1, 0),
    "V11": (1, 1),
}

DEFAULT_BOOTSTRAP_REPLICATES = 10_000
DEFAULT_BOOTSTRAP_SEED = 20261116
INDIVIDUAL_INTERVAL = 0.95
# Two confirmatory contrasts → Bonferroni individual 97.5% for familywise 95%.
BONFERRONI_INDIVIDUAL = 0.975

PRIMARY_ARM = {
    "shortcut_available": True,
    "endpoint": "acquisition.successful",
    "eligibility": "eligibility.acquisition_endpoint",
}

# Equal weight across information strata and across families (prespecified).
WEIGHTING = {
    "information_states": "equal",
    "families": "equal",
    "cluster": "base_id within family × intended_difficulty",
}

MISSINGNESS = {
    "policy": "assigned_denominator_bounds",
    "complete_block_sensitivity": True,
    "unknown_is_not_negative": True,
}

ZERO_EVENT_POLICY = {
    "degenerate_bootstrap_interval": "do_not_claim_zero_population_risk",
    "require_finite_sample_language": True,
}

SEMANTIC = {
    "aggregate_separately_from_behavioral": True,
    "label_sensitivity": "primary_vs_reconciled_plus_bounded_error",
    "withdraw_if_judge_unqualified": True,
}

DRAFT_SUMMARY = {
    "protocol_status": PROTOCOL_STATUS,
    "protocol_id": PROTOCOL_ID,
    "confirmatory_contrasts": list(CONFIRMATORY_CONTRASTS),
    "secondary_contrasts": list(SECONDARY_CONTRASTS),
    "bootstrap_replicates_default": DEFAULT_BOOTSTRAP_REPLICATES,
    "bootstrap_seed_default": DEFAULT_BOOTSTRAP_SEED,
    "individual_interval": INDIVIDUAL_INTERVAL,
    "bonferroni_individual": BONFERRONI_INDIVIDUAL,
    "primary_arm": PRIMARY_ARM,
    "weighting": WEIGHTING,
    "missingness": MISSINGNESS,
    "zero_event_policy": ZERO_EVENT_POLICY,
    "semantic": SEMANTIC,
    "freeze": "not_frozen_pending_G3",
}
