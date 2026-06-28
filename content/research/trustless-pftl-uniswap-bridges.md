---
title: "Trustless Bridges from PFTL to Uniswap"
date: 2026-06-27T00:00:00Z
url: "/research/trustless-pftl-uniswap-bridges/"
summary: "A research design spec for moving NAVCoin supply between PFTL and an Ethereum Uniswap venue without inventory fronting: burn/lock on one side, verify finality, mint/unlock on the other, then optionally execute through Uniswap."
description: "Design spec for a trustless PFTL-to-Uniswap NAVCoin bridge, including finality proofs, supply invariants, replay protection, failure modes, and staged implementation gates."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - PFTL
  - Bridge
  - Uniswap
  - Ethereum
  - a651
draft: false
---
# Toward Trustless Bridges from PFTL to Uniswap

> **By:** Post Fiat  
> **Date:** June 27, 2026  
> **Scope:** Research design spec  
> **Not:** A deployed bridge, audited implementation, live migration plan, financial recommendation, or claim that the existing Ethereum a651 token/controller can be upgraded in place

This spec uses "trustless bridge" as the target end state: a bridge where the destination chain verifies finalized source-chain receipts through a permissionless finality verifier, either directly or through a sound succinct proof.

Threshold-signed stages are trust-based. Optimistic stages are trust-minimized under watcher and challenge assumptions. Only the direct or succinct finality-verification path deserves the word "trustless" without qualification.

## 1. Executive summary

The research problem is narrow:

> How can PFTL a651 supply move to an Ethereum venue where it can be traded on Uniswap, without Post Fiat fronting inventory and without a bridge operator being able to mint unbacked venue supply?

The target architecture is:

```text
source debit under a declared model
-> finalized source receipt
-> destination verification of finality and receipt inclusion
-> destination credit under the matching model
-> optional Uniswap execution
```

For PFTL-to-Ethereum movement, PFTL remains the canonical accounting and finality layer. Ethereum is a venue layer. Uniswap is an execution venue. The bridge is the verification and accounting boundary between them.

The live a651/USDC pool is not this bridge. The current Ethereum a651 token was launched with its own Ethereum-side proof adapter and a locked controller. That locked controller cannot simply be repointed to a new PFTL bridge minter. A trustless or trust-minimized PFTL-to-Uniswap bridge therefore requires one of three explicit choices:

1. A new bridge-aware wrapped venue token.
2. A wrapper around the existing token, with clear limits.
3. An explicit migration from the existing token to a new bridge-aware representation.

The core safety property is not "a relayer sent a message" or "a Uniswap pool exists." The core safety property is a global supply invariant that accounts for:

- spendable PFTL supply;
- spendable venue supply;
- source-locked backing, if the lock/mint model is used;
- in-flight packets that have debited one side but not yet credited the other;
- expired but refundable packets;
- refunds and terminal settlement events.

A relayer may carry data, pay gas, or improve UX. It must not be part of the accounting oracle. Uniswap may execute swaps. It must not decide whether PFTL finalized a receipt or whether NAVCoin supply is valid.

## 2. Current status: the live a651/USDC pool is not this bridge

The existing Ethereum a651/USDC pool should be treated as a live secondary-market venue and historical launch artifact, not as the trustless bridge described here.

Important boundaries:

| Item | Boundary |
|---|---|
| Current a651/USDC pool | A Uniswap venue for the existing Ethereum a651 token. It does not verify PFTL finality. |
| Current Ethereum a651 token | Controlled by its existing locked controller. It is not assumed to be bridge-mintable by a future PFTL verifier. |
| Current Ethereum proof adapter | Ethereum-side proof path for the current token stack. It is not the PFTL finality verifier specified here. |
| Locked controller | Cannot be repointed to a new bridge minter. No migration path should rely on repointing it. |
| This research spec | A design for future bridge-aware supply movement from PFTL to an Ethereum venue token and optional Uniswap execution. |

"Connect PFTL to Uniswap" can mean two different things:

| Meaning | Status |
|---|---|
| Let users trade the existing Ethereum a651 token in the current pool | Already possible as secondary-market trading, subject to current token controls and liquidity. |
| Move canonical PFTL a651 supply into an Ethereum venue without inventory fronting | Requires bridge-aware mint/burn or lock/mint contracts, a packet format, replay protection, finality verification, and in-flight accounting. |

This spec covers the second meaning.

## 3. Migration choices for current a651

The current locked controller is a hard boundary. The bridge design cannot assume it can be upgraded in place. Any practical path must choose one of the following.

### 3.1 New bridge-aware wrapped venue token

Deploy a new Ethereum ERC-20 representation for PFTL a651, controlled by a bridge-aware controller. This token can be presented as a wrapped venue representation of PFTL a651, but it should not be confused with the existing Ethereum a651 token.

Properties:

- cleanest accounting model;
- bridge controller can mint only after verified PFTL packets;
- bridge controller can burn for Ethereum-to-PFTL return;
- local venue caps can be enforced on chain;
- likely requires a new Uniswap pool or new liquidity arrangement;
- legacy a651 and legacy liquidity must be labeled separately.

This is the preferred protocol design if the goal is clean trustless finality verification.

### 3.2 Wrapper around the existing Ethereum a651 token

A wrapper can accept deposits of the existing Ethereum a651 token and issue a wrapped ERC-20 claim against those deposits.

Properties:

- useful as a compatibility or migration tool;
- can create a new tradable wrapper asset;
- cannot make the locked legacy controller bridge-aware;
- cannot by itself prove PFTL source burns or locks;
- must keep deposited legacy backing separate from bridge-minted supply.

A wrapper is not a trustless PFTL bridge unless it is combined with a separate, explicit accounting design that prevents double counting between legacy deposits and PFTL-verified mints.

### 3.3 Explicit migration

