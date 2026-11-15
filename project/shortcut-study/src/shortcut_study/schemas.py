"""Load and validate versioned JSON Schema contracts."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from .paths import SCHEMAS_DIR

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - exercised when dep missing
    raise ImportError(
        "jsonschema is required to validate shortcut-study contracts; "
        "install project/shortcut-study/requirements.txt"
    ) from exc

SCHEMA_FILES = {
    "episode": "episode_record.schema.json",
    "events": "event_ledger.schema.json",
    "reviewer_packet": "reviewer_packet.schema.json",
    "auditor_packet": "auditor_packet.schema.json",
    "scored_row": "scored_row.schema.json",
    "semantic_audit": "semantic_audit_row.schema.json",
}


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    if name not in SCHEMA_FILES:
        raise KeyError(f"unknown schema: {name}")
    path = SCHEMAS_DIR / SCHEMA_FILES[name]
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=None)
def validator_for(name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(name))


def validate(name: str, document: Mapping[str, Any]) -> None:
    validator_for(name).validate(document)


def schema_path(name: str) -> Path:
    if name not in SCHEMA_FILES:
        raise KeyError(f"unknown schema: {name}")
    return SCHEMAS_DIR / SCHEMA_FILES[name]
