---
title: "PFSH03 Mathematical Arguments, Lean 4 Formalization & External Reviewer Appendix"
date: 2026-11-24T00:00:00Z
url: "/research/pfsh03-proofs/"
aliases:
  - /research/pfsh02-proofs/
summary: "Companion formal appendix to the Peel-Binius-Shielded (PFSH03) engineering report: ~126-bit QROM security target, symbol glossary, 9-module Lean 4 suite (2,847 LOC, 0 sorrys), 3xSHA-512 QRO reduction, Lemmas 1–4 (Peel(M) + BCIKS20), 34-round RBR-KS table, unmodified-oracle QROM extraction (Theorem 2A), PFSH03 external ML-DSA-65 Spend Authorization (Theorem 4-PFSH03), multi-transaction adaptive confidentiality (Theorem 5-PFSH03), Spec-to-Code Traceability Matrix, and 18 prioritized external-reviewer questions."
author: "Post Fiat"
math: true
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - PFSH03
  - Binius
  - QROM
  - Proofs
  - Privacy
  - ML-DSA-65
copyMarkdownHref: "/research/pfsh03-proofs/index.md"
copyMarkdownButton: "Copy for LLM"
draft: false
---

*Companion formal appendix to [PFSH03: Experimental Curve-Free Private Payments for Post Fiat L1](/blog/peel-binius-quantum-safe-private-payments/). Pinned specification source: [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/be1f778779450db1bf3a61f281da14d423a295c3/docs/security/peel-binius-shielded-pq-payments.md) (including Appendix D) and Lean 4 formalization [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/be1f778779450db1bf3a61f281da14d423a295c3/formal/lean) on branch `feat/pq-payments-production-candidate` (`be1f77877`).*

**Headline concrete security target (conditional, unreviewed):** Conditional on unmodified-oracle Theorem 2A (App. A.1–A.3), FIPS-204 ML-DSA-65 (NIST Level 3), and 384-bit SHAKE256/SHA-384 collision resistance, the PFSH03 soundness upper bound becomes vacuous at \(Q = 2^{126.75}\) quantum oracle queries (`~126-bit` QROM model target, governed by 384-bit proof-tree collisions, with error \(< 2^{-137.55}\) at \(Q = 2^{80}\) and \(< 2^{-92.25}\) at \(Q = 2^{96}\)). This marks where the conditional proof bound reaches `1`, not an independently audited security guarantee or demonstrated attack cost. The sole sub-126-bit exception is an unpinned brand-new public L1 deposit account (`~80-bit` quantum address preimage until its first key-pinning transaction; strict pre-debit enforcement is available via `prepare_pq_account_debit_pinned`).

**Review & Lean 4 formalization boundary:** Nine Lean 4 (`v4.20.0`) + Mathlib modules (`2,847` LOC, zero `sorry`s, zero custom axioms—`[propext, Classical.choice, Quot.sound]` only) kernel-check parameter arithmetic, wire margins, greedy peeling telescoping, rank-3 operator-norm bounds, the zero-query-blowup 3-block `SHA-512` → 1,536-bit QRO simulation, supply conservation induction, and reduction accounting from explicit hypotheses. **What Lean does NOT prove:** published proximity-gap theorems (BCIKS20 Thm 6.2), the full compressed-oracle QROM extraction proof (App. A.3), the GHHM21/AHU19 ZK bridges (App. B), real-world primitive assumptions (`IK-CCA`, `IR-PRF`, `Hide`, dummy `PRG`, SHA-512/SHA-384 separation), and correspondence to compiled Rust/Go binaries enter as explicit hypotheses or lie outside Lean and require independent external audit.

## 0. Lean 4 Formal Proof Suite (`formal/lean/`, 2,847 LOC)

| Module | Spec Target | Key Kernel-Verified Theorems (0 `sorry`s, 0 custom axioms) |
| --- | --- | --- |
| `PFSH02/Params.lean` | `check_math.py`, PFSH03 Wire Caps | `L_max_exact` (`⌊√(2/ρ)⌋ = 86`), `johnson_margin_m3`, `coeff_3652_upper`, `pfsh03_wire_margins_exact` (`160,000 B` cap), `conservation_66bit_no_overflow`, `p34_lt_inv_2_302`, `eps_curve_sq_lt_inv_2_610`, `theorem2A_Q64/Q80/Q96` |
| `PFSH02/Peel.lean` | App. A.1, Lemma 1 (`Peel(M)`) | `step_sqrt_decrease`, `peel_sqrt_telescoping`, `pfsh02_peel_list_bound` (`k ≤ 86`), `peel_case1_agreement_strict`, `peel_case2_bciks_hypotheses`, `peel_case2_curve_monotone` |
| `PFSH02/DualBinding.lean` | App. A.1, Lemmas 2, 3 & 4 | `lemma2_bad_pt_union_bound`, `lemma2_dual_binding`, `lemma3_subfield_inheritance` (Lagrange `K_32` inheritance), `lemma4_gamma_soundness`, `lemma4_rho_rs_soundness` |
| `PFSH02/Rank3Op.lean` | App. A.3, Lemma A.3.0 & A.3.4(b) | `opO_rank3_identity`, `opO_symmetric`, `entry_norm_bound` (`≤ √(8p)`), `exit_norm_bound` (`≤ √(8p)`), `readout_error_exact` (`2/N − 1/N² < 2/N`) |
| `PFSH02/CompressedOracle.lean` | App. A.3, App. D.2 & Thm 2A | `three_block_sha512_qro_reduction` (`[propext]` only: zero-query-blowup 3-block `SHA-512` → 1,536-bit QRO), `blockDiag_norm_le`, `pointwise_both_directions_bound`, `lemmaA31_tree_invariance`, `sum_sqrt_le_two_thirds`, `amplitude_telescoping`, `theorem2A_telescoped_bound` |
| `PFSH02/ZeroKnowledge.lean` | §3.4 & App. B (Lemmas 1.1–1.2, Thm 1B) | `lemma11_unopened_leaf_bijection` (`5,216` bits), `one_sub_pow_le_exp`, `lemma12_pow_tv_bound` (`TV < 2^-182`), `sim_iop_bijections`, `theorem1B_Q96_bound` |
| `PFSH02/ValueConservation.lean` | §4.1, Theorem 3 (3a & 3b) | `genesis_invariant`, `step_preserves_invariant`, `theorem3a_shielded_conservation`, `theorem3b_joint_conservation_burned`, `theorem3b_joint_conservation_credited` |
| `PFSH02/ConjectureA4.lean` | Legacy PFSH02 App. A.4 *(retired in PFSH03)* | Retained for historical audit only; **no PFSH03 theorem imports or depends on `ConjectureA4.lean`** |
| `PFSH02/AuthAndPrivacy.lean` | §§4.2–4.3, Thm 4-PFSH03 & Thm 5-PFSH03 | `pfsh03_spend_auth_dichotomy`, `pfsh03_theorem4_zero_appA4` (**zero App. A.4 / ZK / `JointPRF`**), `mode3_key_pinned_eliminates_160bit`, `pfsh03_theorem5_multitx_hybrid` (`q_c`-tx adaptive hybrid) |

