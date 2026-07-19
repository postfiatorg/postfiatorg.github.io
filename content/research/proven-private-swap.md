---
title: "Anatomy of a Proven Private Swap: 250 USDC, Verified End to End"
date: 2026-07-12T00:00:00Z
draft: true
url: "/research/proven-private-swap/"
summary: "On July 12, 2026, Post Fiat executed a real 250 USDC private swap through the shipping product path: counted cash, consensus-bound NAV, shield ingress, a Halo2 private swap, private egress, trustless verification, exact conservation, and six-validator convergence."
description: "The live mechanics and proof record of a 250 USDC private swap between native assets that trade to NAV with on-chain-proven reserves."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Proof of Reserves
  - OTC
  - Privacy
  - Uniswap
  - Bridge
  - PFTL
  - Post Fiat
---

*Part of the NAVCoin series. [The proposal](/blog/navcoin-proposal/) defined native assets that trade to NAV with on-chain-proven reserves. [The architecture](/blog/navcoin-ethereum/) defined one verified reserve portfolio, one canonical NAV, and many access venues. [pfUSDC](/blog/pfusdc/) defined the countable cash leg, and [the OTC MVP](/blog/navcoin-otc-mvp-proven/) proved the transparent round trip with real value. On July 12, 2026, the private route ran end to end through the shipping product path with 250 real USDC.*

## The live result

Post Fiat executed the complete private swap path with a fresh wallet and a fresh at-NAV RFQ. The run deposited 250 USDC into the Arbitrum I-1 vault in transaction `135339…6f97`. An observer-certified claim credited exactly 250,000,000 pfUSDC atoms on PFTL. The product then executed shield ingress, the cryptographic private swap on the warm prover, private egress, public receipt reconciliation, and final verification.

The trustless verifier exited 0. Vault value increased by 250,000,000 atoms. Certified pfUSDC issuance increased by 250,000,000 atoms. The difference was zero. All six validators converged on the same final height and state root with empty mempools.

This is the first shipping product path that combines real source-chain value, native assets priced to an on-chain-proven NAV, a private two-asset swap, trustless end-to-end verification, and atom-for-atom conservation in one certified run. The swap is private where privacy matters and proven everywhere else.

## What we are enabling

An OTC trade of a reserve-backed asset today runs on stacked trust. The desk trusts the issuer's balance sheet PDF. Both sides trust each other's settlement. The venue price floats free of whatever the reserves actually are, and the only privacy available is the privacy of settling somewhere nobody can audit at all.

The transaction described here replaces each of those trust points with a machine check, and it does so without giving up the one thing OTC participants actually need privacy for — the trade itself:

- **The reserves are proven before anything prices off them.** Not attested quarterly; proven per epoch, in consensus, with challenge windows and a deadman switch.
- **The cash is counted before it backs anything.** Dollars enter as source-labeled, finality-checked receipts, not as an undifferentiated wrapped ticker.
- **The mint price is computed, not quoted.** Consensus derives the price from the finalized reserve proof. A wallet cannot assert a price; it can only commit to the one the ledger derives.
- **The trade is proven, not watched.** The swap settles inside a shielded circuit. The chain verifies a proof that the trade was valid; it never learns the asset, the amount, or the counterparties.
- **The exit conserves supply.** Movement to Ethereum runs through a packet state machine whose supply invariant is re-validated by consensus after every single transition, on both legs, with exactly one terminal state per packet.

One sentence: **the swap is private where privacy matters and proven everywhere else.**

## The route at a glance

```text
 Ethereum / Arbitrum                PFTL (canonical NAV + supply ledger)              Ethereum
 ───────────────────                ─────────────────────────────────────             ────────
 USDC ──deposit+proof──▶ pfUSDC ──shield──▶ [ Orchard: private swap ] ──egress──▶ a651
                          (counted            pfUSDC note ⇄ a651 note                  │
                           receipt)           (zk proof; nothing else                  │ export packet
                                              visible on chain)                        ▼
                                                                            bridge controller consumes
                                     NAV reserve packets ──▶ finalized      packet once ──▶ wa651 ──▶
                                     epoch state (nav_per_unit,             Uniswap pool (atomic
                                     verified_net_assets, freshness)        mint-and-swap or hold)
```

Five stages. Each one closes a specific trust assumption.

## Stage 1 — Reserves are proven before anything trades

A NAVCoin's reserves live in **reserve packets**: per-epoch consensus objects carrying `nav_per_unit`, `circulating_supply`, `verified_net_assets`, and the proof that backs them. What counts as proof is a registered, content-addressed **proof profile**, and the evidence tiers are explicit per leg — cryptographic where the source chain allows it ([six domains proven](/blog/proof-of-leverage/), from Aave debt receipts to an in-circuit Monero reserve), quorum-attested by registered observers where the source is a public API, with every tier labeled rather than flattened.

A packet is not usable the moment it arrives. It survives a bonded challenge window, finalizes into the asset's consensus state (`finalized_epoch`, `nav_per_unit`, `finalized_reserve_packet_hash`), and starts aging against a freshness bound. An issuer who stops proving does not get a stale green light — mint and exit fail closed. Staleness is a protocol fact, not an operator courtesy.

## Stage 2 — Cash the chain can count

The buyer's side of the trade enters as [pfUSDC](/blog/pfusdc/): a PFTL-native cash receipt minted only from proven source-chain deposits. Not every dollar-shaped token is the same asset — native, CCTP-bridged, and custodial dollars enter as differently labeled receipts with different haircuts, and only **counted** receipts back anything. In the July 12 live run, the Arbitrum I-1 vault gained exactly 250,000,000 USDC atoms and the certified PFTL account gained exactly 250,000,000 pfUSDC atoms. The observer-certified claim linked the source-chain deposit to the PFTL credit, atom for atom.

