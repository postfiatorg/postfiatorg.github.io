---
title: "Heavy ZK: Circuit Anatomy and Prover Optimization for Shielded NAVCoin Swaps"
date: 2026-06-20T00:00:00Z
draft: true
summary: "A detailed look at the Halo2 zk-SNARK circuit behind Post Fiat's shielded NAVCoin swaps — every constraint, every gadget, why proving takes minutes on stock hardware, and the concrete optimization path from minutes to sub-second using multicore parallelism, production-optimized field arithmetic, and GPU acceleration via decentralized compute markets (Akash/io.net)."
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

*Companion to the [private NAV OTC swaps design](/blog/private-nav-otc-swaps/) and the [shielded-swap proven-live record](/blog/navcoin-otc-mvp-proven/). This post dissects the circuit that makes private NAVCoin swaps work, analyzes why proving is slow on stock hardware, and proposes the optimization path to production speed.*

## The circuit at a glance

The shielded NAVCoin swap is a **real Halo2 zk-SNARK** over the Pallas/Vesta (Pasta) curve suite, with `K = 16` (2¹⁶ ≈ 65,536 circuit rows). For comparison, Zcash's Orchard action circuit runs at `K = 21` (~2 million rows) — **our circuit is ~30× smaller**. Yet on stock hardware, our proving takes minutes while Zcash takes ~1–2 seconds. This post explains why and how to close that gap.

The circuit proves, in zero knowledge, that a shielded swap is valid: two input notes (of different asset types) are spent from the anchored commitment tree, two output notes are created, per-asset value conservation holds, the spender is authorized, and the action is bound to the chain's domain — **without revealing which assets, how much, or who**.

## Circuit anatomy: every constraint

### 1. Sinsemilla note commitments (×4: 2 inputs + 2 outputs)

Each note carries a **1597-bit commitment message** segmented into Sinsemilla pieces:

```text
pool_domain || asset_tag_lo || asset_tag_hi || g_d || pk_d || value || rho || psi
```

Six 250-bit pieces + one 100-bit final piece, committed under the domain `postfiat.asset_orchard.note_commit.v1`. The circuit re-derives each commitment from the private witness (asset_id, value, rho, psi, recipient) and constrains it to equal the public note commitment — so the proof **binds** the commitment to the witness without revealing it.

**This is the asset-typing extension.** Standard Orchard notes bind only recipient/value/rho/psi. Our notes add `asset_tag_lo` and `asset_tag_hi` (a 256-bit SHA3-384-truncated commitment to the asset identity) into the Sinsemilla message — so the circuit can enforce per-asset conservation (the whole point of a multi-asset shielded swap).

### 2. Merkle anchor verification (×2: both inputs)

Each input note must be proven to exist in the **32-layer Orchard commitment tree** (the Merkle anchor). The circuit computes the Merkle root from the note's position + authentication path and constrains it to equal the public anchor — proving the note was in the tree at the anchored state.

```text
for each input note:
  compute_root(cmx, position, auth_path[32]) == public_anchor
```

This is the "you can't spend a note that doesn't exist" constraint.

### 3. Nullifier derivation (×2)

Each spent note produces a **nullifier** — a deterministic, nullifier-key-derived tag that prevents double-spending. The circuit derives each nullifier from the note's commitment + the nullifier private key (`nk`) + `rho` via Poseidon, and constrains it to equal the public nullifier. Consensus maintains a nullifier set; a reused nullifier is rejected.

```text
nf = Poseidon^nullifier_domain(nk, rho, cmx) == public_nf
```

### 4. Per-asset value conservation

The **core swap constraint.** For each asset `a` present in the inputs, the sum of input values for `a` must equal the sum of output values for `a`:

```text
for each asset a in inputs:
  Σ(input_value where asset == a) == Σ(output_value where asset == a)
```

