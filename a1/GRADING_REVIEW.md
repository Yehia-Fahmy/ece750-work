# Assignment 1 — Grading Review & Recommendations

**Course:** ECE 750T (Responsible AI)  
**Submission reviewed:** `a1/` on `main` (commit `c314035`)  
**Reviewer stance:** instructor / grader  
**Companion PR:** code/report conciseness edits are in a separate PR (`cursor/a1-concise-fixes`). This document is feedback only.

> **Scope note.** The official handout `A1.pdf` is gitignored and was not present in this review environment. Requirements below are reconstructed from the supplied starter contracts (`student.py` docstrings, `train.py`, `check_metrics.py`, `data.py`) and from the standard Creager-style fair-classification exercise this assignment clearly follows (Adult + accuracy / reweighted accuracy / \(\Delta_{DP}\), soft DP regularizer, and the three written probability questions). If the local handout asks for extra prose (e.g., fairness interpretation of correlated features), treat those rows as “verify against PDF.”

---

## Overall verdict

**Strong submission.** The required implementations are correct, the experimental protocol is reproducible and avoids test-set peeking for \(\alpha\) selection, numerical results are internally consistent, and the written proofs for Question 2 are essentially complete.

**Estimated grade band (assuming equal weight on coding + write-up completeness):** high A / near-full credit, with only minor presentation and “design discussion” polish items left.

| Area | Score (informal) | Comment |
| --- | --- | --- |
| Q1.1 correlations | Full | Correct ranking rule; signed values reported |
| Q1.2 baseline metrics | Full | Numbers match saved JSON; male higher positive rate |
| Q1.3 prediction correlations | Full | All / \(A{=}0\) / \(A{=}1\) top-3 correct |
| Q1.4(a) penalty + differentiability | Near-full | Correct soft squared gap; could mention \(\lvert\cdot\rvert\) kink explicitly |
| Q1.4(b) \(\alpha\) sweep + plots | Full | Sensible range; trade-off discussed; non-monotonic DP noted |
| Q2.1 independence vs conditional dependence | Full | Classic XOR construction, check is correct |
| Q2.2 independence + separation | Full | Nondegenerate ternary-\(Y\) example works |
| Q2.3 \(\mathrm{RWAcc}_A\) lower bound | Full | Construction \(h\in\{g,1-g\}\) is the intended one |
| Code quality / checks | Full | Passes public metric checks; gradients verified |
| Reproducibility / disclosure | Full | README commands + GenAI disclosure present |

---

## Requirements checklist

### Coding contracts (`student.py`)

| Requirement | Evidence | Result |
| --- | --- | --- |
| Pearson correlations per feature column | `correlations()` matches `np.corrcoef`; constants → `nan` | Pass |
| Rank outside the function by \(\lvert\rho\rvert\), tie-break by column index | `run_analysis.ranked` | Pass |
| Predictions via `score >= 0.5` | `metrics()` | Pass |
| Accuracy, reweighted accuracy \(\frac12(\mathrm{acc}_0+\mathrm{acc}_1)\), \(\Delta_{DP}=\lvert\mathrm{rate}_0-\mathrm{rate}_1\rvert\) | `metrics()` + `check_metrics.py` | Pass |
| Missing group → `None` rates and dependent aggregates | Explicit empty-group case in checks | Pass |
| JSON-serializable Python `int`/`float`/`None` | Return types | Pass |
| Differentiable DP penalty on soft scores | `dp_penalty` = squared mean-score gap; autograd nonzero when groups differ | Pass |
| Training loop skips penalty if a batch lacks a group | Handled in supplied `train.py` | Pass (not student-owned) |

### Experimental / write-up requirements

| Requirement | Evidence | Result |
| --- | --- | --- |
| Q1.1: top-10 features vs \(Y\) and vs \(A\) on **train** | Report + `results/q11_correlations.json` | Pass |
| Q1.2: test accuracy, RW accuracy, \(\Delta_{DP}\); which group has higher \(\widehat Y\) | Report matches `q14_metrics.json` \(\alpha=0\) | Pass |
| Q1.3: top-3 correlations of features with \(\widehat Y\) overall and within each \(A\) | Report + `q13_correlations.json` | Pass |
| Q1.4: soft DP regularizer explained; \(\alpha\) range justified; metrics vs \(\alpha\) plotted | Report §1.4 + three PNGs | Pass |
| Fixed training settings (seed 0, 10 epochs, batch 256, Adam \(10^{-3}\), WD \(10^{-5}\), 64 hidden) | README + `train.py` defaults | Pass |
| Written Q2.1–Q2.3 | Report §2 | Pass |
| Assistance disclosure | Report end matter | Pass |

---

## Question-by-question commentary

### Q1.1 — Feature correlations
Correct and complete. Marriage / relationship features dominate both lists, which is the expected Adult pattern and sets up the fairness story for later parts. No correctness issues.

**Optional enrichment (not required unless the PDF asks):** one sentence noting that several top-\(Y\) features are also strongly tied to sex would show conceptual engagement.

### Q1.2 — Unregularized classifier
Numbers are consistent with the saved run. Male (\(A=1\)) positive rate \(0.2587\) vs female \(0.0880\) is clearly stated. Reweighted accuracy \(>\) accuracy is expected under unequal group sizes and unequal group accuracies (female accuracy is higher on this run).

