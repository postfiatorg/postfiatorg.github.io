---
title: "Create a NAVCoin: SDK, Neutral Fee Formulas & Accounting Guide"
url: "/docs/create-a-navcoin/"
type: "page"
layout: "single"
kicker: "Pillar 7 · Open NAVCoin Primitive"
date: 2026-11-27
summary: "How to launch a permissionless or credential-gated NAVCoin on postfiatl1v2 using the Python/Rust SDK, with optional deterministic fee schedules (NavFeeScheduleV1), exact integer math, worked example, and primary-market accounting."
---

A **NAVCoin** on `postfiatl1v2` is a neutral, open software primitive: an on-chain asset backed by verified reserves whose per-unit reference value (`nav_per_unit`) updates each finalized epoch and integrates with primary `pfUSDC` routes and optional secondary venues (such as Uniswap).

Third-party NAVCoin creation opens through the open **Python and Rust NAVCoin SDK** with two completely optional modules:

- **Optional deterministic fee schedules (`NavFeeScheduleV1`, Pillar 7):** Off by default. A zero-fee NAVCoin carries zero fee schedule state and displays zero fee UI clutter.
- **Optional credential policies ([Pillar 8](/docs/did-credentials/)):** Permissionless by default. Anyone can hold, transfer, or trade a default NAVCoin on the DEX with zero `trust_set` steps.

## 1. Universal NAV Integrity & Primary-Market Accounting

### Single Core Accounting Model

Primary subscription moves counted settlement value (`pfUSDC`) into the NAVCoin reserve and creates new NAVCoin units; primary redemption retires NAVCoin units and releases the corresponding reserve value:

```text
counted reserves in  <->  valid NAVCoin supply out
```

### Universal `floor(V * U / S)` Consensus Rule (All NAVCoins)

Consensus enforces **`nav_per_unit == floor(V * U / S)`** across **every** NAVCoin and **every** proof profile — including zero-fee NAVCoins without a fee schedule — where:

- `V` = verified net assets (valuation atoms, e.g., `usd_1e6`)
- `S` = valid global circulating supply across all representations and in-flight claims (NAVCoin atoms)
- `U` = `10^precision` (display unit scale)

Finalization also enforces `packet.circulating_supply == live_ledger_supply` (rejecting stale reserve packets if supply changed between snapshot and finalization). This closes undisclosed hidden fees via NAV understatement.

### Primary Issue & Redeem Spreads

For `x` units issued or redeemed:

```text
# Primary Issue (issue_multiplier = (10_000 + issue_spread_bps) / 10_000)
base_value = ceil(x * nav_per_unit / U)
user_due   = ceil(base_value * (10_000 + issue_spread_bps) / 10_000)
issue_fee  = user_due - base_value

# Primary Redeem (redeem_multiplier = (10_000 - redeem_spread_bps) / 10_000)
gross_value = floor(x * nav_per_unit / U)
user_out    = floor(gross_value * (10_000 - redeem_spread_bps) / 10_000)
redeem_fee  = gross_value - user_out
```

All arithmetic uses checked integer math — never floating point.

## 2. Optional Deterministic Fee Schedules (`NavFeeScheduleV1`)

Attaching `NavFeeScheduleV1` to a `NavTrackedAsset` is **100% optional**. When enabled, creators configure any subset of four protocol-capped parameters:

| Parameter | Field | Hard Protocol Cap | Notes |
| --- | --- | --- | --- |
| **Annual rate** | `annual_rate_bps` | `500 bps` (`5%/year`) | Time-based rate computed strictly from protocol constant `blocks_per_year` |
| **High-water-mark rate** | `hwm_rate_bps` | `5,000 bps` (`50%`) | Per finalized epoch on per-unit net gains above all-time high-water mark `H` |
| **Issue / redeem spread** | `issue_spread_bps`, `redeem_spread_bps` | `500 bps` (`5%`) | Primary-market subscription and redemption spreads |
| **FX fix fee cap** | `fix_fee_cap_bps` | `100 bps` (`1%`) | Ceiling for scheduled FX fix settlements |
| **Increase notice** | `increase_notice_blocks` | Minimum **7 days** in blocks | Creators may set longer notice or permanently freeze ceilings with `rates_locked = true` |
| **Fee recipient** | `recipient` | Distinct from `issuer` account | Receives claimed fee units via `nav_fee_claim` |

