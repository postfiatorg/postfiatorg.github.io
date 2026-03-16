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

Post Fiat is an XRPL-derived Layer 1 design that turns validator-list publication from an opaque publisher function into a replayable public pipeline. On XRPL-style networks, consensus depends on the construction of the trusted validator set: which validators are included, why they were included, how concentration is managed, and how list updates are published. Today, XRPL provides signed validator lists, multiple publisher support, and configurable thresholds, but the rationale behind widely used recommended lists remains only partially visible.

Post Fiat publishes: (i) raw evidence, (ii) a normalized scoring snapshot, (iii) a pinned execution manifest for the model/runtime stack, (iv) model-produced candidate scores and short rationales, and (v) a deterministic set-construction rule with explicit churn controls. The result is a material reduction in information asymmetry between list publisher and network participants.

The core technical requirement is **effective rank-driven consensus**: repeated executions of the same scoring process on the same inputs must produce stable pairwise rankings, stable top-k overlap, and stable inclusion/exclusion decisions near the validator-set cutoff. Exact token-level equality is desirable when available, but rank stability is the primary operational target.

Post Fiat proceeds in phases. In **Phase 1**, a foundation remains the authoritative list publisher but publishes a complete audit trail. In **Phase 2**, validators rerun the same scoring process in shadow mode and publicly measure convergence. In **Phase 3A**, if convergence is sustained, authoritative list content shifts from foundation-only output to validator-converged output. **Phase 3B** decentralizes snapshot assembly, round announcement, list signing, and delivery infrastructure.

In parallel, current `postfiatd` work shows that this publication model can coexist with adjacent protocol extensions: a validator-consensus account-exclusion path and a native Orchard/Halo2 privacy path derived from Zcash's Orchard design. Those extensions are not the same thing as validator-list publication, but they matter because they show how governance, compliance controls, and privacy can evolve inside the same XRPL-derived stack.

---

## 1. Scope and Background

### 1.1 Validator-list publication is security-critical

XRPL documentation defines a Unique Node List (UNL) as the set of validators a server trusts not to collude, and stresses that UNL entries should represent independent entities chosen to minimize correlated failure or malicious collusion.[XRPL Docs, "Unique Node List (UNL)"] Servers can consume one or more recommended validator lists from publishers, and can require that a validator appear on a threshold number of lists before it is trusted.[XRPL Docs, "Configure Validator List Threshold"]

XRPL's safety depends on the overlap and composition of trusted validators. XRPL's own "Consensus Protections" page states that less than roughly 90% overlap can cause participants to diverge in the worst case, and that signed recommended lists are used in practice to keep overlap high.[XRPL Docs, "Consensus Protections Against Attacks and Failure Modes"]

Validator-list publication is a security-sensitive governance function.

### 1.2 Publication authority is real authority

XRPL's validator-list mechanism acknowledges that list publication is a trust surface. Lists are signed, versioned, sequenced, and expire. The 2025 default-UNL migration required operators to update both the list URL and the publisher key, or risk falling out of sync.[XRPL Blog, "Default UNL Migration"] XRPL's documentation also notes that the default configuration uses published lists from recognized publishers and that servers configured in this way achieve full overlap with others using the same configuration.[XRPL Docs, "Consensus Protections Against Attacks and Failure Modes"]

That migration was evidence that publication infrastructure itself is part of the governance model.

### 1.3 Formal analyses confirm the stakes

Formal analyses of RPCA have identified important constraints and failure cases. Chase and MacBrough showed that safety requires much tighter UNL-overlap conditions than early informal descriptions suggested.[Chase and MacBrough 2018] Amores-Sesar, Cachin, and Mićić later derived an abstract protocol from the source code and showed that safety and liveness may fail in simple executions under relatively benign assumptions.[Amores-Sesar, Cachin, and Mićić 2021]

If validator-list composition is a security-critical input to consensus, then making list construction auditable and eventually multi-party is a meaningful improvement — independent of whether the base protocol's formal properties change.

---

## 2. The Governance Problem: Validator Selection as a Principal–Agent Mechanism

### 2.1 Opaque list construction creates information asymmetry

A recommended validator list is a mechanism with two layers:

1. **Selection**: which candidates are included, retained, or removed.
2. **Publication**: how that list is signed, distributed, and updated.

In a publisher-managed model, the publisher P has private information Θ_P: internal criteria, soft constraints, subjective judgments, compliance pressures, reputational priors, and institutional incentives. Network participants observe only the resulting published set V_t at time t.

This is a principal–agent problem with hidden information. The agent (publisher) chooses an outcome on behalf of the principals (network participants), but the principals cannot directly observe the full decision rule. The result is a persistent information asymmetry:

V_t = G_t(X_t, Θ_P)

where:
- X_t is the observable candidate evidence at round t,
- Θ_P is the publisher's hidden decision state,
- G_t is the actual selection-and-publication function.

Under an opaque regime, participants mostly observe V_t and fragments of X_t, but not Θ_P and not the full effective mechanism.

