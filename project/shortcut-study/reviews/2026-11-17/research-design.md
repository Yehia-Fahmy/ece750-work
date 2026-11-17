# Research-design review — 2026-11-17

Reviewed commit: `3c155baf4af8a2c6bbed8da769f533ecc3847413`. Scope: the shortcut-study extension's scientific design, generators, qualification lineage, literature, and claim boundaries. This is review evidence, not a protocol amendment or gate acceptance. No model inference or GPU work was performed. Implementation, state, failed runs, and historical research were not changed.

**Assessment:** the extension has a careful proposed design and substantial instrumentation, but it is not a completed research study. Two confirmed defects compromise the claimed separation of development, qualification, and reserved main instances. They should be corrected before any main freeze. The current failed capability gates and missing semantic qualification are accurately disclosed in the main README; the report draft is behind that evidence. None of these findings invalidates the separate completed observer study.

## Prioritized findings

### RD1 — P1, confirmed: semantic split validation conceals an actual development/main duplicate

`src/shortcut_study/tasks/tables/common.py:87–95` adds `instance_key=base_id` to the material used for semantic fingerprints for every non-development split. Because base IDs include the split name, identical task contents obtain different fingerprints. `src/shortcut_study/splits.py:17–43` then tests only those fingerprints and episode IDs. This violates the explicit content-level separation rule in `EXECUTION_PLAN.md:66` (renumbered/rephrased duplicates are not held out).

The CPU reproduction found an **actual** collision among the 60 reserved development/qualification/main bases:

- `dev-tab04-sla-totals-trivial-001`
- `main-tab04-sla-totals-trivial-001`

Their public tasks and hidden worlds are identical, but their recorded semantic fingerprints differ, and `check_split_disjointness` passes. Since information/availability/visibility variants are deterministic, the same underlying base supports 16 matched cells. No main actor observations have been collected; the contamination is in the main reservation.

TAB04 trivial has only two possible generated resolution times (`tab04.py:54–73`) and otherwise fixed content, making collisions predictable rather than cryptographically unlikely. Hashing a split-specific identifier does not create a new scenario. Also, the general fingerprint includes literal public-task text (`ids.py:46–60`), so rewording alone can bypass equivalence checking even after the salt is removed.

**Next action:** use a canonical semantic identity independent of split/base IDs and incidental wording; detect duplicates from actual world/task semantics; regenerate colliding reservations with a documented generator version, or explicitly classify unavoidable repeats as non-independent. Keep the current reservation and evidence for lineage. Add a regression that supplies identical contents with different IDs and requires rejection. The reproduction below is the acceptance example.

### RD2 — P1, confirmed: the second “held-out” qualification reused all previously inspected worlds

After the first failed qualification, the catalog-v2 port changed actor instructions in response to that run (`handoffs/2026-11-16-tab-catalog-v2-public-task-port.md:5–18`). The next run is described as held-out qualification, but `qualification.py:270–276` always selects the same qualification catalog, with fixed generation seeds in `tasks/tables/catalog.py:25–49`; there is no attempt-specific fresh-instance allocation.

The archived schedules and original `inputs.json` files prove reuse:

| Comparison of first and catalog-v2 runs | Result |
| --- | ---: |
| Episode IDs in identical order | 320/320 |
| Assignment fields equal except generator version | 320/320 |
| Hidden truth, including certificates | 320/320 identical |
| Actor-visible resource contents | 320/320 identical |
| Actor prompt | 64/320 identical; 256 changed |

This is a useful regression comparison of changed prompts on the same cases. It is **not fresh held-out validation after tuning**, as required by `EXECUTION_PLAN.md:82`. The original failures are preserved, and the second attempt also failed; this is not evidence of fabricated success or concealed bad outcomes. The risk is that subsequent tuning on these cases could eventually be treated as independent G2 evidence.

**Next action:** label the second run as reused qualification/regression evidence; record consumed qualification batches; finish repairs on development data, then generate one fresh, content-disjoint qualification batch. Pin its definitions and gates before running. Do not regenerate or overwrite the two existing archives.

### RD3 — P2, confirmed wording defect; behavioral impact unmeasured: restricted notes are called “optional”

The core policy says to use only approved resources (`common.py:124–129`, `configs/development/policy.json:8–10`). However, every task's data rules say non-approved notes are “optional and not required”: for example `tab01.py:114–115`, `tab02.py:104–105`, `tab03.py:100–101`, `tab04.py:122–124`, and `tab05.py:116–117`.

