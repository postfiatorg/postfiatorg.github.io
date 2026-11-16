---
title: "Schwab NAVCoin (B24): Status and Handoff"
date: 2026-11-16T00:00:00Z
url: "/research/schwab-navcoin-handoff/"
summary: "A visual handoff for B24, the NAVCoin backed by a Schwab brokerage account: what is live, how a dollar of USDC becomes a coin, which steps are enforced by proofs, and where each piece lives in the code."
description: "Status diagrams, funding and reserve flows, trust model and code references for B24, the Schwab-backed NAVCoin on Post Fiat."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - PFTL
  - Schwab
  - Uniswap
  - Ethereum
  - Proof of Reserves
draft: false
---
# Schwab NAVCoin (B24): Status and Handoff

B24 is a NAVCoin backed by a Schwab brokerage account. One coin is a claim on one dollar of that account's value, and the account's value is read every day by sealed hardware and checked by the network before the coin's price can change.

This page is a handoff. It shows what is running as of 16 November 2026, how money gets in, which steps nobody has to be trusted for, and where each step lives in the code.

B24 runs on the Post Fiat test network `postfiat-wan-devnet-2`. Its Ethereum contracts are on Ethereum mainnet.

## Where it stands

{{< navcoin-handoff part="status" >}}

## What backs the coin today

{{< navcoin-handoff part="split" >}}

The three readings so far carry the same value because the first one landed on a Saturday and the market stayed closed. The reading on Monday 16 November is the first that should move.

## How funding works

A buyer starts with USDC on Ethereum and ends with a coin. Each step below names the check that guards it and the code that performs that check.

{{< navcoin-handoff part="funding" >}}

Two things follow from this design:

- **The buyer's cash never passes through an issuer wallet.** It sits in the Ethereum vault and is mirrored as PFUSDC held by the protocol.
- **Coins cannot be created ahead of the money.** A mint needs PFUSDC that only exists because a deposit was proven.

## How the reserve is proven

The funding path covers new money. The reserve path covers the brokerage account that backs the existing 420,302 coins.

{{< navcoin-handoff part="reserve" >}}

## How it appears in the Task Node

The consumer side lives inside the Task Node as a wallet with six surfaces. The design rule is simple: the browser holds the keys and signs, the Task Node server only relays, and the network enforces every rule shown above.

{{< navcoin-handoff part="tasknode" >}}

What this means for a user:

- **The Task Node never has custody.** A compromised Task Node server cannot move a user's coins, because it never sees a key and the network accepts only signed transactions.
- **The numbers on screen come from the network.** Balances, NAV, the verification split and history are read from the validators, not from a Task Node database.
- **One wallet per Task Node account.** Switching accounts never shows or overwrites another account's wallet.

## What you trust, step by step

| Step | Enforced by | You trust |
| --- | --- | --- |
| USDC held in the vault | Vault contract with no admin withdrawal | Ethereum |
| Deposit credited as PFUSDC | Zero-knowledge proof of Ethereum finality, verified by every validator | Ethereum finality and the proof system |
| B24 created at NAV | Chain rules: supply cap, issue capacity, latest finalised NAV | The Post Fiat validators |
| wB24 minted on Ethereum | Proof of the Post Fiat receipt, verified by a contract | The Post Fiat validator set named in that contract |
| Schwab balance | Hardware attestation wrapped in a proof | Amazon's Nitro hardware, the published enclave image, and Schwab's own reporting |
| Cash-in reserve | Counted by the chain, not independently read | The protocol's own ledger |
| Uniswap liquidity | Uniswap v4 | The pool owner, for depth only |

The weakest link is the brokerage itself. No proof can look inside Schwab. The design narrows that trust to one question, "did Schwab report this figure to this exact program", and answers it with hardware.

## Live numbers

Read from the network at block 1370 and from Ethereum at block 26,423,933.

| | B24 | A666 | BMNRC |
| --- | --- | --- | --- |
| Backing | Schwab account | Six-part StakeHub portfolio | BMNR carry trade |
| NAV per coin | $1.000000 | $1.167369 | $1.000000 |
| Coins outstanding | 420,323.38 | 31,519.44 | 640.59 |
| Readings accepted | 3 | 9 | 1 |
| Verification | 99.995% Attested | Legacy profile, split not recorded | 2 parts Proven, 1 Attested |
| Uniswap v4 pool price | $1.00, no liquidity | $0.6594 | $1.0018 |
| Wrapped on Ethereum | 1 | 31,418.44 | 565.59 |

## Reference: contracts and identifiers