### 2.2 Transparent scoring narrows hidden discretion

Under a transparent model-assisted regime, participants observe:
- raw evidence R_t,
- normalized scorer input X_t,
- model/runtime manifest Φ_t,
- prompt/policy specification P_t,
- model scores S_t,
- deterministic selector G,
- published validator list V_t.

The effective uncertainty about how the list came to be drops materially:

H(Θ_P | V_t) > H(Θ_P | R_t, X_t, Φ_t, P_t, S_t, G)

Governance choices remain in what evidence is collected, how it is normalized, what prompt is used, and when the network updates policy — but those choices are moved into named, inspectable, reviewable artifacts instead of remaining an unobserved residual.

### 2.3 The mechanism-design framing

The Revelation Principle says that if a desirable social choice rule is implementable, it can be implemented by a direct mechanism with truthful revelation under appropriate assumptions. The operational lesson is direct:

> If the network publishes the evidence, the policy, the execution environment, and the outcome, hidden discretion has less room to hide.

The benefit is a reduction in unverifiable editorial power.

### 2.4 A transparent permitter oracle

Lewis-Pye and Roughgarden's framework for permissionless consensus emphasizes the role of a **permitter oracle**: some mechanism must determine who is effectively allowed to participate.[Lewis-Pye and Roughgarden 2023] In XRPL-style systems, validator-list publication already plays that role for the recommended trust set.

Post Fiat turns this from an opaque publisher oracle into a **transparent, auditable permitter oracle**: the inputs are public, the policy is public, the runtime configuration is public, the outputs are public, and in later phases, the outputs can be independently recomputed and compared.

---

## 3. Design Goals

Post Fiat is designed around six goals.

### 3.1 Auditability over mystique

The value of the system comes from publishing the entire round pipeline. "The AI decided" is not a sufficient explanation. A good round explains itself in artifacts.

### 3.2 Stability over single-run purity

Governance needs stable rankings and stable set membership more than it needs perfect word-for-word transcript identity in every environment. The operational target is the same practical validator set across runs, or explainable bounded differences.

### 3.3 Narrow authority transfer

Authority moves only after it is measured. A foundation can remain authoritative in Phase 1 while publishing the evidence necessary for others to audit and later reproduce the process.

### 3.4 Explicit concentration management

Validator diversity requires naming the concentration surfaces that matter:
- country,
- ASN,
- cloud provider,
- datacenter,
- operator/entity identity.

### 3.5 Conservative failure behavior

A missed round, failed publish, stale manifest, or convergence drop degrades to a last known-good list or foundation publication.

### 3.6 Compatibility with existing validator-list mechanics

Phase 1 fits XRPL-style list publication as it already exists: signed lists, explicit publisher keys, sequence numbers, expirations, and standard retrieval paths.

---

## 4. Round Architecture

Each scoring round is a pipeline. The round is reproducible from artifacts.

### 4.1 Stage 1: Evidence collection

A round collects candidate evidence from multiple sources:

1. **Objective operational metrics**: agreement rates, uptime, software version and patch hygiene, amendment behavior, fee-vote behavior, missed validations, long-run operational consistency.

2. **Identity and attestation signals**: verified / not verified, institutional / individual / unknown, domain-attested / not domain-attested, optional public operator metadata.

3. **Concentration and correlation signals**: country, ASN, cloud provider, datacenter region, operator clustering.

4. **Low-confidence observer-dependent metrics**: peer count, topology position, latency from a given observer. These are weighted cautiously because they reflect a specific vantage point rather than a universal property.

### 4.2 Stage 2: Deterministic normalization

Raw evidence is transformed into a canonical scoring snapshot — the exact scorer input. The normalization step exists because raw evidence alone is insufficient for reproducibility. If two operators consume the same source data but transform it differently, they are running different rounds.

A round publishes:
- the raw evidence,
- the normalized snapshot,
- and the hash of the normalized snapshot.

### 4.3 Stage 3: Pinned model-assisted scoring

A pinned local model processes the normalized snapshot under a published prompt and outputs:
- an integer score per candidate,
- a short rationale per candidate,
- and optionally additional structured fields useful for diagnostics.

Let:
- X_t be the normalized snapshot at round t,
- Φ_t be the execution manifest (model, weights, tokenizer, engine, runtime),
- P_t be the scoring prompt/policy,
- M_{Φ_t} be the scorer instantiated under that manifest.

Then:

S_t = M_{Φ_t}(P_t, X_t)

where S_t ∈ {0,…,100}^n is the vector of candidate scores for n validators.

The model evaluates candidates. The final validator set is chosen by a deterministic set constructor operating on published scores.

### 4.4 Stage 4: Deterministic list construction

The final recommended validator set is built by a deterministic selector:

U_t = G(S_t, U_{t-1}; θ, K, δ)

where:
- U_t is the selected validator set at round t,
- U_{t-1} is the prior round's set,
- θ is a minimum score threshold,
- K is the maximum list size,
- δ is the churn-control margin.

