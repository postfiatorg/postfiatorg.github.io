---
title: "pfUSDC: Source-Labeled Cash Receipts for NAVCoin"
date: 2026-06-18T00:00:00Z
draft: true
summary: "pfUSDC is a proposed PFTL-native cash receipt asset for NAVCoin settlement. It would count external USDC only after source proof, finality, policy haircuts, and reserve allocation are recorded, so NAVCoin primary subscriptions consume counted cash instead of trusting an undifferentiated wrapped-dollar ticker."
categories:
  - Post Fiat Research
tags:
  - pfUSDC
  - NAVCoin
  - USDC
  - Stablecoins
  - Proof of Reserves
  - Post Fiat
  - PFTL
  - OTC
---

The private NAVCoin subscription design has a hard precondition: the cash leg must be countable before it can release newly minted NAVCoin.

Calling that leg "USDC on PFTL" hides too much. Native issuer USDC, Circle CCTP USDC, third-party bridged USDC, custodial USDC, and synthetic dollars are not the same risk. A ticker does not tell the reserve system where the cash came from, what finality proof exists, who can freeze it, how it can be redeemed, or how much of it should count.

pfUSDC is the proposed answer: a PFTL-native cash receipt asset backed by source-labeled reserve receipts.

It is not fake-native Circle USDC. It is not an opaque bridge wrapper. It is a way for PFTL to say: "This dollar claim came from this route, passed this proof, received this haircut, and can support this much settlement."

## Status: research proposal, not a live stablecoin

This post is a design proposal. It does not announce a launched pfUSDC asset.

At the time of writing:

- pfUSDC is not live.
- No pfUSDC contracts, circuits, adapters, or replay verifiers are being represented here as deployed or audited.
- No haircut values in this article are validated risk parameters.
- No legal claim, bankruptcy treatment, or redemption right is created by this article.
- pfUSDC would still depend on external systems: Circle, bridges, custodians, attestations, source chains, legal entities, and market liquidity.

The design target is narrower and more honest:

```text
PFTL cannot turn a weak dollar claim into a strong dollar claim.

It can label the claim.
It can wait for finality.
It can haircut the claim.
It can allocate the counted value once.
It can pause impaired sources.
It can refuse to release NAVCoin from uncounted cash.
```

That is the point.

## The mental model

There are three different things in the design. Confusing them makes pfUSDC sound more magical than it is.

### 1. The external dollar claim

This is the thing outside PFTL: USDC on Arbitrum, a CCTP burn-and-mint attestation, a custodian statement, a bridge deposit, or some other accepted claim.

It is where most of the real-world risk lives.

### 2. The ReserveReceipt

A `ReserveReceipt` is not the user-facing money. It is an accounting object.

It records:

- source domain
- source transaction or attestation
- finality evidence
- amount
- vault or bridge route
- policy version
- haircut
- counted value
- allocation status

The receipt stays in the reserve ledger. It should be replayable by auditors and verifiers.

### 3. pfUSDC

pfUSDC is the thing that can move between users or into a NAVCoin subscription escrow. In the simplest version, it can be a transparent source-labeled receipt token. Later, it can be represented as shielded notes.

The important distinction:

```text
ReserveReceipt = non-transfer accounting record
counted value  = haircut-adjusted reserve capacity
pfUSDC         = transferable PFTL cash receipt backed by counted capacity
```

A minimal flow looks like this:

```text
external USDC claim
  -> source proof or attestation
  -> ReserveReceipt
  -> finality check
  -> haircut policy
  -> counted value
  -> pfUSDC mint or direct counted-cash credit
  -> NAVCoin MintEscrow allocation
```

If a user sends pfUSDC to another user, the receipt does not move. The transfer moves a claim against counted reserve capacity. The reserve ledger remains the accounting source of truth.

## Why this has to exist before NAVCoin subscriptions

A NAVCoin primary subscription is not just a trade. It can release newly minted NAVCoin. If the cash leg is weak, stale, frozen, or double-counted, the NAVCoin reserve can be damaged at issuance.

Without a counted-cash primitive, the flow is discretionary:

```text
buyer deposits some asset called USDC
issuer or operator decides whether it counts
NAVCoin releases if the operator accepts it
```

With pfUSDC or counted receipts, the flow becomes mechanical:

```text
buyer deposits accepted external USDC
ReserveReceipt records source and proof
policy computes counted value
MintEscrow consumes counted value
NAVCoin releases only if reserve checks pass
```

