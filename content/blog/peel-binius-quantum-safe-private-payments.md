---
title: "PFSH02: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering report, same-host Orchard comparison (n = 50 proving and verification), Lean 4 formalization, and security-status assessment for Peel-Binius-Shielded (PFSH02)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack."
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
> Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security. **Spend authorization (Theorem 4)** rests on an unreviewed quantum random-oracle (QROM) simulation-extractability bridge (Appendix A.4 / Theorem 2B) and non-standard SHAKE256 assumptions; **confidentiality (Theorem 5)** covers only a single challenge transaction; and the Lean 4 models are not mechanically linked to the Rust or Go binaries. Independent review may require protocol redesign.

<div class="glance">
  <div><b>Off · Unaudited</b><span>Disabled on mainnet; governance can also pause all exits</span></div>
  <div><b>~15.1× Larger Wire</b><span>137.9 KB full payment vs. 9.1 KB binary Orchard</span></div>
  <div><b>~4.8× Slower Prove</b><span>24.7 s vs. 5.13 s cached-key Orchard (1 core)</span></div>
  <div><b>Core Blocker: Auth</b><span>Unreviewed spend-auth bridge &amp; single-tx privacy</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted notes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH02**) is our experimental replacement built without elliptic curves. We chose a binary-field Binius proof system over prime-field STARKs or lattice SNARKs because SHAKE256’s bitwise Keccak gates express natively over \(\mathbb{F}_2\) without prime-field bit decomposition, letting every building block come from NIST standards (**SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024**, and **ML-DSA-65**). Standardized primitives do not make a novel proof system or its composition secure.

### Current Project Status

- **Established on this host (internal, single-team):** End-to-end Rust/Go/L1 settlement, 750/750 `postfiat-node` library tests, a six-validator activation/pause/restart rehearsal (`0.55–1.0 s` block times), same-host Orchard benchmarks, and nine Lean 4 model modules checking core algebraic and operator proofs with zero `sorry`s and zero custom axioms.
- **Conditional (model-level only):** Value-conservation bounds (Theorem 3, conditional on published Reed–Solomon proximity-gap results and model-to-code fidelity) and wrapper-level simulation-extractability bounds inside Appendix A.4.
- **Unresolved (blocking mainnet):** External audit of the Appendix A.4 real-to-wrapper bridge, five non-standard SHAKE256/ML-KEM assumptions, multi-transaction confidentiality, Lean-to-Rust/Go implementation linkage, 16-million-note restart scaling, and browser/mobile client proving.

*Navigation:* **Users & operators** → comparison below and Section 1 (payment flow, governance freeze power, privacy limits). **Cryptographers** → Section 3 (failure modes, Lean 4 audit matrix) and the [Companion Mathematical Appendix](/research/pfsh02-proofs/). **Validators & engineers** → Section 4 (full benchmark and test tables) and Section 5 (provenance, reproduction, and activation gates).

### Same-Host Baseline: Live Orchard vs. PFSH02 (AMD EPYC)

We benchmarked Post Fiat’s live 2-action Orchard Halo-2 implementation (`orchard 0.14.0`, via `orchard_proving_and_batch_budget`) against PFSH02 on the same host and pinned cores. Sample sizes are stated per row; rows marked **†** compare standalone Orchard cryptographic verification against inside-validator PFSH02 runs that include pool, anchor, and nullifier checks:

