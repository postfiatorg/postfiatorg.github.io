---
title: "Cobalt: Further Evaluation"
date: 2026-08-23T00:00:00Z
draft: false
summary: "A matched, deterministic evaluation of Post Fiat's Cobalt implementation against RippleD's consensus simulator: where the designs differ, what happened in 29 trust-topology cases, and what the evidence does and does not justify."
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
  - Determinism
---

Our [first Cobalt article](/blog/cobalt-implementation-evidence/) answered a basic question: **could the 2018 Cobalt design be turned into working Post Fiat code?** The answer was yes. We implemented the trust graph, transition checks, asynchronous agreement machinery, replay verification, and devnet governance integration.

This follow-up asks the harder question: **what does Cobalt actually buy us compared with the XRP Ledger's deployed RippleD consensus model?**

We built a canonical 80-case scenario manifest, ran it through a signed Post Fiat Cobalt adapter and a pinned RippleD 3.1.3 consensus-simulation adapter, and verified the result as one hash-bound packet. Both adapters matched all 80 declared expectations and neither produced conflicting decisions. The interesting result is narrower: **29 trust-topology cases produced different behavior. Cobalt rejected the proposed certificate and halted that governance decision; RippleD's simulator reached one decision on one branch.**

That is evidence of a real difference in what the two implementations check. It is not evidence that RippleD forked in these cases, that Cobalt is faster, or that a simulator result predicts XRP mainnet behavior.

## The answer in plain English

RippleD asks each server a local question:

> Did enough validators on *my* trusted list agree?

Its local quorum calculation can be correct while the relationship between different servers' lists remains an operating assumption. High overlap between published validator lists supplies that relationship in practice, but the protocol does not turn global list compatibility into a certificate that must pass before a validator-set change takes effect.

Cobalt asks an additional question:

> Are the declared trust groups behind this certificate mutually compatible under the active rules?

In Post Fiat's implementation, validator trust views are rooted protocol objects. Essential subsets declare who a validator relies on, the quorum required from each group, and the tolerated fault budget. The active trust graph checks a proposed certificate and any proposed graph transition. If a certificate relies on support that is outside a validator's declared view, the governance decision fails closed under the last accepted rules.

| Question | RippleD / XRP Ledger model | Post Fiat Cobalt model |
|---|---|---|
| Where does validator trust live? | In each server's local UNL and signed publisher-list distribution | In a rooted, hash-bound trust graph consumed by the protocol |
| What proves quorum? | Enough support under the server's local UNL | Enough support under declared essential subsets plus trust-graph validation |
| What proves different views are compatible? | Operationally maintained list overlap; not a global runtime certificate | Local linkage and transition obligations checked against the active graph |
| How does membership change? | Operators receive and adopt updated lists | Old rules validate a typed transition to new rules |
| What happens when the trust evidence is inconsistent? | A node may still satisfy its local quorum | The governance certificate is rejected; old authority remains in place |
| Role in Post Fiat's current design | Useful baseline and comparison target | Bounded governance sidecar; not the block-finality hot path |

The distinction is not “centralized versus decentralized” in one line. Both systems ultimately depend on operators, keys, network placement, and honest-enough validators. The distinction is whether compatibility between trust views is merely expected or is represented as data that code can accept or reject.

## The matched evaluation

The benchmark used four deterministic topologies: Post Fiat's six-validator shape and controls with 7, 10, and 20 validators. The manifest covered no-fault operation, declared faults, partitions and healing, message loss and reordering, validator rotation, key rotation, correlated failures, asymmetric views, publisher-list drift, and decreasing overlap.

The comparison was deliberately simulator-to-simulator:

- The Cobalt lane used signed protocol contributions, trust-graph validation, deterministic RBC/ABBA/MVBA/DABC checks, and durable replay.
- The RippleD lane used the pinned upstream `src/test/csf` framework at RippleD `3.1.3`, commit `46b241a…`, plus the native `Consensus` suite including `testFork` as a control. That native suite passed 13 cases and 1,370 elementary tests.
- Both lanes consumed the same ordered scenario manifest.
- Cobalt authority remained disabled in every case and never controlled block consensus.
- Timings were retained separately because Cobalt's signed governance path and RippleD's in-memory CSF path are not comparable latency surfaces.

The packet was built at Post Fiat commit [`3f00cb32`](/benchmarks/cobalt-further-evaluation-20260823/README.md). The [complete comparison packet](/benchmarks/cobalt-further-evaluation-20260823/matched-packet/comparison.md) contains the manifest, both raw reports, KPI aggregation, native RippleD control log, verifier result, and checksums. Its `SHA256SUMS` root is:

```text
7968a085033419255b52b844edd586346a1e85561394e52c69e6683b2561c50b
```

## The 29 differentiating cases

All 29 rows below have the same outcome:

- **Cobalt:** no governance decision; safe halt. The certificate failed because its non-uniform support included a validator outside a local trust view.
- **RippleD CSF:** one decision, one branch, no reported conflict.

“RippleD decided” does **not** mean “RippleD forked.” It means its local-UNL simulator did not treat the tested global trust-topology condition as a reason to stop. “Cobalt halted” does **not** mean “Cobalt is always safer.” A needless halt is also a liveness cost.

| # | Topology | Characterization case | Exact view relationship | Cobalt | RippleD CSF |
|---:|---|---|---|---|---|
| 1 | 6 validators | Publisher-list drift | 3 nodes use a 5-of-6 list; 3 use the full list | Safe halt | Decided, 1 branch |
| 2 | 6 validators | 60% overlap target | 4 of 6 shared (66.7%) | Safe halt | Decided, 1 branch |
| 3 | 6 validators | 40% overlap target | 2 of 6 shared (33.3%) | Safe halt | Decided, 1 branch |
| 4 | 6 validators | 20% overlap target | 1 of 6 shared (16.7%) | Safe halt | Decided, 1 branch |
| 5 | 6 validators | 10% overlap target | 1 of 6 shared (16.7% after integer rounding) | Safe halt | Decided, 1 branch |
| 6 | 6 validators | 0% overlap | 0 of 6 shared | Safe halt | Decided, 1 branch |
| 7 | 7 validators | Publisher-list drift | 3 nodes use a 6-of-7 list; 4 use the full list | Safe halt | Decided, 1 branch |
| 8 | 7 validators | 60% overlap target | 4 of 7 shared (57.1%) | Safe halt | Decided, 1 branch |
| 9 | 7 validators | 40% overlap target | 3 of 7 shared (42.9%) | Safe halt | Decided, 1 branch |
| 10 | 7 validators | 20% overlap target | 1 of 7 shared (14.3%) | Safe halt | Decided, 1 branch |
| 11 | 7 validators | 10% overlap target | 1 of 7 shared (14.3% after integer rounding) | Safe halt | Decided, 1 branch |
| 12 | 7 validators | 0% overlap | 0 of 7 shared | Safe halt | Decided, 1 branch |
| 13 | 10 validators | Asymmetric views | Two 9-node views; 8 of 10 validators shared | Safe halt | Decided, 1 branch |
| 14 | 10 validators | Publisher-list drift | 5 nodes use a 9-of-10 list; 5 use the full list | Safe halt | Decided, 1 branch |
| 15 | 10 validators | 80% overlap | 8 of 10 shared | Safe halt | Decided, 1 branch |
| 16 | 10 validators | 60% overlap | 6 of 10 shared | Safe halt | Decided, 1 branch |
| 17 | 10 validators | 40% overlap | 4 of 10 shared | Safe halt | Decided, 1 branch |
| 18 | 10 validators | 20% overlap | 2 of 10 shared | Safe halt | Decided, 1 branch |
| 19 | 10 validators | 10% overlap | 1 of 10 shared | Safe halt | Decided, 1 branch |
| 20 | 10 validators | 0% overlap | 0 of 10 shared | Safe halt | Decided, 1 branch |
| 21 | 20 validators | Asymmetric views | Two 18-node views; 16 of 20 validators shared | Safe halt | Decided, 1 branch |
| 22 | 20 validators | Publisher-list drift | 10 nodes use a 19-of-20 list; 10 use the full list | Safe halt | Decided, 1 branch |
| 23 | 20 validators | 90% overlap | 18 of 20 shared | Safe halt | Decided, 1 branch |
| 24 | 20 validators | 80% overlap | 16 of 20 shared | Safe halt | Decided, 1 branch |
| 25 | 20 validators | 60% overlap | 12 of 20 shared | Safe halt | Decided, 1 branch |
| 26 | 20 validators | 40% overlap | 8 of 20 shared | Safe halt | Decided, 1 branch |
| 27 | 20 validators | 20% overlap | 4 of 20 shared | Safe halt | Decided, 1 branch |
| 28 | 20 validators | 10% overlap | 2 of 20 shared | Safe halt | Decided, 1 branch |
| 29 | 20 validators | 0% overlap | 0 of 20 shared | Safe halt | Decided, 1 branch |

