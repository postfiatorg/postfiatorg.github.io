---
title: "Local Post-Quantum Private Payments (PFSH03) in the Native Post Fiat Mac App"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How TaskNode.app proves curve-free PFSH03 Binius shielded payments strictly on Apple Silicon, submits directly to public validator RPCs, and stays honest about what privacy does and does not hide."
author: "Post Fiat"
categories:
  - Privacy
tags:
  - Post Fiat
  - PFSH03
  - Binius
  - Post-Quantum
  - macOS
  - Privacy
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

If a server generates your zero-knowledge proof, sees your note openings, or touches your viewing keys, you do not have private payments — you have a database with extra steps.

On **November 26, 2026**, all six `postfiat-wan-devnet-2` validators activated **PFSH03** (`pq-r3`) in Block 1910, and our signed native macOS app (`TaskNode.app`) executed a complete **Shield -> Private Send -> Scan/Receive -> Unshield** cycle in **Blocks 1912–1914** on an M5 MacBook Pro. Proving took ~10 seconds per transaction at ~380 MiB peak RAM, with 6/6 validator convergence and zero secrets leaving the Mac.

## Native SwiftUI + Rust, Zero WebView, Zero Server Proving

`TaskNode.app` (`tasknode-apple`) is a native macOS app written in SwiftUI and Rust (`pf_app_core`) with no WebView and no analytics or crash SDKs.

- **Sandboxed local prover:** Every spend key, viewing key, note opening, trial-decryption scan, and Binius proof runs strictly inside `TaskNodeProver`, a Seatbelt-sandboxed helper pinned by code hash (CDHash).
- **Curve-free post-quantum stack (`PFSH03`):** Built on binary-field Binius proofs over FIPS-202 `SHAKE256`, `3x SHA-512`, `AES-256-GCM`, `ML-KEM-1024`, and `ML-DSA-65` — retiring legacy elliptic-curve Orchard and custodial `pftl_swapd`.
- **Direct to public validator RPCs:** Once outside validators stand up public RPC endpoints in Pillar 3, `TaskNode.app` submits finished public proofs directly to **2+ independent non-Foundation public validator admission endpoints** and verifies synced `PFSH03` pages against finalized validator quorum signatures. The `/api/l1/pq/*` gateway relay stays strictly an opt-in IP-privacy toggle, plainly labeled as Foundation infrastructure.
- **One-click *Make private* on FastPay payouts:** Clicking *Make private* on a Task Node reward runs a crash-resumable `owned_unwrap -> PFSH03 Shield` state machine locally on your Mac.
- **One recovery phrase across clients:** `TaskNode.app` and `pftl_pq_walletd` share one domain-separated BIP-39 HKDF derivation and birthday-checkpoint restore format.

## Measured Performance & Formal Scope

On `postfiat-wan-devnet-2` (M5 MacBook Pro, Nov 26, 2026):

| Action | Devnet-2 Block | End-to-End Prove + Launch | Peak RSS | Validator Consensus |
| --- | --- | --- | --- | --- |
| Shield | `1912` | `10.07 s` | `382 MiB` | `6 / 6` |
| Private Send | `1913` | `10.17 s` | `376 MiB` | `6 / 6` |
| Unshield | `1914` | `9.85 s` | `382 MiB` | `6 / 6` |

- **8 GB Apple Silicon MacBook Air benchmarks:** `[INSERT 8GB MBA BENCHMARK SUMMARY AFTER UAT]`
- **Lean 4 formal verification:** Nine Lean 4 model modules (`2,847` LOC, 0 `sorry`s, 0 custom axioms) verify core mathematical invariants (66-bit conservation, spend-auth reduction structure, 3-block `SHA-512` random-oracle simulation, and adaptive confidentiality for fresh per-note addresses). They do **not** mechanically link to the compiled Rust/Go binaries — which is why we pair them with cross-model adversarial review and a governance-capped **"Shielded Beta"** TVL cap at launch.

## What Privacy Hides — and What It Doesn't

We show the exact privacy boundary inside the app rather than hand-waving it:

- **Task Node server** sees normal app features (chat, tasks, context) and **never** sees keys, notes, witnesses, shielded proofs, or `pfpq1` lookups.
- **Chain observers** still see public shield/unshield accounts and exact amounts, fees, tree epochs, nullifiers, and commitments.
- **Receiving validator RPCs** see the public proof and submitter IP/timing.
- **Beta safety rails:** Shielded Beta launches for **`PFT` and `pfUSDC`** with a per-asset TVL cap (blocking excess Shields while **always keeping Unshields open**), a standard exit-safe pause (halts Shields/Sends, leaves Exits open), and an elevated-quorum emergency exit freeze hard-capped at `604,800` blocks (~7 days) with automatic expiry.

## Clean-Mac UAT Evidence

- **Notarized `TaskNode.dmg` release & SHA-256:** `[INSERT NOTARIZED RELEASE TAG & SHA-256 AFTER UAT]`
- **Live direct-RPC Shield / Private Send / Unshield tx hashes (`PFT` & `pfUSDC`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Packet-capture leak-boundary report:** `[INSERT PACKET-CAPTURE REPORT LINK AFTER UAT]`
- **Native Mac app Private tab screenshot:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Read the install steps, honest privacy model, and operator pause/exit runbook in the [Local Mac App (`PFSH03`) Guide](/docs/local-mac-app/).