A simple instance of G:

1. Score all candidates.
2. Discard scores below θ.
3. Rank remaining candidates.
4. Include at most K candidates.
5. Apply churn control: a challenger displaces an incumbent only if it exceeds the incumbent by at least δ, unless a hard-failure condition applies.

The model is used for **candidate evaluation**. **Set publication** is deterministic.

### 4.5 Stage 5: Publication artifacts

Each round publishes at least the following bundle:

```text
round_t/
├── raw/
│   ├── source_a.json
│   ├── source_b.json
│   └── ...
├── normalized_snapshot.json
├── execution_manifest.json
├── prompt_version.txt
├── scores.json
├── selection_result.json
├── vl.json
└── metadata.json
```

The critical property is chain-of-custody:

raw evidence → normalized snapshot → scores → selected set → signed published list

A round can also anchor the root hash or CID of this artifact bundle on-chain, making later equivocation materially harder.

---

## 5. Scoring Surfaces

### 5.1 What the scorer evaluates

The scoring policy is explicit about its decision surfaces:

- **Quality surfaces**: uptime, agreement, software diligence, historical reliability.
- **Identity surfaces**: operator transparency, institutional credibility, domain attestation.
- **Concentration surfaces**: country, ASN, cloud provider, datacenter, operator clustering.
- **Low-confidence observational surfaces**: latency and topology from a single observer.

The scorer gives the greatest weight to objective, long-horizon indicators and lower weight to single-observer signals.

### 5.2 Concentration as a portfolio problem

A validator list is not just a ranking of individually good nodes. It is also a portfolio problem. A set of individually strong validators can still be collectively fragile if many share the same cloud provider, jurisdiction, ASN, or operator.

List construction has both:
- **per-candidate quality**, and
- **set-level correlation risk**.

The concentration surfaces are explicit, published, and reviewable.

### 5.3 Identity without unnecessary PII

Identity data is minimal. The public system publishes:

- `verified: true/false`
- `entity_type: institutional / individual / unknown`
- `domain_attested: true/false`

This improves auditability without turning validator governance into a doxxing exercise.

---

## 6. Stability and Reproducibility

### 6.1 The right target is rank stability

The practical governance targets are:

1. **Pairwise rank agreement**
2. **Top-k overlap**
3. **Cutoff-band stability**
4. **Observed churn across rounds**

These are measured directly.

Let s^(a) and s^(b) be score vectors from two independent runs on the same snapshot. Define pairwise rank agreement as:

PRA(a,b) = (2 / n(n-1)) Σ_{i<j} 𝟙[sign(s_i^(a) − s_j^(a)) = sign(s_i^(b) − s_j^(b))]

Define top-k overlap as:

TopK(a,b;k) = |Top_k(s^(a)) ∩ Top_k(s^(b))| / k

And round-to-round churn as:

Churn(t) = 1 − |U_t ∩ U_{t-1}| / |U_t|

### 6.2 Low-temperature decoding is necessary but not sufficient

In autoregressive decoding, token selection under temperature τ is:

P(x_t = i) = exp(z_i / τ) / Σ_j exp(z_j / τ)

As τ → 0, sampling converges toward greedy selection of the argmax token. But real inference systems add implementation-level variance: API batching, kernel reduction order, precision modes, tensor-parallel configuration, and hardware differences can all perturb logits enough to change downstream tokens.

This is why external APIs should not be treated as authoritative for governance-critical rounds. Even at temperature 0, identical inputs may produce different outputs across API calls due to serving infrastructure variance.[Anthropic Docs, "Temperature"]

### 6.3 Recent serving work has narrowed the gap materially

Thinking Machines Lab identified batch-size variance as a major source of nondeterministic inference and described batch-invariant kernels as a practical fix.[He 2025] SGLang has since documented a deterministic inference mode built on batch-invariant operators supporting FlashInfer, FlashAttention 3, and Triton backends.[SGLang Docs, "Deterministic Inference"] The SGLang team reports an average slowdown of roughly 34% relative to its nondeterministic baseline in tested configurations.[LMSYS Blog, 2025]

For a protocol that standardizes model weights, prompt, tokenizer, inference engine, runtime flags, and hardware profile, exact reproducibility is increasingly achievable — and rank stability is already a realistic near-term target.

### 6.4 Precision matters

Numerical precision remains a real source of divergence. Yuan et al. show that limited precision can materially affect reproducibility, particularly for reasoning-style models, and propose mitigation strategies such as LayerCast to improve stability.[Yuan et al. 2025]

This is one reason the **execution manifest** is a first-class artifact. A weight hash alone is not enough. Reproducibility depends on the whole stack.

### 6.5 Preliminary benchmark

The project's internal pilot benchmark scored 35 current XRPL validator URLs in two independent 100-run batches under a fixed prompt, producing identical mode scores for all 35 candidates. Before authoritative deployment, the project will publish the prompt, manifest, raw outputs, and replay harness for public verification. A compact excerpt appears in **Appendix A**.

