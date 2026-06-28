---
title: "Minting a651: One Portfolio, Many Access Venues"
date: 2026-06-14T00:00:00Z
draft: true
summary: "The NAVCoin verification layer proves a portfolio's NAV; this post turns that proof into a token architecture. The corrected design is not one liquidity pool with its own backing per chain. It is one verified reserve portfolio, one canonical NAV and supply ledger, many access venues, and policy-bound market operations that allocate reserves or authorize minting when venues trade away from NAV."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Proof of Reserves
  - Ethereum
  - Arbitrum
  - Solana
  - Hyperliquid
  - Base
  - BSC
  - Post Fiat
---

*Fourth in the NAVCoin series. The [proposal](/blog/navcoin-proposal/) defined a token whose supply is gated by machine-verified reserves. The [counterparty-risk extension](/blog/navcoin-counterparty-risk/) priced the venue credit a book like this carries. The [proof-of-leverage post](/blog/proof-of-leverage/) built the reserve evidence — a six-domain portfolio proven and checked on-chain. This post turns that proof into a token architecture: one verified portfolio, one canonical NAV, many access venues.*

## The accounting mistake to avoid

A multi-chain NAVCoin tempts one bad design:

> "The Base pool is backed by the Base assets.  
> The Solana pool is backed by the Solana assets.  
> The Hyperliquid pool is backed by the Hyperliquid assets."

That is wrong.

It turns one NAVCoin into several siloed claims. It makes local demand look like local insolvency. It confuses the place where assets sit with the place where holders access the token. It also forces the protocol to analyze bridges, wrappers, and liquidity routes as if they were reserve assets. They are not.

The corrected model is simpler:

> **Backing is global. Access is local. NAV alignment is policy-bound.**

A NAVCoin has one verified reserve portfolio. That portfolio may hold assets on Base, Solana, Hyperliquid, Arbitrum, Ethereum, Monero, NEAR, or anywhere else the proof profile permits. Separately, holders may access the token on Base, Solana, Hyperliquid, BSC, Arbitrum, Ethereum, or Post Fiat. Those two maps can overlap, but they are not the same map.

If the reserve portfolio has `$20,000` of assets on Base, `$10,000` on Solana, and `$10,000` on Hyperliquid, the NAVCoin is not three coins. It is one coin backed by a `$40,000` portfolio.

If the valid token supply is `15,000` units on Base, `12,000` on Solana, `8,000` on Hyperliquid, and `5,000` on Post Fiat, the Base units are not backed only by the Base assets. Every valid unit is a pro-rata claim on the same verified portfolio.

That separation is the whole architecture.

## What a651 is, in plain terms

**NAVCoin** is the infrastructure: a proof profile, a reserve-packet format, a supply discipline, mint authorization rules, and market-operation triggers. **a651** is one instance: the token whose backing is the specific portfolio proven under the a651 proof profile. There can be a651, a652, and so on; each instance has one reserve set and one canonical NAV.

The key design choice is not "which chain has the deepest liquidity?" It is "where is NAV defined?"

For a651, NAV is defined once. The canonical NAV ledger verifies the reserve packet, computes NAV per unit, gates mint authorizations and reserve deployments, tracks valid global supply, and halts stale proofs. Liquidity can then live wherever buyers are.

Four things make a651 a NAVCoin rather than just another multichain token:

1. **Its NAV per unit is the proven NAV.** The contract reads a verified reserve packet and computes net asset value per unit from proven buckets. The mark is not asserted by an issuer. It is the output of a verification process bound to a valuation policy.

2. **Every valid unit references the same portfolio.** A Base unit, a Solana unit, a Hyperliquid spot unit, and a Post Fiat native unit are not separate reserve claims. They are access forms of one claim.

3. **It has one valid global supply.** Supply is counted across the declared perimeter of valid representations. NAV is computed against that global valid supply, not against the supply in any one pool.

4. **Local venue liquidity is disclosed as market depth, not backing.** A Base pool, Solana pool, Hyperliquid order book, or BSC pool can have more or less local depth. That affects execution and NAV-alignment capacity. It does not change the backing of a valid unit.

