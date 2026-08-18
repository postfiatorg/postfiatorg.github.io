---
title: "Trustless UltraShort Tokens"
date: 2026-08-18T00:00:00Z
url: "/blog/trustless-ultrashort-tokens/"
type: "blog"
breadcrumb_label: "Blog"
breadcrumb_url: "/blog/"
summary: "A proposal to turn an autonomously managed Hyperliquid short-perpetual position into a Tier-4 NAVCoin that can be held in MetaMask, traded in an AMM, and redeemed against proven strategy equity."
description: "Trustless UltraShort Tokens are proposed NAVCoin series backed by isolated, onchain perpetual positions whose collateral, execution, funding, NAV, supply, and redemption are verified end to end."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Hyperliquid
  - Leveraged ETFs
  - Perpetual Futures
  - Proofs
  - Uniswap
  - PFTL
draft: false
---

> **Status: research proposal, not a deployed product.** “Trustless” has a
> deliberately narrow meaning here. The target design removes an operator from
> custody, trading, bridge, share-supply, and redemption decisions. It does not
> make Samsung's price, Hyperliquid's consensus, a HIP-3 deployer's oracle, USDC,
> smart contracts, or proof systems infallible. No token should be described as
> Tier 4 until the full subscription-and-redemption path has passed adversarial
> tests with live funds and no privileged fallback.

## The proposal in one paragraph

A Trustless UltraShort Token is a fungible NAVCoin backed by one isolated,
autonomously managed short-perpetual strategy. A user chooses an underlying and
a leverage policy—“short Samsung at 2×,” for example—deposits USDC, and receives
an ERC-20 in MetaMask after contracts have swept the collateral into HyperCore,
opened the corresponding `xyz:SMSN` short, and proved the resulting position and
equity to PFTL. The token's NAV moves with realized and unrealized short P&L,
funding, fees, and trading costs. Holders can transfer it, use it in DeFi, or
trade it in a Uniswap-compatible pool. Redemption locks the token, closes the
holder's pro-rata share of the perp position, returns USDC, and only then reduces
global supply. Keepers may submit transactions, but immutable policy—not a
manager—decides what may be traded, where collateral may go, and when shares may
exist.

The product is best understood as **a rolling onchain perp position packaged as
a NAVCoin**, not as an ETF placed onchain and not as a synthetic token whose
issuer promises to hedge somewhere else.

## The user experience

The intended wallet flow is four choices and one confirmation:

```text
Underlying       Samsung Electronics (xyz:SMSN)
Direction        Short
Leverage policy  Target 2.0×, rebalance band 1.8×–2.2×
Spend            1,000 USDC

Estimated opening cost       1.31 USDC
Current funding to shorts     live signed rate
Realized 90-day funding       +12.73% of constant 1× notional
Estimated liquidation buffer  shown from current venue parameters
Receive                        ~998.69 usSMSN-2x at $1 initial NAV
```

After confirmation, the wallet shows honest stages rather than a spinner:

```text
USDC escrowed
    -> credited to the strategy on HyperCore
    -> Samsung short filled inside the slippage limit
    -> position and equity proven
    -> NAVCoin shares issued
    -> ERC-20 delivered to MetaMask
```

If the order cannot fill within the disclosed limit, no tradable token is
minted. The user receives a refund claim against the still-segregated cash. A
backend outage cannot turn “pending” into an unbacked asset.

The wallet shows both the live signed rate and realized cumulative funding over
fixed windows. It does not substitute one volatile hour for the historical cash
flow or annualize that hour as an expected yield.

## Why build this now

Leveraged and inverse exposure is no longer a niche product category. Direxion's
2026 review reports that the US leveraged-fund universe nearly quadrupled over
five years, reached **$160.5 billion** of assets by the end of November 2025, and
was on pace for **16.9 billion shares** of 2025 trading volume versus **7.3
billion** in 2024. It estimates the category represented roughly 8% of all US
stock-exchange trading activity in 2025. Those are issuer estimates, but
independent venue data point in the same direction: IEX data reported by ETF.com
in July 2026 put leveraged products at roughly **40% of ETF trading volume**, with
seven leveraged products among the ten most actively traded ETFs. The
denominators differ—one is all exchange activity and one is ETF activity—but the
message is consistent: traders already pay heavily for packaged leverage.[^direxion]
[^etfcom]

### Bloomberg same-store check

We also checked a deliberately fixed basket of six long-running US products:
TQQQ, SQQQ, SOXL, SOXS, UPRO, and SPXU. The basket includes three bull/bear
pairs, was fixed before measuring the result, and avoids attributing all growth
from new launches to organic trading growth.

