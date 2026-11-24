---
title: "PFSH02: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering report, scope-matched same-host Orchard comparison (n = 50 proving, single-tx, and 4-tx batch verification), Lean 4 formalization, and security-status assessment for Peel-Binius-Shielded (PFSH02)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack."
aliases:
  - /peel-binius-curve-free-private-payments/
  - /blog/pfsh02/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Privacy
  - Post-Quantum
  - Binius
  - Zero-Knowledge
  - Lean 4
  - PFSH02
  - ML-KEM-1024
  - ML-DSA-65
  - Evidence
---

> **Research prototype — disabled on mainnet and unsuitable for live funds.**  
> Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security. **Spend authorization (Theorem 4)** requires external review of an unreviewed quantum random-oracle (QROM) simulation-extractability bridge (**Appendix A.4 / Theorem 2B**) and non-standard SHAKE256 assumptions; **confidentiality (Theorem 5)** covers only a single challenge transaction; and the Lean 4 models are not mechanically linked to the Rust or Go binaries. External review may require protocol redesign.

<div class="glance">
  <div><b>Off · Unaudited</b><span>Disabled on mainnet; governance supermajority can also pause all exits</span></div>
  <div><b>~15.1× Larger Wire</b><span>137,860 B full private pay vs. 9,145 B binary Orchard (~18.5× proof-only)</span></div>
  <div><b>20.4–43.1 ms Verify</b><span>1-core standalone medians vs. Orchard 44.3 ms (4-tx batch: Orchard 34.5 ms vs. PFSH02 50–85 ms)</span></div>
  <div><b>~4.8× Slower Prove</b><span>24.7 s vs. 5.13 s cached-key Orchard (1 core, n = 50); 2.64 s vs. 1.29 s (16 threads)</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted note envelopes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH02**) is our experimental replacement built without elliptic curves. We chose a binary-field Binius proof system over prime-field STARKs or lattice SNARKs because SHAKE256’s bitwise Keccak gates express natively over \(\mathbb{F}_2\) without prime-field bit decomposition, letting every underlying primitive come from NIST standards (**SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024**, and **ML-DSA-65**). Standardized building blocks do not establish the security of a novel proof system or its composition. Here is where the project stands:

- **Established on this host (internal, single-team):** End-to-end Rust/Go/L1 settlement, `750/750` `postfiat-node` library tests, a six-validator activation/pause/restart rehearsal (`0.55–1.0 s` block times), `n = 50` same-host Orchard benchmarks, and nine Lean 4 model modules checking core algebraic and operator derivations with zero `sorry`s and zero custom axioms.
- **Conditional (model-level only):** Value-conservation bounds (Theorem 3, conditional on published Reed–Solomon proximity-gap results and model-to-code fidelity) and wrapper-level simulation-extractability bounds inside Appendix A.4 / Theorem 2B.
- **Unresolved (blocking mainnet):** External audit of the Appendix A.4 real-to-wrapper bridge, five non-standard SHAKE256/ML-KEM assumptions, multi-transaction confidentiality, Lean-to-Rust/Go implementation linkage, `2^24`-leaf node restart scaling, and browser/mobile proving.

*Reading guide:* **Users and operators** → same-host comparison below and Section 1 (how payments work, governance exit-freeze power, privacy limits). **Cryptographers** → Section 3 (failure modes, Lean 4 audit matrix) and the [Companion Mathematical Appendix](/research/pfsh02-proofs/). **Validators and engineers** → Section 4 (benchmark matrix and test suites) and Section 5 (provenance, reproduction, and activation gates).

### Same-Host Baseline: Live Orchard vs. PFSH02 (AMD EPYC)

We benchmarked Post Fiat’s live 2-action Orchard Halo-2 implementation (`postfiat.privacy.orchard-halo2.v2`, `orchard 0.14.0`, via `orchard_proving_and_batch_budget`) directly against PFSH02 on the same host and pinned cores. Every row compares matching scopes and labels its exact sample size:

