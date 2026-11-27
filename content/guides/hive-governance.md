---
title: "Hive Governance Packet & Verification Guide"
url: "/docs/hive-governance/"
type: "page"
layout: "single"
kicker: "Pillar 1 · Hive Governance"
date: 2026-11-27
summary: "Canonical schema, protocol-state snapshot method, carry-over accountability rules, two-pass minutes drafting, postfiatl1v2 anchoring, and offline verification for Post Fiat Hive governance sessions."
---

Post Fiat runs governance as a public loop of signed information packets, time-boxed live sessions, frozen transcripts, and on-chain anchors on `postfiatl1v2`. Anyone can inspect a session archive and verify every artifact offline without trusting Task Node's database or third-party Nostr relays.

## 1. End-to-End Session Lifecycle

Governance sessions run on demand whenever the founder opens one in Task Node. There is no fixed calendar schedule and no synthetic missed-session penalty state.

Every session follows a strict state machine:

```text
Draft -> Live -> Frozen -> InReview -> Anchoring -> Published
                                              \-> RulingPending -> RulingAnchored (optional)
```

Sessions cancelled before publication enter `Aborted`. Editing draft minutes increments a revision counter and never mutates the frozen transcript.

1. **Snapshot & Carry-Over (`Draft`):** `pf-gov-collector` pins all `postfiatl1v2` RPC reads to a single finalized `block_height` and loads the previous published session's deliverables list.
2. **Packet Publication (`Live`):** The founder marks every carry-over item (`done`, `in_progress`, `not_done`, or `dropped`), adds the session brief, open questions, and proposed decisions, and signs `pf.governance.packet.v1` with their wallet. Task Node pins the canonical artifact to IPFS and anchors the CID on `postfiatl1v2`.
3. **30-Minute Session Room (`Live`):** Task Node opens a dedicated `hive_group_channels` room and posts an announcement card in main Hive Chat. Main Hive Chat stays open throughout.
4. **Transcript Freeze (`Frozen`):** When the founder closes the room (or the 30-minute timer expires), Task Node runs a final Nostr relay EOSE catch-up back to session-open time, applies canonical inclusion rules, and freezes the ordered transcript bundle.
5. **Two-Pass Minutes & Wallet Approval (`InReview` -> `Anchoring` -> `Published`):** Task Node drafts minutes and next deliverables, the founder reviews and signs with their wallet, and Task Node pins and anchors both the transcript bundle and signed minutes on `postfiatl1v2`.
6. **Optional Flagged Deterministic Ruling (`RulingPending` -> `RulingAnchored`):** Only decisions explicitly checked with `run_deterministic_ruling` are exported to the deterministic runner (Google setup or Vast on demand).

## 2. Authority Binding & Carry-Over Accountability

### Founder Authority Binding

At launch, session opening and minutes approval are **founder-only (1-of-1)**. The approval record includes `signer_set_id` and `threshold` fields so multi-sig stewards can be added later without changing the schema.

The founder's official `postfiatl1v2` address is pinned in the block explorer and verifier configuration. Every wallet-signed `pf.governance.packet.v1` embeds the founder's authorized `nostr_pubkey` (upgrading to a native [Pillar 6 on-chain identity](/docs/onchain-identity/) once minted). The explorer renders only `GOVERNANCE` anchors signed by the pinned authority key; outsider transactions with `kind = 12` memos are ignored.

### Direct Carry-Over (No Auto PFT Bounties)

Governance sessions do not generate automatic PFT bounties from minutes. Instead, every new session packet automatically instantiates with the previous session's `next_deliverables[]` list. Each prior deliverable requires an explicit public status in `previous_deliverables_status[]`:

- `done`
- `in_progress`
- `not_done`
- `dropped`

## 3. Snapshot Methodology (`pf.governance.snapshot.v1`)

`pf-gov-collector` eliminates torn reads by pinning every `postfiatl1v2` RPC call to one finalized `block_height`.

