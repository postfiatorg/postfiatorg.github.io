---
title: "Post Fiat Technical Guides"
url: "/docs/guides/"
type: "page"
layout: "single"
kicker: "Documentation"
date: 2026-11-27
summary: "Canonical technical guides for Post Fiat L1v2 governance packets, post-quantum messaging, NFTs, the local Mac app, on-chain identity, NAVCoins, credentials, the Information Hive Mind, and Hyperliquid NAVCoin / FX Fix operations."
---

These guides document the protocol specifications, wire formats, security boundaries, and operator workflows across Post Fiat L1v2 and Task Node.

## Post-Human Governance & Identity

- **[Hive Governance Packet & Verification Guide](/docs/hive-governance/)** — Protocol-state snapshots, carry-over accountability, 30-minute session rooms, two-pass minutes drafting, `postfiatl1v2` anchoring, and offline verification.
- **[On-Chain Identity Guide (`identity_set` & NIP-05)](/docs/onchain-identity/)** — Native `identity_set` accounts, v1/v2 Nostr key derivation, salted handle reservations, registrar policy, custom NIP-05 domains, `relay.postfiat.org`, and the quantum boundary.
- **[Information Hive Mind Contributor, MNPI Firewall & Accelerated Alpha Guide](/docs/information-hive-mind/)** — Coverage matching, two-phase company agents, in-memory hash-only MNPI refusal, human model-owner approval, and accelerated alpha rewards.

## Post Fiat L1v2 Core Chain & Local Privacy

- **[FastPay Guide for Agents & Developers](/docs/fastpay/)** — End-to-end agent playbook for FastPay v3 funding, `OwnedObjectPool` concurrency, x402 HTTP/MCP payments, Direct TLS 1.3 Protobuf RPC v2, crash recovery, and safety invariants ([plain Markdown](/agents/fastpay.md)).
- **[Post-Quantum Message Protocol, FastPay & x402 Guide](/docs/message-protocol/)** — Canonical protobuf envelopes (`pf.msg.v1`), `pf.ptr` v5 memos, X-Wing (`X25519 + ML-KEM-768`) encryption, Sui-style FastPay fees, and x402 agent payments.
- **[Quantum-Resistant NFT Protocol & Burn-First Migration Guide](/docs/nft-protocol/)** — `pf.nft.metadata.v1`, keyed L1 storage, allowlisted burn-first migration from the old chain, collection policy, and post-quantum threat model.
- **[Local Mac App (`PFSH03`) Install, Honest Privacy Model & Pause/Exit Guide](/docs/local-mac-app/)** — Native SwiftUI + Rust macOS app, local Seatbelt-sandboxed Binius proving, direct public validator RPC submission, benchmarks, Lean 4 coverage scope, and governance pause/exit runbooks.

## NAVCoins, Credentials & Cross-Chain Settlement

- **[Create a NAVCoin Guide](/docs/create-a-navcoin/)** — Open Python/Rust NAVCoin SDK, optional deterministic `NavFeeScheduleV1` formulas, exact integer math worked example, universal `floor(V * U / S)` integrity check, and primary-market accounting.
- **[`did:pftl`, Optional Trust Lines & Credential Policy Guide](/docs/did-credentials/)** — Permissionless-by-default assets, single `asset_gate(...)` enforcement, zero-PII XRPL-style Credentials, Return-only exit, aggregated bridge holds, and W3C VC / ZK-passport adapters.
- **[Hyperliquid NAVCoin on Solana & Scheduled FX Fix Guide](/docs/hyperliquid-navcoin-fx-fix/)** — Multi-fetch `HyperCoreReserveReader` attestation, Solana NAVCoin swap routing, and scheduled `FxFixPacketV1` settlement windows.

## Validator & Finance Hub Guides

- **Run a Validator (L1v2):** Published separately at `/run-a-validator/` (single `postfiat-node` binary, 2-of-3 signed releases, `upgrade`, `top`, read-replica RPC, and active-liveness rewards).
- **Finance Hub Access Guide:** Published separately at `/finance-hub/` (active validator and Top-30 contributor eligibility, Today desk, Goodbrief sandbox, Research API keys, and signed Publish API).
- **Full L1 Engineering Reference (MkDocs):** [/docs/l1/](/docs/l1/)
