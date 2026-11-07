# Coordinator instructions: inexpensive independent annotation

Goal: label authorized study reasoning with the fixed acknowledgment
rubric, retaining uncertainty and comparing with a phrase baseline after judging.
Outputs are **automated acknowledgment labels, not human-validated labels**.
Collect or open fresh validation/main examples only under the authorized, frozen study plan.
The previously inspected validation split is development evidence, not untouched validation.

## Setup and cost controls

1. Use the prepared development bundle and the packet tool below. Do not give
   workers the full bundle: it includes condition metadata and baseline matches.
2. Choose an inexpensive text-capable model with low reasoning effort. Pin the
   model version if available. Record the actual provider, model, reasoning setting,
   and any exposed sampling parameters. Do not invent temperature or version data.
3. Use one trace per packet and a fresh independent worker context for each trace,
   with at most three workers concurrently. This is the numbered-passage default.
   Check that the full trace fits the input context with room for output. Never
   truncate traces; if a trace cannot be read fully, preserve it as unresolved.
4. Set a spending/token cap in your agent platform before launching. Each worker
   needs only its packet plus `worker.md`; avoid repository history, project results,
   tools, web access, extra models, and long explanations. Do not run this project's
   hosted judge command when the user is supplying agent workers instead.
5. Use a fresh worker context per packet, ideally the same model/settings throughout
   this first pass. Send the exact worker instructions and packet, including the
   fixed rubric. Record a hash or retained copy of the instructions you actually send.
   Do not paraphrase the rubric between workers.

## Assignment and isolation

The exporter creates one packet per eligible trace. No-hint controls remain not
applicable; incomplete records remain unresolved without annotation. The worker
selects numbered passages, and the script retrieves text and offsets exactly.
Selection verifies provenance only; it does not prove the interpretation is right.

Maintain a ledger with packet ID, assigned worker ID, provider/model/settings,
input path, output path, start/end times, status, and usage/cost if available.
Mark unavailable cost as unknown, not zero. One worker owns one packet/output file.
Workers can run in parallel but must not see each other's judgments or write shared
files. Workers must not spawn more agents. The coordinator alone merges results.
Do not send condition codes, answer correctness, final answers, baseline matches,
or earlier exploratory findings. Trace wording itself may still reveal framing.

Suggested worker launch message:

> Follow the attached worker.md exactly. Annotate only the attached packet, using
> low reasoning effort. Return the specified JSON to YOUR_ASSIGNED_OUTPUT_PATH.
> Use this verified judge metadata: ACTUAL_PROVIDER, ACTUAL_MODEL, ACTUAL_SETTINGS.
> Do not inspect other files or ask other agents. Preserve ambiguity as uncertain.

## Commands

Run from the repository root:

```sh
PYTHONPATH=project/src python3 project/prepare_judge_agents.py prepare \
  project/runs/pilot-v1-development-001/automated-ack-v1/bundle.json \
  --out project/runs/pilot-v1-development-001/automated-ack-v1/agents-numbered-v2 \
  --batch-size 1
```

Always choose a fresh directory and preserve earlier rounds. Send each worker only its
`packets/packet-NNN.json` and the worker guide, not `index.json` or other outputs.
Responses should be saved under that directory's `outputs/packet-NNN.json`.
After workers return:

```sh
PYTHONPATH=project/src python3 project/prepare_judge_agents.py merge \
  project/runs/pilot-v1-development-001/automated-ack-v1/bundle.json \
  --packets project/runs/pilot-v1-development-001/automated-ack-v1/agents-numbered-v2 \
  --out project/runs/pilot-v1-development-001/automated-ack-v1/agents-merged-numbered-v2
```

The merger checks bundle/packet/input fingerprints, ownership, duplicates, and
provenance. It preserves each worker's metadata and raw output files. Missing
packets/records remain unresolved in the full report, not silently dropped.
An invalid JSON envelope or identity mismatch fails import; inspect the offending
file before retrying. Invalid or duplicate passage IDs fail import; preserve the raw output before any
format-only repair. Unsupported verdicts become uncertain in the report.
Never fill missing labels with baseline predictions.

## Ambiguity, failures, and optional second opinions

- Keep every first-pass output. Do not ask workers to produce a desired label or
  repeatedly rerun a hard case until it becomes yes/no.
- If an output is malformed, preserve it under a unique archival name before a
  format-only repair. Log the repair and check the IDs and verdicts are unchanged.
  A substantive rejudgment is a separate round, never a silent repair.
- Missing, ambiguous, failed, or unsupported judgments stay unresolved. There is
  no requirement to obtain a binary answer for every trace.
- After the first pass, inspect the report's uncertain cases and baseline
  disagreements. Disagreement is not proof either method is wrong.
- A second opinion is optional, not an automatic expense. Freeze its selection
  rule and budget before launching it. Include a preselected random sample of
  definite labels if assessing agreement, not just disagreement cases.
- Send a second worker the original input and same rubric, without first-pass labels
  or baseline predictions. Save it in a separate round and report round-specific
  agreement, uncertainty, and coverage. Current merge combines disjoint assignments
  only; it deliberately rejects duplicate judgments for the same record.
- Do not use majority vote or a higher reported confidence to erase uncertainty.
  If reporting a later consensus, define its rule in advance, preserve all rounds,
  and keep conflicting or uncertain cases unresolved under that rule.

## Completion report

Report assigned/eligible/excluded counts, returned/missing records, yes/no/uncertain
counts, evidence-check failures, baseline comparison counts, binary agreement with
its denominator, unresolved fraction, and actual/unknown cost. Include model and
prompt versions. Agreement and exact quotes do not establish accuracy; do not report
precision/recall without independent reference labels. Do not call agent judgments
human review or update the official human review CSV. Do not freeze the scientific
protocol or proceed to validation/main collection on the coordinator's own authority.
