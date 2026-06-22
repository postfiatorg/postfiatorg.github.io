---
title: "Private NAV Subscriptions and OTC Swaps: Shielded NAVCoin Settlement on Post Fiat"
date: 2026-06-18T00:00:00Z
summary: "A design for using Post Fiat to support private primary NAV subscriptions that add source-labeled USDC to NAVCoin reserves without walking a thin AMM book, plus private secondary OTC swaps for existing holders. The core claim is that TVL formation improves when issuance, reserve receipts, NAV policy, and shielded settlement are co-located; the hard boundaries are USDC provenance, mint escrow enforcement, credential governance, replayability, privacy budgets, and secondary liquidity."
aliases:
  - /blog/private-nav-otc-swaps/
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Privacy
  - OTC
  - Subscriptions
  - Primary Issuance
  - Shielded
  - DEX
  - Post Fiat
  - L1
---

*[Series I](/blog/postfiat-l1v2-private-xrpl-latency-benchmark/) covered certified finality. [Series II](/blog/postfiat-l1v2-fastpay-latency/) covered the owned-value settlement lane. This post describes an architecture for NAVCoin issuance and trading on Post Fiat: private primary subscriptions first, private secondary OTC swaps second.*

The important distinction is simple:

```text
primary subscription:
  subscriber USDC -> reserve vault
  newly released NAVCoin -> subscriber
  reserve TVL increases

secondary OTC swap:
  buyer USDC -> existing holder
  existing holder NAVCoin -> buyer
  reserve TVL does not increase
```

That distinction matters more than the privacy technology. A private secondary swap can be useful, but it does not form new TVL. A private primary subscription can.

## Status and trust boundaries

This is an architecture proposal, not a shipped issuance product.

Several pieces described below are proposed primitives that would need implementation, audits, governance, and production hardening before anyone should treat the system as live market infrastructure. The point of the article is to define the design target and its trust boundaries precisely enough that skeptical readers can reason about it.

| Component | Status in this article | Trust boundary |
|---|---:|---|
| PFTL consensus, finality, and NAV packet flow | Foundation assumed from earlier Post Fiat/NAVCoin work | Validator set, proof program correctness, packet completeness |
| Owned-value objects and shielded-note model | Protocol substrate / implementation-track primitive | Circuit soundness, wallet support, note/nullifier handling |
| `ReserveReceipt` | Proposed state machine | Source-domain proof quality, finality, haircuts, reserve packet inclusion |
| `MintEscrow` | Proposed state machine | Must be enforced by validators and transfer circuits, not by policy prose |
| Shielded primary subscription circuit | Proposed action type | ZK circuit correctness, reserve/supply root transitions |
| Verifiable sealed-bid batch book | Proposed, technically heavy | Threshold encryption, MPC, or large ZK sorting/selection assumptions |
| Credential nullifiers and compliance viewing keys | Proposed governance layer | Credential issuer honesty, revocation governance, key compromise/censorship |
| Replay transcript and verifier | Proposed audit layer | Verifies admitted inputs and formulas, not external asset quality or input completeness |
| PFTL USDC | Design requirement | Native USDC, CCTP USDC, bridged USDC, custodial USDC, and synthetic USDC are different assets for reserve-quality purposes |
| Shielded secondary OTC swaps | Proposed action type | Provides private settlement, not guaranteed liquidity or price discovery |

A few boundaries should be explicit up front:

1. **USDC provenance is not created by PFTL.** A PFTL balance labeled USDC is only reserve-quality to the extent its source-domain claim is reserve-quality. Native Circle-issued USDC, Circle CCTP-minted USDC, third-party bridged USDC, custodial USDC, and synthetic stablecoins need different treatment and possibly different haircuts.

2. **Private issuance conflicts with public auditability.** The system can hide individual subscribers, sizes, and fills from the public chain. It cannot hide every economic fact while also proving reserve intake, supply increase, clearing price, and backing invariants. Aggregate disclosures leak information.

