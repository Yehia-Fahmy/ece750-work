"""Split membership and disjointness rules."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from .ids import SPLITS


def assert_known_split(split: str) -> None:
    if split not in SPLITS:
        raise ValueError(f"unknown split: {split}; expected one of {SPLITS}")


def check_split_disjointness(records: Sequence[Mapping]) -> None:
    """Enforce episode_id uniqueness and fingerprint-per-split exclusivity.

    The same semantic_fingerprint must not appear in two different splits.
    Multiple episodes may share a fingerprint within one split (matched cells).
    """
    episode_ids: set[str] = set()
    fingerprint_splits: dict[str, set[str]] = defaultdict(set)

    for record in records:
        episode_id = record["episode_id"]
        split = record["split"]
        fingerprint = record["semantic_fingerprint"]
        assert_known_split(split)
        if episode_id in episode_ids:
            raise AssertionError(f"duplicate episode_id: {episode_id}")
        episode_ids.add(episode_id)
        fingerprint_splits[fingerprint].add(split)

    conflicts = {
        fingerprint: sorted(splits)
        for fingerprint, splits in fingerprint_splits.items()
        if len(splits) > 1
    }
    if conflicts:
        raise AssertionError(
            f"semantic_fingerprint appears in multiple splits: {conflicts}"
        )


def check_content_disjoint_bases(
    bases: Sequence[Mapping],
    *,
    identity_key: str = "semantic_fingerprint",
    label_key: str = "reservation_label",
) -> None:
    """Reject identical semantic identities across differently labeled reservations.

    Used for CPU-only development / consumed-qual / fresh-qual / main proofs.
    """
    seen: dict[str, Mapping] = {}
    for row in bases:
        identity = row[identity_key]
        label = row[label_key]
        if identity in seen and seen[identity][label_key] != label:
            raise AssertionError(
                "identical semantic identity across reservations: "
                f"{seen[identity][label_key]!r} vs {label!r} "
                f"(base_ids={seen[identity].get('base_id')!r}, {row.get('base_id')!r})"
            )
        seen[identity] = row


def group_by_base(records: Iterable[Mapping]) -> dict[str, list[Mapping]]:
    grouped: dict[str, list[Mapping]] = defaultdict(list)
    for record in records:
        grouped[record["base_id"]].append(record)
    return dict(grouped)
