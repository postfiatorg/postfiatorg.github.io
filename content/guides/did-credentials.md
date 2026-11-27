---
title: "did:pftl, Optional Trust Lines & Credential Policy Guide"
url: "/docs/did-credentials/"
type: "page"
layout: "single"
kicker: "Pillar 8 · On-Chain Identity & Credentials"
date: 2026-11-27
summary: "Permissionless-by-default assets on postfiatl1v2, single asset_gate enforcement, zero-PII XRPL-style Credentials, Return-only exit, aggregated bridge holds, did:pftl resolution, and W3C VC / ZK-passport adapters."
---

On `postfiatl1v2`, **everything is permissionless by default**. Users do **not** need trust lines to hold, transfer, bid on, or escrow default assets or NAVCoins.

When a third-party asset creator requires eligibility rules (for example, a KYC-gated or jurisdiction-restricted NAVCoin), Post Fiat provides an opt-in, zero-PII credential layer where **the asset creator chooses which verifiers to trust** and Post Fiat governance never acts as a compliance gatekeeper.

## 1. Permissionless by Default & Optional Trust Lines

| Asset Type | `trust_set` Required? | DEX Offers & Escrows | Policy Immutability |
| --- | --- | --- | --- |
| **Default (Permissionless)** | **No.** Holding lines auto-create on receipt, DEX offer, or escrow | Auto-creates missing line (10-atom burned line fee) | `requires_authorization` can **never** flip `false -> true` after launch |
| **Opt-in Gated (`requires_authorization = true`)** | No manual pre-step if user passes `asset_gate` (or manual approval in `either`/`both` mode) | Checked live by `asset_gate(...)` at executing height | Can open one-way (`true -> false`) or loosen anytime; tightening requires **7-day block notice** (with emergency compromised-issuer removal escape hatch) |

### Anti-Bloat & Holder Controls

- **Consistent 10-atom line fee:** Charged across all line-creation paths (payments, DEX offers, escrows, NAV mints).
- **Auto-pruning empty implicit lines:** Zero-balance, non-frozen, default-limit implicit lines prune automatically on debit/zero-out so dust does not accumulate permanent ledger state.
- **Binding `holder_limit`:** Holders who explicitly set a `TrustLine.holder_limit` are never auto-raised above it.
- **Opt-in `refuse_unsolicited_assets`:** Account flag (off by default for normal users, available for institutional wallets) that blocks unsolicited third-party asset deliveries. Wallets and the explorer clearly badge unsolicited assets.

## 2. Single `asset_gate(...)` Enforcement & Return-Only Exit

Behind a governed activation height (closing an earlier helper bug that implicitly created `authorized = true` lines on gated assets), **every** user-facing issued-asset movement runs through one single consensus function:

```text
asset_gate(asset, from, to, op_kind, block_height) -> Allow | Reject(code) | Hold
```

Covered paths:

- Payments and swaps
- DEX offers (`offer_create`, fills) and escrows
- NAV mint and NAV redeem
- Ethereum and Solana bridge imports
- Fast-lane permits (with explicit `RevokeHolderPermit`)
- Pillar 7 `nav_fee_claim` *(note: atomic fee accrual inside `nav_epoch_finalize` mints into the protocol unclaimed bucket without calling `asset_gate` so epoch finalization can never deadlock)*

Gated assets create missing recipient lines **only** when `asset_gate` passes, and always with `line.authorized = false` so credentials stay checked live on every future movement and revocations always take effect immediately.

### Default Exit Rule: Return-Only (Funds Never Stranded)

When a holder's credential expires or is revoked on a gated asset, the default policy is **Return-only**:

- Third-party transfers and new market acquisitions are blocked.
- `offer_cancel` and escrow refunds **always** return locked units to the owner's own line.
- `AssetBurn`, `NavRedeemAtNav` (if a NAV route exists), and direct `pay-issuer` transfers **always succeed** so funds are never stranded.
- Issuers whose jurisdiction requires strict freeze/clawback may opt into `freeze_enabled` / `clawback_enabled` explicitly at asset creation (wallets warn users clearly on escrows of `clawback_enabled` assets).

### Anti-DoS DEX Pruning, Bounded Clawback & Aggregated Bridge Holds

