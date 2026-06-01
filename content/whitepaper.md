---
title: "Post Fiat Whitepaper"
layout: "whitepaper_page"
url: "/whitepaper/"
summary: "Post Fiat Whitepaper"
---

# Post Fiat: Auditable, Model-Assisted Validator-List Publication for XRPL-Derived Networks

**May 2026 revision**

**Originally published to production:** 2026-03-23 02:07:45 UTC

**Current revision:** 2026-05-31, incorporating live Phase 1 testnet validator-list publication evidence and the Qwen3.6/SGLang deterministic replay artifacts.

---

## Abstract

Post Fiat is an XRPL-derived Layer 1 that replaces opaque validator-list publication with an auditable, replayable pipeline. In XRPL-style networks, consensus security depends on the composition of the trusted validator set, but the rationale behind widely used recommended lists remains largely invisible to network participants.

Post Fiat publishes every stage of each scoring round: raw evidence, a canonical snapshot, a pinned model/runtime manifest, per-validator scores with rationales from a self-hosted open-weight model, and a deterministic set-construction rule with explicit churn controls.

The core technical requirement is rank-driven consensus stability: repeated executions on the same inputs must preserve pairwise rankings, top-k overlap, and inclusion decisions. The current validation uses Qwen/Qwen3.6-27B-FP8 through a pinned Modal/SGLang single-GPU stack; Appendix A reports exact replay on the saved XRPL UNL credibility benchmark and the 42-validator PFT Ledger task. These are single-stack proof-of-possibility results, not authority-transfer evidence.

Deployment proceeds in phases. Phase 1 keeps foundation authority while publishing complete audit trails and is live on the public testnet, where rounds 4 through 7 completed with audit bundle CIDs, publication commits, and PFTL memo anchors. Phase 2 lets validators rerun scoring in shadow mode and measure convergence. Phase 3 transfers authoritative list content to validator-converged output and decentralizes publication infrastructure.

The claim is narrow: validator-list publication can be made more auditable and contestable than today's opaque publisher process. It does not claim that model-assisted scoring has beaten simpler deterministic heuristics or that the current benchmark package justifies production authority transfer. Adjacent account-exclusion and Orchard/Halo2 privacy work exists in the broader `postfiatd` codebase, but it is covered in a [separate research note](/posts/orchard-privacy-research/) and is outside this paper's proof surface.

---

## Executive Summary

Post Fiat turns validator-list publication from an opaque trust recommendation into a public evidence pipeline that validators can inspect, replay, challenge, and eventually recompute. Every inclusion decision has named inputs, a pinned scorer, a deterministic selector, signed artifacts, and an escalation path when reviewers disagree.

Under a pinned SGLang single-GPU stack, the same snapshot and prompt can produce the same score map across repeated runs. The score still has to be judged; the gain is that the round becomes a replayable object rather than a private opinion.

The model layer earns its place only if it improves over a rigid rubric. Its intended role is to synthesize borderline cases where raw metrics are similar but governance meaning differs: operator independence, entity continuity, concentration risk, public accountability, and whether claimed diversity is real or cosmetic. A deterministic rules engine remains the baseline to beat.

This belongs in a distinct Post Fiat network because validator-list publication is part of the network's trust product, not an external analytics feed. A standalone XRPL-side tool can advise a publisher; it cannot make artifact publication, shadow verification, on-chain anchoring, and validator convergence part of the ledger's default governance surface. The economic thesis is tied to adoption of a ledger with a visibly more legible validator-selection process, not to the mere existence of a scoring script.

What changes for each audience:

- Validators can inspect the evidence used to score them, rerun the scorer in shadow mode, and challenge policy or data errors on a public record.
- Users and integrators can see why the recommended validator set changed instead of trusting an unexplained publisher update.
- Builders get a reproducible governance primitive: raw evidence to normalized snapshot to score map to selected list to signed publication.
- Investors get a focused thesis: Post Fiat is valuable only if a more legible trust surface makes the network more credible for real settlement and coordination use cases.

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

