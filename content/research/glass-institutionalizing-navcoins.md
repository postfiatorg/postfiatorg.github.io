---
title: "Glass: Institutionalizing NAVCoins"
date: 2026-08-15T00:00:00Z
url: "/research/glass-institutionalizing-navcoins/"
type: "blog"
breadcrumb_label: "Research"
breadcrumb_url: "/research/"
summary: "A research proposal for extending NAVCoin's verified reserve machinery into institutional collateral passports: reusable reserve rights, complete liability cells, policy-specific solvency checks, and replayable verified inference without pretending that computation proves off-chain truth."
description: "Glass is a proposed institutional layer for NAVCoins and other digital claims, turning verified reserve evidence into policy-specific, portable collateral passports on PFTL."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - Glass
  - NAVCoin
  - Verified Inference
  - Collateral
  - Solvency
  - PFTL
draft: false
---

> **Status: research proposal with an off-chain experimental mock.** Glass is
> not a separate deployed protocol, a new chain, or a claim that Post Fiat can
> cryptographically prove an undisclosed off-chain fact. This note defines a
> possible institutional extension of the existing NAVCoin architecture. The
> live mock described below exercises the normalization and deterministic-policy
> boundary, but has no consensus, custody, lending, issuance, or liquidation
> authority.

## The proposal in one paragraph

NAVCoin answers a bounded question: **what is one verified reserve portfolio
worth, how many claims exist against it, and may those claims be issued or
redeemed at the finalized NAV?** Glass generalizes the same machinery for an
institution deciding whether it may accept a digital claim. A custodian,
on-chain vault, fund administrator, or other authorized source commits evidence
about assets, control, liabilities, and encumbrances. Verified inference maps
that heterogeneous evidence into a canonical claim graph under a pinned model,
policy, runtime, and output schema. Deterministic PFTL rules then apply a relying
party's explicit haircuts, freshness limits, concentration limits, legal-control
requirements, and coverage threshold. The output is a time-bounded
`GlassPassport` that a lender, exchange, wallet, bridge, or issuance contract can
consume. A passport can permit new risk while current; when evidence becomes
stale or coverage fails, it disables new issuance or borrowing without blocking
redemption or recapitalization.

The distinction is product versus institutional control plane:

- **NAVCoin** is a pro-rata claim on one verified portfolio with primary
  subscription and redemption at NAV.
- **Glass** is a proposed policy engine and portable eligibility receipt for
  NAVCoins and, eventually, other reserve-backed liabilities.

Glass should begin as a module on PFTL, using NAVCoin as its first live asset
class. Nothing in this proposal requires a new L1 or a separate token.

<figure class="research-diagram">
  <img src="/research/glass/glass-product-stack.svg" alt="Architecture diagram showing PFTL evidence, verified inference, and deterministic policy enforcement as the shared base. NAVCoin sits above it as a verified portfolio token with mint and redemption at NAV. Glass sits alongside it as institutional reserve rights, liability cells, solvency specifications, and portable passports consumed by lenders, exchanges, wallets, bridges, and treasuries.">
  <figcaption>Glass does not replace NAVCoin. It exposes NAVCoin's verification substrate as an institutional eligibility layer while NAVCoin remains the first concrete financial product.</figcaption>
</figure>

## What NAVCoin already establishes

The [NAVCoin proposal](/blog/navcoin-proposal/) already makes reserve evidence a
protocol input instead of a PDF. Its proof profiles bind sources, policies,
freshness, and verification methods. Finalized packets constrain supply; stale
or invalid evidence fails closed. The current canonical collateralization model
adds the essential accounting identity:

```text
counted reserves in  -> NAVCoin supply out
NAVCoin supply in    -> counted reserves out
```

One portfolio has one verified net asset value and one global economic supply,
even when native units move to an external venue as wrapped units. Primary
issuance and redemption change both reserves and supply. Secondary trades and
bridges change neither.

That machinery already answers four questions for a single NAVCoin:

1. Which reserve and valuation policy is active?
2. What eligible net assets were verified under it?
3. What is the valid global supply?
4. May a primary issuance or redemption execute now?

Glass does not deserve a separate category merely for repeating those checks.
Its incremental purpose is to let an external capital allocator ask a different
question:

> Under **my** policy, may I rely on this particular claim, at this particular
> haircut and exposure limit, given the evidence and authority currently on
> record?

## What Glass adds