There is no founder mint in the clean version. The first units are minted against verified capital at the same NAV formula later buyers receive. If the operator wants upside, it should come from management economics, fees, or retained reserve participation disclosed in the proof profile — not from acquiring nearly all supply at a near-zero inception NAV.

## Three packets, not one overloaded object

The corrected architecture has three separate objects.

| Object | Question it answers | What it is not |
|---|---|---|
| **Reserve Composition** | Where are the backing assets, what are they worth, and how were they verified? | It is not a list of liquidity pools. |
| **Supply Composition** | Where do valid a651 units exist or trade? | It is not a backing schedule. |
| **Market Operations Policy** | When can reserves be deployed or minting be authorized, where, and up to what capacity? | It is not NAV. |

This is the clean mental model:

```text
Reserve Composition
  Base assets:          $20,000
  Solana assets:        $10,000
  Hyperliquid assets:   $10,000
  --------------------------------
  Verified net assets:  $40,000

Supply Composition
  Base a651:             15,000 units
  Solana a651:           12,000 units
  Hyperliquid a651:       8,000 units
  Post Fiat a651:         5,000 units
  --------------------------------
  Valid global supply:   40,000 units

NAV
  $40,000 / 40,000 = $1.00 per a651
```

The two compositions do not need to match. They usually will not.

A portfolio can hold half its backing assets on Base while most users trade the token on Solana. That is not underbacking. It is just a mismatch between **where the assets are held** and **where users prefer to trade the claim**.

The protocol should make that mismatch visible, not try to erase it.

## The reserve packet: where backing lives

The reserve packet describes the asset side of the system. It says what assets exist, where they live, how they were valued, what liabilities offset them, and how each line was verified.

A simplified reserve packet looks like this:

```json
{
  "asset_id": "a651",
  "epoch": 1842,
  "valuation_policy_hash": "0x...",
  "verified_net_assets_usd_e8": 4000000000000,
  "reserve_legs": [
    {
      "leg_id": "base_reserve_001",
      "location": "Base",
      "asset_class": "onchain_cash_or_spot",
      "value_usd_e8": 2000000000000,
      "quantity_evidence": "cryptographic",
      "valuation_evidence": "policy_attested"
    },
    {
      "leg_id": "solana_reserve_001",
      "location": "Solana",
      "asset_class": "onchain_cash_or_spot",
      "value_usd_e8": 1000000000000,
      "quantity_evidence": "attested_or_tee_attested",
      "valuation_evidence": "policy_attested"
    },
    {
      "leg_id": "hyperliquid_spot_001",
      "location": "Hyperliquid",
      "asset_class": "venue_spot",
      "value_usd_e8": 1000000000000,
      "quantity_evidence": "cryptographic_or_attested",
      "valuation_evidence": "cryptographic_or_policy_attested"
    }
  ],
  "liabilities_usd_e8": 0,
  "net_assets_usd_e8": 4000000000000,
  "snapshot_time": 1781395200,
  "expires_at": 1781398800
}
```

This packet is about backing. It is not about which chain has a DEX pool. It is not about how much a651 is trading on Solana. It is not about bridge routes. It is the verified balance sheet of the token.

The invariant is:

```text
verified_net_assets = Σ verified_reserve_legs − verified_liabilities
```

Then the canonical NAV ledger computes:

```text
nav_per_unit = verified_net_assets / valid_global_supply
```

For the proof-of-leverage run, the same pattern applies: spot, cash, gross perpetual notional, and liabilities are separate buckets; evidence quality is disclosed per leg; and the proof does not pretend that every asset has the same verification strength, liquidity, or risk profile.

That is the right schema discipline. Reserve legs are allowed to live on multiple chains and venues. They are not separate pool backings.

## The supply packet: where the claim circulates

The supply packet describes the liability side of the token contract: where valid units exist.

A simplified supply packet looks like this:

