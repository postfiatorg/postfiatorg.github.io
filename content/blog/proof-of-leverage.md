---
title: "Proof of Disclosed Leverage"
date: 2026-06-14T00:00:00Z
summary: "A zero-knowledge proof of a disclosed leverage profile: six legs, six verification domains, no hidden address disclosure. The proof commits spot, cash, gross perpetual notional, and Aave debt, with each line labeled by quantity and valuation evidence on a three-rung trust scale. It does not prove global solvency or completeness; it proves the disclosed account set reconciles exactly to the public buckets."
categories:
  - Post Fiat Research
tags:
  - Proof of Reserves
  - Proof of Leverage
  - Zero Knowledge
  - SP1
  - Post Fiat
---

This is a proof of **disclosed leverage**, not a proof of solvency.

That distinction is the point. A zero-knowledge proof can verify the accounts, receipts, outcomes, signatures, and arithmetic that an operator chooses to disclose. It cannot prove that no other accounts, liabilities, or off-platform obligations exist. Any article that blurs those two claims is overstating what proof-of-reserves technology can do.

The contribution here is narrower and testable: for one disclosed account set, SP1 verifies six legs across six verification domains and commits the resulting balance-sheet buckets on-chain. The public output contains no addresses and no private position sizes. It contains the buckets, the policy hash, and the evidence tier of every leg.

This is a demonstration run on a deliberately small account set. The point is the verification mechanism, not the amount of capital in the example.

In the NAVCoin architecture, this is a reserve-evidence primitive. The [NAVCoin proposal](/blog/navcoin-proposal/) defines machine-verified NAV packets that gate minting and redemption; the [counterparty-risk extension](/blog/navcoin-counterparty-risk/) adds venue credit risk as a separate observable field. This post supplies a live example of one packet component: a disclosed portfolio slice whose assets, liabilities, venue exposure, and evidence tiers can be checked without revealing every private position.

Terminology: SP1 is the zero-knowledge virtual machine that runs the verifier logic, Groth16 is the succinct proof checked on-chain, and `USD-e8` means fixed-point dollars with eight decimal places.

## Public Result

The verified public values were:

| Bucket | USD | Detail |
|---|---:|---|
| Spot | **$20,529.43** | locked $10,794.80; unlocked $9,734.62 |
| Cash | **$3,319.24** | locked $3,230.52; unlocked $88.72 |
| Gross perpetual notional | **$24,233.27** | no directional netting |
| Liability | **$199.97** | Aave debt |

The disclosed reserve base is spot plus cash: **$20,529.43 + $3,319.24 = $23,848.67**. The gross perp notional ratio is **$24,233.27 / $23,848.67 = 1.016x**. The Aave liability ratio is **$199.97 / $23,848.67 = 0.84%**.

Those are not solvency ratios. They are ratios over the disclosed account set only. Their value is that the numbers can be independently checked against the proof, not that they close the completeness problem.

## Evidence Coverage

The proof publishes two evidence tiers per leg:

- **Quantity tier**: how the unit amount was established.
- **Valuation tier**: how the USD conversion was established.

The denominator matters, so the reserve coverage is stated explicitly:

| Reserve quantity tier | USD-e8 basis | Approx. USD | Share of disclosed spot+cash |
|---|---:|---:|---:|
| Cryptographic quantity | `2284664144120` | $22,846.64 | 95.80% |
| Attested quantity | `100202589000` | $1,002.03 | 4.20% |
| Total disclosed reserves | `2384866733120` | $23,848.67 | 100.00% |

This table is only about reserve quantities: spot and cash. It excludes gross perp notional and liability because those are separate risk buckets, not reserve assets. The entire attested-quantity remainder is a single leg — the Solana stake.

Valuation is a different axis. Aave and Hyperliquid valuations are cryptographic under their chain/oracle assumptions. NEAR, EVM spot, Solana, and Monero USD prices are attested to the committed valuation policy.

## Leg Disclosures

| Leg | Verification domain | Quantity | Valuation |
|---|---|---|---|
| Aave debt + collateral | Arbitrum | cryptographic | cryptographic |
| Hyperliquid account | HyperEVM / HyperCore | cryptographic | cryptographic |
| NEAR staking | NEAR | cryptographic | attested |
| EVM spot | Ethereum | cryptographic | attested |
| Solana stake | Solana | attested | attested |
| Monero reserve | Monero | cryptographic | attested |

The evidence model has three rungs, and this run uses two of them:

- **Cryptographic** — the proof checks a chain, receipt, outcome, or storage commitment under the source system's own consensus. A false value would require forging that chain's consensus. It does not mean "trustless in every possible sense."
- **TEE-attested** — the value is computed by open, reproducibly-built code running in a hardware enclave whose code measurement and output signature are independently verifiable. This removes operator discretion but trusts the enclave vendor, not source-chain consensus — strictly weaker than cryptographic. No leg uses it in this run; it is named because it is the upgrade path for the attested lines, not a tier we are claiming here.
- **Attested** — a named signer, reserve proof, or policy source supplies the value, and the proof binds that value to the published policy.

Two legs are worth a closer look — the Monero reserve and the Solana stake.

**Monero** is bounded enough to verify in-circuit. The SP1 guest checks the reserve proof's ownership signatures, key-image ring signature, RingCT amount opening, and the output's inclusion in a Monero block. That makes the *control, amount, and existence* of the reserve cryptographic. The one thing it cannot prove in-circuit — that the outputs are unspent, since Monero commits no spent-key-image accumulator — is handled by committing the key images for anyone to check against the chain, rather than asserting it.

