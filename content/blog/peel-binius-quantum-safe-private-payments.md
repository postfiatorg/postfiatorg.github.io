---
title: "PFSH02: Experimental Curve-Free Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering report, like-for-like same-host Orchard comparison, Lean 4 formalization, and security-status assessment for Peel-Binius-Shielded (PFSH02)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack."
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
> Passing tests, benchmarks, and Lean 4 model proofs do not establish end-to-end cryptographic security. **Spend authorization (Theorem 4)** still requires independent external review of an unreviewed QROM simulation-extractability bridge (**Appendix A.4 / Theorem 2B**) and non-standard SHAKE256 assumptions; **confidentiality (Theorem 5)** is modeled only for a single challenge transaction; and the Lean 4 models are not mechanically linked to the Rust or Go binaries. External review may require protocol redesign.

<div class="glance">
  <div><b>Off · Unaudited</b><span>Disabled on mainnet; external cryptographic &amp; code audit open</span></div>
  <div><b>~15.1× Larger Wire</b><span>137,860 B full private pay vs. 9,145 B binary Orchard (~18.5× proof-only)</span></div>
  <div><b>20–45 ms · ~25 s</b><span>Same-host 1-tx verify vs. Orchard 43 ms; 1-core prove ~25 s (~550 MiB RAM)</span></div>
  <div><b>Main Blocker</b><span>Unreviewed App. A.4 / Thm 2B auth bridge, single-tx privacy &amp; code audit</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash’s elliptic-curve **Orchard** protocol: encrypted note envelopes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve zero-knowledge proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH02**) is our experimental replacement built without elliptic curves. It combines a binary-field interactive oracle proof, hash-based note trees, lattice key encapsulation, and lattice deposit signatures built from NIST-standardized primitives (**SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024**, and **ML-DSA-65**). Standardized building blocks do not establish the security of a novel proof system or its composition. Before diving into details, here is where the work actually stands:

- **Established on this host (internal, single-team):** End-to-end Rust/Go/L1 settlement, `750/750` `postfiat-node` library tests, a six-validator activation/pause/restart rehearsal, same-host Orchard benchmarks, and nine Lean 4 model modules checking core algebraic/operator proofs with zero `sorry`s and zero custom axioms.
- **Conditional (model-level only):** Value-conservation bounds (Theorem 3, conditional on published BCIKS20 proximity gaps and model-to-code fidelity) and wrapper-level simulation-extractability bounds inside Appendix A.4 / Theorem 2B.
- **Unresolved (blocking mainnet):** Independent audit of the Appendix A.4 real-to-wrapper bridge, five non-standard SHAKE256/ML-KEM assumptions, multi-transaction confidentiality, Lean-to-Rust/Go implementation linkage, `2^24`-leaf node restart scaling, and browser/mobile proving.

*Reading guide:* **Users and operators** → same-host comparison below and Section 1 (payment flow, governance freeze risk, privacy limits). **Cryptographers** → Section 3 (failure modes, Lean 4 scope vs. audit boundaries) and the [Companion Mathematical Appendix](/research/pfsh02-proofs/). **Validators and engineers** → Section 4 (benchmark matrix and test suites) and Section 5 (build provenance, reproduction commands, and activation gates).

### Same-Host Baseline: Live Orchard vs. PFSH02 (CPU 2, AMD EPYC, `n = 50`)

We benchmarked Post Fiat’s live 2-action Orchard Halo-2 implementation (`postfiat.privacy.orchard-halo2.v2`, `orchard 0.14.0`, `verify_serialized_orchard_action`) directly against PFSH02 on the exact same pinned core (`CPU 2`, `ITERATIONS=50`, `report_hash = b4d43930...`). Every row below compares matching accounting scopes:

| Dimension (Scope-Matched) | Live Orchard (`orchard_verification_budget`, `n = 50`) | PFSH02 Prototype (`n = 50`) |
| --- | --- | --- |
| **Core assumptions** | Discrete log on Pasta curves (Halo 2) | SHAKE256, `3×SHA-512`, ML-KEM-1024, ML-DSA-65 + unreviewed QROM bridges & non-standard hash/KEM assumptions |
| **Proof bytes only (2-output transfer)** | **`7,264 B`** (Halo 2 proof, 2 actions) | **`134,140 B`** measured (`134,813 B` expected; **`~18.5×`** larger proof) |
| **Full binary 2-output transfer** | **`9,145 B`** canonical binary fields *(proof + `113 B` bundle + `2×884 B` actions; `9,297 B` w/ optional compact/binding fields)* | **`137,860 B`** full L1 `Profile 2` private pay (**`~15.1×`** larger; `140,476 B` inner ceiling) |
| **Single-tx verify (`CPU 2`, `n = 50`)** | **`43 ms` median** (`43–44 ms` range; cached VK, incl. Halo 2 proof + RedPallas spend-auth & binding sigs) | **`20.4 ms`** standalone Rust accel · **`23.6–24.1 ms`** validator accel · **`37.0–39.6 ms`** portable validator (`45.2 ms` max) |
| **Client proving (1 core)** | **`9.47 s`** (`action_build_and_prove_ms`, incl. action/key build) | **`24.61–24.71 s` med** (`~2.6×` slower, `27.68 s` max, `~550 MiB` RAM; `2.64 s` on 16 threads; browser/mobile untested) |
| **Throughput & raw daily wire volume** | Up to `8` actions/bundle (`max_actions = 8`, RPC batch cap `8`; no fixed 4-tx block cap) | **`≤ 4` PQ txs/block** (`4–8 tx/s` ceiling = **`~44–89 GiB/day`** raw tx bytes before indexing/replication; `~11.1 GiB/day` at `1 tx/s`) |
| **Assurance status** | Externally audited upstream (`orchard`); deployed in Zcash | **Unaudited**, single-team prototype; core math checked in Lean 4; disabled on mainnet |

On the same pinned core, PFSH02’s single-transaction verification spans `20.4 ms` (standalone accelerated Rust), `23.6–24.1 ms` (accelerated inside the validator), and `37.0–39.6 ms` median / `45.2 ms` max (portable fallback), placing it in the same range as—and faster on accelerated paths than—Post Fiat’s `43 ms` live 2-action Orchard verifier (`verify_serialized_orchard_action`, which checks the Halo 2 proof plus RedPallas spend-authorization and binding signatures). The costs measured in this PFSH02 prototype are **`~15.1×` larger full binary transactions** (`~18.5×` proof-only), **`~2.6×` slower single-core proving** (`~25 s` and `~550 MiB` RAM), tight block density (`≤ 4` txs/block with heavy archival growth at peak load), and **novel cryptography that has not been externally reviewed**.

---

## 1. Payment Flow, Governance Risks & Privacy Boundaries

