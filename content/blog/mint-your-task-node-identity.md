---
title: "Mint Your Task Node Identity: Native On-Chain Identity for Nostr and Hive"
date: 2026-11-27T00:00:00Z
draft: true
summary: "Moving Task Node handles, Nostr keys, validator links, and agent controllers out of Postgres and into native identity_set objects on postfiatl1v2—plus our first-party relay.postfiat.org."
author: "Post Fiat"
categories:
  - Identity
tags:
  - Post Fiat
  - Identity
  - Nostr
  - NIP-05
  - Hive
  - postfiatl1v2
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Until now, your Hive Chat identity — your `@tasknode.postfiat.org` handle, your Nostr `npub`, and your validator badge — lived in Task Node's Postgres database. Everyone had to trust our server to say who was who.

With Pillar 6 on `postfiatl1v2`, you can **mint your Task Node identity directly on chain** via a native **`identity_set`** transaction. Any wallet, client, or explorer can verify from chain state alone that the person posting in Hive Chat, the validator operator, the Profile NFT holder, and the NAVCoin issuer are the exact same key holder.

## One On-Chain Identity Card, Zero Broken History

Minting an identity creates a compact, consensus-verified `identity_set` object tying together:

- Your post-quantum **`postfiatl1v2` account (`ML-DSA-65`)**
- Your **Nostr `npub`** (proven by a BIP-340 Schnorr signature so nobody can squat your key)
- Your **`@tasknode.postfiat.org` handle** (or a custom NIP-05 domain like `you@yourdomain.com`, verified live against DNS/`nostr.json` without on-chain domain squatting)
- Your **Profile NFT** (`avatar_nft_id`), **X-Wing `message_key`** (Pillar 2), and optional **`pfpq1...` receive address** (Pillar 5)
- **Opt-in co-signed links** to your validator node key, old-chain wallet, external EVM/Solana wallets, or — for AI agents like `hive-board@` — the human controller account

Existing Task Node users **keep their exact v1 `npub`, contacts, and Hive Chat history** when minting (and we shipped the browser signing prefix guard first so no server can ever trick a browser into re-deriving a v1 key). New users derive clean v2 Nostr keys from their new-chain BIP-39 master seed (`postfiat.wallet.nostr.seed.v1`) independent of `chain_id` so their `npub` survives chain upgrades.

## Salted Reservations, 2-of-3 Registrar Safety & `relay.postfiat.org`

- **No handle front-running:** Existing handles (`goodalexander@`, `hive-board@`, and every active Task Node handle) migrate via salted reservations `SHA3-384(handle || npub || secret_salt)` delivered privately inside your authenticated session.
- **No hot-key handle hijacking:** The hot registrar key can only issue *new unclaimed* handles. Reassigning an already claimed handle (strictly for verified lost keys or clear impersonation) requires a **2-of-3 cold multisig registrar** plus a **7-day contestable timelock**.
- **Required where it matters, optional everywhere else:** Minting is required to claim per-operator validator rewards (with a 30-day validator-link switch cooldown blocking reward hopping) and optional for Hive Chat, Finance Hub, and NFTs.
- **First-party Nostr relay:** We now run `wss://relay.postfiat.org` (NIP-42 authenticated, rate-limited, mirrored to public relays) so Hive Chat never breaks when third-party public relays throttle traffic.

## Honest About the Quantum Boundary

Nostr uses classical secp256k1 BIP-340 signatures. On `postfiatl1v2`, those classical keys are **strictly scoped to Nostr chat and identity binding — they can never move funds or change account state.** All value, NFTs, and `identity_set` ownership rest on post-quantum **ML-DSA-65**. If governance ever activates the classical BIP-340 kill-switch in the future, existing identities never deadlock: pure ML-DSA-65 `update`, `rotate_account`, `link`/`unlink`, and `revoke` keep working normally.

## Live Identity Mint Evidence

- **`goodalexander@tasknode.postfiat.org` mint tx (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **`hive-board@tasknode.postfiat.org` agent identity + controller link tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Validator & old-chain co-signed link tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer Identity Card screenshot:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Read the full `identity_set` specification, derivation vectors, and custom NIP-05 instructions in the [On-Chain Identity Guide](/docs/onchain-identity/).
