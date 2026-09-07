---
title: "A Framework for Trustless Single Stock Option Indices"
date: 2026-09-07T00:00:00Z
lastmod: 2026-09-07T19:18:26Z
draft: false
type: "blog"
url: "/blog/trustless-single-stock-option-indices/"
aliases: ["/research/single-stock-options-trackers/"]
breadcrumb_label: "Post Fiat Blog"
breadcrumb_url: "/blog/"
summary: "Call options already attract billions. An options NAVCoin brings that demand on-chain through one spot token that continuously rebalances and rolls a single stock's call exposure."
description: "A spot token for a continuously maintained single-stock call strategy. The $8.05 billion NVDA and Micron premium market, automatic rebalancing, Ethereum distribution and Post Fiat verification."
author: "Post Fiat"
options_tee: true
categories: ["Post Fiat Research"]
tags: ["Options", "Convexity", "NAVCoin", "Ethereum", "Uniswap", "TEE", "Post Fiat"]
---

**Call options already attract billions of dollars. This proposal gives that
market a simple on-chain product: a spot token that continuously maintains a
single stock's call exposure.**

The proposed **options NAVCoin** holds a portfolio of fully paid calls. Its
rulebook handles contract selection, rebalancing and replacement as options age.
The investor holds one Ethereum token through successive baskets and trades it
on Uniswap. Post Fiat supplies the verification infrastructure behind the strategy
and, in the full product, its backing and share accounting.

**The business case starts with existing demand.** Buyers pay for the possibility
of a large upside payoff with a defined amount at risk. That payoff can be worth
buying even when its expected financial return is negative. The product's value
is making this exposure easy to access and maintain in a wallet.

Our initial sizing found **$8.05 billion of outstanding at-the-money and
out-of-the-money call premium value in Nvidia and Micron alone**. The opportunity
is to bring an established buying behavior on-chain through a token that wallets,
exchanges and other applications can integrate as a spot asset.

{{< options-tee-diagram kind="spot" >}}

## An $8 billion starting market in two stocks

**For these two stocks, listed calls dwarf the tracked equity-perp market.**
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
237 times NVDA's reported perp OI and 134 times Micron's—about **181 times
combined**, using the reported venue totals.

An illustrative asset base equal to **1% of the two-stock premium value would be
$80.45 million**. This illustrates the scale of a product serving a small share of the measured market. The wider addressable category extends across single-stock
calls and the repeated purchases that maintain those positions over time.
For context, OCC reported **8.27 billion single-stock option contracts traded
in 2025**, covering calls and puts, up **26.8%** from 2024.
[OCC annual volume](https://www.theocc.com/newsroom/views/2026/01-05-occ-annual-2025-and-december-2025-volume).

The product opportunity is a standard spot interface for that ongoing activity:
**buy a single stock's call strategy once, then let the portfolio maintain it.**

## One token maintains the call strategy

Maintaining a call position means repeatedly choosing contracts, sizing the
purchase and deciding when to replace them. A holder who wants ongoing Nvidia
call exposure must keep doing that work as individual contracts expire.

An options NAVCoin makes the strategy continuous. The investor buys one token;
the portfolio rebalances its calls and rolls into replacement contracts under
a published rulebook. **The options expire. The token carries the strategy
across those expirations.**

{{< options-tee-diagram kind="basket" >}}

The rulebook specifies the eligible maturities and strikes, premium allocation,
position sizing and roll conditions. Each observation produces a **target**:
the contracts and quantities the strategy should hold. Actual holdings can then
be reconciled against that target. In the funded product, replacement premiums
and trading costs are paid from portfolio assets and reflected in NAV.

{{< options-tee-diagram kind="roll" >}}

The demonstrated Nvidia and Micron strategies each selected five calls in a
common expiration. The engine applies explicit rules to each stock separately.
This makes the product repeatable: its identity stays attached to its published
method while the basket evolves.

## Why package it as a spot token?

The spot format turns that maintained strategy into something existing crypto
applications can use:

- **Investors buy a persistent position in one transaction.** Choose a stock and
  a dollar amount, then hold the same wallet asset through successive rolls.
- **Wallets and exchanges integrate a spot asset.** An ERC-20 balance and a
  trading pair provide a familiar way to distribute stock-option exposure.
- **Liquidity providers get a new category of trading pairs.** Secondary trades
  transfer shares of an existing portfolio, allowing the same underlying basket
  to support repeated token trading.
- **Product builders can offer a family of single-stock exposures.** Each stock
  and declared strategy can use the same verification and accounting machinery.

{{< options-tee-diagram kind="products" >}}

The investor is buying **convexity**: a call's participation can increase as the
stock rises, with loss limited to the premium paid. A call gives its holder the
right to buy shares at a fixed strike price during its exercise period.
[OIC long-call mechanics](https://www.optionseducation.org/strategies/all-strategies/long-call).

In the fully funded design, someone buying $1,000 of tokens commits that $1,000,
plus transaction fees. The holder can keep the position through an interim
drawdown without maintenance-margin top-ups. The portfolio pays for subsequent
calls from its assets; the investor continues to hold the token.

{{< options-tee-diagram kind="payoff" >}}

The diagram shows the payoff the buyer pays for: a $100-strike call bought for
$10 per share loses at most $10 and earns $30 if the stock finishes at $140.

| Exposure | What the investor gets | What maintaining it involves |
|---|---|---|
| Spot stock | Linear participation in the company | Holding shares |
| Margined long perpetual | Linear exposure with adjustable leverage | Margin management and funding payments or receipts |
| Options NAVCoin | Rolling upside convexity with a defined capital commitment | The portfolio maintains fully funded calls under its rulebook |

A fully paid call can survive a temporary drawdown and participate in a recovery
before expiry. A leveraged perp may liquidate during that drawdown. The call
buyer pays premium for this payoff; time decay, implied volatility and rolling
costs affect the token's NAV, and the entire investment can be lost. Perp holders
manage margin and funding, which can be paid or received.
[Liquidation](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations)
and [funding mechanics](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding).

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

The options version serves an established buying behavior through a new
interface: **one spot token that keeps a single stock's call strategy running
across rebalances and expirations.** Investors already commit billions to calls.
A continuously maintained token gives that market an on-chain home, with a
defined capital commitment for the buyer and a common verification system for
the applications that distribute it.

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