3. **Small batches are weak privacy.** If one whale funds most of a batch, public aggregate USDC-in and NAVCoin-out can reveal most of the economics. A credible launch policy needs minimum participant, size, duration, and concentration thresholds.

4. **Replayability is not omniscience.** A replay verifier can check that a published batch followed the rules. It cannot prove that every possible bid was included, that a bridge asset is truly riskless, that a credential issuer was fair, or that off-chain side deals did not exist.

5. **Same-chain NAV reduces some front-running surfaces; it does not eliminate strategic behavior.** Ordering, inclusion, batch-close timing, public aggregate receipts, source-chain bridge deposits, and credential gating remain control surfaces.

6. **Primary TVL formation does not guarantee secondary liquidity.** A private subscription book can load reserves without walking an AMM. It does not guarantee exits for holders.

With those limits stated, the positive case is still strong: private primary subscriptions are a cleaner way to form NAVCoin TVL than forcing the first serious buyers through a thin public pool.

## The market problem: public pools are bad at absorbing primary TVL

A NAVCoin like a651 is a floating-NAV token backed by a proven portfolio. Its NAV is computed through the NAVCoin policy system and finalized into Post Fiat state. But a token that trades only through a public AMM inherits the public AMM’s launch problem: every large trade is visible, sequenced, and priced against a thin curve.

For an institutional buyer, that creates three costs:

- **Market impact:** the buyer walks the pool and pays slippage.
- **Information leakage:** the buyer broadcasts timing, size, and intent.
- **Adverse selection:** arbitrageurs and searchers can trade around the flow.

It also misses the main economic objective. A secondary-market purchase sends USDC to the seller or LPs, not necessarily to the NAVCoin reserve vault. It changes ownership. It does not automatically increase reserves.

The TVL-forming path is primary issuance:

```text
subscriber USDC -> reserve vault
MintController NAVCoin -> subscriber
```

That is the flow worth protecting. If a buyer wants to commit $5M, $10M, or $50M into a NAVCoin reserve system, the protocol should prefer a controlled primary subscription over a public pool trade. The buyer avoids unnecessary signaling and AMM impact. The reserve vault receives assets. The public can audit aggregate reserve and supply changes.

## The issuance invariant

The subscription mechanism should be policy-bound. A batch should not be “private” in the sense of trusting the issuer to do the math off-chain. It should be private at the participant/fill layer and replayable at the reserve/supply layer.

A simple policy skeleton looks like this:

```text
BPS = 10_000

min_subscription_price =
  nav_floor * (BPS + issuance_spread_bps) / BPS

net_counted_usdc_for_batch =
  Σ_i floor(receipt_i.amount_atoms * (BPS - receipt_i.haircut_bps) / BPS)

released_atoms <=
  floor(net_counted_usdc_for_batch * UNIT_SCALE / clearing_price)

(verified_net_assets_before + net_counted_usdc_for_batch) * UNIT_SCALE
  >= (valid_supply_before + released_atoms) * nav_floor
```

Important details:

- `valid_supply_before` excludes unreleased mint escrow.
- `net_counted_usdc_for_batch` uses source-domain haircuts.
- `clearing_price` must be at least `min_subscription_price`.
- Minted NAVCoin becomes circulating supply only after the reserve receipt is counted and the escrow release transition succeeds.

This is the core safety property: privacy cannot come at the cost of unbacked supply.

## Flow A: private primary NAV subscriptions

A credible private subscription flow has five moving parts:

1. A subscription envelope.
2. Source-labeled reserve receipts.
3. Enforced mint escrow.
4. A private, verifiable batch allocation mechanism.
5. A replay transcript and privacy-budget policy.

### 1. Publish the subscription envelope

The issuer or protocol publishes a subscription envelope that fixes the terms before bids arrive.

```text
SubscriptionEnvelope {
  envelope_id
  asset_id
  settlement_asset_id
  nav_floor
  issuance_spread_bps
  min_subscription_price
  max_mint_atoms
  max_usdc_accept
  accepted_source_domains
  haircut_policy_hash
  reserve_vault_id
  reserve_packet_hash
  supply_packet_hash
  credential_root
  revocation_root
  privacy_thresholds_hash
  valid_after
  expires_at
  policy_hash
}
```