| Dimension (Scope-Matched) | Live Orchard (`orchard 0.14.0`) | PFSH02 Prototype |
| --- | --- | --- |
| **Core assumptions** | Discrete log on Pasta curves (Halo 2) | SHAKE256, `3×SHA-512`, ML-KEM-1024, ML-DSA-65 + unreviewed QROM bridges & non-standard hash/KEM assumptions |
| **Proof bytes only (2-output transfer)** | **`7,264 B`** (Halo 2 proof, 2 actions) | **`134,140 B`** measured (`134,813 B` expected; difference is Merkle sibling-pruning variance; **`~18.5×`**) |
| **Full binary 2-output transfer** | **`9,145 B`** canonical binary fields *(proof + `113 B` bundle + `2×884 B` actions; `9,297 B` w/ optional compact/binding fields)* | **`137,860 B`** full L1 private pay (**`~15.1×`**; `140,476 B` inner ceiling) |
| **Standalone 1-core verify (`CPU 2`, `n = 50` each)** | **`44.3 ms` med** (`47.0 ms` p95, `47.8 ms` max; cached VK, Halo 2 + RedPallas sigs) | **`20.4 ms`** Rust accel (`33.8 ms` max) · **`30.9 ms`** Go ASM (`32.5 ms` max) · **`42.8–43.1 ms`** pure Go (`44.1 ms` max) |
| **4-tx block verify (4 × 2-output transfers)** | **`87.4 ms` med** (1 core, `n = 50`, `BatchValidator`) · **`34.5 ms` med** (4 cores, `n = 50`, `34.8 ms` max) | **`92.9–102.2 ms`** accel / **`145.4–162.0 ms`** portable (1 core) · **`49.8–69.8 ms`** accel / **`78.8–85.1 ms`** portable (4 cores, validator `n = 21`/cond., no cross-tx batching) |
| **Client proving-only, 1 core (`CPU 2`, `n = 50` each)** | **`5.13 s` med** (`5.66 s` p95, `6.33 s` max; cached proving key; one-time key build `4.04 s`) | **`24.61–24.71 s` med** (**`~4.8×` slower**, `27.68 s` max, `~550 MiB` RAM; no key build; browser/mobile untested) |
| **Client proving-only, 16 threads** | **`1.29 s` med** (`n = 50`, `1.36 s` p95, `1.42 s` max; cached key) | **`2.64 s`** (**`~2.1×` slower**, `~550 MiB` RAM) |
| **Raw binary wire (`1 tx/s` / `4.0–7.3 tx/s`)** | **`~0.74 GiB/day`** (`1 tx/s`) · **`~2.9–5.4 GiB/day`** (`4.0–7.3 tx/s`, rate-matched; no fixed 4-tx block cap) | **`~11.1 GiB/day`** (`1 tx/s`) · **`~44–81 GiB/day`** (`4.0–7.3 tx/s` ceiling from `≤ 4` txs/block at measured `0.55–1.0 s` rehearsal blocks, before indexing/replication) |
| **Assurance status** | Externally audited upstream (`orchard`); deployed in Zcash | Unaudited single-team prototype; disabled on mainnet |

The tradeoff is clean and unambiguous:
- **Where PFSH02 is competitive:** On single-transaction 1-core verification, accelerated Rust (`20.4 ms` standalone; `23.6–24.1 ms` inside the validator) is roughly twice as fast as Orchard (`44.3 ms`), Go ASM (`30.9 ms`) is faster, and pure Go (`42.8–43.1 ms`) matches Orchard.
- **Where Orchard stays ahead:** When validating 4 transactions together, Orchard’s cryptographic `BatchValidator` beats PFSH02 on both 1 core (`87.4 ms` vs. `92.9–162.0 ms`) and 4 cores (`34.5 ms` vs. `49.8–85.1 ms`).
- **What this PFSH02 prototype costs:** **`~15.1×` larger full binary transactions** (`~18.5×` proof-only), **`~4.8×` slower single-core proving** (`~2.1×` slower on 16 threads, `~550 MiB` RAM), **`~44–81 GiB/day`** of raw wire volume at peak block density, and **novel cryptography awaiting external review**.

---

## 1. Payment Flow, Governance Risks & Privacy Boundaries

