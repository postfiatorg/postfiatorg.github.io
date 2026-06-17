---
title: "Post Fiat Latency Series II: FastPay — Removing Consensus from Owned-Value Settlement"
date: 2026-06-16T00:00:00Z
summary: "Series II implements a FastPay-style owned-value lane for Post Fiat: simple payments finalize on validator certificates, while consensus checkpoints them asynchronously. The result is measured on a controlled EU validator fleet and a six-validator cross-continent testnet — reaching 183 ms finality across three continents with post-quantum signatures — and is supported by a formal safety invariant, implementation notes, and an adversarial gate."
aliases:
  - /post-fiat-latency-series-ii/
  - /posts/post-fiat-latency-series-ii/
  - /postfiat-l1v2-fastpay-latency/
  - /posts/postfiat-l1v2-fastpay-latency/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - L1
  - FastPay
  - Latency
  - Finality
  - Benchmark
  - Post-Quantum
---

[Series I](/blog/postfiat-l1v2-private-xrpl-latency-benchmark/) made certified-receipt finality small. Series II removes the consensus wait from the simple-payment critical path.

A blockchain normally routes payments through consensus because consensus is the general-purpose double-spend firewall: it puts transactions in one total order before state changes. A **lane** is the settlement path a transfer takes. The account lane uses Cobalt consensus. The owned-value lane is narrower and faster: when the value being spent has one logical writer — the owner — validators only need to agree that this exact object version has not already been spent.

That is the FastPay move. The wallet broadcasts one canonical owned-transfer order, validators lock that input object version and sign it, and the wallet assembles a quorum certificate. The certificate is final; Cobalt checkpoints it asynchronously.

Post Fiat now has that lane.

![FastPay consensusless fast path: wallet broadcasts to validators, collects signed votes, assembles a final certificate — no consensus round on the critical path](/benchmarks/fastpay-fastpath-diagram.svg)

## The result

The structural result is simple: owned-value settlement finalizes on a validator certificate, not on a consensus commit.

Measured back-to-back through native TCP RPC against the same three-validator Hetzner EU WAN testnet, the owned lane reaches p50 55 ms; p95 58 ms; p99 60 ms over n=25,000 wallet-to-certificate samples. The consensus-bound account lane measures p50 152 ms; p95 162 ms; p99 163 ms over n=25 submit-to-finality samples. Its p50 includes a 141 ms certified consensus round, plus ~5 ms mempool admission and ~6 ms batching. The Series I certified-receipt baseline was 88 ms p50.

All latency and cryptographic figures used in this article are reconciled here:

| item | value | context |
|---|---:|---|
| Series I certified-receipt baseline | 88 ms p50 | full-vote native-transfer receipt path from the prior study |
| Measurement harness | native TCP RPC from a fleet-co-located client against the same three-validator Hetzner EU WAN testnet; owned lane n=25,000, account lane n=25 | same transport, same fleet, back-to-back |
| Account lane, submit-to-finality (n=25) | p50 152 ms; p95 162 ms; p99 163 ms; range 145–163 ms | consensus-bound transfer path; each sample is a full consensus round |
| Account-lane mempool admission | ~5 ms | p50 decomposition of the consensus-bound transfer path |
| Account-lane batch step | ~6 ms | p50 decomposition of the consensus-bound transfer path |
| Account-lane certified consensus round | 141 ms p50 | the round on the account-lane critical path; the owned lane does not pay it |
| Owned lane, wallet-to-certificate (n=25,000) | p50 55 ms; p95 58 ms; p99 60 ms | consensusless certificate path; co-located EU fleet, per-request connections |
| Owned lane, cross-continent WAN, wallet-to-quorum (n=5,000) | p50 183 ms; p95 186 ms; p99 188 ms | 6 validators across 3 continents (EU + NJ + SG); persistent connections, finality at quorum(4) |
| Owned lane, cross-continent WAN, wallet-to-all-6-signed (n=5,000) | p50 287 ms; p95 289 ms; p99 291 ms | full certificate propagation across 3 continents |
| Owned-lane serving path | 55 ms production in-process path; earlier 63 ms included an ~8 ms child-process harness artifact | deployed validators do not pay a per-request child-process fork |
| Owned-lane network contribution | ~53 ms | two EU-internal round trips for broadcast and quorum collection |
| Owned-lane critical-path cryptography | ~1 ms | 3 parallel validator signatures at 0.52 ms each plus client verification |
| Sequential cryptography benchmark | 3.3 ms | owner signature, 3 validator signatures, aggregation, and verification executed sequentially |
| Certificate byte cost | ~15 KB | 4x ML-DSA-65 signatures |
| Derived latency share | network ~96%; post-quantum signatures ~2%; scheduling/aggregation ~2% | decomposition of the owned-lane p50 |
| External FastPay reference | 43 ms; ML-DSA-65 signatures are ~50x larger than ed25519 signatures | original FastPay paper comparison, calibration point only |