Implemented via a permutation/select gate (`q_conservation` selector) that enforces the two input legs map to the two output legs with value conservation. Combined with the asset-tag binding (constraint #1), this prevents value inflation, asset mismatch, and merge/split attacks.

### 5. Spend authorization

Each input's spend authority is proven via the **RedPallas** randomized-verification-key derivation:

```text
rk = ak + [α]G         (randomized verification key)
pk_d = [ivk] · g_d     (diversified public key)
ivk = BLAKE2s(ak, nk, rivk)  (incoming viewing key)
```

The circuit proves these ECC relations hold, and consensus verifies RedPallas signatures over `H_sig` (the spend-authority hash that binds the full action transcript). This proves the note owner authorized the spend — without revealing the spend key.

### 6. Action binding (`H_action` + `swap_binding_hash`)

The **two-layer binding model** (the design's answer to the foundational binding question):

- **Layer 1 (consensus):** consensus recomputes `swap_binding_hash`, `H_action`, and `H_sig` from the canonical action fields.
- **Layer 2 (circuit):** the circuit re-derives `H_action` from the public instance and constrains it to instance row 17/18. The Halo2 verifier checks the proof against the exact public instance consensus constructed.

```text
consensus recomputes: pool_domain, eo_hash, H_action, swap_binding_hash, H_sig
circuit constrains:   H_action(public_instance) == instance[17..18]
verifier checks:      proof verifies against the consensus-constructed instance
```

Changing any field (anchor, nullifier, rk, output commitment, fee, encrypted output) changes the public instance → the old proof fails. Forging a binding hash fails (consensus recomputes + circuit constrains). Replaying across chains fails (domain binding changes `pool_domain`).

### 7. Public distinctness

```text
nf_old[0] != nf_old[1]       (no double-spend as two inputs)
cmx_new[0] != cmx_new[1]     (no duplicate output)
```

Enforced in-circuit via a nonzero-difference gate. Defense-in-depth alongside consensus's nullifier-set + commitment-set duplicate checks.

### 8. Range checks + nonzero gates

- **Asset tag nonzero:** each limb (lo, hi) proven nonzero via two inverse gates (asset_tag_lo ≠ 0 OR asset_tag_hi ≠ 0).
- **Value nonzero:** each swap value > 0.
- **128-bit range checks** on asset-tag limbs (via lookup range tables).
- **64-bit range checks** on values.

### 9. Domain binding

The circuit binds to: `chain_id`, `genesis_hash`, `protocol_version`, `pool_id` (`asset-orchard-v1`), `circuit_id` (`shielded_swap.asset_conservation.v1`), `note_version`. These are absorbed into `H_action` as constants (via the fixed-column domain-tag gates). A proof from a different chain/genesis/pool/circuit fails verification.

## Constraint count summary

| Component | Approximate gate contribution |
|---|---|
| Sinsemilla note commitment (×4) | ~8,000 (dominant — Sinsemilla hash + lookup tables) |
| Merkle path verification (×2, depth 32) | ~3,500 (Poseidon CRH per level × 32 × 2) |
| Poseidon nullifier derivation (×2) | ~1,200 (full + partial rounds) |
| ECC spend authorization (×2) | ~2,000 (variable-base scalar mul + add) |
| Conservation + distinctness | ~200 |
| Range checks + nonzero | ~500 |
| H_action / swap_binding_hash | ~800 |
| **Total (approximate)** | **~16,000–18,000 constraint rows** (within K=16 = 65,536) |

## Why proving is slow (the honest analysis)

The circuit is small (K=16, ~30× smaller than Zcash's Orchard). The proving is slow because of **three layers of unoptimization in the prover backend:**

### Bottleneck 1: Serial MSM (multi-scalar multiplication)

The dominant proving cost (~60–80%). Halo2's IPA commitment scheme requires MSMs over the circuit's fixed/commitment columns. The stock `halo2_proofs` crate performs these **serially, single-threaded** — even on a 32-core machine.

**Stock halo2 (our current setup):** `halo2_proofs = "0.3"` with no `multicore` feature → `maybe-rayon` falls back to a serial stub → **1 core doing all the MSM work.**

**Zcash's production fork:** parallel Pippenger MSM via `rayon` → all cores → near-linear speedup.

### Bottleneck 2: Serial FFT

The second-biggest cost (~15–30%). The polynomial operations (evaluation, interpolation) use FFTs over the evaluation domain. Stock halo2: serial. Zcash's fork: parallel.

### Bottleneck 3: Generic field arithmetic

The inner loop — Pallas base/scalar field operations (multiplications, additions, inversions). Stock halo2 uses generic Rust big-integer arithmetic. Zcash's fork uses **hand-optimized assembly/intrinsics** (the `pasta_curves` crate with platform-specific backends).

### The combined effect

On a 32-core box with stock halo2:
- MSM: ~1 core → should be 32 cores → **~32× wasted**
- FFT: ~1 core → should be 32 cores → **~32× wasted**
- Field arithmetic: generic Rust → assembly → **~2–3× wasted**

Combined: **~50–100× slower than Zcash's production prover on the same hardware**, for a smaller circuit. That's the gap from seconds (Zcash) to minutes (ours).

## Optimization proposal

### Tier 0: Enable multicore (free, immediate)

```toml
# Cargo.toml — one line
halo2_proofs = { version = "0.3", features = ["multicore"] }
```

Activates `maybe-rayon`'s `parallel` feature → real rayon (parallel MSM + FFT across all cores). No circuit change, no VK change, no proof incompatibility — just the backend parallelizes.

**Expected speedup:** ~16–32× on this 32-core box. **Minutes → seconds.**

This is the immediate, free optimization. The circuit, the VK, the proofs — everything stays identical. Only the prover backend changes from serial to parallel.

### Tier 1: Swap to the ecc-cash halo2 fork

Replace stock `halo2_proofs` with the [ecc-cash halo2 fork](https://github.com/zcash/halo2) — the production-optimized version with:
- Parallel Pippenger MSM (beyond what rayon provides — algorithmic improvement).
- Parallel FFT with better cache behavior.
- Pasta-curve assembly backends (platform-specific field arithmetic).

The circuit + VK + proofs are compatible (same proof system, same curves). This is a dependency swap, not a circuit change.

**Expected additional speedup:** ~2–3× on top of Tier 0. **Seconds → ~1–2s.**

### Tier 2: GPU acceleration (ICICLE-Halo2)

Offload the MSM + FFT to GPU via [Ingonyama's ICICLE-Halo2](https://www.ingonyama.com/post/2-fast-2-furious-icicle-halo2-v2) integration:

- ICICLE replaces the CPU MSM/FFT with CUDA kernels.
- Benchmarked at **25–50× speedup** on NVIDIA GPUs (RTX 4080/3090/4090).
- The circuit stays identical — only the prover backend moves to GPU.

**Expected speedup:** 25–50× → **sub-second proving.**

**GPU provisioning (crypto-native):** rent an NVIDIA GPU on a decentralized compute marketplace:
- **Akash Network** (AKT, Cosmos): fully on-chain GPU lease — broadcast an SDL deployment, providers bid, pay in AKT. StakeHub orchestrates the lease + prover container.
- **io.net** (IO, Solana): aggregated GPU marketplace, API-driven, larger pool. Pay in IO.

The StakeHub → GPU network path: StakeHub leases a GPU (Akash SDL / io.net API) → deploys the ICICLE-Halo2 prover container → feeds it the witness → gets the proof → submits the swap to PFTL → closes the lease. Fully crypto-native, no web signup, no fiat.

### Tier 3: Circuit-level optimizations

- **Reduce K** if the constraint count allows (K=15 = 32K rows if we're under 32K constraints).
- **Optimize Sinsemilla gadget layout** — the note commitments dominate; reducing the message pieces or using a more efficient Sinsemilla configuration saves gates.
- **Lookup table efficiency** — the range checks use lookup tables; tuning the table width reduces the lookup cost.
- **Batch proving** — if multiple swaps share the same anchor/structure, prove them in a single circuit (amortized MSM).

**Expected speedup:** ~1.5–2× on top of Tier 1/2.

### Tier 4: Proving service architecture

For production, the proving should be a **service** (not per-swap on-chain):

```text
user/StakeHub → lease GPU (Akash/io.net) → run ICICLE-Halo2 prover → submit proof to PFTL → close lease
```

- **PFTL's role:** verify the proof (fast, constant-size, in consensus). That's it.
- **StakeHub's role:** orchestrate the GPU lease + run the prover + submit. Off-chain.
- **GPU network's role:** provide the hardware. Paid in AKT/IO (crypto-native).

The proof generation is off-chain (StakeHub-controlled); PFTL only verifies. Clean separation: PFTL = truth (verify), StakeHub = execution (prove + submit), GPU network = compute (rent + run). No PFTL transaction type for GPU leasing — that's operator tooling.

## The optimization path summarized

| Tier | Optimization | Effort | Speedup | Prove time |
|---|---|---|---|---|
| **0** | Enable `multicore` (32 cores) | 1-line Cargo.toml | **~16–32×** | **~seconds** |
| **1** | Ecc-cash halo2 fork (assembly + Pippenger) | Dependency swap | +2–3× | **~1–2s** |
| **2** | GPU (ICICLE-Halo2, Akash/io.net) | Integration | 25–50× | **sub-second** |
| **3** | Circuit-level (K reduction, Sinsemilla tuning) | Circuit redesign | +1.5–2× | further reduction |
| **4** | Proving service (StakeHub → Akash/io.net) | Architecture | — | production scaling |

Tier 0 alone (enabling multicore on the 32-core box we already have) could close most of the gap — **minutes to seconds with a one-line change**. Tiers 1–4 stack on top for production-grade speed (sub-second, GPU-accelerated, crypto-native compute).

## What this means

The shielded NAVCoin swap circuit is **real, sound, and production-ready** — it's a complete Halo2 zk-SNARK with Sinsemilla note commitments, Merkle verification, Poseidon nullifier derivation, ECC spend authorization, per-asset conservation, and full domain binding. It's smaller than Zcash's Orchard circuit.

The proving speed is **not a circuit limitation** — it's an **engineering investment** in the prover backend. The same optimization path Zcash took (parallel MSM/FFT → assembly → GPU) is available to us, starting with a one-line feature flag that could give 16–32× on existing hardware.

The crypto-native GPU path (Akash/io.net + ICICLE-Halo2) makes the proving itself decentralized — StakeHub leases GPUs on-chain, pays in crypto, generates proofs at sub-second speed, submits to PFTL. The whole privacy stack — from compute rental to proof generation to on-chain verification — is crypto-native.

---

*Implementation: `postfiatl1v2` branch `navcoin-market-ops-envelope`, `crates/privacy_orchard/src/asset_orchard_circuit.rs` (the circuit), `asset_orchard_sinsemilla.rs` (the note-commitment gadget), `verify.rs` (the consensus verifier). Design spec: `docs/specs/asset-orchard-swap-circuit-design-v2.md` (TIH-reviewed, GPT-5.5-pro-rewritten). Proven live: a651↔a652 shielded swap on the 6-validator WAN devnet (2026-06-19).*