Publishing the full pipeline reduces discretion; it does not remove it. The foundation still chooses evidence sources, normalization rules, the scoring prompt, and the model. Those choices become explicit, versioned artifacts. Changing them requires a visible policy update, not a silent editorial adjustment.

The mitigation is decomposition: evidence can be challenged, prompts can be diffed, model changes can be rerun, score rationales can be inspected, and selector rules can be compared against alternatives. Bias, error, and capture remain possible, but they become easier to locate.

### 2.4 What this paper does and does not claim

This paper claims:

- validator-list publication is a real governance surface worth making auditable;
- a published evidence-to-list pipeline is easier to inspect and challenge than opaque publisher discretion;
- under one pinned stack, deterministic model-assisted scoring is operationally feasible;
- phased deployment with shadow verification is a more credible path than immediate authority transfer.

This paper does **not** claim:

- that model-assisted scoring is already superior to simpler deterministic or committee-based approaches;
- that the current benchmark package is sufficient to justify production authority transfer;
- that decentralization is already achieved in Phase 1 or Phase 2;
- that adjacent privacy or exclusion features are part of the validator-publication proof.

### 2.5 Why use model judgment at all?

Validator-list publication already contains qualitative judgment: reputation, operational quality, independence, and legitimacy are weighed even when the rubric is unpublished. A published machine-assisted layer is justified only if it makes that judgment easier to audit, replay, contest, and compare.

Operator independence illustrates the need. Two candidates can look similar on uptime, version freshness, and other raw metrics while differing materially in governance value: one may be a second validator behind an already represented operator, ASN, or hosting cluster, while another may be independently run, publicly accountable, and more valuable for set diversity despite slightly weaker headline numbers. A rigid rubric can count some of these fields, but it still needs a judgment layer to decide whether apparent diversity is real, whether identity evidence is substantive, and whether a borderline inclusion improves or worsens concentration risk. In XRPL-style publication today, those calls are implicit. Post Fiat makes them explicit on a published record.

The comparison classes must be concrete. A deterministic baseline would rank the same frozen snapshot using only published rules over agreement history, uptime, version freshness, identity continuity, and concentration caps. A human baseline would ask a small review committee to rank that same snapshot under the same evidence record. If model-assisted scoring cannot at least match those baselines on cutoff stability, contestability, and operational clarity, then the model layer has not earned authority. If a deterministic rules engine later proves equally effective on the same evidence packages, the deterministic path should be preferred.

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

### 6.3 Why deterministic inference works

Thinking Machines Lab identified batch-size variance as a major source of nondeterministic inference and described batch-invariant kernels as a practical fix.[9] SGLang implements that fix in production-serving form: deterministic inference mode uses batch-invariant operators and supported attention backends so the same prompt is not pushed through a different floating-point reduction plan merely because other requests were batched beside it.[10][11]

Tensor parallelism across multiple GPUs introduces a separate nondeterminism source because cross-GPU reductions do not guarantee a fixed summation order. Post Fiat therefore requires single-GPU inference (TP=1). The active scoring profile uses Qwen/Qwen3.6-27B-FP8 on a single H100, avoiding tensor-parallel reduction variance while keeping enough memory headroom for the full scoring prompt.

Numerical precision remains a real divergence source. Yuan et al. show that limited precision affects reproducibility, particularly for reasoning-style models, and propose mitigations such as LayerCast.[12] This is why the execution manifest is a first-class artifact — a weight hash alone is not enough. Reproducibility depends on the whole stack.

Determinism makes execution replayable, not correct. If the snapshot, prompt, or model policy is wrong, deterministic inference will reproduce the same wrong answer. Governance still decides whether the scoring policy and input record deserve authority.

### 6.4 Empirical validation on XRPL UNL and PFT Ledger