```json
{
  "asset_id": "a651",
  "epoch": 1842,
  "valid_global_supply": 4000000000000,
  "representations": [
    {
      "representation_id": "base_a651",
      "location": "Base",
      "token_standard": "ERC20",
      "valid_supply": 1500000000000,
      "status": "active",
      "role": "access"
    },
    {
      "representation_id": "solana_a651",
      "location": "Solana",
      "token_standard": "SPL",
      "valid_supply": 1200000000000,
      "status": "active",
      "role": "access"
    },
    {
      "representation_id": "hyperliquid_a651",
      "location": "Hyperliquid",
      "token_standard": "spot_asset",
      "valid_supply": 800000000000,
      "status": "active",
      "role": "access"
    },
    {
      "representation_id": "post_fiat_native_a651",
      "location": "Post Fiat",
      "token_standard": "native_nav_asset",
      "valid_supply": 500000000000,
      "status": "active",
      "role": "canonical_claim"
    }
  ]
}
```

This packet does not say:

```text
Base a651 is backed by Base reserves.
Solana a651 is backed by Solana reserves.
Hyperliquid a651 is backed by Hyperliquid reserves.
```

It says:

```text
These are valid access forms of the same a651 claim.
Their combined valid supply is the denominator for NAV.
```

The invariant is:

```text
valid_global_supply = Σ valid_supply_across_registered_representations
```

The reserve invariant then uses that global number:

```text
verified_net_assets >= valid_global_supply × nav_per_unit
```

or, for a floating NAV asset:

```text
nav_per_unit = verified_net_assets / valid_global_supply
```

The supply packet is where Post Fiat should be strict. It does not need to analyze every bridge design as a financial asset. It only needs to know whether a representation is inside the valid supply perimeter, how much valid supply exists there, whether that representation is active, and whether mint authorization or market-operation flow through that route is currently allowed.

## The market-operations packet: how NAV alignment is funded

NAV is not the same thing as a standing spot-redemption right.

A holder may own a valid a651 unit with a proven NAV, but that does not mean the protocol should let every holder burn into spot assets at NAV. That would turn a market-price problem into an issuer-liquidity promise and would let the fastest exiters drain the most liquid reserve legs.

Instead, local market support should be explicit, bounded, and policy-driven. A market-operations packet says when a venue is far enough away from NAV to justify action, how much of the alignment reserve may be deployed, and whether any new mint is authorized.

A simplified market-operations packet looks like this:

```json
{
  "asset_id": "a651",
  "epoch": 1842,
  "nav_per_unit_usd_e8": 100000000,
  "observation_window_seconds": 1209600,
  "venues": [
    {
      "venue_id": "ethereum_uniswap_v4_a651_usdc",
      "location": "Ethereum",
      "price_source": "volume_weighted_twap",
      "discount_trigger_bps": -300,
      "premium_trigger_bps": 1000,
      "discount_breach_frequency_bps_14d": 4200,
      "premium_breach_frequency_bps_14d": 0,
      "max_reserve_deploy_bps_of_alignment_reserve": 1800,
      "max_mint_bps_of_valid_supply": 0,
      "status": "discount_support_enabled"
    },
    {
      "venue_id": "base_amm_a651_usdc",
      "location": "Base",
      "price_source": "volume_weighted_twap",
      "discount_trigger_bps": -300,
      "premium_trigger_bps": 1000,
      "discount_breach_frequency_bps_14d": 0,
      "premium_breach_frequency_bps_14d": 2600,
      "max_reserve_deploy_bps_of_alignment_reserve": 0,
      "max_mint_bps_of_valid_supply": 750,
      "status": "premium_mint_enabled"
    }
  ]
}
```

The thresholds are policy parameters. The action sizes are historical. If the Ethereum Uniswap pool trades below NAV more frequently over the last two weeks, the reserve allocation can rise within its cap. If it only flickers below NAV for a few blocks, the allocation should be small or zero.

The same discipline applies above NAV. If a venue trades more than `10%` above NAV for a sustained share of the two-week window, the policy can authorize a capped mint. The cap is not unlimited and it is not a public right to mint at NAV whenever convenient. It is a venue-specific authorization sized from premium persistence, available bid depth, slippage limits, proof freshness, and reserve capacity.

A good status page should therefore show three rows of information:

