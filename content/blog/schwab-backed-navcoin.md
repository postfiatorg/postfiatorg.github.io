---
title: "How a Schwab-Backed NAVCoin Works"
date: 2026-11-12T00:00:00Z
draft: false
summary: "B23 is a native PFTL asset that trades to the net asset value of a Charles Schwab brokerage account. The issuer commits the account value on-chain each day. Consensus enforces the packet's supply cap, and holders can convert B23 back to PFUSDC at NAV through an on-chain reserve."
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - NAVCoin
  - Proof of Reserves
  - PFUSDC
  - Task Node
  - RWA
---

B23 is a NAVCoin backed by a Charles Schwab brokerage account. It is a native asset on PFTL, the Post Fiat L1 blockchain, and it trades to NAV. Its **net asset value**, or NAV, is the account value behind each B23.

The issuer records that value on-chain each day. PFTL turns the record into rules for issuing B23 and paying holders who burn it. Every signature on PFTL uses ML-DSA, a post-quantum signature scheme.

## The short version

B23 connects three parts: a brokerage account, an on-chain reserve and a market. The account sets NAV. The reserve pays holders in PFUSDC. The market lets buyers and sellers agree on a price.

The key step is enforcement. The daily account record becomes part of the ledger, and PFTL checks every mint and every burn against it. Supply cannot outgrow the account value the record states.

## How the account becomes NAV

{{< b23-flow kind="mechanism" >}}

Schwab computes the account's **net liquidation value**: what everything in the account is worth, minus what the account owes the broker. The margin loan and the value of short positions are already subtracted. B23 uses that figure without adjustment. PFUSDC in the separate reserve is excluded from this calculation.

**1. The daily read.** At the same cutoff each day, a reader queries Schwab's API, the interface used to read account data. It records net liquidation value, balances and positions.

**2. The reserve packet.** The issuer signs and submits a packet to PFTL. It carries account value, NAV per B23, B23 supply and the cutoff time. It also carries a commitment to the account's identity and hashes—digital fingerprints—of the positions, cash and liabilities. The packet becomes a permanent record.

**3. The NAV epoch.** Finalizing the packet opens an epoch: the period in which that packet sets NAV. Epoch numbers must rise. Packet supply is the denominator used to state NAV and the cap for total B23 supply during that epoch. It can include B23 the issuer plans to mint. Consensus checks the backing rule:

**Packet supply × NAV per B23 ≤ packet account value.**

**4. Mint at NAV.** Only the issuer can mint. Every mint names the current epoch and its packet hash. Consensus checks both and enforces the packet's supply cap.

The opening mint is against the whole account balance. The 2,000 B23 minted earlier against one measured $2,000 wire are part of that opening supply, not an addition to it. That wire was already in the account, so it counts once. From the opening epoch on, every B23 tracks an equal share of the whole account, not a particular deposit.

### What anyone can check on PFTL

- Each packet's account value, NAV, supply, cutoff, account commitment and hashes.
- The order in which NAV epochs finalized.
- The packet's backing calculation and the supply cap applied to each mint.
- The current epoch and packet used by each mint and burn at NAV.
- PFUSDC in the reserve, the fee setting and every payment out.

**Under the hood.** The PFTL transactions are `nav_reserve_submit`, `nav_epoch_finalize` and `nav_mint_at_nav`. A mint naming a stale epoch fails with `nav_epoch_mismatch`. A mint past packet supply fails with `nav_supply_cap_exceeded`. Market offers use `offer_create` and `offer_cancel` on PFTL's native order book.

## Three operations, three different effects

- **Mint at NAV — issuer only.** New B23 is issued against the account value in a finalized packet. Supply rises.
- **Burn at NAV — any holder.** B23 is destroyed. PFUSDC leaves the reserve. Both supply and the reserve fall.
- **Buy or sell on the market — anyone.** Existing B23 changes hands for PFUSDC. Supply, account value and the reserve stay the same.

Task Node gives these operations separate screens and labels.