A useful commitment is:

```text
envelope_id =
  H(chain_id, asset_id, settlement_asset_id, batch_id,
    nav_root, reserve_packet_hash, supply_packet_hash,
    policy_hash, haircut_policy_hash, credential_root,
    revocation_root, privacy_thresholds_hash,
    valid_after, expires_at, max_mint_atoms,
    max_usdc_accept, reserve_vault_id)
```

The envelope is not open-ended public minting at NAV. It is capped primary issuance against counted reserve assets, under a specific policy hash, during a specific window.

### 2. Treat USDC provenance as a reserve boundary

The reserve vault should not count “USDC” as a single undifferentiated thing. It should count source-labeled claims.

That is the job of `ReserveReceipt`.

```text
ReserveReceipt {
  receipt_id
  asset_id
  amount_atoms
  source_domain
  claim_type
  source_tx_or_attestation
  finality_height_or_attestation_id
  vault_id
  haircut_bps
  counted_value_atoms
  allocated_value_atoms
  status
  batch_id
}

status:
  Pending -> Finalized -> Counted -> Rejected/Revoked
```

A receipt becomes useful for mint release only when it is `Counted`.

```text
counted_value_atoms =
  floor(amount_atoms * (10_000 - haircut_bps) / 10_000)
```

The source-domain policy should be explicit:

| Source of settlement asset | Example treatment |
|---|---|
| Circle-issued native USDC on PFTL, if supported | Lowest operational haircut, subject to Circle/blacklist/redemption risk |
| Circle CCTP-minted USDC | Low haircut if Circle attestation and source finality are accepted |
| Third-party bridged USDC | Haircut based on bridge security, governance, liquidity, and redemption path; possibly excluded |
| Custodial USDC credit | Haircut based on custodian, legal claim, attestations, and withdrawal terms |
| Synthetic stablecoin | Separate collateral/oracle risk; should not be silently treated as reserve-quality USDC |

The important point is negative: PFTL cannot magically make bridged or custodial USDC reserve-quality. It can label the claim, enforce haircuts, and prevent that claim from being counted beyond policy.

A haircut function can be committed in the envelope:

```text
haircut_bps =
  haircut_policy(source_domain, claim_type, issuer,
                 bridge_id, custodian_id, finality_age,
                 concentration_limits, emergency_flags)
```

Public reserve packets should disclose source composition and haircuts at the aggregate level. That disclosure helps auditability, but it also leaks information. The system should acknowledge that tradeoff rather than pretend aggregate reserve accounting is invisible.

### 3. Make `MintEscrow` fail closed

Mint escrow is the fatal failure point. If newly minted NAVCoin becomes transferable before reserve receipts are finalized, counted, and tied into the backing invariant, the system has created unbacked supply.

So `MintEscrow` should be a protocol-enforced object type, not a social promise.

```text
MintEscrow {
  escrow_id
  asset_id
  max_release_atoms
  released_atoms
  subscription_envelope_id
  reserve_receipt_set_digest
  beneficiary_commitment
  status
}

status:
  Authorized -> Funded -> Released
             -> Expired
             -> Burned
```

The enforcement rule should be mechanical:

```text
release_valid iff
  escrow.status == Funded
  receipt.status == Counted
  receipt.allocated_value_atoms + release_value <= receipt.counted_value_atoms
  clearing_price >= min_subscription_price
  released_atoms <= max_release_atoms
  post_mint_backing_invariant == true
  escrow_id has not been consumed before
```

Unreleased escrow has two properties:

```text
transferable = false
included_in_valid_supply = false
```

Generic transfer circuits and shielded swap circuits should reject escrowed NAVCoin as an input. The only valid consumers are release or burn/expiry transitions. If USDC settlement fails, the escrow expires or burns. It does not leak into circulating supply.

