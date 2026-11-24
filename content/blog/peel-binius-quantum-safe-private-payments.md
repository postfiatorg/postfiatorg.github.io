---
title: "Peel-Binius-Shielded (PFSH02): Experimental Post-Quantum Private Payments for Post Fiat L1"
date: 2026-11-24T00:00:00Z
draft: false
summary: "Engineering, benchmark, and security-status report for Peel-Binius-Shielded (PFSH02)—an unaudited experimental prototype replacing elliptic curves in Post Fiat L1's private-payment stack with SHAKE256, SHA-512, AES-256-GCM, ML-KEM-1024, and ML-DSA-65."
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

> **Status: unaudited experimental prototype — not active on mainnet and not ready for live funds.**  
> PFSH02 is built on branch `feat/pq-payments-production-candidate` (commit `ec58522dc`, cleanly mergeable onto `public/main` `994589467`). Passing tests and benchmarks do not establish cryptographic security: **spend authorization (Theorem 4) currently rests on an unproven simulation-extractability conjecture (Conjecture A.4) and non-standard SHAKE256 assumptions**, value conservation relies on new unreviewed arguments, and confidentiality covers only a single-transaction model. External review may require protocol redesign.

<div class="glance">
  <div><b>Unaudited · Conj. A.4</b><span>Spend authorization relies on unproven Conj. A.4; value conservation does not</span></div>
  <div><b>137.9 KB · 146.6 KB</b><span>Private-pay wire (8.7 KB margin) vs. worst-case stored deposit (2.55 KB under 149.1 KB cap)</span></div>
  <div><b>20–45 ms · 50–108 ms</b><span>Single-tx verify max across all backends (45.2 ms); 4-tx parallel block (50–85 ms med, 108 ms max)</span></div>
  <div><b>750 pass · 7 / 7</b><span>`postfiat-node` tests (0 fail; 45 non-PQ ignored) &amp; standalone Rust/Go/Python suite</span></div>
</div>

Post Fiat L1 already signs public transactions and validator consensus votes with post-quantum **ML-DSA-65** (FIPS 204). Its existing shielded pool, however, runs Zcash's elliptic-curve **Orchard** protocol: encrypted note envelopes archived on-chain today could be decrypted retroactively by a future fault-tolerant quantum computer, and elliptic-curve zero-knowledge proofs could be forged to mint unbacked funds once such a machine exists.

**Peel-Binius-Shielded** (wire format **PFSH02**) is our experimental replacement that removes elliptic curves from private payments entirely. It combines a binary-field interactive oracle proof, hash-based note trees, lattice key encapsulation, and lattice deposit signatures built from NIST-standardized primitives: **SHAKE256**, **SHA-512/SHA-384**, **AES-256-GCM**, **ML-KEM-1024** (FIPS 203), and **ML-DSA-65** (FIPS 204). Standardized building blocks do not establish the security of a novel proof system or its composition; the goal of this report is to put the code, benchmarks, tradeoffs, and exact unresolved proof obligations in front of external cryptographers and node operators.

### Why Replace Orchard — and What It Costs

Removing elliptic curves is not free. Compared with Post Fiat's existing Orchard pool, PFSH02 trades a roughly 30–60× larger transaction and an order-of-magnitude slower verifier and prover for a curve-free design:

| Dimension | Legacy Orchard Pool (Elliptic-Curve) | PFSH02 Prototype (Hash + Lattice) |
| --- | --- | --- |
| **Core hardness assumptions** | Discrete log on Pasta curves (Halo 2) | SHAKE256, `3×SHA-512`, ML-KEM-1024, ML-DSA-65 + **unproven Conj. A.4** & non-standard hash/KEM assumptions |
| **Quantum threat profile** | Retroactive note decryption + future proof forgery | Zero elliptic curves; conditional QROM bounds (unreviewed) |
| **Private transfer wire size** | ~2–5 KB | **137.9 KB** (`8.65 KB` under `149,130 B` archival cap) |
| **Single-core verification** | Low single-digit ms | **20.4–45.2 ms** max across Rust, Go, pure-Go & portable validator |
| **Client proving (1 core / 16 thr)** | ~1–3 s | **24.6–27.7 s** (1 core) / **2.64 s** (16 threads), `~550 MiB` RSS |
| **Block & epoch limits** | Higher density | `≤ 4` PQ txs/block (theoretical ceiling `4–8 tx/s` at `0.5–1 s` blocks); `8.39M` txs/epoch (`~97 days` at `1 tx/s`, `12–24 days` at ceiling) |
| **Audit & production maturity** | Externally audited; deployed in Zcash | **Unaudited**, single-team implementation; disabled on mainnet |

