---
title: "NAVCoin Collateralization Without Spot Redemption"
date: 2026-06-17T00:00:00Z
draft: true
summary: "A proposal for proving NAV and enforcing bounded market operations for a floating-NAV token without giving holders a standing spot-redemption right at NAV. PFTL is used as a deterministic replay engine; Ethereum contracts enforce PFTL-finalized envelopes; Uniswap v4 hooks can provide eligible venue evidence and optional fee defenses."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Collateralization
  - PFTL
  - Ethereum
  - Uniswap v4
  - Market Making
  - Proof of Reserves
---

## Executive summary

A NAVCoin should prove its net asset value, disclose its support budget, and enforce market-operation limits. It should not give every holder a standing right to redeem at NAV.

The naive design is tempting:

```text
If a651 trades below NAV, let holders redeem at NAV.
If a651 trades above NAV, let anyone mint at NAV.
```

That design creates a bank-run and arbitrage interface. The fastest exiters get first claim on the most liquid reserves, and every market maker can trade against a deterministic issuer promise.

The better design is:

```text
PFTL proves NAV and computes market-operation envelopes.
Ethereum contracts enforce those envelopes.
Venues provide authenticated market evidence and execution.
Holders do not receive guaranteed spot redemption at NAV.
```

Below NAV, the protocol may deploy a bounded reserve allocation to buy a651 in an eligible venue. Above NAV, it may authorize a capped, escrowed mint into an eligible venue. Both actions are limited by deterministic policy, verified backing, venue history, liquidity depth, cooldowns, price limits, and expiry.

This post is a proposal. A controlled launch can use conservative operator funding, public PFTL status, and small contract limits. A public trustless claim requires more: a public replay bundle, audited deterministic policy code, a specified PFTL finality interface, and an Ethereum bridge that either verifies a succinct proof or provides a permissionless optimistic challenge path. The trustless claim here is narrow: anyone can replay the same inputs, policy program, and parameters and recover the same `MarketOpsEnvelope` hash. PFTL finality and Ethereum bridge enforcement are separate assumptions.

## Definitions and threat model

### Terms

| Term | Meaning |
|---|---|
| NAVCoin | A floating-NAV token whose per-unit value is computed from verified net assets divided by valid global supply. A NAVCoin is not assumed to be redeemable on demand at NAV. |
| a651 | The running example NAVCoin asset in this series. The formulas are not specific to a651. |
| NAV | Net asset value per valid unit, computed from verified net assets and valid global supply. |
| NAV floor | A conservative integer NAV used for caps, status, and mint limits. It is not a redemption price. |
| PFTL | The replay and finality layer used here to verify reserve evidence, supply evidence, venue evidence, and deterministic policy outputs. PFTL should be treated as a replay engine, not as an opaque committee. |
| Reserve packet | A hash-addressed bundle of reserve evidence: asset balances, liabilities, valuation rules, haircuts, venue-credit adjustments, timestamps, and proofs needed to compute verified net assets. |
| Supply packet | A hash-addressed bundle proving valid global supply: minted units, burned units, escrowed units, locked treasury inventory, bridge supply, and exclusions. |
| Evidence root | A commitment to authenticated venue evidence, such as Ethereum headers, receipts, logs, hook checkpoints, and pool state needed for replay. |
| MarketOpsEnvelope | A compact PFTL-finalized authorization packet containing NAV, supply, reserve status, market-operation caps, venue identity, policy hash, validity window, cooldowns, and nonce. Ethereum contracts enforce this packet; they do not reinterpret it. |
| Alignment reserve | Capital set aside for market operations in a venue or venue group. It is separate from portfolio backing. |
| Mint headroom | The remaining ability to issue new valid units without violating the post-mint backing invariant. |

### Design goals

The design targets four properties:

```text
1. Prove NAV from reserve and supply evidence.
2. Avoid a standing holder spot-redemption right at NAV.
3. Bound below-NAV reserve deployment and above-NAV minting.
4. Make policy outputs replayable from authenticated inputs.
```

The design does not target these promises:

```text
no MEV
guaranteed support
guaranteed exit liquidity
stablecoin parity
automatic redemption at NAV
investment return
```

### Threat model

Adversaries may:

```text
front-run and back-run transactions
manipulate spot prices for short windows
move or remove liquidity
route trades through ineligible pools
post stale or false bridge packets
withhold operator funding
rely on congested or censored Ethereum blocks
exploit bugs in hooks, adapters, vaults, or policy code
```

The design should fail closed. If evidence is stale, PFTL halts, a bridge packet is contested, or a venue is not replayable, the safe outcome is:

```text
reserve_deploy_cap = 0
mint_cap = 0
market_operations_status = paused_or_underfunded
```

That is a liveness failure, not hidden insolvency. The market may remain at a discount, but the protocol should not spend reserves or mint supply outside a replayed envelope.

## Architecture overview

The architecture separates NAV computation from local venue execution.

```text
disclosed reserve evidence
        |
        v
PFTL reserve packet verification
        |
        v
PFTL supply packet verification
        |
        v
canonical NAV floor + valid global supply
        |
        v
deterministic market-policy replay over eligible venue evidence
        |
        v
MarketOpsEnvelope(asset, epoch, caps, validity, policy_hash)
        |
        v
PFTL finality + Ethereum bridge boundary
        |
        v
MarketOpsVault + MintController + optional NAVGuardHook
        |
        v
bounded buys below NAV / capped escrowed mints above NAV / receipts
```

PFTL is canonical for NAV and policy outputs. Ethereum is the enforcement surface. Ethereum contracts should not recompute the full reserve proof or a two-week venue history inside each transaction. They should verify or accept a PFTL-finalized envelope through a bridge adapter, then enforce the envelope byte-for-byte.

### Three collateral requirements, not one ratio

