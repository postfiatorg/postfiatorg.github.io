---
title: "Hyperliquid NAVCoin Swaps on Solana and the Scheduled Post Fiat FX Fix"
date: 2026-11-27T00:00:00Z
draft: true
summary: "Wiring HyperCoreReserveReader and independent non-issuer attestations to Solana NAVCoin swaps, alongside automated London-style FxFixPacketV1 settlement windows on postfiatl1v2."
author: "Post Fiat"
categories:
  - NAVCoin
tags:
  - Post Fiat
  - NAVCoin
  - Hyperliquid
  - Solana
  - FX Fix
  - postfiatl1v2
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Every Post Fiat NAVCoin sits on five interlocking pieces: a secondary-venue wrapper with NAV protection, a canonical `postfiatl1v2` asset and primary-market book, proof-backed `USDC -> pfUSDC` bridges on Ethereum and Solana, primary exit routes back to settlement assets, and scheduled discrete settlement windows via the **Post Fiat FX Fix**.

This milestone wires two near-term production workflows together: **tracking a Hyperliquid-reserve NAVCoin on Solana** and **running scheduled London-style `FxFixPacketV1` windows**.

## Tracking a Hyperliquid NAVCoin on Solana

Hyperliquid clearinghouse and spot state are public and address-indexed, making them a natural fit for verifiable NAVCoin reserves:

- **`HyperCoreReserveReader` + multi-fetch non-issuer attestation:** Reserve observations combine HyperEVM `HyperCoreReserveReader` receipts inside the HyperEVM receipt trie with deterministic multi-fetch observations (`postfiat.nav_observation.hyperliquid.v1`) normalized over exact decimal strings — zero floating-point round-trips, querying the declared master account address (plus any explicitly enumerated subaccounts/vaults).
- **Independent non-issuer attestor enforcement:** Consistent with Pillar 7, whenever `attested_value > 0` on a fee-enabled NAVCoin, `postfiatl1v2` consensus requires an independent registered `NavAttestor` (`attestor_account != issuer_account`), and the explorer renders the proven vs. attested split plainly.
- **Solana USDC -> `pfUSDC` -> Hyperliquid NAVCoin -> SPL wrapper:** Users can enter or exit through Solana `USDC` and swap the SPL-wrapped Hyperliquid NAVCoin on Solana while primary issuance, redemption, and universal `nav_per_unit == floor(V * U / S)` accounting stay anchored on `postfiatl1v2`.

## Automated London-Style Scheduled FX Fix (`FxFixPacketV1`)

Continuous public order books leak execution intent and fragment liquidity. Post Fiat's **`FxFixPacketV1`** (`postfiat.fx_fix.packet.v1`) provides discrete, uniform-rate settlement windows modeled on the London 4pm FX fix:

- **Deterministic chain of fixes:** Each scheduled window publishes exact rational pricing (`ratio_numerator / ratio_denominator`), `band_bps`, `fee_bps` (capped at `100 bps` / `1%` for NAVCoins), `valid_from_height`, `expires_at_height`, `minimum_base_atoms`, `capacity_base_atoms`, `capacity_quote_atoms`, `max_fills` (`<= 1,024`), a `SHA3-384` `source_observation_commitment`, and `previous_fix_hash` chaining back to epoch 1.
- **Bounded, replay-proof reservations:** Users inspect live windows via `fx_fix_list`, `fx_fix_info`, and `fx_fix_quote`, lock a deterministic `reservation_id` (`active` -> `filled` or `released`), and settle atomically within the active block-height window. Each reservation executes exactly once; any replay attempt is rejected with `asset_orchard_fx_fix_not_active`, and unfilled reservations release cleanly at window expiry.
- **Transparent path for gated assets:** Permissionless NAVCoins and `pfUSDC` pairs settle cleanly across scheduled FX Fix windows, while credential-gated assets ([Pillar 8](/docs/did-credentials/)) settle on the transparent scheduled fix path under `asset_gate(...)`.

## Live UAT Evidence

- **Solana Hyperliquid NAVCoin live dust swap tx (`Solana`):** `[INSERT LIVE SOLANA TX HASH AFTER UAT]`
- **Hyperliquid reserve attestation & `NavEpochFinalize` tx (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Scheduled `FxFixPacketV1` registration & live fill tx (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer NAVCoin & FX Fix window view:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

See the operator checklists, RPC queries, and normalization details in the [Hyperliquid NAVCoin on Solana & Scheduled FX Fix Guide](/docs/hyperliquid-navcoin-fx-fix/).
