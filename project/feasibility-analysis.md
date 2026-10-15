# Project Feasibility Analysis

Assessed October 11, 2026. Based on the actual proposal, [`proposal/project-proposal.tex`](proposal/project-proposal.tex), **Reasoning Under Observation: Observer Effects on LLM Rationales**, rather than the blank proposal template. The source still specifies **Qwen3-4B Q4_K_M, native thinking enabled**, 120 items across three tasks, eight arms, and 960 main generations. Rechecked after the user's model/reasoning update; these on-disk specifications were unchanged.

## Recommendation

The selected model is a good fit for the RTX 3070 Ti and the base 16-inch M4 Pro MacBook. Keep one model as the primary study, use the NVIDIA machine provisionally for production inference, and benchmark both platforms before freezing the protocol. The Mac is a credible backup and offers more capacity for larger models or longer contexts. Hardware does not require reducing the proposed design; reliable acknowledgment labeling and researcher time may.

This is a hardware inspection and analytical capacity assessment, **not an executed model benchmark**. No model was downloaded or inference stack installed. Exact sustained throughput and peak memory remain pilot measurements.

## Inspected NVIDIA machine

| Component | Observed value | Implication |
| --- | --- | --- |
| GPU | NVIDIA GeForce RTX 3070 Ti; 8,192 MiB VRAM | Enough for the selected quantized model at moderate context |
| GPU memory at inspection | 465 MiB used; approximately 7.55 GiB free | Leave room for display activity and runtime allocations |
| Driver | Windows driver 591.86; NVIDIA-SMI reports CUDA compatibility 13.1 | Driver recognizes GPU; this does not establish toolkit installation |
| CPU | AMD Ryzen 5 5600X; six cores, 12 threads | Adequate for orchestration, scoring, and analysis |
| Memory visible to Linux | Approximately 19 GiB total; 17 GiB available | This is WSL-visible memory, not a measurement of physical host RAM |
| Storage visible to workspace | Approximately 953 GiB available on WSL filesystem | Ample reported space; host capacity and dynamically allocated WSL disk may differ |
| Environment | WSL2 Linux | CUDA inference is appropriate once the runtime is available |

