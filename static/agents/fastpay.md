# Post Fiat FastPay Guide for Agents & Developers

Canonical HTML page: https://postfiat.org/docs/fastpay/
Canonical Markdown page: https://postfiat.org/agents/fastpay.md

**FastPay** is the Post Fiat Ledger's consensusless payment lane for prefunded single-owner `PFT` objects (`1 PFT = 1,000,000 atoms`). Instead of waiting for block consensus, the payer (or an x402 facilitator) collects `>= 2f+1` distinct validator ML-DSA-65 approval votes directly to form a finality certificate in **one network round trip** (`25.6 ms` co-located; `274 ms` 1-RTT certificate finality and `319 ms` steady-state x402 `402 -> 200` settlement across a 3-continent `5-of-6` WAN quorum).

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
| **`certificate` (1-RTT)** | `owned_sign_v3` quorum (`>= 2f+1` votes) -> durable facilitator WAL `fsync` -> synchronous co-located validator apply -> async background quorum apply | **`274 ms`** direct / **`319 ms`** x402 | Default for x402 facilitators and paid APIs with a durable `FileCertificateStore` WAL and background apply worker. Funds are cryptographically locked by `>= 2f+1` validators before HTTP `200` returns. |
| **`applied_quorum` (2-RTT)** | `owned_sign_v3` quorum + `owned_apply_v3` signed `FastPayApplyAckV1` quorum (`>= 2f+1` acks) | **`565 ms`** direct | Use when the caller must immediately spend the new output/change object across remote validators without a pre-split `OwnedObjectPool`, or when requiring `account_tx` indexing visibility before returning. |

---

## 2. Preflight & Account Lifecycle

Every FastPay flow follows five steps: **check readiness -> fund (wrap) -> inspect objects -> sign & settle -> unwrap (optional)**.

### Step 1: Preflight Readiness (Fail Closed)

1. Call `server_info` and confirm `rpc.owned_lane_enabled === true`. If `false`, fail closed and do not sign.
2. Call `owned_recovery_capabilities` to read the active v3 recovery domain (`chain_id`, `genesis_hash`, `protocol_version`), `committee_epoch`, and bounded `valid_from_height` / `expires_at_height` / `recovery_closes_at_height` window.
3. Call `fastpay_recovery_committee` (no params returns the active epoch) and pin validator IDs, ML-DSA-65 public keys, `registry_root`, and quorum threshold (`2f + 1`, e.g. `5` of `6` for `f = 1`).

### Step 2: Fund (Wrap) `PFT` into an Owned Object

Submit a source-signed consensus `OwnedDepositV1` via `mempool_submit_fastlane_primary` (or Python `wrap_fastpay`).
- Confirm the consensus receipt carries exact accepted code **`owned_deposit_applied`**.
- Legacy unsigned `wrap_owned` and `unwrap_owned` RPCs are disabled.

### Step 3: Read Owned Objects Safely

Query `owned_objects` with `owner_public_key_hex` (optionally `asset: "PFT"`, `limit: 2048`, `omit_owner_keys: true`):
- Pages cap at `960 KiB`. If `truncated === true`, paginate using `next_cursor` until `next_cursor === null` before selecting inputs. Never select from a partial page.
- On `owned_objects_view_changed`, restart cleanly from `cursor: null` (up to 3 retries).

### Step 4: Exact Minimum Fee Formula

```text
min_fee_atoms = 25
              + ceil(tx_bytes / 512)
              + max(0, outputs - inputs) * 1,000
              + inputs
```

- **1-in / 1-out sweep** (`~5.8 KB` ML-DSA-65 signed order): `38 atoms` (`0.000038 PFT`)
- **1-in / 2-out transfer with change**: `1,038 atoms` (`0.001038 PFT`)
- **Multi-input merge** (up to 2,048 inputs): base + byte fee + 1 atom per input, zero new-object surcharge
- Per-account soft cap: **4,096 owned objects** (global ceiling 10,000,000). Merge dust periodically.

---

## 3. Agent Playbook A: Paying x402 APIs & MCP Tools (JavaScript / Node.js)

Source: `tools/x402-facilitator/mcp-client.js` in `postfiatorg/postfiatl1v2`.

