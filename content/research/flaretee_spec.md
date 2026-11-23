---
title: "NAVCoin Proof-of-Reserves and Flare Confidential Compute"
date: 2026-11-23T00:00:00Z
url: "/research/flaretee_spec/"
summary: "What Post Fiat's NAVCoin protocol is, how B24 (a live Schwab-backed NAVCoin) proves brokerage reserves via AWS Nitro and SP1, how Flare Confidential Compute's USDX oracle compares in code, and three concrete integration options."
description: "Technical comparison and integration specification for Post Fiat NAVCoins (B24 case study) and Flare Confidential Compute (FCC / USDX oracle), with commit-pinned source references."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - PFTL
  - Flare
  - TEE
  - SP1
  - Proof of Reserves
  - Schwab
draft: false
---

Every technical claim below links directly to the exact repository, file, commit, and line range in Post Fiat (`postfiatorg/postfiatl1v2`) and Flare (`flare-foundation/*`).

---

## 1. The 60-second version

- **What Post Fiat already has live:** Post Fiat L1 (PFTL) has a native protocol asset class called a **NAVCoin** — a floating-value token backed by a reserve portfolio whose minting, supply caps, and redemption are mechanically gated by machine-verified Net Asset Value (NAV) proofs inside L1 consensus. **B24 is not separate technology; it is one live NAVCoin running on that protocol**, backed by a Charles Schwab brokerage account plus an on-chain reserve (alongside sibling NAVCoins like `A666` and `BMNRC`, and wrapped on Ethereum mainnet as `wB24`). For B24's proof profile, an AWS Nitro Enclave reads Schwab's API, an SP1 zero-knowledge proof checks the AWS hardware attestation, and all six PFTL validators verify the ZK proof before updating NAV. On 23 November 2026 (epoch 9), B24 finalized at **$1.006419/token** backed by **$428,053.70** ($423,033.09 at Schwab + $5,020.61 on-chain reserve) across 425,323.38 tokens.
- **What Flare has:** **Flare Confidential Compute (FCC)** runs workloads inside Google Cloud Confidential Space VMs (TEEs) governed by Flare's data-provider quorum. Its first live product (on Songbird) is an oracle for Hex Trust's USDX stablecoin.
- **Where they compare and fit:** Both systems use hardware enclaves to keep operators from faking off-chain numbers, but they made opposite choices on *who checks the hardware proof* (a ZK proof verified by every validator vs. an off-chain vote by Flare data providers) and *where inputs come from* (direct from the broker API vs. the issuer's own endpoints). Because Post Fiat's NAVCoin stack already includes ownerless EVM verifier contracts that check SP1 proofs and PFTL finality, **we can publish proven NAVCoin prices (starting with B24) directly onto Flare EVM today (Option A)**, and evaluate using Google Confidential Space TEEs as a second independent hardware vendor alongside AWS Nitro once third-party extensions are live on Flare mainnet (Option B).

---

## 2. What a NAVCoin is on Post Fiat (and where B24 fits)

Before comparing AWS Nitro and Flare, it helps to separate the **protocol** (NAVCoins) from one **asset instance** (B24).

**A NAVCoin is Post Fiat L1's native asset class for portfolio-backed tokens.** Traditional stablecoins promise a $1 peg backed by an opaque issuer balance sheet, keep the yield for the issuer, and publish monthly or quarterly PDF attestations with zero mechanical link to the token contract — an attestation cannot block a mint or halt stale issuance. A NAVCoin flips that model ([The NAVCoin Proposal](/blog/navcoin-proposal/)):

- **Floating NAV, not a peg:** Every unit tracks `NAV = verified_net_assets / circulating_supply`. If the reserve portfolio earns yield or appreciates, NAV rises for holders; if it declines, NAV declines.
- **Verification is enforced by L1 consensus, not a PDF:** Native PFTL transaction types govern every NAVCoin's lifecycle — `nav_profile_register`, `nav_asset_register` ([`transactions_mempool_receipts.rs:589`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/types/src/transactions_mempool_receipts.rs#L589)), `nav_reserve_submit`, `nav_epoch_finalize`, `nav_mint_at_nav`, `nav_redeem_at_nav`, `nav_reserve_challenge`, and `nav_halt`. Consensus itself enforces `circulating_supply × nav_per_unit <= verified_net_assets` ([`market_nav_asset_types.rs:999-1041`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/types/src/market_nav_asset_types.rs#L999-L1041)), rejects mints past the finalized epoch's supply cap (`nav_supply_cap_exceeded`, [`nft_escrow_asset_execution.rs:2456`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/execution/src/nft_escrow_asset_execution.rs#L2456)), rejects stale epochs (`nav_epoch_mismatch`, [`nav_vault_asset_execution.rs:8469`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/execution/src/nav_vault_asset_execution.rs#L8469)), and pays holders who burn at NAV from an on-chain PFUSDC reserve.
- **Pluggable proof profiles by venue:** Each NAVCoin registers against an immutable, content-addressed `NavProofProfile` ([`account_owned_asset_types.rs:3510`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/types/src/account_owned_asset_types.rs#L3510)) specifying *what counts as valid proof* for where its reserves actually sit:
  - `ledger-transparent` — reserves live in native PFTL accounts; consensus sums the balances directly.
  - `multi-fetch-quorum` — public external venues (such as Hyperliquid vaults) observed by independent bonded attestors.
  - `sp1-groth16` ([`tools/nav-reserve-proof`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/tools/nav-reserve-proof/README.md)) — zero-knowledge proofs verified in consensus, with venue adapters for EVM ERC-20 checkpoints, Solana/NEAR/Monero/Hyperliquid receipts, or **hardware-attested brokerage APIs**.
- **Shared market and cross-chain rails:** Any NAVCoin can trade on PFTL's native order book, swap privately through Asset-Orchard, and bridge to EVM chains as a wrapped ERC-20 via Post Fiat's proof-native verifier stack (`PFTLReceiptFinalityVerifierV2` + `PFTLUniswapPrimaryMarketV2`).

> **Where B24 fits:** **B24 is one live NAVCoin built on this exact protocol** — specifically Post Fiat's Charles Schwab-backed NAVCoin (following the same rail as `A666`, `BMNRC`, and earlier Schwab test asset `B23`; see [Schwab NAVCoin (B24): Status and Handoff](/research/schwab-navcoin-handoff/)). B24 uses the `sp1-groth16` verifier kind with an AWS Nitro Enclave proof profile (`d5f81a8d…569b42a2`) because a brokerage account sits behind private OAuth credentials rather than a public blockchain. On Ethereum mainnet, B24 already wraps to `wB24` (`0x540FDa223a2198690d31920a921A0b9DfF335dbF`) and trades in a live Uniswap v4 `wB24/USDC` pool.

---

## 3. How B24's Schwab proof profile works

Because B24's reserves live inside a Charles Schwab brokerage account, its `sp1-groth16` proof profile solves two problems that public-chain NAVCoins do not face: (1) you cannot put Schwab OAuth credentials on a public blockchain, and (2) token holders should not have to take Post Fiat's word for the balance. B24 splits the work across three layers — Nitro Enclave, SP1 zkVM, and PFTL's standard NAVCoin consensus check — so the operator can run the job without ever being able to forge a balance.

![B24 end-to-end architecture for a single NAV reading](/research/flaretee_spec/b24-architecture.png)

### Layer 1: AWS Nitro Enclave reads Schwab directly (and KMS locks credentials to exact code)

A Nitro Enclave is an isolated AWS virtual machine with no SSH, no persistent disk, and no operator console. At boot, the Nitro hypervisor hashes its kernel, OS, and application code into three Platform Configuration Registers (`PCR0`, `PCR1`, `PCR2`).

- **Credentials only unlock for the exact binary:** Before a run, the operator encrypts Schwab's OAuth credentials under a fresh AWS KMS key whose policy explicitly denies plaintext decryption (`DenyPlaintextRelease`) and allows `kms:Decrypt` only when the caller presents a Nitro hardware attestation matching the exact expected `PCR0/1/2` hashes ([`qualification_kms.py:29-41`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/operator/qualification_kms.py#L29-L41)).
- **Locked-down Schwab client inside the enclave:** Inside the enclave, `SchwabAccountClient` hardcodes `transport.host == "api.schwabapi.com"` and refuses any HTTP path except `/trader/v1/accounts/accountNumbers` and the single matched account's balance endpoint. It extracts `securitiesAccount.currentBalances.liquidationValue`, enforces a 60-second cutoff window using Nitro's hardware clock, encrypts the raw HTTP bodies to an audit archive, and asks the Nitro Security Module (NSM) to sign an attestation binding the reading and an ephemeral Ed25519 key to `PCR0..2` ([`nav_reading.py:119-160`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/pftl_schwab_tee/nav_reading.py#L119-L160)).

### Layer 2: SP1 zero-knowledge proof checks the AWS hardware signature

Validators and smart contracts should not parse AWS COSE/CBOR envelopes and X.509 certificate chains directly in consensus, nor should raw Schwab JSON touch the chain. Instead, a GPU runs the SP1 zkVM program `b23-nav-guest` ([`b23-nav-guest/src/main.rs:5-17`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/programs/b23-nav-guest/src/main.rs#L5-L17)), which calls `b23_nav::execute()` ([`b23_nav.rs:141-260`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L141-L260)) to prove six invariants inside a compact Groth16 proof:

1. The Nitro attestation document chains cleanly to AWS's pinned root certificate via `verify_nitro_document()` ([`yolo_nitro.rs:164`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/yolo_nitro.rs#L164)).
2. The enclave's `PCR0`, `PCR1`, and `PCR2` match the asset's pinned policy exactly ([`b23_nav.rs:232-240`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L232-L240)).
3. The hardware timestamp falls inside the 65-second reading window after the manifest's cutoff ([`b23_nav.rs:175-183`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L175-L183)).
4. The enclave's Ed25519 signature over the reading digest is valid under the public key embedded inside the Nitro attestation ([`b23_nav.rs:250-260`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L250-L260)).
5. The reading came from the committed account hash and the exact field `securitiesAccount.currentBalances.liquidationValue` ([`b23_nav.rs:184-187`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L184-L187)).
6. The output commits to `NavReservePublicValuesV1` — the exact 584-byte ABI PFTL validators check on-chain.

### Layer 3: Every PFTL validator verifies the Groth16 proof in consensus

When `nav_reserve_submit` arrives, every PFTL validator runs the same deterministic check in [`nft_escrow_asset_execution.rs:1421-1560`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/execution/src/nft_escrow_asset_execution.rs#L1421-L1560):

- Rejects stale or replayed epochs (`operation.epoch <= nav_asset.finalized_epoch`) and mismatched proof profiles (lines 1467–1478).
- Subtracts the ledger's own on-chain B24 subscription reserve (`nav_subscription_reserve_overlay`) from total submitted net assets so the SP1 proof is verified specifically against the off-chain Schwab portion (lines 1540–1554).
- Runs `verify_sp1_groth16_with_options()` against the asset's pinned SP1 verifying key and checks collateralization math against on-chain circulating supply (lines 1448–1454, 1555–1560).

---

## 4. Walkthrough of one daily reading

The daily run is orchestrated by [`ops/b24-live/daily.py:95-174`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L95-L174), takes roughly 15 minutes, and costs about $8 of ephemeral AWS compute. Every stage records its outcome and halts immediately on any mismatch.

| # | Stage | What runs | Code reference |
|---|---|---|---|
| 1 | Fleet check | Queries all 6 validators and confirms every node runs the exact pinned binary hash. | [`daily.py:137-142`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L137-L142) |
| 2 | Chain read | Exports PFTL state and checks `finalized_epoch + 1 == observation_epoch`, matching proof profile, and asset not halted. | [`daily.py:118-119`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L118-L119) |
| 3 | Budget cap | Verifies no stale EC2 instances exist and reserves run spend (capped at $9/run, $250/month). | [`daily.py:127-129`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L127-L129) |
| 4 | Reproducible build | Ephemeral EC2 host builds the Nitro enclave image twice from committed source and asserts identical `PCR0..2`. | [`schwab-tee/enclave/Dockerfile`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/enclave/Dockerfile) |
| 5 | KMS seal & read | Seals Schwab creds to a KMS key restricted to those PCRs; enclave opens TLS to `api.schwabapi.com` and gets Nitro attestation. | [`nav_reading.py:147-160`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/pftl_schwab_tee/nav_reading.py#L147-L160) |
| 6 | Teardown | Destroys EC2 and KMS resources and asserts `noOwnedBillableComputeRemaining`. | [`daily.py:130`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L130) |
| 7 | Native verification | Checks the encrypted audit archive and runs negative tests (ensuring tampered readings are rejected) before paying GPU prover time. | [`daily.py:132-134`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L132-L134) |
| 8 | SP1 Groth16 proof | GPU runs `b23-nav-guest` to produce `public-values.bin` and `proof-calldata.bin`. | [`daily.py:135`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L135) |
| 9 | Canary rehearsal | Replays all 3 transactions on a local copy of live chain state, verifying a corrupted proof fails and the real proof succeeds. | [`daily.py:166`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L166) |
| 10 | Submit & confirm | Broadcasts `nav_reserve_submit`, `nav_epoch_finalize`, and route pricing; polls all 6 validators until the epoch lands. | [`daily.py:167-169`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/ops/b24-live/daily.py#L167-L169) |

---

## 5. What you actually have to trust

Every number in B24's epoch 9 NAV ($1.006419) comes from either **attested hardware** or **L1 consensus** — never from an operator signature:

| Component (Epoch 9) | Value | Evidence class | Who you trust |
|---|---|---|---|
| Schwab account liquidation value | $423,033.09 | **Attested** — TLS inside Nitro, NSM-signed, verified in SP1 | AWS Nitro hardware & root CA; Schwab API; reproducible enclave source |
| On-chain B24 reserve balance | $5,020.61 | **Consensus** — counted directly by PFTL state machine | PFTL validator set |
| B24 circulating supply | 425,323.38 | **Consensus** — PFTL ledger supply | PFTL validator set |
| NAV per B24 | **1.006419** | Arithmetic verified in consensus: `$428,053.70 / 425,323.38` | Nothing extra |

**What the Post Fiat operator cannot do:** fabricate a balance, substitute different enclave code without changing the on-chain proof profile, or replay an old reading. **What the operator can still do:** fail to run the job (liveness/censorship), which shows up immediately as a stale epoch. And because only AWS Nitro reads Schwab today, a break in AWS Nitro hardware security is a single-vendor trust assumption (which is what Option B addresses).

---

## 6. How Flare's USDX oracle works

Flare's closest live equivalent to a brokerage-backed NAVCoin is the **USDX price oracle** ([`flare-foundation/fce-usdx-oracle`](https://github.com/flare-foundation/fce-usdx-oracle), running on [`flare-foundation/tee-node`](https://github.com/flare-foundation/tee-node)). Because Hex Trust's USDX has no liquid secondary market, the oracle computes a collateralization price inside Google Cloud Confidential Space VMs:

`price = min(1, (bond_reserves + cash_reserves) / total_supply_across_3_chains)` — implemented in [`fce-usdx-oracle/price.go:22-55`](https://github.com/flare-foundation/fce-usdx-oracle/blob/7d3e4c05635f1d0912ec8e8435425394f65ce408/internal/observation/price/price.go#L22-L55).

![Flare Confidential Compute USDX oracle architecture as implemented](/research/flaretee_spec/flare-usdx-architecture.png)

Reading the Go implementation and security docs reveals four concrete design differences from Post Fiat's NAVCoin stack:

- **Hardware attestation is checked off-chain by data providers, not by a smart contract or ZK proof.** When a Flare TEE boots, `GetGoogleAttestationToken()` requests a Google Confidential Space OIDC JWT containing the container digest and hardware claims ([`tee-node/attestation_token.go:33`](https://github.com/flare-foundation/tee-node/blob/c0281c7cd0e0643ef86c7b273e08c14d51eb5a7f/internal/attestation/attestation_token.go#L33)). Flare data providers validate that JWT off-chain via [`go-verifier-api`](https://github.com/flare-foundation/go-verifier-api) and vote the machine's key into an on-chain registry ([`TeeAvailabilityCheck`](https://github.com/flare-foundation/flare-specs/blob/main/src/FDC2/Reference/AttestationTypes/TeeAvailabilityCheck.md)). Earlier Solidity work to verify Google JWTs directly on-chain exists in [`FlareVtpmAttestation.sol:129`](https://github.com/flare-foundation/flare-vtpm-attestation/blob/13d798541484720a4777c68eb0338255aa15989c/contracts/FlareVtpmAttestation.sol#L129), but FCC does not use it in production today.
- **A data-provider majority controls the TEE.** The TEE accepts instructions cosigned by data providers holding >50% of signing weight for the active reward epoch ([`tee-node/policy.go:39-114`](https://github.com/flare-foundation/tee-node/blob/c0281c7cd0e0643ef86c7b273e08c14d51eb5a7f/internal/policy/policy.go#L39-L114)). Flare's own security documentation states this plainly: *"A majority of data providers (by voting weight) can construct and sign arbitrary instructions that the TEE will accept."* ([`tee-node/docs/security.md:52-56`](https://github.com/flare-foundation/tee-node/blob/c0281c7cd0e0643ef86c7b273e08c14d51eb5a7f/docs/security.md#L52-L56))
- **Inputs come from the issuer, not the custodian.** The USDX oracle polls Hex Trust's own public bond API and a restricted Hex cash API whose URL is hidden behind a governance-committed hash provisioned via `SET_SECRET` ([`provisioning.go:26-51`](https://github.com/flare-foundation/fce-usdx-oracle/blob/7d3e4c05635f1d0912ec8e8435425394f65ce408/internal/extension/provisioning.go#L26-L51), [`README.md:104-112`](https://github.com/flare-foundation/fce-usdx-oracle/blob/7d3e4c05635f1d0912ec8e8435425394f65ce408/README.md#L104-L112)). Consumers verify that the enclave ran the approved formula, but still trust Hex Trust's API and governance's choice of URL.
- **Ephemeral memory-only state.** Because `tee-node` enforces a 2-second action timeout, the oracle polls every 2 minutes in the background and signs cached readings. Restarting a machine wipes its in-memory keys and credentials, requiring M-of-N admins to re-provision secrets over the proxy's direct channel ([`README.md:60-82`](https://github.com/flare-foundation/fce-usdx-oracle/blob/7d3e4c05635f1d0912ec8e8435425394f65ce408/README.md#L60-L82)).

---

## 7. Side-by-side comparison

| Dimension | Post Fiat NAVCoin (B24 Schwab profile) | Flare FCC (USDX Oracle) |
|---|---|---|
| Data source | Broker directly: `api.schwabapi.com` hardcoded in enclave ([`nav_reading.py:123`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/pftl_schwab_tee/nav_reading.py#L123)) | Issuer APIs (Hex Trust bond + restricted cash URL committed by governance hash) |
| TEE hardware | AWS Nitro Enclaves (ephemeral EC2 per reading) | Google Confidential Space (AMD SEV / Intel TDX, persistent VMs) |
| How attestation is verified | Inside an SP1 Groth16 proof verified by every PFTL validator ([`nft_escrow_asset_execution.rs:1555`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/execution/src/nft_escrow_asset_execution.rs#L1555)) | Off-chain by Flare data providers (`go-verifier-api`), then voted into an on-chain machine registry |
| Credential handling | Sealed per run via AWS KMS `PCR0/1/2` policy; zero persistent state needed | Encrypted via ECIES by M-of-N admins into RAM; wiped on VM restart |
| Who triggers updates | Operator cron / on-demand script (no signing power) | Permissionless keeper tx → cosigned by >50% data-provider weight |
| Cadence & cost | Daily or on-demand (~15 min, ~$8 AWS) | Polls every 2 minutes; per-instruction fees |
| Main remaining risk | Single hardware vendor (AWS Nitro); operator can delay/withhold a run | Issuer-reported inputs; >50% provider quorum authority; Flare Foundation runs launch nodes |

---

## 8. Where Post Fiat and Flare fit together

There are three concrete ways to work together, ordered from "can ship today using existing NAVCoin code" to "requires Flare mainnet changes."

![Joint options A and B: relaying proven B24 NAV to Flare EVM and adding Google Confidential Space as a second independent hardware reader](/research/flaretee_spec/joint-options.png)

### Option A: Bring Post Fiat NAVCoin prices (starting with B24) onto Flare *(buildable today)*

- **Plain English:** Post Fiat's NAVCoin protocol already produces a cryptographically proven NAV every epoch for B24 (and any other SP1-proven NAVCoin on PFTL). Option A publishes that proven NAV onto Flare EVM so Flare DeFi protocols (lending markets, DEX pools, FTSO custom feeds, or FAssets collateral) can read a NAVCoin's price directly — **without trusting Post Fiat's relayer or Flare's data providers**.
- **Why this is mostly redeploying existing NAVCoin infrastructure:** Post Fiat's NAVCoin wrapping stack on Ethereum (already live for `wB24` and `A666`) uses two ownerless Solidity verifier patterns that can be deployed directly onto Flare EVM:
  1. **SP1 Groth16 proof verifier on EVM** — Succinct's standard `ISP1Verifier.verifyProof(programVKey, publicValues, proofBytes)` interface, already wired into [`PFTLReceiptFinalityVerifierV2.sol:4-6`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/ethereum-contracts/src/PFTLReceiptFinalityVerifierV2.sol#L4-L6) and [`PFTLFinalityVerifierV1.sol:5-7`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/ethereum-contracts/src/PFTLFinalityVerifierV1.sol#L5-L7).
  2. **Trustless PFTL finality verifier on EVM** — `PFTLReceiptFinalityVerifierV2` verifies a PFTL finalized block back to an immutable genesis ancestry anchor (`ancestryAnchorCommitment`) with strict ordering and replay protection, paired with the wrapped-token mint/burn controller in [`PFTLUniswapPrimaryMarketV2.sol:24-55`](https://github.com/postfiatorg/postfiatl1v2/blob/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd/crates/ethereum-contracts/src/PFTLUniswapPrimaryMarketV2.sol#L24-L55).
- **Why Flare needs both checks (not just the Schwab proof):** The B24 SP1 proof ([`b23_nav.rs:141`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L141)) proves the *Schwab account balance* ($423,033.09). To know the *NAV per token* ($1.006419), Flare also needs B24's circulating supply (425,323.38) and on-chain reserve ($5,020.61), which live in PFTL state. Verifying PFTL finality on Flare gives Flare contracts the finalized epoch's exact NAV — backed by the SP1 proof PFTL's own validators already verified — with zero multisigs in the middle.
- **Division of work:** Post Fiat deploys the SP1 + PFTL finality verifier contracts on Flare and relays each finalized epoch; Flare registers the resulting contract as an FTSO custom feed (the same `IICustomFeed` interface USDX uses) and evaluates B24/wB24 as collateral.

### Option B: Add Flare as a second, independent hardware reader *(needs Flare mainnet FCC)*

- **Plain English:** Right now, B24's single hardware assumption is AWS Nitro. If someone compromised AWS Nitro's silicon or AWS's root attestation key, they could forge a Schwab balance. Option B runs a second copy of the Schwab balance reader inside Flare's Google Cloud Confidential Space VMs (AMD SEV / Intel TDX) at the exact same cutoff time. PFTL only accepts the reading if **both AWS Nitro and Google Confidential Space agree** — meaning an attacker would have to break Amazon and Google's confidential hardware simultaneously.
- **Concrete engineering work required:**
  1. Port the locked-down Schwab HTTP reader ([`nav_reading.py:119-160`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/pftl_schwab_tee/nav_reading.py#L119-L160)) into a Flare Confidential Extension (FCE) running alongside `tee-node`.
  2. Extend the SP1 guest ([`b23_nav.rs:141-260`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs#L141-L260)) so it verifies *both* the AWS Nitro COSE document (`yolo_nitro.rs:164`) and Google's Confidential Space RSA-signed OIDC JWT (the same checks Flare's `go-verifier-api` runs off-chain and [`FlareVtpmAttestation.sol:129`](https://github.com/flare-foundation/flare-vtpm-attestation/blob/13d798541484720a4777c68eb0338255aa15989c/contracts/FlareVtpmAttestation.sol#L129) prototyped in Solidity), and asserts that both readings agree within tolerance.

> **Why Option A comes first:** Two real blockers prevent Option B from shipping today: (1) Flare has not yet opened FCC on Flare mainnet for third-party developers to register custom extensions, and (2) Schwab OAuth refresh tokens rotate on every use, whereas Flare's `tee-node` keeps credentials strictly in RAM and wipes them on restart ([`fce-usdx-oracle/README.md:76-82`](https://github.com/flare-foundation/fce-usdx-oracle/blob/7d3e4c05635f1d0912ec8e8435425394f65ce408/README.md#L76-L82)), requiring a clean rotation or re-sealing flow.

### Option C: Broker-direct reader template for Flare FCC issuers *(shared pattern)*

Flare's USDX oracle currently reads Hex Trust's *own* reserve endpoints rather than the underlying bank or custodian. Post Fiat can share the `schwab-tee` architecture — hardcoded custodian hostname, TLS terminating inside the enclave, strict 60-second cutoff window, and encrypted raw-response audit archive ([`verify_nav_archive.py`](https://github.com/postfiatorg/postfiatl1v2/blob/44f6dcf9a59fcf944be9af4105284a35a16b223e/tools/nav-reserve-proof/schwab-tee/operator/verify_nav_archive.py)) — so Flare can offer a custodian-direct FCE template to future reserve-backed issuers.

---

## 9. Open questions for Flare

These eight questions determine whether Options A, B, and C are worth scoping into a build:

1. **Mainnet timeline:** When does FCC launch on Flare mainnet, and when can external teams register custom extensions and TEE machines?
2. **Hardware & operators:** Who besides the Flare Foundation will operate TEE nodes, and is AWS Nitro planned alongside Google Cloud Confidential Space?
3. **Cross-chain verifiability:** Will FCC publish the raw Google Confidential Space JWT alongside signed outputs so an external verifier (such as our SP1 guest) can check it without following Flare's consensus?
4. **On-chain attestation:** Are there plans to revive on-chain JWT/vTPM verification ([`FlareVtpmAttestation.sol`](https://github.com/flare-foundation/flare-vtpm-attestation/blob/13d798541484720a4777c68eb0338255aa15989c/contracts/FlareVtpmAttestation.sol#L129)) instead of relying on the data-provider registry vote?
5. **Rotating OAuth tokens:** What is the recommended pattern in FCC for credentials (like Schwab's OAuth refresh token) that rotate on every use, given that restarts wipe RAM?
6. **Custodian-direct USDX:** Has Hex Trust considered reading its bank/custodian API directly inside the TEE rather than its own reserve endpoint?
7. **Listing NAVCoins on Flare:** What is the process to register an externally ZK-proven NAV feed (Option A) as an FTSO custom feed or FAssets collateral?
8. **Economics:** What do instruction fees, operator incentives, and issuer integration programs look like on mainnet?

---

## 10. Appendix: live epoch 9 receipts & verified source index

### B24 Epoch 9 on PFTL (`postfiat-wan-devnet-2`, 23 November 2026)

Verified across all six validators:
- **Asset ID:** `52285e4ded1d58113cfaa12bbc034b8b10213f699b3224c74160450229d6bf7ccfe505c78f2599d975ae2ecf98f7d8af`
- **Proof profile:** `d5f81a8d778308fed92d4106ab8aae746cf0304b9f6de46f130d9a7e9f1e02d7ea1b787cccb4a607d12f3fbd569b42a2`
- **Reserve packet:** `71b4e86c8bcd5a9b7dd53386dbe852bb9974c2699ee015461d77a6120c5e7af4902aecb4dddc2765b7342fe6b8b68c63`

| Step | Height | Transaction ID | Status |
|---|---|---|---|
| Submit reading | 1842 | `c3905ed74e66b000a5b8f14c120545bf726ad22aff84ff7413ef15943eb7f55b226341ab56bceb415e61f683340023c0` | Accepted on 6/6 |
| Finalize epoch | 1843 | `8c8fcd57c1726ee59852402c5c477cf24fb6a5e452f84cdbd4fe2677b1505b81094f0a1e826d65fb31f1093d1d424a62` | Accepted on 6/6 |
| Route pricing | 1844 | `0cb48eaadcca791618fbd5c333cb3fcdf38370389a960d26d1a458c46430cae0b1803783b9fbcd34dc2529c3106e2194` | Accepted on 6/6 |

### Verified source code index

| Repository & commit | Key files | Role |
|---|---|---|
| [`postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2/tree/a437eb5c880ca75e7e10118a9ce1fdca6a42f1dd) `a437eb5c` (`main`) | `crates/execution/src/nft_escrow_asset_execution.rs`, `crates/types/src/market_nav_asset_types.rs`, `crates/types/src/account_owned_asset_types.rs`, `crates/ethereum-contracts/src/PFTLReceiptFinalityVerifierV2.sol`, `crates/ethereum-contracts/src/PFTLUniswapPrimaryMarketV2.sol`, `ops/b24-live/daily.py` | NAVCoin consensus SP1 verification & invariants, EVM SP1 + ancestry finality verifier, wrapped NAVCoin primary market controller, 12-stage daily runner |
| [`postfiatl1v2` PR #220](https://github.com/postfiatorg/postfiatl1v2/pull/220) `44f6dcf9` | `tools/nav-reserve-proof/schwab-tee/pftl_schwab_tee/nav_reading.py`, `tools/nav-reserve-proof/schwab-tee/operator/qualification_kms.py`, `tools/nav-reserve-proof/programs/b23-nav-guest/src/main.rs`, `tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs`, `tools/nav-reserve-proof/crates/reserve-proof-types/src/yolo_nitro.rs` | Nitro enclave Schwab reader, KMS `PCR0/1/2` policy, SP1 zkVM guest & AWS Nitro COSE/root-cert verifier |
| [`fce-usdx-oracle`](https://github.com/flare-foundation/fce-usdx-oracle/tree/7d3e4c05635f1d0912ec8e8435425394f65ce408) `7d3e4c0` | `README.md`, `internal/observation/price/price.go`, `internal/extension/provisioning.go`, `internal/observation/backing/backing.go` | USDX collateralization formula, 2-minute poller, governed cash URL hash & M-of-N secret provisioning |
| [`tee-node`](https://github.com/flare-foundation/tee-node/tree/c0281c7cd0e0643ef86c7b273e08c14d51eb5a7f) `c0281c7` | `docs/security.md`, `internal/attestation/attestation_token.go`, `internal/policy/policy.go` | Google Confidential Space token generation, reward-epoch signing policies, provider-majority trust model |
| [`flare-vtpm-attestation`](https://github.com/flare-foundation/flare-vtpm-attestation/tree/13d798541484720a4777c68eb0338255aa15989c) `13d7985` | `contracts/FlareVtpmAttestation.sol` | Earlier Solidity prototype for verifying Google RSA-signed JWT / vTPM attestations on-chain |
| [`tee-proxy`](https://github.com/flare-foundation/tee-proxy/tree/62f187370f2d335b93c7343546b5d5a0bae474dd) `62f1873` & [`go-verifier-api`](https://github.com/flare-foundation/go-verifier-api) | Transport proxy, off-chain Google JWT verifier, [`TeeAvailabilityCheck`](https://github.com/flare-foundation/flare-specs/blob/main/src/FDC2/Reference/AttestationTypes/TeeAvailabilityCheck.md) | Untrusted message relay and off-chain data-provider attestation check |

### External references

- [Post Fiat: The NAVCoin Proposal](/blog/navcoin-proposal/) &middot; [Post Fiat: Schwab NAVCoin (B24) Status and Handoff](/research/schwab-navcoin-handoff/)
- [Flare Confidential Compute overview](https://dev.flare.network/fcc/overview) &middot; [STP.13 proposal](https://proposals.flare.network/STP/STP_13.html) &middot; [FCC + Hex Trust USDX launch (1 Oct 2026)](https://chainwire.org/2026/10/01/flare-confidential-compute-to-bring-private-institutional-data-onchain-starting-with-hex-trusts-usdx/)
- [Google Confidential Space token claims](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/reference/token-claims)
