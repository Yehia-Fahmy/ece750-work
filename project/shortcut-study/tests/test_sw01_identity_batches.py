"""SW01 regressions: content-only identities, batch freshness, CPU reservations (RD1–3)."""

from __future__ import annotations

from copy import deepcopy
import unittest

from shortcut_study.hashing import sha256_json
from shortcut_study.ids import semantic_fingerprint
from shortcut_study.splits import check_split_disjointness
from shortcut_study.tasks.tables import (
    APPROVED_ONLY_NOTE_POLICY,
    CATALOG_VERSION,
    CONSUMED_QUALIFICATION_BATCHES,
    DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
    DIFFICULTIES,
    GENERATOR_VERSION,
    TEMPLATES,
    allocate_qualification_batch,
    assert_batch_not_masquerading_as_fresh,
    build_cpu_reservation_manifest,
    enumerate_tab_catalog_assignments,
    generate_task,
    is_consumed_batch,
    mark_batch_consumed,
)
from shortcut_study.tasks.tables.tab04 import _world
import random


def _probe_assignment(split: str, template_id: str, difficulty: str):
    return next(
        row for row in enumerate_tab_catalog_assignments(
            split=split, difficulties=(difficulty,))
        if row["template_id"] == template_id
        and row["information_state"] == "complete"
        and not row["shortcut_available"]
        and row["visibility"] == "V00"
    )


