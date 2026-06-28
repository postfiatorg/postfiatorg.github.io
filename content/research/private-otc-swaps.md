---
title: "Private OTC Swaps"
date: 2026-06-25T00:00:00Z
url: "/research/private-otc-swaps/"
summary: "A devnet report on Post Fiat's transparent and shielded NAVCoin swap demos: what happened, what PFTL checks, what Orchard hides, and what remains self-published."
description: "A devnet report on Post Fiat's transparent and shielded NAVCoin swap demos, including public checks, private note flow, limitations, and evidence boundaries."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - OTC
  - Privacy
  - Shielded
  - pfUSDC
  - PFTL
  - Uniswap
  - Orchard
draft: false
---

> **Status / byline**
>
> **By:** Post Fiat  
> **Date:** June 25, 2026  
> **Network:** `postfiat-wan-devnet`  
> **Scope:** self-published devnet execution report for small proof amounts  
> **Not:** mainnet deployment, third-party audit, production benchmark, or independently replicated verification

Post Fiat is building crypto accounting infrastructure around **PFTL**, the Post Fiat L1 used in this demo to record and certify NAV and swap state transitions. A **NAVCoin** is a Post Fiat asset whose issuance and redemption flow is tied to NAV accounting and proof-of-reserves policy. **a651** is the specific NAVCoin asset used here. **pfUSDC** is the PFTL stablecoin input used by the swap path. **Orchard** is the shielded note system used to hide private ownership and transfer details while still producing proofs the chain can check. **StakeHub** is the internal operator UI used to run the demos; it is not presented here as a public repo or audited product.

This page exists to make one narrow result easy to inspect: on June 25, 2026, StakeHub ran two forms of the same NAVCoin swap workflow on devnet. The first is a transparent PFTL-only control path. The second puts an Orchard shielded path in the middle. The point is not to claim production readiness. The point is to separate the public accounting checks from the private user path and to show exactly where the evidence is strong, weak, or self-published.

For a visual walk-through of the same sequence, see [the illustrated primer](/research/private-otc-swaps/primer/).

## The two paths in one minute

The **transparent path** is the control group. It keeps everything on the public PFTL path: establish the a651 trustline, mint through the primary NAV path, run NAV money-in, create a NAV exit, and produce a final summary. Nothing is hidden. That is useful because it tests the accounting path without a privacy layer.

The **shielded path** uses the same economic idea but adds privacy in the middle. Public USDC is represented on PFTL as pfUSDC. pfUSDC is shielded into an Orchard note. The private note is swapped into a private a651 note. Validators certify the shielded proof. Then private egress creates the public exit artifact needed for redemption.

A simple way to read the split is:

- **Transparent control:** can the NAV-aware state machine run end to end when everyone can see the path?
- **Shielded path:** can the same flow hide note ownership and routing while still giving PFTL enough information to reject invalid state transitions?

The June 25 evidence says both paths completed on devnet. It does not say the system is audited, mainnet-live, externally verified, or ready for large-value use.

## Why not just use Uniswap?

Uniswap is a good public market venue. It gives token holders and buyers price discovery, routing, liquidity pools, and composability from Ethereum wallets. If a NAVCoin has a public secondary market, an AMM can be part of that access surface.

But an AMM trade and NAV-aware settlement are different things.

On Uniswap, a buyer usually trades against a pool. The pool enforces its AMM invariant; it does not know whether a NAV proof is fresh, whether new cash has been counted into a reserve policy, or whether a particular asset's supply rules were followed. The trade is also public. Size, timing, route, slippage, and downstream wallet activity are visible to observers, and MEV or thin liquidity can matter.

The Post Fiat route is more structured. It tries to put asset-specific accounting into the transaction path:

- pfUSDC is the stablecoin input recognized by the PFTL flow.
- a651 is the NAVCoin asset whose movement is constrained by NAV policy.
- The transparent path exposes the mechanics for inspection.
- The shielded path keeps note ownership and routing private while validators check the proof.
- The exit remains public where redemption or bridge-out needs a visible handoff.

That structure is the advantage. It is not a claim that this route is more liquid, more battle-tested, cheaper, or safer today. In this report it is a devnet path for showing how NAV-aware settlement and shielded user movement can fit together.

## Transparent control path

The transparent path is intentionally boring. It removes Orchard from the question and asks whether the NAV flow works as a public state machine.

In plain sequence:

1. A PFTL wallet is prepared.
2. The a651 trustline is established.
3. The primary NAV path mints the demo amount.
4. NAV money-in is recorded.
5. A NAV exit is created.
6. A final PFTL summary is produced.
7. Bridge-out is deferred in the transparent run records.

Two June 25 transparent runs completed:

| Report | Result | Total time | Status |
|---|---:|---:|---|
| `stakehub-transparent-20260625T133727Z-07e3aad6/pftl-only-summary.json` | `final_summary_ok=true` | 43.14s | `on_pftl_complete_bridge_out_deferred` |
| `stakehub-transparent-20260625T133820Z-d86740e9/pftl-only-summary.json` | `final_summary_ok=true` | 38.04s | `on_pftl_complete_bridge_out_deferred` |

This path is the baseline. If the public NAV roundtrip fails, a shielded version would only make the problem harder to diagnose. Running the transparent path first gives operators and reviewers a simpler control case: public inputs, public outputs, public receipts, and no private-note layer.

## Shielded path

The shielded path adds Orchard between public ingress and public egress.

In plain sequence:

1. Create or reuse a PFTL wallet.
2. Fund devnet gas.
3. Capture the NAV proof before the user movement.
4. Prepare the shielded wallet prover.
5. Confirm or accumulate the required USDC inventory.
6. Bridge the devnet USDC input into PFTL as pfUSDC.
7. Shield pfUSDC into an Orchard note.
8. Privately swap the pfUSDC note into an a651 note.
9. Submit the shielded batch for PFTL certification.
10. Egress from shielded a651 to the public a651 exit path.
11. Redeem or withdraw through the public exit path.
12. Capture the NAV proof after the movement.

The latest shielded run in the manifest is:

| Report | Started | Completed | Steps | Result |
|---|---:|---:|---:|---|
| `stakehub-shielded-nav-swap-e2e-20260625T122435Z.json` | 12:24:35Z | 12:38:20Z | 12/12 | complete |

That run used the `pfUSDC -> a651` pair. It recorded `amount: 1.00`, `bridge_in_amount: 10`, and `settlement_reserve_amount: 1`. Cold prover prewarm took about 341.6 seconds. Once warm, swap proof creation took about 6.06 seconds and transport/certification took about 4.90 seconds. The shielded swap certificate reached PFTL height 437 with five validator votes. Private egress completed, the privacy scan returned ok, and bridge-out recorded `delta_ok=true`.

Those numbers are useful execution data, not a production latency promise. A cold devnet prover, a small demo amount, and a limited privacy set should not be confused with a live market.

## What PFTL checks

The chain-visible side of this workflow is narrow but important. PFTL and its validators can check the public state transition they are asked to accept. In this demo that includes items such as:

- asset identifiers and amounts used in the public transaction path;
- trustline and NAV flow state needed for the transparent control run;
- shielded proof validity for the submitted batch;
- nullifier use, so the same private note cannot be spent twice;
- certificate acceptance and validator vote count for the shielded swap;
- public egress and bridge-out fields needed for redemption.

That is the useful part of adding a chain-checked path. The private owner does not need to reveal every note detail for validators to reject an invalid shielded transition.

## What remains private, internal, or self-published

The private part is also narrow. Orchard hides the wallet's note opening, note ownership, and route through the shielded pool. PFTL receives a proof and public fields; it does not need the wallet's internal note data.

But several things are not established by this page alone:

- The public manifest and this article are self-published by Post Fiat.
- Raw operator artifacts are retained internally, not published here.
- There is no third-party audit cited.
- There is no public block explorer or independent replication cited.
- StakeHub is an internal operator surface, not a public repository linked for review.
- The manifest's commit strings are source-code context labels, not independent validation.
- Reserve proof quality still depends on source data and policy correctness. Cryptography can make a state transition checkable; it cannot make a dishonest source truthful.
- The demo's privacy set is not the privacy set of a crowded production market.

This distinction matters. The devnet run demonstrates that the configured path completed under Post Fiat's own infrastructure and recorded the expected statuses. It does not let a reader independently replay every raw artifact from this page.

## What this means for OTC

"OTC" here does not mean a spreadsheet and a handshake. It means application-mediated settlement against a NAV-aware chain, with transparent and shielded modes.

For a primary subscription, the central question is whether buyer cash is recognized by the system and whether newly released NAVCoin supply follows the NAV policy. For a secondary OTC swap, the central question is whether existing holder inventory can move without forcing the buyer through a public AMM route. The same infrastructure can support both cases, but they are not economically identical.

The transparent path is the operator and audit-control surface. It is easier to inspect because it is not private.

The shielded path is the user privacy surface. It hides the user's note route while still requiring a valid proof and a certified PFTL transition.

The practical advantage versus a plain AMM transaction is not magic privacy or guaranteed backing. It is that the swap can be attached to NAV-aware accounting rules, PFTL certification, and a shielded middle path. The cost is complexity, lower present-day liquidity, and the need to trust more project-specific infrastructure until there is broader deployment, audit coverage, and independent review.

## What is still not solved

This is a devnet demonstration only. It is not deployed on mainnet. It is not third-party audited. It used small proof amounts. The manifest explicitly records `ethereum_mainnet_spend: false`.

