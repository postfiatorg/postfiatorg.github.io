---
title: "Local Mac App (PFSH03) Install, Honest Privacy Model & Pause/Exit Guide"
url: "/docs/local-mac-app/"
type: "page"
layout: "single"
kicker: "Pillar 5 · Local Task Node"
date: 2026-11-27
summary: "Install guide, unified BIP-39 recovery, direct public validator RPC submission, honest privacy model, Apple Silicon benchmarks, Lean 4 coverage scope, and governance pause/exit runbook for TaskNode.app and PFSH03."
---

**`TaskNode.app` (`tasknode-apple`)** is a native SwiftUI + Rust (`pf_app_core`) macOS application with zero WebView attack surface and zero analytics or crash SDKs. It provides native Task Node workflows (Chat, Tasks, Requests, Context, Rewards, Wallet, Bridges, Markets, Hive, Governance, NFTs, Identity, and Finance Hub web handoff) alongside **local post-quantum shielded payments (`PFSH03`)** proved strictly on your Mac.

On **November 26, 2026**, all six `postfiat-wan-devnet-2` validators activated `pq-r3` in **Block 1910** and executed a live Shield -> Private Send -> Scan/Receive -> Unshield cycle from a signed `TaskNode-PQ.app` on an M5 MacBook Pro across **Blocks 1912–1914** with 6/6 validator consensus.

## 1. Architecture & Hard Custody Boundary

```text
TaskNode.app (SwiftUI + Rust pf_app_core)
 ├── macOS Keychain + Encrypted Local Vault (BIP-39 phrase, ML-DSA-65, X-Wing, PFSH03 notes)
 ├── Seatbelt-Sandboxed TaskNodeProver (CDHash-pinned, curve-free Binius prover)
 ├── Normal app APIs (chat, tasks, context)  --->  Task Node Server
 └── Public PFSH03 proofs & queries (default) --->  2+ Independent Public Validator RPCs
                                                    (opt-in Foundation relay toggle only)
```

- **Zero secrets leave your Mac:** Spend keys, viewing keys, note openings, trial-decryption scans, and Binius zero-knowledge proofs execute strictly inside the CDHash-pinned, Seatbelt-sandboxed `TaskNodeProver` helper.
- **Direct validator submission by default:** Once [Pillar 3 outside public validator RPCs](/run-a-validator/) are live, `TaskNode.app` submits finished public proofs directly to **2+ independent non-Foundation public validator admission endpoints** discovered from the signed validator registry feed. During early devnet bootstrap while only Foundation validators exist, the UI explicitly discloses that Foundation infrastructure operates the validators.
- **Opt-in IP-privacy relay:** The `/api/l1/pq/*` gateway relay is strictly opt-in. When enabled, the UI states plainly that it runs on Foundation infrastructure and sees IP/timing metadata (never keys, notes, or private witnesses).
- **Cryptographic light-client verification:** `TaskNode.app` ships with the pinned genesis/committee root and verifies every synced `PFSH03` output page and Merkle root against finalized ML-DSA-65 validator quorum signatures across 2+ endpoints — never trusting unsigned JSON.
- **No Task Node lookup of `pfpq1` addresses:** Shielded receive addresses (`pfpq1...`) are entered via paste, QR scan, or direct on-chain Pillar 6 RPC — never queried through the Task Node server.

## 2. Installing `TaskNode.app` & Unified BIP-39 Recovery

### Requirements

- **Platform:** Apple Silicon macOS (`arm64`, macOS 14+ recommended). Linux and Windows support follows via the shared `pftl_pq_walletd` local daemon + browser UI; iOS follows later.
- **Distribution:** Developer ID signed and Apple notarized `.dmg` / `.app` with Hardened Runtime and pinned `TaskNodeProver` CDHash (no Gatekeeper bypass required).

### Install & First Run

1. Download the notarized `TaskNode.dmg` from the official Post Fiat release channel and verify its SHA-256 checksum against the signed release manifest.
2. Drag `TaskNode.app` into `/Applications` and launch it.
3. Choose **Create new recovery phrase** or **Restore from BIP-39 recovery phrase**.
4. Confirm Touch ID / macOS Keychain enrollment for vault unlock and transaction review.

### Unified BIP-39 Seed Derivation & Birthday Checkpoints

Production `TaskNode.app` and `pftl_pq_walletd` share one domain-separated HKDF hierarchy from the master BIP-39 seed (aligned with [Pillar 6 on-chain identity](/docs/onchain-identity/)) with shared CI test vectors so any client restores the exact same transparent and `PFSH03` shielded notes.

- Vault backups store a **birthday checkpoint height** so clean-Mac restores scan only from account creation forward and mark spent nullifiers accurately.
- **Fresh per-note addresses:** The wallet defaults to fresh indexed `pfpq1...` receive addresses (`wallet.address(index)`) and rotates change keys automatically so incoming payments do not link when spent.
- **Pinning brand-new public accounts:** A brand-new public account has only a 160-bit address hash until its first signed transaction pins its full 1,952-byte ML-DSA-65 public key on chain. Perform one small signed self-transfer (enforced automatically by the wallet) before large shields.

## 3. Using Shielded Payments (`PFT` & `pfUSDC`)

### Supported Assets at Launch

- **Supported:** Native **`PFT`** and **`pfUSDC`**.
- **Not supported in v1:** NAVCoins and credential-gated assets stay outside the shielded pool until Pillar 7/8 disclosure rules are defined. Legacy Orchard and custodial `pftl_swapd` are retired (any historical Orchard notes migrate via a plain two-step public exit -> `PFSH03` shield).