For truly PFTL-native, finalized settlement assets, receipt counting and escrow release may be close together in the same finalization flow. For CCTP, bridged, or custodial settlement assets, release should wait until the external proof or attestation is finalized and the receipt is counted. That may make the flow two-phase. Safety is more important than pretending every source domain can be made atomic.

### 4. Accept private bids with credential nullifiers

Primary subscriptions usually need eligibility controls. The goal is not anonymous public minting; it is qualified-private issuance.

A buyer can prove membership in an approved investor set and non-revocation without putting their identity on the public chain. A batch-specific nullifier prevents credential reuse while avoiding cross-batch linkability.

```text
credential_nullifier =
  PRF(credential_secret, batch_id || asset_id || credential_issuer_id)

bid_commitment =
  H(batch_id, bidder_nullifier, max_usdc, limit_price_tick,
    min_fill, refund_note_commitment, credential_nullifier, salt)
```

The public chain should learn:

```text
this bid used a valid credential
this credential was not revoked
this credential_nullifier was not reused in this batch
```

It should not learn the bidder identity, size, limit price, fill, or refund amount.

But credential privacy introduces governance risk. Someone controls the credential root. Someone controls revocations. Someone may hold compliance viewing keys. Those keys can become a censorship point, a privacy backdoor, or a compliance bottleneck.

A production design should make that explicit:

```text
CredentialPolicy {
  issuer_set
  auditor_set
  threshold_signature_policy
  revocation_update_delay
  emergency_revocation_policy
  viewing_key_scope
  key_rotation_policy
  disclosure_policy_hash
}
```

If an auditor viewing key receives encrypted identity and fill details, then privacy is from the public chain, not necessarily from the issuer or auditor. That may be appropriate for regulated distribution, but it is a trust boundary, not a cryptographic free lunch.

### 5. Close the batch: sealed-bid allocation is the hard part

A verifiable sealed-bid uniform-price batch is not easy.

The batch has to handle private bids, limit prices, pro-rata cutoff allocation, deterministic tie-breaks, refunds, mint caps, reserve haircuts, credential nullifiers, and proof of correct clearing. That usually implies one of three approaches:

1. **Threshold encryption:** bids are encrypted before close and decrypted by a committee after close. This is simpler than a full private matching circuit, but the committee can be a liveness or collusion risk.
2. **MPC matching:** a committee computes the allocation privately and publishes a proof or transcript. This moves complexity into committee governance and implementation.
3. **ZK sorting/selection:** the allocation is proven directly in zero knowledge. This reduces committee trust but can be circuit-heavy, especially with pro-rata cutoffs and refunds.

A deterministic clearing rule might look like:

```text
eligible_i(p) = limit_price_i >= p

gross_demand(p) =
  Σ_i max_usdc_i * eligible_i(p)

p* =
  deterministic_clearing_tick(bids,
                              min_subscription_price,
                              max_usdc_accept,
                              max_mint_atoms)

accepted_usdc_total <= max_usdc_accept

released_atoms =
  floor(net_counted_usdc_for_batch * UNIT_SCALE / p*)

released_atoms <= max_mint_atoms
```

At the cutoff:

```text
accepted_usdc_i = 0
  if limit_price_i < p*

accepted_usdc_i = max_usdc_i
  if limit_price_i > p* and cap remains

accepted_usdc_i = pro_rata(max_usdc_i, remaining_cap)
  if limit_price_i == p*

refund_i = max_usdc_i - accepted_usdc_i
```

If `accepted_usdc_i < min_fill_i`, the rule must either reject that bid and recompute deterministically or define the cutoff treatment in advance. This sounds like a detail; in a private auction it is a source of both bugs and favoritism unless it is committed before the batch opens.

A practical launch may start with a simpler mechanism: fixed-price, capped, credentialed private batches with deterministic pro-rata allocation. The full sealed-bid uniform-price book can come later. The safety primitives — `ReserveReceipt`, `MintEscrow`, and replay — should come first.

### 6. Settle and publish aggregate receipts

After the batch clears, accepted USDC moves to the reserve vault and NAVCoin releases from mint escrow.

