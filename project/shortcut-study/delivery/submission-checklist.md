# Submission checklist — S4 course package

**Course report due:** 2026-12-04 (America/Toronto; 11:59pm under general written-work policy).  
**Presentation date / official page limit:** **TBD** (reconcile with instructor instructions).  
**`state.json` → `constraints.submission_authorized`:** **false** — this checklist does **not** authorize upload.

Legend: **Ready** = available from Git / already done · **Yehia-only** = researcher action or local machine · **Blocked/TBD** = unresolved course logistics

---

## A. Ready from Git (packaging / review)

- [x] S4 declared on `main` via [#26](https://github.com/Yehia-Fahmy/ece750-work/pull/26); `primary_actor_episodes = 0`
- [x] WP12 Markdown draft: `report/methods-skeleton.md` (methods + pilots + dual G2 FAIL + withdrawals; **no fabricated main results**)
- [x] Gate honesty in report/README + state: G0 accepted; G2 failed; G3/G4/G5 canceled; WP09–WP11 canceled
- [x] Tracked qualification evidence for all cited pilot / FAIL numbers
- [x] Historical observer report untouched: `project/report/final-report.md` + PDF
- [x] Preservation: 111/111 historical hashes match (checked in `reproduction-log.md`)
- [x] Observer stats reproduce: `project/verify_final_results.py`
- [x] Extension CPU tests: 213 passed (with `requirements.txt`)
- [x] WP13 delivery artifacts: `delivery/packaging-manifest.md`, `reproduction-log.md`, this checklist
- [x] Slide **outline** present: `report/slides-outline.md` (no in-repo deck template)
- [x] AI disclosure draft present in methods skeleton
- [x] Explicit statement that semantic-judge claims are withdrawn
- [x] Explicit empty main-results slots (not filled with development stand-ins)

## B. Yehia-only before / at submission

- [ ] Confirm official page limit and presentation date/format with course instructions
- [ ] Produce extension **course PDF** from S4 Markdown (four-page core + separated appendices/references until limit known); do not invent numeric main contrasts
- [ ] Produce **slide deck + speaker notes** from `report/slides-outline.md` (deck shell/template **TBD** — none shipped in this repo)
- [ ] Optional: generate compact **pilot-only** summary tables/figures for the four-page core (sourced only from tracked qualification JSON)
- [ ] Finalize AI-disclosure wording to match actual assistance used in the submitted PDF
- [ ] On the research machine: confirm local raw archives listed in packaging manifest §B still present if authenticity questions arise
- [ ] Visual PDF/slide inspection (links, figures vs tables, no soft-washed G2)
- [ ] Set / keep scope claims in the submitted PDF to **S4 (0 main episodes)** — not 320 or 3,200
- [ ] **Course upload / LMS submission** — researcher only; flip `submission_authorized` only under explicit Yehia authorization
- [ ] Do **not** start WP09 main collection or rewrite FAIL archives as part of packaging

## C. Explicitly out of scope for Dec 4 (do not treat as incomplete homework)

- [x] G2 pass / main-qualified actor — **failed**; not required under S4
- [x] G3 freeze / `configs/frozen/` — **canceled**
- [x] WP09–WP11 confirmatory main analysis — **canceled**
- [x] Independent semantic-judge conclusions — **withdrawn**
- [x] Visibility acquisition-effect estimates from development or failed held-out — **withdrawn**

## D. Ready vs Yehia-only summary

| Item | Owner |
| --- | --- |
| S4 declaration + state honesty | Ready (Git; lagging review of this packaging PR) |
| Methods / limitations / evidence tables (Markdown) | Ready for review |
| Delivery manifest + reproduction log + checklist | Ready for review |
| Slide outline | Ready (outline only) |
| Extension PDF | **Yehia-only** |
| Final slide deck / speaker notes | **Yehia-only** (template TBD) |
| Page limit / presentation logistics | **TBD** |
| LMS / course submission | **Yehia-only** (`submission_authorized=false`) |
| Raw archive authenticity rehash | **Yehia-only** (local machine) |
| GPU re-run of held-out | Not required for S4 package; **Yehia-only** if attempted later |