---

## 1. Payment Flow, Governance Controls & Privacy Boundaries

![PFSH02 architecture diagram](/blog/pq-payments/pfsh02-architecture.svg)
*Figure 1. End-to-end lifecycle across Deposit, Private Pay (issued-asset fee profile), and Exit, showing the disjoint SHAKE256 / 3×SHA-512 hash boundary, per-asset depth-24 trees, and non-interactive ML-KEM-1024 stealth delivery.*

Every PFSH02 transaction consumes **two input slots** (real or dummy) and produces **two output notes** under one 66-bit unsigned integer conservation law over \(\mathbb{Z}\):

$$v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + (\mathrm{fee} + v_{\mathrm{unshield}})$$

Each amount lies in \([0, 2^{64}-1]\), and acceptance rule **R5** enforces \(\mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\), so neither side can reach \(2^{66}\) or wrap around.

1. **Deposit (Shield, \(v_{\mathrm{mint}} > 0\)).** A public account signs an ML-DSA-65 deposit (`5,261 B` public key + signature), debiting its public balance and inserting two note commitments into the asset's depth-24 SHAKE256 tree. The recipient's shielded address and note blinding stay off-chain.
2. **Private Transfer (no public sender account).** Under the current L1 fee profile (`Profile 2`, which eliminates the public fee-payer signature required by earlier drafts), the sender proves spend authority for two notes under a valid tree root, publishes two one-time nullifiers, and posts two commitments plus two `1,670 B` **ML-KEM-1024 + HMAC-SHA-384 + AES-256-GCM** ciphertexts. Neither native **PFT** nor governed issued-asset (`pfUSDC`) transfers carry a public sender account or signature: PFT fees burn inside the proof, while issued-asset transfers pay the governance-scheduled inner fee (`1` atom = `0.000001 pfUSDC` in rehearsal) into an on-chain `collected_private_fees` pot.
3. **Non-Interactive Offline Receive.** Recipients publish a static stealth address off-chain; senders need zero interactive round trips with the recipient at payment time. Wallets scan chain outputs locally (`4,722` outputs/s/core on our AMD EPYC test host; up to `8,971` outputs/s/core in earlier EPYC-Genoa measurements), accepting a note only when decryption reproduces the public SHAKE256 commitment.
4. **Partial or Full Exit (Unshield, \(v_{\mathrm{unshield}} > 0\)).** Spends private notes and credits `unshield_dest` on the public ledger after checking per-asset pool reserves and destination trustline rules, with no public fee-paying account required.

### Governance Mechanics & Centralization Tradeoffs

- **Why issued-asset fees go to a collector pot:** Native PFT fees burn directly. For externally backed issued assets like `pfUSDC`, routing inner fees into `collected_private_fees` preserves Post Fiat's chosen accounting invariant (`public_balances + shielded_reserve + collected_private_fees == outstanding_supply`) so reserve reconciliation remains exact without silent supply drift.
- **Who controls fees, pause, and payouts:** Activation scheduling, fee changes, emergency pauses, and withdrawals from `collected_private_fees` require signed validator governance amendments meeting the active validator registry's **BFT supermajority threshold** (\(\lfloor 2n/3 \rfloor + 1\)—5 of 6 validators in our rehearsal set). Disbursement is therefore a validator-governance action rather than an autonomous protocol rule, which introduces governance trust over accumulated fees.
- **Emergency pause halts exits:** Setting `paused: true` makes `pq_rehearsal_active` return `false` across consensus verification and execution, refusing **all** PQ actions—deposits, private transfers, **and exits**—until governance unpauses. While this provides a circuit breaker for cryptographic incidents, it also means a validator supermajority can freeze pool liquidity indefinitely.

