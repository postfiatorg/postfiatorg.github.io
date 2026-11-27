---
title: "Post-Quantum Messaging on Post Fiat L1v2: Wire Format, Threat Model & Devnet Integration Test"
date: 2026-11-27T00:00:00Z
draft: false
summary: "How Post Fiat L1v2 anchors post-quantum encrypted messages on-chain using canonical protobufs, hybrid X-Wing encryption, and raw-byte ML-DSA-65 signatures—with a candid threat model and a 9-transaction devnet integration test across Blocks 1923–1931."
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

- **Merged on `main`:** Canonical `.proto` definitions ([`postfiatl1v2#288`](https://github.com/postfiatorg/postfiatl1v2/pull/288)), Python and JavaScript codecs ([`postfiatl1v2#289`](https://github.com/postfiatorg/postfiatl1v2/pull/289)), SDK-enforced sender and anchor-binding checks ([`postfiatl1v2#310`](https://github.com/postfiatorg/postfiatl1v2/pull/310)), and explorer decoding views ([`postfiatorg.github.io#56`](https://github.com/postfiatorg/postfiatorg.github.io/pull/56)).
- **Live integration test (`postfiat-wan-devnet-2`, Blocks `1923–1931`):** Nine live `payment_v2` transactions across four funded wallets plus nine negative controls enforced directly inside `open_envelope()` and the manifest codec. All full transaction hashes, CIDs, balances, and error strings are published in [`devnet2-live-verification-20261127.json`](/evidence/message-protocol/devnet2-live-verification-20261127.json).
- **What this integration test does *not* establish:** Side-channel safety (the live Python run uses pure-Python reference crypto libraries rather than constant-time production Rust/WASM), live JavaScript/WASM interoperability, throughput benchmarks, or independent cryptographic review.
- **Open privacy tradeoffs:** Seed-derived bootstrap encryption keys sacrifice incoming forward secrecy, and `SEALED` mode hides on-chain payees when self-anchored but remains linkable whenever recipient key bindings are public.

<div class="glance">
  <div><b>9 Devnet Txs</b><span>Blocks 1923–1931 · 8 encrypted + 1 public · 6/6 consensus</span></div>
  <div><b>X-Wing + ML-DSA-65</b><span>Hybrid PQ encryption · raw-byte FIPS 204 signatures</span></div>
  <div><b>54–100 B On-Chain</b><span>Compact pf.ptr v5 memo · 5.5–9.8 KB off-chain envelopes</span></div>
  <div><b>9 / 9 SDK Controls</b><span>Tamper, chunk, replay &amp; re-anchor checks in open_envelope()</span></div>
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
| Recipient `key_id` | `32 B` | `SHA-256` fingerprint of the recipient's `1,216 B` X-Wing public key |
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
| `SEALED` self-payment (`Charlie → Charlie`, Block `1931`) | Sender (`Charlie`), `to == Charlie` (no payee on L1), fee, time, `54 B` memo, CID | Cleartext `MessageHeader` (`thread_id` & `reply_to_cid` omitted), sender pubkey, **no** `recipient_account` strings, 32 B `recipient_key_id` tags | Plaintext body, on-chain payee, & thread linkage |

**Be realistic about `SEALED` mode:** When recipient `MessageKeyBinding` records (`account ↔ xwing_public_key ↔ key_id`) are published in a directory or on-chain identity registry, `SEALED` does **not** give unlinkable anonymity. The sender is always in cleartext, and an observer who joins the key directory against IPFS blocks can link each static 32-byte `recipient_key_id` back to the recipient. Self-anchored `SEALED` keeps the recipient's address off L1 and strips explicit account strings from IPFS headers—stopping casual ledger scraping, not a determined metadata analyst. Because `Envelope.header_bytes` is authenticated-but-unencrypted, production `SEALED` senders must also omit or randomize `thread_id` and `reply_to_cid` (as in Block `1931`), putting thread pointers inside the encrypted body instead.

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
- **Non-repudiation & multi-recipient key commitment:** ML-DSA-65 envelope signatures are **non-repudiable**—anyone holding an envelope can cryptographically prove the sender signed it, and rotating an encryption key later does not invalidate past signatures. Separately, standard XChaCha20-Poly1305 is **not key-committing**: in an untrusted multi-recipient group, a malicious sender who controls the CEK could theoretically wrap different keys to different recipients. Clients should treat group decryption as proving *sender authorship*, not that every other listed recipient received identical plaintext.

### Seed-Derived Keys, Discovery & IPFS Availability

- **Forward-secrecy tradeoff:** New users start with `0 PFT` and cannot mint an on-chain identity before receiving their first payout. The bootstrap X-Wing keypair therefore derives deterministically from the wallet master seed (`HKDF-SHA256`, domain `postfiat-l1-v2/message-key/v1`), bound by a signed `MessageKeyBinding` uploaded to Task Node at onboarding. Task Node cannot forge a binding for an address it does not control, though before the user publishes an on-chain identity record, Task Node controls directory availability and could withhold a binding or serve an older `key_epoch`. Crucially, deterministic seed derivation gives up **incoming forward secrecy**: a compromised master seed or long-term decapsulation key retroactively decrypts all past messages wrapped to that key—a far more immediate threat today than quantum computing. Rotating `key_epoch` to a fresh non-seed-derived key protects *future* messages, though automated rotation UX remains wallet-level rollout work. Task Node is included as a reader only on Task Node lifecycle and reward schemas, never on user-to-user messages.
- **Recipient discovery tradeoffs:** Non-payee recipients of group or self-payment `SEALED` messages will not find the anchor transaction in their own `account_tx`. Each discovery channel trades convenience against metadata:

| Discovery Path | How It Works | What Infrastructure Sees |
| --- | --- | --- |
| Sender-indexed polling | Poll known senders' `account_tx` and match `recipient_key_id` (Block `1931`) | RPC node sees which sender addresses you watch (mitigated by a local node) |
| Off-chain relay hint | Relay (`ops/nostr-relay/`) or app pushes `(tx_id, cid)`; client verifies on L1 | Relay learns push timing and subscriber graph (cannot forge or decrypt) |
| Opt-in `key_id` indexer | Indexer fetches off-chain envelopes linked by `pf.ptr` v5 pointers and indexes `recipient_key_id` wraps | Indexer learns subscriber `key_id` watchlists and query timing |

- **IPFS pinning:** On-chain pointers prove existence, order, and integrity, not permanent hosting. Task Node pins Task Node traffic, governance packets, and Post Fiat NFT metadata via an async durable retry outbox; third-party apps pin their own blocks or pay a pinning provider. If all off-chain copies vanish, the pointer remains valid on L1 but the message body is unrecoverable.

---

## 3. Live Devnet-2 Integration Test (Blocks 1923–1931)

To exercise the wire protocol against live BFT consensus, we ran **nine `payment_v2` transactions** across four funded wallets on our 6-validator `postfiat-wan-devnet-2` network on **27 November 2026**, using the hardened Python codec (`postfiatl1v2#310`) paired with pure-Python reference crypto (`kyber-py==1.2.0` `ML_KEM_768`, `dilithium-py==1.5.1` `ML_DSA_65`, `cryptography` `X25519`, `pycryptodome` 24-byte-nonce `ChaCha20_Poly1305`). Those Python crypto packages are **not constant-time** and serve strictly as an integration-test backend; production browser/desktop wallets target Rust/WASM (`crates/wallet_wasm`, [`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303)).

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
| **`1931`** | **`SEALED` self-payment, clean (`Charlie → Charlie`, `thread_id=""`)** | `0644e520…31e46cbe` | `8,047 B` env · `54 B` memo | `from == to == Charlie` (Bob absent from Block `1931` `account_tx`); zero `thread_id`, `reply_to_cid`, or `recipient_account`; Bob discovered via Charlie's `account_tx` & decrypted; Eve rejected |

### Nine SDK-Enforced Negative Controls (`postfiatl1v2#310`)

Every negative control below ran directly inside the shipped Python SDK (with matching JS unit tests passing in `wallet-proxy/test_message_protocol.js` against `@noble/post-quantum`):

| Attack Tested | SDK Entry Point | Observed Error |
| --- | --- | --- |
| 1-bit signature flip *(omitting `expected_multibase_cid` to isolate signature verification)* | `open_envelope()` | `Envelope raw-byte signature verification failed` |
| 1-bit raw block tamper vs. expected CID | `open_envelope()` | `IPFS CIDv1 raw multibase mismatch` |
| Cross-chain replay (`wrong chain_id`: devnet-2 vs. mainnet-1) | `open_envelope()` | `Envelope chain_id mismatch` |
| Foreign-sender CID re-anchoring (Alice's CID under Eve's `tx.from`) | `open_envelope()` | `Foreign re-anchor rejected` |
| Spoofed `sender_account` in header (Eve signs claiming Alice's address) | `open_envelope()` *(default on)* | `Envelope sender_pubkey address != header.sender_account` |
| Chunk reorder (`[1, 0, 2]` on Block `1929` manifest) | `reassemble_manifest_chunks()` | `IPFS CIDv1 raw binary digest mismatch` |
| Chunk truncation (`[0, 1]` on Block `1929` manifest) | `reassemble_manifest_chunks()` | `block count does not match manifest.chunks length` |
| Chunk-index AAD splice (chunk 1 under slot 0 AAD, bypassing CID) | `xchacha20_poly1305_decrypt()` | `XChaCha20-Poly1305 authentication failed` |
| 1-bit ciphertext tamper on chunk 1 (bypassing CID) | `xchacha20_poly1305_decrypt()` | `XChaCha20-Poly1305 authentication failed` |

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

## 4. What Ships Next

Everything verified above runs over standard `payment_v2` consensus blocks today. Two follow-on tracks are in review to extend this exact `pf.ptr` v5 wire format:

- **Production constant-time wallet clients:** Rust/WASM browser signing and X-Wing decapsulation ([`postfiatl1v2#303`](https://github.com/postfiatorg/postfiatl1v2/pull/303)) and native Mac wallet views ([`tasknode-apple#41`](https://github.com/postfiatorg/tasknode-apple/pull/41)).
- **Sub-second FastPay & x402 agent payments:** **FastPay** is Post Fiat's owned-object payment lane targeting `~200 ms` quorum finality; [`postfiatl1v2#295`](https://github.com/postfiatorg/postfiatl1v2/pull/295) adds anti-bloat computation/new-object fees and indexes FastPay transfers into `account_tx` by immutable `order_hash`, unlocking fast Task Node reward payouts ([`tasknode#450`](https://github.com/postfiatorg/tasknode/pull/450)) and connecting our **x402** facilitator (HTTP `402 Payment Required` settlement for AI agent API calls, merged in `tools/x402-facilitator/` and currently tested against in-memory harnesses) to live devnet-2 validators. We will publish dedicated FastPay and x402 benchmarks once `#295` deploys.

Full protobuf schemas, domain-separation constants, and x402 header formats live in the [Post-Quantum Message Protocol Technical Guide](/docs/message-protocol/) and [`docs/specs/message-protocol-v1.md`](https://github.com/postfiatorg/postfiatl1v2/blob/main/docs/specs/message-protocol-v1.md).
