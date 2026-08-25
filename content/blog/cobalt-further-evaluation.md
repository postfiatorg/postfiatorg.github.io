---
title: "Cobalt: Further Evaluation"
date: 2026-08-23T00:00:00Z
lastmod: 2026-08-24T00:00:00Z
draft: false
summary: "Deterministic liveness evidence supports activating Cobalt for validator governance on Post Fiat's controlled testnet."
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
  - RippleD
  - XRPL
---

Post Fiat should activate Cobalt as the validator-registry and trust-transition authority on its controlled testnet.

This is a reversible testnet experiment, not a mainnet certification. It moves a qualified governance protocol from shadow operation to limited live authority. Consensus v2 will continue ordering transactions and finalizing blocks. Cobalt will govern validator membership, validator keys, and trust relationships. Its block-control flag will remain false.

The decision standard is whether Cobalt behaves predictably at the current six-validator boundary and can be removed cleanly if live results diverge. Six questions matter:

| Question | Required result |
|---|---|
| Agreement | Participating validators converge on one registry history |
| Quorum liveness | Five of six validators progress in the tested schedules |
| Below-quorum safety | Four of six preserve the current registry |
| Recovery | A lagging or restarted validator recovers the exact history |
| Finality isolation | Consensus v2 remains the sole block-finality protocol |
| Reversibility | A separately authorized transition restores Foundation authority |

The qualification evidence passes all six at the tested boundary. Live activation is the next gate.

## Why Cobalt belongs on the testnet

Foundation governance is the current default authority. It can authorize registry updates, but it does not give the validator set a protocol-checked way to ratify changes across non-identical trust views.

Cobalt adds that capability. Each validator has a declared trust view. The protocol checks whether those views are compatible, whether each relevant group has enough support, and whether a proposed registry transition follows the active rules. The accepted result is a signed, replayable governance history.

Leaving Cobalt in shadow mode would keep producing rehearsal evidence while avoiding the question a controlled testnet exists to answer: can the qualified authority path operate live without disturbing block finality? Activation answers that question with limited blast radius and an exercised return path.

## What the evidence establishes

Determinism, safety, and liveness are separate claims.

- **Determinism:** the same admitted evidence replays to the same registry decision and history.
- **Safety:** incompatible or insufficient support produces no competing accepted registry roots.
- **Liveness:** the configured five-validator quorum progresses under the tested network and fault schedules.
- **Recovery:** a validator that misses history verifies and restores the exact accepted sequence before rejoining.

The controlled-testnet registry contains six validators and uses a five-validator governance quorum. The tests therefore expect progress with five available domains and preservation of the current registry with four.

