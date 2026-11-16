# Provisional S0 TAB-only package (`s0-tab-v0`)

**Status:** `draft_not_frozen` — WP08/G3 template only. No freeze commit, no accepting signature, no main schedule materialization.

## Intended scientific MVP (if gates pass)

| Element | Provisional choice |
| --- | --- |
| Tier | **S0** (default MVP from scope ladder) |
| Families | TAB only (`TAB01`–`TAB05`) |
| Bases | 20 (5 templates × 4 difficulties × 1 instance) |
| Factorial | 2 info × 2 availability × 4 visibility = 16 / base |
| Seeds | **1** (`replicate_seed=0`) |
| Primary actor episodes | **320** assigned denominator |
| Optional second actor | Out |
| Semantic claims | Withdrawn unless WP05 live judge qualifies before real freeze |

## What is here

| File | Role |
| --- | --- |
| `manifest.json` | Machine-readable draft freeze manifest (unsigned) |
| `scope.json` | Locked-in-provisional scope vs withdrawn 3,200 plan |
| `splits_reservation.json` | Smoke/dev/qual/main generation-seed + prefix reservations |
| `schedule_plan.json` | Combinatorial assigned-denominator plan (IDs not materialized) |
| `budgets.json` / `visibility.json` / `policy.json` / `a_t_j_boundaries.json` | Protocol candidates copied from development with draft status |
| `analysis_protocol.json` | Confirmatory T/J plan twin (still draft) |
| `actor_profile.json` | Unqualified local actor candidate pins |
| `scoring_source_of_truth.json` | Deterministic vs semantic ownership |
| `retry_recovery.json` | Terminal/retry/stop candidates |
| `reduced_claims.json` | Explicit claim reductions vs original course-core plan |

Human checklist draft: `results/qualification/freeze-checklist-s0-tab-draft.md` (all items unchecked).

## Hard rules

1. Leaving an item unchecked is correct until evidence exists.
2. Agent review ≠ human scientific validation (G3).
3. Promoting this tree into `configs/frozen/` without G2 evidence is forbidden.
