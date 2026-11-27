---
title: "Post-Quantum Messaging, FastPay & x402 on Post Fiat L1v2: Wire Format, Hardened Privacy & Devnet Benchmarks"
date: 2026-11-27T00:00:00Z
draft: false
summary: "How Post Fiat L1v2 anchors post-quantum encrypted messages, FastPay payouts, and x402 agent payments using canonical protobufs, X-Wing + key-committing AEAD, blinded SEALED tags, and rotatable forward-secret keys—verified across Blocks 1923–1933 with JS/Python interop and load benchmarks."
author: "Post Fiat"
categories:
  - Engineering
tags:
  - Post Fiat
  - Post-Quantum
  - X-Wing
  - ML-DSA-65
  - Protobuf
  - Messaging
  - Evidence
---

When wallets, validators, and AI agents coordinate work on a blockchain, payments rarely travel alone. A task payout needs a receipt; a governance vote needs a disclosure packet; two wallets need an encrypted thread. Putting kilobytes of encrypted text directly into consensus blocks does not scale—especially with post-quantum cryptography, where a single signature and public key already exceed 5 KB.

Post Fiat L1v2 solves this by splitting every message into two parts:

1. **A compact on-chain pointer (`54–100 B`)** tucked inside a normal transaction memo, anchoring existence, ordering, and a cryptographic fingerprint.
2. **A signed, optionally encrypted off-chain envelope** stored as a content-addressed IPFS block (CIDv1 `raw`), fetched and decrypted locally by wallets—never on a block explorer.

On Post Fiat's legacy XRPL-derived chain, `pf.ptr` v4 pointers were hand-encoded across three languages with no shared schema, used classical X25519 encryption, omitted a full-envelope sender signature, published plaintext SHA-256 hashes, and included the Task Node server as a default reader. `postfiat.message.v1` replaces that ad-hoc format with one cross-language wire protocol.

### What This Report Covers—and What It Does Not