Glass adds four reusable protocol objects above the existing evidence lifecycle.

### 1. `ReserveRight`

A `ReserveRight` is a unique, expiring record of a claimed right over a defined
quantity of an asset. It binds:

- the asset, quantity, owner, and controlling party;
- the source of the control assertion;
- the custody or control agreement, if one exists;
- jurisdiction, seniority, eligible uses, and disclosed encumbrances;
- one current `LiabilityCell` assignment; and
- its assurance class and expiry.

For assets directly controlled by an on-chain vault, PFTL can enforce exclusive
assignment and release. For off-chain assets, the ledger can enforce only the
commitments made inside Glass. It cannot prevent a custodian or owner from
creating a secret external pledge.

### 2. `LiabilityCell`

A `LiabilityCell` defines the complete *committed perimeter* of claims relying on
a reserve pool. For a NAVCoin, the liability is its global authorized supply.
For another product, it could be a bridge's wrapped supply, an exchange's
committed customer balances, or a tokenized fund's units and senior claims.

The word *committed* matters. Glass can prove that a submitted liability root was
processed consistently and that an included customer appears in it. Glass
cannot prove that an issuer disclosed every liability it has elsewhere.

### 3. `SolvencySpec`

A `SolvencySpec` is the relying party's versioned acceptance policy. It defines:

- accepted assets, sources, jurisdictions, and assurance classes;
- prices, haircuts, concentration and liquidity limits;
- maturity and liability-priority treatment;
- evidence freshness and challenge windows;
- minimum coverage and stress scenarios; and
- the exact failure behavior consumers must enforce.

There is deliberately no universal Glass opinion of "safe." A conservative
lender and a retail wallet can evaluate the same committed facts under different
specifications and receive different answers.

### 4. `GlassPassport`

A `GlassPassport` is a portable, expiring receipt stating that one
`LiabilityCell` passed one `SolvencySpec` against one finalized claim graph. It
identifies the state roots, policy version, coverage result, exceptions,
assurance composition, issue time, expiry, and permitted actions.

Consumers must verify the passport's state and expiry on PFTL rather than copy a
green badge forever. A status change is part of the protocol output.

## Where verified inference fits

Solvency arithmetic does not require artificial intelligence. Addition,
haircuts, concentration checks, signature verification, expiry, and state
transitions should remain deterministic code.

Verified inference belongs at the semantic boundary where institutional evidence
is difficult to normalize:

- custody statements use incompatible names and identifiers;
- legal agreements express control, priority, and permitted use in prose;
- fund reports mix assets, receivables, fees, and contingent liabilities;
- related entities appear under aliases and changing ownership structures;
- maturity, liquidity, and encumbrance terms require classification; and
- two records may describe the same underlying asset or obligation.

The model's job is to propose a canonical interpretation with provenance. The
protocol's job is to determine whether that interpretation satisfies an explicit
policy. A receipt proves **which computation ran over which committed inputs**;
it does not prove that a source told the truth.

<figure class="research-diagram">
  <img src="/research/glass/glass-inference-pipeline.svg" alt="Verified inference pipeline diagram. Signed source evidence is content-addressed and committed. A pinned confidential worker normalizes it into structured claims and emits an attested inference receipt. Deterministic PFTL checks validate signatures, schemas, exclusivity, arithmetic, freshness, haircuts, and coverage. The resulting Glass Passport is consumed by institutional applications. Challenges can target evidence, inference, or deterministic policy execution.">
  <figcaption>The trust boundary is explicit: inference normalizes evidence; deterministic rules make the eligibility decision; neither step upgrades reported evidence into guaranteed off-chain truth.</figcaption>
</figure>

### The verified-inference contract

A conforming worker receives only content-addressed inputs and a finalized
`InferenceProfile`. Conceptually:

```text
Normalize(
  evidence_root,
  inference_profile_id,
  prior_claim_graph_root
) -> InferenceReceipt
```

The `InferenceProfile` pins:

```yaml
inference_profile:
  profile_id: H(canonical_profile_bytes)
  runtime_digest: bytes32
  model_digest: bytes32
  tokenizer_digest: bytes32
  system_prompt_digest: bytes32
  extraction_template_digest: bytes32
  output_schema_digest: bytes32
  parser_digest: bytes32
  decoding:
    temperature: 0
    top_p: 1
    max_output_tokens: uint32
  allowed_evidence_schemas: [bytes32]
  attestation_policy_id: bytes32
  valid_from_height: uint64
  valid_until_height: uint64
```