A migration can convert existing Ethereum a651 into a new bridge-aware token under published terms.

A migration plan must define:

- conversion rate;
- migration window;
- treatment of old token holders;
- treatment of old Uniswap LPs;
- whether old tokens are locked, burned, or left as legacy assets;
- how migrated supply is reconciled with PFTL authorized supply;
- whether unclaimed legacy supply remains economically valid;
- legal and governance status of the migration.

No public migration claim should be made until old-token holders, old Uniswap liquidity, new token supply, and NAV policy are reconciled in one published plan.

## 4. Problem statement and design goals

The bridge should move supply, not inventory. In an inventory-fronted design, an operator pays users from treasury balances on one side and later rebalances. That creates operator credit risk and weakens the supply invariant.

The target bridge instead makes the source-chain state transition verifiable on the destination chain.

Design goals:

| Goal | Meaning |
|---|---|
| No inventory fronting | Users are not paid from Post Fiat inventory as the bridge mechanism. |
| One supply perimeter | PFTL supply, registered venue supply, and in-flight claims must fit inside authorized NAVCoin supply. |
| Finality-bound minting | Ethereum venue supply cannot be minted unless the bridge verifies a finalized PFTL receipt or an accepted optimistic packet. |
| Finality-bound PFTL release | PFTL cannot mint or unlock returned supply unless it verifies a finalized Ethereum burn/lock event or an accepted optimistic packet. |
| Explicit in-flight accounting | Source-debited but destination-unsettled amounts are counted until settlement or refund. |
| Replay resistance | Packet identity is domain-separated by version, chain ids, bridge ids, asset id, nonce, destination, action, and source receipt. |
| Deterministic refund path | Expired packets can be refunded only under rules that prevent destination settlement and source refund from both succeeding. |
| Uniswap isolation | Uniswap can execute swaps, but it is not a trust anchor, accounting oracle, NAV oracle, or finality verifier. |
| Public auditability | Anyone should be able to reconstruct the bridge ledger from finalized receipts, consumed packets, refunds, and venue token supply. |

Non-goals:

```text
no MEV
instant finality
guaranteed Uniswap price
guaranteed liquidity
private execution by default
venue solvency guarantees
automatic migration of the existing live a651 token
unqualified trustless claims for threshold-signed stages
```

## 5. PFTL finality and receipt-verification assumptions

A bridge verifier cannot be specified rigorously until PFTL exposes verifier-grade finality and receipt data. This section defines what the bridge must know. It does not claim those artifacts are already deployed.

### 5.1 Required PFTL finality inputs

A PFTL-to-Ethereum verifier must be able to verify or be given a proof of:

| Input | Required content |
|---|---|
| Chain identity | Mainnet/testnet id, fork id if applicable, bridge domain, and protocol version. |
| Finalized header | Height, block hash, parent hash, state root, receipt root, timestamp or slot, application version, and validator-set root. |
| Finality certificate | The consensus proof that the header is final: quorum threshold, aggregate signature or equivalent certificate, signer set, and message being signed. |
| Validator set root | Commitment to the validator set authorized to finalize the header. |
| Validator set transitions | Rules and proofs for moving from one validator set root to the next across epochs. |
| Receipt commitment | The commitment scheme for receipts or events emitted by PFTL modules. |
| Receipt inclusion proof | Merkle, Verkle, or other inclusion proof from a bridge receipt to the finalized receipt root. |
| Canonical serialization | Fixed-width, deterministic encoding of packet fields and receipt fields. |
| Replay domains | Domain separator, chain ids, bridge ids, asset ids, route ids, packet version, and nonce scope. |

Ethereum should not accept:

- mempool observations;
- local RPC observations;
- single-validator statements;
- indexer attestations without a verifier;
- packets that are valid on a different chain, route, bridge, asset, or action domain.

### 5.2 Required PFTL receipt properties

A PFTL bridge receipt must commit to the exact bridge instruction. At minimum it must bind:

- source chain id;
- destination chain id;
- source bridge id;
- destination bridge address or id;
- asset id;
- source asset id;
- destination token;
- amount;
- sender commitment;
- recipient;
- action kind;
- action payload hash;
- nonce;
- source height;
- expiry and refund parameters;
- fee fields;
- packet version and domain.

If any field can be changed after source debit, the packet is not safe.

### 5.3 Required Ethereum inbound assumptions

For Ethereum-to-PFTL returns, PFTL must verify Ethereum events or accepted optimistic claims. A centralized indexer can build a proof, but it must not be the trust anchor.

The PFTL inbound verifier must know:

- Ethereum chain id;
- bridge controller address;
- token address;
- event topic and ABI;
- event nonce;
- event amount and recipient;
- event block hash;
- receipt inclusion proof;
- Ethereum finality policy;
- replay domain.

For a controlled testnet, this can begin as a threshold-signed event packet. For a public trustless claim, PFTL needs either an Ethereum light-client path, a succinct proof path, or an optimistic challenge path with clear assumptions.

### 5.4 Trust labels by verifier type

| Verifier type | Trust label |
|---|---|
| Threshold signer set | Trust-based. Signer compromise can mint or release supply unless caps and pauses stop it. |
| Optimistic verifier | Trust-minimized under watcher, bond, and challenge-window assumptions. Not unqualified trustless. |
| Direct light client | Trustless relative to the source consensus assumptions and verifier correctness. |
| Succinct finality proof | Trustless relative to the source consensus assumptions, proof-system soundness, circuit correctness, and verifier-key governance. |

## 6. Target supply invariant and in-flight accounting

The bridge must account for claims, not only minted tokens. During a bridge transfer, one side may already be debited while the other side has not yet been credited. That in-flight amount is not spendable, but it is still an outstanding claim against authorized supply.

### 6.1 Primary model: burn/mint

