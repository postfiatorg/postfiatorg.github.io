---
title: "Canonical NAVCoin Transaction"
date: 2026-06-27T00:00:00Z
url: "/blog/canonical-navcoin-transaction/"
summary: "A plain-English explanation of the correct NAVCoin transaction architecture: PFTL as the source of truth, proof-of-reserves epochs, bridge-verified wrapping, Uniswap as a venue, Orchard privacy, and the gates that keep supply honest."
description: "Plain-English explanation of canonical NAVCoin transactions, including PFTL, proof of reserves, wrapped Ethereum venue tokens, Uniswap, Orchard notes, bridge proofs, and safety gates."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - PFTL
  - Uniswap
  - Bridge
  - Orchard
  - Proof of Reserves
draft: false
---

Start with the [illustrated primer](/research/canonical-navcoin-transaction-primer/). It walks through the whole transaction as a click-through deck: proof of reserves, PFTL supply, wrapping to Ethereum, Uniswap trading, Orchard privacy, private egress, and the safety gates.

This post explains the same thing in plain English.

## The simple version

A canonical NAVCoin transaction has one rule:

> **PFTL decides what exists. Other chains are venues where that claim can trade.**

That sounds abstract, so use a concert-ticket analogy.

PFTL is the official ticket office. It knows how many real tickets exist. Ethereum is a resale marketplace. Uniswap is one booth inside that marketplace. A wrapped NAVCoin on Ethereum is not a second official ticket office. It is a resale-market version of a ticket that must trace back to the official office.

If Ethereum can mint wrapped NAVCoins without checking PFTL, the system is not canonical. It is just another token with a story.

## What came before

The first a651 deployment was a useful demo. It put an Ethereum token in a Uniswap pool and connected it to an Ethereum-side proof adapter. That let us test market behavior, launch mechanics, dashboards, and NAVCoin UX.

But it was not the correct final architecture.

The problem was not Uniswap. Uniswap did its job: it gave the token a public market. The problem was truth. The Ethereum token and Ethereum proof adapter were too close to being treated as the source of truth, while the actual source of truth should be PFTL.

The old shape was:

```text
Ethereum a651 token
  -> Ethereum proof adapter
  -> Uniswap a651/USDC pool
```

The correct shape is:

```text
PFTL reserve proof + PFTL supply ledger
  -> verified bridge packet
  -> wrapped Ethereum NAVCoin
  -> Uniswap venue
```

That change matters. It means the external token can only exist because PFTL authorized it.

## What a NAVCoin is

A NAVCoin is a token tied to a verified reserve portfolio.

It is not a stablecoin. A stablecoin usually says, "one token is worth one dollar." A NAVCoin says, "one token is worth its pro-rata share of the verified net asset value."

If the reserve portfolio is worth `$28,000` and there are `4,000` valid units, the NAV is:

```text
$28,000 / 4,000 = $7.00 per unit
```

If the portfolio goes up, NAV goes up. If the portfolio goes down, NAV goes down. The promise is not "always one dollar." The promise is narrower:

- the reserve proof is fresh;
- the policy is known;
- liabilities are counted;
- supply is counted;
- stale or invalid proofs fail closed;
- minting cannot outrun the verified accounting.

## Proof of reserves: the balance sheet

Before any token movement matters, the system needs to know what backs the coin.

A proof-of-reserves run collects reserve evidence. That can include on-chain wallets, exchange balances, cash balances, collateral, borrowings, and venue positions. It also counts liabilities, because a wallet with `$10,000` of assets and `$3,000` of debt is not a `$10,000` reserve.

The basic formula is:

```text
verified net assets = reserves + cash - liabilities
```

The proof packet should include:

| Item | Why it matters |
|---|---|
| Reserve legs | Where the assets are and how they were measured. |
| Cash | Cash or stablecoin-like balances that are real reserve assets. |
| Liabilities | Borrowing or claims that reduce net assets. |
| Valuation policy | The rulebook for prices, haircuts, and treatment of positions. |
| Timestamp | So stale proofs cannot pretend to be current. |
| Proof hash | So the displayed number is tied to evidence, not copy. |

Cryptography cannot make a lying venue honest. If an exchange lies about a balance, the proof can only prove what was reported. But the proof can make the process checkable, repeatable, hash-bound, and fresh.

That is already a large improvement over "trust this dashboard number."

## PFTL finalizes the NAV epoch

Once the reserve proof exists, PFTL should turn it into protocol state.

That means validators check the packet and finalize an epoch. The epoch says:

