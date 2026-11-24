---
title: "PFSH03: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering report, same-host Orchard comparison, Lean 4 formalization, WASM32/low-RSS prover benchmarks, two-tier exit-safe pause, fail-fast verifier hardening, and security-status assessment for Peel-Binius-Shielded (PFSH03)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack."
aliases:
  - /peel-binius-curve-free-private-payments/
  - /blog/pfsh02/
  - /blog/pfsh03/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Privacy
  - Post-Quantum
  - Binius
  - Zero-Knowledge
  - Lean 4
  - PFSH03
  - ML-KEM-1024
  - ML-DSA-65
  - Evidence
---

> **Research prototype — disabled on mainnet and unsuitable for live funds.**  
> Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security. Both **value conservation** and **spend authorization** share one unreviewed single-oracle quantum random-oracle (QROM) extraction argument (**Theorem 2A**) and its circuit wiring, **multi-transaction confidentiality** relies on unreviewed privacy assumptions (and degrades if users reuse static receive addresses), and the Lean 4 models check algebraic and reduction plumbing from explicit hypotheses rather than linking mechanically to the compiled Rust or Go binaries. Independent external review may still require protocol changes.

<div class="glance">
  <div><b>Off · Unaudited</b><span>Disabled on mainnet; exit-safe pause + renewable 604,800-block freeze</span></div>
  <div><b>~16.4× Larger Wire</b><span>149.6 KB raw tx vs. 9.1 KB Orchard (~95% prunable on non-archive nodes)</span></div>
  <div><b>355 MiB Native · 39.4 s WASM</b><span>Subtree-streaming prover (-37% RSS); 1-thread V8 measured</span></div>
  <div><b>Main Blocker: Audit</b><span>Unaudited Theorem 2A SPOF, circuit wiring, DoS &amp; binaries</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted notes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH03**) is our experimental replacement built without elliptic curves. We chose a binary-field Binius proof system over prime-field STARKs or lattice SNARKs because SHAKE256’s bitwise Keccak gates express natively over \(\mathbb{F}_2\) without prime-field bit decomposition, letting every building block come from NIST standards (**SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024**, and **ML-DSA-65**). Standardized primitives do not make a novel proof system or its composition secure.

**Model-level security target (conditional, unreviewed):** Conditional on our unreviewed single-oracle QROM extraction proof (**Theorem 2A / App. A.1–A.3**), **FIPS-204 ML-DSA-65**, and 384-bit SHAKE256/SHA-384 collision resistance, the PFSH03 soundness upper bound reaches trivial probability `1` at \(Q = 2^{126.75}\) quantum oracle queries (`~126-bit` QROM model target, governed by 384-bit proof-tree collisions, with bound \(< 2^{-137.55}\) at \(Q = 2^{80}\) and \(< 2^{-92.25}\) at \(Q = 2^{96}\)). This figure marks where the conditional proof bound becomes vacuous—not an audited security guarantee or demonstrated attack cost. The sole sub-126-bit exception is an unpinned brand-new public L1 deposit account (`~80-bit` quantum address preimage until its first key-pinning transaction; strict pre-debit enforcement is available via `prepare_pq_account_debit_pinned`).

### Current Project Status

