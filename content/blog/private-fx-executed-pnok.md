---
title: "A Controlled Private FX Swap: pfUSDC–pNOK Atomic Settlement"
date: 2026-08-02T00:00:00Z
draft: false
url: "/private-fx-executed-pnok/"
breadcrumb_label: "Blog"
breadcrumb_url: "/blog/"
summary: "On 1 August 2026, a controlled, bilateral, pre-arranged swap atomically exchanged 20 private pfUSDC for 210 sandbox-backed pNOK in one Asset-Orchard state transition. Real Ethereum-mainnet USDC funded the dollar leg; the NOK leg relied on sandbox WNOK and an operator-controlled checkpoint. The run demonstrated atomicity, replay resistance, validator convergence, recovery, and supply conservation—not live redemption, Tier-4 finality, operator-blind matching, price discovery, market depth, or an independent audit."
description: "An evidence-backed engineering report on a controlled pfUSDC–pNOK atomic swap using real Ethereum-mainnet USDC and sandbox WNOK-backed pNOK, with explicit limits around finality, redemption, matching, privacy, and independent assurance."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - FX
  - Private FX
  - pNOK
  - pfUSDC
  - CBDC
  - Settlement
  - Privacy
  - PFTL
  - Post Fiat
---

*[A Proposal for Better Private FX Settlement](/private-fx-settlement/) argued that two currency legs should become one atomic event without publishing private settlement data. This direct engineering follow-up reports a narrower result: on 1 August 2026, controlled participants executed a bilateral, pre-arranged fixed-rate pfUSDC–pNOK swap through the shipping browser, prover, and wallet-proxy path.*

Real Ethereum-mainnet USDC entered Post Fiat L1 (**PFTL**, the settlement ledger used in this experiment) as pfUSDC. The counter-asset was pNOK backed one-for-one by WNOK in an isolated sandbox. Twenty pfUSDC and 210 pNOK then changed owners atomically in one **Asset-Orchard** state transition—PFTL’s shielded-note system for privately holding and spending assets.

This was not a live FX market or production bridge. The pNOK route used an operator-controlled source checkpoint, the rate and participants were arranged in advance, and redemption was not exercised.

> **Result and boundary**
>
> | Demonstrated | Not demonstrated |
> |---|---|
> | 20 pfUSDC exchanged atomically for 210 pNOK | Production or official NOK |
> | Real Ethereum-mainnet USDC funded pfUSDC | Tier-4 source finality or live pNOK redemption |
> | Both private notes settled in one state transition | Operator-blind matching or price discovery |
> | Exact replays had no effect | Multi-party depth or statistical anonymity |
> | Six validators converged | Independent security audit |
> | Browser/prover/proxy recovery campaign completed | Production readiness |
> | pfUSDC and pNOK supply accounting held | Unattended public operation |

The acceptance reports linked below are project-authored evidence from the qualification campaign. They are not an independent security audit.

## Terms used in this report

A shielded **note** records private asset ownership and value through a commitment rather than a public account balance. Asset-Orchard consumes input notes and creates output notes under a zero-knowledge proof. Each spend publishes a **nullifier**, a unique one-time marker that lets validators reject reuse without revealing the note opening.

The experiment used a finalized fixed exchange rate, called **FIX** in its artifacts. Here, FIX means the fixed quote approved for this swap—not the Financial Information eXchange messaging protocol. “Fixed quote” is used below.

**Tier-4** denotes the intended source boundary in which PFTL verifies source-chain finality cryptographically rather than relying on an operator checkpoint or signer fallback. This experiment did not reach that boundary.

**K=15** is the configured proving-circuit size parameter used by the two circuits prewarmed during recovery testing.

## What executed

The earlier proposal combined three objectives:

1. settle both currency legs payment-versus-payment, or neither;
2. avoid publishing private note data to the settlement ledger; and
3. eventually cross opposite flow through a discrete, uniform-price batch rather than a continuous public order book.

This run exercised the atomic-settlement primitive and narrow ledger privacy. It did not implement the proposed batch market.

A buyer deposited 20 USDC on Ethereum mainnet, received 20 pfUSDC on PFTL, and shielded it into an Asset-Orchard note. A controlled liquidity facility supplied 210 pNOK from existing private inventory. The fixed quote was 10.500000 pNOK per pfUSDC, with zero fee and zero price impact.