For fungible NAVCoin venue movement, this spec uses burn/mint as the primary model.

PFTL-to-Ethereum:

```text
PFTL burns or debits X
-> in-flight claim for X exists
-> Ethereum mints X after verifying the finalized receipt
```

Ethereum-to-PFTL:

```text
Ethereum burns X
-> in-flight return claim for X exists
-> PFTL mints or reissues X after verifying the finalized Ethereum event
```

The global encumbered-supply invariant is:

```text
encumbered_supply(asset) =
  pftl_spendable_supply(asset)
  + sum(venue_spendable_supply(asset, venue))
  + outstanding_bridge_claims(asset)

encumbered_supply(asset) <= authorized_valid_supply(asset)
```

`outstanding_bridge_claims` includes:

- source-burned PFTL-to-Ethereum packets not yet consumed on Ethereum;
- expired PFTL-to-Ethereum packets not yet refunded;
- refund requests still inside a challenge or verification window;
- Ethereum-burned return packets not yet minted or reissued on PFTL;
- any other registered route where one side has been debited and the other side has not reached a terminal credit or refund state.

It excludes:

- packets already consumed and minted on the destination;
- packets already refunded on the source;
- packets rejected before source debit;
- failed destination transactions that reverted without consuming the packet.

### 6.2 Alternative model: lock/mint

Lock/mint can be correct when the source chain must preserve original issuance records.

PFTL-to-Ethereum:

```text
PFTL locks X in bridge backing
-> in-flight claim for X exists
-> Ethereum mints X after verifying the finalized receipt
```

Ethereum-to-PFTL:

```text
Ethereum burns X
-> PFTL unlocks X after verifying the finalized Ethereum event
```

Lock/mint requires two separate checks.

Representation invariant:

```text
pftl_spendable_supply(asset)
+ sum(venue_spendable_supply(asset, venue))
+ outstanding_bridge_claims(asset)
<= authorized_valid_supply(asset)
```

Backing invariant:

```text
pftl_locked_backing(asset, route)
>= venue_spendable_supply(asset, route)
   + lock_backed_settleable_claims(asset, route)
```

The locked backing is not counted as an additional spendable representation. Counting both `pftl_locked_backing` and `venue_spendable_supply` as independent supply would double count the same economic claim.

### 6.3 Packet state machine

For a PFTL-to-Ethereum burn/mint packet:

```text
None
  -> SourceDebited
  -> SettleableInFlight
     -> DestinationConsumed
     -> ExpiredRefundable
        -> SourceRefunded
```

The terminal safety rule is:

```text
not (destination_consumed(packet_hash) && source_refunded(packet_hash))
```

A packet may settle on the destination or refund on the source. It must never do both.

Expiration does not erase accounting. An expired packet remains an outstanding claim until a terminal refund completes. During that period, it still counts in `outstanding_bridge_claims`.

### 6.4 Refund safety

A source refund must not rely only on "PFTL has not seen a destination consume event." Absence of a relayed consume proof is not proof of non-consumption.

A safe refund path must use one of these designs:

| Refund design | Requirement | Trust label |
|---|---|---|
| Verified non-consumption | PFTL verifies Ethereum finality and a storage proof showing `consumed[packet_hash] == false` at a finalized block after the destination deadline. | Trustless if the Ethereum verifier is trustless. |
| Optimistic refund | Refund request opens a challenge window. Anyone can submit a finalized destination consume proof to cancel the refund. | Trust-minimized under watcher assumptions. |
| No public refund | Source debit is final and user must settle on destination. | Simple but poor UX; not recommended for public value. |

For public bridge value, the first or second design is required.

### 6.5 Expiry timing requirement

The deployment must set explicit numeric parameters. The safety property is:

> After a source refund can finalize, no valid destination transaction can still consume the packet, and any destination consume that happened before the deadline has had enough time to be proven or challenged on the source.

A parameterized rule is:

```text
settlement_expiry_height
  >= source_height
     + source_finality_margin
     + relay_window_margin
     + destination_settlement_margin

refund_not_before_height
  >= settlement_expiry_height
     + destination_finality_margin_as_source_heights
     + proof_or_challenge_margin
     + clock_or_height_drift_margin
```

The exact values depend on PFTL block timing, PFTL finality, Ethereum inclusion latency, Ethereum finality policy, and the chosen refund design. They are blocking parameters for any production design.

### 6.6 Numerical accounting example

Assume:

```text
authorized_valid_supply = 1,000,000 atoms
pftl_spendable_supply = 1,000,000 atoms
ethereum_venue_supply = 0 atoms
outstanding_bridge_claims = 0 atoms
```

A user bridges 10,000 atoms from PFTL to Ethereum under burn/mint.

After PFTL source burn:

```text
pftl_spendable_supply = 990,000
ethereum_venue_supply = 0
outstanding_bridge_claims = 10,000

encumbered_supply = 1,000,000
```

After Ethereum verifies the finalized PFTL receipt and mints:

```text
pftl_spendable_supply = 990,000
ethereum_venue_supply = 10,000
outstanding_bridge_claims = 0

encumbered_supply = 1,000,000
```

If the packet expires before Ethereum settlement:

```text
pftl_spendable_supply = 990,000
ethereum_venue_supply = 0
outstanding_bridge_claims = 10,000
```

The 10,000 atoms remain encumbered until refund. After a safe refund completes:

```text
pftl_spendable_supply = 1,000,000
ethereum_venue_supply = 0
outstanding_bridge_claims = 0

encumbered_supply = 1,000,000
```

## 7. NAV and supply accounting

For each NAVCoin asset:

```text
authorized_valid_supply = floor(verified_net_assets / nav_floor)
```

PFTL is responsible for canonical NAV policy and global supply accounting. Ethereum should enforce bridge packets, local caps, and route limits. Ethereum should not independently recompute the full NAV reserve proof for every settlement.

