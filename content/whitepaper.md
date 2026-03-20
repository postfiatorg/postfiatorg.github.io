---
title: "Post Fiat Whitepaper"
layout: "single"
url: "/whitepaper/"
summary: "Post Fiat Whitepaper"
---

# Post Fiat: Auditable, Model-Assisted Validator-List Publication for XRPL-Derived Networks

**Draft — March 2026**

---

## Abstract

Post Fiat is an XRPL-derived Layer 1 that replaces opaque validator-list publication with an auditable, replayable pipeline. In XRPL-style networks, consensus security depends on the composition of the trusted validator set, but the rationale behind widely used recommended lists remains largely invisible to network participants.

Post Fiat publishes every stage of each scoring round: raw evidence collected from network data sources, a canonically normalized snapshot, a pinned execution manifest for the model and runtime stack, per-validator scores with rationales produced by a self-hosted open-weight model, and a deterministic set-construction rule with explicit churn controls.

The core technical requirement is rank-driven consensus stability: repeated executions on the same inputs must produce the same pairwise rankings, top-k overlap, and inclusion decisions. Preliminary validation on PFT Ledger's testnet — 42 validators scored by Qwen3-Next-80B-A3B-Instruct-FP8 under SGLang's deterministic inference mode — achieved bit-identical output across five independent runs.

The system proceeds in phases. Phase 1 maintains foundation authority while publishing complete audit trails. Phase 2 enables validators to independently rerun scoring in shadow mode and measure convergence. Phase 3 transfers authoritative list content to validator-converged output and decentralizes publication infrastructure.

---

## 1. Scope and Background

### 1.1 Validator-list publication is security-critical

On XRPL-style networks, each server maintains a Unique Node List (UNL) — the set of validators it trusts not to collude. UNL entries should represent independent entities chosen to minimize correlated failure.[XRPL Docs, "Unique Node List (UNL)"] Servers can consume signed recommended lists from publishers and require validators to appear on multiple lists before trusting them.[XRPL Docs, "Configure Validator List Threshold"]

Safety depends directly on validator-set overlap. Less than roughly 90% overlap between participants' trusted sets can cause divergence in the worst case.[XRPL Docs, "Consensus Protections Against Attacks and Failure Modes"] Signed recommended lists keep overlap high in practice — making list publication a security-critical governance function.

### 1.2 Publication authority is real authority

Lists are signed, versioned, sequenced, and expire. The 2025 default-UNL migration required operators to update both list URL and publisher key or risk falling out of sync.[XRPL Blog, "Default UNL Migration"] That event demonstrated that publication infrastructure is part of the governance model, not merely a distribution mechanism.

### 1.3 Formal analyses confirm the stakes

Chase and MacBrough showed that RPCA safety requires tighter UNL-overlap conditions than early informal descriptions suggested.[Chase and MacBrough 2018] Amores-Sesar, Cachin, and Mićić derived an abstract protocol from the source code and showed that safety and liveness can fail under relatively benign assumptions.[Amores-Sesar, Cachin, and Mićić 2021]

If validator-list composition is a security-critical input to consensus, making list construction auditable and eventually multi-party is a meaningful improvement — independent of changes to the base protocol's formal properties.

---

## 2. The Governance Problem

### 2.1 Opaque list construction creates information asymmetry

A recommended validator list involves two decisions: which candidates to include, and how to sign and distribute the result. In a publisher-managed model, the publisher holds private information — internal criteria, subjective judgments, compliance pressures, reputational priors — that network participants cannot observe. Participants see the published set but not the decision rule that produced it.

This is a principal–agent problem. The publisher acts on behalf of the network but retains hidden discretion over selection criteria.

### 2.2 Transparent scoring narrows hidden discretion

Under a transparent model-assisted regime, participants can observe the raw evidence, the normalized scorer input, the model and runtime manifest, the scoring prompt, the model's output scores, and the deterministic selector that produces the final list. Governance choices still exist — what evidence to collect, how to normalize it, what prompt to use — but those choices become named, inspectable, reviewable artifacts rather than unobserved residuals.

