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

## The original NAVCoin: A666

B24 is the second kind of NAVCoin. The first was A666, which is still live. A666 is backed by a working portfolio spread across six networks, and it is where the proof system was built.

{{< navcoin-handoff part="portfolio" >}}

The amount held is proven cryptographically for five of the six parts. Only the Solana stake relies on an attested reading. Dollar values are proven for the two parts that have an on-chain price source and attested for the rest.

A666 has 31,519 coins outstanding at a NAV of $1.167, nine accepted readings, and a wrapped token with a Uniswap v4 pool on Ethereum mainnet.

### A multi-asset on-chain portfolio as the next coin type

A666 and B24 sit at opposite ends. A666 holds assets that live on public networks, so most of it can be proven outright. B24 holds assets inside a brokerage, so it can only be attested.

The natural next coin is a larger, deliberately built version of A666: a multi-asset portfolio held entirely on-chain. Because every position is on a public network, such a coin can aim for a split that is mostly Proven, with no enclave and no broker in the trust path.

What already exists for it:

- **A reader for each kind of position**: lending, perpetuals, staking, spot and Monero. These are the six files in the diagram above.
- **A combining program** that nets assets against debt and outputs one figure with its split.
- **The same chain rules B24 uses** for creation, cash-in, staleness and the Ethereum wrapper.

What a new portfolio coin needs: a manifest naming its positions, a reading schedule, and its own Ethereum route. A new kind of position needs a new reader.

## Private swaps

Everything above happens in public. The network also has a shielded pool, so a NAVCoin can be held and swapped without revealing the holder, the asset or the amount.

{{< navcoin-handoff part="private" >}}

The private path was proven on the test network in June and July 2026, including a 250 USDC run through every step. It is not yet offered for B24, and the Task Node wallet has no private tab. Turning it on for a coin is a matter of enabling its route for the shielded pool and adding the screens, not of building the cryptography.

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

## Review surface

This is what a reviewer should read, in order of how much money or trust depends on it. Paths are in the code index at the end.

| Priority | Area | The question to answer | Where |
| --- | --- | --- | --- |
| 1 | Deposit proof | Can PFUSDC ever be credited without a real, final Ethereum deposit? Can one deposit be credited twice? | `programs/pfusdc-eth-mainnet-ingress/src/lib.rs`, `nav_vault_asset_execution.rs:1232` |
| 1 | Bridge vault | Is there any way to move USDC out other than a valid proof? | `ERC20BridgeVaultL1.sol:127`, `:191` |
| 1 | Creation and cash-in | Can coins be minted beyond the caps, or cashed in beyond the reserve? Is the fee always paid in the same transaction? | `nav_vault_asset_execution.rs:4729`, `:4070`, `:4577` |
| 1 | Ethereum wrapper | Can wB24 be minted without a locked native coin behind it? Can one receipt mint twice? | `PFTLReceiptFinalityVerifierV2.sol:229`, `PFTLUniswapHandoffController.sol:1615`, `:1753` |
| 2 | Enclave reading | Does the proof pin the exact enclave image? What can the machine's operator change without detection? | `yolo_nitro.rs:164`, `b23_nav.rs:141`, `containers/yolo-nitro/` |
| 2 | Proof verification on chain | Is every reading bound to the program key in the coin's profile? What happens to a stale reading? | `nav_sp1_verifier.rs:86`, `nav_vault_asset_execution.rs:3000` |
| 2 | Verification split | Can a reading claim more Proven or Attested value than its proof supports? | `account_owned_asset_types.rs:813`, `gallery/model.js:10` |
| 3 | Task Node relay | Can the server see or forward key material? Can a signed-out or cross-site request reach the network? | `server/l1/gateway.js:49`, `custody-boundary.js` |
| 3 | Browser wallet | Is the seed ever stored or sent unencrypted? Does switching accounts isolate wallets? | `lib/vault.js:137`, `core.js:54` |
| 3 | Daily job | What happens when a run fails, and who is told? Does the spending cap stop it silently? | `ops/b24-live/daily.py` |
| 4 | Private path | Does the shielded swap conserve each asset? Is a private order bound to a fresh reading? | `orchard_state_application.rs:1131`, `nav_vault_asset_execution.rs:4950` |

Known gaps a reviewer will find, listed so they are not rediscovered: the withdrawal path for new deposits and the Ethereum-to-native return are not built; five of six validators sign Ethereum-side approvals with no spare; the launch needed a manual repair three times for a known network bug; and none of this code is on the public main line yet.

## Second Set of Eyes

