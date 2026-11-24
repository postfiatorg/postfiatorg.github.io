---
title: "PFSH03: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering report, same-host Orchard comparison, Lean 4 formalization, and security-status assessment for Peel-Binius-Shielded (PFSH03)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack."
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
> Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security. Both **value conservation** and **spend authorization** still depend on an unreviewed single-oracle quantum random-oracle (QROM) extraction argument and its circuit wiring, **multi-transaction confidentiality** relies on unreviewed privacy assumptions (and degrades if users reuse static receive addresses), **validators can freeze all shielded exits indefinitely via governance**, and the Lean 4 models are not mechanically linked to the compiled Rust or Go binaries. Independent external review may still require protocol changes.

<div class="glance">
  <div><b>Off · Unaudited</b><span>Disabled on mainnet; governance can also freeze all exits</span></div>
  <div><b>~16.4× Larger Wire</b><span>149.6 KB full payment vs. 9.1 KB binary Orchard (160 KB cap)</span></div>
  <div><b>~4.8× Slower Prove</b><span>24.6 s vs. 5.13 s cached-key Orchard (1 core)</span></div>
  <div><b>Main Blocker: Audit</b><span>Unaudited QROM extraction, circuit wiring &amp; binaries</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted notes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH03**) is our experimental replacement built without elliptic curves. We chose a binary-field Binius proof system over prime-field STARKs or lattice SNARKs because SHAKE256’s bitwise Keccak gates express natively over \(\mathbb{F}_2\) without prime-field bit decomposition, letting every building block come from NIST standards (**SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024**, and **ML-DSA-65**). Standardized primitives do not make a novel proof system or its composition secure.

### Current Project Status