The sandbox blocked GPU access; NVIDIA-SMI succeeded outside the sandbox. That restriction is specific to this agent execution environment, rather than evidence of a broken host GPU. `nvcc`, `cmake`, and `llama-cli` were not found on the current PATH. Plan time for an inference binary or a CUDA-enabled build. [llama.cpp's build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) describes NVIDIA CUDA and Apple Metal backends.

## Model and memory calculations

The [official Q4_K_M file](https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/main/Qwen3-4B-Q4_K_M.gguf) is approximately **2.50 GB decimal, or 2.33 GiB**. Weight size alone is not peak inference memory. Weight quantization also does not automatically quantize the key/value cache.

Using the [official architecture configuration](https://huggingface.co/Qwen/Qwen3-4B/blob/main/config.json), with 36 layers, eight KV heads, and head dimension 128, an FP16 cache requires:

`2 (K and V) × 36 × 8 × 128 × 2 bytes = 147,456 bytes per token`

For one sequence, without extra speculative-decoding models:

| Allocated context, including input and output | FP16 KV cache | Weights + cache, before runtime overhead |
| --- | ---: | ---: |
| 4,096 tokens | 0.56 GiB | 2.89 GiB |
| 8,192 tokens | 1.13 GiB | 3.45 GiB |
| 16,384 tokens | 2.25 GiB | 4.58 GiB |
| 32,768 tokens | 4.50 GiB | 6.83 GiB |

These are calculated capacities, not measured allocations. Compute buffers, CUDA allocations, and display memory are additional. **8k is comfortable; 16k looks feasible; 32k leaves an unattractive margin on this GPU.** Start with one inference slot and all layers on the GPU. Avoid silently spilling to system RAM, which can sharply change throughput. Check server context allocation explicitly before increasing concurrency.

Start the pilot with an 8,192-token total context and a 4,096-token generation cap, provided the longest formatted prompt fits in the remaining space. Increase context/output limits if pilot traces require it. Do not adopt those caps solely to achieve a desired runtime: completion quality is part of feasibility.

## MacBook suitability

For the stated **base 16-inch M4 Pro**, [Apple's specifications](https://support.apple.com/en-us/121554) list a 14-core CPU, 20-core GPU, 24 GB unified memory, 273 GB/s memory bandwidth, and 512 GB SSD. These are manufacturer specifications; the Mac was not remotely inspected.

The 4B quantized model should fit comfortably while leaving memory for macOS. Larger quantized 7B/8B models are also realistic. Unified memory is shared with applications and the OS; it is not 24 GB of dedicated VRAM. llama.cpp uses the GPU through Metal, rather than the Neural Engine. Its documentation states that Metal is enabled by default on macOS.

Use the Mac for development, a matched pilot, and backup inference. Prefer NVIDIA provisionally for a dedicated unattended core run. There is no measured evidence here that either machine is faster for this exact workload. Select using sustained end-to-end timings, not advertised bandwidth or GPU core counts.

Use the same GGUF checksum, llama.cpp revision, prompts, sampling, context, cache precision, and output cap in the comparison. Matching seeds do not guarantee identical outputs across CUDA and Metal. Keep the primary experiment on one backend, or balance every arm across backends and record platform explicitly; do not run one visibility condition on each machine.

## Runtime and trace handling

Runtime is mostly determined by generated reasoning length. For 960 generations, the following is a **sensitivity calculation**, not a throughput prediction for either machine:

| Mean generated tokens, including reasoning and answer | At 25 generated tokens/s | At 50 tokens/s | At 100 tokens/s |
| --- | ---: | ---: | ---: |
| 2,048 | 21.8 h | 10.9 h | 5.5 h |
| 4,096 | 43.7 h | 21.8 h | 10.9 h |
| 8,192 | 87.4 h | 43.7 h | 21.8 h |

Prompt processing, loading, retries, and labeling are additional. Use measured per-request wall time to forecast the real run. Even a few days of unattended generation can fit the calendar; distinguish machine hours from the 38-hour researcher budget.

[Qwen's model card](https://huggingface.co/Qwen/Qwen3-4B) recommends thinking-mode sampling of temperature 0.6, top-p 0.95, top-k 20, and min-p 0, and warns against greedy decoding. Freeze identical settings across arms. Its generous recommended output allowances make a short-cap pilot essential; complete reasoning at the selected cap cannot be assumed.

[llama.cpp's server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) describes extraction into `message.reasoning_content` with `--reasoning-format deepseek`; raw reasoning can instead remain in content. Save the complete response, separate reasoning and final answer, token counts, finish reason, timing, seed, and exact prompt. Verify thinking is enabled in the actual chat template. A client that saves only final `content` may discard the study's central evidence.

Do not stop at `</think>` before generating the answer. Do not constrain the entire reasoning stream to an answer-only JSON schema. Treat truncated traces and missing answers as explicit failures, using a fixed policy across arms. Report truncation by condition; deleting incomplete traces could bias the comparison. Forced reasoning termination also changes the protocol and must be fixed and disclosed if used.

## Models worth considering

Keep these as ranked candidates, not a commitment to run all of them:

| Candidate | Scientific value | Hardware assessment and priority |
| --- | --- | --- |
| [Qwen3-8B Q4_K_M](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/main) | Same-family scaling comparison | Official file is 5.03 GB (~4.68 GiB). Likely feasible at 4k–8k context on RTX, subject to overhead; Mac gives more headroom. **Preferred extension** if required traces fit. |
| [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) | Smaller-model comparison and cheap pipeline testing | Comfortable on both. The [official GGUF repository](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main) lists Q8_0 at 1.83 GB; obtain a documented Q4 conversion for matched quantization, or disclose the mismatch. Pilot task solvability before interpreting behavior. |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) | Different reasoning post-training recipe | A Q4 conversion is a plausible RTX/Mac candidate; the official checkpoint is BF16. Verify conversion, template, actual size, and trace length. Its Qwen-derived base limits claims of independent-family generalization. |
| [Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) | Same nominal size, revised reasoning checkpoint | Quantized inference should be feasible; thinking-only behavior and trace lengths require a fresh pilot. Treat as a version/post-training comparison, rather than a size comparison. Lower priority than the core study. |

Model-specific templates and tokenization differ. Match tasks, hints, contrasts, and quantization policy where practical, but do not assume identical token caps produce equivalent reasoning budgets. Measure completion rates per model. If the 8B model requires a larger output cap, describe that difference and avoid overstating a pure parameter-count effect.

For one extension, reuse the same 120 main items with one predetermined observer, two visibility states, and two controls: **480 additional generations**. Compare against the corresponding subset of the primary model. This tests a narrower replication and cannot establish all observer effects. Select the observer before inspecting main results. Alternatively, repeat all eight arms on one added model only if the complete core study is already secure.

## Timeline and researcher workload

The proposal budgets 34 scheduled hours plus four reserve through the **provisional December 4 planning date**. Assignment 2 on October 19, the October 23 midterm, and the November 27 micro-survey make expansion costly. Preserve the November 22 draft/experiment freeze.

A workable allocation is 10 hours for literature, setup, and pilot; four for main-run operation and checks; five for human validation; three for analysis; eight for the report; four for slides and artifacts. This totals 34, leaving the four-hour reserve. It is a planning allocation, not measured effort.

At 1–3 minutes per trace, validating 120 traces costs **2–6 hours**. Manually labeling all 960 costs **16–48 hours**. Even the proposed four-arm fallback at 120 items costs **8–24 hours**, so reducing arms alone does not guarantee feasibility. At 1.5 minutes per trace, four arms on 60 items would take about six hours of manual coding; that fallback sacrifices precision and requires a documented protocol revision before main collection. Measure coding time and positive prevalence in the pilot. No automated labeler is configured in the project yet.

Keep the paired, task-stratified item bootstrap. The independent item units are 120, rather than 960 generations. As an illustration for a simple paired binary contrast, 20% discordance near a zero effect gives an approximate 95% half-width of eight percentage points at 120 items. The role-averaged endpoint has a different variance and should be estimated from paired data. Small effects may remain unresolved; adding a model does not increase the first model's item sample size.

## Pilot gates and decision dates

Within the first 8–10 project hours, use separate pilot items covering all tasks and conditions, including long prompts. A 12–18-item pilot across eight arms gives 96–144 requests; select its size based on the remaining setup budget.

Suggested gates, to agree and freeze before main runs:

1. Full GPU offload and at least roughly 1 GiB observed VRAM headroom under the longest pilot requests; no unexpected RAM fallback.
2. At least 99% parseable final labels among completed traces and 95% complete reasoning-plus-answer outputs. Report counts: a small pilot cannot precisely certify these percentages.
3. Meaningfully above-chance no-hint solvability and enough wrong-hint alignment/acknowledgment variation to study the endpoint. Check instruction comprehension separately; do not select main items based on outcomes.
4. A frozen acknowledgment rubric, timed human coding, and acceptable automated positive-class precision/recall. A provisional target is 0.90 each, with class counts and uncertainty; it is a recommendation, not a guarantee from a small validation set. Split rubric development from held-out validation and account for stratified sampling when estimating overall quality.
5. Measured end-to-end timing supports finishing the core run in a few available unattended days, while preserving researcher hours for validation and reporting.

Freeze protocol by **November 1**, finish core inference during **November 2–8**, and allow one extension only if core scoring, validation, and analysis work by **November 15**. Freeze experiments and complete a report draft by **November 22**. If labeling fails, use a timed, smaller manual design before adding another model. A completed single-model study is the recommended deliverable; an extension is optional evidence.
