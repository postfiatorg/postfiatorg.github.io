---
title: "Heavy ZK: Circuit Anatomy and Prover Optimization for Shielded NAVCoin Swaps"
date: 2026-06-20T00:00:00Z
summary: "A grounded technical look at the devnet-proven, code-reviewed Halo2 circuit behind Post Fiat's shielded NAVCoin swaps: every major constraint, the measured CPU prover bottleneck, the K=15/key-cache optimization sprint, and the remaining path to GPU-accelerated proving."
categories:
  - Post Fiat Research
tags:
  - Halo2
  - zk-SNARK
  - Shielded
  - NAVCoin
  - Optimization
  - GPU
  - Akash
  - Post Fiat
---

*Companion to the [private NAV OTC swaps design](/blog/private-nav-otc-swaps/) and the [shielded-swap proven-live record](/blog/navcoin-otc-mvp-proven/). This post dissects the circuit that makes private NAVCoin swaps work, analyzes why proving is slow on the current devnet prover path, and lays out a benchmark-driven optimization roadmap toward mainnet-grade proving performance.*

In this design, **NAVCoins are assets that trade to NAV**. The circuit treats each NAVCoin as an asset identity committed inside an Orchard-style note, then proves conservation and spend validity without revealing asset identity, value, or owner.

## Scope and evidence level

Before the optimization story, here is the current status precisely:

- The shielded swap circuit is implemented and has been proven live on a **6-validator WAN devnet** with a single `a651 ↔ pfUSDC` shielded swap.
- The implementation has gone through internal code review; **10 findings were fixed**.
- The design spec has been TIH-reviewed and rewritten, but the implementation has **not** completed an external third-party audit.
- It is **not mainnet-deployed**, **not load-tested**, and **not production-audited**.
- CPU speedup numbers below are now **measured on this circuit and this 32-vCPU host**. GPU numbers remain targets/projections until an ICICLE-Halo2 prover is integrated and benchmarked.

The engineering conclusion changed after measurement: the original minutes-level path was mostly repeated key generation, not proof verification. After in-process key caching and reducing the circuit from `K = 16` to `K = 15`, the best measured CPU hot path is about **5.8 seconds to prove** and **66 ms to verify**. That is close to, but not under, the `<5s` CPU target.

## The circuit at a glance

The shielded NAVCoin swap circuit is a Halo2 zk-SNARK over the Pallas/Vesta Pasta curve suite. It originally shipped at `K = 16`; the optimization sprint proved that it fits safely at `K = 15`:

```text
2^15 = 32,768 circuit rows
```

For comparison, Zcash Orchard action circuits are commonly discussed at `K = 21`, or roughly two million rows. Row count alone is not a complete proving-time predictor — column count, lookup density, commitment scheme, backend implementation, CPU cache behavior, and parallelism all matter — but the comparison is still informative: this swap circuit is far smaller than a heavily optimized Orchard proving stack.

The circuit is designed to prove, in zero knowledge, that a shielded swap is valid:

- two input notes are spent from an anchored commitment tree;
- two output notes are created;
- per-asset value conservation holds;
- the spender is authorized;
- nullifiers are derived correctly;
- action data is bound to the chain domain;
- public nullifiers and output commitments are distinct;

without revealing which assets, how much value, or which spend authority is involved.

## Circuit anatomy: every constraint

### 1. Sinsemilla note commitments, `×4`: 2 inputs + 2 outputs

Each note carries a **1597-bit commitment message** segmented into Sinsemilla pieces:

```text
pool_domain || asset_tag_lo || asset_tag_hi || g_d || pk_d || value || rho || psi
```

The message is packed as six 250-bit pieces plus one final partial piece, committed under the domain:

```text
postfiat.asset_orchard.note_commit.v1
```

The circuit re-derives each note commitment from private witness data:

```text
asset_id, value, rho, psi, recipient
```

and wires the resulting commitment into the rest of the circuit. For input notes, the derived commitment feeds the Merkle path and nullifier derivation. For output notes, the derived commitment is constrained to the public output commitment in the instance.

This is the asset-typing extension. Standard Orchard notes bind recipient, value, `rho`, and `psi`. These notes additionally bind:

```text
asset_tag_lo || asset_tag_hi
```

where the asset tag is a 256-bit SHA3-384-truncated commitment to the asset identity, split into two 128-bit limbs. That asset binding is what lets the circuit enforce per-asset conservation without revealing the asset.

### 2. Merkle anchor verification, `×2`: both inputs

Each input note must be proven to exist in the **32-layer Orchard commitment tree**. The circuit recomputes the root from the note commitment, note position, and authentication path, then constrains it to equal the public anchor:

```text
for each input note:
  compute_root(cmx, position, auth_path[32]) == public_anchor
```

This is the “you cannot spend a note that was not in the anchored tree” constraint.

### 3. Nullifier derivation, `×2`

Each spent note produces a public nullifier. The circuit derives the nullifier from the nullifier private key, `rho`, and the note commitment, using the nullifier Poseidon domain, then constrains it to equal the public nullifier:

```text
nf = Poseidon^nullifier_domain(nk, rho, cmx) == public_nf
```

Consensus maintains the nullifier set. A reused nullifier is rejected.

### 4. Per-asset value conservation

This is the core swap constraint.

For each asset present in the inputs, the sum of input values for that asset must equal the sum of output values for that same asset:

```text
for each asset a in inputs:
  Σ(input_value where asset == a) == Σ(output_value where asset == a)
```

The current layout implements this with a permutation/select gate controlled by `q_conservation`, enforcing that the two input legs map to the two output legs with value conservation. Combined with the asset-tag binding inside the note commitment, this prevents:

- value inflation;
- swapping one asset tag for another;
- mismatched input/output assets;
- merge/split attacks across different asset identities.

The equality relationships are proven over private asset tags. The public verifier sees only commitments, nullifiers, anchors, and action-binding data.

### 5. Spend authorization

Each input’s spend authority is proven through Orchard-style key relationships and RedPallas randomized verification keys:

```text
rk = ak + [α]G         (randomized verification key)
pk_d = [ivk] · g_d     (diversified public key)
ivk = BLAKE2s(ak, nk, rivk)  (incoming viewing key)
```

The circuit proves the relevant ECC/key-derivation relationships hold for the note being spent. Consensus verifies RedPallas signatures over `H_sig`, the spend-authority hash that binds the full action transcript.

Together, the circuit and consensus signature check prove that the note owner authorized the spend without revealing the spend key.

### 6. Action binding: `H_action` + `swap_binding_hash`

The design uses a two-layer binding model:

- **Layer 1, consensus:** consensus recomputes `swap_binding_hash`, `H_action`, and `H_sig` from canonical action fields.
- **Layer 2, circuit:** the circuit re-derives `H_action` from the public instance and constrains it to instance rows `17/18`.
- **Verifier check:** the Halo2 verifier checks the proof against the exact public instance constructed by consensus.

```text
consensus recomputes: pool_domain, eo_hash, H_action, swap_binding_hash, H_sig
circuit constrains:   H_action(public_instance) == instance[17..18]
verifier checks:      proof verifies against the consensus-constructed instance
```

Changing any action field — anchor, nullifier, randomized verification key, output commitment, fee, encrypted output, or domain data — changes the public instance. The old proof no longer verifies. Replaying across chains fails because the domain binding changes `pool_domain` and therefore the action hash.

### 7. Public distinctness

The circuit enforces public distinctness for nullifiers and output commitments:

```text
nf_old[0] != nf_old[1]       (no same note spent twice in one action)
cmx_new[0] != cmx_new[1]     (no duplicate output commitment)
```

This is enforced with a nonzero-difference gate. It is defense-in-depth alongside consensus-level nullifier-set and commitment-set duplicate checks.

### 8. Range checks + nonzero gates

The circuit enforces:

- **Asset tag nonzero:** the asset tag pair `(asset_tag_lo, asset_tag_hi)` is constrained not to be all-zero. The current layout allocates inverse-gate checks over the tag limbs / nonzero predicate.
- **Value nonzero:** each swap value must be nonzero.
- **128-bit range checks** on asset-tag limbs via lookup range tables.
- **64-bit range checks** on values.

Together, the value range check plus nonzero check gives:

```text
1 <= value <= 2^64 - 1
```

### 9. Domain binding

The circuit binds the proof to the intended chain and circuit domain:

```text
chain_id
genesis_hash
protocol_version
pool_id      = asset-orchard-v1
circuit_id   = shielded_swap.asset_conservation.v1
note_version
```

These domain values are absorbed into `H_action` as constants through fixed-column domain-tag gates. A proof from a different chain, genesis, pool, circuit, or note version fails verification against the consensus-constructed instance.

## Constraint count summary

| Component | Approximate gate contribution |
|---|---:|
| Sinsemilla note commitment, `×4` | ~8,000 rows |
| Merkle path verification, `×2`, depth 32 | ~3,500 rows |
| Poseidon nullifier derivation, `×2` | ~1,200 rows |
| ECC spend authorization, `×2` | ~2,000 rows |
| Conservation + distinctness | ~200 rows |
| Range checks + nonzero | ~500 rows |
| `H_action` / `swap_binding_hash` | ~800 rows |
| **Total approximate usage** | **~16,000–18,000 rows** |