### 6.6 Statistical fingerprints

Repeated-run statistics — mode, mean, variance, selected rationales — provide evidence that a claimed model/process was actually run. Their strength depends on benchmark design, number of runs, number of candidates, output space structure, and adversary knowledge. Post Fiat treats these fingerprints as useful evidence for shadow verification, complemented by stronger cryptographic assurance layers as they mature (Section 9).

---

## 7. Execution Manifest and Hashing Discipline

### 7.1 Full manifest pinning

Each round publishes a full execution manifest, including at minimum:

- model identifier,
- model snapshot revision,
- hashes of all weight shards,
- tokenizer files,
- config files,
- prompt version,
- output schema version,
- inference engine version/commit,
- attention backend,
- dtype / quantization mode,
- container image digest,
- CUDA / driver version,
- determinism flags.

This prevents silent drift.

### 7.2 Domain-separated hashing

Any hash that influences governance is domain-separated and typed. A generic commitment format:

c = SHA256(d ‖ v ‖ r ‖ h ‖ σ)

where:
- d is a domain tag,
- v is a version byte,
- r is the round identifier,
- h is a content hash,
- σ is a salt or auxiliary field.

Governance systems fail in embarrassing ways when serialization rules are implicit.

### 7.3 Replay requirements

The implementation supports:
- `replay_round(round_id)`,
- `rebuild_from_raw(round_id)`,
- and `dry_run`.

If a round cannot be replayed from its own artifacts, it is not auditable.

---

## 8. Security Model and Anti-Gaming Analysis

### 8.1 Threat model

The relevant adversaries include:
- a manipulative list publisher,
- a validator trying to cheaply imitate institutional credibility,
- operators attempting to copy others' outputs without recomputation,
- clusters of validators masquerading as independent entities,
- and operational failures in list publication itself.

### 8.2 Layered identity signals

Sybil resistance uses layered signals:

- long-run performance history,
- domain attestation via `xrp-ledger.toml`,
- minimal public verification state,
- operator clustering analysis,
- concentration analysis,
- and model-based assessment of public institutional credibility.

XRPL's two-way domain verification process binds a validator public key and a domain through reciprocal claims, creating strong evidence that the same operator controls both.[XRPL Docs, "xrp-ledger.toml File"]

### 8.3 Costly signaling and institutional credibility

Spence's costly-signaling framework applies directly. Appearing credible to a model trained on large public corpora is not free. It is typically cheaper to operate a legitimate institution well than to manufacture years of convincing public evidence across independent sources. This raises the cost of cheap Sybil identities relative to systems that treat every pseudonymous operator as equally credible by default.

### 8.4 Commit–reveal as anti-copying infrastructure

In Phase 2 shadow mode, validators commit to output hashes before reveals open:

c_i = SHA256(d ‖ v ‖ r ‖ H(S_i) ‖ σ_i)

where:
- S_i is validator i's scored output,
- H(S_i) is its content hash,
- σ_i is a random salt.

This prevents simple after-the-fact copying once a canonical output is visible.

### 8.5 Attack summary

| Attack | Mitigation | Residual risk |
|---|---|---|
| Fake domain / fake operator identity | Two-way domain attestation, public verification state, operator review | Stronger against casual spoofing than long-horizon social engineering |
| Metric gaming | Long-horizon performance metrics, public evidence, low weight on short-term optics | Possible if attacker incurs real operating cost |
| Output copying in shadow mode | Commit–reveal timing, public convergence reports | Does not prove local execution by itself |
| Hidden publisher discretion | Raw evidence + snapshot + manifest + deterministic selector | Snapshot assembly may remain centralized in early phases |
| Concentration masquerading as diversity | Country/ASN/cloud/datacenter/operator clustering | Entity resolution is imperfect; conservative defaults apply |
| Collusion among trusted validators | High-overlap requirements and public concentration analysis | Addressed by set-level correlation monitoring, not scoring alone |

---

## 9. Assurance Roadmap

### 9.1 Available immediately

The production assurance stack at launch:

1. Publish raw evidence and normalized snapshot.
2. Pin the full execution manifest.
3. Use local/self-hosted scoring for authoritative rounds.
4. Use structured outputs.
5. Use deterministic selection.
6. Measure replay stability directly.
7. In Phase 2, publish convergence reports.

This is already a materially more inspectable system than a purely editorial list.

### 9.2 Strengthening assurance over time

Additional assurance layers on a clear development path:

- **TEE-backed scoring**: NVIDIA H100/Blackwell GPUs support hardware-level confidential computing with an on-die root of trust, AES-encrypted memory, secure boot, and remote attestation. Benchmarks from Phala Network show average throughput overhead below 7%. TEE attestation proves that specific code ran on genuine, untampered hardware.

