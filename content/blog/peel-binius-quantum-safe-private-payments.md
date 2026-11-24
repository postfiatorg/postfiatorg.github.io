---
title: "PFSH02: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering, benchmark, Lean 4 formalization, and security-status report for Peel-Binius-Shielded (PFSH02)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack with SHAKE256, SHA-512, AES-256-GCM, ML-KEM-1024, and ML-DSA-65."
aliases:
  - /peel-binius-quantum-safe-private-payments/
  - /posts/peel-binius-quantum-safe-private-payments/
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

> **Research prototype — disabled on mainnet and not suitable for live funds.**  
> Built on branch `feat/pq-payments-production-candidate` (commit `26e5a10a5`, cleanly mergeable onto `public/main` `994589467`). Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security: **spend authorization (Theorem 4) still requires external review of the full QROM simulation-extractability bridge (Appendix A.4 / real-to-wrapper view equivalence) and non-standard SHAKE256 assumptions**, confidentiality (Theorem 5) covers only a single-transaction model, and Lean’s abstractions have not yet been formally linked to the Rust/Go binaries. External review may require protocol redesign.

<div class="glance">
  <div><b>2,729 LOC Lean 4</b><span>9 modules, 0 `sorry`s, 0 custom axioms; model-to-code &amp; external audit open</span></div>
  <div><b>137,860 B pay</b><span>Measured private transfer (146,580 B max archived deposit; 149,130 B cap)</span></div>
  <div><b>45.2 ms · 108.4 ms</b><span>Observed maxima: single-tx verify (all backends) &amp; 4-tx parallel block</span></div>
  <div><b>750 pass · 7 / 7</b><span>`postfiat-node` (0 fail; 45 non-PQ ignored) &amp; standalone Rust/Go/Python suite</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted note envelopes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve zero-knowledge proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH02**) is our experimental replacement built without elliptic curves. It assembles a binary-field interactive oracle proof, hash-based note trees, lattice key encapsulation, and lattice deposit signatures from NIST-standardized primitives: **SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024** (FIPS 203), and **ML-DSA-65** (FIPS 204). Standardized building blocks do not establish the security of a novel proof system or its composition; this report puts the implementation, single-host measurements, **2,729-line Lean 4 + Mathlib proof library**, operational tradeoffs, and remaining audit obligations directly in front of external cryptographers, node operators, and governance participants.

*Reading guide:* **Users and operators** → comparison table below and Section 1 (payment flow, governance freeze risk, privacy boundaries). **Cryptographers** → Section 3 (failure modes, Lean 4 kernel-verified core vs. open audit boundaries) and the [Companion Mathematical Appendix](/research/pfsh02-proofs/). **Validators and engineers** → Section 4 (benchmarks and test suites) and Section 5 (local reproduction and activation gates).

### Illustrative Comparison: Legacy Orchard vs. PFSH02

