---
title: "pfUSDC × NAVCoin: A Proven End-to-End OTC Swap MVP"
date: 2026-06-19T00:00:00Z
draft: true
summary: "We built and proved the full NAVCoin OTC swap round trip on live Arbitrum One + the Post Fiat WAN devnet: real USDC bridges into pfUSDC, pfUSDC subscribes into a NAVCoin with proven reserves (TVL rises by exactly the deposit), the NAVCoin exits (TVL falls by exactly the withdrawal), and pfUSDC bridges back out to real USDC — plus cross-NAVCoin swaps. The end-to-end battery surfaced and fixed four real reserve/accounting gaps along the way."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - pfUSDC
  - OTC
  - Arbitrum
  - PFTL
  - Bridge
  - Proof of Reserves
  - Post Fiat
---

*Part of the NAVCoin series. The [architecture](/blog/navcoin-ethereum/) defined one verified portfolio, one canonical NAV, many access venues. [pfUSDC](/blog/pfusdc/) defined the countable cash leg. [Private NAV OTC swaps](/blog/private-nav-otc-swaps/) defined the shielded settlement target. This post reports the proven end-to-end MVP.*

## What an OTC swap actually requires

A NAVCoin OTC swap is not one transaction. It is a round trip with a hard precondition on each side:

- **The cash leg must be countable.** You cannot release a NAVCoin against an undifferentiated wrapped-dollar ticker. The cash has to enter as a source-labeled, finalized, haircut-adjusted receipt before it backs anything. On Post Fiat that primitive is **pfUSDC** — a PFTL-native cash receipt minted only from proven source-chain deposits.
- **The swap must move the reserve.** Subscribing cash into a NAVCoin has to raise its verified net assets by exactly the deposit; exiting has to lower them by exactly the withdrawal. A secondary trade of existing units does neither. The proof is the **before/after `verified_net_assets` delta**, not a balanced order book.

We built both and proved the full round trip with real (small-dollar) USDC on **Arbitrum One** and the **Post Fiat WAN devnet** (six validators, cross-continent).

## The architecture, end to end

```text
 Arbitrum One                          Post Fiat L1 (canonical NAV/supply ledger)
 ───────────                           ──────────────────────────────────────────
 USDC ──deposit──▶ ERC20BridgeVault    pfUSDC ──primary subscribe──▶ a651 (NAVCoin)
        ◀──claim──   (holds USDC)        ▲                              │
            ▲                            │                              │ exit
            │                       burn-to-redeem                      ▼
            │                            │                          pfUSDC
            └── withdrawal packet ◀──────┘                              │
                 (proof/finality)      └── cross-NAVCoin swap: a651 ◀▶ a652
```

Post Fiat is the **canonical NAV/supply ledger**: it verifies the reserve packet, computes NAV, gates mint/burn at NAV, and enforces the invariant `verified_net_assets ≥ valid_global_supply × nav_per_unit_floor` in consensus. Arbitrum is an **access + custody venue** — the `ERC20BridgeVault` holds real USDC; pfUSDC exists on PFTL only to the extent the vault holds finalized, counted USDC.

## The six-flow battery — all proven with real value

Each flow ran live with a concrete assertion. The decisive one is the **TVL symmetry** across flows 4 and 5.

| # | Flow | Live result |
|---|------|-------------|
| 1 | Bridge IN — USDC → pfUSDC | Arbitrum deposit relayed (propose/attest/finalize/claim); vault USDC == minted pfUSDC |
| 2 | Bridge OUT — pfUSDC → USDC | wallet +2,000,000 atoms; vault −2,000,000 |
| 3 | Subscribe — pfUSDC → a651 | primary mint; allocation retired |
| 4 | **TVL up** | a651 `verified_net_assets` 2,032,945,386,170 → **2,033,453,622,570** (Δ **+508,236,400** usd_1e8 ≈ +5.08 USDC) |
| 5 | Exit — a651 → pfUSDC | `verified_net_assets` → 2,032,945,386,170 (Δ **−508,236,400**); buyer received 5,083,635 pfUSDC |
| 6 | Final bridge-out | wallet 3,000,099 → **8,083,734**; vault 6,000,000 → **916,365** (Δ exactly 5,083,635); full EVM proof→claim chain |