- **DEX book anti-poisoning:** Permissionless `offer_prune_ineligible` cleans stale ineligible resting makers, and skipped ineligible makers are counted separately from filled crosses (persisting cancellations on partial fills) so stale makers cannot exhaust the 64-cross DEX cap.
- **Bounded `asset_clawback`:** Accepts an explicit bounded list (max **64** offers, escrows, or holds per transaction) to prevent `O(N)` block-validation DoS.
- **Aggregated bridge holds (`(asset, recipient)`):** Finalized Ethereum or Solana bridge imports cannot be rolled back on the source chain. Any non-fatal recipient rejection — `asset_gate` failure, `holder_limit` exceeded, or `refuse_unsolicited_assets` — routes cleanly into a single **aggregated claimable hold keyed by `(asset, recipient)`** (emitting individual `source_reference` IDs in receipts without creating unbounded per-transfer state objects). Holds are claimable once eligible, returnable/burnable under Return-only, and reachable by `asset_clawback`.
- **Shielded pool boundary:** Gated assets are barred from shielded pools (`PFSH03`) in v1.
- **Ethereum/Uniswap wrappers for gated NAVCoins:** Two explicit launch modes — **PFTL only** (no Uniswap pool) or **PFTL + Ethereum free-moving wrapper, clearly disclosed** (no ERC-3643 allowlist bridge in v1).

## 3. Issuer Registry & Zero-PII XRPL-Style Credentials

### On-Chain Issuer Registry (Creator-Owned Trust)

Each gated-asset creator specifies which `(issuer_id, credential_type)` pairs their asset accepts. Post Fiat governance does not curate, approve, or bond KYC vendors.

An `IssuerRecord` stores:

- `issuer_id` and `admin_account` (rotatable via two-step **`issuer_admin_transfer`** so losing one admin key never bricks an issuer)
- Rotatable `ML-DSA-65` `signing_accounts[]` with optional compromise cutoff height
- `domain` string (verified **off chain** by the explorer and W3C DID resolvers — never non-deterministic DNS inside consensus)
- Namespaced `credential_types[]` (e.g., `<domain>/kyc.basic`, `<domain>/passport.over18`) and optional linked vendor DIDs

### Credential Lifecycle & Zero-PFT Delegated Acceptance

**Zero personal data (PII) is ever written to `postfiatl1v2`.** An on-chain credential stores only `(subject, issuer_id, credential_type, issued_height, expiry_height, signing_account, status, salted_commitment_hash)`.

- **Delegated atomic onboarding (`credential_create_and_accept`):** During an off-chain KYC or ZK-passport flow, the user signs both proof-of-control and credential acceptance; the issuer submits them in one transaction (paying a small refundable deposit). Brand-new **`0 PFT`** accounts can receive an accepted credential with zero gas chicken-and-egg deadlock.
- **Standard two-step flow:** `credential_create` followed by subject-signed `credential_accept` is also supported.
- **Safe renewal:** Renewing a credential overwrites `issued_height`, `signing_account`, and `status`, blocking a compromised old signing key from renewing prior records past its cutoff height.
- **Deletion & deposit return:** `credential_delete` (callable by subject, issuer, or anyone post-expiry) removes the ledger object and returns the refundable deposit to the issuer.

### Credential Policy Expressions

A gated asset sets `approval_mode` (`either` manual issuer authorization OR valid credential, or `both`) and a bounded `credential_policy`: an **OR-list of AND-rules** over `(issuer_id, credential_type)` pairs, benchmarked at the worst-case 64-maker DEX cross.

## 4. `did:pftl` Method Specification

Post Fiat accounts resolve natively as W3C Decentralized Identifiers via the **`did_resolve`** RPC:

```text
did:pftl:<chain_id>:<account>
```

Example:

```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:pftl:postfiat-mainnet-1:pftl1...",
  "verificationMethod": [
    {
      "id": "did:pftl:postfiat-mainnet-1:pftl1...#mldsa-1",
      "type": "MlDsa65VerificationKey2025",
      "controller": "did:pftl:postfiat-mainnet-1:pftl1...",
      "publicKeyHex": "<1952-byte-mldsa65-pubkey-once-revealed>"
    }
  ],
  "service": [],
  "pftlIdentity": {
    "handle": "example@tasknode.postfiat.org",
    "nostrPubkey": "<optional-pillar6-npub>"
  }
}
```

**Privacy default in wallets:** Wallets default to a **separate account** for credentialed assets and warn explicitly before linking a credentialed account to a public [Pillar 6 social identity](/docs/onchain-identity/).

## 5. Reference Issuer Adapters (W3C VC & ZK-Passport)

Post Fiat ships two reference off-chain adapters that verify proofs off chain and submit `ML-DSA-65` credentials (keeping heavy SNARK verifiers out of L1 consensus):

1. **Generic W3C VC Webhook Adapter:** Accepts standard signed W3C Verifiable Credentials from an asset creator's chosen KYC vendor, verifies subject ML-DSA-65 proof-of-control, computes the salted commitment hash, and submits `credential_create_and_accept`.
2. **Open-Source ZK-Passport Verifier Adapter (Self / OpenPassport style):** Verifies NFC passport ZK proofs off chain (for example, age `>= 18` or jurisdiction exclusion without disclosing name or passport number) and mints the corresponding zero-PII `<domain>/passport.*` credential on `postfiatl1v2`.