- **Optimistic ML verification**: ORA Protocol deploys optimistic ML (opML) on Ethereum mainnet, supporting 7B+ models on standard PCs. Inference results are posted on-chain and assumed correct; during a challenge period, any validator can initiate a bisection-based dispute game verified via a Fraud Proof Virtual Machine. Security requires only one honest verifier.

- **Zero-knowledge ML**: zkLLM (CCS 2024) demonstrated proofs for models up to 13 billion parameters in 1–15 minutes with proof sizes under 200KB. zkPyTorch proved Llama-3 inference at approximately 150 seconds per token. For Post Fiat's scoring task, ZK proofs of a 7B–13B scoring model are feasible today on a batch/async basis. Proving 70B models will follow as GPU-optimized provers mature.

- **TLS Notary**: Provides cryptographic proof that a specific API call returned a specific response. Combined with deterministic temperature-0 inference, this creates a verifiable chain for API-based scoring rounds.

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

## 10. Phased Deployment and Trust Model

### 10.1 Phase 1: Foundation publication with full audit trail

The foundation remains the authoritative publisher. It:
- collects evidence,
- normalizes the snapshot,
- runs the scorer,
- applies the deterministic selector,
- signs the validator list,
- and publishes the full round bundle.

Operationally centralized, fully auditable.

### 10.2 Phase 2: Validator-side shadow verification

Validators independently rerun the same round using the published snapshot and manifest. The foundation's list remains authoritative, but validators commit to and later reveal their own outputs so the network can measure:

- exact artifact matches,
- score-level agreement,
- top-k overlap,
- and list-level convergence.

This phase answers the key empirical question: **can independent operators reproduce the process closely enough for governance?**

### 10.3 Phase 3A: Content authority transfer

If Phase 2 demonstrates sustained convergence (pairwise rank agreement > 95%, top-k overlap > 90%), the authoritative content of the published list shifts from the foundation's own output to the converged validator output. The foundation may still sign and distribute the list, but it no longer has sole editorial control over the content.

### 10.4 Phase 3B: Publication decentralization

Publication authority includes snapshot assembly, round announcement, list signing, artifact hosting, and delivery path control. Phase 3B decentralizes these surfaces.

### 10.5 Fallback rules

Every phase has a conservative fallback:
- missed round → retain last known-good list,
- participation drops below threshold → revert to foundation-only publication,
- manifests diverge → treat round as diagnostic rather than authoritative,
- publication fails → preserve continuity before novelty.

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

Validator-list scoring is periodic, structured, and batchable — not a high-frequency chatbot workload. This makes it a strong candidate for self-hosted or tightly controlled inference.

The exact model size, quantization mode, and hardware profile are governance parameters. What matters is that the model discriminates among candidates meaningfully, runs under a pinned manifest, and deploys at a cost affordable for the target validator class.

### 11.2 The cost trend is decisive

Stanford's 2025 AI Index reports that GPT-3.5-equivalent inference costs fell by more than 280× between late 2022 and late 2024, and that the gap between top closed-weight and top open-weight models narrowed sharply over the same period.[Stanford HAI, AI Index 2025] Epoch AI reports rapid price declines for fixed-performance inference across task categories.[Epoch AI 2025]

A governance workload that runs weekly or monthly on a pinned local model is operationally plausible for serious validators today. Consumer-grade dual-GPU systems achieve 27 tokens/second on 70B quantized models, matching single-H100 datacenter performance at roughly one-quarter the cost. The 50× annual cost decline means the economic barrier drops by an order of magnitude each year.

### 11.3 Validator incentives

Post Fiat follows XRPL's principle that no direct validator reward is the best validator reward. Validators run because they use the network, not because they are paid to validate. This avoids the perverse dynamics of reward-driven validation — where the economic incentive to validate attracts participants whose primary interest is extraction rather than network health.

The foundation allocates resources specifically for incentivizing participation in UNL selection reproduction: the shadow verification process in Phase 2 where validators independently rerun the scoring pipeline and publish convergence data. This is a narrower, more defensible use of incentives — it pays for the specific work of proving that the scoring process is reproducible, not for the general act of running a node.

This design avoids the failure mode of bribing institutions to appear on a validator list. The credibility signal in model-assisted scoring should reflect genuine institutional commitment to the network, not a subsidy relationship with the foundation.

---

## 12. Adjacent Protocol Extensions in `postfiatd`

### 12.1 Validator-consensus account exclusion

In addition to validator-list publication, `postfiatd` includes a PostFiat-specific account-exclusion mechanism. Two amendments, `PF_AccountExclusion` and `PF_ValidatorVoteTracking`, allow trusted validators to add or remove account exclusions through validation traffic, track those votes on-ledger, and maintain an exclusion view over the active validator set.[postfiatd branch research, 2026]

The relevant distinction from standard XRPL is that exclusion is not just an issuer-side freeze on an issued asset. In `postfiatd`, an account can become excluded by validator consensus once the exclusion threshold is met, and generic transaction processing rejects transactions when either the sender or destination account is excluded.[postfiatd branch research, 2026]