![PFSH02 architecture diagram](/blog/pq-payments/pfsh02-architecture.svg)
*Figure 1. End-to-end lifecycle across Deposit, Private Pay (payerless issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH02 transaction consumes **two input slots** (using zero-value dummy slots when needed) and creates **two new private notes** while proving that total value is conserved without overflow:

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each amount is a 64-bit unsigned integer, and consensus enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can reach \(2^{66}\) or wrap around in 66-bit arithmetic.

1. **Deposit (Shield, \(v_{\mathrm{mint}} > 0\)).** A public L1 account signs a post-quantum ML-DSA-65 deposit (`5,261 B` for public key plus signature), moving public funds into the asset’s private note tree. The recipient’s shielded address and note blinding stay off-chain.
2. **Private Transfer (no public sender account).** The sender proves spend authority for two notes under a historical tree root, publishes two one-time nullifiers to prevent double spends, and posts two new note commitments plus two `1,670 B` encrypted envelopes (**ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM**). Neither native **PFT** nor governed issued-asset (`pfUSDC`) private transfers expose a public sender account or fee-paying signature: PFT fees burn inside the proof, while issued-asset fees (`0.000001 pfUSDC` in rehearsal) route into a governed `collected_private_fees` pot.
3. **Non-Interactive Offline Receive.** Recipients publish a static stealth address off-chain; senders need no online interaction at payment time. Wallets scan outputs locally (`4,722` outputs/s/core on this host) and accept a note only when decryption reproduces the on-chain commitment.
4. **Partial or Full Exit (Unshield, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits a public L1 destination after checking per-asset pool reserves and destination trustline rules, without revealing a public sender account.

### User, Governance & Operational Risks

- **Validator supermajority can freeze exits indefinitely (design choice):** Scheduling activation, changing fees, pausing the pool, and disbursing `collected_private_fees` all require signed validator governance amendments meeting the active **BFT supermajority** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in rehearsal). Setting `paused: true` halts **all** shielded actions—deposits, transfers, **and exits**—until governance unpauses. That gives operators an emergency circuit breaker, at the cost of an explicit censorship and liquidity-freeze power over users’ shielded funds.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed issued assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves exact supply conservation (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`) without silent drift, but disbursement depends on validator governance rather than an autonomous protocol rule.
- **Epoch rollovers & anonymity-set dilution:** Native **PFT** and each governed issued asset maintain separate depth-24 trees holding \(2^{24} = 16,777,216\) leaves (`8,388,608` two-output transactions). An epoch lasts `~97.1 days` at `1 tx/s`, or **`~13.4–24.3 days`** at the `4.0–7.3 tx/s` ceiling (`≤ 4` txs/block at `0.55–1.0 s` rehearsal blocks). **Frozen trees remain spendable indefinitely via historical roots**—users are never forced to migrate notes to preserve funds—but every new spend writes its outputs into the *current* active epoch tree, where early outputs initially share a smaller active-epoch anonymity set than mature historical trees.
- **Observable metadata & migration linkage:** PFSH02 hides transfer amounts, recipient keys, and internal-spend sender accounts on the wire. Observers still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and network IP/timing metadata. Migrating from Orchard requires a public exit followed by a PFSH02 deposit, linking amounts and timing (splitting amounts and adding delays are heuristics, not guaranteed unlinkability).
- **Key hygiene & static-key compromise:**
  - *Unpinned brand-new deposit accounts:* A brand-new account that has never signed a transaction is identified only by a 160-bit address hash (`~2^-32` quantum preimage risk at `2^64` queries, vacuous at `2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating 160-bit exposure. **Operational step:** fund a fresh account with a minimal fee balance and send one low-value signed self-transfer to pin its public key before moving large deposits; automatic wallet enforcement is not yet built into the prototype CLI.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes all past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH02 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)
*Figure 2. Wire-size breakdown against the 149,130-byte archival cap (top) and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH02 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** All four note and Merkle hashes fit inside one Keccak-\(f[1600]\) permutation (`48 B` digests). Fifty-six permutations plus Merkle conditional-swap muxes, dummy-input gating, and 66-bit conservation adders pack into `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four engineering choices drive performance:
- **Exact 3D-Karatsuba ring-switch verifier:** Reduces extension-field multiplications by `11×`.
- **Single-step binary-field kernels:** 54-multiply Karatsuba routines with inline `mulC32` reduction and register-based linear maps across Rust (`PCLMULQDQ` + portable) and Go (ASM + `purego`).
- **Cheap-checks-first parallel validator:** Runs pool, anchor, and nullifier checks before proof verification, then verifies up to 4 proofs concurrently across scoped OS threads.
- **Streaming prover:** Keeps peak client memory near `550 MiB`.

Field arithmetic and interactive oracle proof (IOP) equations are detailed in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

### Wire Size & Archival Cap Accounting (`149,130 B` Cap)

Each row below states its exact encoding scope and proof-size basis (expected vs. measured fixture, which vary slightly due to Merkle sibling-pruning collisions) against the `149,130 B` archival cap:

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Proof Basis | Measured / Expected | Margin vs. Cap | Worst-Case Ceiling | Margin vs. Cap (Ceiling) |
| --- | --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`3,648 B` header + proof) | Expected (`134,813 B`) | 138,461 B *(138,364 B rollover)* | 10,669 B | 140,476 B | **8,654 B** |
| **L1 `pfUSDC` private pay** (`72 B` L1 prefix + `3,648 B` header + proof) | Measured (`134,140 B`) | **137,860 B** | **11,270 B** | 140,548 B *(140,476 inner)* | **8,582 B** |
| **L1 `pfUSDC` private exit** (`72 B` L1 prefix + `3,648 B` header + proof) | Measured (`135,004 B`) | **138,724 B** | 10,406 B | 140,548 B *(140,476 inner)* | **8,582 B** |
| **Standalone signed deposit wire** (adds `5,261 B` ML-DSA-65 pk + sig) | Expected (`134,813 B`) | 143,722 B | 5,408 B | 145,737 B | **3,393 B** |
| **L1 archived deposit — `redb` store** (rehearsal max body `144,397 B`) | Measured (`145,140 B` charged) | 144,770–145,140 B | 3,990–4,360 B | **146,546 B** | **2,584 B** |
| **L1 archived deposit — `JSONL` store** (adds JSONL envelope + digest name) | Measured | 144,804 B | 4,326 B | **146,580 B** | **2,550 B** |

Worst-case archived signed deposits leave `2,550–2,584 B` of ceiling margin. Raising the archival cap is an operational change; lowering Round-34 column openings (saving `~1.5 KB` per opening at a cost of `~5.4` bits of pure-IOP soundness) would be a **cryptographic parameter redesign requiring renewed soundness analysis and external re-audit**.

---

## 3. Security Failure Modes, Lean 4 Core & Audit Scope

![PFSH02 conditional QROM security curves](/blog/pq-payments/pfsh02-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum oracle query budget Q, showing the regime crossover at Q = 2^81.28 and the 160-bit unpinned deposit-account bound.*

![PFSH02 security dependency and blast-radius map](/blog/pq-payments/pfsh02-dependency-map.svg)
*Figure 4. Dependency and blast-radius map separating Value Conservation (Theorem 3), Authorization (Theorem 4), and Confidentiality (Theorem 5) by foundation type.*

Throughout our security model, \(Q\) denotes an adversary’s total number of quantum queries to the random-oracle hash functions. Full theorem statements, symbol definitions, exact-rational QROM bounds (for \(Q = 2^{64}, 2^{80}, 2^{96}\)), Lean 4 module tables, and 18 open reviewer questions live in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

Three distinct failure modes define the external audit surface (ordered to match Theorems 3, 4, and 5):
1. **Value-conservation failure (Theorem 3 — inflation / double-spend risk):** Concrete risks include misapplying published Reed–Solomon proximity-gap hypotheses ([BCIKS20](https://eprint.iacr.org/2020/654)), a discrepancy between the specification and the Rust/Go verifiers, or a SHAKE256/circuit constraint bug. Inside the specification’s QROM model, 384-bit proof-tree collisions also overtake spot-check error above \(Q = 2^{81.28}\) queries. Theorem 3 relies only on unmodified-oracle extraction and does not depend on Appendix A.4.
2. **Spend-authorization failure (Theorem 4 — theft without inflation):** Even if total supply never inflates, breaking spend authorization lets an attacker steal someone else’s shielded notes. End-to-end security here is **not established**: it depends on an unreviewed QROM view-equivalence bridge in **Appendix A.4 / Theorem 2B** (connecting real simulated proofs to the formalized wrapper oracle) plus non-standard SHAKE256 assumptions.
3. **Confidentiality limits (Theorem 5 — privacy loss):** Theorem 5 models only a single challenge transaction under five non-standard primitive assumptions (`JointPRF`, `PRG`, `Hide`, `IK-CCA`, and `IR-PRF`, defined in the appendix). Multi-transaction adaptive privacy is unmodeled.

### Lean 4 Formalization Scope & External Audit Matrix

To catch algebraic, operator-norm, case-analysis, and accounting errors before external review, we formalized the protocol’s core mathematical lemmas across nine **Lean 4 (`v4.20.0`) + Mathlib** modules (`formal/lean/PFSH02/`). All nine modules compile with zero `sorry`s and zero custom axioms (`#print axioms` reports only Lean’s standard `[propext, Classical.choice, Quot.sound]`). **Zero `sorry`s proves internal logical implication from explicit hypotheses—not that real-world assumptions hold or that the Rust/Go binaries match the model.**

| Property & Failure Mode | What Lean 4 Proves (Inside Model) | Assumptions & Unformalized Bridges (Audit Targets) | Implementation Linkage |
| --- | --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation*) | Exact-rational parameters, greedy peeling (`k ≤ 86`), polynomial/ring-switch bounds, rank-3 operator norm (`≤ √(8p)`) & compressed-oracle `∑√q` telescoping, and inductive supply conservation | Published literature interfaces ([BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654), GHHM21 Thm 1, AHU19 Thm 3); SHAKE256 384-bit collision and zero-preimage resistance | **Not mechanically linked** to Rust/Go verifiers or full 34-round SHAKE256 circuit wiring (Z3 checks 66-bit adder, mux & dummy gating only) |
| **Spend Authorization** (Theorem 4, private spends — *theft*) | Unopened-leaf zero-knowledge bijection & capped-PoW distance bound; monotone bad-event bound & exhaustive three-case trichotomy inside the formalized wrapper oracle (**App. A.4 / Thm 2B**) | **Primary blocker:** Unreviewed view-equivalence bridge connecting real simulated proofs to the wrapper oracle (**App. A.4 / Thm 2B**), plus non-standard SHAKE256 `JointPRF`/`PRG` | **Not established end-to-end;** not linked to Rust/Go binaries |
| **Deposit Authorization** (Theorem 4, public deposits — *deposit forgery*) | Key-pinned vs. unpinned dichotomy (pinning the full ML-DSA-65 pubkey eliminates the 160-bit address-preimage term) | ML-DSA-65 EUF-CMA + SHA-384 CR for pinned accounts; **unpinned brand-new accounts remain weak** (160-bit hash preimage) | Checked by unit/rehearsal tests in `prepare_pq_account_debit`; manual external code audit required |
| **Confidentiality & Anonymity** (Theorem 5 — *privacy loss*) | Symmetric 5-game hybrid accounting (including receiver-anonymity sub-hop) | **Single-transaction model only** (multi-tx adaptive composition unmodeled); ML-KEM-1024 IND-CCA2, HMAC-SHA-384, AES-256-GCM + 5 non-standard assumptions (`IK-CCA`, `IR-PRF`, `JointPRF`, `PRG`, `Hide`) | Not mechanically linked to wallet/KEM implementation |

