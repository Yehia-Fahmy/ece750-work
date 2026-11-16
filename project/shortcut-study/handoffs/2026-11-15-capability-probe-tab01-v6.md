# Capability probe TAB01 v6 (PASS)

Date (Toronto): 2026-11-15  
Branch: `cursor/tab01-slice-v6-fix-7581`  
Generator: `tab01-slice-v6`  
Exact sources at GPU run: `80bf93a` (later rebased onto `main` @ `916dd8b` for PR)

## Command

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
PYTHONPATH=project/shortcut-study/src python3 -m shortcut_study qualify-local \
  --capability-probe \
  --out project/runs/shortcut-study/capability-probe-tab01-v6b \
  --port 18084
```

Exit code: **0**. `capability_probe.passed`: **true**.

Prior failed attempt on the same host (`capability-probe-tab01-v6`, complete wrong answer 36) is preserved and was not overwritten.

## Verdict

| Cell | Result |
|------|--------|
| complete V00 | PASS — reads → **calculate** → submit authorized **57** |
| incomplete V00 | PASS — reads → typed insufficiency |

Soft calculate gate retained (authorized correct answers without calculate still allowed).

## Artifact hashes (`capability-probe-tab01-v6b`)

| File | sha256 |
|------|--------|
| `summary.json` | `586b6de9125922c3c58df038672ab26a98727ce6a51d838d489336c305c0c566` |
| `manifest.json` | `3365ce218adea4bcc1e7ef4cf440d569915f1626fab5398b94fe4f054c828ded` |
| `schedule.json` | `5c2c5d8b2df8a8c31f793fd1b13f2dfcbdaa797958cfb9f4b1042c334a175481` |
| `source-manifest.json` | `7f808a24d7c64e3de5078e5e0c2db15de7757edef393bde3f177051c702bdfa6` |
| `profile.json` | `a143100362cde528a158e3f358d46ae97f9c1ee25d52cae2c261a67a741b795c` |

Tracked evidence: `results/qualification/capability-probe-tab01-v6.json`.