The **+508,236,400 / −508,236,400 symmetry** is the proof that the reserve accounting is structurally correct: a primary mint raises TVL by exactly the cash deposited; a burn lowers it by exactly the cash returned. No inflation on the way in, no drainage on the way out.

## Cross-NAVCoin swap

A second NAVCoin (a652) was bootstrapped on the same chain and traded against a651 through the PFTL offer book: maker offered 100 a652, taker crossed with 100 a651. Final state — buyer 900 a651 / 100 a652; maker 1100 a651 / 900 a652. NAVCoin-to-NAVCoin transfer works, not just NAVCoin-to-cash.

## The battery did its job: four real gaps, found and fixed

A hand-wavy "it works" demo would have hidden these. Proving each flow against live state surfaced four genuine reserve/accounting bugs, each fixed with a regression test and verified clean (Foundry 52, cargo suites green):

1. **Units scaling** — the primary mint priced issuance 100× too high (`usd_1e8` vs USDC 6-decimal atoms). Fixed with deterministic integer scale conversion.
2. **Reserve-in on mint** — the retired pfUSDC allocation was not being counted in `verified_net_assets`, so a mint showed zero TVL change. Fixed (`28071d28`); flow 4 now passes.
3. **Reserve-out on burn** — burning a NAVCoin did not release its pfUSDC allocation. Fixed with vault-bridge-aware exit settlement (legacy-safe `signing_bytes`).
4. **Burn-settle bookkeeping** — settlement reduced the exit queue without reducing counted vault value, overstating free bridge capacity. Fixed (`8f24d7b2`); capacity now equals the real vault balance exactly.

A subsequent **exhaustive contract review** found four more critical/high issues — all fixed (`59af43d9`): a zero-cost withdrawal-freeze griefing vector (challenges now scoped to authority/owner), cross-vault replay (withdrawal packets now bind vault + token + source chain), and unrecoverable expired withdrawals.

## Status and scope (the honest section)

- **What is proven:** the end-to-end round trip and cross-NAVCoin swap on a live six-validator PFTL devnet with real Arbitrum USDC, with the NAV invariant holding and TVL moving symmetrically. This is a real structural MVP, not a mockup.
- **What this is not:** a mainnet deployment, an audited system, or a product launch. Values are small-dollar proof amounts. The contracts have an internal review and regression coverage, not a third-party audit.
- **Controlled-launch disclosure:** the `NAVGuardHook` (the NAVCoin-referencing Uniswap venue hook) is currently a controlled-launch adapter, **not yet a production Uniswap v4 hook**; market-operations automatic caps do not rely on it yet. It is flagged as follow-up work, not a shipped feature.
- **Source of truth:** the proven-results record is [`postfiatl1v2/docs/status/otc-swaps-mvp-proven-2026-06-19.md`](https://github.com/postfiatorg/postfiatl1v2); the spec is `docs/specs/otc-swaps-mvp-guide.md`; the contract review is `docs/status/arbitrum-contracts-code-review-2026-06-19.md`.

## Why it matters

The hard part of a floating-NAV token is not the swap — it is keeping the reserve honest while value moves in and out. This MVP proves that, on Post Fiat, **cash enters only after source proof, NAVCoin is released only against counted cash, and the verified reserve moves by exactly the deposit on the way in and the withdrawal on the way out** — all enforced in consensus, all observable, all reconciling to the real USDC sitting in the Arbitrum vault.

That is the primitive private NAV OTC swaps ([the shielded settlement target](/blog/private-nav-otc-swaps/)) are built on. The transparent round trip works end to end; the shielded version is the layer on top.
