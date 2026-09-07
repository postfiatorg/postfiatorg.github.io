---
title: "A Framework for Trustless Single Stock Option Indices"
date: 2026-09-07T00:00:00Z
draft: false
type: "blog"
url: "/blog/trustless-single-stock-option-indices/"
aliases: ["/research/single-stock-options-trackers/"]
breadcrumb_label: "Post Fiat Blog"
breadcrumb_url: "/blog/"
summary: "A verifiable engine for single-stock options exposure—and a framework for packaging it as a NAVCoin held on Ethereum and traded on Uniswap."
description: "A visual explanation of single-stock options trackers and proposed options NAVCoins: upside convexity, brokerage custody, Ethereum tokens, Uniswap trading, redemption, and Post Fiat verification."
author: "Post Fiat"
options_tee: true
categories: ["Post Fiat Research"]
tags: ["Options", "Verifiable Indices", "NAVCoin", "Ethereum", "Uniswap", "TEE", "Post Fiat"]
---

A single-stock options tracker maintains an options strategy on one company as
contracts age and market conditions change. Pick a company and specify the
strategy's rulebook. The tracker calculates which options to hold, in what
quantities, and when to rebalance or roll into new contracts. That proposed
portfolio is its **target**.

Post Fiat's prototype adds something important: **a proof that the target was
calculated from the committed inputs using the specified rules.** The calculation
can use private brokerage data while publishing enough evidence for other systems
to check it. This is the primitive we built: a verifiable engine for single-stock
options trackers.

A funded version could become an **options NAVCoin**: a token representing a
share of an actual options portfolio, held in an Ethereum wallet and traded on
Uniswap. The rulebook maintains the exposure; verified accounting connects the
token to the portfolio's net asset value, or NAV. That product architecture is
the next layer proposed here. The completed demonstration proves target
construction; custody, live execution and token issuance remain additional work.

## 1. What exactly is being tracked?

Think of a tracker for Nvidia. Its universe is listed call options on Nvidia.
A rulebook determines the eligible expiration, which strikes belong in the basket,
how much premium to allocate and when to replace aging contracts. A Micron tracker
would apply its rulebook to Micron's options instead. These are two separate
single-company strategies.

{{< options-tee-diagram kind="basket" >}}

