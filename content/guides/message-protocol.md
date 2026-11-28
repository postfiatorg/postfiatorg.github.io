---
title: "Post-Quantum Message Protocol, FastPay & x402 Guide"
url: "/docs/message-protocol/"
type: "page"
layout: "single"
kicker: "Pillar 2 · Message Protocol"
date: 2026-11-27
summary: "Canonical protobuf wire spec (pf.msg.v1, pf.ptr v5), X-Wing post-quantum encryption, Sui-style FastPay fees and account_tx indexing, Task Node reward payouts, and x402 agent payments."
---

The Post Fiat Ledger standardizes human, wallet, and AI-agent messaging across one canonical protobuf specification (`postfiatl1v2/proto/pf/`), hybrid post-quantum encryption (**X-Wing**), content-addressed **IPFS** storage, sub-second **FastPay** transport, and **x402** machine-native payments.

Pillars 1 (Governance), 4 (NFTs), 6 (On-Chain Identity), 7 (NAVCoin disclosures), and 10 (Hive Mind claim packets) all build on this wire format.

## 1. Canonical Protobuf Packages & `pf.ptr` v5 Memo Format

Canonical `.proto` definitions live in `postfiatl1v2/proto/pf/` with generated libraries for **JavaScript/TypeScript**, **Python**, and **Rust (`prost`)**, validated against one shared cross-language test-vector suite.

- `pf/msg/v1/`: `Pointer`, `Envelope`, `Header`, `Reader`, `ContentKind` (preserving v4 kinds `1..11` plus `GOVERNANCE = 12`), `CipherSuite`, `BodyEncoding`, `Manifest`, and `pf.msg.text.v1`.
- `pf/task/v1/` and `pf/reward/v1/`: The six core Task Node task-lifecycle and reward schemas.
- **Permissionless custom schemas:** Third-party apps can define custom schemas using `schema = 1` paired with a full schema name string.

### Memo Constraints (`pf.ptr` v5)

`postfiatl1v2` allows up to 4 memos per transaction, 256 decoded bytes per memo (512 bytes total), encoded in **lowercase hex**. Uppercase hex from legacy old-chain v4 tooling is rejected by `postfiatl1v2`.

| Field | Format | Notes |
| --- | --- | --- |
| `memo_type` | `pf.ptr` | ASCII hex |
| `memo_format` | `v5` | Identifies canonical protobuf `Pointer` |
| `memo_data` | Lowercase hex protobuf bytes (`<= 256` B) | Replaces ASCII CID strings with 36-byte binary `cid_bin` (or `inline` payload for tiny public records such as x402 request hashes) |
| Visibility flags | Exactly one of `public`, `private`, `sealed` | Consensus/client parser rejects ambiguous flag combinations |

Pure messages that transfer no value to another party use a **FastPay self-transfer** or a **`payment_v2` self-payment**. No separate message transaction type is required.

### Zero Re-Serialization Rule & Large Payloads

An `Envelope` (`pf.msg.v1`) is stored as a single IPFS **CIDv1 `raw` block (SHA-256)** up to **1 MiB**, allowing clients to compute the exact CID offline before pinning.

`Envelope` carries `header`, `readers[]`, and `body` as opaque raw byte fields. Verifiers MUST check the CID and the **ML-DSA-65** signature over those exact transmitted bytes **before** decoding inner protobuf messages, and MUST never re-serialize protobuf to verify a signature. This eliminates cross-language canonicalization drift.

Payloads larger than 1 MiB (up to **16 MiB**) use a signed `Manifest` listing ordered chunk CIDs with chunk-index-bound authenticated encryption.

### Body Encoding

- `PROTOBUF` is the default encoding.
- `CANONICAL_JSON` (RFC 8785 / JCS) is supported for human-inspectable artifacts such as Pillar 1 governance packets and Pillar 4 NFT JSON projections.

### IPFS Pinning Responsibility & Durable Outbox