| Jan. 1 through Aug. 18 | Average daily dollar volume | Change from prior sample |
|---|---:|---:|
| 2024 | $9.82B | — |
| 2025 | $12.94B | +31.8% |
| 2026 | $19.52B | +50.9% |

Bloomberg reported **$72.76 billion** of current combined fund assets for those
six products on August 18, 2026. The volume calculation is Post Fiat's:
`PX_LAST × VOLUME`, summed by trading day over the identical calendar window.
The fund-asset figure is Bloomberg's `FUND_TOTAL_ASSETS`. This is a six-fund
bellwether check, not a total-market estimate; it excludes closed funds, new
products, ETNs, and every issuer outside the selected series. Bloomberg data are
proprietary, so this proposal publishes the method and derived aggregates rather
than redistributing the raw feed.

The demand is also becoming more granular. Single-stock leveraged products now
cover semiconductor, software, crypto-equity, and thematic names, while borrow
demand around those products can itself be material. S&P Global reported in
2026 that leveraged and inverse products were taking a growing share of ETF
launches and that securities-lending demand around prominent single-stock funds
had become economically meaningful.[^spglobal]

## What the customer is buying

The customer is buying a transferable claim on the net equity of a transparent
short strategy:

```text
strategy collateral
+ realized short P&L
+ unrealized short P&L
+ funding received
- funding paid
- trading fees and slippage
- protocol and proof fees
- finalized liabilities and safety haircuts
= strategy net equity
```

If Samsung falls 5%, a perfectly maintained 2× short begins with approximately
a 10% gross gain before funding and costs. If Samsung rises 5%, it begins with
approximately a 10% gross loss. Rebalancing, compounding, gaps, funding, mark
methodology, and execution make the actual return different. Like a daily-reset
leveraged ETF, it is path dependent. Tokenization does not repeal volatility
drag or liquidation.

What changes is the control surface:

| Conventional packaged short | Trustless UltraShort target |
|---|---|
| Broker and fund sponsor execute the hedge | A fixed contract policy submits orders |
| Shares exist because an authorized participant creates them | Shares exist only after position proof |
| NAV and holdings arrive on a reporting cadence | Strategy equity is finalized from committed onchain state |
| Held in a brokerage account | ERC-20 held in MetaMask |
| Exchange-hours secondary market | AMM transferability, subject to chain and pool liveness |
| Sponsor controls the operating perimeter | Governance can register a version; it cannot redirect an existing immutable series |

This is not automatically a better instrument for every investor. The target
customer values bearer ownership, transparent funding, programmatic collateral,
continuous transfer, and proof-gated issuance enough to accept perp, oracle,
smart-contract, and crypto-market risks.

## It is a specialized NAVCoin

The [NAVCoin proposal](/blog/navcoin-proposal/) defines a token as a pro-rata
claim on a verified reserve portfolio. The
[canonical collateralization model](/blog/navcoin-collateralization/) adds the
essential separation between primary issue/redemption and secondary trading.
Trustless UltraShort keeps that model and narrows the reserve portfolio to one
strategy account and one immutable mandate.

Each series registers:

```text
SeriesConfig {
  underlying_market       // e.g. xyz:SMSN
  direction               // short
  collateral_asset        // linked HyperCore/HyperEVM USDC
  leverage_policy         // target or deterministic range
  rebalance_band
  max_leverage
  min_liquidation_buffer
  max_order_slippage
  max_position_vs_oi
  max_position_vs_depth
  mark_and_oracle_policy
  funding_policy
  fee_policy
  proof_profile
  strategy_contract
  permitted_core_actions
  representation_contracts
}
```

One series has one equity pool, one policy, one NAV, and one global supply. Its
shares can appear natively on PFTL and as wrapped units on HyperEVM or another
registered EVM, but those are representations of the same economic supply—not
additional claims.

Uniswap is the secondary market. It does not set primary NAV, authorize minting,
count as reserve equity, or change global supply. A discount or premium can
exist; permissionless issue/redemption arbitrage is what should pull the pool
toward NAV.

## A fungible token cannot contain private leverage settings

“Let the user choose any leverage” sounds simple but violates fungibility if two
holders of the same token can have different claims. The leverage setting must
belong to the series, not to an individual balance.

There are two viable product forms:

1. **Fixed-target series.** `usSMSN-2x` targets 2.0× short exposure and only
   rebalances outside a published band, such as 1.8×–2.2×.
