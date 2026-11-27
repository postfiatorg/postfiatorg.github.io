---
title: "The Open NAVCoin SDK and Optional Deterministic Fee Schedules"
date: 2026-11-27T00:00:00Z
draft: true
summary: "Opening third-party NAVCoin creation with a Python and Rust SDK, universal floor(V * U / S) NAV enforcement, and 100% optional deterministic on-chain fee schedules."
author: "Post Fiat"
categories:
  - NAVCoin
tags:
  - Post Fiat
  - NAVCoin
  - SDK
  - Fees
  - postfiatl1v2
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

A NAVCoin should be a neutral software primitive anyone can build on `postfiatl1v2` — an asset backed by verified reserves that settles cleanly against `pfUSDC` and secondary pools like Uniswap.

With Pillar 7, we are opening third-party NAVCoin creation through our Python and Rust SDK and adding an **entirely optional deterministic fee schedule (`NavFeeScheduleV1`)** on chain.

## Optional Means Zero Clutter When Off

Not every NAVCoin needs ongoing fees. If a creator launches a NAVCoin without attaching `NavFeeScheduleV1`, there is zero fee logic running on chain and zero fee clutter in Task Node or the block explorer.

At the same time, consensus now enforces **`nav_per_unit == floor(V * U / S)` across EVERY NAVCoin and EVERY proof profile** — even zero-fee NAVCoins — along with `packet.circulating_supply == live_ledger_supply`. Nobody can sneak an undisclosed fee into a NAVCoin by quietly understating NAV.

## Deterministic Fee Mechanics When Enabled

Creators who choose to attach `NavFeeScheduleV1` configure any subset of four hard-capped protocol parameters using neutral, factual mechanics:

- **Annual time-based rate:** Up to **`5%/year` (`500 bps`)**, computed strictly from protocol constant `blocks_per_year` and bounded by `accrual_cap_blocks` (so annual fees stop if the deadman halts dealing).
- **High-water-mark gain rate:** Up to **`50%` (`5,000 bps`)**, calculated per finalized epoch only on per-unit net gains above the all-time high-water mark `H`.
- **Primary issue / redeem spreads:** Capped at **`5%` (`500 bps`)**.
- **FX fix fee cap:** Capped at **`1%` (`100 bps`)**.

There is no Post Fiat protocol or validator fee cut in v1.

Because `postfiatl1v2` cannot directly pull cash out of an off-chain brokerage or Hyperliquid account, accrued fees settle atomically inside `nav_epoch_finalize` by minting the exact matching number of NAVCoin units into an on-chain unclaimed bucket (counted in circulating supply, bypassing `asset_gate` so finalization can never deadlock). The recipient claims those units later via `nav_fee_claim`. Every calculation uses widened `u256` integer intermediates rounding down at every step so dust always stays with holders, and post-fee `N_after` relays directly to Ethereum's `NAVGuardHook.sol` so L1 and Uniswap stay in lockstep.

## Hard Protections Against Silent Fee Hikes

- **Minimum 7-day notice on any increase:** Raising any rate, spread, or accrual cap — or shortening the notice period — enters a pending state for at least 7 days (in blocks). Even legacy spread updates on unscheduled NAVCoins obey the exact same 7-day notice. Pure decreases apply on the next epoch.
- **No exit throttling during pending hikes:** Routes cannot reduce cash-in exit capacity while a fee increase is pending.
- **Zero retroactive taxation:** Attaching a schedule initializes `h_last = h_attach` and `H = N_current` on the first funded epoch, and mixed-rate intervals accrue at the lower of old and new rates.
- **Non-issuer attestor required for attested reserves:** Whenever `attested_value > 0` on a fee-enabled NAVCoin, consensus requires an independent `NavAttestor` with `attestor_account != issuer_account`.
- **Permanent rate ceiling lock (`rates_locked`):** Creators can permanently lock rate ceilings while preserving a visible recipient-rotation path so a lost recipient key never bricks fee claims.

## Independent Exact-Atom Verification

The Python (`postfiat_rpc.navcoin`) and Rust (`crates/rpc_sdk`) SDKs ship `create_navcoin(...)` and `recompute_fees(asset_id, epoch)` verified against 100+ shared exact-atom test vectors. Any holder can independently recompute every finalized epoch down to the single atom and compare against `NavFeeAccrualV1` on the block explorer.

## Live Devnet SDK Evidence

- **Zero-fee NAVCoin creation tx (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Fee-enabled NAVCoin creation & multi-epoch `NavFeeAccrualV1` tx hashes:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Pending fee-increase notice & cancel tx hashes:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer fee schedule & accrual view:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Follow the worked math example and SDK code snippets in the [Create a NAVCoin Guide](/docs/create-a-navcoin/).