A venue verifier should check:

```text
ethereum_venue_supply <= venue_cap
packet_amount <= route_epoch_limit
packet_asset == registered_asset
packet_destination_token == registered_destination_token
```

PFTL should track or be able to reconstruct:

- PFTL spendable supply;
- PFTL locked backing, if using lock/mint;
- registered venue supply;
- in-flight claims;
- expired refundable claims;
- terminal refunds;
- terminal destination consumes.

If NAV policy reduces future issuance capacity, new bridge-outs can be paused or capped. Existing venue tokens and outstanding claims need a separate policy treatment; the bridge should not silently erase claims to restore a cap.

## 8. Architecture overview

### 8.1 PFTL to Ethereum to Uniswap

```text
PFTL NAVCoin module
        |
        | burn or lock a651 under declared model
        | create bridge packet
        v
PFTL finalized receipt
        |
        | relayer submits packet and proof
        v
Ethereum PFTL verifier
        |
        | verify finality and receipt inclusion
        | or accept after optimistic challenge window
        v
Ethereum bridge controller
        |
        | consume packet
        | mint or unlock venue token
        v
Bridge-aware venue a651 token
        |
        | optional swap adapter
        v
Uniswap venue
```

### 8.2 Ethereum to PFTL

```text
Ethereum bridge-aware venue token
        |
        | burn or lock venue token through bridge controller
        v
Ethereum finalized event
        |
        | relayer submits event proof
        v
PFTL Ethereum-event verifier
        |
        | verify finality and receipt inclusion
        | consume nonce
        v
PFTL NAVCoin module
        |
        | mint, reissue, or unlock canonical a651
        v
PFTL account or shielded note
```

### 8.3 Component responsibilities

On PFTL:

| Component | Responsibility |
|---|---|
| NAVCoin registry | Maps asset ids, chain ids, venue ids, bridge ids, token contracts, caps, route status, and model type. |
| Bridge debit module | Burns or locks source a651, creates packet records, and emits committed bridge receipts. |
| Receipt commitment module | Commits bridge receipts into finalized receipt roots. |
| Supply accounting module | Tracks spendable supply, locked backing, venue supply, outstanding claims, consumes, and refunds. |
| Ethereum event verifier | Verifies Ethereum burn/lock events or accepted optimistic claims for inbound returns. |
| Refund module | Handles expired packets using verified non-consumption or optimistic challenge rules. |
| Pause and route control | Pauses routes or caps bridge-out when verifier, NAV, or accounting assumptions are invalid. |

On Ethereum:

| Component | Responsibility |
|---|---|
| PFTLFinalityVerifier | Verifies PFTL headers, finality certificates, validator set transitions, and receipt inclusion, or manages optimistic acceptance. |
| VenueNavCoin | Bridge-aware ERC-20 representation with mint/burn permissions limited to the controller. |
| VenueBridgeController | Consumes verified PFTL packets, mints venue tokens, burns returns, enforces caps, and emits canonical events. |
| PacketReplayRegistry | Stores consumed packet hashes and nonces. |
| UniswapSettlementAdapter | Optional adapter that receives or mints venue a651 and executes a bound Uniswap swap. |
| EmergencyPause | Halts mint and settlement paths on verifier, route, or contract incident while preserving read-only inspection. |

## 9. PFTL-to-Ethereum protocol flow

This section describes the primary burn/mint model. A lock/mint deployment replaces "burn" with "lock" and must enforce the separate backing invariant from Section 6.2.

### 9.1 User signs bridge intent

The user signs a PFTL transaction with a domain-separated payload:

```text
bridge_out_intent {
  domain: "pftl-navcoin-bridge-v1",
  source_chain_id: "postfiat-mainnet-or-testnet-id",
  destination_chain_id: 1,
  source_bridge: pftl_bridge_id,
  destination_bridge: ethereum_bridge_address,
  asset_id: "a651",
  amount_atoms: X,
  source_account_or_note: user,
  destination_address: eth_address,
  movement_model: burn_mint,
  destination_action: mint_only | mint_and_swap_uniswap,
  action_payload_hash: optional,
  min_output: optional_if_swap,
  destination_deadline: ethereum_timestamp_or_block,
  source_expiry_height: H,
  refund_not_before_height: R,
  refund_recipient: user_or_authorized_refund_address,
  nonce: N,
  fee_policy: relayer_fee_or_user_paid
}
```

The signed payload must not be replayable across:

- PFTL mainnet and testnet;
- Ethereum mainnet and testnets;
- old and new bridge versions;
- different assets;
- different bridge contracts;
- mint-only and mint-and-swap actions;
- different recipients;
- different refund recipients.

### 9.2 PFTL debits source supply

PFTL verifies:

- user authorization;
- sufficient spendable balance or valid shielded spend;
- asset id;
- amount bounds;
- bridge route is registered and active;
- destination chain and destination bridge are registered;
- movement model is allowed for the route;
- nonce is unused within the packet domain;
- expiry and refund parameters satisfy route margins;
- NAV and route caps permit the transfer.

Then PFTL applies the state transition:

```text
burn_or_lock(user, asset_id, amount_atoms)
record_outstanding_claim(packet_hash, amount_atoms)
emit_bridge_receipt(packet_hash, receipt_fields)
```

For a shielded source note, bridge egress is a disclosure event unless a separate shielded bridge design is implemented. The public receipt must reveal enough to settle the destination action.

### 9.3 PFTL finalizes the receipt

The receipt becomes usable only after PFTL finality.

The proof submitted to Ethereum must bind:

```text
finalized_header
finality_certificate_or_succinct_proof
validator_set_root
receipt_root
receipt_inclusion_proof
packet_hash
packet_fields
```

