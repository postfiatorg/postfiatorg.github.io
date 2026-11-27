---
title: "Hyperliquid NAVCoin on Solana & Scheduled FX Fix Guide"
url: "/docs/hyperliquid-navcoin-fx-fix/"
type: "page"
layout: "single"
kicker: "Near-Term NAVCoin Operations"
date: 2026-11-27
summary: "Operator and user guide for Hyperliquid-reserve NAVCoins traded on Solana via HyperCoreReserveReader and non-issuer attestors, plus scheduled London-style FxFixPacketV1 settlement windows."
---

Every Post Fiat NAVCoin combines five building blocks:

1. **Secondary-venue wrapper + NAV guard** (e.g., Uniswap ERC-20 wrapper + `NAVGuardHook` on Ethereum, or SPL wrapper + Solana liquidity routing)
2. **Canonical `postfiatl1v2` NAVCoin asset + primary-market offer book**
3. **Proof-backed `USDC -> pfUSDC` bridges** on Ethereum and Solana
4. **Primary-market exit routes** back into settlement assets
5. **Scheduled London-style FX Fix (`FxFixPacketV1`)** for discrete, uniform-rate settlement windows

This guide covers the two operational workflows that bring Hyperliquid-backed NAVCoins to Solana and automate scheduled FX Fix windows.

## Part A: Hyperliquid NAVCoin on Solana

### 1. Reserve Observation Architecture

Hyperliquid account state is public and address-indexed (no API keys required), supporting two complementary verification layers:

- **On-chain HyperEVM receipt (`HyperCoreReserveReader.sol`):** Reads HyperCore perp clearinghouse state and spot balances inside a HyperEVM block so the receipt sits inside the exact committee-signed HyperEVM receipt trie.
- **Multi-fetch non-issuer attestation (`postfiat_rpc.hyperliquid`):** `N` independent observers POST to Hyperliquid `/info` (`clearinghouseState`, `spotClearinghouseState`, `allMids`) against the declared **master account address** (never an agent wallet address, which returns empty data; any subaccounts or vaults must be enumerated explicitly in the declared reserve perimeter).

#### Deterministic Normalization (`postfiat.nav_observation.hyperliquid.v1`)

1. All numeric fields stay verbatim decimal strings (zero floating-point round-trips; finite decimal validation enforced).
2. `assetPositions` and spot `balances` sort canonically by `coin`.
3. Observers hash canonical JSON under domain tag `postfiat.nav_observation.hyperliquid.v1` using `SHA3-384`.
4. **Non-issuer attestor invariant (Pillar 7):** Whenever `attested_value > 0` on a fee-enabled NAVCoin, `postfiatl1v2` consensus requires the attesting signature from a registered `NavAttestor` with **`attestor_account != issuer_account`**, and the explorer displays the proven vs. attested reserve split explicitly.

### 2. Solana Swap & Bridge Route (User Flow)

```text
Solana USDC  --(Solana bridge)-->  pfUSDC on postfiatl1v2  --(NAV primary/DEX route)-->  HL-NAVCoin
                                                                                              |
Solana SPL HL-NAVCoin  <--(Solana egress bridge + verifier)--  postfiatl1v2 HL-NAVCoin <-----+
```

1. **Acquire on Solana:** Users swap `USDC` for the SPL-wrapped Hyperliquid NAVCoin on Solana (or bridge `USDC` through the Solana `pfUSDC` vault to mint directly at finalized `nav_per_unit` on `postfiatl1v2`).
2. **Verify live NAV before swapping:** Query `nav_asset_info(asset_id)` on `postfiatl1v2` (or inspect the explorer NAVCoin card) to verify the latest finalized `nav_per_unit`, epoch height, `HyperCoreReserveReader` / attestor status, and deadman freshness (`max_epoch_gap_blocks`).
3. **Exit to USDC:** Burn/export the SPL NAVCoin back to `postfiatl1v2`, redeem at finalized NAV via `NavRedeemAtNav` into `pfUSDC`, and exit `pfUSDC` to Solana or Ethereum `USDC`.

### 3. Operator Checklist (Hyperliquid Reserve Attestation)

1. Register the `NavProofProfile` (`source_class = "hyperliquid"` or `"hyperliquid-testnet"`) with explicit `max_snapshot_age_blocks`, `max_epoch_gap_blocks`, `min_attestations`, and `tolerance_bp`.
2. Enumerate the exact master Hyperliquid address (plus every subaccount/vault) in `reserve_accounts`.
3. Verify `HyperCoreReserveReader` receipt inclusion and collect independent non-issuer attestations (`attestor_account != issuer_account`).
4. Submit `NavReserveSubmit` and `NavEpochFinalize`; confirm `nav_per_unit == floor(V * U / S)` and verify Solana route NAV guard repins to the new epoch height.
5. **Live dust-swap verification record:** `[INSERT LIVE SOLANA HYPERLIQUID NAVCOIN DUST SWAP TX HASHES AFTER UAT]`

