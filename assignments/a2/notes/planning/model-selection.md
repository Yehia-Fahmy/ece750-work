# Assignment 2: instructor example planning

Historical planning record from October 13. The use case and AI policy were updated on October 14; see [revision-notes.md](../revision-notes.md) for the current scope and fully permitted AI use.

Research date: 13 October 2026 (America/Toronto).
Status: complete. User selected Florence-2 and requested the student hand-in format. The final report, destination-specific screenshots/PDF, and distribution archive are in `../../`. The summary is two pages; references and provenance occupy page 3. WSL diagnostics confirmed the 8 GB RTX 3070 Ti. No model inference was needed or performed.
Worktree: `/home/yehia/ece750-work/.worktrees/assignment-2-submission`.
Branch: `codex/assignment-2-submission`.

## Requirements established from the handout

The authoritative source is [A2.pdf](../../A2.pdf), both pages. The existing response template is [a2-yfahmy.tex](../../a2-yfahmy.tex). Read the handout together with the template; use the handout if their prompts differ.

- Audit **one public documentation artifact** for a dataset, model, or other AI artifact. Instructor approval of a student's selection is unnecessary.
- Assess it against a **specific use**, identifying the documentation's purpose, intended audience, and the authors' stated scope. Distinguish documented intentions from our proposed application.
- Record the documentation URL, access date, and version/revision when available.
- Executive summary: **at most two pages**, at least 11-point font, 1-inch margins, three required sections. The template includes the identifying header in those two pages. References, appendices, and any AI disclosure follow outside the limit.
- **Context: 8/40.** Identify artifact, documentation, use, purpose, audience, scope, and provenance.
- **Critique: 20/40.** Explain strengths and significant gaps using a relevant documentation framework and precise citations. Every major finding should affect the reader's ability to judge the chosen use.
- **Proposed changes: 12/40.** Prioritize changes that follow from the critique; identify needed evidence and who can supply it. Do not invent missing facts. Replacement text is optional and may go in an appendix.
- No programming or empirical model evaluation is required. Optional demonstrations belong in supplementary material and must not be presented as evidence of broad suitability.
- Student submission: individual work; section screenshots to Crowdmark, full PDF to LEARN, with supplements zipped if supplied. Due October 19 at 11:59pm ET.

The assignment's student AI policy is narrower than the general policy in L01: AI may edit students' own prose, with disclosure, but may not generate their analysis or responses. The requested artifact is an instructor-provided post-assignment example. Label its provenance and intended use clearly; it should not imply that students were permitted to generate their responses with AI. No detailed marking rubric beyond the 8/20/12 allocation was found in this export, so the eventual commentary should explain design choices without claiming official full-mark guarantees.

## Course alignment

Reviewed L01–L04 and the corresponding annotated copies. Text extraction found the same lecture content apart from a clarification in L02's annotated slide 107 about unequal base rates and predictive parity. The repository contains no L05 or separate complete course outline/reading-list file. Do not treat this local export as all material on LEARN.

| Material | Relevant connection | How the example should use it |
| --- | --- | --- |
| L01, slides 25, 31, 36, 52 | Models operate within institutions; predictions do not choose policies; connect harms to mechanisms | Name the reader's deployment decision, affected people, and consequences of errors |
| L02, slides 56, 72, 110–116 | Quality of service and representational harm; fairness criteria and abstraction traps | Explain what aggregate results omit and why a human-review workflow still needs evidence |
| L03, slides 135–145 | Distribution shift, split design, leakage and benchmark exposure | Explain why published benchmark results need not transfer to the proposed setting |
| L03, slides 147–149, 152–158 | Open-ended criteria; evaluator limitations; audit scope, access and authority | Specify whose judgments matter and separate a documentation review from a behavioral audit |
| L04, slides 175–177, 184–190 | Construct validity, data handoffs, documentation and the model-card revision example | Explain why a convenient score does not establish useful or faithful outputs; propose evidence-backed revisions |
| L04, slides 191–194 | Reproducibility and evaluation documentation | Request evaluation conditions and uncertainty, with a versioned record |

The most direct teaching precedent is **L04 slide 188**, which revises a smile-detector card for a proposed use involving children: identify an unsupported use, explain missing evidence, and request relevant evaluation. We should model that chain of reasoning rather than list absent headings mechanically.