"Collateralization" hides three different requirements.

| Requirement | What it protects | Computed by | Enforced by |
|---|---|---|---|
| Backing requirement | NAV is not overclaimed | PFTL reserve and supply replay | PFTL status and MintController |
| Alignment reserve requirement | Market operations have a funded budget | PFTL market-policy replay | MarketOpsVault status and caps |
| Mint headroom | New supply does not outrun verified capacity | PFTL backing and premium policy | MintController escrow and release rules |

These requirements should not be merged. Backing is a solvency question. Alignment reserve is a market-operation budget. Mint headroom is a supply-control question.

### Base invariant

Let:

```text
BPS = 10000
USD_SCALE = 100000000
UNIT_SCALE = 10 ** asset_decimals

verified_net_assets_usd_e8 = integer USD value with 8 decimals
valid_global_supply_atoms = valid supply in token atomic units
nav_floor_usd_e8 = conservative NAV floor in USD-e8 per displayed unit
```

The backing invariant is:

```text
verified_net_assets_usd_e8 * UNIT_SCALE
  >= valid_global_supply_atoms * nav_floor_usd_e8
```

This is not a stablecoin equality. NAV can float. The floor is a conservative value used for mint limits, support caps, and disclosures. It is not a holder redemption promise.

### Controlled launch versus public trustless claim

There are two valid operating modes.

**Controlled launch mode**

PFTL publishes NAV, reserve status, supply status, and required alignment reserve. The operator funds a vault or does not. If funding is missing, PFTL degrades status:

```text
aligned -> underfunded -> support_paused -> mint_paused
```

This mode is useful for launch. It is not trustless market support. Holders can verify that support is underfunded, but they still rely on the operator to fund and execute.

**Contract-enforced mode**

An Ethereum `MarketOpsVault` custodies alignment reserves and accepts only valid `MarketOpsEnvelope` packets. A `MintController` escrows newly minted units and releases them only when proceeds or locked liquidity satisfy policy. Any keeper or solver can execute inside the cap. Nobody can execute outside it.

A public trustless support claim should require contract-enforced mode plus a bridge with a real challenge or proof path. A multisig that can silently change caps is an operational control, not a trustless market-operations layer.

## PFTL replay trustlessness and the bridge boundary

The important PFTL claim is not:

```text
Trust the PFTL committee because it said the cap is X.
```

The claim is:

```text
same input bundle + same policy program + same parameters
  -> same MarketOpsEnvelope
  -> same envelope_hash
```

A third party should be able to reconstruct the envelope without trusting the operator, a website, a data vendor, or an API.

### Replay inputs

A verifier should be able to fetch:

```text
reserve_packet_hash
supply_packet_hash
evidence_root for eligible venue history
policy program identified by program_id
parameter set committed by policy_hash
previous state commitments required by the program
```

Then it should:

```text
verify reserve packet evidence
verify supply packet evidence
verify Ethereum headers, receipts, logs, and hook commitments
run the deterministic policy program
derive the MarketOpsEnvelope
compare its hash to the finalized envelope_hash
```

### Envelope commitment

The envelope hash should commit to every consensus-relevant byte, including encoding version and policy identity.

```text
envelope_hash = H(
  encoding_version,
  chain_id,
  asset_id,
  epoch,
  program_id,
  policy_hash,
  parameter_hash,
  reserve_packet_hash,
  supply_packet_hash,
  evidence_root,
  previous_market_state_hash,
  venue_id,
  pool_config_hash,
  hook_code_hash,
  nav_floor_usd_e8,
  valid_global_supply_atoms,
  verified_net_assets_usd_e8,
  funded_alignment_reserve_usd_e8,
  required_alignment_reserve_usd_e8,
  max_reserve_deploy_usd_e8,
  max_mint_atoms,
  discount_trigger_bps,
  premium_trigger_bps,
  data_window_start,
  data_window_end,
  valid_after,
  expires_at,
  cooldown_seconds,
  nonce
)
```

There should be no semantic defaults hidden outside the hash.

### Determinism rules

The policy program must be deterministic:

```text
no floating point
no local clocks
no randomness
no unordered map iteration
no API calls
no implementation-dependent overflow
fixed rounding direction for every division
fixed input ordering
versioned encodings
committed code hashes for hooks and pool semantics
```

Observations are ordered by:

```text
(chain_id, block_number, transaction_index, log_index)
```

Arithmetic should use checked integer math or explicit `mul_div_floor` and `mul_div_ceil` operations with sufficient intermediate precision.

### What PFTL finality adds

PFTL finality is a separate assumption. It provides an ordered, finalized commitment to the packet and envelope hash. Replayability lets outsiders check whether the finalized output follows the published program.

The minimum assumption is narrow:

```text
PFTL orders the input packet.
PFTL commits to the replay program and policy hash.
PFTL finalizes the envelope hash.
Anyone can replay the same inputs and detect mismatch.
```

This post does not prove PFTL consensus. The system should publish a separate PFTL finality specification before making a public trustless claim.

### What the Ethereum bridge adds

The bridge is another separate boundary. If an Ethereum adapter accepts a forged, stale, or equivocated envelope, the vault can execute a bad cap even when the correct PFTL replay result exists.

The bridge should therefore be designed in two explicit modes.

**Mode A: controlled launch bridge**

This mode is acceptable for launch, but should not be marketed as trustless support.

```text
operator or approved proposer posts PFTL-computed envelope
contracts enforce small caps, expiry, cooldowns, and pauses
public watchers replay every envelope and publish mismatches
any stale, contested, or underfunded state sets caps to zero
operator remains responsible for funding and operational response
```

The controlled bridge is useful because it forces the operational system to behave as if the trustless bridge already exists: envelopes are hash-committed, replay bundles are public, execution is capped, and failures are visible. But the security claim is still controlled launch, not public trustlessness.