### Q1.3 — Correlations with predictions
Using hard predictions \(\widehat Y=\mathbf{1}\{\mathrm{score}\ge 0.5\}\) is the right object. The \(A=0\) list shifting toward `relationship_Wife` is a nice empirical observation; the write-up reports it cleanly without over-claiming.

### Q1.4 — DP regularizer
**Penalty choice.** Squared difference of group-mean sigmoid scores is an appropriate smooth surrogate of demographic parity. The report correctly rejects thresholded predictions for backprop and documents the empty-group batch rule.

**\(\alpha\) protocol.** Selecting the range from **training** metrics only is good experimental hygiene and should be rewarded. Excluding \(0.1\) (too weak) and \(300/1000\) (collapse to all-negative) is well justified by `results/q14_train_selection.json`.

**Results reading.** The accuracy–fairness trade-off through \(\alpha=30\) is clear. Calling out non-monotonic test \(\Delta_{DP}\) (\(0.0012\) at 30 vs \(0.0040\) at 100) is exactly the sort of careful observation graders like.

### Q2.1
Standard construction (\(Y = X \oplus R\)). The conditional-independence failure check is explicit and correct.

### Q2.2
Satisfies the book-style request: ternary \(Y\), \(A\not\perp Y\), while \(R\perp A\) and \(R\perp A\mid Y\) (because \(R\) is a deterministic function of \(Y\)). Nondegeneracy is checked.

### Q2.3
The flip-if-needed construction \(h\in\{g,1-g\}\) yields equality \(\mathrm{RWAcc}_A(h)=\tfrac12\Delta_{DP}(g)+\tfrac12\), which implies the required inequality. Proof is short and sufficient.

---

## Code review notes

**What is already good**
- Clear separation: student logic in `student.py`, instructor loop in `train.py`, evaluation/analysis helpers elsewhere.
- Public checks pass; correlation matches NumPy; DP penalty backpropagates with the analytically expected gradients.
- Analysis script documents train-only \(\alpha\) selection and refuses misaligned prediction IDs.

**Nits (none are correctness failures)**
1. `README.md` on `main` duplicates large result tables already in the report — harder to maintain; the companion PR trims this.
2. Report on `main` uses two full-width tables for Q1.1 and slightly wordy Q1.4/Q2 prose — companion PR tightens.
3. Three separate Q1.4 figures are fine; a single multi-panel figure would be even easier to grade at a glance.
4. `requirements.txt` pins Python-package versions but README requires 3.13; worth confirming the course VM matches (3.12 also ran the metric checks here).

---

## Recommendations (action items)

### Must-fix before submission (if not already done)
1. Confirm the local `A1.pdf` has no extra prompts beyond what the report answers (especially interpretive questions on Q1.1/Q1.3).
2. Recompile `report.pdf` from `report.tex` after any last edit so PDF and TeX cannot drift.
3. Keep `data/`, `.venv/`, `runs/`, and checkpoints out of the submission zip (already gitignored).

### Should-fix for a cleaner, easier-to-grade packet
1. Merge the companion conciseness PR (or cherry-pick its report/README/`student.py` edits).
2. In Q1.4(a), add one explicit clause that absolute deviation is non-differentiable at 0, which motivates the square.
3. Add a one-line figure caption naming the three plotted metrics (companion PR does this).
4. If page limits are strict, prefer the combined Q1.1 table and shorter Q2 proofs from the companion PR.

### Nice-to-have (will not change correctness marks)
1. One combined accuracy / RW-accuracy / \(\Delta_{DP}\) plot with dual axes or twin panels.
2. Brief fairness interpretation tying Q1.1 proxy features to the Q1.2 disparity.
3. Record wall-clock and skipped-penalty-batch counts from `config.json` in an appendix if the handout asks for experimental details.

### Do **not** change without re-running everything
- Random seed, optimizer hyperparameters, or \(\alpha\) grid after test evaluation — would invalidate the reported tables.
- Soft vs hard targets inside `dp_penalty` — hard labels would break the differentiability requirement.

---

## Suggested marking rubric (for self-check)

| Item | Points (example) | This submission |
| --- | ---: | --- |
| `correlations` + Q1.1 table | 10 | 10 |
| `metrics` + Q1.2 report | 15 | 15 |
| Q1.3 correlations with \(\widehat Y\) | 10 | 10 |
| `dp_penalty` + differentiability write-up | 15 | 14–15 |
| \(\alpha\) sweep, plots, discussion | 15 | 15 |
| Q2.1 | 10 | 10 |
| Q2.2 | 10 | 10 |
| Q2.3 | 10 | 10 |
| Clarity / reproducibility / disclosure | 5 | 5 |
| **Total** | **100** | **~99–100** |

Minor deductions, if any, would come from presentation length/duplication or a missing one-liner on why \(\lvert\cdot\rvert\) is avoided—not from conceptual or numerical errors.

---

## Bottom line

Ship the numerical and proof content as-is. Prefer the companion PR’s tighter LaTeX/README/`student.py` for readability. Use this document as the grading memo; it intentionally contains recommendations only and does not alter assignment answers.
