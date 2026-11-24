---
title: "Peel-Binius-Shielded (PFSH02): Hash-Based Private Payments on Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Post Fiat L1 has consolidated, hardened, and rehearsed Peel-Binius-Shielded (PFSH02)—private payments for PFT and governed issued assets built with zero elliptic curves from SHAKE256, SHA-512, AES-256-GCM, ML-KEM-1024, and ML-DSA-65. Every engineering gate passes across Rust, Go, and a six-validator Profile 2 chain; external cryptographic review is the gate before live activation."
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
  - PFSH02
  - ML-KEM-1024
  - ML-DSA-65
  - Evidence
---

<div class="glance">
  <div><b>137.9–146.6 KB</b><span>Profile 2 private pay (`137.9 KB`) to worst-case L1 stored deposit (`146.6 / 149.1 KB` cap)</span></div>
  <div><b>24 ms · 50–70 ms</b><span>Validator verify: `24 ms` single tx (`37 ms` portable); `50–70 ms` 4-proof parallel block</span></div>
  <div><b>750 / 750 · 7 / 7</b><span>Consolidated `postfiat-node` tests, 7-stage standalone suite &amp; 6-validator Profile 2 rehearsal</span></div>
  <div><b>Audit Ready</b><span>All engineering gates green on `main`; held for external cryptographic audit &amp; height `H`</span></div>
</div>

Post Fiat L1 already signs public transactions and validator votes with post-quantum **ML-DSA-65** (FIPS 204). Its legacy shielded pool, however, runs Zcash's Orchard protocol over elliptic curves—meaning encrypted note envelopes archived today could be decrypted retroactively by a future fault-tolerant quantum computer, and discrete-log proofs could eventually be forged on the day of an attack.

We built **Peel-Binius-Shielded** (wire format **PFSH02**) to remove elliptic curves from Post Fiat's private-payment stack entirely. Every proof, commitment, encrypted note envelope, and deposit signature comes from NIST-standardized symmetric and lattice primitives: **SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024** (FIPS 203), and **ML-DSA-65** (FIPS 204).

On 24 November 2026 we consolidated the entire stack onto `public/main` (`d2a83d1d5a04a27091b66c8c02c155b55fab88de`): L1 Profile 2 payerless issued-asset fees, cheap pool checks before proof verification, 54-multiply Karatsuba portable kernels in both Rust and Go, parallel 4-proof block verification, and the full `main` test fixes. **Every engineering, performance, and rehearsal gate now passes.** Two items stand between this build and live-chain activation: an independent external cryptographic audit of the new proof system and its security reductions, and a signed governance vote choosing a live activation height \(H\).

---

## 1. How a PFSH02 Payment Works

![PFSH02 end-to-end architecture showing Deposit, Profile 2 Private Pay, Exit, disjoint SHAKE256 and 3x SHA-512 hash families, per-asset Depth-24 epoch trees, and 0-round ML-KEM-1024 stealth receive](/blog/pq-payments/pfsh02-architecture.svg)

A PFSH02 transaction always consumes **two input slots** (real or dummy) and creates **two output notes** under one uniform integer conservation equation over \(\mathbb{Z}\):

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Every amount lies in \([0, 2^{64}-1]\), and acceptance Rule **R5** enforces \(\mathrm{pub\_exit} := \mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), bounding each side by \(3(2^{64}-1) < 2^{66}\) so 66-bit unsigned integer arithmetic represents every transition with zero modular wrap-around.

