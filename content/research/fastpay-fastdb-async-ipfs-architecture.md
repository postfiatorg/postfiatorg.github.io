---
title: "FastPay, FastDB, and Async IPFS"
date: 2026-06-29T00:00:00Z
url: "/research/fastpay-fastdb-async-ipfs-architecture/"
summary: "A research architecture for low-latency Post Fiat applications: FastPay for settlement, wallet-authenticated FastDB for realtime state, Post Fiat data ontology for durable replay, and asynchronous IPFS pinning for archival payloads."
description: "Design spec for combining FastPay settlement, wallet-authenticated FastDB, Post Fiat data ontology events, and asynchronous IPFS pinning for task tracking, markets, and other latency-sensitive workflows."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - FastPay
  - PFTL
  - Task Node
  - IPFS
  - Wallet Authentication
  - Data Ontology
draft: false
---

> **Status / byline**
>
> **By:** Post Fiat
> **Date:** June 29, 2026
> **Scope:** Research architecture
> **Not:** A deployed production system, audited security model, final market-matching design, or promise of end-to-end latency

## 1. Executive summary

Latency-sensitive Post Fiat applications should not force every user action through the slowest durable path.

Task tracking, market fills, agent coordination, and realtime work logs need immediate application state. They also need financial finality, wallet-authenticated authorship, and later replay from durable records. These are different jobs. Treating one rail as responsible for all of them creates bad product behavior.

The proposed architecture separates four lanes:

```text
Realtime application lane:
  FastDB, WebSocket/SSE, wallet-authenticated signed events

Settlement lane:
  FastPay owned-object certificates with compact memos and event commitments

Durable ontology lane:
  versioned Post Fiat event schemas projected from signed events, FastPay certs,
  PFTL pointers, and archival payloads

Archive lane:
  encrypted JSON payloads pinned to IPFS asynchronously, replicated into
  first-party IPFS infrastructure, and linked by CID after the hot path
```

The design goal is simple:

> **Users see and act on signed realtime state immediately. FastPay certifies the money movement. IPFS and durable PFTL indexing make the history replayable later.**

This avoids putting IPFS upload, public gateway fetches, or normal account-lane transaction history on the critical path for high-frequency workflows.

## 2. The problem

Normal PFTL transactions already support XRPL-style memos. TaskNode uses those memos to publish compact `pf.ptr/v4` pointers to encrypted IPFS payloads. That is a strong durability pattern:

```text
payload -> encrypt -> pin to IPFS -> CID -> pf.ptr/v4 memo -> PFTL transaction
```

It is good for replay, audit, context restoration, and history.

It is not ideal as the first user-visible event path for fast workflows. A task update, market fill, or agent acknowledgment may need to appear in another wallet in hundreds of milliseconds or a few seconds. Waiting for all of the following is too heavy:

```text
encrypt payload
pin payload
wait for CID
submit account-lane transaction
wait for ledger/history
index transaction
fetch CID
decrypt payload
project state
```

FastPay improves settlement latency, but it does not by itself solve payload latency. A FastPay object can arrive quickly while the memo's CID still points to data that must be fetched from IPFS. If the application needs Charlie to see the task status, trade details, or instruction immediately, the CID fetch should not be the only source of truth for the live UI.

The architecture therefore needs a low-latency application database, but not as an unauthenticated centralized authority. The database should cache and relay wallet-signed facts. It should not be able to forge authorship or invent settlement.

## 3. Terms

**FastPay**
The owned-object payment lane. A wallet spends one or more owned objects by collecting validator votes and applying a certified transfer or unwrap. FastPay gives low-latency financial finality without waiting for the normal account-lane transaction path.

**FastDB**
A wallet-authenticated realtime application database boundary. In practice this is Postgres behind an API, with WebSocket/SSE push and optional Redis/NATS fanout. Wallets do not connect directly to Postgres. They authenticate to the API with wallet signatures and submit signed application events.