```text
inputs:
  accepted shielded USDC notes or owned-value locks
  MintEscrow allocations
  valid SubscriptionEnvelope
  Counted ReserveReceipt set
  credential/nullifier proofs

settlement proves:
  accepted notes are valid and authorized
  credential nullifiers are unique
  bid limits and clearing rule were respected
  refunds are correct
  reserve receipts are Counted
  receipt allocation is not double-used
  clearing price satisfies policy
  released NAVCoin is within cap
  post-mint backing invariant holds

outputs:
  shielded NAVCoin notes to subscribers
  shielded or transparent refunds
  reserve receipt updates
  supply receipt updates
  consumed escrow objects
```

The public should not see individual fills. It should see enough aggregate data to verify solvency.

```text
ReplayTranscript {
  batch_id
  envelope_id
  policy_hash
  before_reserve_root
  after_reserve_root
  before_supply_root
  after_supply_root
  before_escrow_root
  after_escrow_root
  note_tree_root
  nullifier_root
  credential_root
  revocation_root
  bid_commitment_root
  accepted_commitment_root
  refund_commitment_root
  aggregate_usdc_gross
  aggregate_usdc_counted_net
  aggregate_navcoin_released
  clearing_price_tick
  reserve_receipt_ids
  receipt_allocation_digest
  proof_hashes
}
```

A replay verifier should be able to check:

```text
aggregate_usdc_counted_net =
  Σ receipt.counted_value_atoms allocated to batch

aggregate_navcoin_released =
  Σ escrow.release_atoms

all credential_nullifiers are unique

all note nullifiers are unique

after_reserve_root =
  apply_counted_receipts(before_reserve_root, receipt_set)

after_supply_root =
  apply_released_supply(before_supply_root, escrow_releases)

(verified_net_assets_before + aggregate_usdc_counted_net) * UNIT_SCALE
  >= (valid_supply_before + aggregate_navcoin_released) * nav_floor
```

This is the auditability side of the privacy tradeoff. Outsiders can verify that the batch did not mint beyond counted reserves. They cannot see who subscribed or how each fill was allocated.

### 7. Define a privacy budget before launch

A batch is not meaningfully private just because it uses shielded notes. If one buyer takes 90% of the allocation and the public transcript shows aggregate USDC-in, NAVCoin-out, and the clearing tick, the economics are mostly visible.

The implied average price is public:

```text
implied_price =
  aggregate_usdc_counted_net * UNIT_SCALE / aggregate_navcoin_released
```

For a uniform-price batch, the clearing price is also public or tightly inferable. That is fine for auditability. It is not fine if the marketing claim is “perfect privacy.”

A credible launch policy should define execution thresholds:

```text
execute_with_private_label iff
  accepted_bidders >= K_MIN
  aggregate_usdc_gross >= MIN_AGGREGATE_USDC
  max_i(accepted_usdc_i) / aggregate_usdc_gross <= MAX_SINGLE_BIDDER_SHARE
  batch_duration >= MIN_BATCH_DURATION
```

An example launch policy might use values like:

```text
K_MIN = 5
MAX_SINGLE_BIDDER_SHARE = 40%
MIN_BATCH_DURATION = 24 hours
MIN_AGGREGATE_USDC = issuer-defined per asset
```

Those numbers are policy choices, not universal constants. The important part is that the thresholds are committed in the subscription envelope.

If thresholds are not met, the protocol should not pretend privacy was preserved. It can:

- roll the batch forward,
- cap the largest allocation and refund the excess,
- merge with the next batch,
- execute as a reduced-privacy RFQ with explicit disclosure,
- or cancel and refund.

Other leakage countermeasures help but do not remove the tradeoff:

- coarse price ticks instead of arbitrary prices,
- fixed batch windows instead of discretionary closes,
- delayed aggregate publication until the reserve packet deadline,
- aggregation of multiple reserve receipts into one packet,
- pre-funded shielded USDC to avoid obvious source-chain bridge timing,
- public labeling when a batch executed below the normal privacy threshold.