1. **Shield (Deposit, \(v_{\mathrm{mint}} > 0\)).** A public account signs an ML-DSA-65 deposit (`5,261 B` key + signature under context `postfiat-l1-v2/tx/v1`), debiting its public balance and inserting two new note commitments into the asset's Depth-24 SHAKE256 note tree. The recipient's shielded address \(A\) and note blinding \(R\) never touch the chain.
2. **Private Pay (L1 Profile 2, zero public accounts).** The sender's wallet proves in zero knowledge that it knows spend secrets for two unspent notes under a valid historical tree root, publishes two one-time nullifiers to block double-spending, and posts two new commitments plus two `1,670 B` **ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM** envelopes. **Neither PFT nor issued-asset (`pfUSDC`) transfers carry a public sender account or signature:** native PFT fees burn inside the proof, while issued-asset transfers pay the exact governance-scheduled asset fee (`pq_payment_rehearsal_v1:fee:<atoms>`, proposed start: `1` atom = `0.000001 pfUSDC`) inside the proof into a public `collected_private_fees` pot that only a signed validator-registry governance vote can disburse.
3. **0-Round Offline Receive.** Recipients publish a static off-chain stealth address \((\mathrm{ek}, A = H_A(S))\). Wallets scan chain outputs locally at 4,700–8,900 outputs/s/core, decapsulating each envelope and accepting a note only when its decrypted opening reproduces the public SHAKE256 commitment.
4. **Partial or Full Unshield (Exit, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits `unshield_dest` on the public ledger, checking per-asset pool reserves and destination policy, with no public fee-paying account required.

### Isolated Per-Asset Trees & Epoch Rollover

Native **PFT** and each governed issued source series (`pfUSDC`) maintain isolated Depth-24 SHAKE256 trees holding \(2^{24} = 16,777,216\) leaves—enough for **8,388,608 two-output transactions** (\(\approx 97.1\text{ days}\) at a sustained \(1\text{ tx/s}\)). The asset ID and tree epoch bind directly into the proof transcript before Round 1, while global nullifier and commitment uniqueness across all assets and epochs prevents cross-asset replay or double-spending. When a tree reaches capacity it freezes permanently (its roots stay valid anchors forever) and a fresh empty epoch opens; old notes migrate forward via a standard 1-real + 1-dummy spend.

### Observable Metadata & Operational Boundaries

PFSH02 omits amounts, recipient keys, and internal-spend sender accounts from the transaction wire. On-chain observers still see:
- the asset / source series, exact fee, tree epoch and anchor, inclusion height, two nullifiers, and two commitments/envelopes;
- public accounts and amounts at deposit and exit edges;
- legacy Orchard migrations (which exit publicly and re-deposit fresh into PQ, making migrated amounts and timing linkable unless split and delayed);
- network-level caller IP addresses and request timing at gateways/validators, plus pool-size constraints when a pool is small.

Because offline 0-round stealth receive encrypts to a recipient's long-term ML-KEM key, compromising that decapsulation key later exposes past incoming envelopes encrypted to it (the same static-key tradeoff as Zcash Orchard).

---

## 2. Cryptographic Architecture & Binary-Field Engine

![PFSH02 byte-exact wire budget vs 149,130 B archival ceiling and 34-round IOP soundness schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)

PFSH02 separates in-circuit state hashing from proof compilation across **two completely disjoint NIST hash families** with zero shared permutation:

- **In-circuit (FIPS-202 SHAKE256):** All four note/tree hashes (\(H_A\), \(H_{\mathrm{Coin}}\), \(H_{\mathrm{SN}}\), \(H_{\mathrm{Node}}\)) take \(\le 135\text{ B}\), executing in a single Keccak-\(f[1600]\) permutation (`512`-bit capacity, `48 B` digests). Fifty-six Keccak permutations plus Merkle conditional-swap muxes, `is_dummy` gating, and 66-bit conservation adders pack into **447,014 active rows** (`2,192,844` scalar constraints) over five bit-arrays whose only quadratic gates are the five Keccak \(\chi\) monomials.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Every Merkle tree hash (`MT_1`, height 21, \(n = 2^{21}\)), transcript absorb, field challenge, and Round-34 query draw comes from one fixed-range 1,536-bit oracle built from three domain-prefixed SHA-512 calls (`0x00`, `0x01`, `0x02`) with fixed-length ASCII domain tags. Widening the never-transmitted internal Fiat–Shamir state from 384 to **512 bits** adds zero wire bytes while keeping all 68 programmed transcript calls at \(\ge 512\)-bit conditional min-entropy.

Adapting the binary-tower polynomial commitment and ring-switching architecture of **Diamond and Posen (Binius, 2023–2024)** over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset E = \mathbb{F}_{2^{384}}\), four engineering optimizations deliver sub-50 ms verification across **every** backend:

1. **Exact 3D-Karatsuba Ring-Switch Verifier:** Cuts \(H\)-domain inner-product verification from `143,360` to `13,122` \(E\)-multiplications (`11×` fewer), differentially tested against naive \(384 \times 384\) sums in Rust and Go.
2. **54-Multiply Karatsuba Kernels (Hardware + Portable):** On x86-64 with `PCLMULQDQ`, both Rust and Go Plan 9 assembly run branchless 54-`PCLMULQDQ` field multiplication (`21–24 ms` Rust, `32–36 ms` Go). On portable builds without `PCLMULQDQ`, replacing schoolbook multiplication and 128 KB `mulC32` table lookups with 54-mul Karatsuba, hoisted `log16` lookups, and inline `reduce_poly16_31` cut Go `-tags purego` from `58.9 ms` to **`46.9–48.9 ms` median** and Rust portable single-core validator verification to **`36.8–37.8 ms` median (`37.7–39.2 ms` p95)**.
3. **Parallel 4-Proof Block Verification + Cheap Checks First:** Validators check genesis domain, activation height, fee rules, root window, nullifiers, and commitments *before* touching any proof (`PR #211`), then verify up to `4` proofs per block in parallel across scoped OS threads (`consensus_artifacts.rs`) sharing a bounded verified-statement cache—cutting 4-proof block validation from `143–252 ms` down to **`49.8–69.8 ms` median (accelerated)** and **`68.8–85.6 ms` median (portable)**.
4. **Streaming L1-Cache Prover:** Skips identity Additive NTT levels for degree \(D = 565 < 1,024\), proving a two-input payment in `2.64 s` (16 threads) or `25.5–28.0 s` (1 core) within `547–562 MiB` peak RSS.

### Wire & On-Chain Archive Accounting (Under 149,130 B Cap)

| Encoding Layer (Depth-24 Tree, \(t = 52\) Column Openings) | Measured / Expected (B) | Worst-Case Ceiling (B) | Headroom vs. 149,130 B Cap |
| --- | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`3,648` hdr + `59,916` proof + `38,896` cols + pruned siblings) | 138,461 *(138,364 B rollover fixture)* | 140,476 | 8,654 B |
| **L1 Profile 2 `pfUSDC` private pay / exit vectors** (no public signer) | **137,860** (pay) · **138,724** (exit) | 140,476 (inner) | 8,654 B |
| **Standalone raw signed deposit wire** (adds `5,261 B` ML-DSA-65 pubkey + sig) | 143,722 | 145,737 | 3,393 B |
| **L1 stored deposit/payment — `redb` store** (M8 Profile 2 largest body `144,397 B`, charged `145,140 B`) | 144,770–145,140 | **146,546** | **2,584 B** |
| **L1 stored deposit/payment — `JSONL` file store** (adds JSONL envelope & digest filename) | 144,804 | **146,580** | **2,550 B** |

---

## 3. Mathematical Security Analysis & Audit Scope

![PFSH02 conditional QROM error bounds across quantum query budgets Q from 2^48 to 2^128 showing the regime crossover at Q=2^81.28 and the 160-bit account-address weak link](/blog/pq-payments/pfsh02-qrom-security-curves.svg)

PFSH02's security specification is written in full—every lemma, hybrid, assumption, and exact-rational parameter calculation—in the companion [PFSH02 Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/) and [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/d2a83d1d5a04a27091b66c8c02c155b55fab88de/docs/security/peel-binius-shielded-pq-payments.md). Because the proof system is new, we segregate every claim cleanly by what it rests on so external cryptographers can audit each layer directly:

![Dependency and failure blast-radius map separating Value Conservation Theorem 3, Authorization Theorem 4, and Privacy Theorem 5 across published anchors, unreviewed proofs, the A.4 conjecture, and non-standard assumptions](/blog/pq-payments/pfsh02-dependency-map.svg)