2. **Adaptive-range series.** `usSMSN-CARRY` may move between, for example,
   1.0× and 2.5× under a deterministic rule tied to funding, liquidity,
   volatility, and liquidation buffer. Every holder owns the same policy.

The wallet may present a leverage slider. Underneath, that slider selects an
existing series or permissionlessly deploys a new series from an audited factory.
It must not silently mix unlike leverage claims in one ERC-20.

### Deterministic leverage controller

For strategy equity \(E_t\), signed position quantity \(Q_t < 0\), and the
registered oracle price \(P_t\):

\[
L_t = \frac{|Q_t|P_t}{E_t}
\]

A fixed-target controller trades only when \(L_t\) leaves the registered band.
An adaptive controller computes a target using bounded integer arithmetic:

\[
L_t^* = \operatorname{clamp}(L_{base} + C(f_t) - R_t,
L_{min}, L_{max})
\]

where \(C(f_t)\) is a capped funding adjustment and \(R_t\) is a deterministic
risk deduction derived from proven depth, oracle deviation, volatility, and
liquidation buffer. The exact functions and lookback windows are series state.
No model, keeper, or UI may improvise them.

The controller should scale toward the high end only when shorts are being paid
and the risk checks remain healthy. Negative funding pushes toward the low end.
Funding is an input to leverage, never a promised yield.

## The Samsung example, using live venue state

At 13:57 UTC on August 18, 2026, Hyperliquid's public
`metaAndAssetCtxs` endpoint reported the following for `xyz:SMSN`:

| Field | Live snapshot |
|---|---:|
| Oracle price | $186.02 |
| Mark price | $185.12 |
| 24-hour notional volume | $120.37M |
| Open interest | 261,653.488 SMSN, about $48.67M at oracle |
| Maximum venue leverage | 10× |
| Margin mode | Isolated only |
| Realized 90-day short funding | +12.73% of constant 1× notional |

Hyperliquid's funding convention is positive when longs pay shorts.[^funding]
Over the fixed 90-day test, Samsung shorts received **12.73% of constant 1×
notional**. At constant 2× exposure on $1,000 of starting equity, that is
approximately **$254.54 of realized funding cash flow** before price P&L,
rebalancing, fees, slippage, and liquidation effects.

This snapshot demonstrates that a usable market exists, not that it is safe or
that its current liquidity supports arbitrary token size. The series must cap
its position against open interest and proven executable depth, not merely the
venue's advertised 10× maximum.

### The economic edge must survive a market-wide test

Funding is not incidental to the instrument. Hyperliquid specifies a default
interest component equivalent to 11.6% annualized paid to shorts when premium is
neutral; the premium component then moves the hourly rate in either direction,
and HIP-3 deployers may apply a funding multiplier.[^funding] Payments are
peer-to-peer rather than a fee retained by Hyperliquid. An UltraShort series
passes the resulting cash flow directly into NAV.

Samsung alone is not credible evidence for that edge. We therefore applied one
fixed 90-day rule to the relevant product universe: HIP-3 `xyz:` markets in the
local Hyperliquid archive. A market required at least 90% of the 2,160 expected
hourly observations and a final observation no more than six hours before the
July 2, 15:00 UTC cutoff.

| Same-window HIP-3 funding test | Result |
|---|---:|
| Eligible markets / frozen universe | 47 / 84 |
| Settled market-hours | 101,261 |
| Market-hours in which shorts received funding | 75.30% |
| Markets with positive net 90-day short funding | **85.11%** |
| Median 90-day funding, constant 1× notional | **+2.50%** |
| 25th–75th percentile, constant 1× | **+0.80% to +3.84%** |
| Equal-market mean, constant 1× | **+2.78%** |

The HIP-3 result spans single stocks, equity indices, commodities, and FX. At
constant 2× notional, its median funding contribution would have been **+5.01%
of starting equity over 90 days** before underlying-price P&L and every other
cost. This is the broad economic evidence for the product; it is not an
annualized projection.

The equal-market table answers a breadth question, not a capacity-weighted
portfolio question. A tiny market receives the same weight as a market that
traded billions of dollars. To test the economically relevant version, we
matched the 30 US-listed stocks and ETFs in the eligible HIP-3 panel to
IBorrowDesk's historical Interactive Brokers stock-loan observations and
weighted them by their HIP-3 notional volume over the same window. The matched
set represented **$40.19 billion** of venue-reported notional. Its
volume-weighted 90-day funding paid shorts **+2.56% of constant 1× notional**,
close to the +2.74% equal-market mean for those same 30 instruments. Twenty-eight
of the 30 paid shorts positive net funding. Volume weighting therefore
strengthens rather than reverses the equity-perp result.

