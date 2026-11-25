---
title: "Post Fiat Layer 1 Roadmap: Requirements and Build Order"
date: 2026-11-25T00:00:00Z
url: "/research/l1-roadmap/"
summary: "The eight Layer 1 priorities from Governance Entry 001, in the order it prescribes, with each stage's intended result, requirements, dependencies, acceptance checks and unknowns. Facts are pinned to postfiatl1v2 commit 693e426e."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Layer 1
  - Roadmap
---

Governance Entry 001 ([network priorities, 9 November 2026](https://github.com/postfiatorg/postfiatorg.github.io/blob/feat/governance-section/content/governance/2026-11-09-network-priorities.md)) prescribes the order of Layer 1 work: devnet stability, ML-DSA-65, Asset-Orchard swaps, SP1 NAV proofs, the replay log, wallet recovery, private swaps, and audits. This page turns that order into requirements and a build sequence. The Task Node board manager creates implementation tasks from it.

**Repository inspected:** [postfiatorg/postfiatl1v2 at `693e426e167a937135f5da55f6093670b76b5376`](https://github.com/postfiatorg/postfiatl1v2/tree/693e426e167a937135f5da55f6093670b76b5376) (main, 25 November 2026).

Each stage separates **Verified** (stated in the repository at that commit, with a link) from **Assumption** (a reading of the governance entry that the repository does not settle). This page sets no dates or budgets.

## How the stages depend on each other

1. **Devnet stability** comes first because every later acceptance check runs on the devnet. A check that passes on an unstable network proves nothing.
2. **ML-DSA-65** is the signature layer under accounts, validators and the PQ spend authorization in stage 7. It must be settled before value-bearing features are built on it.
3. **Asset-Orchard swaps** and **SP1 NAV proofs** together make a NAVCoin: the swap moves it, the proof prices it. Gate Z3 of the [Testnet Path](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/testnet-path.md) needs both.
4. The **replay log** makes decisions and history checkable by anyone. It needs stable blocks (stage 1) to replay.
5. **Wallet recovery** must work before users hold private or NAVCoin balances that only a wallet can reach.
6. **Private swaps** combine stages 2, 3 and 5. They are only as safe as the signatures, swap circuit and recovery under them.
7. **Audits** come last in the order because they review the finished stages 1–7. Audit scoping can start earlier; sign-off cannot come before the code it covers is frozen.

A stage is finished when its acceptance checks pass on the devnet at a recorded commit. The next stage starts after that, except that audit scoping (stage 8) may run alongside.

## 1. Devnet stability

**Intended result.** The six-validator devnet produces blocks, keeps one state root across all validators, serves reads, and survives restarts and rolling upgrades without manual repair.

**Verified.**
- One network runs: `postfiat-wan-devnet-2`, six Foundation-administered validators, quorum 5 of 6 ([Network Status](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/network-status.md)).
- On 25 November 2026 all six reported one tip and one state root on build `04600868` ([Network Status](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/network-status.md)).
- Open defects: RPC reads fail with `storage_writer_busy` while the validator holds the database ([#241](https://github.com/postfiatorg/postfiatl1v2/issues/241)); four node tests fail on main ([#208](https://github.com/postfiatorg/postfiatl1v2/issues/208)).
- The six-clone migration rehearsal (B2) and the qualified-lineage deployment decision (B3) are OPEN ([Testnet Path](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/testnet-path.md)).

**Requirements.** Fix #241 and #208. Close B2 and B3. Make each rollout produce a deployment receipt; the last receipt is from 30 October 2026 ([Network Status](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/network-status.md)).

**Depends on.** Nothing earlier.

**Acceptance checks.** CI is green on main. A rolling upgrade of all six validators completes with one state root before and after. RPC reads succeed during block production. Each rollout has a deployment receipt.

**Unknowns.** Which availability target counts as "stable" (uptime, restart recovery time). Governance Entry 001 does not set one.

## 2. ML-DSA-65 post-quantum signatures

**Intended result.** Every account, validator and governance signature is ML-DSA-65 (FIPS 204), and validator keys are held under a custody process.

**Verified.**
- Accounts and validators sign with ML-DSA-65 ([Network Status](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/network-status.md), [Addresses, Keys And Signatures](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/integrate/addresses-keys-signatures.md)).
- Release gate 3, validator key custody, is OPEN ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).

**Requirements.** Close gate 3: written key-generation, storage, rotation and loss procedures for validator keys. Inventory any remaining non-ML-DSA signature paths (bridges, governance tooling) and either migrate them or document why they stay.

**Depends on.** Stage 1, so key rotation can be rehearsed on a stable devnet.

**Acceptance checks.** A validator key rotation is rehearsed on the devnet with no loss of quorum. The signature inventory lists every signing path and its algorithm.

**Unknowns.** Assumption: "ML-DSA-65" in the governance entry means completing custody and the inventory, because the signature switch itself is already in place.

## 3. Asset-Orchard swaps

**Intended result.** Two assets swap atomically in one shielded transaction, the circuit proves each asset balances, and an independent reviewer has checked the value binding.

**Verified.**
- The swap circuit's `h_action` value binding (item P13) has a prepared audit scope; independent review is required before P13 can close ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).
- Public submission of shielded actions is off on every validator ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).
- Gate Z3, NAVCoin swaps working end to end, is OPEN ([Testnet Path](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/testnet-path.md)).

**Requirements.** Close P13 with an independent review. Run full round trips (deposit, mint, swap, burn, withdraw) on the devnet. Decide when public submission of shielded actions turns on.

**Depends on.** Stages 1 and 2.

**Acceptance checks.** Gate Z3 closes with recorded round trips. The P13 review is published. Conservation holds atom for atom in every recorded swap.

**Unknowns.** Who performs the P13 review, and whether public shielded submission turns on before or after stage 8.

## 4. SP1 proofs of NAVCoin reserve valuations

**Intended result.** Every NAVCoin epoch publishes a NAV computed by an SP1 program from reserve accounts read at a fixed block, and validators verify the proof before accepting the NAV.

**Verified.**
- The proof-of-reserves design and current NAVCoin infrastructure are documented ([NAVCoin proof of reserves](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/business/navcoin-proof-of-reserves.md), [current infrastructure](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/business/navcoin-current-infra.md)).
- Release gate 13, SP1 guest/program reproduction and circuit review, is OPEN ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).

**Requirements.** Make the SP1 guest reproducible from source to the verifying key. Document each reserve leg's trust level. Close gate 13.

**Depends on.** Stage 1 for verification on the devnet; stage 3 for the NAVCoin round trip in Z3.

**Acceptance checks.** Anyone can rebuild the SP1 program from source and get the published verifying key. A NAV epoch is accepted on the devnet only with a valid proof, and a tampered packet is rejected.

**Unknowns.** Which reserve legs stay attested rather than proven, and for how long.

## 5. Replay log

**Intended result.** Anyone can replay a recorded decision or the chain's history and get the same bytes.

**Verified.**
- Byte-for-byte replay of chain history is a stated design rule ([storage scaling research spec](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/architecture/storage-scaling-research-spec.md)).
- Exact replays against a frozen binary are complete for storage qualification (item A3, DONE) ([Testnet Path](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/testnet-path.md)).
- Gate Z2, the AI-governance decision made and live, is OPEN ([Testnet Path](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/status/testnet-path.md)).

**Requirements.** Publish the hash-chained log of governance questions and answers with the inputs needed to replay each entry. Give it a stable format, and tooling that replays one entry end to end.

**Depends on.** Stage 1. Stage 2 if log entries are signed.

**Acceptance checks.** A third party replays a published entry on their own hardware and gets identical output bytes. The log's hash chain verifies from the first entry.

**Unknowns.** Assumption: "the replay log" in the governance entry is the hash-chained log of governance decisions described in its status section. The repository does not define the term. If chain-history replay is meant instead, stage 1's replay tooling covers most of it.

## 6. Wallet recovery

**Intended result.** A user who loses a device recovers transparent, private and NAVCoin balances from their recovery material alone.

**Verified.**
- Wallet documentation is in [docs/wallets](https://github.com/postfiatorg/postfiatl1v2/tree/693e426e167a937135f5da55f6093670b76b5376/docs/wallets) and [RPC and wallets evidence](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/evidence/rpc-and-wallets.md).
- FastPay recovery evidence, release gate 5, is OPEN ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).

**Requirements.** Recovery covers every balance type, including shielded notes. Close gate 5. Write a recovery runbook a non-developer can follow.

**Depends on.** Stage 2 (key derivation), stage 3 (shielded notes) and stage 4 (NAVCoin balances).

**Acceptance checks.** A wallet is wiped and restored on a fresh device, and every balance and spendable note returns. The recovery runbook is followed by someone who did not write it.

**Unknowns.** Whether social or multi-device recovery is in scope, or recovery-phrase restore only.

## 7. Private swaps

**Intended result.** Users swap NAVCoins and other assets privately, with exact conservation, through the public wallet.

**Verified.**
- Private swap production hardening is a deferred plan ([A666 private swap hardening spec](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/deferred-plans/A666-PRIVATE-SWAP-PRODUCTION-HARDENING-SPEC-20260730.md)).
- Release gates 14 (deployed privacy capture review) and 21 (privacy production burndown) are OPEN ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).
- Public submission of shielded actions is off ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).