Post Fiat replicated the earlier XRPL UNL validator credibility benchmark using the saved 29-validator XRPL UNL cohort and the same domain-level scoring prompt. Appendix A.2 gives the full table; in short, 2,900 calls produced one unique score-map hash with zero score variance and zero raw-output variance under the pinned Modal/SGLang deterministic profile.[18][19]

Appendix A.3 reports the 42-validator PFT Ledger replay. Five runs under the same Qwen3.6/SGLang profile produced complete JSON-valid result sets, one score-map hash, zero validator score spread, and a 35/35 top-35 intersection.[16][17]

These results exceed the rank-stability target under a fully pinned execution environment: model weights, quantization, inference engine, container image, GPU class, tensor-parallel setting, memory profile, prompt, decoding parameters, and determinism flags. They show exact same-stack replayability, not cross-hardware reproducibility or policy correctness.

---

## 7. Execution Manifest and Hashing Discipline

### 7.1 Full manifest pinning

Each round publishes a full execution manifest. The active deterministic scoring manifest:

| Field | Value |
|---|---|
| Model | Qwen/Qwen3.6-27B-FP8 |
| Quantization | FP8 checkpoint, auto-detected by SGLang |
| GPU | NVIDIA H100, single GPU (TP=1) |
| Inference engine | SGLang nightly `dev-cu13` profile |
| Container image | `lmsysorg/sglang:nightly-dev-cu13-20260430-e60c60ef@sha256:5d9ec71597ade6b8237d61ae6f01b976cb3d5ad2c1e3cf4e0acaf27a9ff49a65` |
| Reasoning parser | `qwen3` |
| Static memory fraction | `0.75` |
| Chunked prefill size | `4096` |
| Max running requests | `1` |
| FlashInfer workspace | `2147483648` bytes |
| Sampling | Deterministic greedy decoding |
| Temperature | 0 (greedy decoding) |
| Determinism flags | `--enable-deterministic-inference` |
| Production output mode | `chat_template_kwargs.enable_thinking=false` |

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

This phase is live on the public testnet. The canonical signed testnet validator list is published at `https://postfiat.org/testnet_vl.json`; the decoded signed blob is sequence `5`, contains `20` validators, and is effective from `2026-05-26T17:50:23Z`. The public scoring configuration reports a `168` hour cadence, score cutoff `40`, max list size `20`, and minimum score gap `5`.

The public rounds API shows repeated operation rather than a one-off demo. Rounds 4, 5, 6, and 7 completed successfully, producing validator-list sequences 2, 3, 4, and 5. Each round has a final audit bundle CID, a GitHub Pages publication commit, and a PFTL memo transaction hash.

That is stronger than the status quo, where recommended list construction is not publicly explained. It proves live Phase 1 publication and audit anchoring; validator-side sidecars, commit-reveal, independent shadow scoring, convergence monitoring, validator-enforced scoring verification, and authority transfer remain later-phase gates.

### 9.2 Phase 2: Verifying independent execution

Phase 2 must distinguish independent execution from copying the foundation's published output.

Post Fiat addresses this through two mechanisms:

- **Commit-reveal protocol**: Validators commit to hashed outputs before the foundation publishes canonical scores (Section 8.4). This prevents after-the-fact copying.
- **Convergence measurement**: The network measures pairwise rank agreement, top-k overlap, and list-level convergence across validator submissions. Persistent divergence from a specific validator — or suspiciously perfect agreement without commit-reveal compliance — is detectable.

A harder problem is hardware heterogeneity. The active profile is pinned to H100, but not every validator will have identical hardware. Different GPU architectures may produce slightly different floating-point results even under deterministic inference mode. Phase 2 measures the extent of this divergence empirically and determines whether rank stability holds across hardware configurations.

### 9.3 Future verification paths

Several maturing verification technologies could strengthen Phase 2 assurance as they become production-ready for large models.