## Stage 3 — The price is computed, not quoted

With proven reserves and counted cash in place, issuance can happen — and this is the newest piece of the machinery, the one that makes "proof of reserves" load-bearing rather than decorative.

When a wallet mints a NAVCoin against settlement cash, **consensus derives the price from the finalized reserve packet** — `nav_per_unit`, converted through the asset's registered valuation unit and precision. The price field the wallet signs is an equality-checked commitment: if it does not match the ledger-derived value to the atom, the transaction rejects with `pftl_uniswap_price_mismatch`. There is no quote to trust and no oracle to bribe. The same validity rule rejects a halted asset (`pftl_uniswap_nav_asset_halted`), an unfinalized reserve state, a wrong or stale epoch (`stale_pftl_uniswap_nav_epoch`), a mismatched reserve-packet hash, and a packet older than the consensus freshness bound.

The arithmetic is exact in the holder's favor: the wallet is debited precisely `minted_units × derived_price`. Any remainder below one unit never leaves the wallet — no dust silently folds into anyone's reserve.

The first three stages compose into the property the whole series has been building toward: **units of this asset can only come into existence against counted cash, at the machine-verified value of what backs them, while the proof is fresh.**

## Stage 4 — The private middle

Here is where the transaction disappears from view — and only here.

The holder shields pfUSDC into an **Orchard note** — the shielded-pool primitive: the chain records only a cryptographic commitment, the wallet keeps the opening that says what the note contains and who can spend it. The OTC trade itself is then a single shielded action proven by a Halo2 zk-SNARK. Inside the circuit: the buyer's shielded pfUSDC note and the seller's shielded a651 note are consumed, the swapped pair is emitted, and the proof establishes four facts at once — each input note exists in the commitment tree, each spend is authorized by its owner's key, each **nullifier** (the one-time spent-marker that makes double-spending a note impossible without revealing which note was spent) is fresh, and value is conserved per asset across the swap. Validators verify the proof and certify the state transition; they never execute the trade, only check it.

What the chain sees: a valid proof, two nullifiers, two new commitments, a fee. What it does not see: which assets moved, how much, from whom, to whom, or that the two legs were related to any prior public balance. There is no order book entry to front-run, no size to lean on, no counterparty pair to map. In the July 12 product run, the warm prover produced the private swap, validators certified it, private egress completed, and the final verifier accepted the complete evidence chain.

The privacy boundary is scoped, and the scoping is the design: the *edges* of the route (counted cash in, exit receipt out) stay public precisely so the reserve accounting stays provable. The chain checks the rule, never the route.

## Stage 5 — The Uniswap exit

A private position is worth more when it can reach public liquidity without a leap of faith. The bridge is where most designs quietly reintroduce every trust assumption the rest of the stack removed, so it is built as consensus state, not as an operator sidecar:

- **Export is a real debit.** Exporting a651 toward Ethereum debits the holder's actual balance and moves the amount into `outstanding_bridge_claims` — a supply bucket, not a log line.
- **One packet, one consume.** The Ethereum bridge controller verifies the packet and consumes it exactly once against a replay registry, minting the venue token `wa651`. A packet that expires unconsumed refunds on PFTL — and consume and refund are mutually exclusive terminal states, enforced in both orders.
- **The swap is atomic or absent.** A mint-and-swap packet binds the Uniswap action to the mint: exact-input swap, minimum output, deadline. If the swap reverts, the entire settlement reverts and the packet remains consumable or refundable. There is no state where the mint happened and the swap didn't.
- **Returns are derived, not declared.** Coming home, the burn event's identity is recomputed by PFTL consensus from its fields — chain id, controller, token, sender, recipient, amount, nonce, height — and checked against finality depth before a single unit is re-credited.
- **The invariant never sleeps.** After every transition on either leg, consensus re-validates the route's conservation identity: PFTL-spendable + Ethereum-spendable + outstanding claims + pending returns equals authorized supply, exactly. Routes are capped per issuer, and pausing a route blocks everything that grows exposure while never blocking a refund.

The result on the venue side is a pool price that can drift from NAV — venue prices do — with a public, fresh, machine-verified NAV to arbitrage it against, and a bridge whose accounting cannot fork from the canonical ledger.

## What is proven at each boundary

| Boundary | Machine-checked | Stays private |
|---|---|---|
| Cash in | Source, finality, haircut, counted amount | — |
| Mint | Fresh finalized reserve proof; consensus-derived price; exact debit | — |
| Shield | Valid commitment | Note opening, owner |
| OTC swap | Proof validity, nullifier freshness, value conservation | Asset, amount, both counterparties |
| Egress | Right to exit; exit amount and destination | The shielded path that produced it |
| Bridge out | Debit, packet uniqueness, cap, expiry; atomic venue swap | — |
| Return | Recomputed burn id, finality depth, supply movement | — |

Read the table bottom-up and the thesis is visible in the structure: privacy is exactly one row wide, and every row above and below it is a proof.

## Scope

The July 12 run completed on the controlled WAN devnet, not mainnet. Its shipping `public_settlement` row verified the PFTL receipt reconciliation and did not submit a separate EVM withdrawal. The supply-conserving Uniswap bridge path is implemented and covered by consensus tests; it was not the external effect exercised by this live run. Destination events on that route currently carry the declared `CONTROLLED` trust class. This is not a third-party audit or a public routing launch.

## Why it matters

Shielded pools, reserve proofs, bridges, and AMMs have existed as separate systems. Post Fiat composes them in one ledger: the native asset enters at the proven value of its reserves, trades privately without weakening its accounting, and reaches public venues only through supply-conserving machinery. That composition is the product. A desk gets the confidentiality it requires; everyone else gets the proof they were never offered.
