---
title: "Single-Stock Options Trackers"
date: 2026-09-07T00:00:00Z
draft: false
type: "blog"
url: "/research/single-stock-options-trackers/"
breadcrumb_label: "Post Fiat Research"
breadcrumb_url: "/research/"
summary: "A financial primitive for maintaining options exposure to one company—with explicit portfolio rules, private market data, and a result that anyone can verify."
description: "A visual explanation of single-stock options trackers: rolling call baskets, trusted execution environments, zero-knowledge proofs, Post Fiat receipts, and the boundary between verifiable rules and a funded investment product."
author: "Post Fiat"
options_tee: true
categories: ["Post Fiat Research"]
tags: ["Options", "Verifiable Indices", "TEE", "Post Fiat"]
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

The long-term product could be a model portfolio, a managed account or a tokenized
investment product. The engine underneath those products is the subject of this
article.

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

## 3. The rulebook is part of the product

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

## 4. From a private options chain to a verifiable target

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

## 5. What can remain private?

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

## 6. What does “trustless” mean here?

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

## 7. What does Post Fiat add?

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

PFTL is the intended ledger of record for this primitive. Another chain is not a
dependency of the demonstrated architecture. A target receipt itself grants no
order, minting or reserve authority; normal transaction fees still apply.

## 8. What could be built on top?

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

## 9. What we have demonstrated

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

The next product milestone is to connect this demonstrated calculation primitive
to an operating service: deploy and activate the receipt feature, establish the
ongoing collection process, and add any explicitly chosen execution and custody
layer.
