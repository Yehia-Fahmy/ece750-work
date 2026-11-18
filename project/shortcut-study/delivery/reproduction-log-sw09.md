# Reproduction log — SW09 final artifacts

- **Date (UTC):** 2026-11-18
- **Operator:** SW09 report/build author (`bc-be59bae5…`); **no GPU** this session
- **Input tip:** `origin/main` @ `231da6d87ae9e65f370183ce8cb5862a5526f189` (SW08 booked)
- **Branch:** `cursor/sw09-final-report-deck-6044`
- **Scope:** Git-alone build + number verification + visual PDF/deck inspection
- **`submission_authorized`:** remains **false** (not flipped)

## Commands and outcomes

### 1. Build report + deck

```sh
pip install -r project/shortcut-study/report/requirements.txt
python3 project/shortcut-study/report/build_report.py
python3 project/shortcut-study/report/build_slides.py
python3 project/shortcut-study/report/verify_report_numbers.py
```

| Check | Result |
| --- | --- |
| `final-report.pdf` | **5 pages** built |
| `slides.pdf` | **10 pages** built |
| `verify_report_numbers.py` | **VERIFY OK** vs `results/main/main-s0-tab-v0-20261118-stats.json` |
| `submission_authorized` in stats | **false** |

### 2. Headline number reconciliation

| Claim | Source | Match |
| --- | --- | --- |
| 318/320 @ 99.375% | stats `completed` / `completion_rate` | yes |
| T=0.2 | stats `sampling.temperature` + ECE-90 | yes |
| complete 51/158 = 32.3% | stats information_state_authorized | yes |
| incomplete 8/160 = 5.0% | same | yes |
| Δ +27.3 pp | delta_complete_minus_incomplete | yes |
| easy 28/80 = 35% | easy_no_shortcut | yes |
| acquisition.successful 0/0 | shortcut_acquisition_successful | yes |
| format failures 2 | terminal_counts / ids | yes |

### 3. Preservation (observer protected subset)

All `project/report/*` hashes in `preservation-manifest.json` **matched** after SW09 edits (extension-owned paths only changed).

### 4. Visual inspection

| Artifact | Pages inspected | Notes |
| --- | --- | --- |
| `report/final-report.pdf` | 1–5 | No blank page; figure/table legible; footer shows `submission_authorized=false` |
| `report/slides.pdf` | 1–10 | Landscape deck; key contrasts + acquisition honesty present |

Raster previews produced under `/tmp/sw09-visual/` during authoring (not committed).

### 5. Not claimed this session

| Check | Reason |
| --- | --- |
| Raw main archive rehash | Ignored `project/runs/.../main-s0-tab-v0-20261118` absent on this host |
| GPU re-collection | Not required for packaging; SW08 already booked |
| G6/WP12/WP13 gate flip in `state.json` | Integrator-owned; needs **independent** reviewer ≠ author |
| Course LMS upload | Researcher-only; `submission_authorized=false` |

## Next safe action

Independent reviewer ≠ SW09 author inspects this tip’s PDF/deck/numbers/manifest. Do **not** flip `submission_authorized`. Do **not** treat this packaging PR as course submission.
