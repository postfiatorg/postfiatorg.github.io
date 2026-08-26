---
title: "Cobalt: Further Evaluation"
date: 2026-08-23T00:00:00Z
lastmod: 2026-08-26T00:00:00Z
draft: false
summary: "Cobalt remains active on Post Fiat's controlled devnet after six adversarial experiments and live authority drills."
aliases:
  - /cobalt-further-evaluation/
  - /posts/cobalt-further-evaluation/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - L1
  - Cobalt
  - Governance
  - Consensus
  - Security
---

Cobalt remains active as the validator-registry and trust-graph ratification authority on Post Fiat's controlled devnet. It has held that bounded role since height 916. Consensus v2 still orders and finalizes blocks.

That sentence needs two qualifications up front. A separate layer decides which validators deserve trust; Cobalt ratifies changes against those declared trust views. Current proposals and authorizations originate from Foundation-administered validators. The result described here proves protocol capability, not operator decentralization, mainnet readiness, or provider independence.

The adversarial-verification campaign closed with **KEEP_ACTIVE** after six experiments. It attacked trust-graph agreement, Byzantine schedules, durable recovery, block-finality isolation, the live authority-transition path, and the proposal-source boundary. Every required experiment passed.

## What was attacked

The campaign used independent oracles, generated trust graphs, signed Byzantine evidence, schedule search, tampered histories, forged catch-up material, governance pressure during block finality, and live controlled-devnet drills.

| Experiment | Question | Result |
| --- | --- | --- |
| E1 | Does production agree with an independent oracle across generated trust graphs? | Passed |
| E2 | Can Byzantine validators or searched message schedules create conflicting roots, false accepts, or false halts? | Passed |
| E3 | Can tampered durable state or forged catch-up history rejoin as accepted state? | Passed |
| E4 | Can governance stress stop, fork, or materially regress Consensus v2? | Passed |
| E5 | Do the signed live rollback, return, rejection, and stolen-key paths behave as specified? | Passed |
| E6 | Is the proposal source decentralized, or does that require a separate milestone? | Separate milestone required |