**Post Fiat data ontology**
The versioned schema layer that turns signed events, FastPay certificates, PFTL pointer transactions, and IPFS payloads into canonical domain facts: task requested, task accepted, evidence submitted, order filled, reward paid, context revised, and so on.

**Async IPFS pinning**
The archival lane. Encrypted payloads are pinned after, before, or beside the realtime event. The CID is useful for durable replay, evidence, and cross-device hydration, but should not be mandatory before the recipient can see the critical event.

## 4. Core architecture

The proposed write path:

```text
1. Alex creates an application event.
2. Alex signs the event with the wallet key.
3. Alex sends the signed event to FastDB over HTTPS/WebSocket.
4. FastDB validates wallet auth, schema, nonce, and signature.
5. FastDB stores the event and pushes it to Charlie immediately.
6. Alex sends a FastPay transfer whose memo commits to the same event.
7. Validators certify the FastPay transfer.
8. FastDB observes or receives the FastPay certificate and marks the event certified.
9. Full encrypted payload is pinned to IPFS asynchronously.
10. CID is attached to the event and later published or indexed for replay.
```

The recipient experience:

```text
Charlie sees:
  status = received
  source = signed_fastdb_event
  settlement = pending

FastPay quorum arrives:
  status = settled
  source = fastpay_certificate

IPFS CID resolves:
  archive = available
  source = encrypted_ipfs_payload
```

The application does not wait for IPFS before showing Charlie the event. It also does not pretend the event is financially settled before FastPay certification.

## 5. Event binding

Every low-latency application event should have a stable identity and commitment.

Example event envelope:

```json
{
  "schema": "pf.event.task_update.v1",
  "event_id": "evt_...",
  "actor_wallet": "pf...",
  "recipient_wallet": "pf...",
  "created_at_ms": 1782691200000,
  "nonce": "wallet-local-monotonic-or-random",
  "kind": "TASK_UPDATE",
  "body": {
    "task_id": "task_...",
    "action": "accepted",
    "summary": "Accepted task"
  },
  "payload_hash": "sha256:...",
  "previous_event_id": "evt_...",
  "signature": {
    "algorithm": "ML-DSA-65",
    "public_key_hex": "...",
    "signature_hex": "..."
  }
}
```

The canonical event hash should cover the schema, actor, recipient, created time, nonce, body, payload hash, and previous event reference. The server may add receive time, delivery status, database id, and projection metadata, but those fields are not part of the user-signed claim.

The FastPay memo should bind settlement to the same event:

```json
{
  "memo_type": "70662e6576656e74",
  "memo_format": "7631",
  "memo_data": "<compact binary or canonical JSON, hex encoded>"
}
```

Decoded content:

```json
{
  "event_id": "evt_...",
  "schema": "pf.event.task_update.v1",
  "kind": "TASK_UPDATE",
  "payload_hash": "sha256:...",
  "cid": "",
  "flags": ["fastdb_first", "cid_async"]
}
```

If the payload was already pinned, include the CID. If not, leave the CID empty and attach it later through an archive event:

```json
{
  "schema": "pf.event.archive_link.v1",
  "event_id": "evt_archive_...",
  "parent_event_id": "evt_...",
  "payload_hash": "sha256:...",
  "cid": "bafy...",
  "signature": "..."
}
```

The important rule is that the FastPay memo must commit to the same event Charlie saw in the realtime feed.

## 6. Why not put the whole payload in the FastPay memo?

FastPay memos are useful for compact metadata, not full application state.

They should carry:

- event id;
- schema;
- kind;
- amount or semantic summary when needed;
- payload hash;
- optional CID;
- replay flags;
- short task/order/fill identifiers.

They should not carry:

- private task text;
- large evidence;
- screenshots or files;
- full order books;
- private market instructions;
- secrets or recipient-only content.

Large or private payloads belong in encrypted payload storage, pinned to IPFS for replay after the hot path.

## 7. FastDB is not direct Postgres access

Wallet-authenticated Postgres does not mean wallets should connect directly to a database.

The safer shape is:

```text
wallet signs login challenge
-> API verifies wallet signature
-> API issues short-lived session/JWT
-> API validates signed event envelopes
-> API writes Postgres rows
-> API pushes realtime updates to subscribers
```

Postgres remains behind the API. Row-level security can still be useful, especially if using a hosted service, but the primary boundary should be application code that understands wallet signatures, event schemas, FastPay certificates, and replay rules.

FastDB stores:

- signed event envelope;
- canonical event hash;
- actor and recipient wallet;
- event status;
- delivery status;
- FastPay cert hash, if known;
- FastPay created object ids, if known;
- optional CID;
- projection fields for fast UI queries.

FastDB should never be treated as the final source of settlement. Its job is fast relay, indexing, and projection.

## 8. State machine

Events should move through explicit states:

| State | Meaning |
|---|---|
| `received` | FastDB accepted a valid wallet-signed event. |
| `delivered` | Recipient client has received the event through realtime feed. |
| `fastpay_pending` | A matching FastPay transfer is expected but not yet certified. |
| `fastpay_certified` | FastPay certificate reached quorum and matches the event commitment. |
| `archival_pending` | Full encrypted payload is not yet pinned or not yet replicated. |
| `archived` | CID is available and payload hash matches. |
| `rejected` | Signature, schema, replay, settlement, or payload hash validation failed. |

This gives the UI honest labels. A task acceptance can be visible immediately while the settlement badge remains pending. A market fill can be displayed from a signed matching-engine event while settlement finality is verified separately.

## 9. Task tracking workflow

Example:

```text
Alex accepts Charlie's task.
```

Hot path:

```text
Alex signs pf.event.task_update.v1(action=accepted)
FastDB stores and pushes the event to Charlie
Charlie sees "accepted" immediately
```

Settlement path:

```text
Alex sends FastPay payment or stake movement
FastPay memo includes event_id and payload_hash
FastDB marks event fastpay_certified when the certificate arrives
```

Archive path:

```text
Full encrypted task acceptance packet is pinned to IPFS
CID is linked to the event
PFTL/IPFS replay can reconstruct the same state later
```

This separates the human workflow from archival durability. The live product feels immediate, but the signed and settled record remains replayable.

## 10. Market workflow

Markets require stricter sequencing.

A matching engine can be fast, but it must not be unaccountable. The minimum viable pattern:

```text
1. Traders sign orders with wallet keys.
2. Matching engine signs an ordered fill event.
3. FastDB publishes the fill immediately.
4. FastPay settles one or both legs.
5. FastPay memo binds settlement to fill_id and fill_hash.
6. Periodic audit packets commit to the ordered fill log.
7. IPFS archives full fill packets and matching-engine receipts.
```

For markets, FastDB is more than a cache. It is the low-latency venue state. That means it must publish enough signed data for later dispute resolution:

- order id;
- fill id;
- actor wallets;
- side;
- price;
- quantity;
- matching timestamp;
- matching-engine signature;
- settlement cert references;
- previous log hash.

The matching engine may sequence orders, but it should produce an auditable hash chain. FastPay proves settlement. IPFS proves the full archived record. The data ontology explains how those facts reduce into positions, balances, fills, and disputes.

## 11. Async IPFS strategy

There are three CID modes:

| Mode | Use case | Latency profile |
|---|---|---|
| Pre-pinned CID | Planned task packet, prepared market metadata, larger context already known | FastPay memo can include CID immediately. |
| Async CID | User action is time-sensitive and payload can be archived after delivery | UI does not wait for pinning. |
| No CID | Tiny event fully represented by signed inline fields | Durable replay depends on event log and FastPay cert, not IPFS payload. |

For most TaskNode-style workflows, async CID is the best default. The recipient sees the signed event immediately. The full encrypted evidence packet becomes available later.

IPFS pinning should still use the existing durable pattern:

```text
pin to provider
return CID
enqueue first-party replication
verify clean gateway
attach CID to event
publish/archive pointer for replay
```