This is a governance primitive, not merely a token-control primitive. It allows the network to say: a specific account may not participate, regardless of whether the transaction involves an issuer-controlled IOU.

### 12.2 Why exclusion is materially different from standard XRPL freezes

Standard XRPL already supports trust-line freeze, deep freeze, global freeze, and clawback for issued assets. Those are real controls, but they are primarily issuer-side controls over IOUs and trust lines rather than validator-governed network-wide exclusion of native XRP accounts or transaction counterparties.[XRPL Docs, "Common Misunderstandings about Freezes"; XRPL Docs, "Deep Freeze"; postfiatd branch research, 2026]

For sanctions-style enforcement, that distinction matters. OFAC states that virtual-currency compliance obligations are the same as fiat-currency obligations, and that U.S.-subject persons are generally prohibited from engaging in or facilitating prohibited transactions involving blocked persons.[OFAC FAQ 560; OFAC FAQ 1021] A validator-consensus rule that rejects transactions to or from identified accounts is therefore materially closer to the policy target than a narrower IOU-freeze model.

That advantage should not be overstated. The exclusion path only helps when the relevant amendments are enabled and enough validators actually reach the threshold. OFAC also states that listed digital-currency addresses are not exhaustive, and that blocking/reporting duties continue when a U.S. person actually holds blocked property.[OFAC FAQ 562; OFAC FAQ 646; OFAC Virtual Currency Guidance] So Post Fiat's exclusion mechanism is best understood as a stronger protocol-layer enforcement primitive inside a larger compliance program, not as a complete compliance solution by itself.

### 12.3 Orchard / Halo2 privacy as a parallel protocol extension

Separately, the `halo2-devnet-integration` branch of `postfiatd` ports Zcash's Orchard privacy model into an XRPL-derived ledger rather than treating privacy as a mixer, sidecar, or external bridge. It adds the `OrchardPrivacy` amendment and a native `ttSHIELDED_PAYMENT` transaction type, introduces a Rust `orchard-postfiat` crate built around Zcash's `orchard` and `halo2_proofs` libraries, and carries over Orchard's core state model: serialized bundles, commitment-tree anchors, nullifiers for double-spend prevention, note commitments for new shielded outputs, viewing-key-based note discovery, and the Orchard `valueBalance` accounting model that represents net flow between transparent XRP balances and the shielded pool.[postfiatd branch research, 2026]

That design means the same transaction family can support transparent-to-shielded shielding, fully shielded transfers, and shielded-to-transparent unshielding while preserving native ledger accounting. In the branch, proof-bearing bundles are parsed and checked in `preflight`, Halo2 proofs and anchor/nullifier constraints are enforced in `preclaim`, and ledger effects are applied in `doApply` by debiting transparent balances when value enters the shielded pool, crediting transparent destinations when value exits, persisting nullifiers, and appending new note commitments and anchors for future spends.[postfiatd branch research, 2026] The companion wallet/RPC layer exposes full viewing-key registration, ledger scanning, and transaction preparation RPCs so the system can construct and observe t->z, z->z, and z->t flows end to end.[postfiatd branch research, 2026]

The significance is not merely that Post Fiat has "a privacy branch." It is that the privacy layer is structurally based on Zcash's Orchard/Halo2 stack while remaining native to XRPL-style validated-ledger settlement. Because `ShieldedPayment` is processed as a first-class ledger transaction instead of an asynchronous external settlement step, finality should track the network's normal validated-ledger finality rather than waiting for a second protocol to reconcile state. Operationally this remains a devnet-track feature, and the intended end-to-end path is already reflected in the isolated Halo2 devnet workflows and the full-flow integration tests that exercise shielding, shielded transfer, unshielding, wallet scanning, and double-spend rejection.[postfiatd branch research, 2026; agent-hub devnet operations research, 2026]

---

## 13. Boundaries

A successful Post Fiat deployment proves that:
- validator-list publication can become a replayable public pipeline,
- publisher policy choices can be inspected at the level of evidence, manifest, and output,
- independent validators can reproduce the same scoring process with high agreement,
- and authority can migrate gradually from publisher-only judgment toward validator-converged content.

The boundaries are also clear. Model scores are qualitative assessments, not mathematical proofs. Convergent outputs do not by themselves imply social independence among validators. Exact reproducibility across arbitrary GPU architectures requires policy constraints on the execution environment. And concentration monitoring is an ongoing operational discipline, not a one-time fix.

These boundaries define the engineering work ahead, not reasons to defer.

---

## 14. Conclusion

Validator-list publication in XRPL-style networks is a real governance surface. It affects overlap, concentration, and therefore the security envelope in which consensus operates. XRPL already recognizes this by using signed validator lists, configurable thresholds, and explicit publisher keys. But widely used recommended lists remain only partially legible to the public.

Post Fiat replaces opaque editorial selection with a public, replayable, model-assisted pipeline:
- collect evidence,
- normalize it canonically,
- pin the execution environment,
- score candidates under a published policy,
- select the set deterministically,
- publish the artifacts,
- and shift authority only after convergence is demonstrated.

