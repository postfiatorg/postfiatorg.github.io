---
title: "PFSH02 Mathematical Arguments, Conjectures & External Reviewer Appendix"
date: 2026-11-24T00:00:00Z
url: "/research/pfsh02-proofs/"
summary: "Companion formal appendix to the Peel-Binius-Shielded (PFSH02) research-status blog post: symbol glossary, Lemmas 1–4 (Peel(M) + BCIKS20), 34-round RBR-KS table, compressed-oracle QROM extraction (Appendix A.3), multi-proof SE conjecture sketch (Appendix A.4), QROM zero-knowledge (Appendix B), compositional ledger theorems 3–5, and the 18 prioritized questions for external cryptographers."
author: "Post Fiat"
math: true
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - PFSH02
  - Binius
  - QROM
  - Proofs
  - Privacy
copyMarkdownHref: "/research/pfsh02-proofs/index.md"
copyMarkdownButton: "Copy for LLM"
draft: false
---

*Companion formal appendix to [PFSH02: Experimental Curve-Free Private Payments for Post Fiat L1](/blog/peel-binius-quantum-safe-private-payments/). Pinned specification source: [`docs/security/peel-binius-shielded-pq-payments.md`](https://github.com/postfiatorg/postfiatl1v2/blob/26e5a10a5d6f8087b0d20a44b646e88e0042a382/docs/security/peel-binius-shielded-pq-payments.md) and Lean 4 formalization [`formal/lean/`](https://github.com/postfiatorg/postfiatl1v2/tree/26e5a10a5d6f8087b0d20a44b646e88e0042a382/formal/lean) on branch `feat/pq-payments-production-candidate` (`26e5a10a5`).*

**Review & Lean 4 formalization status:** Nine Lean 4 (`v4.20.0`) + Mathlib modules (`2,729` LOC, zero `sorry`s, zero custom axioms—`[propext, Classical.choice, Quot.sound]` only) kernel-check the exact-rational parameters (`Params.lean`), greedy peeling (`Peel.lean`), dual-polynomial binding / `K_32` subfield inheritance / ring-switching (`DualBinding.lean`), rank-3 operator norm & readout (`Rank3Op.lean`), compressed-oracle superposition reduction & telescoping (`CompressedOracle.lean`), unopened-leaf bijection / capped PoW / `Sim_IOP` bijections (`ZeroKnowledge.lean`), ledger supply conservation (`ValueConservation.lean`), Appendix A.4's `E_3` bound & Cases A/B/C trichotomy (`ConjectureA4.lean`), and Mode 3 key-pinning / Theorems 4–5 hybrids (`AuthAndPrivacy.lean`). External peer review remains required for model-to-code fidelity, external literature interfaces (BCIKS20 Thm 6.2, GHHM21 Thm 1, AHU19 Thm 3, and real-`Sim_BCS`-to-`B^H` view equivalence), and the non-standard primitive assumptions (`IK-CCA`, `IR-PRF`, `JointPRF`, `PRG`, `Hide`).

---

## 1. Symbol & Parameter Glossary

| Symbol | Definition & Pinned Value |
| --- | --- |
| \(\mathbb{F}_2 \subset K_{16} \subset K_{32} \subset E\) | Binary tower: \(K_{16} = \mathbb{F}_2[x]/(x^{16}+x^5+x^3+x+1)\), \(K_{32} = K_{16}[Z]/(Z^2+Z+x^{11})\), \(E = K_{32}[Y]/(Y^{12}+Y^3+Y+(Z+x)) \cong \mathbb{F}_{2^{384}}\). |
| \(H, L \subset K_{32}\) | Disjoint \(\mathbb{F}_2\)-affine subspaces: interpolation domain \(H = V_9 = \{0,\dots,511\}\) (\(|H|=512\)); evaluation coset \(L = \texttt{0x00200000} + V_{21}\) (\(|L| = n = 2^{21} = 2,097,152\)). |
| \(D, \rho, L_{\max}\) | Reed–Solomon degree bound \(D = 565\); code rate \(\rho = D/n = 565/2^{21} \approx 0.000269413\); Johnson parameter \(m' = 3\); greedy peeling list bound \(L_{\max} = \lfloor\sqrt{2/\rho}\rfloor = 86\). |
| \(B_0,\dots,B_4; N_C\) | Five witness bit-arrays in \(\mathbb{F}_2^{2^{19}}\) (447,014 active rows; 140 active packed \(K_{32}\) witness rows); total scalar constraints \(N_C = 2,192,844\) (Groups A, B, C). |
| \(MT_1, M, B_{\mathrm{pcs}}, B_{\mathrm{prox}}\) | Height-21 Merkle tree over \(L\) (48 B digests) committing to 163 \(K_{32}\)-rows (140 witness + 5 ring-switch mask + 2 sumcheck-1 mask + 16 sumcheck-2 mask rows, each with 53 randomizers vanishing on \(H\)) plus 2 uniform degree-\(<565\) \(E\)-blinding polynomials \(B_{\mathrm{pcs}}, B_{\mathrm{prox}}\). \(M: L \to (K_{32}^{163}\times E^2)\cup\{\bot\}\) is the extracted Round-1 oracle. |
| \(S_{G_1}, S_{\mathrm{mask2}}\) | Round-1 claimed hypercube sums of the CFS17 Sumcheck-1 blinding polynomial \(G_1\) (Jacobian rank 58/58) and the 16-row Sumcheck-2 mask (Jacobian rank 17/17, determinant degree \(\le 112\)). |
| \(H: X \to Y = \{0,1\}^{1536}\) | Single fixed-range compiler oracle instantiated by \(3\times\mathrm{SHA\text{-}512}\); verifier query budget \(\kappa_v = 68 + 52 + 843 = 963\) per proof. |
| \(t, w_{\mathrm{pow}}, M_{\mathrm{pow}}\) | Round-34 column openings \(t = 52\); PoW difficulty \(w_{\mathrm{pow}} = 20\) bits; hard prover nonce cap \(M_{\mathrm{pow}} = 2^{27} = 128 \cdot 2^{20}\). |
| \(\mathcal{R}_{\mathrm{pay}}(x)\) | NP payment relation: two real/dummy inputs authenticating against Depth-24 SHAKE256 Merkle roots, two output commitments, and exact 66-bit conservation \(v_{\mathrm{in},0} + v_{\mathrm{in},1} + v_{\mathrm{mint}} = v_{\mathrm{out},0} + v_{\mathrm{out},1} + \mathrm{pub\_exit}\) in \(\mathbb{Z}\) with \(\mathrm{pub\_exit} = \mathrm{fee} + v_{\mathrm{unshield}} < 2^{64}\). |

---

## 2. Theorem 1A & Appendix A.1–A.2: 34-Round IOP Knowledge Soundness `[Unreviewed]`

PFSH02 adapts the binary-tower polynomial commitment and ring-switching framework of **Diamond and Posen (Binius, 2023–2024)** to a 34-round IOP with 1-to-1 atomic single-oracle BCS compilation.

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

**Proof of (ii) Proximity curve bound \(\Pr_{\lambda_p}[\mathrm{Bad}_{\mathrm{peel}}(\lambda_p)] \le 2^{-305.79}\):** For \(\lambda_p \in E\), define \(F_{\lambda_p}(M)(x) := B_{\mathrm{prox}}(x) + \lambda_p B_{\mathrm{pcs}}(x) + \sum_{r=0}^{162} \lambda_p^{r+2} M_r(x)\). Fix any \(v \in \mathrm{RS}[E, L, D] \setminus \{F_{\lambda_p}(u) : u \in \mathcal{P}(M)\}\) and let \(A := \{x \in L_0 : v(x) = F_{\lambda_p}(M)(x)\}\). On each peeled slice \(D^{(j-1)}(u_j)\), \(v \ne F_{\lambda_p}(u_j)\) forces \(|A \cap D^{(j-1)}(u_j)| \le D - 1\), so:

$$|A \cap (L_0 \setminus L_{\mathrm{rem}})| \le k(D-1) \le kD \le \sqrt{2D}\bigl(\sqrt{n_0} - \sqrt{n'}\bigr)$$

(strict when \(k \ge 1\)). Partition all \(n' \ge 0\) into two cases:

- **Case 1 (\(0 \le n' \le 2D\)):** Here \((n')^2 \le 2Dn'\), so \(n' \le \sqrt{2Dn'}\). If \(k = 0\), then \(n_0 = n' \le 2D = 1,130 < 48,680 \approx \sqrt{2\rho}\,n\). If \(k \ge 1\), adding the strict peeled bound and \(|A \cap L_{\mathrm{rem}}| \le n' \le \sqrt{2Dn'}\) gives \(|A| < \sqrt{2D}(\sqrt{n_0}-\sqrt{n'}) + \sqrt{2Dn'} = \sqrt{2Dn_0} \le \sqrt{2\rho}\,n\). Thus \(\Pr[\mathrm{Bad}_{\mathrm{peel}}] = 0\).
- **Case 2 (\(n' > 2D\)):** \(M\) has no \(\bot\) entries on \(D_{\mathrm{eval}} := L_{\mathrm{rem}}\) of size \(n' > 2D\), with rate \(\rho' := D/n' < 1/2\). Set \(\delta' := 1 - \sqrt{2\rho'}\). Since \(\rho' < 1/2\), \(\delta' > 0\); since \(\sqrt{2} \approx 1.4142 > 7/6 = 1 + 1/(2\cdot 3)\), \(\delta' < 1 - (1 + \tfrac{1}{2m'})\sqrt{\rho'}\) strictly for \(m' = 3\). Every verbatim hypothesis of BCIKS20 Theorem 6.2 holds on \((\mathbb{F}_q = E, D_{\mathrm{eval}} = L_{\mathrm{rem}}, k' = D, \ell = 164, m' = 3)\). If \(\Pr_{\lambda_p}[\exists v : |A \cap L_{\mathrm{rem}}| \ge \sqrt{2Dn'}] > \varepsilon_{\mathrm{curve}}(3, \rho', n', 164)\), BCIKS20 yields a codeword \(u^* \in \mathrm{RS}[E, L_{\mathrm{rem}}, D]^{165}\) (uniquely extending to \(L\) since \(n' > 2D > D\)) agreeing with \(M\) on \(\ge \sqrt{2Dn'}\) points of \(L_{\mathrm{rem}}\), contradicting that `Peel(M)` halted. Monotonicity \((n')^2 / (\rho')^{3/2} = (n')^{7/2}/D^{3/2} \le n^{7/2}/D^{3/2}\) gives:

$$\Pr_{\lambda_p}[\mathrm{Bad}_{\mathrm{peel}}(\lambda_p)] \le 164 \cdot \frac{(3.5)^7}{3\rho^{3/2}} \cdot \frac{n^2}{2^{384}} = 2^{-305.79}. \quad \blacksquare$$

### 2.3 Lemmas 2–4 & 34-Round RBR-KS Table

- **Lemma 2 (Dual-Polynomial Binding):** For each \(u \in \mathcal{P}(M)\), let \(D_u := \{x \in \mathrm{supp}(M) : M(x) = u(x)\}\). The event \(\mathrm{Bad}_{\mathrm{pt}}(\lambda_p)\) that some \(u \in \mathcal{P}(M)\) and \(x \in \mathrm{supp}(M) \setminus D_u\) satisfy \(F_{\lambda_p}(M(x)) = F_{\lambda_p}(u(x))\) has probability \(\le 86 \cdot 2^{21} \cdot 164 / 2^{384} = 2^{-349.22}\). Conditioned on \(\neg\mathrm{Bad}_{\mathrm{peel}} \land \neg\mathrm{Bad}_{\mathrm{pt}}\), any \((v_{\mathrm{prox}}, v_{\mathrm{open}})\) with joint agreement \(|A_{\mathrm{both}}| \ge \sqrt{2\rho}\,n \approx 48,680 > D = 565\) pins a unique \(u \in \mathcal{P}(M)\) satisfying \(v_{\mathrm{prox}} \equiv F_{\lambda_p}(u)\), \(A_{\mathrm{both}} \subset A_{\mathrm{prox}} \subset D_u\), and \(v_{\mathrm{open}} \equiv b_{\mathrm{pcs}}(u) + \lambda_o \sum_{r=0}^{162} c_r u_r\) identically in \(E[X]_{<D}\). \(\blacksquare\)
- **Lemma 3 (Subfield-\(K_{32}\) Structural Booleanity):** Every peeled slice satisfies \(|D^{(i)}(u)| \ge \sqrt{2D \cdot 2D} = 2D > D\) points in \(L \subset K_{32}\) where \(M_r(x) \in K_{32}\). Lagrange interpolation over any \(D\) points forces \(u_r \in K_{32}[X]_{<D}\), so \(u_r(H) \subset K_{32}\), unpacking uniquely into 32 \(\mathbb{F}_2\) witness bits without quadratic \(b(1-b)=0\) gates. \(\blacksquare\)
- **Lemma 4 (Single-Challenge Ring-Switching):** Let \(\{\beta_u\}_{u=0}^{31}\) be the fixed \(\mathbb{F}_2\)-basis of \(K_{32}\) (represented in bit-index order as `1 << u` in \(x, Z\) coordinates) and \(\{e_{v,u} := Y^v \cdot \beta_u\}_{v=0..11,\,u=0..31}\) be the 384-element \(\mathbb{F}_2\)-basis of \(E = \mathbb{F}_{2^{384}}\). Define \(L_{\rho_{\mathrm{rs}}}(z) := \sum_{j=0}^{383} \mathrm{bit}_j(z)\,\rho_{\mathrm{rs}}^j\) and \(\eta_{1,2,3} := \rho_{\mathrm{rs}}^{384,385,386}\). Any Round-23 discrepancy vanishes with probability \(\le 4/|E|\) over \(\gamma\); any Round-24 discrepancy (including any mismatch in \(S_{G_1}\)) yields a nonzero univariate polynomial of degree \(\le 386\) in \(\rho_{\mathrm{rs}}\), vanishing with probability \(\le 386/|E|\). \(\blacksquare\)

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

**Terminal Extraction:** Whenever \(\mathrm{State}_{\mathrm{KS}}(x, \mathrm{tr}_{34}) = 0\) and \(V(x, \mathrm{tr}_{34}) = 1\), Lemma 2 pins the unique \(u^* \in \mathcal{P}(M) \setminus \mathcal{P}_{\mathrm{bad}}(M)\). \(\mathrm{Ext}_{\mathrm{IOP}}\) interpolates the 140 witness rows over \(K_{32}\) on the first 565 points of \(A_{\mathrm{prox}} \subset D_{u^*}\) in \(O(\min(n, |\mathrm{supp}(M)|) + 140\cdot 565^2)\) time and outputs \(w^* \in \mathcal{R}_{\mathrm{pay}}(x)\) with probability 1. \(\blacksquare\)

---

## 3. Theorem 2A & Appendix A.3: Single-Oracle QROM Extraction `[Unreviewed]`

### Lemma A.3.0 (Exact Rank-3 Self-Adjoint Operator & Both-Directions Norm Bound)

In Zhandry's compressed-oracle representation over \(H: X \to Y = \{0,1\}^{1536}\) (\(N = 2^{1536}\)), each register \(D(x)\) has basis \(\{|\bot\rangle\} \cup \{|u\rangle : u \in Y\}\). In the phase basis \(|x, z, D\rangle\), the query unitary \(O\) block-diagonalizes over \((x, z, D_{-x})\) with \(O_{x,0} = I\) and \(O_{x,z} = \mathrm{ST}_x Z_z \mathrm{ST}_x\) for \(z \ne 0\), where \(|\phi\rangle = N^{-1/2}\sum_{u \in Y}|u\rangle\), \(|\psi_z\rangle = Z_z|\phi\rangle\), and \(\mathrm{ST}_x = I - (|\bot\rangle - |\phi\rangle)(\langle\bot| - \langle\phi|)\).

Evaluating \(O_{x,z}\) on \(\mathrm{span}\{|\bot\rangle, |\phi\rangle, |\psi_z\rangle\} \oplus \perp\) gives \(O_{x,z}|\bot\rangle = |\psi_z\rangle\), \(O_{x,z}|\phi\rangle = |\phi\rangle\), \(O_{x,z}|\psi_z\rangle = |\bot\rangle\), and \(O_{x,z} = Z_z\) on \(\perp\), yielding the exact self-adjoint rank-3 identity:

$$O_{x,z} = Z_z + (|\psi_z\rangle - |\bot\rangle)\langle\bot| + (|\phi\rangle - |\psi_z\rangle)\langle\phi| + (|\bot\rangle - |\phi\rangle)\langle\psi_z|, \qquad O_{x,z}^\dagger = O_{x,z}.$$

For any \(S \subset Y\) with \(\bot \notin S\) and density \(p := |S|/N\):

$$P_S O_{x,z} P_{\neg S} = (P_S|\psi_z\rangle)(\langle\bot| - \langle\phi|)P_{\neg S} + (P_S|\phi\rangle)(\langle\phi| - \langle\psi_z|)P_{\neg S}.$$

Because \(\|P_S|\phi\rangle\|_2 = \|P_S|\psi_z\rangle\|_2 = \sqrt{p}\) and \(\||\bot\rangle - |\phi\rangle\|_2 = \||\phi\rangle - |\psi_z\rangle\|_2 = \sqrt{2}\), both entry and exit/uncompute norms satisfy:

$$\|P_S O_{x,z} P_{\neg S}\|_2 = \|P_{\neg S} O_{x,z} P_S\|_2 \le 2\sqrt{2p} = \sqrt{8p} < \sqrt{10p}. \quad \blacksquare$$

### Lemmas A.3.1–A.3.4 (Tree-Invariance, Transition Capacity & Readout)

- **Lemma A.3.1 (Tree-Invariance):** Let \(S(D) := R(D) \cup C(D)\) be all 384-bit roots and child digests present in `STMT`/`NODE` inputs of \(D\) (\(|S(D)| \le 2|D|\)). Adding a `LEAF`/`NODE` entry \((x, u)\) with \(u[0..48] \notin S(D)\) leaves \(\mathrm{MRoot}_D^{-1}(\mathrm{root})\) and \(\mathrm{Peel}(M)\) bit-for-bit unchanged for every \(\mathrm{root} \in R(D)\); hit probability \(\le 2s/2^{384}\).
- **Lemmas A.3.2 & A.3.3 (Both-Directions Capacity):** Let \(P' := \mathrm{CL} \cup \mathrm{SUC}\). Block-diagonalization reduces \(\llbracket P_s \to P' \rrbracket = \|\Pi_{P'} O \Pi_{P_s}\|_2\) pointwise to classical \((x, z \ne 0, D_{-x})\):
  - *Exit (\(D_{-x} \in P'\)):* `CL` is upward-monotone (\(G_- = \emptyset\)); leaving `SUC \ CL` via `LEAF`/`NODE` requires hitting \(S(D_{-x})\) (\(\le 2s/2^{384}\)).
  - *Entry (\(D_{-x} \notin P'\)):* Under \(\neg\mathrm{CL}(D_{-x})\), each input \(x\) has at most one ancestor chain and partial oracle \(M\) before sampling \(u\): `LEAF`/`NODE` costs \(\le 3(s+1)/2^{384}\); `STMT`/`ABS` costs \(\le 2s/2^{512}\); `CH` costs \(\le \varepsilon_{\mathrm{rbr}}(33a) + 2s/2^{512}\); `C4` costs \(\le p_{34} = 2^{-302.31}\).
  - Combining via Lemma A.3.0 gives \(\llbracket P_s \to P' \rrbracket \le \sqrt{30(s+1)}\,2^{-192} + \sqrt{10\cdot\max(\varepsilon_{\mathrm{rbr}}(33a) + 2s/2^{512},\; p_{34})}\).
- **Lemma A.3.4 (Telescoping & Readout):** Telescoping over \(Q_v = Q + L\kappa_v\) queries and squaring yields \(\Pr[D_{\mathrm{end}} \in P']\). For each classical verifier query \((x_i, y_i)\), recompressing via \(\mathrm{ST}_{x_i}|y_i\rangle = (1 - 1/N)|y_i\rangle + N^{-1/2}|\bot\rangle - N^{-1}\sum_{u\ne y_i}|u\rangle\) gives \(\Pr[D_{\mathrm{end}}(x_i) \ne y_i] = 2/N - 1/N^2 < 2/2^{1536} < 2/2^{384}\). Together this gives Theorem 2A:

$$\varepsilon_{\mathrm{Ext}}(Q, L) \le \left(3.652\, Q_v^{3/2} 2^{-192} + Q_v\sqrt{10\cdot\max(\varepsilon_{\mathrm{rbr}}(33a) + 2 Q_v 2^{-512},\; p_{34})}\right)^2 + \frac{2 L \kappa_v}{2^{384}}. \quad \blacksquare$$

---

## 4. Conjecture 2B & Appendix A.4: Adaptive Multi-Proof SE `[Conjecture]`

*(Sketch only; no standalone published anchor.)*

$$\varepsilon_{\mathrm{SE}}(P, L, Q) \le \varepsilon_{\mathrm{Ext}}(Q_{\mathrm{eff}}, L) + 10\, Q_{\mathrm{eff}}^2 P\left(\frac{68}{2^{512}} + \frac{n-1}{2^{384}} + \left(\frac{t}{n}\right)^t\right) + \frac{3}{2} P \sqrt{Q_{\mathrm{eff}}}\,\frac{68}{2^{256}}$$

where \(Q_{\mathrm{eff}} = Q + P(n-1+t) + L\kappa_v\). Wrapper \(B^H\) pre-samples simulated transcript states \(T_{\mathrm{tr}}\), unopened leaf digests \(T_{\mathrm{leaf}}\), and query-index sets \(T_{\mathrm{qidx}}\), hashes opened leaves and internal nodes on unmodified \(H\), and stores only the 68 programmed transcript entries per simulated proof in a classical overlay \(T_{\mathrm{prog}}\). For any fresh accepted \((x^*, \pi^*)\) under \(\neg\mathrm{CL} \land \neg\mathrm{SUC} \land \neg E_3\):

- **Case A** (new Round-1 tuple, covering every mauled statement \(x^* \ne x_i\)): `STMT` misses \(T_{\mathrm{prog}}\), runs entirely on unmodified \(H\), and extracts via Theorem 2A.
- **Case B** (same Round-1 tuple as simulated proof \(i\), differing at later round \(r^*\)): the transcript forks off \(T_{\mathrm{prog}}\) onto unmodified \(H\), drawing fresh Round-34 query indices outside \(Q_{\mathrm{idx},i}\) and forcing verification of an unopened leaf against \(\mathrm{root}_i\) on unmodified \(H\) *(the primary step needing formalization)*.
- **Case C** (identical transcript and `pow_nonce`, differing opened columns/siblings): direct `LEAF`/`NODE` collision in unmodified \(H\).

---

## 5. Theorem 1B & Appendix B: Multi-Proof QROM Zero-Knowledge `[Unreviewed]`

1. **Algebraic HVZK (\(\mathrm{Sim}_{\mathrm{IOP}}\), App. B.1):** Aborts only on \(E_{\mathrm{exc}}\): any \(r_1[d] = 0\) (\(19/2^{384}\)), \(\tau = 0\) (\(1/2^{384}\)), \(\rho_{\mathrm{rs}} = 0\) (\(1/2^{384}\)), or vanishing of the \(17\times 17\) Sumcheck-2 Jacobian minor (degree \(\le 112\), full rank 17 verified in `check_math.py`, \(\le 112/2^{384}\)). Total \(\Delta_{\mathrm{HVZK}} \le 133/2^{384} = 2^{-376.94}\).
2. **Lemma 1.1 (5,216-Bit Marginal Leaf Min-Entropy & AHU19 O2H):** All algebraic messages depend exclusively on \(U_r|_H\) and never touch the 53 uniform \(K_{32}\) randomizers vanishing on \(H\). With \(|Q_{\mathrm{idx}}| \le 52 < 53\) and bijection \((B_{\mathrm{pcs}}, B_{\mathrm{prox}}) \mapsto (v_{\mathrm{open}}, v_{\mathrm{prox}})\), every unopened leaf preimage has exact marginal conditional min-entropy \(163 \times 32 = 5,216\) bits. Applying AHU19 Theorem 3 (Semi-Classical O2H) and a union bound over \(n-1\) marginals adds \(\le 2 Q \sqrt{n-1}/2^{2608}\) per proof (doubled conservatively to 4 in `check_math.py`).
3. **Lemma 1.2 (Hard-Capped PoW Total Variation):** With \(N = 2^{384}\), \(q = 2^{-20}\) (\(Nq = 2^{364}\)), and cap \(M_{\mathrm{pow}} = 2^{27}\):
   $$\mathrm{TV}(\mathrm{Real}_{\mathrm{capped}}, \mathrm{Ideal}) \le (1-q)^{M_{\mathrm{pow}}} + \frac{M_{\mathrm{pow}}^2}{2N} + \frac{1}{2\sqrt{Nq}} + e^{-Nq} \le 2^{-182.60}.$$
4. **68-Step Product-State GHHM21 Reprogramming (App. B.2):** Reprogramming steps \(r = 1..68\) sequentially before returning proof \(i\) to \(\mathcal{A}\) preserves \(p_{\max} \le 2^{-512}\) at every step, adding \((3/2)\sqrt{Q}\cdot 68 / 2^{256}\) per proof via GHHM21 Theorem 1. Summing across \(P \le 2^{32}\) proofs gives \(\mathrm{Adv}_{\mathrm{QROM\text{-}ZK}}(2^{32}, Q) \le 2^{-150.60}\). \(\blacksquare\)

---

## 6. Compositional Ledger Theorems 3, 4 & 5

### Theorem 3 (Supply Conservation & No Double Spend)

Fold \(\mathcal{A}\) and all \(q_{\mathrm{hon}}\) honest real provers into one unmodified-oracle algorithm \(B^H\) making \(Q_{\mathrm{tot}} = Q + q_{\mathrm{hon}}(2n + M_{\mathrm{pow}} + 68)\) queries and outputting all \(q_{\mathrm{tx}}\) accepted transactions. Extract all witnesses via Theorem 2A (zero simulation, zero A.4, zero ZK). By induction on \(i = 0..q_{\mathrm{tx}}\): dummy inputs enforce \(v_{\mathrm{in},b} = 0\); real inputs authenticate against a historical anchor to locate a unique prior coin (up to \(H_{\mathrm{Node}}\) CR and \(H_{\mathrm{Coin}}\) zero-preimage on `0^48`); openings match up to \(H_{\mathrm{Coin}}\) CR; double spends break \(H_A\) CR or duplicate a nullifier rejected by Rules R2/R3; and 66-bit conservation preserves \(\sum_{c \in \mathrm{Live}_i}\mathrm{val}_L(c) + \mathrm{Unshielded}_{\mathrm{acc}} + \mathrm{Fees}_{\mathrm{acc}} = \mathrm{Supply}_{\mathrm{minted}}\):

$$\mathrm{Adv}_{\mathrm{Bal}}(\mathcal{A}) \le \varepsilon_{\mathrm{Ext}}(Q_{\mathrm{tot}}, q_{\mathrm{tx}}) + \mathrm{Adv}_{\mathrm{ZeroPre}}^{H_{\mathrm{Coin}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Coin}}} + \mathrm{Adv}_{\mathrm{CR}}^{H_A} + \mathrm{Adv}_{\mathrm{CR}}^{H_{\mathrm{Node}}}. \quad \blacksquare$$

### Theorem 4 (Spend Auth, Non-Malleability & Deposit Auth)

- **Modes 1 & 2:** Hop 1 replaces honest proofs via Theorem 1B; Hop 2 replaces honest nullifiers via `[NonStd]` SHAKE256 `JointPRF` and dummy `PRG` (eliminating \(S^*\)); extraction on the fresh forgery via **Conjecture 2B** breaks \(H_A\) one-wayness (Mode 1) or multi-target target-preimage resistance of \(H_{\mathrm{SN}}\) (Mode 2).
- **Mode 3 (Deposit Debit — On-Chain Public-Key Pinning):** In `prepare_pq_account_debit` (`crates/execution/src/entrypoints.rs`), Post Fiat L1 pins the depositor's full 1,952-byte ML-DSA-65 public key in `account.public_key_hex` on its first signed transaction. For any **key-pinned account**, submitting a different public key is rejected deterministically before signature verification, so Mode 3 reduces directly to SHA-384 CR plus ML-DSA-65 EUF-CMA with **zero 160-bit address exposure**. Only an unpinned account that has never signed an on-chain transaction prior to its first shielded deposit incurs the targeted 160-bit address second-preimage term (\(\min(1, Q^2/2^{160})\): \(\sim 2^{-32}\) at \(Q=2^{64}\), vacuous at \(Q=2^{80}\)).

### Theorem 5 (Global-Pool & ZK-Mint Privacy — With Implicit-Rejection Sub-Hop)

The single-challenge-transaction game \(\mathrm{Exp}_{\mathrm{GlobalPriv}}(b)\) grants adaptive access to \(O_{\mathrm{Mint}}\), \(O_{\mathrm{Hon}}\) (excluding challenge inputs/outputs), active wallet-reaction oracle \(O_{\mathrm{Scan}}\), and \(O_{\mathrm{Corrupt}}\) (excluding challenge owners/recipients). The 5-hop hybrid \(H_0 \to H_4\) runs as follows:

1. **\(H_0 \to H_1\) (QROM ZK):** Replace all \(P\) honest proofs with \(\mathrm{Sim}_{\mathrm{BCS}}(x)\) via Theorem 1B.
2. **\(H_1 \to H_2\) (Stealth Envelopes, slots \(c \in \{0,1\}\)):** Five sub-hops per slot: (i) single-user ML-KEM-1024 IND-CCA2 (guessing recipient index, factor \(U\)) replaces \(ss_c\) with uniform \(ss_c^*\); (ii) HMAC-SHA-384 PRF replaces \((K_{\mathrm{aead}}, N_{\mathrm{aead}})\) with independent uniform keys; (iii) AES-256-GCM INT-CTXT + IND$-CPA rejects modified scans and replaces \(\mathrm{ct}_{\mathrm{aead}}\) with encryption of `0^86`; (iv) single-user `[NonStd]` ML-KEM-1024 `IK-CCA` (factor \(U\)) replaces \(\mathrm{ct}_{\mathrm{kem}}^*\) with \(\mathrm{Encaps}(\mathrm{ek}_{\mathrm{dummy}})\); and (v) **implicit-rejection closure (GMP22 fix)**: for any non-recipient candidate \(u' \ne u_c^*\) scanning modified envelopes sharing \(\mathrm{ct}_{\mathrm{kem}}^*\), replace FIPS-203's implicit-rejection key \(J(z_{u'} \parallel \mathrm{ct}_{\mathrm{kem}}^*)\) with a fresh uniform key (`Adv_IR-PRF^{ML-KEM-1024}`), then apply HMAC-SHA-384 PRF and AES-256-GCM INT-CTXT so every such scan rejects identically across both worlds \(b \in \{0,1\}\).
3. **\(H_2 \to H_3\) (Nullifiers):** Replace dummy nullifiers via `[NonStd]` dummy `PRG` and real challenge nullifiers via single-user `[NonStd]` SHAKE256 `JointPRF` (factor \(r U\)).
4. **\(H_3 \to H_4\) (Commitments & Aborts):** Replace both output commitments via `[NonStd]` SHAKE256 `Hide` and account for negligible R3/R4 collision aborts.

$$\mathrm{Adv}_{\mathrm{GlobalPriv}}(\mathcal{A}) \le 2\Bigl[\mathrm{Adv}_{\mathrm{QROM\text{-}ZK}}(P, Q) + 2U(\mathrm{Adv}_{\mathrm{IND\text{-}CCA2}}^{\mathrm{ML\text{-}KEM}} + \mathrm{Adv}_{\mathrm{IK\text{-}CCA}}^{\mathrm{ML\text{-}KEM}}) + 2(\mathrm{Adv}_{\mathrm{IR\text{-}PRF}}^{\mathrm{ML\text{-}KEM}} + 2\mathrm{Adv}_{\mathrm{PRF}}^{\mathrm{HMAC}} + 2\mathrm{Adv}_{\mathrm{INT\text{-}CTXT}}^{\mathrm{GCM}} + \mathrm{Adv}_{\mathrm{IND\$\text{-}CPA}}^{\mathrm{GCM}}) + rU\,\mathrm{Adv}_{\mathrm{JointPRF}}^{\mathrm{SHAKE256}}(2) + d\,\mathrm{Adv}_{\mathrm{PRG}}^{\mathrm{SHAKE256}} + 2\,\mathrm{Adv}_{\mathrm{Hide}}^{\mathrm{SHAKE256}} + \tfrac{2(|\mathrm{Coins}|+|\mathrm{SpentSN}|+4)}{2^{384}}\Bigr].$$

---

## 7. The 18 Prioritized Questions for External Cryptographers

**Classical IOP Soundness (Theorem 1A, Appendix A.1–A.2)**
1. Does Lemma 1 (`Peel(M)`) validly derive list-decoding soundness for the 165-row interleaved RS code from one call to BCIKS20 Theorem 6.2 on \(L_{\mathrm{rem}}\), including when \(|L_{\mathrm{rem}}|\) is small and \(\delta'\) enters the unique-decoding regime?
2. Is \(\mathrm{State}_{\mathrm{KS}}\) well-defined and do all per-round bounds hold for partially defined Round-1 oracles \(M\) as required by Appendix A.3?
3. Is Lemma 4's single-challenge ring-switching step (one \(\rho_{\mathrm{rs}}\), powers up to 386, checking \(S_{G_1}\) and \(S_{\mathrm{mask2}}\) in the same polynomial, adding \(G_1\) without an independent randomizer before Round 24) sound?
4. Do the 2,192,844 constraints evaluated in factored verifier form exactly equal \(\mathcal{R}_{\mathrm{pay}}\)—especially the wiring of note values, addresses, and nullifiers into the 56 Keccak permutations?

**QROM Extraction & Simulation-Extractability (Appendices A.3 & A.4)**
5. Is Lemma A.3.3's case analysis complete—specifically erasing/uncomputing tree entries, trees completed after challenges are drawn, and interleaved partial transcripts—and are the constants exact?
6. Does Chiesa–Manohar–Spooner (TCC 2019) apply as an asymptotic fallback given the Round-34 PoW and single sliced oracle, or is the construction outside CMS19's literal theorem?
7. Is modeling \(3\times\mathrm{SHA\text{-}512}\) as one 1,536-bit QRO acceptable while SHA-384 (same compression function, different IV and domain prefix) is used for `tx_ctx` and HMAC?
8. Does Appendix A.4's classical overlay wrapper \(B^H\) formalize cleanly—specifically Case B, where a forged proof starts inside overwritten entries of \(T_{\mathrm{prog}}\) and continues on unmodified \(H\)?
9. Is weak simulation-extractability (fresh statement \(x^* \ne x_i\)) sufficient for Theorem 4, removing unique proof encodings as a security requirement?

**Zero-Knowledge (Appendix B)**
10. Does \(\mathrm{Sim}_{\mathrm{IOP}}\) match the real prover's exact distribution (beyond the small-model rank checks in `check_math.py`), and are 53 randomizers per row sufficient given that \(v_{\mathrm{prox}}\), \(v_{\mathrm{open}}\), and \(b_{\mathrm{eval}}\) are revealed?
11. In reprogramming step 68 (programming `H_C4` to a PoW-passing output), is composing Lemma 1.2 with GHHM21 Theorem 1 valid in the order used?

**Privacy & System-Level Security (Theorem 5 & L1 Profile 2)**
12. Confirm or refute the implicit-rejection scanning gap in Theorem 5's final hybrid \(H_4\) (Grubbs–Maram–Paterson 2022) and supply the exact hybrid and bound needed to close it.
13. Does Maram–Xagawa (PKC 2023) anonymity for Kyber carry over to standardized FIPS-203 ML-KEM-1024?
14. Are `JointPRF`, dummy `PRG`, and `Hide` reasonable assumptions for single-permutation SHAKE256 with the secret placed inside a sponge whose rate exceeds capacity?
15. What is required to extend Theorem 5 beyond a single challenge transaction to multi-hop spends and cross-epoch migration?
16. Do Theorems 1–5 carry over verbatim to the **L1 Profile 2** transcript (binding network, genesis, pool, asset, epoch, and inner issued fee) and per-asset tree isolation?
17. What single headline security level (and under which explicit assumptions) may Post Fiat state publicly?
18. Is the **160-bit L1 account address** (\(\sim 2^{-32}\) targeted second-preimage reference at \(Q = 2^{64}\)) acceptable for deposits into a system designed for post-quantum security, or should deposit accounts migrate to wider address digests / on-chain key pinning before launch?