The rule should be simple:

```text
No NAVCoin primary mint releases from uncounted cash.
```

The same primitive also matters for private OTC swaps. The cash side can move through shielded PFTL notes, while the reserve side remains auditable in aggregate. Privacy at the transfer layer should not mean ambiguity at the backing layer.

## Is pfUSDC overkill?

A fair objection is that PFTL could simply accept an existing wrapped USDC, or maintain an attestation registry that scores external USDC balances.

That may be enough for some applications. It is not obviously enough for NAVCoin issuance.

| Approach | What it does well | Where it falls short for NAVCoin |
|---|---|---|
| Plain wrapped USDC | Simple UX and liquidity if the wrapper is trusted. | Usually collapses source, bridge, custody, finality, and redemption risk into one ticker. |
| Attestation registry only | Can label and score external balances. | Does not create a PFTL-native cash object that can transfer, be escrowed, be burned, and be allocated without double-counting. |
| Thin pfUSDC receipt asset | Gives PFTL a transferable counted-cash claim tied to reserve receipts. | Requires reserve accounting, source policy, and replay verification. |
| Fully pooled multi-source pfUSDC | Best UX if done well. | Too complex for day one; requires explicit loss-sharing and redemption rules. |

The day-one version should be thin.

pfUSDC does not need to start as a giant multi-source stablecoin. For NAVCoin subscriptions, the minimum useful object is:

```text
source-labeled receipt asset
+ ReserveReceipt registry
+ haircut and pause policy
+ NAVCoin acceptance rule
+ replayable reserve/supply packets
```

If the first version only supports one source domain and one transparent receipt series, that is fine. The goal is counted cash, not a new stablecoin empire.

## Worked example: Arbitrum native USDC into a NAVCoin subscription

This example is illustrative. The numbers are for arithmetic only, not a recommendation.

For Hyperliquid-related reserve operations, the practical first production source domain is Arbitrum native USDC routed through Hyperliquid's native bridge, because Hyperliquid's current deposit path is centered on USDC entering from Arbitrum. Circle Arc is public testnet and should not be an MVP dependency. Arc, xReserve, and CCTP may become cleaner future source domains, but the first production route should use what the venue actually accepts.

Assume:

```text
source_domain = "arbitrum_native_usdc_hyperliquid_route"
USDC decimals = 6
deposit = 100,000.000000 USDC
illustrative_haircut_bps = 25
BPS = 10,000
```

### Step 1: deposit observed

A user deposits 100,000 USDC through the accepted source route.

```text
amount_atoms = 100000 * 1000000
             = 100000000000
```

The adapter creates a `Pending` receipt.

```text
ReserveReceipt:
  source_domain: arbitrum_native_usdc_hyperliquid_route
  amount_atoms: 100000000000
  status: Pending
```

No pfUSDC can be minted yet. No NAVCoin can be released yet.

### Step 2: finality accepted

After the source-domain finality rule is satisfied, the receipt can move from `Pending` to `Finalized`.

```text
Pending -> Finalized
```

This still does not mean the cash is countable. It only means the proof has reached the required finality threshold for that source domain.

### Step 3: haircut applied

Policy applies the illustrative 25 bps haircut.

```text
counted_atoms =
  floor(amount_atoms * (BPS - haircut_bps) / BPS)

counted_atoms =
  floor(100000000000 * (10000 - 25) / 10000)

counted_atoms = 99750000000
```

So the counted value is:

```text
99,750.000000 USDC
```

The receipt can now become `Counted`.

```text
Finalized -> Counted
```

### Step 4: pfUSDC mint capacity

Assume no other supply or allocations exist in this bucket.

```text
available_to_mint = 99,750.000000 pfUSDC
```

The user mints only 60,000 pfUSDC.

```text
pfusdc_minted = 60,000.000000
unallocated_counted_capacity = 39,750.000000
```

The reserve check is:

```text
outstanding_pfusdc <= counted_cash

60,000 <= 99,750
```

### Step 5: NAVCoin subscription uses pfUSDC

The user contributes 50,000 pfUSDC into a NAVCoin subscription batch. The subscription escrow either burns it or locks it and reallocates the counted value from the pfUSDC liability to the NAVCoin cash allocation.

Assume:

```text
subscription_cash = 50,000 USDC
clearing_price = 25 USDC per NAVCoin
```

The maximum release for this batch is:

```text
released_navcoin = floor(subscription_cash / clearing_price)

released_navcoin = floor(50000 / 25)
released_navcoin = 2,000 NAVCoin
```

After the subscription contribution:

```text
counted_cash = 99,750
outstanding_pfusdc = 10,000
allocated_to_nav_batch = 50,000
unallocated_counted_capacity = 39,750
```

The bucket-level check is:

```text
outstanding_pfusdc + allocated_to_nav_batch <= counted_cash

10,000 + 50,000 <= 99,750
```

The NAVCoin floor check also has to pass. Suppose before the batch:

```text
verified_net_assets_before = 2,000,000 USDC
valid_navcoin_supply_before = 100,000 NAVCoin
nav_floor = 20 USDC per NAVCoin
```

After adding 50,000 counted USDC and releasing 2,000 NAVCoin:

```text
verified_net_assets_after = 2,000,000 + 50,000
verified_net_assets_after = 2,050,000

valid_navcoin_supply_after = 100,000 + 2,000
valid_navcoin_supply_after = 102,000

required_floor_assets = 102,000 * 20
required_floor_assets = 2,040,000
```

The batch passes this simplified floor check:

```text
2,050,000 >= 2,040,000
```

The key point is not the specific numbers. The key point is ordering:

```text
source proof first
counted cash second
pfUSDC or cash credit third
NAVCoin release last
```

## Formal primitive: ReserveReceipt and allocation ledger

The following is a proposed accounting interface. It is not a production spec, not audited code, and not a formal verification result.

A `ReserveReceipt` records an admitted external claim.

```text
ReserveReceipt {
  receipt_id
  asset_id
  source_domain
  source_asset
  claim_type
  amount_atoms
  source_tx_or_attestation
  finality_ref
  vault_id
  policy_version
  haircut_bps
  counted_value_atoms
  allocated_value_atoms
  bucket_id
  status
  created_at
  finalized_at
  counted_at
  expires_at
}
```

Suggested statuses:

| Status | Meaning |
|---|---|
| `Pending` | A deposit or claim has been observed, but the source proof is not final enough to count. |
| `Finalized` | The source proof or attestation has met the source-domain finality rule. |
| `Counted` | Policy has accepted the receipt and assigned a haircut-adjusted counted value. |
| `Paused` | New use of the source domain or receipt is stopped while data or risk is reviewed. |
| `Impaired` | The receipt or source bucket has been revalued because recovery, redemption, or proof validity is in doubt. |
| `Rejected` | The proof, source, or policy check failed. |
| `Retired` | The receipt has been fully redeemed, burned out, or otherwise removed from active backing. |

Allocation should be a ledger, not just a status. A counted receipt can be partially allocated to pfUSDC supply, a NAVCoin subscription batch, a redemption queue, or another approved protocol use.

```text
Allocation {
  receipt_id
  source_domain
  amount_atoms
  purpose
  consumer_id
  created_at
}
```

The canonical invariant should be enforced by source bucket.

```text
For each source_domain d:

counted_cash_atoms[d] =
  sum(counted_value_atoms for active Counted receipts in d)
  - sum(retired_counted_value_atoms in d)

allocated_atoms[d] =
  outstanding_pfusdc_atoms[d]
  + nav_batch_allocations_atoms[d]
  + other_protocol_allocations_atoms[d]

allocated_atoms[d] <= counted_cash_atoms[d]
```

If pfUSDC later becomes pooled across multiple source domains, this invariant still needs to hold at the bucket level and in aggregate. A single wallet ticker must not erase the backing composition.

All arithmetic should use integer atoms and basis points.

```text
BPS = 10000

counted_value_atoms =
  floor(amount_atoms * (BPS - haircut_bps) / BPS)
```

No floating point math. Rounding goes against issuance.

## Reserve packets and replay verification

A pfUSDC system should publish reserve packets that let outsiders replay the accounting without seeing every user transfer.

A reserve packet can include:

```text
ReservePacket {
  packet_id
  receipt_root
  supply_root
  source_domain_summary_root
  policy_hash
  total_counted_cash_atoms
  total_valid_pfusdc_supply_atoms
  total_nav_allocations_atoms
  paused_domains
  impaired_domains
  created_at
}
```

A replay verifier should check:

- each receipt is admitted once
- source-domain finality rules are satisfied
- counted values use the published policy version
- rounding is conservative
- allocations do not exceed counted values
- pfUSDC mint and burn events match the supply root
- NAVCoin subscription allocations use counted value only
- paused or impaired domains are not used for new counting

