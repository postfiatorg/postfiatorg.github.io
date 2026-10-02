---
title: "Economics of the NAVCoin"
date: 2026-10-02T00:00:00Z
draft: false
summary: "A NAVCoin connects a provable portfolio to markets anchored on its net asset value. Three pieces make that economically useful: one standard proof of reserves for any strategy, standard liquidity around the proven number, and private swaps in size at NAV."
aliases:
  - /economics-of-the-navcoin/
  - /posts/economics-of-the-navcoin/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - NAVCoin
  - Proof of Reserves
  - Liquidity
  - Privacy
  - OTC
---

*Part of the NAVCoin series. The [proposal](/blog/navcoin-proposal/) defined an asset whose supply is gated by machine-verified reserves. [Proof of leverage](/blog/proof-of-leverage/) built the reserve evidence. [One portfolio, many access venues](/blog/navcoin-ethereum/) turned that proof into a token architecture. The [OTC MVP](/blog/navcoin-otc-mvp-proven/) ran the full swap round trip on live networks. This post explains the economics of the combined design: who gets what, and what makes it work.*

A NAVCoin is an asset built to trade around its latest proven net asset value (NAV). It does not target a $1 peg. Its reserve is proven every epoch, and its NAV is a number the ledger has checked.

That checked number is an accounting anchor. Turning it into an executable price takes three mechanisms: minting and burning at NAV, liquidity concentrated around NAV, and arbitrage between the two.

Three pieces make that economically useful:

1. **One standard proof of reserves, whatever the strategy.** However complicated the reserve is, the market sees the same few numbers, checked the same way.
2. **Standard liquidity around the proven number.** A common market structure connects minting and burning, a public pool and a keeper.
3. **Private swaps in size at NAV.** A $10 million order need not pass through a $2 million public pool. It can use the primary market, with execution costs attached to the trade.

![The three pieces of NAVCoin economics: a standard proof of reserves at the base, standard liquidity built on the proven NAV, and private swaps in size at NAV on top.](/blog/navcoin-economics-overview.svg)

## The problem NAVCoins solve

Useful strategies can be hard to own.

Take a market-neutral carry trade: own a stock and short its perpetual future, and collect the carry and basis between them. The idea fits in one sentence. Running it does not. You need accounts at a tokenized-stock venue and a perpetuals exchange, margin management, rebalancing, and a way to show anyone else that the positions exist.

A NAVCoin makes that evidence reusable. The positions live in accounts that belong only to that NAVCoin. A cryptographic proof shows what those accounts hold. Post Fiat's validators check the proof before accepting the epoch's NAV. Markets can then use that checked number rather than an operator's statement.

## 1. A complex proof of reserves, in one standard shape

A strategy reserve is messy. Our first strategy NAVCoin, BMNRC, holds three things in three places:

- BMNR stock in its own Felix account, on Ethereum;
- a matching BMNR perpetual short in its own Hyperliquid account;
- USDC in its own cash wallet.

Other NAVCoins hold other things: Aave positions, spot crypto, perpetual books, Monero, NEAR balances.

The reserve proof absorbs that mess. A zero-knowledge program (SP1) reads every account at a fixed block, values each position under a published valuation policy, nets assets against liabilities, and outputs one **reserve packet**:

| Field | Meaning |
|---|---|
| `V` | Verified net assets, in the unit of account |
| `S` | Circulating supply of the NAVCoin |
| `N` | NAV per unit, `floor(V / S)` at the asset's precision |
| Epoch | Which reserve snapshot this is |
| Policy hash | Which valuation rules produced `V` |
| Profile | Which proof program and which accounts are in scope |

Validators verify the proof before accepting the packet. On v1 proof profiles, the chain refuses a packet whose NAV does not equal `floor(V / S)` once supply exists. It also refuses trades priced on a stale packet. NAV is the output of a checked computation, not a figure the issuer types in.