### Against the actual alternative: borrow the stock

The relevant comparison is not a hypothetical instrument with zero carry. A
conventional short seller borrows shares, pays the stock-loan fee, posts margin,
and may receive interest on the cash collateral created by the short sale.
IBorrowDesk publishes historical indicative fee, availability, and rebate
observations sourced from Interactive Brokers.[^iborrowdesk] IBKR calculates the
daily gross borrow charge as collateral value multiplied by the annual fee rate
and divided by 360.[^ibkrborrow] Its quoted rebate rate is the applicable
benchmark rate minus the charge for borrowing the shares.[^ibkrrebate]

For each matched ticker, we forward-filled the last available daily observation
across weekends and holidays and accumulated 90 calendar days on IBKR's
360-day convention. The result, per $100 of constant short notional, was:

| Same-window, volume-weighted carry | HIP-3 perp short | Direct stock short |
|---|---:|---:|
| Funding or stock-loan rebate proxy | **+$2.56** | **+$0.83** |
| Gross stock-borrow fee alone | — | -$0.076 |
| HIP-3 advantage versus rebate proxy | **+$1.73** | — |

At constant 2× exposure on $1,000 of starting equity, this isolates about
**$51.11 of HIP-3 funding** against **$16.61 of stock-loan rebate proxy**, a
**$34.50 difference over 90 days** before price P&L and all other costs. If an
account received no interest on its short-sale proceeds, the corresponding
HIP-3 advantage over the gross borrow charge would be about $52.63.

| Market | HIP-3 notional | HIP-3 short funding | Stock rebate proxy | HIP-3 minus stock |
|---|---:|---:|---:|---:|
| MU | $10.46B | +4.01% | +0.84% | **+3.17%** |
| NVDA | $3.92B | +2.86% | +0.84% | **+2.03%** |
| CRWV | $482M | +5.43% | +0.83% | **+4.59%** |
| HIMS | $291M | +9.68% | +0.75% | **+8.93%** |
| TSLA | $1.89B | +0.87% | +0.83% | +0.04% |
| AAPL | $541M | -0.08% | +0.84% | **-0.92%** |
| EWJ | $61M | -1.32% | +0.62% | **-1.94%** |

Twenty-five of the 30 matched HIP-3 markets beat the stock-loan rebate proxy;
AAPL, EWJ, EWY, MSTR, and TSM did not. This is not evidence that liquid US
stocks are expensive to borrow—they were generally cheap in this sample. The
economic claim is more specific: **during this fixed window, long demand in the
matched HIP-3 markets paid shorts a funding premium materially larger than both
the gross cost of sourcing shares and the cash-collateral rebate available to a
conventional stock borrower.**

The rebate comparison is deliberately favorable to the stock short but still
not an account statement. Actual proceeds interest depends on broker, account
size, balance tier, currency, and collateral treatment. Direct stock shorts also
owe manufactured dividends and face recalls, margin rules, market hours, and
corporate actions; perp shorts instead face basis, oracle, venue, liquidation,
and continuously variable funding risk. Underlying-price returns cancel only
approximately because the HIP-3 contract may not track the cash security
perfectly. The published
[matched comparison CSV](/research/trustless-ultrashort/ibkr-comparison-90d-through-20260702.csv)
contains every included ticker and derived field. Its SHA-256 is
`8e8f5e4cac739f4a94522f606beb684f5b83adc596e1d2280351e9c439e25ca7`.

Samsung was among the strongest markets: `xyz:SMSN` ranked third among the 47
eligible HIP-3 markets at **+12.73% of constant 1× notional** in the comparable
90-day window. Its longer 4,310-hour history through August 18 summed to
**+17.25% of constant 1× notional**.

These figures isolate realized funding cash flow. Price P&L, rebalancing, fees,
slippage, and liquidation effects are separate components of token NAV. The
measured funding conclusion is direct:
**shorts were paid across the broad HIP-3 panel and in the capacity-weighted US
equity subset: 85.11% of eligible HIP-3 markets were net positive, while the 30
matched US-listed markets produced +2.56% volume-weighted funding on constant
1× notional. A proof-gated token can pass that cash flow into NAV instead of
burying it.**