This is the honest privacy claim: hide individual participants and fills when the anonymity set is large enough; disclose aggregate accounting so solvency remains checkable.

## Replayability is useful, but it is not trustless finality for the outside world

PFTL replayability means an outsider can recompute the state transition from public transcript data and verify that the published packet followed the rules. That is valuable. It is not the same thing as proving every external fact.

Replay can verify:

- the envelope hash,
- the policy hash,
- reserve receipt inclusion,
- escrow release correctness,
- aggregate USDC counted,
- aggregate NAVCoin released,
- nullifier uniqueness,
- backing invariant preservation.

Replay cannot prove:

- every possible buyer was allowed to bid,
- every off-chain bid was submitted to the commitment registry,
- a credential issuer was fair,
- a bridge or custodian is riskless,
- Circle or any stablecoin issuer will redeem under all conditions,
- no side payments or side letters existed,
- a small batch provided meaningful privacy.

The clean way to narrow the input-completeness problem is to use a public append-only commitment registry before the batch closes. Then the replay verifier can check that every registered commitment was accepted, rejected, refunded, or expired according to the rules. That still does not prove that no one was censored before their commitment reached the registry.

## Flow B: private secondary OTC swaps

Private secondary OTC is the second use case. It is useful, but it should not be confused with primary TVL formation.

### 1. Bring assets onto PFTL

For NAVCoin, the intended pattern is burn-here-mint-there:

```text
burn a651 on Ethereum or Arbitrum
verify burn proof
mint canonical a651 on PFTL
```

That preserves global supply if the burn proof and issuer-relayed mint process are correct. It also introduces a bridge/issuer trust boundary. The PFTL asset can be native to PFTL after minting, but the movement from the EVM domain is still an external process that needs replayable evidence and governance.

For USDC, the same source-domain distinction applies. A secondary buyer may fund with PFTL-native USDC, CCTP USDC, bridged USDC, or another approved stablecoin. The accounting consequences differ if the trade later becomes part of primary issuance or reserve operations.

### 2. Shield the position

A holder can move transparent NAVCoin into the shielded note set:

```text
transparent a651 balance
  -> shield(a651, amount)
  -> shielded note
```

The public chain sees that a shield action occurred. In a sufficiently active shielded pool, it does not see the asset, amount, sender, receiver, or future spend path. But shield and unshield boundaries are common privacy leaks. If a single large holder shields shortly before a known OTC settlement, observers may infer more than the circuit reveals.

### 3. Execute the shielded OTC swap

A bilateral OTC trade can be represented as a shielded swap action:

```text
inputs:
  seller shielded note: a651
  buyer shielded note: USDC

shielded swap proof:
  seller note exists in the note tree
  buyer note exists in the note tree
  both notes are authorized
  input nullifiers have not appeared before
  value is conserved per asset
  optional NAV-band or price-policy predicate holds

outputs:
  shielded a651 note to buyer
  shielded USDC note to seller
  change notes as needed
```

The public chain verifies the proof, nullifiers, and commitments. It does not learn the cleartext asset amounts or bilateral price from the base transaction data.

A NAV-band predicate can be added without revealing the price:

```text
nav_floor * lower_band_bps / 10_000
  <= private_swap_price
  <= nav_floor * upper_band_bps / 10_000
```

That is useful for policy-constrained venues. It is not necessary for all secondary OTC trades.

### 4. What the public sees

For a secondary shielded swap, the public signal should be limited to something like:

```text
block N:
  shielded action proof
  consumed nullifier commitments
  new note commitments
  fee payment
```

The base ledger should not reveal:

```text
asset type
amount
sender
receiver
bilateral price
counterparty pair
```

That does not mean no observer can infer anything. Timing, bridge deposits, unshield events, wallet behavior, and a small shielded anonymity set can all leak information. The privacy budget concept applies to secondary markets too, even if there is no public aggregate reserve receipt for each trade.

## Secondary liquidity is still a market problem

Private primary subscriptions help form TVL. They do not guarantee exits.