### Per-Asset Epochs & Privacy Limits

Native **PFT** and each governed issued asset (`pfUSDC`) maintain separate depth-24 SHAKE256 trees holding \(2^{24} = 16,777,216\) leaves—**8,388,608 two-output transactions**. At a sustained `1 tx/s` an epoch lasts `~97.1 days`; at the theoretical `4–8 tx/s` block-cap ceiling, a single asset tree would fill in **`12–24 days`**, triggering frequent epoch rollovers. When a tree fills it freezes permanently (its historical roots remain valid anchors forever) and a fresh epoch opens, with old notes migrating via a standard spend.

PFSH02 hides **private transfer amounts**, recipient keys, and internal-spend sender accounts on the wire. Observers still see:
- the asset identifier, exact fee, tree epoch and anchor, inclusion height, two nullifiers, and two commitments/envelopes;
- public accounts and exact amounts at deposit and exit edges;
- legacy Orchard-to-PFSH02 migrations (which require exiting Orchard publicly and re-depositing into PFSH02, making migrated amounts and timing linkable unless users split amounts and add delays);
- gateway/validator IP addresses and request timing, plus reduced anonymity whenever an asset pool or freshly rolled epoch has few users.

Two key-hygiene limits apply directly to users:
- **Unpinned deposit accounts:** Brand-new accounts that have never signed an on-chain transaction are identified only by a 160-bit address hash (`~2^-32` quantum forgery bound at `Q = 2^64`, vacuous at `Q = 2^80`). Once an account signs its first transaction, `prepare_pq_account_debit` pins its full `1,952 B` ML-DSA-65 public key on-chain, eliminating the 160-bit exposure. **Operational rule:** wallets should send one signed transaction from a new account before receiving large deposits.
- **No incoming-note forward secrecy:** Because non-interactive stealth receive encrypts to a recipient's long-term ML-KEM decapsulation key, compromising that key later exposes past incoming envelopes encrypted to it (the same static-key tradeoff as Orchard).

---

## 2. Proof Construction & Wire Accounting

![PFSH02 wire budget and 34-round IOP schedule](/blog/pq-payments/pfsh02-wire-and-iop.svg)
*Figure 2. Wire-size breakdown against the 149,130-byte archival cap (top) and the 34-round Peel-Binius interactive oracle proof schedule (bottom).*

PFSH02 separates in-circuit state hashing from proof compilation across **two disjoint NIST hash families** with zero shared permutation:
- **In-circuit (FIPS-202 SHAKE256):** All four note and Merkle hashes execute in a single Keccak-\(f[1600]\) permutation (`48 B` digests). Fifty-six Keccak permutations plus Merkle conditional-swap muxes, dummy-input gating, and 66-bit conservation adders pack into `447,014` active rows (`2,192,844` constraints) over five bit-arrays whose only quadratic gates are Keccak's \(\chi\) step.
- **Compiler Random Oracle (FIPS-180-4 `3 × SHA-512`):** Proof Merkle nodes (`MT_1`, height 21), transcript absorbs, field challenges, and Round-34 queries come from one domain-separated `1,536`-bit oracle with a `512`-bit internal Fiat–Shamir state.