Removing elliptic curves carries steep bandwidth, proving, and throughput costs. The Orchard column reflects illustrative order-of-magnitude reference figures from the [Zcash Protocol Specification (ZIP 224)](https://zips.z.cash/protocol/protocol.pdf) (not re-benchmarked on this host); the PFSH02 column reports single-host measurements on commit `26e5a10a5`:

| Dimension | Legacy Orchard (Illustrative Reference) | PFSH02 Prototype (Measured on `26e5a10a5`) |
| --- | --- | --- |
| **Core assumptions** | Discrete log on Pasta curves (Halo 2) | SHAKE256, `3×SHA-512`, ML-KEM-1024, ML-DSA-65 + unreviewed QROM bridges & non-standard hash/KEM assumptions |
| **Elliptic-curve quantum exposure** | Retroactive note decryption + future proof forgery | No elliptic curves; post-quantum security **unverified** pending external audit |
| **Private transfer size** | ~2–5 KB | **137,860 B** measured (`140,476 B` worst-case non-mint ceiling) |
| **Single-core verification** | Low single-digit ms | **20.4–43.1 ms** per-condition medians; **45.23 ms** largest observed max across all backends |
| **Client proving (1 core)** | ~1–3 s | **24.61–24.71 s** median (`27.68 s` max), `~550 MiB` RSS |
| **Client proving (16 threads)** | — | **2.64 s** (EPYC server; browser/mobile untested) |
| **Block & epoch limits** | Higher density | `≤ 4` PQ txs/block (theoretical ceiling `4–8 tx/s` at `0.5–1 s` blocks); `8,388,608` txs/epoch (`~97.1 days` at `1 tx/s`, **`12–24 days`** at ceiling) |
| **Assurance status** | Externally audited; deployed in Zcash | **Unaudited**, single-team code; core math kernel-checked in Lean 4; disabled on mainnet |

---

## 1. Payment Flow, Governance Risks & Privacy Boundaries

![PFSH02 architecture diagram](/blog/pq-payments/pfsh02-architecture.svg)
*Figure 1. End-to-end lifecycle across Deposit, Private Pay (issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH02 transaction consumes **two input slots** (real or dummy) and produces **two output notes** under one 66-bit unsigned integer conservation law over \(\mathbb{Z}\):

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each amount lies in \([0, 2^{64}-1]\), and acceptance rule **R5** enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can reach \(2^{66}\) or wrap around.

1. **Deposit (Shield, \(v_{\mathrm{mint}} > 0\)).** A public account signs an ML-DSA-65 deposit (`5,261 B` public key + signature), debiting its public balance and inserting two note commitments into the asset’s depth-24 SHAKE256 tree. The recipient’s shielded address and note blinding stay off-chain.
2. **Private Transfer (no public sender account).** Under the current L1 fee profile (`Profile 2`, which removes the public fee-payer signature required in earlier drafts), the sender proves spend authority for two notes under a valid tree root, publishes two one-time nullifiers, and posts two commitments plus two `1,670 B` **ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM** ciphertexts. Neither native **PFT** nor governed issued-asset (`pfUSDC`) transfers carry a public sender account or signature: PFT fees burn inside the proof, while issued-asset transfers pay the governance-scheduled inner fee (`1` atom = `0.000001 pfUSDC` in rehearsal) into an on-chain `collected_private_fees` pot.
3. **Non-Interactive Offline Receive.** Recipients publish a static stealth address off-chain; senders need zero interactive round trips at payment time. Wallets scan outputs locally (`4,722` outputs/s/core on our AMD EPYC test host; up to `8,971` outputs/s/core in earlier EPYC-Genoa measurements), accepting a note only when decryption reproduces the public SHAKE256 commitment.
4. **Partial or Full Exit (Unshield, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits `unshield_dest` on the public ledger after checking per-asset pool reserves and destination trustline rules, with no public fee-paying account required.

### User, Governance & Operational Risks

- **Validator supermajority can freeze exits indefinitely:** Scheduling, fee changes, emergency pauses, and `collected_private_fees` withdrawals all require signed validator governance amendments meeting the active validator registry’s **BFT supermajority threshold** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in rehearsal). Setting `paused: true` refuses **all** PQ actions—deposits, transfers, **and exits**—until governance unpauses, giving a validator supermajority indefinite freeze power over shielded liquidity.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed issued assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves Post Fiat’s supply-conservation accounting invariant (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`) without silent supply drift. Disbursement relies on validator governance rather than an autonomous protocol rule.
- **Frequent epoch rollovers at peak load:** Native **PFT** and each governed issued asset maintain separate depth-24 trees holding \(2^{24} = 16,777,216\) leaves (`8,388,608` two-output transactions). An epoch lasts `~97.1 days` at `1 tx/s`, but only **`12–24 days`** at the theoretical `4–8 tx/s` block-cap ceiling. Frozen trees remain spendable forever via historical roots, yet rolling into an empty epoch forces holders to migrate notes via fresh spends (incurring fees, proving cost, and timing linkage) and resets the new epoch’s anonymity set.
- **Observable metadata & migration linkage:** PFSH02 hides private transfer amounts, recipient keys, and internal-spend sender accounts on the wire. Observers still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and gateway/validator IP addresses and timing. Migrating from legacy Orchard requires a public Orchard exit followed by a PFSH02 deposit, which publicly links amounts and timing (splitting amounts and adding delays are uncertain heuristics, not reliable unlinkability).
- **Key hygiene & static-key compromise:**
  - *Unpinned deposit accounts:* Brand-new accounts that have never signed a transaction are identified only by a 160-bit address hash (`~2^-32` quantum forgery exposure at `Q = 2^64`, vacuous at `Q = 2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain (`mode3_key_pinned_eliminates_160bit` in Lean 4), eliminating 160-bit exposure. **Wallet rule:** send one signed transaction from any brand-new account before receiving large deposits.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes all past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH02 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)
*Figure 2. Wire-size breakdown against the 149,130-byte archival cap (top) and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH02 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** All four note and Merkle hashes run in one Keccak-\(f[1600]\) permutation (`48 B` digests). Fifty-six Keccak permutations plus Merkle conditional-swap muxes, dummy-input gating, and 66-bit conservation adders pack into `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four engineering optimizations bring single-transaction verification below `45.3 ms` max across both hardware-accelerated (`PCLMULQDQ`) and pure-portable Rust/Go builds: an exact 3D-Karatsuba ring-switch verifier (`11×` fewer field multiplications), 54-multiply Karatsuba field kernels with single-step inline `mulC32` reduction and register-based linear maps, cheap pool/nullifier checks before proof verification plus parallel 4-proof block validation across scoped OS threads, and a streaming prover holding peak memory near `550 MiB`. Field arithmetic and IOP equations are detailed in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

### Wire Size & Archival Cap Accounting (`149,130 B` Cap)

Each margin pairs an exact encoding scope against the `149,130 B` archival cap (sized to keep chain growth around `12 GiB/day` at `1 tx/s`):

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Measured / Expected | Margin vs. Cap (Measured) | Worst-Case Ceiling | Margin vs. Cap (Ceiling) |
| --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (header + proof + 52 cols + pruned siblings) | 138,461 B *(138,364 B rollover)* | 10,669 B | 140,476 B | **8,654 B** |
| **L1 `Profile 2` `pfUSDC` private pay / exit** (no public signer) | **137,860 B** (pay) · **138,724 B** (exit) | **11,270 B** · 10,406 B | 140,476 B (inner) | **8,654 B** |
| **Standalone signed deposit wire** (adds `5,261 B` ML-DSA-65 pubkey + sig) | 143,722 B | 5,408 B | 145,737 B | **3,393 B** |
| **L1 archived deposit — `redb` key-value store** (rehearsal max body `144,397 B`, charged `145,140 B`) | 144,770–145,140 B | 3,990–4,360 B | **146,546 B** | **2,584 B** |
| **L1 archived deposit — `JSONL` file store** (adds JSONL envelope + digest filename) | 144,804 B | 4,326 B | **146,580 B** | **2,550 B** |

Worst-case archived signed deposits leave `2,550–2,584 B` of ceiling margin. If future framing or signature updates need additional bytes, the two concrete levers are raising the archival cap or dropping Round-34 column openings (each dropped opening reclaims `~1.5 KB` at a cost of `~5.4` bits of pure-IOP soundness).

---

## 3. Security Failure Modes, Lean 4 Formalization & Audit Scope

![PFSH02 conditional QROM security curves](/blog/pq-payments/pfsh02-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum query budget Q, showing the regime crossover at Q = 2^81.28 and the 160-bit unpinned deposit-account bound.*

![PFSH02 security dependency and blast-radius map](/blog/pq-payments/pfsh02-dependency-map.svg)
*Figure 4. Dependency and blast-radius map separating Value Conservation (Theorem 3), Authorization (Theorem 4), and Confidentiality (Theorem 5) by foundation type.*

Every theorem, underlying lemma (IOP soundness Theorem 1A, QROM zero-knowledge Theorem 1B / App. B, and compressed-oracle extraction Theorem 2A / App. A.3), hybrid game, and exact-rational script output lives in the [Companion Mathematical Appendix](/research/pfsh02-proofs/) and [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/26e5a10a5d6f8087b0d20a44b646e88e0042a382/docs/security/peel-binius-shielded-pq-payments.md).

### What Is Now Kernel-Checked in Lean 4 (`formal/lean/`, 2,729 LOC)

To eliminate algebraic, operator-norm, case-analysis, and accounting errors before external audit, we formalized the mathematical core of PFSH02 in **Lean 4 (`v4.20.0`) + Mathlib** across nine modules (`formal/lean/PFSH02/`). Every theorem compiles with **zero `sorry`s and zero custom axioms** (`#print axioms` reports only Lean’s standard `[propext, Classical.choice, Quot.sound]`):

| Lean 4 Module | Spec Coverage | Kernel-Verified Results |
| --- | --- | --- |
| `Params.lean` | `check_math.py`, Tables 1–2 | `L_max = 86`, Johnson margin `7/6 < √2`, `3.652` constant, wire margins, 66-bit no-overflow, `p_34`, `ε_curve`, and Theorem 2A bounds at `Q = 2^64, 2^80, 2^96` |
| `Peel.lean` | App. A.1, Lemma 1 (`Peel(M)`) | Exact 4-line square-root telescoping, `k ≤ 86`, Case 1 (`0 ≤ n' ≤ 2D`, incl. `n' = 0`), Case 2 BCIKS20 hypotheses & curve monotonicity |
| `DualBinding.lean` | App. A.1, Lemmas 2, 3 & 4 | Univariate Schwartz–Zippel, `Bad_pt` union bound, `A_both ⊆ A_prox ⊆ D_u` + dual-poly binding, Lagrange `K_32` subfield inheritance, ring-switch `γ` (`≤ 4`) & `ρ_rs` (`≤ 386`) bounds |
| `Rank3Op.lean` | App. A.3, Lemma A.3.0 & A.3.4(b) | Exact rank-3 self-adjoint operator `O_s = ST Z_s ST`, both-directions norm `≤ √(8p) ≤ √(10p)`, exact readout error `2/N − 1/N² < 2/N` |
| `CompressedOracle.lean` | App. A.3, Lemmas A.3.1–A.3.4 & Thm 2A | Block-diagonal superposition norm reduction, tree-invariance (`MRoot⁻¹`), both-directions capacity, `∑√q ≤ (2/3)(Q+1)^(3/2)` telescoping, Theorem 2A bound |
| `ZeroKnowledge.lean` | §3.4 & App. B (Lemmas 1.1–1.2, Thm 1B) | Exact `5,216`-bit unopened-leaf bijection, `(1 − q)^M ≤ e^(-qM)` & capped-PoW `TV < 2^-182`, `Sim_IOP` bijections, Theorem 1B bound at `Q = 2^96` |
| `ValueConservation.lean` | §4.1, Theorem 3 (3a & 3b) | Full genesis-to-block induction proving shielded-pool conservation (3a) and joint burned/credited conservation (3b) |
| `ConjectureA4.lean` | App. A.4, Theorem 2B (SE wrapper `B^H`) | Upward monotonicity of `E_3` (`exit = 0`, `Pr[E_3] ≤ 8 Q_eff² p_E3`), escape permanence, and exhaustive deterministic Cases A / B / C trichotomy inside `B^H` |
| `AuthAndPrivacy.lean` | §§4.2–4.3, Theorems 4 & 5 | Mode 3 key-pinning dichotomy (zero axioms), 2-hop Theorem 4 reduction, and symmetric 5-game Theorem 5 hybrid incl. GMP22 sub-hop `(v)` |

**What Lean 4 does *not* close (and still requires external review):**
1. **Model-to-code fidelity:** Confirming that the Lean abstractions match the actual Rust/Go implementations and full 34-round transcript/SHAKE256 circuit wiring;
2. **External literature interfaces:** Checking the black-box interfaces to published [BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654), **GHHM21 Thm 1**, **AHU19 Thm 3**, and the view-equivalence step connecting real `Sim_BCS` unopened leaves to wrapper `B^H` in Appendix A.4;
3. **Non-standard assumptions & multi-tx privacy:** Evaluating the five non-standard assumptions (`JointPRF`: spend key yields independent PRFs across address/nullifier domains; `PRG`: dummy-input derivation is pseudorandom; `Hide`: commitments hide note blinding; `IK-CCA`: FIPS-203 ML-KEM ciphertexts hide the recipient key under CCA; `IR-PRF`: ML-KEM implicit rejection behaves as a PRF for non-recipients) and extending Theorem 5 beyond a single challenge transaction.

### Failure Modes & Conditional Security Summary

Three practical failure modes define the external audit surface:
- **Authorization failure permits theft without inflating supply.** Value conservation (Theorem 3) does not rely on Appendix A.4, **but conservation alone cannot prevent theft** if spend authorization (Theorem 4) fails.
- **Conservation failure permits unbacked minting.** Above \(Q = 2^{81.28}\) quantum oracle queries, 384-bit proof-tree (`MT_1`) collisions overtake spot-check error, degrading the conditional QROM bound to `~2^-92` at `Q = 2^96` and vacuity at `2^126.75`.
- **Multi-transaction adaptive confidentiality is unmodeled.** Theorem 5 covers a single challenge transaction under the five non-standard assumptions above.

**Conditional model bounds below are kernel-checked arithmetic outputs of the unreviewed specification, not established end-to-end system security levels:**

| Security Property & Failure Mode | Foundation & Lean 4 Status | Conditional Model Calculation (`Params.lean` / `math_bounds.json`) |
| --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation risk*) | **Published BCIKS20 + Lean-checked core (model-to-code unreviewed).** Unmodified-oracle extraction only (no simulation, no App. A.4, no ZK): `Peel.lean`, `DualBinding.lean`, `Rank3Op.lean`, `CompressedOracle.lean`, `ValueConservation.lean`, plus 384-bit SHAKE256 CR/zero-preimage. | Classical ROM: \(\lesssim 2^{-238}\) at \(Q=2^{64}\), \(\lesssim 2^{-192}\) at \(Q=2^{96}\).<br/>QROM (cond. on BCIKS20 + model fidelity): \(\lesssim 2^{-171}\) at \(Q=2^{64}\), \(\lesssim 2^{-138}\) at \(Q=2^{80}\), \(\lesssim 2^{-92}\) at \(Q=2^{96}\). |
| **Spend Authorization & Non-Malleability** (Theorem 4, Modes 1–2 — *theft risk*) | **Lean-checked `B^H` core + unreviewed real-to-wrapper bridge & non-standard SHAKE256 assumptions.** `ZeroKnowledge.lean` + `ConjectureA4.lean` (`E_3` + Cases A/B/C) + unreviewed real-`Sim_BCS`-to-`B^H` view equivalence (App. A.4) + SHAKE256 `JointPRF`/`PRG`. | **Not established end-to-end.** Conditional on external audit of App. A.4 bridge & SHAKE256 assumptions: ZK-dominated \(\lesssim 2^{-151}\) at \(Q=2^{64}\) across \(2^{32}\) proofs. |
| **Deposit Authorization** (Theorem 4, Mode 3 — *deposit forgery risk*) | **Standard (Key-Pinned, Lean-checked) / Weak (Unpinned).** `prepare_pq_account_debit` pins the depositor’s full ML-DSA-65 public key in `account.public_key_hex` on first signed tx. | Key-pinned: ML-DSA-65 EUF-CMA + SHA-384 CR.<br/>Unpinned brand-new accounts: 160-bit preimage \(\sim 2^{-32}\) at \(Q=2^{64}\), vacuous at \(Q=2^{80}\). |
| **Confidentiality & Recipient Anonymity** (Theorem 5 — *privacy loss*) | **Single-Transaction Model + Non-Standard Assumptions.** Lean-checked 5-game hybrid (`AuthAndPrivacy.lean`, incl. GMP22 sub-hop `(v)`): Thm 1B ZK + ML-KEM-1024 IND-CCA2 + HMAC-SHA-384 PRF + AES-256-GCM INT-CTXT/IND$-CPA + non-standard `IK-CCA`, `IR-PRF`, `JointPRF`, `PRG`, `Hide`. | Parameterized by user count, scan queries, and primitive advantages (no scalar bound; multi-tx adaptive composition unmodeled). |

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements below ran on 24 November 2026 on branch `feat/pq-payments-production-candidate` (`ec58522dc`; `26e5a10a5` adds only `formal/lean/`, leaving all Rust/Go binaries bit-identical) on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone tests ran `n = 50` trials per fixture (`mint`, `hop1`, `hop2`) pinned to CPU 2. Inside-validator tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, both warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof blocks). These are single-host implementation measurements, not universal hardware guarantees or sustained network-throughput results.