- this is the asset;
- this is the verified net asset value;
- this is the NAV per unit;
- this is the timestamp;
- this is the supply denominator;
- this proof is fresh enough to use.

If the packet is stale, the chain should not let it silently power new minting. If the arithmetic is wrong, it should fail. If the proof does not match the registered policy, it should fail.

That is the first major gate:

```text
No fresh finalized NAV epoch -> no canonical mint.
```

## Native supply comes first

The clean model starts with native NAVCoin supply on PFTL.

A user can bring in counted cash, such as pfUSDC. PFTL can then mint or release native NAVCoin under the NAV policy.

Why not mint directly on Ethereum? Because that puts the venue in charge of existence. The venue should not decide what is real. It should only trade a representation of what PFTL already authorized.

So the native path is:

```text
pfUSDC or other counted input
  -> PFTL NAV policy
  -> native NAVCoin balance on PFTL
```

## Wrapping to Ethereum

Now suppose the user wants to trade on Uniswap.

The user does not need a new, separately backed Ethereum NAVCoin. They need a wrapped representation of the PFTL claim.

The bridge flow should look like this:

```text
1. Debit native NAVCoin on PFTL.
2. Finalize a PFTL bridge receipt.
3. Prove that receipt to Ethereum.
4. Mint the same amount of wrapped NAVCoin on Ethereum.
5. Mark the packet nonce as used so it cannot mint twice.
```

The wrapped token is normal enough for Ethereum wallets and Uniswap. But its mint function is not normal. It should only accept verified PFTL packets.

That is the second major gate:

```text
No verified PFTL packet -> no wrapped Ethereum token.
```

## The bridge is the hard part

The bridge is not just a messenger. A messenger can carry a packet, but it must not be trusted to decide whether the packet is true.

The Ethereum bridge needs to verify one of these:

- a direct PFTL finality proof;
- a succinct proof that PFTL finalized the packet;
- an optimistic packet with a real challenge window and bonded watchers;
- or, for an early controlled stage only, a threshold-signed packet clearly labeled as trusted.

Only the first two deserve the clean word "trustless." A threshold-signed bridge may be useful during a rollout, but it is not the final design.

A real bridge packet needs to bind every field that could be abused:

| Field | Why it matters |
|---|---|
| Source chain | Prevents using a packet from another chain. |
| Destination chain | Prevents replaying the packet somewhere else. |
| Asset id | Prevents swapping the asset meaning. |
| Amount | Prevents changing the mint size. |
| Recipient | Prevents redirecting the mint. |
| Nonce | Prevents replay. |
| Expiry | Prevents ancient packets from floating forever. |
| Receipt root | Ties the packet to finalized PFTL state. |

If any of that can be changed after PFTL debit, the bridge is unsafe.

## Uniswap is a market, not an oracle

Once wrapped NAVCoin exists on Ethereum, Uniswap can trade it against USDC.

That is useful. Uniswap gives:

- public liquidity;
- routing;
- market price;
- composability with Ethereum wallets;
- an easy way for outsiders to buy or sell.

But Uniswap does not know the NAV. It only knows pool balances and swap math.

So a good NAVCoin interface should show two numbers side by side:

```text
Canonical NAV/unit from PFTL: $X.XX
Current market price on Uniswap: $Y.YY
```

If market price is below NAV, that may be a discount, a liquidity problem, a stale proof problem, or a real risk signal. The pool itself cannot tell you which one. The NAV proof and bridge state are separate from the AMM.

## Returning from Ethereum to PFTL

The return path is the mirror image.

If a user wants to leave Ethereum and return to PFTL, the wrapped token should be burned on Ethereum. That burn creates a public event. PFTL then verifies the Ethereum event or accepts a properly challenged packet and releases or mints the native NAVCoin back on PFTL.

The return path is:

```text
wrapped NAVCoin burn on Ethereum
  -> Ethereum finality proof or accepted packet
  -> PFTL release of native NAVCoin
```

Again, the bridge should prevent replay. The same burn event cannot release twice.

## Where Orchard fits

Orchard is the privacy system.

If you have never heard of Orchard, think of it this way:

A normal public token transfer says:

```text
Alice paid Bob 10 tokens.
```

An Orchard-style shielded transfer says:

```text
Someone who owns a valid private note spent it once,
created a new valid private note,
and did not create money from nothing.
```

The chain can check the proof without learning the private note opening.

There are three core ideas:

| Term | Plain-English meaning |
|---|---|
| Note | A private coin-like record owned by a wallet. |
| Commitment | A public fingerprint of that private note. |
| Nullifier | A public "spent once" marker that prevents double spending. |

