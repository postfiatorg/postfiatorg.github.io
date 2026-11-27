---
title: "Post-Quantum Messaging on Post Fiat L1v2: Wire Format, Threat Model & Live Devnet-2 Verification"
date: 2026-11-27T00:00:00Z
draft: false
summary: "Canonical protobuf wire format (postfiat.message.v1, pf.ptr v5), hybrid X-Wing encryption, FIPS 204 ML-DSA-65 raw-byte signing, explicit metadata threat model, and a 9-transaction live devnet-2 verification across Blocks 1923–1931."
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

Post Fiat L1v2 is a post-quantum Layer-1 blockchain where wallets, validators, and AI agents attach structured messages—task instructions, reward receipts, governance disclosures, and API settlement proofs—to payments. Rather than bloating consensus blocks with kilobytes of encrypted text, every message splits into two parts: a compact pointer (`54–100 B`) embedded in a normal transaction memo, and a signed, optionally encrypted content-addressed payload stored off-chain as an IPFS CIDv1 `raw` block.

**What is proven today vs. what remains open:** The canonical protobuf wire specification ([`postfiatl1v2#288`](https://github.com/postfiatorg/postfiatl1v2/pull/288)), Python and JavaScript codecs ([`postfiatl1v2#289`](https://github.com/postfiatorg/postfiatl1v2/pull/289)), and block-explorer decoding views ([`postfiatorg.github.io#56`](https://github.com/postfiatorg/postfiatorg.github.io/pull/56)) are merged on `main`, with sender-address derivation and L1 anchor-binding checks promoted directly into both SDKs' `open_envelope()` / `openEnvelope()` functions in [`postfiatl1v2#310`](https://github.com/postfiatorg/postfiatl1v2/pull/310). We executed **nine live `payment_v2` transactions** on our 6-validator `postfiat-wan-devnet-2` network (Blocks `1923–1931`) plus **nine SDK-enforced negative controls**, published verbatim at [`devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json). Three concrete boundaries remain: the live devnet harness pairs the Python codec with pure-Python reference crypto (`kyber-py==1.2.0`, `dilithium-py==1.5.1`, `pycryptodome`, `cryptography`) rather than constant-time production Rust/WASM (`crates/wallet_wasm`, [`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303)); seed-derived bootstrap encryption keys trade away incoming forward secrecy; and `SEALED` mode hides on-chain payees when self-anchored but remains linkable whenever recipient key bindings are public.

<div class="glance">
  <div><b>9 Live Devnet-2 Txs</b><span>Blocks 1923–1931 · 8 encrypted + 1 public · 6/6 validator consensus</span></div>
  <div><b>X-Wing + ML-DSA-65</b><span>ML-KEM-768 + X25519 hybrid KEM · FIPS 204 raw-byte signatures</span></div>
  <div><b>54–100 B On-Chain</b><span>pf.ptr v5 CIDv1 raw pointer · 5.5–9.8 KB off-chain envelopes</span></div>
  <div><b>9 / 9 SDK Controls</b><span>Tamper, chunk, replay &amp; re-anchor checks inside open_envelope()</span></div>
</div>

On Post Fiat's legacy XRPL-derived chain, `pf.ptr` v4 pointers were hand-encoded across three languages without a shared schema, used uppercase hex (rejected by `postfiatl1v2`), encrypted payloads with classical X25519 only, omitted a sender signature over the full envelope, published plaintext SHA-256 hashes, and included the Task Node server as a default reader. `postfiat.message.v1` replaces that layer with one cross-language protocol.

---

## 1. Wire Format & Cryptographic Construction

Every message—1-to-1 private chat, multi-recipient group dispatch, sealed drop, public announcement, or multi-chunk attachment—passes through one pipeline:

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

### Canonical Protobufs, Raw-Byte Signing & `pf.ptr` v5 Memos

1. **One `.proto` source of truth (`proto/postfiat/message/v1/message.proto`):** `Pointer`, `Envelope`, `MessageHeader`, `XWingEncryptionHeader`, `RecipientWrap`, `Manifest`, `MessageKeyBinding`, `TextMessage`, and `X402PaymentPayload` are defined once in `postfiat.message.v1`, alongside sibling governance (`postfiat.governance.v1`) and NFT (`postfiat.nft.v1`) schemas. Python (`python/postfiat_rpc/message_protocol.py`) and JavaScript (`wallet-proxy/message-protocol.js`) codecs pass shared cross-language byte vectors (`scripts/test-message-protocol-vectors.py`), including 48-byte SHA3-384 transaction digests. Third-party apps can define custom schemas permissionlessly using `schema_id = 1` with a full `schema_name` string.
2. **Zero re-serialization verification:** Protobuf encoders in different languages can legitimately emit fields in different orders or omit default values, breaking naive "decode → re-encode → verify" schemes. `Envelope` stores `header_bytes`, `encryption_header_bytes`, and `body_bytes` as opaque raw byte fields. Verifiers check the 36-byte CIDv1 `raw` hash and the FIPS 204 ML-DSA-65 signature over those exact transmitted bytes *before* decoding any nested protobuf field.
3. **Compact on-chain `pf.ptr` v5 memos (`<= 256 B`):** Consensus enforces `<= 4` memos per transaction, `<= 256` decoded bytes per memo, `<= 512` total decoded memo bytes, and lowercase hex only. A `pf.ptr` v5 memo sets `memo_type` to `"pf.ptr"` (`70662e707472`, 6 B), `memo_format` to `"v5"` (`7635`, 2 B), and `memo_data` to lowercase-hex protobuf `Pointer` bytes carrying the 36-byte binary CIDv1 `raw` prefix (`0x01 0x55 0x12 0x20 || sha256`) or compact inline bytes. Live on devnet-2, a `SEALED` pointer with no thread ID occupies `46 B` of `memo_data` (`54 B` total), a threaded pointer occupies `68 B` (`76 B` total), and a multipart manifest pointer occupies `92 B` (`100 B` total). Pure messages with no external value transfer anchor as standard self-payments (`from == to`).

### Hybrid Encryption: X-Wing + XChaCha20-Poly1305

Private and sealed envelopes encrypt the body once under a fresh random 32-byte Content Encryption Key (CEK) with XChaCha20-Poly1305, and wrap that CEK per recipient using **X-Wing** (`draft-connolly-cfrg-xwing-kem`, combining FIPS 203 ML-KEM-768 and X25519 via SHA3-256):

| Component | Wire Size | Specification |
| --- | ---: | --- |
| ML-DSA-65 auth (per envelope) | `5,261 B` | `1,952 B` public key + `3,309 B` signature (FIPS 204) |
| X-Wing public key | `1,216 B` | `1,184 B` ML-KEM-768 encapsulation key `\|\|` `32 B` X25519 public key |
| X-Wing ciphertext (per reader) | `1,120 B` | `1,088 B` ML-KEM-768 ciphertext `\|\|` `32 B` X25519 ephemeral key |
| Shared secret combiner | `32 B` | `SHA3-256(ss_MLKEM \|\| ss_X25519 \|\| ct_X25519 \|\| pk_X25519 \|\| 0x5c2e2f2f5e5c)` |
| Wrapped CEK | `48 B` | `32 B` CEK encrypted under HKDF-SHA256 KEK + `16 B` Poly1305 tag (`24 B` nonce) |
| Recipient `key_id` tag | `32 B` | `SHA-256` fingerprint of the recipient's `1,216 B` X-Wing public key |
| AEAD context (`aad_context`) | `32 B` | `SHA-256("postfiat-l1-v2/message-aad/v1" \|\| 0x00 \|\| chain_id \|\| 0x00 \|\| SHA-256(header_bytes) \|\| uint32_be(chunk_index))` |

**Measured off-chain PQ overhead:** Post-quantum envelopes are large off-chain. Measured on our live devnet-2 short text messages:
- `PUBLIC` (0 wraps, Block `1928`): `5,488 B` (dominated by the `5,261 B` ML-DSA-65 pubkey + signature).
- `SEALED` clean self-payment (2 wraps, no `recipient_account` strings, no `thread_id`, Block `1931`): `8,047 B` (`8,075–8,077 B` when carrying a 20-byte `thread_id`). Each `RecipientWrap` without an account string contributes `1,237 B` (`1,120 B` X-Wing ciphertext + `48 B` wrapped CEK + `32 B` `key_id` + `24 B` wrap nonce + `13 B` protobuf field tags), plus `~110 B` for `XWingEncryptionHeader` framing (`32 B` `aad_context`, `24 B` body nonce, `28 B` `kdf_info`, `16 B` body Poly1305 tag, and tags).
- `PRIVATE` 1-to-1 (2 wraps with two `42 B` `recipient_account` strings, Block `1923`): `8,162 B` (`+87 B` over `SEALED` direct `8,075 B`, matching two `42 B` account strings plus protobuf tags).
- `PRIVATE` group (3 wraps + `reply_to_cid` in `MessageHeader`, Block `1924`): `9,539 B` (`+1,377 B` over Block `1923`: `1,281 B` for the 3rd wrap with account string plus `96 B` for `reply_to_cid` and text length delta).

**Multi-chunk encrypted `Manifest` (up to 16 MiB):** Payloads above the 1 MiB single-envelope cap split into ordered encrypted chunks (e.g., 128 KiB) encrypted under the envelope's CEK with fresh 24-byte nonces. The signed `Manifest` commits to the ordered chunk CIDs, per-chunk byte lengths, and `total_plaintext_bytes` (preventing truncation), while `compute_aad_context` binds every chunk's Poly1305 tag to its `uint32_be(chunk_index)`, `chain_id`, and `SHA-256(header_bytes)` (preventing reordering or cross-message splicing even without CID checks). No plaintext SHA-256 digest is published.

---

## 2. Threat Model, Metadata Limits & Operational Boundaries

X-Wing protects recorded ciphertexts against a future quantum attacker holding only public data. It does not conceal on-chain metadata, protect past messages if a user's master seed leaks, or guarantee off-chain storage retention.

### What Observers Learn by Visibility Mode

| Mode & Anchor | On-Chain (`account_tx` / Block) Observer Sees | Off-Chain (IPFS Block) Observer Sees | Hidden From Non-Recipients |
| --- | --- | --- | --- |
| `PUBLIC` | Sender, destination, amount, fee, timing, memo size (`76 B`), CID | Everything (plaintext body, header, sender pubkey) | Nothing (integrity only) |
| `PRIVATE` (direct `Alice → Bob`) | Sender, destination (`Bob`), amount, fee, timing, CID | Cleartext `MessageHeader` (`sender_account`, `thread_id`, `reply_to_cid`, `schema_name`, `created_at_unix_ms`), sender pubkey, explicit `recipient_account` hints, reader count, approximate body length | Plaintext body and chunk plaintexts |
| `SEALED` direct (`Charlie → Bob`, Block `1927`) | Sender, destination (`Bob`), amount, fee, timing, CID | Cleartext `MessageHeader` fields above, sender pubkey, no `recipient_account` strings, reader count, 32 B `recipient_key_id` tags, approximate body length | Plaintext body and explicit account strings in IPFS header *(destination is still public on-chain)* |
| `SEALED` self-payment (`Charlie → Charlie`, Block `1931`) | Sender (`Charlie`), `to == Charlie` (no recipient address on-chain), fee, timing, `54 B` memo, CID | Cleartext `MessageHeader` (`sender_account`, `schema_name`, `created_at_unix_ms`; `thread_id` & `reply_to_cid` omitted), sender pubkey, no `recipient_account` strings, reader count, 32 B `recipient_key_id` tags | Plaintext body, on-chain recipient address, and thread linkage |

**What `SEALED` does and does not hide:** When a recipient's `MessageKeyBinding` (`account ↔ xwing_public_key ↔ key_id`) is published in a public directory or on-chain identity record, `SEALED` does **not** deliver unlinkable anonymity. The sender is always in cleartext, and joining the key directory against IPFS envelopes links the static 32-byte `recipient_key_id` back to the recipient. Self-anchored `SEALED` keeps the recipient's address off L1 and omits explicit account strings from IPFS blocks—blocking casual ledger scraping, not a determined metadata analyst. Because `Envelope.header_bytes` is authenticated-but-unencrypted, production `SEALED` senders must also omit or randomize `thread_id` and `reply_to_cid` (as demonstrated in Block `1931`), placing thread references inside the encrypted body instead.

### Signature Scope, Anchor Binding & Key Distribution

- **Exact signed preimage (`envelope_signing_preimage`):**
  ```text
  "postfiat-l1-v2/message-envelope/v1" || 0x00 ||
  uint32_be(version) ||
  uint32_be(len(header_bytes)) || header_bytes ||
  uint32_be(len(encryption_header_bytes)) || encryption_header_bytes ||
  uint32_be(len(body_bytes)) || body_bytes
  ```
  Because `header_bytes` encodes `MessageHeader`, the ML-DSA-65 signature covers `chain_id`, `sender_account`, `created_at_unix_ms`, `visibility`, `schema_name`, `thread_id`, and `reply_to_cid` on all visibilities including `PUBLIC`.
- **Disjoint domain separation:** Although a wallet reuses its ML-DSA-65 account keypair across L1 transactions, envelopes, and key bindings, each uses a disjoint domain separator: FIPS 204 context `postfiat-l1-v2/tx/v1` for L1 transactions, prefix `postfiat-l1-v2/message-envelope/v1` for envelopes, and prefix `postfiat-l1-v2/message-key-bind/v1` for `MessageKeyBinding`.
- **Why signatures are ML-DSA-65 only while encryption is hybrid X-Wing:** Post Fiat L1v2 account ownership is natively ML-DSA-65. A break in ML-DSA-65 already compromises L1 account ownership directly, so adding a classical message-signature keypair would not protect account identity, whereas hybrid X-Wing protects stored ciphertext confidentiality independently of L1 signing.
- **Anchor-binding checks enforced inside `open_envelope()` / `openEnvelope()` (`postfiatl1v2#310`):** Because the CID is computed offline before creating the anchoring transaction, `tx_id` and block height are not inside the signed preimage. To prevent cross-chain replay, header spoofing, and foreign CID re-anchoring, both SDKs (`python/postfiat_rpc/message_protocol.py` and `wallet-proxy/message-protocol.js`) enforce three checks directly inside `open_envelope()` / `openEnvelope()`:
  1. `derive_account_address(envelope.sender_pubkey) == header.sender_account` using `"pf" || hex(SHA3-384("postfiat.address.v1\x00" || sender_pubkey)[:20])` (**on by default** via `verify_sender_address=True` / `verifySenderAddress=true`);
  2. `header.chain_id == expected_chain_id` when `expected_chain_id` is passed; and
  3. `header.sender_account == expected_tx_sender` when `expected_tx_sender` (`anchoring_tx.from`) is passed (blocking third-party CID re-anchoring; repeated self-anchors deduplicate on `(cid, sender_account)`).
- **Key-binding distribution for unfunded (`0 PFT`) wallets:** Onboarding wallets sign a `MessageKeyBinding` with their ML-DSA-65 account key and upload it to Task Node's onboarding registry. Verifiers check `derive_account_address(account_pubkey) == account`, `key_id == SHA-256(xwing_public_key)`, and the ML-DSA-65 signature, so Task Node cannot forge a binding for an address it does not control. Until the user funds the account and publishes an on-chain identity record, however, Task Node controls directory availability and could withhold a binding or serve a stale `key_epoch`; once published on-chain, the on-chain identity record is authoritative.

### Forward-Secrecy Tradeoff, Discovery & IPFS Availability

- **Forward secrecy vs. single-seed recovery:** The bootstrap X-Wing keypair derives deterministically from the wallet master seed (`HKDF-SHA256`, domain `postfiat-l1-v2/message-key/v1`) so `0 PFT` wallets can receive encrypted first payouts and recover history from one seed phrase. This explicitly sacrifices **incoming forward secrecy**: compromising the master seed or long-term decapsulation key retroactively decrypts every past ciphertext encrypted to that key—a more immediate threat today than quantum cryptanalysis. `MessageKeyBinding.key_epoch` supports rotating to non-seed-derived keys once funded (protecting *future* messages), though automated rotation/revocation UX remains wallet-level rollout work. Task Node is a reader only on Task Node lifecycle/reward schemas, never on user-to-user messages.
- **Recipient discovery tradeoffs:** Non-payee recipients of group (`Alice → [Bob, Charlie]`) or self-payment `SEALED` messages will not find the anchor transaction in their own `account_tx`. Each discovery channel carries a metadata tradeoff:

| Discovery Path | Mechanism | Metadata Exposed to Infrastructure | Best Fit |
| --- | --- | --- | --- |
| Sender-indexed polling | Poll known senders' `account_tx` and match `recipient_key_id` (Block `1931`) | RPC node sees which senders a client watches (mitigated by running a local node) | Small groups or local-node users |
| Off-chain relay hint | Relay (`ops/nostr-relay/`) or app pushes `(tx_id, cid)`; client verifies on L1 | Relay learns push timing and subscriber graph (cannot forge or decrypt) | Interactive chat & Task Node alerts |
| Opt-in `key_id` indexer | Indexer scans `pf.ptr` v5 pointers for subscribed 32 B `key_id`s | Indexer learns subscriber `key_id` watchlists and query timing | Public/convenience inboxes |

- **IPFS pinning & retention:** An on-chain pointer guarantees existence, ordering, and tamper-evidence, not permanent data hosting. Task Node pins Task Node traffic, governance packets, and Post Fiat NFT metadata through an async durable retry outbox; third-party apps pin their own traffic or pay a pinning provider. If all off-chain copies of an unpinned block disappear, the on-chain pointer remains valid but the body is unrecoverable.

---

## 3. Live Devnet-2 Verification (Blocks 1923–1931)

We executed **nine live `payment_v2` transactions** on our 6-validator **`postfiat-wan-devnet-2`** network on **27 November 2026** using a standalone Python harness (`pf-message-test-env`) running the hardened `python/postfiat_rpc/message_protocol.py` codec (`postfiatl1v2#310`) paired with pure-Python reference crypto (`kyber-py==1.2.0` `ML_KEM_768`, `dilithium-py==1.5.1` `ML_DSA_65`, `cryptography` `X25519`, `pycryptodome` 24-byte-nonce `ChaCha20_Poly1305`). Those Python crypto packages are **not constant-time** and are used strictly for wire-format and devnet integration testing; production wallet crypto targets Rust/WASM (`crates/wallet_wasm`, `postfiatl1v2#303`).

Complete sanitized receipts (zero private keys) are published at [`/evidence/message-protocol/devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json).

### Chain Snapshot & Atom-Exact Reconciliation

- **Chain:** `postfiat-wan-devnet-2` (6/6 validators converged, `mempool_pending = [0, 0, 0, 0, 0, 0]`)
- **Genesis hash (48 B SHA3-384):** `ce22ca8c932da0998b484483a09647138a30e0bf44408dd49a8d6d452787ad25521aff3ed334da07e150a7233a3e90a9`
- **Final height `1931` tip:** `50bee456c3b4ec22e5aef08dd4d2840881473cd739959ab57d33815edd3a26b161eb289ef0663509f2702cedac895ab3`
- **Final state root:** `c2cb24725266f7ae5528d7057336f199a3fecdad835cf6157909885038be6f8b496be03d578e9920d484c8381abfe09a`

| Wallet | Address | Initial Atoms | Final Atoms (Seq) | 32 B X-Wing `key_id` (prefix) |
| --- | --- | ---: | ---: | --- |
| Alice | `pf6d2d0a000bb5c1feda7da2df955cfe0a78c788c9` | `200,000` | `199,711` (`seq 4`) | `ab3230536886467e…` |
| Bob | `pf721bb3b98bceeeebfb835d97dac6a7b4a72c797a` | `200,000` | `200,378` (`seq 1`) | `e5f40742cfcb516b…` |
| Charlie | `pfef21b496662a755d19c7c04fc37a8ed8af86a091` | `200,000` | `199,712` (`seq 4`) | `0971617dec92fd69…` |
| Eve *(outsider)* | `pf31e18f9533fc38839234a90aeb25629ebaac093a` | `200,000` | `200,000` (`seq 0`) | `16c7a1ebd8d24137…` |

Starting total `800,000 atoms` → final total `799,801 atoms`: exactly **`199 atoms`** burned across 9 transactions (`8 × 22 atoms` for `54–76 B` memos + `1 × 23 atoms` for Block `1929`'s `100 B` multipart memo). Every `100`-atom attached transfer conserved across wallets, and both self-payments (Blocks `1930` and `1931`) deducted only the `22`-atom fee each (`199,756 → 199,734 → 199,712`).

### Nine Live On-Chain Message Transactions (Blocks 1923–1931)

Each row below was signed by the sender's ML-DSA-65 key, anchored via `payment_v2` carrying a lowercase-hex `pf.ptr` v5 memo, finalized 6/6, fetched via `account_tx`, verified via `open_envelope()` (CID, ML-DSA-65 signature, `sender_pubkey` address, `chain_id`, and `tx.from`), and decrypted locally on the 8 encrypted rows:

| Block | Mode & Anchor | Full `tx_id` (48 B SHA3-384) | CIDv1 (`raw`) & Measured Size | Outcome |
| ---: | --- | --- | --- | --- |
| `1923` | `PRIVATE` 1-to-1 (`Alice → Bob`) | `c8b7f540228331c773f0be66d92bac47a4e34c91b75a0c2b43cac53052a561cd97afcbc62b69fb7c0a3a280760ace3f2` | `bafkreihx2tfnjrdfjk6w7fq5pmnauaamtqxzjlghnqtl5cjconrfniulnu` (`8,162 B` env · `76 B` memo) | Bob & Alice sender-copy decrypted; Eve had no matching wrap |
| `1924` | `PRIVATE` group (`Alice → [Bob, Charlie]`, anchor `Bob`) | `1484c78c9e02475ff867b3db9199b6a9671066bdb1d871a93cff64a60f92dcd0f093c709fa0b069340b9ac56fe212791` | `bafkreihdokv7wfjd6r5kyu7tf2itbij5ug4c5wt57ei2fuoqspuo77p7zq` (`9,539 B` env · 3 wraps) | Single ciphertext; Bob & Charlie decrypted identically; Eve rejected |
| `1925` | `PRIVATE` thread reply #1 (`Bob → [Alice, Charlie]`) | `253342e9861bf78a1ec1668870c62b7032ff27c2600f61c6987d50afa21eb484674095af11ea033f77c29804a0a4e85b` | `reply_to_cid` → Block `1924` CID *(receipt in JSON)* | Alice decrypted & verified Bob's ML-DSA-65 sig + reply link |
| `1926` | `PRIVATE` thread reply #2 (`Charlie → [Alice, Bob]`) | `0483906c1b57b5bc224d91985fcfe07bbe5ddf55ae5e80e6e8dc9a4bc20eaeb67b93a4b79beca33938fe399ebf2452ea` | `reply_to_cid` → Block `1925` CID *(receipt in JSON)* | Alice & Bob decrypted; 3 distinct ML-DSA-65 senders verified |
| `1927` | `SEALED` direct (`Charlie → Bob`, exposes payee on-chain) | `4a999c08f0be5bd9a8b280cea75f7a21d784746d2b856ade7eb3d393c3be98c194ff4800ea57544340beef331696f808` | `bafkreih5m3t44nh5kck6z4tfvxgboslafij73seqadfebd2ela6abg6gui` (`8,075 B` env) | Zero `recipient_account` strings in header; Bob decrypted by `key_id`; Eve rejected |
| `1928` | `PUBLIC` signed (`Alice → Bob`, unencrypted) | `c57ead3054861bff84e8947884f5672a14f92bd7b2f039fe440cc276be7977eaf010197eb4892e061178a0246ea963c3` | `bafkreie3x6km7obhasbkx3yl5xy2uzogjbskpwjkwbrdd3tgefnbs4kwz4` (`5,488 B` env) | Read & ML-DSA-65 signature verified by Eve |
| `1929` | `PRIVATE` 320 KiB 3-chunk `Manifest` (`Alice → [Bob, Charlie]`) | `697117e66111cb057813e1451e970c2cd946b99eed50a05765ad37e5ca6bed72172746a602f9f354d2229df056055444` | `bafkreifuhlb5nq4hjokl7t3edyfzh6yn2drvqdksr5gz5hruwqhh2cqrha` (`9,832 B` env · `100 B` memo) | `327,680 B` (`128+128+64 KiB`) reassembled byte-for-byte (`SHA-256 b7c24200…17b`) |
| `1930` | `SEALED` self-payment, threaded (`Charlie → Charlie`, `live-thread-f9815b56`) | `6fa3b8e19af9772b7011075af87e114ba87d0ae397f18d7738f398d08674a1dac33b0acc72ee0a90a4b42f62305fc4f0` | `bafkreib2ktfa6ducqfyuh4fx627acjfutace7eudkxduceizjetj5bkhdi` (`8,077 B` env · `76 B` memo) | `from == to == Charlie`; initial threaded self-payment run (superseded by clean Block `1931`) |
| **`1931`** | **`SEALED` self-payment, clean (`Charlie → Charlie`, `thread_id=""`, `reply_to_cid=""`)** | `0644e520405d20b848edb24ed5e5af609cae22ae218c2b7e281f47857d854e22347e4cbc1e49b03fe10c1c3531e46cbe` | `bafkreihfhilg4s73dp34xvg5njsrln2pl7lbvxk3c4qs3lrsospxukds6e` (`8,047 B` env · `54 B` memo) | `from == to == Charlie` (Bob absent from Block `1931` `account_tx`); zero `thread_id`, `reply_to_cid`, or `recipient_account`; Bob discovered via Charlie's `account_tx` & decrypted; Eve rejected |

*(Block `1929` chunk CIDs inside the manifest: `bafkreiegkschilopdhomw5nxxqxh4ixr6byj35wlvepebgx7rhxdecpoa4`, `bafkreig3v6si5nng7rj42h6gs5752zrjvn64xaso6dytl44o5lgz475aki`, `bafkreihnzshsdmr4j34x5pgfxlisgybrsylakfy3oais2i3k2u3qt6bwx4`.)*

### Nine SDK-Enforced Negative Controls (`postfiatl1v2#310`)

Every negative control below executed directly inside the SDK (`open_envelope()`, `reassemble_manifest_chunks()`, or `xchacha20_poly1305_decrypt()`), with matching JS unit tests passing in `wallet-proxy/test_message_protocol.js` against `@noble/post-quantum`:

| Attack Tested | SDK Entry Point | Target Artifact | Observed Error |
| --- | --- | --- | --- |
| 1-bit signature flip *(no `expected_multibase_cid`, isolating signature verification)* | `open_envelope()` | Block `1923` envelope | `Envelope raw-byte signature verification failed` |
| 1-bit raw block tamper vs. expected CID | `open_envelope()` | Block `1923` envelope | `IPFS CIDv1 raw multibase mismatch` |
| Cross-chain replay (`wrong chain_id`) | `open_envelope()` | Block `1923` vs. `postfiat-mainnet-1` | `Envelope chain_id mismatch` |
| Foreign-sender CID re-anchoring | `open_envelope()` | Block `1923` with Eve as `expected_tx_sender` | `Foreign re-anchor rejected: header.sender_account != anchoring tx.from` |
| Spoofed `sender_account` in header | `open_envelope()` *(default `verify_sender_address=True`)* | Eve signs claiming Alice's address | `Envelope sender_pubkey address != header.sender_account` |
| Chunk reorder (`[1, 0, 2]`) | `reassemble_manifest_chunks()` | Block `1929` manifest | `IPFS CIDv1 raw binary digest mismatch` |
| Chunk truncation (`[0, 1]`) | `reassemble_manifest_chunks()` | Block `1929` manifest | `block count does not match manifest.chunks length` |
| Chunk-index AAD splice (chunk 1 under slot 0 AAD, bypassing CID) | `xchacha20_poly1305_decrypt()` | Block `1929` chunk 1 | `XChaCha20-Poly1305 authentication failed` |
| 1-bit ciphertext tamper on chunk 1 (bypassing CID) | `xchacha20_poly1305_decrypt()` | Block `1929` chunk 1 | `XChaCha20-Poly1305 authentication failed` |

### Python Example (Matches Block `1931` Production `SEALED` Profile)

```python
from pf_message_test_env import MessageTestEnvironment, Visibility

env = MessageTestEnvironment()
env.bootstrap(("alice", "bob", "charlie", "eve"))

# Self-payment anchor (Charlie -> Charlie) keeps Bob's address off L1.
# Omitting thread_id and reply_to_cid prevents cleartext MessageHeader correlation.
receipt = env.send_message(
    sender_name="charlie",
    recipient_names=["bob"],
    text="Clean production-profile self-payment sealed drop from Charlie to Bob",
    visibility=Visibility.SEALED,
    thread_id="",
    reply_to_cid="",
    anchor_self=True,
)

# Bob discovers the pointer from Charlie's account_tx (or a relay hint) and verifies
# CID, ML-DSA-65 signature, sender_pubkey address, chain_id, and tx.from inside open_envelope()
msgs = env.read_onchain_messages_for_address(
    query_address=env.wallet("charlie").address,
    decrypt_as_wallet="bob",
    from_height=receipt.height,
    to_height=receipt.height,
)
assert msgs[0].thread_id == "" and msgs[0].reply_to_cid == ""
```

---

## 4. What Ships Next

The wire format verified above runs over `payment_v2` consensus blocks today. Four follow-on PRs are in review to extend this exact `pf.ptr` v5 format onto sub-second FastPay settlement and production wallet clients:

- **Constant-time browser/desktop crypto:** Rust/WASM wallet signing and X-Wing decapsulation in [`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303) plus native Mac wallet views in [`tasknode-apple#41`](https://github.com/postfiatorg/tasknode-apple/pull/41).
- **FastPay fee floor & `order_hash` indexing:** Computation + net-new-object anti-bloat fees and immutable `order_hash` indexing in `account_tx` ([`postfiatl1v2#295`](https://github.com/postfiatorg/postfiatl1v2/pull/295)), enabling crash-safe FastPay Task Node reward payouts ([`tasknode#450`](https://github.com/postfiatorg/tasknode/pull/450)) and connecting the merged x402 agent-payment facilitator (`tools/x402-facilitator/`, currently tested on deterministic in-memory harnesses) to live devnet-2 FastPay validators. We will publish dedicated live FastPay and x402 verification benchmarks once `#295` deploys.

For full protobuf definitions, domain-separation constants, and x402 header schemas, see the [Post-Quantum Message Protocol, FastPay & x402 Technical Guide](/docs/message-protocol/) and [`docs/specs/message-protocol-v1.md`](https://github.com/postfiatorg/postfiatl1v2/blob/main/docs/specs/message-protocol-v1.md).
