---
title: "On-Chain Identity Guide (identity_set, NIP-05 & Quantum Boundary)"
url: "/docs/onchain-identity/"
type: "page"
layout: "single"
kicker: "Pillar 6 · Hive Identity"
date: 2026-11-27
summary: "Specification for native identity_set objects on postfiatl1v2: v1/v2 Nostr key derivation, browser signing guard, 2-of-3 handle registrar policy, custom NIP-05 verification, relay.postfiat.org, and the quantum boundary."
---

Post Fiat L1v2 replaces Task Node's database-backed identity bindings with a native **`identity_set`** object in ordered consensus. Anyone — wallets, Hive Chat clients, the block explorer, or third-party scripts — can verify directly from `postfiatl1v2` RPC that an `ML-DSA-65` account, a Nostr `npub`, a `@tasknode.postfiat.org` (or custom) NIP-05 handle, a Profile NFT, a validator node key, and an AI agent controller belong to the same key holder.

## 1. Native `identity_set` Object & Consensus Bounds

All `identity_set` operations execute strictly through **ordered consensus** (never FastPay). Every field stays inline and public under explicit consensus byte caps:

| Field | Format / Bound | Purpose |
| --- | --- | --- |
| `account` | `postfiatl1v2` ML-DSA-65 account | Canonical owner of the identity |
| `nostr_pubkey` | 32-byte x-only secp256k1 pubkey | Proven by BIP-340 Schnorr signature (prevents squatting) |
| `derivation_version` | `1` (legacy old-chain) or `2` (new-chain seed KDF) | Tracks Nostr key origin |
| `key_index` | `u32` (starts at `0`) | Supports clean rotations under v2 derivation |
| `identity_kind` | `human` \| `agent` \| `service` | Distinguishes people from bots like `hive-board@` |
| `sequence` | `u64` | Strictly monotonic replay guard |
| `status` | `active` \| `revoked` | Lifecycle state |
| `handle` (optional) | Lowercase ASCII `[a-z0-9._-]`, 2–32 chars, no leading/trailing punctuation | `@tasknode.postfiat.org` or custom NIP-05 claim |
| `relays[]` | Max 5 `wss://` URLs, `<= 128` B each | Preferred Nostr relays (default includes `wss://relay.postfiat.org`) |
| `avatar_nft_id` (optional) | `postfiatl1v2` NFT ID | Links a [Pillar 4 Profile NFT](/docs/nft-protocol/) without minting a duplicate soulbound NFT |
| `message_key` (optional) | X-Wing public key | Authoritative [Pillar 2 message encryption key](/docs/message-protocol/) |
| `pq_receive_address` (optional) | `pfpq1...` | Optional [Pillar 5 shielded receive address](/docs/local-mac-app/) |
| `links[]` | Max 16 entries | Co-signed validator node key, old-chain wallet, human controller (for `agent`), or client-verified EVM/Solana wallets |

### Fees & Required vs. Optional Gating

- **Fees (burned, paid from Task Node starter PFT):** Standard byte-weighted transaction fee plus burned state-expansion fee of **`20,000 atoms` (`0.02 PFT`) for `mint`** and **`10,000 atoms` (`0.01 PFT`) per `link`**. No refundable reserve machinery.
- **Required for:** Claiming per-operator validator rewards ([Pillar 3](/run-a-validator/)), preventing multi-node reward farming.
- **Optional everywhere else at launch:** Hive Chat, Finance Hub, and NFTs work without minting; minting upgrades an account to chain-verified badges.

## 2. Operations, Co-Signing & Uniqueness Rules

### Supported Operations