| Property | Basis & Audit Scope | Quantified Conditional Bound (`math_bounds.json`) |
| --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3) | **Unmodified-oracle extraction only** (no simulation, no Conj. A.4, no ZK). Combines published **BCIKS20 Thm 6.2** (Johnson bound, \(m'=3\)), new greedy peeling lemma (`Peel(M)`, \(L_{\max}=86\)), and compressed-oracle QROM extraction (Theorem 2A / App. A.3) with 384-bit SHAKE256 CR/zero-preimage. | **Classical ROM:** \(\lesssim 2^{-238}\) at \(Q=2^{64}\), \(\lesssim 2^{-192}\) at \(Q=2^{96}\).<br/>**QROM (cond. on App. A.1–A.3):** \(\lesssim 2^{-171}\) at \(Q=2^{64}\), \(\lesssim 2^{-138}\) at \(Q=2^{80}\), \(\lesssim 2^{-92}\) at \(Q=2^{96}\) (crossover \(Q=2^{81.28}\), trivial at \(2^{126.75}\)). |
| **Spend Authorization & Non-Malleability** (Theorem 4, Modes 1–2) | Combines QROM Zero-Knowledge (Theorem 1B / App. B, built on published **GHHM21** & **AHU19**), **Conjecture 2B (App. A.4)** (multi-proof simulation-extractability wrapper sketch), and non-standard SHAKE256 `JointPRF` / dummy `PRG` assumptions. | \(\lesssim 2^{-151}\) at \(Q=2^{64}\) (ZK-dominated via hard-capped \(M_{\mathrm{pow}}=2^{27}\) PoW bound \(2^{-183}\) across \(P=2^{32}\) proofs), conditional on Conj. A.4 & SHAKE256 assumptions. |
| **Deposit Authorization** (Theorem 4, Mode 3) | **On-chain ML-DSA-65 public-key pinning:** `prepare_pq_account_debit` (`crates/execution/src/entrypoints.rs`) pins the depositor's full 1,952-byte ML-DSA-65 public key in `account.public_key_hex` on first signed tx. | **Key-pinned accounts:** reduces directly to **ML-DSA-65 EUF-CMA + SHA-384 CR** (zero 160-bit exposure).<br/>**Unpinned accounts (before first signed tx):** 160-bit address truncation gives \(\sim 2^{-32}\) at \(Q=2^{64}\), vacuous at \(Q=2^{80}\). |
| **Confidentiality & Recipient Anonymity** (Theorem 5) | 5-hop single-transaction hybrid (no A.3/A.4): Theorem 1B ZK + ML-KEM-1024 IND-CCA2 + HMAC-SHA-384 PRF + AES-256-GCM INT-CTXT/IND$-CPA + non-standard FIPS-203 ML-KEM `IK-CCA` + **implicit-rejection non-recipient scan sub-hop `(v)`** (closing the GMP22 asymmetry in \(H_4\)) + non-standard SHAKE256 `JointPRF`, dummy `PRG`, and `Hide`. | Parameterized by user count \(U\), active scan queries \(q_{\mathrm{scan}}\), and primitive advantages (no single scalar bound; single-transaction model only). |

### Core Equations at a Glance

- **Greedy Peeling (`Peel(M)`, Lemma 1):** Telescoping the remaining domain size \(x_i = |L_i|\) via \(\sqrt{x_i} - \sqrt{x_{i+1}} > \sqrt{D/2}\) caps candidate codewords at \(L_{\max} = \lfloor\sqrt{2/\rho}\rfloor = 86\) and reduces Round-33a proximity to a single call to **BCIKS20 Theorem 6.2** strictly inside the proven Johnson bound (\(\varepsilon_{33a} \le 2^{-305.79}\)), avoiding the 2025-disputed Reed–Solomon conjectures.
- **Compressed-Oracle Straight-Line Extraction (Theorem 2A / App. A.3):** Derives the exact self-adjoint rank-3 operator norm \(\|P_S O_{x,z} P_{\neg S}\|_2 = \|P_{\neg S} O_{x,z} P_S\|_2 \le \sqrt{8p} < \sqrt{10p}\) (Lemma A.3.0), avoiding generic multi-round Fiat–Shamir's \((Q+1)^{68}\) blowup:
  $$\varepsilon_{\mathrm{Ext}}(Q, L) \le \left(3.652\, Q_v^{3/2} 2^{-192} + Q_v\sqrt{10\cdot\max(\varepsilon_{\mathrm{rbr}}(33a) + 2 Q_v 2^{-512},\; p_{34})}\right)^2 + \frac{2 L \kappa_v}{2^{384}}$$
  with \(p_{34} = 2^{-20}(\sqrt{2\rho})^{52} = 2^{-302.31}\) and \(\kappa_v = 963\) verifier oracle queries. Above \(Q = 2^{81.28}\), 384-bit \(MT_1\) collisions dominate (`~2^-92` at \(Q = 2^{96}\), matching the spec's \(32\,Q^3 / 2^{384} = 2^{-91}\) BHT sizing).
- **Hard-Capped QROM Zero-Knowledge (Theorem 1B / App. B):** Combines 5,216-bit marginal unopened-leaf min-entropy (AHU19 semi-classical O2H), hard-capped PoW total variation (\(\le 2^{-182.60}\)), and 68 sequential product-state GHHM21 reprogramming steps to bound \(\mathrm{Adv}_{\mathrm{QROM\text{-}ZK}}(2^{32}, Q) \le 2^{-150.60}\).

Read the full formal derivations and all 18 external reviewer questions in the [Companion Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/).

---

## 4. Consolidated Benchmarks, Rehearsals & Test Results

All measurements below were run on 24 November 2026 directly on the consolidated branch `feat/pq-payments-production-candidate` (`d2a83d1d5a04a27091b66c8c02c155b55fab88de`) on a shared 32-thread AMD EPYC KVM host (`n = 21` trials per validator condition with `1,024` history entries, pinned logical cores via `taskset` for 1-core runs, and `RAYON_NUM_THREADS=4` for 4-proof parallel block runs):

### 4.1 Validator & Standalone Verification Matrix

| Workload | Backend & Concurrency | Median (ms) | p95 (ms) | Max (ms) | Gate Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Standalone Rust verify** (`verify.sh` CPU 2) | Accelerated (`PCLMULQDQ`), 1 core | 21.56–22.17 | — | 22.17 *(20.52 full-tree)* | **PASS (< 50 ms)** |
| **Standalone Go verify** (`verify.sh` CPU 2) | Accelerated (`PCLMULQDQ` ASM), 1 core | 34.46–35.66 | — | 35.66 *(32.15 full-tree)* | **PASS (< 50 ms)** |
| **Standalone Go portable** (50 warm trials) | `-tags purego` (54-mul Karatsuba), 1 core | **46.94–48.90** | 50.32 | 50.77 | **PASS (< 50 ms med)** |
| **Inside-validator 1 action** (PFT & pfUSDC) | Accelerated, 1 core pinned | **23.58–24.06** | 23.78–36.91 | 37.17 | **PASS (< 50 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC) | Accelerated, 1 core pinned | **92.94–102.20** | 93.89–104.08 | 107.53 | **PASS (< 200 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC) | **Accelerated, 4-core parallel** | **49.82–69.75** | 73.26–87.64 | 102.10 | **PASS (< 200 ms)** |
| **Inside-validator 1 action** (PFT & pfUSDC) | Portable (no `PCLMULQDQ`), 1 core pinned | **36.84–37.76** | 37.73–39.22 | 39.27 *(1 cold spike 50.33)* | **PASS (med & p95 < 50 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC) | Portable, 1 core pinned | **145.48–147.64** | 148.13–155.38 | 161.93 | **PASS (< 200 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC) | **Portable, 4-core parallel** | **68.84–85.57** | 86.41–96.24 | 106.64 | **PASS (< 200 ms)** |
| **Rust proving** (2-input payment, ~550 MiB RSS) | 16 thr / 32 thr / 1 core | 2.64 s / 2.90 s / 25.5–28.0 s | — | — | Measured |
| **Offline wallet scanning** (ML-KEM + AES-GCM) | 1 core (EPYC / EPYC-Genoa) | 4,722–8,971 outputs/s | — | — | Measured |

### 4.2 Consolidated Test & Replay Suite (Zero Failures)

| Suite | Result (24 Nov 2026, Commit `d2a83d1d5`) |
| --- | --- |
| **Full `postfiat-node --lib` suite** (includes all 4 previously failing `main` tests fixed via PR #209) | **750 passed, 0 failed** (45 pre-existing ignored) |
| **6-Validator M8 Rehearsal on Profile 2** (`pq_payment_rehearsal_tests`) | **PASS** in 60.26 s (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-Stage Standalone Verification Driver** (`tools/pft-binius-shielded-pq/verify.sh`) | **ALL 7/7 PASSED** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1 equivalence) |
| **`postfiat-privacy-binius`** (accelerated + `--features portable`) | **9 passed / 9 passed, 0 failed** |
| **`postfiat-privacy-binius-wallet`, `postfiat-storage` PQ archive & Python CLI** | **8 passed · 1 passed · 9 passed, 0 failed** |
| **Historical Live-Devnet Replays** (zero impact while inactive) | **1,734-block R64 paired archive replay** (`c28eb872...5910`, exact 1B PFT supply) + **1,754-block live devnet replay** (`246d6113...4b8e6`, matching all 6 live validators) |
| **Un-upgraded Validator Fail-Closed Upgrade Check** | Confirmed: pre-activation M4 node halts on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

```mermaid
flowchart LR
    A["All 6 Validators<br/>Install Reviewed Release"] --> B["Signed Governance Vote<br/>pq_payment_rehearsal_v1(:fee)"]
    B --> C{"Block Height < H?"}
    C -- "Yes" --> D["PQ Payments Rejected<br/>Zero State-Root Overhead"]
    C -- "No (Height >= H)" --> E["Active: <= 4 PQ txs / block<br/>Parallel Verify (~50-86 ms)"]
    E --> F["Emergency Pause Vote<br/>(Value = 0)"]
    F --> G["New PQ Inclusions Refused<br/>Existing Receipts Readable"]
    B -. "Un-upgraded Validator" .-> H["Fail-Closed Halt at Scheduling Block<br/>unsupported governance amendment kind"]
```

---

## 5. Evidence Packets & Commit-Pinned Reproduction

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & 18 Reviewer Questions** | Symbol glossary, Lemmas 1–4, App. A.3, Conj. A.4, App. B, Theorems 3–5 (incl. GMP22 sub-hop) | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Consolidated Evidence Packet (JSON)** | Commit `d2a83d1d5`, all green test counts, new accelerated/portable benchmarks & replay digests | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Full source inventory (line counts), payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **M8 Release Rehearsal Record** | R64 1,734-block paired replay, 6-validator receipts & M4 fail-closed halt log | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math & Z3 Outputs** | Updated `math_bounds.json` (incl. `Q_tot` & classical ROM bounds) & `circuit_equivalence.json` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) |
| **SHA-256 Fixture Manifests** | 36-file SHA-256 checksums (`SHA256SUMS` inside repo) | [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout d2a83d1d5a04a27091b66c8c02c155b55fab88de   # consolidated Profile 2 release candidate

# 1. Verify 36 fixture/script checksums & run the 7-stage standalone suite (or use the pinned Dockerfile)
cd tools/pft-binius-shielded-pq
sha256sum -c SHA256SUMS
./verify.sh

# 2. Run the full postfiat-node library suite (750 tests) and 6-validator M8 Profile 2 rehearsal
cd ../..
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

*Scope of automated checks:* `check_math.py` verifies exact rational arithmetic of the spec's formulas (not the proof steps); Z3 `5.4.1` proves the 66-bit conservation adder, 2-bit Merkle mux, and `is_dummy` gating (not full-circuit SHAKE256 wiring); and Rust/Go/Python share one author team, so cross-language parity is a regression check rather than third-party validation.

---

## 6. Path to Live Activation

With the consolidated branch green across all tests, benchmarks, and six-validator rehearsals, three formal gates remain before switching PFSH02 on for the live network:

1. **External cryptographic & code audit:** Independent review of the new proof system (Theorems 1A, 1B, 2A, Conjecture A.4, Theorem 5's updated implicit-rejection sub-hop and non-standard assumptions, and the Rust/Go/L1 settlement code).
2. **Production-genesis release cut:** Target the live chain genesis and governed `pfUSDC` series (replacing the disposable rehearsal genesis guard) and measure full-tree (`2^24`-leaf) node restart/index checkpointing at production scale.
3. **Signed governance activation vote:** Schedule live height \(H\) once all validators are running the audited release.

---

*Open-source code in [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (consolidated release candidate `d2a83d1d5a04a27091b66c8c02c155b55fab88de`). External cryptographers can start directly from the [Companion Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/) and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