The packets are checksum-bound in the [public repository](https://github.com/postfiatorg/postfiatl1v2/tree/main/benchmarks/cobalt-adversarial-verification). Each has its own verifier.

## Agreement across generated trust graphs

E1 built an oracle from the formal essential-subset, strong-support, and linkage rules without importing production Cobalt or the first oracle. The generated corpus covered 10,240 deterministic cases spanning six to 20 validators, randomized view shapes, and named subset/linkage boundaries.

Production and both independent oracles agreed on every case. Compatible graphs decided one root. Incompatible graphs halted without mutating the accepted registry. The packet root is a9e99f03ace2b9e76bdfa1241e9bb47dc622a6ca6ea3f49c91cde37f64359975.

## Byzantine validators and searched schedules

E2 combined RBC, ABBA, MVBA, and DABC equivocation with selective withholding, changing trust views, competing proposals, late votes, re-proposals, partitions, delay, drop, duplication, and reordering.

All 108 validator/strategy cases and 442,368 searched event schedules passed. The campaign verified 120 signed evidence pairs and observed:

- zero conflicting registry roots;
- zero false accepts;
- zero false halts;
- zero synchrony-bound violations; and
- zero rejected-state mutations.

The packet root is 8742d9603621408339d99c3d9fcc1ba8cc43dafdc900acdfccbf86cc60d7cba3.

## Recovery from adversarial history

E3 attacked disposable clones bound to the live registry root. It truncated, padded, reordered, and modified durable history; submitted fabricated transitions and wrong-root certificates; omitted the latest update from catch-up; interrupted transfer; and switched recovery peers.

All 24 durable-history tamper cases and 18 forged catch-up cases rejected with named reasons and no durable mutation. All six interrupted recoveries resumed from a second honest peer and restored byte-identical accepted history without manual repair. The packet root is 9302b3555ab9091b2cae9b2d372d0548fe9f2fb1e67be43dfb3f63d89140b600.

## Consensus v2 under governance stress

E4 ran 500 baseline and 500 attack-lane block-finality rounds from the same signed initial state, six-validator topology, full-vote policy, binaries, and CPU allocation.

Both lanes converged independently at height 501. Consensus v2 never stopped or forked. Baseline wallet-to-finality p95 was 14,133.57 ms; attack-lane p95 was 14,197.47 ms. The increase was 0.4521%, inside the locked 5% budget.

The attack lane completed 47 governance-stress runs covering 940 proposals, 329 safe halts, and 329 view changes. It recorded 987 boundary rejections, 846 named limit rejections, 752 flood rejections, and 12 automatic validator restarts. No manual operator action was required.

Two harness failures are preserved in the packet. One retry window ended before a deliberate restart outage; the other incorrectly compared exact hashes across independent runs with randomized authentication. Neither failure observed a fork or durable divergence. The harness was corrected and the unchanged 500+500 corpus reran cleanly. The packet root is 93ba3db0bcc145144713088b612606fbb3b92c0f542809f258da49a555c14508.

## Live authority drills

E5 exercised the actual controlled-devnet authority lane from heights 920 through 924.

The first signed rollback at height 920 and return at height 921 both committed. The return used a trust binding that did not match the protocol-native post-return graph. No conflicting root, fork, or finality interruption occurred, but that pair was not used as the final gate. The accepted history and remediation are retained rather than erased.

A corrective signed rollback committed at height 922. A separately authorized return to Cobalt committed at height 923 with the correct protocol-native trust binding. Those are the final-gate rollback and return pair.

At height 924, five current validators authorized a legitimate validator-5 key rotation. Validator 5's treated-as-stolen old key did not participate in that authorization quorum. The replacement key was staged only after the registry update committed, and a retry with the old key rejected before write because it no longer matched the current registry.

All nine required negative cases rejected without durable governance or registry mutation:

- early transition;
- stale transition;
- replayed transition;
- wrong registry root;
- cross-chain transition;
- mixed authority;
- new-set self-authorization;
- replayed rollback; and
- stolen-key rotation.

All six validators accepted one height-920-through-924 history. Every block had at least the five required Consensus v2 votes. The final observation found all validator, RPC, and advisory shadow services active and converged at height 924. Cobalt was active for validator-trust governance; Consensus v2 remained block finality.

The E5 packet root is 0695284a7b38ac0129c47e1242f4a2227ad25096147920e79569a924e5f3b3db.

## What held

The campaign supports a precise conclusion:

- incompatible trust views did not produce competing accepted roots;
- Byzantine strategies and searched schedules did not create false decisions;
- tampered recovery material did not rejoin accepted history;
- governance stress did not stop or fork Consensus v2;
- the signed live return path restored Cobalt after rollback;
- negative and stolen-key attempts rejected without durable mutation; and
- six validators converged on one accepted live history.

Cobalt's block-control flag remained false throughout. This was a validator-trust governance result, not a change to transaction ordering or block finality.

## What was fixed

The campaign found and corrected several implementation and harness defects:

- post-rotation DABC ratification now follows the prior committed ratification anchor across registry-root changes;
- the live helper resolves legacy validator sets from the active count when the explicit ID vector is absent;
- already-compact decision certificates are no longer compacted a second time;
- the E4 restart window covers the deliberate outage; and
- the E4 comparator checks convergence within each independently authenticated lane instead of requiring identical cross-lane hashes.

The unchanged affected corpora passed after remediation. The live authority history preserves the initial h920/h921 pair and the corrective h922/h923 pair.

## What remains open

E6 concluded that operator decentralization is not established by these tests. Foundation administration still originates the current proposals and controls the validator authorization custody boundary. That is disclosed, not treated as a protocol pass.

A separately locked follow-on milestone must establish a non-Foundation proposal path and a trust graph in which no single administrator can reach quorum or block it alone. Mainnet authorization, HSM-backed validator custody, public peer discovery, and production storage remain separate release gates.

## Decision

The adversarial result is **KEEP_ACTIVE** for the controlled devnet.

This decision is bounded to Cobalt's validator-registry and trust-graph ratification scope. It does not authorize Cobalt to finalize blocks, does not prove operator decentralization, and does not authorize mainnet use.

Rollback remains reserved for a live conflicting root, failed five-of-six progress under an honest majority, divergent catch-up history, unexpected block authority, or sustained Consensus v2 finality regression. No such stop condition was observed.

## Code and evidence

- [Adversarial verification packets](https://github.com/postfiatorg/postfiatl1v2/tree/main/benchmarks/cobalt-adversarial-verification)
- [Live E5 authority-drill packet](https://github.com/postfiatorg/postfiatl1v2/tree/main/benchmarks/cobalt-adversarial-verification/e5)
- [Cobalt authority handoff](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/node/src/cobalt_handoff.rs)
- [Cobalt decision certificate](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/node/src/cobalt_authority_certificate.rs)
- [Cobalt trust-graph governance](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/consensus_cobalt/src/trust_graph_governance.rs)
- Ethan MacBrough, [“Cobalt: BFT Governance in Open Networks”](https://arxiv.org/abs/1802.07240)