### 4.1 Verification & Proving Matrix (Internal Targets: `< 50 ms` Single-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload (Scope of Median Range) | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Internal Target |
| --- | --- | ---: | ---: | ---: | --- |
| **Standalone Rust verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ`), 1 core | 20.35–20.43 ms | 20.99–26.45 ms | 33.81 ms *(20.21 full-tree)* | Met (`< 50 ms`) |
| **Standalone Go verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ` ASM), 1 core | 30.82–31.11 ms | 31.18–31.99 ms | 32.45 ms *(31.26 full-tree)* | Met (`< 50 ms`) |
| **Standalone Go portable** (`mint`/`hop1`/`hop2`, `n=50` each) | `-tags purego` (0 ASM), 1 core | 42.76–43.08 ms | 43.52–43.72 ms | **44.08 ms** | Met (`< 50 ms`) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core pinned | 23.58–24.06 ms | 23.78–36.91 ms | 37.17 ms | Met (`< 50 ms`) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Portable (no `PCLMULQDQ`), 1 core | 36.96–39.64 ms | 38.70–44.45 ms | **45.23 ms** | Met (`< 50 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Accelerated, 4-core parallel** | 49.82–69.75 ms | 73.26–87.64 ms | 102.10 ms | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Portable, 4-core parallel** | 78.76–85.05 ms | 88.14–99.01 ms | **108.44 ms** | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core sequential | 92.94–102.20 ms | 93.89–104.08 ms | 107.53 ms | Met (`< 200 ms`) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Portable, 1 core sequential | 145.43–161.96 ms | 147.20–201.97 ms | 180.30 ms valid *(207.96 invalid)* | **Missed on invalid batches** (`208.0 ms > 200 ms`); met with 4-core parallel |
| **Rust client proving** (`mint`/`hop1`/`hop2`, `n=50`, `~550 MiB` RSS) | 16 thr / 1 core | 2.64 s / 24.61–24.71 s | 26.29–27.24 s (1c) | 27.68 s (1c) | Measured (EPYC host; browser/mobile untested) |

Across all measured single-transaction configurations (warm and `128 MiB` cold-cache), the largest observed verification time was `45.23 ms`, and for 4-proof parallel blocks `108.44 ms`. Because single-core sequential portable validation of 4 attacker-crafted invalid proofs reached `207.96 ms`, Gate 2 codifies `PCLMULQDQ` support or `≥ 4` verification cores as a validator hardware baseline.

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites

*(Terminology: **M8** is the six-validator activation, pause, and restart rehearsal; **R64** is a captured 1,734-block live-devnet archive used to confirm zero replay drift while PQ payments are inactive.)*

| Suite | Result (24 Nov 2026, Commit `26e5a10a5`) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,729` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib) |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`, `pq_payment_rehearsal_tests`)** | **Passed** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`) |
| **Historical live-devnet replays** | 1,734-block `R64` paired archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Scope of automated checks:* Lean 4 verifies the mathematical derivations inside its formal models (not Rust/Go code equivalence); Z3 `5.4.1` proves the 66-bit conservation adder, 2-bit Merkle mux, and dummy-input gating (not full-circuit SHAKE256 wiring); and Rust, Go, Python, and Lean proofs share one author team, so cross-checks are regression and internal consistency checks rather than independent external review.