An `InferenceReceipt` contains:

```yaml
inference_receipt:
  receipt_id: H(canonical_receipt_bytes)
  profile_id: bytes32
  evidence_root: bytes32
  prior_claim_graph_root: bytes32 | null
  proposed_claim_graph_root: bytes32
  exception_root: bytes32
  source_citations_root: bytes32
  execution_measurement: bytes32
  attestation: bytes
  started_at: uint64
  completed_at: uint64
```

Every extracted claim must point back to one or more locations in committed
evidence. Unsupported claims fail schema admission. Material ambiguity is emitted
as an exception; it is not silently resolved by model confidence.

The receipt is replayable when the inference profile promises reproducible
execution. When hardware or model kernels cannot guarantee byte-identical replay,
the profile must say so and require independent workers, bounded comparison, or
human challenge rather than implying determinism that does not exist.

## Live mock: one synthetic GPU-credit passport

On August 15, 2026, we implemented the smallest end-to-end Glass experiment in
the `postfiatl1v2` research tree and ran its inference leg on an existing Vast.ai
RTX 5090 rental. This is a **synthetic financing packet**. The rented GPU was
execution hardware only; it was not represented as collateral. No real borrower,
custodian, insurer, lien, appraisal, loan, or asset is asserted by the mock.

The packet describes eight fictional NVIDIA B200 GPUs. Five synthetic source
records state the asset schedule, control and lien terms, insurance status,
liquidation appraisal, and liability ledger. The mock policy applies a 20%
haircut and requires 1.100000× coverage, controlled custody, a first-priority
lien, active insurance, accepted jurisdiction, accepted model, and current
evidence.

| Deterministic input or result | Exact mock value |
| --- | ---: |
| GPU quantity | 8 |
| Liquidation value per GPU | 30,000.000000 USDC |
| Gross liquidation value | 240,000.000000 USDC |
| Policy haircut | 20.000000% |
| Eligible collateral value | 192,000.000000 USDC |
| Covered liability | 160,000.000000 USDC |
| Coverage | 1.200000× |
| Minimum coverage | 1.100000× |
| Experimental passport status | `ACTIVE` |

The model did **not** calculate any row after the unit value and liability. It
received a bounded 927-token packet, returned the fourteen requested fields, and
attached one exact source substring to each field. Static code then rejected
unknown fields, checked every citation against the committed source bytes, and
performed the haircut and coverage arithmetic with bounded integers. The model
could not emit a passport status or permitted action. Those are derived by the
deterministic evaluator.

The live inference profile was:

```text
provider: Vast.ai
hardware: NVIDIA GeForce RTX 5090
model: Qwen/Qwen3-14B-FP8
revision: 9a283b4a5efbc09ce247e0ae5b02b744739e525a
model snapshot: 11 files, 16,342,197,548 bytes
model aggregate: sha3-384:baad5c7cacff86db3a3e19861169863f44a619d5b9850430a0c446bc7a4690fd533d282fdcc977c2872e9089899d7623
runtime: SGLang 0.5.5.post3, Torch 2.8.0+cu128, Transformers 4.57.1
decode: temperature 0, top_p 1, seed 0, one running request
attention: Triton; CUDA graphs and JIT DeepGEMM disabled
output control: deterministic decode followed by strict static validation
```

Two independent requests on the same pinned runtime produced byte-identical raw
generated text. Both normalized to the same claim graph. The replayed output was:

```text
inference receipt root:
sha3-384:e1458cc92780f4491cdd06187649ac05342ff2bb70d18ee4383c8ed6875ae3da6733e26f42b6fc35e1726ba842cb89e0

GlassPassport root:
sha3-384:74a56b7ab12084e40e7a17b8a40684edac2bcbc4ae5fb2f8fa9d24034be4a8bd81ea135ba758e5c74a0808573ec566db

sealed file manifest:
sha3-384:9450ae87919b2eee9550c0f0b3012c02d5e507b15b0502b3dec12f412cafaec5291ff7d5cd4f50cb9e4c9299a50942f7
```

The evidence bundle lives at
`docs/evidence/glass-live-mock-v1/` in `postfiatl1v2`. It includes the source
packet, exact request, output schema, environment and model commitment, both raw
responses, both raw generated texts, the narrowly parsed JSON, SGLang startup
log, inference receipt, derived records, passport, and sealed file manifest. The
offline verifier performs no network calls.