Lewis-Pye and Roughgarden's framework for permissionless consensus identifies the role of a **permitter oracle**: some mechanism determining who participates.[Lewis-Pye and Roughgarden 2023] In XRPL-style systems, validator-list publication already plays that role. Post Fiat turns it from an opaque oracle into a transparent one — inputs, policy, runtime, and outputs are all public, and in later phases, independently recomputable.

### 2.3 What remains

Publishing the full pipeline does not eliminate all discretion. The foundation still chooses evidence sources, normalization rules, the scoring prompt, and the model. But those choices are now explicit, versioned artifacts. Changing them requires a visible policy update, not a silent editorial adjustment.

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

Formally:

S_t = M_{Φ_t}(P_t, X_t)

where X_t is the normalized snapshot, Φ_t is the execution manifest (model weights, inference engine, runtime configuration), P_t is the scoring prompt, and S_t ∈ {0,…,100}^n is the score vector for n validators.

The model evaluates candidates. The final validator set is chosen by a deterministic selector operating on published scores.

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

`Institutional credibility` means durable public accountability, identifiable stewardship, and real reputational cost for misconduct — not prestige or brand recognition. Operational reliability outranks reputation proxies.

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

In autoregressive decoding, token selection under temperature τ follows a softmax distribution. As τ → 0, sampling converges to greedy selection of the argmax token. But real inference systems introduce additional variance: API batching, kernel reduction order, precision modes, tensor-parallel configuration, and hardware differences can perturb logits enough to change downstream tokens.[Anthropic Docs, "Temperature"]

External APIs should not be treated as authoritative for governance-critical rounds. Post Fiat uses self-hosted inference to control the full stack.

### 6.3 Deterministic inference is now practical

Thinking Machines Lab identified batch-size variance as a major source of nondeterministic inference and described batch-invariant kernels as a practical fix.[He 2025] SGLang implements a deterministic inference mode built on batch-invariant operators supporting FlashInfer, FlashAttention 3, and Triton backends, with a throughput overhead of roughly 34%.[SGLang Docs, "Deterministic Inference"; LMSYS Blog, 2025]

Numerical precision remains a real divergence source. Yuan et al. show that limited precision affects reproducibility, particularly for reasoning-style models, and propose mitigations such as LayerCast.[Yuan et al. 2025] This is why the execution manifest is a first-class artifact — a weight hash alone is not enough. Reproducibility depends on the whole stack.

### 6.4 Empirical validation on PFT Ledger

Post Fiat's Phase 0 validation scored 42 validators on the PFT Ledger testnet using Qwen3-Next-80B-A3B-Instruct-FP8 — an 80-billion parameter mixture-of-experts model with 3 billion active parameters — running under SGLang v0.5.6 with deterministic inference enabled on a single NVIDIA H200 GPU.

Five independent runs on the same snapshot produced bit-identical output: identical scores, identical rationales, identical token sequences. Scores ranged from 5 to 97 (mean 85.3), with the model correctly differentiating validators with perfect consensus (scoring 95+) from validators with catastrophic 30-day agreement drops (scoring below 40) and effectively offline validators (scoring below 10).

This exceeds the rank-stability target. When the execution environment is fully pinned — model weights, quantization, inference engine, attention backend, CUDA version, and determinism flags — exact reproducibility is achievable, not merely a near-term target.

### 6.5 Statistical fingerprints

Repeated-run statistics — mode, mean, variance, and selected rationales — provide evidence that a claimed model and process was actually run. Post Fiat treats these fingerprints as useful evidence for shadow verification in Phase 2, complemented by stronger cryptographic assurance layers as they mature (Section 9).

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

XRPL's two-way domain verification binds a validator public key and a domain through reciprocal claims, creating strong evidence that the same operator controls both.[XRPL Docs, "xrp-ledger.toml File"]

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