| Snapshot Field | Data Captured | Integrity Record |
| --- | --- | --- |
| `chain_state` | `postfiatl1v2` status, ledger tip, active validator set | RPC source, `block_height`, UTC timestamp, SHA-256 of raw response |
| `bridge_and_nav` | Bridge status and NAVCoin supply state at pinned height | RPC source, `block_height`, UTC timestamp, SHA-256 of raw response |
| `cobalt_state` | Current Cobalt status and latest dynamic-UNL scoring verdict | Source URL, height/timestamp, SHA-256 of raw response |
| `tasknode_health` | Task Node `/api/system/status` | Source URL, UTC timestamp, SHA-256 of raw response |
| `prior_deliverables` | Deliverables copied from the last published `pf.governance.minutes.v1` | Prior session ID, CID, and `postfiatl1v2` anchor tx hash |

Raw responses are pinned alongside the snapshot (within the 16 MiB IPFS cap) so independent verifiers can re-derive every field from raw inputs.

## 4. Packet Schema & `postfiatl1v2` Anchoring

All governance artifacts are serialized as deterministic canonical JSON (**RFC 8785 / JCS**), wrapped in a signed [Pillar 2 `pf.msg.v1` envelope](/docs/message-protocol/) (`body_encoding = CANONICAL_JSON`), pinned as IPFS CIDv1 `raw` blocks, and anchored on `postfiatl1v2` using standard `payment_v2` memos (`pf.ptr` v5).

```json
{
  "schema": "pf.governance.packet.v1",
  "session_id": "gov-2026-11-27-01",
  "founder_account": "pftl1...",
  "nostr_pubkey": "<64-hex-x-only-pubkey>",
  "signer_set_id": "founder-1of1-v1",
  "threshold": 1,
  "snapshot_cid": "bafkrei...",
  "snapshot_sha256": "<64-hex>",
  "title": "Session title",
  "summary": "Plain-English summary of changes since the last session.",
  "previous_deliverables_status": [
    {
      "deliverable_id": "deliv-001",
      "status": "done",
      "note": "Merged and verified on devnet-2."
    }
  ],
  "open_questions": ["Question 1", "Question 2"],
  "proposed_decisions": [
    {
      "decision_id": "dec-001",
      "proposal": "Exact proposal text",
      "run_deterministic_ruling": false
    }
  ],
  "attachments": []
}
```

### Anchor Memo Format (`pf.ptr` v5)

Each anchor memo carries:

- **Memo type:** `pf.ptr`, format `v5` (lowercase hex protobuf bytes, `<= 256` bytes; typical size ~110 bytes)
- **CID:** 36-byte binary `cid_bin`
- **Content kind:** `GOVERNANCE = 12`
- **Thread ID:** `session_id` (lets the block explorer group opening packet, frozen transcript, signed minutes, and optional deterministic ruling into one timeline)

Anchors are tracked idempotently by `(session_id, schema, sha256)`. If an anchor transaction expires before inclusion, retry constructs a new transaction with the current account sequence over the exact same CID. An anchor marks complete only after an accepted `postfiatl1v2` receipt and pin confirmation on at least two independent pinners or gateways.

## 5. Session Room Rules, Anti-Spam & Prompt-Injection Boundary

### Session-Open Toggles

When opening a room, the founder signs a session-open event with three controls:

- **Who can post:** `founder_only`, `allowlist` (for example, active validators), or `all_members` (registered Task Node accounts only; arbitrary unauthenticated Nostr pubkeys are never admitted). When `allowlist` or `all_members` is active, the session-open event commits the CID and SHA-256 of the pinned eligible-pubkey snapshot.
- **AI facilitator mode:** `off`, `agenda` (steps through packet questions in order), or `interactive` (asks structured follow-ups).
- **Session length:** 30 minutes default; founder may extend or close early.

