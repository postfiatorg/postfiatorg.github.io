---
title: "Quantum-Resistant NFT Protocol & Burn-First Migration Guide"
url: "/docs/nft-protocol/"
type: "page"
layout: "single"
kicker: "Pillar 4 · NFT System"
date: 2026-11-27
summary: "Specification for post-quantum NFTs on postfiatl1v2: pf.nft.metadata.v1, keyed L1 storage, collection policy, allowlisted burn-first migration from the old chain, and post-quantum threat model."
---

Post Fiat L1v2 implements native NFTs (`nft_mint`, `nft_transfer`, `nft_burn`) secured by **ML-DSA-65** signatures and **SHA3-384** identifiers. Metadata rides on [Pillar 2's signed `pf.msg.v1` envelope format](/docs/message-protocol/), and historical Task Node NFTs move from the old XRPL-fork chain through a deterministic, burn-first migration that prevents duplicate live copies.

## 1. Metadata Standard (`pf.nft.metadata.v1`) & One-Hash Rule

Every `postfiatl1v2` NFT binds its on-chain record to a single immutable metadata byte stream:

- **`metadata_uri`:** IPFS CIDv1 `raw` block of a public, signed Pillar 2 `pf.msg.v1` envelope wrapping a `pf.nft.metadata.v1` protobuf payload.
- **`metadata_hash`:** `SHA3-384` of those exact raw envelope bytes.
- **Issuer binding:** `envelope.sender_pubkey` **must** match the on-chain `nft.issuer`. Clients and the block explorer reject mismatched signers.
- **Display projection:** JSON views (ERC-721 / XLS-24 compatible) are derived read-only projections from the canonical protobuf envelope.

### Core `pf.nft.metadata.v1` Fields

| Field | Type | Description |
| --- | --- | --- |
| `name`, `description` | `string` | Human-readable title and description |
| `image` | `string` | `ipfs://<cid>` of primary artwork (unchanged on migration) |
| `media[]` | `MediaAttachment[]` | Typed secondary media attachments |
| `attributes[]` | `Attribute[]` | Structured traits |
| `collection` | `string` | Collection name (always displayed alongside `nft.issuer`) |
| `content_hashes` | `map<string, bytes>` | `SHA3-384` digest of every referenced asset |
| `prompt_digest` | `bytes` | Optional digest of generation prompt (encrypted private prompt assets use Pillar 2 X-Wing encrypted to Task Node keys, never to holders, so transfers require zero re-encryption) |
| `license` | `string` | License identifier |
| `origin` | `OriginRecord` (optional) | `source_chain`, `nftoken_id`, `original_issuer`, `original_uri`, `mint_tx`, `retirement_mode`, `burn_tx`, `claim_cid`, `claim_hash` |

Storing **`claim_cid`** alongside `claim_hash` inside `origin` lets any verifier fetch and verify the user's ML-DSA-65 migration claim offline.

## 2. Official Task Node Collection Policy

| Policy Parameter | Task Node Profile Collection Setting | Rationale |
| --- | --- | --- |
| **Issuer structure** | Dedicated migration issuer key (retired when migration closes) + separate ongoing fresh-mint issuer key | Isolates migration risk; allows clean retirement of classical-claim minting |
| **`ISSUER_BURNABLE`** | **`false` (OFF)** | Task Node can never burn a holder's profile NFT (execution still enforces `ISSUER_BURNABLE` cleanly for third-party collections that explicitly enable it) |
| **`TRANSFERABLE`** | **`true` (ON)** | Preserves transferability holders already had on the old chain |
| **Issuer transfer fee** | **`0` PFT** | Avoids charging users when moving NFTs between their own wallets |
| **Gas & IPFS pinning** | Task Node sponsors migration gas/account-creation (per-account capped) and pins official Task Node NFT assets long-term | Third-party issuers pay their own gas and pin their own metadata |
| **Credentials** | Kept separate | KYC, validator, and Top-30 standing live in [Pillar 8 Credentials](/docs/did-credentials/), not duplicated in NFTs |

### Unsolicited Spam Defense

Minting stays permissionless on chain, matching Post Fiat's permissionless-by-default model:

- Consensus rejects any unsolicited mint to another account that sets **both** `BURN_LOCKED` and `TRANSFER_LOCKED` (preventing attackers from permanently gluing unburnable, untransferable junk onto someone else's account).
- Wallets hide NFTs from unfollowed issuers by default.

## 3. L1 Scaling & Activation-Gated State Rules

Behind a governed consensus activation height (preserving byte-identical historical replay):

1. **Keyed NFT storage:** Replaces linear-scan `Vec` storage with keyed lookups and paginated `account_nfts` and `issuer_nfts` RPCs (eliminating `O(N)` RPC dumps).
2. **`ISSUER_BURNABLE` enforcement:** Enforced strictly in execution only when enabled on a collection.
3. **Permanent `used_nft_serials` tombstones:** Every minted `(issuer, serial)` records a permanent tombstone. Even if a holder later burns their migrated NFT on `postfiatl1v2`, that serial can **never** be re-minted.
4. **Partitioned serial space:** Bit 63 (`1 << 63`) separates deterministic hash-derived migrated serials (`bit 63 = 1`) from sequential fresh mints (`bit 63 = 0`), preventing collisions.

## 4. Burn-First Migration Guide (Old Chain -> `postfiatl1v2`)

Migration in v1 covers **Old Post Fiat chain (Task Node / PFTasks) NFTs**. External XRPL mainnet NFTs are not burn-migrated (optional pin-only provenance records can reference them without burning anything on XRPL mainnet).

### Step 1 — Pre-Cutoff Allowlist Inventory

Before any burn is accepted, the read-only inventory tool scans old-chain wallets (`account_nfts`), joins Task Node and PFTasks records, and freezes a **signed pre-cutoff eligibility allowlist**. Only NFTs minted before the cutoff ledger index and present on the allowlist qualify. This prevents attackers from minting cheap junk on the old chain to pollute the official collection or drain sponsored gas.

### Step 2 — Pre-Validate & Persist ML-DSA Claim Before Burning

Never burn an old NFT before the claim is durably pinned:

1. Migration service verifies the `NFTokenID` is on the allowlist and unmigrated.
2. User's new `postfiatl1v2` wallet (`wallet_wasm` or Mac app) signs `pf.nft.claim.v1` with their ML-DSA-65 key, binding `(old_nftoken_id, old_owner, new_account, cutoff_ledger)`.
3. Migration service durably stores and pins the signed claim to IPFS (`claim_cid`).
4. Only after `claim_cid` is pinned does the UI prompt the old-chain wallet to submit `NFTokenBurn` with `claim_hash` in the burn memo.

### Step 3 — Burn Verification & Idempotent Post-Quantum Mint

1. Migration service queries old-chain history RPC and verifies `burn_tx` is finalized, `burn_tx.account == old_owner` (not merely that a burn occurred), and the burn memo matches `claim_hash`.
2. The dedicated migration issuer mints the replacement NFT directly to `new_account` with the exact same `image` CID, `origin` record, and deterministic migrated serial (`bit 63 = 1`).
3. Re-running migration on the same `NFTokenID` — even after a full service database wipe or after the user burns the new NFT — is rejected deterministically by `used_nft_serials` on `postfiatl1v2`.

### Optional Pin-Only Provenance Mode

If a holder prefers to leave an NFT untouched on its original chain, pin-only mode anchors a signed `pf.nft.provenance.v1` Pillar 2 message via a self-payment. The block explorer displays it strictly as a **Recorded Provenance** note — never as a migrated live NFT.

## 5. Offline-Verifiable Explorer View (Survives Stage 4 Shutdown)

The `postfiatl1v2` explorer NFT page displays:

- Artwork and attributes
- **Issuer + collection** together (never collection name alone)
- Live `metadata_hash == SHA3-384(raw_envelope)` and `envelope.sender_pubkey == nft.issuer` verification
- Flags (`TRANSFERABLE`, `ISSUER_BURNABLE`, `BURN_LOCKED`, `TRANSFER_LOCKED`) and transfer history
- **Checked origin provenance:** Verified against a founder-signed, archived old-chain burn-proof bundle pinned to IPFS so provenance remains verifiable permanently after old-chain RPC nodes shut down at Stage 4.

## 6. Honest Post-Quantum Threat Model

| Surface | Post-Quantum Posture | Residual Window / Limit |
| --- | --- | --- |
| New-chain NFT ownership & transfers | **Post-quantum:** ML-DSA-65 signatures + SHA3-384 NFT IDs and metadata hashes | None beyond ML-DSA-65 / SHA3-384 assumptions |
| Migrated NFTs after mint | **Post-quantum:** Old copy is burned; replacement lives under ML-DSA-65 | None once migrated |
| Unmigrated old-chain NFTs during open claim window | **Classical (secp256k1 / Ed25519)** | While the migration window is open, a quantum attacker breaking an old-chain key could submit a burn-and-claim for an *unmigrated* NFT |
| Closing the window (Stage 4) | **Window closed:** Old chain freezes to read-only archive with a published final ledger hash; dedicated migration issuer key is permanently retired | Permanently closes the classical-key claim surface |

## 7. Verification & Test Vector Checklist

Implementers integrating `pf.nft.metadata.v1` or `wallet_wasm` NFT signing must pass the shared test vectors covering:

- Exact `SHA3-384` envelope hash match and `envelope.sender_pubkey != nft.issuer` rejection
- Deterministic `bit 63 = 1` migrated serial derivation and `used_nft_serials` replay rejection after burn on `postfiatl1v2`
- Rejection of non-allowlisted old-chain mints and mismatched burn memos
- Rejection of unsolicited `BURN_LOCKED + TRANSFER_LOCKED` mints
- Oversized metadata fields and dead IPFS gateway fallback behavior
