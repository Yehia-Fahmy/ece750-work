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

`qual-fresh-tab-catalog-v3-001` is now **consumed** (honest FAIL). Any further held-out attempt needs a **new** content-disjoint batch id after greenlit residual repairs. A new output directory alone is not freshness.

## Repair status (code vs gates)

| Finding | Code repair | Scientific gate status |
| --- | --- | --- |
| RD1–3 | Merged (#29); SW05 accepted | Content-disjoint batch API available; **G2 still failed** on consumed archives |
| IMPL-1–3 | Merged (#30/#32); SW05 accepted | Bound audit + task-specific metrics wired; **no new held-out PASS** |
| A1–3 | Merged (#31); SW05 accepted | Estimands/release inputs repaired; **no main analysis** |
| A4/A5 | Addressed in SW03 package; dispositions retained as conditional/clarify in `state.json` until freeze narrative locks denominators | Do not retroactively rewrite historical gate counts |
| G0 (TAB-only) | Historical acceptance (#22) | Scope candidate only |
| G1 | Development/runtime evidence exists | Not a substitute for held-out G2 |
| G2 | Three FAIL archives (incl. fresh v3-001) | **failed / not accepted** — no soft-accept |
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
| C-G2-EASY | Easy no-shortcut on prior FAIL runs ≈ 11/20 (55%) | Easy complete sc-absent bases among qualification | Analysis evidence tables in `reviews/2026-11-17/analysis-evidence.md` | Below 80% on prior FAILs |
| C-G2-FRESH-V3 | Fresh content-disjoint held-out attempt `qual-fresh-tab-catalog-v3-001` | 320 assigned; **new** worlds (not catalog-v2 reuse) | `results/qualification/qual-fresh-tab-catalog-v3-001.json` + runs archive | **FAIL** completion 280/320=87.5% &lt;95%; easy 17/20=85% passes that subgate; **G2 not accepted**; batch **consumed** |
| C-CPU-SUITE | Extension unit suite green at SW05 tip | Full `tests/` discover | SW05 handoff; tip `96eab5b` / main `91baf90` | CPU acceptance only |
| C-SW06-DEV-NARY | Development n-ary `subtract` repair + TAB02/02–05 probes (partial; TAB03 budget_limit remains) | Development split only; **not** held-out | PR #35 / `results/development/sw06-nary-calculate-probes-v1.json` (on tip) | **Not G2**; #35 merged `be3ccda` |
| C-SW06-DEV-TOOLFIRST | Development tool-first cues / TAB03 long-T repair (TAB02–05 V00 improved; visibility residuals remain) | Development split only; **not** held-out; no fresh qual batch | PR #37 merged `272e4d7` | **Not G2**; #37 merged |
| C-SW06-DEV-TOOLCHOICE | Development `tool_choice=required` + cooler sampling; TAB02 visibility cleared; TAB03 V01/V10 still budget_limit | Development split only; **not** held-out; no fresh qual batch | PR #39 merged `bffede3` | **Not G2**; #39 merged |
| C-SW06-DEV-FORCEFIRST | Development force-first `list_resources` + reasoning-budget 256; TAB03 V01/V10 cleared in probes | Development split only; then used under fresh qual | PR #41 merged `f016540` (+ bookkeeping #42/#43) | **Not G2**; enabled fresh attempt |
| C-SW06-DEV-RESIDUAL | Post-v3 FAIL residual repair: adapter v5 later-turn thinking off; tool/turn headroom; temp 0.2 | Development split only; **not** held-out | PR #46 merged `0290663` / `results/development/sw06-residual-format-budget-probes-v1.json` | **Not G2**; format **24/24**; TAB05 extreme was **15/16** → ECE-59 |
| C-SW06-DEV-TAB05-EXTREME | TAB05 extreme residual clearance: adapter v6 anti-dupe; probe-only turns 20; live qual turns stay 16 | Development split only; **not** held-out | PR #48 merged `430c86b` / `results/development/sw06-tab05-extreme-residual-clearance-v1.json` | **Not G2**; TAB05 extreme **16/16**; live-qual turns **16**; root greenlit ECE-63 fresh (g2_accepted still false) |
| C-BATCH-V3 | Fresh batch API + catalog v3 wired | CPU reservation / allocate API | `results/development/sw01-cpu-reservation-manifest-v1.json`, `#33` | v3-001 **consumed** FAIL; ECE-63 needs a **new** batch id (root-greenlit) |
| C-MAIN | Main factorial effects / visibility contrasts | Frozen main denominator | — | **No claim** (no freeze, no main collection) |
| C-SEM | Semantic judge conclusions | Qualified judge + frozen audit scope | — | **Withdrawn / unqualified** unless later accepted |

## Original study vs extension

| Body of work | Location | Rule |
| --- | --- | --- |
| Observer-framing preliminary study | `project/report/` (do not modify) | Separate findings; reproduce via project verify scripts |
| Extension methods / S4 draft | `report/methods-skeleton.md`, `report/slides-outline.md` | Update from this ledger; keep S4 fallback ready |
| Course delivery packaging | `delivery/` | Researcher submits; `submission_authorized=false` |

## Parallel SW06 coordination

- GPU operator: `bc-1121d0a4…` on WSL DESKTOP-VEMMES3 / RTX 3070 Ti.
- Orchestrator / SW04–SW07 CPU authors **must not** acquire the GPU lease or start a second qualification operator.
- Fresh v3-001 **FAIL** on main (#44/#45); prior FAIL rows (`C-G2-ORIG`, `C-G2-V2`, `C-G2-FRESH-V3`) preserved — do not rewrite.
- ECE-53 **done**: #46 merged `0290663` (format 24/24).
- ECE-59 **done**: #48 merged `430c86b` — TAB05 extreme **16/16**; live qual turns 16; probe-only turns 20 (evidence `results/development/sw06-tab05-extreme-residual-clearance-v1.json`).
- ECE-63: root greenlit **NEW** fresh G2; SW06 collecting on WSL; `g2_accepted=false` until batch finishes; requires **new** batch id (do not reuse v3-001).
- Cutoff: Nov 22 18:00 America/Toronto → automatic S4 if no accepted qual+freeze. `submission_authorized=false`.

## Do not

- Present catalog-v2 as a second independent held-out confirmation
- Soft-accept G2 on 87.5% completion or treat easy 85% as overall pass
- Reuse `qual-fresh-tab-catalog-v3-001` as fresh
- Soft-accept ECE-63 mid-collection (`g2_accepted` stays false until honest finish)
- Call development PASS “qualified”
- Invent main effects or exploratory pilot estimates as confirmation
- Soft-wash G2 FAIL or raise budgets as the primary remediation story
- Claim course submission readiness
