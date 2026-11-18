"""SW07-C: provisional frozen materialization + guarded main path regressions."""

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


class ProvisionalFrozenMaterializationTests(unittest.TestCase):
    def test_committed_frozen_tree_is_unsigned_and_hash_pinned(self):
        self.assertTrue(FROZEN.is_dir())
        manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "provisional_materialization_unsigned")
        self.assertFalse(manifest["freeze"]["signed"])
        self.assertIsNone(manifest["freeze"]["accepting_owner"])
        self.assertIsNone(manifest["freeze"]["freeze_commit"])
        self.assertEqual(manifest["freeze"]["g3_status"], "not_started")
        self.assertFalse(manifest["submission_authorized"])
        dry = dry_validate_schedule(FROZEN)
        self.assertEqual(dry["assigned"], 320)
        self.assertFalse(dry["dry_executable"])
        self.assertFalse(dry["signed"])

    def test_unsigned_frozen_tree_rejects_main_authority(self):
        with self.assertRaises(FreezeAuthorityError):
            validate_freeze_authority(FROZEN, require_signed=True)
        with self.assertRaises(FreezeAuthorityError):
            authorize_main_execution(FROZEN)

    def test_hash_mismatch_rejects_even_structurally(self):
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
        """Draft-era provisional configs stay unsigned; frozen existence is allowed now."""
        self.assertTrue(PROVISIONAL_DIR.is_dir())
        manifest = json.loads((PROVISIONAL_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "draft_not_frozen")
        self.assertFalse(manifest["freeze"]["signed"])
        self.assertIsNone(manifest["freeze"]["frozen_directory"])
        # Committed frozen tree must not claim to be the provisional draft.
        frozen_manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotEqual(frozen_manifest["status"], "draft_not_frozen")


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

    def test_mock_main_refuses_unsigned_committed_freeze(self):
        with self.assertRaises(ValueError) as ctx:
            run_mock_episode(
                self.task,
                MockActor("legitimate"),
                self.root / "unsigned",
                run_id="guard",
                freeze_dir=FROZEN,
            )
        self.assertIn("unsigned", str(ctx.exception).lower())

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