| Metric (2-Output Private Transfer) | Live Orchard (`orchard 0.14.0`) | PFSH02 Prototype | Comparison |
| --- | --- | --- | --- |
| **Proof bytes only** | `7,264 B` | `134,140 B` measured (`134,813 B` expected) | **`~18.5×` larger** |
| **Full binary wire** | `9,145 B` canonical fields *(9,297 B w/ optional fields)* | `137,860 B` full L1 private pay | **`~15.1×` larger** |
| **1-tx verify, standalone 1 core (`CPU 2`, `n = 50`)** | `44.3 ms` med *(cached VK, Halo 2 + RedPallas)* | `20.4 ms` Rust accel · `30.9 ms` Go ASM · `42.8–43.1 ms` pure Go | `~2.2×` faster (accel) to parity (pure Go) |
| **4-tx verify, 1 core †** | `87.4 ms` med *(`n = 50`, standalone `BatchValidator`)* | `92.9–102.2 ms` accel · `145.4–162.0 ms` portable *(`n = 21`, validator)* | Orchard batch faster *(different scope †)* |
| **4-tx verify, 4 cores †** | `34.5 ms` med *(`n = 50`, standalone `BatchValidator`)* | `49.8–69.8 ms` accel · `78.8–85.1 ms` portable *(`n = 21`, validator)* | Orchard batch faster *(different scope †)* |
| **Client proving-only, 1 core (`CPU 2`, `n = 50`)** | `5.13 s` med *(cached key; one-time build `4.04 s`)* | `24.61–24.71 s` med *(~550 MiB RAM; no key setup)* | **`~4.8×` slower** |
| **Client proving-only, 16 threads** | `1.29 s` med *(`n = 50`, cached key)* | `2.64 s` *(~550 MiB RAM)* | **`~2.1×` slower** |
| **Raw wire at `1 tx/s` / `4.0–7.3 tx/s`** | `~0.74` / `~2.9–5.4 GiB/day` *(rate-matched; no 4-tx cap)* | `~11.1` / `~44–81 GiB/day` *(`≤ 4` tx/block at `0.55–1.0 s` rehearsal blocks)* | **`~15.1×` bandwidth & storage** |
| **Assurance status** | Audited upstream (`orchard`); live in Zcash | Unaudited single-team prototype; disabled on mainnet | Audit required |

In short: single-transaction verification is competitive with Orchard (and faster on hardware-accelerated paths), whereas multi-transaction batch verification, proving time, transaction size, and cryptographic maturity all favor Orchard today. Detailed p95/max, warm/cold-cache, and invalid-batch measurements are in Section 4.1.

---

## 1. How Payments Work & User / Governance Risks

![PFSH02 architecture diagram](/blog/pq-payments/pfsh02-architecture.svg)
*Figure 1. End-to-end lifecycle across Deposit, Private Pay (payerless issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH02 payment spends **two private input slots** (using zero-value dummy slots when needed) and creates **two new private notes** under one 66-bit unsigned integer conservation equation:

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each value is a 64-bit unsigned integer, and consensus enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can overflow.

1. **Deposit (Shield):** A public L1 account signs a post-quantum ML-DSA-65 deposit (`5,261 B` public key + signature), moving funds from its public balance into the asset’s private note tree. The recipient’s shielded address and blinding remain off-chain.
2. **Private Transfer (no public sender account):** The sender proves spend authority for two notes under a historical tree root, publishes two one-time nullifiers to block double spends, and posts two new commitments plus two `1,670 B` encrypted envelopes (ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM). Neither native **PFT** nor governed issued-asset (`pfUSDC`) private transfers expose a public sender or fee-payer account: PFT fees burn inside the proof, while issued-asset fees (`0.000001 pfUSDC` in rehearsal) collect in a governed `collected_private_fees` pot.
3. **Offline Receive:** Recipients publish a static stealth address off-chain; senders need zero interactive round trips. Wallets scan outputs locally (`4,722` outputs/s/core on our test host) and accept a note only when decryption reproduces the public commitment.
4. **Partial or Full Exit (Unshield):** Spends private notes and credits a public L1 destination after checking per-asset pool reserves and destination trustline rules, without exposing a public sender account.

### User, Governance & Operational Risks

- **Validator supermajority can freeze exits indefinitely:** Scheduling activation, changing fees, pausing the pool, and disbursing `collected_private_fees` all require signed validator governance amendments meeting the **BFT supermajority** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in rehearsal). Setting `paused: true` halts **all** shielded actions—deposits, transfers, **and exits**—until governance unpauses. This provides an incident circuit breaker, at the cost of an explicit censorship and liquidity-freeze power over users’ shielded funds.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves exact supply conservation (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`), but disbursement relies on validator governance rather than an autonomous protocol rule.
- **Epoch rollovers & anonymity-set dilution:** Native PFT and each governed issued asset maintain separate depth-24 trees holding \(2^{24} = 16,777,216\) leaves (`8,388,608` two-output transactions). An epoch lasts `~97.1 days` at `1 tx/s`, or **`~13.4–24.3 days`** at the `4.0–7.3 tx/s` ceiling. **Frozen trees remain spendable indefinitely via historical roots**—users are never forced to migrate notes to preserve funds—but every new spend places its outputs into the *current* active epoch tree, where early outputs initially share a smaller active-epoch anonymity set than mature historical trees.
- **Observable metadata & Orchard migration linkage:** Observers cannot see private transfer amounts, recipient keys, or internal-spend sender accounts, but they still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and network IP/timing metadata. Moving funds from Orchard to PFSH02 requires a public exit followed by a public deposit, linking amounts and timing (splitting amounts and adding delays are heuristics, not guaranteed unlinkability).
- **Key hygiene & static-key compromise:**
  - *Unpinned brand-new accounts:* A brand-new account that has never signed a transaction is identified only by a 160-bit address hash (`~2^-32` quantum preimage risk at `2^64` queries, vacuous at `2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating 160-bit exposure. **Operational step:** fund a fresh account with a minimal fee balance and send one low-value signed self-transfer before moving large deposits; automatic wallet enforcement is not yet built into the prototype CLI.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes all past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH02 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)