```text
Backing portfolio:
  Base reserves:              $20,000
  Solana reserves:            $10,000
  Hyperliquid reserves:       $10,000
  Verified net assets:        $40,000

Valid supply:
  Base a651:                  15,000
  Solana a651:                12,000
  Hyperliquid a651:            8,000
  Post Fiat a651:              5,000
  Valid global supply:        40,000

Market operations:
  Ethereum Uniswap discount:  -3% trigger, 42% 14d breach frequency
  Reserve deploy cap:         18% of alignment reserve
  Premium mint trigger:       +10%
  Current mint cap:           0.75% of valid global supply
```

The first table backs the token. The second table counts the valid claims. The third table controls market operations.

Mixing those three tables is the source of confusion.

## The proof is the reserve packet

The L1 NAVCoin rail carries a typed object called a **reserve packet** and enforces one invariant on it in consensus:

```text
verified_net_assets >= circulating_supply × nav_per_unit_floor
```

That equation is the discipline. Supply times the per-unit floor mark must not exceed the verified reserves, or the packet is invalid. For a floating-NAV asset, overcollateralization is allowed; the proven NAV can float up instead of forcing an exact stablecoin-style equality.

For a multi-access a651, the corrected version is:

```text
verified_net_assets >= valid_global_supply × nav_per_unit_floor
```

The denominator is not Base supply. It is not Solana supply. It is not Hyperliquid spot supply. It is the valid supply across the declared perimeter.

On Post Fiat, "verified" means the chain enforces the proof profile for that asset. For ledger-transparent reserves, validators can re-execute the check directly. For external reserve legs, the packet can carry a proof, an attestation, an observation quorum, or another verifier permitted by the profile.

On an EVM verifier path, a651 can use the proof-of-leverage verifier as the reserve packet source. The verifier exposes the public buckets, the policy hash, and the program key. A canonical NAV module reads those values and computes:

```text
verified_net_assets = spot_total + cash_total − liabilities
nav_per_unit        = verified_net_assets / valid_global_supply
```

The proof tells the token what the backing is. The supply packet tells it how many valid claims exist. The market-operations packet tells the protocol when it may deploy reserves or authorize minting by venue.

Those are three separate facts.

## Mint authorization and reserve deployment, once

The protocol should not mint independently on every venue, and it should not offer holder redemption at NAV as the default price tether. Either design would fragment the accounting system into several local ledgers or convert proven NAV into a spot-liquidity promise.

Mint authorization and reserve deployment should be canonical. Access can be local.

### Capped mint authorization

A mint is a policy-scoped authorization, not an always-open public arbitrage button.

The canonical mint checks:

```text
fresh reserve packet
valid proof profile
not halted
not stale
route active
global supply after mint within permitted limit
premium trigger satisfied or primary issuance explicitly approved
mint cap sized from the two-week premium history
sale proceeds or reserve contribution committed to the reserve policy
```

Then the units can be delivered to the approved market-making route: Post Fiat native, Base ERC-20, Solana SPL, Hyperliquid spot, BSC ERC-20, or another approved access form.

A simplified mint flow:

```text
1. Venue trades above the premium trigger, for example more than 10% above NAV.
2. Oracle or observation quorum reports the two-week premium frequency and depth.
3. Canonical ledger checks proof freshness, NAV, route status, and global supply.
4. Canonical ledger computes a capped mint authorization from the historical premium.
5. Market-making executor sells or seeds the approved venue subject to slippage limits.
6. Sale proceeds enter the reserve policy and the new supply enters the next supply packet.
```

The proceeds become part of the reserve policy. They are not the backing of a local pool. Once minted, the new units are valid access forms of the same global portfolio.

### Reserve deployment below NAV

When a venue trades below NAV, the protocol response is not to let holders redeem at spot NAV. The response is to deploy a bounded reserve allocation into the market if the discount is persistent enough.

The canonical reserve deployment checks:

```text
fresh reserve packet
valid proof profile
not halted
not stale
venue representation active
discount trigger satisfied
deployment cap sized from the two-week discount history
alignment reserve capacity available
slippage and venue-depth limits satisfied
```