### A worked example (illustrative numbers)

The account is worth $100,000 and 100,000 B23 exist. The packet states NAV of $1.00 and supply of 100,000. The backing check passes: 100,000 × $1.00 fits within $100,000.

A holder burns 1,000 B23 with the fee set at 20 basis points, or 0.2%. The holder receives 998 PFUSDC. The management wallet receives 2 PFUSDC. The reserve falls by 1,000 PFUSDC, and supply falls to 99,000.

The account still holds the $1,000 behind the burned B23. If the issuer moves $1,000 out of the account to restore the reserve, the next packet reads $99,000 over 99,000 B23. NAV stays $1.00. If the money stays in the account, the next packet reads $100,000 over 99,000 B23. NAV rises for the remaining holders.

For a separate issuance example, start again with $100,000 and 100,000 B23. The issuer adds $10,000 to the account. The next packet can state supply of 110,000 at NAV of $1.00, and the issuer mints 10,000 B23. Existing holders' NAV is unchanged.

Within one epoch, burns free room under the packet's supply cap. The issuer can mint again up to that cap at the same NAV.

## The PFUSDC reserve

PFUSDC is USDC brought onto PFTL by proof, as shown in Bob's journey below. The reserve holds it on-chain and applies these payment rules:

- **Any holder can burn B23 against the reserve** whenever a current NAV exists. The holder receives NAV minus *x* basis points in PFUSDC. A basis point is one hundredth of a percentage point.
- **The fee moves in the same transaction.** The management wallet receives the fee. Both payments appear in one receipt and add up to the full NAV value of the B23 burned.
- **Each burn is capped by the reserve.** A request larger than the PFUSDC available is rejected whole. It never half-fills.
- **The issuer can add PFUSDC at any time.** Adding to the reserve issues no B23.
- **The issuer sets *x* and can change it at any time**, between 0 and 500 basis points, without redeploying anything. The change takes effect as a new on-chain route policy, which holds the rules for reserve payments. A burn signed under the old setting is rejected once the new one is live.

This reserve gives B23 its pull toward NAV. When the market price is below NAV minus the fee, any holder can buy B23 there and burn it at NAV. That buying pulls the market price up. When the market trades above NAV, the issuer can mint at NAV within the packet's cap and sell. That selling pulls the market price down.

## Bob: from MetaMask to B23

{{< b23-flow kind="bob" >}}

Bob holds USDC on Ethereum in MetaMask and wants B23. He uses Task Node. MetaMask signs the Ethereum side. His B23 lives in his Task Node wallet, whose ML-DSA keys are made in his browser and stored encrypted there.

**1. Connect MetaMask.** Bob opens his PFTL wallet in Task Node and connects MetaMask. Task Node shows his PFTL address as the deposit recipient.

**2. Convert USDC into PFUSDC.** Bob approves USDC and deposits it into the PFUSDC vault contract on Ethereum. The deposit names his PFTL address. Once Ethereum finalizes the block, a prover generates an SP1 zero-knowledge proof: a cryptographic proof that the deposit is in finalized Ethereum state. PFTL checks it and credits Bob exactly the deposited amount as PFUSDC. Verification uses the proof rather than committee signatures, and each deposit can be claimed once. The wallet shows confirmation, Ethereum finality, proof capture, proving, verification and credit.

**3. Buy B23 on the market.** Bob places a buy order with PFUSDC on PFTL's order book. When it meets Alice's sell offer, B23 moves to Bob and PFUSDC moves to Alice. No B23 is created and the reserve does not change.

Bob now holds B23. He can sell it on the market or convert B23 back to PFUSDC at NAV against the reserve.

## Alice: issuing B23

{{< b23-flow kind="alice" >}}

Alice is the issuer. She works on PFTL inside Task Node.

**1. Mint B23 against the Schwab account.** Alice submits the day's signed packet and finalizes the NAV epoch. She then mints at NAV using that packet.

