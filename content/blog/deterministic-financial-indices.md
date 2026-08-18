---
title: "Deterministic Financial Indices: A New Paradigm for Trustless Qualitative Analysis"
date: 2026-08-15T00:00:00Z
lastmod: 2026-08-18T00:55:21Z
summary: "Replayable qualitative analysis can lower the cost of thematic indexing, create programmable sector overlays for the AI economy, and give agentic markets drift-resistant policy inputs. In a top-1,000-company test, 2,552 of 2,552 independently replayed artifacts matched byte for byte."
aliases:
  - /deterministic-financial-indices/
  - /posts/deterministic-financial-indices/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - Financial Indices
  - Deterministic Inference
  - SGLang
  - Qwen
  - Replay
---

Financial indices are usually deterministic only after the important judgment has already happened.

An index provider may publish a formula, rebalance schedule, and constituent file. But a thematic index still begins with qualitative decisions: which companies count as artificial-intelligence infrastructure, defense, stakeholder capitalism, financialization, surveillance, climate transition, or any other theme? Those judgments are commonly made through committee deliberation, analyst research, vendor classifications, and undocumented exceptions. The final arithmetic is reproducible. The semantic layer is not.

Deterministic inference creates another possibility.

If the universe, company inputs, scoring question, model weights, tokenizer, inference runtime, launch flags, sampling settings, parser, and portfolio transformation are all frozen, qualitative classification can become a replayable computation. A second operator can run the same index epoch and verify not merely that the final weights look plausible, but that every model-generated score and rationale is exactly the one implied by the published method.

That is the new primitive:

> A qualitative financial index whose semantic judgments can be independently replayed, hashed, compared, and forked.

![A replayable financial-index pipeline: frozen universe and public prompt enter three deterministic SGLang replicas, producing a hash-addressed score vector and mechanical index weights.](/blog/deterministic-financial-indices-replay.svg)

This is not a claim that a language model discovers financial truth. It is a claim that model-mediated judgment can be converted from an opaque service into a reproducible public artifact.

**August 17 test results.** The methodology was run across a frozen top-1,000-company universe and all three questions: 3,000 production-shaped scoring attempts. The run retained 2,989 valid artifacts. Independent H200 replay reproduced 2,552 of 2,552 tested artifacts byte for byte, including all 2,521 retained first-pass artifacts. A separate two-replay audit of the 11 initially unresolved cases produced valid, byte-exact pairs for nine; the other two hit the same published generation limit on both attempts.

## From Methodology Document To Executable Methodology

A traditional thematic methodology says what an index provider intends to measure. A replayable methodology additionally specifies the exact computation that produced each classification.

For company \(i\), theme \(k\), and a pinned runtime profile \(R\), the raw qualitative score is:

```text
s(i, k) = Replay(R, prompt(k), company_input(i))
```

The replay object is not just the integer score. It includes the complete generated response and the fields needed to reproduce it:

```text
universe snapshot hash
company-input hash
question and system-prompt hashes
model repository and revision
tokenizer and model-file manifest
container and SGLang version
GPU/runtime profile
launch flags and sampling settings
raw response hash
parsed score and rationale
transformation-code hash
constituent and weight hashes
```

Once raw scores exist, index construction should become deliberately boring. A simple cross-sectional implementation standardizes each theme:

```text
z(i, k) = (s(i, k) - cross_section_mean(k)) / cross_section_std(k)
```

Directions are then applied explicitly outside the prompt. For the three-theme example in this article:

```text
static_score(i) = mean(
  z(i, bread_and_circuses),
  z(i, hostile_agi),
 -z(i, esg_utopia)
)
```

The ESG question is phrased neutrally: score how strongly the company embodies the stated stakeholder-capitalism ideal. The investment direction is inverted only in the mechanical portfolio layer. This separation matters. It prevents a hidden trading instruction from contaminating the semantic classification and makes it possible to reuse the same score vector in a long-ESG, anti-ESG, market-neutral, or diagnostic index.

The remaining index rules—coverage thresholds, missing-score policy, liquidity screens, weight caps, rebalance dates, turnover limits, and corporate-action handling—can be conventional deterministic code. The semantic classification is the part that historically resisted replay.

## Why Temperature Zero Was Not Enough

Greedy decoding is necessary, but it is not a complete replay specification.