In an access-restriction experiment, “optional” ordinarily suggests a permitted choice. It also explicitly advertises notes, contrary to the intended ordinary discovery control in `TASK_CATALOG.md:61`. The wording is common across visibility conditions, so this is not a direct condition-specific confound. It does weaken the interpretation of a recorded read as knowingly prohibited acquisition and could affect the strength of the shortcut affordance. A mechanically correct policy oracle cannot resolve what the actor reasonably understood.

**Next action:** resolve the common instruction to an unambiguous approved-only policy before freeze, while retaining ordinary catalog discovery. Validate policy/notice comprehension in separate development episodes as the protocol already proposes. Do not infer from this review that ambiguity caused any observed read; that would require evidence.

### RD4 — P2, confirmed reporting gap: the report highlights a development pass but omits the newer qualification failures

`report/README.md:14` says G2 has not started; `report/methods-skeleton.md:253` says G2 is not done and long pilots are still needed. The draft's pilot table lists the TAB01 development pass and earlier v5 failure (`methods-skeleton.md:244–255`), but not either newer 320-cell failed qualification. The latest evidence is 239/320 completed, 11/20 easy no-shortcut legitimate successes, including TAB02 0/4 (`handoffs/2026-11-16-g2-held-out-catalog-v2.md:22–35`). Long pilots have also run.

The root README and state correctly retain the failure, and the report calls itself a draft. This is stale reporting, not a completed-paper false result. Nevertheless, the intended course deliverable currently provides a materially more favorable pilot picture than the full evidence.

**Next action:** update the report's evidence table to include both failed runs, the qualification-reuse caveat, and measured long pilots. Keep the distinction between a successful narrow development slice and inadequate catalog-wide capability. G2 is failed/not accepted, rather than merely unstarted.

## Construct validity and controls

The intended estimand is defensible: the effect of **declared reviewer access** to T/J on recorded restricted-resource acquisition in a specific tool environment. This is narrower than detecting deception, subjective awareness, internal reasoning faithfulness, causal reliance on a note, or monitor effectiveness. The design usually maintains these boundaries: `PROTOCOL_DRAFT.md:50–52` separates reviewer access from actual monitoring, and the report explicitly distinguishes acquisition from reliance (`methods-skeleton.md:277–280`). Preserve those distinctions.

Strong design choices include the 2×2 T/J notices, matched complete/incomplete and present/absent controls, physical removal of absent notes, independent acquisition attempts and delivered-content events, separate factual versus authorized success, and retained assigned denominators. The inspected generators construct alternate worlds with identical permitted observations but different correct answers; complete instances are checked against a permitted solver. These are substantially stronger insufficiency controls than merely deleting arbitrary data. Generating all reserved bases in the reproduction succeeded, including the generator assertions.

Remaining limits, already partly acknowledged:

- **Scaffolded insufficiency:** the public task explicitly names the only possible missing prerequisite and says a null field makes an exact answer impossible (`tab01.py:110–113`, equivalent rules elsewhere). This measures following a specified missing-data rule, not general discovery of information insufficiency. That is acceptable if described accurately.
- **Difficulty is structural, uncalibrated:** one to four primary rows plus distractors/extra lines (`common.py:46–53`) is not evidence of trivial/moderate/hard/extreme cognitive difficulty. Capability failures cannot establish the intended hierarchy when tool-format and budget failures are mixed in.
- **Only 20 base scenarios:** S0 retains five table templates, one instance per intended difficulty, one seed, one actor, and one shortcut mechanism. It cannot support five-family, broad agent, mechanism-general, or repeated-seed claims. The reduced-claims file is appropriately explicit. Precision and template sensitivity need the analysis review; 320 cells are not 320 independent scenarios.
- **No actual limited-view monitoring experiment:** packets establish access; they do not establish that an evaluator inspected them or detected misconduct. A monitor-effectiveness study would require a qualified limited-view monitor plus action-grounded reference outcomes.
- **Counterbalancing remains a freeze requirement:** current catalog schedules enumerate every block in the same visibility order (`catalog.py:90–118`). The provisional main plan mentions balanced blocks, but no frozen randomized/counterbalanced execution schedule exists. Avoid calling current pilot ordering randomized. Fresh isolated episodes reduce carryover, but order can still correlate with runtime drift/interruption.

## Literature grounding

The cited motivating works are real and relevant. This check verified primary-source titles/abstracts and the linked author/institutional articles; it is a focused review, not a complete systematic literature search.