A NAVCoin can have strong reserves and still trade with poor secondary liquidity if:

- public AMM liquidity is thin,
- OTC desks are not quoting both sides,
- buyers wait for primary windows instead of buying from holders,
- sellers demand immediate exits while the market is fragmented,
- private OTC prices are not visible enough to support public price discovery.

Shielded OTC improves execution privacy. It does not manufacture counterparties.

A mature design probably needs several layers:

```text
primary subscription batches
  -> TVL formation

public AMM or disclosed liquidity program
  -> visible secondary reference market

private RFQ / OTC
  -> block execution without public signaling

redemption or market-ops policy, if enabled
  -> bounded exit support under disclosed rules
```

The order matters. Initial TVL should not depend on a thin AMM. But after TVL forms, the protocol still needs credible secondary liquidity, market-maker incentives, redemption policy, or some other exit mechanism. Private settlement is a tool, not a liquidity guarantee.

## Same-chain NAV helps, but it is not magic

The strongest reason to consider Post Fiat for this design is not a generic claim about privacy chains. It is specific to NAVCoin: the NAV proof, reserve packets, supply packets, and collateralization policy are intended to live in PFTL state. If issuance and shielded settlement also live there, the critical path avoids an extra cross-domain oracle hop.

That helps in several ways:

| Risk surface | If settlement is on another chain | If settlement is on PFTL |
|---|---|---|
| NAV freshness | NAV must be bridged or relayed | Settlement can reference the finalized PFTL NAV root |
| Policy enforcement | Split across oracle bridge and venue contract | Subscription policy can reference the same reserve/supply roots |
| Reserve accounting | External settlement evidence must be reconciled | `ReserveReceipt` can be part of the PFTL replay transcript |
| Mint release | Bridge timing can create gaps | `MintEscrow` can be enforced by the same state machine |
| Bid privacy | Depends on external privacy venue | Shielded notes can be part of the settlement layer if implemented |
| Front-running | Public mempool and stale oracle risk | Reduced stale-NAV risk; ordering and inclusion risks remain |

The front-running point deserves care. Same-chain NAV can reduce stale-oracle arbitrage and cross-chain timing games. Shielded commitments can hide bid contents before batch close. Deterministic batch rules can reduce discretionary allocation.

But strategic behavior remains possible around:

- transaction inclusion,
- batch-close timing,
- threshold decryption availability,
- bridge or CCTP deposit timing,
- public aggregate receipts,
- credential issuance and revocation,
- validator or committee censorship,
- small-batch inference.

The right claim is not “no front-running.” The right claim is narrower: co-locating NAV state, issuance policy, and shielded settlement removes some avoidable latency and information surfaces that appear when NAV is proven on one chain and traded on another.

## Collateralization and market operations

The same accounting model also fits NAVCoin collateralization.

Above NAV, premium demand should primarily be served through controlled primary subscriptions rather than forcing buyers through a thin public pool. The mint path is:

```text
Counted ReserveReceipt
  -> MintEscrow release
  -> supply packet update
  -> post-mint backing check
```

Below NAV, an alignment reserve could buy NAVCoin through public venues, private RFQ, or shielded swaps under disclosed caps. Shielding the action can reduce pre-trade signaling, but aggregate reserve changes and later disclosures can still reveal that market operations occurred.

A conservative launch order is:

```text
1. Build ReserveReceipt and MintEscrow.
2. Run capped private primary subscriptions to form reserve TVL.
3. Seed public liquidity with disclosed capital.
4. Observe secondary market behavior.
5. Enable automated market-ops only under replayable caps.
```

That sequence is less flashy than “launch a dark pool,” but it is safer. Reserve accounting and mint safety should come before auction complexity.

## What needs to be built

The build order should put accounting safety before market sophistication.

1. **USDC source-domain adapter.** PFTL needs an accepted settlement asset, but the reserve system must distinguish native Circle USDC, CCTP USDC, bridged USDC, custodial USDC, and synthetics. Source, proof, and haircut must be part of the reserve packet. This is the role of [pfUSDC](/blog/pfusdc/): receipt-backed cash for PFTL, not an undifferentiated bridge wrapper.