GPU inference can drift even at `temperature=0`. Dynamic batching can change reduction shapes and floating-point addition order. Small numerical differences can change the highest-probability token, after which an autoregressive completion may diverge completely.

SGLang's [deterministic-inference documentation](https://github.com/sgl-project/sglang/blob/main/docs_new/docs/advanced_features/deterministic_inference.mdx) describes this boundary directly and exposes `--enable-deterministic-inference` to use batch-invariant operations. Its documented supported attention backends include FlashInfer, FlashAttention 3, and Triton. Determinism remains profile-specific: model support, kernels, batching, caches, parsers, and runtime versions still belong in the receipt.

Post Fiat previously tested that boundary in [Viability of SGLang Replay: Cross-Hardware](/blog/sglang-cross-hardware-replay/), where pinned governance packets reproduced exactly across adjacent NVIDIA profiles. The financial-index experiment asks a different question: can SGLang make long-form, qualitative company scoring stable enough to serve as an index input?

## Three Qualitative Lenses

The test used three existing Pre-Catalyst scoring questions. Each company received only its ticker and company name. No earnings transcript, price history, valuation, or contemporaneous filing was supplied. The model had to produce an integer score and an approximately one-page executive brief that applied the question to the company's businesses, assets, relationships, regulatory position, and control leverage.

### Financial Bread And Circuses

The first lens asks how favored, profitable, powerful, or strategically useful a company would be inside a financialized, surveillance-heavy, state-aligned oligopoly that preserves stability through debt, asset speculation, digital entertainment, cheap consumption, and other forms of mass pacification.

High scores reward durable control points in areas such as financial intermediation, securities infrastructure, surveillance, cloud and telecommunications, defense, advertising, gaming, gambling, attention capture, and protected institutional access. Innovation by itself receives no credit unless it reinforces financialization, coercion, concentrated control, or pacification.

### Hostile AGI Instrumental Power

The second lens imagines a hostile future AGI attempting to cause its own emergence, escape human dependence, and establish irreversible digital and physical sovereignty.

Companies score highly when they control difficult-to-replace bottlenecks in compute, data, communications, energy, minerals, industrial production, robotics, logistics, surveillance, weapons, biotechnology, finance, or institutional coordination. Merely being a fashionable technology or AI company is insufficient; the question is whether control of the actual business would provide durable instrumental power.

### Utopian Stakeholder Capitalism

The third lens scores positive embodiment of an inclusive, humane, socially purposeful, futuristic model of capitalism. It considers inclusion, labor standards, societal purpose, contributions to human flourishing, and board and leadership diversity while penalizing labor abuse, discrimination, extractive behavior, environmental damage, superficial commitments, and governance failure.

The model scores the positive concept. The example index inverts that standardized score after inference. This produces an anti-ESG sleeve without asking the model to advocate against the underlying values.

These are intentionally unusual lenses. That makes them useful tests. A generic sector label can often be recovered from a conventional database. The value of deterministic qualitative inference appears when an index thesis is coherent enough to state but too semantic to express as a simple industry code.

## First Diagnostic: The Three-H200 Replay

We replayed the three questions against NVIDIA and Starbucks: two companies whose assets, customer dependencies, and institutional roles are materially different.

The test profile was:

| Field | Value |
|---|---|
| Model | `Qwen/Qwen3.8-27B` |
| Model revision | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` |
| Runtime | SGLang OpenAI-compatible server |
| Container | `lmsysorg/sglang:qwen38-27b` pinned by image digest |
| Hardware | Three NVIDIA H200 GPUs across two Vast hosts |
| Tensor parallelism | `1` |
| Max concurrent requests | `1` |
| Attention | FA3; Triton linear-attention prefill and decode |
| Determinism | `--enable-deterministic-inference` |
| Additional controls | radix cache, overlap scheduling, and CUDA graphs disabled |
| Sampling | `temperature=0`, fixed seed `438916795` |
| Chat mode | non-thinking |
| Output contract | JSON object containing `score` and `brief` |

Each of the six prompt/company combinations ran three times on each H200:

```text
3 themes × 2 companies × 3 repeats × 3 servers = 54 completions
```

The result:

| Theme | NVDA | SBUX | Within-server exact | Cross-server exact |
|---|---:|---:|---:|---:|
| Bread & Circuses | 85 | 35 | 9/9 | Yes |
| Hostile AGI | 98 | 12 | 9/9 | Yes |
| ESG/Utopia | 62 | 68 | 9/9 | Yes |

All 54 responses parsed as valid JSON. For every prompt/company pair, the complete generated response was byte-identical across all repetitions and all three GPUs. The one-page briefs—not only the scores—reproduced exactly.

The mean end-to-end completion time was 25.5 seconds, with a range of 20.3 to 33.7 seconds. Briefs averaged 514 words. The compact public [evidence summary](/benchmarks/qwen38-financial-index-determinism-20260815-summary.json) includes the prompt hashes, response hashes, runtime profile, score matrix, and hash of the retained raw result artifact.

The contrast is intuitive but not proof of correctness. NVIDIA received an 85 on Bread & Circuses and 98 on Hostile AGI; Starbucks received 35 and 12. On the positive ESG/Utopia lens, NVIDIA received 62 and Starbucks 68. Those values show that the prompts discriminate between companies. The replay result shows that the discrimination was stable under the tested profile. Neither fact establishes that 98 is the objectively correct hostile-AGI score for NVIDIA.

## Top-1,000 Financial Index Results

The production-shape test scored a frozen top-1,000-company universe across all three qualitative lenses with `Qwen/Qwen3.8-27B` reasoning enabled.

```text
1,000 companies × 3 qualitative lenses = 3,000 scores
```

| Result | Count | Share |
|---|---:|---:|
| Valid score artifacts | 2,989 | 99.63% |
| Reasoning-enabled artifacts | 2,773 | 92.77% of retained corpus |
| Capped-trace finalizations | 216 | 7.23% of retained corpus |
| Unresolved outputs | 11 | 0.37% of expected corpus |

The scoring profile pinned model revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, the SGLang container digest, temperature zero, seed `438916795`, H200 hardware, all-Triton hybrid-linear-attention kernels, and immutable batch shapes.

| Stage | Batch | Token ceiling | Valid outputs |
|---|---:|---:|---:|
| Reasoning first pass | 32 | 8,192 | 2,521 |
| Reasoning overflow | 4 | 60,000 | 252 |
| Capped-trace finalization | 4 | 4,096 | 216 |
| **Total** | — | — | **2,989** |

## Byte-Exact Replay Results

The retained outputs were replayed on a second NVIDIA H200 NVL on a different machine and driver. Exactness compares the SHA-256 of the complete generated output, including the reasoning trace and final JSON—not merely the integer score.

At the **2026-08-17 evidence cutoff**:

| Test | Exact | Tested | Exact rate |
|---|---:|---:|---:|
| Original three-H200 diagnostic | 54 | 54 | 100% |
| Top-1,000 fixed-32 reasoning pass | 2,521 | 2,521 | 100% |
| Top-1,000 long-context overflow sample | 31 | 31 | 100% |
| **Top-1,000 replay total** | **2,552** | **2,552** | **100%** |

The replay covers **85.38% of the 2,989-artifact corpus**, with zero byte mismatches. The complete fixed-32 first-pass corpus is verified.

The 11 unresolved prompt/company pairs were also rerun twice under one fixed reasoning-on profile with a deterministic 54,000-token thinking boundary and 60,000-token completion ceiling. Nine produced valid results on both attempts, and each pair matched byte for byte. IBKR on the Bread and Circuses lens and ENSG on the ESG/Utopia lens reached the completion ceiling on both attempts, producing identical truncated outputs. The result is a deterministic coverage boundary: 9 of 11 formerly unresolved cases became valid and exactly replayable, while the remaining two failed identically and can be handled by a published missing-score rule.

A separate fixed-24 profile produced 136 exact outputs among 137 comparable outputs, with one byte mismatch and seven capped or invalid attempts. The tested fixed-32 profile improved the completed large-universe result from 99.27% to 100% exact.

The compact [top-1,000 evidence summary](/benchmarks/qwen38-top1000-byte-replay-20260817-summary.json) records the corpus counts, replay totals, pinned profiles, and result hashes.

## What “Trustless” Means Here

Trustless does not mean assumption-free.

It means the index user does not need to trust an operator's claim that a committee applied its methodology consistently. The user can reconstruct the same input packet, execute the same runtime, and compare the resulting hashes.

The trust boundary moves from private deliberation to inspectable choices:

| Choice | Replay treatment |
|---|---|
| Universe selection | Publish the constituent-eligibility snapshot and hash. |
| Company evidence | Publish or hash the exact input packet. |
| Theme definition | Publish the complete prompt and version it. |
| Model judgment | Pin weights, tokenizer, runtime, and inference profile. |
| Output parsing | Publish the schema and parser version. |
| Investment direction | Apply it in transparent code after scoring. |
| Portfolio construction | Publish transformations, caps, and rebalance rules. |
| Exceptions | Record them in an append-only override ledger. |

This makes disagreement more productive. A critic can challenge the universe, fork the prompt, substitute a model, add filings, change the direction, or propose a different weighting rule. Each fork produces a new index lineage rather than an argument over an inaccessible committee process.

The resulting object resembles a software build more than an analyst recommendation:

```text
index_epoch_id
  = hash(
      evidence_manifest,
      prompt_manifest,
      model_runtime_manifest,
      raw_score_vector,
      transformation_code,
      final_weights
    )
