---
title: "Post-Quantum Messaging, Sub-Second FastPay & x402 Agent Payments"
date: 2026-11-27T00:00:00Z
draft: true
summary: "Why Post Fiat standardized machine-native messaging on canonical protobufs, X-Wing post-quantum encryption, Sui-style FastPay fees, and x402 agent payments."
author: "Post Fiat"
categories:
  - Engineering
tags:
  - Post Fiat
  - FastPay
  - Post-Quantum
  - X-Wing
  - x402
  - Protobuf
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

If a blockchain is meant for humans and AI agents working together, memos and encrypted messages cannot be an afterthought. On our old XRPL-fork chain, `pf.ptr` v4 memos were hand-encoded across three languages, used classical X25519 encryption, and waited on full consensus blocks.

With Pillar 2 on `postfiatl1v2`, messaging, Task Node payouts, and machine-to-machine API payments share one clean stack.

## One Canonical Wire Format, Post-Quantum by Default

Every Post Fiat message now starts from a single `.proto` source of truth in `postfiatl1v2/proto/pf/`, generating JavaScript, Python, and Rust (`prost`) libraries tested against the same byte vectors.

- **Binary `pf.ptr` v5 memos:** Each transaction memo stays strictly within `postfiatl1v2`'s 256-byte lowercase-hex limit by packing a 36-byte binary IPFS CIDv1 `raw` hash (or inline bytes for small records like an x402 request hash).
- **Zero re-serialization verification:** `Envelope` (`pf.msg.v1`) keeps `header`, `readers[]`, and `body` as opaque raw byte fields. Verifiers check the CID and the sender's **ML-DSA-65** signature over those exact bytes before decoding anything. Cross-language protobuf drift cannot break signatures.
- **X-Wing hybrid encryption:** Private messages encrypt with `XChaCha20-Poly1305` and wrap the content key per recipient using **X-Wing (`X25519 + ML-KEM-768`)**. That adds ~32 bytes per recipient and stays safe even if a flaw were ever found in lattice math. No plaintext SHA-256 hash is ever published.
- **Zero-balance onboarding:** New users start with `0 PFT`, so their wallet derives its X-Wing key from the master seed, signs the binding with its ML-DSA-65 account key, and registers it with Task Node at onboarding. Their very first Task Node payout encrypts cleanly.

## FastPay Speed With Sui-Style Fee Discipline

Task Node reward payouts now default to **FastPay** (~200ms finality, targeting `< 500ms` p50 end-to-end) with encrypted `pf.reward.v1` memos and asynchronous IPFS pinning backed by a durable retry outbox.

Zero-fee FastPay invites state-bloat spam, so `postfiatl1v2` enforces a simple Sui-inspired fee floor on every `OwnedTransferOrderV3`:

```text
min_fee_atoms = 25 + ceil(tx_bytes / 512) + max(0, outputs - inputs) * 1_000 + inputs
```

Normal transfers cost a tiny fraction of a cent (`25 atoms` = `0.000025 PFT` base). Merging up to 2,048 small payout objects stays cheap. Creating net-new owned objects costs `0.001 PFT` per object so object-splitting spam gets expensive fast.

FastPay transfers and unwraps now index directly into `account_tx` and `tx` by immutable **`order_hash`** (never malleable validator certificate digests). On the block explorer, Task Node payouts display a clean **`"Task reward"`** badge — and **only** when the verified envelope signer matches the pinned official Task Node payout key. Decryption always happens locally in your wallet or Mac app, never on the explorer.

## Agent Payments Over x402 (+ MCP Helper)

AI agents need to pay for API calls and data without credit cards or human checkout forms. Post Fiat ships an **x402 v2** binding and facilitator for both:

- **Native `PFT` on FastPay** (`~200ms` quorum finality, deduplicated across replicas by immutable `order_hash`)
- **`pfUSDC` on the consensus lane** (for dollar-denominated settlement)

An API returns `402 Payment Required` with price, payee, request hash, and nonce. The agent signs a FastPay transfer embedding the request hash, retries with `PAYMENT-SIGNATURE`, and gets `200 OK` plus a settlement receipt in a fraction of a second. Our thin MCP wrapper handles that loop automatically inside agent tool calls under local spending caps.

## Live UAT Evidence

- **Live FastPay Task Node reward (`order_hash`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer `"Task reward"` card & local decryption check:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`
- **End-to-end x402 `402 -> pay -> 200` settlement digest:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`

Read the full byte layouts, fee formulas, and x402 specs in the [Post-Quantum Message Protocol, FastPay & x402 Guide](/docs/message-protocol/).
