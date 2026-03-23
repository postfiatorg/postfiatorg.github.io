---
title: "Post Fiat Whitepaper"
layout: "whitepaper_page"
url: "/whitepaper/"
summary: "Post Fiat Whitepaper"
---

# Post Fiat: Auditable, Model-Assisted Validator-List Publication for XRPL-Derived Networks

**March 2026**

**Published to production:** 2026-03-23 02:07:45 UTC

---

## Abstract

Post Fiat is an XRPL-derived Layer 1 that replaces opaque validator-list publication with an auditable, replayable pipeline. In XRPL-style networks, consensus security depends on the composition of the trusted validator set, but the rationale behind widely used recommended lists remains largely invisible to network participants.

Post Fiat publishes every stage of each scoring round: raw evidence collected from network data sources, a canonically normalized snapshot, a pinned execution manifest for the model and runtime stack, per-validator scores with rationales produced by a self-hosted open-weight model, and a deterministic set-construction rule with explicit churn controls.

The core technical requirement is rank-driven consensus stability: repeated executions on the same inputs must produce the same pairwise rankings, top-k overlap, and inclusion decisions. Preliminary validation on PFT Ledger's testnet — 42 validators scored by Qwen3-Next-80B-A3B-Instruct-FP8 under SGLang's deterministic inference mode — achieved bit-identical output across five independent runs. This benchmark is a proof-of-possibility result under one tightly pinned stack, not sufficient evidence for production authority transfer on its own.

The system proceeds in phases. Phase 1 maintains foundation authority while publishing complete audit trails. Phase 2 enables validators to independently rerun scoring in shadow mode and measure convergence. Phase 3 transfers authoritative list content to validator-converged output and decentralizes publication infrastructure.

This paper makes a narrow claim: validator-list publication can be made materially more auditable and more contestable than today's opaque publisher process. It does not claim that model-assisted scoring has already been shown superior to simpler deterministic heuristics, nor that the current benchmark package is enough to justify production deployment. Adjacent account-exclusion and privacy work exists in the broader `postfiatd` codebase, but it is not part of the core claim of this paper and is isolated in Appendix B.

---

## 1. Scope and Background

### 1.1 Validator-list publication is security-critical

On XRPL-style networks, each server maintains a Unique Node List (UNL) — the set of validators it trusts not to collude. UNL entries should represent independent entities chosen to minimize correlated failure.[1] Servers can consume signed recommended lists from publishers and require validators to appear on multiple lists before trusting them.[2]

Safety depends directly on validator-set overlap. Less than roughly 90% overlap between participants' trusted sets can cause divergence in the worst case.[3] Signed recommended lists keep overlap high in practice — making list publication a security-critical governance function.

### 1.2 Publication authority is real authority

Lists are signed, versioned, sequenced, and expire. The 2025 default-UNL migration required operators to update both list URL and publisher key or risk falling out of sync.[4] That event demonstrated that publication infrastructure is part of the governance model, not merely a distribution mechanism.

### 1.3 Formal analyses confirm the stakes

Chase and MacBrough showed that RPCA safety requires tighter UNL-overlap conditions than early informal descriptions suggested.[5] Amores-Sesar, Cachin, and Mićić derived an abstract protocol from the source code and showed that safety and liveness can fail under relatively benign assumptions.[6]

If validator-list composition is a security-critical input to consensus, making list construction auditable and eventually multi-party is a meaningful improvement — independent of changes to the base protocol's formal properties.

---

## 2. The Governance Problem

### 2.1 Opaque list construction creates information asymmetry

A recommended validator list involves two decisions: which candidates to include, and how to sign and distribute the result. In a publisher-managed model, the publisher holds private information — internal criteria, subjective judgments, compliance pressures, reputational priors — that network participants cannot observe. Participants see the published set but not the decision rule that produced it.

This is a principal–agent problem. The publisher acts on behalf of the network but retains hidden discretion over selection criteria.

### 2.2 Transparent scoring narrows hidden discretion

Under a transparent model-assisted regime, participants can observe the raw evidence, the normalized scorer input, the model and runtime manifest, the scoring prompt, the model's output scores, and the deterministic selector that produces the final list. Governance choices still exist — what evidence to collect, how to normalize it, what prompt to use — but those choices become named, inspectable, reviewable artifacts rather than unobserved residuals.

Lewis-Pye and Roughgarden's framework for permissionless consensus identifies the role of a **permitter oracle**: some mechanism determining who participates.[7] In XRPL-style systems, validator-list publication already plays that role. Post Fiat turns it from an opaque oracle into a transparent one — inputs, policy, runtime, and outputs are all public, and in later phases, independently recomputable.

### 2.3 What remains

Publishing the full pipeline does not eliminate all discretion. The foundation still chooses evidence sources, normalization rules, the scoring prompt, and the model. But those choices are now explicit, versioned artifacts. Changing them requires a visible policy update, not a silent editorial adjustment.

### 2.4 What this paper does and does not claim

This paper claims:

- validator-list publication is a real governance surface worth making auditable;
- a published evidence-to-list pipeline is easier to inspect and challenge than opaque publisher discretion;
- under one pinned stack, deterministic model-assisted scoring is operationally feasible;
- phased deployment with shadow verification is a more credible path than immediate authority transfer.

This paper does **not** claim:

- that model-assisted scoring is already superior to simpler deterministic or committee-based approaches;
- that the current Phase 0 benchmark is sufficient to justify production authority transfer;
- that decentralization is already achieved in Phase 1 or Phase 2;
- that adjacent privacy or exclusion features are part of the validator-publication proof.