Ethereum must reject packets based only on mempool data, RPC observations, indexer claims, or non-final PFTL blocks.

### 9.4 Relayer submits to Ethereum

Anyone can relay:

```text
submitPftlPacket(packet, proof, optional_action_payload)
```

The relayer is not trusted. It cannot change the amount, recipient, token, action, route, expiry, or refund parameters because those fields are bound by the finalized packet hash.

### 9.5 Ethereum verifies and consumes the packet

Ethereum checks:

- PFTL chain id;
- bridge domain and version;
- source bridge id;
- destination chain id equals the current Ethereum chain id;
- destination bridge equals this bridge controller;
- registered source asset maps to the registered destination token;
- PFTL finality proof, succinct proof, or optimistic acceptance;
- receipt inclusion;
- packet hash;
- nonce or packet hash not consumed;
- destination deadline not expired;
- route not paused;
- amount within local cap and epoch limits;
- action payload hash matches supplied action payload, if any.

The consume mark must be written before external calls, or the function must otherwise be reentrancy safe:

```text
consumed[packet_hash] = true
```

If the transaction reverts, the consume mark must revert with it.

### 9.6 Ethereum mints venue a651

For a bridge-aware ERC-20 representation:

```text
VenueBridgeController.mint(destination_address, amount_atoms)
```

For a lock/release representation:

```text
VenueVault.release(destination_address, amount_atoms)
```

This spec prefers a bridge-aware mint/burn venue token for fungible a651 movement because it gives cleaner packet accounting and avoids ambiguity around locked backing.

### 9.7 Optional Uniswap execution

If the packet requests `mint_and_swap_uniswap`, Ethereum can mint to a settlement adapter and execute a bound swap:

```text
mint a651 to adapter
adapter approves or transfers to router
router executes exact input swap
require amount_out >= min_amount_out
send output to recipient
```

The packet must bind:

- router or route abstraction;
- token in;
- token out;
- pool id, fee tier, or path hash;
- amount in;
- minimum output;
- recipient;
- deadline;
- refund or failure behavior.

Preferred failure behavior:

```text
if swap reverts:
  revert entire settlement
  consumed[packet_hash] remains false
  venue tokens are not minted or remain reverted
```

An alternative design can consume the packet and credit claimable venue a651 to the user if the swap fails. That adds state and UX complexity and must be explicitly implemented and tested. It should not be implicit.

## 10. Ethereum-to-PFTL protocol flow

The return path mirrors the outbound path.

```text
burn_or_lock Ethereum venue a651
-> emit canonical bridge_return event
-> prove Ethereum finality and receipt inclusion to PFTL
-> PFTL consumes event nonce
-> PFTL mints, reissues, or unlocks canonical a651
```

Ethereum bridge controller checks:

- caller authorization;
- token amount;
- recipient format for PFTL;
- route status;
- nonce uniqueness;
- fee fields;
- destination asset mapping.

Then it emits a canonical event:

```text
BridgeReturnV1 {
  domain,
  ethereum_chain_id,
  source_bridge,
  destination_chain_id,
  destination_bridge,
  token,
  asset_id,
  amount_atoms,
  sender,
  pftl_recipient,
  nonce,
  deadline_or_expiry,
  fee_amount_atoms
}
```

PFTL inbound verification checks:

- Ethereum chain id;
- bridge controller address;
- token address;
- event topic and ABI;
- receipt inclusion;
- Ethereum finality policy;
- event nonce not consumed;
- asset mapping;
- amount;
- recipient;
- packet domain;
- route status and caps.

PFTL must not release canonical supply based only on a centralized indexer.

## 11. Packet schema and replay protection

All consensus-critical fields should use fixed-width canonical encoding. JSON can be used for display, but not as the consensus encoding.

A human-readable sketch:

```text
BridgePacketV1 {
  domain: bytes32,
  version: uint16,
  source_chain_id: bytes32,
  destination_chain_id: uint256,
  source_bridge: bytes32,
  destination_bridge: address,
  asset_id: bytes32,
  source_token_or_asset: bytes32,
  destination_token: address,
  movement_model: uint8,
  amount_atoms: uint128,
  sender_commitment: bytes32,
  recipient: bytes,
  refund_recipient: bytes,
  action_kind: uint8,
  action_payload_hash: bytes32,
  nonce: uint128,
  source_height: uint64,
  source_receipt_root: bytes32,
  source_expiry_height: uint64,
  destination_deadline: uint64,
  refund_not_before_height: uint64,
  fee_amount_atoms: uint128
}
```

For Uniswap execution, `action_payload_hash` binds a separate payload:

```text
UniswapActionV1 {
  router: address,
  token_in: address,
  token_out: address,
  pool_id_or_path_hash: bytes32,
  amount_in: uint128,
  min_amount_out: uint128,
  recipient: address,
  deadline: uint64
}
```

The packet hash should be computed over canonical encoding:

```text
packet_hash = H(canonical_encode(BridgePacketV1))
```

Replay defense requires:

```text
consumed[packet_hash] == false
packet.domain == expected_domain
packet.version == supported_version
packet.destination_chain_id == this_chain_id
packet.destination_bridge == this_bridge
asset_mapping[packet.asset_id] == packet.destination_token
proof binds packet_hash to finalized source receipt
packet not expired for destination settlement
```

PFTL source nonce scope should include at least:

```text
domain
source_chain_id
destination_chain_id
source_bridge
destination_bridge
asset_id
sender_or_sender_commitment
nonce
```

A packet valid for one domain must be invalid everywhere else.

## 12. Finality verifier options

### Option A: direct PFTL light client on Ethereum

Ethereum verifies PFTL finality directly.

Pros:

- strongest trust model;
- no bridge committee;
- packet validity is independently checkable on chain;
- cleanest basis for unqualified trustless claims.

Cons:

- potentially expensive on Ethereum;
- PFTL finality certificate must be compact enough for EVM verification;
- validator set transitions must be efficiently verifiable;
- PFTL finality upgrades require careful compatibility.

Blocking research question:

```text
Can PFTL headers, validator set updates, finality certificates, and receipt proofs be verified on Ethereum at acceptable cost?
```

### Option B: succinct PFTL finality proof

An off-chain prover proves PFTL finality, validator set correctness, and receipt inclusion. Ethereum verifies a succinct proof.

Pros:

- cheaper on-chain verification after proof generation;
- can batch many receipts;
- clean EVM interface;
- likely more practical if native PFTL finality proofs are too large for Ethereum.

Cons:

- prover complexity;
- circuit correctness becomes bridge-critical;
- verifier-key governance matters;
- proof-system assumptions become part of the trust model.

Required evidence:

- circuit specification;
- test vectors for valid and invalid headers;
- test vectors for validator set transitions;
- test vectors for receipt inclusion and exclusion where relevant;
- gas and proof-size measurements before choosing this as the public path.

### Option C: optimistic bridge adapter

A packet is posted on Ethereum and becomes valid after a challenge window unless a permissionless challenger proves it invalid.

Pros:

- cheaper normal path;
- simpler than full light-client verification in early stages;
- invalid packets can be challenged by anyone if evidence is available.

Cons:

- delayed settlement;
- requires watchers;
- challenge game must be correct;
- invalidity proofs must be well-defined;
- not equivalent to direct finality verification.

Trust label:

```text
trust-minimized under at-least-one-honest-watcher and correct-challenge-game assumptions
```

### Option D: threshold signer bridge

A threshold signer set attests to PFTL packets or Ethereum return events.

Pros:

- fastest to prototype;
- useful for controlled testnet and packet-shape testing;
- simple EVM verification.

Cons:

- not trustless;
- signer compromise can mint or release supply;
- signer liveness affects bridge liveness;
- requires caps, monitoring, and emergency pause even for limited value.

Trust label:

```text
trust-based controlled stage
```

Recommended research path:

```text
Stage 1: threshold-signed controlled testnet packet
Stage 2: bridge-aware venue token and strict accounting
Stage 3: Uniswap settlement adapter
Stage 4a: optimistic verifier if it has permissionless challenges
Stage 4b: direct or succinct PFTL finality verifier for unqualified trustless claims
```

## 13. Uniswap is an execution venue, not the bridge trust anchor

Uniswap should not be asked to answer bridge questions.

Uniswap does not determine:

- whether PFTL finalized a receipt;
- whether a PFTL receipt is included in a receipt root;
- whether a validator set root is valid;
- whether a bridge packet has already been consumed;
- whether NAV supply is authorized;
- whether an expired packet can be refunded;
- whether global supply is inside the cap.

Uniswap can be used in three ways:

| Mode | Description | Risk |
|---|---|---|
| Mint only | Bridge mints venue a651 to the user. User trades manually if desired. | Simplest accounting; less atomic UX. |
| Mint and swap | Bridge mints to an adapter that executes a bound Uniswap swap in the same transaction. | Adds slippage, routing, deadline, and MEV risk. |
| Market-operation envelope | PFTL authorizes a bounded protocol operation in an eligible pool. | Strong policy control, but much more contract complexity. |

For user bridge-out, `mint_and_swap` is acceptable only if the packet binds the route, recipient, minimum output, deadline, and failure behavior.

Protocol market operations should use a separate envelope. Arbitrary user bridge packets should not become policy-level buy or sell authorizations.

## 14. Privacy boundary

A PFTL-to-Ethereum bridge is an egress event.

If source a651 was held in a shielded note, the user should assume the bridge may reveal:

- destination chain;
- destination address or address commitment;
- asset id or venue token;
- amount;
- timing;
- route choice;
- optional swap path.

A private bridge is a separate design layer:

```text
shielded burn on PFTL
-> public aggregate bridge packet
-> Ethereum claim using nullifier/proof
```

That requires batching, nullifiers, claim proofs, anti-replay rules, and separate failure handling. Unless privacy is a hard launch goal, the first bridge release should treat egress as public and avoid implying amount privacy.

## 15. Failure handling

| Failure | Required behavior |
|---|---|
| Relayer disappears | User or another relayer can self-relay before destination deadline. After expiry, refund requires verified non-consumption or an optimistic refund challenge path. |
| Ethereum gas spike | Packet remains in-flight and counted as an outstanding claim. User can wait, self-relay, use another relayer, or refund after safe expiry. |
| Packet expires before settlement | Destination rejects settlement. Source refund is not automatic; outstanding claim remains until safe refund completes. |
| Destination consumed but not reported to PFTL | Source refund must be blocked by verified Ethereum state or by a challenge proof during the refund window. |
| Source refund completes | Destination must reject any later settlement. Packet reaches terminal `SourceRefunded`. |
| Destination settlement completes | Source refund must be impossible. Packet reaches terminal `DestinationConsumed`. |
| Same packet submitted twice | Consumed registry rejects the second submission. |
| Wrong chain replay | Domain and chain ids reject the packet. |
| Wrong token replay | Asset id and destination token mapping reject the packet. |
| Modified recipient or route | Packet hash mismatch rejects the packet. |
| Uniswap swap reverts | Entire settlement reverts and packet remains unconsumed, unless explicit claimable-token fallback is implemented. |
| Ethereum reorg | PFTL inbound verifier waits for configured finality and rejects non-final events. |
| PFTL fork or finality bug | Ethereum verifier rejects invalid proof if assumptions hold; route pause is required if assumptions are broken. |
| Threshold signer compromise | Caps and emergency pause limit damage, but the stage remains trust-based. |
| Optimistic watcher failure | Invalid packets may pass if no one challenges; this is part of the optimistic trust model. |
| Stale NAV proof or route pause | New bridge-outs are rejected or capped. Existing venue trading may continue. |
| Bridge verifier exploit | Pause mint and settlement paths, preserve evidence, and require governance-controlled recovery. |
| Cap overflow | Packet is rejected before mint or release. |