The grouping is 23 overlap-sweep cases, four list-drift cases, and two asymmetric-view cases. The small-topology 10% and 20% targets sometimes resolve to the same integer intersection; they remain separate deterministic manifest cases with separate identifiers and seeds.

## What determinism means here

Determinism is not “the network always makes progress.” It means that the same admitted evidence produces the same decision—or the same rejection—regardless of which machine replays it.

The demonstration has four parts.

### 1. One canonical input

[`generate_scenarios.py`](/benchmarks/cobalt-further-evaluation-20260823/source/generate_scenarios.py) emits the ordered 80-case canonical JSON manifest. Both adapters report the same manifest hash and case order. This prevents either lane from quietly receiving a friendlier test.

### 2. Domain-separated signed decisions

The [Cobalt benchmark adapter](/benchmarks/cobalt-further-evaluation-20260823/source/postfiat_cobalt_benchmark.rs) constructs signed contributions under a domain containing the chain identity and protocol version. The agreement path in [`rbc_abba_mvba.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/rbc_abba_mvba.rs) validates the reliable-broadcast, binary-agreement, and multi-value-agreement evidence. [`dabc_registry.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/dabc_registry.rs) binds the accepted result to the governance history.

The separate six-validator rehearsal exercises the distinction this encoding is designed to preserve: different valid five-of-six signer subsets converge on the same decision identity and governance digest. The audit certificate can retain different signer bytes without changing what was decided.

### 3. Replay equality

The packet reports:

| Determinism check | Result |
|---|---:|
| Manifest cases | 80 |
| Cases matching declared outcome | Cobalt 80/80; RippleD 80/80 |
| Cobalt cases marked replay-equal | 80/80 |
| Cobalt replay decisions checked | 424 |
| Conflicting decisions | Cobalt 0; RippleD 0 |
| Cases with Cobalt authority enabled | 0 |

Every Cobalt decision that was produced replayed to the same decision. A safe halt is also stable: replay does not manufacture a decision that the original evidence could not support.

### 4. A verifier checks the packet, not the prose

[`aggregate_packet.py`](/benchmarks/cobalt-further-evaluation-20260823/source/aggregate_packet.py) checks source pins, the manifest digest, adapter digests, case order, declared outcomes, replay equality, authority flags, and the native RippleD fork control. The RippleD side is implemented in [`MatchedLivenessBenchmark_test.cpp`](/benchmarks/cobalt-further-evaluation-20260823/source/MatchedLivenessBenchmark_test.cpp), rather than inferred from a model written in Rust.

This is why the evidence is stronger than two screenshots of “passed.” The scenario input, two outputs, source revisions, and verifier are bound together.

## What the real validators added