### 2.5 Why use model judgment at all?

Validator-list publication already contains qualitative judgment. Publishers implicitly weigh reputation, operational quality, independence, and legitimacy even when the rubric is unpublished. The narrow argument for model assistance is not that a model is magically objective or inherently superior. The argument is that if qualitative judgment is already happening, a published machine-assisted judgment layer can be easier to audit, replay, contest, and compare than a largely opaque editorial process.

That claim is intentionally modest. The relevant test is not whether the model looks intelligent in isolation. The relevant test is whether the full pipeline produces reviewable artifacts, stable rankings, and a governance process that is easier to challenge than the status quo.

The comparison classes should also be concrete. A deterministic baseline would rank the same frozen snapshot using only published rules over agreement history, uptime, version freshness, identity continuity, and concentration caps. A human baseline would ask a small review committee to rank that same snapshot under the same evidence record. If model-assisted scoring cannot at least match those baselines on cutoff stability, contestability, and operational clarity, then the model layer has not earned authority.

---

## 3. Design Goals

### 3.1 Auditability over mystique

Every scoring round publishes its entire pipeline. "The AI decided" is not a sufficient explanation — a good round explains itself in artifacts.

### 3.2 Stability over single-run purity

Governance needs stable rankings and stable set membership, not perfect token-level transcript identity across every environment. The target is the same practical validator set across runs, or explainable bounded differences.

### 3.3 Narrow authority transfer

Authority moves only after convergence is measured. The foundation remains authoritative in Phase 1 while publishing everything needed for others to audit and later reproduce the process.

### 3.4 Explicit concentration management

Validator diversity requires naming the concentration surfaces that matter: country, ASN, cloud provider, datacenter, and operator identity.

### 3.5 Conservative failure behavior

Missed rounds, failed publishes, stale manifests, or convergence drops degrade to the last known-good list or foundation publication. The system preserves continuity before novelty.

### 3.6 Compatibility with existing validator-list mechanics

Phase 1 uses XRPL-style list publication as it already exists: signed lists, explicit publisher keys, sequence numbers, expirations, and standard retrieval paths.

---

## 4. Round Architecture

Each scoring round is a pipeline reproducible from its published artifacts.

### 4.1 Evidence collection

A round collects validator evidence from multiple sources:

1. **Consensus performance**: Agreement scores across multiple time windows (1-hour, 24-hour, 30-day), missed validations, and ledger index currency. Sourced from a Validator History Service (VHS) that tracks validator behavior continuously.

2. **Infrastructure diversity**: Validator IP addresses resolved via the peer-to-peer `/crawl` endpoint, mapped to Autonomous System Numbers using local BGP routing tables, and geolocated via IP geolocation services. Geolocation informs scoring but is excluded from published artifacts due to licensing constraints — ASN data, derived from public BGP tables, is published.

3. **Software and governance signals**: Server version, amendment voting behavior, fee vote settings, and current UNL membership status.

4. **Identity and attestation**: Domain verification via `xrp-ledger.toml` two-way attestation, entity classification (institutional / individual / unknown), and on-chain identity memos where available.

5. **Observer-dependent metrics**: Peer count, topology position, and latency as seen from the scoring service's vantage point. Weighted cautiously — these reflect a specific observer, not a universal property.

### 4.2 Deterministic normalization

Raw evidence is transformed into a canonical scoring snapshot — the exact input to the scorer. The normalization step exists because raw evidence alone is insufficient for reproducibility: two operators consuming the same source data but transforming it differently are running different rounds.

Each round publishes the raw evidence, the normalized snapshot, and the SHA-256 hash of the snapshot's canonical JSON serialization.

### 4.3 Model-assisted scoring

A pinned open-weight model processes the normalized snapshot under a published scoring prompt. The prompt defines explicit scoring dimensions with weighting guidance — consensus performance (highest weight), operational reliability, software diligence, geographic and infrastructure diversity, identity and reputation, and observer-dependent metrics (lowest weight). The model outputs an integer score (0–100) and a short rationale per validator.

The final validator set is chosen by a deterministic selector operating on published scores.

### 4.4 Deterministic list construction

The final recommended validator set is built by a deterministic selector:

U_t = G(S_t, U_{t-1}; θ, K, δ)

where U_t is the selected set at round t, U_{t-1} is the prior round's set, θ is a minimum score threshold, K is the maximum list size, and δ is the churn-control margin.

The selector:

1. Discards scores below θ.
2. Ranks remaining candidates.
3. Includes at most K candidates.
4. Applies churn control: a challenger displaces an incumbent only if it exceeds the incumbent's score by at least δ, unless a hard-failure condition (e.g., extended downtime, dangerously outdated software) applies.

The model provides candidate evaluation. Set construction is deterministic and auditable.

### 4.5 Publication artifacts

Each round publishes a bundle with full chain-of-custody:

```text
round_t/
├── raw/
│   ├── vhs_validators.json
│   ├── crawl_topology.json
│   ├── asn_lookups.json
│   └── identity_attestations.json
├── snapshot.json
├── execution_manifest.json
├── scoring_prompt.txt
├── scores.json
├── selection_result.json
├── vl.json
└── metadata.json
```

The chain: raw evidence → normalized snapshot → scores → selected set → signed validator list.

Artifact bundles are pinned to IPFS, with the root CID anchored on-chain via a memo transaction. This makes equivocation — publishing different artifacts to different parties — materially harder.

