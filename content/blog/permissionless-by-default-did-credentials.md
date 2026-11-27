---
title: "Permissionless by Default, Optional Compliance: did:pftl and Zero-PII Credentials"
date: 2026-11-27T00:00:00Z
draft: true
summary: "Why NAVCoins on Post Fiat L1v2 never require trust lines by default, how single-point asset_gate and zero-PII XRPL-style Credentials work for opt-in gated assets, and why asset creators—not Post Fiat—choose their issuers."
author: "Post Fiat"
categories:
  - Identity
tags:
  - Post Fiat
  - DID
  - Credentials
  - NAVCoin
  - postfiatl1v2
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

One question comes up every time someone builds an asset on an XRPL-descended chain: *"Do users have to send a trust-line transaction before they can buy or receive a NAVCoin?"*

On `postfiatl1v2`, the answer is **no**. Everything is **permissionless by default**. You can receive, hold, escrow, or place a DEX offer on any default asset or NAVCoin without ever sending a manual `trust_set` transaction. Empty implicit lines auto-prune on zero-out so dust never bloats the ledger, and `requires_authorization` can **never** flip from `false` to `true` after launch.

At the same time, real-world builders sometimes need an opt-in gated asset (for example, a jurisdiction-restricted or KYC-gated NAVCoin). Pillar 8 delivers that without turning Post Fiat into a compliance gatekeeper and without putting a single byte of personal data on chain.

## Closing the Gating Bypass First: One `asset_gate(...)` Everywhere

Before adding new features, we closed a real bug in our legacy execution code where an implicit line helper accidentally set `authorized = true` on missing recipient lines even for gated assets.

Behind a governed activation height, **every** user-facing issued-asset movement — payments, swaps, DEX offers, escrows, NAV mint/redeem, Ethereum/Solana bridge imports, fast-lane permits, and `nav_fee_claim` — now runs through one single `asset_gate(asset, from, to, op_kind, block_height)` function evaluated live at the executing height.

Three design choices make gated assets practical without breaking the chain:

1. **Return-only default exit (funds are never stranded):** If a holder's credential expires or is revoked, they cannot transfer to third parties, but `offer_cancel`, escrow refunds, `AssetBurn`, `NavRedeemAtNav`, and direct `pay-issuer` transfers **always succeed**.
2. **Aggregated bridge holds `(asset, recipient)`:** Cross-chain Ethereum and Solana imports are already final on the source chain. If a recipient fails `asset_gate`, exceeds `holder_limit`, or sets `refuse_unsolicited_assets`, `postfiatl1v2` parks those units in a single aggregated claimable hold keyed by `(asset, recipient)` — never jamming a Solana batch proof and never creating unbounded per-transfer state objects.
3. **Anti-poisoning DEX & bounded clawback:** Permissionless `offer_prune_ineligible` cleans stale resting makers without exhausting the 64-cross DEX limit, and optional `asset_clawback` is strictly bounded to 64 objects per transaction.

## Zero-PII XRPL-Style Credentials & `did:pftl`

- **Creator-owned issuer trust:** Each gated-asset creator chooses which `(issuer_id, credential_type)` pairs their asset accepts (`either` manual approval OR valid credential, or `both`). Post Fiat governance never curates, approves, or bonds KYC vendors.
- **Zero PII on chain:** External verifiers run off chain and submit a tiny ML-DSA-65 signed credential storing only `(subject, issuer_id, credential_type, expiry, salted_commitment_hash)`.
- **Zero-PFT delegated onboarding (`credential_create_and_accept`):** Users sign proof-of-control and acceptance during the off-chain flow and the issuer submits them atomically, eliminating the `0 PFT` gas deadlock for brand-new accounts.
- **Reference adapters included:** We ship both a **generic W3C VC webhook adapter** and an **open-source ZK-passport verifier adapter** (Self / OpenPassport style) verified off chain, keeping heavy SNARK verifiers out of L1 consensus.
- **`did:pftl:<chain_id>:<account>`:** Every account resolves natively over `did_resolve` RPC. Wallets default to a separate account for credentialed assets and warn explicitly before linking KYC status to a public Pillar 6 social identity.

## Live UAT Evidence

- **Permissionless NAVCoin DEX trade (zero `trust_set`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Gated NAVCoin + sandbox ZK-passport / W3C VC `credential_create_and_accept` tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Credential revocation & Return-only exit tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Bridge hold creation & claim tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer Asset Policy & Issuer Registry view:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Read the full `did:pftl` spec, `asset_gate` rules, and adapter guides in the [`did:pftl`, Optional Trust Lines & Credential Policy Guide](/docs/did-credentials/).