- **Established on this host (internal, single-team):** End-to-end Rust/Go/L1 PFSH03 settlement, 750/750 `postfiat-node` library tests, a six-validator activation/pause/restart rehearsal (`22.19 ms` worst uncached L1 verify; `621,112 B` 4-proof block under the `640,000 B` cap), 9/9 Python wallet CLI tests across epoch rollover, same-host Orchard benchmarks, and nine Lean 4 model modules (`2,837` LOC, 0 `sorry`s, 0 custom axioms).
- **Conditional (model-level only):** Both **value conservation** and **spend authorization** now reduce in the formal model to the same unmodified-oracle extraction argument (**Theorem 2A**) plus standard **FIPS-204 ML-DSA-65** and 384-bit collision resistance—conditional on published Reed–Solomon proximity-gap results ([BCIKS20](https://eprint.iacr.org/2020/654)), external verification of our QROM extraction proof, and model-to-code fidelity. **Multi-transaction adaptive confidentiality** is formalized in Lean 4 for fresh per-note addresses, conditional on QROM zero-knowledge and remaining privacy assumptions.
- **Unresolved (blocking mainnet):** Independent external audit of the proof system, single-oracle QROM extraction (Theorem 2A), `pk_hash0/1` circuit wiring, remaining privacy assumptions (`IK-CCA`, `IR-PRF`, `Hide`, dummy `PRG`), Lean-to-Rust/Go implementation linkage, 16-million-note restart checkpointing, and browser/mobile client proving.

*Navigation:* **Users & operators** → Section 1 (payment flow, governance exit-freeze power, address-reuse and privacy limits) and comparison below. **Cryptographers** → Section 3 (how PFSH03 narrows the spend-auth trust surface, remaining failure modes, Lean 4 audit matrix) and the [Companion Mathematical Appendix](/research/pfsh03-proofs/). **Validators & engineers** → Section 4 (benchmark and test tables) and Section 5 (provenance, reproduction, and activation gates).

### Same-Host Baseline: Live Orchard vs. PFSH03 (AMD EPYC)

We benchmarked Post Fiat’s live 2-action Orchard Halo-2 implementation (`orchard 0.14.0`, via `orchard_proving_and_batch_budget`) against **PFSH03** on the same host and pinned cores. Sample sizes are stated per row; rows marked **†** compare standalone Orchard cryptographic verification against inside-validator PFSH03 runs that include ML-DSA-65 spend-auth, pool, anchor, and nullifier checks:

| Metric (2-Output Private Transfer) | Live Orchard (`orchard 0.14.0`) | PFSH03 Prototype | Comparison |
| --- | --- | --- | --- |
| **Proof bytes only** | `7,264 B` | `135,340 B` measured (`134,813 B` expected) | **`~18.6×` larger** |
| **Full binary wire** | `9,145 B` canonical fields *(9,297 B w/ optional fields)* | `149,582 B` full L1 private pay *(incl. 10.5 KB ML-DSA-65)* | **`~16.4×` larger** |
| **1-tx verify, standalone 1 core (`CPU 2`, `n = 50`)** | `44.26 ms` med *(cached VK; Halo 2 + RedPallas spend-auth)* | `22.1–22.2 ms` Rust accel · `33.6–33.7 ms` Go ASM · `45.4–46.0 ms` pure Go *(incl. 2× ML-DSA-65 spend-auth + Binius; in-validator `24.5–25.1 ms`)* | `~2.0×` faster (accel) to parity (pure Go) |
| **4-tx verify, 1 core †** | `87.36 ms` med *(`n = 50`, standalone `BatchValidator`)* | `95.5–140.9 ms` accel · `146.6–147.9 ms` portable *(`n = 21`, validator)* | Orchard batch faster *(different scope †)* |
| **4-tx verify, 4 cores †** | `34.54 ms` med *(`n = 50`, standalone `BatchValidator`)* | `47.4–47.8 ms` accel · `79.2–79.7 ms` portable *(`n = 21`, validator)* | Orchard batch faster *(different scope †)* |
| **Client proving-only, 1 core (`CPU 2`)** | `5.13 s` med *(`n = 50`, cached key; `4.04 s` setup)* | `24.62 s` med *(`n = 10`, ~572 MiB RAM; no setup)* | **`~4.8×` slower** |
| **Client proving-only, 16 threads** | `1.29 s` med *(`n = 50`, cached key)* | `2.71 s` med *(`n = 10`, ~572 MiB RAM)* | **`~2.1×` slower** |
| **Raw wire at `1 tx/s` / `4.0–7.3 tx/s`** | `~0.74` / `~2.9–5.4 GiB/day` *(rate-matched; no 4-tx cap)* | `~12.0` / `~48–88 GiB/day` *(`≤ 4` tx/block at `0.55–1.0 s` rehearsal blocks)* | **`~16.4×` bandwidth & storage** |
| **Assurance status** | Audited upstream (`orchard`); live in Zcash | Unaudited single-team prototype; disabled on mainnet | Audit required |

In short: single-transaction verification is competitive with Orchard (and faster on hardware-accelerated paths), whereas multi-transaction batch verification, proving time, transaction size, and cryptographic maturity all favor Orchard today. Full p95/max, warm/cold-cache, and invalid-batch measurements appear in Section 4.1.

---

## 1. How Payments Work & User / Governance Risks

**Plain-language summary for users:** Today PFSH03 is off on mainnet and should not hold live funds. When active in a future audited release, a user will wait ~25 seconds on a single CPU core (or ~2.7 s across 16 threads) to send a private payment, should generate a fresh receive address for each incoming payment so later spends stay unlinkable, should send one small signed transaction from a brand-new public L1 account before making large deposits, and should know that a validator supermajority can pause all shielded transfers and exits.

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

- **Validator supermajority can freeze exits indefinitely:** Scheduling activation, changing fees, pausing the pool, and disbursing `collected_private_fees` all require signed validator governance amendments meeting the **BFT supermajority** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in rehearsal). Setting `paused: true` halts **all** shielded actions—deposits, transfers, **and exits**—until governance unpauses. This provides an incident circuit breaker at the cost of an explicit censorship and liquidity-freeze power over users’ shielded funds.
- **Static-address reuse links spends (safe against theft, weakens unlinkability):** Because PFSH03 reveals `pk_in` at *spend* time (never at receive time), using fresh indexed receive addresses keeps spends unlinkable across transactions. Reusing one static receive address across multiple notes does not weaken theft protection (ML-DSA-65 is many-time EUF-CMA), but spending two notes from that same static address publishes the same `pk_dsa` on-chain and publicly links those spends. Wallets must default to fresh per-note addresses and rotate change keys automatically.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves exact supply conservation (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`), but disbursement relies on validator governance rather than an autonomous protocol rule.
- **Epoch rollovers & anonymity-set dilution:** Native PFT and each governed issued asset maintain separate depth-24 trees holding \(2^{24} = 16,777,216\) leaves (`8,388,608` two-output transactions). An epoch lasts `~97.1 days` at `1 tx/s`, or **`~13.4–24.3 days`** at the `4.0–7.3 tx/s` ceiling. **Frozen trees remain spendable indefinitely via historical roots**, but every new spend places its outputs into the *current* active epoch tree, where early outputs initially share a smaller active-epoch anonymity set than mature historical trees.
- **Observable metadata & Orchard migration linkage:** Observers cannot see private transfer amounts, recipient keys, or internal-spend L1 accounts, but they still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and network IP/timing metadata. Moving funds from Orchard to PFSH03 requires a public exit followed by a public deposit, linking amounts and timing (splitting amounts and adding delays are heuristics, not guaranteed unlinkability).
- **Key hygiene & static-key compromise:**
  - *Unpinned brand-new L1 deposit accounts:* A brand-new public L1 account that has never signed a transaction is identified only by a 160-bit address hash (`~2^-32` quantum preimage risk at `2^64` queries, vacuous at `2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating 160-bit exposure. **Operational step:** fund a fresh account with a minimal fee balance and send one low-value signed self-transfer before moving large deposits; automatic wallet enforcement is part of Gate 3.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes all past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH03 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh03-wire-and-iop.svg)
*Figure 2. PFSH03 wire-size breakdown against the 160,000-byte archival cap (top), highlighting the 10,522-byte external ML-DSA-65 spend-authorization block, and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH03 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** Every note owner address binds the hash of a per-note ML-DSA-65 public key to a secret blinding/nullifier key \(r_{\mathrm{pk}}\):
  $$A = \mathrm{SHAKE256}\bigl(\texttt{0x00} \parallel \mathrm{pk\_hash}_{48} \parallel r_{\mathrm{pk},48}\bigr), \qquad \mathrm{SN} = \mathrm{SHAKE256}\bigl(\texttt{0x02} \parallel r_{\mathrm{pk},48} \parallel \mathrm{Coin}_{48}\bigr)$$
  Because \(1 + 48 + 48 = 97 \le 135\) bytes fits inside one Keccak-\(f[1600]\) permutation (`p = 0, 3`), all 56 permutations, Merkle muxes, dummy-input gating, and 66-bit conservation adders remain at `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step. Public `pk_hash0` and `pk_hash1` enter as constant statement bits.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four engineering choices drive verifier and prover performance:
- **Exact 3D-Karatsuba ring-switch verifier:** Cuts extension-field multiplications by `11×` (derivation in the appendix).
- **Single-step binary-field kernels:** 54-multiply Karatsuba routines with inline `mulC32` reduction and register-based linear maps across Rust (hardware-accelerated + portable) and Go (ASM + `purego`).
- **Cheap-checks-first parallel validator:** Runs pool, anchor, nullifier, and external ML-DSA-65 spend-auth checks before Binius verification, then verifies up to 4 proofs concurrently across scoped OS threads.
- **Streaming prover:** Holds peak client memory near `572 MiB` (`585,352 KiB` peak in rehearsal).

### Wire Size & Archival Cap Accounting (`160,000 B` Cap)

External per-note ML-DSA-65 spend authorization adds `10,522 B` (`2 × 1,952 B` pk + `2 × 3,309 B` sig) to every transaction, lifting the archival ceiling from `149,130 B` (in our earlier PFSH02 draft) to `160,000 B` (`640,000 B` per 4-payment block). Measured proofs vary slightly because Merkle sibling-pruning collisions differ per transaction:

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Proof Basis | Measured / Expected | Margin vs. Cap | Worst-Case Ceiling | Ceiling Margin |
| --- | --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`14,170 B` header+auth + proof) | Expected (`134,813 B`) | 148,983 B *(148,814 B rollover)* | 11,017 B | 150,998 B | **9,002 B** |
| **L1 `pfUSDC` / `PFT` private pay** (`72 B` prefix + `14,170 B` + proof) | Measured (`135,340 B`) | **149,582 B** | **10,418 B** | 151,070 B *(150,998 inner)* | **8,930 B** |
| **L1 `pfUSDC` private exit** (`72 B` prefix + `14,170 B` + proof) | Measured (`134,668 B`) | **148,910 B** *(148,958 PFT)* | 11,090 B | 151,070 B *(150,998 inner)* | **8,930 B** |
| **Standalone signed deposit wire** (adds `5,261 B` deposit ML-DSA-65) | Expected (`134,813 B`) | 154,244 B | 5,756 B | 156,259 B | **3,741 B** |
| **L1 archived deposit — `redb` store** *(verified `153,143 B` body + framing)* | Measured (`153,852 B` stored) | 153,852 B *(M8 max `155,902 B`)* | 4,098–6,148 B | **157,068 B** | **2,932 B** |
| **L1 archived deposit — `JSONL` store** *(adds JSONL envelope + digest)* | Measured (`153,886 B` stored) | 153,886 B | 6,114 B | **157,102 B** | **2,898 B** |

Worst-case archived signed deposits leave `2,898–2,932 B` of headroom under `160,000 B`. Raising the archival cap is an operational change; lowering Round-34 column openings (saving `~1.5 KB` per opening at a cost of `~5.4` bits of pure-IOP soundness) would be a **cryptographic parameter redesign requiring renewed soundness analysis and external re-audit**.

---

## 3. Security Failure Modes, Lean 4 Core & Audit Scope

![PFSH03 conditional QROM security curves](/blog/pq-payments/pfsh03-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum oracle query budget Q, showing unmodified-oracle Theorem 2A (shared by Value Conservation and Spend Authorization), the 384-bit tree-collision crossover at Q = 2^81.28, and the 160-bit unpinned deposit-account bound.*

![PFSH03 security dependency and blast-radius map](/blog/pq-payments/pfsh03-dependency-map.svg)
*Figure 4. PFSH03 dependency and blast-radius map: PFSH03 retires Appendix A.4, moving Spend Authorization onto FIPS-204 ML-DSA-65 plus the still-unaudited Theorem 2A extraction layer shared with Value Conservation.*

Throughout our security model, \(Q\) denotes an adversary’s total quantum queries to the random-oracle hash functions. Full theorem statements, symbol definitions, exact-rational QROM bounds, Lean 4 module tables, and 17 prioritized external-reviewer questions live in the [Companion Mathematical Appendix](/research/pfsh03-proofs/).

**How PFSH03 changes the spend-authorization trust surface—and what remains open:** In our earlier PFSH02 draft, spend authorization proved secret knowledge only inside Binius, forcing the reduction to simulate honest proofs under an unreviewed multi-proof simulation-extractability conjecture (Appendix A.4 / Theorem 2B) plus SHAKE256 `JointPRF`/`PRG`. In PFSH03, moving spend signatures outside the circuit lets the reduction hold \(r_{\mathrm{pk}}\), run the real unmodified prover, and answer honest spends via standard ML-DSA-65 signing queries. That narrows the dependency from an unreviewed conjecture (App. A.4) to **FIPS-204 ML-DSA-65 EUF-CMA** plus our **still-unaudited single-oracle QROM extraction argument (Theorem 2A / App. A.3)** and 384-bit collision resistance. Because Theorem 3 and Theorem 4 now share Theorem 2A, **a single error in Theorem 2A or the circuit’s `pk_hash0/1` wiring would break both inflation resistance and theft protection**.

Three failure modes define the external audit surface:
1. **Value conservation (Theorem 3 — inflation or double-spend risk):** Concrete risks include misapplying published Reed–Solomon proximity-gap results ([BCIKS20](https://eprint.iacr.org/2020/654)), an error in our single-oracle QROM extractor (Theorem 2A / App. A.3), a mismatch between the specification and the Rust/Go verifiers, or a SHAKE256/circuit constraint bug. Inside the QROM model, 384-bit proof-tree collisions overtake spot-check error above \(Q = 2^{81.28}\) queries.
2. **Spend & deposit authorization (Theorem 4 — theft or transaction hijacking):** Relies on **FIPS-204 ML-DSA-65 EUF-CMA**, unmodified-oracle extraction (**Theorem 2A / App. A.3**, unaudited), 384-bit SHAKE256/SHA-384 collision resistance, and exact circuit wiring of public `pk_hash0/1`—plus the 160-bit preimage caveat for unpinned brand-new L1 deposit accounts. Appendix A.4, QROM zero-knowledge, and `JointPRF`/`PRG` are no longer part of the Theorem 4 reduction.
3. **Multi-transaction confidentiality (Theorem 5 — privacy loss):** Formalized as an adaptive \(q_c\)-transaction hybrid in Lean 4 (`pfsh03_theorem5_multitx_hybrid`). With fresh per-note indexed addresses, cross-note SHAKE256 `JointPRF` drops out; remaining privacy assumptions are QROM zero-knowledge (Theorem 1B / App. B), ML-KEM-1024 `IND-CCA2` plus unreviewed `IK-CCA`/`IR-PRF`, HMAC-SHA-384, AES-256-GCM, and single-use SHAKE256 `Hide` plus dummy `PRG` (alongside the static-address reuse and metadata caveats in Section 1).

### Lean 4 Formalization Scope & External Audit Matrix

We formalized the core mathematical arguments across nine **Lean 4 (`v4.20.0`) + Mathlib** modules (keeping the historical package path `formal/lean/PFSH02/`, `2,837` LOC), compiling with zero `sorry`s and zero custom axioms (`#print axioms` reports only Lean’s standard `[propext, Classical.choice, Quot.sound]`). **Zero `sorry`s checks internal implication from explicit hypotheses—not that real-world assumptions hold or that the Rust/Go binaries match the model.**

| Property & Failure Mode | Checked in Lean 4 (Model Level) | Assumptions & Unformalized Audit Targets | Implementation Linkage |
| --- | --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation*) | Exact-rational parameters, `pfsh03_wire_margins_exact`, greedy peeling (`k ≤ 86`), polynomial/ring-switch bounds, rank-3 operator norm (`≤ √(8p)`) & compressed-oracle telescoping, inductive supply conservation | Published literature bridges ([BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654)); **unaudited** single-oracle extraction (App. A.1–A.3); SHAKE256 384-bit collision & zero-preimage resistance | **Not mechanically linked** to Rust/Go verifiers or full 34-round circuit wiring (Z3 checks 66-bit adder, mux & dummy gating only) |
| **Spend Authorization** (Theorem 4, private spends — *theft & tx hijacking*) | `pfsh03_spend_auth_dichotomy` & `pfsh03_theorem4_zero_appA4`: reduction to ML-DSA-65 EUF-CMA + unmodified-oracle Theorem 2A + 384-bit CR (retires App. A.4, ZK & `JointPRF`) | FIPS-204 ML-DSA-65 EUF-CMA + **unaudited** App. A.1–A.3 (shared with Thm 3) + 384-bit SHAKE256/SHA-384 CR + public `pk_hash0/1` circuit wiring audit | Tested in Rust & Go (`39` adversarial controls incl. 4 ML-DSA-65 spend-auth attacks); **not mechanically linked** to binaries |
| **Deposit Authorization** (Theorem 4, public deposits — *deposit forgery*) | `mode3_key_pinned_eliminates_160bit`: pinning the full ML-DSA-65 pubkey removes the 160-bit preimage term | ML-DSA-65 EUF-CMA + SHA-384 CR for pinned accounts; **unpinned brand-new accounts remain weak** (160-bit preimage) | Tested in `prepare_pq_account_debit`; manual external code audit required |
| **Multi-Tx Confidentiality** (Theorem 5 — *privacy loss*) | `pfsh03_theorem5_multitx_hybrid`: adaptive `q_c`-tx hybrid + unopened-leaf ZK bijection (`5,216` bits), capped-PoW TV (`< 2^-182`), GMP22 implicit-rejection sub-hop | **Unaudited** App. B (`GHHM21`/`AHU19` bridges); ML-KEM-1024 `IND-CCA2`/`IK-CCA`/`IR-PRF`, HMAC, AES-GCM, single-use `Hide` & dummy `PRG`; **fresh per-note addresses required for spend unlinkability** | Not mechanically linked to wallet/KEM code |