**Solana** is the genuinely hard case, and it is hard for a specific, checkable reason: Solana replaced its Merkle accounts hash with a homomorphic lattice hash and removed the per-slot delta hash, so there is no longer an openable per-account commitment to prove a balance against — the inclusion-proof technique that works for the other chains has no Solana analog. A cheap chain-consensus proof is therefore not available today. Its realistic upgrade is **TEE-attested** — an open, reproducibly-built enclave computing the balance from finalized state and attesting the computation — which is stronger than an operator read but is not, and should not be labeled, a consensus proof. We mark it `attested` here and `TEE-attested` on the roadmap rather than dress it up as cryptographic.

## Why The Buckets Are Separated

The public values deliberately avoid a single net number.

Cash is not exposure. Spot is not cash. Locked value is not as liquid as unlocked value. Gross perp notional is not a borrow, and a short perp is not automatically a liability. Aave debt is a liability. Netting these together would encode an opinion about hedging and liquidity.

The v2 public values therefore report independent buckets:

- spot locked and spot unlocked;
- cash locked and cash unlocked;
- gross perpetual notional;
- liability.

Readers can compute their own ratios. The proof does not choose a flattering one.

## How The Two Largest Non-Aave Lines Are Proven

The Hyperliquid and NEAR legs are the important mechanism tests.

**Hyperliquid.** HyperCore does not expose a per-account state proof. HyperEVM does commit a standard Ethereum `receiptsRoot`. A reader contract calls HyperCore precompiles for the disclosed account, emits one canonical snapshot event, and the SP1 guest verifies the event's transaction receipt against the HyperEVM block header. The same snapshot includes HyperCore price data, so both quantity and valuation are cryptographic under Hyperliquid's consensus and precompile semantics.

**NEAR.** Public RPC does not serve the staking-pool storage proof we need. A NEAR reader contract instead records the staking-pool callback result. The SP1 guest verifies the callback execution outcome to the block `outcome_root`, folds that block to the light-client head's `block_merkle_root`, and checks the validator-endorsed head. The staking-pool code hash is pinned. Quantity is cryptographic under NEAR consensus; USD valuation remains attested.

These proofs do not establish that the operator disclosed every account. They establish that the included Hyperliquid and NEAR quantities were not invented in a signed spreadsheet.

## Verification Artifact

This run was verified on Arbitrum One using the real SP1 Groth16 verifier contract, not a mock:

- Chain: Arbitrum One (`42161`)
- Submission transaction: [`0x996022d2...6bd75f08`](https://arbiscan.io/tx/0x996022d255ca9052f16a5632a3c9747f7e796a0c4c32c22d7da895c76bd75f08)
- Program verification key: `0x004d1cd3f36e6ea60662af428edbea9d3aba45f04fe496da909d6bbe9fbf9258`
- Valuation policy hash: `0x8fcf3cd44c8180744563e85579ed91b7fd3882e560dc41ea4dc0c18cb01f289d`
- SP1 Groth16 verifier: [`0xA2F0Dc64C77C3a219f5AFfBac96376d0DF27Cc1E`](https://arbiscan.io/address/0xA2F0Dc64C77C3a219f5AFfBac96376d0DF27Cc1E)
- `StakeHubLeverageVerifier`: [`0x3F40563A3D786d008854f046A78Cc2216ceAC3e1`](https://arbiscan.io/address/0x3F40563A3D786d008854f046A78Cc2216ceAC3e1)
- Gas used for `submitExposure`: **1,195,653**
- HyperEVM anchor: block `37,755,877`
- NEAR anchor: block `202,590,562`
- Monero anchor: reserve proof at block `3,695,719`

The full first verification cost was **$0.2283** at the stated gas and ETH assumptions. Reusing the verifier leaves only the `submitExposure` call, about **$0.04** under the same assumptions.

## How To Independently Check It

The public check is self-contained in the [`postfiatorg.github.io`](https://github.com/postfiatorg/postfiatorg.github.io) repository, in [`scripts/verify_proof_of_leverage.py`](https://github.com/postfiatorg/postfiatorg.github.io/blob/main/scripts/verify_proof_of_leverage.py):

```bash
python3 scripts/verify_proof_of_leverage.py
```

The script uses only Python's standard library and Arbitrum JSON-RPC. It calls `latest()` and `programVKey()` on the `StakeHubLeverageVerifier`, decodes the ABI return, and checks that the public buckets, policy hash, verification key, leg count, and per-leg evidence tiers match this article.

A successful run ends with the same public values:

```text
spot_total_usd_e8=2052942777620 ($20,529.43)
cash_total_usd_e8=331923955500 ($3,319.24)
perp_notional_total_usd_e8=2423326655000 ($24,233.27)
liability_usd_e8=19997391450 ($199.97)
leg_count=6
verification=PASS
```

This verifies the public artifact. Full hidden-input reproduction is a stronger check and requires the evidence bundle used to generate the proof. Without that bundle, a reader can verify proof acceptance and the on-chain public values, but cannot rerun the private witness computation.

## What This Does Not Prove

- It does not prove total assets.
- It does not prove total liabilities.
- It does not prove that no other exchange accounts or wallets exist.
- It does not prove legal solvency.
- It does not make attested prices cryptographic.
- It does not make a bad valuation policy good.
- It does not turn a TEE-attested line into a consensus proof. Where a value would be computed in a hardware enclave (the upgrade path for the attested lines), the trust is the enclave code plus its hardware vendor — reducible with open, reproducible code and multiple vendors, but never a source-chain proof.

The proof makes a narrower disclosure much harder to fake. For the disclosed account set, it verifies the included evidence, computes the buckets in-circuit, independently reconciles them before proving, and publishes exactly which lines are cryptographic and which remain attested.

That is enough to be useful. It is not enough to be called a complete solvency proof.