*Figure 2. Wire-size breakdown against the 149,130-byte archival cap (top) and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH02 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** All four note and Merkle hashes fit inside one Keccak-\(f[1600]\) permutation (`48 B` digests). Fifty-six permutations plus Merkle muxes, dummy-input gating, and 66-bit conservation adders pack into `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four engineering choices drive verifier and prover efficiency:
- **Exact 3D-Karatsuba ring-switch verifier:** Cuts extension-field multiplications by `11×` (from 384-bit naive folding to structured sub-block products; derivation in the appendix).
- **Single-step binary-field kernels:** 54-multiply Karatsuba routines with inline `mulC32` reduction and register-based linear maps across Rust (hardware-accelerated + portable) and Go (ASM + `purego`).
- **Cheap-checks-first parallel validator:** Runs pool, anchor, and nullifier checks before proof verification, then verifies up to 4 proofs concurrently across scoped OS threads.
- **Streaming prover:** Holds peak client memory near `550 MiB`.

### Wire Size & Archival Cap Accounting (`149,130 B` Cap)

Measured proofs differ slightly from expected proof sizes because Merkle sibling-pruning collisions vary per transaction. Each row lists its exact proof basis against the `149,130 B` archival cap:

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Proof Basis | Measured / Expected | Margin vs. Cap | Worst-Case Ceiling | Ceiling Margin |
| --- | --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`3,648 B` header + proof) | Expected (`134,813 B`) | 138,461 B *(138,364 B rollover)* | 10,669 B | 140,476 B | **8,654 B** |
| **L1 `pfUSDC` private pay** (`72 B` prefix + `3,648 B` header + proof) | Measured (`134,140 B`) | **137,860 B** | **11,270 B** | 140,548 B *(140,476 inner)* | **8,582 B** |
| **L1 `pfUSDC` private exit** (`72 B` prefix + `3,648 B` header + proof) | Measured (`135,004 B`) | **138,724 B** | 10,406 B | 140,548 B *(140,476 inner)* | **8,582 B** |
| **Standalone signed deposit wire** (adds `5,261 B` ML-DSA-65 pk + sig) | Expected (`134,813 B`) | 143,722 B | 5,408 B | 145,737 B | **3,393 B** |
| **L1 archived deposit — `redb` store** *(max body `144,397 B` + DB framing)* | Measured (`145,140 B` charged) | 144,770–145,140 B | 3,990–4,360 B | **146,546 B** | **2,584 B** |
| **L1 archived deposit — `JSONL` store** *(adds JSONL envelope + digest name)* | Measured | 144,804 B | 4,326 B | **146,580 B** | **2,550 B** |

Worst-case archived signed deposits leave `2,550–2,584 B` of headroom. Raising the archival cap is an operational change; lowering Round-34 column openings (saving `~1.5 KB` per opening at a cost of `~5.4` bits of pure-IOP soundness) would be a **cryptographic parameter redesign requiring renewed soundness analysis and external re-audit**.

---

## 3. Security Failure Modes, Lean 4 Core & Audit Scope

![PFSH02 conditional QROM security curves](/blog/pq-payments/pfsh02-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum oracle query budget Q, showing the 384-bit tree-collision crossover at Q = 2^81.28 and the 160-bit unpinned deposit-account bound.*

![PFSH02 security dependency and blast-radius map](/blog/pq-payments/pfsh02-dependency-map.svg)
*Figure 4. Dependency and blast-radius map separating Value Conservation (Theorem 3), Authorization (Theorem 4), and Confidentiality (Theorem 5) by foundation type.*

Throughout our security model, \(Q\) denotes an adversary’s total quantum queries to the random-oracle hash functions. Full theorem statements, symbol definitions, exact-rational QROM bounds, Lean 4 module tables, and 18 open reviewer questions live in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

Three failure modes define the external audit surface:
1. **Value conservation (Theorem 3 — inflation or double-spend risk):** Concrete risks include misapplying published Reed–Solomon proximity-gap results ([BCIKS20](https://eprint.iacr.org/2020/654)), a mismatch between the specification and the Rust/Go verifiers, or a SHAKE256/circuit constraint bug. Inside the specification’s QROM model, 384-bit proof-tree collisions also overtake spot-check error above \(Q = 2^{81.28}\) queries. Theorem 3 uses unmodified-oracle extraction only and does not depend on Appendix A.4.
2. **Spend authorization (Theorem 4 — theft without inflation):** Even if total supply cannot inflate, breaking spend authorization allows theft of another user’s shielded notes. End-to-end security here is **not established**: it depends on an unreviewed QROM view-equivalence bridge in **Appendix A.4 / Theorem 2B** (connecting real simulated proofs to the formalized wrapper oracle) plus non-standard SHAKE256 assumptions.
3. **Confidentiality (Theorem 5 — privacy loss):** Modeled only for a single challenge transaction under five non-standard assumptions (`JointPRF`, `PRG`, `Hide`, `IK-CCA`, and `IR-PRF`, defined in the appendix). Multi-transaction adaptive privacy is unmodeled.

### Lean 4 Formalization Scope & External Audit Matrix

We formalized the core mathematical lemmas across nine **Lean 4 (`v4.20.0`) + Mathlib** modules (`formal/lean/PFSH02/`, `2,729` LOC), compiling with zero `sorry`s and zero custom axioms (`#print axioms` reports only Lean’s standard `[propext, Classical.choice, Quot.sound]`). **Zero `sorry`s checks internal implication from explicit hypotheses—not that real-world assumptions hold or that the Rust/Go binaries match the model.**

