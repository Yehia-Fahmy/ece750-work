# Packaging manifest — SW09 S0 behavioral package

- **Base tip for this inventory:** SW08 booked main on `231da6d` (collection tip `e29e158`)
- **Tier:** S0 TAB-only frozen main (`s0-tab-v0`), **behavioral-only**
- **Run:** `main-s0-tab-v0-20261118` — assigned 320; completed **318**; format failures **2**
- **Sampling:** T=**0.2** / top_p=0.95 (ECE-90 errata)
- **Submission authorized:** **false** (researcher LMS upload only)
- **Independent acceptance:** required from a reviewer **≠** SW09 author before G6/WP12/WP13 acceptance

Historical S4 packaging inventory remains in [`packaging-manifest.md`](packaging-manifest.md) as dated evidence.

## A. Ships from Git (tracked)

### A1. Final report / deck

| Path | Role |
| --- | --- |
| `report/final-report.md` | Integrated course report source |
| `report/final-report.pdf` | Readable PDF |
| `report/info-contrast.png` / `.pdf` | Figure 1 |
| `report/slides.md` / `slides.pdf` | Final deck |
| `report/speaker-notes.md` | Speaker notes |
| `report/build_report.py` / `build_slides.py` / `verify_report_numbers.py` | Build + verify |
| `report/requirements.txt` | Deps |
| `report/claim-evidence-ledger.md` | Claim ledger (includes C-MAIN-S0-*) |

### A2. Main evidence

| Path | Role |
| --- | --- |
| `results/main/main-s0-tab-v0-20261118.json` | SW08 booking evidence |
| `results/main/main-s0-tab-v0-20261118-stats.json` | Behavioral contrasts |
| `handoffs/2026-11-18-sw08-main-s0-tab-v0.md` | Collection handoff |
| `configs/frozen/s0-tab-v0/` | Signed freeze (+ ECE-90 temp errata) |

### A3. Observer preliminary (protected; unchanged)

| Path | Role |
| --- | --- |
| `project/report/final-report.md` / `.pdf` | Original study |

## B. Local raw authenticity (ignored)

| Local path | Ties to |
| --- | --- |
| `project/runs/shortcut-study/main-s0-tab-v0-20261118/` | Main booking JSON / assumptions |

Absent on clean cloud checkouts; tracked stats still reproduce report numbers.

## C. Explicit non-claims

| Item | Honesty |
| --- | --- |
| Semantic T/J conclusions | **Withdrawn** |
| Shortcut *use* from `acquisition.successful` | **Not claimed** (count = 0) |
| Course LMS upload | **Not authorized** (`submission_authorized=false`) |
| G6 / WP12 / WP13 acceptance | Pending **independent** reviewer ≠ author |