## 9. Assurance Roadmap

### 9.1 Available at launch

Phase 1 provides:

1. Published raw evidence and normalized snapshot.
2. Pinned execution manifest.
3. Self-hosted scoring — no external API dependence.
4. Deterministic selection with structured outputs.
5. Direct replay stability measurement.
6. Convergence reports beginning in Phase 2.

### 9.2 Strengthening assurance over time

Additional assurance layers on a clear development path:

- **TEE-backed scoring**: NVIDIA H100/Blackwell GPUs support hardware-level confidential computing with on-die root of trust, AES-encrypted memory, secure boot, and remote attestation. Phala Network benchmarks show throughput overhead below 7%.[Phala Network 2025]

- **Optimistic ML verification**: ORA Protocol deploys optimistic ML (opML) on Ethereum mainnet, supporting 7B+ models. Inference results post on-chain and are assumed correct; during a challenge period, any validator can initiate a bisection-based dispute game. Security requires only one honest verifier.[ORA Protocol 2025]

- **Zero-knowledge ML**: zkLLM (CCS 2024) demonstrated proofs for models up to 13B parameters in 1–15 minutes with proof sizes under 200KB. zkPyTorch proved Llama-3 inference at ~150 seconds per token. ZK proofs of a 7B–13B scoring model are feasible today on a batch basis; proving 70B+ models follows as GPU-optimized provers mature.[Sun et al. 2024; Polyhedra 2025]

- **TLS Notary**: Cryptographic proof that a specific API call returned a specific response. Useful for verifiable chains in API-based scoring rounds.[TLSNotary]

- **Multi-publisher publication paths** to reduce dependence on any single signer or hosting path.

### 9.3 Verification maturity summary

| Approach | Model Scale | Overhead | Security Model | Status |
|---|---|---|---|---|
| Statistical fingerprinting | Any size | 100× inference runs | Probabilistic | Deployed |
| TEE (H100/Blackwell) | Any size | <7% throughput | Hardware trust | Production-ready |
| opML (ORA Protocol) | 7B+ | Low (optimistic) | Crypto-economic | On-chain today |
| ZK-ML (zkLLM/zkPyTorch) | Up to 13B | 50–100× compute | Cryptographic | 12–24 months for LLM-scale |
| TLSNotary | N/A (API proofs) | ~25MB bandwidth | Cryptographic (transport) | Available |

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

Stanford's 2025 AI Index reports that GPT-3.5-equivalent inference costs fell by more than 280× between late 2022 and late 2024, with the gap between closed-weight and open-weight models narrowing sharply.[Stanford HAI, AI Index 2025] Epoch AI reports rapid fixed-performance inference price declines across task categories.[Epoch AI 2025]

Consumer-grade dual-GPU systems already achieve 27 tokens/second on 70B quantized models, matching single-H100 datacenter performance at roughly one-quarter the cost. For Phase 2 shadow verification, this means validators can afford to rerun scoring locally without datacenter-grade infrastructure.

### 11.3 Validator incentives

Post Fiat follows XRPL's principle that no direct validator reward is the best validator reward. Validators run because they use the network, not because they are paid to validate.

The foundation allocates resources specifically for Phase 2 shadow verification — paying for the work of proving that the scoring process is reproducible, not for general node operation. Credibility signals in model-assisted scoring should reflect genuine institutional commitment to the network, not a subsidy relationship with the foundation.

### 11.4 Why a distinct network

This whitepaper is not a token-distribution memorandum. Its purpose is to explain the infrastructure mechanism that justifies a distinct Post Fiat network. Validator-list publication is part of the trust surface that determines whether sophisticated users regard a ledger as credible and governable. If Post Fiat makes that surface materially more transparent than the status quo, that difference is itself an economic proposition.

The token is justified as ownership of, and settlement inside, a network with a different governance surface, compliance posture, and credibility profile. The investment case starts with governance legitimacy and network utility.

---