A verified packet establishes what the named accounts held at the snapshot block, how the published policy valued those positions and liabilities, and the resulting NAV at the asset's precision.

![A standard reserve proof: accounts on several venues are read at a fixed block, valued under a published policy, and compressed into one reserve packet that every validator checks before NAV is accepted.](/blog/navcoin-economics-proof.svg)

**The standardization is the economic point.** A shipping container lets cranes, ships and trucks handle different cargo in the same way. A reserve packet does the same for strategy evidence. A wallet, exchange, lender or market maker can read `N` and check the packet's verification and freshness through one interface.

One integration supports every strategy that can be proven. An allocator still evaluates the return source, venues and capacity, but no longer needs a different process for checking each operator's reserve arithmetic. The ledger answers that question every epoch under the stated policy.

## 2. Standard liquidity around the proven number

The liquidity design connects three routes around `N`.

**The primary market at NAV.** New units are minted against new assets at NAV; units are burned for their pro-rata portion of the reserve. The executable entry price is NAV plus the disclosed fee and position-building costs. The executable exit value is NAV minus applicable fees and unwind costs.

**A public pool near NAV.** For instant trades, the design uses a public pool. For BMNRC, that is a wrapped token on Ethereum, paired with USDC on Uniswap v4. Liquidity sits in a narrow band around NAV rather than across every possible price.

**A keeper that closes the gap.** Above NAV, the keeper sells into the pool. Below NAV, it buys. It then squares its inventory through the primary market.

While the proof is fresh, the primary market is open and the keeper has capital, that round trip creates an incentive to close price gaps. Its cost includes fees, position execution, gas, a bridge proof and exposure during about 30 minutes of settlement. Those costs define the keeper's economic trading band—not the reserve proof alone. When the proof goes stale, the ledger stops pricing trades on the old number, and the keeper stops with it.

![Standard liquidity: the primary market mints and burns at NAV, the public pool concentrates liquidity in a band around NAV, and a keeper sells above NAV and buys below, squaring its inventory at NAV.](/blog/navcoin-economics-pools.svg)

**Market-neutral NAVs can make this capital-efficient.** Offsetting stock exposure with a perpetual short reduces sensitivity to the stock's direction. Carry and basis still change NAV. When that anchor moves slowly, a narrow band can offer small slippage with modest capital.

**The interface repeats; the economics remain strategy-specific.** The design reuses a route template, pool structure and keeper logic. Each strategy's NAV movement, execution costs and capacity determine how tightly that structure can operate.

**A $10 million mint, from snapshot to settlement.** Consider a NAVCoin with a $2 million public pool:

1. **Snapshot.** The accepted packet reports `V`, `S` and `N`. While it remains fresh, the ledger permits pricing against it.
2. **Quote.** The buyer commits $10 million of net reserve value, plus the disclosed fee and actual cost of building the extra positions. “At NAV” describes the unit-price anchor, not the buyer's total bill.
3. **Execution and mint.** At `N`, $10 million of net value supports `$10 million / N` new units, subject to asset precision. When net assets and supply increase in that proportion, entry itself leaves NAV unchanged before rounding.
4. **Settlement and next proof.** The next proof values the enlarged book. For the entry to avoid diluting existing holders, the buyer's payment must cover the actual execution cost, including adverse changes while constructing the added positions. A cost estimate alone does not establish that result.

A burn reverses the calculation: the holder receives the NAV value of the units burned, less the actual cost of unwinding the corresponding positions and applicable fees. The public pool need not absorb either trade.

The keeper needs capital to carry inventory through its own round trip. If minting or burning is unavailable, that route cannot close a pool-price gap. Exact quote terms for execution and settlement are listed in Scope; the roughly 30-minute bridge settlement is not a promise that a $10 million strategy order finishes in that time.

**Who earns what:**

