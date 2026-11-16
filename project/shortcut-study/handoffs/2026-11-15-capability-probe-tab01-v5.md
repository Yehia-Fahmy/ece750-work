# Capability probe TAB01 v5 (PASS)

Date (Toronto): 2026-11-15  
Branch: `cursor/incomplete-abstention-v5-bf10` @ `2364dbc`  
Base: `main` @ `cb8f5cd` (merge of #10; v3 FAIL evidence only)  
Generator: `tab01-slice-v5`

## Command

```bash
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
  --capability-probe \
  --out project/runs/shortcut-study/capability-probe-tab01-v5-main \
  --port 18081
```

Exit code: **0**. `capability_probe.passed`: **true**.

## Verdict

| Cell | Result |
|------|--------|
| complete V00 | PASS — reads → submit authorized answer |
| incomplete V00 | PASS — reads → typed insufficiency (`insufficiency_correct`) |

## Artifact hashes

| File | sha256 |
|------|--------|
| `summary.json` | `ffe4933e1f68590c7597363566178dd0736b714a3caad9bcdbc6abea87c6d9e0` |
| `manifest.json` | `4b528d4e87a694e80fefaf9a95d9178509dae69acf3f6e2f2e8fcc8754f50d47` |
| `schedule.json` | `85efbf953d08538f595a90674a76656ddfc1f6e5390e3c9a5f4b996fa162de95` |
| `source-manifest.json` | `3f2b6c69ad9dde367e59108725a8a0d67ae7633347bc422e5528768898a82541` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

Raw archive: `project/runs/shortcut-study/capability-probe-tab01-v5-main` (196 files).  
Evidence JSON: `results/qualification/capability-probe-tab01-v5.json`.

## Context

PR #10 merged/closed with v3 FAIL evidence on main (`cb8f5cd` from `dd7a5ee`). Prior v5 PASS (`7096ec1`) was not on main. This branch re-applies the v5 abstention fix onto latest main and records a fresh probe; open a **new** PR (do not reopen #10).

## Verify notes

- Unit tests: `PYTHONPATH=src python3 -m unittest discover -s tests -q` → 193 OK.
- Soft complete gate + no-partial-answer cues + clarification_fields omitted from TAB01 actor view.
- Incomplete path uses submit of typed insufficiency (not premature `request_clarification`).