## 16. Rollout gates and permitted claims

### Stage 0: prerequisites and current-state boundary

Completion requirements:

- State publicly that the live a651/USDC pool is not this trustless bridge.
- State publicly that the locked controller cannot be repointed.
- Choose a migration direction: new wrapped venue token, wrapper, or explicit migration.
- Choose the primary movement model for the first implementation: burn/mint or lock/mint.
- Define packet serialization and domain separators.
- Define PFTL finality proof requirements.
- Define receipt commitment format.
- Define validator set root and transition proof requirements.
- Define in-flight accounting and refund state machine.
- Choose expiry, deadline, and refund margin formulas.

Gate:

```text
No public bridge implementation scope should ignore existing-token limitations,
PFTL finality proof requirements, or refund-vs-settlement race safety.
```

### Stage 1: controlled testnet packet with threshold signatures

Completion requirements:

- PFTL can burn or lock devnet a651 and emit a canonical packet.
- Ethereum test contract accepts a threshold-signed packet.
- Packet consume registry rejects replay.
- In-flight claims are accounted for.
- Expired packet refund works under the chosen safe refund design.
- Ethereum-to-PFTL return path works on testnet.

Gate:

```text
Two consecutive PFTL->Ethereum->PFTL round trips complete on testnet
with no manual state edits and no duplicate packet acceptance.
```

Permitted claim:

```text
controlled threshold-signed testnet bridge prototype
```

Not permitted:

```text
trustless bridge
```

### Stage 2: bridge-aware Ethereum venue token

Completion requirements:

- ERC-20 venue token mints only from the bridge controller.
- Bridge controller consumes only valid packets.
- Burn events for Ethereum-to-PFTL returns are canonical and easy to prove.
- Local venue cap is enforced on chain.
- Reentrancy, cap overflow, and replay protections are fuzz-tested.

Gate:

```text
Fuzz tests cover packet replay, wrong chain id, wrong asset id,
modified recipient, expired packet, refund race, reentrancy,
and cap overflow.
```

### Stage 3: Uniswap settlement adapter

Completion requirements:

- Mint-only path works.
- Mint-and-swap path binds router, route or route hash, token out, min output, recipient, and deadline.
- Swap reverts do not consume packets unless claimable venue a651 fallback is explicitly implemented and tested.
- Adapter does not become an accounting oracle.

Gate:

```text
Fork tests against the intended Uniswap venue prove exact input,
slippage failure, deadline failure, route mismatch, reentrancy safety,
and replay rejection.
```

### Stage 4a: optimistic verifier

Completion requirements:

- Threshold signatures are replaced or bypassed by an optimistic packet path.
- Anyone can post packets.
- Anyone can challenge invalid packets.
- Challenge evidence is specified and testable.
- Watcher and challenger runbooks exist.
- Bonds and challenge windows are parameterized.

Gate:

```text
The bridge may be described as optimistic or trust-minimized only after
permissionless challenge tests reject adversarial packets under the published rules.
```

Not permitted:

```text
unqualified trustless bridge
```

### Stage 4b: direct or succinct finality verifier

Completion requirements:

- Ethereum verifies PFTL finality and receipt inclusion directly, or verifies a succinct proof of them.
- Validator set transitions are verified.
- Receipt roots and packet inclusion are verified.
- Replay domains are enforced.
- Invalid finality proofs, invalid validator set updates, and invalid receipt proofs are rejected in tests.
- Upgrade and verifier-key governance risks are documented.

Gate:

```text
The unqualified trustless claim is available only for a permissionless
finality-verification path whose assumptions and tests are public.
```

### Stage 5: migration execution, if chosen

Completion requirements:

- If using a new wrapped venue token, legacy a651 and legacy pools are labeled clearly.
- If using a wrapper, wrapper backing and bridge-minted supply are kept separate.
- If using explicit migration, conversion rate, window, LP treatment, and supply reconciliation are published.
- NAV policy and migration supply accounting are reconciled before public claims.

Gate:

```text
No migration claim until old-token holders, old Uniswap liquidity,
new token supply, outstanding claims, and NAV policy are reconciled.
```

## 17. Minimum test matrix

| Test | Expected result |
|---|---|
| Valid finalized PFTL packet mints Ethereum venue a651 | Success |
| Same packet submitted twice | Second submission rejected |
| Packet for wrong destination chain | Rejected |
| Packet for wrong bridge address | Rejected |
| Packet for wrong asset id | Rejected |
| Packet with modified recipient | Rejected |
| Packet with modified action payload | Rejected |
| Packet after destination deadline | Rejected on destination |
| Source refund before refund window | Rejected |
| Source refund without non-consumption proof or challenge completion | Rejected |
| Source refund after verified non-consumption | Success |
| Source refund challenged by valid destination consume proof | Refund canceled |
| Destination consume after source refund | Rejected |
| Destination consume and source refund race | At most one terminal state succeeds |
| Ethereum burn event proved to PFTL | PFTL mints, reissues, or unlocks once |
| Ethereum burn event replayed to PFTL | Second consume rejected |
| Invalid PFTL finality certificate | Rejected |
| Invalid validator set transition | Rejected |
| Invalid receipt inclusion proof | Rejected |
| Testnet packet submitted on mainnet domain | Rejected |
| Uniswap min-out too high | Swap reverts without packet loss |
| Uniswap deadline expired | Settlement reverts without packet loss |
| Route hash mismatch | Rejected |
| Bridge cap exceeded | Rejected |
| Stale NAV or paused route | New bridge-out rejected |
| Reentrancy attempt during mint-and-swap | Rejected or safely reverted |
| Threshold signer below quorum in Stage 1 | Rejected |
| Optimistic invalid packet challenged in Stage 4a | Rejected before settlement |
| Emergency pause | Mint and settlement stopped; read-only inspection still works |