| Participant | Earns | From |
|---|---|---|
| Holder | The strategy's net return | Carry, basis or whatever the reserve earns |
| Liquidity provider | Pool fees | Instant trades through the band |
| Keeper | The pool-to-NAV spread, less round-trip costs | Closing gaps through the primary market |
| Validators and PFT | Network fees, paid in PFT | Epoch finalization, proof checks, minting and burning, private swaps |

## 3. Private swaps in size at NAV

Primary-market capacity is different from public-pool liquidity.

A $10 million purchase through a $2 million pool would move its price far above NAV, if it filled at all. A primary-market mint instead expands the strategy: more stock bought, more perpetuals shorted. Its capacity comes from those underlying markets, not the pool.

On Post Fiat, the swap can also settle inside a shielded pool on PFTL. Amounts, asset and counterparties are hidden from public view, while the reserve stays provable. The design combines private block trading with a published, machine-checked valuation anchor.

![Private swap in size: a $10 million order through a $2 million public pool moves the price far from NAV, while a private mint uses the primary market and leaves the public pool untouched.](/blog/navcoin-economics-otc.svg)

**Three rules govern the economics:**

1. **The large buyer pays the entry's execution cost.** Existing holders remain undiluted by entry only when the net value added supports the units minted at the applicable NAV.
2. **Every NAVCoin publishes its capacity.** Large tickets fill over a stated time, against an agreed quote, within the depth of the strategy's markets.
3. **Burning uses the same cost allocation.** A large holder exits privately at NAV minus the cost of unwinding their portion, rather than selling into the public pool.

“Entry leaves NAV unchanged” is an accounting condition, not a claim that the strategy stops earning or losing value during execution.

Swaps can also run between NAVCoins at the ratio of their proven NAVs, privately, in one settlement. We ran that cross-NAVCoin swap on live networks in June ([OTC MVP](/blog/navcoin-otc-mvp-proven/)).

Dark pools provide private equity trading; private on-chain exchanges provide private crypto trading. The NAVCoin design brings private settlement together with epoch-by-epoch reserve evidence and a NAV-based primary market.

## Why this needs Post Fiat

Each component can be built separately. This architecture uses Post Fiat to put three responsibilities in one settlement layer:

- **Check reserve proofs as part of consensus,** making accepted NAV a ledger property rather than an app's assertion.
- **Enforce NAV rules natively:** tie minting to proven NAV, halt stale-NAV trading, and track supply across the asset's chains.
- **Settle privately** while keeping reserves auditable.

That is Post Fiat's role in this design, not a claim that no other architecture could combine those functions.

Ethereum, Solana and other chains are distribution venues for wrapped units and public pools. PFTL is where reserve proofs, NAV rules and private settlement come together. Activity elsewhere connects back to minting, burning and settlement on PFTL.

## Scope

- **Valuation and custody.** Proof establishes snapshot holdings and policy-based value, not stressed liquidation proceeds or venue safety. Reserve positions remain at their venues; the [counterparty-risk post](/blog/navcoin-counterparty-risk/) prices that exposure.
- **Timing and liquidity.** Positions, basis and execution costs can change between proofs. Delta neutrality does not make NAV constant. Stale-proof halts stop use of an old anchor; they do not guarantee an exit. Keeper capital and primary-market availability determine whether arbitrage can operate.
- **Quote terms.** Every quote prices against a finalized NAV no more than 100 blocks old, and it shows the fee, the available amount and the route state before the buyer signs. Exit capacity is the smallest of the policy limit, the unencumbered reserve principal and the per-order limit. In its first release, BMNRC's route issues at most its opening `V` per epoch, so larger tickets fill across several epochs.
- **Capacity and visibility.** Capacity comes from the strategy's markets. Private swaps hide ownership transfers; the strategy's trades at public venues remain visible.
- **Status.** A666 runs on PFTL today, with proven reserves and a wrapped Uniswap market. BMNRC, the first stock-and-perpetual NAVCoin, is opening this week. Private swaps at size move from devnet qualification to live operation next. The combined market structure above describes the design; the live swap round trip does not establish production capacity for a $10 million order.