A catalogue of independent checks, written so each one can be handed to an agent as it stands. Every item says what to check, when it passes, and where to start. None of them has been run as an independent review yet; the boxes are empty on purpose.

Rules for every agent:

- **Read only.** Work on a local copy or a private fork of Ethereum. No transactions on the live network, no funds moved, no services restarted.
- **No secrets.** Never open, print or copy key files, tokens or credentials. Report a secret you find by its path, not its contents.
- **Evidence, not opinion.** Each finding cites a file and line or pastes the command and its output.
- **One verdict per item:** PASS, FAIL or UNCLEAR, followed by what would settle an UNCLEAR.
- **Do not fix.** Report. Fixes are separate work.

### A. Can money be created, taken or stuck?

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | A1 | Crediting the same Ethereum deposit twice | Every replay route is rejected, with a test that shows it | `nav_vault_asset_execution.rs:1232`, `:1954` |
| ☐ | A2 | Crediting a deposit that never finalised | A proof built on a swapped or stale signer set is rejected, and that test exists and runs | `programs/pfusdc-eth-mainnet-ingress/src/lib.rs:336` |
| ☐ | A3 | Every way USDC can leave the vault | The only exit is a valid proof; the admin key can pause and nothing else | `ERC20BridgeVaultL1.sol:127`, `:191` |
| ☐ | A4 | Why USDC deposited now cannot be withdrawn | The claim that the vault's checker pins the older bridge setting is confirmed or disproved from the deployed bytecode | Vault `0xE7A432a2…`, `ERC20BridgeVaultL1.sol:191` |
| ☐ | A5 | Minting past the supply cap or issue capacity | No sequence of creates, including concurrent ones, exceeds either limit | `nav_vault_asset_execution.rs:4729`, `:4070`, `:4577` |
| ☐ | A6 | Rounding at creation and cash-in | Every rounding goes in the protocol's favour and dust cannot be farmed with many small orders | `nav_vault_asset_execution.rs:4482`, `redeem/model.js:10` |
| ☐ | A7 | Cashing in more than the reserve holds | Refused cleanly; the fee reaches the management wallet in the same transaction every time | `nav_vault_asset_execution.rs:5364` |
| ☐ | A8 | Minting wB24 twice from one receipt | A consumed receipt cannot be reused; wrapped supply never exceeds native coins locked | `PFTLUniswapHandoffController.sol:1615`, `:1753` |
| ☐ | A9 | Who can unpause, re-point or upgrade the Ethereum contracts | A written list of every privileged function and the address that holds it, with nothing unexpected | `PFTLUniswapHandoffController.sol`, `PFTLReceiptFinalityVerifierV2.sol:229` |

### B. Is the Schwab number what it claims to be?

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | B1 | Whether the proof pins the exact enclave image | A reading from any other image fails verification, and the pinned image can be rebuilt from source to the same measurement | `yolo_nitro.rs:164`, `b23_nav.rs:141`, `containers/yolo-nitro/` |
| ☐ | B2 | Replaying an old attestation as today's reading | Yesterday's signed result cannot be accepted as a new reading | `b23_nav.rs:141`, `nav_vault_asset_execution.rs:3000` |
| ☐ | B3 | What the machine's operator can change undetected | A written list of everything outside the enclave that influences the result, each shown harmless or flagged | `containers/yolo-nitro/aws/`, `nav_reading.py` |
| ☐ | B4 | Who can change a coin's proof setting | Replacing the pinned program key needs the authority the design says it needs, and no weaker path exists | `nav_sp1_verifier.rs:86`, proof profile registration |
| ☐ | B5 | Recomputing B24's three readings independently | NAV, supply and the split are reproduced from the published values by a script that shares no code with ours | `account_owned_asset_types.rs:813`, coin page data |
| ☐ | B6 | Claiming more Proven or Attested value than the proof supports | The parts can never sum past the total, on chain or on screen | `gallery/model.js:10`, `nav_reserve_public_values.rs:51` |
| ☐ | B7 | What a stale coin actually refuses | BMNRC is past its freshness limit today: confirm by read-only calls that creation and cash-in are refused | Route state for BMNRC |
| ☐ | B8 | The four items that can post to Schwab after the reading | Their worst-case size is estimated against the account and compared with the 0.05 percent cash-in margin | `nav_reading.py` |