**2. Set up the reserve.** Alice adds PFUSDC and sets the fee *x*. From then on any holder can burn B23 at NAV minus *x* basis points, and the management wallet receives the fee on every burn. Task Node gives her controls to add PFUSDC or change *x* at any time.

**3. Put up a market.** Alice posts a sell offer on PFTL's order book from a holder account separate from the issuer account. PFTL keeps issuing and trading apart by requiring that separation. She can cancel any unfilled part of the offer.

## How B23 compares with industry proof of reserves

{{< b23-flow kind="proof-comparison" >}}

Proof-of-reserves systems measure backing and publish evidence about it. The key questions are who reads the assets, what gets published, whether liabilities are counted and where enforcement happens.

**Ethena custodian attestations.** Ethena's USDe is backed by assets held off-exchange with institutional custodians. Each month, Ethena publishes reports from all its integrated custodians. They confirm the existence, control and value of the backing assets. The custodians observe the assets, and Ethena publishes the reports on its website and Transparency dashboard. Nothing on-chain acts on them.

**Ethena weekly proof of reserves.** A program inside an AWS Nitro enclave, an isolated computing environment, reads balances and derivatives positions from custodians, exchanges and the blockchain. It values spot assets with Pyth prices. It checks whether backing exceeds USDe supply, whether opposing positions offset price exposure and whether only approved assets are used. The enclave signs its answers. Outside attestors check that signature, the API credentials and whether the enclave ran a build they reproduced from the code. Ethena does not describe any contract that uses the proof to gate minting.

**Chaos Labs proof of reserves.** Chaos Labs reads collateral on-chain and turns custodian and exchange data into on-chain inputs. Its oracle—a service that supplies data to the chain—tracks locked reserves, issued supply across supported chains and whether reserves meet or exceed supply. Any contract can read the result in one call. Each integrator chooses how its contract acts on it.

**Chainlink Proof of Reserve.** Chainlink publishes reserve figures through the same interface as a price feed. Off-chain figures come from an API operated by an auditor, accounting firm, custodian or issuer. Chainlink node operators carry the number on-chain. Chainlink notes that many of these feeds rely on a single data provider, and it requires contracts that use them to add their own value bounds, caps, circuit breakers, freshness checks and pause controls. Comparing reserves with supply, and acting on it, is the consuming contract's job.

**B23 on PFTL.** The issuer's reader takes Schwab's net liquidation value at a fixed daily cutoff. That figure already subtracts the margin loan and short positions. The issuer signs the packet with ML-DSA, and it becomes ledger state. PFTL's consensus rules apply the backing check, the supply cap, the current-epoch checks and the reserve payment rules directly.

The distinction is where enforcement lives. Chainlink and Chaos Labs feeds can drive enforcement in each contract that chooses to read them. B23 puts the rule in the base protocol. Every B23 mint passes through it.

## Safeguards

B23 ties a fixed daily read to a permanent record, a supply cap and visible reserve payments.

### In B23's rules today

- **A fixed cutoff and a fixed measure.** The reader uses Schwab's reported net liquidation value at the same time each day.
- **Permanent packets.** Each packet commits to account identity, cutoff, value and the hashes behind it. Later records for that cutoff can be checked against those hashes.
- **A backing check and a supply cap.** Consensus applies the packet's arithmetic and issuance rules.
- **Current epoch checks.** Mints and burns name the current epoch and packet. Reserve burns also carry a maximum NAV age in the route policy.
- **Visible, atomic payments.** The reserve is on-chain. Each completed burn pays the holder and management wallet together.
- **A separate market.** Order-book trades never change supply or NAV.

### The next layers