The implementation also exercises failure cases for expired evidence, missing
insurance, sub-threshold coverage, unresolved extraction exceptions, fabricated
citations, citation/source mismatch, injected decision fields, floating-point
input, arithmetic overflow, altered manifests, non-identical repeats, fixture
captures presented as live runs, and attempts to enable consensus authority.
When evidence is stale or deficient, new-risk simulation is removed while
repayment, added collateral, and challenge simulation remain available.

### What the mock revealed

The mock is useful partly because the runtime did not behave like an abstract
diagram. Qwen3.6-27B-FP8 required a newer Qwen architecture and CUDA 13 SGLang
stack than the existing CUDA 12.8 rental could safely run, so the experiment
pinned Qwen3-14B-FP8 instead. The 5090's SM120 kernels also required CUDA graphs
and JIT DeepGEMM to be disabled. This SGLang build hung when the prompt crossed
its 1,024-token chunk boundary, so the evidence packet was made concise without
removing any required claim. Its guided-decoding backends also compiled the
original repeated citation grammar pathologically slowly; the final run used
deterministic generation followed by the same fail-closed executable schema and
exact-citation checks.

Those are prototype constraints, not properties to conceal. The experiment has
no TEE attestation, no proof that the synthetic source statements are true, no
multi-provider replay, no legal-control analysis, and no PFTL state transition.
It demonstrates that the proposed separation can execute: a model normalizes
cited evidence, deterministic code makes the capital decision, and every output
is replayable. It does not yet demonstrate production verified inference or a
production Glass market.

## A minimal Glass protocol specification

The following is the smallest useful protocol surface. Names are provisional;
the separation of responsibilities is not.

### Canonical records

```yaml
reserve_right:
  right_id: bytes32
  asset_id: bytes32
  quantity_atoms: uint128
  owner_entity_id: bytes32
  controller_entity_id: bytes32
  source_authority_id: bytes32
  assurance_class: DIRECT | CONTROLLED | ATTESTED
  jurisdiction_code: string
  control_document_root: bytes32 | null
  priority_rank: uint32 | null
  encumbrance_root: bytes32
  eligible_use_root: bytes32
  assigned_liability_cell_id: bytes32 | null
  observed_at: uint64
  expires_at: uint64
  status: PROPOSED | ACTIVE | CHALLENGED | RELEASED | EXPIRED | REVOKED

liability_cell:
  cell_id: bytes32
  issuer_entity_id: bytes32
  liability_asset_id: bytes32
  quantity_atoms: uint128
  liability_root: bytes32
  seniority_root: bytes32
  supply_perimeter_root: bytes32
  observed_at: uint64
  expires_at: uint64
  status: CURRENT | STALE | DISPUTED | DEFICIENT | CLOSED

solvency_spec:
  spec_id: bytes32
  policy_owner_id: bytes32
  accepted_asset_policy_root: bytes32
  accepted_source_policy_root: bytes32
  accepted_assurance_classes: [DIRECT, CONTROLLED]
  price_policy_id: bytes32
  haircut_policy_root: bytes32
  concentration_policy_root: bytes32
  liquidity_policy_root: bytes32
  liability_priority_policy_root: bytes32
  min_coverage_ratio_ppm: uint64
  max_evidence_age_seconds: uint64
  challenge_window_blocks: uint64
  failure_policy: bytes32
  valid_from_height: uint64
  valid_until_height: uint64

glass_passport:
  passport_id: bytes32
  liability_cell_id: bytes32
  solvency_spec_id: bytes32
  claim_graph_root: bytes32
  inference_receipt_root: bytes32
  eligible_collateral_value_atoms: uint128
  covered_liability_value_atoms: uint128
  coverage_ratio_ppm: uint64
  assurance_mix_root: bytes32
  exception_root: bytes32
  permitted_action_root: bytes32
  issued_at_height: uint64
  expires_at_height: uint64
  status: PROPOSED | ACTIVE | CHALLENGED | STALE | DEFICIENT | REVOKED
```

All quantities use deterministic fixed-point integer arithmetic. Every policy and
record is content-addressed under a protocol-selected canonical encoding. No
floating-point value is consensus-critical.

### Deterministic evaluation

For each active reserve right \(i\), let:

- \(q_i\) be eligible quantity;
- \(p_i\) be the price admitted by the price policy;
- \(h_i\) be the applicable haircut in parts per million; and
- \(c_i\) be the amount remaining after concentration and liquidity limits.

