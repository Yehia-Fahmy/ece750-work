# Claim / evidence ledger (SW04) — 2026-11-17

Status: **living CPU ledger** for the extension report. Not a freeze. Not main results.
`submission_authorized` remains **false**. Parallel SW06 GPU work is owned by the WSL operator only.

## Qualification-reuse caveat (required)

The two archived held-out attempts are **not** two independent fresh validations:

| Run ID | Role | Worlds | Label |
| --- | --- | --- | --- |
| `g2-held-out-20261116` | Original G2 attempt | Consumed | **FAIL** (preserved) |
| `g2-held-out-20261116-catalog-v2` | Post-tuning repeat on the **same** hidden worlds | Consumed / regression | **FAIL** (preserved); **not** a fresh held-out confirmation |

Evidence: `reviews/2026-11-17/research-design.md` (RD2); `reviews/2026-11-17/research-design-evidence.json` (`qualification_reuse`); consumed registry in `src/shortcut_study/tasks/tables/batches.py`.

Fresh qualification after SW05 must use a **new** content-disjoint batch (default id `qual-fresh-tab-catalog-v3-001`). A new output directory alone is not freshness.

## Repair status (code vs gates)

| Finding | Code repair | Scientific gate status |
| --- | --- | --- |
| RD1–3 | Merged (#29); SW05 accepted | Content-disjoint batch API available; **G2 still failed** on consumed archives |
| IMPL-1–3 | Merged (#30/#32); SW05 accepted | Bound audit + task-specific metrics wired; **no new held-out PASS** |
| A1–3 | Merged (#31); SW05 accepted | Estimands/release inputs repaired; **no main analysis** |
| A4/A5 | Addressed in SW03 package; dispositions retained as conditional/clarify in `state.json` until freeze narrative locks denominators | Do not retroactively rewrite historical gate counts |
| G0 (TAB-only) | Historical acceptance (#22) | Scope candidate only |
| G1 | Development/runtime evidence exists | Not a substitute for held-out G2 |
| G2 | Two FAIL archives | **failed / not accepted** |
| G3 | Unsigned draft checklist only | **not_started** — blocked on accepted fresh G2 + freeze review |

## Quantitative claims → artifacts

Use this table for report prose. Prefer hashes/paths over adjectives like “validated.”

| Claim ID | Claim (keep narrow) | Denominator / definition | Artifact | Status |
| --- | --- | --- | --- | --- |
| C-DEV-TAB01-V6 | TAB01 development 16-cell native slice completed with capture gates | Assigned development vertical-slice cells | `results/qualification/native-qualification-tab01-v6-16cell.json` | Recorded development evidence — **not** held-out |
| C-CAP-TAB01-V6 | TAB01 capability probe (2 cells) passed under probe gates | Probe assignment set | `results/qualification/capability-probe-tab01-v6.json` | Narrow probe only |
| C-G1-PILOTS | Long pilots: 10 development hard/extreme complete V00 sc-absent episodes | Development split only | `results/qualification/g1-long-pilots-20261116.json` | WP06 notes; not G2 |
| C-G2-ORIG | Held-out G2 FAIL (original) | 320 assigned qualification cells | `results/qualification/g2-held-out-20261116.json` + runs archive | FAIL preserved |
| C-G2-V2 | Held-out G2 FAIL (catalog-v2 regression reuse) | 320 assigned; **reused worlds** | `results/qualification/g2-held-out-20261116-catalog-v2.json` | FAIL preserved; **not independent** |
| C-G2-EASY | Easy no-shortcut legitimate success on held-out ≈ 11/20 bases (both FAIL runs) | Easy complete sc-absent bases among qualification | Analysis evidence tables in `reviews/2026-11-17/analysis-evidence.md` | Below 80% gate; do not soft-wash |
| C-CPU-SUITE | Extension unit suite green at SW05 tip | Full `tests/` discover | SW05 handoff; tip `96eab5b` / main `91baf90` | CPU acceptance only |
| C-SW06-DEV-NARY | Development n-ary `subtract` repair + TAB02/02–05 probes (partial; TAB03 budget_limit remains) | Development split only; **not** held-out | PR #35 / `results/development/sw06-nary-calculate-probes-v1.json` (on tip) | **Not G2**; independent review pending |
| C-BATCH-V3 | Fresh batch API + catalog v3 wired | CPU reservation / allocate API | `results/development/sw01-cpu-reservation-manifest-v1.json`, `#33` | Enables future fresh G2; **does not claim G2 PASS** |
| C-MAIN | Main factorial effects / visibility contrasts | Frozen main denominator | — | **No claim** (no freeze, no main collection) |
| C-SEM | Semantic judge conclusions | Qualified judge + frozen audit scope | — | **Withdrawn / unqualified** unless later accepted |

## Original study vs extension

| Body of work | Location | Rule |
| --- | --- | --- |
| Observer-framing preliminary study | `project/report/` (do not modify) | Separate findings; reproduce via project verify scripts |
| Extension methods / S4 draft | `report/methods-skeleton.md`, `report/slides-outline.md` | Update from this ledger; keep S4 fallback ready |
| Course delivery packaging | `delivery/` | Researcher submits; `submission_authorized=false` |

## Parallel SW06 coordination

- GPU operator: `bc-1121d0a4…` on WSL DESKTOP-VEMMES3 / RTX 3070 Ti (ECE-42).
- Orchestrator / SW04–SW07 CPU authors **must not** acquire the GPU lease or start a second qualification operator.
- When SW06 posts outcomes: append rows here with run id, batch id, freshness mode (`fresh` vs `regression`), gate PASS/FAIL, and hashes — do not rewrite prior FAIL rows.

## Do not

- Present catalog-v2 as a second independent held-out confirmation
- Call development PASS “qualified”
- Invent main effects or exploratory pilot estimates as confirmation
- Soft-wash G2 FAIL or raise budgets as the primary remediation story
- Claim course submission readiness