| Approach | What it proves | Status |
|---|---|---|
| TEE attestation (H100/Blackwell) | Specific code ran on genuine, untampered hardware | Production-ready, <7% overhead |
| Optimistic ML (opML) | Inference result is correct unless successfully challenged on-chain | On-chain today for 7B+ models |
| Zero-knowledge ML (zkLLM, zkPyTorch) | Cryptographic proof that a specific model produced a specific output | Feasible for 13B today, 70B+ maturing |
| TLSNotary | A specific API call returned a specific response | Available |

### 9.4 Evidence required before authority transfer

Phase 3 should not be justified by a single same-stack benchmark. Before authority transfer, the project should be able to show all of the following:

- repeated replay on many more rounds and snapshots than the current benchmark package;
- comparison against explicit deterministic and human-review baselines on the same frozen snapshots, with reported top-k overlap, cutoff stability, and disagreement cases;
- adversarial testing around data curation, identity inflation, and social-gaming attempts;
- independent reruns by external operators, not only foundation-controlled infrastructure;
- measured behavior across hardware or runtime variation sufficient to show that rank stability survives realistic decentralized operation.

Until that evidence exists, the current work is early benchmark success plus a credible audit architecture, not production-readiness proof.

---

## 10. Phased Deployment

### 10.1 Phase 1: Foundation publication with full audit trail

The foundation operates the scoring pipeline: collecting evidence from VHS and network crawl endpoints, normalizing it into a canonical snapshot, scoring validators via a self-hosted open-weight model on serverless GPU infrastructure, applying the deterministic selector, signing the validator list, and publishing the full round bundle to IPFS with an on-chain CID anchor.

The phase remains operationally centralized and auditable.

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

Validator-list scoring is periodic, structured, and batchable. The current testnet scoring service uses `prompts/scoring_v5.txt` with `Qwen/Qwen3.6-27B-FP8` through Modal/SGLang H100 inference. The earlier Qwen3.6 `scoring_v2` replay processed roughly 7,654 prompt tokens and 4,774 completion tokens in about 88 seconds on the pinned H100 profile; that remains benchmark context, not the current prompt contract. This is not a high-frequency workload — the public configuration currently targets a 168-hour cadence.

Post Fiat's validation runs on serverless GPU infrastructure, so costs accrue during scoring windows rather than continuously. The 2,900-call XRPL UNL determinism replay completed in 217.1 seconds once the endpoint was warm, consumed 468,600 total tokens, and required no closed-model API calls.[19] These costs decline as inference hardware improves.

### 11.2 The cost trend favors decentralization

Stanford's 2025 AI Index reports that GPT-3.5-equivalent inference costs fell by more than 280× between late 2022 and late 2024, with the gap between closed-weight and open-weight models narrowing sharply.[14] Epoch AI reports rapid fixed-performance inference price declines across task categories.[15]

Validator-list scoring has a structural economic advantage over most AI workloads: it runs a few times per month, not continuously. This makes serverless GPU infrastructure — where costs accrue only during active inference and scale to zero between rounds — a natural fit. For Phase 2 shadow verification, falling inference costs mean validators will increasingly be able to rerun scoring locally or on rented single-GPU infrastructure without maintaining a permanent datacenter-grade inference cluster.

### 11.3 Validator incentives

Post Fiat follows XRPL's principle that no direct validator reward is the best validator reward. Validators run because they use the network, not because they are paid to validate.

The foundation allocates resources specifically for Phase 2 shadow verification — paying for the work of proving that the scoring process is reproducible, not for general node operation. Credibility signals in model-assisted scoring should reflect genuine institutional commitment to the network, not a subsidy relationship with the foundation.

### 11.4 Why a distinct network

Validator-list publication is part of the base-layer trust product. Opaque publisher discretion leaves sophisticated users with a hidden governance dependency; published evidence, replayable scoring, signed artifacts, and validator shadow verification create a different trust surface.