The nullifier is important. It lets validators reject a reused private note without knowing which note belonged to whom.

## A shielded NAVCoin swap

Now combine NAVCoin with Orchard.

A user can start with public pfUSDC on PFTL, shield it into a private note, and privately swap that note into a NAVCoin note.

The public chain sees:

- a valid shielded action;
- note commitments;
- nullifiers;
- proof validity;
- finality certificate.

The public chain does not need to see:

- which note was the user's;
- the note opening;
- the user's full route through the shielded pool.

That gives a private middle, but not a fully invisible universe. The edges are still accounting edges. If the user bridges out to Ethereum or redeems to USDC, the exit artifact becomes public because public settlement requires public fields.

## The gates

The correct architecture is mostly a list of places where the system must be willing to say no.

| Gate | What it blocks |
|---|---|
| Proof freshness gate | Stale NAV data powering new mints. |
| Reserve arithmetic gate | Wrong net asset values. |
| Supply gate | More valid supply than authorized. |
| Bridge finality gate | Minting from unfinalized source-chain messages. |
| Replay gate | Reusing a packet or burn event. |
| Nullifier gate | Spending the same private note twice. |
| Egress gate | Leaving privacy without a valid public exit. |
| Pause/halt gate | Continuing when proof, bridge, or policy status is unsafe. |

These gates are not user-hostile. They are the product. Without them, the token is just a wrapper with branding.

## A full canonical transaction

Here is the whole thing as one path:

```text
1. Reserves are measured.
2. A proof packet computes verified net assets.
3. PFTL finalizes a fresh NAV epoch.
4. User enters counted cash, such as pfUSDC.
5. PFTL mints or releases native NAVCoin under policy.
6. User optionally shields into Orchard.
7. User optionally swaps privately inside Orchard.
8. User wants Ethereum venue access.
9. PFTL debits native NAVCoin and creates a bridge export packet.
10. Ethereum verifies PFTL finality or a succinct proof.
11. Ethereum bridge mints wrapped NAVCoin.
12. Wrapped NAVCoin trades on Uniswap against USDC.
13. User can burn wrapped NAVCoin to return to PFTL.
14. PFTL verifies the return and releases native NAVCoin.
```

The user-facing version can be simple: buy, shield, swap, bridge, trade, return.

The protocol version is stricter: prove, finalize, mint, debit, verify, wrap, trade, burn, verify, release.

## What needs to be built

The old pool has been cleared out. The correct version needs a new contract stack.

At minimum:

1. **A new bridge-aware Ethereum wrapped NAVCoin.** Not the retired standalone demo token.
2. **An Ethereum bridge controller.** It mints only after verified PFTL packets and burns for return.
3. **A PFTL finality verifier on Ethereum.** Direct or succinct proof preferred.
4. **A PFTL inbound verifier for Ethereum burns.** PFTL must verify return events or accepted packets.
5. **Replay protection.** Every packet and burn event is consumed once.
6. **Proof freshness adapter.** Interfaces should show canonical PFTL NAV, not stale Ethereum mirror data.
7. **A new Uniswap pool.** The pool trades the wrapped token, not the old standalone token.
8. **Dashboard labels.** Users should see "canonical NAV," "market price," "wrapped supply," "bridge status," and "proof freshness" as separate concepts.

There can be staged versions. A threshold-signed bridge can help test UX. An optimistic bridge can reduce trust if watchers are real. The final target is direct or succinct verification of PFTL finality.

## What this does not claim

This is a design explanation, not a statement that the final bridge is deployed.

It does not claim:

- a production trustless bridge exists today;
- the old Ethereum a651 token can be safely upgraded in place;
- Uniswap price equals NAV;
- proof of reserves eliminates source dishonesty;
- Orchard privacy works without a real anonymity set;
- a relayer is a trust anchor;
- a threshold-signed bridge is the final trustless design.

The claim is narrower: if NAVCoin is going to be canonical, PFTL must be the truth layer, external tokens must be bridge-verified representations, and privacy must sit inside a proof-checked transaction path rather than replacing public accounting.

## Why this is worth doing

The correct version is more work than deploying another ERC-20 and seeding a pool.

But it gives a clean answer to the core question:

> Why should anyone believe this token represents the verified NAVCoin supply?

Because every wrapped unit can be traced to a finalized PFTL debit, every native unit sits under a finalized NAV epoch, every proof has freshness rules, every packet has replay protection, and every private movement still has a proof the chain can check.

That is the difference between "a token with a NAV website" and a canonical NAVCoin transaction.