The strongest version of this idea is also the narrowest. It requires measurable claims about artifact integrity, reproducibility, rank stability, set stability, and governance transparency.

At the same time, the broader `postfiatd` line shows that this governance work can sit alongside adjacent protocol changes — including validator-consensus account exclusion and Orchard/Halo2 privacy — without reducing the validator-list proposal to marketing language. The publication mechanism remains the narrow core. The surrounding protocol experiments show where a more opinionated XRPL-derived stack may go next.

That is ambitious enough — and credible enough — to be worth building.

---

## Appendix A — Preliminary Benchmark

The following table reproduces the project's two-batch URL-scoring benchmark on 35 current XRPL validator domains. The prompt, manifest, raw outputs, and replay harness will be published before authoritative deployment.

| Validator | Run 1 Mode | Run 2 Mode |
|---|---:|---:|
| shadow.haas.berkeley.edu | 85 | 85 |
| ripple.ittc.ku.edu | 75 | 75 |
| validator.poli.usp.br | 75 | 75 |
| xrp-col.anu.edu.au | 75 | 75 |
| xrp.unic.ac.cy | 75 | 75 |
| students.cs.ucl.ac.uk | 75 | 75 |
| xrp-validator.interledger.org | 72 | 72 |
| validator.xrpl-labs.com | 65 | 65 |
| ripplevalidator.uwaterloo.ca | 65 | 65 |
| bitso.com | 65 | 65 |
| ripple.kenan-flagler.unc.edu | 55 | 55 |
| ripple.com | 55 | 55 |
| bithomp.com | 45 | 45 |
| www.bitrue.com | 45 | 45 |
| xrpscan.com | 45 | 45 |
| validator.gatehub.net | 45 | 45 |
| arrington-xrp-capital.blockdaemon.com | 45 | 45 |
| xrp.vet | 35 | 35 |
| validator.aspired.nz | 35 | 35 |
| v2.xrpl-commons.org | 35 | 35 |
| anodos.finance | 25 | 25 |
| xrpl.aesthetes.art | 25 | 25 |
| xrpkuwait.com | 25 | 25 |
| xrpgoat.com | 25 | 25 |
| data443.com | 25 | 25 |
| xpmarket.com | 25 | 25 |
| validator.xrpl.robertswarthout.com | 25 | 25 |
| cabbit.tech | 25 | 25 |
| onxrp.com | 25 | 25 |
| verum.eminence.im | 25 | 25 |
| xspectar.com | 25 | 25 |
| aureusox.com | 15 | 15 |
| ekiserrepe.es | 15 | 15 |
| jon-nilsen.no | 15 | 15 |
| katczynski.net | 15 | 15 |

A separate phrase-to-integer benchmark showed zero or near-zero variance in most cases, with a small number of higher-variance prompts preserving identical modal outputs across repeated runs.

---

## References

### XRPL protocol, validator lists, and operations

- XRPL Docs. **Unique Node List (UNL)**. https://xrpl.org/docs/concepts/consensus-protocol/unl
- XRPL Docs. **Consensus Protections Against Attacks and Failure Modes**. https://xrpl.org/docs/concepts/consensus-protocol/consensus-protections
- XRPL Docs. **Configure Validator List Threshold**. https://xrpl.org/docs/infrastructure/configuration/configure-validator-list-threshold
- XRPL Docs. **xrp-ledger.toml File**. https://xrpl.org/docs/references/xrp-ledger-toml
- XRPL Docs. **Run rippled as a Validator**. https://xrpl.org/docs/infrastructure/configuration/server-modes/run-rippled-as-a-validator
- XRPL Docs. **validator_list method**. https://xrpl.org/docs/references/http-websocket-apis/peer-port-methods/validator-list
- XRPL Docs. **Common Misunderstandings about Freezes**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/common-misconceptions-about-freezes
- XRPL Docs. **Deep Freeze**. https://xrpl.org/docs/concepts/tokens/fungible-tokens/deep-freeze
- XRPL Docs. **FAQ**. https://xrpl.org/about/faq
- XRPL Blog. **Default UNL Migration** (2025). https://xrpl.org/blog/2025/default-unl-migration
- XRPL Blog. **Move to the New XRPL Foundation Commences** (2025). https://xrpl.org/blog/2025/move-to-the-new-xrpl-foundation-commences

### Post Fiat implementation and sanctions policy