## The design move

Cobalt is Post Fiat’s governed consensus and registry layer. The account lane enters Cobalt to get a certified total order before application. The owned-value lane settles a single owned-object spend directly with validator signatures.

```text
Account lane                              Owned-value lane
(certified consensus)                     (FastPay-style certificate)

wallet signs transfer                     wallet signs owned-transfer order
  -> admission                              -> broadcast order to validators in parallel
  -> batching / proposal                    -> validators check freshness
  -> validator voting                       -> validators lock input object version
  -> certified consensus                    -> validators sign canonical order bytes
  -> local application                      -> client aggregates quorum certificate
  -> finality receipt                       -> TRANSFER CERTIFICATE  *** FINAL ***
                                            -> certificate applied by validators
                                            -> checkpointed into Cobalt asynchronously
```

There is no proposal, consensus vote round, or block on the owned-value critical path. The certificate is the settlement artifact. Once the client holds a valid quorum certificate, no conflicting certificate for the same input object version can be formed.

Consensus remains responsible for governance, checkpointing, and registry transitions. It is not responsible for deciding the payment in the synchronous path.

## Why the numbers look the way they do

The account lane waits for total order. The owned-value lane waits for quorum observation of a single object version.

The two measurements share the same boundary: the moment the client holds a final settlement artifact. For the account lane that artifact is a consensus commit; for the owned lane it is the quorum certificate itself, which needs no further commit. So wallet-to-certificate and submit-to-finality are the same boundary measured on two settlement models — one that still calls consensus, one that does not.

That distinction explains the measurement. The account-lane p50 is dominated by the certified consensus round: 141 ms p50 out of a 152 ms p50 submit-to-finality path, with ~5 ms in mempool admission and ~6 ms in batching. The owned lane removes that certified consensus round from the synchronous path.

The owned-lane p50 is instead dominated by fleet propagation and quorum collection. Its network contribution is ~53 ms: two EU-internal round trips for broadcast and signature collection. Critical-path cryptography is ~1 ms because validator signing is parallel: 3 parallel validator signatures at 0.52 ms each plus client verification. The sequential cryptography benchmark — owner signature, 3 validator signatures, aggregation, and verification executed sequentially — is 3.3 ms, but that is not the critical path.

The certificate is ~15 KB because it carries 4x ML-DSA-65 signatures. In the measured owned lane the p50 decomposes as roughly ~96% network, ~2% cryptography, and ~2% scheduling and client-side aggregation/verification. The post-quantum signature scheme is present on the path; it is not the bottleneck.

The 55 ms figure is the validator's production serving path. Validators answer `owned_sign` from their long-lived RPC process — the same process that serves every other RPC method — so the figure includes full JSON serialization over the wire and the ML-DSA signature computation. What it does not include is per-request process forking, because a deployed validator never forks a child per request. An earlier 63 ms measurement routed the call through a child process; that ~8 ms was a benchmark harness artifact, not protocol cost, and a deployed validator does not pay it.

The external FastPay paper’s 43 ms result is a calibration point, not the Post Fiat claim. The claim here is the structural one: for owned-value payments, Post Fiat settles on a quorum certificate and checkpoints later.

## Cross-continent: the same lane at geographic scale

The co-located EU result above proves the structural delta. The question that matters for a real network is whether it holds when the validators are not in one region. To answer it, the same owned-value lane was deployed across **six validators on three continents** — three in the EU, one in New Jersey, one in Amsterdam, one in Singapore — and measured end-to-end over the public internet.

The owned lane reaches **p50 183 ms to finality** (the quorum certificate) and **287 ms to every validator signed** over n=5,000 samples, with zero failures. Measured peer-to-peer round-trips on this fleet span 81 ms (US↔EU), 169 ms (EU↔Asia), and 234 ms (US↔Asia).

The number is not 55 ms because the certificate has to physically round-trip to the quorum at the speed of light, and the quorum now spans oceans. FastPay removes **consensus rounds**, not **network latency**: a consensus-bound spend on the same geography would pay several of those round-trips for proposal, voting, and certification; the owned lane pays one round-trip to the quorum and stops. The 183 ms is that one round-trip, dominated by the leg to the fourth-closest validator. Removing consensus is worth more, not less, when the round-trips it removes are expensive.

For context against deployed fast chains:

| chain | path | latency | notes |
|---|---|---:|---|
| Solana | all transactions (leader / consensus) | ~400 ms optimistic; ~12.8 s hard finality | Proof-of-History clock, Tower BFT; no owned-object fast path |
| Sui | owned-object fast path (BCB) | sub-second (hundreds of ms) | the same Byzantine consistent broadcast mechanism this lane uses |
| Sui | shared-object consensus (Mysticeti) | ~390 ms | for objects that require global ordering |
| Post Fiat | owned-value fast path (BCB) | **183 ms to finality** | six validators across three continents; **ML-DSA-65 post-quantum signatures** |