---

## Part B: Scheduled London-Style FX Fix (`FxFixPacketV1`)

Instead of continuous public order-book slippage, Post Fiat's **FX Fix** lets an operator publish a consensus-finalized, time-bounded, capacity-bounded fixed exchange rate (`FxFixPacketV1`, schema `postfiat.fx_fix.packet.v1`) over a scheduled window (for example, daily London 16:00 UTC or intraday UTC windows).

### 1. `FxFixPacketV1` Wire Structure & Limits

| Field / Constant | Rule / Bound | Purpose |
| --- | --- | --- |
| `schema` / `version` | `postfiat.fx_fix.packet.v1` / `1` | Canonical packet identifier |
| `operator` | Valid `postfiatl1v2` account | Authorized fix operator |
| `base_asset_id`, `quote_asset_id` | Distinct issued asset IDs | Asset pair (e.g., `pfUSDC` / `pNOK` or `pfUSDC` / NAVCoin) |
| `epoch` & `previous_fix_hash` | Monotonic (`epoch == 1` has `None`; `epoch > 1` links prior hash) | Tamper-evident fix chain |
| `ratio_numerator`, `ratio_denominator` | Nonzero `u64` exact rational | Fixed exchange rate (zero floating point) |
| `band_bps` / `fee_bps` | `<= 10_000` (NAVCoin fix cap: `<= 100 bps` / `1%` per Pillar 7) | Price band & fee rate |
| `valid_from_height`, `expires_at_height` | `valid_from <= expires_at` | Deterministic block-height execution window |
| `minimum_base_atoms`, `capacity_base_atoms`, `capacity_quote_atoms` | `1 <= min <= capacity` | Per-fill floor and window liquidity bounds |
| `max_fills` | `1..=1,024` (`MAX_FX_FIX_FILLS`) | Hard per-fix fill ceiling |
| `source_label`, `source_observation_commitment` | 96-hex `SHA3-384` commitment | Reference-rate observation evidence |
| `governance_policy_hash` | 96-hex `SHA3-384` | Active governance policy binding |
| `packet_hash` | `SHA3-384("postfiat.fx_fix.packet_hash.v1\0" || preimage)` | Deterministic packet ID |

Global state limits: max `128` active `FxFixStateV1` entries (`MAX_FX_FIX_STATES`), max `1,024` total reservations (`MAX_FX_FIX_RESERVATIONS`), and max `64` active reservations per fix (`MAX_ACTIVE_FX_FIX_RESERVATIONS_PER_FIX`).

### 2. Scheduled Execution Flow (Operator & User)

1. **Schedule publication (Operator):** Before window open (`valid_from_height`), the scheduled fix daemon collects the reference observation, computes `source_observation_commitment`, builds `FxFixPacketV1` chaining `previous_fix_hash`, and submits the consensus registration transaction.
2. **Discovery & quote (User / Wallet):** Clients call read RPCs:
   - `fx_fix_list` — enumerate active and scheduled fix windows
   - `fx_fix_info` — inspect exact rate, band, fee, capacity, and expiry height
   - `fx_fix_quote` — compute exact integer quote atoms for a candidate `base_atoms` amount (validates `minimum_base_atoms <= base_atoms <= uncommitted_capacity`)
3. **Reservation (`active` -> `filled` or `released`):** Wallet acquires a deterministic `reservation_id` (`postfiat.fx_fix.reservation_id.v1`) locking capacity for the window.
4. **Atomic settlement:** The swap executes within `[valid_from_height, expires_at_height]`, consuming the exact reservation once (`state = filled`, `fill_count += 1`). Any replay attempt is rejected with `asset_orchard_fx_fix_not_active`.
5. **Expiry & next window:** Once `block_height > expires_at_height`, unfilled reservations release cleanly and the scheduler publishes `epoch + 1` chaining the closed fix's `packet_hash`.

### 3. Transparency & Asset-Gating Note

- Default permissionless NAVCoins and `pfUSDC` pairs settle cleanly across scheduled FX Fix windows.
- Credential-gated assets ([Pillar 8](/docs/did-credentials/)) stay outside shielded pools in v1 and settle via the transparent scheduled fix path subject to `asset_gate(...)`.
- **Live scheduled FX Fix fill record:** `[INSERT LIVE SCHEDULED FX FIX PACKET HASH & FILL TX HASH AFTER UAT]`