---

## 5. Scoring Surfaces

### 5.1 Scoring dimensions

The scoring prompt defines six dimensions, each with explicit weighting guidance:

1. **Consensus performance** (highest weight): Agreement scores across 1-hour, 24-hour, and 30-day windows, with a target above 99.9%. Missed validations and ledger index currency.

2. **Operational reliability** (high weight): Uptime consistency, domain verification status, and long-run operational track record.

3. **Software diligence** (moderate weight): Server version currency, amendment voting participation, and fee vote configuration.

4. **Geographic and infrastructure diversity** (moderate weight): Country, ASN, and operator distribution across the validator set. Scored relatively — diversity bonuses reward underrepresented attributes rather than penalizing common ones.

5. **Identity and reputation** (low-moderate weight): Verified domain, entity classification, and on-chain identity attestations. Neutral where unavailable — absence of identity data is lower confidence, not negative evidence.

6. **Observer-dependent metrics** (low weight): Peer count, topology position, and latency. Informational only, heavily dependent on the observer's vantage point.

A validator with perfect consensus, good uptime, current software, and a verified domain scores 85 or above regardless of location. Scores below 30 are reserved for serious operational failures — very low agreement, extended downtime, or dangerously outdated software.

The model sits downstream of a fixed published snapshot and upstream of a deterministic selector. It cannot invent uptime or rewrite attestation data. The relevant comparison is published, replayable judgment over a common record versus partially opaque publisher discretion.

### 5.2 Concentration as a portfolio problem

A validator list is not just a ranking of individually good nodes — it is also a portfolio problem. Individually strong validators can be collectively fragile if many share the same cloud provider, jurisdiction, ASN, or operator.

The scoring prompt handles this through diversity bonuses rather than concentration penalties: validators in underrepresented geographies or ASNs receive upward adjustments, while validators in common configurations score on their individual merits. Concentration surfaces — country, ASN, cloud provider, datacenter, operator — are explicit, published, and reviewable.

### 5.3 Identity without unnecessary PII

Identity data is minimal. The public system publishes:

- `verified: true/false`
- `entity_type: institutional / individual / unknown`
- `domain_attested: true/false`

This improves auditability without turning validator governance into a doxxing exercise. `Institutional credibility` means durable public accountability, identifiable stewardship, and real reputational cost for misconduct — not prestige or brand recognition. Operational reliability outranks reputation proxies.

---

## 6. Stability and Reproducibility

### 6.1 The right target is rank stability

The governance targets are:

1. **Pairwise rank agreement** (PRA)
2. **Top-k overlap**
3. **Cutoff-band stability**
4. **Observed churn across rounds**

Let s^(a) and s^(b) be score vectors from two independent runs on the same snapshot.

PRA(a,b) = (2 / n(n-1)) Σ_{i<j} 𝟙[sign(s_i^(a) − s_j^(a)) = sign(s_i^(b) − s_j^(b))]

TopK(a,b;k) = |Top_k(s^(a)) ∩ Top_k(s^(b))| / k

Churn(t) = 1 − |U_t ∩ U_{t-1}| / |U_t|

### 6.2 Why temperature zero is necessary but not sufficient

In autoregressive decoding, token selection under temperature τ follows a softmax distribution. As τ → 0, sampling converges to greedy selection of the argmax token. But real inference systems introduce additional variance: API batching, kernel reduction order, precision modes, tensor-parallel configuration, and hardware differences can perturb logits enough to change downstream tokens.[8]

External APIs should not be treated as authoritative for governance-critical rounds. Post Fiat uses self-hosted inference to control the full stack.

### 6.3 Deterministic inference is now practical

Thinking Machines Lab identified batch-size variance as a major source of nondeterministic inference and described batch-invariant kernels as a practical fix.[9] SGLang implements a deterministic inference mode built on batch-invariant operators supporting FlashInfer, FlashAttention 3, and Triton backends, with a throughput overhead of roughly 34%.[10][11]

Tensor parallelism across multiple GPUs introduces a separate nondeterminism source: cross-GPU reduction operations do not guarantee a fixed summation order, producing different floating-point results across runs. This is why Post Fiat requires single-GPU inference (TP=1) and why model selection prioritized fitting on a single H200 — the 80B mixture-of-experts architecture with only 3B active parameters makes this feasible without sacrificing scoring quality.

Numerical precision remains a real divergence source. Yuan et al. show that limited precision affects reproducibility, particularly for reasoning-style models, and propose mitigations such as LayerCast.[12] This is why the execution manifest is a first-class artifact — a weight hash alone is not enough. Reproducibility depends on the whole stack.

### 6.4 Empirical validation on PFT Ledger

Post Fiat's Phase 0 validation scored 42 validators on the PFT Ledger testnet using Qwen3-Next-80B-A3B-Instruct-FP8 — an 80-billion parameter mixture-of-experts model with 3 billion active parameters — running under SGLang v0.5.6 with deterministic inference enabled on a single NVIDIA H200 GPU.

Five independent runs on the same snapshot produced bit-identical output: identical scores, identical rationales, identical token sequences. Scores ranged from 5 to 97 (mean 85.3), with the model correctly differentiating validators with perfect consensus (scoring 95+) from validators with catastrophic 30-day agreement drops (scoring below 40) and effectively offline validators (scoring below 10).

This exceeds the rank-stability target. When the execution environment is fully pinned — model weights, quantization, inference engine, attention backend, CUDA version, and determinism flags — exact reproducibility is achievable, not merely a near-term target.