- `mint` — Create the account's on-chain identity with ML-DSA-65 + BIP-340 Nostr proof.
- `update` — Modify relays, avatar NFT, `message_key`, or `pq_receive_address`.
- `link` / `unlink` — Attach or detach linked keys. Linked-key self-unlink commits to an explicit `link_id` (not the owner's sequence) so it cannot be front-run.
- `rotate` (`planned` or `compromised`) — Rotate `nostr_pubkey`. A **`compromised`** `npub` can **never** be rebound (blocking impersonation). A **`planned`** rotation keeps handles and links intact.
- `rotate_account` — Move the identity to a new `postfiatl1v2` account. **Must be co-signed by BOTH the old account and the new destination account** (blocking unwanted identity dumps); validator and controller links enter *pending re-confirmation* until co-signed against the new account.
- `revoke` — Permanently revoke the identity.

### Namespace-Scoped Uniqueness

Consensus enforces global uniqueness **only** on:

1. `(account)` — 1 active identity per account
2. `(nostr_pubkey)` — 1 active identity per Nostr pubkey
3. `(registered_namespace, handle)` — e.g., `@tasknode.postfiat.org`
4. `(validator_node_id)` — co-signed via Pillar 3's signer allow-list (`postfiat-l1-v2/identity-link/v1`), with a **30-day cooldown** between operator switches to block validator-reward hopping
5. `(old_chain_account)` — proven by strict low-S DER ECDSA signature

**Custom NIP-05 domains (`you@yourdomain.com`) and external EVM/Solana links are stored as non-unique client-verified claims**, verified live against DNS/`nostr.json` or client signatures so nobody can squat another person's domain on chain.

### Query RPCs & SDK

- `identity_info(account)`
- `identity_by_nostr(nostr_pubkey)`
- `identity_by_handle(namespace, handle)`
- `identity_by_link(link_type, target)`
- SDK helper `resolveIdentity(...)` reads purely from `postfiatl1v2` RPC with zero dependency on Task Node's database.

## 3. Nostr Key Derivation (v1 Legacy vs. v2 Seed KDF) & Signing Guard

### Browser Signing Guard (Prerequisite Security Fix)

Before any v1 identity mint runs, Task Node enforces a strict client-side prefix guard:

- `signedCollaborationProof` signs **only** payloads starting with `Task Node collaboration authorization`.
- The Nostr v1 derivation helper is the **only** path allowed to sign `Task Node private messaging identity`.

This blocks a compromised server from tricking the browser into re-deriving a user's v1 Nostr private key through a collaboration challenge.

### Preserving Existing v1 `npub`s vs. Clean v2 Seed Derivation

Because `ML-DSA-65` signatures are randomized, new users cannot derive a deterministic Nostr key by hashing an ML-DSA signature:

- **Existing Task Node users (`derivation_version = 1`):** Keep their exact legacy `npub`, contacts, and Hive Chat history intact when minting, or opt straight into v2 during handle claim. Anyone can `rotate` from v1 to v2 at any time.
- **New users & rotations (`derivation_version = 2`):** Derive the secp256k1 Nostr key directly from the new-chain BIP-39 master seed via `derive_wallet_seed` (implemented once in Rust `rpc_sdk` / `wallet_wasm`, shared across web, Mac app, and CLI with CI test vectors):
  - Domain tag: `postfiat.wallet.nostr.seed.v1`
  - Role: `nostr-messaging`
  - Inputs: `(master_seed, account_index, key_index)` — **intentionally excluding `chain_id`** so the user's `npub` survives chain upgrades.
  - **Key-compromise note:** Compromising the master BIP-39 seed compromises both the `ML-DSA-65` account key and v2 Nostr keys.

## 4. Handle Registrar Policy & Custom NIP-05 Guide

### Salted Handle Reservations

To migrate existing `@tasknode.postfiat.org` handles (such as `goodalexander` and the first `agent` identity `hive-board@` with its co-signed human controller link) without front-running:

1. The registrar publishes `handle_reserve` committing to `SHA3-384(handle || npub || secret_salt)`.
2. `secret_salt` is delivered privately inside the user's authenticated Task Node session so outsiders cannot precompute `hash(npub)` and race the claim.
3. The user submits `identity_set(mint)` revealing `secret_salt` to claim the handle atomically.

### Two-Tier Registrar Authority (No Hot-Key Hijacking)

- **Hot Task Node registrar key:** May issue attestations for **new unclaimed** `@tasknode.postfiat.org` handles only.
- **2-of-3 cold/multisig registrar authority (`handle_reassign`):** Reassigning an already claimed handle (strictly for verified lost-key recovery or clear abuse/impersonation, always logged on chain with a reason code) requires **2-of-3 cold multisig** plus a **7-day timelock** during which the current owner can contest or cancel (unless an emergency compromise flag is co-signed).

### Binding a Custom NIP-05 Domain (`you@yourdomain.com`)

1. Add `you@yourdomain.com` as your custom handle claim in `identity_set`.
2. Serve `https://yourdomain.com/.well-known/nostr.json?name=you` returning your exact 64-hex `nostr_pubkey` (and optional `relays`) with `Access-Control-Allow-Origin: *`, or publish the matching DNS TXT record `_postfiat-identity.yourdomain.com`.
3. Wallets and the explorer cross-check the live `nostr.json` / DNS record against your on-chain `nostr_pubkey` and display **Client-verified NIP-05**.

## 5. Chain-Backed Hive Badges & `relay.postfiat.org`

- **Chain-backed NIP-05 & badges:** Task Node serves `nostr.json` and Hive badges (*Minted*, *Validator · node_id*, *Old chain*) directly from `postfiatl1v2` for minted accounts. On `revoke` or compromised `rotate`, badges strip immediately from all events not anchored on chain before the revoke height (never trusting client-supplied `created_at`).
- **First-party relay (`wss://relay.postfiat.org`):** Operates alongside public mirrors (Primal, nos.lol, Damus) so Hive Chat never depends solely on third-party relays. Enforces NIP-42 authentication / registered-member write admission, per-pubkey rate limits, and inbound mirror filtering. Non-production builds never publish kind-0 profiles to public relays.

## 6. Honest Quantum Boundary

| Component | Algorithm | Quantum Posture & Mitigation |
| --- | --- | --- |
| Account ownership, `identity_set` writes, funds, NFTs, validator consensus | **ML-DSA-65 (FIPS 204)** | **Post-quantum.** Classical Nostr keys can **never** move funds or authorize chain state changes |
| Nostr chat signing & v1/v2 `npub` binding | **BIP-340 Schnorr (secp256k1)** | **Classical (required by Nostr protocol).** Domain-separated per `(op, chain_id, account, sequence)`. High-value governance and claim events attach ML-DSA-65 companion signatures |
| Future classical proof retirement | Governance BIP-340 kill-switch | If governance activates the BIP-340 kill-switch in the future, existing identities **never deadlock** — pure ML-DSA-65 `update`, `rotate_account`, `link`/`unlink`, and `revoke` continue working |