**Requirements.** Reopen and finish the hardening spec. Close gates 14 and 21. Settle the post-quantum path: PFSH03 is a production candidate in [#232](https://github.com/postfiatorg/postfiatl1v2/pull/232), disabled until a governance activation vote.

**Depends on.** Stages 2, 3 and 6.

**Acceptance checks.** A private swap through the public wallet conserves value atom for atom. Gates 14 and 21 close. Turning private payments on goes through a governance vote.

**Unknowns.** Whether the first production private swaps use Orchard or PFSH03.

## 8. Audits

**Intended result.** Independent reviewers have audited consensus, circuits, contracts and bridges, and the findings are fixed or accepted in writing.

**Verified.**
- No external security audit is recorded in the repository ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).
- Open audit-related release gates: 11 (`h_action` external audit), 12 (specialist consensus, circuit, contract and bridge review), 13 (SP1 reproduction) and 15 (external bridge verifier) ([Security](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/index.md)).
- Audit sizing exists: 225,070 nonblank core source lines at `1f478e0c` ([Core feature LOC inventory](https://github.com/postfiatorg/postfiatl1v2/blob/693e426e167a937135f5da55f6093670b76b5376/docs/security/core-feature-loc-audit-inventory.md)).

**Requirements.** Fix the scope for each audit to frozen commits from stages 1–7. Engage reviewers. Publish reports and the response to each finding.

**Depends on.** Code freeze of the stage each audit covers. Scoping may start earlier.

**Acceptance checks.** Each gate in 11, 12, 13 and 15 links a published report. Every finding has a fix commit or a written acceptance.

**Unknowns.** Which firms review, and whether the PFSH03 cryptography gets its own review separate from gate 12.