A conventional inverse ETF is not literally zero carry: swaps embed financing
and borrow, collateral may earn interest, and expenses reduce NAV. Its holder
sees those effects netted together. UltraShort makes the hourly funding leg
separately observable and policy-addressable. The immutable
[per-market universe CSV](/research/trustless-ultrashort/funding-universe-90d-through-20260702.csv),
[universe summary](/research/trustless-ultrashort/funding-universe-summary-through-20260702.json),
and [universe analysis script](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/scripts/analyze_ultrashort_funding_universe.py)
publish the inclusion rule, every eligible market result, distributions, source
hashes, and calculations. The derived CSV SHA-256 is
`d3f5902cd8a957b1cfdd46876716349ea288903365cfa838c7811ef5a25af1aa`.
Samsung's complete [hourly case file](/research/trustless-ultrashort/smsn-funding-hourly-through-20260818.csv)
and [case summary](/research/trustless-ultrashort/smsn-funding-summary-through-20260818.json)
remain published for observation-level audit.

## Trustless collateral sweep

The hardest requirement is not wrapping the position. It is proving that every
dollar accepted for shares was actually placed under the series mandate without
giving an operator a withdrawal key.

The clean initial deployment keeps both strategy settlement and the wrapped
token on **HyperEVM**. MetaMask supports HyperEVM, and a Uniswap-compatible AMM
can run there. This avoids pretending that Hyperliquid's current native Arbitrum
withdrawal API is callable by an autonomous contract when it is not.

Hyperliquid's live `spotMeta` response listed canonical USDC with a linked
HyperEVM contract on August 18, 2026. That makes the proposed EVM ↔ Core route
plausible, not proven. Hyperliquid's own documentation warns that linking alone
does not validate ERC-20 bytecode or guarantee that the system address holds
sufficient supply.[^coreevm] The launch proof profile must pin the USDC contract,
verify its code and system balance, and demonstrate both transfer directions
before accepting deposits.

```text
                         HYPERLIQUID (one HyperBFT state)

 MetaMask            HyperEVM contracts                 HyperCore
 --------            ------------------                 ---------
 USDC -------> SubscriptionEscrow
                         |
                         | ERC-20 transfer to the
                         | linked token system address
                         v
                                                  strategy spot USDC
                                                         |
                         CoreWriter policy --------------+
                                                         v
                                                  xyz perp collateral
                                                         |
                                                  short xyz:SMSN
                                                         |
                         HyperCoreReader <---------------+
                              |
                    finalized receipt proof
                              v
                         PFTL NAV state
                              |
                    Tier-4 issuance proof
                              v
 MetaMask <------- wrapped usSMSN ERC-20 -----> AMM pool
```

Hyperliquid's current read precompiles expose HyperCore state to HyperEVM and
guarantee that returned values match HyperCore when the EVM block is built.
CoreWriter allows a contract to place limit orders, cancel them, transfer USD
between spot and perp classes, and send spot assets on behalf of the contract's
own HyperCore account.[^corewriter] The strategy address must be initialized on
HyperCore before it sends a CoreWriter action; initialization and an action in
the same EVM block fail under the documented ordering.[^timing]

### Subscription state machine

1. The user transfers HyperEVM USDC into a series-specific escrow with minimum
   shares, maximum slippage, and deadline.
2. The escrow moves linked USDC to the same contract's HyperCore spot balance.
3. The controller transfers the allowed amount to the registered HIP-3 perp
   class and places a bounded order through CoreWriter.
4. A reader contract records position, collateral, account equity, funding,
   mark, oracle, and market identifiers in a HyperEVM receipt.
5. A proof opens that receipt against the HyperEVM `receiptsRoot` and anchors
   the header to HyperBFT finality. PFTL checks the pinned reader, market,
   strategy address, freshness, fill, leverage, and arithmetic.
6. PFTL finalizes the new NAV and share supply. A Tier-4 PFTL proof authorizes
   the representation contract to mint shares to the subscriber.

Steps span blocks and are therefore not atomic in the database sense. Safety
comes from the state machine: cash is segregated while pending; a failed or
expired order cannot produce transferable shares; retries are idempotent; every
receipt identifier is single-use.

### Redemption state machine

1. The holder locks wrapped shares in `RedemptionEscrow` with a minimum USDC
   payout and deadline. Locking is reversible until execution begins.
2. PFTL verifies the lock and authorizes a proportional, reduce-only close.
3. The controller closes the corresponding share of the short through
   CoreWriter and moves released USD from the perp class to spot.
4. The controller sends spot USDC to its linked HyperEVM system address. The
   corresponding ERC-20 is credited on HyperEVM.
5. A new receipt proves the reduced position and returned cash. PFTL finalizes
   the lower global supply; the representation contract burns the locked shares
   and pays the actual net USDC proceeds.