The circuit now fits inside `K = 15`:

```text
2^15 = 32,768 rows
```

The sprint tested the next lower size as well. `K = 14` fails with `NotEnoughRowsAvailable`, so `K = 15` is the smallest viable parameter set without reducing constraints.

## Why proving is slow: the honest analysis

The original devnet prover path took minutes on stock CPU-oriented paths. That was slow for a `K = 16` circuit, and the sprint measured why.

The main reason was repeated key generation. The one-shot CLI path rebuilt the full proving key and verifying key around each proof:

```text
K=16 cold path:
  proving-key build   341,879 ms
  proof generation     10,515 ms
  verifying-key build  18,081 ms
  proof verification       88 ms
```

The proof itself was seconds, not minutes. The key build made the operator-visible flow feel like minutes.

The three main bottlenecks are:

1. MSM: multi-scalar multiplication;
2. FFT: polynomial evaluation/interpolation;
3. field arithmetic: hot-loop Pasta field operations.

After key caching and `K = 15`, the measured hot path is:

```text
K=15 hot path:
  proof generation      5,780 ms
  proof verification       66 ms
  proof bytes           6,816
```

### Bottleneck 1: serial or under-parallelized MSM

MSM is usually the dominant prover cost, often on the order of **60–80%** of proving time in PLONKish systems, depending on circuit shape and commitment scheme.

If MSMs run on one core, a 16-core or 32-core machine is mostly idle. Mature proving backends use parallel Pippenger-style MSM implementations, split work across cores, and tune bucket accumulation and memory layout.

The measurement corrected an earlier suspicion: stock `halo2_proofs = "0.3.2"` in this workspace **does** expose and enable multicore through `maybe-rayon`/Rayon. A single-thread control proved it:

```text
K=16 default Rayon prove_ms        10,515
K=16 RAYON_NUM_THREADS=1 prove_ms  69,389
measured prove speedup              6.60x
```

Multicore is real and material. It is not sufficient by itself.

### Bottleneck 2: serial or under-parallelized FFT

FFT work is usually the second major prover cost, often **15–30%** depending on circuit layout.

Halo2 proving requires polynomial transformations over the evaluation domain. If those FFTs run serially, proving time scales poorly even for a relatively small circuit. Optimized Halo2 stacks parallelize FFTs and improve cache behavior.

Again, this is not just a configuration detail. The optimized Zcash/ECC-style Halo2 stack is already the dependency line here; further gains require profiling and either circuit-level work or a different proving backend.

### Bottleneck 3: generic or less-optimized field arithmetic

The innermost loop is Pasta field arithmetic:

```text
Pallas base field operations
Pallas scalar field operations
Vesta/Pallas curve operations
```

Depending on crate lineage, build flags, and CPU target, the prover may be using generic Rust big-integer paths rather than platform-tuned assembly/intrinsics. Optimized Pasta backends can materially improve MSM, FFT, and hash-gadget performance.

This is a real engineering gap: it is not enough to say “use more cores” if each field operation is also slower than it needs to be.

### The combined effect

A small circuit with an unoptimized prover can be much slower than a larger circuit with a mature prover stack.

A plausible performance gap is:

```text
serial MSM/FFT       → large multicore loss
generic field ops    → additional constant-factor loss
cache/layout issues  → additional backend loss
```

The earlier “50–100×” class of gap should be retired as a CPU claim. The measured CPU improvement from the low-risk sprint is much narrower but real: key caching removes repeated keygen in long-lived processes, and `K = 15` brings hot proof generation to about `5.8s`.

The actionable point is narrower and stronger: the next CPU step is flamegraph-level profiling of the remaining `5.8s`, especially MSM, FFT, Sinsemilla, Merkle, lookup, and field-arithmetic costs.

## Optimization results

The optimization path became empirical:

```text
baseline measurement
→ multicore determination
→ in-process key cache
→ K=15 circuit parameter reduction
→ backend/fork decision
→ GPU prover scope
```

### Tier 0: baseline and multicore determination

The old framing was “one Cargo feature gives 16–32×.” That was too strong.

Measured result:

```text
halo2_proofs 0.3.2 default = ["batch", "multicore"]
multicore = ["maybe-rayon/threads"]

K=16 default Rayon:
  prove_ms       10,515
  verify_ms          88

K=16 single-thread:
  prove_ms       69,389
  verify_ms         637
```

Multicore is already enabled and worth about `6.6×` on proof generation versus one thread. The remaining problem was not a missing feature flag.

