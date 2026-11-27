---
title: "The Post Fiat L1v2 Validator & RPC Program"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How outside operators run Post Fiat L1v2 validators and read-replica RPC nodes from one signed binary—with no stake or bond, SSH monitoring, latency-fair uptime, and real research rewards."
author: "Post Fiat"
categories:
  - Validators
tags:
  - Post Fiat
  - Validators
  - postfiat-node
  - RPC
  - Finance Hub
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Moving `postfiatl1v2` from six Foundation nodes to an outside validator network starts with respecting operators' time. You should not need five internal runbooks, two separate binaries, or a six-figure token bond just to run a reliable node.

## What Active Validators Earn (No Stake, No Bond)

Post Fiat L1v2 validator admission is **stake-free and bond-free**. Approved operators who stay active in the on-chain registry and maintain uptime earn three things per operator:

1. **Post Fiat Finance Hub access** — ~60 GoodAlexander company and crypto models, the daily **Today** desk, **Goodbrief**, and the GoodAlexander Library.
2. **GoodAlexander Research API keys** — programmatic access reserved strictly for active validators.
3. **$20/month in Task Node USD credit** — usable directly on Task Node (including Deep Research), granted once per operator across old and new chains via Pillar 6 on-chain identity (no multi-node farming).

## One Binary for Validators and RPC

There is no separate RPC codebase. Validators, private loopback RPC servers, and opt-in public TLS read-replica RPC endpoints all run the exact same **`postfiat-node`** binary (`linux-x86_64` and `linux-aarch64`).

Every tagged release is co-signed by **2-of-3 offline ML-DSA-65 release keys** with pinned catch-up checkpoints, checksums, systemd units, and SBOMs. Three operational tools make day-two ops boring by design:

- **`postfiat-node upgrade`:** Checks `>= 2x` free disk space, verifies 2-of-3 release signatures, backs up chain state only, swaps the binary, health-checks, and rolls back automatically on failure — while **never** touching `/var/lib/postfiat/signer-guard/`, the immutable double-sign guard directory owned by the isolated `postfiat-signer` OS user. Upgrades are always operator-initiated; nodes never auto-reboot mid-consensus.
- **`postfiat-node top`:** A read-only SSH terminal dashboard showing block height, peer health, recent vote participation, upcoming activation countdowns, signer guard health, disk usage, and live Task Node eligibility. Zero web port to expose.
- **Consensus-isolated RPC (`< 250ms` p95 reads):** Public RPC and private-action admission run in a separate rate-limited read-replica process with dedicated cgroups so public read floods can never stall consensus voting. The Foundation operates the first two public RPC endpoints so Mac shielded users work on day one; outside validators can opt in anytime.

## Latency-Fair Uptime and Active-Liveness Enforcement

Counting only fast-quorum `precommit_qc.votes` quietly kicks geographically distant validators out of the set because closer nodes close the quorum first. Instead, **three independent geographically distributed observers** credit every valid signed vote or consensus heartbeat submitted within each block-height round window and sign the `postfiat-validator-uptime-v1` feed (2-of-3 observer agreement required).

To keep Finance Hub, API keys, and the monthly credit active:

- **Day-0 ramp-in:** Newly ratified validators unlock access immediately on registry inclusion.
- **Steady state:** Sustain **`>= 95%`** participation over `25` of `30` completed height-days.
- **14-day grace & fast recovery:** Falling below 95% enters a 14-day grace period; sustaining `>= 95%` for **3 consecutive height-days** restores active status immediately.
- **Revocation:** If grace expires unrecovered, Finance Hub disables, active Research API keys invalidate immediately, and the `$20/mo` credit pauses.

## Rollout Plan & Live Rehearsal Evidence

Our first outside cohort (`G0`) onboards old-chain Dynamic UNL validators via `IdentityReceiptV1` as we launch public testnet (`n >= 12`) and scale Foundation nodes down to at most 2 correlated seats. New operators then enter through deterministic Admission Policy V1 and validator ratification.

- **Clean-host rehearsal ratification tx (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Signed release & `postfiat-node upgrade` verification:** `[INSERT LIVE RELEASE TAG & TX HASH AFTER UAT]`
- **`postfiat-node top` & Task Node connect screenshot:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Start from the single canonical [Run a Validator Guide](/run-a-validator/).