---

## 4. Benchmarks, Rehearsals & Test Results

All PFSH03 and Orchard measurements ran on 24 November 2026 on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone PFSH03 and Orchard verification tests ran `n = 50` trials per condition pinned to CPU 2 (`RAYON_NUM_THREADS=1`, `GOMAXPROCS=1`). Standalone PFSH03 proving ran `n = 10` trials on CPU 2 and 16 threads (versus `n = 50` for Orchard). Inside-validator PFSH03 tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` on `CPU 0–3` for parallel 4-proof blocks). These are single-host measurements, not universal hardware guarantees.

### 4.1 Full Verification & Proving Matrix (Internal Targets: `< 50 ms` 1-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Target Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Orchard 1-tx baseline** (`n = 50`, cached VK) | Halo 2 + RedPallas, 1 core CPU 2 | **44.26 ms** | 47.01 ms | 47.82 ms | Baseline |
| **Orchard 4-tx batch baseline** (`n = 50`, cached VK) | Standalone `BatchValidator`, 1c / **4c** | 87.36 / **34.54 ms** | 90.48 / 34.65 ms | 93.96 / **34.75 ms** | Baseline |
| **PFSH03 standalone Rust** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ`), 1 core | 22.09–22.21 ms | 22.27–22.55 ms | **25.12 ms** | Met (`< 50 ms`) |
| **PFSH03 standalone Go** (`mint`/`hop1`/`hop2`, `n = 50`) | Accelerated (`PCLMULQDQ` ASM), 1 core | 33.62–33.66 ms | 33.97–34.02 ms | **35.28 ms** | Met (`< 50 ms`) |
| **PFSH03 standalone Go portable** (`mint`/`hop1`/`hop2`, `n = 50`) | `-tags purego` (0 ASM), 1 core | 45.42–46.02 ms | 46.44–46.82 ms | **48.47 ms** | Met (`< 50 ms`) |
| **PFSH03 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core pinned | 24.54–25.13 ms | 24.77–37.92 ms | **38.01 ms** | Met (`< 50 ms`) |
| **PFSH03 validator 1-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable (no `PCLMULQDQ`), 1 core | 36.90–37.83 ms | 37.67–45.46 ms | **45.52 ms** | Met (`< 50 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Accelerated, 4-core parallel** | **47.35–47.78 ms** | 47.56–65.93 ms | **88.36 ms** | Met (`< 200 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | **Portable, 4-core parallel** | **79.22–79.69 ms** | 79.41–80.07 ms | **107.76 ms** | Met (`< 200 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Accelerated, 1 core sequential | 95.47–140.89 ms | 96.31–190.15 ms | 135.38 ms valid · **209.43 ms invalid** | **Missed on 1c invalid burst** (`max = 209.4 ms`) |
| **PFSH03 validator 4-tx** (PFT & pfUSDC, warm/cold, `n = 21`) | Portable, 1 core sequential | 146.57–147.90 ms | 147.88–184.70 ms | 185.36 ms valid · 195.28 ms invalid | Tight on 1c (`4c` required in Gate 2) |
| **Orchard proving-only** (`n = 50`, cached PK) | 16 thr / 1 core CPU 2 | 1.29 s / **5.13 s** | 1.36 s / 5.66 s | 1.42 s / 6.33 s | Baseline |
| **PFSH03 proving-only** (`n = 10`, ~572 MiB RSS) | 16 thr / 1 core CPU 2 | **2.71 s** / **24.62 s** | 2.81 s / 26.81 s | 2.81 s / 26.81 s | Measured (browser/mobile untested) |

Every 4-core parallel validator run (accelerated `88.36 ms` max; portable `107.76 ms` max) stayed under `200 ms`, whereas single-core sequential validation reached `209.43 ms` on a cold invalid burst—so Gate 2 requires `≥ 4` verification cores qualified on representative validator hardware.

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites (PFSH03)

| Suite | Result (24 Nov 2026) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,837` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib) |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`)** | **Passed** in `32.57 s` (`worst_uncached_verify_l1_ms = 22.194 ms`, largest body `155,159 B`, 4-proof block `621,112 B ≤ 640,000 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + **39** named attacks incl. 4 ML-DSA-65 spend-auth attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + Go `delivery-helper` ML-DSA-65/ML-KEM-1024 cross-check + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8` + Go `cmd/delivery`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`, 8 finalized payments across epoch rollover, 92 RPC secret-leakage checks) |
| **Historical live-devnet replays (`R64` + 1,754-block)** | 1,734-block `R64` pre-activation archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Note:* Rust, Go, Python, Z3, and Lean artifacts share one author team, so cross-language agreement checks internal consistency rather than independent external review.