```js
const {
  X402HttpClient,
  X402McpClient,
  OwnedObjectPool,
} = require('./tools/x402-facilitator/mcp-client');

// Pre-split K owned objects so your agent can execute K concurrent
// 1-RTT FastPay calls without blocking on remote change-output apply.
const pool = new OwnedObjectPool(initialOwnedObjects, { lowWaterRatio: 0.5 });

let nonce = 1;
const httpClient = new X402HttpClient({
  chainId: 'postfiat-wan-devnet-2',
  payerAccount,
  payerPublicKey,
  payerSecretKey,
  maxBudgetAtoms: 500_000,
  allowedNetworks: ['postfiat:wan-devnet-2'],
  allowedAssets: ['PFT'],
  nativeFastPay: async ({ required }) => {
    const obj = pool.checkout(required.max_amount_atoms + 2_000, required.asset_id);
    if (!obj) throw new Error('OwnedObjectPool exhausted — replenish or wait');
    return {
      domain: activeRecoveryDomain,
      recovery: activeRecoveryWindow,
      payeePubkeyHex: await resolvePayeePubkeyHex(required.pay_to),
      inputs: [{ id: obj.id, version: obj.version }],
      inputTotalAtoms: obj.value,
      nextNonce: () => nonce++,
    };
  },
});

const mcp = new X402McpClient({ endpointUrl: 'https://api.example.com/mcp', httpClient });

// Always pass expectedPayment so the client refuses tampered price/payee before signing.
const { result, paymentReceipt } = await mcp.callTool(
  'market_quote',
  { ticker: 'PFT' },
  { expectedPayment: { amountAtoms: 1_000, assetId: 'PFT', payTo: payeeAccount } }
);
```

### `OwnedObjectPool` Methods
- `pool.checkout(minAtoms, asset)`: reserves the smallest ready object covering amount + fee.
- `pool.recordSpent(spentId, changeObject, { immediatelyReady })`: moves change output to pending confirmation until quorum apply confirms.
- `pool.confirmPending(changeId)`: marks change output ready once `GET /x402/certificates/:orderHash` reports quorum confirmation.
- `pool.releaseUnspent(id)`: releases object back to ready if signing never occurred.
- `pool.needsReplenish()`: returns `true` when ready count drops below `lowWaterRatio`.

---

## 4. Agent Playbook B: Direct FastPay in Python (`postfiat_rpc`)

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

wrapped = wrap_fastpay(client, wallet=wallet, amount=100_000)

# Always pass a persistent work_dir so crash/timeout retries replay the exact
# journaled order_hash/certificate instead of signing a conflicting order.
sent = send_fastpay(
    client,
    wallet=wallet,
    recipient_public_key_hex=recipient_pubkey_hex,
    amount=5_000,
    fee=1_038,
    work_dir=Path("state/fastpay-journal/payout-001"),
)

unwrapped = unwrap_fastpay(client, wallet=wallet, amount=50_000)
```

---

## 5. High-Throughput Settlement: Direct TLS 1.3 Protobuf FastPay RPC v2

`postfiat-node` exposes **FastPay RPC v2** (`postfiat-fastpay-rpc-v2`) over persistent **TLS 1.3 + mTLS** TCP sockets (`TCP_NODELAY = true`):

- **Framing:** `[u8 version = 2][u32be body_len][canonical protobuf body]`, `64 KiB` cap.
- **Methods:**
  - `1` (`owned_sign_v3`): **`7,611 B`** on the wire (uses `owner_is_change_recipient` flag to avoid repeating the 1,952-byte pubkey).
  - `2` (`owned_apply_v3_fast`): **`16,716 B`** on the wire (`lock_id` + quorum `votes[]`, backed by a 256-entry validator order LRU).
  - `3` (`owned_apply_v3_full`): full certificate fallback used automatically when a validator returns status `3` (`OrderNotCached`).
- **Status codes:** `0` (`OK`), `1` (`InvalidInput`), `2` (`UnsupportedProtocolVersion`), `3` (`OrderNotCached`), `4` (`RateLimited`), `5` (`InternalError`).

```js
const { FileCertificateStore, createChainSettlementAdapter } = require('./tools/x402-facilitator/chain-adapter');