- `postfiatd` branch research, inspected March 16, 2026. Review of `halo2-devnet-integration` branch files including `include/xrpl/protocol/detail/features.macro`, `src/libxrpl/protocol/STValidation.cpp`, `src/xrpld/app/consensus/RCLConsensus.cpp`, `src/xrpld/app/consensus/RCLValidations.cpp`, `src/xrpld/app/misc/ExclusionManager.h`, `src/xrpld/app/tx/detail/Change.cpp`, `src/xrpld/app/tx/detail/Transactor.cpp`, `orchard-postfiat/src/lib.rs`, `orchard-postfiat/src/bundle_real.rs`, `orchard-postfiat/src/ffi/bridge.rs`, `src/xrpld/app/tx/detail/ShieldedPayment.cpp`, and `src/test/rpc/OrchardFullFlow_test.cpp`.
- `agent-hub` devnet operations research, inspected March 16, 2026. Review of `products/blockchain/systems/massive_rippled_pr_system/validator_churn_test_playbook.md` and the documented `halo2-devnet-build.yml`, `halo2-devnet-deploy.yml`, `halo2-devnet-update.yml`, and `halo2-devnet-destroy.yml` workflows for isolated end-to-end validator testing.
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 560: Are my OFAC compliance obligations the same, regardless of whether a transaction is denominated in digital currency or traditional fiat currency?** https://ofac.treasury.gov/faqs/560
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 562: How will OFAC identify digital currency-related information on the SDN List?** https://ofac.treasury.gov/faqs/562
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 646: How do I block digital currency?** https://ofac.treasury.gov/faqs/646
- U.S. Department of the Treasury, Office of Foreign Assets Control. **FAQ 1021: Do the prohibitions of Executive Order (E.O.) 14024 and other Russia-related sanctions extend to virtual currency?** https://ofac.treasury.gov/faqs/1021
- U.S. Department of the Treasury, Office of Foreign Assets Control. **Sanctions Compliance Guidance for the Virtual Currency Industry**. https://ofac.treasury.gov/system/files/126/virtual_currency_guidance_brochure.pdf

### Consensus and XRPL research

- Chase, Brad, and Ethan MacBrough. **Analysis of the XRP Ledger Consensus Protocol**. arXiv:1802.07242, 2018.
- Amores-Sesar, Ignacio, Christian Cachin, and Jovana Mićić. **Security Analysis of Ripple Consensus**. OPODIS 2020 / LIPIcs 184, 2021.
- Tumas, Vytautas, Sean Rivera, Damien Magoni, and Radu State. **Topology Analysis of the XRP Ledger**. SAC 2023 / arXiv:2205.00869.

### Mechanism design, information asymmetry, and signaling

- Hurwicz, Leonid. **Optimality and Informational Efficiency in Resource Allocation Processes**. 1960.
- Akerlof, George. **The Market for "Lemons": Quality Uncertainty and the Market Mechanism**. *Quarterly Journal of Economics*, 1970.
- Myerson, Roger. **Optimal Auction Design**. *Mathematics of Operations Research*, 1981.
- Spence, Michael. **Job Market Signaling**. *Quarterly Journal of Economics*, 1973.
- Douceur, John. **The Sybil Attack**. IPTPS, 2002.
- Lewis-Pye, Andrew, and Tim Roughgarden. **Byzantine Generals in the Permissionless Setting**. arXiv:2101.07095 / 2023 revision.

### Inference stability and reproducibility

- Holtzman, Ari, et al. **The Curious Case of Neural Text Degeneration**. ICLR, 2020.
- Anthropic Docs. **Temperature**. https://docs.anthropic.com/en/docs/resources/glossary
- He, Horace and Thinking Machines Lab. **Defeating Nondeterminism in LLM Inference**. Thinking Machines Lab: Connectionism, 2025.
- SGLang Docs. **Deterministic Inference**. https://github.com/sgl-project/sgl-project.github.io/blob/main/_sources/advanced_features/deterministic_inference.md
- LMSYS / SGLang Team. **Towards Deterministic Inference in SGLang and Reproducible RL Training**. 2025.
- Yuan, Jiayi, et al. **Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference**. arXiv:2506.09501, 2025.
- Dong, Yixin, et al. **XGrammar: Flexible and Efficient Structured Generation Engine for Large Language Models**. arXiv:2411.15100 / MLSys 2025.

### Verification and cryptographic assurance

- Phala Network. **TEE Benchmarks for GPU Inference**. 2025.
- ORA Protocol. **Optimistic Machine Learning (opML)**. 2025.
- Sun, Haochen, et al. **zkLLM: Zero Knowledge Proofs for Large Language Models**. ACM CCS, 2024.
- Polyhedra Network. **zkPyTorch**. 2025.
- TLSNotary Project. https://tlsnotary.org

### Incentives and economics

- Brünjes, Lars, Aggelos Kiayias, Elias Koutsoupias, and Aikaterini-Panagiota Stouka. **Reward Sharing Schemes for Stake Pools**. arXiv:1807.11218 / EuroS&P 2020.
- Stanford HAI. **AI Index Report 2025**. https://hai.stanford.edu/ai-index/2025-ai-index-report
- Epoch AI. **LLM inference price trends** (2025). https://epoch.ai/data-insights/llm-inference-price-trends

### Representation convergence

- Jha, Minyoung, et al. **The Strong Platonic Representation Hypothesis**. 2025.

---
