# Reproduction log — S4 packaging check (WP13 / G6)

- **Date (UTC):** 2026-11-17
- **Operator role:** packaging / independent reproduction (CPU cloud agent); **no GPU** this session
- **Input tip:** `origin/main` @ `d0b65c3913ec20808d7d23658c543eda3f977b18` (#26 S4 declaration merged)
- **Branch:** `cursor/g6-wp13-s4-delivery-7177`
- **Scope:** Git-alone derived checks for S4 course package; raw authenticity and GPU re-run **not** claimed here

## Commands and outcomes

### 1. Historical preservation hashes

```sh
# Verify all 111 historical_files_sha256 + design snapshot against working tree
python3 - <<'PY'
# (inline sha256 check against project/shortcut-study/preservation-manifest.json)
PY
```

| Check | Result |
| --- | --- |
| Historical tracked files | **111/111 match** |
| Design snapshot `project/shortcut-study-design-v2.md` | **match** |
| Failures / missing | **0** |

### 2. Observer-study statistical reproduction (Git-alone)

```sh
PYTHONPATH=project/src python3 project/verify_final_results.py
```

| Check | Result |
| --- | --- |
| Derived rows | **240** verified |
| Primary / secondary / correctness / control stats | **reproduced** |
| Notes | Statistical reproduction only; not raw-source authenticity; not semantic-label validation |

### 3. Extension unit tests (CPU; after `pip install -r project/shortcut-study/requirements.txt`)

```sh
cd project/shortcut-study
PYTHONPATH=src:../../project/src:. python3 -m unittest discover -s tests -q
```

| Check | Result |
| --- | --- |
| Tests | **213 passed** in ~9.7s |
| GPU / model inference | **none** |
| Note | Clean environment needed `jsonschema` from `requirements.txt` |

### 4. Report count reconciliation (tracked qualification JSON only)

Compared narrative figures in `report/methods-skeleton.md` §5.1–§5.2 / §7.1 to committed JSON:

| Claim in draft | Source field | Match |
| --- | --- | --- |
| G2 #23 completion **238/320 = 74.38%** | `gates.G2-GPU-2.terminal_completion` in `g2-held-out-20261116.json` | **yes** |
| G2 #23 easy **11/20 = 55%** | `gates.G2-GPU-3.authorized_success` | **yes** |
| G2 #25 completion **239/320 = 74.69%** | `g2-held-out-20261116-catalog-v2.json` | **yes** |
| G2 #25 easy **11/20 = 55%**; TAB02 **0/4** | same file `per_template` | **yes** |
| v6 16-cell **16/16** PASS | `native-qualification-tab01-v6-16cell.json` verdict notes | **yes** |
| Main acquisition-by-visibility rates | — | **absent by S4 decision** (correct) |

### 5. Link / path audit (submission-oriented)

| Path class | Status |
| --- | --- |
| Cited `results/qualification/*.json` in report | Present on disk |
| S4 / WP12 handoffs | Present |
| `project/runs/shortcut-study/` | **gitignored** — expected absent on this cloud checkout; authenticity package is local-only |
| `results/main/<run_id>/` | **absent** — correct under S4 |

### 6. Not run (honest gaps)

| Check | Reason |
| --- | --- |
| Raw archive rehash vs embedded sha256 | Raw trees not present on this agent host |
| `finalize_analysis.py` observer raw audit | Needs local `project/runs/` + `project/data/` |
| GPU `qualify-local` re-run | No GPU authorization / lease this session; S4 does not require regenerating FAIL archives to package the narrative |
| Extension course PDF visual inspection | PDF not yet generated |
| Slide deck visual inspection | Outline only; deck **TBD** |

## Reproduction classes satisfied this session

| Class | Satisfied? |
| --- | --- |
| Git-alone derived narrative + observer stats + extension tests | **Yes** |
| Local raw authenticity | **No** (archives not on host; documented in packaging manifest §B) |
| GPU re-run | **No** (not required for packaging; documented in §C) |

## Next safe action

Lagging reviewer inspects this delivery set + WP12 Markdown draft. Yehia produces PDF/slides and performs course submission when authorized. Do **not** start main collection. Do **not** flip `submission_authorized` from packaging alone.