There is **no hurdle rate** and **no Post Fiat protocol or validator fee cut** in v1.

### Anti-Bypass Protections

1. **7-day minimum notice on any increase:** Any increase to `annual_rate_bps`, `hwm_rate_bps`, `issue_spread_bps`, `redeem_spread_bps`, `fix_fee_cap_bps`, or `accrual_cap_blocks`, or any decrease to `increase_notice_blocks`, enters a pending state and cannot activate until `effective_height >= current_height + max(7_days_blocks, increase_notice_blocks)`. Legacy spread updates on unscheduled NAVCoins obey the exact same 7-day increase notice. Pure fee decreases apply at the next finalization.
2. **Exit capacity protection during pending hikes:** Routes cannot reduce cash-in exit capacity while a fee increase is pending, giving holders a guaranteed exit window before higher rates take effect.
3. **Permanent ceiling lock with safe key rotation (`rates_locked`):** Setting `rates_locked = true` permanently prevents any future rate ceiling increase while still permitting a visible `recipient` account rotation (with 7-day notice if the recipient key is lost) so a lost recipient key never bricks fee claims.
4. **Non-issuer attestor requirement for attested reserves:** Whenever `attested_value > 0` on a fee-enabled NAVCoin, consensus requires an independent registered `NavAttestor` with **`attestor_account != issuer_account`**. Issuer-only attested reserves cannot charge high-water-mark fees, and the explorer displays the proven vs. attested reserve split explicitly.

## 3. Exact Integer Accrual Formulas (Inside `nav_epoch_finalize`)

When a NAVCoin has an active `NavFeeScheduleV1`, fees accrue atomically inside `nav_epoch_finalize` in NAVCoin units using **widened `u256` intermediates**, rounding down at every step so dust always stays with holders.

### Initialization (Zero Retroactive Accrual)

- When a schedule first attaches at height `h_attach`, `h_last` initializes to **`h_attach`** (never `0`).
- High-water mark `H` initializes to **`N_current`** on the first finalization with `S > 0` so pre-existing gains prior to attaching a schedule are never assessed.
- If a pending schedule activates across an epoch interval, that interval accrues at the **lower** of the old and new rates.

### Four-Step Accrual Algorithm

Let `V` = verified net assets (valuation atoms), `S` = circulating supply (NAVCoin atoms), `U = 10^precision`, `H` = prior high-water mark per unit, `m = annual_rate_bps`, `p = hwm_rate_bps`, `Δh = min(h - h_last, accrual_cap_blocks)` (bounded by `max_epoch_gap_blocks` so annual accrual halts if the deadman stops dealing), and `Y = blocks_per_year` (recorded explicitly inside `NavFeeAccrualV1`).

```text
Step 1 (Time-based rate first):
  F_m = floor(V * m * Δh / (10_000 * Y))
  N_m = floor((V - F_m) * U / S)

Step 2 (High-water-mark rate on gain above H):
  g   = max(0, N_m - H)
  F_p = floor(g * S * p / (10_000 * U))

Step 3 (Atomic unit mint into unclaimed bucket):
  F   = F_m + F_p
  ΔS  = floor(F * S / (V - F))

Step 4 (Post-fee state update):
  S'      = S + ΔS
  N_after = floor(V * U / S')
  H'      = max(H, N_after)
```

### Edge Cases, Unclaimed Bucket & Ethereum Sync

- `S == 0`, `V == 0`, or `F >= V` never fail epoch finalization; consensus records a zero or clamped `NavFeeAccrualV1` with an explicit reason code.
- If `S + ΔS` would exceed `max_supply`, `ΔS` clips to `max_supply - S` and the clipped remainder is forgone (zero hidden carry-forward debt).
- **Zero Pillar 8 deadlock:** `ΔS` mints directly into the protocol's on-chain **unclaimed fee bucket** (counted inside `circulating_supply`, bypassing `asset_gate`). The fee recipient later calls **`nav_fee_claim`**, which runs through `asset_gate` normally.
- **Ethereum / Uniswap NAV lockstep:** `nav_epoch_finalize` emits the post-fee `N_after` in the signed epoch packet relayed to Ethereum's `NAVGuardHook.sol` and `PFTLUniswapPrimaryMarketV2.sol`. Routes reject dealing on stale pre-fee epochs until re-pinned.