| Property & Failure Mode | Checked in Lean 4 (Model Level) | Assumptions & Unformalized Audit Targets | Implementation Linkage |
| --- | --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation*) | Exact-rational parameters, greedy peeling (`k ≤ 86`), polynomial/ring-switch bounds, rank-3 operator norm (`≤ √(8p)`) & compressed-oracle telescoping, inductive supply conservation | Published literature bridges ([BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654), GHHM21 Thm 1, AHU19 Thm 3); SHAKE256 384-bit collision and zero-preimage resistance | **Not mechanically linked** to Rust/Go verifiers or full 34-round circuit wiring (Z3 checks 66-bit adder, mux & dummy gating only) |
| **Spend Authorization** (Theorem 4, private spends — *theft*) | Unopened-leaf zero-knowledge bijection, capped-PoW distance bound, monotone bad-event bound & three-case trichotomy inside the formalized wrapper oracle (App. A.4 / Thm 2B) | **Primary blocker:** Unreviewed view-equivalence bridge connecting real simulated proofs to the wrapper oracle (App. A.4 / Thm 2B), plus non-standard SHAKE256 `JointPRF`/`PRG` | **Not established end-to-end;** not linked to Rust/Go binaries |
| **Deposit Authorization** (Theorem 4, public deposits — *deposit forgery*) | Key-pinned vs. unpinned dichotomy (pinning the full ML-DSA-65 pubkey removes the 160-bit preimage term) | ML-DSA-65 EUF-CMA + SHA-384 CR for pinned accounts; **unpinned brand-new accounts remain weak** (160-bit preimage) | Tested in `prepare_pq_account_debit`; manual external code audit required |
| **Confidentiality & Anonymity** (Theorem 5 — *privacy loss*) | Symmetric 5-game hybrid accounting (including receiver-anonymity sub-hop) | **Single-transaction model only**; ML-KEM-1024 IND-CCA2, HMAC-SHA-384, AES-256-GCM + 5 non-standard assumptions (`IK-CCA`, `IR-PRF`, `JointPRF`, `PRG`, `Hide`) | Not mechanically linked to wallet/KEM code |

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements ran on 24 November 2026 on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone PFSH02 and Orchard tests ran `n = 50` trials per condition pinned to CPU 2 (`RAYON_NUM_THREADS=1` for 1-core Orchard; `CPU 0–3` for 4-core Orchard). Inside-validator PFSH02 tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof blocks). These are single-host measurements, not universal hardware guarantees.