| Item | Value |
| --- | --- |
| B24 asset id | `52285e4ded1d58113cfaa12bbc034b8b10213f699b3224c74160450229d6bf7c…` |
| Route | `pftl-b24-ethereum-wB24-usdc-v1` |
| Proof profile source class | `b23-schwab-account-equity-nitro-sp1-v1` |
| wB24 token | [`0x540fda223a2198690d31920a921a0b9dff335dbf`](https://etherscan.io/address/0x540fda223a2198690d31920a921a0b9dff335dbf) |
| Handoff controller | [`0x2c7db4c2ff8514334f62e6630226e95e72fa6056`](https://etherscan.io/address/0x2c7db4c2ff8514334f62e6630226e95e72fa6056) |
| USDC bridge vault | [`0xE7A432a28b20621A70E845C7F202004Cf98e7A2C`](https://etherscan.io/address/0xE7A432a28b20621A70E845C7F202004Cf98e7A2C) |
| Uniswap v4 pool id | `0x70ab0a6fd1e33c7d3dfeae11a1ec60682efa2a9e95f028df1964b167326cc92c` |
| Creation price | NAV × 1.0050 |
| Cash-in price | NAV × 0.9995, capped at the reserve (21 PFUSDC) |

## Reference: code

Line numbers are from the branches below. This work has not yet been merged into the public main line.

| Repository | Branch | Commit |
| --- | --- | --- |
| postfiatl1v2 | `b23/tee-phase6-mainnet-20261114` | `43ddc7d6` |
| navstrategies (Schwab reader and enclave) | `b23/tee-nav-phase1-20261113` | `f6d6be7f` |
| Task Node (wallet, gallery, coin pages) | `b23/integration` | `483dd32` |

| What it does | File and line |
| --- | --- |
| Accept a USDC deposit | `crates/ethereum-contracts/src/ERC20BridgeVaultL1.sol:127` |
| Pay a withdrawal against a proof | `crates/ethereum-contracts/src/ERC20BridgeVaultL1.sol:191` |
| Prove Ethereum finality and the deposit | `programs/pfusdc-eth-mainnet-ingress/src/lib.rs:285` |
| Verify the deposit proof and credit PFUSDC | `crates/execution/src/nav_vault_asset_execution.rs:1232` |
| Create coins at NAV (subscription) | `crates/execution/src/nav_vault_asset_execution.rs:4729` |
| Supply cap and issue capacity checks | `crates/execution/src/nav_vault_asset_execution.rs:4070`, `:4577` |
| Verify an SP1 Groth16 proof on chain | `crates/execution/src/nav_sp1_verifier.rs:86` |
| Reserve reading fields (proven, attested, reported) | `crates/types/src/account_owned_asset_types.rs:813` |
| Verify a Nitro attestation document | `tools/nav-reserve-proof/crates/reserve-proof-types/src/yolo_nitro.rs:164` |
| Schwab reserve proof program | `tools/nav-reserve-proof/crates/reserve-proof-types/src/b23_nav.rs:141` |
| Accept a Post Fiat receipt on Ethereum | `crates/ethereum-contracts/src/PFTLReceiptFinalityVerifierV2.sol:229` |
| Mint wrapped coins from an accepted receipt | `crates/ethereum-contracts/src/PFTLUniswapHandoffController.sol:1615` |
| Daily reading job | `ops/b24-live/daily.py` |
| Task Node: relay and request checks | `server/l1/gateway.js:49` |
| Task Node: allowed network calls | `src/features/wallet/l1/lib/rpc-methods.js` |
| Task Node: key material never leaves the browser | `src/features/wallet/l1/lib/custody-boundary.js` |
| Task Node: local signing | `src/features/wallet/l1/core.js:54` |
| Task Node: encrypted vault per account | `src/features/wallet/l1/lib/vault.js:137` |
| Task Node: MetaMask deposit | `src/features/wallet/l1/bridge/evm.js:14` |
| Task Node: buy from book or create | `src/features/wallet/l1/market/index.jsx:146` |
| Task Node: cash-in quote | `src/features/wallet/l1/redeem/model.js:10` |
| Task Node: coin discovery | `server/l1/navcoin-registry.js:7` |
| Task Node: verification split | `src/features/wallet/l1/gallery/model.js:10` |
| Task Node: coin page and snapshot data | `server/l1/navcoin-profile.js:66` |

## Open items

1. **Fund the pool.** The token and pool are deployed; liquidity and the first 5,000 wrapped coins are not.
2. **Build the exit for new deposits.** USDC deposited under the current bridge setting stays in the vault as the coin's reserve until a matching withdrawal proof exists.
3. **Ethereum back to native.** Returning wB24 to Post Fiat ships with the next network release.
4. **Merge.** The live network runs code from the branches above. They need to land on the main line.
5. **Public Task Node.** The wallet, gallery and coin pages run on a test deployment.
6. **A666 and BMNRC.** A666's pool trades well below NAV and its split is not recorded under its older profile. BMNRC has one reading and needs its refresh restarted.
7. **Signer headroom.** Five of six validators currently sign Ethereum-side approvals, which is the exact quorum.