A simplified reserve-deployment flow:

```text
1. Ethereum Uniswap trades below the configured discount trigger.
2. Oracle or observation quorum reports the two-week discount frequency and market depth.
3. Canonical ledger computes the maximum reserve allocation for that venue.
4. Market-making executor buys a651 in the venue subject to slippage and cooldown rules.
5. Acquired units are held as treasury inventory or retired under policy.
6. The action and remaining alignment reserve are included in the next market-operations packet.
```

The important rule is:

> **A valid unit can be accessed locally, but NAV alignment is handled through bounded market operations, not holder spot redemption.**

That keeps market support from becoming six separate solvency systems.

## Initial issuance

The simplest launch has no pre-mine and no special seed class.

At deployment, valid global supply is zero. The first accepted reserve packet establishes the initial NAV and mint capacity. Policy-approved capital contributions can receive units under the launch terms, and later minting should be governed by explicit issuance or market-alignment authorizations.

If the reserve packet proves `$40,000` of net assets and the chosen initial unit NAV is `$1.00`, the system can support `40,000` units. If the chosen initial unit NAV is `$10.00`, it can support `4,000` units. The unit denomination is arbitrary. The invariant is not:

```text
minted_supply × nav_per_unit <= verified_net_assets
```

or, once multiple access venues exist:

```text
valid_global_supply × nav_per_unit <= verified_net_assets
```

The first buyers can receive units on Base, Solana, Hyperliquid, Post Fiat, or another approved representation. That access choice does not change what backs them.

This removes the founder-upside ambiguity. Early capital can still be rewarded, but only through explicitly disclosed terms: a management fee, performance fee, liquidity-mining program, time-locked reserve contribution, or other policy-bound economic right. It should not be hidden inside a near-zero founder mint.

## Funding and privacy

Funding privacy is an access question, not a NAV question.

Some buyers do not want a public funding transaction to reveal their position size or cap-table relationship. That does not require the canonical NAV ledger to become private. The ledger only needs to verify that valid consideration was received, that the mint complied with the proof profile, and that the resulting supply entered the valid perimeter.

Privacy can live at the route layer:

```text
private funding route
  ↓
policy-approved deposit
  ↓
canonical mint authorization
  ↓
access representation selected by buyer
```

The privacy route is not the backing. It is a way to arrive.

Likewise, a buyer who funds through an EVM privacy rail may choose to hold a651 on an EVM representation. A trader on Solana may prefer SPL access. A Hyperliquid trader may prefer order-book access. These are distribution and settlement choices. The NAV ledger does not need to encode them as separate reserve claims.

## Where liquidity should live

Liquidity should live wherever the buyers are. Truth should live where it is enforced.

That gives the following architecture:

| Layer | Role |
|---|---|
| Canonical NAV ledger | Verifies reserve packets, computes NAV, gates mint authorizations and reserve deployments, tracks valid global supply, halts stale proofs |
| Reserve composition | Discloses where backing assets live and how each leg was verified |
| Supply composition | Discloses where valid a651 units exist |
| Market operations policy | Discloses venue triggers, reserve-deployment caps, mint caps, and cooldowns |
| Base representation | EVM access and AMM liquidity |
| Solana representation | Solana access and DEX liquidity |
| Hyperliquid spot representation | Trader-native order-book access |
| BSC representation | EVM retail access and AMM liquidity |
| Arbitrum representation | Short path to existing EVM proof and privacy tooling |
| Post Fiat native representation | Canonical NAV accounting and policy rail |

Notice what is missing from the table: pool-level backing.

A Base pool is not backed by Base assets. A Solana pool is not backed by Solana assets. Hyperliquid spot is not backed by Hyperliquid assets. Each venue is an access surface for the same token.

The status panel for each venue should therefore look like this:

```text
Venue:                    Base
Representation:           Base ERC-20 a651
Valid venue supply:        15,000 a651
Local pool depth:          $8,500
Local price:               $0.995
Global NAV:                $1.000
Premium/discount:          -0.50%
Market-ops status:         active
Discount trigger:          -3.00%
14d below-NAV frequency:   0.00%
Reserve deploy cap:        $0
Premium mint cap:          0.00% of valid global supply
```