Then:

\[
E = \sum_i \min\left(c_i, q_i p_i \frac{1{,}000{,}000-h_i}{1{,}000{,}000}\right)
\]

For liability classes \(j\), with quantity \(l_j\), admitted value \(v_j\), and
priority or stress multiplier \(s_j\):

\[
L = \sum_j l_j v_j s_j
\]

A passport can become `ACTIVE` only if all of the following are true:

```text
1. Every counted ReserveRight is ACTIVE and unexpired.
2. Every source and assurance class is accepted by the SolvencySpec.
3. No right is assigned to another active LiabilityCell in Glass state.
4. Evidence and inference receipts satisfy freshness and attestation policy.
5. Concentration, liquidity, maturity, and jurisdiction rules pass.
6. E * 1,000,000 >= L * min_coverage_ratio_ppm.
7. The challenge window closes without an upheld challenge.
8. The passport commits the exact claim, inference, price, and policy roots.
```

For a NAVCoin, the liability perimeter is the valid global NAVCoin supply and the
reserve policy remains canonical. A third-party Glass specification may apply a
more conservative haircut or exposure cap, but it cannot alter NAVCoin's own NAV
or accounting state.

## Assurance classes and honest claims

Glass must state what authority actually exists.

| Class | Evidence of control | What PFTL can honestly enforce |
| --- | --- | --- |
| **Direct** | Asset is held by a protocol-controlled on-chain vault | Balance, assignment, movement, release, and liquidation according to code |
| **Controlled** | Authorized custodian or collateral agent signs a recognized control or segregation commitment | Identity, signature, document scope, expiry, claimed priority, and conflicting assignments made inside Glass |
| **Attested** | Authorized source reports an asset but grants no control right | Provenance, freshness, committed content, policy execution, and contradictions visible in submitted evidence |

A `SolvencySpec` must select accepted classes and apply class-specific limits. The
protocol must never silently present an attested balance as legally controlled
collateral.

## State transitions and failure semantics

A healthy system does not reduce every problem to a global pause. It changes only
the actions that no longer have sufficient evidence.

<figure class="research-diagram">
  <img src="/research/glass/glass-state-machine.svg" alt="Glass state and collateral graph diagram. A reserve right can be assigned to only one liability cell in Glass state. Finalized evidence and a passing solvency specification activate a passport. Stale evidence, deficient coverage, an upheld challenge, or revocation moves the passport out of active status. New issuance, borrowing, and added exposure stop, while redemption, repayment, collateral addition, and challenge remain available.">
  <figcaption>Failure is asymmetric: Glass closes the path that creates new risk while preserving the paths that reduce risk or let holders exit.</figcaption>
</figure>

The baseline action matrix is:

