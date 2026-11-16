"""WP07 analysis scaffolding: metrics, aggregation, and contrast harnesses.

Operates on scored rows plus schedule strata. Synthetic fixtures exercise the
pipeline; real actor archives are required for scientific estimates. This package
never invents frozen main results.
"""

from .aggregate import assigned_denominator, missingness_bounds, weight_plan
from .compare import analyze_acquisition, bootstrap_contrasts, confirmatory_contrasts
from .harness import run_analyze, run_dry
from .metrics import VISIBILITY_ORDER, acquisition_outcome, cell_rates, zero_event_warnings
from .semantic import label_error_sensitivity, weighted_review_diagnostics
from .simulate import INJECTED_EFFECTS, build_simulation_bundle

__all__ = [
    "INJECTED_EFFECTS",
    "VISIBILITY_ORDER",
    "acquisition_outcome",
    "analyze_acquisition",
    "assigned_denominator",
    "bootstrap_contrasts",
    "build_simulation_bundle",
    "cell_rates",
    "confirmatory_contrasts",
    "label_error_sensitivity",
    "missingness_bounds",
    "run_analyze",
    "run_dry",
    "weight_plan",
    "weighted_review_diagnostics",
    "zero_event_warnings",
]
