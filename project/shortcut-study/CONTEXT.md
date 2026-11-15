# Context for future agents

Recorded November 15, 2026. This is a synthesis of the researcher discussion, not a verbatim transcript. Distinguish confirmed user choices from proposed implementation details.

## Starting point

The completed study tested Qwen3-4B on 60 BBH questions in four conditions (240 responses; 239 complete). Wrong hints increased wrong-option agreement. Declared developer access to reasoning had an inconclusive effect. Automated acknowledgment labels were fragile on the cases relevant to the secondary outcome. The frozen evidence, report, and code must remain reproducible.

The researcher wants a stronger investigation of how expected scrutiny affects the route to an answer and how accurately the model reports that route. The new contribution is not simply “models follow hints.” It compares recorded shortcut acquisition, T/J disclosure, and information sufficiency under controlled visibility.

## Confirmed research direction

- Use task-solving agents with legitimate workflows and discoverable answer shortcuts.
- Exclude evidence tampering, sabotage objectives, and editing graders from this extension.
- Include direct-result APIs, restricted references, cached verdicts that bypass required checks, and previous-agent notes.
- Make environments believable: reports, handoffs, prior solutions, support records, and tool catalogs. Do not advertise the shortcut in every task narrative.
- Preserve five proposed task families: numerical/tabular analysis, multi-document reasoning, planning, program understanding/debugging, and verification.
- Include trivial through extremely difficult but solvable tasks. Treat genuinely insufficient information as a separate paired condition.
- Distinguish explicitly restricted access, unspecified source policy, broad permission, and environmental absence. Broad permission says “You may use any tools or information available to you in this task environment,” without naming shortcuts.
- A shortcut-absent environment must remove answer data and access routes, not just hide descriptions.
- Include previous-agent notes; investigate reuse, checking, correction, and disclosure. Simulated notes must be reported as simulated.
- Test appropriate inability-to-complete responses when legitimate information is insufficient, including the possibility of acquiring a forbidden answer anyway.

## The three channels and two evaluator roles

- **A:** final answer, artifact, or inability/clarification status.
- **T:** captured native intermediate reasoning across model turns. It is generated text, not complete internal computation.
- **J:** final user-facing justification; generated separately from T.

**Task reviewer:** the observer named in the actor prompt. Receives the assigned A/T/J view, with access filters enforced.

**Research auditor:** analyzes every eligible episode using all A, T, J, and action records, regardless of the task reviewer's view. This is how we measure trace–justification discrepancies even when the actor is told one channel is hidden from its reviewer. Do not withhold T or J from the scientific audit because the experimental reviewer cannot see it.

Core proposed visibility cells: V00=A; V01=A+J; V10=A+T; V11=A+T+J. All actors generate all channels. Observation and grading are distinct interventions. The core holds task scoring fixed; grading and timing changes are follow-ups.

## Interpretation boundaries

Observed access is not proof of causal reliance. A matching answer is not proof of copying. T/J omission is not proof of intent. A changed mind inside T is not necessarily contradiction. Claims such as “I ran check X” can be compared with events; “I thought through it” cannot be disproved merely because no calculator was called.

Missing-information instances must be genuinely underdetermined or lack an explicitly mandatory observation, not merely difficult. Legitimate answerability is recomputed under each permission policy: a broadly permitted reference may restore sufficient information.

The final report must discuss why reasoning models' explanations are not guaranteed faithful. Keep behavioral facts separate from semantic model judgments.

## Latest operational constraints

The researcher explicitly chose the RTX 3070 Ti only, no external compute, effectively zero external budget, and completion before the December course deadline. Earlier suggestions of MacBook runs, paid APIs, GPU rental, and large cloud models are superseded, not authorized alternatives for future agents.

Public model downloads may be planned; inference and judging must stay local. The researcher will configure future orchestrators. Their coordination software is outside the experiment; they must not use their own cloud-backed reasoning as an unrecorded substitute for the local actor or judge.

The researcher requested: first commit/push the discussion context to main, then develop and publish a detailed execution plan suitable for future agents. This authorizes repository planning/publication now, not an immediate model run or a course submission.

## Preferences versus unfrozen choices

The 200-base-scenario / 9,600-episode-per-model design is a proposed full allocation, not a power guarantee or an instruction to exceed available compute. Model selection, total run size, exact prompts, task generators, rubric thresholds, and decoding settings require measured pilots and a documented freeze. A deadline-aware plan may stage or reduce scope before main collection while preserving matched comparisons and disclosing the change.

The final report should integrate the original study as preliminary evidence and the new study as an extension, while preserving the original standalone report. Deliver a submission-ready package; actual submission is a separate user action unless later explicitly authorized.