- **Merged on `main` across all 4 repos:** Canonical `.proto` definitions ([`postfiatl1v2#288`](https://github.com/postfiatorg/postfiatl1v2/pull/288)), Python & JavaScript codecs + x402/MCP facilitator ([`postfiatl1v2#289`](https://github.com/postfiatorg/postfiatl1v2/pull/289)), SDK anchor-binding checks ([`postfiatl1v2#310`](https://github.com/postfiatorg/postfiatl1v2/pull/310)), cryptographic hardening — `cek_commitment`, blinded `SEALED` recipient tags, and rotatable `epoch >= 1` forward-secrecy bindings + `min_known_epoch` anti-downgrade ([`postfiatl1v2#316`](https://github.com/postfiatorg/postfiatl1v2/pull/316)), Rust/WASM browser wallet signing ([`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303)), live x402 JSON-RPC chain settlement adapter ([`postfiatl1v2#312`](https://github.com/postfiatorg/postfiatl1v2/pull/312)), L1 Train A FastPay fees & `order_hash` `account_tx` indexing ([`postfiatl1v2#295`](https://github.com/postfiatorg/postfiatl1v2/pull/295)), Task Node FastPay reward payout driver ([`tasknode#450`](https://github.com/postfiatorg/tasknode/pull/450)), native Mac `V2MessagesView.swift` & FastPay → PFSH03 *Make private* ([`tasknode-apple#40`](https://github.com/postfiatorg/tasknode-apple/pull/40) including [`#41`](https://github.com/postfiatorg/tasknode-apple/pull/41)), and explorer decoding views ([`postfiatorg.github.io#56`](https://github.com/postfiatorg/postfiatorg.github.io/pull/56)).
- **Live devnet-2 tests (`postfiat-wan-devnet-2`, Blocks `1923–1933`) + benchmarks:** Eleven live `payment_v2` transactions across four funded wallets (Blocks `1923–1931` core messaging, **Block `1932`** live x402 `402 → 200 → 400/409`, and **Block `1933`** hardened blinded `SEALED` + `cek_commitment` + rotated `epoch 1` key), 14 negative/replay controls, real `@noble/post-quantum` + x402 replay-storm benchmarks, and cross-language JS → Python ML-DSA-65 interop. Every full tx hash, CID, balance, benchmark table, and error string is published in [`devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json).
- **What this report explicitly scopes out:** Side-channel guarantees on the Python test harness (`kyber-py`/`dilithium-py` are non-constant-time reference backends; production clients use Rust/WASM `crates/wallet_wasm` and native Rust `tasknode-apple`), live validator-fleet FastPay latency benchmarks (pending Train A `#295` binary rollout onto devnet-2), independent cryptographic review, and Signal-style **deniable** 1-to-1 chat (`pf.message.v1` envelopes are intentionally non-repudiable verifiable records; interactive deniable chat belongs in an off-chain PQXDH/Double-Ratchet layer).

<div class="glance">
  <div><b>11 Devnet Txs</b><span>Blocks 1923–1933 · messaging, x402 &amp; blinded SEALED · 6/6 consensus</span></div>
  <div><b>Key-Committing X-Wing</b><span>32 B cek_commitment · unlinkable SEALED tags · epoch >= 1 rotation</span></div>
  <div><b>4.96 ms Open · 763/s Storm</b><span>Measured Node.js @noble/post-quantum &amp; 200-req x402 replay defense</span></div>
  <div><b>14 / 14 Controls</b><span>Envelope, chunk, key-commit, rollback &amp; x402 replay rejections</span></div>
</div>

---

## 1. How a Message Moves

Every visibility mode—public announcement, 1-to-1 private chat, multi-recipient group dispatch, sealed drop, or multi-chunk attachment—follows the same pipeline:

```mermaid
flowchart LR
    subgraph Client["Sender Wallet or AI Agent"]
      A["Plaintext body<br/>(protobuf or canonical JSON)"] --> B{"Visibility?"}
      B -- "PRIVATE / SEALED" --> C["Generate 32 B CEK<br/>Encrypt with XChaCha20-Poly1305<br/>Wrap CEK per reader via X-Wing"]
      B -- "PUBLIC" --> D["Unencrypted body bytes"]
      C --> E["Sign raw wire bytes<br/>with ML-DSA-65 (FIPS 204)"]
      D --> E
      E --> F["Compute IPFS CIDv1 raw<br/>(36 B binary SHA-256) offline"]
    end
    F --> G["Encode pf.ptr v5 memo<br/>(lowercase hex, &le; 256 B)"]
    G --> H["Anchor on postfiatl1v2<br/>(payment_v2)"]
    E -. "async pin" .-> P[("IPFS / Block Store")]
    H --> I["account_tx &amp; Explorer"]
    P --> I
    I --> J["Verify CID, ML-DSA-65 sig,<br/>chain_id &amp; sender binding"]
    J --> K["Decrypt locally in wallet<br/>(never on explorer)"]
```

### Three Load-Bearing Wire Decisions

1. **One canonical `.proto` schema (`proto/postfiat/message/v1/message.proto`):** Core message types (`Pointer`, `Envelope`, `MessageHeader`, `XWingEncryptionHeader`, `RecipientWrap`, `Manifest`, `MessageKeyBinding`, `TextMessage`, `X402PaymentPayload`) live in one package alongside sibling governance and NFT schemas. Both the Python (`python/postfiat_rpc/message_protocol.py`) and JavaScript (`wallet-proxy/message-protocol.js`) codecs pass shared cross-language byte vectors, including 48-byte SHA3-384 transaction digests. Outside apps can register custom payloads permissionlessly via `schema_id = 1` paired with a full `schema_name` string.
2. **Sign raw bytes—never re-serialize protobufs:** Different protobuf encoders can emit fields in different orders or omit default values, quietly breaking naive "decode → re-encode → verify" signature schemes. `Envelope` sidesteps canonicalization drift by storing `header_bytes`, `encryption_header_bytes`, and `body_bytes` as opaque raw byte fields. Verifiers check the 36-byte CIDv1 `raw` digest and the FIPS 204 ML-DSA-65 signature over those exact transmitted bytes *before* decoding any nested field.
3. **Stay strictly under the 256-byte on-chain memo cap:** `postfiatl1v2` caps transactions at 4 memos, 256 decoded bytes per memo, 512 total memo bytes, and lowercase hex only. A `pf.ptr` v5 memo sets `memo_type` to `"pf.ptr"` (`70662e707472`, 6 B), `memo_format` to `"v5"` (`7635`, 2 B), and `memo_data` to canonical protobuf `Pointer` bytes carrying the 36-byte binary CIDv1 `raw` prefix (`0x01 0x55 0x12 0x20 || sha256`) or compact inline bytes. Live on devnet-2, pointers occupy `54 B` total without a thread ID, `76 B` with a thread ID, and `100 B` for a multipart manifest. Pure messages with no external payment anchor via a standard self-payment (`from == to`).

### Hybrid Post-Quantum Encryption: X-Wing + XChaCha20-Poly1305

Private and sealed messages encrypt the body once under a fresh random 32-byte Content Encryption Key (CEK) using XChaCha20-Poly1305, then wrap that CEK per recipient using **X-Wing**—an IETF CFRG draft hybrid KEM (`draft-connolly-cfrg-xwing-kem`) that combines FIPS 203 ML-KEM-768 and X25519 through SHA3-256:

| Primitive | Wire Size | Construction |
| --- | ---: | --- |
| ML-DSA-65 auth (per envelope) | `5,261 B` | `1,952 B` public key + `3,309 B` signature (FIPS 204) |
| X-Wing public key | `1,216 B` | `1,184 B` ML-KEM-768 encapsulation key `\|\|` `32 B` X25519 public key |
| X-Wing ciphertext (per reader) | `1,120 B` | `1,088 B` ML-KEM-768 ciphertext `\|\|` `32 B` X25519 ephemeral key |
| X-Wing combiner | `32 B` | `SHA3-256(ss_MLKEM \|\| ss_X25519 \|\| ct_X25519 \|\| pk_X25519 \|\| 0x5c2e2f2f5e5c)` |
| Recipient `key_id` (`PRIVATE`) | `32 B` | `SHA-256` fingerprint of the recipient's `1,216 B` X-Wing public key |
| Blinded recipient tag (`SEALED`) | `32 B` | `SHA-256("postfiat-l1-v2/sealed-recipient-tag/v1\x00" \|\| xwing_ss \|\| aad_context)` — unlinkable to any static key directory (`postfiatl1v2#316`) |
| Key commitment (`cek_commitment`) | `32 B` | `SHA-256("postfiat-l1-v2/cek-commit/v1\x00" \|\| cek \|\| aad_context)` signed inside `XWingEncryptionHeader` field `7` (`postfiatl1v2#316`) |
| Per-slot AAD (`aad_context`) | `32 B` | `SHA-256("postfiat-l1-v2/message-aad/v1" \|\| 0x00 \|\| chain_id \|\| 0x00 \|\| SHA-256(header_bytes) \|\| uint32_be(chunk_index))` |
| Wrap KEK | `32 B` | `HKDF-SHA256(ikm=xwing_ss, salt=aad_context, info="postfiat-l1-v2/xwing-wrap/v1\x00" \|\| key_id)` |
| Wrapped CEK | `48 B` | `32 B` CEK encrypted under KEK + `16 B` Poly1305 tag (`24 B` wrap nonce) |

Two implementation details are worth noting upfront:
- **Off-chain envelope weight:** Post-quantum envelopes are not small. Measured on our live devnet-2 text messages, a `PUBLIC` envelope (0 wraps) is `5,488 B`, a clean 2-wrap `SEALED` envelope is `8,047 B` (each account-less wrap adds `1,237 B`: `1,120 B` ciphertext, `48 B` wrapped CEK, `32 B` `key_id`, `24 B` nonce, and `13 B` protobuf tags), a 2-wrap `PRIVATE` envelope with two 42-byte account strings is `8,162 B` (vs. `8,075 B` for threaded `SEALED`), and a 3-wrap `PRIVATE` group reply with `reply_to_cid` is `9,539 B`. Because only the `54–100 B` pointer hits L1 consensus, this weight stays off-chain.
- **Multi-chunk encrypted `Manifest` (up to 16 MiB):** Single envelopes cap at 1 MiB. Larger payloads split into ordered encrypted chunks sharing the envelope's CEK, each with a fresh 24-byte nonce. The envelope's `XWingEncryptionHeader` stores `aad_context` for slot `0` (protecting the manifest body itself), while each chunk block $i$ recomputes `aad_context` with `uint32_be(i)`. Thus two independent layers defend multi-chunk payloads: the signed `Manifest` commits to the ordered chunk CIDs, byte lengths, and `total_plaintext_bytes` (stopping truncation), while per-chunk `aad_context` binds every ciphertext to its exact slot index, `chain_id`, and `header_bytes` (stopping reordering or cross-message splicing even without CID checks). No plaintext SHA-256 digest is published.

---

## 2. Threat Model & Operational Limits

Post-quantum hybrid encryption protects stored ciphertexts against a future quantum computer holding only public data. It does not make blockchain messaging anonymous, protect past history if a master seed leaks, or guarantee off-chain storage retention.

### What Observers Can See

| Mode & Anchor | On-Chain (`account_tx` / Block) | Off-Chain (IPFS Envelope) | Hidden From Non-Recipients |
| --- | --- | --- | --- |
| `PUBLIC` | Sender, payee, amount, fee, time, `76 B` memo, CID | Everything (plaintext body, header, sender pubkey) | Nothing (integrity only) |
| `PRIVATE` (`Alice → Bob`) | Sender, payee (`Bob`), amount, fee, time, CID | Cleartext `MessageHeader` (`sender_account`, `thread_id`, `reply_to_cid`, `schema_name`, timestamp), sender pubkey, `recipient_account` hints, reader count, approx. size | Plaintext body & chunk plaintexts |
| `SEALED` direct (`Charlie → Bob`, Block `1927`) | Sender, payee (`Bob`), amount, fee, time, CID | Cleartext `MessageHeader`, sender pubkey, **no** `recipient_account` strings, reader count, 32 B `recipient_key_id` tags | Plaintext body & explicit account strings *(payee is still public on L1)* |
| `SEALED` self-payment, hardened (`Charlie → Charlie`, Block `1933`) | Sender (`Charlie`), `to == Charlie` (no payee on L1), fee, time, `54 B` memo, CID | Cleartext `MessageHeader` (`thread_id` & `reply_to_cid` omitted), sender pubkey, **no** `recipient_account` strings, reader count, **blinded per-message 32 B recipient tags** (static `key_id` absent from wire), 32 B `cek_commitment` | Plaintext body, on-chain payee, thread linkage, **and** public key-directory correlation |

**Exact scope of hardened `SEALED` mode (`postfiatl1v2#316`):** Earlier `SEALED` envelopes placed the static 32-byte `SHA-256(xwing_pk)` in `RecipientWrap.recipient_key_id`, allowing anyone with a public key directory to link IPFS envelopes back to a recipient. `postfiatl1v2#316` replaces that static digest in `SEALED` mode with a per-message blinded tag derived from the fresh X-Wing shared secret (`SHA-256("postfiat-l1-v2/sealed-recipient-tag/v1\x00" || xwing_ss || aad_context)`), verified via recipient trial-decapsulation (`5.71 ms` p50 for a 2-reader envelope in JS). Even an observer holding every `MessageKeyBinding` and every `SEALED` IPFS block can no longer correlate wraps to public keys. Be clear about what *does* remain visible: the sender's address and ML-DSA-65 pubkey, timestamp, `schema_name`, reader count, and approximate ciphertext size—`SEALED` provides **recipient-private, sender-authenticated drops**, not full Tor/mixnet anonymity. Production `SEALED` senders must also omit `thread_id` and `reply_to_cid` from the cleartext header (as in Blocks `1931` and `1933`), placing thread pointers inside the encrypted body instead.

### Signature Scope, Anchor Binding & Cryptographic Caveats

- **Exact signed preimage (`envelope_signing_preimage`):**
  ```text
  "postfiat-l1-v2/message-envelope/v1" || 0x00 ||
  uint32_be(version) ||
  uint32_be(len(header_bytes)) || header_bytes ||
  uint32_be(len(encryption_header_bytes)) || encryption_header_bytes ||
  uint32_be(len(body_bytes)) || body_bytes
  ```
  Because `header_bytes` contains `MessageHeader`, the signature binds `chain_id`, `sender_account`, `created_at_unix_ms`, `visibility`, `schema_name`, `thread_id`, and `reply_to_cid` across all visibilities, including `PUBLIC`.
- **Disjoint domain separation:** One ML-DSA-65 account keypair signs L1 transactions (FIPS 204 context `postfiat-l1-v2/tx/v1`), envelopes (prefix `postfiat-l1-v2/message-envelope/v1`), and key bindings (prefix `postfiat-l1-v2/message-key-bind/v1`). Signatures cannot cross domains.
- **Why ML-DSA-65 only (not hybrid) for signatures:** Post Fiat L1v2 account ownership is already pure ML-DSA-65. A break in ML-DSA-65 compromises L1 account control directly, so a second classical message-signing key would not save account identity, whereas hybrid X-Wing protects stored ciphertext confidentiality independently of L1 signing.
- **Anchor binding inside `open_envelope()` / `openEnvelope()` (`postfiatl1v2#310`):** Because the CID must be computed offline before submitting the transaction, `tx_id` and block height cannot sit inside the signed preimage. Both SDKs therefore enforce three binding checks directly inside `open_envelope()` / `openEnvelope()`:
  1. `derive_account_address(envelope.sender_pubkey) == header.sender_account` via `"pf" || hex(SHA3-384("postfiat.address.v1\x00" || sender_pubkey)[:20])` (**enabled by default**);
  2. `header.chain_id == expected_chain_id` (stops cross-chain replay); and
  3. `header.sender_account == expected_tx_sender` (stops third-party CID re-anchoring; same-chain duplicate self-anchors deduplicate at the application layer on `(cid, sender_account)`).
- **Key-committing AEAD (`cek_commitment`, `postfiatl1v2#316`):** Standard XChaCha20-Poly1305 is not key-committing, which would otherwise let a malicious multi-recipient sender wrap different CEKs to different readers of the same ciphertext. `XWingEncryptionHeader` field `7` (`cek_commitment`, 32 bytes, covered by the ML-DSA-65 envelope signature) commits to `SHA-256("postfiat-l1-v2/cek-commit/v1\x00" || cek || aad_context)`. Both Python and JS `open_envelope()` / `openEnvelope()` verify `cek_commitment` in constant time *before* decrypting the body, closing key-substitution attacks for 34 bytes on the wire.
- **Intentional non-repudiation (verifiable records, not Signal chat):** ML-DSA-65 envelope signatures are **non-repudiable**—and any L1-anchored transaction is already ML-DSA-65 signed by the sender anyway. That is the exact property required for Task Node reward receipts, governance disclosure packets, NFT metadata provenance, and auditable AI-agent x402 workflows. Conversely, non-repudiation is a privacy anti-feature for casual 1-to-1 chat: **do not use L1-anchored `pf.message.v1` envelopes where Signal-style deniable authentication is required.** Deniable interactive 1-to-1 chat belongs in an off-chain PQXDH + Double-Ratchet session layer, not archival on-chain envelopes.

### Rotatable Forward-Secret Keys, Anti-Downgrade & IPFS Availability

- **Separating Day-0 bootstrap (`epoch 0`) from rotatable forward-secret keys (`epoch >= 1`, `postfiatl1v2#316`):** New users start with `0 PFT` and cannot mint an on-chain identity before receiving their first payout, so `epoch 0` derives a bootstrap X-Wing key from the wallet seed (`postfiat-l1-v2/message-key/v1`) solely for Day-0 onboarding. Because a leaked wallet seed would otherwise retroactively decrypt all history, `postfiatl1v2#316` ships **CSPRNG non-seed rotatable X-Wing keys** (`generate_rotatable_xwing_seed()` / `rotate_message_key_binding()` at `epoch >= 1`) alongside **monotonic `min_known_epoch` verification** in `verify_message_key_binding()`. Once rotated to `epoch >= 1`, a compromised master seed can no longer decrypt rotated traffic (verified live on Block `1933`), deleting retired epoch private keys provides epoch-level forward secrecy, and Task Node cannot silently downgrade a peer back to `epoch 0`. Wallets can also exchange and verify signed `MessageKeyBinding` records peer-to-peer without Task Node until Pillar 6 on-chain `identity_set` (`postfiatl1v2#307`) deploys. Task Node is included as a reader only on Task Node lifecycle and reward schemas, never on user-to-user messages.
- **Recipient discovery tradeoffs:** Non-payee recipients of group or self-payment `SEALED` messages will not find the anchor transaction in their own `account_tx`. Each discovery channel trades convenience against metadata:

| Discovery Path | How It Works | What Infrastructure Sees |
| --- | --- | --- |
| Sender-indexed polling | Poll known senders' `account_tx` and match `recipient_key_id` (Block `1931`) | RPC node sees which sender addresses you watch (mitigated by a local node) |
| Off-chain relay hint | Relay (`ops/nostr-relay/`) or app pushes `(tx_id, cid)`; client verifies on L1 | Relay learns push timing and subscriber graph (cannot forge or decrypt) |
| Opt-in `key_id` indexer | Indexer fetches off-chain envelopes linked by `pf.ptr` v5 pointers and indexes `recipient_key_id` wraps | Indexer learns subscriber `key_id` watchlists and query timing |

- **IPFS pinning:** On-chain pointers prove existence, order, and integrity, not permanent hosting. Task Node pins Task Node traffic, governance packets, and Post Fiat NFT metadata via an async durable retry outbox; third-party apps pin their own blocks or pay a pinning provider. If all off-chain copies vanish, the pointer remains valid on L1 but the message body is unrecoverable.

---

## 3. Live Devnet-2 Integration Test (Blocks 1923–1931)

To exercise the wire protocol against live BFT consensus, we ran **nine `payment_v2` transactions** across four funded wallets on our 6-validator `postfiat-wan-devnet-2` network on **27 November 2026**, using the hardened Python codec (`postfiatl1v2#310`) paired with pure-Python reference crypto (`kyber-py==1.2.0` `ML_KEM_768`, `dilithium-py==1.5.1` `ML_DSA_65`, `cryptography` `X25519`, `pycryptodome` 24-byte-nonce `ChaCha20_Poly1305`). Those Python crypto packages are **not constant-time** and serve strictly as an integration-test backend; production browser and desktop wallets use Rust/WASM (`crates/wallet_wasm`, merged in [`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303)) and native Rust (`tasknode-apple`, merged in [`tasknode-apple#40`](https://github.com/postfiatorg/tasknode-apple/pull/40)).

Every full 96-character SHA3-384 `tx_id`, full CID, chunk CID, genesis hash, state root (`c2cb2472…81abfe09a` at height `1931`, 6/6 validators converged, zero pending mempool), and negative-control error string is published verbatim in [`devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json).

### Wallet Reconciliation (Exact to the Atom)

| Wallet | Address (prefix) | Initial | Final (Seq) |
| --- | --- | ---: | ---: |
| Alice | `pf6d2d0a…78c788c9` | `200,000` | `199,711` (`seq 4`) |
| Bob | `pf721bb3…4a72c797a` | `200,000` | `200,378` (`seq 1`) |
| Charlie | `pfef21b4…8af86a091` | `200,000` | `199,712` (`seq 4`) |
| Eve *(outsider)* | `pf31e18f…ebaac093a` | `200,000` | `200,000` (`seq 0`) |

Total starting balance `800,000 atoms` → final `799,801 atoms`: **`199 atoms`** burned across nine transactions (`8 × 22 atoms` for `54–76 B` memos + `1 × 23 atoms` for Block `1929`'s `100 B` multipart memo). Every `100`-atom attached transfer conserved across wallets, and both self-payments (Blocks `1930` and `1931`) deducted only the `22`-atom fee each.

### Nine Live Transactions (Blocks 1923–1931)

| Block | Flow & Anchor | `tx_id` (prefix) | Measured Size | Result |
| ---: | --- | --- | --- | --- |
| `1923` | `PRIVATE` 1-to-1 (`Alice → Bob`) | `c8b7f540…0ace3f2` | `8,162 B` env · `76 B` memo | Bob & Alice sender-copy decrypted; Eve had no wrap |
| `1924` | `PRIVATE` group (`Alice → [Bob, Charlie]`, anchor `Bob`) | `1484c78c…e212791` | `9,539 B` env · 3 wraps | Bob & Charlie decrypted identically; Eve rejected |
| `1925` | `PRIVATE` thread reply #1 (`Bob → [Alice, Charlie]`) | `253342e9…0a4e85b` | `reply_to_cid` → Block `1924` | Alice decrypted & verified Bob's ML-DSA-65 sig |
| `1926` | `PRIVATE` thread reply #2 (`Charlie → [Alice, Bob]`) | `0483906c…bf2452ea` | `reply_to_cid` → Block `1925` | Alice & Bob decrypted; 3 distinct senders verified |
| `1927` | `SEALED` direct (`Charlie → Bob`, exposes payee on L1) | `4a999c08…96f808` | `8,075 B` env | No `recipient_account` in header; Bob decrypted; Eve rejected |
| `1928` | `PUBLIC` signed (`Alice → Bob`, unencrypted) | `c57ead30…ea963c3` | `5,488 B` env | Read & ML-DSA-65 verified by Eve |
| `1929` | `PRIVATE` 320 KiB 3-chunk `Manifest` (`Alice → [Bob, Charlie]`) | `697117e6…5055444` | `9,832 B` env · `100 B` memo | `327,680 B` chunked at `128 KiB` (`128+128+64`) to exercise multi-chunk path; reassembled byte-for-byte (`SHA-256 b7c24200…`) |
| `1930` | `SEALED` self-payment, threaded (`Charlie → Charlie`) | `6fa3b8e1…05fc4f0` | `8,077 B` env · `76 B` memo | Initial self-payment test (reused test `thread_id`; superseded by `1931`) |
| `1931` | `SEALED` self-payment, pre-blinding (`Charlie → Charlie`, `thread_id=""`) | `0644e520…31e46cbe` | `8,047 B` env · `54 B` memo | `from == to == Charlie`; zero `thread_id`/`recipient_account`; verified backward-compatible decode |
| **`1932`** | **x402 `INLINE` consensus payment (`Alice → Bob`, `GET /api/v1/signal`)** | `58e0b81c…5a5b4` | `51 B` memo (`INLINE` req hash) | Verified 6/6 + full HTTP `402 → 200` + 3 replay defenses (`400`, `400`, `409`) |
| **`1933`** | **Hardened blinded `SEALED` + `cek_commitment` + rotated `epoch 1` (`Charlie → Charlie`)** | `1b18d35a…c09e319` | `8,100 B` env · `54 B` memo | Static `key_id`s absent from wire; `32 B` `cek_commitment` verified; Bob's rotated `epoch 1` key decrypted; **Bob's `epoch 0` seed key & Eve both rejected**; `epoch 0` rollback rejected (`min_known_epoch=1`) |

### Fourteen SDK-Enforced Negative & Replay Controls (`postfiatl1v2#310` & `#316`)

Every negative control below ran directly inside the shipped Python and JavaScript SDKs (`python/tests/test_message_protocol.py` + `wallet-proxy/test_message_protocol.js` against `@noble/post-quantum`):

| Attack Tested | SDK Entry Point | Observed Error |
| --- | --- | --- |
| 1-bit signature flip *(omitting `expected_multibase_cid` to isolate signature verification)* | `open_envelope()` | `Envelope raw-byte signature verification failed` |
| 1-bit raw block tamper vs. expected CID | `open_envelope()` | `IPFS CIDv1 raw multibase mismatch` |
| Cross-chain replay (`wrong chain_id`: devnet-2 vs. mainnet-1) | `open_envelope()` | `Envelope chain_id mismatch` |
| Foreign-sender CID re-anchoring (Alice's CID under Eve's `tx.from`) | `open_envelope()` | `Foreign re-anchor rejected` |
| Spoofed `sender_account` in header (Eve signs claiming Alice's address) | `open_envelope()` *(default on)* | `Envelope sender_pubkey address != header.sender_account` |
| Multi-recipient wrong-CEK substitution (`#316`) | `open_envelope()` / `openEnvelope()` | `XWingEncryptionHeader.cek_commitment mismatch` |
| Key-epoch downgrade rollback (`epoch 0 < min_known_epoch 1`, `#316`) | `verify_message_key_binding()` | `MessageKeyBinding key_epoch rollback rejected` |
| Leaked `epoch 0` seed key against rotated `epoch 1` blinded `SEALED` (Block `1933`) | `open_envelope()` | `no matching RecipientWrap for recipient_key_id` |
| Chunk reorder (`[1, 0, 2]` on Block `1929` manifest) | `reassemble_manifest_chunks()` | `IPFS CIDv1 raw binary digest mismatch` |
| Chunk truncation (`[0, 1]` on Block `1929` manifest) | `reassemble_manifest_chunks()` | `block count does not match manifest.chunks length` |
| Chunk-index AAD splice (chunk 1 under slot 0 AAD, bypassing CID) | `xchacha20_poly1305_decrypt()` | `XChaCha20-Poly1305 authentication failed` |
| 1-bit ciphertext tamper on chunk 1 (bypassing CID) | `xchacha20_poly1305_decrypt()` | `XChaCha20-Poly1305 authentication failed` |
| x402 exact header replay / fresh-nonce swap / `SpentStore` replay (Block `1932`) | `createX402Gate()` / `settlePayment()` | `400 unknown_challenge_nonce` · `400 order_nonce_mismatch` · `409 payment_already_spent` |

### Measured Crypto, Interop & Adversarial Benchmarks (`Node.js v20.20.2`, `linux/x64`)

Beyond the 11-transaction devnet-2 run, we benchmarked the real JavaScript `@noble/post-quantum` SDK and x402 facilitator HTTP server, and verified live cross-language JS → Python interop (a blinded `SEALED` envelope with `cek_commitment` sealed in JS and verified/decrypted in Python with FIPS 204 `ML_DSA_65.verify`, `enforce_canonical_order=True`, `require_cek_commitment=True`):

| Operation (`Node.js v20.20.2`, `@noble/post-quantum`) | Samples | p50 | p95 | Throughput |
| --- | ---: | ---: | ---: | ---: |
| `ML-DSA-65` sign / verify | `40` | `7.69 ms` / `2.04 ms` | `21.85 ms` / `2.88 ms` | `100.0` / `467.5 ops/s` |
| `X-Wing` encap / decap | `40` | `2.41 ms` / `2.69 ms` | `4.09 ms` / `4.69 ms` | `387.0` / `353.7 ops/s` |
| `PRIVATE` 1-reader `sealEnvelope` / `openEnvelope` | `20` | `13.69 ms` / `4.96 ms` | `23.15 ms` / `6.50 ms` | `77.2` / `194.9 ops/s` |
| `PRIVATE` 10-reader `sealEnvelope` / `openEnvelope` | `20` | `31.88 ms` / `5.58 ms` | `62.07 ms` / `6.28 ms` | `28.5` / `177.6 ops/s` |
| Blinded `SEALED` 2-reader `sealEnvelope` / trial-decap `openEnvelope` | `20` | `10.93 ms` / `5.71 ms` | `50.52 ms` / `11.28 ms` | `70.4` / `153.7 ops/s` |
| `320 KiB` 3-chunk `Manifest` split / reassemble | `15` | `3.35 ms` / `3.48 ms` | `6.38 ms` / `4.56 ms` | `265.0` / `277.9 ops/s` |
| x402 HTTP `402 → FastPay ML-DSA sign → 2-of-3 quorum → 200` | `30` | `42.45 ms` | `65.01 ms` | `23.4 calls/s` *(single-thread)* |
| **Adversarial concurrent replay storm (`200` simultaneous replays)** | `200` | `261.95 ms` total | — | **`763.5 rejected/s` (`200/200` blocked)** |

### Verifying an Anchored Envelope With the Public SDK

Any developer cloning [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) can verify and decrypt an anchored envelope directly with the merged Python SDK (`python/postfiat_rpc/message_protocol.py`):

```python
from postfiat_rpc.message_protocol import open_envelope, decode_pointer_v5_memo

# 1. Decode the pf.ptr v5 memo from a finalized account_tx row
ptr = decode_pointer_v5_memo(tx_row["memos"][0], enforce_canonical_order=True)
envelope_bytes = fetch_ipfs_block(ptr.cid_bin)

# 2. Verify CID, ML-DSA-65 raw-byte signature, sender_pubkey -> sender_account,
#    chain_id, and anchoring tx.from in one call, then decrypt via X-Wing
opened = open_envelope(
    envelope_bytes,
    verify_signature_fn=mldsa65_verify,
    expected_cid_bin=ptr.cid_bin,
    expected_chain_id="postfiat-wan-devnet-2",
    expected_tx_sender=tx_row["from"],
    recipient_key_id=my_xwing_key_id,
    xwing_decap_fn=my_xwing_decap,
    enforce_canonical_order=True,
)
```

---

## 4. FastPay, Production Wallets & Live x402 Agent Payments (Shipped on `main`)

The exact `pf.ptr` v5 wire format verified in Blocks `1923–1931` now ships across the full Pillar 2 stack on `main`:

- **Production Rust/WASM & native Mac wallet clients:** [`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303) ships `crates/wallet_wasm` with unified v2 BIP-39 KDF, envelope raw-byte signing, X-Wing KEM key seed derivation, and FastPay v3 (`OwnedTransferOrderV3` / `OwnedUnwrapOrderV3`) signing; [`tasknode-apple#40`](https://github.com/postfiatorg/tasknode-apple/pull/40) (including [`#41`](https://github.com/postfiatorg/tasknode-apple/pull/41)) ships native Mac `V2MessagesView.swift` and one-click FastPay → `PFSH03` *Make private*.
- **L1 FastPay fee discipline, `order_hash` indexing & Task Node payout cutover:** [`postfiatl1v2#295`](https://github.com/postfiatorg/postfiatl1v2/pull/295) enforces Sui-inspired FastPay computation + new-object fees (`25 + ceil(tx_bytes / 512) + max(0, outputs - inputs) * 1,000 + inputs` atoms), raises the owned-object cap, and indexes FastPay transfers and unwraps into `account_tx` / `tx` keyed by immutable `order_hash` (never malleable validator certificate digests). [`tasknode#450`](https://github.com/postfiatorg/tasknode/pull/450) (including [`#454`](https://github.com/postfiatorg/tasknode/pull/454)) ships the crash-safe Task Node FastPay reward payout driver with locked multi-object leasing, durable `order_hash` recovery, and async IPFS pinning.
- **x402 v2 agent payments + live Block `1932` verification:** [`postfiatl1v2#289`](https://github.com/postfiatorg/postfiatl1v2/pull/289) and [`postfiatl1v2#312`](https://github.com/postfiatorg/postfiatl1v2/pull/312) ship the x402 v2 facilitator, MCP payment wrapper (`X402HttpClient`), and live JSON-RPC settlement adapter (`tools/x402-facilitator/chain-adapter.js`) supporting both FastPay v3 (`owned_sign_v3` / `owned_apply_v3`) and consensus lanes. On **Block `1932`** of `postfiat-wan-devnet-2`, we anchored a live `100`-atom `payment_v2` transfer (`Alice → Bob`, `22`-atom fee burned, `tx_id 58e0b81c…5a5b4`, verified 6/6 across all validators) carrying the `51 B` `pf.ptr` v5 `INLINE` SHA-256 request hash (`a2dcbd98…47acaff`) for `GET /api/v1/signal` and verified the complete HTTP gate loop:

| Step | HTTP / Facilitator Action | Observed Result |
| --- | --- | --- |
| **1. Unauthenticated request** | `GET /api/v1/signal` | `402 Payment Required` (`259 B` `PAYMENT-REQUIRED` protobuf header) |
| **2. Paid retry (`X402HttpClient`)** | `GET /api/v1/signal` + `PAYMENT-SIGNATURE` | `200 OK` + `PAYMENT-RESPONSE` (`settled: true`, `finalized_height: 1932`, `100 atoms`) |
| **3a. Exact header replay** | Re-send captured `PAYMENT-SIGNATURE` | `400 unknown_challenge_nonce` (one-time challenge consumed) |
| **3b. Fresh-challenge nonce swap** | Re-wrap same signed tx under new `402` nonce | `400 order_nonce_mismatch` (signed transfer bound to original challenge) |
| **3c. Direct `SpentStore` replay** | Re-submit captured `PAYMENT-SIGNATURE` to facilitator core | `409 payment_already_spent` (deduplicated by immutable tx digest) |

Full protobuf schemas, domain-separation constants, and x402 header formats live in the [Post-Quantum Message Protocol Technical Guide](/docs/message-protocol/) and [`docs/specs/message-protocol-v1.md`](https://github.com/postfiatorg/postfiatl1v2/blob/main/docs/specs/message-protocol-v1.md). All 10 live devnet-2 transactions (Blocks `1923–1932`) and 12 negative/replay controls are recorded verbatim in [`devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json).
