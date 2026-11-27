---
title: "Post-Human Governance in Public: Packets, Carry-Over & Replayable Rulings"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How Post Fiat runs on-demand 30-minute Hive governance sessions with automatic protocol snapshots, direct carry-over accountability, postfiatl1v2 anchoring, and offline verification."
author: "Post Fiat"
categories:
  - Governance
tags:
  - Post Fiat
  - Hive Governance
  - postfiatl1v2
  - IPFS
  - Nostr
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Most crypto governance is theater. Proposals get written in private Discord rooms, voted on by a handful of token whales, and forgotten two weeks later. Nobody checks whether last month's promises actually shipped.

Post Fiat is building post-human governance in public around one simple loop: **publish a signed information packet, act on it in a public session, freeze the record on chain, and force the next session to score what actually got done.**

## How a Session Runs

There is no fake calendar cadence and no auto-generated bounty machine. Whenever I start a governance session in Task Node, six things happen in order:

1. **One-height protocol snapshot:** `pf-gov-collector` pins all `postfiatl1v2` reads to a single finalized block height — chain tip, active validator set, bridge and NAVCoin supply, Cobalt status, and Task Node health — and saves every raw RPC response alongside its SHA-256 hash.
2. **Automatic carry-over from last time:** The new packet loads every deliverable from the previous session's signed minutes. I have to mark each item publicly as `done`, `in_progress`, `not_done`, or `dropped`. Either the work happened or it didn't.
3. **Signed opening packet:** I write a plain-English brief, list open questions and proposed decisions, and sign `pf.governance.packet.v1` with my wallet. Task Node pins the canonical JSON (RFC 8785) wrapped in a Pillar 2 envelope to IPFS and anchors its binary CID on `postfiatl1v2` via a `pf.ptr` v5 memo (`kind = 12`).
4. **30-minute dedicated Hive room:** A fresh room opens for the session so normal Hive Chat keeps moving. I choose who can post (`founder_only`, `allowlist`, or `all_members` restricted to registered Task Node accounts) and set the event-driven AI facilitator mode (`off`, `agenda`, or `interactive`, targeting under 10 seconds per reply).
5. **Frozen transcript and two-pass minutes:** When the room closes, Task Node catches up from Nostr relays, applies deterministic inclusion and rate-limit rules, orders messages by server receipt sequence, and pins the entire raw signed event bundle to IPFS. Minutes draft in two separate passes: **Pass 1** drafts decisions and next deliverables using *only* my signed packet, agenda prompts, and my signed messages — community text is structurally excluded so prompt injection cannot sneak a fake decision into the minutes. **Pass 2** summarizes community input separately as quoted data. I review, edit if needed, and sign the final minutes with my wallet.
6. **Optional flagged deterministic rulings:** Normal session facilitation runs on Task Node's standard inference stack with zero rented GPUs. Only decisions I explicitly check for deterministic governance go to our read-only runner on Google or Vast, which returns replay hashes for my wallet to anchor on chain. The runner never holds a signing key.

## Live Session Evidence

- **Session ID:** `[INSERT LIVE SESSION ID AFTER UAT]`
- **Opening packet anchor (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Frozen transcript & signed minutes anchor (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Flagged deterministic ruling anchor (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Explorer Governance Timeline:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

## Verify Any Session Yourself

You do not have to trust Task Node's database or third-party Nostr relays. The explorer ignores any `kind = 12` memo not signed by the pinned founder authority key, and anyone can verify a full session offline using only a `postfiatl1v2` RPC and a public IPFS gateway:

```bash
verify-governance-session \
  --session-id [INSERT LIVE SESSION ID AFTER UAT] \
  --rpc https://rpc.postfiat.org \
  --ipfs-gateway https://ipfs.postfiat.org
```

Add `--check-relays wss://relay.postfiat.org` to compare live Nostr relays against the frozen transcript manifest and check for server omissions.

For the full packet schema, snapshot derivation rules, and verification steps, read the [Hive Governance Packet & Verification Guide](/docs/hive-governance/).
