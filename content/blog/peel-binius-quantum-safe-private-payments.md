---
title: "Peel-Binius-Shielded (PFSH02): Post-Quantum Private Payments on Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering, benchmark, and security analysis of Peel-Binius-Shielded (PFSH02)—Post Fiat L1's unaudited release candidate for private PFT and governed issued-asset payments built without elliptic curves from SHAKE256, SHA-512, AES-256-GCM, ML-KEM-1024, and ML-DSA-65."
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
  <div><b>137.9–146.6 KB</b><span>Profile 2 private pay (137.9 KB) to worst-case L1 stored deposit (146.6 / 149.1 KB cap)</span></div>
  <div><b>20–44 ms · 50–86 ms</b><span>Single-tx verify across Rust/Go/purego (max 44.1 ms); 4-proof parallel block (50–70 ms accel, 69–86 ms portable)</span></div>
  <div><b>750 pass · 7 / 7</b><span>`postfiat-node` tests (0 fail; 45 non-PQ ignored), 7-stage standalone suite &amp; 6-validator Profile 2 rehearsal</span></div>
  <div><b>Pre-Audit RC</b><span>Branch `feat/pq-payments-production-candidate` (`2ae8c8e02`); blocked on audit, prod cut &amp; height `H`</span></div>
</div>

Post Fiat L1 already signs public transactions and validator votes with post-quantum **ML-DSA-65** (FIPS 204). Its legacy shielded pool, however, runs Zcash's Orchard protocol over elliptic curves—meaning encrypted note envelopes archived today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve zero-knowledge proofs could be forged to mint unbacked funds once such a machine exists.

We built **Peel-Binius-Shielded** (wire format **PFSH02**) to eliminate elliptic curves from Post Fiat's private-payment stack. The design assembles a new binary-field interactive oracle proof, hash-based note trees, lattice key encapsulation, and lattice deposit signatures from NIST-standardized building blocks: **SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024** (FIPS 203), and **ML-DSA-65** (FIPS 204). **Standardized primitives do not, by themselves, establish the security of a new proof system or its composition.**

On 24 November 2026 we consolidated the implementation onto release-candidate branch `feat/pq-payments-production-candidate` (commit `2ae8c8e02`, merged cleanly atop `public/main` `994589467`, not yet merged into `public/main`). Every implemented test suite, verification-latency benchmark, and six-validator Profile 2 rehearsal passes—including pure-Go verification without hardware acceleration at `42.8–43.1 ms` median (`44.1 ms` max across 150 trials).

### Where This Build Stands