Post Fiat's owned lane is competitive with Sui's owned-object path and faster than Solana's optimistic confirmation — and it carries ML-DSA-65 signatures that are roughly 50× the size of the ed25519 signatures those chains use. The post-quantum cost is not on the critical path.

The WAN measurement uses persistent TCP connections: the wallet opens one connection per validator and reuses it, so each certificate costs one network round-trip rather than a fresh handshake plus a round-trip. That keep-alive path is now part of the deployed `rpc-serve` (the earlier co-located figures used per-request connections; the structural result — owned far below consensus — is the same either way).

## Why removing consensus is safe

A consensusless lane is safe only if conflicting certificates cannot both exist. FastPay’s core safety property is quorum intersection plus a per-validator one-signature lock.

In Cobalt terms, the signer universe is a registry-scoped essential subset: a validator set with size, quorum, and Byzantine budget satisfying Cobalt’s local cover-intersection rule. The owned lane uses the same condition; it changes the settlement artifact, not the trust model.

Definitions for a fixed registry:

- An owned-transfer order consumes a specific input object version.
- A valid certificate contains owner authorization and at least quorum validator votes over the same canonical order bytes.
- Two orders conflict if they attempt to consume the same input object version into different effects.
- An honest validator locks before signing and signs at most one order for the same input object version within the registry.

**Theorem (no-conflicting-certificate).** For a validator essential subset $S$ with $n_S$ validators, quorum $q_S$, and Byzantine budget $t_S$ satisfying Cobalt’s local safety condition

\[
t_S < 2q_S - n_S,
\]

two valid certificates, each with at least $q_S$ votes from $S$, for conflicting orders on the same input object version cannot both exist.

*Proof.* Let $A$ and $B$ be the signer sets of two valid certificates from $S$. Since $|A| \ge q_S$ and $|B| \ge q_S$ inside a universe of size $n_S$,

\[
|A \cap B| \ge 2q_S - n_S.
\]

By Cobalt’s local safety condition, $2q_S - n_S > t_S$. Therefore the intersection contains more validators than the Byzantine budget, so it contains at least one honest validator. That honest validator would have had to sign both conflicting orders for the same input object version, contradicting the lock invariant. $\square$

This is not a new trust assumption. The condition $t_S < 2q_S - n_S$ is the same local safety row enforced by Cobalt’s cover extractor for every essential subset, described in whitepaper §6.3. The owned-value lane instantiates that invariant as a FastPay quorum over an essential subset.

The adversarial reading is direct. A Byzantine validator may sign two conflicting orders; that behavior is exactly what the Byzantine budget $t_S$ counts. For two conflicting certificates to exist, their signer-set intersection would need to be entirely Byzantine. The bound prevents that: the intersection is larger than $t_S$, so it contains an honest validator, and the per-validator one-signature lock per (object, version) within a registry prevents the honest double-sign. The fixed-registry scope is also deliberate. Validator keys, quorums, Byzantine budgets, and locks are interpreted inside one registry; finalized certificates become durable committed state, and `owned-safe-unlock` clears old-registry unfinalized locks at the transition boundary. Reconfiguration does not mix quorum systems or rely on stale locks for safety.

## Liveness

The safety theorem bounds what can go wrong with conflicting certificates. The natural follow-up is liveness: what happens if a client never assembles a quorum?

A client that broadcasts an order and collects fewer than quorum votes holds no finalized certificate, so its spend is not applied. Value does not move on a partial certificate. Validators that did sign have locked the input object version for that order within the registry — but those locks are not permanent, and two recovery paths exist:

1. **Within the registry**, the owner re-broadcasts the same order to collect the remaining votes. Existing locks are on the non-conflicting order, so re-broadcast completes; a lock refuses only a *conflicting* spend, never the owner's own intended one.
2. **Across registries**, `owned-safe-unlock` clears every lock at the registry boundary, so an unfinalized lock can never strand value past the next transition.

Consensus is not on the certificate critical path, but it remains available. An owner whose certificate lane cannot make progress can spend the same value through the account lane instead. Consensusless here means the fast path needs no block; it does not mean consensus has been removed from the system.

## What was built

The owned-value lane is implemented in `postfiatl1v2` on branch `fastpay-m1`.