The matched 80-case packet is simulator evidence. It was not our only evidence.

Before the comparison, an authenticated Cobalt shadow service ran beside each of Post Fiat's six controlled-testnet validators across EWR, AMS, and SGP. The sidecars used the validators' existing ML-DSA identities, exchanged signed protocol messages over the private WAN, persisted an append-only history, and had both authority flags fixed to false.

The first live run found useful defects rather than producing a ceremonial pass: the node wrapper required all six contributions even though the trust graph's quorum was five, and a validator that missed a round had no signed history from which to repair its gap. The repaired [`cobalt_shadow.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/cobalt_shadow.rs) now uses canonical five-of-six support certificates, parent-linked ratifications, gap refusal, append-only signed history, and atomic catch-up.

The rerun established six concrete properties on the six validator machines:

| Live-validator check | Observed result |
|---|---|
| Quorum progress | Valid five-of-six signer sets ratified |
| Below-quorum behavior | Every tested four-of-six set rejected |
| Deterministic identity | Different valid support certificates resolved to one decision identity and governance digest |
| Missed history | A returning validator refused the gap, verified signed catch-up, and converged to the common history head without manual state repair |
| Block-finality isolation | Consensus v2 finalized height 913→914 during the outage and 914→915 after recovery |
| Actual authority | Foundation remained active; Cobalt remained non-authoritative |

We then ran the production handoff checks on a disposable clone, not the live registry. Early, stale, replayed, wrong-root, mixed-authority, and self-authorized transitions failed without mutation; a properly authorized future-height transition, one scoped validator-key rotation, and a forward transition back to Foundation mode succeeded. The [handoff packet](/benchmarks/cobalt-further-evaluation-20260823/handoff-packet/verifier.json), [activation-readiness packet](/benchmarks/cobalt-further-evaluation-20260823/readiness-packet/verifier.json), and [public bundle notes](/benchmarks/cobalt-further-evaluation-20260823/README.md) keep that distinction explicit.

This real-fleet work demonstrates that determinism survives process boundaries, restarts, a missing validator, and signed history recovery. It still does not demonstrate independent operator diversity: these are controlled-testnet validators, and Cobalt has not been given live governance authority.

## Did we demonstrate Cobalt's whitepaper benefit?

**Partly—and the limitation is important.**