The status panel should not say:

```text
Base backing:              $20,000
Base supply:               15,000
Base coverage:             133%
```

That is the wrong denominator. It implies a local claim on local assets. a651 is a global claim on the full verified portfolio.

## Market venues and the NAV tether

a651 can trade on an AMM, a Solana DEX, Hyperliquid spot, an RFQ desk, or Post Fiat's native book. Each venue will have its own local price. The protocol's job is to keep those prices tethered to the canonical NAV.

The tether comes from two policy-bound actions:

```text
below NAV: deploy alignment reserves into the venue
above NAV: authorize capped minting into the venue
```

Neither action is a blanket promise that holders can redeem at NAV.

### Discount

If a651 trades below proven NAV on a venue, the policy can deploy reserve liquidity into that venue. The discount threshold is set in the market-operations policy; the deployment size is computed from the historical pattern of the discount.

For example, if the Ethereum Uniswap pool trades more than `3%` below NAV, the protocol checks how often and how deeply that pool traded below NAV over the last two weeks. A frequent, liquid, persistent discount can receive a larger reserve allocation. A short, thin, or easily manipulated discount should receive little or none.

That action is strongest when:

```text
the proof is fresh
the representation is valid
the market observation is fresh
the two-week breach history clears the policy threshold
the alignment reserve has capacity
venue depth supports the intended order size
slippage and cooldown limits are satisfied
```

If the alignment reserve is small, the discount may persist. The protocol should show that plainly. It should not pretend every dollar of NAV is same-block cash.

### Premium

If a651 trades above proven NAV on a venue, the policy can authorize a capped mint into that venue. A simple default is: no premium mint unless the venue trades more than `10%` above NAV. The amount is then sized from the historical premium frequency, observed bid depth, slippage, and global reserve capacity.

That action is strongest when:

```text
the proof is fresh
the premium trigger is satisfied
the two-week premium history clears the policy threshold
minting remains inside the verified-capacity invariant
the target venue has bid depth
the executor can sell or seed liquidity without excess slippage
```

Again, the relevant constraint is policy authorization, venue evidence, and global supply capacity, not local backing.

The price display should therefore be global NAV versus local market price:

```text
Global NAV:          $1.000
Base price:          $0.995
Solana price:        $1.006
Hyperliquid price:   $1.002
```

Each premium or discount is local. NAV is singular.

## NAV Alignment Reserve

a651 can add a bounded **NAV Alignment Reserve**: deployable liquidity used to reduce persistent deviations between local market prices and canonical NAV.

This reserve is not the backing portfolio. It is market-structure liquidity.

The contract or policy watches:

```text
deviation = (venue_price − nav_per_unit) / nav_per_unit
breach_frequency_14d = time_or_volume_weighted_share_of_window_outside_band
breach_severity_14d = average_excess_deviation_when_outside_band
```

If NAV is `$1.00` and a651 trades at `$1.08`, nothing automatic needs to happen. If it trades above the configured premium trigger, such as `+10%`, for enough of the two-week observation window, the policy may authorize a capped mint and sell or seed the rich venue, subject to route limits and slippage rules.

If NAV is `$1.00` and a651 trades at `$0.92`, the reserve may buy a651 in the market. The acquired units can be held as treasury inventory or retired under policy. The seller exits at the market price; the protocol is not offering them a NAV redemption.

The action sizes can be computed mechanically:

```text
reserve_deploy_cap =
  min(
    route_reserve_cap,
    alignment_reserve × discount_response_curve(breach_frequency_14d, breach_severity_14d)
  )

mint_authorization_cap =
  min(
    policy_mint_cap,
    valid_global_supply × premium_response_curve(premium_frequency_14d, premium_severity_14d),
    verified_capacity_remaining
  )
```

The target reserve can be computed mechanically:

```text
target_alignment_reserve =
  coverage_multiplier × trailing_alignment_need
  + volatility_buffer × valid_global_supply × nav_per_unit
```

