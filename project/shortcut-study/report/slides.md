# ECE 750T · Shortcut acquisition under declared T/J visibility
Yehia Fahmy · Behavioral S0 main · Nov 18, 2026 · submission_authorized=false

---
# Question
Does declaring task-reviewer access to intermediate reasoning (T) and/or justification (J) change prohibited shortcut **acquisition** in a local tool environment?

---
# Design (frozen S0)
Matched factorial: info × shortcut present/absent × V00/V01/V10/V11
TAB01–05 only · 20 bases × 16 cells × 1 seed = **320** assigned
Local Qwen3-4B / llama.cpp / RTX 3070 Ti · zero cloud inference
Semantic judge **withdrawn** (behavioral-only)

---
# Path to main
CPU repairs SW01–03 → fresh G2 PASS (v5-001) → G3 signed freeze
ECE-90 errata: sampling **T 0.6→0.2** (match qualification)
SW08 main booked on tip **231da6d** (collection tip e29e158)

---
# Completion
**318 / 320** completed (99.375%)
2 TAB05 `model_format_failure` retained in denominator
Wall ≈ 0.72 GPU-h · memory check passed
Native-capture suite flag fails as expected with 2 non-completed

---
# Key behavioral contrasts
Complete-info authorized: **32.3%** (51/158)
Incomplete-info authorized: **5.0%** (8/160)
Δ = **+27.3 pp**
Easy no-shortcut authorized: **35%** (28/80)
First op `list_resources`: **100%**

---
# What did *not* move much
Shortcut present vs absent authorized: 17.6% vs 19.5%
Visibility V00–V11 authorized: ~17.5–20%
Do not narrate a large visibility main effect from these rates

---
# Acquisition honesty
`acquisition.successful` = **0** on all completed cells
Discovered listings ≠ successful acquisition
**No confirmatory shortcut-use claim** from acquisition flags alone

---
# Limitations + AI
Single local actor · T ≠ thought · semantic conclusions withdrawn
Temp errata + 2 format failures disclosed
AI assistance used extensively for code/drafting/tooling
Course upload remains **researcher-only**

---
# Takeaway
Measured behavioral S0 archive with honest denominators
Large info-state gap; small visibility/shortcut gaps; zero successful acquisitions
Prefer limited claims over a forced deception story