### One-Click *Make Private* From FastPay Payouts

Task Node task rewards arrive as FastPay owned objects, while `PFSH03` Shields draw from your consensus-lane account balance. Clicking **Make private** on any FastPay payout runs a single crash-resumable state machine:

```text
owned_unwrap (FastPay -> consensus balance)  -->  PFSH03 Shield (consensus -> private note)
```

Exact signed bytes and intent state (`submitted`, `accepted`, `rejected`, `conflicted`, `expired`) are persisted locally before broadcast so retries resend identical bytes and concurrent spends across devices never double-prove.

### Fee Mechanics & Pool Conservation

- **Shield (Deposit):** Pays a public PFT transaction fee.
- **Private Send & Unshield (Exit):** Pays its fee inside the proof in the spent note's own asset (no public fee-payer account is exposed). `PFT` inner fees burn; `pfUSDC` inner fees route to the governed `collected_private_fees` collector.
- **Per-asset conservation invariant:** Consensus enforces `total_shielded_in >= total_unshielded_out + fees` independently for `PFT` and `pfUSDC`, preventing cross-asset value leakage.

## 4. Honest Privacy Model

Local proving eliminates the Task Node server as a private-payment observer. It does **not** hide everything at the network or ledger layer:

| Observer | What They CAN See | What They CANNOT See |
| --- | --- | --- |
| **Chain / Block Explorer** | Public shield/unshield accounts and exact amounts, asset ID, fee, tree epoch/anchor, inclusion height, nullifiers, commitments, encrypted envelopes | Note values on private sends, sender/receiver link on private sends, which prior commitment a nullifier spends |
| **Receiving Validator RPC** | Public proof bytes, submitter IP address, submission timing | Spend keys, viewing keys, note openings, private witnesses |
| **Task Node Server** | Normal non-private app traffic (chat, tasks, context) | Keys, notes, witnesses, shielded proofs, `pfpq1` lookups |

### In-App Safety Disclosures

- The pool is labeled **"Shielded (Beta)"** until pool activity clears the anonymity floor (`16+` candidate notes / `128+` actions).
- The UI warns against shielding and immediately unshielding identical amounts (which leaks timing and value correlation).
- Compromising a recipient's long-term ML-KEM decapsulation key exposes past incoming envelopes encrypted to it (same static-key tradeoff as Orchard).

## 5. Hardware Benchmarks & Admission DoS Limits

### Measured Devnet-2 Performance (M5 MacBook Pro, Nov 26, 2026)

| Operation | End-to-End Prove + Helper Time | Peak RSS | Validator Consensus |
| --- | --- | --- | --- |
| Shield (`Block 1912`) | `10.07 s` | `382 MiB` | `6 / 6` |
| Private Send (`Block 1913`) | `10.17 s` | `376 MiB` | `6 / 6` |
| Unshield (`Block 1914`) | `9.85 s` | `382 MiB` | `6 / 6` |

- **8 GB Apple Silicon MacBook Air benchmarks** (cold/warm prove time, peak RSS, battery delta, thermal state): `[INSERT 8GB MBA BENCHMARK TABLE AFTER UAT]`
- **Fail-fast validator admission:** Before running Binius verification, validators check `< 1ms` syntax, external ML-DSA-65 spend authorization, 20-bit Round-34 PoW, per-IP rate limits, 60-second mempool expiry, and deterministic fee priority (max 1 queued proof per submitter per block, max **4 proofs per block**).

## 6. Lean 4 Formal-Verification Coverage Scope

Post Fiat maintains **9 Lean 4 model modules (`2,847` LOC, 0 `sorry`s, 0 custom axioms)** in `postfiatl1v2/formal/lean/`.

- **What the Lean 4 models check:** Algebraic soundness plumbing, 66-bit unsigned value conservation, spend-authorization reduction structure, our 3-block `SHA-512` random-oracle simulation, and adaptive multi-transaction confidentiality under fresh per-note addresses from explicit mathematical hypotheses.
- **What the Lean 4 models do NOT prove:** They do **not** mechanically link the Lean specification to the compiled Rust/Go binaries, and they do not replace multi-model adversarial review of circuit wiring (`pk_hash0/1`), prover/verifier code, admission backpressure, or macOS sandbox boundaries.

## 7. Operator Pause, Beta TVL Cap & Exit-Freeze Runbook

PFSH03 launches under a governance-controlled **"Shielded Beta" TVL cap per asset** (blocking new Shields above cap while **always keeping Unshields open**). Raising or lifting the cap requires a ratified governance amendment after multi-model adversarial review closes.

### Tier 1 — Standard Exit-Safe Pause

- **Mechanism:** Governance amendment `pq_payment_rehearsal_v1 = 0` ratified by standard BFT supermajority (`floor(2n/3) + 1`, e.g. 5/6).
- **Effect:** Immediately halts new **Shields** and **Private Sends** while keeping **Exits (`Mode::Exit`) open** so users can withdraw funds cleanly.

### Tier 2 — Emergency Time-Bounded Exit Freeze

- **Mechanism:** Separate governance amendment `pq_exit_freeze_until_v1` requiring an **elevated quorum** (`min(n, floor(5n/6) + 1)` — 6/6 unanimous in a 6-validator set).
- **Auto-expiry hard cap:** Capped at **`MAX_PQ_EXIT_FREEZE_BLOCKS = 604,800`** blocks past inclusion height (~7 days at 1-second blocks). Exits reopen automatically at `freeze_until + 1` with no governance action required.
- **Honest trust note:** Because an elevated quorum can ratify consecutive freeze amendments, coordinated supermajority validator censorship remains an explicit governance trust assumption.
