# Frozen tree — `s0-tab-v0`

**Status:** `frozen_signed` — G3 accepted (ECE-87).

- `freeze.signed` is **true**; accepting owner **Yehia F**.
- Freeze timestamp: `2026-11-17T22:45:00-05:00` (America/Toronto).
- Freeze commit (scientific tip at signature): `571d88865ee3d2d83ea152275b58436fccacc06c`.
- Scope remains **behavioral-only** with semantic withdrawal (SW07-B).
- `submission_authorized` remains **false**.
- Runners accept `split=main` only with this signed matching tree.
- Independent freeze review must be someone other than the signature-PR author before merge.
- SW08 GPU main collection is permitted only after merge + explicit kickoff — not started here.

## Errata (ECE-90)

Yehia-authorized freeze errata on main tip `cbe74a8+`:

- `primary_actor.sampling.temperature`: **0.6 → 0.2**
- Reason: align frozen main decoding with accepted G2 qualification sampling (`configs/development/local-qualification.json` T=0.2; `qual-fresh-tab-catalog-v5-001`).
- Component `sha256` pins re-computed; `freeze.signed=true`, `g3_status=accepted`, `accepting_owner=Yehia F`, and `submission_authorized=false` unchanged.
- Independent review of this errata PR must be someone **other than** the errata PR author before merge.