The verifier cannot check off-chain legal recovery. It can verify the accounting trail. It cannot make a custodian solvent, force Circle to redeem, reverse a bridge exploit, or win a bankruptcy case.

## Source domains in practice

pfUSDC should not flatten different dollar routes into one risk bucket.

| Source domain | Example claim | MVP treatment |
|---|---|---|
| Arbitrum native USDC for Hyperliquid route | USDC enters through the route Hyperliquid currently accepts for its native bridge flow. | Practical first source domain for Hyperliquid-related reserves, if Post Fiat needs that venue. |
| Circle CCTP route | USDC is burned on one supported chain and minted through Circle attestation on another. | Cleaner future route if PFTL support and operational controls are ready. |
| Circle Arc/xReserve route | Circle-associated stablecoin infrastructure and reserve tooling. | Future candidate; Arc is public testnet and should not be required for the MVP. |
| Direct issuer route | Circle issues directly on PFTL, if ever supported. | Potentially cleanest operational route, still subject to issuer freeze and redemption policy. |
| Canonical bridge route | USDC locked on one chain, receipt asset minted on PFTL. | Higher bridge, governance, and upgrade risk. |
| Custodial route | Custodian holds USDC, cash, or T-bills and publishes attestations. | Requires legal claim analysis, audit cadence, and withdrawal limits. |
| Synthetic dollar route | Dollar asset backed by collateral, oracle pricing, or market incentives. | Usually should be a separate asset, not pfUSDC, unless risk policy explicitly accepts it. |

The first production version should choose one source domain. Multi-source pooling should come later, after impairment and redemption rules are tested.

## Haircut and risk policy

Haircuts are not magic. They are a conservative accounting rule for how much of a gross external claim can count.

The starting framework should be explicit, versioned, and replayable. It should also be treated as unvalidated until tested against real stress, redemption data, bridge incidents, and legal review.

A proposed formula shape:

```text
raw_haircut_bps =
  source_floor_bps
  + proof_finality_bps
  + bridge_or_contract_bps
  + issuer_or_custody_bps
  + legal_recovery_bps
  + liquidity_exit_bps
  + concentration_bps
  + freshness_bps
  + governance_upgrade_bps
  + stress_event_bps

haircut_bps = min(raw_haircut_bps, 10000)

if raw_haircut_bps >= pause_threshold_bps:
  pause_new_counting = true
```

Example inputs:

| Input | What it measures |
|---|---|
| `source_floor_bps` | Minimum haircut for the source, even in normal conditions. |
| `proof_finality_bps` | Reorg, finality, or attestation risk. |
| `bridge_or_contract_bps` | Bridge contract security, validator set, multisig control, audits, upgrade delay. |
| `issuer_or_custody_bps` | Issuer freeze risk, custodian control, withdrawal restrictions. |
| `legal_recovery_bps` | Quality of holder rights, bankruptcy remoteness, jurisdiction, documentation. |
| `liquidity_exit_bps` | Ability to exit the route at par in size and under stress. |
| `concentration_bps` | Additional risk if too much reserve value sits in one source domain. |
| `freshness_bps` | Penalty for stale proofs, attestations, reserve packets, or venue data. |
| `governance_upgrade_bps` | Risk from admin keys, upgrade rights, emergency powers, or weak timelocks. |
| `stress_event_bps` | Incident add-on for exploits, freezes, halted withdrawals, depegs, or abnormal spreads. |

A concrete policy process could start with:

- routine risk review on a fixed cadence, such as weekly or monthly
- on-chain publication of `policy_version` and `policy_hash`
- delayed haircut decreases through a timelock
- immediate emergency pauses or haircut increases for stress events
- explicit maximum countable exposure per source domain
- automatic freshness penalties when required data is stale
- mandatory pause when freshness thresholds are missed beyond a grace period

Illustrative freshness rules might look like this:

```text
source_proof_max_age_seconds = 3600
reserve_packet_max_age_seconds = 86400
custody_attestation_max_age_seconds = 86400
policy_review_max_age_seconds = 604800
```

Those numbers are examples, not recommendations. The actual values should depend on the source domain.

Routine haircut changes can apply only to new receipts unless the policy marks them as retroactive. Stress events are different. If a bridge exploit, issuer freeze, custodian failure, or redemption halt affects existing receipts, the affected bucket has to be revalued through an impairment packet.

Policy should also include caps and floors:

```text
minimum_haircut_bps[source_domain] > 0
maximum_counted_exposure_atoms[source_domain] = policy-defined
pause_threshold_bps[source_domain] = policy-defined
```

Governance itself is a risk input. A system where governance can lower haircuts instantly, admit new sources without review, or mint around the invariant is not a conservative reserve system.

## Redemption, impairment, and loss allocation

Redemption is where wrappers often hide the hard part. pfUSDC should not promise a universal instant exit unless the source domain can actually support it.

Possible redemption modes:

| Mode | Description | Suitable for MVP? |
|---|---|---|
| Source-specific redemption | Burn pfUSDC from a source bucket and redeem through that same source route. | Yes. Cleanest accounting. |
| Pooled redemption | Burn pfUSDC against a mixed reserve pool. | Later. Requires explicit loss-sharing rules. |
| Market redemption | Swap pfUSDC through PFTL or EVM liquidity. | Useful, but not a par guarantee. |

The default should be source-domain isolation.

If a pfUSDC unit is backed by the Arbitrum/Hyperliquid route, it should not silently redeem against a stronger Circle-native or CCTP bucket unless the protocol has explicitly precommitted to that socialization. Strong buckets should not unknowingly insure weak buckets.

For the MVP, wallets and contracts should preserve source labels. That can mean separate series, such as `pfUSDC.arbhl`, or one display ticker with mandatory bucket metadata. A single unqualified ticker is dangerous if users cannot see what backs it.

### Impairment process

When a source domain is impaired:

1. Pause new receipts from becoming `Counted`.
2. Pause new pfUSDC minting from the affected bucket.
3. Freeze or queue source-specific redemption from the affected bucket.
4. Publish an impairment packet.
5. Recompute counted value for affected receipts.
6. Apply pro-rata writedown to claims allocated to that bucket if recoverable value is below bucket claims.
7. Reopen only after recapitalization, recovery, or policy resolution.

A default pro-rata formula:

```text
bucket_claim_atoms[d] =
  outstanding_pfusdc_atoms[d]
  + nav_batch_allocations_atoms[d]
  + redemption_queue_atoms[d]
  + other_protocol_allocations_atoms[d]

recoverable_counted_atoms[d] =
  updated_counted_cash_atoms[d]
  + insurance_atoms[d]
  + recapitalization_atoms[d]

bucket_factor_bps[d] =
  min(BPS, floor(recoverable_counted_atoms[d] * BPS / bucket_claim_atoms[d]))
```

If `bucket_factor_bps` is below `BPS`, claims in that bucket are impaired pro rata.

```text
redeemable_atoms =
  floor(claim_atoms * bucket_factor_bps / BPS)
```

This is not pleasant, but it is legible. The alternative is worse: pretending everything is fine until the strongest assets have been drained by the fastest redeemers.

### NAVCoin-specific impairment

If impairment happens before NAVCoin is released from a subscription batch, the batch should halt or resize.

If impairment happens after pfUSDC has been burned into a NAVCoin subscription and NAVCoin has already been released, the exposure has moved into the NAVCoin reserve. The reserve accounting should mark down verified net assets for that source bucket. NAVCoin then follows its own collateralization and market-operations policy.

pfUSDC cannot make that loss disappear. It can make sure the loss is located, measured, and not double-counted.

### Recapitalization

A source bucket can be restored by:

- successful off-chain recovery
- issuer or bridge remediation
- insurance payment
- sponsor recapitalization
- governance-approved capital injection

Any recapitalization asset should itself enter through a source-labeled receipt. The protocol should not restore par by governance vote alone.

### Residual off-chain risk

The user still bears the external risk of the claim.

A receipt can prove that a deposit was observed and counted under a policy. It does not, by itself, guarantee that:

- Circle will redeem
- a custodian is solvent
- a bridge can be recovered after an exploit
- a frozen account can be unfrozen
- a court will recognize a holder claim
- exit liquidity will exist at par during stress

Legal structure matters. If pfUSDC is ever shipped, the reserve documentation should specify who owns the reserve assets, who has redemption rights, what happens in insolvency, and whether holders have direct or indirect claims. Without that, the protocol has accounting rigor but not legal certainty.

## Auditability and privacy

pfUSDC can use shielded transfers, but reserve accounting cannot be fully private.

The public should be able to verify:

```text
total valid pfUSDC supply
total counted cash value
source-domain composition by bucket
haircut policy hash
paused domains
impaired domains
reserve receipt root
supply root
NAVCoin subscription allocations
```