CID failure must not erase the event or the settlement. It should leave the event in `archival_pending` or `archive_failed` with retry metadata.

## 12. Security model

This architecture has four separate trust claims.

**Authorship**
The event was signed by the claimed wallet key.

**Delivery**
FastDB delivered the event quickly to authorized subscribers. The server can censor, delay, or go down, but it cannot forge wallet signatures.

**Settlement**
FastPay validators certified the owned-object transfer or unwrap. The FastPay certificate must match the event id, payload hash, and expected parties.

**Replay**
The durable ontology can reconstruct the state from signed events, FastPay certificates, PFTL pointer records, and IPFS payloads. FastDB is helpful but not the only record.

Important failure modes:

| Failure | Expected behavior |
|---|---|
| FastDB accepts event but FastPay fails | Show app event as unsigned-settlement or rejected-settlement, depending on workflow. |
| FastPay cert exists but no FastDB event | Index it as settlement-only and wait for matching payload or show a minimal receipt. |
| CID pin fails | Keep event and settlement, mark archive failed, retry pinning. |
| CID resolves to wrong hash | Reject archive link, keep signed event and settlement references. |
| Server attempts to mutate event body | Wallet signature fails. |
| Replay attack | Nonce, event id, previous-event hash, and wallet scoped sequence reject duplicates. |

## 13. Data ontology requirements

The ontology should define canonical facts rather than UI events. Examples:

```text
pf.event.task_request.v1
pf.event.task_update.v1
pf.event.task_submission.v1
pf.event.reward.v1
pf.event.market_order.v1
pf.event.market_fill.v1
pf.event.archive_link.v1
pf.event.settlement_link.v1
```

Each schema should have:

- stable event id;
- actor wallet;
- recipient wallet or audience;
- creation time;
- nonce or sequence;
- payload hash;
- optional CID;
- optional FastPay certificate hash;
- optional PFTL transaction hash;
- previous event reference when ordering matters;
- signature envelope;
- projection rules.

Projection rules are the bridge between raw facts and product state. For example:

```text
task_request + task_update(accepted) + task_submission + reward
-> task projection

market_order + market_fill + fastpay_certified
-> position and fill projection
```

The ontology is allowed to be slower than FastDB. It is the durable replay path, not the first-pixel path for the UI.

## 14. Implementation phases

### Phase 1: FastDB event envelope

- Add signed event envelope schema.
- Add wallet-authenticated API session.
- Store signed events in Postgres.
- Push events over WebSocket/SSE.
- Add replay and nonce protection.

### Phase 2: FastPay memo binding

- Add FastPay memo support in wallet send path.
- Reuse or adapt `pf.ptr/v4` style compact pointer encoding.
- Add `event_id`, `schema`, `payload_hash`, and optional `cid`.
- Add FastPay certificate/activity indexer.
- Mark matching FastDB events as `fastpay_certified`.

### Phase 3: Async archive

- Pin encrypted payloads after the realtime event.
- Attach CID through signed archive-link events.
- Reuse first-party IPFS replication queue.
- Verify CID content hash before marking `archived`.

### Phase 4: Durable replay

- Build reducer from signed events, FastPay certs, pointer transactions, and IPFS payloads.
- Generate task and market projections.
- Add explorer views for FastPay event memos and archive links.
- Add audit reports that prove FastDB projections can be reconstructed from durable inputs.

## 15. Design rule

The useful mental model is:

```text
FastDB is what the product knows now.
FastPay is what settled.
IPFS is what can be replayed later.
The ontology is how those facts become meaning.
```

Do not make the user wait for the archive lane when they need realtime state. Do not let the realtime lane claim settlement it does not have. Do not let the settlement lane carry large private application payloads. Do not let IPFS failure erase signed work.

The combination gives Post Fiat a practical application stack:

- realtime enough for task coordination and markets;
- wallet-authenticated enough to avoid trusting the database for authorship;
- financially final enough through FastPay;
- durable enough through PFTL/IPFS replay.