---

## 5. Build Provenance, Evidence Artifacts & Activation Gates

**Build provenance:** [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2), branch `feat/pq-payments-production-candidate`, commit `51e7d96870b5e0e926d89b8d273b12eb3e750aa0` (`51e7d9687`, cleanly mergeable onto `public/main`).

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & Reviewer Questions** | PFSH03 symbol glossary, 9-module Lean 4 map (`2,837` LOC), Theorem 4 (external ML-DSA-65 + Thm 2A), Theorem 5 (`q_c`-tx hybrid) & 17 reviewer questions | [`/research/pfsh03-proofs/`](/research/pfsh03-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,837` LOC), `lakefile.toml`, `README.md` | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/51e7d96870b5e0e926d89b8d273b12eb3e750aa0/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | PFSH03 provenance, Lean 4 summary, Orchard & PFSH03 baselines, test counts & validator tables | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Rehearsal & Archive Replay Record** | Six-validator `M8` activation/pause/restart log plus separate `R64` 1,734-block pre-activation archive replay | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for Lean 4, `~3 min` (~3.7 GiB RSS) for `verify.sh`, `~5 min` for the `n = 50` 1-core Orchard run, `~6 min` for `postfiat-node --lib`, and `~1 min` for the six-validator rehearsal.

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout 51e7d96870b5e0e926d89b8d273b12eb3e750aa0   # branch feat/pq-payments-production-candidate (PFSH03)

# 1. Build and kernel-verify all 9 Lean 4 proof modules (2,837 LOC, 0 sorrys, 0 custom axioms)
(cd formal/lean && lake exe cache get && lake build PFSH02)

# 2. Verify 36 fixture/script checksums & run the 7-stage standalone suite
(cd tools/pft-binius-shielded-pq && sha256sum -c SHA256SUMS && ./verify.sh)

# 3. Run the same-host n = 50 Orchard proving-only & 4-bundle batch-verify baselines
RAYON_NUM_THREADS=1 PROVE_ITERS=50 VERIFY_ITERS=50 taskset -c 2 \
  cargo run --release --locked -p postfiat-privacy-orchard --example orchard_proving_and_batch_budget
RAYON_NUM_THREADS=4 PROVE_ITERS=4 VERIFY_ITERS=50 taskset -c 0-3 \
  cargo run --release --locked -p postfiat-privacy-orchard --example orchard_proving_and_batch_budget

# 4. Run the postfiat-node library suite (750 tests) and 6-validator M8 rehearsal
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation

No activation date is set; PFSH03 stays disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic & implementation audit:** External cryptographers must publish a signed audit covering Theorem 3 (value conservation), Theorem 4 (external per-note ML-DSA-65 spend authorization + unmodified-oracle Theorem 2A + `pk_hash0/1` circuit wiring), Theorem 5 (multi-transaction adaptive confidentiality and remaining privacy assumptions `IK-CCA`, `IR-PRF`, `Hide`, dummy `PRG`), Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement code—with every high or critical finding resolved and re-verified on the release commit.
2. **Production-genesis cut, measured hardware qualification, and scale validation:**
   - Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series;
   - run reproducible qualification benchmarks on representative validator hardware verifying `< 200 ms` max latency on attacker-crafted 4-proof invalid batches with `≥ 4` verification cores;
   - implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and
   - publish measured browser-WASM/mobile proving and sustained multi-node load/storage results.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with wallet-enforced automatic key pinning for brand-new L1 deposit accounts, fresh per-note receive-address defaults, Orchard exit/re-deposit tooling, and explicit user-facing privacy guidance on migration linkage.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `51e7d9687`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/51e7d96870b5e0e926d89b8d273b12eb3e750aa0/formal/lean), the [Companion Mathematical Appendix](/research/pfsh03-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