```text
Ethereum mainnet             Post Fiat L1                    Besu sandbox
─────────────────            ────────────                    ────────────
20 USDC                      20 pfUSDC note                  500 WNOK
   │                              │                              │
   └─ deposit + finality ────────▶│                              └─ vault lock
                                  │                                   │
                                  │              500 pNOK issued ◀────┘
                                  │                    │
                                  ▼                    ▼
                         ┌──────────────────────────────┐
                         │     Asset-Orchard swap       │
                         │                              │
                         │ buyer:    20 pfUSDC ─────┐   │
                         │                         ├──▶ buyer: 210 pNOK
                         │ facility: 210 pNOK ──────┘   │
                         │                              │
                         │ one proof · two nullifiers   │
                         │ two outputs · zero fee       │
                         └──────────────────────────────┘
```

The 500 pNOK issuance established the facility’s sandbox-backed inventory; only 210 pNOK participated in the reported buyer acquisition.

## The dollar leg: mainnet USDC to private pfUSDC

The buyer did not start with a balance created solely for the internal test. The run approved and deposited exactly 20,000,000 six-decimal USDC atoms into the canonical Ethereum-mainnet vault in [transaction `0xf124…72ac`](https://etherscan.io/tx/0xf12487ac976fc7f148ee44de75ad7375a2af4c2bcf35ad5805bcdf9cb64972ac).

The recorded vault balance and total obligations each rose from 165,031,396 to 185,031,396 atoms. The depositor’s USDC balance fell by the same 20,000,000 atoms.

The deposit record deterministically bound the source chain, vault, token, depositor, amount, nonce, PFTL recipient, and route identifier. Once the pfUSDC claim became spendable on PFTL, the wallet burned the transparent balance into a private Asset-Orchard note. The public ingress record contained the burn transaction and output commitment; the note opening and spend authority remained wallet-local.

Thus the dollar leg began with a public, source-bound cash event and crossed the privacy boundary afterward.

## The NOK leg: sandbox WNOK to pNOK

The other leg used the [CBDC tokenization sandbox](https://github.com/Norges-Bank-CBDC-Lab/cbdc-tokenization-sandbox/tree/f1ad067e09fa3e4838be9605bd1fe450831e9244) at pinned upstream revision `f1ad067e`. The controlled bridge was added at source commit [`7e293b4`](https://github.com/goodalexander/cbdc-tokenization-sandbox/tree/7e293b4288279849bfe4810b25eea8d577c53bd7), and the isolated Besu chain used a digest-pinned Besu 26.7.0 image.

The source vault held 500 WNOK. The PFTL route counted one 500-WNOK deposit and issued exactly 500 pNOK atoms. Project-authored acceptance checks found that the vault had the required allowlist and transfer permission but no WNOK mint or burn authority. They also checked that issued pNOK supply equaled the counted bridge value.

The facility shielded that pNOK inventory into Asset-Orchard. The swap transferred existing pNOK; it did not mint pNOK during execution, extend unsecured NOK credit, or repair reserves afterward.

**Sandbox WNOK and pNOK are not official NOK, not a production CBDC, and not an endorsement by Norges Bank.** The source boundary remained an operator-controlled checkpoint rather than a Tier-4 verifier of Besu finality.

## Public fixed quote, private note data

The experiment did not perform price discovery. It consumed a consensus-registered, expiring, capacity-bounded fixed quote:

```text
pair                  pfUSDC / pNOK
buyer pays            20.000000 pfUSDC
buyer receives        210 pNOK
fixed quote           10.500000 pNOK / pfUSDC
fee                   0
price impact          0 bps
execution             private on PFTL
source boundary       controlled sandbox checkpoint
```

The pair, rate, expiry, reservation, remaining capacity, and final action identifiers were public. Publishing those fields made the terms auditable and prevented the wallet or coordinator from substituting another rate after approval.

The note openings, spend-authority material, input ownership, and output ownership remained private. Inside the proof, both input notes had to be valid members of the anchored commitment tree; both spends had to be authorized; both nullifiers had to be fresh; both outputs had to be correctly formed; and value had to be conserved separately for each asset.

Validators checked the proof and applied one transition containing two nullifiers and two output commitments. They did not receive the private note openings or take custody of either leg. In this controlled state machine, there was no valid outcome in which only one payment settled.

## Qualification, replay, and recovery

The campaign went beyond one successful execution. It ran ten consecutive browser-initiated pNOK acquisitions and nine inverse private swaps that restored inventory between acquisitions: 19 unique private jobs in total.

Across those jobs:

- both input nullifiers and both outputs appeared exactly once for each acquisition;
- pfUSDC and pNOK issued supply remained unchanged through secondary swaps;
- every tested exact replay was rejected without changing supply or appending an output;
- all six PFTL validators converged;
- the fixed quote’s bounded capacity was exhausted exactly after the nineteenth fill; and
- no manual state edit repaired inventory between runs.

The project-authored harness evaluated 18 assertions and reported 18 passing. Checks covered source revisions, vault privileges, one-for-one pNOK accounting, fixed-quote arithmetic, output ownership, replay behavior, a public-artifact privacy scan, wallet labels, browser repetition, and validator convergence. The evidence is preserved in the commit-pinned [acceptance report](https://github.com/postfiatorg/postfiatl1v2/blob/b79b46c6a9034c9389aac0cc690a6c7d11809e85/deployments/pnok-private-fix-20260801/acceptance/public/report.json) and [acceptance status](https://github.com/postfiatorg/postfiatl1v2/blob/b79b46c6a9034c9389aac0cc690a6c7d11809e85/docs/status/PNOK-PRIVATE-FIX-DEMO-ACCEPTANCE-20260801.md).

Recovery tests deliberately restarted a validator during an inverse swap, restarted the resident prover and cold-prewarmed both K=15 circuits, and killed the wallet proxy during a browser acquisition. After a reload and wallet unlock, the durable job resumed and completed with `retry_count = 2`. Duplicate submission remained idempotent.

Cold-starting both circuits took approximately 323 seconds on the 32-thread host. The warm path supported this controlled run, but the result reinforces the operational requirement for a resident, prewarmed prover.

## Privacy without an anonymity claim

Asset-Orchard hid ledger note data: note openings, spend authority, owners, and output ownership were not published. That does not make the trade anonymous.

The pair and fixed quote were public. Every browser acquisition repeated the exact 20-pfUSDC/210-pNOK size. Timing and knowledge that the only available quote had been exercised therefore permitted statistical inference about the likely amount, despite the absence of a public amount field in the shielded action.

A single trade can have cryptographically private state and weak statistical cover. Variable sizes, more counterparties, deeper batches, and internal crossing are needed before this primitive can support the proposal’s stronger market-level leakage bounds.

## Proposal questions answered—and left open

| Question from the proposal | Result on 1 August 2026 |
|---|---|
| Can two private currency assets settle as one PvP action? | Yes, in the controlled Asset-Orchard path. |
| Can validators certify it without note openings? | Yes. |
| Can a public rate bind private settlement? | Yes, through the expiring, capacity-bounded fixed quote. |
| Can exact replay be rejected without changing supply? | Yes, in the tested cases. |
| Can the browser path recover after component failure? | Yes, for the tested validator, prover, and proxy restarts. |
| Is pNOK ingress Tier-4? | No; it used a controlled sandbox checkpoint. |
| Was live pNOK-to-WNOK redemption exercised? | No. |
| Was matching operator-blind or was price discovered? | No; participants and rate were pre-arranged. |
| Was multi-party batch depth demonstrated? | No; there was no live order book or batch auction. |
| Was the system independently audited? | No; the cited reports are project-authored. |

The experiment established a specific primitive: mainnet USDC could enter as pfUSDC, two private asset notes could exchange atomically under a public fixed quote, replays could be made ineffective, six validators could converge, recovery could survive the tested failures, and supply accounting could remain intact.

The remaining work is separate and substantial: Tier-4 pNOK finality, proof-verified egress and live redemption, operator-blind matching, price discovery, multi-party depth, independent security review, and production operations. The proposal’s market is not complete, but its atomic settlement primitive has now been exercised under controlled conditions with the trust boundary stated alongside the result.