- **Verified in code and rehearsal:** `750` passed / `0` failed in `postfiat-node --lib` (`45` pre-existing `#[ignore]` tests are opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, or legacy-disk suites; **0 of 45 touch PQ payments**); `7/7` stages pass in the standalone Rust/Go/Python driver; the 6-validator Profile 2 rehearsal passes end-to-end with payerless issued-asset fees, emergency pause, cold restart, and snapshot import; every standalone backend verifies below `45 ms` max on a single core.
- **Unresolved cryptographic obligations:** The proof system has **not** undergone external audit. Value conservation (Theorem 3) rests on published [BCIKS20](https://eprint.iacr.org/2020/654) plus a new unreviewed peeling lemma and compressed-oracle extraction proof; **spend authorization and non-malleability (Theorem 4) currently rely on an unproven simulation-extractability conjecture (Conjecture A.4) and non-standard SHAKE256 assumptions**; confidentiality (Theorem 5) is analyzed in a single-transaction model and depends on a non-standard ML-KEM key-privacy assumption. All three implementations (Rust, Go, Python) share one author team, so cross-language parity is a regression check rather than third-party validation.
- **Operating costs and practical tradeoffs:** Each private payment is `~138–146 KB` (leaving only `2.55–2.58 KB` of headroom under the `149,130 B` archival cap); blocks cap PQ payments at `4` (`~578 KB` max, roughly `4–8 tx/s` peak at `0.5–1 s` block intervals, or `~12 GiB/day` archival growth at `1 tx/s`); client proving takes `2.64 s` on 16 threads or `24.6–27.7 s` on 1 core (`~550 MiB` peak RSS); each per-asset depth-24 tree holds `8,388,608` two-output transactions (`~97.1 days` at `1 tx/s`) before epoch rollover, and small per-asset pools yield small anonymity sets; deposits from unpinned brand-new accounts expose a 160-bit address preimage (`~2^-32` at `Q = 2^64`) until their first signed transaction; compromising a recipient's static ML-KEM key exposes past incoming envelopes; and an emergency governance pause halts **all** PQ actions, including exits, until unpaused.
- **Three gates before live-chain activation:** (1) independent external cryptographic and code audit resolving blocking findings (including Conjecture A.4), (2) a production-genesis release cut with production-scale (`2^24`-leaf) node restart and index-checkpoint measurements, and (3) a signed validator-supermajority governance vote setting live activation height \(H\).

---

## 1. How a PFSH02 Payment Works

![PFSH02 end-to-end architecture showing Deposit, Profile 2 Private Pay, Exit, disjoint SHAKE256 and 3x SHA-512 hash families, per-asset Depth-24 epoch trees, and 0-round ML-KEM-1024 stealth receive](/blog/pq-payments/pfsh02-architecture.svg)

Every PFSH02 transaction consumes **two input slots** (real or dummy) and creates **two output notes** under one uniform integer conservation law over \(\mathbb{Z}\):

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

All individual amounts lie in \([0, 2^{64}-1]\), and acceptance rule **R5** enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), bounding each side by \(3(2^{64}-1) < 2^{66}\) so 66-bit unsigned arithmetic represents every balance transition without modular wrap-around.