- **Established on this host (internal, single-team):** End-to-end Rust/Go/L1 PFSH03 settlement (`751/751` `postfiat-node` tests, six-validator M8 rehearsal, `7/7` `verify.sh` with expanded Z3 + Rust/Go differential `pk_hash0/1` audit), two-tier exit-safe pause + auto-expiring emergency exit-freeze, pruned-node `pq_bodies_v1` storage (`~95%` disk savings), fail-fast verifier ordering + 4-thread sibling cancellation, low-RSS subtree-streaming prover (`355–361 MiB`, ARM64 `PMULL` kernels, and a `39.36 s` single-threaded V8 WASM32 baseline), same-host Orchard benchmarks, and nine Lean 4 model modules (`2,847` LOC, 0 `sorry`s, 0 custom axioms).
- **Conditional (model-level only):** Both **value conservation** and **spend authorization** reduce in the formal model to the same unmodified-oracle extraction argument (**Theorem 2A**) plus **FIPS-204 ML-DSA-65**, our zero-query-blowup 3-block `SHA-512` → 1,536-bit QRO simulation (`three_block_sha512_qro_reduction`), and 384-bit collision resistance—conditional on [BCIKS20](https://eprint.iacr.org/2020/654), external verification of Theorem 2A, and model-to-code fidelity. **Multi-transaction adaptive confidentiality** is formalized in Lean 4 for fresh per-note addresses, conditional on QROM zero-knowledge and remaining privacy assumptions.
- **Unresolved (blocking mainnet):** Independent external audit of Theorem 2A (shared single point of failure for inflation and theft), `pk_hash0/1` circuit wiring, remaining privacy assumptions (`IK-CCA`, `IR-PRF`, `Hide`, dummy `PRG`), adversarial invalid-proof DoS & mempool admission backpressure, Lean-to-Rust/Go implementation linkage, 16-million-note restart checkpointing, and real mobile/Safari WebView proving.

*Navigation:* **Users & operators** → Section 1 (payment flow, two-tier exit-safe pause, pruned storage, address-reuse and privacy limits) and comparison below. **Cryptographers** → Section 3 (Theorem 2A SPOF, `3 × SHA-512` QRO reduction, explicit Lean 4 scope limits) and the [Companion Mathematical Appendix](/research/pfsh03-proofs/). **Validators & engineers** → Section 4 (native, WASM32, and fail-fast rejection benchmarks) and Section 5 (provenance, reproduction, and activation gates).

### Same-Host Baseline: Live Orchard vs. PFSH03 (AMD EPYC)

We benchmarked Post Fiat’s live 2-action Orchard Halo-2 implementation (`orchard 0.14.0`, via `orchard_proving_and_batch_budget`) against **PFSH03** on the same host and pinned cores. Sample sizes are stated per row; rows marked **†** compare standalone Orchard cryptographic verification against inside-validator PFSH03 runs that include ML-DSA-65 spend-auth, pool, anchor, and nullifier checks:

| Metric (2-Output Private Transfer) | Live Orchard (`orchard 0.14.0`) | PFSH03 Prototype | Comparison |
| --- | --- | --- | --- |
| **Proof bytes only** | `7,264 B` | `135,340 B` measured (`134,813 B` expected) | **`~18.6×` larger** |
| **Full binary wire** | `9,145 B` canonical fields *(9,297 B w/ optional fields)* | `149,582 B` full L1 private pay *(incl. 10.5 KB ML-DSA-65)* | **`~16.4×` larger** |
| **1-tx verify, standalone 1 core (`CPU 2`, `n = 50`)** | `44.26 ms` med *(cached VK; Halo 2 + RedPallas spend-auth)* | `22.1–22.2 ms` Rust accel · `33.6–33.7 ms` Go ASM · `45.4–46.0 ms` pure Go *(incl. 2× ML-DSA-65 + Binius; in-validator `24.5–25.1 ms`)* | `~2.0×` faster (accel) to parity (pure Go) |
| **Fail-fast invalid-tx reject (`1 core`, `n = 20`)** | N/A *(full batch check)* | `0.22 ms` bad sig · `0.53 ms` bad 20-bit PoW/transcript · `15.33 ms` valid-PoW bad Merkle | Rejects bad sig/PoW before Merkle math |
| **4-tx verify, 1 core †** | `87.36 ms` med *(`n = 50`, standalone `BatchValidator`)* | `95.5–140.9 ms` accel · `146.6–147.9 ms` portable *(`n = 21`, validator)* | Orchard batch faster *(different scope †)* |
| **4-tx verify, 4 cores †** | `34.54 ms` med *(`n = 50`, standalone `BatchValidator`)* | `47.4–47.8 ms` accel · `79.2–79.7 ms` portable *(`n = 21`, validator; `0.0002 ms` sibling abort)* | Orchard batch faster *(different scope †)* |
| **Client proving-only, native 1 core (`CPU 2`)** | `5.13 s` med *(`n = 50`, cached key; `4.04 s` setup)* | `24.62–25.67 s` med *(`355 MiB` peak RSS via subtree streaming; no setup)* | **`~4.8–5.0×` slower** |
| **Client proving-only, native 16 threads** | `1.29 s` med *(`n = 50`, cached key)* | **`2.66 s`** med *(`361 MiB` peak RSS; down `-37%` from `572 MiB`)* | **`~2.1×` slower** |
| **Client proving-only, WASM32+SIMD128 (`V8`, 1 thr)** | Not measured on this host | **`39.36 s`** prove · **`70.80 ms`** verify · **`378.9 MiB`** linear mem (`830 KB` `.wasm`) | First browser-engine baseline *(mobile/Safari untested)* |
| **Archive wire vs. pruned validator disk (`4.0–7.3 tx/s`)** | `~2.9–5.4 GiB/day` *(rate-matched; no 4-tx cap)* | `~48–88 GiB/day` full archive · **`~1.3–2.4 GiB/day`** pruned (`~4 KB/tx` retained via `prune_pq_bodies`) | `~16.4×` wire; **`~95%` prunable** on non-archive nodes |
| **Assurance status** | Audited upstream (`orchard`); live in Zcash | Unaudited single-team prototype; disabled on mainnet | Audit required |

Single-transaction verification is competitive with Orchard (and faster on hardware-accelerated paths), fail-fast ordering drops malformed signatures and PoW before Merkle verification, and subtree streaming cut native prover RAM by 37% (`355–361 MiB`) alongside an `830 KB` WASM32 module (`39.36 s` single-threaded in V8). Proving speed, raw wire size, multi-transaction batch verification, and cryptographic maturity still favor Orchard today.

---

## 1. How Payments Work & User / Governance Risks

**Plain-language summary for users:** Today PFSH03 is off on mainnet and should not hold live funds. When active in a future audited release, sending a private payment takes `~25 s` on one native core (`~2.7 s` across 16 threads, or `~39 s` single-threaded in WASM32) using `~355–379 MiB` RAM. Users should generate a fresh receive address for each incoming payment so later spends stay unlinkable, and should let wallets pin brand-new public deposit accounts with one small signed transaction before large deposits. Under our upgraded **two-tier governance circuit breaker**, a standard operational pause halts new deposits and internal transfers while **leaving exits open**; freezing exits requires a separate elevated quorum (`6/6` unanimous in rehearsal) with each freeze amendment expiring automatically after at most `604,800` blocks (`~7 days` at `1 s` blocks) unless unanimously renewed.

![PFSH03 architecture diagram](/blog/pq-payments/pfsh03-architecture.svg)
*Figure 1. PFSH03 lifecycle across Deposit, Private Pay (external per-note ML-DSA-65 spend authorization + payerless issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH03 payment spends **two private input slots** (using zero-value dummy slots when needed) and creates **two new private notes** under one 66-bit unsigned integer conservation equation:

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each value is a 64-bit unsigned integer, and consensus enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can overflow.

1. **Deposit (Shield):** A public L1 account signs a post-quantum ML-DSA-65 deposit (`5,261 B` public key + signature), moving funds from its public balance into the asset’s private note tree. The recipient’s shielded address and blinding remain off-chain.
2. **Private Transfer (no public L1 sender account):** Each input slot carries an external per-note ML-DSA-65 public key and signature committing to the transaction context (outputs, envelopes, anchor, nullifiers, asset, epoch, fee, and exit destination), verified **before** Binius. Neither native **PFT** nor governed issued-asset (`pfUSDC`) private transfers expose a public L1 sender or fee-payer account: PFT fees burn inside the proof, while issued-asset fees (`0.000001 pfUSDC` in rehearsal) collect in a governed `collected_private_fees` pot.
3. **Offline Receive with Per-Note Indexed Addresses:** Wallets derive fresh receive addresses (`wallet.address(index)`) deterministically from one recovery seed—each with its own independent `(pk_dsa, r_pk)` blinded behind `A = H_A(pk_hash, r_pk)`—so senders need zero interactive round trips and never learn `pk_dsa`. Wallets scan outputs locally (`~3,500–4,700` trials/s/core in rehearsal) and accept a note only when decryption reproduces the public commitment.
4. **Partial or Full Exit (Unshield):** Spends private notes and credits a public L1 destination after checking per-asset pool reserves and destination trustline rules, without exposing a public sender account.

### User, Governance & Operational Risks

- **Two-tier exit-safe pause & block-capped (renewable) emergency exit-freeze:**
  - *Tier 1 — Standard Pause (`pq_payment_rehearsal_v1`, value = 0; standard BFT supermajority \(\lfloor 2n/3 \rfloor + 1 = 5/6\)):* Halts new **deposits (`Shield`)** and **private transfers (`Internal`)** while keeping **`Mode::Exit` open** (preserving the last active issued-asset exit fee via `pq_issued_fee_for_mode`) so users can withdraw during a routine pause.
  - *Tier 2 — Emergency Exit-Freeze (`pq_exit_freeze_until_v1`):* Freezing exits is isolated to a separate amendment requiring an **elevated quorum** (\(\min(n, \lfloor 5n/6 \rfloor + 1)\)—**6 of 6 unanimous** in rehearsal) and a mandatory block-height expiry **hard-capped at `MAX_PQ_EXIT_FREEZE_BLOCKS = 604,800` blocks** past inclusion height (`~7 days` at `1 s` blocks, though wall-clock duration depends on actual block cadence). A single freeze amendment **automatically expires** at `freeze_until + 1` with no governance action required, eliminating unattended indefinite freezes. However, because a unanimous validator set can enact consecutive renewals, users must still treat coordinated unanimous validator censorship as an explicit trust assumption rather than a hard cryptographic withdrawal guarantee.
- **Static-address reuse links spends (safe against theft, weakens unlinkability):** Because PFSH03 reveals `pk_in` at *spend* time (never at receive time), fresh indexed receive addresses keep spends unlinkable across transactions. Reusing one static receive address across multiple notes does not weaken theft protection (ML-DSA-65 is many-time EUF-CMA), but spending two notes from that same static address publishes the same `pk_dsa` on-chain and publicly links those spends. Wallets must default to fresh per-note addresses and rotate change keys automatically.
- **Throughput ceiling, storage pruning & anonymity-set fragmentation:** At `~150 KB/tx` and `≤ 4` proofs per block (`640,000 B` block cap), peak private throughput is **`~4.0–7.3 tx/s`** (`~48–88 GiB/day` raw wire on full archive nodes). For **non-archive validators**, `NodeStore::prune_pq_bodies` (`crates/storage/src/pq_archive.rs`) deletes verified `pq_bodies_v1` proof blobs outside a kept checkpoint window—reclaiming **`~95%` of PQ disk usage** (`~150 KB → ~4 KB/tx`, `~1.3–2.4 GiB/day` at ceiling) while retaining `pq_pool` output pages, commitments, envelopes, and global nullifiers for wallet scanning. Separate per-asset, per-epoch depth-24 trees (`8,388,608` two-output transactions per epoch, `~13.4–24.3 days` at ceiling, `~97.1 days` at `1 tx/s`) still fragment anonymity sets across assets and fresh epochs; unified multi-asset pools (MASP), depth-32 trees, and proof-size reductions are deferred to a future **PFSH04** design.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves exact supply conservation (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`), but disbursement relies on validator governance rather than an autonomous protocol rule.
- **Observable metadata & Orchard migration linkage:** Observers still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and network IP/timing metadata. Moving funds from Orchard to PFSH03 requires a public exit followed by a public deposit, linking amounts and timing.
- **Key hygiene & static-key compromise:**
  - *Unpinned brand-new L1 deposit accounts:* A brand-new public L1 account that has never signed a transaction is identified only by a 160-bit address hash (`~2^-32` quantum preimage risk at `2^64` queries, vacuous at `2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating 160-bit exposure; strict pre-debit enforcement is available via `prepare_pq_account_debit_pinned`. **Operational step:** pin fresh accounts with one low-value signed self-transfer before large deposits; wallet-enforced pinning is part of Gate 3.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction, Prover Optimizations & Wire Accounting

![PFSH03 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh03-wire-and-iop.svg)
*Figure 2. PFSH03 wire-size breakdown against the 160,000-byte archival cap (top), highlighting the 10,522-byte external ML-DSA-65 spend-authorization block, and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH03 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** Every note owner address binds the hash of a per-note ML-DSA-65 public key to a secret blinding/nullifier key \(r_{\mathrm{pk}}\):
  $$A = \mathrm{SHAKE256}\bigl(\texttt{0x00} \parallel \mathrm{pk\_hash}_{48} \parallel r_{\mathrm{pk},48}\bigr), \qquad \mathrm{SN} = \mathrm{SHAKE256}\bigl(\texttt{0x02} \parallel r_{\mathrm{pk},48} \parallel \mathrm{Coin}_{48}\bigr)$$
  Because \(1 + 48 + 48 = 97 \le 135\) bytes fits inside one Keccak-\(f[1600]\) permutation (`p = 0, 3`), all 56 permutations, Merkle muxes, dummy-input gating, and 66-bit conservation adders remain at `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step. Public `pk_hash0` and `pk_hash1` enter as constant statement bits.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from `H(x) = SHA-512(0x00||x) || SHA-512(0x01||x) || SHA-512(0x02||x)` with a `512`-bit internal Fiat–Shamir state and fixed-length prefix-free domain tags (`encode_statement = 408 B`).

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), five engineering optimizations drive verifier and prover performance:
- **Exact 3D-Karatsuba ring-switch verifier:** Cuts extension-field multiplications by `11×` (derivation in the appendix).
- **Single-step binary-field kernels (`PCLMULQDQ`, ARM64 `PMULL`, portable & WASM32):** 54-multiply Karatsuba routines with inline `mulC32` reduction across Rust (`PCLMULQDQ`, branchless ARM64 `vmull_p64` `PMULL`, portable, and sequential `wasm32-unknown-unknown +simd128`) and Go (ASM + `purego`).
- **Fail-fast verifier ordering + cooperative 4-thread abort:** Both Rust (`verify_abortable`) and Go (`verifyBiniusProof`) verify external ML-DSA-65 spend signatures, Fiat–Shamir transcript replay, non-zero challenge guards, the **20-bit Round-34 PoW (`eval_h_c4`)**, opened-column count, and Ring-Switching sum check **before** circuit MLE evaluation, 3D-Karatsuba ring-switch, or Merkle path hashing. Parallel 4-proof block validation shares an `AtomicBool` abort flag so sibling threads cancel on the first invalid proof.
- **Subtree-root streaming prover (`-37%` peak RSS, bit-identical proofs):** Instead of retaining `201.3 MiB` of `MT_1` leaf digests across Sumcheck 1, the prover retains only `2,048` height-10 subtree roots (`192 KiB`) and recomputes only the `≤ 52` touched 1,024-leaf subtrees at Round 34—cutting native peak RSS from `572 MiB` to **`355–361 MiB`** while producing bit-identical proofs.
- **WASM32+SIMD128 compilation:** A `wasm32` sequential parallel-iterator shim lets the exact Rust prover and verifier compile to an **`830 KB` `.wasm`** module measured directly in V8.

### Wire Size & Archival Cap Accounting (`160,000 B` Cap)

External per-note ML-DSA-65 spend authorization adds `10,522 B` (`2 × 1,952 B` pk + `2 × 3,309 B` sig) to every transaction under the `160,000 B` archival ceiling (`640,000 B` per 4-payment block). Measured proofs vary slightly because Merkle sibling-pruning collisions differ per transaction:

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Proof Basis | Measured / Expected | Margin vs. Cap | Worst-Case Ceiling | Ceiling Margin |
| --- | --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`14,170 B` header+auth + proof) | Expected (`134,813 B`) | 148,983 B *(148,814 B rollover)* | 11,017 B | 150,998 B | **9,002 B** |
| **L1 `pfUSDC` / `PFT` private pay** (`72 B` prefix + `14,170 B` + proof) | Measured (`135,340 B`) | **149,582 B** | **10,418 B** | 151,070 B *(150,998 inner)* | **8,930 B** |
| **L1 `pfUSDC` private exit** (`72 B` prefix + `14,170 B` + proof) | Measured (`134,668 B`) | **148,910 B** *(148,958 PFT)* | 11,090 B | 151,070 B *(150,998 inner)* | **8,930 B** |
| **Standalone signed deposit wire** (adds `5,261 B` deposit ML-DSA-65) | Expected (`134,813 B`) | 154,244 B | 5,756 B | 156,259 B | **3,741 B** |
| **L1 archived deposit — `redb` store** *(verified `153,143 B` body + framing)* | Measured (`153,852 B` stored) | 153,852 B *(M8 max `155,902 B`)* | 4,098–6,148 B | **157,068 B** | **2,932 B** |
| **L1 archived deposit — `JSONL` store** *(adds JSONL envelope + digest)* | Measured (`153,886 B` stored) | 153,886 B | 6,114 B | **157,102 B** | **2,898 B** |

Worst-case archived signed deposits leave `2,898–2,932 B` of headroom under `160,000 B`. We do **not** lower Round-34 column openings (`t = 52`) to save bytes: each dropped opening saves `~1.5 KB` at a cost of `~5.4` bits of pure-IOP soundness and would require renewed soundness analysis and external re-audit.

---

## 3. Security Failure Modes, Lean 4 Scope & Audit Matrix

![PFSH03 conditional QROM security curves](/blog/pq-payments/pfsh03-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage upper bounds versus quantum oracle query budget Q, showing unmodified-oracle Theorem 2A (shared by Value Conservation and Spend Authorization, becoming vacuous at Q = 2^126.75), the 384-bit tree-collision crossover at Q = 2^81.28, and the 160-bit unpinned deposit-account bound.*

![PFSH03 security dependency and blast-radius map](/blog/pq-payments/pfsh03-dependency-map.svg)
*Figure 4. PFSH03 dependency and blast-radius map: PFSH03 retires Appendix A.4, moving Spend Authorization onto FIPS-204 ML-DSA-65 plus the still-unaudited Theorem 2A extraction layer shared with Value Conservation.*

Throughout our security model, \(Q\) denotes an adversary’s total quantum queries to the random-oracle hash functions. Full theorem statements, symbol definitions, exact-rational QROM bounds, a **Spec-to-Code & Lean 4 Traceability Matrix**, and 18 prioritized external-reviewer questions live in the [Companion Mathematical Appendix](/research/pfsh03-proofs/).

**Honest assessment of Theorem 2A as a single point of failure—and what we hardened around it:**  
In PFSH03, moving spend signatures outside Binius retires our earlier unreviewed Appendix A.4 conjecture, QROM zero-knowledge, and SHAKE256 `JointPRF`/`PRG` from spend authorization. However, **Theorem 3 (inflation resistance) and Theorem 4 (theft resistance) now share one unaudited QROM extraction proof (Theorem 2A / App. A.3) and the `pk_hash0/1` circuit wiring**: a flaw in either would compromise both. Ahead of external review, we tightened two concrete surfaces around Theorem 2A:
1. **`3 × SHA-512` → 1,536-bit QRO reduction (Lean 4):** In `CompressedOracle.lean` (`three_block_sha512_qro_reduction`, axioms: `[propext]` only), we proved that because each 8-byte ASCII domain tag has a fixed input byte length (`PFS-LEAF` `761 B`, `PFS-NODE` `110 B`, `PFS-STMT` `561 B` with constant `408 B` `encode_statement`, `PFS-C4  ` `121 B`)—making inputs prefix-free and ruling out Merkle–Damgård length extension—any \(Q\)-query adversary given independent quantum access to the 512-bit counter slices \(h(b \parallel x)\) (`b ∈ {0, 1, 2}`) is simulated with **at most \(Q\) queries (zero query blowup)** against the atomic 1,536-bit tuple oracle \(H(x) = (h(0\parallel x), h(1\parallel x), h(2\parallel x))\). Reviewers still must evaluate the SHA-512/SHA-384 shared-compression-function boundary (Reviewer Question #7).
2. **Z3 + Rust/Go differential `pk_hash0/1` circuit wiring verification:** We expanded `verify_circuit_equivalence.py` (`z3_pfsh03_56perm_pk_hash_wiring: unsat+rust_go_diff_verified`) to check all 56 Keccak permutations, verify Rust/Go `perm_input_spec` parity for `pk_hash0/1` and `r_pk0/1` in `p = 0, 3`, and run differential bit-flip tests on `pk_in0` and `pk_in1` confirming identical `pub_rhs` sensitivity in both Rust and Go.

Three failure modes define the external audit surface:
1. **Value conservation (Theorem 3 — inflation or double-spend risk):** Concrete risks include misapplying [BCIKS20](https://eprint.iacr.org/2020/654), an error in our unaudited single-oracle QROM extractor (**Theorem 2A / App. A.3**), a spec-to-binary mismatch, or a circuit bug. Above \(Q = 2^{81.28}\), 384-bit proof-tree collisions overtake spot-check error and set the \(Q = 2^{126.75}\) vacuous-bound ceiling.
2. **Spend & deposit authorization (Theorem 4 — theft or transaction hijacking):** Relies on **FIPS-204 ML-DSA-65 EUF-CMA**, unmodified-oracle **Theorem 2A** (unaudited, shared with Thm 3), 384-bit SHAKE256/SHA-384 collision resistance, and exact `pk_hash0/1` wiring—plus the `~80-bit` unpinned deposit-account caveat (`prepare_pq_account_debit_pinned` available for strict enforcement).
3. **Multi-transaction confidentiality (Theorem 5 — privacy loss):** Formalized as an adaptive \(q_c\)-transaction hybrid in Lean 4 (`pfsh03_theorem5_multitx_hybrid`). With fresh per-note indexed addresses, cross-note `JointPRF` drops out; remaining privacy assumptions are QROM zero-knowledge (Theorem 1B / App. B), ML-KEM-1024 `IND-CCA2` plus unreviewed `IK-CCA`/`IR-PRF`, HMAC-SHA-384, AES-256-GCM, and single-use SHAKE256 `Hide` plus dummy `PRG`.

### What Lean 4 Checks—and What It Does Not Check

We formalized the algebraic, operator-norm, wire-margin, and reduction plumbing across nine **Lean 4 (`v4.20.0`) + Mathlib** modules (`formal/lean/PFSH02/`, **`2,847` LOC**, zero `sorry`s, zero custom axioms—`[propext, Classical.choice, Quot.sound]` only). **Boundary of machine checking:** Lean checks parameter arithmetic, greedy peeling telescoping, rank-3 operator norm bounds, the 3-block `SHA-512` → 1,536-bit QRO simulation, supply induction, and reduction accounting from explicit hypotheses. **Proximity gaps ([BCIKS20](https://eprint.iacr.org/2020/654)), the full compressed-oracle QROM extraction bridge, the GHHM21/AHU19 ZK bridges, real-world primitive assumptions, and Rust/Go binary equivalence enter as explicit hypotheses or lie outside Lean.**

| Property & Failure Mode | Checked in Lean 4 (Model Plumbing & Bounds) | Outside Lean / Explicit Audit Hypotheses | Code Traceability & Automated Checks |
| --- | --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation*) | Exact-rational parameters, `pfsh03_wire_margins_exact`, greedy peeling (`k ≤ 86`), polynomial/ring-switch bounds, rank-3 operator norm (`≤ √(8p)`), `three_block_sha512_qro_reduction`, compressed-oracle telescoping, inductive supply conservation | [BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654); **unaudited** single-oracle extraction (App. A.1–A.3); SHAKE256 384-bit CR & zero-preimage; SHA-512/SHA-384 separation | **Not mechanically linked** to Rust/Go binaries; Z3 + 3-way Rust/Go/Python IR checks 66-bit adder, mux, dummy gating, and 56-perm Keccak DAG (`verify_circuit_equivalence.py`); manual external code audit required |
| **Spend Authorization** (Theorem 4, private spends — *theft & tx hijacking*) | `pfsh03_spend_auth_dichotomy` & `pfsh03_theorem4_zero_appA4`: accounting reduction to ML-DSA-65 EUF-CMA + unmodified-oracle Theorem 2A + 384-bit CR (retires App. A.4, ZK & `JointPRF`) | FIPS-204 ML-DSA-65 EUF-CMA + **unaudited** App. A.1–A.3 (shared SPOF with Thm 3) + 384-bit SHAKE256/SHA-384 CR + full `pk_hash0/1` wiring audit | Z3 + differential Rust/Go `pk_in0/1` bit-flip check (`unsat+rust_go_diff_verified`) + `39` adversarial controls (incl. 4 ML-DSA-65 spend-auth attacks); **not mechanically linked** to binaries |
| **Deposit Authorization** (Theorem 4, public deposits — *deposit forgery*) | `mode3_key_pinned_eliminates_160bit`: pinning the full ML-DSA-65 pubkey removes the 160-bit preimage term | ML-DSA-65 EUF-CMA + SHA-384 CR for pinned accounts; **unpinned brand-new accounts remain weak** (160-bit preimage) | `prepare_pq_account_debit` + strict `prepare_pq_account_debit_pinned` in `crates/execution/src/entrypoints.rs`; manual audit required |
| **Multi-Tx Confidentiality** (Theorem 5 — *privacy loss*) | `pfsh03_theorem5_multitx_hybrid`: adaptive `q_c`-tx hybrid accounting + unopened-leaf ZK bijection (`5,216` bits), capped-PoW TV (`< 2^-182`), GMP22 implicit-rejection sub-hop | **Unaudited** App. B (`GHHM21`/`AHU19` bridges); ML-KEM-1024 `IND-CCA2`/`IK-CCA`/`IR-PRF`, HMAC, AES-GCM, single-use `Hide` & dummy `PRG`; **fresh per-note addresses required** | Not mechanically linked to wallet/KEM code |

---

## 4. Benchmarks, Fail-Fast Rejection, Rehearsals & Test Results

All native PFSH03, WASM32, and Orchard measurements ran on 24 November 2026 on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone PFSH03 and Orchard verification tests ran `n = 50` trials per condition pinned to CPU 2 (`RAYON_NUM_THREADS=1`, `GOMAXPROCS=1`). Inside-validator PFSH03 runs used `n = 21` trials per condition across PFT and `pfUSDC`, warm and cold (`128 MiB` L3 eviction), against `1,024` history entries (`RAYON_NUM_THREADS=4` on `CPU 0–3` for parallel 4-proof blocks). The `wasm32-unknown-unknown +simd128` run executed the compiled `849,531 B` (`830 KB`) `.wasm` module in Node.js `v20.20.2` (V8, 1 thread, pinned CPU 2). These are single-host measurements, not universal hardware guarantees.

### 4.1 Full Verification, Fail-Fast Rejection & Proving Matrix (Internal Targets: `< 50 ms` 1-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Target Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Orchard 1-tx baseline** (`n = 50`, cached VK) | Halo 2 + RedPallas, 1 core CPU 2 | **44.26 ms** | 47.01 ms | 47.82 ms | Baseline |
| **Orchard 4-tx batch baseline** (`n = 50`, cached VK) | Standalone `BatchValidator`, 1c / **4c** | 87.36 / **34.54 ms** | 90.48 / 34.65 ms | 93.96 / **34.75 ms** | Baseline |
| **PFSH03 standalone Rust** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ`), 1 core | 22.09–22.21 ms | 22.27–22.55 ms | **25.12 ms** | Met (`< 50 ms`) |
| **PFSH03 standalone Go** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ` ASM), 1 core | 33.62–33.66 ms | 33.97–34.02 ms | **35.28 ms** | Met (`< 50 ms`) |
| **PFSH03 standalone Go portable** (`mint`/`hop1`/`hop2`, `n = 50`) | `-tags purego` (0 ASM), 1 core | 45.42–46.02 ms | 46.44–46.82 ms | **48.47 ms** | Met (`< 50 ms`) |
| **PFSH03 fail-fast invalid reject** (`n = 20`, 1 core) | Bad ML-DSA-65 sig / **Bad 20-bit PoW** / Valid-PoW bad Merkle | **0.22 ms** / **0.53 ms** / **15.33 ms** | — | Sibling abort **`0.0002 ms`** | Microbenchmarked (`Gate 1` DoS audit open) |
| **PFSH03 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core pinned | 24.54–25.13 ms | 24.77–37.92 ms | **38.01 ms** | Met (`< 50 ms`) |
| **PFSH03 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable (no `PCLMULQDQ`), 1 core | 36.90–37.83 ms | 37.67–45.46 ms | **45.52 ms** | Met (`< 50 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Accelerated, 4-core parallel** | **47.35–47.78 ms** | 47.56–65.93 ms | **88.36 ms** | Met (`< 200 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Portable, 4-core parallel** | **79.22–79.69 ms** | 79.41–80.07 ms | **107.76 ms** | Met (`< 200 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core sequential *(pre-fail-fast)* | 95.47–140.89 ms | 96.31–190.15 ms | 135.38 ms valid · **209.43 ms invalid** | **Missed on 1c invalid burst** (`4c` required + fail-fast added) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable, 1 core sequential | 146.57–147.90 ms | 147.88–184.70 ms | 185.36 ms valid · 195.28 ms invalid | Tight on 1c (`4c` required in Gate 2) |
| **Orchard proving-only** (`n = 50`, cached PK) | 16 thr / 1 core CPU 2 | 1.29 s / **5.13 s** | 1.36 s / 5.66 s | 1.42 s / 6.33 s | Baseline |
| **PFSH03 proving-only (subtree-streaming)** (`355–361 MiB` RSS) | 16 thr (`n = 3`) / 1 core (`CPU 2`) | **2.66 s** / **25.67 s** | 2.69 s / — | 2.69 s / 25.67 s | **`-37%` RSS** vs. `572 MiB` baseline (`24.62 s` 1c `n = 10`) |
| **PFSH03 WASM32+SIMD128** (`830 KB` `.wasm`, `378.9 MiB` linear mem) | Node.js `v20.20.2` V8, 1 thread `CPU 2` | **39.36 s** prove / **70.80 ms** verify | — | 232.72 ms verify max | First browser-engine measurement *(iOS/Android untested)* |

Before our fail-fast verifier reordering, a single-core cold invalid 4-proof burst hit `209.43 ms`. Checking external ML-DSA-65 signatures (`0.22 ms`), transcript replay, and the 20-bit Round-34 PoW (`0.53 ms`) before circuit MLE, 3D-Karatsuba, or Merkle paths—paired with 4-thread cooperative `AtomicBool` sibling cancellation (`0.0002 ms`)—raises the per-proof attacker cost to reach the `15.33 ms` Merkle stage to `~2^20` SHA-512 PoW evaluations. Because microbenchmarks alone do not establish network-level DoS resilience (P2P bandwidth saturation, mempool queues, and coordinated invalid-batch bursts), adversarial invalid-proof flooding and mempool admission backpressure are explicitly included in Gate 1’s external audit scope alongside Gate 2’s `≥ 4`-core hardware qualification.

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites (PFSH03)

| Suite | Result (24 Nov 2026) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,847` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib; includes `three_block_sha512_qro_reduction`) |
| **Full `postfiat-node --lib` suite** | **751 passed, 0 failed** (incl. `two_tier_pq_pause_keeps_exits_open_and_emergency_freeze_auto_expires`; `45` pre-existing `#[ignore]` opt-in external-bridge/legacy tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`)** | **Passed** in `32.06 s` (`worst_uncached_verify_l1_ms = 24.38 ms`, largest body `155,159 B`, 4-proof block `621,112 B ≤ 640,000 B`, exit-safe pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + **39** named attacks incl. 4 ML-DSA-65 spend-auth attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + Go `delivery-helper` cross-check + `check_math.py` + expanded Z3 5.4.1 `pk_hash0/1` differential audit) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`10/10` accel, `10/10` portable incl. fail-fast DoS test), `postfiat-privacy-binius-wallet` (`8/8` + Go `cmd/delivery`), `postfiat-storage` PQ archive (`2/2` incl. `prune_pq_bodies`), Python CLI (`9/9`, 8 finalized payments across epoch rollover, 92 RPC secret-leakage checks) |
| **Historical live-devnet replays (`R64` + 1,754-block)** | 1,734-block `R64` pre-activation archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Note:* Rust, Go, Python, Z3, and Lean artifacts share one author team, so cross-language agreement checks internal consistency rather than independent external review.

---

## 5. Build Provenance, Evidence Artifacts & Activation Gates

**Build provenance:** [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2), branch `feat/pq-payments-production-candidate`, commit `be1f778779450db1bf3a61f281da14d423a295c3` (`be1f77877`, cleanly mergeable onto `public/main`).

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs, Traceability Matrix & Reviewer Questions** | PFSH03 symbol glossary, 9-module Lean 4 map (`2,847` LOC), `3 × SHA-512` QRO reduction, Theorem 4 & 5, Spec-to-Code Traceability Matrix & 18 reviewer questions | [`/research/pfsh03-proofs/`](/research/pfsh03-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,847` LOC), `lakefile.toml`, `README.md` | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/be1f778779450db1bf3a61f281da14d423a295c3/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | PFSH03 provenance, Lean 4 summary, Orchard, native/WASM32, fail-fast rejection & validator tables | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Rehearsal & Archive Replay Record** | Six-validator `M8` activation/pause/restart log plus separate `R64` 1,734-block pre-activation archive replay | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` (`z3_pfsh03_56perm_pk_hash_wiring`) & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for Lean 4, `~3 min` (~3.7 GiB RSS) for `verify.sh`, `~5 min` for the `n = 50` 1-core Orchard run, `~6 min` for `postfiat-node --lib`, and `~1 min` for the six-validator rehearsal.

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout be1f778779450db1bf3a61f281da14d423a295c3   # branch feat/pq-payments-production-candidate (PFSH03)

# 1. Build and kernel-verify all 9 Lean 4 proof modules (2,847 LOC, 0 sorrys, 0 custom axioms)
(cd formal/lean && lake exe cache get && lake build PFSH02)

# 2. Verify 36 fixture/script checksums & run the 7-stage standalone suite (incl. Z3 pk_hash0/1 audit)
(cd tools/pft-binius-shielded-pq && sha256sum -c SHA256SUMS && ./verify.sh)

# 3. Run fail-fast DoS & pruned-storage crate tests (accel & portable)
cargo test --release --locked -p postfiat-privacy-binius -- --nocapture
cargo test --release --locked -p postfiat-privacy-binius --features portable
cargo test --release --locked -p postfiat-storage --lib pq_archive

# 4. Run the postfiat-node library suite (751 tests, incl. two-tier pause & 7-day exit freeze) and 6-validator M8 rehearsal
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation

No activation date is set; PFSH03 stays disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic, DoS & implementation audit:** External cryptographers and systems auditors must publish a signed audit covering Theorem 3 (value conservation), Theorem 4 (external per-note ML-DSA-65 spend authorization + unmodified-oracle Theorem 2A + `3 × SHA-512`/SHA-384 boundary + `pk_hash0/1` circuit wiring), Theorem 5 (multi-transaction adaptive confidentiality and remaining privacy assumptions `IK-CCA`, `IR-PRF`, `Hide`, dummy `PRG`), **adversarial invalid-proof DoS flooding and mempool admission backpressure**, Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement and two-tier governance code—with every high or critical finding resolved and re-verified on the release commit.
2. **Production-genesis cut, measured hardware qualification, and scale/mobile validation:**
   - Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series;
   - run reproducible qualification benchmarks on representative validator hardware (x86-64 and ARM64) verifying `< 200 ms` max latency on attacker-crafted 4-proof invalid batches with `≥ 4` verification cores;
   - implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and
   - extend our `39.36 s` V8 WASM32 baseline with real iOS/Android mobile WebView, ARM64 `PMULL` device, and multi-threaded `SharedArrayBuffer` WASM proving benchmarks.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with wallet-enforced automatic key pinning (`prepare_pq_account_debit_pinned`) for brand-new L1 deposit accounts, fresh per-note receive-address defaults, Orchard exit/re-deposit tooling, and explicit user-facing privacy guidance on migration linkage.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `be1f77877`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/be1f778779450db1bf3a61f281da14d423a295c3/formal/lean), the [Companion Mathematical Appendix & Traceability Matrix](/research/pfsh03-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