The [frozen 18-case comparison](https://github.com/postfiatorg/postfiatl1v2/tree/main/benchmarks/cobalt-activate-or-retire/section2-packet) covers compatible views, incompatible views, support boundaries, divergent roots, faults, recovery, and validator changes. The expected outcomes were frozen in an oracle with no production Cobalt dependency, and the production adapters cannot call it. The packet records source commit `01822ecc53ad1cdab50e6c55536fcc7b81aba02a` and SHA256SUMS root `40bc86c9416a1b468f5625a2ff83724c9268f9d49c41007e9b0c4bc70c43c1e1`.

Cobalt passed all 18 cases with:

- zero conflicting registry roots;
- zero validator-outcome mismatches; and
- identical replay for all 17 decision-producing cases.

A registry root is the cryptographic commitment to one validator-registry state. Conflicting roots mean validators accepted incompatible states for the same governance step. Zero conflicts is therefore the direct safety result, while identical replay is the determinism result.

Three tested 20-validator configurations used 90% trust-list overlap:

| Configuration | Outcome |
|---|---|
| Compatible views with sufficient support | Decide |
| Support exactly at the declared boundary | Decide |
| Support below the declared boundary | Preserve the current registry |

These cases show that Cobalt can progress across compatible non-identical views. It halts at the tested support boundary rather than treating every difference in validator trust as a reason to stop.

## Liveness under faults

The [six-domain simulation](https://github.com/postfiatorg/postfiatl1v2/tree/main/benchmarks/cobalt-activate-or-retire/section3-packet) runs the production Cobalt decision and recovery paths across six isolated validator domains. Each domain has its own identity, key, trust view, durable state, message schedule, and failure boundary.

Five available domains progressed. Four available domains preserved the accepted registry. Those are alternative schedules that test the two sides of the quorum boundary.

Across 14 governance rounds, the simulation covered:

- crash and restart;
- delay and message loss;
- duplicate and reordered delivery;
- equivocation;
- partition and healing;
- stale replay;
- validator admission and removal;
- validator-key rotation; and
- trust-view transition.

Every recovering domain reached byte-identical durable history. Cobalt produced zero conflicting roots throughout the fault matrix. The packet records source commit `eb1c84b3e88e710256ab09fce7a90ea501906925` and SHA256SUMS root `9a35119045698754ffdd11eea123bfad03bf2b3c23b700a55f0f539f5152bc18`.

The observed result is precise: progress at the configured quorum, stable state below quorum, and exact recovery under the listed schedules.

## The RippleD difference

A RippleD-style server measures support against its local Unique Node List. That answers a local question: did enough validators I trust support this proposal? It does not answer the network-wide governance question: did validators with different trust views authorize one compatible registry state?

The decisive comparison case, `six-divergent-local-quorums`, isolates that gap without Byzantine validators, unavailable nodes, delay, duplication, reordering, or stale messages.

The six validators form two trust groups:

| Local view | Trusted validators | Local quorum | Supported registry |
|---|---|---:|---|
| Validators 00, 01, 02 | Validators 00, 01, 02 | 3 of 3 | Root A |
| Validators 03, 04, 05 | Validators 03, 04, 05 | 3 of 3 | Root B |

Every validator sees unanimous support inside its own UNL. Validators 00 through 02 therefore accept Root A. Validators 03 through 05 accept Root B. Each decision is locally valid, yet the validator-governance adapter ends with two incompatible accepted registry roots.

That conflict matters even while ledger consensus remains synchronized. A validator registry defines which identities and keys may authorize later governance and participate under the active network rules. Two accepted roots mean the two groups disagree about the authority set from which the next valid transition must descend. Key rotation, validator admission, removal, and future authorization can therefore begin from different histories.

Cobalt evaluates the relationship between the trust views before accepting either proposal. In this case, every cross-group pair is unsafe: three validators on the left multiplied by three on the right produces nine pairs with no shared essential subset satisfying linkage. The production trust-graph gate marks the graph unsafe, all six validators halt the governance transition, no candidate reaches commitment, and the current registry remains authoritative.

| Same input | RippleD-style governance adapter | Cobalt |
|---|---|---|
| Local support | Each group has a valid 3-of-3 quorum | Each group has local support |
| Cross-view compatibility | Outside the local quorum decision | Nine unsafe cross-group pairs detected |
| Accepted result | Root A for one group, Root B for the other | No new root |
| Registry history | Two incompatible accepted states | Current registry preserved |

This is a validator-governance result, not a claim that RippleD ledger consensus forked. The native RippleD CSF control stayed synchronized on one ledger branch in the same packet. The comparison isolates a narrower point: local ledger quorum and globally compatible validator-governance authority are different properties.

Cobalt's advantage is also more precise than “halt when views differ.” The compatible 90%-overlap cases decide successfully. Cobalt permits non-identical trust views when their essential subsets satisfy linkage, then rejects the disconnected topology where two locally unanimous groups could authorize different registry histories.

That is the capability Post Fiat gains: trust compatibility becomes an explicit, signed precondition of validator-governance authority rather than an operating assumption maintained outside the decision itself.

## Consensus v2 remains in control

The [matched finality receipt](https://github.com/postfiatorg/postfiatl1v2/blob/main/benchmarks/cobalt-activate-or-retire/section3-packet/consensus-v2-finality-receipt.json) compares 50 Consensus v2 rounds without Cobalt workload against 50 rounds with the Cobalt workload running for 99.9985% of the integration-lane wall time. Both lanes used the same identities, keys, topology, binary, host, and initial state.

| Lane | Finality p95 |
|---|---:|
| Consensus v2 baseline | 1,617.88 ms |
| Consensus v2 with Cobalt | 1,660.42 ms |

The increase was 2.63%, inside the 5% qualification budget. Fifty rounds make this a focused integration-regression result rather than a performance SLA. The decisive isolation result is architectural: Cobalt remained outside transaction ordering and block finality.

## Residual risk

Finite simulations cannot enumerate every trust graph, Byzantine strategy, WAN schedule, or implementation failure. The finality run is too small to predict long-duration latency. Live service orchestration may expose faults absent from the controlled harness.

Those limits define the next experiment. They support a reversible controlled-testnet activation with explicit stop conditions, while leaving mainnet authorization for a later evidence gate. Continued shadow operation cannot produce evidence from the live authority path.

## Release and cutover

The [release qualification](https://github.com/postfiatorg/postfiatl1v2/blob/main/benchmarks/cobalt-handoff-rehearsal/release-qualification-v1.json) used the optimized binary and replayed the exact 915-block migrated controlled-testnet archive. The disposable qualification environment then exercised a signed future-height activation, six rejected transition cases, a scoped validator-key rotation, and a separately authorized return to Foundation authority.

All 15 handoff gates passed. The release packet's SHA256SUMS root is `f4f2f202111dc327ee590310ba65dc53e0611a578041ba878a3e23298e47a3e2`. The live fleet remained unchanged, and Cobalt authority remains off today.

The controlled-testnet cutover should proceed at a newly authorized future height. Its acceptance conditions are concrete:

- one accepted registry history;
- zero conflicting roots;
- five-of-six progress;
- exact catch-up after interruption;
- Consensus v2 continues finalizing while live latency is compared with the qualification baseline; and
- Cobalt block control remains false.

A conflicting root, failed five-of-six progress, divergent catch-up history, unexpected block authority, or sustained finality regression stops the activation. The last accepted registry remains in force while the qualified transition restores Foundation authority.

## Decision

The evidence supports activation on the controlled testnet. Cobalt makes compatible trust views live, preserves one registry history under faults, recovers deterministically, and stays outside block finality. Continued shadow operation would repeat tests that have already passed while withholding the live governance evidence the testnet is designed to produce.

Mainnet authorization remains a later decision with its own evidence standard.

## Code and evidence

- Trust graph and transitions: [`trust_graph_governance.rs`](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/consensus_cobalt/src/trust_graph_governance.rs)
- Agreement validation: [`rbc_abba_mvba.rs`](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/consensus_cobalt/src/rbc_abba_mvba.rs)
- Ordered governance history: [`dabc_registry.rs`](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/consensus_cobalt/src/dabc_registry.rs)
- Recovery service: [`cobalt_shadow.rs`](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/node/src/cobalt_shadow.rs)
- Authority handoff: [`cobalt_handoff.rs`](https://github.com/postfiatorg/postfiatl1v2/blob/main/crates/node/src/cobalt_handoff.rs)
- Ethan MacBrough, [“Cobalt: BFT Governance in Open Networks”](https://arxiv.org/abs/1802.07240)
- Post Fiat, [“Cobalt on the Devnet: Implementing the Road Not Taken”](/blog/cobalt-implementation-evidence/)