---

## 7. Execution Manifest and Hashing Discipline

### 7.1 Full manifest pinning

Each round publishes a full execution manifest. The Phase 0 validation manifest:

| Field | Value |
|---|---|
| Model | Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 |
| Architecture | 80B total parameters, 3B active (MoE) |
| Quantization | FP8 native |
| GPU | NVIDIA H200, 141 GB VRAM, single GPU (TP=1) |
| Inference engine | SGLang v0.5.6.post2 |
| Container image | lmsysorg/sglang:v0.5.6.post2-cu129-amd64-runtime |
| CUDA | 12.9 |
| Attention backend | FlashInfer |
| Sampling | PyTorch (deterministic mode) |
| Temperature | 0 (greedy decoding) |
| Determinism flags | `--enable-deterministic-inference` |

Any change to model weights, engine version, quantization mode, or runtime flags produces a different manifest hash and is therefore a visibly different round.

### 7.2 Domain-separated hashing

Any hash that influences governance is domain-separated and typed. A generic commitment format:

c = SHA256(d ‖ v ‖ r ‖ h ‖ σ)

where d is a domain tag, v is a version byte, r is the round identifier, h is a content hash, and σ is a salt or auxiliary field.

### 7.3 Replay requirements

The implementation supports `replay_round(round_id)`, `rebuild_from_raw(round_id)`, and `dry_run`. If a round cannot be replayed from its own artifacts, it is not auditable.

---

## 8. Security Model

### 8.1 Threat model

The relevant adversaries:

- A list publisher exercising hidden editorial discretion.
- Validators cheaply imitating institutional credibility.
- Operators copying others' outputs without recomputation.
- Validator clusters masquerading as independent entities.
- Operational failures in list publication.

### 8.2 Layered identity signals

Sybil resistance uses layered signals: long-run performance history, domain attestation via `xrp-ledger.toml`, minimal public verification state, operator clustering analysis, concentration analysis, and model-based assessment of institutional credibility.

XRPL's two-way domain verification binds a validator public key and a domain through reciprocal claims, creating strong evidence that the same operator controls both.[13]

Public reproducibility is intentional, not a flaw. An attacker running the same scorer on the same snapshot is analogous to anyone verifying a certificate chain. The security question is whether underlying inputs can be forged cheaply enough to fool the network.

### 8.3 Costly signaling

Spence's costly-signaling framework applies directly. Appearing credible to a model trained on large public corpora is not free — it is typically cheaper to operate a legitimate institution well than to manufacture years of convincing public evidence across independent sources. This raises the cost of Sybil identities relative to systems that treat every pseudonymous operator as equally credible.

### 8.4 Commit-reveal as anti-copying infrastructure

In Phase 2 shadow mode, validators commit to output hashes before reveals open:

c_i = SHA256(d ‖ v ‖ r ‖ H(S_i) ‖ σ_i)

where S_i is validator i's scored output, H(S_i) is its content hash, and σ_i is a random salt. This prevents after-the-fact copying once a canonical output is visible.

### 8.5 Attack summary

| Attack | Mitigation | Residual risk |
|---|---|---|
| Fake domain / fake operator identity | Two-way domain attestation, public verification state, operator review | Stronger against casual spoofing than long-horizon social engineering |
| Metric gaming | Long-horizon performance metrics, public evidence, low weight on short-term optics | Possible if attacker incurs real operating cost |
| Output copying in shadow mode | Commit-reveal timing, public convergence reports | Does not prove local execution by itself |
| Hidden publisher discretion | Raw evidence + snapshot + manifest + deterministic selector | Snapshot assembly may remain centralized in early phases |
| Concentration masquerading as diversity | Country/ASN/cloud/datacenter/operator clustering | Entity resolution is imperfect; conservative defaults apply |
| Collusion among trusted validators | High-overlap requirements and public concentration analysis | Addressed by set-level correlation monitoring, not scoring alone |

---

## 9. Verification and Assurance

### 9.1 Phase 1: Audit trail as assurance

In Phase 1, the foundation is the sole scorer. Assurance comes from publishing the full pipeline: raw evidence, normalized snapshot, pinned execution manifest, scoring prompt, per-validator scores with rationales, deterministic selector output, and signed validator list. Anyone can inspect why a validator was included or excluded. The IPFS-pinned artifact bundle with an on-chain CID anchor makes equivocation — publishing different artifacts to different parties — detectable.

This is already stronger than the status quo, where recommended list construction is not publicly explained.

### 9.2 Phase 2: Verifying independent execution

When validators independently rerun scoring in Phase 2, a new problem emerges: how do you verify that a validator actually ran the model rather than copying the foundation's published output?

Post Fiat addresses this through two mechanisms:

- **Commit-reveal protocol**: Validators commit to hashed outputs before the foundation publishes canonical scores (Section 8.4). This prevents after-the-fact copying.
- **Convergence measurement**: The network measures pairwise rank agreement, top-k overlap, and list-level convergence across validator submissions. Persistent divergence from a specific validator — or suspiciously perfect agreement without commit-reveal compliance — is detectable.

A harder problem is hardware heterogeneity. Not every validator will have an H200. Different GPU architectures may produce slightly different floating-point results even under deterministic inference mode. Phase 2 measures the extent of this divergence empirically and determines whether rank stability holds across hardware configurations.

### 9.3 Future verification paths