- **Independent readers.** Several operators read the same account, each with its own session, servers and code. A packet finalizes only when every registered reader agrees.
- **Repeatable cutoff values.** Readers rebuild value as of the cutoff and match every account flow to on-chain events, so a read at any hour gives the same number.
- **A nonce in the money.** The chain publishes a nonce: an unpredictable number used once. A small cash transfer makes the account balance end in those cents. A read showing that balance proves the account was live and under control after the number appeared.
- **Withdrawal drills.** On a schedule, a small amount travels from Schwab back to PFUSDC, visible on-chain. The drill shows that money comes out, not only that it is there.
- **Origin proofs.** A TLS transcript proof shows that the bytes of the read came from Schwab's servers.
- **Withdrawal controls.** Money leaving the account is restricted to pre-agreed destinations, and the restriction itself can be checked.

## Two routes for USDC: Ethereum and Arc

Bob uses Ethereum mainnet because his USDC is there. PFTL also has an entry route from Arc, Circle's Ethereum-compatible chain, for users who hold USDC there. Both routes produce PFUSDC without changing the Schwab account, NAV, B23 reserve or market.

- **Finality.** Ethereum finalizes in minutes. Arc finalizes each block in under a second using Tendermint-style BFT consensus, a method for validators to agree on blocks, among an approved validator set.
- **Proof checks.** The Ethereum SP1 proof checks Ethereum finality and the deposit. The Arc proof checks validator signatures and the deposit receipt against a validator set fixed by PFTL governance.
- **Steps from Ethereum.** The direct route is approve, deposit and wait for PFUSDC. Going through Arc first adds a transfer through Circle's Cross-Chain Transfer Protocol, or CCTP. Circle lists roughly 15 to 19 minutes for a standard transfer or about 20 seconds for a fast one.

## What this does not prove

- **The packet is issuer-signed, not Schwab-signed.** The chain proves which packet finalized and whether transactions obeyed it. It does not prove that the submitted figure matches Schwab's API at the cutoff.
- **The backing check verifies arithmetic, not new deposits.** Consensus checks that packet supply times NAV fits within the account value. It does not check that new supply matches new money in the account. A packet that lowers NAV while supply grows is visible to everyone on-chain.
- **Schwab is the broker, not a party to B23.** Schwab holds the account as broker and signs nothing on PFTL. The chain enforces the reserve and the market. Rights to the Schwab account itself sit outside the protocol.
- **A snapshot does not control the account.** Money can leave after the read. Unsettled trade cash, accrued margin interest, dividends owed on short positions and fees can affect the next figure.
- **Pricing comes from Schwab.** No second pricing source checks it.
- **The pull toward NAV is as deep as the reserve.** Burns at NAV are limited to the PFUSDC in the reserve, and they pause when NAV is older than the route policy allows. Beyond that, holders sell at the market price.
- **The added safeguards are next steps.** There is one reader today. The next layers listed above are not yet live.
- **Arc has testnet coverage.** PFTL's Arc route has run end to end on Arc testnet. B23's entry route is Ethereum.

## Sources

- Ethena, custodian attestations: <https://docs.ethena.fi/resources/custodian-attestations>
- Ethena, "Custodian Attestations of Assets Backing USDe: September": <https://ethena.fi/blog/custodian-attestations-of-assets-backing-usde-september-3>
- Ethena, "USDe Proof of Reserves Launch": <https://paragraph.com/@ethena-labs/usde-proof-of-reserves-launch>
- Ethena, "Ethena Engineering Blog: Proof of Reserves": <https://paragraph.com/@ethena-labs/ethena-engineering-blog-proof-of-reserves>
- Chaos Labs, "Proof of Reserve as Risk Infrastructure": <https://chaoslabs.xyz/posts/proof-of-reserve-as-risk-infrastructure>
- Chaos Labs, oracles: <https://chaoslabs.xyz/oracles>
- Chainlink, SmartData and Proof of Reserve feeds: <https://docs.chain.link/data-feeds/smartdata>
- Chainlink, selecting data feeds and single-source providers: <https://docs.chain.link/data-feeds/selecting-data-feeds>
- Arc, consensus layer: <https://docs.arc.io/arc/concepts/consensus-layer>
- Circle, CCTP finality and block confirmations: <https://developers.circle.com/cctp/concepts/finality-and-block-confirmations>