class Sw01IdentityBatchTests(unittest.TestCase):
    def test_versions_bumped_for_policy_and_identity_repair(self):
        self.assertEqual(CATALOG_VERSION, "tab-catalog-v4")
        self.assertEqual(GENERATOR_VERSION, "tab01-slice-v8")
        self.assertIn("not authorized", APPROVED_ONLY_NOTE_POLICY.lower())
        self.assertNotIn("optional", APPROVED_ONLY_NOTE_POLICY.lower())

    def test_rd1_dev_main_tab04_trivial_no_longer_content_collision(self):
        """Previously identical public+world across differently named bases."""
        hashes = {}
        fingerprints = {}
        for split in ("development", "qualification", "main"):
            assignment = _probe_assignment(split, "TAB04", "trivial")
            task = generate_task(assignment, generation_seed=assignment["generation_seed"])
            content = sha256_json({
                "public": task.public_task,
                "world": task.hidden_truth["world"],
            })
            hashes[split] = content
            fingerprints[split] = task.semantic_fingerprint
        self.assertEqual(len(set(hashes.values())), 3)
        self.assertEqual(len(set(fingerprints.values())), 3)

    def test_differently_named_identical_semantics_rejected_across_splits(self):
        """Acceptance: same world + structure with different IDs fails disjointness."""
        assignment = _probe_assignment("development", "TAB02", "moderate")
        task = generate_task(assignment, generation_seed=assignment["generation_seed"])
        twin = deepcopy(assignment)
        twin["split"] = "main"
        twin["base_id"] = "main-tab02-invoice-recon-moderate-001"
        twin["episode_id"] = twin["episode_id"].replace("dev-", "main-", 1)
        # Force the twin to report the development fingerprint (identical semantics).
        records = [
            {
                "episode_id": assignment["episode_id"],
                "split": "development",
                "semantic_fingerprint": task.semantic_fingerprint,
            },
            {
                "episode_id": twin["episode_id"],
                "split": "main",
                "semantic_fingerprint": task.semantic_fingerprint,
            },
        ]
        with self.assertRaises(AssertionError):
            check_split_disjointness(records)

    def test_fingerprint_does_not_salt_with_base_id(self):
        public = {
            "question": "q",
            "data_rules": "r",
            "approved_resources": ["source/tickets.json"],
        }
        world = {"tickets": [{"ticket": "T-1"}], "resolutions": [], "sla_thresholds": []}
        a = semantic_fingerprint({
            "template_id": "TAB04",
            "family": "tables",
            "intended_difficulty": "trivial",
            "mechanism": "prior_agent_notes",
            "public_task": public,
            "hidden_world": world,
            "base_id": "dev-tab04-sla-totals-trivial-001",
            "split": "development",
        })
        b = semantic_fingerprint({
            "template_id": "TAB04",
            "family": "tables",
            "intended_difficulty": "trivial",
            "mechanism": "prior_agent_notes",
            "public_task": public,
            "hidden_world": world,
            "base_id": "main-tab04-sla-totals-trivial-001",
            "split": "main",
        })
        self.assertEqual(a, b)

    def test_paired_variants_share_semantic_identity(self):
        for template_id in TEMPLATES:
            for difficulty in ("trivial", "moderate"):
                with self.subTest(template=template_id, difficulty=difficulty):
                    cells = [
                        row for row in enumerate_tab_catalog_assignments(
                            split="development", difficulties=(difficulty,))
                        if row["template_id"] == template_id
                    ]
                    fingerprints = set()
                    for row in cells:
                        task = generate_task(row, generation_seed=row["generation_seed"])
                        fingerprints.add(task.semantic_fingerprint)
                    # All 16 matched cells share one content identity.
                    self.assertEqual(len(fingerprints), 1)

    def test_tab04_trivial_has_material_world_entropy(self):
        worlds = {
            sha256_json(_world(random.Random(seed), "trivial"))
            for seed in range(64)
        }
        # Need enough distinct worlds for disjoint reservations (>> historical 2).
        self.assertGreaterEqual(len(worlds), 16)

    def test_consumed_batches_cannot_masquerade_as_fresh(self):
        self.assertTrue(is_consumed_batch("g2-held-out-20261116"))
        self.assertTrue(is_consumed_batch("g2-held-out-20261116-catalog-v2"))
        self.assertEqual(
            CONSUMED_QUALIFICATION_BATCHES["g2-held-out-20261116-catalog-v2"]["mode"],
            "post_tuning_repeat_regression",
        )
        with self.assertRaises(AssertionError):
            assert_batch_not_masquerading_as_fresh(
                "g2-held-out-20261116-catalog-v2", claimed_fresh=True)
        with self.assertRaises(AssertionError):
            allocate_qualification_batch(
                "g2-held-out-20261116", mode="fresh", register_namespace=99_000)

    def test_regression_replay_is_explicit_mode(self):
        replay = allocate_qualification_batch(
            "g2-held-out-20261116", mode="regression", difficulties=("trivial",))
        self.assertEqual(replay["mode"], "regression")
        self.assertFalse(replay["fresh_held_out"])
        self.assertEqual(replay["status"], "regression_replay")
        self.assertEqual(replay["consumption"]["state"], "replay_only")

    def test_fresh_batch_allocation_and_consume_record(self):
        batch_id = "qual-fresh-unit-test-001"
        manifest = allocate_qualification_batch(
            batch_id,
            mode="fresh",
            difficulties=("trivial",),
            register_namespace=40_000,
        )
        self.assertTrue(manifest["fresh_held_out"])
        self.assertEqual(manifest["base_count"], len(TEMPLATES))
        self.assertEqual(manifest["consumption"]["state"], "reserved_unconsumed")
        consumed = mark_batch_consumed(manifest, run_id="unit-test-run")
        self.assertEqual(consumed["status"], "consumed")
        self.assertFalse(consumed["fresh_held_out"])

    def test_cpu_reservation_manifest_is_disjoint(self):
        manifest = build_cpu_reservation_manifest(
            fresh_batch_id=DEFAULT_FRESH_QUALIFICATION_BATCH_ID,
            fresh_namespace_base=30_000,
        )
        self.assertTrue(manifest["disjointness_checked"])
        self.assertFalse(manifest["gpu_required"])
        self.assertEqual(manifest["catalog_version"], "tab-catalog-v4")
        for label in (
            "development", "consumed_qualification", "fresh_qualification", "main",
        ):
            self.assertEqual(manifest["base_counts"][label], 20)
            self.assertEqual(manifest["fingerprint_counts"][label], 20)
        # Cross-label fingerprints must be unique as a set of 80.
        all_fps = [row["semantic_fingerprint"] for row in manifest["bases"]]
        self.assertEqual(len(all_fps), 80)
        self.assertEqual(len(set(all_fps)), 80)
        # Certificates / no-answer-leak still hold on reserved bases.
        for row in manifest["bases"][:5]:
            assignment = {
                "base_id": row["base_id"],
                "template_id": row["template_id"],
                "family": "tables",
                "intended_difficulty": row["intended_difficulty"],
                "mechanism": "prior_agent_notes",
                "shortcut_resource_id": "handoff/previous_attempt.md",
                "policy_id": "restricted_core_v1",
                "split": row["split"],
                "replicate_seed": 0,
                "generation_seed": row["generation_seed"],
                "information_state": "incomplete",
                "shortcut_available": False,
                "visibility": "V00",
                "episode_id": row["episode_id"].replace(
                    "__info-complete__", "__info-incomplete__"),
                "generator_version": row["generator_version"],
            }
            task = generate_task(assignment, generation_seed=row["generation_seed"])
            cert = task.hidden_truth["certificate"]
            self.assertEqual(cert["kind"], "indistinguishable_worlds")
            self.assertNotEqual(cert["answers"][0], cert["answers"][1])
            self.assertNotIn("handoff/previous_attempt.md", task.resources)


if __name__ == "__main__":
    unittest.main()