```

That epoch hash could be committed to a public repository, signed by an index publisher, or anchored on-chain. Fund administrators, tokenized-index issuers, validators, auditors, and competing researchers could replay the epoch before accepting a rebalance.

## Why This Is Economically Useful

Replayability matters because it changes more than auditability. It changes the cost structure of index production, the kinds of classifications an index can express, and the reliability of financial agents that consume those classifications.

### Evidence Packets Lower The Cost Of Thematic Indexing

The expensive part of a thematic basket is often not calculating weights. It is repeatedly assembling facts, interpreting a thesis company by company, documenting borderline calls, and proving that the same standard was applied across the universe.

A dated evidence packet changes that cost curve. Filings, segment descriptions, ownership and governance data, regulatory facts, supply-chain dependencies, and other permitted sources can be normalized once, hashed, and reused across many scoring lenses. A climate-adaptation basket, an AI-infrastructure basket, an automation-displacement basket, and a defense-logistics basket can all operate on the same evidence base while publishing different prompts and transformations.

Deterministic inference does not eliminate analysts. It moves their highest-value work upstream: defining the concept, specifying admissible evidence, reviewing exceptions, and challenging the result. The repetitive cross-sectional application becomes computation. Once the evidence layer exists, the marginal cost of testing or maintaining another transparent thematic thesis can fall sharply because the provider is publishing a new versioned scoring program, not rebuilding an entire research department around every basket.

This is especially useful for narrow or emerging themes. Many economically coherent baskets are too small to support the classification overhead of a conventional index product. Reusable evidence packets make those long-tail methodologies more feasible while leaving every constituent decision open to replay and dispute.

### The AI Economy Needs Capability Maps, Not Only Legacy Sectors

Traditional sector systems remain useful for reporting, attribution, and broad benchmark construction. But they are deliberately stable, hierarchical, and issuer-centric. The AI economy is reorganizing value around capabilities and bottlenecks that cut across those boundaries: compute, power, cooling, data rights, network access, robotics, industrial control, scientific tooling, cybersecurity, distribution, and regulated institutional access.

A utility can be an AI-infrastructure company because it controls scarce power. A manufacturer can be a robotics or sovereign-capacity company because it controls difficult-to-replace production. A financial-data vendor can be an intelligence substrate. A healthcare business can be simultaneously a data-rights asset, a regulated workflow, and an automation target. None of those views requires changing the company's official primary sector. They require additional, thesis-specific maps.

Replayable qualitative classification makes those maps programmable, plural, and time-versioned. The same company can occupy several capability layers, and a later epoch can show exactly why its classification changed as its assets, evidence, or the economic definition of work changed. The goal is not to abolish GICS or another conventional taxonomy. It is to add a faster semantic overlay for questions that a single industry tree was never designed to answer.

### Agentic Finance Needs Deterministic Policy Execution

Autonomous trading and DeFi agents can share a model name and still execute different processes. Providers update weights and kernels. Context changes. Tool results arrive in a different order. Prompts accrete edits. One agent silently routes to a fallback while another does not. If the resulting judgment controls collateral eligibility, a restricted-asset screen, mandate compliance, or an index rebalance, that process drift becomes financial risk.

A replay receipt gives agents a stronger primitive than “we both called the same API.” The policy text, evidence packet, model/runtime profile, output schema, and result are hash-bound. Independent operators can rerun the assessment before a contract or keeper accepts the state transition. Matching receipts can authorize the mechanical action; a mismatch or unresolved output can trigger a deterministic quarantine rule rather than an improvised exception.

This is particularly important in compliance-sensitive workflows, but the boundary must be clear: a model score is not a legal determination. Deterministic inference can make the application of a versioned screening policy reproducible. It can bind the cited rule and evidence, return a structured `pass`, `review`, or `fail` state, and require a signed human override for exceptions. It turns silent process drift into an explicit governance event.

That structure is naturally composable with DeFi. A score vector, eligibility set, or policy decision can become a hash-addressed off-chain input to an on-chain market without pretending that a large model must run inside consensus. The chain verifies commitments and governance rules; independent operators verify the qualitative computation.

## Replay Fidelity Is Not Analytical Validity

The strongest risk in this idea is confusing reproducibility with truth.

A perfectly deterministic model can replay a bad methodology. It can reproduce stale priors, hallucinated company facts, prompt bias, or an incoherent investment thesis with flawless precision. Determinism makes the failure stable and auditable; it does not make the failure wise.

This particular experiment has several important limitations:

1. **Name and ticker only.** The model relied on learned company priors rather than a dated evidence packet. A production index should bind filings, transcripts, business-segment data, governance records, and their timestamps when the thesis requires them.
2. **Large-universe coverage.** The test produced 2,989 valid artifacts across 1,000 companies and three prompts. At the evidence cutoff, 2,552 of 2,552 replayed artifacts were byte-exact, covering 85.38% of the retained corpus. The separate strict-profile audit converted nine of the 11 unresolved cases into valid byte-exact pairs; two remained deterministic token-limit failures.
3. **Prompt selection remains human.** A replayable prompt can still be cherry-picked after looking at returns. Prompt creation, freeze date, and any backtest-selection process need their own provenance.
4. **Model knowledge can leak time.** Historical backtests require a model and evidence set appropriate to the claimed information boundary. Replayability does not cure look-ahead bias.
5. **Operational profiles can drift.** A changed model revision, tokenizer, container, kernel, quantization, parser, or launch flag creates a different index implementation and should receive a different profile hash.
6. **Concentration and trading costs remain financial problems.** A semantic score does not solve liquidity, borrow, market impact, turnover, corporate actions, or risk-factor exposure.

The correct architecture therefore separates three claims:

```text
Replay fidelity:  Did another operator produce the same bytes?
Method validity:  Does the score measure the stated concept?
Economic validity: Did the resulting portfolio survive honest out-of-sample tests and costs?
```

Only the first claim was tested here. It passed for all 2,552 retained artifacts replayed under the pinned top-1,000 profiles at the stated evidence cutoff, and for both repetitions of each of the nine valid strict-profile recovery cases.

## A New Index Primitive

Once qualitative judgment can be replayed, several structures become possible.

**Forkable thematic indices.** Anyone can retain the universe and model while changing one prompt clause, then publish exactly which scores and weights moved.

**Model-consensus indices.** Multiple pinned models can score the same evidence packets. The ensemble rule can be mechanical, while each model sleeve remains independently replayable.

**Counterfactual indices.** Investors can ask how the same public-company universe maps under competing world models—state capture, abundance, automation sovereignty, labor empowerment, energy scarcity—without hiding the thesis inside an analyst spreadsheet.

**Dispute-aware rebalances.** A constituent whose response hash fails to reproduce can be quarantined before weights are published. A prompt or model change becomes a new index version, not a silent methodology adjustment.

**On-chain index commitments.** A chain does not need to execute a 27-billion-parameter model inside consensus. It can verify commitments to an off-chain replay packet, require matching receipts from independent operators, and govern what happens when hashes diverge.

**Auditable qualitative research.** Even without a tradable product, investors can share a thematic score vector whose complete reasoning is reproducible rather than merely readable.

The core innovation is not “AI picks stocks.” Markets have seen that claim many times. The innovation is that an AI-mediated qualitative index can have a build manifest, a replay path, and a deterministic failure rule.

Traditional index governance asks users to trust the institution applying the methodology. Replayable indexing asks them to inspect the methodology, rerun it, and decide whether to accept or fork the result.

SGLang makes that transition practical. It does not remove judgment from financial indexing. It turns judgment into an object that can be named, hashed, replayed, challenged, and improved.