### Tier 1: key-cache hot path

The largest operational win was removing repeated key construction in long-lived processes.

Measured `K = 16` hot-cache result:

```text
cold proving-key lookup    341,142 ms
first proof                 10,054 ms
cold verifying-key lookup   20,095 ms
first verify                    94 ms
hot proving-key lookup           0 ms
second proof                 9,909 ms
hot verifying-key lookup          0 ms
second verify                   91 ms
```

This does not make a one-shot CLI invocation fast, because the process still has to build the key once. It does make repeated swaps in a long-lived prover or validator process fast enough that the proof itself becomes the bottleneck.

### Tier 2: circuit-level K reduction

The circuit fit at `K = 15` and failed at `K = 14`.

Measured `K = 15` result:

```text
K=15 cold path:
  pk_build_ms     330,005
  prove_ms          5,841
  vk_build_ms      10,233
  verify_ms            63
  proof_bytes       6,816

K=15 hot path:
  proof generation  5,780 ms
  verification         66 ms
```

The K reduction produced a measured `1.8×` cold proof speedup and `1.71×` hot proof speedup versus K=16.

### Tier 3: backend/fork decision

The current dependency is already `halo2_proofs 0.3.2` from `https://github.com/zcash/halo2`, the Zcash/ECC line used by Orchard. The visible alternative `halo2-axiom 0.5.1` is not a safe drop-in for this sprint: it is a KZG/trusted-setup, nightly-only fork from the Axiom/PSE line.

So the CPU backend decision is:

```text
keep halo2_proofs 0.3.2
keep multicore enabled
do not migrate to a different proof-system backend inside this sprint
```

### Tier 4: GPU acceleration with ICICLE-Halo2

The GPU path is to offload MSM and FFT work to CUDA kernels using an ICICLE-Halo2-style backend.

The reason this is attractive is straightforward: MSM and FFT are exactly the workloads where GPUs can outperform CPUs when the circuit is large enough and data movement is managed well.

Published ICICLE/Halo2-related benchmarks report large speedups for compatible workloads on NVIDIA GPUs. For this circuit, that remains an external benchmark signal, not an internal result.

There are integration questions to answer:

- Pasta curve support and backend compatibility;
- transcript/proof compatibility with the consensus verifier;
- memory transfer overhead;
- whether `K = 15` is large enough to saturate the GPU;
- end-to-end time including witness loading and proof serialization;
- deterministic deployment and reproducible builds.

The current measured CPU hot proof is about `5.8s`. The GPU target is `<2s`, with sub-second as the stretch target, but it remains unmeasured until the ICICLE branch runs on real GPU hardware.

#### GPU provisioning: crypto-native compute

The crypto-native proving architecture remains compelling:

- **Akash Network**: lease NVIDIA GPU capacity through an on-chain deployment flow, with providers bidding on the workload.
- **io.net**: access an aggregated GPU marketplace through API-driven provisioning.

The intended StakeHub flow is:

```text
StakeHub leases GPU capacity
→ deploys the ICICLE-Halo2 prover container
→ feeds the witness into the prover environment
→ receives the proof
→ submits the shielded swap action to PFTL
→ closes the lease
```

This keeps proof generation off-chain while using crypto-native compute markets for hardware provisioning.

One operational caveat matters: the prover sees the witness. A decentralized GPU marketplace supplies compute, but it does not automatically make witness handling trustless. StakeHub must treat the prover environment as a sensitive execution boundary, using hardened containers, ephemeral keys, encrypted transport, strict logs, and, where appropriate, TEEs or operator-controlled hardware.

### Tier 5: deeper circuit-level optimizations

The low-risk K reduction is done. Deeper tuning now means changing gadget layout, not just parameters.

Candidate circuit optimizations:

- **Reduce gadget rows enough to approach K=14.** K=14 currently fails, so this requires real constraint reduction.
- **Optimize the Sinsemilla gadget layout.** Note commitments dominate the row count. Any reduction in message packing, lookup usage, or fixed-table layout can pay off.
- **Improve lookup table efficiency.** Range checks and Sinsemilla lookups should be checked for table width, column usage, and row pressure.
- **Batch proving.** If multiple swaps share structure or anchor data, proving several actions in one circuit may amortize fixed costs.

Further speedup from circuit-level work is possible, but it is now more invasive than the K=15 change and should be driven by a flamegraph/row-usage profile.

### Tier 6: proving service architecture

For mainnet-scale operation, proving should be treated as an off-chain service, not something consensus performs.

The clean separation is:

```text
PFTL      = verifies proofs in consensus
StakeHub  = orchestrates proving and transaction submission
GPU layer = supplies compute
```

A concrete flow:

```text
user / StakeHub
→ lease GPU capacity on Akash or io.net
→ run Halo2 / ICICLE-Halo2 prover container
→ generate proof off-chain
→ submit proof + action to PFTL
→ PFTL verifies proof
→ close compute lease
```

PFTL does not need a transaction type for GPU leasing. GPU leasing is operator tooling. Consensus only needs the public instance, proof, and verification key semantics.

## Optimization path summarized

CPU numbers here are measured on the PostFiat AssetOrchard circuit and this 32-vCPU host. GPU remains scoped, not measured.

| Tier | Optimization | Measured / target result | Status |
|---|---|---:|---|
| **0** | Baseline | K=16 proof `10.515s`; cold path `370.7s` | Measured |
| **1** | Multicore determination | Default Rayon is `6.60×` faster than one thread for proving | Measured |
| **2** | In-process key cache | hot key lookup `0ms`; K=16 hot proof+verify about `10.0s` | Landed |
| **3** | K=15 reduction | K=15 hot proof `5.780s`; verify `66ms`; proof `6,816 bytes` | Landed |
| **4** | Backend/fork migration | no safe drop-in fork; keep Zcash/ECC `halo2_proofs 0.3.2` | Decided |
| **5** | GPU backend via ICICLE-Halo2 | target `<2s`; stretch sub-second | Scoped, unmeasured |
| **6** | Deeper circuit tuning | target: close remaining `0.8-0.9s` CPU gap | Future profiling |

The speedups should not be blindly multiplied. Bottlenecks shift after each tier. For example, once MSM is parallelized, FFT or hashing may dominate; once GPU transfer overhead is included, a small `K = 15` circuit may gain less than a larger circuit.

## Benchmark evidence

The measured sprint artifacts are:

```text
docs/status/zk-prover-baseline-benchmark.md
docs/status/zk-prover-multicore-determination.md
docs/status/zk-prover-key-cache-optimization.md
docs/status/zk-prover-k15-circuit-optimization.md
docs/status/zk-prover-backend-fork-decision.md
docs/status/icicle-gpu-prover-scope.md
docs/status/zk-prover-optimization-results.md
```

The release soundness regression stayed green after the optimization:

```bash
cargo test -p postfiat-privacy-orchard \
  swap_consensus_verifier_accepts_real_proof_and_rejects_forged_nonconservation \
  --release -- --ignored --nocapture
```

The K=15 metadata pin test also stayed green:

```bash
cargo test -p postfiat-privacy-orchard \
  swap_full_shape_key_metadata_is_pinned_and_consistent \
  --release -- --ignored --nocapture
```

## What this means

The shielded NAVCoin swap circuit is not just a paper sketch. It is implemented, code-reviewed internally, and proven on a WAN devnet. It includes Sinsemilla note commitments, Merkle anchor verification, Poseidon nullifier derivation, ECC spend authorization, per-asset conservation, action binding, public distinctness, range checks, and domain binding.

But the correct status is:

```text
devnet-proven
code-reviewed internally
pending external audit
pending mainnet load testing
pending deeper CPU profiling and GPU prover benchmarks
```

The proving slowdown is now better understood. The minutes-level path was mostly cold proving-key generation. The proof itself was about `10.5s` at K=16 and about `5.8s` at K=15. Multicore is already active. The remaining CPU gap is either circuit/gadget optimization or a different proving backend.

The crypto-native GPU path remains strategically important. StakeHub can orchestrate off-chain proving using Akash or io.net GPU capacity, generate Halo2 proofs with an optimized backend, and submit only the proof and public action data to PFTL. PFTL remains the verifier; StakeHub handles execution; the GPU layer supplies compute.

That is the right separation of concerns. CPU projections have now been replaced with measurements; GPU remains the next measurement gap.

---

*Implementation: `postfiatl1v2` branch `navcoin-market-ops-envelope`, `crates/privacy_orchard/src/asset_orchard_circuit.rs` (the circuit), `asset_orchard_sinsemilla.rs` (the note-commitment gadget), `verify.rs` (the consensus verifier). Design spec: `docs/specs/asset-orchard-swap-circuit-design-v2.md` (TIH-reviewed, GPT-5.5-pro-rewritten). Current evidence: internal code review with 10 findings fixed, a live `a651 ↔ pfUSDC` shielded swap on the 6-validator WAN devnet, and measured CPU prover benchmarks on 2026-06-20. Pending: external audit, mainnet deployment, load testing, deeper CPU profiling, and GPU prover benchmarks.*