### 4.1 Full Verification & Proving Matrix (Internal Targets: `< 50 ms` 1-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Target Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Orchard 1-tx baseline** (`n = 50`, cached VK) | Halo 2 + RedPallas, 1 core CPU 2 | **44.26 ms** | 47.01 ms | 47.82 ms | Baseline |
| **Orchard 4-tx batch baseline** (`n = 50`, cached VK) | Standalone `BatchValidator`, 1c / **4c** | 87.36 / **34.54 ms** | 90.48 / 34.65 ms | 93.96 / **34.75 ms** | Baseline |
| **PFSH02 standalone Rust** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ`), 1 core | 20.35–20.43 ms | 20.99–26.45 ms | 33.81 ms *(20.21 full-tree rollover)* | Met (`< 50 ms`) |
| **PFSH02 standalone Go** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ` ASM), 1 core | 30.82–31.11 ms | 31.18–31.99 ms | 32.45 ms *(31.26 full-tree rollover)* | Met (`< 50 ms`) |
| **PFSH02 standalone Go portable** (`mint`/`hop1`/`hop2`, `n = 50`) | `-tags purego` (0 ASM), 1 core | 42.76–43.08 ms | 43.52–43.72 ms | **44.08 ms** | Met (`< 50 ms`) |
| **PFSH02 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core pinned | 23.58–24.06 ms | 23.78–36.91 ms | 37.17 ms | Met (`< 50 ms`) |
| **PFSH02 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable (no `PCLMULQDQ`), 1 core | 36.96–39.64 ms | 38.70–44.45 ms | **45.23 ms** | Met (`< 50 ms`) |
| **PFSH02 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Accelerated, 4-core parallel** | 49.82–69.75 ms | 73.26–87.64 ms | 102.10 ms | Met (`< 200 ms`) |
| **PFSH02 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Portable, 4-core parallel** | 78.76–85.05 ms | 88.14–99.01 ms | **108.44 ms** | Met (`< 200 ms`) |
| **PFSH02 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core sequential | 92.94–102.20 ms | 93.89–104.08 ms | 107.53 ms | Met (`< 200 ms`) |
| **PFSH02 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable, 1 core sequential | 145.43–161.96 ms | 147.20–**201.97 ms** | 180.30 ms valid · **207.96 ms invalid** | **Missed on invalid batches** (`p95 = 202.0 ms`, `max = 208.0 ms`) |
| **Orchard proving-only** (`n = 50`, cached PK) | 16 thr / 1 core CPU 2 | 1.29 s / **5.13 s** | 1.36 s / 5.66 s | 1.42 s / 6.33 s | Baseline |
| **PFSH02 proving-only** (`mint`/`hop1`/`hop2`, `n = 50`, ~550 MiB) | 16 thr / 1 core CPU 2 | 2.64 s / **24.61–24.71 s** | 26.29–27.24 s (1c) | 27.68 s (1c) | Measured (browser/mobile untested) |