| Passport state | New issuance | New borrowing or collateral use | Redemption or repayment | Add collateral | Challenge |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ACTIVE` | Allowed by consumer policy | Allowed by consumer policy | Allowed | Allowed | Allowed |
| `CHALLENGED` | Disabled | Disabled | Allowed | Allowed | Allowed |
| `STALE` | Disabled | Disabled | Allowed | Allowed | Allowed |
| `DEFICIENT` | Disabled | Disabled | Allowed | Allowed | Allowed |
| `REVOKED` | Disabled | Disabled | Allowed only under product resolution rules | Allowed | Allowed |

Glass cannot force an independent application to behave correctly merely by
publishing a status. An integration is Glass-enforced only when its contract or
governed policy actually consumes current PFTL state.

## Privacy and disclosure

An institution may need to prove coverage without publishing its full position
book. The protocol should separate public state from encrypted evidence:

- public: entity identifiers or pseudonymous regulated identifiers, policy
  roots, source classes, aggregate eligible value, liability value, coverage,
  status, expiry, exceptions, and challenge history;
- selectively disclosed: instrument-level positions, agreements, customer
  inclusion paths, and source citations; and
- confidential: raw account statements, customer balances, proprietary
  positions, and unredacted legal documents.

Confidential execution protects disclosure. It does not improve source honesty.
A relying party chooses whether a private proof and its assurance class are
sufficient for the risk it is taking.

## Who consumes a passport

Glass becomes economically meaningful only when a passport changes a real
capital-allocation decision:

- a lending market sets collateral eligibility, haircut, and exposure limits;
- an exchange decides whether it will list or hold an issuer's liability;
- a treasury router selects which wrapped or reserve-backed assets it may use;
- a wallet distinguishes current, stale, challenged, and deficient backing;
- a bridge contract prevents new wrapped issuance when source coverage fails;
- a NAVCoin issuer demonstrates institution-specific eligibility without
  changing its canonical NAV; or
- a custodian provides a reusable, signed control commitment rather than a new
  PDF for every bilateral integration.

The initial wedge should be NAVCoin itself. Post Fiat controls both ends of the
first integration: the asset generates verified reserve state, and a wallet or
venue consumes a passport derived from that state. The next test is not another
internal badge. It is a third party making a consequential eligibility or
exposure decision from the passport.

## Economics without invented token demand

Glass can charge in USDC for:

- passport issuance and renewal;
- active certified exposure;
- confidential evidence processing and inference;
- policy evaluation and passport consumption;
- enterprise monitoring, history, and service-level guarantees; and
- implementation of institution-specific adapters.

Source operators, confidential workers, challengers, and specialist reviewers
can receive payment for measurable service work. PFTL transaction fees continue
to use PFT under the network's normal fee policy.

No separate GLASS token is assumed here. Bonding can initially use PFT,
stablecoin-denominated performance bonds, legal recourse, or product-specific
first-loss capital depending on the fault being covered. A new token would be
justified only if production evidence showed that certified exposure requires a
distinct, objectively slashable capacity market that the existing security model
cannot provide.

## What Glass does not solve

The proposal fails if its language outruns its evidence. In particular:

- **No proof of undisclosed facts.** Glass cannot prove that an issuer revealed
  every liability or external pledge.
- **No alchemy from inference receipts.** A verified model execution can still
  normalize a false source statement perfectly.
- **No universal legal priority.** Priority over off-chain assets depends on the
  relevant agreement, jurisdiction, perfection, and insolvency process.
- **No automatic adoption.** A passport has value only when capital allocators
  consume it in binding eligibility decisions.
- **No substitute for redemption.** Solvency status cannot compensate for a
  product whose holders cannot enforce or execute their exit rights.
- **No universal risk opinion.** Different institutions can legitimately apply
  different haircuts and reject the same evidence.

These are not edge-case disclaimers. They define the boundary between a useful
verification protocol and a misleading one.

## Proposed implementation sequence

### Phase 0 — NAVCoin passport

Derive a read-only passport from one existing NAVCoin's finalized reserve packet,
global supply, NAV policy, bridge perimeter, and redemption status. Let the Post
Fiat wallet consume it. Demonstrate expiry and fail-closed behavior without
introducing any new custody authority.

### Phase 1 — Direct reserve rights

Add `ReserveRight`, `LiabilityCell`, and `SolvencySpec` records for assets already
under programmatic on-chain control. Prove exclusive in-protocol assignment,
deterministic policy evaluation, challenges, and state transitions. Integrate one
external relying contract that changes a real exposure limit.

### Phase 2 — Verified normalization

Introduce pinned `InferenceProfile`s and `InferenceReceipt`s for heterogeneous
signed documents. Benchmark extraction against deterministic parsers and human
review, measure disagreement and exception rates, and publish replay artifacts.
Model assistance earns authority only where it outperforms the simpler baseline
under an explicit error budget.

### Phase 3 — Controlled off-chain rights

Add verified organizational authority, custodian participation, jurisdiction-
specific control templates, encrypted evidence, and bounded source limits. Begin
with one legally reviewed asset and one capital allocator rather than claiming
universal collateral coverage.

### Phase 4 — Portable institutional market

Standardize adapters for lenders, exchanges, treasuries, wallets, and bridges.
Measure the only adoption metric that matters: financial exposure whose terms are
actually controlled by a current Glass passport.

## The thesis

NAVCoin turns a verified portfolio into a redeemable digital asset. Glass asks
whether the verification machinery can become reusable institutional
infrastructure without losing the honesty of the original accounting model.

The credible claim is not that blockchain discovers truth. It is narrower:

> Post Fiat can make the evidence, interpretation, policy, and resulting capital
> decision attributable, replayable, challengeable, time-bounded, and executable.

If that makes one institution accept a NAVCoin on better terms, Glass has begun
to institutionalize NAVCoins. If it later does the same for claims issued by
other systems, it has become a general collateral-passport protocol. Until then,
it remains a research program built on NAVCoin—not a separate universal network
declared into existence.