### Rate Limits & Turn Budget

- **Non-founder rate limit:** 1 message per 15 seconds per registered account, max 10 messages per non-founder account per session. Founder is exempt.
- **Facilitator latency:** Event-driven on new messages, targeting `< 10` seconds per reply (replacing the 60-second poll loop).
- **Turn budget isolation:** Maximum 25 facilitator turns per session — **15 turns reserved strictly for founder/agenda prompts** and at most **10 turns** for community follow-ups.

### Canonical Transcript Inclusion

At freeze, an event enters the official transcript only if:

1. Its Nostr BIP-340 signature is valid.
2. It targets the session's `hive_group_channels` room.
3. Its author appears in the pinned eligible-pubkey snapshot.
4. Task Node received it between session open and session freeze within per-account rate limits.

Messages are ordered by Task Node's server receipt sequence (preventing backdated client timestamps). Excluded events are recorded by event ID with explicit reason codes. The transcript bundle pins the manifest, eligible-pubkey snapshot, every raw signed Nostr event, and a readable Markdown transcript to IPFS so history never depends on live Nostr relays.

### Two-Pass Minutes Drafting (Structural Prompt-Injection Boundary)

Minutes generation runs in two isolated passes so untrusted community text cannot inject decisions or deliverables:

- **Pass 1 (`previous_deliverables_review[]`, `decisions[]`, `next_deliverables[]`):** Sees **only** the founder-signed packet, agenda prompts, and founder-signed messages. Community messages and attachments are excluded from Pass 1 context.
- **Pass 2 (`community_input[]`):** Summarizes community messages separately as quoted data.

Every final approval requires the founder's explicit wallet signature; the server never signs minutes on the founder's behalf.

## 6. Custody-Safe Deterministic Rulings

When a decision is flagged `run_deterministic_ruling: true`, Task Node exports the pinned snapshot, founder brief, and signed minutes to the deterministic governance runner on our Google setup or Vast on demand.

The runner is **read-only compute and never holds a founder signing key**. It returns the replayable ruling artifact and replay hashes to `RulingPending`. The founder reviews the output and signs the `RulingAnchored` transaction from their own wallet.

## 7. Independent Offline Verification (`verify-governance-session`)

Anyone can verify a published governance session using only public IPFS gateways and a `postfiatl1v2` RPC endpoint.

```bash
# Deterministic offline verification (IPFS + postfiatl1v2 RPC only)
verify-governance-session \
  --session-id gov-2026-11-27-01 \
  --rpc https://rpc.postfiat.org \
  --ipfs-gateway https://ipfs.postfiat.org \
  --founder-account pftl1...

# Optional best-effort Nostr relay check to spot potential server censorship
verify-governance-session \
  --session-id gov-2026-11-27-01 \
  --rpc https://rpc.postfiat.org \
  --ipfs-gateway https://ipfs.postfiat.org \
  --founder-account pftl1... \
  --check-relays wss://relay.postfiat.org
```

### What Deterministic Verification Checks

1. Anchor transactions on `postfiatl1v2` were signed by the pinned `founder_account` and carry valid `pf.ptr` v5 memos with `kind = 12` and matching `thread_id`.
2. Every fetched IPFS raw block matches its binary `cid_bin` and envelope ML-DSA-65 signature over the exact transmitted bytes.
3. The founder's embedded `nostr_pubkey` matches the session-open event and founder messages in the transcript.
4. Every included transcript event has a valid BIP-340 signature, belongs to the pinned eligible-pubkey snapshot, and respects per-account rate limits.
5. Snapshot fields re-derive cleanly from the pinned raw RPC/HTTP responses.
6. Any anchored deterministic ruling matches its committed replay hash and references the exact snapshot and minutes CIDs.

The optional `--check-relays` flag is separated cleanly from deterministic verification: it queries live Nostr relays for events targeting the session room and flags any valid, in-window events missing from the frozen manifest.