## 12. Boundaries

The claim is comparative, not magical. A published, replayable judgment layer is easier to audit, challenge, and correct than an unpublished rubric or informal committee process.

The boundaries are clear:

- Model scores are qualitative assessments, not mathematical proofs.
- Convergent outputs do not by themselves imply social independence among validators.
- Exact reproducibility across arbitrary GPU architectures requires policy constraints on the execution environment.
- Concentration monitoring is an ongoing operational discipline, not a one-time fix.

These boundaries define engineering work ahead, not reasons to defer.

---

## 13. Conclusion

Validator-list publication is a real governance surface. It determines overlap, concentration, and the security envelope in which consensus operates. Widely used recommended lists remain only partially legible to the public.

Post Fiat replaces opaque editorial selection with a public, replayable, model-assisted pipeline: collect evidence, normalize it canonically, pin the execution environment, score candidates under a published policy, select the set deterministically, publish the artifacts, and shift authority only after convergence is demonstrated.

Preliminary validation confirms that the approach works. Scoring 42 PFT Ledger validators with a self-hosted 80B-parameter model under deterministic inference produced bit-identical output across five independent runs — exact reproducibility, not merely rank stability.

The broader `postfiatd` roadmap includes adjacent protocol work — validator-consensus account exclusion and Orchard/Halo2 privacy — documented in Appendix B. The publication mechanism remains the narrow core of this paper.

---

## Appendix A — Phase 0 Benchmark: PFT Ledger Testnet

### A.1 Model selection

Phase 0 evaluated models across two benchmark rounds to find the best combination of scoring quality, determinism, and single-GPU feasibility:

- **Round 1** tested large models via external API (Qwen3-235B-A22B variants, MiniMax-M1-80B) to establish quality baselines.
- **Round 2** tested H200-compatible models via self-hosted inference (Qwen3-Next-80B-A3B, Qwen3-32B, GPT-OSS-120B) to find a model that fits on a single GPU with FP8 quantization.

Qwen3-Next-80B-A3B-Instruct-FP8 was selected: comparable scoring quality to the 235B variant, 80B total parameters with only 3B active (mixture-of-experts), fits on a single H200 with headroom, and achieved 100% determinism under SGLang's deterministic inference mode.

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

Five independent runs on the same snapshot produced bit-identical output:

- Same scores for all 42 validators.
- Same rationale text, token for token.
- Same JSON structure and ordering.

This exceeds the >99% rank-stability target established in the Phase 0 decision gate. Under a fully pinned execution environment, exact reproducibility — not merely statistical stability — is achievable.

---

## Appendix B — Adjacent Protocol Extensions in `postfiatd`

### B.1 Validator-consensus account exclusion

In addition to validator-list publication, `postfiatd` includes a PostFiat-specific account-exclusion mechanism. Two amendments, `PF_AccountExclusion` and `PF_ValidatorVoteTracking`, allow trusted validators to add or remove account exclusions through validation traffic, track those votes on-ledger, and maintain an exclusion view over the active validator set.[postfiatd branch research, 2026]

The relevant distinction from standard XRPL is that exclusion is not just an issuer-side freeze on an issued asset. In `postfiatd`, an account can become excluded by validator consensus once the exclusion threshold is met, and generic transaction processing rejects transactions when either the sender or destination account is excluded.[postfiatd branch research, 2026]

This is a governance primitive, not merely a token-control primitive. It allows the network to say: a specific account may not participate, regardless of whether the transaction involves an issuer-controlled IOU.

### B.2 Why exclusion is materially different from standard XRPL freezes

Standard XRPL already supports trust-line freeze, deep freeze, global freeze, and clawback for issued assets. Those are real controls, but they are primarily issuer-side controls over IOUs and trust lines rather than validator-governed network-wide exclusion of native XRP accounts or transaction counterparties.[XRPL Docs, "Common Misunderstandings about Freezes"; XRPL Docs, "Deep Freeze"; postfiatd branch research, 2026]