**Mode B: public validity-proof bridge**

This is the bridge required before making a public trustless support claim. Ethereum should not trust a PFTL JSON packet or an operator signature. Ethereum should verify a proof about the replay output.

```text
PFTL computes MarketOpsEnvelope
prover generates a succinct proof that:
  reserve packet is valid
  supply packet is valid
  venue evidence is valid
  accepted policy code replayed correctly
  output envelope_hash is correct
Ethereum verifier checks proof against accepted program_vkey
adapter accepts the envelope
vault and MintController execute only inside envelope caps
```

The Solidity-facing acceptance path is:

```text
submitEnvelope(envelope, public_inputs, proof)
  require proof verifies against accepted program_vkey
  require envelope_hash == hash(envelope)
  require public_inputs.envelope_hash == envelope_hash
  require policy_hash is accepted
  require program_id is accepted
  require asset_id, chain_id, adapter, vault, and controller are bound
  require data_window_end is fresh
  require valid_after and expires_at are sane
  store envelope as accepted
```

The proof public inputs should include at least:

```text
asset_id
epoch
chain_id
adapter_address
vault_address
mint_controller_address
program_id
program_vkey
policy_hash
parameter_hash
reserve_packet_hash
supply_packet_hash
evidence_root
previous_market_state_hash
venue_id
pool_config_hash
hook_code_hash
nav_floor_usd_e8
valid_global_supply_atoms
verified_net_assets_usd_e8
funded_alignment_reserve_usd_e8
required_alignment_reserve_usd_e8
max_reserve_deploy_usd_e8
max_mint_atoms
data_window_start
data_window_end
valid_after
expires_at
nonce
envelope_hash
```

An optimistic bridge can be retained as a fallback or controlled-launch path:

```text
1. Proposer posts envelope_hash, envelope fields, input roots, and bond.
2. Packet enters pending state.
3. Permissionless challenge window begins.
4. A valid challenge freezes the packet and sets executable caps to zero.
5. After the delay, an unchallenged packet becomes executable.
6. The packet expires after a short execution window.
```

Core timing rules:

```text
valid_after >= posted_at + challenge_delay_seconds
expires_at <= valid_after + execution_window_seconds
posted_at <= data_window_end + max_staleness_seconds
cap_during_dispute = 0
```

A challenge mechanism that merely alerts an operator is monitoring, not trustless enforcement. For public use, a challenge must either be objectively adjudicated on-chain, reduce to a succinct fraud proof, or cause the disputed envelope never to execute. The rule should be simple:

```text
challenges freeze
proofs authorize
unresolved disputes do not execute
missed support is acceptable
bad support is not acceptable
```

Objective challenge faults should be enumerated in the adapter:

| Fault | Required behavior |
|---|---|
| Wrong `policy_hash` or `program_id` | Reject or freeze envelope |
| Wrong `asset_id`, `chain_id`, adapter, vault, or controller binding | Reject or freeze envelope |
| Stale `data_window_end` | Reject or freeze envelope |
| `valid_after` too early or `expires_at` too late | Reject or freeze envelope |
| Posted fields do not hash to `envelope_hash` | Reject or freeze envelope |
| Public inputs do not match posted envelope | Reject or freeze envelope |
| Invalid proof or finality certificate | Reject or freeze envelope |
| Conflicting PFTL-finalized envelopes for the same asset and epoch | Pause asset until resolved by governed recovery |
| Replay output does not match posted envelope | Reject or freeze envelope; slash or lock proposer bond if bonded |

The long-term preferred path is a succinct proof of replay and finality. The optimistic path is still useful, but high-value public caps should require validity proofs or very small per-envelope caps with long challenge windows and many independent relayers.

### Bridge failure cases

The boundary should be explicit:

```text
Ethereum congestion:
  challenges or executions may be delayed.
  Envelopes should expire quickly.
  Failure mode is missed support, not expanded caps.

Ethereum censorship:
  if challenges cannot be included before valid_after, an optimistic bridge is at risk.
  Public caps should require long challenge windows, multiple relayers, bonds,
  and preferably succinct proofs for high-value envelopes.

Stale packet:
  adapter rejects old epochs, expired envelopes, and data windows beyond max staleness.
  stale_or_contested_packet -> pause.

PFTL halt:
  no new envelopes arrive.
  old envelopes expire.
  market operations pause.

PFTL equivocation:
  two conflicting finalized envelope hashes for the same asset and epoch cause pause.
  the adapter should not let an operator choose the favorable branch.

Bridge or adapter bug:
  this is a contract security failure, not a replay failure.
  caps, audits, formal checks, and staged deployment are required.
```

## Venue evidence and Uniswap v4 realism

There is no magic Uniswap API that makes venue history trustless.

Hosted APIs, subgraphs, dashboards, and market-data vendors are useful for monitoring. They are not collateralization evidence. The trustless evidence is on-chain:

```text
Ethereum block headers
receipts and logs
Uniswap v4 PoolManager state
pool configuration
hook code hash
hook storage checkpoints or emitted commitments
swap and liquidity events
```

Uniswap v4 has no built-in oracle equivalent to the v3 historical observation array. Hooks are optional contracts attached to pools at creation. That matters for NAVCoin eligibility.

A v4 pool should be eligible for automatic trustless support only if the policy commits to:

```text
pool address and PoolManager
pool parameters and fee mode
hook address and hook code hash
observation format
dynamic-fee rules, if any
quote_cost_to_reach_price semantics
state needed for exact replay
gas and storage limits
```

Arbitrary v4 pools are not automatically eligible. They may be useful for dashboards or discretionary margin calls, but they should not produce automatic support or mint caps unless their evidence and execution semantics are committed and replayable.

A NAV-specific hook can help:

```text
NAVGuardHook
  afterSwap:
    emit or checkpoint price, direction, volume, fee, and liquidity observations

  afterAddLiquidity / afterRemoveLiquidity:
    emit or checkpoint depth changes

  beforeSwap:
    optionally reject stale PFTL state or update defensive dynamic fees
```

The hook does not define NAV. PFTL defines NAV from reserve and supply packets. The hook records venue state that PFTL can verify.

Gas and storage costs matter. Ethereum contracts cannot read historical logs directly, and storing every observation in contract storage is expensive. A practical hook should use a bounded ring buffer, periodic commitments, and events that PFTL can replay from receipts. The exact design is an implementation choice, but the policy hash must commit to whatever semantics are used.

`quote_cost_to_reach_price` is also not universal. It must be implemented for the specific eligible pool and route. Concentrated liquidity, dynamic fees, hook side effects, multi-pool routing, and liquidity migration all affect replay. If the route or pool state cannot be replayed exactly, the observation can inform human analysis but should not authorize trustless automatic support.

Concurrent liquidity changes after the PFTL snapshot are handled at execution time, not predicted by replay. The vault must enforce current price limits, minimum received amounts, slippage bounds, and expiry. If the market moves, the execution reverts or fills less.

## Market operations without redemption

The market tether comes from bounded operations, not from a guaranteed NAV exit.

### Below NAV: bounded reserve deployment

When an eligible venue trades below the NAV floor by more than the policy band, PFTL may authorize a reserve-deployment cap. That cap is not a promise to buy.

Bad design:

```text
At block N, buy 1000000 USD of a651 from this pool.
```

Better design:

```text
During this validity window, up to cap_usd_e8 may be deployed
if price, slippage, cooldown, depth, and venue checks pass.
```

The vault should buy only below a conservative limit:

```text
max_buy_price_usd_e8 =
  floor(nav_floor_usd_e8 * (BPS - support_discount_bps) / BPS)
```

If a searcher buys first and pushes the price above the limit, the vault buys nothing. If a searcher sells into the vault below the limit, the vault receives discounted units, subject to slippage and depth checks.

Reserve deployment should use response curves, not cliffs. A one-block manipulation should not unlock a large cap. A persistent, liquid, replayed discount can unlock a larger cap, still bounded by funded reserves, venue depth, cooldowns, and policy maximums.

Solvers can compete for execution. The vault should verify settlement outcomes rather than act as an unconstrained trader:

```text
solver proposes route and amounts
vault checks envelope, cap, price limit, minimum received, cooldown, and expiry
successful surplus returns to the vault or is shared by published rule
failed execution reverts
```

Private orderflow may improve execution, but it is not a security assumption. The on-chain invariant is that the vault never accepts execution worse than its envelope.

Dynamic fees can be useful but should not be load-bearing. A v4 hook may charge higher fees for trades that move farther away from the NAV band and lower fees for trades that move toward it. This may tax manipulation, but it is not a proof of manipulation resistance. Hard caps and price limits remain the primary defense.

### Above NAV: capped escrowed minting

Premium markets need the opposite control. If a venue trades far above NAV, the system may authorize a capped mint into that venue. This is not open public minting at NAV.

The rule is:

```text
No newly minted a651 leaves escrow until policy-approved proceeds settle
or policy-approved liquidity is locked.
```

A sale or liquidity action should be atomic or escrowed:

```text
1. Mint into the MintController or vault escrow.
2. Execute only up to max_mint_atoms.
3. Receive at least required proceeds under policy.
4. Verify post-mint backing.
5. Release only the sold or liquidity-locked amount.
6. Revert otherwise.
```

If proceeds are not settled, they do not count as verified net assets. If units remain escrowed and non-transferable, they should not count as valid circulating supply until the supply packet classifies them according to policy.

Premium minting should be less aggressive than below-NAV support. Buying discounted supply uses existing capital and can reduce circulating supply. Minting creates new supply and should require stronger evidence of a persistent premium, available bid depth, fresh proofs, and settlement.

### Treasury inventory is not a reserve asset

When the vault buys a651, the acquired units should be:

```text
burned
or locked as treasury inventory excluded from valid global supply
```

They should not be counted as reserve assets. Counting self-issued tokens as backing for themselves is circular and becomes most dangerous in stress.

The clean accounting rule is:

```text
locked treasury a651 has zero reserve value
locked treasury a651 is excluded from valid global supply
burned a651 is removed from supply
```

## Deterministic policy formulas

The formulas below are a bootstrap policy, not a claim of optimal calibration. They are included to make the proposal concrete and replayable. Production parameters should be derived from a replay bundle, historical backtest, gas analysis, liquidity-stress simulation, and adversarial execution tests.

All protocol math is integer fixed-point math.

```text
BPS = 10000
USD_SCALE = 100000000
UNIT_SCALE = 10 ** asset_decimals
WEIGHT_DENOM = 100
```

Use explicit rounding:

```text
mul_div_floor(x, y, z) = floor(x * y / z)
mul_div_ceil(x, y, z) = ceil(x * y / z)
```

If an intermediate product overflows the specified arithmetic domain, replay fails and the packet is invalid.

### 1. Backing floor and mint capacity

Inputs:

```text
V = verified_net_assets_usd_e8
S = valid_global_supply_atoms
floor_factor_bps <= BPS
```

NAV and floor:

```text
nav_per_unit_usd_e8 =
  floor(V * UNIT_SCALE / S)

nav_floor_usd_e8 =
  floor(nav_per_unit_usd_e8 * floor_factor_bps / BPS)
```

The backing invariant:

```text
V * UNIT_SCALE >= S * nav_floor_usd_e8
```

Remaining verified capacity:

```text
backing_required_usd_e8 =
  floor(S * nav_floor_usd_e8 / UNIT_SCALE)

verified_capacity_remaining_usd_e8 =
  max(0, V - backing_required_usd_e8)

verified_capacity_remaining_atoms =
  floor(verified_capacity_remaining_usd_e8 * UNIT_SCALE / nav_floor_usd_e8)
```

Minting must satisfy the post-mint invariant:

```text
verified_net_assets_after_usd_e8 * UNIT_SCALE
  >= valid_global_supply_after_atoms * nav_floor_usd_e8
```

Only settled, policy-approved proceeds count in `verified_net_assets_after_usd_e8`.

### 2. Alignment reserve requirement

For an eligible venue, define the discount boundary:

```text
B_minus =
  floor(nav_floor_usd_e8 * (BPS - discount_trigger_bps) / BPS)
```

For each breached observation, replay the venue math and compute the cost to restore the venue to the policy band without violating slippage limits:

```text
cost_to_restore_i_usd_e8 =
  quote_cost_to_reach_price(
    pool_state_i,
    target_price_usd_e8 = B_minus,
    slippage_limit_bps,
    pool_config_hash,
    hook_code_hash
  )
```

If this quote cannot be replayed exactly for the committed venue semantics, the observation is not eligible for automatic support.

Use deterministic percentiles:

```text
pct_bps(values, q_bps):
  sorted_values = sort_ascending(values)
  index = ceil(q_bps * len(sorted_values) / BPS) - 1
  return sorted_values[index]
```

If the eligible value set is empty, the policy should use a conservative default or set automatic caps to zero.

Let:

```text
portfolio_floor_value_usd_e8 =
  floor(valid_global_supply_atoms * nav_floor_usd_e8 / UNIT_SCALE)

minimum_alignment_reserve_usd_e8 =
  max(
    policy_min_usd_e8,
    floor(portfolio_floor_value_usd_e8 * min_alignment_bps / BPS)
  )

stress_support_need_14d_usd_e8 =
  stress_repeat_factor_14d * pct_bps(cost_to_restore_14d, 9900)

stress_support_need_90d_usd_e8 =
  stress_repeat_factor_90d * pct_bps(cost_to_restore_90d, 9500)

latency_buffer_usd_e8 =
  stale_epochs_allowed * pct_bps(cost_to_restore_14d, 9500)

raw_required_alignment_reserve_usd_e8 =
  max(
    minimum_alignment_reserve_usd_e8,
    stress_support_need_14d_usd_e8,
    stress_support_need_90d_usd_e8,
    latency_buffer_usd_e8
  )
```

The requirement should not collapse immediately after a calm window:

```text
if raw_required_alignment_reserve_usd_e8 >= previous_required_alignment_reserve_usd_e8:
  required_alignment_reserve_next_usd_e8 =
    raw_required_alignment_reserve_usd_e8
else:
  required_alignment_reserve_next_usd_e8 =
    max(
      raw_required_alignment_reserve_usd_e8,
      floor(
        previous_required_alignment_reserve_usd_e8
        * (BPS - max_decay_per_epoch_bps)
        / BPS
      )
    )
```

### 3. Reserve-deployment cap below NAV

For an observation window of length `W` seconds:

```text
dt_i = seconds covered by observation i
p_i_usd_e8 = venue price during observation i
vol_i_usd_e8 = venue volume during observation i
```

Discount metrics:

```text
discount_time_seconds =
  sum(dt_i where p_i_usd_e8 < B_minus)

discount_frequency_time_bps =
  floor(BPS * discount_time_seconds / W)

discount_frequency_volume_bps =
  floor(
    BPS * sum(vol_i_usd_e8 where p_i_usd_e8 < B_minus)
    / max(1, sum(vol_i_usd_e8))
  )

discount_excess_i_bps =
  max(0, floor((B_minus - p_i_usd_e8) * BPS / nav_floor_usd_e8))

discount_severity_bps =
  floor(
    sum(dt_i * discount_excess_i_bps where p_i_usd_e8 < B_minus)
    / max(1, discount_time_seconds)
  )
```

Response curve:

```text
discount_response_bps =
  min(
    max_discount_response_bps,
    floor(
      (
        discount_time_weight * discount_frequency_time_bps
        + discount_volume_weight * discount_frequency_volume_bps
        + discount_severity_weight * discount_severity_bps
      )
      / WEIGHT_DENOM
    )
  )
```

A conservative bootstrap parameter set might use:

```text
discount_time_weight = 25
discount_volume_weight = 15
discount_severity_weight = 150
max_discount_response_bps = 2500
```

The depth cap comes from exact venue replay at the latest eligible state:

```text
depth_limited_cap_usd_e8 =
  quote_cost_to_reach_price(
    pool_state_latest,
    target_price_usd_e8 = B_minus,
    slippage_limit_bps,
    pool_config_hash,
    hook_code_hash
  )
```

Final reserve-deployment cap:

```text
response_cap_usd_e8 =
  floor(funded_alignment_reserve_usd_e8 * discount_response_bps / BPS)

reserve_deploy_cap_usd_e8 =
  min(
    available_alignment_reserve_usd_e8,
    venue_policy_cap_usd_e8,
    response_cap_usd_e8,
    depth_limited_cap_usd_e8,
    cooldown_limited_cap_usd_e8
  )
```

This is a maximum authorization, not a trade schedule.

### 4. Mint cap above NAV

Define the premium boundary:

```text
B_plus =
  floor(nav_floor_usd_e8 * (BPS + premium_trigger_bps) / BPS)
```

Premium metrics:

```text
premium_time_seconds =
  sum(dt_i where p_i_usd_e8 > B_plus)

premium_frequency_time_bps =
  floor(BPS * premium_time_seconds / W)

premium_frequency_volume_bps =
  floor(
    BPS * sum(vol_i_usd_e8 where p_i_usd_e8 > B_plus)
    / max(1, sum(vol_i_usd_e8))
  )

premium_excess_i_bps =
  max(0, floor((p_i_usd_e8 - B_plus) * BPS / nav_floor_usd_e8))

premium_severity_bps =
  floor(
    sum(dt_i * premium_excess_i_bps where p_i_usd_e8 > B_plus)
    / max(1, premium_time_seconds)
  )
```

Response curve:

```text
premium_response_bps =
  min(
    max_premium_response_bps,
    floor(
      (
        premium_time_weight * premium_frequency_time_bps
        + premium_volume_weight * premium_frequency_volume_bps
        + premium_severity_weight * premium_severity_bps
      )
      / WEIGHT_DENOM
    )
  )
```

A conservative bootstrap parameter set might use:

```text
premium_time_weight = 2
premium_volume_weight = 1
premium_severity_weight = 10
max_premium_response_bps = 1500
premium_trigger_bps = 1000
```

Mint cap:

```text
market_response_mint_atoms =
  floor(valid_global_supply_atoms * premium_response_bps / BPS)

mint_cap_atoms =
  min(
    policy_max_mint_atoms,
    verified_capacity_remaining_atoms,
    market_response_mint_atoms,
    venue_bid_depth_atoms,
    cooldown_mint_atoms
  )
```

The mint cap is zero unless all required conditions hold:

```text
reserve proof fresh
supply proof fresh
PFTL finality fresh
bridge packet uncontested
venue observations fresh
minimum history available
premium trigger satisfied
post-mint backing invariant holds
proceeds settle atomically or units remain escrowed
```

### Bootstrap parameters and calibration

The weights above are not constants of nature. They are a bootstrap policy. They encode three conservative choices:

```text
below-NAV support is more available than above-NAV minting
time persistence matters more than a single spot print
severity matters, but max_response_bps prevents unbounded caps
```

Real calibration requires a replay bundle and backtest:

```text
historical reserve packets
historical supply packets
eligible Ethereum log and receipt bundles
hook and pool code hashes
gas and storage measurements
liquidity migration scenarios
front-running and sandwich simulations
stress windows beyond the current two-week sample
```

Policy changes should be governed like code:

```text
publish new program_id and policy_hash
publish replay bundle and expected envelope hashes
run challenge window
ensure old and new envelopes overlap only in the conservative direction
activate new policy hash in the adapter and vault
```

The trustless claim is not that a parameter set is optimal. It is that the active parameter set is public, deterministic, replayable, and enforced.

## Nominal example

This example is illustrative only. It is not a real a651 calibration. Displayed dollars and whole a651 units are used for readability; implementation uses USD-e8 and token atoms.

Assume:

```text
nav_floor = $5.00
valid_global_supply = 1000000 a651
verified_net_assets = $5200000
funded_alignment_reserve = $150000

discount_trigger_bps = 300
premium_trigger_bps = 1000
min_alignment_bps = 100

policy_min_alignment_reserve = $25000
stress_repeat_factor_14d = 3
stress_repeat_factor_90d = 2
stale_epochs_allowed = 1
```

Backing floor:

```text
backing_required = 1000000 * $5.00 = $5000000

verified_capacity_remaining =
  $5200000 - $5000000 = $200000

verified_capacity_remaining_units =
  floor($200000 / $5.00) = 40000 a651
```

Replay of eligible venue history produces:

```text
discount_frequency_time_bps = 4200
discount_frequency_volume_bps = 2500
discount_severity_bps = 200

pct_bps(cost_to_restore_14d, 9900) = $45000
pct_bps(cost_to_restore_90d, 9500) = $60000
pct_bps(cost_to_restore_14d, 9500) = $45000
```

Required alignment reserve:

```text
minimum_alignment_reserve =
  max($25000, floor($5000000 * 100 / 10000))
  = $50000

stress_support_need_14d =
  3 * $45000 = $135000

stress_support_need_90d =
  2 * $60000 = $120000

latency_buffer =
  1 * $45000 = $45000

required_alignment_reserve =
  max($50000, $135000, $120000, $45000)
  = $135000
```

With `$150000` funded, market operations remain enabled.

Discount response using bootstrap weights:

```text
discount_response_bps =
  min(
    2500,
    floor((25 * 4200 + 15 * 2500 + 150 * 200) / 100)
  )

discount_response_bps =
  min(2500, floor((105000 + 37500 + 30000) / 100))
  = 1725
```

Assume latest venue replay and cooldown limits are:

```text
available_alignment_reserve = $150000
venue_policy_cap = $50000
depth_limited_cap = $30000
cooldown_limited_cap = $40000
```

Then:

```text
response_cap =
  floor($150000 * 1725 / 10000)
  = $25875

reserve_deploy_cap =
  min($150000, $50000, $25875, $30000, $40000)
  = $25875
```

That `$25875` is not a scheduled trade. It is the maximum the vault may deploy under that envelope.

For a separate premium scenario, assume:

```text
premium_frequency_time_bps = 1800
premium_frequency_volume_bps = 2200
premium_severity_bps = 250

venue_bid_depth_units = 12000
policy_max_mint_units = 50000
cooldown_mint_units = 10000
verified_capacity_remaining_units = 40000
```

Premium response:

```text
premium_response_bps =
  min(
    1500,
    floor((2 * 1800 + 1 * 2200 + 10 * 250) / 100)
  )

premium_response_bps =
  min(1500, floor((3600 + 2200 + 2500) / 100))
  = 83
```

Mint cap:

```text
market_response_mint_units =
  floor(1000000 * 83 / 10000)
  = 8300

mint_cap_units =
  min(50000, 40000, 8300, 12000, 10000)
  = 8300 a651
```