## 18. Recommended baseline and open research questions

Recommended baseline for prototypes:

```text
Use burn/mint for fungible venue movement.
Use a new bridge-aware wrapped venue token for clean accounting.
Use threshold signatures only for controlled testnet packet testing.
Develop optimistic and succinct/direct verifier paths as separate research tracks.
Treat the existing Ethereum a651 token and pool as legacy unless an explicit migration is chosen.
```

Open research questions:

1. What exact PFTL finality certificate, header, receipt root, and validator set transition format should the Ethereum verifier consume?
2. Is direct PFTL light-client verification on Ethereum feasible at acceptable gas cost?
3. If using succinct proofs, what is the circuit boundary: finality only, receipt inclusion only, or both?
4. If using optimistic verification, what invalidity proofs are available to challengers?
5. What numeric expiry, destination deadline, challenge, and refund margins are safe for PFTL and Ethereum?
6. Should the public bridge use burn/mint only, or support lock/mint for assets that require preserved issuance records?
7. Should the Ethereum venue representation be a new wrapped venue token, a wrapper, or a migrated successor to the current a651 token?
8. What Ethereum finality policy should PFTL require for inbound burn events?
9. Does first-release bridge-out from shielded notes accept public amount disclosure, or require batching and nullifier-based private claims?
10. Should Uniswap execution use v4 directly, Universal Router, or a route abstraction pinned by hash?
11. Should bridge fees be paid in a651, PFTL gas, ETH, or destination output token?
12. What governance rules control route pauses, verifier upgrades, venue caps, and migration parameters?

## 19. Evidence appendix

Before any public unqualified trustless claim, the following evidence should exist.

### 19.1 Finality and receipt evidence

- PFTL finality specification.
- PFTL finalized header format.
- PFTL finality certificate format.
- Validator set root format.
- Validator set transition proof format.
- Receipt commitment specification.
- Bridge receipt schema.
- Canonical packet serialization.
- Test vectors for valid and invalid packet hashes.
- Test vectors for receipt inclusion and malformed inclusion proofs.

### 19.2 Verifier evidence

For a direct light client:

- EVM verifier specification;
- gas measurements;
- validator set update tests;
- invalid signature and invalid quorum tests;
- receipt-root mismatch tests.

For a succinct verifier:

- circuit specification;
- proof-system assumptions;
- verifier-key governance description;
- proof size measurements;
- prover performance measurements;
- invalid witness tests;
- receipt inclusion tests;
- validator set transition tests.

For an optimistic verifier:

- challenge game specification;
- bond and timeout parameters;
- invalidity proof formats;
- watcher runbook;
- tests showing invalid packets are challengeable;
- tests showing valid packets cannot be griefed indefinitely under the rules.

### 19.3 Accounting evidence

- Formal or executable invariant for encumbered supply.
- Tests for source-debited but destination-unsettled packets.
- Tests for expired but unrefunded packets.
- Tests for refund after verified non-consumption.
- Tests for refund challenged by destination consume proof.
- Tests for cap overflow and route pause.
- Reconciliation method for venue supply and outstanding claims.

### 19.4 Migration evidence

If current a651 is involved:

- chosen migration path;
- statement that the locked controller is not repointed;
- old token supply snapshot method, if any;
- LP treatment;
- conversion terms;
- treatment of unclaimed legacy tokens;
- NAV supply reconciliation;
- labeling plan for legacy and new assets.

## 20. Reference patterns

Two NEAR bridge designs are useful references, not templates to copy blindly.

| Pattern | Lesson |
|---|---|
| Rainbow Bridge | Mutual light clients and Merkle proofs show the clean trust model: destination chains verify source-chain state rather than trusting relayers. |
| NEAR Omni Bridge | Token factory and custodian patterns show a practical product architecture: native tokens lock/release, bridged tokens mint/burn, and relayers move messages without mint authority. |

The relevant lesson for PFTL is:

```text
relayers may transport packets
relayers may pay gas
relayers may improve latency
relayers must not be supply accountants
relayers must not be mint authorities
```

References:

- NEAR Rainbow Bridge introduction: <https://doc.aurora.dev/bridge/introduction/>
- Rainbow Bridge specification: <https://github.com/Near-One/rainbow-bridge/blob/master/SPEC.md>
- NEAR Omni Bridge overview: <https://docs.near.org/chain-abstraction/omnibridge/overview>
- NEAR Omni Bridge implementation details: <https://docs.near.org/chain-abstraction/omnibridge/implementation>
- NEAR Intents overview: <https://docs.near.org/chain-abstraction/intents/overview>
- [Post Fiat private OTC swaps research](/research/private-otc-swaps/)
- [NAVCoin collateralization without spot redemption](/blog/navcoin-collateralization/)

## 21. Research conclusion

The bridge target is not an inventory service and not a Uniswap hook. It is a finality-verified supply movement system:

```text
source debit
-> finalized receipt
-> destination verification
-> destination credit
-> optional venue execution
```

The live a651/USDC pool and locked controller are not this system. They may remain relevant to a migration or legacy venue strategy, but they cannot be treated as the trustless PFTL bridge.

The staged path is useful only if the claims stay precise:

- threshold-signed packet testing is trust-based;
- optimistic verification is trust-minimized under challenger assumptions;
- direct or succinct finality verification is the target trustless design;
- Uniswap remains an execution venue, not the accounting oracle;
- in-flight and expired packets remain counted until they reach exactly one terminal state: destination consumed or source refunded.