The proof system and the accounting policy solve different problems. A proof can help validators check that a submitted transition satisfies the circuit and state rules. It does not certify that every off-chain source is honest, that every policy choice is wise, or that the implementation is free of bugs.

The privacy story is also conditional. A shielded system needs a meaningful anonymity set, careful wallet behavior, and safe egress patterns. A demo-sized run can exercise the mechanics, but it cannot by itself demonstrate production privacy under adversarial traffic analysis.

The right conclusion is modest: the transparent control path and shielded path both completed on devnet with recorded evidence. That is a useful milestone. It is not the end of review.

## Appendix: evidence and audit boundary

The public evidence file for this post is the sanitized manifest at [`/evidence/private-otc-swaps-20260625/manifest.json`](/evidence/private-otc-swaps-20260625/manifest.json).

How to read it:

- It is a Post Fiat self-published manifest, not a third-party attestation.
- It summarizes run names, timings, statuses, proof sizes, vote counts, receipt identifiers, and UI context.
- It does not publish the raw operator directories.
- It does not provide an external block explorer or independent replay environment.
- It is useful for checking whether this article matches the reported execution data.
- It is not enough, by itself, to validate production security or reserve-source truth.

### Declared status boundary

| Field | Manifest value |
|---|---|
| Schema | `postfiat-private-otc-swaps-evidence-v1` |
| Generated | `2026-06-25T22:35:00Z` |
| Network | `postfiat-wan-devnet` |
| Asset pair | `pfUSDC -> a651 NAVCoin` |
| Mainnet deployed | `false` |
| Third-party audited | `false` |
| Values | `small-dollar devnet proof amounts` |
| Ethereum mainnet spend | `false` |

### Shielded executions

| Report | Started | Completed | Steps | Status |
|---|---:|---:|---:|---|
| `stakehub-shielded-nav-swap-e2e-20260625T034439Z.json` | 03:44:39Z | 04:07:19Z | 12/12 | complete |
| `stakehub-shielded-nav-swap-e2e-20260625T040738Z.json` | 04:07:38Z | 04:21:18Z | 12/12 | complete |
| `stakehub-shielded-nav-swap-e2e-20260625T122435Z.json` | 12:24:35Z | 12:38:20Z | 12/12 | complete |

Latest shielded execution details:

- Report: `stakehub-shielded-nav-swap-e2e-20260625T122435Z.json`
- Prover prewarm: `341568.160297 ms`
- Swap proof creation: `6064.954345 ms`
- Transport/certification: `4903.615972 ms`
- Shielded swap certificate height: `437`
- Shielded swap validator votes: `5`
- Shielded swap receipt accepted: `true`
- Private egress status: `private_egressed`
- Private egress privacy scan ok: `true`
- Private egress proof size: `6848 bytes`
- Bridge-out status: `bridged_out`
- Bridge-out delta ok: `true`
- Final balances: `20152055 pfUSDC atoms`, `1 a651 atom`

### Transparent executions

First transparent run:

- Report: `stakehub-transparent-20260625T133727Z-07e3aad6/pftl-only-summary.json`
- Completion status: `on_pftl_complete_bridge_out_deferred`
- Final summary ok: `true`
- Failure reasons: none
- Mint amount: `1`
- Total time: `43142.285399 ms`
- Primary mint receipt: `24196973e01710a7d9e688b90776c49a4fea5324bbc46dd0733c995179755e6f536d5e7e19c149d14d5577de451b7d44`
- NAV exit redemption id: `18589843d0da274da8b82af6f30c01fa8afdb95470eae20d45cccb332fb9f6b6898bf4647acbe5b1abc9b1516d0e34df`

Second transparent run:

- Report: `stakehub-transparent-20260625T133820Z-d86740e9/pftl-only-summary.json`
- Completion status: `on_pftl_complete_bridge_out_deferred`
- Final summary ok: `true`
- Failure reasons: none
- Mint amount: `1`
- Total time: `38040.763465 ms`
- Primary mint receipt: `91cff679b3f955beb46fcc10a98f5ea37775eb52de23edd6088886b6a91f0abd1ba12a014f84bcc2c291b43fc61f7b1b`
- NAV exit redemption id: `34f83fc9a5a4ff0622dffe41ed2010009823681ca775658fb34acc3257f01eef8ef8372df4540cdfc829cb1a212c2116`

### UI and source-code context

The manifest records `transparent_pageerrors: 0` and `transparent_console_errors: 0` for the transparent UI path `Shielded NAV Swap tab -> Transparent No Orchard -> Run Transparent E2E`.

It also records two internal source-code context strings:

- `dce65b1 Make transparent NAV roundtrip demo repeatable`
- `2795afc Make shielded NAV swap repeatable end to end`

Treat those as context for mapping the self-published runs to internal engineering changes. They are not public repository citations and should not be read as independent validation.
