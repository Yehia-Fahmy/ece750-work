# Shortcut-study report (WP12 / SW09)

**Active package (2026-11-18):** SW09 final artifacts after SW08 main booking on tip `231da6d`. Scope is **behavioral S0** (`main-s0-tab-v0-20261118`, 318/320 @ T=0.2). Semantic conclusions remain withdrawn. `submission_authorized=false`.

The earlier S4 Markdown draft remains historical fallback prose in [`methods-skeleton.md`](methods-skeleton.md); it is **not** the current claim set. Use [`final-report.md`](final-report.md) / [`final-report.pdf`](final-report.pdf) for submission-oriented reading.

| Artifact | Role |
| --- | --- |
| [`final-report.md`](final-report.md) | Integrated course report source (S0 behavioral main) |
| [`final-report.pdf`](final-report.pdf) | Built PDF (provisional 4-page core + references/appendix) |
| [`info-contrast.png`](info-contrast.png) / [`info-contrast.pdf`](info-contrast.pdf) | Figure 1 from tracked stats |
| [`slides.md`](slides.md) / [`slides.pdf`](slides.pdf) | Final deck source + PDF |
| [`speaker-notes.md`](speaker-notes.md) | Speaker notes |
| [`build_report.py`](build_report.py) / [`build_slides.py`](build_slides.py) | Reproducible builders |
| [`verify_report_numbers.py`](verify_report_numbers.py) | Clean-checkout number check vs stats JSON |
| [`requirements.txt`](requirements.txt) | Report/deck Python deps |
| [`claim-evidence-ledger.md`](claim-evidence-ledger.md) | Claim → artifact table |
| [`methods-skeleton.md`](methods-skeleton.md) | Historical S4 draft (superseded for main claims) |
| [`slides-outline.md`](slides-outline.md) | Early outline (superseded by `slides.md`) |
| [`../delivery/`](../delivery/) | Packaging / reproduction / checklist |

Protected observer study remains at [`project/report/`](../../report/) — do not modify.

## Build

```bash
pip install -r project/shortcut-study/report/requirements.txt
python3 project/shortcut-study/report/build_report.py
python3 project/shortcut-study/report/build_slides.py
python3 project/shortcut-study/report/verify_report_numbers.py
```