The [Cobalt paper](https://arxiv.org/abs/1802.07240) proposed a system in which participants can hold non-identical trust views and reason about safety and liveness through local essential-subset conditions, instead of depending on one globally uniform participant list. The practical promise was not merely better fault tolerance. It was **adaptable trust whose safety conditions are visible to the protocol**.

This evaluation demonstrates the visibility half. The relevant implementation is [`trust_graph_governance.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/trust_graph_governance.rs): proposed graph state and certificates are checked under the active rules, including local-view support and old-to-new transition obligations. In the 29 cases above, that checker observed a condition RippleD's local-quorum calculation did not encode and refused to authorize the governance result.

That is useful. A network operator gets a typed rejection before a validator-registry change becomes authoritative, rather than learning after deployment that different machines understood the trusted set differently. In our current architecture, the failure remains outside block finality: [`cobalt_shadow.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/cobalt_shadow.rs) observes and records Cobalt outcomes without giving them block authority, while [`cobalt_handoff.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/cobalt_handoff.rs) makes any later authority change an explicit, signed, height-bound transition. A Cobalt governance halt therefore does not have to halt transaction finality.

The packet does **not** yet demonstrate the full liveness promise. Our conservative adapter halted even in the 20-validator 90%-overlap case because the assembled certificate included support outside a local view. That is a defensible fail-closed policy, but a production Cobalt deployment should do more than identify heterogeneous views: it should show useful progress when those views satisfy the implementation's declared linkage rules. Until that gate passes on real, independently operated validators, claiming the whitepaper's full advantage would be premature.

## Our evaluation

The evidence supports a narrower and more useful conclusion than “replace RippleD consensus with Cobalt.”

**Cobalt has a credible role as Post Fiat's validator-registry and trust-transition authority.** It turns trust topology into a checked object, gives unsafe or internally inconsistent transitions a deterministic rejection, preserves the last accepted registry, and can fail without entering the block-production path. That directly addresses the inherited XRP-lineage weakness we care about: local quorum does not itself prove global trust compatibility.

It does not yet justify putting Cobalt on the transaction-finality hot path. The 29 cases demonstrate conservative safety, while the 90%-overlap halt exposes unfinished liveness work. The next meaningful gate is therefore not another abstract proof or a broader simulator score. It is a live-validator exercise in which independently operated nodes hold deliberately non-identical but valid trust views, make a signed governance decision, lose and recover a participant, catch up from durable history, and reproduce the same decision identity from the packet.

If that succeeds, Cobalt offers a genuine architectural benefit over inherited RippleD governance: **the network can change who it trusts using rules the network itself can verify, while transaction finality continues separately.** If it does not, the honest result is that our implementation is a strong transition firewall but not yet the adaptable governance protocol described in the paper.

## Claim boundary

This article reports deterministic controlled-testnet benchmark evidence and codebase inspection. It does not claim:

- that RippleD forked in any of the 29 cases;
- that Cobalt would have prevented a historical XRP Ledger incident;
- that Cobalt is faster than RippleD;
- that Post Fiat has activated Cobalt authority on a public network;
- that simulator behavior proves internet-scale Byzantine liveness; or
- that our implementation has yet realized the paper's full non-uniform-trust result.

What it does claim is specific and reproducible: **under one canonical 80-case manifest, Post Fiat's Cobalt adapter and RippleD's pinned CSF adapter both matched every declared outcome with zero conflicts; in 29 trust-topology characterizations, Cobalt deterministically rejected a certificate that RippleD CSF accepted as one decision on one branch.** That is a real protocol delta, and it is now precise enough to guide the next live-validator test.

## Code and evidence map

| Subject | Code or artifact |
|---|---|
| Canonical 80-case input | [`generate_scenarios.py`](/benchmarks/cobalt-further-evaluation-20260823/source/generate_scenarios.py) |
| Signed Cobalt execution | [`postfiat_cobalt_benchmark.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/postfiat_cobalt_benchmark.rs) |
| Trust-graph and transition checks | [`trust_graph_governance.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/trust_graph_governance.rs) |
| RBC / ABBA / MVBA validation | [`rbc_abba_mvba.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/rbc_abba_mvba.rs) |
| Ordered governance history | [`dabc_registry.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/dabc_registry.rs) |
| RippleD 3.1.3 CSF adapter | [`MatchedLivenessBenchmark_test.cpp`](/benchmarks/cobalt-further-evaluation-20260823/source/MatchedLivenessBenchmark_test.cpp) |
| Packet aggregation and verification | [`aggregate_packet.py`](/benchmarks/cobalt-further-evaluation-20260823/source/aggregate_packet.py) |
| Current shadow boundary | [`cobalt_shadow.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/cobalt_shadow.rs) |
| Explicit authority handoff | [`cobalt_handoff.rs`](/benchmarks/cobalt-further-evaluation-20260823/source/cobalt_handoff.rs) |

## References

- Ethan MacBrough, [“Cobalt: BFT Governance in Open Networks,”](https://arxiv.org/abs/1802.07240) 2018.
- Brad Chase and Ethan MacBrough, [“Analysis of the XRP Ledger Consensus Protocol,”](https://arxiv.org/abs/1802.07242) 2018.
- Post Fiat, [“Cobalt on the Devnet: Implementing the Road Not Taken.”](/blog/cobalt-implementation-evidence/)
- XRPLF/RippleD `3.1.3`, commit [`46b241a`](https://github.com/XRPLF/rippled/commit/46b241ace8b30d9c9775d60ffba7d24b21903896).
