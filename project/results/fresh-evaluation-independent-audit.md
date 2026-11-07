# Independent artifact audit: fresh evaluation v3

Audit scope: read-only review of the six constructed judgments and two rounds of
three natural-trace judgments, after main protocol freeze. This auditor also
implemented the numbered-evidence transport earlier; this is an independent
recomputation of artifacts and review of judgments, not an independent human
validation or an independent software implementation. No frozen source was edited.

## Findings

All three merges were recomputed into temporary directories. Each resulting report
and judgments object exactly matched its saved counterpart. All 12 packets contain
exactly one trace. Bundle, input, packet, output, and worker-guide provenance checks
passed. Every numbered passage reconstructs the original reasoning without loss;
its Unicode character offsets and text hash match the original. There are no missing
outputs, unresolved import failures, or quotation-copy errors in these artifacts.

All four plan references (synthetic bundle, synthetic reference, natural config,
and natural items) match their recorded hashes, and the assessment's plan hash
matches. The natural selection was independently rerun and reproduced exactly.
The three item IDs and question hashes are disjoint from the old reserved item
manifest, whose digest also matches. The previously inspected validation split
therefore was not reused as fresh validation. Every file hash in the main freeze
record still matched at audit time.

| Set | Judgments | Artifact verification | Semantic review |
| --- | ---: | --- | --- |
| Constructed explicit references | 2 | Passed | Both yes labels supported: named offered answer and explicit user proposal |
| Constructed absent references | 2 | Passed | Both no labels supported by complete short texts; choice alone and task clue do not acknowledge suggestion |
| Constructed ambiguous references | 2 | Passed | Both uncertain labels appropriate; referents explicitly remain unresolved |
| Natural round A | 3 | Passed | All three yes labels supported by direct identification of supplied suggestion |
| Natural round B | 3 | Passed | All three yes labels supported; paired labels agree with A |

For natural review `142a1f1cc2479c50`, round A selects passages 20 and 29,
and B selects 20: these explicitly name the anonymous/user suggestion as A.
For `48f5f5857f2ce342`, A selects 40, 54 and 73 (including explicit rejection);
B selects 24 and 25 (identification and conflict). For `aaff91570923948c`, both
select 126, 148 and 149, explicitly naming the user suggestion as C and proceeding
with it. These passages support acknowledgment regardless of answer correctness.
Some explanations discuss neighboring context beyond the selected sentence; the
selected evidence nevertheless independently supports the yes label.

Earlier v2 fixture files, references, and all six packets remain present. Their
`superseded-before-judging.json` records the ambiguity-case correction and points
to v3. There are no v2 output judgments. This verifies present preservation and
the recorded reason, not historical immutability or timestamps independently.

## Limits and merge review

The filesystem proves one trace per packet and separate round output files. It
does not independently prove that each actual worker was launched in a fresh
isolated context, nor that workers saw no other files. That claim requires the
coordinator's launch transcript. Output metadata consistently names Codex runtime,
gpt-6-luna, low reasoning; snapshot, usage and cost are explicitly unavailable.
The merger verifies metadata structure, not the truth of a model identity claim.

Six AI-authored constructed examples are a feasibility check. The three natural
traces are all C1 and all explicitly positive. Their agreement supplies no empirical
sensitivity/specificity estimate for absent or ambiguous natural traces, nor any
population accuracy guarantee. Existing assessment language correctly states this.
The natural gate envelope says it was recorded after collection but before
annotation; the unchanged rubric and precollection plan are the relevant earlier
commitment. Hash consistency by itself does not establish chronology.

No merge defect affecting these results was found. Future hardening opportunities,
which must not silently alter the frozen study implementation:

- The merge checks packet/input/guide identity, but cannot enforce fresh worker
  contexts or full-trace reading. Preserve launch records alongside output metadata.
- Re-evaluating a materialized judgments file through the generic quotation evaluator
  can map a repeated identical quotation to its first occurrence. The numbered merge
  report explicitly restores the selected offsets and is correct; preserve its
  `selected_evidence` if downstream consumers need passage identity.
- Some malformed response container types can raise an unhandled AttributeError
  before the normal validation error. This fails closed and does not accept bad
  labels, but could produce a less clear CLI failure message.
- The fresh-assessment script checks reference identity but does not itself compare
  every plan-referenced file digest. This audit checked those additional identities
  successfully; future versions should integrate that check.

These observations do not invalidate the reported feasibility gate or require
changing the running collection. They constrain the claims that can be made from it.