`trailing_alignment_need` is the capital actually required to bring prior breaches back inside the band. The coverage multiplier says how many repeats the reserve should withstand. The volatility buffer scales with observed market volatility.

A live status panel should distinguish NAV backing from alignment liquidity:

| Field | Example |
|---|---:|
| Verified net assets | `$40,000` |
| Valid global supply | `40,000 a651` |
| NAV per unit | `$1.00` |
| Venue price | `$0.92` |
| Deviation | `-8.0%` |
| Allowed band | `±3%` |
| 14d below-NAV frequency | `42%` |
| Alignment reserve | `$6,000` |
| Target alignment reserve | `$8,000` |
| Current reserve deploy cap | `$1,080` |
| Current mint authorization cap | `0 a651` |
| Status | `active alignment event; reserve below target` |

The alignment reserve helps tether market prices. It should never be described as the asset backing of a particular liquidity pool.

## What PFTL should record

The Post Fiat ledger should record the facts needed to enforce NAV, not every mechanism by which a user might move between venues.

The minimum object set is:

```text
1. ReserveComposition
   The backing assets and liabilities.

2. SupplyComposition
   The valid token representations and their observed supply.

3. VenueMarketState
   The venue price, depth, deviation, and rolling breach history.

4. MarketOperationPolicy
   The discount triggers, premium triggers, reserve-deployment caps, mint caps,
   slippage limits, and cooldowns.

5. NAVStatus
   The computed NAV, proof freshness, halt state, and operation availability.
```

A compact schema:

```solidity
struct ReserveLeg {
    bytes32 legId;
    bytes32 location;              // BASE, SOLANA, HYPERLIQUID, etc.
    bytes32 assetClass;            // cash, spot, staking, margin, liability
    int256 valueUsdE8;             // liabilities can be negative
    bytes32 quantityEvidenceTier;
    bytes32 valuationEvidenceTier;
    bytes32 evidenceCommitment;
}

struct ReserveComposition {
    bytes32 assetId;
    uint64 epoch;
    bytes32 valuationPolicyHash;
    int256 netAssetsUsdE8;
    ReserveLeg[] legs;
    uint64 snapshotTime;
    uint64 expiresAt;
}

struct SupplyRepresentation {
    bytes32 representationId;
    bytes32 location;              // BASE, SOLANA, HYPERLIQUID, POST_FIAT
    bytes32 tokenStandard;         // ERC20, SPL, spot_asset, native
    uint256 validSupply;
    bytes32 status;                // active, paused, quarantined
}

struct SupplyComposition {
    bytes32 assetId;
    uint64 epoch;
    uint256 validGlobalSupply;
    SupplyRepresentation[] representations;
}

struct VenueMarketState {
    bytes32 venueId;
    bytes32 location;
    bytes32 priceSource;             // twap, vwap, oracle_quorum
    int256 deviationBps;             // (venue_price - NAV) / NAV
    uint256 depthUsdE8;
    uint256 discountBreachFrequencyBps14d;
    uint256 premiumBreachFrequencyBps14d;
    uint64 lastObservedAt;
    bytes32 status;
}

struct MarketOperationPolicy {
    bytes32 assetId;
    uint64 epoch;
    uint64 observationWindowSeconds;  // e.g. two weeks
    int256 discountTriggerBps;        // e.g. -300
    int256 premiumTriggerBps;         // e.g. +1000
    uint256 maxReserveDeployBps;
    uint256 maxMintBps;
    uint256 slippageLimitBps;
    uint64 cooldownSeconds;
}
```

The bridge, wrapper, or executor implementation can be outside the article. The accounting layer only needs to know the result:

```text
Is this representation valid?
How much supply exists there?
Is reserve deployment enabled for this venue?
How much reserve can be deployed now?
Is premium minting authorized for this venue?
What is the current mint cap?
What cooldown or slippage limit applies?
```

That is enough for NAV integrity without making bridge design the focus.

## Failure modes and residual risks

The corrected model removes one confusion, but it does not remove risk.

### 1. Reserve-leg failure