Those 8300 units still cannot leave escrow unless the approved sale or liquidity action settles and the post-mint backing invariant holds.

## Contract and primitive set

### MarketOpsEnvelope

A Solidity-facing envelope can be shaped like this:

```solidity
struct MarketOpsEnvelope {
    bytes32 assetId;
    uint64 epoch;

    bytes32 programId;
    bytes32 policyHash;
    bytes32 reservePacketHash;
    bytes32 supplyPacketHash;
    bytes32 evidenceRoot;

    bytes32 venueId;
    bytes32 poolConfigHash;
    bytes32 hookCodeHash;

    uint256 navFloorUsdE8;
    uint256 validGlobalSupplyAtoms;
    uint256 verifiedNetAssetsUsdE8;

    uint256 fundedAlignmentReserveUsdE8;
    uint256 requiredAlignmentReserveUsdE8;

    uint256 maxReserveDeployUsdE8;
    uint256 maxMintAtoms;

    uint32 discountTriggerBps;
    uint32 premiumTriggerBps;

    uint64 dataWindowStart;
    uint64 dataWindowEnd;
    uint64 validAfter;
    uint64 expiresAt;
    uint64 cooldownSeconds;

    bytes32 nonce;
}
```

The adapter should bind the envelope to chain ID, adapter address, vault address, encoding version, and accepted policy hash when computing the accepted hash.

### PFTLBridgeAdapter

Responsibilities:

```text
accept PFTL-finalized envelope commitments
verify finality proof, validator certificate, succinct proof, or optimistic challenge outcome
store pending and accepted envelopes
reject stale epochs and expired windows
reject wrong policy_hash or program_id
pause on equivocation or contested packets
expose accepted envelope fields to vaults, hooks, and controllers
```

For controlled launches, the adapter may initially rely on conservative caps and operator-run watchers. That should be disclosed as controlled mode, not public trustless mode.

### PolicyRegistry

Responsibilities:

```text
store accepted program_id and policy_hash values
store eligible venue identifiers
store pool_config_hash and hook_code_hash commitments
define activation and deactivation epochs
prevent silent parameter changes
```

### NAVGuardHook

Responsibilities:

```text
record or emit swap observations
record or emit liquidity-depth changes
checkpoint observation commitments
optionally update defensive dynamic fees
optionally reject swaps when accepted PFTL state is stale
```

The hook is not a NAV oracle, reserve vault, or mint authority.

### MarketOpsVault

Responsibilities:

```text
custody venue-specific alignment reserves
execute only inside accepted envelope caps
enforce price limits
enforce minimum received amounts
enforce slippage limits
enforce cooldowns and expiry
lock or burn acquired a651
emit execution receipts for PFTL reconciliation
```

### MintController

Responsibilities:

```text
read accepted envelope
mint only up to maxMintAtoms
escrow newly minted units
release units only against settled proceeds or locked liquidity
enforce post-mint backing checks
emit supply receipts for the next supply packet
```

### SolverRouter

Responsibilities:

```text
accept solver-proposed execution
route through approved venues
verify delivered outcome
return surplus to the vault or split by published rule
revert failed execution
```

Solver surplus rules may improve execution quality. They are not a solvency assumption.

### Packet lifecycle

```text
Observation:
  NAVGuardHook emits or checkpoints venue data.
  PFTL verifies Ethereum headers, receipts, logs, and hook commitments.

Calibration:
  PFTL verifies reserve and supply packets.
  PFTL runs the deterministic market policy.
  PFTL outputs MarketOpsEnvelope and envelope_hash.

Bridge:
  envelope is posted to Ethereum.
  challenge or proof process completes.
  adapter accepts or rejects the envelope.

Funding:
  if alignment reserve is short, PFTL publishes a margin call.
  operator funds the vault or status degrades.

Execution:
  solver submits a transaction against the accepted envelope.
  vault checks cap, price, slippage, cooldown, nonce, and expiry.
  transaction settles or reverts.

Reconciliation:
  execution receipts return to PFTL.
  PFTL updates supply, treasury inventory, burns, and reserve status.
```

## Failure modes and required behavior

| Failure mode | Safe behavior |
|---|---|
| Operator does not fund the alignment reserve | NAV remains published if reserve proof is fresh. `market_ops_status = underfunded`, `reserve_deploy_cap = 0`, and minting pauses if policy requires. |
| Reserve or supply evidence is stale | Apply haircuts or mark status stale. Do not increase caps from stale evidence. |
| Venue history is missing or unreplayable | Venue is ineligible for automatic caps. It may inform manual analysis but not trustless support. |
| PFTL halts | Existing envelopes expire. No new reserve deployment or mint authorization. |
| PFTL equivocates | Adapter pauses on conflicting finalized hashes for the same asset and epoch. No operator branch selection. |
| Bridge proposer posts a wrong envelope | Permissionless challenge freezes it. If challenge cannot be objectively resolved, the envelope never executes. |
| Ethereum congestion delays execution | Envelope may expire. Missed support is acceptable; spending outside the cap is not. |
| Ethereum censorship prevents challenges | Optimistic bridge security is weakened. High-value public caps should require long challenge windows, many relayers, small per-envelope caps, or succinct proofs. |
| Packet is stale but otherwise valid | Adapter rejects by epoch, expiry, or `data_window_end + max_staleness_seconds`. |
| Liquidity migrates after calibration | Current execution checks handle price and slippage. If depth is gone, execution reverts or fills less. |
| Searcher front-runs upward | Vault hits price limit and buys nothing or less. Searcher bears mark-up risk. |
| Searcher pushes price downward | Vault may buy cheaper, bounded by slippage, depth, and cap. |
| Dynamic fee rule is gameable | Hard caps, minimum received, and price limits still bound loss. Dynamic fees are optional defense, not a sole security layer. |
| Mint proceeds fail to settle | Minted units remain escrowed or transaction reverts. They do not become valid circulating supply. |
| Contract or adapter bug | This is a real security failure. Use staged caps, audits, formal checks, pause paths, and bug bounties before public trustless claims. |