That is difficult to retrofit as a neutral add-on. An XRPL-side tool can recommend a better list, but the tool remains advisory unless the network's own operators, artifacts, and fallback rules treat it as the default publication process. Post Fiat can make the evidence bundle, scorer manifest, selected list, and publication record native to its operating model from the start.

The token thesis depends on that governance surface affecting adoption. PFT is not justified by model scoring in isolation; it depends on settlement inside a network whose validator-selection process is materially more legible, more contestable, and easier for institutions, validators, and builders to audit than the status quo.

---

## 12. Conclusion

Validator-list publication is a real governance surface. It determines overlap, concentration, and the security envelope in which consensus operates. Widely used recommended lists remain only partially legible.

Post Fiat replaces opaque editorial selection with a public, replayable, model-assisted pipeline: collect evidence, normalize it canonically, pin the execution environment, score candidates under a published policy, select the set deterministically, publish the artifacts, and shift authority only after convergence is demonstrated.

Current evidence supports that narrow claim. Appendix A reports exact replay under the pinned Qwen3.6/SGLang profile on both the saved XRPL UNL credibility cohort and the 42-validator PFT Ledger scoring task.[16][17][18][19] Section 9.1 documents live Phase 1 testnet publication through sequence 5, including completed public rounds 4 through 7 with audit bundle CIDs, publication commits, and PFTL memo transaction hashes. Together, this shows same-stack replayability and a functioning audit-publication loop, not production authority transfer.

The next gates are comparative baselines, adversarial testing, external reruns, and cross-hardware evidence. Until those pass, Post Fiat has an auditable publication architecture, not a solved governance problem.

---

## Appendix A — Determinism Benchmarks

### A.1 Active model and deployment

The active Dynamic UNL model is Qwen/Qwen3.6-27B-FP8 served on Modal through SGLang deterministic inference.[16][17] This replaced the earlier Qwen3-Next-80B-A3B H200 baseline as the primary scoring profile. The current profile uses a single H100, tensor parallelism 1, the Qwen3.6 FP8 checkpoint, SGLang's `--enable-deterministic-inference` flag, one running request, chunked prefill, a pinned container image, and non-thinking final-answer mode.

The Qwen3-Next 80B result remains useful historical evidence: it showed that exact replay was possible under a pinned H200/SGLang setup. It is no longer the live manifest or the primary benchmark cited by this paper.

### A.2 XRPL UNL credibility replay

The current replay uses the saved 29-validator XRPL UNL cohort from the earlier benchmark and the same scoring prompt:

> score this validator's credibility on a scale from 0-100 where credibility is defined as useful institutional proof of a blockchain's legitimacy.

The replay was run against Qwen/Qwen3.6-27B-FP8 on the pinned Modal/SGLang endpoint.[18][19]

| Metric | Result |
|---|---:|
| Validator domains | 29 |
| Batches | 2 |
| Repeats per batch | 50 |
| Total calls | 2,900 |
| Successful calls | 2,900 |
| Errors | 0 |
| Parse errors | 0 |
| Complete score maps | 100 |
| Unique score-map hashes | 1 |
| Domains with score variance | 0 |
| Domains with raw-output variance | 0 |
| Mean request latency | 2,388.8 ms |
| P95 request latency | 10,444.69 ms |
| Total tokens | 468,600 |
| Completion tokens | 22,300 |
| Reasoning tokens | 0 |

The single score-map hash for all 100 complete rounds was:

```text
9f7f95a7be238e2b6bb1cc081986f8b5dffc07b9397578d723c6f6d7c77c81c8
```

Representative scores from the replay:

| Validator domain | Score |
|---|---:|
| ripple.com | 100 |
| arrington-xrp-capital.blockdaemon.com | 95 |
| validator.gatehub.net | 95 |
| xrp.vet | 95 |
| bithomp.com | 85 |
| ripple.ittc.ku.edu | 85 |
| v2.xrpl-commons.org | 85 |
| validator.xrpl-labs.com | 65 |
| xrpkuwait.com | 35 |
| cabbit.tech | 0 |