### C. Can the Task Node leak or mislead?

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | C1 | Smuggling key material past the relay | Nested, encoded and renamed secrets are all rejected | `custody-boundary.js`, `server/l1/gateway.js:54` |
| ☐ | C2 | Reaching the network signed out or from another site | Both the request path and the live-update path refuse | `server/l1/gateway.js:75`, `:82`, `:101` |
| ☐ | C3 | Calling anything outside the allowed list | Only the listed read and submit calls pass | `lib/rpc-methods.js`, `server/l1/gateway.js:49` |
| ☐ | C4 | The browser vault | The seed is never stored or sent unencrypted, key stretching is adequate, and one account cannot open another's wallet | `lib/vault.js:137`, `:208` |
| ☐ | C5 | Every number on the coin pages | An independent script reads all six validators and Ethereum and matches the four coin pages exactly | `server/l1/navcoin-profile.js:66`, `server/l1/profile/ethereum.js` |
| ☐ | C6 | What the screen says when something fails | No path shows success without an accepted receipt | `market/index.jsx`, `redeem/index.jsx`, `bridge/controller.js` |
| ☐ | C7 | Merging the wallet branch into the public Task Node | A dry-run merge with the full test suite, and a list of what breaks | Task Node `b23/integration` |

### D. Will it keep running?

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | D1 | How the daily job fails | Each failure (expired Schwab access, cloud outage, proof failure, spending cap) ends in a clear state and somebody is told | `ops/b24-live/daily.py` |
| ☐ | D2 | Running the daily job twice in one day | The second run cannot post a conflicting reading | `ops/b24-live/daily.py` |
| ☐ | D3 | Total cloud spend against the $100 cap | A dated total, the run rate, and the day the cap is reached | Cloud billing, job records |
| ☐ | D4 | The network bug that needed manual repair three times at launch | Reproduced on a local copy with a root cause | Launch records, `status/tee.md` |
| ☐ | D5 | Why the fifth validator cannot sign Ethereum-side approvals | Root cause and the steps to restore a spare signer | Validator authority keys (paths only) |
| ☐ | D6 | Merging the network branches into the main line | A merge order, the conflicts, and a build that still produces the live network's state | `b23/*` branches |
| ☐ | D7 | Secrets in the branches and evidence folders before anything goes public | No key, token or credential is committed; anything found is reported by path only | All `b23/*` branches, the evidence folders |

### E. The other coins and the private path

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | E1 | Why A666's pool trades at $0.66 against a NAV of $1.167 | The swap history explains it: never re-centred, sold into, or something else | Pool `0xc5f1e4b5…`, Ethereum logs |
| ☐ | E2 | Moving A666 to a proof setting that records its split | A plan showing its page would then report the Proven and Attested shares, with no change to its supply | `stakehub-six-leg-reserves-v3` profile |
| ☐ | E3 | Restarting BMNRC's reading | The reason it stopped in October is confirmed and the restart steps are listed | BMNRC reading pipeline |
| ☐ | E4 | Private swaps conserving each asset | No shielded swap can create or destroy value in any asset; a spent note cannot be spent again | `orchard_state_application.rs:961`, `:1131` |
| ☐ | E5 | Private create and cash-in using an old price | A private order tied to a stale or superseded reading is refused | `nav_vault_asset_execution.rs:4950`, `:5151` |

### F. Does the writing match the code?

| ☐ | ID | Throw an agent at | Passes when | Start at |
| --- | --- | --- | --- | --- |
| ☐ | F1 | Every file and line on this page | Each reference opens to code that does what the page says it does | The code tables on this page |
| ☐ | F2 | Every number on this page | Each figure is re-read from the network or Ethereum and matches, or is marked out of date | Live numbers and split diagram |
| ☐ | F3 | The unpublished Schwab blog post | A list of every statement that is wrong now that B24 replaced B23 | Site pull request 29 |
| ☐ | F4 | The trust table | For each row, an attempt to name something else the user must trust that the table leaves out | "What you trust, step by step" |

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
| A666: combine six positions into one figure | `tools/nav-reserve-proof/crates/reserve-proof-types/src/lib.rs:488` |
| A666: position readers | `aave_v3.rs`, `hyperliquid_receipt.rs`, `near_receipt.rs`, `evm_spot.rs`, `monero_reserve.rs`, `solana_stake.rs` in the same folder |
| Private swap: circuit and proof check | `crates/privacy_orchard/src/asset_orchard_circuit.rs`, `asset_orchard_action_builders.rs:264` |
| Private swap: apply and check accounting | `crates/node/src/orchard_state_application.rs:961`, `:1131` |
| Private create and cash-in at NAV | `crates/execution/src/nav_vault_asset_execution.rs:4950`, `:5151` |
| Shield and unshield | `crates/node/src/orchard_state_application.rs:1393`, `:1523` |
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