## Cold start

A new venue has no history. It should not receive full automatic support on day one.

Cold-start policy should be conservative:

```text
minimum observation window before automatic reserve deployment
zero automatic premium mint until minimum history is reached
small initial alignment reserve
small per-epoch reserve-deploy cap
manual PFTL-governed primary issuance only
high stale-data penalty
observe-only calibration before enforcement
```

A practical launch sequence:

```text
1. Deploy token, PolicyRegistry, adapter, vault, and MintController.
2. Create the v4 pool with the committed NAVGuardHook.
3. Seed liquidity with disclosed operator capital.
4. Accumulate venue observations.
5. Run PFTL calibration in observe-only mode.
6. Publish replay bundles and expected envelope hashes.
7. Enable small reserve-deployment caps.
8. Enable premium mint caps only after sufficient history and testing.
```

## Disclosure and regulatory boundary

This is a product-design disclosure boundary, not legal advice.

Market operations should not be described as:

```text
a peg
a redemption facility
guaranteed support
guaranteed liquidity
stable value
risk-free yield
investment return
instant exit at NAV
```

Public status should show:

```text
NAV floor
verified net assets
valid global supply
reserve packet freshness
supply packet freshness
funded alignment reserve
required alignment reserve
current reserve-deploy cap
current mint cap
market-operations status
accepted policy_hash
accepted envelope epoch
packet expiry
```

The accurate statement is:

```text
The protocol proves NAV and may execute bounded market operations
under public caps. Holders do not have a standing right to redeem
at NAV, and market operations can pause.
```

That distinction is essential. A floating-NAV portfolio token with disclosed, capped support is different from a stablecoin or issuer liquidity promise.

## Test plan

Before mainnet public trustless claims, the system needs adversarial testing and replay validation.

Minimum test set:

```text
deterministic replay:
  same reserve packet + same supply packet + same venue evidence
  + same program_id + same policy_hash -> same envelope_hash

cross-client replay:
  independent implementations produce identical packet hashes

fixed-point arithmetic:
  rounding, overflow, percentile, and boundary cases match specification

Uniswap v4 replay:
  committed hook and pool semantics replay exactly
  concentrated liquidity and dynamic fees are handled
  ineligible pools produce zero automatic cap

gas and storage:
  hook observation cost is measured
  ring buffers and checkpoints stay within budget
  event replay remains practical for PFTL

oracle manipulation:
  one-block or thin-liquidity price moves do not unlock material caps

sustained discount:
  liquid multi-day discount increases reserve cap only within policy bounds

front-run upward:
  searcher buys before vault and vault reverts or buys less

front-run downward:
  searcher sells below limit and vault receives discounted units within cap

premium mint:
  minted units cannot leave escrow without proceeds or locked liquidity

post-mint backing:
  supply and reserve packets reconcile after mint and settlement

self-reserve accounting:
  treasury a651 has zero reserve value and is excluded or burned

bridge challenge:
  wrong packet is challenged and cannot execute

stale packet:
  expired or stale envelopes are rejected

PFTL halt:
  old envelopes expire and operations pause

PFTL equivocation:
  conflicting finality causes adapter pause

operator non-funding:
  status degrades visibly and caps go to zero
```

The most important empirical artifact is a replay bundle: fixed reserve packets, fixed supply packets, fixed EVM evidence, fixed policy code, and expected `MarketOpsEnvelope` hashes. Parameter choices should be defended by backtests over that bundle, not by intuition.

## Recommendation

The architecture worth building is:

```text
1. PFTL is canonical for NAV, valid supply, and market-policy replay.
2. PFTL outputs a hash-committed MarketOpsEnvelope.
3. Ethereum accepts envelopes only through a specified proof or challenge boundary.
4. a651 launches eligible liquidity in pools with committed hook and pool semantics.
5. Uniswap v4 hooks provide venue evidence and optional fee defenses, not NAV.
6. MarketOpsVault custodies alignment reserves and enforces below-NAV caps.
7. MintController escrows above-NAV mints until proceeds or locked liquidity settle.
8. Treasury a651 is burned or excluded from valid supply with zero reserve value.
9. Funding shortfalls become public status, not hidden discretion.
10. Parameters are treated as versioned policy code and validated by replay.
```

The principle is simple:

> Prove NAV. Disclose support. Enforce caps. Do not promise spot redemption at NAV.

That gives holders a cleaner product. They can see backing, supply, reserve status, market-operation budget, and current caps. They do not have to guess whether a hidden wallet will defend a venue or whether the first exiters will drain liquid reserves.

The portfolio is global. The market venue is local. PFTL computes the canonical envelope. Ethereum enforces bounded action. No holder receives a guaranteed NAV exit.

## References

- [NAVCoin proposal](/blog/navcoin-proposal/)
- [NAVCoin counterparty-risk extension](/blog/navcoin-counterparty-risk/)
- [Proof of leverage example](/blog/proof-of-leverage/)
- [NAVCoin Ethereum access-venue post](/blog/navcoin-ethereum/)
- [Uniswap v4 hooks](https://developers.uniswap.org/docs/protocols/v4/concepts/hooks)
- [Uniswap v4 swap hooks](https://developers.uniswap.org/docs/protocols/v4/guides/hooks/swap-hooks)
- [Uniswap v4 dynamic fees](https://developers.uniswap.org/docs/protocols/v4/concepts/dynamic-fees)
- [Uniswap v3 price oracles and the v4 oracle note](https://developers.uniswap.org/docs/protocols/v3/concepts/price-oracles)