If a close cannot execute within the user's limit, the token unlocks instead of
being destroyed. Once a position has been reduced, the resulting cash remains a
reserve asset owed to that redemption until it can be paid. A proof outage may
delay completion; it may not give governance or a keeper the cash.

### Why Ethereum/Arbitrum cash-out is a separate route

Hyperliquid's native bridge credits deposits sent from Arbitrum, but its current
withdrawal flow requires a user-wallet `withdraw3` signature and validator
processing.[^bridge] CoreWriter does not expose that withdrawal action. Giving a
server or committee the strategy's signing key would defeat the proposal.

The initial product therefore redeems to USDC on HyperEVM. A later Ethereum or
Arbitrum route must be one of:

- a proof-verified bridge whose contracts can lock/burn HyperEVM USDC and release
  destination USDC without an operator signature; or
- a permissionless solver market in which a solver pays destination-chain USDC
  and claims the proven HyperEVM proceeds through an atomic claim protocol.

The wallet may offer those routes only with separate trust, fee, liquidity, and
timing disclosures. “Tier-4 UltraShort redemption” must not inherit a Tier-3
cash-out hidden behind the same button.

## NAV and supply accounting

At finalized epoch \(t\), strategy net equity is:

\[
E_t = C_t + RP_t + UP_t + F_t - X_t - H_t
\]

where \(C\) is collateral, \(RP\) realized P&L, \(UP\) unrealized P&L, \(F\)
net funding, \(X\) explicit fees and execution costs, and \(H\) registered
haircuts or liabilities. With valid global supply \(S_t\):

\[
NAV_t = \frac{E_t}{S_t}
\]

PFTL should consume the HyperCore account-equity value committed through the
reader, then cross-check it against position, mark, oracle, collateral, and
funding fields under the proof profile. All monetary arithmetic uses bounded
integers and registered decimal scales. A stale API response is not a reserve
packet.

For a subscription that adds proven net equity \(\Delta E\), new shares are
computed from the pre-subscription NAV:

\[
\Delta S = \frac{\Delta E}{NAV_{pre}}
\]

Rounding direction, dust treatment, and every fee are fixed in the series. A
redemption receives the actual proceeds of its pro-rata close, subject to the
user's limit; any difference from the quoted NAV is explicitly attributed to
funding, price movement, fees, and execution.

## Tier 4: what is and is not trustless

The [pfUSDC Tier-4 design](/blog/pfusdc-trustless-bridge/) defines the relevant
standard: both ingress and egress facts are verified, and there is no observer,
multisig, or signer fallback. Applying that standard here requires more than a
proof-of-reserves dashboard.

| Boundary | Tier-4 target | Residual trust |
|---|---|---|
| User USDC to strategy | Contract-restricted escrow and HyperEVM/Core transfer | USDC contract, linked-token accounting, and HyperBFT execution |
| Position opening and rebalance | CoreWriter actions constrained by immutable series code | CoreWriter correctness and market liquidity |
| Position/NAV observation | Receipt inclusion plus HyperBFT finality proof; deterministic PFTL checks | Proof soundness and registered valuation policy |
| Share mint/burn | PFTL-gated global supply plus proof-verified representation | PFTL consensus and verifier contracts |
| Redemption | Reduce-only close, proven cash return, then burn and payout | Market liquidity, chain liveness, USDC |
| Underlying price | Pinned HIP-3 oracle/deployer and deviation policy | **The oracle can still be wrong or manipulated** |
| Secondary trading | Permissionless AMM | Pool liquidity, MEV, price deviation, AMM code |

For `xyz:SMSN`, the HIP-3 deployer determines important market parameters and
the oracle maps a Korean equity into a continuously traded USD perp. HIP-3
markets are isolated, but isolation does not make the oracle true. A 2026
TradeXYZ oracle incident involving SK Hynix reportedly caused roughly $60
million of liquidations after an anomalous Seoul print; reimbursement was a
discretionary venue response.[^galaxy] That is exactly the kind of source risk a
receipt faithfully proves rather than eliminates.

The honest claim is:

> No operator can mint an UltraShort share before the registered position is
> live, redirect strategy collateral, choose an unregistered trade, or complete
> redemption without reducing the proven liability. The holder still bears the
> registered venue, oracle, market, collateral, contract, and consensus risks.

## Required invariants

The implementation is not acceptable unless these invariants hold under model,
fuzz, fork, and live-bounded tests:

1. **One global supply.** PFTL native supply plus all registered wrapped supply
   equals finalized economic supply; bridges never create net claims.
2. **Position before shares.** No transferable share exists until collateral,
   fill, leverage, and equity are proven under the current profile.
