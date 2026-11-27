---
title: "Quantum-Resistant NFTs and Burn-First Migration on Post Fiat L1v2"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How Post Fiat moved native NFTs to ML-DSA-65 signatures, signed Pillar 2 metadata, keyed L1 storage, and replay-proof burn-first migration from the old chain."
author: "Post Fiat"
categories:
  - Engineering
tags:
  - Post Fiat
  - NFTs
  - Post-Quantum
  - ML-DSA-65
  - postfiatl1v2
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Historical Task Node profile NFTs were minted on our old XRPL-fork chain under classical keys. Leaving them stranded on a retiring chain — or casually re-minting duplicates on the new chain while the old copies still trade — is the wrong way to migrate assets.

On `postfiatl1v2`, NFTs (`nft_mint`, `nft_transfer`, `nft_burn`) are native ledger objects secured by **ML-DSA-65** signatures and **SHA3-384** identifiers, backed by keyed L1 storage and a burn-first migration that makes duplicate live copies impossible.

## One Byte Stream, One Hash (`pf.nft.metadata.v1`)

NFT metadata on most chains is an unsigned JSON URL that can silently drift or break. On `postfiatl1v2`, every NFT's `metadata_uri` points to a public, signed [Pillar 2 `pf.msg.v1` envelope](/docs/message-protocol/) pinned as an IPFS CIDv1 `raw` block, and its on-chain `metadata_hash` is the exact `SHA3-384` digest of those raw envelope bytes.

The envelope's `sender_pubkey` must match the on-chain `nft.issuer`. JSON views (ERC-721 / XLS-24) are strictly display projections. If an envelope signature does not match the issuer, wallets and the block explorer reject it.

## Collection Policy Without Surprises

For the official Task Node profile collection on `postfiatl1v2`:

- **`ISSUER_BURNABLE` is OFF:** Task Node can never burn a user's NFT.
- **`TRANSFERABLE` is ON:** Holders keep full transferability.
- **Issuer fee is `0` PFT:** Moving your own NFT between wallets costs no issuer tax.
- **Spam protection without permissioning:** Minting remains permissionless on chain, while consensus blocks unsolicited mints to another account that set *both* `BURN_LOCKED` and `TRANSFER_LOCKED` so nobody can permanently weld junk onto your wallet.

## Burn-First Migration: Zero Duplicate Copies

Migrating old Post Fiat chain NFTs follows four strict rules:

1. **Frozen pre-cutoff allowlist:** A read-only inventory scans old-chain wallets and joins Task Node / PFTasks records to freeze a signed pre-cutoff allowlist. Nobody can mint cheap junk on the old chain after cutoff to pollute the official collection or drain sponsored migration gas.
2. **Claim pinned before burn:** Before prompting any irreversible old-chain burn, your `postfiatl1v2` wallet signs `pf.nft.claim.v1` with its ML-DSA-65 key and Task Node durably pins that claim to IPFS (`claim_cid`).
3. **Validated burn -> deterministic mint:** Your old wallet submits `NFTokenBurn` with `claim_hash` in its memo. Once old-chain history RPC confirms `burn_tx.account == old_owner` and the memo hash matches, the dedicated migration issuer mints the replacement directly to your new account with the exact same artwork CID and verifiable origin metadata.
4. **Permanent `used_nft_serials` tombstones:** Migrated NFTs occupy a partitioned serial space (`bit 63 = 1`) backed by permanent `used_nft_serials` tombstones in `postfiatl1v2` consensus. Even if the migration DB were wiped or you burned your migrated NFT on `postfiatl1v2`, that old `NFTokenID` can never be re-minted a second time.

Users who prefer leaving an old NFT untouched can use **pin-only** mode, which anchors a signed provenance note without minting a second live NFT.

## Why the Classical Claim Window Must Close

Once migrated, an NFT is post-quantum. While the old-chain migration window remains open, however, any *unmigrated* NFT still rests behind a classical key. When the old chain freezes to a read-only archive at Stage 4 with a published final ledger hash, we permanently retire the dedicated migration issuer key — closing the classical claim window for good. Archived, founder-signed burn-proof bundles pinned to IPFS keep explorer origin verification working even after old-chain RPC nodes shut down.

## Live Migration & Mint Evidence

- **Founder old-chain burn tx:** `[INSERT LIVE OLD-CHAIN BURN TX HASH AFTER UAT]`
- **Migrated `postfiatl1v2` NFT mint tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Fresh native `postfiatl1v2` profile NFT mint tx:** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Block Explorer NFT card & verified origin:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

See the full specification, test vectors, and migration steps in the [Quantum-Resistant NFT Protocol & Burn-First Migration Guide](/docs/nft-protocol/).