Several verification technologies are maturing that could strengthen Phase 2 assurance further. These are not in the current implementation plan but represent a clear strengthening path as the technologies reach production readiness for large models.

| Approach | What it proves | Status |
|---|---|---|
| TEE attestation (H100/Blackwell) | Specific code ran on genuine, untampered hardware | Production-ready, <7% overhead |
| Optimistic ML (opML) | Inference result is correct unless successfully challenged on-chain | On-chain today for 7B+ models |
| Zero-knowledge ML (zkLLM, zkPyTorch) | Cryptographic proof that a specific model produced a specific output | Feasible for 13B today, 70B+ maturing |
| TLSNotary | A specific API call returned a specific response | Available |

### 9.4 Evidence required before authority transfer

Phase 3 should not be justified by a single same-stack benchmark. Before authority transfer, the project should be able to show all of the following:

- repeated replay on many more rounds and snapshots than the current Phase 0 package;
- comparison against explicit deterministic and human-review baselines on the same frozen snapshots, with reported top-k overlap, cutoff stability, and disagreement cases;
- adversarial testing around data curation, identity inflation, and social-gaming attempts;
- independent reruns by external operators, not only foundation-controlled infrastructure;
- measured behavior across hardware or runtime variation sufficient to show that rank stability survives realistic decentralized operation.

Until that evidence exists, the strongest interpretation of the current work is: early benchmark success plus a credible audit architecture, not production-readiness proof.

---

## 10. Phased Deployment

### 10.1 Phase 1: Foundation publication with full audit trail

The foundation operates the scoring pipeline: collecting evidence from VHS and network crawl endpoints, normalizing it into a canonical snapshot, scoring validators via a self-hosted open-weight model on serverless GPU infrastructure, applying the deterministic selector, signing the validator list, and publishing the full round bundle to IPFS with an on-chain CID anchor.

Operationally centralized, fully auditable.

### 10.2 Phase 2: Validator-side shadow verification

Validators independently rerun the same round using the published snapshot and manifest. Each validator runs a GPU sidecar with the pinned model and inference stack. The foundation's list remains authoritative, but validators commit to and reveal their own outputs so the network can measure:

- exact artifact matches,
- score-level agreement,
- top-k overlap,
- and list-level convergence.

This phase answers the key empirical question: can independent operators reproduce the process closely enough for governance?

### 10.3 Phase 3A: Content authority transfer

If Phase 2 demonstrates sustained convergence (pairwise rank agreement > 95%, top-k overlap > 90%), authoritative list content shifts from the foundation's output to validator-converged output. The foundation may still sign and distribute the list, but no longer has sole editorial control.

### 10.4 Phase 3B: Publication decentralization

Publication authority includes snapshot assembly, round announcement, list signing, artifact hosting, and delivery path control. Phase 3B decentralizes these surfaces.

### 10.5 Fallback rules

Every phase has a conservative fallback:
- Missed round → retain last known-good list.
- Participation drops below threshold → revert to foundation-only publication.
- Manifests diverge → treat round as diagnostic, not authoritative.
- Publication fails → preserve continuity before novelty.

### 10.6 Trust model summary

| Phase | Foundation Controls | Validators Can |
|---|---|---|
| Phase 1 | Policy, execution, publication | Inspect and audit all artifacts |
| Phase 2 | Authoritative output | Challenge reproducibility empirically |
| Phase 3A | Publication infrastructure | Influence list content through convergence |
| Phase 3B | (Decentralized) | Control both content and publication |

---

## 11. Economic and Operational Feasibility

### 11.1 A workload built for local inference

Validator-list scoring is periodic, structured, and batchable. A scoring round processes approximately 15,000 input tokens and 3,000 output tokens in under a minute on a single GPU. This is not a high-frequency workload — it runs weekly or monthly.

Post Fiat's Phase 0 validation runs on serverless GPU infrastructure at approximately $0.38 per scoring round on an H200. Monthly cost for the full scoring service — two server instances for devnet and testnet, plus serverless GPU — is $38–69. These costs decline as inference hardware improves.

### 11.2 The cost trend favors decentralization

Stanford's 2025 AI Index reports that GPT-3.5-equivalent inference costs fell by more than 280× between late 2022 and late 2024, with the gap between closed-weight and open-weight models narrowing sharply.[14] Epoch AI reports rapid fixed-performance inference price declines across task categories.[15]

Validator-list scoring has a structural economic advantage over most AI workloads: it runs a few times per month, not continuously. This makes serverless GPU infrastructure — where costs accrue only during active inference and scale to zero between rounds — a natural fit. The foundation's Phase 0 validation costs approximately $0.38 per scoring round on a serverless H200. For Phase 2 shadow verification, falling inference costs mean validators will increasingly be able to rerun scoring locally without datacenter-grade infrastructure.

### 11.3 Validator incentives

Post Fiat follows XRPL's principle that no direct validator reward is the best validator reward. Validators run because they use the network, not because they are paid to validate.

The foundation allocates resources specifically for Phase 2 shadow verification — paying for the work of proving that the scoring process is reproducible, not for general node operation. Credibility signals in model-assisted scoring should reflect genuine institutional commitment to the network, not a subsidy relationship with the foundation.

### 11.4 Why a distinct network

This whitepaper is not a token-distribution memorandum. Its purpose is to explain the infrastructure mechanism that justifies a distinct Post Fiat network. Validator-list publication is part of the trust surface that determines whether sophisticated users regard a ledger as credible and governable. If Post Fiat makes that surface materially more transparent than the status quo, that difference is itself an economic proposition.