Primary framework: [Mitchell et al., Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993), Figure 1 and section 4. Tailor its categories to the application: model identity, intended/out-of-scope uses, relevant factors, metrics, evaluation/training data, disaggregated results, ethical considerations, caveats. For training-data questions, [Gebru et al., Datasheets for Datasets](https://arxiv.org/abs/1803.09010) can supplement the model-card framework.

## Model shortlist

Hardware assumption: the desktop RTX 3070 Ti has **8 GB VRAM**, according to [NVIDIA's specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3070-3070ti/). Confirm the user's exact card and OS before implementing a demo. No CUDA device or `nvidia-smi` was available in this workspace; **none of these models was run here**.

| Candidate | Interesting demonstration | Documentation-audit angle | Expected fit on 8 GB |
| --- | --- | --- | --- |
| **Microsoft Florence-2-base — first choice** | Image captions, object detection, OCR | Technical documentation versus evidence for faithful, useful image descriptions | Strong prospect: 0.23B parameters, approximately 0.46 GB FP16 weights alone; batch one, bounded output; total VRAM unmeasured |
| **OpenAI Whisper-small — strongest speech alternative** | Multilingual speech transcription and translation into English | Disclosed hallucinations and uneven language/accent performance; translating caveats into usable deployment guidance | Official repository estimates approximately 2 GB VRAM for small |
| **Meta SAM 2.1 Hiera Small — best interactive demo** | Click to segment an object; propagate its mask through a short video | Prompt protocol, domain coverage, annotation quality, and failure/recovery guidance | 46M parameters; image inference is a strong prospect; video state, resolution and number of objects can dominate memory |
| **Qwen3-4B-Instruct-2507 — conversational alternative** | A local text assistant | Capability benchmarks versus limitations and evidence for a specific conversational use | Use 4-bit quantization and a short context; 16-bit weights alone are about 8 GB, leaving little room for runtime/KV cache |
| **Google Gemma 3 4B IT — richer LLM/VLM card alternative** | Image questions and local text generation | Extensive card with safety claims that can be checked for specificity and coverage | Use quantization and bounded context; original HF weights require accepting Google's terms |

**Florence-2.** Audit Microsoft's [checkpoint card](https://huggingface.co/microsoft/Florence-2-base), with its [paper](https://arxiv.org/abs/2311.06242) as supporting documentation. The card provides task prompts, model variants, examples and benchmark tables, but no dedicated intended-use, limitation or ethical-consideration sections. This offers a balanced critique. Keep the audit scoped to the base checkpoint: do not attribute fine-tuned variants' scores to it. The paper identifies source datasets and automated annotation/filtering, so claiming training sources are entirely undisclosed would be incorrect. Further evidence about coverage and annotation quality can still be requested. Its example loader uses remote model code; inspect and pin the revision if a demo is built.

**Whisper.** Prefer the developer-authored [official model card](https://github.com/openai/whisper/blob/main/model-card.md); the HF card identifies partial authorship by Hugging Face. The official card explicitly addresses intended use, hallucinations, uneven performance and broader implications. The [official repository](https://github.com/openai/whisper) supplies the memory estimate. A proposed use is drafting subtitles for consented multilingual teaching recordings, reviewed before publication. Choose multilingual `small`, not `small.en`, if translation or non-English input matters.

**SAM 2.1.** Use the [checkpoint documentation](https://huggingface.co/facebook/sam2.1-hiera-small), [official repository](https://github.com/facebookresearch/sam2), and linked research/data documentation with clear attribution. The HF card is primarily a usage guide, so define its boundary explicitly and credit information in linked sources. A proposed use is human-assisted annotation of short wildlife videos. The official speed figures use an A100; do not promise that speed on a 3070 Ti.

**Qwen3.** The [developer card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) provides benchmark results, configuration, inference and sampling guidance. A proposed use is answering questions about a supplied university handbook. Examine what evidence establishes faithful answers, abstention and performance across user groups. A [third-party quantized release](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF) exists; distinguish its provenance and performance from the original checkpoint. Quantized deployment cannot automatically inherit original-weight benchmark results.

**Gemma 3.** The [Google model card](https://ai.google.dev/gemma/docs/core/model_card_3) and [HF checkpoint card](https://huggingface.co/google/gemma-3-4b-it) describe data categories, intended uses, ethics/safety evaluations and limitations. The HF card acknowledges English-only safety evaluation despite multilingual support. This is a useful alternative when teaching a critique of comparatively detailed documentation. The two surfaces differ in some reported details, reinforcing the need to fix the document version and audit boundary.

All checkpoint revisions checked through the HF API are recorded in [source-revisions.json](source-revisions.json). Pin the chosen card's README to the recorded commit and capture its content/hash when drafting the final audit. GitHub and Google web documents need their own revision or archived snapshot if chosen as the primary artifact.

## Recommended Florence-2 example scope

**Decision:** should a university website team use Florence-2-base to draft descriptions of campus photographs, which editors review before publication, for readers who use screen readers?

This is our proposed use, not a use established by Microsoft's card. Image descriptions must fit the page's communicative purpose; a technically accurate inventory can still be unhelpful. The central question is what documentation would let an editor judge when to trust, correct or reject a draft.

Provisional argument: the card supports trying the model, but does not establish suitability for this workflow. A strong answer should connect each finding to a concrete decision and evidence request:

1. Explain the intended deployment boundary and review responsibilities; request accessible-use guidance from maintainers and website/accessibility staff.
2. Define faithful, useful descriptions with intended users and accessibility experts. Request task-relevant evaluations of omissions, unsupported statements and editing burden, across image conditions and relevant populations, rather than treating caption-overlap metrics as sufficient.
3. Summarize training coverage and label quality with known limitations. The data team can provide source/coverage and annotation-validation evidence. Do not infer measured bias from the absence of subgroup results.
4. Provide a versioned, reproducible evaluation recipe and actionable caveats. Maintainers can provide revisions, preprocessing, prompts, decoding settings, sample sizes and uncertainty; local evaluators can test the proposed workflow.

Prioritize two or three of these for the two-page response. Record supporting evidence and longer replacement prose in an appendix. Proposed tests must be labelled as future work unless actually run; a handful of local examples can illustrate failure mechanisms but cannot establish fairness, safety or accessibility suitability.

## Final package after selection

Recommended: student-facing example in the provided three-section format, references after the two-page summary, plus separate instructor commentary explaining the reasoning and evidence trail. Preserve the original student template. Label the output as an instructor example rather than an official grading rubric. Optional: an appendix with proposed replacement text, evidence table and a local demo script, depending on user preference.

Before distribution: verify citations and revision provenance, compile and inspect the PDF, confirm the executive summary occupies at most two pages without shrinking font/margins, and ensure all proposed facts/evaluations are distinguished from established evidence. Local LaTeX executables were unavailable during this research pass; no final solution PDF has been compiled yet.

## Questions presented to the user

1. Model direction: Florence-2 (recommended), Whisper-small, SAM 2.1 Small, or Qwen3-4B; Gemma 3 is another option in this shortlist.
2. Package: two-page example plus references and instructor commentary (recommended), also a demo script, or only the example and references.
3. For a possible demo: operating system and exact GPU/VRAM.