![PFSH02 architecture diagram](/blog/pq-payments/pfsh02-architecture.svg)
*Figure 1. End-to-end lifecycle across Deposit, Private Pay (issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH02 transaction consumes **two input slots** (real or dummy) and produces **two output notes** under one 66-bit unsigned integer conservation law over \(\mathbb{Z}\):

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each amount lies in \([0, 2^{64}-1]\), and acceptance rule **R5** enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can reach \(2^{66}\) or wrap around.

1. **Deposit (Shield, \(v_{\mathrm{mint}} > 0\)).** A public account signs an ML-DSA-65 deposit (`5,261 B` public key + signature), debiting its public balance and inserting two note commitments into the asset’s depth-24 SHAKE256 tree. The recipient’s shielded address and note blinding stay off-chain.
2. **Private Transfer (no public sender account).** Under the current L1 fee profile (`Profile 2`, which removes the public fee-payer signature required in earlier drafts), the sender proves spend authority for two notes under a valid tree root, publishes two one-time nullifiers, and posts two commitments plus two `1,670 B` **ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM** ciphertexts. Neither native **PFT** nor governed issued-asset (`pfUSDC`) transfers carry a public sender account or signature: PFT fees burn inside the proof, while issued-asset transfers pay the governance-scheduled inner fee (`1` atom = `0.000001 pfUSDC` in rehearsal) into an on-chain `collected_private_fees` pot.
3. **Non-Interactive Offline Receive.** Recipients publish a static stealth address off-chain; senders need zero interactive round trips at payment time. Wallets scan outputs locally (`4,722` outputs/s/core measured on this AMD EPYC host), accepting a note only when decryption reproduces the public SHAKE256 commitment.
4. **Partial or Full Exit (Unshield, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits `unshield_dest` on the public ledger after checking per-asset pool reserves and destination trustline rules, with no public fee-paying account required.

### User, Governance & Operational Risks

- **Validator supermajority can freeze exits indefinitely (design choice):** Scheduling, fee changes, emergency pauses, and `collected_private_fees` withdrawals all require signed validator governance amendments meeting the active registry’s **BFT supermajority threshold** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in rehearsal). Setting `paused: true` refuses **all** PQ actions—deposits, transfers, **and exits**—until governance unpauses. That gives operators an incident circuit breaker, but it is an explicit censorship and liquidity-freeze power over users’ shielded funds.
- **Governance custody of issued-asset fees:** Native PFT fees burn directly. For externally backed issued assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves Post Fiat’s supply-conservation invariant (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`) without silent supply drift. Disbursement relies on validator governance rather than an autonomous protocol rule.
- **Epoch rollovers & anonymity-set dilution:** Native **PFT** and each governed issued asset maintain separate depth-24 trees holding \(2^{24} = 16,777,216\) leaves (`8,388,608` two-output transactions). An epoch lasts `~97.1 days` at `1 tx/s`, or **`12–24 days`** at the theoretical `4–8 tx/s` ceiling. Frozen trees remain spendable indefinitely via historical anchors—**users are never forced to migrate notes to preserve funds**. However, every new spend writes its change and recipient outputs into the *current* active epoch tree, so spending gradually migrates balances into the new tree, where early outputs initially share a smaller active-epoch anonymity set than spends anchored in mature historical trees.
- **Observable metadata & migration linkage:** PFSH02 hides private transfer amounts, recipient keys, and internal-spend sender accounts on the wire. Observers still see asset IDs, exact fees, tree epochs and anchors, inclusion heights, nullifiers, commitments/envelopes, public deposit/exit accounts and amounts, and gateway/validator IP addresses and timing. Migrating from Orchard requires a public exit followed by a PFSH02 deposit, which links amounts and timing (splitting amounts and adding delays are uncertain heuristics, not reliable unlinkability).
- **Key hygiene & static-key compromise:**
  - *Unpinned brand-new deposit accounts:* A brand-new account that has never signed an on-chain transaction is identified only by a 160-bit address hash (`~2^-32` quantum preimage exposure at `Q = 2^64` queries, vacuous at `Q = 2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating 160-bit exposure. **Operational requirement:** fund a fresh account with a minimal fee balance and send one low-value signed transaction (for example a self-transfer) to pin its public key before moving large deposits; automatic enforcement is not yet wired into the prototype CLI.
  - *No incoming-note forward secrecy:* Compromising a recipient’s long-term ML-KEM decapsulation key exposes all past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH02 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)
*Figure 2. Wire-size breakdown against the 149,130-byte archival cap (top) and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH02 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** All four note and Merkle hashes run in one Keccak-\(f[1600]\) permutation (`48 B` digests). Fifty-six Keccak permutations plus Merkle conditional-swap muxes, dummy-input gating, and 66-bit conservation adders pack into `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak’s \(\chi\) step.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four implementation choices drive verification speed: an exact 3D-Karatsuba ring-switch verifier (`11×` fewer field multiplications), 54-multiply Karatsuba field kernels with single-step inline `mulC32` reduction and register-based linear maps, cheap pool/nullifier checks before proof verification plus parallel 4-proof block validation across scoped OS threads, and a streaming prover holding peak memory near `550 MiB`. Field arithmetic and IOP equations live in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

### Wire Size & Archival Cap Accounting (`149,130 B` Cap)

Each row pairs an exact encoding scope against the `149,130 B` archival cap (originally sized to keep chain growth around `12 GiB/day` at `1 tx/s`; note that sustained operation at the `4–8 tx/s` block ceiling reaches `~44–89 GiB/day` of raw tx bytes before archival framing or replication):

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Measured / Expected | Margin vs. Cap (Measured) | Worst-Case Ceiling | Margin vs. Cap (Ceiling) |
| --- | ---: | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`3,648 B` header + `134,813 B` exp. proof) | 138,461 B *(138,364 B rollover)* | 10,669 B | 140,476 B | **8,654 B** |
| **L1 `Profile 2` `pfUSDC` private pay / exit** (no public signer; `72 B` outer prefix) | **137,860 B** (pay) · **138,724 B** (exit) | **11,270 B** · 10,406 B | 140,476 B (inner) | **8,654 B** |
| **Standalone signed deposit wire** (adds `5,261 B` ML-DSA-65 pubkey + sig) | 143,722 B | 5,408 B | 145,737 B | **3,393 B** |
| **L1 archived deposit — `redb` key-value store** (rehearsal max body `144,397 B`, charged `145,140 B`) | 144,770–145,140 B | 3,990–4,360 B | **146,546 B** | **2,584 B** |
| **L1 archived deposit — `JSONL` file store** (adds JSONL envelope + digest filename) | 144,804 B | 4,326 B | **146,580 B** | **2,550 B** |

Worst-case archived signed deposits leave `2,550–2,584 B` of ceiling margin. If future framing or signature changes exceed that headroom, raising the archival cap is an operational change; lowering Round-34 column openings (which saves `~1.5 KB` per opening at a cost of `~5.4` bits of pure-IOP soundness) would be a **cryptographic parameter redesign requiring renewed soundness analysis and external re-audit**, not a routine wire-budget adjustment.

---

## 3. Security Failure Modes, Lean 4 Core & Audit Scope

![PFSH02 conditional QROM security curves](/blog/pq-payments/pfsh02-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum oracle query budget Q, showing the regime crossover at Q = 2^81.28 and the 160-bit unpinned deposit-account bound.*

![PFSH02 security dependency and blast-radius map](/blog/pq-payments/pfsh02-dependency-map.svg)
*Figure 4. Dependency and blast-radius map separating Value Conservation (Theorem 3), Authorization (Theorem 4), and Confidentiality (Theorem 5) by foundation type.*

Throughout our security model, \(Q\) denotes an adversary’s total number of quantum queries to the random-oracle hash functions. Full theorem statements, exact-rational QROM bounds (for \(Q = 2^{64}, 2^{80}, 2^{96}\)), Lean 4 module tables, and 18 open reviewer questions live in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

Three practical failure modes define the external audit surface:
- **Spend-authorization failure (Theorem 4) permits theft without inflating supply.** Value conservation (Theorem 3) does not rely on **Appendix A.4 / Theorem 2B** (the adaptive QROM simulation-extractability argument), **but conservation alone cannot prevent theft** if spend authorization breaks.
- **Value-conservation failure (Theorem 3) permits unbacked minting or double spends.** Concrete risks include a misapplication of published [BCIKS20](https://eprint.iacr.org/2020/654) proximity-gap hypotheses, a discrepancy between the formal specification and the Rust/Go verifiers, or a SHAKE256/circuit constraint bug. Inside the specification’s QROM model, 384-bit proof-tree (`MT_1`) collisions also overtake spot-check error above \(Q = 2^{81.28}\) queries (exact conditional exponents are tabulated in the appendix).
- **Confidentiality limits (Theorem 5) leave multi-transaction privacy unmodeled.** Theorem 5 analyzes a single challenge transaction under five non-standard primitive assumptions: `JointPRF` (spend key yields independent PRFs across address/nullifier domains), `PRG` (dummy-input derivation is pseudorandom), `Hide` (commitments hide note blinding), `IK-CCA` (FIPS-203 ML-KEM ciphertexts hide the recipient key under CCA), and `IR-PRF` (ML-KEM implicit rejection behaves as a PRF for non-recipients).

### Lean 4 Formalization Scope & External Audit Matrix

To eliminate algebraic, operator-norm, case-analysis, and accounting slips before external review, we formalized the protocol’s core mathematical lemmas across nine **Lean 4 (`v4.20.0`) + Mathlib** modules (`formal/lean/PFSH02/`). All nine modules compile with zero `sorry`s and zero custom axioms (`#print axioms` reports only Lean’s standard `[propext, Classical.choice, Quot.sound]`). **Zero `sorry`s proves internal logical implication from explicit hypotheses—not that real-world assumptions hold or that the Rust/Go implementation matches the model.**

| Property & Failure Mode | What Lean 4 Proves (Inside Model) | Assumptions & Unformalized Bridges (Audit Targets) | Implementation Linkage |
| --- | --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3 — *inflation risk*) | Exact-rational parameters (`Params`), greedy peeling (`Peel`, `k ≤ 86`), polynomial/ring-switch bounds (`DualBinding`), rank-3 operator norm `≤ √(8p)` & compressed-oracle `∑√q` telescoping (`Rank3Op`, `CompressedOracle`), inductive supply conservation (`ValueConservation`) | Black-box literature bridges ([BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654), GHHM21 Thm 1, AHU19 Thm 3); SHAKE256 384-bit collision/zero-preimage resistance | **Not mechanically linked** to Rust/Go verifiers or full 34-round SHAKE256 circuit wiring (Z3 checks 66-bit adder, mux & dummy gating only) |
| **Spend Authorization** (Theorem 4, Modes 1–2 — *theft risk*) | Unopened-leaf bijection & capped-PoW TV bound (`ZeroKnowledge`); monotone `E_3` bound & deterministic Cases A/B/C trichotomy inside wrapper `B^H` (`ConjectureA4` / **Thm 2B**) | **Primary blocker:** Unreviewed view-equivalence bridge from real `Sim_BCS` unopened leaves to wrapper `B^H` (**App. A.4 / Thm 2B**), plus non-standard SHAKE256 `JointPRF`/`PRG` | **Not established end-to-end;** not linked to Rust/Go binaries |
| **Deposit Authorization** (Theorem 4, Mode 3 — *deposit forgery*) | Key-pinned vs. unpinned dichotomy (`AuthAndPrivacy`: pinning full ML-DSA-65 pubkey eliminates 160-bit preimage term) | ML-DSA-65 EUF-CMA + SHA-384 CR for pinned accounts; **unpinned brand-new accounts remain weak** (160-bit hash preimage) | Checked by unit/rehearsal tests in `prepare_pq_account_debit`; manual external code audit required |
| **Confidentiality & Anonymity** (Theorem 5 — *privacy loss*) | Symmetric 5-game hybrid accounting including GMP22 sub-hop `(v)` (`AuthAndPrivacy`) | **Single-transaction model only** (multi-tx adaptive composition unmodeled); ML-KEM-1024 IND-CCA2, HMAC-SHA-384, AES-256-GCM + 5 non-standard assumptions (`IK-CCA`, `IR-PRF`, `JointPRF`, `PRG`, `Hide`) | Not mechanically linked to wallet/KEM implementation |