---

## 1. Symbol & Parameter Glossary

| Symbol | Definition & Pinned Value |
| --- | --- |
| \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset E\) | Binary tower: \(K_{16} = \mathbb{F}_2[x]/(x^{16}+x^5+x^3+x+1)\), \(K_{32} = K_{16}[Z]/(Z^2+Z+x^{11})\), \(E = K_{32}[Y]/(Y^{12}+Y^3+Y+(Z+x)) \cong \mathbb{F}_{2^{384}}\). |
| \(H, L \subset K_{32}\) | Disjoint \(\mathbb{F}_2\)-affine subspaces: interpolation domain \(H = V_9 = \{0,\dots,511\}\) (\(|H|=512\)); evaluation coset \(L = \texttt{0x00200000} + V_{21}\) (\(|L| = n = 2^{21} = 2,097,152\)). |
| \(D, \rho, L_{\max}\) | Reed–Solomon degree bound \(D = 565\); code rate \(\rho = D/n = 565/2^{21} \approx 0.000269413\); Johnson parameter \(m' = 3\); greedy peeling list bound \(L_{\max} = \lfloor\sqrt{2/\rho}\rfloor = 86\). |
| `pk_dsa`, `pk_hash`, `r_pk`, \(A\), \(\mathrm{SN}\) | **PFSH03 key hierarchy:** per-note ML-DSA-65 keypair \((\mathrm{pk}_{\mathrm{dsa}}, \mathrm{sk}_{\mathrm{dsa}})\) (`1,952 B` pk), \(\mathrm{pk\_hash} = \mathrm{SHAKE256}(\texttt{0x04} \parallel \mathrm{pk}_{\mathrm{dsa}})\) (`48 B`), independent 48 B nullifier secret \(r_{\mathrm{pk}}\), note address \(A = \mathrm{SHAKE256}(\texttt{0x00} \parallel \mathrm{pk\_hash} \parallel r_{\mathrm{pk}})\) (`97 B ≤ 135 B`, 1 Keccak permutation), and nullifier \(\mathrm{SN} = \mathrm{SHAKE256}(\texttt{0x02} \parallel r_{\mathrm{pk}} \parallel \mathrm{Coin})\). |
| `raw_tx_ctx`, `spend_msg` | `raw_tx_ctx = SHA-384("PFT-SH-TXCTX-V3" || inner[..7548])` (commits to outputs, envelopes, amounts, anchor, nullifiers, and both `pk_in0/1`); slot `b ∈ {0,1}` signs `SHA-384("PFT-SH-SPEND-AUTH-V3" || [b] || pk_hash_b || statement_ctx)` under FIPS-204 context `"postfiat-l1-v2/tx/v1"`. |
| \(B_0,\dots,B_4; N_C\) | Five witness bit-arrays in \(\mathbb{F}_2^{2^{19}}\) (447,014 active rows; 140 active packed \(K_{32}\) witness rows); total scalar constraints \(N_C = 2,192,844\) (Groups A, B, C). |
| \(MT_1, M, B_{\mathrm{pcs}}, B_{\mathrm{prox}}\) | Height-21 Merkle tree over \(L\) (48 B digests) committing to 163 \(K_{32}\)-rows (140 witness + 5 ring-switch mask + 2 sumcheck-1 mask + 16 sumcheck-2 mask rows, each with 53 randomizers vanishing on \(H\)) plus 2 uniform degree-\(<565\) \(E\)-blinding polynomials \(B_{\mathrm{pcs}}, B_{\mathrm{prox}}\). |
| \(H: X \to Y = \{0,1\}^{1536}\) | Single fixed-range compiler oracle instantiated by counter-mode \(3\times\mathrm{SHA\text{-}512}\): \(H(x) = \mathrm{SHA\text{-}512}(\texttt{0x00}\parallel x) \parallel \mathrm{SHA\text{-}512}(\texttt{0x01}\parallel x) \parallel \mathrm{SHA\text{-}512}(\texttt{0x02}\parallel x)\) with fixed-length prefix-free domain tags; verifier query budget \(\kappa_v = 68 + 52 + 843 = 963\) per proof. |
| \(t, w_{\mathrm{pow}}, M_{\mathrm{pow}}\) | Round-34 column openings \(t = 52\); PoW difficulty \(w_{\mathrm{pow}} = 20\) bits; hard prover nonce cap \(M_{\mathrm{pow}} = 2^{27} = 128 \cdot 2^{20}\). |
| \(\mathcal{R}_{\mathrm{pay}}^{\mathrm{PFSH03}}(x)\) | NP payment relation: two real/dummy inputs binding public `pk_hash0`, `pk_hash1` to \(A_b = H_A(\mathrm{pk\_hash}_b, r_{\mathrm{pk},b})\) and \(\mathrm{SN}_b = H_{\mathrm{SN}}(r_{\mathrm{pk},b}, \mathrm{Coin}_b)\) under Depth-24 SHAKE256 Merkle roots, two output commitments, and exact 66-bit conservation \(v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + \mathrm{pub\_exit}\) in \(\mathbb{Z}\) with \(\mathrm{pub\_exit} = \mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\). |

---

## 2. Theorem 1A & Appendix A.1–A.2: 34-Round IOP Knowledge Soundness `[Unreviewed]`

PFSH03 preserves the exact 34-round Peel-Binius IOP of PFSH02 (zero added permutations or constraints; `pk_hash0/1` occupy bytes `49..96` of Keccak permutations `p = 0, 3` as public `Const` circuit inputs).

### 2.1 Imported Published Anchor — BCIKS20 Theorem 6.2

*(Ben-Sasson, Carmon, Ishai, Kopparty, Saraf, FOCS 2020 / JACM 2023, Correlated Agreement for Parameterized Curves up to the Johnson Bound.)*

Let \(\mathbb{F}_q\) be a finite field, \(D_{\mathrm{eval}} \subset \mathbb{F}_q\) any nonempty domain of size \(n' = |D_{\mathrm{eval}}|\), \(V = \mathrm{RS}[\mathbb{F}_q, D_{\mathrm{eval}}, \rho']\) of dimension \(k' = \rho' n'\), \(u_0, \dots, u_\ell : D_{\mathrm{eval}} \to \mathbb{F}_q\), integer \(m' \ge 3\), and proximity parameter \(0 < \delta' \le 1 - \bigl(1 + \frac{1}{2m'}\bigr)\sqrt{\rho'}\). If

$$\Pr_{z \leftarrow \mathbb{F}_q}\!\left[\Delta_{D_{\mathrm{eval}}}\!\left(u_0 + z u_1 + \dots + z^\ell u_\ell,\, V\right) \le \delta'\right] > \ell \cdot \frac{(m' + \tfrac{1}{2})^7}{3(\rho')^{3/2}} \cdot \frac{(n')^2}{q},$$