3. **No free collateral.** Subscription cash is escrowed, deployed, refundable,
   or owed to a specific claim. It is never an operator balance.
4. **Restricted strategy.** The controller can trade only the registered market,
   direction, collateral, order types, leverage bounds, and destinations.
5. **No keeper authority.** Anyone may call maintenance functions; caller
   identity cannot change the allowed state transition or destination.
6. **Single-use evidence.** Deposit, fill, bridge, mint, burn, and payout receipt
   identifiers cannot be replayed.
7. **Freshness fails closed for risk.** Stale or invalid proofs disable issuance
   and leverage increases.
8. **Exits remain open.** A halt preserves reduce-only orders, cash return,
   redemption claims, and proof challenges wherever the underlying chain is
   live.
9. **Liquidation is explicit.** The series can lose all NAV. It may never mint a
   replacement claim to conceal that loss.
10. **Secondary trades are accounting-neutral.** AMM swaps change holders and
    market price, not strategy equity or global share supply.
11. **Governance cannot seize.** Upgrades use new series versions. An existing
    immutable series cannot be repointed to a new market, oracle, or withdrawal
    address.
12. **No silent downgrade.** If either proof direction is unavailable, the
    product reports the exact lower tier and disables the Tier-4 label.

## Risk controls that belong in code

### Liquidation and gap risk

Launch leverage should be materially below the venue maximum. A 10× venue limit
is not a sensible retail product target. The controller needs minimum margin
buffer, maximum leverage, reduce-only emergency behavior, and a rule for gaps
while the reference equity market is closed.

### Oracle and market-hours risk

Samsung trades in Korea while the perp can trade outside Korean cash hours. The
policy must distinguish primary-market, off-hours, and halted states; cap oracle
deviation; define FX treatment; and disable new exposure when the registered
oracle or executable quotes are stale. Corporate actions need deterministic
handling before the ex-date, not an administrator's retrospective edit.

### Capacity risk

Series open interest must be capped as a fraction of Hyperliquid market open
interest and executable depth. Subscription may partially fill and refund the
rest. A Uniswap pool with deep apparent liquidity cannot authorize a larger
perp position than the backing venue can safely carry.

### Funding and basis risk

Funding belongs entirely in NAV. Positive funding paid to shorts increases
equity; negative funding reduces it. No protocol marketing may annualize one
hour's rate as expected yield. Perp basis, mark construction, and oracle moves
must be visible next to funding.

### Contract and chain risk

The product composes PFTL, HyperBFT, HyperCore, HyperEVM, USDC, proof circuits,
representation contracts, and an AMM. Each component adds failure modes. Tier 4
removes discretionary custody; it does not imply zero technical risk.

## Fees and protocol economics

The business should make money in ways a holder can reconcile directly to NAV:

- an annualized management fee accrued per block or epoch;
- a small issue/redemption protocol fee;
- exact pass-through of trading, proof, bridge, and gas costs; and
- optionally, a share of **positive realized funding**, never a fee calculated
  from advertised or unrealized funding.

AMM fees belong to liquidity providers. Remaining funding and strategy P&L
belong to token holders. The protocol should not run an undisclosed market-maker
inventory or socialize one series' execution losses across another.

The strongest commercial wedge is not merely “another 2× token.” It is a
factory for long-tail, globally accessible exposure that conventional ETF
sponsors cannot launch economically or distribute continuously: Korean equities,
private-market proxies, commodities, rates, baskets, and hedges—provided a
liquid perp and a defensible oracle already exist. Each series converts existing
Hyperliquid liquidity into a composable bearer asset while the protocol earns
transparent recurring fees.

## Implementation sequence

### Phase 0 — falsify the route

- Deploy a same-address HyperEVM controller and initialize its HyperCore account
  before any CoreWriter call.
- Verify the linked USDC contract code and system-address backing, then move
  USDC EVM → Core → HIP-3 perp class and back Core → EVM without an EOA trade or
  withdrawal key.
- Open and close a bounded `xyz:SMSN` isolated position using only permissionless
  keeper calls.
- Confirm every required position, margin, funding, mark, oracle, and balance
  field is exposed by the read precompiles. The existing local Hyperliquid proof
  work identifies a real coverage gap around some spot/cash fields; launch must
  not paper over it with an API response.

Failure of any item blocks the Tier-4 claim.

### Phase 1 — one non-transferable live strategy

- Fixed 1× short on a deep, continuously traded crypto underlying.
- One immutable controller, no token, no AMM.
- Prove subscriptions, fills, equity, funding, rebalances, closes, and refunds.
- Run invariant, reorg, stale-proof, keeper-censorship, partial-fill, and
  liquidation simulations.