For sanctions-style enforcement, that distinction matters. OFAC states that virtual-currency compliance obligations are the same as fiat-currency obligations, and that U.S.-subject persons are generally prohibited from engaging in or facilitating prohibited transactions involving blocked persons.[OFAC FAQ 560; OFAC FAQ 1021] A validator-consensus rule that rejects transactions to or from identified accounts is therefore materially closer to the policy target than a narrower IOU-freeze model.

That advantage should not be overstated. The exclusion path only helps when the relevant amendments are enabled and enough validators actually reach the threshold. OFAC also states that listed digital-currency addresses are not exhaustive, and that blocking/reporting duties continue when a U.S. person actually holds blocked property.[OFAC FAQ 562; OFAC FAQ 646; OFAC Virtual Currency Guidance] So Post Fiat's exclusion mechanism is best understood as a stronger protocol-layer enforcement primitive inside a larger compliance program, not as a complete compliance solution by itself.

### B.3 Orchard / Halo2 privacy as a parallel protocol extension

Separately, the `halo2-devnet-integration` branch of `postfiatd` ports Zcash's Orchard privacy model into an XRPL-derived ledger rather than treating privacy as a mixer, sidecar, or external bridge. It adds the `OrchardPrivacy` amendment and a native `ttSHIELDED_PAYMENT` transaction type, introduces a Rust `orchard-postfiat` crate built around Zcash's `orchard` and `halo2_proofs` libraries, and carries over Orchard's core state model: serialized bundles, commitment-tree anchors, nullifiers for double-spend prevention, note commitments for new shielded outputs, viewing-key-based note discovery, and the Orchard `valueBalance` accounting model that represents net flow between transparent XRP balances and the shielded pool.[postfiatd branch research, 2026]

That design means the same transaction family can support transparent-to-shielded shielding, fully shielded transfers, and shielded-to-transparent unshielding while preserving native ledger accounting. In the branch, proof-bearing bundles are parsed and checked in `preflight`, Halo2 proofs and anchor/nullifier constraints are enforced in `preclaim`, and ledger effects are applied in `doApply` by debiting transparent balances when value enters the shielded pool, crediting transparent destinations when value exits, persisting nullifiers, and appending new note commitments and anchors for future spends.[postfiatd branch research, 2026] The companion wallet/RPC layer exposes full viewing-key registration, ledger scanning, and transaction preparation RPCs so the system can construct and observe t->z, z->z, and z->t flows end to end.[postfiatd branch research, 2026]

The significance is not merely that Post Fiat has "a privacy branch." It is that the privacy layer is structurally based on Zcash's Orchard/Halo2 stack while remaining native to XRPL-style validated-ledger settlement. Because `ShieldedPayment` is processed as a first-class ledger transaction instead of an asynchronous external settlement step, finality should track the network's normal validated-ledger finality rather than waiting for a second protocol to reconcile state. Operationally this remains a devnet-track feature, and the intended end-to-end path is already reflected in the isolated Halo2 devnet workflows and the full-flow integration tests that exercise shielding, shielded transfer, unshielding, wallet scanning, and double-spend rejection.[postfiatd branch research, 2026; agent-hub devnet operations research, 2026]

---

## References

### XRPL protocol and validator lists

- XRPL Docs. **Unique Node List (UNL)**. https://xrpl.org/docs/concepts/consensus-protocol/unl
- XRPL Docs. **Consensus Protections Against Attacks and Failure Modes**. https://xrpl.org/docs/concepts/consensus-protocol/consensus-protections
- XRPL Docs. **Configure Validator List Threshold**. https://xrpl.org/docs/infrastructure/configuration/configure-validator-list-threshold
- XRPL Docs. **xrp-ledger.toml File**. https://xrpl.org/docs/references/xrp-ledger-toml
- XRPL Docs. **Common Misunderstandings about Freezes**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/common-misconceptions-about-freezes
- XRPL Docs. **Deep Freeze**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/deep-freeze
- XRPL Blog. **Default UNL Migration** (2025). https://xrpl.org/blog/2025/default-unl-migration