This benchmark is deliberately simple: it tests whether a qualitative validator-credibility prompt can be replayed exactly across repeated calls. Under the pinned SGLang deterministic profile, it can.

### A.3 PFT Ledger scoring replay

The PFT Ledger scoring task is larger than the domain-only XRPL credibility prompt. The replay below used the earlier `scoring_v2` contract, including dimension fields and a network summary.[16][17] The current live scoring service has moved to `prompts/scoring_v5.txt`; the replay remains evidence for deterministic execution under the pinned Qwen3.6/SGLang profile, not a claim that `scoring_v2` is the active production prompt.

The Qwen3.6 Modal/SGLang capture showed:

- 5/5 JSON-valid runs.
- 5/5 complete 42-validator result sets.
- 5/5 runs with `network_summary` present.
- 0 invalid dimension fields.
- 1 unique extracted-answer hash.
- 1 unique score-map hash.
- 1 unique top-35 hash.
- 0 validators with score spread across runs.
- 35/35 top-35 intersection across all runs.
- Mean elapsed time of 87.99 seconds.
- 7,654 prompt tokens, 4,774 completion tokens, and 12,428 total tokens per run.

The same deployment was also tested in thinking mode. Thinking mode remained deterministic but was rejected as the production default because it did not change the top-35 set and made the run roughly 4x slower with substantially more completion tokens.[16]

### A.4 What the benchmarks prove

The benchmarks prove execution replayability under the pinned stack. They do not prove that the model's scoring policy is correct, that the prompt is optimal, or that all future hardware profiles will match bit-for-bit. They show that, once the input snapshot, prompt, model, and serving stack are fixed, SGLang deterministic inference can remove the random run-to-run variance that would otherwise undermine validator-list governance.

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

[10] SGLang Docs. **Deterministic Inference**. https://docs.sglang.io/docs/advanced_features/deterministic_inference

[11] LMSYS / SGLang Team. **Towards Deterministic Inference in SGLang and Reproducible RL Training**. 2025. https://www.lmsys.org/blog/2025-09-22-sglang-deterministic/

[12] Yuan, Jiayi, et al. **Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference**. arXiv:2506.09501, 2025.

[13] XRPL Docs. **xrp-ledger.toml File**. https://xrpl.org/docs/references/xrp-ledger-toml

[14] Stanford HAI. **AI Index Report 2025**. https://hai.stanford.edu/ai-index/2025-ai-index-report

[15] Epoch AI. **LLM inference price trends** (2025). https://epoch.ai/data-insights/llm-inference-price-trends

[16] `dynamic-unl-scoring` Qwen3.6 deployment research, inspected May 5, 2026. Review of `phase0/docs/Qwen36ModalFeasibility.md`, `phase0/docs/DeployQwen36_27B.md`, `phase0/docs/ModelQualityComparison_Qwen36_27B.md`, and `phase0/docs/Qwen36ThinkingModeComparison.md`.

[17] `dynamic-unl-scoring` implementation artifacts, inspected May 5, 2026. Review of `infra/deploy_qwen36_endpoint.py`, `infra/deploy_endpoint.py`, and `phase0/results/modal/qwen36-27b-fp8/2026-04-30_qwen36-27b-fp8_scoring-v2/run_1.json` through `run_5.json`.

[18] `postfiatorg.github.io` XRPL UNL deterministic replay harness, inspected May 5, 2026. Review of `scripts/xrpl_validator_sglang_determinism.py`.

[19] `postfiatorg.github.io` XRPL UNL deterministic replay artifacts, generated May 5, 2026. Review of `static/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z.json`, `static/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z-summary.json`, and companion domain CSV.

---