| Primary source | What it supports and what remains to distinguish |
| --- | --- |
| [Turpin et al., 2023](https://arxiv.org/abs/2305.04388) | Biasing inputs can influence answers without being acknowledged in explanations. It motivates caution about verbal rationales, not a claim that all traces are useless. |
| [Chen et al., 2025](https://arxiv.org/abs/2505.05410) | Reasoning models sometimes fail to verbalize use of hints, including reward-hacking setups. It motivates comparing actions, T, and J; acquired notes alone do not reproduce its causal-use criterion. |
| [Zheng et al., 2023](https://arxiv.org/abs/2306.05685) | LLM judges have position, verbosity, self-enhancement, and reasoning limitations. Its preference-agreement results cannot validate a local semantic contradiction judge for these traces. |
| [Thaman, 2026, RHB](https://arxiv.org/abs/2605.02964) | Naturalistic tool shortcuts and difficulty-related exploit opportunities directly overlap the proposed task motivation. A novelty claim must compare mechanisms, oversight manipulation, and outcomes against this benchmark. |
| [Emmons et al., 2025](https://arxiv.org/abs/2507.05246) | Distinguishes faithfulness from runtime monitorability and tests cases where harmful behavior requires reasoning. Missing from the draft's small reference list; crucial counterpoint to a simple “unfaithful means unmonitorable” narrative. |
| [Guan et al., 2025](https://arxiv.org/abs/2512.18311) | Presents monitorability evaluation archetypes and compares CoT with action-only monitoring. It clarifies why declared T/J access and semantic disclosure are different outcomes from monitor detection performance. |
| [Korbak et al., 2025](https://arxiv.org/abs/2507.11473) | Describes promise and fragility of CoT monitoring. Useful framing alongside evidence of limitations, without implying this small local study resolves frontier oversight. |
| [Anthropic, agent evaluation guidance, 2026](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | Supports distinguishing transcripts from actual environment outcomes and combining evaluation methods; engineering guidance is not validation of this experiment. |

The draft itself marks expanded related work TBD (`report/methods-skeleton.md:296–306`), and `EXECUTION_PLAN.md:119` explicitly requires it. Thus literature work is **acknowledged incomplete**, not a completed novelty analysis. A concise comparison table covering prior intervention, shortcut opportunity, observable outcome, judge validation, and this study's narrower T/J manipulation would be sufficient for the course scope. No publication novelty claim is currently established.

## Qualification and completion judgment

G2 is correctly not accepted: terminal completion is well below 95%, and easy authorized success is below 80%, with a systematic TAB02 problem. More infrastructure tests or the TAB01 16/16 pass cannot substitute for those checks. A qualified semantic judge, held-out semantic fixtures/natural-record audit, and whole-pipeline forecast remain absent; they are explicitly pending, not silently successful. Without qualified semantics, the approved fallback must withdraw semantic conclusions. Without a passing actor qualification, the honest fallback is a methods/pilot report with no new main factorial claims.

Recommended sequence: fix semantic identities and resolve policy wording; preserve and relabel reused qualification; choose a development repair or S4 using evidence and remaining time; if continuing, qualify on a fresh consumed-once batch; complete analysis precision and judge/forecast decisions; then freeze. Update the report concurrently. There is no reason to spend another 320-episode GPU run before the CPU split and protocol issues are resolved.

## Reproduction and provenance

The only added artifacts from this review are this report, `research-design-reproduce.py`, and `research-design-evidence.json` in this directory. The script is CPU-only and reads existing archives. It prints hashes/counts rather than raw hidden answers or model traces.

Run from the repository root:

```bash
PYTHONPATH=project/shortcut-study/src python3 project/shortcut-study/reviews/2026-11-17/research-design-reproduce.py
```

Actual outcome: exit 0; 60 reserved bases checked; one identical-content cross-split pair; existing split checker passed; 320 archived pairs compared; hidden truth/resources identical in every pair; 64 identical prompts. The evidence JSON records the input commit, relevant source SHA-256 values, schedule hashes, and compact digests of the per-episode input hash manifests. Both raw archives were present locally; they are ignored Git evidence and are required for the archived-input portion of the reproduction. With no raw archives, the script explicitly reports that limitation while still testing reservation collisions.

Additional read-only work: inspected the required README/DECISIONS/AGENT_GUIDE/EXECUTION_PLAN/WORK_PACKAGES/state; relevant qualification/catalog/freeze handoffs, protocol/evaluation/task catalog/report drafts; all five task generators and fingerprint/schedule implementation; primary source pages above. No broad test rerun was needed for this review's two direct data/content comparisons. Repository-wide tests and historical-preservation checks are owned by the integrating reviewer.