### Consensus research

- Chase, Brad, and Ethan MacBrough. **Analysis of the XRP Ledger Consensus Protocol**. arXiv:1802.07242, 2018.
- Amores-Sesar, Ignacio, Christian Cachin, and Jovana Mićić. **Security Analysis of Ripple Consensus**. OPODIS 2020 / LIPIcs 184, 2021.

### Mechanism design and signaling

- Spence, Michael. **Job Market Signaling**. *Quarterly Journal of Economics*, 1973.
- Lewis-Pye, Andrew, and Tim Roughgarden. **Byzantine Generals in the Permissionless Setting**. arXiv:2101.07095 / 2023 revision.

### Inference stability and reproducibility

- Anthropic Docs. **Temperature**. https://docs.anthropic.com/en/docs/resources/glossary
- He, Horace and Thinking Machines Lab. **Defeating Nondeterminism in LLM Inference**. Thinking Machines Lab: Connectionism, 2025.
- SGLang Docs. **Deterministic Inference**. https://github.com/sgl-project/sgl-project.github.io/blob/main/_sources/advanced_features/deterministic_inference.md
- LMSYS / SGLang Team. **Towards Deterministic Inference in SGLang and Reproducible RL Training**. 2025.
- Yuan, Jiayi, et al. **Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference**. arXiv:2506.09501, 2025.

### Verification and cryptographic assurance

- Phala Network. **TEE Benchmarks for GPU Inference**. 2025.
- ORA Protocol. **Optimistic Machine Learning (opML)**. 2025.
- Sun, Haochen, et al. **zkLLM: Zero Knowledge Proofs for Large Language Models**. ACM CCS, 2024.
- Polyhedra Network. **zkPyTorch**. 2025.
- TLSNotary Project. https://tlsnotary.org

### Economics

- Stanford HAI. **AI Index Report 2025**. https://hai.stanford.edu/ai-index/2025-ai-index-report
- Epoch AI. **LLM inference price trends** (2025). https://epoch.ai/data-insights/llm-inference-price-trends

### Post Fiat implementation and sanctions policy

- `postfiatd` branch research, inspected March 16, 2026. Review of `halo2-devnet-integration` branch files including `include/xrpl/protocol/detail/features.macro`, `src/libxrpl/protocol/STValidation.cpp`, `src/xrpld/app/consensus/RCLConsensus.cpp`, `src/xrpld/app/consensus/RCLValidations.cpp`, `src/xrpld/app/misc/ExclusionManager.h`, `src/xrpld/app/tx/detail/Change.cpp`, `src/xrpld/app/tx/detail/Transactor.cpp`, `orchard-postfiat/src/lib.rs`, `orchard-postfiat/src/bundle_real.rs`, `orchard-postfiat/src/ffi/bridge.rs`, `src/xrpld/app/tx/detail/ShieldedPayment.cpp`, and `src/test/rpc/OrchardFullFlow_test.cpp`.
- `agent-hub` devnet operations research, inspected March 16, 2026. Review of `products/blockchain/systems/massive_rippled_pr_system/validator_churn_test_playbook.md` and the documented `halo2-devnet-build.yml`, `halo2-devnet-deploy.yml`, `halo2-devnet-update.yml`, and `halo2-devnet-destroy.yml` workflows for isolated end-to-end validator testing.
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 560**. https://ofac.treasury.gov/faqs/560
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 562**. https://ofac.treasury.gov/faqs/562
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 646**. https://ofac.treasury.gov/faqs/646
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 1021**. https://ofac.treasury.gov/faqs/1021
- U.S. Department of the Treasury, Office of Foreign Assets Control. **Sanctions Compliance Guidance for the Virtual Currency Industry**. https://ofac.treasury.gov/system/files/126/virtual_currency_guidance_brochure.pdf

---