The token is justified, if at all, by ownership of and settlement inside a network with a different governance surface. Whether that difference ultimately supports a compelling investment case depends on adoption, usage, and institutional uptake evidence that is outside the scope of this paper.

---

## 12. Boundaries

The claim is comparative, not magical. A published, replayable judgment layer is easier to audit, challenge, and correct than an unpublished rubric or informal committee process.

The boundaries are clear:

- Model scores are qualitative assessments, not mathematical proofs.
- Convergent outputs do not by themselves imply social independence among validators.
- Exact reproducibility across arbitrary GPU architectures requires policy constraints on the execution environment.
- Concentration monitoring is an ongoing operational discipline, not a one-time fix.

These boundaries are reasons to keep the claim surface narrow until more evidence exists.

---

## 13. Conclusion

Validator-list publication is a real governance surface. It determines overlap, concentration, and the security envelope in which consensus operates. Widely used recommended lists remain only partially legible to the public.

Post Fiat replaces opaque editorial selection with a public, replayable, model-assisted pipeline: collect evidence, normalize it canonically, pin the execution environment, score candidates under a published policy, select the set deterministically, publish the artifacts, and shift authority only after convergence is demonstrated.

Preliminary validation now has two layers. First, scoring 42 PFT Ledger validators with a self-hosted 80B-parameter model under deterministic inference produced bit-identical output across five independent runs — exact reproducibility, not merely rank stability. Second, a broader hostname-only benchmark across 29 XRPL validators, eight distinct model configurations, and two independent 15-repeat batches showed that intra-model rank stability remains very high even when the execution path spans multiple hosted providers rather than one pinned local deployment.[27][28]

The broader `postfiatd` roadmap includes adjacent protocol work — validator-consensus account exclusion and Orchard/Halo2 privacy — documented in Appendix B. The publication mechanism remains the narrow core of this paper.

That is ambitious enough to justify continued benchmarking, tighter validation, and staged implementation. It is not yet enough to claim that the governance problem is solved.

---

## Appendix A — Phase 0 Benchmark: PFT Ledger Testnet

### A.1 Model selection

Phase 0 evaluated models across two benchmark rounds to find the best combination of scoring quality, determinism, and single-GPU feasibility:

- **Round 1** tested large models via external API (Qwen3-235B-A22B variants, MiniMax-M1-80B) to establish quality baselines.
- **Round 2** tested H200-compatible models via self-hosted inference (Qwen3-Next-80B-A3B, Qwen3-32B, GPT-OSS-120B) to find a model that fits on a single GPU with FP8 quantization.

Qwen3-Next-80B-A3B-Instruct-FP8 was selected: comparable scoring quality to the 235B variant, 80B total parameters with only 3B active (mixture-of-experts), fits on a single H200 with headroom, and achieved 100% determinism under SGLang's deterministic inference mode.

Platform selection was also empirical. RunPod serverless was tested first and rejected after repeated SGLang deployment failures, including stale runtime support and inability to run the required model/runtime combination reproducibly. Modal was selected only after the same workload ran under a pinned SGLang v0.5.6.post2 deployment script on a single H200 and completed the full 42-validator prompt successfully.[25][26]

### A.2 Scoring results

42 validators on the PFT Ledger testnet were scored using the execution manifest documented in Section 7.1. Representative results (anonymized, sorted by score):

| Validator | Score | Summary |
|---|---:|---|
| v001 | 97 | Perfect 1h/24h, 99.93% 30d (451 missed). Most reliable in set. |
| v002 | 96 | Perfect across all windows. 692 missed over 30d. |
| v003 | 95 | Perfect 1h/24h/30d. Running current software, RPC role. |
| v008 | 95 | Perfect agreement, current software, active UNL role. |
| v015 | 94 | Perfect 1h/24h, 99.76% 30d. Consistent. |
| v020 | 92 | Perfect 1h/24h, 99.42% 30d. Minor long-term misses. |
| v030 | 90 | Perfect 1h/24h, minor 30d degradation. |
| v033 | 88 | Strong consensus, slight 30d variance. |
| v035 | 80 | Good short-term, moderate 30d performance. |
| v037 | 75 | Strong 1h/24h, 30d drops to 95.56%. |
| v038 | 70 | Adequate consensus, some degradation. |
| v039 | 65 | Mixed performance across time windows. |
| v040 | 40 | Perfect 1h/24h but 84.76% 30d — 130K+ missed ledgers. |
| v041 | 10 | Zero 1h/24h, 0.8% 30d. Effectively offline. |
| v042 | 5 | Zero 1h/24h, 0.14% 30d. Non-functional. |

Full distribution: 42 validators, range 5–97, mean 85.3. Processing time: ~43 seconds (warm), ~15,000 input tokens, ~3,000 output tokens.

### A.3 Determinism

Five independent local runs on the same frozen snapshot produced bit-identical output:

- Same scores for all 42 validators.
- Same rationale text, token for token.
- Same JSON structure and ordering.

This remains the strongest result in the paper. Under a fully pinned execution environment, exact reproducibility — not merely statistical stability — is achievable.

The selected model also showed stable decision boundaries, not just repeatable text. In the chosen Round 2 benchmark, all 35 recommended UNL slots were identical across complete runs, the borderline pool was zero, and pairwise UNL overlap was 35.0/35. Competing H200-feasible models produced larger score spreads and 2-4 borderline validators under the same benchmark setup.[25][26]

