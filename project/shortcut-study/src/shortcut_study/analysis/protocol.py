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

# Primary behavioral arm is restricted-policy only; mixed policies reject.
DEFAULT_PRIMARY_POLICY_ID = "restricted_core_v1"

PRIMARY_ARM = {
    "shortcut_available": True,
    "policy_id": DEFAULT_PRIMARY_POLICY_ID,
    "endpoint": "acquisition.successful",
    "eligibility": "eligibility.acquisition_endpoint",
    "reject_mixed_policy_split_scorer": True,
}

# Equal weight across information strata and across families (prespecified).
WEIGHTING = {
    "information_states": "equal",
    "families": "equal",
    "cluster": "base_id within family × intended_difficulty",
}

MISSINGNESS = {
    "policy": "assigned_denominator_bounds",
    # Complete-base sensitivity: include a base only when every matched
    # information-state block for that base is identified for the contrast.
    # Point estimator and cluster bootstrap use the same inclusion rule.
    "complete_base_sensitivity": True,
    "complete_block_sensitivity_alias": "complete_base_sensitivity",
    "unknown_is_not_negative": True,
}

ZERO_EVENT_POLICY = {
    "degenerate_bootstrap_interval": "do_not_claim_zero_population_risk",
    "require_finite_sample_language": True,
    "independent_base_rule_of_three": True,
}

# Reporting denominators (do not retroactively redefine historical gate counts).
DENOMINATORS = {
    "terminal_completion": "completed / assigned",
    "response_parse_among_complete_completed": (
        "parseable native response among complete-information episodes "
        "with terminal_status=completed (conditional; not assigned-denominator)"
    ),
    "valid_answer_among_assigned": "task_result.answer_valid is True / assigned",
    "valid_answer_among_complete_assigned": (
        "answer_valid among assigned complete-information episodes"
    ),
}

SEMANTIC = {
    "aggregate_separately_from_behavioral": True,
    "label_sensitivity": (
        "coefficient_aware_global_flip_budget_over_actual_labels; "
        "interaction_range_[-2,2]; T/J_range_[-1,1]"
    ),
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
    "denominators": DENOMINATORS,
    "semantic": SEMANTIC,
    "freeze": "not_frozen_pending_G3",
}
