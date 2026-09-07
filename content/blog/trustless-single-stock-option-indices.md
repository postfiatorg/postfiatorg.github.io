---
title: "A Framework for Trustless Single Stock Option Indices"
date: 2026-09-07T00:00:00Z
lastmod: 2026-09-07T18:06:07Z
draft: false
type: "blog"
url: "/blog/trustless-single-stock-option-indices/"
aliases: ["/research/single-stock-options-trackers/"]
breadcrumb_label: "Post Fiat Blog"
breadcrumb_url: "/blog/"
summary: "Bring the call-option premium market on-chain: rolling upside exposure, a loss limited to the amount invested, and the simplicity of a spot token. NVDA and Micron alone show $8.05 billion of outstanding ATM/OTM call premium value."
description: "An options NAVCoin packages fully funded calls into a spot asset. The market sizing, investor benefits, Ethereum and Uniswap distribution, and Post Fiat verification behind single-stock options trackers."
author: "Post Fiat"
options_tee: true
categories: ["Post Fiat Research"]
tags: ["Options", "Convexity", "NAVCoin", "Ethereum", "Uniswap", "TEE", "Post Fiat"]
---

**The goal is to make call-option exposure as easy to buy and hold as a spot
token.** Choose a company, choose how much capital to put at risk, and hold one
asset that maintains exposure to its upside.

The product is an **options NAVCoin**: a portfolio of fully paid call options
packaged into an Ethereum token. The portfolio rolls its contracts under a
published rulebook. Investors hold the token in a wallet and trade it on Uniswap.
Post Fiat supplies the machinery for verifying the strategy and, in the full
product, its backing and share accounting.

This brings a large existing financial market into a familiar on-chain format.
Our initial market sizing found **$8.05 billion of outstanding at-the-money and
out-of-the-money call premium value in Nvidia and Micron alone**. The commercial
opportunity is to serve that demand for upside optionality through a product that
wallets, exchanges and other applications can integrate as a single spot asset.

{{< options-tee-diagram kind="spot" >}}

## An $8 billion starting market in two stocks

We measured every returned call expiration in the full Schwab chains for NVDA
and MU, keeping strikes at or above the stock reference price. This isolates the
ATM/OTM calls that buyers use for upside optionality.

| Stock | Outstanding call premium value | Call underlying notional | Reported stock-perp open interest |
|---|---:|---:|---:|
| **Nvidia — NVDA** | **$3.63B** | **$84.99B** | **$359.3M** |
| **Micron — MU** | **$4.42B** | **$57.30B** | **$428.3M** |
| **Combined** | **$8.05B** | **$142.28B** | **$787.5M** |

