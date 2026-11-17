# Packaging manifest — S4 course package (WP13)

**Historical packaging inventory at the base below.** The later [completion handoff](../SWARM_START.md) assigns a gated S0 attempt with S4 fallback and delegates all artifact production to agents. “Yehia packaging/only” labels in this dated inventory describe prior ownership, not current instructions. Keep its recorded hashes as evidence; publish a new final manifest after completion. Existing “held-out” labels retain archive names but do not establish freshness: the review found all worlds reused in the second run.

- **Base tip (includes #26 S4 declaration):** `d0b65c3913ec20808d7d23658c543eda3f977b18`
- **Tier:** S4 honest course fallback (`primary_actor_episodes = 0`)
- **Frozen protocol:** none (`frozen_protocol = null`; G3 canceled)
- **Submission authorized:** **false** (researcher action only)

This manifest separates three reproduction classes required by `ARTIFACT_CONTRACTS.md`:

1. **Git-alone** — clean checkout of this repository.
2. **Local raw archive** — ignored trees under `project/runs/shortcut-study/` (and original `project/runs/` for the observer study).
3. **GPU re-run** — fresh local inference on RTX 3070 Ti (not required to *read* the course narrative; required only to regenerate raw actor archives).

Do **not** duplicate model blobs or raw episode trees into `delivery/`.

---

## A. Ships from Git (tracked; required for course narrative)

### A1. Extension planning / status

| Path | Role |
| --- | --- |
| `project/shortcut-study/README.md` | Extension entry + S4 status |
| `project/shortcut-study/state.json` | Gates, WP status, S4 decision block |
| `project/shortcut-study/preservation-manifest.json` | Historical hash lock |
| `project/shortcut-study/handoffs/2026-11-17-s4-honest-course-fallback.md` | S4 declaration |
| `project/shortcut-study/handoffs/2026-11-17-wp12-s4-report.md` | WP12 S4 draft handoff |
| `project/shortcut-study/delivery/*` | This packaging set |

### A2. WP12 report (Markdown draft; PDF still Yehia)

| Path | Role |
| --- | --- |
| `project/shortcut-study/report/README.md` | Report directory status |
| `project/shortcut-study/report/methods-skeleton.md` | S4 course-report draft |
| `project/shortcut-study/report/slides-outline.md` | Slide outline (no deck template in-repo) |

### A3. Historical observer study (untouched; preliminary evidence)

| Path | Role | sha256 @ `d0b65c3` |
| --- | --- | --- |
| `project/report/final-report.md` | Completed observer Markdown | `a893afee4c1728572e0b66c854ffa152b185499d9adc9ce4510553dfc0fc184b` |
| `project/report/final-report.pdf` | Completed observer PDF | `6c8b58b29b690e5e0ad0a3dc30f81ecbcd43aa5dacfd4210370814e82dd6feb9` |
| `project/results/final-automated-evaluation.json` | Derived rows for observer stats | `e950d187debab62bc639617aa8abeebf3a932c9285b894430a0b4eae503db4a0` |

### A4. Measured extension evidence (tracked qualification / development JSON)

Evidence kind is encoded in each JSON (`local_model_*_not_main` / held-out FAIL). **None of these are a main factorial.**

| Path | Role | sha256 @ `d0b65c3` |
| --- | --- | --- |
| `results/qualification/capability-probe-tab01-v6.json` | TAB01 v6 probe **PASS** | `cda4b7a61c7a0c1a88b9e2994d2e299971ad3ae26235c1c5ecfa14f4a5031b14` |
| `results/qualification/native-qualification-tab01-v6-16cell.json` | TAB01 v6 16-cell **PASS** | `d14d3f9f0a9e8abb3dea6e87191e83ab56476c64c3c3c87cbf8bd8c86a1afb47` |
| `results/qualification/native-qualification-tab01-v5-16cell.json` | Prior v5 16-cell **FAIL** (preserved) | `d2e5894a3a46edbc47daa6568ce2dbf566019b1e18cd2547afdcb9dc431182ef` |
| `results/qualification/g1-long-pilots-20261116.json` | Long-pilot telemetry (9/10; not G1 accept) | `a23980475a91d61d9cb6dc871114a84daf27d3dfe7c8f2cc4b3bb3e1aa9c533d` |
| `results/qualification/g2-held-out-20261116.json` | G2 FAIL #23 | `d220ac92be0f8244f166d450a03c37d5f03082d1d0adce5d014b8cc1bee959e1` |
| `results/qualification/g2-held-out-20261116-catalog-v2.json` | G2 FAIL #25 | `609e0d3354162fc8f4bd4d238cb7d5200cd2fcabef94d7e3c0e3444a46bb3643` |
| `results/qualification/g2-held-out-packaging-v1.json` | CPU held-out packaging (not G2 accept) | `ca5bb747f1cfa7e6638c6e8057ed574c4ac203aa2920f68ae70638e274b81a2f` |
| `results/development/tab-catalog-v2-public-task-port.json` | Catalog-v2 CPU port (#24) | `17727bb00f9b65350287ecd9604a048c60b0ff2d17164b645b7b2793cd1b213d` |
| `results/development/cpu-vertical-slice-v1.json` | Mock CPU vertical slice | `97ea2a4ebd79dc82bb869efe04cfab08dc5e5b66095170722c56eabaece2c6d4` |
| `results/development/wp07-analysis-scaffold-v1.json` | Synthetic analysis harness only | `a4336c4a2df03c312489ccfcfe1e6a61f123e6541f9fadea9311e3f7511d83a2` |

Paths above are relative to `project/shortcut-study/` except observer paths.

### A5. Explicitly **not** in Git (and not claimed as course main results)

| Missing / empty | Honesty |
| --- | --- |
| `configs/frozen/<protocol_version>/` | Never committed under S4 |
| `results/main/<run_id>/` | No main collection |
| Extension course PDF | Not generated; Yehia packaging |
| Final slide deck / speaker notes | Outline only; deck **TBD** |

---

## B. Needs local raw archives (authenticity; not required for Git-derived narrative)

Tracked qualification JSON embeds archive hashes and summary counts. Full raw requests/responses/events live under **gitignored** trees:

| Local path (host DESKTOP-VEMMES3 / WSL canonical checkout) | Ties to tracked evidence |
| --- | --- |
| `project/runs/shortcut-study/capability-probe-tab01-v6b` (or sibling probe dirs named in JSON) | `capability-probe-tab01-v6.json` |
| `project/runs/shortcut-study/native-qualification-tab01-v6-16cell` | `native-qualification-tab01-v6-16cell.json` |
| `project/runs/shortcut-study/native-qualification-tab01-v5-16cell` | v5 FAIL preserve |
| `project/runs/shortcut-study/g1-long-pilots-20261116` | long pilots |
| `project/runs/shortcut-study/g2-held-out-20261116` | G2 FAIL #23 |
| `project/runs/shortcut-study/g2-held-out-20261116-catalog-v2` | G2 FAIL #25 |
| `project/runs/` + `project/data/` (original observer epochs) | Observer raw-source audit via `finalize_analysis.py` |

**Cloud / clean-laptop checkouts without these trees can still:**

- read the S4 report draft and tracked qualification summaries;
- reproduce observer **statistics** via `project/verify_final_results.py`;
- run extension unit tests (CPU).

They **cannot** re-verify raw HTTP/tool byte authenticity without the local archives.

Pinned model/runtime assets under ignored `project/data/shortcut-study/assets/` are likewise local-only; do not commit them.

---

## C. Requires GPU re-run (RTX 3070 Ti; zero external inference)

| Action | When needed | Not needed for |
| --- | --- | --- |
| Re-run `qualify-local` development / held-out commands | Regenerating raw actor archives or attempting a *new* held-out after a real lever | Reading S4 narrative; citing existing FAIL/PASS JSON |
| Fresh semantic judge episodes | Never under S4 (judge claims withdrawn) | Course package |
| Main factorial collection (WP09) | **Canceled** under S4 — do not start | — |

Any GPU re-run must use the canonical lease (`project/runs/shortcut-study/gpu.lock`), owned offline server, and pinned local checkpoint. Re-running does **not** rewrite historical FAIL archives; new outputs need a new `run_id`.

---

## D. Claims retained vs withdrawn (package-level)

Copied from `state.json` → `s4_decision` / S4 handoff — packaging must not soft-wash:

**Retained:** observer study; extension methods/stack; TAB01 v6 development PASS; long-pilot telemetry; two G2 FAIL archives; limitations + AI disclosure.

**Withdrawn:** main S0/S1/3200 factorial; G2 pass; freeze; WP09–WP11 confirmatory findings; semantic-judge conclusions; visibility-effect estimates from development or failed held-out.
