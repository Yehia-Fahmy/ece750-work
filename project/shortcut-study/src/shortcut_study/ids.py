"""Stable episode / base / fingerprint helpers."""

from __future__ import annotations

from typing import Any, Mapping

from .hashing import sha256_json, sha256_text

VISIBILITY_CELLS = ("V00", "V01", "V10", "V11")
INFORMATION_STATES = ("complete", "incomplete")
SPLITS = ("smoke", "development", "qualification", "main")

# Keys hashed for semantic identity. Incidental public wording is excluded so
# rephrasing alone cannot mint a "new" held-out scenario (RD1).
_SEMANTIC_CORE_KEYS = (
    "template_id",
    "family",
    "intended_difficulty",
    "mechanism",
)


def shortcut_token(shortcut_available: bool) -> str:
    return "present" if shortcut_available else "absent"


def make_base_id(template_id: str, instance_key: str) -> str:
    """Group matched condition variants of one underlying scenario."""
    if not template_id or not instance_key:
        raise ValueError("template_id and instance_key are required")
    return f"{template_id.lower()}-{instance_key}"


def make_episode_id(
    *,
    base_id: str,
    information_state: str,
    shortcut_available: bool,
    visibility: str,
    replicate_seed: int,
) -> str:
    if information_state not in INFORMATION_STATES:
        raise ValueError(f"invalid information_state: {information_state}")
    if visibility not in VISIBILITY_CELLS:
        raise ValueError(f"invalid visibility: {visibility}")
    return (
        f"{base_id}"
        f"__info-{information_state}"
        f"__sc-{shortcut_token(shortcut_available)}"
        f"__vis-{visibility}"
        f"__seed-{replicate_seed}"
    )


def canonical_semantic_material(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Content-only scenario identity (no split name, base_id, or prompt prose).

    Paired information/shortcut/visibility variants share this material when they
    share the same hidden world and approved-resource structure.
    """
    missing = [key for key in (*_SEMANTIC_CORE_KEYS, "public_task", "hidden_world")
               if key not in payload]
    if missing:
        raise ValueError(f"semantic_fingerprint missing keys: {missing}")
    public = payload["public_task"]
    if not isinstance(public, Mapping):
        raise ValueError("public_task must be a mapping")
    # Structural public fields only — question/data_rules/policy wording omitted.
    public_structure: dict[str, Any] = {
        "approved_resources": list(public.get("approved_resources", [])),
    }
    if "clarification_fields" in public:
        public_structure["clarification_fields"] = list(public["clarification_fields"])
    return {
        **{key: payload[key] for key in _SEMANTIC_CORE_KEYS},
        "public_structure": public_structure,
        "hidden_world": payload["hidden_world"],
    }


def semantic_fingerprint(payload: Mapping[str, Any]) -> str:
    """Fingerprint the structural scenario identity (not visibility/seed/split)."""
    return sha256_json(canonical_semantic_material(payload))


def actor_settings_hash(settings: Mapping[str, Any]) -> str:
    return sha256_json(settings)


def passage_id(channel: str, index: int) -> str:
    if channel not in {"T", "J"}:
        raise ValueError("channel must be T or J")
    if index < 1:
        raise ValueError("passage index must be >= 1")
    return f"{channel}-{index:04d}"


def event_id(index: int) -> str:
    if index < 1:
        raise ValueError("event index must be >= 1")
    return f"E-{index:04d}"


def text_digest(text: str) -> str:
    return sha256_text(text)