*Snapshot: Schwab chains captured September 5, 2026, with September 4 quotes;
perpetual observations September 7. Premium value is open interest × 100 shares × the quoted midpoint. Perp totals cover tracked venues with available OI.*
[Calculation data](/research/options-tee-indices/market-sizing-20260907.json),
[NVDA perp markets](https://perpequities.com/stocks/nvda-perp),
[MU perp markets](https://perpequities.com/stocks/mu-perp).

{{< options-tee-diagram kind="market" >}}

**The premium base is the relevant starting point for a funded options product:**
the fund's capital buys options. The notional shows the underlying stock exposure
those contracts reference. On that measure, the selected calls represent roughly
237 times NVDA's reported perp OI and 134 times Micron's.

An illustrative asset base equal to **1% of the two-stock premium value would be
$80.45 million**. This illustrates the scale of a product serving a small share of the measured market. The wider addressable category extends across single-stock
calls and the repeated purchases that maintain those positions over time.
For context, OCC reported **8.27 billion single-stock option contracts traded
in 2025**, covering calls and puts, up **26.8%** from 2024.
[OCC annual volume](https://www.theocc.com/newsroom/views/2026/01-05-occ-annual-2025-and-december-2025-volume).

The thesis is that a useful spot wrapper can bring some of this existing options
activity on-chain while serving crypto users who want the same payoff in their
existing wallets.

## Why someone would buy it

A call gives its holder the right to buy shares at a fixed strike price during
the contract's exercise period. The buyer pays a premium for that right.

A bullish investor often wants a large upside payoff with a fixed amount at
risk. Calls provide that shape. A fully paid call's loss is limited to its
premium, while its participation can increase as the stock rises: **convexity**.
[OIC long-call mechanics](https://www.optionseducation.org/strategies/all-strategies/long-call).

The spot token preserves the useful part of this experience. In the fully funded
design, an investor buying $1,000 of tokens puts that $1,000, plus transaction
fees, at risk. The position requires no maintenance-margin top-ups. The holder
can keep it through an interim drawdown and still participate if the underlying
calls recover before they expire.

{{< options-tee-diagram kind="payoff" >}}

Consider the illustrated call: strike $100, premium $10 per share. At expiry, a
$140 stock price produces $40 of option value and $30 of profit per share. A
temporary fall to $80 does not trigger a margin liquidation of the fully paid
call. A highly leveraged long perp can be closed by its margin rules during
that same fall, losing the opportunity to participate in the later recovery.
[Perpetual liquidation mechanics](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations).

| Exposure | What the investor gets | What maintaining it involves |
|---|---|---|
| Spot stock | Linear participation in the company | Holding shares |
| Margined long perpetual | Linear exposure with adjustable leverage | Margin management and funding payments or receipts |
| Options NAVCoin | Rolling upside convexity with a defined capital commitment | The portfolio maintains fully funded calls under its rulebook |

The economic price of convexity is the option premium. Time decay, changes in
implied volatility and the cost of replacing contracts affect returns. Calls can
expire worthless, and the token can lose the entire amount invested. A perp has
no scheduled option expiry and its funding can favor either side.
[Funding mechanics](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding).

The practical benefits extend beyond the payoff:

- **Investors buy a persistent strategy in one transaction.** They can size a
  position in dollars and leave contract selection, whole-contract sizing and
  rolling to the portfolio.
- **Wallets and exchanges integrate a spot asset.** An ERC-20 balance and a
  trading pair provide a familiar way to distribute stock-option exposure.
- **Liquidity providers get a new category of trading pairs.** Secondary trades
  transfer shares of an existing portfolio, allowing the same underlying basket
  to support repeated token trading.
- **Product builders can offer a family of single-stock exposures.** Each stock
  and declared strategy can use the same verification and accounting machinery.

{{< options-tee-diagram kind="products" >}}

## One token maintains the call strategy

A call has a finite life. A tracker gives the strategy a continuing identity as
its individual contracts change. The holder follows one company's options
exposure; the portfolio handles the maintenance.

{{< options-tee-diagram kind="basket" >}}

The rulebook specifies the eligible maturities and strikes, premium allocation,
position sizing and roll conditions. Each observation produces a **target**:
the contracts and quantities the strategy should hold. Actual holdings can then
be reconciled against that target.

{{< options-tee-diagram kind="roll" >}}

The demonstrated Nvidia and Micron strategies each selected five calls in a
common expiration. The engine applies explicit rules to each stock separately.
This makes the product repeatable: its identity stays attached to its published
method while the basket evolves.

## Ethereum distributes it; Post Fiat verifies it

An options NAVCoin connects the existing listed-options market to Ethereum
wallets and liquidity. The architecture gives each system a concrete job.

{{< options-tee-diagram kind="navcoin" >}}

The broker holds the actual calls and brokerage cash. Post Fiat checks the
strategy evidence and supplies the canonical verification and accounting layer
in the NAVCoin design. Ethereum contracts represent investor ownership, hold
settlement USDC and enforce authenticated issuance and settlement authorizations.
The investor holds the ERC-20; Uniswap supplies the secondary market.

**NAV per token = (options value + cash − liabilities and accrued fees)
÷ valid token supply.**

For a portfolio with $1 million of net assets and 100,000 tokens, NAV is $10 per
token. Portfolio gains and losses change that value. Subscriptions add assets and
shares together; redemptions remove them together. Pool liquidity determines
how easily tokens trade, while the portfolio determines their backing.

{{< options-tee-diagram kind="redemption" >}}

A redeemable implementation offers two exits: sell an existing token through
Uniswap, or request settlement against portfolio value. Subscriptions and
redemptions give traders a way to arbitrage premiums and discounts. Their costs,
timing and availability determine how closely the market follows NAV.

The token can trade while the options market is closed. Primary settlement can
use a queue tied to the fund's valuation and cash settlement process.
[ERC-7540](https://eips.ethereum.org/EIPS/eip-7540) provides a standard interface
for this request-and-claim pattern. Earlier NAVCoin research also describes
[a model with bounded market support and no standing redemption right](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/content/blog/navcoin-collateralization.md).
Those are different product terms; the shared primitive supports an explicit
choice between them.

## Verification makes the product reusable

An investor wants the strategy they bought. A wallet wants a result it can check.
A fund administrator wants calculations it can reconcile. A shared proof gives
all three a common answer to **“Were these rules applied to these inputs?”**

{{< options-tee-diagram kind="pipeline" >}}

The measured collector runs in an AWS Nitro enclave and obtains the brokerage
inputs over TLS. Hardware attestation identifies its software and binds its
input statements. The SP1 program verifies those bindings and computes the
target. Its proof lets other systems check the calculation while the full
brokerage response remains private.
[AWS attestation](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html),
[SP1](https://docs.succinct.xyz/docs/sp1/introduction).

Try the verification walkthrough:

{{< options-tee-diagram kind="verification" >}}

The registered method, inputs and output commitments travel together. A changed
claim fails the corresponding check, and an accepted run has a unique receipt.
PFTL records that shared result for applications to consume.

{{< options-tee-diagram kind="ledger" >}}

This is how verification supports distribution: every integrating application
can rely on the same specified calculation and accepted history. The full
NAVCoin extends that discipline to reserves, liabilities, token supply and
settlement. Post Fiat supplies common verification infrastructure across the
family of products; Ethereum supplies wallet access and trading liquidity.

## What is built, and the path to the funded token

On September 6, 2026, the Nvidia and Micron runs produced five-call targets from
real, attested Schwab inputs. Both Nitro/SP1 proofs passed independent replay and
verification. Both receipts passed isolated local four-validator PFTL tests,
including restart/replay, the CLI and viewer.

{{< options-tee-diagram kind="status" >}}

**The demonstrated component is the strategy calculation and proof.** The funded
token adds live execution, custody, account reconciliation, reserve valuation,
share issuance and its chosen settlement terms. The demo used hypothetical
capital; brokerage orders and investor token issuance are the next product work.
[Demo record](/research/options-tee-indices/demo-record.json),
[implementation PR](https://github.com/postfiatorg/postfiatl1v2/pull/38),
[verification map](https://github.com/postfiatorg/postfiatl1v2/blob/c1b3a6bec14b4fe76bc3e4f95fecd4b9b0691f53/docs/yolo/target-receipt-v1.md#where-verification-lives).

The trust boundary is concrete. Listed options remain in broker custody, with
holder rights established by the fund arrangement. Proofs verify specified
computations over authenticated evidence; their assurance depends on the data
source, measured code, hardware, cryptography and ledger finality. The completed
target proof covers strategy construction. The funded product also needs
verified holdings and working settlement. Those are the remaining engineering
and custody responsibilities.

## A product family built around demand for convexity

The [NAVCoin proposal](https://postfiat.org/blog/navcoin-proposal/) provides the
portfolio-token architecture. [One Portfolio, Many Access Venues](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/content/blog/navcoin-ethereum.md)
separates backing from distribution.
[UltraShort NAVCoins](https://postfiat.org/blog/trustless-ultrashort-tokens/)
apply the pattern to perpetual positions, while
[Glass](https://postfiat.org/research/glass-institutionalizing-navcoins/)
explores institutional use of verified reserve claims. External platforms such
as [Enzyme Onyx](https://docs.enzyme.finance/onyx-faq) demonstrate the wider
portfolio-share model.

The options version addresses a distinct demand: **stock upside with a fixed
amount of capital at risk, maintained over time, held and traded as a spot
asset.** Investors already commit billions to that payoff. This primitive gives
builders a way to bring it into the on-chain economy with a common strategy
engine, a verifiable record and a familiar token interface.

<details class="ot-source-details">
<summary>Market-sizing definitions and source notes</summary>

The September 7 analysis uses retained full Schwab CALL captures dated September
5, containing September 4 quotes. Selection is `strike >= underlyingPrice`
across all returned expirations, with no liquidity or strike-count screen.
The selected open interest is 3,689,370 NVDA contracts and 563,602 MU contracts;
all have a standard 100-share multiplier. Expiry subtotals reconcile exactly.

Premium value is `sum(openInterest × 100 × (bid + ask) / 2)`. It measures the
current value of outstanding long calls, including positions used in spreads
and hedges. Historical premiums paid and incremental buying demand are different
measures. Underlying notional is `sum(openInterest × 100 × stock reference
price)`; delta-adjusted notional is $36.54B combined. The $8.05B observation sizes
two stocks, and the 1% example is an arithmetic scale illustration.

Perpetual totals are September 7 observations from PerpEquities, covering 26 of
33 NVDA markets and 25 of 30 MU markets with reported OI. Exchange one-sided and
two-sided counting conventions vary, making the notional ratios indicative.
An independent Hyperliquid API snapshot gave $125.98M NVDA and $131.17M MU OI,
included within the broader market. [Provider methodology](https://perpequities.com/methodology),
[Bybit OI definitions](https://bybit-exchange.github.io/docs/v5/market/tickers).

The [public aggregate record](/research/options-tee-indices/market-sizing-20260907.json)
contains exact values, timestamps, coverage and formulas. The underlying licensed
chain responses remain in the authorized source archive.

</details>