All conditional QROM numerical outputs from `Params.lean` and `math_bounds.json` are tabulated in the [Companion Mathematical Appendix](/research/pfsh02-proofs/) so they are read alongside their explicit hypotheses rather than mistaken for established system security ratings.

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements below ran on 24 November 2026 on one shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone tests ran `n = 50` trials per fixture (`mint`, `hop1`, `hop2`) pinned to CPU 2. Inside-validator tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, both warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof blocks). These are single-host implementation measurements, not universal hardware guarantees or sustained multi-node throughput results.

### 4.1 Verification & Proving Matrix (Internal Targets: `< 50 ms` Single-Tx Max, `< 200 ms` 4-Tx Parallel Block Max)

| Workload (Scope of Median Range) | Backend & Concurrency | Per-Condition Medians | p95 | Largest Observed Max | Internal Target |
| --- | --- | ---: | ---: | ---: | --- |
| **Live Orchard 2-action baseline** (`orchard_verification_budget`, `n=50`) | Halo 2 + RedPallas (cached VK), 1 core CPU 2 | **43 ms** | 44 ms | 44 ms | Reference baseline |
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

Because single-core sequential portable validation of 4 attacker-crafted invalid proofs reached `207.96 ms`, Gate 2 requires measured hardware qualification against the `< 200 ms` 4-proof invalid-batch ceiling (using `PCLMULQDQ` support or `≥ 4` verification cores as the candidate baseline).