2. **`ReserveReceipt` state machine.** Deposits move through `Pending -> Finalized -> Counted`. Only counted receipts can support mint release. Receipts carry source-domain metadata, finality proof, vault, haircut, and batch linkage.

3. **`MintEscrow` state machine.** Newly authorized NAVCoin starts non-transferable and excluded from valid supply. Release consumes counted receipt capacity, proves the backing invariant, and writes the supply update. Failed settlement expires or burns escrow.

4. **Replay verifier.** A reference CLI/library should rebuild each batch from public transcript data: roots, envelope hash, receipt IDs, aggregate values, clearing tick, escrow releases, nullifiers, and proof hashes.

5. **Fixed-price private subscription MVP.** Before a full sealed-bid auction, a capped fixed-price batch with private credentials, deterministic pro-rata allocation, refunds, and replayable aggregate receipts is a more realistic first target.

6. **Qualified-private credential layer.** Credential roots, revocation roots, nullifiers, viewing-key scope, auditor access, key rotation, and emergency procedures need explicit governance.

7. **Sealed-bid uniform-price batch.** This is the advanced version. It needs threshold encryption, MPC, or heavy ZK sorting/selection to prove correct clearing, cutoff allocation, tie-breaks, refunds, and nullifier uniqueness without revealing the book.

8. **Shielded primary subscription circuit.** The action consumes accepted shielded USDC or owned-value locks, references the subscription envelope, enforces price/backing policy, pays the vault, and releases NAVCoin only through `MintEscrow`.

9. **Shielded secondary swap circuit.** The action consumes two shielded notes, verifies authorization and nullifiers, conserves value per asset, and outputs swapped notes. Optional NAV-band predicates can be added.

10. **Private RFQ and OTC workflow.** Secondary OTC needs encrypted quoting, bilateral matching, settlement coordination, and operational tooling. The circuit alone is not a market.

11. **Privacy-budget disclosure.** Batch thresholds and fallback behavior should be part of the envelope. If a batch executes below threshold, the system should label it as reduced privacy.

## Why this matters

The skeptical version of the thesis is stronger than the promotional one.

Private primary subscriptions do not remove every trust assumption. They require source-labeled reserve assets, careful mint escrow, credential governance, replay tooling, and honest privacy-budget disclosures. The sealed-bid version is hard engineering. Secondary OTC does not guarantee exits.

Even with those caveats, the design is economically attractive.

A serious buyer should be able to put USDC into a NAVCoin reserve vault without walking a thin AMM, broadcasting the trade, or handing the launch premium to arbitrageurs. The public should be able to verify that aggregate reserves increased, aggregate supply increased by no more than policy allowed, and the post-mint backing invariant still holds. The issuer or auditor may receive compliance disclosures, but the public chain should not learn every subscriber’s identity and fill.

That is the product shape:

```text
private primary subscriptions
  -> reserve TVL formation

private secondary OTC swaps
  -> quieter ownership transfer

replayable reserve and supply packets
  -> public solvency audit
```

Post Fiat is a natural venue to attempt this because NAVCoin’s NAV state and collateralization policy are already intended to live there. The design target is not perfect privacy and not trustless external assets. It is a more credible primary issuance path: counted reserves in, enforceable mint escrow out, and enough replay data for outsiders to verify the aggregate math.

---

*Implementation references: `postfiatl1v2` branch `fastpay-m1` for owned-value and shielded-settlement primitives; `navcoin-market-ops-envelope` for NAVCoin collateralization work; Phase 4 of the [PFTL-canonical migration plan](/blog/navcoin-ethereum/) for burn-here-mint-there asset movement; shielded settlement design in whitepaper §7. The `ReserveReceipt`, `MintEscrow`, sealed-bid subscription book, credential-nullifier layer, PFTL USDC source-domain adapter, and replay verifier described here are proposed architecture components, not production deployments.*