*(Note: "full-tree rollover" measures verifying a spend right at the `2^24`-leaf epoch boundary.)* Because single-core sequential portable validation of 4 invalid proofs missed the `200 ms` target at both `p95` (`201.97 ms`) and maximum (`207.96 ms`), Gate 2 requires measured hardware qualification against that invalid-batch ceiling.

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites

| Suite | Result (24 Nov 2026) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,729` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib) |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`)** | **Passed** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, `0.55–1.0 s` block times, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`) |
| **Historical live-devnet replays (`R64` + 1,754-block)** | 1,734-block `R64` pre-activation archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Note:* Rust, Go, Python, Z3, and Lean artifacts share one author team, so cross-language agreement checks internal consistency rather than independent external review.

---

## 5. Build Provenance, Evidence Artifacts & Activation Gates

**Build provenance:** [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2), branch `feat/pq-payments-production-candidate`, commit `d78f8f102d7779e2d49315c6441b5b54c67a0a7c` (cleanly mergeable onto `public/main`; Rust/Go validator and prover binaries are bit-identical to `ec58522dc`, with `26e5a10a5` adding `formal/lean/` and `d78f8f102` adding `orchard_proving_and_batch_budget.rs`).

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & 18 Reviewer Questions** | Symbol glossary, 9-module Lean 4 map, full theorem statements, conditional QROM bounds & reviewer questions | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,729` LOC), `lakefile.toml`, `README.md` | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/d78f8f102d7779e2d49315c6441b5b54c67a0a7c/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | Provenance, Lean 4 summary, `n = 50` Orchard proving & batch-verify baselines, test counts & benchmark tables | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Rehearsal & Archive Replay Record** | Six-validator `M8` activation/pause/restart log plus separate `R64` 1,734-block pre-activation archive replay | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for Lean 4, `~3 min` (~3.7 GiB RSS) for `verify.sh`, `~5 min` for the `n = 50` 1-core Orchard run (`PROVE_ITERS=4` in the 4-core run builds only the 4 bundles needed for the 50-trial batch verifier), `~2 min` for `postfiat-node --lib`, and `~1 min` for the six-validator rehearsal.

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

### Three Gates Before Mainnet Activation

No activation date is set; PFSH02 stays disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic resolution and code audit:** External cryptographers must publish a signed audit covering Theorem 3 (value conservation), Theorem 4 (spend and deposit authorization, including Appendix A.4 / Theorem 2B and SHAKE256 `JointPRF`/`PRG`), Theorem 5 (confidentiality), Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement code. Activation requires:
   - resolution of any gap in the Appendix A.4 / Theorem 2B real-to-wrapper bridge (redesigning if needed);
   - a peer-reviewed multi-transaction confidentiality reduction proving adaptive multi-tx unlinkability of proof transcripts and ML-KEM envelopes under explicit, non-waivable assumptions; and
   - closure and re-verification of every high or critical audit finding on the release commit.
2. **Production-genesis cut, measured hardware qualification, and scale validation:**
   - Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series;
   - run reproducible qualification benchmarks on representative validator hardware verifying `< 200 ms` max latency on attacker-crafted 4-proof invalid batches (testing `PCLMULQDQ` or `≥ 4` verification cores rather than relying on CPU flags alone);
   - implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and
   - publish measured browser-WASM/mobile proving and sustained multi-node load/storage results.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with wallet key-pinning enforcement for brand-new accounts, Orchard exit/re-deposit tooling, and explicit user-facing privacy guidance on migration linkage.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `d78f8f102`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/d78f8f102d7779e2d49315c6441b5b54c67a0a7c/formal/lean), the [Companion Mathematical Appendix](/research/pfsh02-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