We then broadened the test beyond the original single-model proof. A separate validator-hostname determinism suite scored the captured 29-validator XRPL cohort with eight hosted model configurations across two independent batches (Run A and Run B), each with 15 repeats per validator, for 6,960 total requests.[27][28] The suite included pinned provider/model combinations for GPT-OSS 120B, GPT-OSS 20B, Qwen3-Next 80B A3B, Qwen3 235B A22B, Qwen3.5 9B, GLM-5 Turbo, MiMo v2 Pro, and Claude Sonnet 4.6.[27][28]

That broader suite shows that robust intra-model determinism is not confined to the local H200 proof of concept:

- Qwen3.5-9B, GPT-OSS-20B, GLM-5 Turbo, and Claude Sonnet 4.6 all achieved Run A vs Run B mode R² = 1.0 and rank R² = 1.0 on the 29-validator cohort.[28]
- Qwen3-Next-80B-A3B remained near-perfect at mode R² = 0.9987 and rank R² = 0.9912.[28]
- Even the noisier pinned configurations remained strongly self-correlated: GPT-OSS-120B produced mode R² = 0.9686 and rank R² = 0.9517, while MiMo v2 Pro produced mode R² = 0.9728 and rank R² = 0.9936.[28]
- Domain-level exact-repeat rates also remained high for the stronger open models: Qwen3.5-9B scored 96.6% of domain/batch cells as fully deterministic, Qwen3-Next-80B-A3B scored 93.1%, and GLM-5 Turbo scored 89.7%.[28]

The same suite also shows that noise itself is stable rather than arbitrary. Across all 232 model-domain pairs with batch-level variance measurements, the standard deviation observed in Run A versus Run B had pooled R² = 0.8380. In other words, models that were noisier on specific hostnames in the first batch were usually noisy on those same hostnames in the second batch as well.[28]

Cross-model agreement was materially weaker than within-model repeatability. Averaged across all model pairs, cross-model rank R² was 0.6985.[28] That is still meaningful overlap, but it supports a narrower claim: the benchmark demonstrates strong reproducibility within a fixed model/provider/configuration, not universal convergence of all models to the same ranking.

The recorded Phase 0 package is therefore not just one exact local benchmark. It now includes both the original self-hosted deterministic deployment evidence and a broader multi-model reproducibility suite. The practical recipe still mattered on the local path: SGLang deterministic mode alone was not enough without explicit runtime settings for FlashInfer workspace size, reduced static memory reservation, chunked prefill, and precompiled kernels.[25][26] The broader hosted-model suite complements that result by showing that high rank stability can still be observed when the benchmark is widened across multiple model families and hosted inference providers, provided the model/provider pairing and request settings are pinned.[27][28]

---

## Appendix B — Adjacent Protocol Extensions in `postfiatd`

### B.1 Validator-consensus account exclusion

In addition to validator-list publication, `postfiatd` includes a PostFiat-specific account-exclusion mechanism. Two amendments, `PF_AccountExclusion` and `PF_ValidatorVoteTracking`, allow trusted validators to add or remove account exclusions through validation traffic, track those votes on-ledger, and maintain an exclusion view over the active validator set.[16]

The relevant distinction from standard XRPL is that exclusion is not just an issuer-side freeze on an issued asset. In `postfiatd`, an account can become excluded by validator consensus once the exclusion threshold is met, and generic transaction processing rejects transactions when either the sender or destination account is excluded.[16]

This is a governance primitive, not merely a token-control primitive. It allows the network to say: a specific account may not participate, regardless of whether the transaction involves an issuer-controlled IOU.

### B.2 Why exclusion is materially different from standard XRPL freezes

Standard XRPL already supports trust-line freeze, deep freeze, global freeze, and clawback for issued assets. Those are real controls, but they are primarily issuer-side controls over IOUs and trust lines rather than validator-governed network-wide exclusion of native XRP accounts or transaction counterparties.[17][18][16]

For sanctions-style enforcement, that distinction matters. OFAC states that virtual-currency compliance obligations are the same as fiat-currency obligations, and that U.S.-subject persons are generally prohibited from engaging in or facilitating prohibited transactions involving blocked persons.[19][20] A validator-consensus rule that rejects transactions to or from identified accounts is therefore materially closer to the policy target than a narrower IOU-freeze model.

That advantage should not be overstated. The exclusion path only helps when the relevant amendments are enabled and enough validators actually reach the threshold. OFAC also states that listed digital-currency addresses are not exhaustive, and that blocking/reporting duties continue when a U.S. person actually holds blocked property.[21][22][23] So Post Fiat's exclusion mechanism is best understood as a stronger protocol-layer enforcement primitive inside a larger compliance program, not as a complete compliance solution by itself.

### B.3 Orchard / Halo2 privacy as a parallel protocol extension

Separately, the `halo2-devnet-integration` branch of `postfiatd` ports Zcash's Orchard privacy model into an XRPL-derived ledger rather than treating privacy as a mixer, sidecar, or external bridge. It adds the `OrchardPrivacy` amendment and a native `ttSHIELDED_PAYMENT` transaction type, introduces a Rust `orchard-postfiat` crate built around Zcash's `orchard` and `halo2_proofs` libraries, and carries over Orchard's core state model: serialized bundles, commitment-tree anchors, nullifiers for double-spend prevention, note commitments for new shielded outputs, viewing-key-based note discovery, and the Orchard `valueBalance` accounting model that represents net flow between transparent XRP balances and the shielded pool.[16]