1. **Shield (Deposit, \(v_{\mathrm{mint}} > 0\)).** A public account signs an ML-DSA-65 deposit (`5,261 B` public key + signature under context `postfiat-l1-v2/tx/v1`), debiting its public balance and inserting two new note commitments into the asset's depth-24 SHAKE256 note tree. The recipient's shielded address \(A\) and note blinding \(R\) stay off-chain.
2. **Private Pay (L1 Profile 2, no public sender account).** The sender's wallet proves in zero knowledge that it knows spend secrets for two unspent notes under a valid historical tree root, publishes two one-time nullifiers to prevent double-spending, and posts two new commitments plus two `1,670 B` **ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM** encrypted envelopes. **Neither PFT nor issued-asset (`pfUSDC`) transfers carry a public sender account or signature:** native PFT fees burn inside the proof, while issued-asset transfers pay the governance-scheduled asset fee (`pq_payment_rehearsal_v1:fee:<atoms>`, rehearsal start: `1` atom = `0.000001 pfUSDC`) inside the proof into an on-chain `collected_private_fees` pot.
3. **Non-Interactive Offline Receive.** Recipients publish a static stealth address \((\mathrm{ek}, A = H_A(S))\) off-chain; senders need zero interactive round trips with the recipient at payment time. Wallets scan chain outputs locally at `4,722–8,971` outputs/s/core, decapsulating each envelope and accepting a note only when its decrypted opening reproduces the public SHAKE256 commitment.
4. **Partial or Full Unshield (Exit, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits `unshield_dest` on the public ledger, checking per-asset pool reserves and destination trustline/account policy, with no public fee-paying account required.

### Governance Controls, Issued-Asset Fees & Emergency Pause

- **Why issued-asset fees go to a collector pot instead of burning:** Native PFT fees burn directly, reducing total PFT supply. For externally backed issued assets such as `pfUSDC`, burning tokens inside a private spend would break 1:1 backing parity with off-chain reserves. Routing inner issued-asset fees into `collected_private_fees` keeps `public_balances + shielded_reserve + collected_private_fees == outstanding_supply` exact at every block.
- **Who controls fees, pause, and disbursement:** Scheduling activation, changing the issued-asset fee, pausing the pool, and withdrawing from `collected_private_fees` (`pq_private_fee_withdraw_v1:<recipient>`) all require signed validator governance amendments meeting the active validator registry's **BFT supermajority threshold** (\(\lfloor 2n/3 \rfloor + 1\) validators—5 of 6 in the rehearsal set; sub-threshold amendments are rejected with `BFT threshold`). Withdrawals credit a recipient holding an enabled trustline for the asset.
- **Emergency pause semantics:** A governance amendment with `paused: true` makes `pq_rehearsal_active` return `false` across `consensus_artifacts.rs` and `pq_payment_actions.rs`. That halts **all** PQ transactions—deposits, private transfers, **and exits**—until governance unpauses. Existing receipts and state remain readable, but funds inside the PQ pool cannot exit while a pause is active.

### Per-Asset Trees, Epoch Rollover & Privacy Boundaries

Native **PFT** and each governed issued source series (`pfUSDC`) maintain separate depth-24 SHAKE256 trees holding \(2^{24} = 16,777,216\) leaves—**8,388,608 two-output transactions** (\(\approx 97.1\text{ days}\) at a sustained `1 tx/s`). The asset ID and tree epoch bind into the proof transcript before Round 1, while global nullifier and commitment uniqueness across all assets and epochs prevents cross-asset replay. When a tree fills, it freezes permanently (its roots stay valid anchors forever) and a fresh empty epoch opens; old notes migrate forward via a standard 1-real + 1-dummy spend.

PFSH02 hides **private transfer amounts**, recipient keys, and internal-spend sender accounts from the transaction wire. On-chain observers still see:
- the asset / source series, exact fee, tree epoch and anchor, inclusion height, two nullifiers, and two commitments/envelopes;
- public accounts and exact amounts at deposit and exit edges;
- legacy Orchard migrations (which exit publicly and re-deposit fresh into PQ, making migrated amounts and timing linkable unless split and delayed);
- network-level caller IP addresses and request timing at gateways/validators, plus reduced anonymity whenever an asset pool or freshly rolled epoch is small.

Because non-interactive stealth receive encrypts to a recipient's long-term ML-KEM decapsulation key, compromising that key later exposes past incoming envelopes encrypted to it (no forward secrecy for incoming notes—the same static-key tradeoff as Zcash Orchard).

---

## 2. Cryptographic Design & Binary-Field Engine

![PFSH02 byte-exact wire budget vs 149,130 B archival ceiling and 34-round IOP soundness schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)

PFSH02 splits in-circuit hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:

- **In-circuit (FIPS-202 SHAKE256):** All four note and tree hashes (\(H_A\), \(H_{\mathrm{Coin}}\), \(H_{\mathrm{SN}}\), \(H_{\mathrm{Node}}\)) take \(\le 135\text{ B}\), executing in a single Keccak-\(f[1600]\) permutation (`512`-bit capacity, `48 B` digests). Fifty-six Keccak permutations plus Merkle conditional-swap muxes, `is_dummy` gating, and 66-bit conservation adders pack into **447,014 active rows** (`2,192,844` scalar constraints) over five bit-arrays whose only quadratic gates are the five Keccak \(\chi\) monomials.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Every proof Merkle node (`MT_1`, height 21, \(n = 2^{21}\)), transcript absorb, field challenge, and Round-34 query draw comes from one fixed-range 1,536-bit oracle built from three domain-prefixed SHA-512 calls (`0x00`, `0x01`, `0x02`) with fixed-length ASCII domain tags. Keeping the never-transmitted internal Fiat–Shamir state at **512 bits** adds zero wire bytes while giving all 68 programmed transcript calls \(\ge 512\)-bit conditional min-entropy.

Adapting the binary-tower polynomial commitment and ring-switching architecture of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset E = \mathbb{F}_{2^{384}}\), four engineering optimizations bring verification below `50 ms` across hardware-accelerated and pure-portable backends alike:

1. **Exact 3D-Karatsuba Ring-Switch Verifier:** Cuts \(H\)-domain inner-product verification from `143,360` to `13,122` \(E\)-multiplications (`11×` fewer), differentially tested against naive \(384 \times 384\) sums in Rust and Go.
2. **54-Multiply Karatsuba Kernels (Hardware + Portable):** On x86-64 with `PCLMULQDQ`, Rust (`20.4 ms` standalone) and Go (`30.9 ms` standalone) run branchless 54-`PCLMULQDQ` multiplication. On portable builds without `PCLMULQDQ`, 54-mul Karatsuba, single-step inline `mulC32`, hoisted `log16` tables, and register-based ring-switch accumulation cut Go `-tags purego` from `71.5 ms` down to **`42.8–43.1 ms` median (`44.1 ms` max)** and Rust portable inside-validator verification to **`36.8–37.8 ms` median (`39.2 ms` p95)**.
3. **Cheap Checks First + Parallel 4-Proof Block Verification:** Validators check genesis domain, activation height, fee rules, root window, nullifiers, and commitments *before* verifying any proof (`PR #211`), then verify up to `4` proofs per block concurrently across scoped OS threads sharing a bounded verified-statement cache—cutting 4-proof block validation from `143–252 ms` to **`49.8–69.8 ms` median (accelerated)** and **`68.8–85.6 ms` median (portable)**.
4. **Streaming L1-Cache Prover:** Skips identity Additive NTT levels for degree \(D = 565 < 1,024\), proving a two-input payment in `2.64 s` (16 threads) or `24.6–27.7 s` (1 core) within `547–562 MiB` peak RSS. That memory and CPU budget is practical for desktop/server wallets and browser WASM with worker threads, but remains heavy for low-end mobile devices without outsourced proving.

### Wire & On-Chain Archive Accounting (149,130 B Cap)

| Encoding Layer (Depth-24 Tree, \(t = 52\) Column Openings) | Measured / Expected (B) | Worst-Case Ceiling (B) | Headroom vs. 149,130 B Cap |
| --- | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (`3,648` hdr + `59,916` proof + `38,896` cols + pruned siblings) | 138,461 *(138,364 B rollover)* | 140,476 | 8,654 B |
| **L1 Profile 2 `pfUSDC` private pay / exit vectors** (no public signer) | **137,860** (pay) · **138,724** (exit) | 140,476 (inner) | 8,654 B |
| **Standalone raw signed deposit wire** (adds `5,261 B` ML-DSA-65 pubkey + sig) | 143,722 | 145,737 | 3,393 B |
| **L1 stored deposit/payment — `redb` store** (M8 Profile 2 largest body `144,397 B`, charged `145,140 B`) | 144,770–145,140 | **146,546** | **2,584 B** |
| **L1 stored deposit/payment — `JSONL` file store** (adds JSONL envelope & digest filename) | 144,804 | **146,580** | **2,550 B** |

The `2,550–2,584 B` ceiling margin on worst-case signed deposits is tight by design (anchored to the `12 GiB/day` archival target at `1 tx/s`). Any future increase in signature size, envelope fields, or archive framing requires either raising the archival cap or trimming proof parameters.

---

## 3. Security Foundations & Audit Scope

![PFSH02 conditional QROM error bounds across quantum query budgets Q from 2^48 to 2^128 showing the regime crossover at Q=2^81.28 and the 160-bit unpinned account-address regime](/blog/pq-payments/pfsh02-qrom-security-curves.svg)

Every lemma, hybrid game, assumption, and exact-rational calculation lives in the companion [PFSH02 Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/) and [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/2ae8c8e02cdd39e5ed0ed84dd8a8d57241005fac/docs/security/peel-binius-shielded-pq-payments.md). We separate each security property by what it rests on so external reviewers can inspect the blast radius of every assumption independently:

![Dependency and failure blast-radius map separating Value Conservation Theorem 3, Authorization Theorem 4, and Privacy Theorem 5 across published anchors, unreviewed proofs, the A.4 conjecture, and non-standard assumptions](/blog/pq-payments/pfsh02-dependency-map.svg)

| Property | Proof Basis & Unresolved Dependencies | Quantified Conditional Bound (`math_bounds.json`) |
| --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3) | **Unmodified-oracle extraction only** (no simulation, no Conj. A.4, no ZK). Combines published **[BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654)** strictly inside the proven Johnson bound (\(m'=3\), avoiding unproven beyond-Johnson proximity conjectures), new unreviewed greedy peeling lemma (`Peel(M)`, \(L_{\max}=86\)), and compressed-oracle QROM extraction (Theorem 2A / App. A.3) with 384-bit SHAKE256 collision/zero-preimage resistance. | **Classical ROM:** \(\lesssim 2^{-238}\) at \(Q=2^{64}\), \(\lesssim 2^{-192}\) at \(Q=2^{96}\).<br/>**QROM (cond. on App. A.1–A.3):** \(\lesssim 2^{-171}\) at \(Q=2^{64}\), \(\lesssim 2^{-138}\) at \(Q=2^{80}\), \(\lesssim 2^{-92}\) at \(Q=2^{96}\) (384-bit \(MT_1\) collision crossover at \(Q=2^{81.28}\), trivial at \(2^{126.75}\)). |
| **Spend Authorization & Non-Malleability** (Theorem 4, Modes 1–2) | Combines QROM Zero-Knowledge (Theorem 1B / App. B, built on published **GHHM21** & **AHU19**), **Conjecture A.4** (an unproven multi-proof simulation-extractability wrapper sketch), and non-standard SHAKE256 `JointPRF` / dummy `PRG` assumptions. | \(\lesssim 2^{-151}\) at \(Q=2^{64}\) (ZK-dominated via hard-capped \(M_{\mathrm{pow}}=2^{27}\) PoW bound \(2^{-183}\) across \(P=2^{32}\) proofs), **conditional on resolving Conj. A.4** & SHAKE256 assumptions. |
| **Deposit Authorization** (Theorem 4, Mode 3) | **On-chain ML-DSA-65 public-key pinning:** `prepare_pq_account_debit` (`crates/execution/src/entrypoints.rs`) pins the depositor's full `1,952 B` ML-DSA-65 public key in `account.public_key_hex` on its first signed transaction. | **Key-pinned accounts:** reduces directly to **ML-DSA-65 EUF-CMA + SHA-384 CR** (zero 160-bit exposure).<br/>**Unpinned brand-new accounts (before first signed tx):** 160-bit address truncation gives \(\sim 2^{-32}\) at \(Q=2^{64}\), vacuous at \(Q=2^{80}\). |
| **Confidentiality & Recipient Anonymity** (Theorem 5) | 5-hop **single-transaction** hybrid (no A.3/A.4): Theorem 1B ZK + ML-KEM-1024 IND-CCA2 + HMAC-SHA-384 PRF + AES-256-GCM INT-CTXT/IND$-CPA + non-standard FIPS-203 ML-KEM `IK-CCA` + **implicit-rejection non-recipient scan sub-hop `(v)`** (closing the GMP22 asymmetry in \(H_4\)) + non-standard SHAKE256 `JointPRF`, dummy `PRG`, and `Hide`. | Parameterized by user count \(U\), active scan queries \(q_{\mathrm{scan}}\), and primitive advantages (no single scalar bound; multi-transaction adaptive composition not yet modeled). |

Two architectural takeaways matter most for reviewers:
- **Blast-radius isolation:** Value conservation (no inflation, no double spend) does **not** depend on Conjecture A.4, zero-knowledge simulation, or ML-KEM anonymity. Even if an audit rejects Conjecture A.4 and requires protocol changes for spend authorization, the supply-conservation core rests on unmodified-oracle extraction alone.
- **Unpinned-account operational rule:** Any account that has signed at least one on-chain transaction has its full ML-DSA-65 public key pinned and suffers zero 160-bit address exposure. Wallets receiving funds onto a brand-new address prior to pinning remain in the 160-bit preimage regime until their first signed transaction.

Full theorem statements, the exact compressed-oracle extraction formula, symbol definitions, and all 18 external reviewer questions are published in the [Companion Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/).

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements below were collected on 24 November 2026 on release-candidate branch `feat/pq-payments-production-candidate` (`2ae8c8e02`; Rust L1 crates bit-identical to `d2a83d1d5`, with `2ae8c8e02` optimizing `go-verifier/field.go`) on a shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone benchmarks ran `n = 50` trials per fixture (`mint`, `hop1`, `hop2`) pinned to CPU 2; inside-validator benchmarks ran `n = 21` trials per condition across PFT and `pfUSDC`, both warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof runs). These are single-host test-environment measurements, not universal hardware guarantees.

### 4.1 Verification & Proving Matrix (Uniform Gates: `< 50 ms` Single-Tx, `< 200 ms` 4-Tx Block)

| Workload (Scope of Median Range) | Backend & Concurrency | Per-Condition Medians | p95 | Max | Gate Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Standalone Rust verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ`), 1 core | **20.35–20.43 ms** | 20.99–26.45 ms | 33.81 ms *(20.21 full-tree)* | **PASS (< 50 ms)** |
| **Standalone Go verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ` ASM), 1 core | **30.82–31.11 ms** | 31.18–31.99 ms | 32.45 ms *(31.26 full-tree)* | **PASS (< 50 ms)** |
| **Standalone Go portable** (`mint`/`hop1`/`hop2`, `n=50` each) | `-tags purego` (0 ASM), 1 core | **42.76–43.08 ms** | 43.52–43.72 ms | **44.08 ms** | **PASS (< 50 ms)** |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core pinned | **23.58–24.06 ms** | 23.78–36.91 ms | 37.17 ms | **PASS (< 50 ms)** |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Portable (no `PCLMULQDQ`), 1 core | **36.84–37.76 ms** | 37.73–39.22 ms | 39.27 ms warm *(50.33 cold outlier)* | **PASS med/p95/warm** *(1 cold outlier)* |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core pinned | **92.94–102.20 ms** | 93.89–104.08 ms | 107.53 ms | **PASS (< 200 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Accelerated, 4-core parallel** | **49.82–69.75 ms** | 73.26–87.64 ms | 102.10 ms | **PASS (< 200 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Portable, 1 core pinned | **145.48–147.64 ms** | 148.13–155.38 ms | 161.93 ms | **PASS (< 200 ms)** |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Portable, 4-core parallel** | **68.84–85.57 ms** | 86.41–96.24 ms | 106.64 ms | **PASS (< 200 ms)** |
| **Rust proving** (`mint`/`hop1`/`hop2`, `n=50`, ~550 MiB RSS) | 16 thr / 1 core | 2.64 s / **24.61–24.71 s** | 26.29–27.24 s (1c) | 27.68 s (1c) | Measured |
| **Offline wallet scanning** (ML-KEM-1024 + AES-GCM) | 1 core (EPYC / EPYC-Genoa) | 4,722–8,971 outputs/s | — | — | Measured |

### 4.2 Test, Replay & Rehearsal Suites

| Suite | Result (24 Nov 2026, Branch `feat/pq-payments-production-candidate`) |
| --- | --- |
| **Full `postfiat-node --lib` suite** (includes PR #209 fixes for the 4 pre-existing `main` failures) | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` external-bridge/Solana/Base-Sepolia/Anvil/legacy-disk tests; **0 PQ tests ignored**) |
| **6-Validator M8 Rehearsal on Profile 2** (`pq_payment_rehearsal_tests`) | **PASS** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-Stage Standalone Verification Driver** (`tools/pft-binius-shielded-pq/verify.sh`) | **ALL 7/7 PASSED** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **`postfiat-privacy-binius`** (accelerated + `--features portable`) | **9 passed / 9 passed, 0 failed** |
| **`postfiat-privacy-binius-wallet`, `postfiat-storage` PQ archive & Python CLI** | **8 passed · 1 passed · 9 passed, 0 failed** |
| **Historical Live-Devnet Replays** (zero impact while inactive) | **1,734-block R64 paired archive replay** (`c28eb872...5910`, exact 1B PFT supply) + **1,754-block live devnet replay** (`246d6113...4b8e6`, matching all 6 live validators) |
| **Un-upgraded Validator Fail-Closed Upgrade Check** | Confirmed: pre-activation M4 node halts on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

---

## 5. Evidence Packets & Commit-Pinned Reproduction

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & 18 Reviewer Questions** | Symbol glossary, Lemmas 1–4, App. A.3, Conj. A.4, App. B, Theorems 3–5 (incl. GMP22 sub-hop) | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Consolidated Evidence Packet (JSON)** | Commit `2ae8c8e02`, test counts, 50-trial standalone & 21-trial validator benchmarks, replay digests | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Full source inventory (line counts), payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **M8 Release Rehearsal Record** | R64 1,734-block paired replay, 6-validator receipts & M4 fail-closed halt log | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math & Z3 Outputs** | Updated `math_bounds.json` (incl. `Q_tot` & classical ROM bounds) & `circuit_equivalence.json` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) |
| **SHA-256 Fixture Manifests** | 36-file SHA-256 checksums (`SHA256SUMS` inside repo) | [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout 2ae8c8e02cdd39e5ed0ed84dd8a8d57241005fac   # branch feat/pq-payments-production-candidate

# 1. Verify 36 fixture/script checksums & run the 7-stage standalone suite (or use the pinned Dockerfile)
cd tools/pft-binius-shielded-pq
sha256sum -c SHA256SUMS
./verify.sh

# 2. Benchmark Go purego (no ASM / no PCLMULQDQ) across 50 trials on CPU 2
(cd go-verifier && go build -tags purego -o /tmp/go-verifier-purego .)
taskset -c 2 /tmp/go-verifier-purego bench --tx payments/tx_mint.bin --ledger payments/ledger_mint.json --trials 50

# 3. Run the postfiat-node library suite (750 tests) and 6-validator M8 Profile 2 rehearsal
cd ../..
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

*Scope of automated checks:* `check_math.py` validates exact rational arithmetic of the spec's formulas, not the proof derivations; Z3 `5.4.1` proves the 66-bit conservation adder, 2-bit Merkle mux, and `is_dummy` gating, not full-circuit SHAKE256 wiring; and Rust, Go, and Python share one author team, so cross-language parity is a regression check rather than independent verification.

---

## 6. Three Gates to Live Activation

Three formal gates remain before PFSH02 can activate on the live network:

1. **External cryptographic and code audit:** Independent review of the proof system—specifically Theorems 1A, 1B, 2A, **Conjecture A.4**, Theorem 5's implicit-rejection sub-hop and non-standard assumptions, and the Rust/Go/L1 settlement code—with resolution of any blocking findings (including protocol changes if required).
2. **Production-genesis release cut and scale validation:** Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with the live chain genesis and governed `pfUSDC` series, and measure full-tree (`2^24`-leaf) node restart and index checkpointing at production scale (currently cold restart rebuilds `PqIndexes` by walking historical pair pages).
3. **Signed governance activation vote:** Once every validator runs the audited production release, ratify a BFT-supermajority governance amendment setting live activation height \(H\).

---

*Open-source code lives in [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (release-candidate branch `feat/pq-payments-production-candidate`, commit `2ae8c8e02`). External cryptographers can start directly from the [Companion Mathematical Arguments & Reviewer Appendix](/research/pfsh02-proofs/) and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
