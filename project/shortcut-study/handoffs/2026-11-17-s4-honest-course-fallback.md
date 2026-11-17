# Package handoff — S4 honest course fallback **declared** — 2026-11-17

- Owner and role: integrator (scope/gate record) + report author path for WP12; CPU only; no GPU this turn.
- Status: **ready_for_review** — S4 declared; do **not** self-merge.
- Input commit and dependencies: `main` @ `6eb9633` ([PR #25](https://github.com/Yehia-Fahmy/ece750-work/pull/25) post-catalog-v2 G2 FAIL merged); prior G2 FAIL [#23](https://github.com/Yehia-Fahmy/ece750-work/pull/23); G0 accept [#22](https://github.com/Yehia-Fahmy/ece750-work/pull/22); TAB01 v6 PASS [#20](https://github.com/Yehia-Fahmy/ece750-work/pull/20); scope ladder `docs/shortcut-study-scope-path.md` tier **S4**.
- Output: this handoff + `state.json` S4 declaration + companion WP12 S4 draft handoff on `cursor/s4-honest-course-fallback-8582`.
- Paths changed: `state.json`, this handoff, `handoffs/2026-11-17-wp12-s4-report.md`, `report/methods-skeleton.md`, `report/README.md`, `README.md` status line, provisional `reduced_claims.json` / `scope.json` S4 flags. No schemas rewritten; no qualification JSON rewritten; both G2 FAIL archives untouched.

## Decision

**Declare tier S4 — honest course fallback.**

| Element | Choice |
| --- | --- |
| Main factorial / frozen collection | **None** (`primary_actor_episodes = 0`) |
| `gates.G2` | **failed** (not accepted) |
| `gates.G3` / freeze | **canceled** (`frozen_protocol` remains `null`) |
| `gates.G4` / `G5` | **canceled** (no main actor/audit collection) |
| WP09–WP11 | **canceled** under S4 |
| WP12 | **in_progress** — honest S4 course-report draft |
| Course package content | Original observer study + validated extension methods/pilots + explicit incomplete outcomes |

## Why now (evidence, not hope)

| Evidence | Result | Tracked |
| --- | --- | --- |
| G2 held-out #23 | **FAIL** — 238/320 completed (74.38%); easy 11/20 (55%) | `results/qualification/g2-held-out-20261116.json` |
| Catalog-v2 port #24 | CPU public-task port only; does not clear G2 | `results/development/tab-catalog-v2-public-task-port.json` |
| G2 re-held-out #25 | **FAIL** — 239/320 completed (74.69%); easy 11/20 (55%) | `results/qualification/g2-held-out-20261116-catalog-v2.json` |
| TAB01 v6 development | **PASS** probe + 16/16 archive (not held-out) | `capability-probe-tab01-v6.json`, `native-qualification-tab01-v6-16cell.json` |
| G1 long pilots | Recorded 9/10; **not** G1 acceptance | `g1-long-pilots-20261116.json` |

Catalog-v2 did **not** clear G2 (nearly unchanged vs #23). Per scope-ladder S4 rule and Dec 4 calendar: stop main-collection ambition; ship the honest fallback.

## Claims retained vs withdrawn

**Retained (honest):**

- Historical observer-study result (separate namespace; not rewritten).
- Extension methods, contracts, mediated environment, scoring/audit-prep stack.
- TAB01 `tab01-slice-v6` development capability probe + 16-cell PASS as **pilot** evidence.
- G1 long-pilot telemetry as **pilot** evidence (9/10 completed).
- Two preserved G2 FAIL archives as **negative** held-out evidence.
- Limitations, uncertainty language, and AI disclosure.

**Withdrawn:**

- Any **main** S0/S1/S2/S3 factorial claim (including the provisional 320-episode S0 freeze target).
- G2 pass / main-qualified actor / freeze (`G3`) / WP09–WP11 confirmatory findings.
- Independent semantic-judge conclusions (judge never qualified; no cloud judge).
- Original 3,200-episode five-family course core (already withdrawn for Dec 4; remains withdrawn).
- Visibility acquisition-effect estimates from development cells or failed held-out archives.

## Explicit non-claims

- This handoff does **not** invent main results, acquisition rates, or visibility contrasts.
- This handoff does **not** rewrite either G2 FAIL archive.
- This handoff does **not** accept G1 formally (pilots remain recorded-only).
- WP12 draft under S4 is **not** WP12 package acceptance (PDF/slides/WP13 still required).

## Commands / GPU

- Documentation + state only; no `qualify-local`; no GPU lease.

## Next safe action

1. Lagging reviewer reviews this PR (author must not self-merge).
2. Finish course packaging path under S4: refine WP12 → PDF/slides → WP13; submission remains Yehia-only.
3. Do **not** start WP09 main collection; do **not** soft-wash G2.

## Acceptance reviewer, decision, and date

Integrator scope decision **2026-11-17**: S4 declared after #25 merge. Lagging reviewer reviews before merge.