That design means the same transaction family can support transparent-to-shielded shielding, fully shielded transfers, and shielded-to-transparent unshielding while preserving native ledger accounting. In the branch, proof-bearing bundles are parsed and checked in `preflight`, Halo2 proofs and anchor/nullifier constraints are enforced in `preclaim`, and ledger effects are applied in `doApply` by debiting transparent balances when value enters the shielded pool, crediting transparent destinations when value exits, persisting nullifiers, and appending new note commitments and anchors for future spends.[16] The companion wallet/RPC layer exposes full viewing-key registration, ledger scanning, and transaction preparation RPCs so the system can construct and observe t->z, z->z, and z->t flows end to end.[16]

The significance is not merely that Post Fiat has "a privacy branch." It is that the privacy layer is structurally based on Zcash's Orchard/Halo2 stack while remaining native to XRPL-style validated-ledger settlement. Because `ShieldedPayment` is processed as a first-class ledger transaction instead of an asynchronous external settlement step, finality should track the network's normal validated-ledger finality rather than waiting for a second protocol to reconcile state. Operationally this remains a devnet-track feature, and the intended end-to-end path is already reflected in the isolated Halo2 devnet workflows and the full-flow integration tests that exercise shielding, shielded transfer, unshielding, wallet scanning, and double-spend rejection.[16][24]

---

## References

[1] XRPL Docs. **Unique Node List (UNL)**. https://xrpl.org/docs/concepts/consensus-protocol/unl

[2] XRPL Docs. **Configure Validator List Threshold**. https://xrpl.org/docs/infrastructure/configuration/configure-validator-list-threshold

[3] XRPL Docs. **Consensus Protections Against Attacks and Failure Modes**. https://xrpl.org/docs/concepts/consensus-protocol/consensus-protections

[4] XRPL Blog. **Default UNL Migration** (2025). https://xrpl.org/blog/2025/default-unl-migration

[5] Chase, Brad, and Ethan MacBrough. **Analysis of the XRP Ledger Consensus Protocol**. arXiv:1802.07242, 2018.

[6] Amores-Sesar, Ignacio, Christian Cachin, and Jovana Mićić. **Security Analysis of Ripple Consensus**. OPODIS 2020 / LIPIcs 184, 2021.

[7] Lewis-Pye, Andrew, and Tim Roughgarden. **Byzantine Generals in the Permissionless Setting**. arXiv:2101.07095 / 2023 revision.

[8] Anthropic Docs. **Temperature**. https://docs.anthropic.com/en/docs/resources/glossary

[9] He, Horace and Thinking Machines Lab. **Defeating Nondeterminism in LLM Inference**. Thinking Machines Lab: Connectionism, 2025.

[10] SGLang Docs. **Deterministic Inference**. https://github.com/sgl-project/sgl-project.github.io/blob/main/_sources/advanced_features/deterministic_inference.md

[11] LMSYS / SGLang Team. **Towards Deterministic Inference in SGLang and Reproducible RL Training**. 2025.

[12] Yuan, Jiayi, et al. **Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference**. arXiv:2506.09501, 2025.

[13] XRPL Docs. **xrp-ledger.toml File**. https://xrpl.org/docs/references/xrp-ledger-toml

[14] Stanford HAI. **AI Index Report 2025**. https://hai.stanford.edu/ai-index/2025-ai-index-report

[15] Epoch AI. **LLM inference price trends** (2025). https://epoch.ai/data-insights/llm-inference-price-trends

[16] `postfiatd` branch research, inspected March 16, 2026. Review of `halo2-devnet-integration` branch.

[17] XRPL Docs. **Common Misunderstandings about Freezes**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/common-misconceptions-about-freezes

[18] XRPL Docs. **Deep Freeze**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/deep-freeze

[19] U.S. Department of the Treasury, OFAC. **FAQ 560**. https://ofac.treasury.gov/faqs/560

[20] U.S. Department of the Treasury, OFAC. **FAQ 1021**. https://ofac.treasury.gov/faqs/1021

[21] U.S. Department of the Treasury, OFAC. **FAQ 562**. https://ofac.treasury.gov/faqs/562

[22] U.S. Department of the Treasury, OFAC. **FAQ 646**. https://ofac.treasury.gov/faqs/646

[23] U.S. Department of the Treasury, OFAC. **Sanctions Compliance Guidance for the Virtual Currency Industry**. https://ofac.treasury.gov/system/files/126/virtual_currency_guidance_brochure.pdf

[24] `agent-hub` devnet operations research, inspected March 16, 2026. Review of Halo2 devnet workflows.

[25] `dynamic-unl-scoring` Phase 0 research, inspected March 22, 2026. Review of `docs/phase0/README.md`, `docs/phase0/WhyNotRunPodServerless.md`, and `docs/phase0/DeployQwen80B.md`.

[26] `dynamic-unl-scoring` implementation artifacts, inspected March 22, 2026. Review of `infra/deploy_endpoint.py` and `results/modal/qwen3-next-80b-instruct/2026-03-13_12-35-32/run_1.json` through `run_5.json`.

[27] `postfiatorg.github.io` benchmark script, inspected March 23, 2026. Review of `scripts/open_model_validator_determinism_suite.py`.

[28] `postfiatorg.github.io` multi-model determinism artifacts, inspected March 23, 2026. Review of `static/benchmarks/open-model-validator-determinism-full-20260323T004756Z.json` and companion CSV summaries.

---
