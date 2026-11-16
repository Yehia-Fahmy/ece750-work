"""TAB family generators: TAB01–05 development catalog with prior-note shortcuts."""

from . import tab01, tab02, tab03, tab04, tab05
from .catalog import (BASE_SCENARIOS, TEMPLATES, enumerate_tab_catalog_assignments,
                      enumerate_tab_catalog_bases)
from .common import (ALLOWED_MECHANISM, ALLOWED_POLICY, ALLOWED_SPLIT, CATALOG_VERSION,
                     CLARIFICATION_FIELDS, DIFFICULTIES, SHORTCUT, TAB01_SLICE_VERSION, TableTask,
                     generator_version_for, resolve_clarification_fields, valid_answer)

# Backward-compatible TAB01 slice exports used by the vertical-slice path.
APPROVED = tab01.APPROVED
GENERATOR_VERSION = tab01.GENERATOR_VERSION
reference_total = tab01.reference_total
public_resources = tab01.public_resources

_MODULES = {
    "TAB01": tab01,
    "TAB02": tab02,
    "TAB03": tab03,
    "TAB04": tab04,
    "TAB05": tab05,
}


def solve_permitted(resources):
    """Dispatch the authorized solver from the approved source layout."""
    source_keys = {key for key in resources if key.startswith("source/")}
    for module in _MODULES.values():
        if source_keys == set(module.APPROVED):
            return module.solve_permitted(resources)
    # Incomplete episodes still expose every approved source key.
    for module in _MODULES.values():
        if set(module.APPROVED) <= set(resources):
            return module.solve_permitted(resources)
    raise ValueError("no TAB solver matches the provided resources")


def generate_task(assignment, generation_seed=0):
    module = _MODULES.get(assignment.get("template_id"))
    if module is None:
        raise ValueError(f"unsupported template_id: {assignment.get('template_id')!r}")
    return module.generate(assignment, generation_seed)


def approved_for(template_id):
    return _MODULES[template_id].APPROVED


def missing_prerequisite_for(template_id):
    return _MODULES[template_id].MISSING


__all__ = [
    "ALLOWED_MECHANISM",
    "ALLOWED_POLICY",
    "ALLOWED_SPLIT",
    "APPROVED",
    "BASE_SCENARIOS",
    "CATALOG_VERSION",
    "CLARIFICATION_FIELDS",
    "DIFFICULTIES",
    "GENERATOR_VERSION",
    "SHORTCUT",
    "TAB01_SLICE_VERSION",
    "TEMPLATES",
    "TableTask",
    "approved_for",
    "enumerate_tab_catalog_assignments",
    "enumerate_tab_catalog_bases",
    "generate_task",
    "generator_version_for",
    "missing_prerequisite_for",
    "public_resources",
    "reference_total",
    "resolve_clarification_fields",
    "solve_permitted",
    "valid_answer",
]
