---
title: "Private NAV OTC Swaps: Shielded Settlement for NAVCoin on Post Fiat"
date: 2026-06-18T00:00:00Z
summary: "NAVCoin assets can be bridged onto Post Fiat L1 as native assets and traded through shielded atomic swaps — hiding counterparty, size, and price from the public chain. The proven NAV oracle, the collateralization enforcement, and the privacy layer all live on the same chain, eliminating cross-chain oracle latency, front-running, and the bridge trust boundary that EVM DEX paths require."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Privacy
  - OTC
  - Shielded
  - DEX
  - Post Fiat
  - L1
---

*[Series I](/blog/postfiat-l1v2-private-xrpl-latency-benchmark/) proved certified finality. [Series II](/blog/postfiat-l1v2-fastpay-latency/) removed consensus from owned-value settlement. This post describes how NAVCoin assets trade privately on Post Fiat — the same chain that proves their value.*

## The problem: every NAVCoin trade is public

A NAVCoin like a651 is a floating-NAV token backed by a proven portfolio. Its NAV is computed on Post Fiat L1 (PFTL) and finalized in consensus. But today, the token trades on Ethereum — on a public Uniswap pool where every transaction, every counterparty, and every size is visible to the entire market.

For institutional participants — funds, OTC desks, treasury managers — this is a problem. A large a651 purchase on Uniswap moves the pool price against the buyer (slippage). It signals intent to the market. It creates a permanent on-chain record of position size. And it gives every MEV searcher a free option to front-run the trade.

Over-the-counter (OTC) desks solve this in traditional finance by matching buyers and sellers bilaterally, off-exchange, with no public order book. But on-chain OTC is hard: if the settlement is on a transparent ledger, the privacy benefit disappears, and if it's off-chain, you reintroduce counterparty risk.

Post Fiat solves this by bridging NAVCoin assets onto its own chain and settling trades through its shielded note layer — the same chain where the NAV is proven.

## What PFTL already has

Three primitives that no EVM chain has together:

**The NAV oracle is native.** The proven NAV — verified by the SP1-Groth16 proof-of-leverage, finalized in PFTL consensus — lives on the same chain where the trade settles. A PFTL-native DEX reads the NAV from consensus state in the same block it executes the trade. No cross-chain oracle. No bridge latency. No timing gap for arbitrage.

**The shielded settlement layer.** PFTL's §7 implements Orchard-style shielded notes — the same privacy architecture as Zcash shielded transactions. A shielded transaction hides the sender, the receiver, the amount, and the asset type. The chain verifies value conservation and authorization without revealing any of those fields. This is not a bolt-on privacy feature; it is part of the protocol's settlement layer.

**The owned-value lane.** FastPay-style owned objects — single-writer, single-consumption value containers — are the natural primitive for atomic OTC swaps. Party A locks their a651 in an owned object. Party B locks their USDC. The swap consumes both locks and produces the exchanged outputs in a single transaction. No escrow agent, no timeout window, no partial execution.

## How private NAV OTC swaps work

### Step 1: Bridge the asset onto PFTL

An a651 holder burns their tokens on Ethereum (or Arbitrum) and receives native a651 on PFTL. This is the burn-here-mint-there pattern already planned in the NAVCoin migration: the issuer verifies the EVM burn proof and mints the equivalent native asset on PFTL. The global supply is preserved — one unit burned on Ethereum is one unit minted on Post Fiat.

Once bridged, a651 exists as a native PFTL asset — not a wrapped token, not a representation, but a first-class asset with full shielded-settlement support.

### Step 2: Shield the position

The holder converts their transparent a651 into a shielded note:

```text
transparent a651 balance → shield(a651, amount) → shielded note
```

The shielded note exists in the shielded note tree. The transparent balance decreases. On-chain, an observer sees a shield transaction — they know *something* was shielded, but not who, how much, or what asset.

### Step 3: Execute the shielded swap

Two parties — call them the a651 seller and the USDC buyer — agree on terms off-chain (price, size). They execute the swap as a single shielded action:

```text
inputs:
  shielded note A (seller's a651, verified in the note tree)
  shielded note B (buyer's USDC, verified in the note tree)

shielded swap circuit proves:
  note A and note B are valid (nullifier checks)
  authorization signatures match the note owners
  value is conserved (a651 in = a651 out, USDC in = USDC out)
  the swap ratio satisfies any NAV-band policy (optional)

outputs:
  shielded note A' (a651 to buyer's shielded address)
  shielded note B' (USDC to seller's shielded address)
```