The public does not need every user's balance. But it does need reserve composition. Otherwise users cannot distinguish a clean source bucket from an impaired one.

A practical design is aggregate disclosure:

```text
source_domain
claim_type
haircut_band
time_window
aggregate_gross_value
aggregate_counted_value
bucket_status
```

Detailed receipts can be available to auditors, issuers, or compliance parties through viewing keys or encrypted disclosures. Low-volume buckets may still leak timing information. The first version should prioritize transparent reserve accounting, then add shielded transfers once the accounting is replayable.

## MVP build order

The MVP should be deliberately narrow.

1. Pick one source domain.
   - For Hyperliquid-related reserves, the practical first production source domain is Arbitrum native USDC routed through Hyperliquid's native bridge.
   - Do not depend on Circle Arc for the MVP while it is public testnet.
   - Treat Circle Arc, xReserve, and CCTP as future cleaner source candidates.

2. Define the legal and operational control surface.
   - Who controls the reserve account or bridge route?
   - What rights do pfUSDC holders have?
   - What is the redemption queue?
   - What happens if the source freezes or fails?

3. Implement a transparent `ReserveReceipt` registry.
   - One source adapter.
   - One policy version.
   - Integer atom accounting.
   - Conservative rounding.

4. Implement source-labeled pfUSDC.
   - No multi-source pooling on day one.
   - No hidden fungibility across risk buckets.
   - Mint only from `Counted` receipts.

5. Implement the NAVCoin acceptance rule.
   - MintEscrow accepts only counted pfUSDC or direct counted-cash credits.
   - Each unit of counted value can be allocated once.
   - NAVCoin releases only after cash and floor checks pass.

6. Publish reserve and supply packets.
   - Receipt root.
   - Supply root.
   - Policy hash.
   - Source-domain summary.
   - Paused and impaired status.

7. Build a replay verifier.
   - Verify receipts.
   - Verify haircuts.
   - Verify allocations.
   - Verify supply.
   - Verify NAVCoin subscription consumption.

8. Add redemption and impairment handling.
   - Source-specific redemption.
   - Impairment packets.
   - Pro-rata bucket writedown.
   - Recapitalization path.

9. Add privacy later.
   - Shielded pfUSDC transfers.
   - Private OTC swap settlement.
   - Selective disclosure.
   - Aggregate reserve transparency.

10. Add more source domains only after the first one works.
    - CCTP route.
    - Circle Arc/xReserve route if production-ready and useful.
    - Direct issuer route if ever supported.
    - Custodial route only with legal review.

The first version does not need sealed-bid auctions, pooled redemptions, complex multi-source risk sharing, or full privacy. It needs counted cash that cannot be double-counted.

## Conclusion

NAVCoin primary issuance needs a cash primitive that is stricter than a ticker.

pfUSDC is that proposed primitive: source-labeled, receipt-backed, haircut-adjusted cash for PFTL settlement. It does not remove Circle risk, bridge risk, custodian risk, legal risk, or liquidity risk. It makes those risks visible enough that NAVCoin MintEscrow can refuse uncounted cash.

That is the design target: not fake-native USDC, not an opaque wrapper, but a thin receipt-backed cash rail that can grow only after its accounting, redemption, and impairment rules work.

## References and related links

- Related Post Fiat: [Private NAV Subscriptions and OTC Swaps](/blog/private-nav-otc-swaps/).
- Related Post Fiat: [NAVCoin Collateralization Without Spot Redemption](/blog/navcoin-collateralization/).
- Hyperliquid: [how to start trading](https://hyperliquid.gitbook.io/hyperliquid-docs/onboarding/how-to-start-trading), [bridge docs](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/bridge), and [Arbitrum USDC deposit note](https://hyperliquid.gitbook.io/hyperliquid-docs/support/faq/deposit-or-transfer-issues-missing-lost/deposited-via-arbitrum-network-usdc).
- Circle Arc: [Arc public site](https://www.arc.io/), [Circle Arc introduction](https://www.circle.com/blog/introducing-arc-an-open-layer-1-blockchain-purpose-built-for-stablecoin-finance), and [Arc public testnet announcement](https://www.arc.io/blog/circle-launches-arc-public-testnet).
- Circle xReserve: [Circle xReserve introduction](https://www.circle.com/blog/introducing-circle-xreserve).
- Circle multichain USDC: [Multichain USDC](https://www.circle.com/multi-chain-usdc).