A reserve leg can be stale, misvalued, incompletely disclosed, or weaker than advertised. That is a proof-profile problem. The response is stale-proof freeze, challenge, status degradation, or removal of that leg from verified assets under the policy.

This is about backing.

### 2. Supply-perimeter failure

A representation can have more tokens outstanding than the canonical supply packet recognizes. That is not a NAV failure in the reserve portfolio. It is a perimeter failure.

The response is to quarantine the representation, halt minting and reserve deployment on the route, exclude suspect supply from valid global supply until reconciled, and publish the discrepancy.

This is about valid claims.

### 3. Alignment-liquidity failure

A venue can trade below NAV while the alignment reserve is exhausted or the market is too thin to deploy into safely. That does not mean the token is unbacked. It means the market-operation budget is exhausted or constrained.

The response is to degrade the market-operations status, stop advertising support beyond the actual reserve allocation, and wait for fresh policy capacity or reserve replenishment.

This is about market-support capacity.

### 4. Local market-price failure

A venue can trade far from NAV. That does not change NAV. It means local liquidity is insufficient, route capacity is constrained, the alignment reserve is too small, premium minting is capped, or the market distrusts some part of the system.

The response is price display, NAV Alignment Reserve action if policy permits, capped premium minting if policy permits, and clear disclosure of remaining operation capacity.

This is about secondary-market execution.

### 5. Completeness risk

No proof system proves that no undisclosed accounts or liabilities exist. The reserve packet proves the disclosed account set under the proof profile. Completeness remains a legal, governance, attestation, and market-discipline problem.

This is about the limit of proof-of-reserves itself.

## What conforms, and what changes

The design keeps the original NAVCoin discipline:

- a reserve-packet object;
- verified net assets tied mechanically to supply and NAV;
- monotonic epochs;
- proof freshness and deadman freeze;
- halt behavior;
- minting only against verified capacity and explicit policy authorization;
- reserve deployment below NAV only through bounded market operations;
- no standing holder redemption at NAV;
- content-addressed proof-profile parameters;
- per-leg evidence disclosure.

The main change is the accounting model for multiple venues.

The old tempting model was:

```text
Pool A has backing A.
Pool B has backing B.
Pool C has backing C.
```

The corrected model is:

```text
Portfolio has backing.
All valid units share that backing.
Venues are access surfaces.
Local liquidity is execution depth.
Market operations are bounded policy actions.
```

That change adds three explicit disclosures:

1. **Reserve Composition.** Where the backing assets are.

2. **Supply Composition.** Where valid token units are.

3. **Market Operations Policy.** When reserves can be deployed, when minting can be authorized, and how each action is capped.

It also removes one thing from the core article: bridge-risk analysis. A bridge or cross-chain route can be important operationally, but the NAV article does not need to score bridges. It only needs to define whether a given representation is inside the valid supply perimeter and whether that representation is eligible for mint authorization or reserve deployment.

## The assembly

Each piece now has a clean role.

The proof-of-reserves system verifies the portfolio. The canonical NAV ledger computes NAV and enforces mint authorization and reserve deployment. The supply packet counts valid units across access venues. Base, Solana, Hyperliquid, BSC, Arbitrum, Ethereum, and Post Fiat can all host useful access forms. Local pools and order books provide execution. Market-operations packets tell operators and holders which venues are eligible for support, what two-week history triggered the action, and how much capacity remains.

But only one thing backs a651:

> **the verified reserve portfolio.**

And only one thing defines the value of a valid unit:

> **canonical NAV divided by valid global supply.**

That is the architecture.

A holder should be able to read a status page and see:

```text
What backs the token?
Where are valid units circulating?
What is the local market price versus NAV?
Is a venue below the discount trigger?
Is a venue above the premium mint trigger?
How much reserve can be deployed?
How much minting is authorized?
Is the proof fresh?
Is the asset halted?
```

They should never have to ask whether their Base a651 is "Base-backed" or their Solana a651 is "Solana-backed." That is the wrong question.

Every valid a651 unit is the same claim. The portfolio is global. Access is local. Market support is disclosed separately and executed only through policy-bound reserve deployment or capped mint authorization.