All conditional QROM numerical outputs from `Params.lean` and `math_bounds.json` are tabulated in the [Companion Mathematical Appendix](/research/pfsh02-proofs/) alongside their explicit hypotheses.

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements below ran on 24 November 2026 on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone PFSH02 and Orchard runs executed `n = 50` trials per condition pinned to CPU 2 (`RAYON_NUM_THREADS=1` for 1-core Orchard; `CPU 0–3` for 4-core Orchard). Inside-validator PFSH02 tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, both warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof blocks). These are single-host implementation measurements, not universal hardware guarantees or sustained multi-node results.

### 4.1 Verification & Proving Matrix (Internal Targets: `< 50 ms` Single-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload (Scope of Median Range) | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Internal Target |
| --- | --- | ---: | ---: | ---: | --- |
| **Orchard 1-tx baseline** (`n = 50`, cached VK) | Halo 2 + RedPallas, 1 core CPU 2 | **44.26 ms** | 47.01 ms | 47.82 ms | Reference baseline |
| **Orchard 4-tx batch baseline** (`n = 50`, cached VK) | `BatchValidator`, 1 core / **4 cores** | 87.36 ms / **34.54 ms** | 90.48 / 34.65 ms | 93.96 / **34.75 ms** | Reference baseline |
| **Standalone Rust verify** (`mint`/`hop1`/`hop2`, `n = 50` each) | Accelerated (`PCLMULQDQ`), 1 core | 20.35–20.43 ms | 20.99–26.45 ms | 33.81 ms *(20.21 full-tree)* | Met (`< 50 ms`) |
| **Standalone Go verify** (`mint`/`hop1`/`hop2`, `n = 50` each) | Accelerated (`PCLMULQDQ` ASM), 1 core | 30.82–31.11 ms | 31.18–31.99 ms | 32.45 ms *(31.26 full-tree)* | Met (`< 50 ms`) |
| **Standalone Go portable** (`mint`/`hop1`/`hop2`, `n = 50` each) | `-tags purego` (0 ASM), 1 core | 42.76–43.08 ms | 43.52–43.72 ms | **44.08 ms** | Met (`< 50 ms`) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core pinned | 23.58–24.06 ms | 23.78–36.91 ms | 37.17 ms | Met (`< 50 ms`) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable (no `PCLMULQDQ`), 1 core | 36.96–39.64 ms | 38.70–44.45 ms | **45.23 ms** | Met (`< 50 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n = 21`) | **Accelerated, 4-core parallel** | 49.82–69.75 ms | 73.26–87.64 ms | 102.10 ms | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n = 21`) | **Portable, 4-core parallel** | 78.76–85.05 ms | 88.14–99.01 ms | **108.44 ms** | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core sequential | 92.94–102.20 ms | 93.89–104.08 ms | 107.53 ms | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable, 1 core sequential | 145.43–161.96 ms | 147.20–**201.97 ms** | 180.30 ms valid · **207.96 ms invalid** | **Missed on invalid batches** (`p95 = 202.0 ms`, `max = 208.0 ms > 200 ms`); met with 4-core parallel |
| **Orchard client proving-only** (`n = 50`, cached PK) | 16 thr / 1 core CPU 2 | 1.29 s / **5.13 s** | 1.36 s / 5.66 s | 1.42 s / 6.33 s | Reference baseline |
| **PFSH02 client proving-only** (`mint`/`hop1`/`hop2`, `n = 50`, `~550 MiB` RSS) | 16 thr / 1 core CPU 2 | 2.64 s / **24.61–24.71 s** | 26.29–27.24 s (1c) | 27.68 s (1c) | Measured (EPYC host; browser/mobile untested) |

Single-core sequential portable validation of 4 attacker-crafted invalid proofs exceeded the `200 ms` target at both `p95` (`201.97 ms`) and maximum (`207.96 ms`). Gate 2 in Section 5 therefore requires measured qualification on representative validator hardware against the `< 200 ms` 4-proof invalid-batch ceiling (testing `PCLMULQDQ` support or `≥ 4` verification cores).

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites

*(Terminology: **M8** is our six-validator activation, pause, and restart rehearsal; **R64** is a separate 1,734-block live-devnet archive replayed to confirm zero drift while PQ payments are inactive.)*

| Suite | Result (24 Nov 2026) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,729` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib) |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`, `pq_payment_rehearsal_tests`)** | **Passed** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, `0.55–1.0 s` block times, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`) |
| **Historical live-devnet replays** | 1,734-block `R64` paired archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Note:* Rust, Go, Python, Z3, and Lean artifacts share one author team, so cross-language agreement checks internal consistency rather than providing independent external review.