### Worked Example (Exact Integer Numbers)

Suppose `precision = 6` (`U = 1,000,000`), `V = 1,100,000.000000` (`1,100,000,000,000` micro-USD), `S = 1,000,000.000000` (`1,000,000,000,000` atoms), `H = 1.000000` (`1,000,000`), `m = 100 bps` (`1%/yr`), `p = 1,000 bps` (`10%`), and `Δh / Y = 0.01`:

1. `F_m = floor(1,100,000 * 100 * 0.01 / 10,000) = 110.000000`
2. `N_m = floor((1,100,000 - 110) * U / 1,000,000) = 1.099890`
3. `g = 1.099890 - 1.000000 = 0.099890`
4. `F_p = floor(0.099890 * 1,000,000 * 1,000 / 10,000) = 9,989.000000`
5. `F = 110 + 9,989 = 10,099.000000`
6. `ΔS = floor(10,099 * 1,000,000 / (1,100,000 - 10,099)) = 9,265.979203` NAVCoin units
7. `S' = 1,009,265.979203`
8. `N_after = H' = floor(1,100,000 * U / 1,009,265.979203) = 1.089901`

Result: Existing holders retain `1,000,000 * 1.089901 = 1,089,901.000000` in backing, and the `9,265.979203` fee units are worth `10,098.999999` at `N_after` (`<= F`, dust stays with holders).

## 4. Creating a NAVCoin With the Python SDK

The `postfiat_rpc.navcoin` SDK (and Rust `crates/rpc_sdk`) packages creation, optional schedule configuration, and independent exact-atom verification validated against 100+ shared Rust/Python test vectors.

### Zero-Fee Permissionless NAVCoin (Default)

```python
from postfiat_rpc.navcoin import create_navcoin

receipt = create_navcoin(
    rpc_url="https://rpc.postfiat.org",
    issuer_wallet=wallet,
    asset_code="EXMP",
    precision=6,
    valuation_unit="usd_1e6",
    proof_profile_id=profile_id,
    fee_schedule=None,       # Optional: omit for zero fee schedule state
    credential_policy=None,  # Optional: omit for permissionless-by-default trading
)
print("Asset ID:", receipt["asset_id"])
```

### Fee-Enabled NAVCoin & Independent Atom Recomputation

```python
from postfiat_rpc.navcoin import NavFeeScheduleConfig, create_navcoin, recompute_fees

schedule = NavFeeScheduleConfig(
    annual_rate_bps=100,        # 1.00%/yr (cap: 500)
    hwm_rate_bps=1000,          # 10.00% HWM gain rate (cap: 5000)
    issue_spread_bps=50,        # 0.50% primary issue spread (cap: 500)
    redeem_spread_bps=50,       # 0.50% primary redeem spread (cap: 500)
    fix_fee_cap_bps=25,         # 0.25% FX fix cap (cap: 100)
    recipient="pftl1recipient...",
    increase_notice_blocks=604_800,  # >= 7 days
    accrual_cap_blocks=86_400,
    rates_locked=False,
)

receipt = create_navcoin(
    rpc_url="https://rpc.postfiat.org",
    issuer_wallet=wallet,
    asset_code="EXMPF",
    precision=6,
    valuation_unit="usd_1e6",
    proof_profile_id=profile_id,
    fee_schedule=schedule,
)

# Independently recompute any finalized epoch to the single atom
check = recompute_fees(
    rpc_url="https://rpc.postfiat.org",
    asset_id=receipt["asset_id"],
    epoch=1,
)
assert check["matches_onchain_accrual"] is True
```

### Fee Schedule Operations & Explorer RPCs

- **Consensus operations:** `nav_fee_schedule_attach`, `nav_fee_schedule_set`, `nav_fee_schedule_cancel`, `nav_fee_claim`.
- **Read RPCs:** `nav_fee_schedule(asset_id)` and `nav_fee_history(asset_id)`.
- **Block explorer:** Renders every schedule attach/update/cancel (old -> new values and effective height), per-tx spreads, fix fee rates, and per-epoch `NavFeeAccrualV1` math (including `blocks_per_year` used). For NAVCoins with no schedule configured, no fee section is displayed.