### Phase 2 — one wrapped NAVCoin

- Issue a capped, fixed-target series after a complete live proof loop.
- Add PFTL global-supply accounting and the HyperEVM representation.
- Add redemption escrow before adding secondary liquidity.
- Publish raw transaction, receipt, proof, supply, P&L, and conservation evidence.

### Phase 3 — AMM and variable leverage

- Seed a small Uniswap-compatible USDC pool with no protocol promise to defend
  NAV.
- Display pool price, finalized NAV, premium/discount, available primary
  capacity, funding, and liquidation buffer separately.
- Introduce adaptive leverage only after deterministic shadow operation shows
  lower liquidation risk and acceptable turnover versus fixed leverage.

### Phase 4 — destination-chain settlement

- Add a proof-backed solver route or a genuinely proof-verified USDC bridge.
- Test censorship, solver failure, proof delay, and destination liquidity.
- Keep HyperEVM USDC redemption as the canonical fallback.

## Launch acceptance test

The first product is ready only when an external reviewer can independently
verify this complete loop:

```text
HyperEVM USDC
  -> segregated subscription
  -> HyperCore collateral
  -> registered short position
  -> finalized NAVCoin shares
  -> wrapped ERC-20 in MetaMask
  -> AMM transfer to a second wallet
  -> redemption lock
  -> proportional reduce-only close
  -> wrapped and global supply reduction
  -> HyperEVM USDC payout
```

The evidence bundle must prove beginning and ending balances, every fee, actual
funding, actual fill prices, maximum leverage, global supply conservation, and
the absence of any privileged transaction. “The UI says complete” is not an
acceptance test.

## Conclusion

Leveraged ETFs prove the product demand; Hyperliquid supplies liquid,
continuously rolled perp exposure; NAVCoin supplies the accounting and issuance
discipline. The opportunity is to combine them without keeping the one feature
that makes most tokenized funds untrustworthy: an operator who can mint first,
hedge later, move the collateral, or decide whether redemption happens.

Trustless UltraShort Tokens should begin with a narrow promise: **a bearer share
of a specific autonomous short strategy, issued only after the position is
proven and redeemed only through a proven pro-rata close.** If that loop works,
variable-leverage series and long-tail markets become factory outputs. If the
loop needs an operator key, it is not Tier 4 and should not be sold as one.

“UltraShort” is a working research name and may overlap existing financial
product branding. Production naming requires trademark and regulatory review.

## Sources

[^direxion]: Direxion, [*Compound Insights: 2026 Leveraged & Inverse ETF Outlook*](https://www.direxion.com/uploads/Direxion_Compound-Insights_white-paper_22.pdf).
[^etfcom]: ETF.com, [“ETFs Just Set a Trading Volume Record”](https://www.etf.com/sections/features/etfs-just-set-trading-volume-record), July 21, 2026.
[^spglobal]: S&P Global Market Intelligence, [“Leveraged ETFs gain momentum as borrow demand builds”](https://www.spglobal.com/market-intelligence/en/news-insights/research/2026/07/leveraged-etfs-gain-momentum-as-borrow-demand-builds), July 2026.
[^funding]: Hyperliquid documentation, [Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding).
[^iborrowdesk]: IBorrowDesk, [Stock Borrow Fees & Short Availability](https://www.iborrowdesk.com/). IBorrowDesk is an independent site and is not affiliated with Interactive Brokers.
[^ibkrborrow]: Interactive Brokers Reporting Reference, [Borrow Fee Details](https://www.ibkrguides.com/reportingreference/reportguide/borrowfeedetails_default.htm).
[^ibkrrebate]: Interactive Brokers Campus, [Rebate Rate](https://www.interactivebrokers.com/campus/glossary-terms/rebate-rate/).
[^corewriter]: Hyperliquid documentation, [Interacting with HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore).
[^coreevm]: Hyperliquid documentation, [HyperCore ↔ HyperEVM transfers](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/hypercore-less-than-greater-than-hyperevm-transfers).
[^timing]: Hyperliquid documentation, [Interaction timings](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interaction-timings).
[^bridge]: Hyperliquid documentation, [Bridge2](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/bridge2) and [HyperCore bridge](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/bridge).
[^galaxy]: Galaxy Research, [“Hyperliquid, TradeXYZ, Oracle Risk, and Liquidations”](https://www.galaxy.com/insights/research/hyperliquid-tradexyz-oracle-liquidations), July 31, 2026.