- **Task Node pins:** All Task Node lifecycle/reward traffic, Pillar 1 governance packets, and official Post Fiat NFT metadata.
- **Outside developers & third-party apps:** Pin their own envelopes (or pay a pinning gateway over x402).
- **Durable async outbox:** Pinning runs asynchronously so it never adds latency to FastPay payments. Clients persist envelopes to a durable local or server outbox with exponential retry (browser/NAT clients upload raw blocks through Task Node's authenticated CID-verified pin endpoint) so closing a tab never strands an unpinned CID.

## 2. Post-Quantum Encryption (X-Wing) & Zero-Balance Bootstrap

Private and sealed messages encrypt bodies with **X-Wing (`X25519 + ML-KEM-768`)** + **HKDF-SHA256** + **XChaCha20-Poly1305**:

1. Generate a fresh random 32-byte content encryption key (`CEK`).
2. Encrypt the payload body with `XChaCha20-Poly1305` (no plaintext SHA-256 hash is ever published).
3. For each recipient in `readers[]`, encapsulate a shared secret with X-Wing, derive a wrap key via `HKDF-SHA256` bound to `(header_hash, chain_id, recipient_key_id)`, and wrap `CEK`.
4. Sign the raw envelope bytes with the sender's ML-DSA-65 account key.

### Zero-Balance New-User Key Bootstrap

Every wallet deterministically derives its X-Wing message KEM key from the master seed using HKDF domain `postfiat-l1-v2/message-key/v1`.

Because new Task Node users start with `0 PFT` and cannot submit an on-chain [Pillar 6 `identity_set`](/docs/onchain-identity/) before receiving their first reward:

1. At onboarding, the wallet signs its derived X-Wing public key with its ML-DSA-65 account key under domain `postfiat-l1-v2/message-key-bind/v1`.
2. Task Node stores this signed binding so the user's very first FastPay payout encrypts cleanly to their wallet.
3. Once the user mints an on-chain Pillar 6 identity, the on-chain `message_key` becomes authoritative and clients cross-check it.

**Forward-secrecy note:** Deterministic seed derivation ensures a user can restore and decrypt historical messages from one BIP-39 recovery phrase, which trades away per-message forward secrecy if the master seed is later compromised.

### Reader Policy & Legacy Dual-Read

- Task Node is included as a reader **only** on Task Node lifecycle and reward schemas the server must process — **never** on user-to-user messages or shielded (`PFSH03`) payments.
- Wallets decode both legacy `pf.ptr` v4 and canonical `pf.ptr` v5 pointers. Importing an old-chain seed lets a user decrypt historical classical X25519 payloads locally.
- **Shielded (`PFSH03`) payments:** In v1, `PFSH03` transactions do not carry in-note encrypted memos so the Binius ZK circuit stays untouched. Optional private notes travel off-chain via Hive/Nostr.

## 3. Sui-Style FastPay Fees, `account_tx` History & Crash-Safe Payouts

### FastPay Fee & Anti-Bloat Formula (v1)

To prevent zero-fee spam and owned-object state bloat while keeping transfers sub-cent and merging cheap, validators enforce a minimum FastPay fee on every `OwnedTransferOrderV3`:

```text
min_fee_atoms = 25
              + ceil(tx_bytes / 512) * 1
              + max(0, outputs - inputs) * 1_000
              + inputs * 1
```

- Creating net-new owned objects (`outputs > inputs`) costs `1,000 atoms` (`0.001 PFT`) per new object on top of the 25-atom base fee (`0.000025 PFT`).
- Merging up to 2,048 small payout objects pays only the base fee plus 1 atom per input and byte surcharge — no new-object surcharge.
- The brittle 100,000 chain-wide owned-object kill switch is replaced by per-account soft caps and a higher global ceiling.
- A future v2 upgrade may add Sui-style refundable storage deposits (99% rebate on merge/unwrap) if owned-object volume warrants it.

### Canonical `order_hash` Indexing in `account_tx` & `tx`

Applied FastPay transfers and unwraps (including their `pf.ptr` v5 memos) are indexed directly into `account_tx` and `tx` keyed by **`order_hash`** — the immutable hash of the signed `OwnedTransferOrderV3`. Indexing by `order_hash` rather than `certificate_digest` guarantees a single canonical transaction ID regardless of which validator quorum signatures arrived first.

### Crash-Safe Task Node Payout Pool

Task Node pays task rewards over FastPay by default using a leased pool of ~20 owned objects (serialized with DB row locks):

1. Task Node durably persists `(payout_id, object_id, order_hash, signed_order_bytes)` **before** submitting to validators.
2. On crash or timeout, recovery always polls or resubmits that exact `order_hash` — never signing a conflicting order on the same object (avoiding equivocation locks).
3. Fallback to `payment_v2` executes only after confirming the FastPay order was never certified and cleanly recovering or replacing the leased object, ensuring zero double payouts.
4. Target latency: `p50 < 500ms`, `p95 < 2s`, `< 1%` consensus-lane fallback.
5. Task Node payouts use **`private`** visibility (not `sealed`): the body stays encrypted to the recipient and Task Node, while the explorer displays a clean `"Task reward"` badge and CID.

## 4. Spoof-Proof Explorer Rendering

The block explorer decodes public `pf.msg.v1` envelopes using the published protobuf `FileDescriptorSet` with strict HTML escaping, zero script execution, click-to-load media, oversize/dead-CID guards, and an operator abuse denylist.

- **Verified sender:** Displayed only when `envelope.sender_pubkey` matches the transaction signer.
- **`"Task reward"` badge:** Displayed **only** when the verified `sender_pubkey` matches the pinned official Task Node payout key. Outsider `pf.reward.v1` messages render as generic *Private message* so payouts cannot be spoofed.
- **Zero key exposure:** The explorer never handles private keys or decrypts private messages; decryption happens strictly inside the user's local wallet or Mac app.

## 5. Worked Wire Example (`pf.ptr` v5 Over FastPay)

```json
{
  "transport": "fastpay_owned_transfer_v3",
  "order_hash": "<96-hex-immutable-order-hash>",
  "fee_atoms": 35,
  "memos": [
    {
      "memo_type": "70662e707472",
      "memo_format": "7635",
      "memo_data": "<lowercase-hex-protobuf-Pointer-<=256-bytes>"
    }
  ],
  "decoded_pointer": {
    "version": 5,
    "kind": 10,
    "visibility": "private",
    "cid_bin": "<36-byte-cidv1-raw-sha256>",
    "schema": "pf.reward.v1",
    "thread_id": "task-98412"
  }
}
```

## 6. Agent Payments via x402 (+ Thin MCP Helper)

Post Fiat supports **x402 v2** (`PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, `PAYMENT-RESPONSE`) so APIs and MCP tools can charge AI agents per request with sub-second finality. For complete copy-pasteable JavaScript, Python, `OwnedObjectPool`, Direct TLS 1.3 Protobuf RPC v2, and crash-safety rules, see the **[FastPay Guide for Agents & Developers](/docs/fastpay/)** ([plain Markdown](/agents/fastpay.md)).

### Supported Settlement Lanes

| Scheme | Asset & Lane | Finality | Deduplication Key |
| --- | --- | --- | --- |
| `exact` / `pf-fastpay-settled` | Native `PFT` over FastPay | 1-RTT quorum certificate (`273 ms` p50 / `307 ms` p95 direct WAN; `322 ms` p50 / `350 ms` p95 x402 WAN; `11.7 ms` co-located `owned_sign_v3`) | Immutable 48 B `order_hash` |
| `exact` (consensus fallback) | `pfUSDC` via `issued_payment_v2` | Ordered consensus accepted receipt | Canonical `tx_hash` |

### End-to-End Flow

1. Client sends an HTTP request to a paid endpoint.
2. Server responds `402 Payment Required` with `PAYMENT-REQUIRED` specifying price, payee account, asset/lane, request hash, and expiry nonce.
3. Client signs a FastPay `OwnedTransferOrderV3` (embedding the request hash in an inline `pf.ptr` v5 memo) and retries with `PAYMENT-SIGNATURE`.
4. The Post Fiat facilitator validates ML-DSA signatures, `payTo`, amount, and nonce locally (under per-IP and per-key rate limits) **before** contacting validators, collects quorum votes (or confirms the consensus receipt for `pfUSDC`), records the spent `order_hash` / `tx_hash` across replicas to block replay, and returns `200 OK` with `PAYMENT-RESPONSE` containing the settlement digest.

### Thin MCP Payment Wrapper

The Post Fiat x402 package ships a thin MCP tool wrapper that intercepts `402` responses from MCP servers, checks the local per-call and daily spending cap, signs the FastPay transfer via the local wallet, and retries automatically.
