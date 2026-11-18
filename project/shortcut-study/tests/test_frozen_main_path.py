"""SW07-C / ECE-87: frozen materialization + guarded main path regressions."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from shortcut_study.adapters.mock import MockActor
from shortcut_study.freeze import (
    PROTOCOL_CANDIDATE,
    FreezeAuthorityError,
    authorize_main_execution,
    dry_validate_schedule,
    frozen_dir,
    materialize_provisional_frozen_tree,
    sha256_file,
    sign_freeze_manifest_for_tests,
    validate_freeze_authority,
)
from shortcut_study.paths import CONFIGS_DIR
from shortcut_study.runner import recover_mock_episode, run_mock_episode
from shortcut_study.tasks.tables import enumerate_tab_catalog_assignments, generate_task

PROVISIONAL_DIR = CONFIGS_DIR / "provisional" / "s0-tab-only"
FROZEN = frozen_dir(PROTOCOL_CANDIDATE)


class SignedFrozenMaterializationTests(unittest.TestCase):
    def test_committed_frozen_tree_is_signed_and_hash_pinned(self):
        self.assertTrue(FROZEN.is_dir())
        manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "frozen_signed")
        self.assertTrue(manifest["freeze"]["signed"])
        self.assertEqual(manifest["freeze"]["accepting_owner"], "Yehia F")
        self.assertEqual(
            manifest["freeze"]["freeze_commit"],
            "571d88865ee3d2d83ea152275b58436fccacc06c",
        )
        self.assertEqual(manifest["freeze"]["g3_status"], "accepted")
        self.assertFalse(manifest["submission_authorized"])
        actor = json.loads((FROZEN / "actor_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(actor["primary_actor"]["sampling"]["temperature"], 0.2)
        self.assertEqual(actor["primary_actor"]["sampling"]["top_p"], 0.95)
        self.assertEqual(actor["errata"]["id"], "ECE-90")
        self.assertEqual(manifest["errata"]["id"], "ECE-90")
        scope = json.loads((FROZEN / "scope.json").read_text(encoding="utf-8"))
        self.assertEqual(
            scope["semantic_claims"]["default"], "withdrawn_behavioral_only"
        )
        dry = dry_validate_schedule(FROZEN)
        self.assertEqual(dry["assigned"], 320)
        self.assertTrue(dry["signed"])
        authority = validate_freeze_authority(FROZEN, require_signed=True)
        self.assertTrue(authority["executable_main"])
        self.assertEqual(authority["authority"], "accepted")
        self.assertEqual(
            authority["component_sha256"]["actor_profile"],
            manifest["freeze"]["component_sha256"]["actor_profile"],
        )

    def test_unsigned_clone_rejects_main_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "frozen"
            shutil.copytree(FROZEN, clone)
            manifest = json.loads((clone / "manifest.json").read_text(encoding="utf-8"))
            manifest["status"] = "provisional_materialization_unsigned"
            manifest["freeze"]["signed"] = False
            manifest["freeze"]["accepting_owner"] = None
            manifest["freeze"]["freeze_commit"] = None
            manifest["freeze"]["g3_status"] = "not_started"
            (clone / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaises(FreezeAuthorityError):
                validate_freeze_authority(clone, require_signed=True)
            with self.assertRaises(FreezeAuthorityError):
                authorize_main_execution(clone)

    def test_hash_mismatch_rejects_even_when_signed(self):
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "frozen"
            shutil.copytree(FROZEN, clone)
            budgets = json.loads((clone / "budgets.json").read_text(encoding="utf-8"))
            budgets["tampered"] = True
            (clone / "budgets.json").write_text(
                json.dumps(budgets, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaises(FreezeAuthorityError) as ctx:
                validate_freeze_authority(clone, require_signed=False)
            self.assertIn("hash mismatch", str(ctx.exception))

    def test_provisional_draft_tree_invariants_retained(self):
        """Draft-era provisional configs stay unsigned; frozen tree is separately signed."""
        self.assertTrue(PROVISIONAL_DIR.is_dir())
        manifest = json.loads((PROVISIONAL_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "draft_not_frozen")
        self.assertFalse(manifest["freeze"]["signed"])
        self.assertIsNone(manifest["freeze"]["frozen_directory"])
        frozen_manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotEqual(frozen_manifest["status"], "draft_not_frozen")
        self.assertTrue(frozen_manifest["freeze"]["signed"])


class GuardedMainPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.assignment = enumerate_tab_catalog_assignments(
            split="main", difficulties=("trivial",)
        )[0]
        self.task = generate_task(
            self.assignment, generation_seed=self.assignment["generation_seed"]
        )

    def _clone_signed_freeze(self) -> Path:
        clone = self.root / "signed-freeze"
        shutil.copytree(FROZEN, clone)
        # Re-stamp with test-only owner to keep production owner distinct in mock inputs.
        sign_freeze_manifest_for_tests(
            clone,
            accepting_owner="test-only-owner-not-yehia",
            freeze_commit="deadbeefcafebabe0123456789abcdef01234567",
        )
        return clone

    def test_mock_main_still_refused_without_freeze_dir(self):
        with self.assertRaises(ValueError) as ctx:
            run_mock_episode(
                self.task, MockActor("legitimate"), self.root / "no-freeze", run_id="guard"
            )
        self.assertIn("freeze_dir", str(ctx.exception))

    def test_mock_main_refuses_unsigned_clone(self):
        clone = self.root / "unsigned"
        shutil.copytree(FROZEN, clone)
        manifest = json.loads((clone / "manifest.json").read_text(encoding="utf-8"))
        manifest["status"] = "provisional_materialization_unsigned"
        manifest["freeze"]["signed"] = False
        manifest["freeze"]["accepting_owner"] = None
        manifest["freeze"]["freeze_commit"] = None
        manifest["freeze"]["g3_status"] = "not_started"
        (clone / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError) as ctx:
            run_mock_episode(
                self.task,
                MockActor("legitimate"),
                self.root / "unsigned-out",
                run_id="guard",
                freeze_dir=clone,
            )
        self.assertIn("unsigned", str(ctx.exception).lower())

    def test_mock_main_runs_under_committed_signed_freeze(self):
        episode, ledger = run_mock_episode(
            self.task,
            MockActor("legitimate"),
            self.root / "main-ok-committed",
            run_id="guarded-main-committed",
            freeze_dir=FROZEN,
        )
        self.assertEqual(episode["split"], "main")
        self.assertTrue(ledger["events"])
        inputs = json.loads(
            (self.root / "main-ok-committed" / "inputs.json").read_text(encoding="utf-8")
        )
        self.assertEqual(inputs["freeze_authority"]["accepting_owner"], "Yehia F")

    def test_mock_main_refuses_mismatched_hashes_even_if_signed_fields_present(self):
        clone = self._clone_signed_freeze()
        scope = json.loads((clone / "scope.json").read_text(encoding="utf-8"))
        scope["tampered"] = "yes"
        (clone / "scope.json").write_text(
            json.dumps(scope, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError) as ctx:
            run_mock_episode(
                self.task,
                MockActor("legitimate"),
                self.root / "mismatch",
                run_id="guard",
                freeze_dir=clone,
            )
        self.assertIn("hash mismatch", str(ctx.exception))

    def test_mock_main_runs_under_signed_matching_freeze(self):
        clone = self._clone_signed_freeze()
        episode, ledger = run_mock_episode(
            self.task,
            MockActor("legitimate"),
            self.root / "main-ok",
            run_id="guarded-main",
            freeze_dir=clone,
        )
        self.assertEqual(episode["split"], "main")
        self.assertTrue(ledger["events"])
        inputs = json.loads((self.root / "main-ok" / "inputs.json").read_text(encoding="utf-8"))
        self.assertEqual(inputs["freeze_authority"]["accepting_owner"], "test-only-owner-not-yehia")
        self.assertEqual(
            inputs["freeze_authority"]["component_sha256"]["schedule"],
            sha256_file(clone / "schedule.json"),
        )

    def test_interrupted_main_id_remains_recoverable_without_replacement(self):
        clone = self._clone_signed_freeze()
        directory = self.root / "main-interrupted"
        episode, ledger = run_mock_episode(
            self.task,
            MockActor("legitimate"),
            directory,
            run_id="guarded-main",
            freeze_dir=clone,
        )
        terminal_bytes = (directory / "terminal.json").read_bytes()
        (directory / "reviewer.json").unlink()
        recovered_episode, recovered_ledger = recover_mock_episode(directory)
        self.assertEqual(recovered_episode["episode_id"], episode["episode_id"])
        self.assertEqual(recovered_ledger["integrity_sha256"], ledger["integrity_sha256"])
        self.assertEqual((directory / "terminal.json").read_bytes(), terminal_bytes)

    def test_materialize_refuses_overwrite(self):
        with self.assertRaises(FreezeAuthorityError):
            materialize_provisional_frozen_tree(FROZEN)


if __name__ == "__main__":
    unittest.main()