---

## 5. Evidence Artifacts, Reproduction & Activation Gates

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & 18 Reviewer Questions** | Symbol glossary, Lean 4 theorem map, Lemmas 1–4, Thms 1A/1B/2A, App. A.3–A.4, App. B, Thms 3–5 | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,729` LOC), `lakefile.toml`, `README.md` (`commit 26e5a10a5`) | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/26e5a10a5d6f8087b0d20a44b646e88e0042a382/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | Commit `26e5a10a5`, Lean 4 summary, test counts, 50-trial standalone & 21-trial validator tables, replay digests | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Six-Validator Rehearsal Record** | `R64` 1,734-block replay, validator receipts & fail-closed halt log | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for the Lean 4 Mathlib cache + build, `~3 min` and `~3.7 GiB` peak RSS for `verify.sh`, `~2 min` for `postfiat-node --lib`, and `~1 min` for the six-validator rehearsal.

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout 26e5a10a5d6f8087b0d20a44b646e88e0042a382   # branch feat/pq-payments-production-candidate

# 1. Build and kernel-verify all 9 Lean 4 proof modules (0 sorrys, 0 custom axioms)
(cd formal/lean && lake exe cache get && lake build PFSH02)

# 2. Verify 36 fixture/script checksums & run the 7-stage standalone suite
(cd tools/pft-binius-shielded-pq && sha256sum -c SHA256SUMS && ./verify.sh)

# 3. Run the postfiat-node library suite (750 tests) and 6-validator M8 rehearsal
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation (Acceptance Criteria)

No activation date is set; PFSH02 remains disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic resolution and code audit:** External cryptographers must publish a written review covering **Theorem 3** (value conservation, incl. `Peel(M)`, Thm 1A, and Thm 2A / App. A.3 QROM extraction), **Theorem 4 Modes 1–3** (spend and deposit authorization, incl. Thm 1B / App. B QROM ZK, SHAKE256 `JointPRF`/`PRG`, and the Appendix A.4 / Theorem 2B real-`Sim_BCS`-to-`B^H` view-equivalence bridge), **Theorem 5** (confidentiality), the Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement code. Activation is blocked until any protocol or proof gap in Appendix A.4 is resolved, an accepted multi-transaction confidentiality scope is documented, and every high/critical audit finding is closed on the release commit.
2. **Production-genesis cut, hardware qualification, and scale validation:** Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series; enforce a validator minimum-hardware baseline (`PCLMULQDQ` support or `≥ 4` verification cores so attacker-crafted 4-proof invalid batches stay under `200 ms`); implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and measure real browser-WASM/mobile client proving and multi-node sustained-load behavior.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited production release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with user-facing migration tooling and explicit privacy guidance for exiting the legacy Orchard pool.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `26e5a10a5`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/26e5a10a5d6f8087b0d20a44b646e88e0042a382/formal/lean), the [Companion Mathematical Appendix](/research/pfsh02-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