---

## 5. Build Provenance, Evidence Artifacts & Activation Gates

**Build provenance:** All results come from [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2), branch `feat/pq-payments-production-candidate`, commit `d78f8f102d7779e2d49315c6441b5b54c67a0a7c` (cleanly mergeable onto `public/main`; Rust/Go validator and prover binaries are bit-identical to `ec58522dc`, with `26e5a10a5` adding `formal/lean/` and `d78f8f102` adding the standalone `orchard_proving_and_batch_budget` benchmark example).

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs, Lean 4 Map & 18 Reviewer Questions** | Symbol glossary, 9-module Lean 4 table, Lemmas 1–4, Thms 1A/1B/2A, App. A.3–A.4 (Thm 2B), App. B, Thms 3–5 & conditional bounds | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,729` LOC), `lakefile.toml`, `README.md` | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/d78f8f102d7779e2d49315c6441b5b54c67a0a7c/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | Provenance, Lean 4 summary, `n = 50` Orchard proving & batch-verify baselines, test counts & benchmark tables | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Rehearsal & Archive Replay Record** | Six-validator `M8` activation/pause/restart log plus separate `R64` 1,734-block pre-activation archive replay | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for the Lean 4 Mathlib cache + build, `~3 min` and `~3.7 GiB` peak RSS for `verify.sh`, `~5 min` for the `n = 50` 1-core Orchard proving/batch baseline, `~2 min` for `postfiat-node --lib`, and `~1 min` for the six-validator rehearsal.

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout d78f8f102d7779e2d49315c6441b5b54c67a0a7c   # branch feat/pq-payments-production-candidate

# 1. Build and kernel-verify all 9 Lean 4 proof modules (0 sorrys, 0 custom axioms)
(cd formal/lean && lake exe cache get && lake build PFSH02)

# 2. Verify 36 fixture/script checksums & run the 7-stage standalone suite
(cd tools/pft-binius-shielded-pq && sha256sum -c SHA256SUMS && ./verify.sh)

# 3. Run the same-host n = 50 Orchard proving-only & 4-bundle batch-verify baselines
RAYON_NUM_THREADS=1 PROVE_ITERS=50 VERIFY_ITERS=50 taskset -c 2 \
  cargo run --release --locked -p postfiat-privacy-orchard --example orchard_proving_and_batch_budget
RAYON_NUM_THREADS=4 PROVE_ITERS=4 VERIFY_ITERS=50 taskset -c 0-3 \
  cargo run --release --locked -p postfiat-privacy-orchard --example orchard_proving_and_batch_budget
RAYON_NUM_THREADS=16 PROVE_ITERS=50 VERIFY_ITERS=50 \
  cargo run --release --locked -p postfiat-privacy-orchard --example orchard_proving_and_batch_budget

# 4. Run the postfiat-node library suite (750 tests) and 6-validator M8 rehearsal
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation (Acceptance Criteria)

No activation date is set; PFSH02 remains disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic resolution and code audit:** External cryptographers must publish a signed written audit covering Theorem 3 (value conservation), Theorem 4 (spend and deposit authorization, including Appendix A.4 / Theorem 2B and SHAKE256 `JointPRF`/`PRG`), Theorem 5 (confidentiality), Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement code. Activation requires all three:
   - resolution of any gap in the Appendix A.4 / Theorem 2B real-to-wrapper bridge (redesigning if needed);
   - a peer-reviewed multi-transaction confidentiality reduction proving adaptive multi-tx unlinkability of proof transcripts and ML-KEM envelopes under explicit, non-waivable assumptions; and
   - closure and re-verification of every high or critical audit finding on the release commit.
2. **Production-genesis cut, measured hardware qualification, and scale validation:**
   - Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series;
   - run reproducible qualification benchmarks on representative validator hardware classes verifying `< 200 ms` max latency on attacker-crafted 4-proof invalid batches (testing `PCLMULQDQ` or `≥ 4` verification cores rather than relying on CPU flags alone);
   - implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and
   - publish measured browser-WASM/mobile proving and sustained multi-node load/storage results.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with wallet key-pinning enforcement for brand-new accounts, Orchard exit/re-deposit tooling, and explicit user-facing privacy guidance on migration linkage.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `d78f8f102`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/d78f8f102d7779e2d49315c6441b5b54c67a0a7c/formal/lean), the [Companion Mathematical Appendix](/research/pfsh02-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