A call gives its buyer the right to buy the underlying shares at a specified
strike under the contract's terms. Its value depends on the stock, time remaining
and implied volatility, among other factors. A rolling call tracker therefore
provides **options exposure to a stock**; it does not promise the stock's return
or a constant leverage multiple. A purchased call can lose its entire premium.
[OIC's long-call explanation](https://www.optionseducation.org/strategies/all-strategies/long-call)
describes those economics.

Our demonstrated design selected five call positions in a common expiration for
each stock. The starting cash was hypothetical capital available to pay option
premiums. It was not cash collateral attached to shares of the underlying. A
90% premium budget was divided into five equal sleeves; whole-contract sizing
could leave additional cash unspent. Those are the demonstrated rule choices,
not requirements for every tracker someone might design.

## 2. Why make this a primitive?

An option expires. Persistent exposure requires a sequence of decisions: retain
these contracts, rebalance their quantities, or roll into another expiration.
A tracker packages that maintenance into an explicit, repeatable process.

{{< options-tee-diagram kind="roll" >}}

The financial idea is useful even before adding cryptography. It gives a strategy
a stable identity while its underlying contracts change. A user can understand
and compare the rulebook instead of repeatedly selecting individual options.
An investment platform can integrate one target feed instead of rebuilding the
selection process for every customer.

The verification layer makes the same object easier to use across organizations.
An operator, a wallet, a fund administrator and a ledger can refer to the same
calculation and check that it follows the same specification. This reduces the
need to accept an operator's spreadsheet, API response or assertion on faith.
It does not establish that the strategy is profitable or suitable for an investor.

The exposure also answers a different need from a leveraged perpetual. A fully
paid long call offers **upside convexity**: its participation can increase as the
stock rises, while its loss is limited to the premium paid, plus fees. It has no
maintenance-margin liquidation as a standalone funded position. A margined long
perpetual gives linear exposure and can be liquidated during a drawdown before
the stock recovers. The call pays for this difference through premium, time decay
and expiry; perpetual funding can be paid or received and changes over time.
[OIC call mechanics](https://www.optionseducation.org/strategies/all-strategies/long-call),
[Hyperliquid liquidation](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations)
and [funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding).

A rolling call portfolio carries that convex exposure forward by buying new
options under its rulebook. It can still lose all its invested capital. A token
wrapper preserves the absence of holder margin calls only when its underlying
calls are fully funded and the holder does not borrow against the token.

## 3. An options NAVCoin in an Ethereum wallet

Imagine a Nvidia options NAVCoin and a separate Micron options NAVCoin. Each
represents its own portfolio. Investors hold an ERC-20 token; the portfolio holds
the actual calls selected by its rulebook and any residual cash. NAV changes as
those positions change value, trading occurs and expenses accrue.

**NAV per token = (actual options value + cash − liabilities and accrued fees)
÷ valid token supply.**

For illustration, a portfolio with $1 million of net assets and 100,000 tokens
has a $10 NAV per token. That number comes from the portfolio's own holdings,
not from total open interest in the stock's options chain or the money in a
Uniswap pool.

{{< options-tee-diagram kind="navcoin" >}}

The architecture separates three responsibilities:

| Layer | What it holds or enforces |
|---|---|
| Broker / custodian | Actual listed options, brokerage cash and the account records needed to establish the portfolio's assets and obligations |
| Post Fiat verification | The registered strategy, authenticated reserve evidence, NAV calculations and canonical supply accounting in the proposed NAVCoin integration |
| Ethereum / Uniswap | ERC-20 ownership, settlement USDC, issuance and redemption contracts, and secondary-market trading |

**Self-custody of the token is different from custody of the options.** A Schwab
call remains a brokerage-held security. Putting its portfolio share on Ethereum
does not move that contract into an Ethereum vault. The fund arrangement must
establish who controls the account and what token holders can claim. Authenticated
account evidence makes that arrangement more checkable; cryptography cannot make
a broker's obligations disappear.

Ethereum contracts would need to authenticate accepted NAV and supply
authorizations before acting on them. In the PFTL-ledger design, this includes
verifying the relevant PFTL finality evidence. A relayer merely carrying a number
across chains is insufficient. This separation follows the
[existing NAVCoin architecture](https://postfiat.org/research/private-nav-swap-explainer/):
the canonical accounting and the trading venue can live on different chains.

## 4. Selling the token and redeeming the portfolio

Uniswap provides a market where buyers and sellers exchange the token. It does
not automatically set its price to NAV. A $10 NAV token may trade at $9.70 or
$10.30 depending on liquidity, expected portfolio moves and the ease of entering
or leaving the fund.

{{< options-tee-diagram kind="redemption" >}}

In a redeemable design, a trader buying below NAV can request redemption against
portfolio value; above NAV, a subscriber can acquire new shares and sell them.
That mechanism can narrow price differences when costs, settlement times and
access permit. A published NAV alone provides no such arbitrage route, and
redemption does not guarantee an exact market-price match.

Brokerage-held options make **queued settlement** a useful design candidate.
Investors can trade existing ERC-20 tokens while the stock-options market is
closed, provided the token is transferable and the pool has liquidity. A primary
subscription or redemption can settle after the required valuation, execution
and cash movement. The product must specify when its exchange rate is determined
and which costs apply, so stale quotes do not transfer value between holders.
[ERC-7540](https://eips.ethereum.org/EIPS/eip-7540) provides a standard request-and-claim
interface for asynchronous vault deposits and redemptions; it does not itself
provide custody or determine a fair NAV.

Earlier NAVCoin work contains two distinct product models:

| Model | Holder's exit and price connection |
|---|---|
| Redeemable portfolio share | Sell on the market or request redemption under the fund's stated settlement terms; subscriptions and redemptions connect price to NAV |
| NAV-tracked token without a standing redemption right | Sell on the market; disclosed, bounded market operations may support alignment, while discounts or premiums can persist |

The second model appears in the
[collateralization draft](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/content/blog/navcoin-collateralization.md).
Both can use Ethereum and Uniswap. This article identifies the choice; it does
not select redemption terms, trading rules or market-support budgets for a live
options fund.

## 5. The rulebook is part of the product

“Use liquid calls on this stock” leaves many decisions unresolved. Which maturity?
What counts as liquid? Which strikes? How are quantities rounded? What happens
when the current basket reaches its roll threshold?

For verification to mean anything, the relevant choices must be explicit. The
tracker's identity includes its methodology and parameters. The computation also
binds the data collection and the supplied starting portfolio state.

{{< options-tee-diagram kind="rulebook" >}}

A cryptographic commitment is a fingerprint of a particular record. It lets the
system detect a substitution: these parameters rather than a different set;
this collection rather than another snapshot; this starting state rather than an
invented balance. The full records still need to be available to the people
reviewing the strategy. A fingerprint alone does not tell a reader whether a
rulebook is sensible.

In the demonstrated run, both trackers selected November 20, 2026. The maturity
rule chose the qualifying captured expiry closest to 60 days, beyond the existing
30-day roll threshold, while preserving the other declared eligibility and sizing
rules. That choice was made explicit before proving. Changing the method means
changing the committed method; a provider cannot silently replace it under the
same registered expectations.

The deterministic [Rust calculator](https://github.com/postfiatorg/postfiatl1v2/blob/d3aeb780bff327bc2d9734226770aba7433ba5d9/tools/nav-reserve-proof/crates/reserve-proof-types/src/yolo_target.rs)
implements those choices. Python and Rust were checked against one another.

## 6. From a private options chain to a verifiable target

A useful tracker needs market data. Brokerage responses may contain licensed
quotes and account-related inputs that should not be copied onto a public ledger.
Simply hiding the data, however, would leave everyone trusting whoever ran the
calculation.

We combine a **trusted execution environment (TEE)** with a **zero-knowledge
proof**. They answer different questions.

{{< options-tee-diagram kind="pipeline" >}}

The TEE in this implementation is AWS Nitro Enclaves: an isolated environment
whose memory is separated from its parent server. The collector runs inside it.
Because an enclave has no direct external network interface, the parent relays
traffic; the collector inside the enclave terminates the Schwab TLS connection.
The parent relays encrypted traffic rather than receiving plaintext quotes.
[AWS describes the isolation model](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html).

Nitro supplies a signed **attestation** identifying measured software and binding
its statements to that identity. Those measurements are compared with the allowed
collector image. KMS key release can also be conditioned on attestation. This
links the input statement to specific software running in the protected environment.
[AWS's attestation documentation](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html)
explains the measurements and key-policy mechanism.

The SP1 program then verifies the attestation and signed input bindings and
recalculates the target. Its proof lets another computer verify that this program
completed successfully without receiving the private witness—the complete input
material used to prove the run. [SP1](https://docs.succinct.xyz/docs/sp1/introduction)
is the proving system used for this step.

The important separation is **evidence about the data-producing software** and
**evidence about the calculation**. The current guest verifies enclave statements
binding the normalized inputs. It does not independently prove a Schwab TLS
transcript or establish that the broker's market data is economically correct.

## 7. What can remain private?

A public verifier needs the proof and the public commitments. It does not need the
whole options chain, the private witness or the complete target position table.
Authorized parties can retain the encrypted source material and replay it when
an audit requires the underlying records.

{{< options-tee-diagram kind="privacy" >}}

The demonstrated target interface has exactly **408 public bytes**, plus the
proof. Those bytes bind the program, method, parameters, collection, prior state
and target, and report a status and counts. On-chain registration also exposes
metadata such as the submitter and run identity. This is selective disclosure,
not a promise that all activity or metadata is invisible.

A hash is an identifier, not encryption. Low-entropy values may still be guessable.
The privacy design combines encrypted retention, protected processing and a proof
that does not require publishing the witness. Detailed disclosure to investors
or auditors remains a product-policy choice.

The [public ABI](https://github.com/postfiatorg/postfiatl1v2/blob/c1b3a6bec14b4fe76bc3e4f95fecd4b9b0691f53/crates/types/src/yolo_target_public_values.rs)
defines exactly which fields are exposed.

## 8. What does “trustless” mean here?

The valuable claim is precise: **a verifier does not have to trust the operator's
assertion that it applied the registered calculation correctly.** The proof and
registration checks enforce that boundary.

Try changing what the operator submits in the walkthrough below.

{{< options-tee-diagram kind="verification" >}}

A provider can propose a different strategy. What it cannot do is substitute the
rules, input commitments or proved output while still passing verification as
the original registered run. A valid result also cannot consume the same run
registration twice. These checks live in the
[PFTL receipt verifier](https://github.com/postfiatorg/postfiatl1v2/blob/c1b3a6bec14b4fe76bc3e4f95fecd4b9b0691f53/crates/execution/src/yolo_target_verifier.rs).

That is a meaningful reduction in trust, but calling the entire product
unconditionally trustless would go further than the implementation supports.

{{< options-tee-diagram kind="trust" >}}

Someone still has to review the rulebook and select the correct program and
collector identities. The data source can be wrong. The hardware attestation
system and measured collection code remain assumptions. The proof system has
cryptographic and setup assumptions, and ledger finality depends on consensus.
If a future product holds real options, its broker, custody, execution and account
reconciliation create additional obligations. A target proof does not prove that
those options were bought or that a token is redeemable.

It is best understood as **verifiable rule execution over attested inputs**.
That guarantee can be embedded in products with different custody and disclosure
arrangements without confusing the proof with those arrangements.

## 9. What does Post Fiat add?

A mathematical proof can be checked independently. A shared ledger answers the
next questions: which tracker and program were registered, which result was
accepted for a run, and where that accepted result sits in a common history.

{{< options-tee-diagram kind="ledger" >}}

PFTL's registration pins the program verification key and expected commitments,
along with the authorized submitter, prior state and run identity. After the
required activation conditions are met, consensus verifies the submitted proof
and records the receipt. Duplicate and conflicting submissions are rejected
under the registration rules.

This gives applications a common reference for the result. A wallet or
administrator can query the receipt instead of deciding which operator API
response is authoritative. The validators verify the succinct proof; they do
not retrieve private chains or regenerate it.

PFTL is the intended ledger of record for this primitive. In the proposed NAVCoin
product, Ethereum distribution would sit above that verification and accounting
layer. The completed target receipt itself grants no order, minting or reserve
authority; normal transaction fees still apply. The bridge, reserve checks and
issuance controls need their own integration and evidence before investor funds
depend on them.

## 10. How this connects to earlier NAVCoin proposals

The primitive produces a target and evidence for that target. It is useful because
several different products can consume the same object.

{{< options-tee-diagram kind="products" >}}

A model-portfolio service could distribute verifiable targets. A managed-account
service could translate them into broker orders and reconcile the resulting
holdings. A fund or tokenized tracker could add custody, share accounting,
valuation, subscriptions and redemptions around the strategy.

These are possible product layers, not capabilities created automatically by a
proof. Moving from “the target was correctly calculated” to “investors actually
own the exposure” requires execution and reconciliation. Moving from there to a
tradable token requires another explicit set of economic and legal arrangements.
The value of the primitive is that these products can share a verifiable strategy
engine instead of treating every calculation as an opaque operator claim.

The options NAVCoin fits a product family already described in Post Fiat's work:

| Precedent | Connection to the options tracker |
|---|---|
| [The NAVCoin Proposal](https://postfiat.org/blog/navcoin-proposal/) | Binds portfolio evidence, valuation, liabilities and supply to a floating-NAV token |
| [One Portfolio, Many Access Venues — draft](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/content/blog/navcoin-ethereum.md) | Separates one portfolio's backing and global supply from the venues where its tokens trade |
| [Trustless UltraShort Tokens](https://postfiat.org/blog/trustless-ultrashort-tokens/) | Proposes packaging a managed perpetual position as a transferable, redeemable NAVCoin; an options portfolio supplies a different payoff and custody model |
| [Glass: Institutionalizing NAVCoins](https://postfiat.org/research/glass-institutionalizing-navcoins/) | Explores how reserve rights, liabilities and control evidence could support institutional acceptance of portfolio claims |

These are architectural precedents with their own declared implementation
boundaries. The UltraShort design uses an on-chain perpetual venue; its proposed
custody controls cannot simply be assumed to apply to a Schwab account.

An external precedent is [Enzyme Onyx](https://docs.enzyme.finance/onyx-faq), which
supports ERC-20 vault shares and portfolios of on-chain or off-chain assets, with
configurable transferability and manager-reported valuation. The proposed Post
Fiat contribution is to bind authenticated evidence and verified calculations to
the controls that determine which portfolio claims may exist.

## 11. What we have demonstrated

On September 6, we completed the target/proof workflow for **Micron and Nvidia**.
Each calculation produced target quantities for five November 20 calls using retained,
attested Schwab responses. Both real Nitro/SP1 proofs passed independent
verification and authorized input replay. Both were accepted through isolated
local four-validator PFTL receipt tests, including restart/replay and the Python
CLI and viewer.

{{< options-tee-diagram kind="status" >}}

This was a closed-market demonstration: one retained observation per stock,
September 4 as the source market date, original timestamps, a declared 48-hour
quote-age bound, explicit demo no-halts assumptions, and $100,000 hypothetical
starting options cash per tracker with zero holdings. It did not execute trades,
launch a funded tracker, demonstrate the reference five-observation collection,
or submit these receipts to an external PFTL network. The [dated demo record](/research/options-tee-indices/demo-record.json) preserves the effective parameters and result identities.

The PFTL implementation is in [PR #38](https://github.com/postfiatorg/postfiatl1v2/pull/38).
The demonstrated state is documented in the
[Micron](https://github.com/postfiatorg/postfiatl1v2/blob/912c476a6d0e0224e44bbe6b091989e14ef43c88/docs/yolo/evidence/target-receipt-v1-liquid-mu-20260906-summary.json)
and [Nvidia](https://github.com/postfiatorg/postfiatl1v2/blob/912c476a6d0e0224e44bbe6b091989e14ef43c88/docs/yolo/evidence/target-receipt-v1-liquid-nvda-20260906-summary.json)
qualification records. The [verification map](https://github.com/postfiatorg/postfiatl1v2/blob/c1b3a6bec14b4fe76bc3e4f95fecd4b9b0691f53/docs/yolo/target-receipt-v1.md#where-verification-lives)
links the guest, attestation verifier, calculator, consensus checks and client.
NAVStrategies contains the measured collection, orchestration and replay side.

The next product milestone is to connect the demonstrated calculation to actual
holdings: deploy and activate the receipt feature, maintain ongoing collection,
execute the chosen strategy and reconcile the resulting account. An options
NAVCoin then adds reserve valuation, custody and holder rights, share accounting,
Ethereum issuance, liquidity and a specified exit process. Each layer needs
evidence for its own claim before the combined product can be presented as live.