| component | where | role |
|---|---|---|
| `OwnedObject`, `OwnedTransferOrder`, `OwnedTransferCertificate` | `crates/types` | canonical owned-value state and certificate types |
| `apply_owned_transfer` | `crates/execution` | single consumption, value conservation, and resource caps |
| `apply_owned_certificate` | `crates/execution` | verifies owner authorization and quorum validator votes before applying; a bare order is never trusted |
| `owned-sign` | `crates/node` | checks freshness, locks the input object version, and refuses conflicting orders |
| `owned-apply` | `crates/node` | verifies a finalized certificate and applies it to a real ledger through `NodeStore` |
| `checkpoint-pending` and `checkpoint_log` | `crates/node` | durable committed state that survives registry transitions |
| `owned-safe-unlock` | `crates/node` | registry-scoped lock cleanup at validator-set boundaries |

The live path exercised the full flow: wallet order creation, validator freshness checks, lock acquisition, validator signing, certificate assembly, certificate verification, ledger application, durable checkpoint logging, conflict refusal, tamper rejection, and replay rejection.

## Adversarial safety gate

| adversarial case | result |
|---|---|
| 4 valid votes (quorum 3) → applies | ✅ passes |
| 2 valid + 2 **forged** votes (wrong key) → insufficient quorum | ✅ rejected |
| exactly-quorum boundary (3 of 3) → applies | ✅ passes |
| replay of consumed certificate → single-consumption | ✅ rejected |
| tampered owner signature → `OwnerAuthFailed` | ✅ rejected |
| **conflicting order for same input version** → lock table | ✅ **refused** (live, EU fleet) |

## Reconfiguration safety

A consensusless lane must not strand value across validator-set changes. The owned-value lane handles registry transitions with durable certificate state and registry-scoped locks.

```text
registry transition N -> N+1
  ├─ checkpoint log
  │   finalized certificates remain durable committed state
  │   across any registry change
  │
  └─ registry-scoped locks
      locks carry the registry fingerprint
      at the boundary, owned-safe-unlock clears old-registry locks

      result:
        objects locked by equivocation under N unlock under N+1
        finalized certificates remain committed
        unfinalized equivocation cannot create permanent deadlock
```

This is Sui-Lutris epoch-close safety adapted to Cobalt’s governed registry transitions: close the old validator set, carry finalized state forward, and clear only registry-scoped unfinalized locks. Cobalt already supplies the transition handoff and cover-intersection invariant; the owned-value lane uses those properties for certificate settlement.

## Limitations and what's next

The current boundary of the result is precise:

- **Measurement scope:** both lanes were measured by native TCP RPC from a fleet-co-located client against the same three-validator Hetzner EU WAN testnet, back-to-back; these are not mainnet measurements.
- **Review scope:** the safety mechanisms are implemented and tested, including the adversarial gate above; independent security review has not completed.
- **Sampling:** the account lane is n=25 because it is consensus-round-bound (range 145–163 ms across 25 samples; p50 152 ms) — each sample is a full consensus round plus a funding cycle. The owned lane is n=25,000 because each sample is a sub-100 ms certificate.
- **Scale:** the co-located measurements are on a 3-validator EU fleet; the cross-continent measurements are on a 6-validator fleet spanning three continents (n=5,000). The owned-lane cryptography is ~1 ms on the critical path because validator signing is parallel, and the certificate is ~15 KB (4× ML-DSA-65 signatures at quorum 3). Certificate size and the broadcast fan-out scale with the quorum size, so at mainnet-scale validator counts the certificate cost and network contribution grow; the structural result — no consensus round on the critical path — is independent of validator count.
- **Production hardening:** remaining work is DOS/admission limits on the broadcast path, validation at mainnet-scale validator counts and registry topologies, and checkpoint cadence tuning.

## Conclusion

Series I reduced the synchronous wait for certified finality. Series II removes consensus from the simple owned-value payment path.

For this class of transfer, finality is a quorum certificate over a single owned-object spend. Consensus remains in the system, but it runs after settlement to checkpoint the certificate into the governed chain. The implementation now includes the certificate verifier, validator lock table, single-consumption execution rule, durable checkpoint lane, registry-safe unlock path, and adversarial gate.

The result holds at geographic scale: on a six-validator testnet spanning three continents, the owned lane reaches finality in 183 ms — competitive with Sui's owned-object path and faster than Solana's optimistic confirmation, while carrying post-quantum signatures. Removing consensus is worth the most exactly where the round-trips it removes are the most expensive.

The protocol result is simple: a payment no longer needs to wait for a block when ownership and quorum intersection are enough.

---

*Series I: [Certified Finality vs. Validated Ledgers](/blog/postfiat-l1v2-private-xrpl-latency-benchmark/). Implementation: `postfiatl1v2` branch `fastpay-m1` (`crates/fastpay-prototype`, `crates/execution/src/lib_parts/owned_transfer.rs`, `crates/node/src/lib_parts/part_03.rs`). Safety proof notes: [`docs/fastpay_safety_proofs.md`](https://github.com/agticorp/postfiatl1v2/blob/fastpay-m1/docs/fastpay_safety_proofs.md).*