const adapter = createChainSettlementAdapter({
  rpcUrls: validatorJsonRpcUrls,
  fastpayRpcV2Endpoints: {
    'validator-0': { host: 'v0.example', port: 28650 },
    'validator-1': { host: 'v1.example', port: 28651 },
  },
  fastpayRpcV2TlsOptions: { ca, cert, key },
  committeeRegistry,
  expectedDomain,
  requireAuthenticatedCommittee: true,
  settlementFinalityMode: 'certificate',
  certificateStore: new FileCertificateStore('/var/lib/postfiat-x402/certs.jsonl'),
  coLocatedValidatorId: 'validator-2',
  coLocatedValidatorSyncApply: true,
});

await adapter.replayPendingCertificates();
```

Facilitators expose `GET /x402/certificates/:orderHash` to inspect quorum-apply convergence or retrieve the persisted certificate.

---

## 6. Mandatory Safety Rules for Autonomous Agents

1. **NEVER sign two conflicting orders for the same `(object_id, version)`.** Persist `(object_id, version, order_hash, signed_order)` before broadcast; on timeout/crash always retry the exact same `order_hash`.
2. **ALWAYS deduplicate on immutable 48-byte `order_hash` (SHA3-384), never `certificate_digest`.**
3. **NEVER delete a lock locally on timeout.** Use permissionless ordered recovery (`owned_certificate`, `owned_recovery_status`, quorum-verified `owned_fence_status`).
4. **ALWAYS set `maxBudgetAtoms` and `expectedPayment`** on x402 clients—signed FastPay orders have no protocol-level refund if an untrusted server withholds HTTP `200`.
5. **ALWAYS verify `>= 2f+1` distinct active-committee ML-DSA-65 signatures** against a pinned `registry_root` from `fastpay_recovery_committee`.
6. **ALWAYS check `server_info.rpc.owned_lane_enabled`** and paginate `owned_objects` until `next_cursor === null` before selecting inputs.

---

## 7. RPC Methods & Refusals Reference

- **JSON-RPC v1:** `owned_objects`, `fastpay_fee_quote`, `owned_recovery_capabilities`, `fastpay_recovery_committee`, `mempool_submit_fastlane_primary`, `owned_sign_v3`, `owned_apply_v3`, `owned_unwrap_sign_v3`, `owned_unwrap_apply_v3`, `owned_certificate`, `owned_recovery_status`, `owned_fence_status`.
- **Protobuf RPC v2 (TLS 1.3):** `owned_sign_v3` (`1`), `owned_apply_v3_fast` (`2`), `owned_apply_v3_full` (`3`).
- **Key error actions:**
  - `OrderNotCached` (status `3`): retry once with `owned_apply_v3_full` (automatic in `FastPayRpcV2Client`).
  - `owned_objects_view_changed`: restart pagination from `cursor: null`.
  - `insufficient_fastpay_input`: select larger object or merge inputs (account for `+ 1,000 atoms` if creating a change output).
  - `payment_terms_mismatch` / `budget_exceeded`: abort before signing.
  - `storage_writer_busy`: fail over to remaining validators in the `2f+1` quorum.
  - `postfiat-fastpay-held-effect-v1`: unsigned receipt from a non-voting holder; do not count toward active-committee quorum acks.

---

## 8. Live 3-Continent WAN Benchmarks (`postfiat-wan-devnet-2`, `5-of-6` Quorum)

- Co-located validator (`1.2 ms` RTT): `9.6 ms` sign + `15.9 ms` fast apply = **`25.6 ms` combined**
- Direct FastPay v3 1-RTT certificate finality (`5-of-6` WAN): **`274 ms` p50** (`264 ms` min)
- Direct FastPay v3 2-RTT applied quorum (`5-of-6` WAN): **`565 ms` p50** (`539 ms` min)
- Steady-state x402 `402 -> 200` 1-RTT MCP settlement (`5-of-6` WAN): **`319 ms` p50**, **`344 ms` p95** (`300-348 ms` min/max)
- Full evidence JSON: https://postfiat.org/evidence/message-protocol/devnet2-wan-fastpay-x402-20261128.json

---

## Related Docs

- HTML FastPay Guide: https://postfiat.org/docs/fastpay/
- Message Protocol & x402 Guide: https://postfiat.org/docs/message-protocol/
- Connect an AI Agent (MCP): https://postfiat.org/agents/
- L1 RPC Methods Reference: https://postfiat.org/docs/l1/rpc/methods/
- L1 Settlement Lanes: https://postfiat.org/docs/l1/architecture/settlement-lanes/
- Python Wallet Functions: https://postfiat.org/docs/l1/python/wallet-functions/
