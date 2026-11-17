# Package handoff — SW07 freeze prep (draft stubs only) — 2026-11-17

- Owner and role: orchestrator / integrator (`bc-ece62cad…`); **CPU prep only**
- Status: draft_in_progress — **not a freeze**; G3 remains unsigned
- Depends on: accepted SW05 (done); **accepted SW06 fresh G2** (in progress on WSL — do not duplicate)
- Input commit: `91baf90`
- Output paths:
  - `results/qualification/sw07-freeze-prep-v1.json`
  - `results/qualification/freeze-checklist-s0-tab-post-sw05.md` (unsigned delta checklist)
  - this handoff
- Concrete behavior:
  - Restate that runners must keep rejecting `split=main` until a **signed** `configs/frozen/<version>/` path exists
  - List post-SW05 CPU prerequisites that are now available vs still blocked on SW06
  - Do **not** create `configs/frozen/`; do **not** remove main guards; do **not** claim G3
- GPU: **no GPU work**; SW06 operator is `bc-1121d0a4…` on DESKTOP-VEMMES3
- Next safe action after SW06 accept: promote provisional → frozen with hashes, materialize main schedule, add guarded executable path + tests, independent freeze review — only then G3

## Guarded main path requirements (design notes for later implementation)

When SW06 accepts and freeze is authorized, the executable main path must:

1. Require accepted versioned freeze directory + exact source/config/checkpoint/template/policy/schedule hashes
2. Reject unsigned, provisional, or mismatched manifests
3. Use disjoint main instances from development / consumed-qual / fresh-qual
4. Keep assigned denominator, paired/counterbalanced order, technical retry/recovery rules
5. Preserve interrupted/unattempted IDs without replacing attempted outcomes
6. Leave draft-era main-refusal tests intact; add separate frozen-path tests

Until then: keep current main refusal; treat all provisional configs as non-authoritative.