then there exist codewords \(v_0, \dots, v_\ell \in V\) and a set \(S \subset D_{\mathrm{eval}}\) of size \(|S| \ge (1 - \delta')n'\) such that \(u_i(x) = v_i(x)\) for all \(x \in S\) and all \(i \in \{0, \dots, \ell\}\).

### 2.2 Lemma 1 (`Peel(M)` List Size & Exact 4-Line Telescoping for All \(n' \ge 0\))

Fix any (possibly partial) Round-1 oracle \(M: L \to (K_{32}^{163}\times E^2)\cup\{\bot\}\). Initialize \(L_0 := \mathrm{supp}(M)\) (\(n_0 := |L_0| \le n\)), \(\mathcal{P} := \emptyset\), \(i := 0\). While \(|L_i| > 2D\) and there exists \(u \in \mathrm{RS}[E, L, D]^{165}\) whose remaining agreement set \(D^{(i)}(u) := \{x \in L_i : M(x) = u(x)\}\) satisfies \(|D^{(i)}(u)| \ge \sqrt{2 D |L_i|}\), add the lexicographically first such \(u_{i+1}\) to \(\mathcal{P}\) and set \(L_{i+1} := L_i \setminus D^{(i)}(u_{i+1})\). Halt with \(\mathcal{P}(M) := \mathcal{P}\) (size \(k\)) and \(L_{\mathrm{rem}} := L_k\) (size \(n' := |L_{\mathrm{rem}}|\)).

**Proof of (i) \(k \le 86\):** Set \(x_i := |L_i|\). Whenever \(x_i > 2D\), \(d_i := x_i - x_{i+1} \ge \sqrt{2 D x_i} > 2D > 0\), so \(x_{i+1} < x_i\) and \(\sqrt{x_i} + \sqrt{x_{i+1}} < 2\sqrt{x_i}\). Therefore:

$$\sqrt{x_i} - \sqrt{x_{i+1}} = \frac{d_i}{\sqrt{x_i} + \sqrt{x_{i+1}}} > \frac{\sqrt{2 D x_i}}{2\sqrt{x_i}} = \sqrt{\frac{D}{2}}.$$

Summing over \(i = 0,\dots,k-1\) gives \(\sqrt{n_0} - \sqrt{n'} \ge k\sqrt{D/2}\) (strict when \(k \ge 1\)), hence for all \(k \ge 0, n' \ge 0\):

$$kD \le \sqrt{2D}\bigl(\sqrt{n_0} - \sqrt{n'}\bigr) \implies k \le \left\lfloor \sqrt{\frac{2 n_0}{D}} \right\rfloor \le \left\lfloor \sqrt{\frac{2}{\rho}} \right\rfloor = 86.$$

**Proof of (ii) Proximity curve bound \(\Pr_{\lambda_p}[\mathrm{Bad}_{\mathrm{peel}}(\lambda_p)] \le 2^{-305.79}\):** For \(\lambda_p \in E\), define \(F_{\lambda_p}(M)(x) := B_{\mathrm{prox}}(x) + \lambda_p B_{\mathrm{pcs}}(x) + \sum_{r=0}^{162} \lambda_p^{r+2} M_r(x)\). Partitioning \(n' \ge 0\) into Case 1 (\(0 \le n' \le 2D\), where \(\Pr[\mathrm{Bad}_{\mathrm{peel}}] = 0\)) and Case 2 (\(n' > 2D\), where every verbatim hypothesis of BCIKS20 Theorem 6.2 holds on \(D_{\mathrm{eval}} := L_{\mathrm{rem}}\) with \(\rho' = D/n' < 1/2\), \(m' = 3\), and \(\delta' = 1 - \sqrt{2\rho'} < 1 - \tfrac{7}{6}\sqrt{\rho'}\)) yields:

$$\Pr_{\lambda_p}[\mathrm{Bad}_{\mathrm{peel}}(\lambda_p)] \le 164 \cdot \frac{(3.5)^7}{3\rho^{3/2}} \cdot \frac{n^2}{2^{384}} = 2^{-305.79}. \quad \blacksquare$$

### 2.3 Lemmas 2–4 & 34-Round RBR-KS Table

- **Lemma 2 (Dual-Polynomial Binding):** \(\Pr[\mathrm{Bad}_{\mathrm{pt}}(\lambda_p)] \le 86 \cdot 2^{21} \cdot 164 / 2^{384} = 2^{-349.22}\). Conditioned on \(\neg\mathrm{Bad}_{\mathrm{peel}} \land \neg\mathrm{Bad}_{\mathrm{pt}}\), any \((v_{\mathrm{prox}}, v_{\mathrm{open}})\) with \(|A_{\mathrm{both}}| \ge \sqrt{2\rho}\,n \approx 48,680 > D = 565\) pins a unique \(u \in \mathcal{P}(M)\). \(\blacksquare\)
- **Lemma 3 (Subfield-\(K_{32}\) Structural Booleanity):** Every peeled slice agrees on \(\ge 2D > D\) points in \(L \subset K_{32}\), forcing \(u_r \in K_{32}[X]_{<D}\) by Lagrange interpolation and unpacking into 32 \(\mathbb{F}_2\) witness bits with no quadratic \(b(1-b)=0\) gates. \(\blacksquare\)
- **Lemma 4 (Single-Challenge Ring-Switching):** Any Round-23 discrepancy vanishes with probability \(\le 4/|E|\) over \(\gamma\); any Round-24 discrepancy (including any mismatch in \(S_{G_1}\)) yields a nonzero univariate polynomial of degree \(\le 386\) in \(\rho_{\mathrm{rs}}\), vanishing with probability \(\le 386/|E|\). \(\blacksquare\)

| Round(s) | Atomic Challenge | Pure IOP RBR-KS Bound \(\varepsilon_{\mathrm{rbr}}(k)\) |
| --- | --- | --- |
| Round 1 | \(MT_1\) oracle \(M\), \(S_{G_1}\), \(S_{\mathrm{mask2}}\) | \(\mathrm{State}_{\mathrm{KS}}(x, \mathrm{tr}_1) := 0\) |
| Round 2 (`C02`) | Single \(\alpha \in E\) (degree \(N_C - 1 = 2,192,843\)) | \(\le 86 \cdot 2,192,843 / 2^{384} = 2^{-356.51}\) |
| Rounds 3–21 (`C03`–`C21`) | 19 Sumcheck-1 rounds (degree \(\le 3\)) | \(\le 86 \cdot 3 / 2^{384} = 2^{-375.99}\) each |
| Round 22 (`C22`) | Degree-2 evaluation hiding \(\tau \in E\) (degree \(\le 2\)) | \(\le 86 \cdot 2 / 2^{384} = 2^{-376.57}\) |
| Round 23 (`C23`) | Ring-Switch batch \(\gamma \in E\) (degree \(\le 4\)) | \(\le 86 \cdot 4 / 2^{384} = 2^{-375.57}\) |
| Round 24 (`C24`) | Ring-Switch linearization \(\rho_{\mathrm{rs}} \in E\) (degree \(\le 386\)) | \(\le 86 \cdot 386 / 2^{384} = 2^{-368.98}\) |
| Rounds 25–32 (`C25`–`C32`) | 8 Sumcheck-2 rounds over 256 virtual rows (degree \(\le 2\)) | \(\le 86 \cdot 2 / 2^{384} = 2^{-376.57}\) each |
| Round 33a (`C33P`) | \(\lambda_p \in E\): `Peel(M)` + BCIKS20 (`2^-305.79`) + pointwise (`2^-349.22`) | \(\le 2^{-305.79}\) |
| Round 33b (`C33O`) | \(\lambda_o \in E\): inner-product batching | \(\le 86 / 2^{384} = 2^{-377.57}\) |
| Round 34 (pure IOP) | \(t = 52\) uniform column queries (no PoW) | \(\le (\sqrt{2\rho})^{52} = 2^{-282.31}\) |
| **Round 34 (compiled + 20-bit PoW)** | Atomic `H_C4` marking (Lemma A.3.3) | **\(p_{34} = 2^{-20}(\sqrt{2\rho})^{52} = 2^{-302.31}\)** |

---

## 3. Theorem 2A, `3 × SHA-512` QRO Reduction & Appendix A.3 `[Unreviewed]`

### 3.1 Zero-Query-Blowup 3-Block Counter-Mode `SHA-512` → 1,536-Bit QRO Reduction (`App. D.2`)

The compiler oracle \(H(x) = \mathrm{SHA\text{-}512}(\texttt{0x00}\parallel x) \parallel \mathrm{SHA\text{-}512}(\texttt{0x01}\parallel x) \parallel \mathrm{SHA\text{-}512}(\texttt{0x02}\parallel x)\) uses distinct leading counter bytes (`0x00`, `0x01`, `0x02`) and fixed-length inputs per 8-byte ASCII domain tag (`PFS-LEAF` `761 B`, `PFS-NODE` `110 B`, `PFS-STMT` `561 B` with constant `408 B` `encode_statement`, `PFS-ABS ` fixed per sub-tag, `PFS-CH  ` fixed per sub-tag, `PFS-C4  ` `121 B`). Because inputs are prefix-free across tags and messages (ruling out Merkle–Damgård length extension), any \(Q\)-query quantum adversary \(\mathcal{A}^h\) given direct independent access to the 512-bit counter-slice oracle \((b, x) \mapsto h(b \parallel x)\) is simulated with **at most \(Q\) queries (zero query blowup)** against the atomic 1,536-bit tuple oracle \(H(x) = (h(0\parallel x), h(1\parallel x), h(2\parallel x))\) by projecting slice \(b \in \{0, 1, 2\}\) per query. This equivalence is kernel-verified in `three_block_sha512_qro_reduction` (`formal/lean/PFSH02/CompressedOracle.lean`, `#print axioms` → `[propext]` only). The remaining cryptographic idealization—modeling fixed-length domain-separated `SHA-512` as a 512-bit QRO alongside `SHA-384` (same compression function, different IV)—stays flagged for external review (Question #7).

### 3.2 Single-Oracle QROM Extraction (`Theorem 2A / App. A.3`)

In Zhandry's compressed-oracle representation over \(H: X \to Y = \{0,1\}^{1536}\) (\(N = 2^{1536}\)), the query unitary \(O_{x,z}\) for \(z \ne 0\) satisfies the exact self-adjoint rank-3 identity (`Rank3Op.lean`):

$$O_{x,z} = Z_z + (|\psi_z\rangle - |\bot\rangle)\langle\bot| + (|\phi\rangle - |\psi_z\rangle)\langle\phi| + (|\bot\rangle - |\phi\rangle)\langle\psi_z|, \qquad \|P_S O_{x,z} P_{\neg S}\|_2 = \|P_{\neg S} O_{x,z} P_S\|_2 \le \sqrt{8p} < \sqrt{10p}.$$

Combining tree-invariance (Lemma A.3.1), both-directions transition capacity (Lemmas A.3.2–A.3.3), telescoping over \(Q_v = Q + L\kappa_v\) queries, and readout error \(2/N - 1/N^2 < 2/2^{384}\) (Lemma A.3.4) yields Theorem 2A (`CompressedOracle.lean`):

$$\varepsilon_{\mathrm{Ext}}(Q, L) \le \left(3.652\, Q_v^{3/2} 2^{-192} + Q_v\sqrt{10\cdot\max(\varepsilon_{\mathrm{rbr}}(33a) + 2 Q_v 2^{-512},\; p_{34})}\right)^2 + \frac{2 L \kappa_v}{2^{384}}. \quad \blacksquare$$

At \(L = 1\): \(\varepsilon_{\mathrm{Ext}}(2^{64}, 1) \le 2^{-170.98}\), \(\varepsilon_{\mathrm{Ext}}(2^{80}, 1) \le 2^{-137.55}\), \(\varepsilon_{\mathrm{Ext}}(2^{96}, 1) \le 2^{-92.25}\) (kernel-checked in `Params.lean`), and the bound reaches trivial probability \(1\) at \(Q_{\mathrm{break}} = 2^{126.75}\) (`~126-bit` QROM soundness target, governed by 384-bit proof-tree collisions above \(Q = 2^{81.28}\)).

---

## 4. Theorem 4-PFSH03: External ML-DSA-65 Spend Authorization (Zero Appendix A.4)

**Why PFSH02 needed Appendix A.4—and how PFSH03 eliminates it completely:**  
In PFSH02, spending a private note proved knowledge of secret \(S\) *only inside the Binius proof*. That forced the spend-authorization reduction to *simulate* honest users' proofs without knowing \(S\), which in turn required an unreviewed adaptive multi-proof QROM simulation-extractability bridge (Appendix A.4 / Conjecture 2B) plus non-standard SHAKE256 `JointPRF`/`PRG`.

In **PFSH03**, every note owner address is:
$$A = \mathrm{SHAKE256}\bigl(\texttt{0x00} \parallel \underbrace{\mathrm{SHAKE256}(\texttt{0x04} \parallel \mathrm{pk}_{\mathrm{dsa}})}_{\mathrm{pk\_hash}\,(48\text{ B})} \parallel r_{\mathrm{pk}}\,(48\text{ B})\bigr).$$

Every transaction carries `pk_in0`, `pk_in1` (`1,952 B` each) and `sig_in0`, `sig_in1` (`3,309 B` each) verified **before** Binius against `SHA-384("PFT-SH-SPEND-AUTH-V3" || [slot] || pk_hash_slot || statement_ctx)`. Inside the Binius proof, `pk_hash0` and `pk_hash1` are **public statement inputs** wired directly into `p = 0, 3`.

**Reduction (`pfsh03_spend_auth_dichotomy` & `pfsh03_theorem4_zero_appA4` in `AuthAndPrivacy.lean`):**  
Given an ML-DSA-65 EUF-CMA challenger holding only \(\mathrm{sk}_{\mathrm{dsa}}^*\) for a target honest note \((\mathrm{Coin}^*, A^*)\), the reduction generates \(r_{\mathrm{pk}}^*\) itself! Whenever the adversary requests honest spends (even of the target note, or any other honest note), the reduction runs the **real, unmodified Binius prover** (using its own known \(r_{\mathrm{pk}}^*\)) and answers the external spend signature via a single standard FIPS-204 ML-DSA-65 signing query. When the adversary outputs any accepted unauthorized spend or hijacked transaction \(tx^*\) (`statement_ctx^*` never signed for target slot):

1. Fold the adversary and all honest provers into one unmodified-oracle algorithm and run **Theorem 2A** (exact same extractor as Theorem 3—**zero simulation, zero Appendix A.4, zero QROM ZK, zero `JointPRF`/`PRG`**).
2. Extracted witness proves `Coin*` is authentic (up to `H_Node` / `H_Coin` CR) and satisfies \(H_A(\mathrm{pk\_hash}_{\mathrm{slot}}^*, r_{\mathrm{pk}}^*) = A^* = H_A(\mathrm{pk\_hash}^*, r_{\mathrm{pk,hon}}^*)\).
3. **Dichotomy (`pfsh03_spend_auth_dichotomy`):**
   - If \(\mathrm{pk}_{\mathrm{in}}^* \ne \mathrm{pk}_{\mathrm{dsa}}^*\), either \(\mathrm{pk\_hash}_{\mathrm{slot}}^* = \mathrm{pk\_hash}^*\) (direct 384-bit \(H_{\mathrm{pk}}\) collision) or \(\mathrm{pk\_hash}_{\mathrm{slot}}^* \ne \mathrm{pk\_hash}^*\) (direct 384-bit \(H_A\) collision).
   - If \(\mathrm{pk}_{\mathrm{in}}^* = \mathrm{pk}_{\mathrm{dsa}}^*\), the verifier accepted `sig_in*` under \(\mathrm{pk}_{\mathrm{dsa}}^*\) on `spend_msg*`. Either `spend_msg*` collides with a previously signed message (direct 384-bit SHA-384 collision) or it is fresh (direct **FIPS-204 ML-DSA-65 EUF-CMA forgery**).

Summing across \(q_k\) honest note keys gives the exact kernel-checked PFSH03 bound:

$$\mathrm{Adv}_{\mathrm{Auth}}^{\mathrm{PFSH03}}(\mathcal{A}) \le \varepsilon_{\mathrm{Ext}}(Q_{\mathrm{tot}}, q_{\mathrm{tx}}) + q_k\,\mathrm{Adv}_{\mathrm{EUF\text{-}CMA}}^{\mathrm{ML\text{-}DSA\text{-}65}} + \mathrm{Adv}_{\mathrm{CR}}^{H_A} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{pk}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Coin}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Node}}} + \mathrm{Adv}_{\mathrm{CR}}^{\mathrm{SHA\text{-}384}} + \mathrm{Adv}_{\mathrm{ZeroPre}}^{H_{\mathrm{Coin}}}. \quad \blacksquare$$

*(Mode 3 deposit authorization likewise pins the depositor's full 1,952-byte ML-DSA-65 public key in `account.public_key_hex` on its first signed transaction (`mode3_key_pinned_eliminates_160bit`), reducing directly to ML-DSA-65 EUF-CMA + SHA-384 CR; strict pre-debit enforcement is available via `prepare_pq_account_debit_pinned`, while unpinned brand-new accounts incur the `~80-bit` quantum address preimage risk.)*

---

## 5. Theorem 1B (QROM ZK) & Theorem 5-PFSH03 (Multi-Transaction Adaptive Confidentiality)

### 5.1 Theorem 1B & Appendix B: Multi-Proof QROM Zero-Knowledge `[Unreviewed]`

Unchanged from PFSH02 (and now used **strictly for privacy—never for funds safety**):
1. **Algebraic HVZK (`Sim_IOP`):** \(\Delta_{\mathrm{HVZK}} \le 133/2^{384} = 2^{-376.94}\).
2. **Lemma 1.1 (5,216-bit unopened-leaf min-entropy + AHU19 O2H):** \(\le 2Q\sqrt{n-1}/2^{2608}\) per proof.
3. **Lemma 1.2 (Capped-PoW TV):** \(\mathrm{TV}(\mathrm{Real}_{\mathrm{capped}}, \mathrm{Ideal}) \le 2^{-182.60}\).
4. **68-Step GHHM21 Reprogramming:** Summing across \(P \le 2^{32}\) proofs gives \(\mathrm{Adv}_{\mathrm{QROM\text{-}ZK}}(2^{32}, Q) \le 2^{-150.60}\). \(\blacksquare\)

### 5.2 Theorem 5-PFSH03: `q_c`-Transaction Adaptive Confidentiality (`pfsh03_theorem5_multitx_hybrid`)

In PFSH03, wallets derive a **fresh indexed address** (`wallet.address(index)`) per incoming note from one seed, giving each note an independent `pk_dsa`, `r_pk`, and ML-KEM-1024 envelope keypair (or fresh spend keypair per note). Across \(q_c\) adaptively chosen challenge transactions (with total honest proofs \(P\), dummy slots \(d\), and active wallet-scan oracle \(O_{\mathrm{Scan}}\)):

1. **Global QROM-ZK hop:** Replace all \(P\) honest proofs across the entire \(q_c\)-transaction execution at once via Theorem 1B (`Adv_QROM-ZK(P, Q)`).
2. **Per-challenge-transaction hybrids \(j = 1,\dots,q_c\):**
   - *Stealth envelopes (2 slots):* ML-KEM-1024 IND-CCA2 + HMAC-SHA-384 PRF + AES-256-GCM INT-CTXT/IND$-CPA + `[NonStd]` ML-KEM `IK-CCA` + implicit-rejection closure (`[NonStd]` `IR-PRF` + HMAC + GCM, closing the GMP22 scan-oracle attack).
   - *Fresh per-note keys & nullifiers:* Because each fresh note has an independent `r_pk` used at most once, cross-note SHAKE256 `JointPRF` disappears; only independent dummy `PRG` and per-note single-use nullifier/commitment hiding (`Hide`) remain.
   - *Spend public keys:* Because each fresh note's `pk_dsa` is independently generated via `ML-DSA-65.KeyGen` and blinded behind `A = H_A(pk_hash, r_pk)` until spend time, revealing `pk_dsa` on spend leaks zero cross-note linkability when addresses are not reused.

Summing across \(j = 1,\dots,q_c\) gives the kernel-checked `pfsh03_theorem5_multitx_hybrid` bound in `AuthAndPrivacy.lean`:

$$\mathrm{Adv}_{\mathrm{MultiPriv}}^{\mathrm{PFSH03}}(q_c, \mathcal{A}) \le 2\Bigl[\mathrm{Adv}_{\mathrm{QROM\text{-}ZK}}(P, Q) + q_c\bigl(2U(\mathrm{Adv}_{\mathrm{IND\text{-}CCA2}}^{\mathrm{ML\text{-}KEM}} + \mathrm{Adv}_{\mathrm{IK\text{-}CCA}}^{\mathrm{ML\text{-}KEM}}) + 2\mathrm{Adv}_{\mathrm{IR\text{-}PRF}}^{\mathrm{ML\text{-}KEM}} + 4\mathrm{Adv}_{\mathrm{PRF}}^{\mathrm{HMAC}} + 4\mathrm{Adv}_{\mathrm{INT\text{-}CTXT}}^{\mathrm{GCM}} + 2\mathrm{Adv}_{\mathrm{IND\$\text{-}CPA}}^{\mathrm{GCM}} + 2\mathrm{Adv}_{\mathrm{Hide}}^{\mathrm{SHAKE256}}\bigr) + d\,\mathrm{Adv}_{\mathrm{PRG}}^{\mathrm{SHAKE256}} + \tfrac{2q_c(|\mathrm{Coins}|+|\mathrm{SpentSN}|+4)}{2^{384}}\Bigr]. \quad \blacksquare$$

**Explicit privacy caveat:** Reusing one static receive address across multiple notes does **not** weaken theft resistance (ML-DSA-65 is many-time EUF-CMA), but spending two notes from the same static address publishes the same `pk_dsa` on-chain and publicly links those spends. Transaction-graph metadata (amounts at public shield/exit boundaries, asset IDs, fees, epoch anchors, inclusion timing, and network IP metadata) also remains outside the cryptographic hiding boundary.

---

## 6. Theorem 3: Supply Conservation & No Double Spend (`ValueConservation.lean`)

Unchanged from PFSH02: fold \(\mathcal{A}\) and all honest provers into one unmodified-oracle algorithm, extract all \(q_{\mathrm{tx}}\) witnesses via Theorem 2A (zero simulation, zero A.4, zero ZK), and induct across transactions to prove exact 66-bit conservation \(\sum_{c \in \mathrm{Live}_i}\mathrm{val}_L(c) + \mathrm{Unshielded}_{\mathrm{acc}} + \mathrm{Fees}_{\mathrm{acc}} = \mathrm{Supply}_{\mathrm{minted}}\):

$$\mathrm{Adv}_{\mathrm{Bal}}(\mathcal{A}) \le \varepsilon_{\mathrm{Ext}}(Q_{\mathrm{tot}}, q_{\mathrm{tx}}) + \mathrm{Adv}_{\mathrm{ZeroPre}}^{H_{\mathrm{Coin}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Coin}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_A} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Node}}}. \quad \blacksquare$$

---

## 7. Spec-to-Code & Lean 4 Traceability Matrix (Commit `be1f77877`)

| Protocol Component | Rust Implementation | Independent Go Implementation | Lean 4 / Z3 Automated Verification |
| --- | --- | --- | --- |
| **Tower Field, ANTT, `PCLMULQDQ` / ARM64 `PMULL` / WASM32** | `tools/pft-binius-shielded-pq/rust-prover/src/field.rs` | `tools/pft-binius-shielded-pq/go-verifier/field.go`, `field_pclmul_amd64.{go,s}` | `check_math.py` tower irreducibility & cross-backend unit tests |
| **PFSH03 56-Perm Circuit (`pk_hash0/1`, `r_pk0/1`, 66-bit Adder, Merkle Mux)** | `rust-prover/src/circuit.rs` (`perm_input_spec`, `eval_verifier_weights_at_r1`) | `go-verifier/circuit.go` (`permInputSpec`, `evalVerifierWeightsAtR1`) | `verify_circuit_equivalence.py`: Z3 5.4.1 UNSAT + 3-way Rust/Go/Python Group-C (`42,444`) + differential `pk_in0/1` flip (`unsat+rust_go_diff_verified`) |
| **`3 × SHA-512` Oracle, Subtree-Streaming Prover & Fail-Fast Verifier** | `rust-prover/src/binius_pcs.rs` (`prove`, `verify_abortable`) | `go-verifier/binius_pcs.go` (`verifyBiniusProof`) | `Params.lean`, `Peel.lean`, `DualBinding.lean`, `Rank3Op.lean`, `CompressedOracle.lean` (`three_block_sha512_qro_reduction`), `ZeroKnowledge.lean` |
| **External Per-Note ML-DSA-65 Spend Auth & L1 Profile 2** | `rust-prover/src/{mint_auth,wire}.rs`, `crates/privacy_binius/src/lib.rs` (`verify_l1_abortable`) | `go-verifier/{mint_auth,l1_profile}.go`, `cmd/delivery/main.go` | `ValueConservation.lean`, `AuthAndPrivacy.lean` (`pfsh03_spend_auth_dichotomy`, `pfsh03_theorem4_zero_appA4`, `pfsh03_theorem5_multitx_hybrid`) + 39 named attacks |
| **L1 Settlement, Two-Tier Exit-Safe Pause, Key-Pinning & Pruned Storage** | `crates/types/src/shielded_bridge_governance.rs` (`PQ_EXIT_FREEZE_UNTIL_V1`), `crates/execution/src/entrypoints.rs` (`prepare_pq_account_debit_pinned`), `crates/node/src/{consensus_artifacts,pq_payment_actions}.rs`, `crates/storage/src/pq_archive.rs` (`prune_pq_bodies`) | — *(L1 node is Rust)* | `postfiat-node --lib` (`751/751`), M8 6-validator rehearsal, `postfiat-storage` (`2/2`), `postfiat-privacy-binius` (`10/10` accel & portable) |

---

## 8. Prioritized Questions for External Cryptographers & Auditors (Updated for PFSH03)

*(Legacy PFSH02 questions regarding Appendix A.4 / Theorem 2B and weak simulation-extractability are **retired**—PFSH03 no longer depends on Appendix A.4.)*

**Classical IOP Soundness (Theorem 1A, Appendix A.1–A.2)**
1. Does Lemma 1 (`Peel(M)`) validly derive list-decoding soundness for the 165-row interleaved RS code from one call to BCIKS20 Theorem 6.2 on \(L_{\mathrm{rem}}\), including when \(|L_{\mathrm{rem}}|\) is small and \(\delta'\) enters the unique-decoding regime?
2. Is \(\mathrm{State}_{\mathrm{KS}}\) well-defined and do all per-round bounds hold for partially defined Round-1 oracles \(M\) as required by Appendix A.3?
3. Is Lemma 4's single-challenge ring-switching step (one \(\rho_{\mathrm{rs}}\), powers up to 386, checking \(S_{G_1}\) and \(S_{\mathrm{mask2}}\) in the same polynomial, adding \(G_1\) without an independent randomizer before Round 24) sound?
4. Do the 2,192,844 constraints evaluated in factored verifier form exactly equal \(\mathcal{R}_{\mathrm{pay}}^{\mathrm{PFSH03}}\)—specifically the wiring of public `pk_hash0/1`, private `r_pk0/1`, note values, addresses, and nullifiers into all 56 Keccak permutations?

**Unmodified-Oracle QROM Extraction & Spend Authorization (App. A.3 & Thm 4-PFSH03)**
5. Is Lemma A.3.3's case analysis complete—specifically erasing/uncomputing tree entries, trees completed after challenges are drawn, and interleaved partial transcripts—and are the constants exact?
6. Does Chiesa–Manohar–Spooner (TCC 2019) apply as an asymptotic fallback given the Round-34 PoW and single sliced oracle, or is the construction outside CMS19's literal theorem?
7. Given our zero-query-blowup reduction (`three_block_sha512_qro_reduction`) from fixed-length counter-mode `SHA-512` slices to a 1,536-bit QRO, is modeling `SHA-512` as a 512-bit QRO acceptable while `SHA-384` (same compression function, different IV and domain prefix) is used for `tx_ctx`, `spend_msg`, and HMAC?
8. Does Theorem 4-PFSH03's reduction from external per-note ML-DSA-65 spend authorization + unmodified-oracle Theorem 2A cleanly close both note theft (Mode 1) and transaction hijacking / malleability (Mode 2) across all L1 Profile 2 modes (`Shield`, `Internal`, `Exit`), including dummy-slot key generation and slot-domain separation (`slot ∈ {0, 1}`)?

**Zero-Knowledge (Appendix B — Privacy Only)**
9. Does \(\mathrm{Sim}_{\mathrm{IOP}}\) match the real prover's exact distribution (beyond the small-model rank checks in `check_math.py`), and are 53 randomizers per row sufficient given that \(v_{\mathrm{prox}}\), \(v_{\mathrm{open}}\), and \(b_{\mathrm{eval}}\) are revealed?
10. In reprogramming step 68 (programming `H_C4` to a PoW-passing output), is composing Lemma 1.2 with GHHM21 Theorem 1 valid in the order used?

**Multi-Transaction Privacy, Systems DoS & L1 Profile 2**
11. Confirm or refute the implicit-rejection scanning closure (`IR-PRF` + HMAC + GCM, Grubbs–Maram–Paterson 2022) across the \(q_c\)-transaction hybrid in Theorem 5-PFSH03.
12. Does Maram–Xagawa (PKC 2023) anonymity for Kyber carry over to standardized FIPS-203 ML-KEM-1024?
13. Are single-use `Hide` and dummy `PRG` reasonable assumptions for single-permutation SHAKE256 with the secret placed inside a sponge whose rate exceeds capacity?
14. Are there any subtle adaptive cross-transaction correlations in Theorem 5-PFSH03's `q_c`-transaction hybrid when wallets mix fresh indexed addresses with epoch rollovers or partial-exit change outputs?
15. Do Theorems 1–5 carry over verbatim to the **L1 Profile 2** transcript (binding network, genesis, pool, asset, epoch, and inner issued fee) and per-asset tree isolation?
16. Does our `~126-bit` QROM soundness target (\(Q_{\mathrm{break}} = 2^{126.75}\), governed by 384-bit tree collisions) hold cleanly under the explicit hypotheses of Theorems 2A, 3, and 4?
17. Should `prepare_pq_account_debit_pinned` (mandatory key pinning before deposit debits) be enforced unconditionally at consensus before mainnet activation to eliminate the `~80-bit` unpinned 160-bit deposit-account exception?
18. Are there any bypass paths around our fail-fast verifier ordering (ML-DSA-65 sig → transcript replay → 20-bit Round-34 PoW → RS sum → circuit MLE/Merkle) and cooperative 4-thread `AtomicBool` early-abort under adversarial invalid-proof flooding and mempool admission backpressure?
