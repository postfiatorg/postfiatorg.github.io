---
title: "FastPay Guide for Agents & Developers"
url: "/docs/fastpay/"
type: "page"
layout: "single"
kicker: "FastPay · Sub-Second Settlement"
date: 2026-11-28
summary: "How AI agents and applications fund, spend, pool, recover, and settle sub-second FastPay v3 payments and x402 HTTP/MCP API calls on the Post Fiat Ledger."
---

**FastPay** is the Post Fiat Ledger's consensusless payment lane for prefunded single-owner `PFT` objects (`1 PFT = 1,000,000 atoms`). Instead of waiting for block consensus, the payer (or an x402 facilitator) collects `q = n - f` distinct validator ML-DSA-65 approval votes directly to form a finality certificate in **one network round trip** (`27.0 ms` co-located; `274 ms` 1-RTT certificate finality and `319 ms` x402 `402 → 200` settlement across a 3-continent `5-of-6` WAN quorum, with sub-second cross-block p95 tails).

> **For AI agents & coding tools:** A standalone plain-Markdown copy of this guide is served at [`/agents/fastpay.md`](/agents/fastpay.md) (and [`/docs/fastpay/index.md`](/docs/fastpay/index.md)).

---

## 1. When to Use FastPay vs. Consensus (`payment_v2`)

| Use Case | Recommended Lane | Why |
| --- | --- | --- |
| Pay-per-call AI agent APIs & MCP tools (`x402`) | **FastPay (`OwnedTransferOrderV3`)** | Sub-second 1-RTT certificate finality (`~319 ms` WAN), immutable `order_hash` deduplication, 51-byte inline `request_hash` memo |
| High-frequency `PFT` payouts & micropayments | **FastPay (`OwnedTransferOrderV3`)** | Consensusless parallel settlement with an `OwnedObjectPool`; indexed directly in `account_tx` and `tx` by `order_hash` |
| Anchoring `pf.ptr` v5 messages with sub-second confirmation | **FastPay self-transfer or transfer** | Carries up to 4 memos (`<= 256 B` each, lowercase hex) without waiting for block consensus |
| Transfers from an unwrapped account balance | **Consensus (`payment_v2`)** | No prior owned-object funding step needed |
| Issued assets (`pfUSDC`, NAVCoins), escrows, NFTs, DEX offers | **Consensus (`issued_payment_v2`, etc.)** | FastPay v3 moves native `PFT` owned objects only |

### Choosing 1-RTT (`certificate`) vs. 2-RTT (`applied_quorum`) Finality

| Finality Mode | Network Hops | WAN p50 (`5-of-6`) | When to Use |
| --- | --- | ---: | --- |
| **`certificate` (1-RTT)** | `owned_sign_v3` quorum (`>= 2f+1` votes) → durable facilitator WAL `fsync` → synchronous co-located validator apply → async background quorum apply | **`274 ms`** direct / **`319 ms`** x402 | Default for x402 facilitators and paid APIs with a durable `FileCertificateStore` WAL and background apply worker. Funds are cryptographically locked by `>= 2f+1` validators before HTTP `200` returns. |
| **`applied_quorum` (2-RTT)** | `owned_sign_v3` quorum + `owned_apply_v3` signed `FastPayApplyAckV1` quorum (`>= 2f+1` acks) | **`565 ms`** direct | Use when the caller must immediately spend the new output/change object across remote validators without a pre-split `OwnedObjectPool`, or when requiring `account_tx` indexing visibility before returning. |

---

## 2. Preflight & Account Lifecycle

Every FastPay flow follows five steps: **check readiness → fund (wrap) → inspect objects → sign & settle → unwrap (optional)**.

### Step 1: Preflight Readiness (Fail Closed)

Before signing any FastPay order, verify that the target endpoint has the owned lane enabled and fetch the active recovery committee and window:

1. Call `server_info` and confirm `rpc.owned_lane_enabled === true`. If `false` (an operator passed `--disable-owned-lane`), fail closed and do not sign.
2. Call `owned_recovery_capabilities` to read the active v3 recovery domain (`chain_id`, `genesis_hash`, `protocol_version`), `committee_epoch`, and bounded `valid_from_height` / `expires_at_height` / `recovery_closes_at_height` window.
3. Call `fastpay_recovery_committee` (no params returns the active epoch) and pin the committee validator IDs, ML-DSA-65 public keys, `registry_root`, and quorum threshold (`2f + 1`, e.g. `5` of `6` for `f = 1`).

### Step 2: Fund (Wrap) `PFT` into an Owned Object

FastPay spends **owned objects**, not raw account balances. Move `PFT` from an account into a FastPay owned object via a source-signed consensus `OwnedDepositV1` submitted through `mempool_submit_fastlane_primary` (or Python's `wrap_fastpay`).

- Confirm the consensus receipt carries exact accepted code **`owned_deposit_applied`**.
- Derive or read the created `object_id` (version `0`).
- Legacy unsigned `wrap_owned` and `unwrap_owned` RPCs are disabled and must never be called.

### Step 3: Read Owned Objects Safely

Query `owned_objects` with `owner_public_key_hex` (optionally `asset: "PFT"`, `limit: 2048`, `omit_owner_keys: true`):

- A response page is capped at `960 KiB`. If `truncated === true`, you **must** paginate using `next_cursor` until `next_cursor === null` before selecting inputs—never select from a partial page.
- Every page of a consistent snapshot shares the same `view_digest`. If an object changes mid-pagination, the node returns **`owned_objects_view_changed`**; restart cleanly from page 1 (up to 3 retries).

### Step 4: Exact Minimum Fee Formula

Validators enforce a Sui-inspired anti-bloat minimum fee on every `OwnedTransferOrderV3` (you can also query `fastpay_fee_quote`):

```text
min_fee_atoms = 25
              + ceil(tx_bytes / 512)
              + max(0, outputs - inputs) * 1,000
              + inputs
```

| Transfer Shape (`signing_bytes_len` = canonical unsigned order bytes) | Minimum Fee | Cost in PFT |
| --- | ---: | ---: |
| **1-in / 1-out sweep** (`4,582 B`, `ceil / 512 = 9`, no change object) | `35 atoms` | `0.000035 PFT` |
| **1-in / 2-out payment with change** (`8,513 B`, `ceil / 512 = 17`, 1 net-new object) | `1,043 atoms` | `0.001043 PFT` |
| **10-in / 1-out merge** (`5,590 B`, `ceil / 512 = 11`, up to 2,048 inputs via JSON-RPC v1) | `46 atoms` | `0.000046 PFT` (zero new-object surcharge) |

Every account has a **4,096 owned-object soft cap** (under a 10,000,000 global ceiling). Agents should consolidate dust objects periodically using multi-input merges or unwraps (up to 2,048 inputs per transaction).

---

## 3. Agent Playbook A: Paying x402 APIs & MCP Tools (JavaScript / Node.js)

Post Fiat ships a native x402 v2 client (`X402HttpClient`), MCP JSON-RPC tool wrapper (`X402McpClient`), and pre-split `OwnedObjectPool` in [`tools/x402-facilitator/mcp-client.js`](https://github.com/postfiatorg/postfiatl1v2/blob/main/tools/x402-facilitator/mcp-client.js).

```js
const {
  X402HttpClient,
  X402McpClient,
  OwnedObjectPool,
} = require('./tools/x402-facilitator/mcp-client');

// 1. Pre-split K owned objects so your agent can execute K concurrent
//    1-RTT FastPay calls without blocking on remote change-output apply.
const pool = new OwnedObjectPool(initialOwnedObjects, { lowWaterRatio: 0.5 });

let nonce = 1;
const httpClient = new X402HttpClient({
  chainId: 'postfiat-wan-devnet-2',
  payerAccount,          // pf... lowercase canonical address
  payerPublicKey,        // 1,952-byte ML-DSA-65 public key Buffer
  payerSecretKey,        // ML-DSA-65 secret key Buffer
  maxBudgetAtoms: 500_000, // Hard lifetime cap across calls (fees included)
  allowedNetworks: ['postfiat:wan-devnet-2'],
  allowedAssets: ['PFT'],
  nativeFastPay: async ({ required }) => {
    // Check out an unspent owned object that covers price + change fee
    const obj = pool.checkout(required.max_amount_atoms + 2_000, required.asset_id);
    if (!obj) throw new Error('OwnedObjectPool exhausted — replenish or wait');
    return {
      domain: activeRecoveryDomain, // { chain_id, genesis_hash, protocol_version }
      recovery: activeRecoveryWindow, // { committee_epoch, valid_from_height, expires_at_height, recovery_closes_at_height }
      payeePubkeyHex: await resolvePayeePubkeyHex(required.pay_to),
      inputs: [{ id: obj.id, version: obj.version }],
      inputTotalAtoms: obj.value,
      nextNonce: () => nonce++,
    };
  },
});

const mcp = new X402McpClient({
  endpointUrl: 'https://api.example.com/mcp',
  httpClient,
});

// 2. Always pass expectedPayment so the client refuses price/payee tampering
//    before signing anything.
const { result, paymentReceipt } = await mcp.callTool(
  'market_quote',
  { ticker: 'PFT' },
  {
    expectedPayment: {
      amountAtoms: 1_000,
      assetId: 'PFT',
      payTo: payeeAccount,
    },
  }
);
// paymentReceipt.order_hash is the immutable 48-byte SHA3-384 receipt ID.
```

### Why `OwnedObjectPool` Matters for Agents

An owned object `(id, version)` can only be spent **once**. If an agent holds a single owned object and fires two parallel tool calls, the second call either blocks waiting for the change output to apply across remote validators (`2-RTT`) or—worse—attempts to spend the same object version twice (causing an equivocation lock).

Keeping **`K` pre-split objects** in `OwnedObjectPool` lets an agent fire `K` concurrent 1-RTT FastPay / x402 requests immediately:
- `pool.checkout(minAtoms, 'PFT')` reserves the smallest ready object that covers the payment + fee.
- `pool.recordSpent(id, changeObj)` moves the change object to pending confirmation until the facilitator confirms quorum apply (`GET /x402/certificates/:orderHash`), then `pool.confirmPending(changeObj.id)` returns it to the ready pool.
- `pool.releaseUnspent(id)` returns an object if signing never happened.
- Check `pool.needsReplenish()` to split fresh objects asynchronously before the pool runs dry.

---

## 4. Agent Playbook B: Direct FastPay in Python (`postfiat_rpc`)

For Python agents and backend workers, `postfiat_rpc.wallet` wraps `OwnedDepositV1`, `OwnedTransferOrderV3`, and `OwnedUnwrapOrderV3` using the same Rust signing primitives as `postfiat-node`:

```python
from pathlib import Path
from postfiat_rpc import (
    PostFiatRpcClient,
    create_wallet,
    wrap_fastpay,
    send_fastpay,
    unwrap_fastpay,
)

client = PostFiatRpcClient("127.0.0.1:27650")
wallet = create_wallet(chain_id="postfiat-wan-devnet-2", wallet_dir="wallets/agent")

# 1. Fund a FastPay owned object from your L1 account balance (consensus deposit)
wrapped = wrap_fastpay(client, wallet=wallet, amount=100_000)

# 2. Send a recovery-safe FastPay v3 transfer.
#    ALWAYS pass a persistent work_dir so a crash/timeout retry replays the
#    exact journaled order_hash / certificate instead of signing a conflicting order.
sent = send_fastpay(
    client,
    wallet=wallet,
    recipient_public_key_hex=recipient_pubkey_hex,
    amount=5_000,
    fee=1_038,
    work_dir=Path("state/fastpay-journal/payout-001"),
)

# 3. Unwrap owned objects back to a normal L1 account balance (up to 2,048 inputs)
unwrapped = unwrap_fastpay(client, wallet=wallet, amount=50_000)
```

---

## 5. High-Throughput Settlement: Direct TLS 1.3 Protobuf FastPay RPC v2

For x402 facilitators, payment gateways, and latency-sensitive agents talking directly to validators, `postfiat-node` exposes **FastPay RPC v2** (`postfiat-fastpay-rpc-v2`) over persistent **TLS 1.3 + mutual TLS (mTLS)** TCP sockets with `TCP_NODELAY`:

- **Framing:** `[u8 version = 2][u32be body_len][canonical protobuf body]`, capped at **64 KiB** (`MAX_FASTPAY_V2_FRAME_BYTES = 65536`).
- **Compact wire sizes:**
  - `owned_sign_v3` (method `1`): **`7,611 B`** (fits inside a single 10-MSS TCP initial congestion window, using `owner_is_change_recipient` to avoid repeating the 1,952-byte owner pubkey on change outputs).
  - `owned_apply_v3_fast` (method `2`): **`16,716 B`** (sends `lock_id` + quorum `votes[]` only; validators look up the signed order from their 256-entry `SignedOwnedTransferOrderV3` LRU cache populated during `owned_sign_v3`).
  - `owned_apply_v3_full` (method `3`): automatic fallback when a validator replies with status `3` (`OrderNotCached`, e.g., after a restart or on a non-voting holder).
- **Status codes:** `0` (`OK`), `1` (`InvalidInput`), `2` (`UnsupportedProtocolVersion`), `3` (`OrderNotCached`), `4` (`RateLimited`), `5` (`InternalError`).

### Configuring the Production x402 Settlement Adapter

```js
const {
  FileCertificateStore,
  createChainSettlementAdapter,
} = require('./tools/x402-facilitator/chain-adapter');

const certStore = new FileCertificateStore('/var/lib/postfiat-x402/certs.jsonl');

const adapter = createChainSettlementAdapter({
  rpcUrls: [
    'http://validator-0:27650',
    'http://validator-1:27651',
    // ... all active committee validators
  ],
  // Enable direct TLS 1.3 binary Protobuf v2 transport:
  fastpayRpcV2Endpoints: {
    'validator-0': { host: 'v0.example', port: 28650 },
    'validator-1': { host: 'v1.example', port: 28651 },
    // ...
  },
  fastpayRpcV2TlsOptions: { ca, cert, key },
  committeeRegistry,
  expectedDomain,
  requireAuthenticatedCommittee: true,
  settlementFinalityMode: 'certificate', // 1-RTT finality (or 'applied_quorum' for 2-RTT)
  certificateStore: certStore,           // REQUIRED in production for 1-RTT durability
  coLocatedValidatorId: 'validator-2',   // Local validator for synchronous apply before HTTP 200
  coLocatedValidatorSyncApply: true,
});

// On startup, replay any unconfirmed certificates left in the WAL before crash:
await adapter.replayPendingCertificates();
```

Facilitators expose `GET /x402/certificates/:orderHash` so payers, agents, and monitors can inspect background quorum-apply convergence (`status`, `confirmed_validators`, `remaining_validators`) or retrieve the complete ML-DSA-65 certificate.

---

## 6. Mandatory Safety Rules for Autonomous Agents

Agents handling real `PFT` over FastPay **must** obey these six invariants:

1. **Never sign two conflicting orders for the same `(object_id, version)`.**
   On network timeout or process crash, **never** rebuild an order with a new nonce, fee, or recipient for the same input object. Persist `(object_id, version, order_hash, signed_order)` to disk **before** broadcasting and always retry that exact `order_hash`. Signing two conflicting orders for the same object version creates an equivocation lock until ordered recovery resolves it.
2. **Deduplicate strictly on immutable `order_hash` (48-byte SHA3-384), never `certificate_digest`.**
   A single FastPay transfer can yield different `certificate_digest` values depending on which `2f+1` validator votes arrived first. Both `account_tx`, `tx`, and `FileSpentStore` key on immutable `order_hash`.
3. **Never delete a lock locally on timeout—use ordered recovery.**
   If a payment fails to assemble a full quorum certificate before `expires_at_height`, recover permissionlessly via `owned_certificate`, `owned_recovery_status`, and quorum-verified `owned_fence_status` (`FastPayFenceStatusV2`). Ordered recovery either confirms the complete certificate once or cancels the lock and advances the object version.
4. **Always pin `maxBudgetAtoms` and `expectedPayment` on x402 clients.**
   Once an agent signs and transmits a FastPay order to an API server, the server can settle it on-chain even if it withholds the HTTP `200` body—there is no protocol-level refund. Bound exposure with tight per-call `expectedPayment: { amountAtoms, assetId, payTo }`, conservative `maxBudgetAtoms`, and bounded `expires_at_height`.
5. **Verify `>= 2f+1` distinct active-committee signatures against a pinned `registry_root`.**
   Never trust a single validator's reply or an unverified committee list. Pin the active committee epoch and `registry_root` from `fastpay_recovery_committee` and verify distinct ML-DSA-65 signatures locally.
6. **Check `owned_lane_enabled` and paginate `owned_objects` completely.**
   Fail closed when `server_info.rpc.owned_lane_enabled` is `false`, never select inputs from a `truncated: true` page, and restart pagination on `owned_objects_view_changed`.

---

## 7. RPC Methods & Error Handling Quick Reference

| Method | Transport | Purpose |
| --- | --- | --- |
| `owned_objects` | JSON-RPC v1 | Paginated list of owned objects (`limit <= 2048`, `cursor`, `view_digest`, `total_value`) |
| `fastpay_fee_quote` | JSON-RPC v1 | Fee quote and per-account / global owned-object capacity check |
| `owned_recovery_capabilities` | JSON-RPC v1 | Active v3 recovery domain, `committee_epoch`, and validity/recovery height windows |
| `fastpay_recovery_committee` | JSON-RPC v1 | Active (or specific `epoch`) committee validator IDs, ML-DSA-65 pubkeys, `registry_root` |
| `mempool_submit_fastlane_primary` | JSON-RPC v1 | Submit consensus-committed `OwnedDepositV1` wrap or ordered recovery action |
| `owned_sign_v3` | Protobuf v2 / JSON-RPC v1 | Persist-before-sign validator ML-DSA-65 approval vote (`7,611 B` on v2) |
| `owned_apply_v3_fast` / `owned_apply_v3` | Protobuf v2 / JSON-RPC v1 | Apply certified transfer and return signed `FastPayApplyAckV1` (`16,716 B` fast path on v2) |
| `owned_unwrap_sign_v3` / `owned_unwrap_apply_v3` | JSON-RPC v1 | Sign and apply v3 owned-to-account unwrap (up to 2,048 inputs + 1 change output) |
| `owned_certificate` | JSON-RPC v1 | Fetch a persisted complete certificate by digest or `lock_id` |
| `owned_recovery_status` | JSON-RPC v1 | Inspect ordered recovery state for a `lock_id` |
| `owned_fence_status` | JSON-RPC v1 | Validator ML-DSA-65-signed `FastPayFenceStatusV2` (`confirmed` or `cancelled` from certified blocks only) |

### Common Refusals & What Agents Should Do

| Error / Refusal | Meaning | Agent Action |
| --- | --- | --- |
| `OrderNotCached` (v2 status `3`) | Validator does not have the signed order in its 256-entry LRU | Automatically retry once with `owned_apply_v3_full` (handled transparently by `FastPayRpcV2Client`) |
| `owned_objects_view_changed` | Objects mutated between `owned_objects` pages | Restart pagination from `cursor: null` (up to 3 attempts) |
| `insufficient_fastpay_input` | Selected input cannot cover `amount + min_fee_atoms` | Select a larger object or merge multiple inputs (remember `+ 1,000 atoms` if creating change) |
| `payment_terms_mismatch` | Server `402` challenge differed from `expectedPayment` | Abort immediately without signing; alert operator or switch provider |
| `budget_exceeded` | Request price + fee exceeds `maxBudgetAtoms` | Stop spending; request human budget top-up |
| `storage_writer_busy` | Validator writer lease saturated during block commit | Fail over to remaining validators in the `2f+1` quorum |
| `postfiat-fastpay-held-effect-v1` (unsigned receipt) | Non-voting holder accepted and persisted the effect locally | Treat as held/recorded on that holder; do not count toward active-committee quorum acks |

---

## 8. Live WAN Performance Profile (`postfiat-wan-devnet-2`)

Measured on the live 6-validator `postfiat-wan-devnet-2` Rust fleet (`5-of-5` active signing keys in epoch 1 with `validator-5` as a non-voting holder; `1.3–2.4 ms` co-located RTT to `230 ms` bare max transcontinental RTT; direct TLS 1.3 Protobuf v2 with 300 s persistent idle timeout, append-only `owned_locks.wal` + CRC32C speculative effect WAL, lock-free chain-tip sidecar, post-block snapshot sidecar + commit-time WAL pruning, `0` hot-path `redb` opens and `0` cache misses across `1,370` server RPCs, `0` full-history storage scans) across an unfiltered 3-phase run crossing `19` live consensus blocks (`N = 50` direct + `N = 50` sequential x402 + `K = 8` concurrent `OwnedObjectPool` burst):

| Operation (unfiltered cross-block, 5-of-5 active signers) | Min | p50 | p95 | Max |
| --- | ---: | ---: | ---: | ---: |
| Co-located validator (`validator-2`, `~2 ms` RTT) `owned_sign_v3` (`N = 50`) | `9.7 ms` | **`11.7 ms`** | **`18.3 ms`** | `32.1 ms` |
| Co-located validator (`validator-2`, `~2 ms` RTT) `owned_apply_v3_fast` (`N = 50`) | `13.0 ms` | **`16.6 ms`** | **`23.0 ms`** | `39.9 ms` |
| Direct FastPay v3 **1-RTT certificate assembly** (`N = 50`, 7 blocks) | `258.1 ms` | **`273.0 ms`** | **`306.6 ms`** | `369.1 ms` |
| Direct FastPay v3 **2-RTT applied quorum** (`N = 50`, 7 blocks) | `529.1 ms` | **`563.8 ms`** | **`596.0 ms`** | `662.3 ms` |
| Full **x402 `402 → 200` 1-RTT MCP settlement** (`N = 50`, co-located client/facilitator; remote agents add `2 × client RTT`) | `298.8 ms` | **`321.7 ms`** | **`350.2 ms`** | `363.8 ms` |
| Concurrent **`OwnedObjectPool` x402 burst** (`K = 8` parallel, `N = 32`, 4 waves) | `316.6 ms` | **`602.7 ms`** | **`865.6 ms`** | `868.5 ms` (`9.33 calls/s` mean) |

Full evidence JSON: [`devnet2-wan-fastpay-x402-20261128-r8.json`](/evidence/message-protocol/devnet2-wan-fastpay-x402-20261128-r8.json).

---

## Further Reading

- **[Sub-Second Post-Quantum Payments: FastPay v3 & x402 on the Post Fiat Ledger](/blog/sub-second-post-quantum-fastpay-x402/)** — Systems deep dive on owned objects, anti-bloat fees, zero-`redb` hot paths, and 3-continent WAN tail-latency anatomy.
- **[Post-Quantum Messaging on the Post Fiat Ledger](/blog/post-quantum-messaging-fastpay-x402/)** — `postfiat.message.v1` off-chain envelopes, raw-byte ML-DSA-65 signing, and hybrid X-Wing encryption.
- **[Post-Quantum Message Protocol & x402 Guide](/docs/message-protocol/)** — `pf.ptr` v5 memos, X-Wing envelopes, and explorer rendering.
- **[Connect an AI Agent to Task Node](/agents/)** — MCP setup for Claude Code, Codex, Antigravity, Cursor, and custom apps.
- **[L1 RPC Methods Reference](/docs/l1/rpc/methods/)** — Full JSON-RPC method specifications and pagination rules.
- **[L1 Settlement Lanes](/docs/l1/architecture/settlement-lanes/)** — FastPay vs. consensus, W6 atomic swaps, FastSwap, and Asset-Orchard.
- **[Python Wallet Functions](/docs/l1/python/wallet-functions/)** — `wrap_fastpay`, `send_fastpay`, and `unwrap_fastpay` API reference.