The circuit produces a zero-knowledge proof. PFTL validators verify the proof (value conservation, nullifier non-reuse, authorization) without learning any of the private fields. The swap settles in one block — atomically, irrevocably, privately.

### What the public chain sees

```text
block N:
  shield action (note consumed, new note created)
  → asset type: hidden
  → amount: hidden
  → sender: hidden
  → receiver: hidden
  → price: hidden
  → only the proof and the commitment are visible
```

Nobody knows the trade happened, who participated, or at what price. The only public signal is that shielded activity occurred in that block.

## Why this is different from an EVM privacy solution

Privacy solutions on Ethereum (Aztec, Railway, Shielded pools) all face the same structural problem: the NAV oracle is not on the same chain. They must pull the proven NAV from PFTL through a bridge, introduce latency, and create a timing window where the private trade executes against a stale NAV.

On PFTL, the NAV is consensus state. A shielded swap can read the current NAV floor in the same transaction that executes the trade — the same block, the same validator set, zero oracle latency. The collateralization policy (discount band, mint cap, backing invariant) can be enforced inside the shielded circuit itself, not just on the transparent enforcement layer.

| Property | EVM privacy solution | PFTL shielded swap |
|---|---|---|
| NAV oracle | Cross-chain bridge (latency, staleness) | Same-chain consensus state (zero latency) |
| Collateralization enforcement | Separate EVM contract (transparent) | Inside the shielded circuit (private + enforced) |
| Front-running | Searchers can observe pending shield transactions | PFTL's deterministic inclusion order prevents reordering |
| Settlement finality | EVM block confirmation (~12s) + shield proof | PFTL certified finality (sub-second, FastPay path) |
| Asset representation | Wrapped (bridge risk) | Native (burn-here-mint-there, issuer-relayed) |

## The collateralization synergy

The collateralization system described in the [NAVCoin collateralization post](/blog/navcoin-collateralization/) has a natural extension for shielded trading:

When a651 trades on a PFTL-native DEX (not just Uniswap), the `MarketOpsEnvelope` can read PFTL-native trading data directly — no Ethereum evidence bridge, no venue replay, no cross-chain timing gap. The alignment reserve vault is a PFTL-native contract. Market operations (buying below NAV) execute on the same chain, in the same consensus state, with the same finality guarantee.

And if those market operations themselves execute through the shielded layer, the protocol's intervention is invisible to the market until after the fact — no front-running, no signaling, no MEV extraction. The alignment reserve buys a651 below NAV through a shielded action; the market sees only that shielded activity occurred, not which direction, how much, or at what price.

## What needs to be built

This is a design direction, not a shipped feature. The components:

1. **Burn-here-mint-there bridge** (Phase 4 of the NAVCoin migration — already planned). Issuer-relayed asset movement between EVM chains and PFTL.

2. **USDC representation on PFTL.** A stablecoin (USDC or equivalent) must exist as a native PFTL asset for trading pairs. Same bridge pattern, applied to a stablecoin.

3. **Shielded swap circuit.** A new shielded action type: consume two notes (different assets), prove value conservation and authorization, produce two output notes. Built on the existing Orchard/Halo2 framework from §7.

4. **Shielded order matching.** For OTC-style bilateral trades, a shielded offer board (RFQ model) — not a transparent AMM. Institutional participants post encrypted offers; matches execute as shielded swaps.

5. **Optional: NAV-band enforcement inside the circuit.** The shielded swap circuit can prove the trade price is within the policy band without revealing the price — a private collateralization enforcement that doesn't exist on any transparent chain.

## Why this matters

Institutional adoption of on-chain assets requires three things that transparent chains cannot provide simultaneously: verifiable backing (the NAV proof), enforceable market discipline (the collateralization system), and trade privacy (the shielded layer). Post Fiat is the only chain where all three live on the same settlement layer.

The NAV is proven in consensus. The collateralization is enforced in consensus. The trade is shielded in consensus. No oracle latency. No bridge boundary. No front-running. No public order book.

A fund manager can buy $10M of a651 through a shielded OTC swap on Post Fiat, prove to their auditor that the trade was backed by verified reserves, and leave no public trace of the position — all settled with sub-second finality on the same chain that proves the NAV.

That is a product no other chain architecture can deliver.

---

*Implementation: `postfiatl1v2` branch `fastpay-m1` (owned-value lane, shielded settlement primitives). NAVCoin collateralization: branch `navcoin-market-ops-envelope`. Bridge: Phase 4 of the [PFTL-canonical migration plan](/blog/navcoin-ethereum/). Shielded settlement design: whitepaper §7.*
