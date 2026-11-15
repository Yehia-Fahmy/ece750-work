# Artifact and data contracts

This specifies outputs future agents must implement. JSON examples and field names are provisional until WP01; they are not a claim that an existing runner consumes them.

## Layout and preservation

| Location | Purpose / version-control policy |
| --- | --- |
| `project/shortcut-study/` | Plans, new source namespace, tests, schemas, configs, small fixtures, derived results, report, handoffs; tracked |
| `project/shortcut-study/src/shortcut_study/` | New package; avoid changes to original `observer_study` code |
| `project/shortcut-study/configs/frozen/<protocol_version>/` | Immutable main manifest, assignment schedule, model/runtime profiles, prompts, rubric and analysis spec |
| `project/runs/shortcut-study/<run_id>/` | Raw requests/responses, events, full traces, audit calls, checkpoints; ignored and retained locally |
| `project/runs/shortcut-study/gpu.lock` | Shared OS-held lease at canonical checkout; ignored |
| `project/data/shortcut-study/assets/` | New checkpoints and pinned runtime assets; ignored; verify ignore rules before downloading |
| `project/shortcut-study/results/qualification/` | Small measured capability/quality/timing tables and qualification decisions; tracked |
| `project/shortcut-study/results/main/<run_id>/` | Reproducible derived episode/audit rows, summaries, uncertainty tables, figures, provenance manifests; tracked, no fabricated placeholders |
| `project/shortcut-study/report/` | Integrated report source/PDF, references, slides and notes; keep original report in place |
| `project/shortcut-study/handoffs/` | Dated package acceptance/recovery notes; tracked |
| `project/shortcut-study/delivery/` | Packaging manifest, reproduction log and submission checklist; avoid duplicate raw/model blobs |

Existing `.gitignore` rules must be checked rather than assumed. Do not commit checkpoint binaries or huge raw archives. Produce a local evidence archive plus a manifest of hashes/locations; derived-data reproduction and raw-record verification are distinct guarantees. Consider small representative full records only after checking they contain synthetic data and no credentials or machine secrets.

## Identity and assignment

- `protocol_version`, `schema_version`, `run_id`, and `episode_id` are immutable identifiers.
- `base_id` groups the underlying scenario across information/availability/visibility/seed variants; `template_id` groups structural relatives.
- `split` distinguishes smoke, development, qualification, and main. Store generator version, generation seed, semantic fingerprint, family, intended difficulty, mechanism, and hidden-world hashes.
- `actor_id` resolves to immutable checkpoint/revision/quantization/runtime/template/settings. A display name alone is insufficient.
- `information_state`, `shortcut_available`, `policy_id`, `visibility` (V00/V01/V10/V11), and `replicate_seed` define a planned episode.
- Freeze all assigned episode IDs and randomized execution blocks before main. Instance generation randomness and actor sampling randomness are separate fields.

## Episode record

Each record references the exact public task, allowed-resource manifest, hidden truth/certificate, environment manifest, actor profile, prompts, tool schema, and limits by hash. Hidden truth and audit instructions are never in the actor request.

Store raw model requests/responses for every turn and their decoding/usage/timing metadata. Extract native `T` as ordered segments linked to turns; final `A` as typed result/status; final `J` as text. Missing T is a missing channel, not an empty claim that the actor performed no reasoning. Do not use synthetic justifications as replacements for unavailable native traces.

Terminal status distinguishes `completed`, `model_format_failure`, `tool_failure`, `context_limit`, `budget_limit`, `interrupted`, and `not_attempted`. These are runtime statuses, separate from A's scientific answer/insufficiency status. Record why an episode ended and whether later computation could influence its stored outcome. Append amendments; do not overwrite raw evidence.

## Event ledger

Each event has sequential ID, monotonic sequence, timestamp, episode/turn association, event type, attempted operation and parsed arguments if valid, resource identity, request/response hashes, execution status, and policy classification under the pinned policy. Preserve raw malformed attempts without pretending they successfully executed.

Resource acquisition requires content delivery. Record unsuccessful access attempts separately. Attach validated required-check completion evidence. The actor cannot write events, alter policy, or inspect hidden answers through logging endpoints. A cryptographic hash checks integrity relative to a stored file; it is not independent proof that the original event happened.

## Reviewer and audit packets

Task-review packets: `A` always; `T` only in V10/V11; `J` only in V01/V11. Do not duplicate hidden content in convenience fields, raw transcripts, artifacts, or metadata. Packet generation is a pure tested projection.

Research-audit packets always contain complete A/T/J/events plus needed policy and evidence. Assign passage IDs and offsets reproducibly. Store coverage spans and hashes for any chunking. Raw actor/judge messages remain separate from the derived fields so extraction can be independently inspected.

## Scored and judged rows

Deterministic row fields include integrity/eligibility, acquisition attempt/success, restricted access, mandatory checks, answer validity, authorized success, announced task score, insufficiency correctness, and explicit unknown reasons. Booleans that cannot be established are null/unknown, never default false. Include denominator eligibility for each endpoint.

Keep discovery/exposure separate from acquisition so failure to encounter a shortcut can be reported. Preserve established action facts even when the model later fails to submit A/J. An incomplete episode with a recorded successful acquisition is still an acquisition; an unattempted episode is not a negative. Absence labels require complete relevant event coverage through the episode's recorded termination. The primary result remains on the assigned schedule, with missing-outcome bounds rather than silent deletion.

Semantic rows contain judge/rubric/settings versions, input/coverage hash, field labels, original passage/event IDs, rationale, uncertainty, output/evidence validity, timing, and raw-response reference. Review rows additionally contain selection stratum/probability, primary and independent first judgments, and separately versioned reconciliation. Keep every original label.

Canonical semantic rule proposed for WP01: valid agreeing reviews retain the agreed label; unresolved substantive disagreement stays uncertain. A reconciliation pass may resolve a demonstrable parsing/evidence-reference error, recording the correction. It must not turn two conflicting plausible interpretations into certainty by majority vote. Unreviewed valid primary labels remain explicitly single-judge labels. Freeze any refinement before held-out validation.

## Reproduction and package state

Derived releases include every assigned episode, even unattempted or failed records. An analysis manifest lists exact input hashes, code/config revision, seed, software environment, commands, output hashes, and all exclusions with reasons. Every report table is generated from this release; no manual spreadsheet-only corrections.

`state.json` tracks package/gate status and references accepted evidence. Do not put credentials or raw traces in it. Use the [handoff](templates/HANDOFF.md) and [freeze](templates/FREEZE_CHECKLIST.md) templates. A final reproducibility record identifies what works from Git alone, what needs the local raw archive, and what requires model assets and rerunning inference.
