# Package handoff — SW01 task identities / batches — 2026-11-17

- Owner and role: `sw01_task_engineer` (ECE-36); CPU-only task engineer
- Status: ready_for_review
- Input commit and dependencies: `3f77a18` on `cursor/sw00-completion-baseline-be8a` (SW00 tip); findings RD1–3; assignment `handoffs/2026-11-17-sw01-assignment.md`
- Output commit (or explicitly uncommitted paths): see git tip of `cursor/sw01-task-identity-batches-1b07` after push
- Paths changed; shared-contract version: allowlisted SW01 paths only; catalog `tab-catalog-v3`, TAB01 slice `tab01-slice-v7`; batch schema `shortcut-qualification-batch-v1` / reservation `shortcut-cpu-reservation-manifest-v1`
- Concrete behavior implemented:
  1. **RD1:** Removed split/base_id fingerprint salt; fingerprints are content-only (`canonical_semantic_material` ignores incidental public wording). Expanded TAB04 entropy so development / qualification / main worlds are content-disjoint. Cross-split identical semantics now fail `check_split_disjointness`.
  2. **RD2:** Added `tasks/tables/batches.py` with consumed-batch registry (catalog-v2 annotated as `post_tuning_repeat_regression`), fresh allocation + immutable semantic manifests, explicit `regression` replay mode, and CPU reservation manifest proving 80 disjoint fingerprints across development / consumed-qual / fresh-qual / main.
  3. **RD3:** Replaced “optional and not required” note wording with shared `APPROVED_ONLY_NOTE_POLICY` (approved-only; catalog discovery retained).
- Commands run and actual outcomes:
  - Pre-fix reproduce: 1 content duplicate pair (`dev-tab04-…-trivial-001` / `main-tab04-…-trivial-001`); existing checker passed.
  - Post-fix reproduce: `content_duplicate_pairs_across_splits: []`; checker passed; 60 bases.
  - `PYTHONPATH=src python3 -m unittest tests.test_sw01_identity_batches tests.test_ids_splits tests.test_tab_catalog tests.test_task_prompt_review` → **32 OK**
  - Full extension suite `unittest discover -s tests` → **225 OK** (informational; integrator owns wave acceptance)
  - No GPU; no new 320-episode qualification; `submission_authorized` untouched
- Evidence/manifest paths and hashes:
  - `results/development/sw01-cpu-reservation-manifest-v1.json` — `manifest_sha256=c1cd65c39e4bf50b029975122546afddb6622092a6a5e3129d299928eba3068c`
  - `results/development/sw01-identity-batches-v1.json`
  - Source SHA-256 (post-fix): `ids.py` `0b156519…`; `splits.py` `67a77929…`; `common.py` `e505351c…`; `batches.py` `d686996a…`; `tab04.py` `7890ee8e…`
- Failures, uncertain findings, and scope limitations:
  - Did not edit `qualification.py` / `held_out.py` / `__main__.py` / `configs/` / `schemas/` / `state.json` (integrator-owned). CLI still selects the historical qualification catalog until wired.
  - Raw qualification archives unavailable on this host; RD2 archive byte-comparison not re-proven here (lineage recorded in consumed registry).
  - Policy wording change is instruction-level only; no behavioral actor measurement of comprehension.
  - TAB01 moderate world layout preserved; version bump reflects policy/fingerprint contract change.
  - Static `fixtures/episodes/*.json` fingerprints still use the pre-repair algorithm values; they were **not** rewritten (outside allowlist). Integrator/SW03 may regenerate deliberately if contract fixtures must match `canonical_semantic_material`.
- GPU lease owner/process/job, or no GPU work: **no GPU work**
- Terminal/incomplete/unattempted job IDs if applicable: none
- Next safe action and required dependency:
  1. Integrator merges batch API into `qualification.py` / schemas / CLI (proposal below).
  2. **Independent reviewer `sw03_analyst`** runs the review brief below on this PR commit.
  3. Do not start GPU qualification until SW05 accepts identity/batch repairs.
- Acceptance reviewer, decision, and date (filled on review): pending — `sw03_analyst`

## Interface proposal for integrator (qualification batch consumption)

Wire `shortcut_study.tasks.tables.batches` without treating a new output directory as freshness:

| Hook | Call |
| --- | --- |
| Before held-out run | `allocate_qualification_batch(batch_id, mode="fresh", register_namespace=…)` → persist manifest under run inputs; reject if `is_consumed_batch(batch_id)` |
| Schedule generation | Use `generation_seed_for_batch` / fresh `base_id`s from the manifest, not only `enumerate_tab_catalog_assignments(split="qualification")` |
| After attempt closes | `mark_batch_consumed(manifest, run_id=…)` and append to durable consumption ledger (schema TBD under integrator) |
| Re-run old worlds | `allocate_qualification_batch(consumed_id, mode="regression")` only; label evidence as regression |
| Config bump | `configs/development/tab_catalog.json` → `tab-catalog-v3`; document `tab01-slice-v7` |
| Preserve | Never rename/delete `g2-held-out-20261116` or `…-catalog-v2` archives |

## Review brief for `sw03_analyst` (author ≠ reviewer)

Reproduce independently on the SW01 PR tip:

```sh
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/research-design-reproduce.py
# expect content_duplicate_pairs_across_splits == []

cd project/shortcut-study && PYTHONPATH=src python3 -m unittest \
  tests.test_sw01_identity_batches tests.test_ids_splits \
  tests.test_tab_catalog tests.test_task_prompt_review
```

Check:

1. Fingerprints ignore split/base_id and incidental wording; TAB04 trivial no longer collides across splits.
2. Consumed batches cannot claim `fresh`; catalog-v2 annotated as post-tuning repeat; regression mode explicit.
3. CPU reservation manifest shows 20×4 disjoint fingerprints; no GPU.
4. Policy text is approved-only (no “optional and not required”).
5. Path allowlist respected; no `state.json` / qualification wiring edits; interface proposal present.
6. Do not mark acceptance without inspecting the exact PR commit hashes.