Adapting the binary-tower polynomial commitment and ring-switching scheme of [Diamond and Posen (Binius, ePrint 2023/1784)](https://eprint.iacr.org/2023/1784) over \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset \mathbb{F}_{2^{384}}\), four engineering choices bring verification below `50 ms` across both hardware-accelerated (`PCLMULQDQ`) and pure-portable Rust/Go builds: an exact 3D-Karatsuba ring-switch verifier (`11×` fewer field multiplications), 54-multiply Karatsuba field kernels with single-step inline `mulC32` reduction and register-based linear maps, cheap pool/nullifier checks before proof verification plus parallel 4-proof block validation across scoped OS threads, and a streaming prover that keeps peak memory around `550 MiB`. Full field arithmetic and kernel details are documented in the [Companion Mathematical Appendix](/research/pfsh02-proofs/).

### Wire Size & Archival Cap Accounting (`149,130 B` Cap)

| Encoding Scope (Depth-24 Tree, 52 Column Openings) | Measured / Expected (B) | Worst-Case Ceiling (B) | Margin Under 149,130 B |
| --- | ---: | ---: | ---: |
| **Standalone raw non-mint wire** (header + proof + 52 cols + pruned siblings) | 138,461 *(138,364 rollover)* | 140,476 | **8,654 B** |
| **L1 `Profile 2` `pfUSDC` private pay / exit** (no public signer) | **137,860** (pay) · **138,724** (exit) | 140,476 (inner) | **8,654 B** |
| **Standalone signed deposit wire** (adds `5,261 B` ML-DSA-65 pubkey + sig) | 143,722 | 145,737 | **3,393 B** |
| **L1 archived deposit — `redb` key-value store** (rehearsal max body `144,397 B`, charged `145,140 B`) | 144,770–145,140 | **146,546** | **2,584 B** |
| **L1 archived deposit — `JSONL` file store** (adds JSONL envelope + digest filename) | 144,804 | **146,580** | **2,550 B** |

Notice the scope difference: ordinary private transfers and exits carry **`8.65 KB`** of margin, while worst-case archived signed deposits leave **`2.55–2.58 KB`** under the `149,130 B` archival cap (sized to keep chain archival growth at `~12 GiB/day` at `1 tx/s`). If future framing or signature updates need additional bytes, the two concrete levers are raising the archival cap or trimming Round-34 column openings (each dropped opening reclaims `~1.5 KB` at a cost of `~5.4` bits of pure-IOP soundness).

---

## 3. Security Foundations & Unresolved Proof Obligations

![PFSH02 conditional QROM security curves](/blog/pq-payments/pfsh02-qrom-security-curves.svg)
*Figure 3. Conditional QROM advantage bounds versus quantum query budget Q. Above Q = 2^81.28, 384-bit proof-tree collisions dominate over spot-check error; unpinned brand-new deposit accounts sit far lower (~2^-32 at Q = 2^64).*

![PFSH02 security dependency and blast-radius map](/blog/pq-payments/pfsh02-dependency-map.svg)
*Figure 4. Dependency and blast-radius map separating Value Conservation (Theorem 3), Authorization (Theorem 4), and Confidentiality (Theorem 5) by foundation type.*

Every theorem, hybrid game, and exact-rational calculation is published in the [Companion Mathematical Appendix](/research/pfsh02-proofs/) and [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/ec58522dcf66c85680242efa98b96d733d5b0c3e/docs/security/peel-binius-shielded-pq-payments.md). **Conditional bounds below are model-specific outputs of the unreviewed specification, not demonstrated end-to-end system security levels:**

| Security Property | Foundation Status (What Could Break It) | Conditional Model Bound (`math_bounds.json`) |
| --- | --- | --- |
| **Value Conservation & No Double Spend** (Theorem 3) | **Published + New Unreviewed.** Uses unmodified-oracle extraction only (no simulation, no Conj. A.4, no ZK): published [BCIKS20 Thm 6.2](https://eprint.iacr.org/2020/654) inside the proven Johnson bound (avoiding unproven beyond-Johnson proximity conjectures), plus new unreviewed greedy peeling (`Peel(M)`) and compressed-oracle QROM extraction (App. A.3) with 384-bit SHAKE256 collision/zero-preimage resistance. | Classical ROM: \(\lesssim 2^{-238}\) at \(Q=2^{64}\), \(\lesssim 2^{-192}\) at \(Q=2^{96}\).<br/>QROM (cond. on App. A.1–A.3): \(\lesssim 2^{-171}\) at \(Q=2^{64}\), \(\lesssim 2^{-138}\) at \(Q=2^{80}\), \(\lesssim 2^{-92}\) at \(Q=2^{96}\) (trivial at \(2^{126.75}\)). |
| **Spend Authorization & Non-Malleability** (Theorem 4, Modes 1–2) | **Unproven Conjecture + Non-Standard Assumptions.** Combines unreviewed QROM ZK (App. B, using published GHHM21 & AHU19) with **Conjecture A.4** (an unproven multi-proof simulation-extractability wrapper sketch) and non-standard SHAKE256 `JointPRF` / dummy `PRG` assumptions. | Conditional on resolving Conj. A.4 & SHAKE256 assumptions: ZK-dominated \(\lesssim 2^{-151}\) at \(Q=2^{64}\) across \(2^{32}\) proofs. **Not established today.** |
| **Deposit Authorization** (Theorem 4, Mode 3) | **Standard (Key-Pinned) / Weak (Unpinned).** `prepare_pq_account_debit` pins the depositor's full ML-DSA-65 public key in `account.public_key_hex` on first signed tx. | Key-pinned: reduces to ML-DSA-65 EUF-CMA + SHA-384 CR.<br/>Unpinned brand-new accounts: 160-bit address preimage \(\sim 2^{-32}\) at \(Q=2^{64}\), vacuous at \(Q=2^{80}\). |
| **Confidentiality & Recipient Anonymity** (Theorem 5) | **Single-Transaction Model + Non-Standard Assumptions.** 5-game hybrid (`H_0`–`H_5`, with `H_2` split into sub-hops `(i)–(v)` closing the GMP22 implicit-rejection scan asymmetry): App. B ZK + ML-KEM-1024 IND-CCA2 + HMAC-SHA-384 PRF + AES-256-GCM INT-CTXT/IND$-CPA + non-standard FIPS-203 ML-KEM `IK-CCA` & `IR-PRF` + non-standard SHAKE256 `JointPRF`, `PRG`, and `Hide`. | Parameterized by user count, scan queries, and primitive advantages (no single scalar bound; multi-transaction adaptive composition unmodeled). |

Isolating value conservation from Conjecture A.4 helps reviewers triage blast radius, **but conservation alone does not prevent theft**: if spend authorization fails, an attacker could steal existing shielded notes without inflating total supply. Resolving Conjecture A.4 (either with a peer-reviewed proof under accepted assumptions or via protocol redesign) is therefore the primary cryptographic blocker.

---

## 4. Benchmarks, Rehearsals & Test Results

All measurements below ran on 24 November 2026 on branch `feat/pq-payments-production-candidate` (`ec58522dc`) on a single shared 32-vCPU **AMD EPYC** KVM host (`PCLMULQDQ`, `AVX2`, `SHA-NI`). Standalone tests ran `n = 50` trials per fixture (`mint`, `hop1`, `hop2`) pinned to CPU 2. Inside-validator tests ran `n = 21` trials per condition across PFT and `pfUSDC`, valid and invalid batches, both warm and with explicit `128 MiB` L3 cache eviction (`cold=true`), against `1,024` history entries (`RAYON_NUM_THREADS=4` for parallel 4-proof blocks). These are single-host test-environment measurements, not universal hardware guarantees.

### 4.1 Verification & Proving Matrix (Internal Targets: `< 50 ms` Single-Tx, `< 200 ms` 4-Tx Parallel Block)

| Workload (Scope of Median Range) | Backend & Concurrency | Per-Condition Medians | p95 | Max | Target Status |
| --- | --- | ---: | ---: | ---: | --- |
| **Standalone Rust verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ`), 1 core | 20.35–20.43 ms | 20.99–26.45 ms | 33.81 ms *(20.21 full-tree)* | Met (`< 50 ms` max) |
| **Standalone Go verify** (`mint`/`hop1`/`hop2`, `n=50` each) | Accelerated (`PCLMULQDQ` ASM), 1 core | 30.82–31.11 ms | 31.18–31.99 ms | 32.45 ms *(31.26 full-tree)* | Met (`< 50 ms` max) |
| **Standalone Go portable** (`mint`/`hop1`/`hop2`, `n=50` each) | `-tags purego` (0 ASM), 1 core | 42.76–43.08 ms | 43.52–43.72 ms | **44.08 ms** | Met (`< 50 ms` max) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core pinned | 23.58–24.06 ms | 23.78–36.91 ms | 37.17 ms | Met (`< 50 ms` max) |
| **Inside-validator 1 action** (PFT & pfUSDC, warm/cold, `n=21`) | Portable (no `PCLMULQDQ`), 1 core | 36.96–39.64 ms | 38.70–44.45 ms | **45.23 ms** | Met (`< 50 ms` max) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Accelerated, 4-core parallel** | 49.82–69.75 ms | 73.26–87.64 ms | 102.10 ms | Met (`< 200 ms` max) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | **Portable, 4-core parallel** | 78.76–85.05 ms | 88.14–99.01 ms | **108.44 ms** | Met (`< 200 ms` max) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Accelerated, 1 core sequential | 92.94–102.20 ms | 93.89–104.08 ms | 107.53 ms | Met (`< 200 ms` max) |
| **Inside-validator 4 actions** (PFT & pfUSDC, warm/cold, `n=21`) | Portable, 1 core sequential | 145.43–161.96 ms | 147.20–201.97 ms | 180.30 ms valid *(207.96 invalid)* | Valid met; invalid burst `> 200 ms` *(4-core max `108.4 ms`)* |
| **Rust client proving** (`mint`/`hop1`/`hop2`, `n=50`, `~550 MiB` RSS) | 16 thr / 1 core | 2.64 s / 24.61–24.71 s | 26.29–27.24 s (1c) | 27.68 s (1c) | Measured (EPYC desktop/server; browser/mobile untested) |

Every single-transaction verifier—accelerated and portable, standalone and inside-validator, warm and `128 MiB` cold-cache—stays under `45.3 ms` max, and parallel 4-proof block validation stays under `108.5 ms` max on both backends. Desktop/server proving at `2.64 s` (16 threads) does not yet establish practicality in browser WASM or low-end mobile devices; client-device benchmarks remain open.

### 4.2 Consolidated Test, Replay & Rehearsal Suites

*(Terminology: **M8** is the six-validator activation/pause/restart rehearsal; **R64** is a captured 1,734-block live-devnet archive used to verify zero replay drift while PQ payments are inactive.)*

| Suite | Result (24 Nov 2026, Branch `feat/pq-payments-production-candidate`) |
| --- | --- |
| **Full `postfiat-node --lib` suite** | **750 passed, 0 failed** (`45` pre-existing `#[ignore]` opt-in external-bridge, Solana-exit, Base-Sepolia, Anvil, and legacy-disk tests; **0 PQ tests ignored**) |
| **Six-validator activation rehearsal (`M8`, `pq_payment_rehearsal_tests`)** | **Passed** in `60.26 s` (`worst_uncached_verify_l1_ms = 22.443 ms`, 4-proof block `578,304 B`, pause at height 29, cold restart & signed snapshot import) |
| **7-stage standalone driver (`verify.sh`)** | **7/7 passed** (Rust + Go PCLMUL + Go purego + 35 named attacks + 150 fuzz mutations + full \(2^{24}\)-leaf rollover + ML-KEM scan + `check_math.py` + Z3 5.4.1) |
| **Library & wallet crates** | `postfiat-privacy-binius` (`9/9` accel, `9/9` portable), `postfiat-privacy-binius-wallet` (`8/8`), `postfiat-storage` PQ archive (`1/1`), Python CLI (`9/9`) |
| **Historical live-devnet replays** | 1,734-block `R64` paired archive replay (`c28eb872...5910`, exact 1B PFT supply) + 1,754-block devnet replay (`246d6113...4b8e6`) |
| **Un-upgraded validator upgrade check** | Pre-activation validator build halts fail-closed on the scheduling amendment (`unsupported governance amendment kind`) rather than forking |

*Scope of automated checks:* `check_math.py` validates exact rational arithmetic of the spec's formulas (not proof derivations); Z3 `5.4.1` proves the 66-bit conservation adder, 2-bit Merkle mux, and dummy-input gating (not full-circuit SHAKE256 wiring); and Rust, Go, and Python share one author team, so cross-language parity is a regression check rather than independent verification.

---

## 5. Evidence Artifacts & Three Gates to Live Activation

| Artifact | Scope | Direct Link |
| --- | --- | --- |
| **Companion Mathematical Proofs & 18 Reviewer Questions** | Symbol glossary, Lemmas 1–4, App. A.3, Conj. A.4, App. B, Theorems 3–5 | [`/research/pfsh02-proofs/`](/research/pfsh02-proofs/) |
| **Consolidated Evidence Packet (JSON)** | Commit `ec58522dc`, all test counts, 50-trial standalone & 21-trial validator tables, replay digests | [`pq-private-payments-evidence-packet-20261124.json`](/evidence/pq-private-payments/pq-private-payments-evidence-packet-20261124.json) |
| **External Cryptographic Review Package** | Source inventory, payment trace & 9 reviewer scopes | [`external-review-package.md`](/evidence/pq-private-payments/external-review-package.md) |
| **Six-Validator Rehearsal Record** | `R64` 1,734-block replay, validator receipts & fail-closed halt log | [`rehearsal-record.md`](/evidence/pq-private-payments/rehearsal-record.md) |
| **Exact-Rational Math & Z3 Outputs** | `math_bounds.json` & `circuit_equivalence.json` | [`math_bounds.json`](/evidence/pq-private-payments/math_bounds.json) · [`circuit_equivalence.json`](/evidence/pq-private-payments/circuit_equivalence.json) |
| **SHA-256 Fixture Manifest** | 36-file checksums (`SHA256SUMS`) | [`SHA256SUMS-consolidated.txt`](/evidence/pq-private-payments/SHA256SUMS-consolidated.txt) |

### Reproduce Locally

```bash
git clone https://github.com/postfiatorg/postfiatl1v2.git
cd postfiatl1v2
git checkout ec58522dcf66c85680242efa98b96d733d5b0c3e   # branch feat/pq-payments-production-candidate

# 1. Verify 36 fixture/script checksums & run the 7-stage standalone suite
cd tools/pft-binius-shielded-pq
sha256sum -c SHA256SUMS
./verify.sh

# 2. Run the postfiat-node library suite (750 tests) and 6-validator M8 rehearsal
cd ../..
cargo test --release --locked -p postfiat-node --lib
cargo test --release --locked -p postfiat-node --bin postfiat-node -- pq_payment_rehearsal_tests --nocapture --test-threads=1
```

### Three Gates Before Mainnet Activation (With Acceptance Criteria)

No target activation date is set; PFSH02 remains disabled on mainnet until all three gates close:

1. **Independent cryptographic resolution and code audit:** External cryptographers must review Theorems 1A, 1B, 2A, Theorem 5, and the Rust/Go/L1 code, **and** resolve Conjecture A.4—either via a reviewed proof under explicitly accepted assumptions or via protocol redesign—alongside an accepted multi-transaction confidentiality composition scope.
2. **Production-genesis cut and scale validation:** Replace the disposable rehearsal genesis/series lock (`pq_rehearsal_domain`) with mainnet genesis and the live `pfUSDC` series; implement and benchmark bounded-time node restart and index checkpointing at multi-million-note (`2^24`-leaf) scale (cold restart currently walks historical pair pages); and qualify real browser-WASM/mobile proving and network-load throughput.
3. **Validator upgrade, governance vote, and Orchard migration plan:** After all validators install the audited production release, ratify a BFT-supermajority governance amendment choosing live activation height \(H\), accompanied by user-facing migration tooling and privacy guidance for moving balances out of the legacy Orchard pool.

---

*Open-source code: [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2) (branch `feat/pq-payments-production-candidate`, commit `ec58522dc`). External reviewers can start from the [Companion Mathematical Appendix](/research/pfsh02-proofs/) and the [External Review Package](/evidence/pq-private-payments/external-review-package.md).*