### 4.2 Consolidated Test, Replay, Rehearsal & Formal Suites

*(Terminology: **M8** is the six-validator activation, pause, and restart rehearsal; **R64** is a separate 1,734-block live-devnet archive used to confirm zero replay drift while PQ payments are inactive.)*

| Suite | Result (24 Nov 2026) |
| --- | --- |
| **Lean 4 formal proof library (`formal/lean/`)** | **9 / 9 modules built (`2,729` LOC), 0 `sorry`s, 0 custom axioms** (`lake build PFSH02`, Lean `v4.20.0` + Mathlib) |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`, `pq_payment_rehearsal_tests`)** | **Passed** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`) |
| **Historical live-devnet replays** | 1,734-block `R64` paired archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Internal consistency caveat:* Rust, Go, Python, Z3, and Lean artifacts were written by a single team, so cross-language agreement is an internal consistency check rather than independent external review.

---

## 5. Build Provenance, Evidence Artifacts & Activation Gates

**Build provenance:** All results come from [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2), branch `feat/pq-payments-production-candidate`, commit `26e5a10a5d6f8087b0d20a44b646e88e0042a382` (cleanly mergeable onto `public/main` `994589467`; Rust/Go binaries are bit-identical to `ec58522dc`, with `26e5a10a5` adding only `formal/lean/`).

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs, Lean 4 Map & 18 Reviewer Questions** | Symbol glossary, 9-module Lean 4 table, Lemmas 1–4, Thms 1A/1B/2A, App. A.3–A.4 (Thm 2B), App. B, Thms 3–5 & conditional bounds | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Lean 4 Proof Suite (Source)** | 9 modules (`2,729` LOC), `lakefile.toml`, `README.md` | [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/26e5a10a5d6f8087b0d20a44b646e88e0042a382/formal/lean) |
| **Consolidated Evidence Packet (JSON)** | Provenance, Lean 4 summary, like-for-like Orchard baseline, test counts & benchmark tables | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Rehearsal & Archive Replay Record** | Six-validator `M8` activation/pause/restart log plus separate `R64` 1,734-block pre-activation archive replay | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math, Z3 & SHA-256 Manifest** | `math_bounds.json`, `circuit_equivalence.json` & 36-file `SHA256SUMS` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) · [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

*Tested toolchain & resources:* Lean `v4.20.0` (`elan` + `lake exe cache get`), Rust `1.85+` (`cargo --locked`), Go `1.25.1`, Python `3.12` + `z3-solver 5.4.1` (or `tools/pft-binius-shielded-pq/Dockerfile`). Expect `~2 min` for the Lean 4 Mathlib cache + build, `~3 min` and `~3.7 GiB` peak RSS for `verify.sh`, `~2 min` for `postfiat-node --lib`, `~1 min` for the six-validator rehearsal, and `~15 s` for the 50-trial Orchard baseline.

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout 26e5a10a5d6f8087b0d20a44b646e88e0042a382   # branch feat/pq-payments-production-candidate

# 1. Build and kernel-verify all 9 Lean 4 proof modules (0 sorrys, 0 custom axioms)
(cd formal/lean && lake exe cache get && lake build PFSH02)

# 2. Verify 36 fixture/script checksums & run the 7-stage standalone suite
(cd tools/pft-binius-shielded-pq && sha256sum -c SHA256SUMS && ./verify.sh)

# 3. Run the same-host 50-trial Orchard baseline on CPU 2
ITERATIONS=50 taskset -c 2 cargo run --release --locked -p postfiat-privacy-orchard --example orchard_verification_budget

# 4. Run the postfiat-node library suite (750 tests) and 6-validator M8 rehearsal
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation (Acceptance Criteria)

No activation date is set; PFSH02 remains disabled on mainnet until all three gates close and the final release commit reproduces every artifact:

1. **Independent cryptographic resolution and code audit:** External cryptographers must publish a signed written audit covering **Theorem 3** (value conservation, incl. `Peel(M)`, Thm 1A, and Thm 2A / App. A.3 QROM extraction), **Theorem 4 Modes 1–3** (spend and deposit authorization, incl. Thm 1B / App. B QROM ZK, SHAKE256 `JointPRF`/`PRG`, and the **Appendix A.4 / Theorem 2B** real-`Sim_BCS`-to-`B^H` view-equivalence bridge), **Theorem 5** (confidentiality), Lean 4 model-to-code correspondence, and the Rust/Go/L1 settlement code. Activation is blocked until (a) any gap in Appendix A.4 / Theorem 2B is resolved (redesigning if needed), (b) every high or critical audit finding is closed and re-verified on the release commit, and (c) Post Fiat engineering and validator governance sign off on a published multi-transaction confidentiality specification stating either a proved multi-tx bound or explicit accepted limits.
2. **Production-genesis cut, measured hardware qualification, and scale validation:** Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series; run reproducible qualification benchmarks on representative validator hardware classes verifying `< 200 ms` max latency on attacker-crafted 4-proof invalid batches (testing `PCLMULQDQ` or `≥ 4` verification cores rather than relying on CPU flags alone); implement and verify bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and publish measured browser-WASM/mobile proving and sustained multi-node load/storage results.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited release binary pinned to the final release commit, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), paired with wallet key-pinning enforcement for brand-new accounts, Orchard exit/re-deposit tooling, and explicit user-facing privacy guidance on migration linkage.

---

*Open-source repository: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `26e5a10a5`). External reviewers can begin with [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/26e5a10a5d6f8087b0d20a44b646e88e0042a382/formal/lean), the [Companion Mathematical Appendix](/research/pfsh02-proofs/), and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
