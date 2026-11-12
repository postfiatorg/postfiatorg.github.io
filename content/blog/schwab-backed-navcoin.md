---
title: "How a Schwab-Backed NAVCoin Works"
date: 2026-11-12T00:00:00Z
draft: false
summary: "B23 is a native PFTL asset that trades to the net liquidation value of a Charles Schwab brokerage account. The issuer commits the account value on-chain each day. Consensus enforces the packet's supply cap, and holders can convert B23 back to PFUSDC at NAV through an on-chain reserve."
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

B23 is a NAVCoin backed by a Charles Schwab brokerage account. It is a native asset on PFTL, the Post Fiat L1 blockchain. B23 is an asset that trades to NAV: the account's net asset value per B23.

At a fixed daily cutoff, the issuer reads the account value and commits it on-chain in a signed packet. The packet states the account value, NAV per B23 and B23 supply. Consensus checks those numbers and enforces the supply cap. Every signature on PFTL uses ML-DSA, a post-quantum signature scheme.

Any PFTL wallet can hold B23, trade it on the native order book or burn it at NAV against an on-chain PFUSDC reserve. The brokerage account sets NAV. The PFUSDC reserve pays holders who burn.

## The short version

- **One account sets NAV.** NAV per B23 is the Schwab account's net liquidation value divided by B23 supply. PFUSDC in the reserve is separate and is not counted in NAV.
- **A daily read becomes ledger state.** The issuer signs and submits a reserve packet. Finalizing it opens a NAV epoch: the period in which that packet sets NAV.
- **The packet caps supply.** Consensus checks that packet supply times NAV does not exceed packet account value. A mint cannot take total supply past the packet's supply.
- **The reserve pays for burns.** Burning destroys B23 and pays PFUSDC to the holder and a management wallet in one transaction.
- **Market trades move existing B23.** Buyers and sellers set the price. Trades change neither supply nor the reserve.

## How the account becomes NAV

{{< b23-flow kind="mechanism" >}}

Schwab computes the account's **net liquidation value**: what everything in the account is worth, minus what the account owes the broker. The margin loan and the value of short positions are already subtracted. B23 uses that figure without adjustment.

**1. The daily read.** At the same cutoff each day, a reader queries Schwab's API, the interface used to read account data. It records net liquidation value, balances and positions. The fixed cutoff sets the moment of the read.

**2. The reserve packet.** The issuer signs and submits the packet to PFTL. It carries account value, NAV per B23, B23 supply and the cutoff time. It also carries a commitment to the account's identity and hashes—digital fingerprints—of the positions, cash and liabilities. The packet becomes a permanent record.

**3. The NAV epoch.** Finalizing the packet opens a new epoch. Each new epoch prices NAV on the supply that exists. Epoch numbers must rise. Consensus checks the backing rule:

**Packet supply × NAV per B23 ≤ packet account value.**

**4. Mint at NAV.** Only the issuer can mint. Every mint names the current epoch and its packet hash. Consensus checks both and rejects any mint that would take total supply past the packet's supply.

The opening mint is against the whole account balance. The 2,000 B23 minted earlier against one measured $2,000 wire are part of that opening supply. The wire was already in the account and counts once. Every B23 then tracks an equal portion of the whole account.

A higher account value alone changes NAV on the existing supply. New B23 beyond that supply can be minted only when a packet shows more account value supporting more supply at the stated NAV, such as after the issuer adds money to the account. Dividing account value by supply sets the price; the packet's separate supply cap controls issuance.

### What anyone can check on PFTL

- Each packet's account value, NAV, supply, cutoff, account commitment and hashes.
- The order in which NAV epochs finalized.
- The packet's backing calculation and the supply cap applied to each mint.
- The current epoch and packet used by each mint and burn at NAV.
- PFUSDC in the reserve, the fee setting and every payment out.

**Under the hood.** The PFTL transactions are `nav_reserve_submit`, `nav_epoch_finalize` and `nav_mint_at_nav`. A mint naming a stale epoch fails with `nav_epoch_mismatch`. A mint past packet supply fails with `nav_supply_cap_exceeded`. Market offers use `offer_create` and `offer_cancel` on PFTL's native order book.

## Three operations, three different effects

- **Mint at NAV — issuer only.** New B23 is created against the account value in a finalized packet. Supply rises within the packet's cap.
- **Burn at NAV — any holder.** B23 is destroyed. PFUSDC leaves the reserve. Both supply and the reserve fall.
- **Buy or sell on the market — anyone.** Existing B23 changes hands for PFUSDC. Supply, account value and the reserve stay the same.

Task Node gives these operations separate screens and labels.

The accounting follows the same sequence. At opening, the account supports the opening supply. For new issuance, added account value supports added supply at the stated NAV. A market sale then transfers B23 to a buyer without changing that backing.

A burn reduces supply while paying from the separate PFUSDC reserve. The next packet divides the Schwab account value by the supply that remains. When the issuer moves money from Schwab to replenish the reserve, account value falls by the amount moved. If that amount equals the NAV value of the B23 burned, NAV per remaining B23 stays unchanged. If the account value stays the same after a burn, the next packet divides it among fewer B23.

PFUSDC in the reserve is never added to the Schwab account value when calculating NAV.

## The PFUSDC reserve

The account holds stocks and cash at Schwab. The **PFUSDC reserve** holds the asset used to pay holders on PFTL. PFUSDC is USDC brought onto PFTL by proof, as shown in Bob's journey below.

- **Any holder can burn B23 against the reserve** whenever a current NAV exists. The holder receives NAV minus *x* basis points in PFUSDC. A basis point is one hundredth of a percentage point.
- **The fee moves in the same transaction.** The management wallet receives the fee. Both payments appear in one receipt and add up to the full NAV value of the B23 burned.
- **Each burn is capped by the reserve.** A request larger than the PFUSDC available is rejected whole. It never half-fills.
- **The issuer can add PFUSDC at any time.** Adding to the reserve creates no B23.
- **The issuer sets *x* and can change it at any time**, between 0 and 500 basis points, without redeploying anything. The change takes effect as a new on-chain route policy, which holds the rules for reserve payments. A burn signed under the old setting is rejected once the new one is live.

This reserve gives B23 its pull toward NAV. When the market price is below NAV minus the fee, any holder can buy B23 there and burn it at NAV. That buying pulls the market price up. When the market trades above NAV, the issuer can mint at NAV within the packet's cap and sell. That selling pulls the market price down.

## Bob: from MetaMask to B23

{{< b23-flow kind="bob" >}}

Bob holds USDC on Ethereum in MetaMask and wants B23. He uses Task Node. MetaMask signs the Ethereum side. His B23 lives in his Task Node wallet, whose ML-DSA keys are created in his browser and stored encrypted there.

**1. Connect MetaMask.** Bob opens his PFTL wallet in Task Node and connects MetaMask. Task Node shows his PFTL address as the deposit recipient.

**2. Convert USDC into PFUSDC.** Bob approves USDC and deposits it into the PFUSDC vault contract on Ethereum. The deposit names his PFTL address. Once Ethereum finalizes the block, a prover generates an SP1 zero-knowledge proof: a cryptographic proof that the deposit is in finalized Ethereum state. PFTL checks it and credits Bob exactly the deposited amount as PFUSDC. Verification uses the proof rather than committee signatures, and each deposit can be claimed once. The wallet shows confirmation, Ethereum finality, proof capture, proving, verification and credit.

**3. Buy B23 on the market.** Bob places a buy order with PFUSDC on PFTL's order book. When it meets Alice's sell offer, B23 moves to Bob and PFUSDC moves to Alice. Supply and the reserve stay unchanged.

Bob now holds B23. He can sell it on the market or convert B23 back to PFUSDC at NAV against the reserve.

## Alice: issuing B23

{{< b23-flow kind="alice" >}}

Alice is the issuer. She works on PFTL inside Task Node.

**1. Mint B23 against the Schwab account.** Alice submits the day's signed packet and finalizes the NAV epoch. She mints at NAV within its supply cap. Additional issuance requires a packet showing the added account value that supports the added supply.

**2. Set up the reserve.** Alice adds PFUSDC and sets the fee *x*. Burns pay holders NAV less the fee and pay the fee to the management wallet. Alice can add PFUSDC or change the fee at any time, with no redeploy.

**3. Put up a market.** Alice posts a sell offer on PFTL's order book from a holder account separate from the issuer account. PFTL keeps issuing and trading apart by requiring that separation. She can cancel any unfilled part of the offer.

## How B23 compares with industry proof of reserves

{{< b23-flow kind="proof-comparison" >}}

Proof-of-reserves systems measure backing and publish evidence about it. The key questions are who reads the assets, what gets published, whether liabilities are counted and where enforcement happens.

**Ethena custodian attestations.** Ethena's USDe is backed by assets held off-exchange with institutional custodians. Each month, Ethena publishes reports from all its integrated custodians. They confirm the existence, control and value of the backing assets. The custodians observe the assets, and Ethena publishes the reports on its website and Transparency dashboard. Nothing on-chain acts on them.

**Ethena weekly proof of reserves.** A program inside an AWS Nitro enclave, an isolated computing environment, reads balances and derivatives positions from custodians, exchanges and the blockchain. It values spot assets with Pyth prices. It checks whether backing exceeds USDe supply, whether opposing positions offset price exposure and whether only approved assets are used. The enclave signs its answers. Outside attestors check that signature, the API credentials and whether the enclave ran a build they reproduced from the code. Ethena does not describe any contract that uses the proof to gate minting.

**Chaos Labs proof of reserves.** Chaos Labs reads collateral on-chain and turns custodian and exchange data into on-chain inputs. Its oracle—a service that supplies data to the chain—tracks locked reserves, issued supply across supported chains and whether reserves meet or exceed supply. Any contract can read the result in one call. Whether a contract acts on it is up to each integrator.

**Chainlink Proof of Reserve.** Chainlink publishes reserve figures through the same interface as a price feed. Off-chain figures come from an API operated by an auditor, accounting firm, custodian or issuer. Chainlink node operators carry the number on-chain. Chainlink notes that many of these feeds rely on a single data provider, and it requires contracts that use them to add their own value bounds, caps, circuit breakers, freshness checks and pause controls. Comparing reserves with supply, and acting on it, is the consuming contract's job.

**B23 on PFTL.** The issuer's reader takes Schwab's net liquidation value at a fixed daily cutoff. The issuer signs the reserve packet with ML-DSA. Its account value, NAV and supply become ledger state. Consensus checks the backing calculation, caps supply and requires the current finalized epoch for mints and burns. Reserve payments and the fee split follow the same protocol rules.

The distinction is where enforcement lives. Chainlink and Chaos Labs feeds can drive enforcement in each contract that chooses to read them. B23 puts the rule in the base protocol. No transaction can mint B23 outside it.

## Safeguards

B23 ties a fixed daily read to a permanent record, a supply cap and visible reserve payments.

### In B23's rules today

- **A fixed cutoff and a fixed measure.** The reader uses Schwab's reported net liquidation value at the same time each day.
- **Permanent packets.** Each packet commits to account identity, cutoff, value and the hashes behind it. Later records for that cutoff can be checked against those hashes.
- **A backing check and a supply cap.** Consensus checks packet supply times NAV against account value, then checks each mint against packet supply.
- **Current epoch checks.** Mints and burns name the current epoch and packet. Reserve burns also carry a maximum NAV age in the route policy.
- **Visible, atomic payments.** The reserve is on-chain. Each completed burn pays the holder and management wallet together.
- **A separate market.** Order-book prices leave supply and NAV unchanged.

### The next layers

- **Independent readers.** Several operators read the same account with separate sessions, servers and code. Every registered reader agrees before a packet finalizes.
- **Repeatable cutoff values.** Readers rebuild value as of the cutoff and match every account flow to on-chain events.
- **A nonce in the money.** The chain publishes an unpredictable number. A small cash transfer makes the account balance end in those cents. A read showing that balance demonstrates account control after the number appeared.
- **Withdrawal drills.** A small amount travels from Schwab back to PFUSDC on a schedule, making the exit path visible on-chain.
- **Origin proofs.** A TLS transcript proof establishes that the read's bytes came from Schwab's servers.
- **Withdrawal controls.** Verifiable controls keep outgoing account transfers tied to pre-agreed destinations.

## Two routes for USDC: Ethereum and Arc

Bob enters from Ethereum mainnet because his USDC is there. PFTL also has an ingress route from Arc, Circle's EVM chain. Both routes produce PFUSDC.

- **Finality.** Ethereum finalizes in minutes. Arc finalizes each block in under a second using Tendermint-style BFT consensus, a method for validators to agree on blocks, among a permissioned validator set.
- **Proof checks.** The Ethereum SP1 proof checks Ethereum finality and the deposit. The Arc proof checks validator signatures and the deposit receipt against a validator set pinned by PFTL governance.
- **Steps from Ethereum.** The direct route is approve, deposit and wait for PFUSDC. Going through Arc adds a transfer through Circle's CCTP first. Circle lists roughly 15 to 19 minutes for a standard transfer or about 20 seconds for a fast one.
- **Effect on B23.** Both routes produce PFUSDC without changing the Schwab account, NAV, B23 reserve or market.

Ethereum serves Bob directly. Arc serves users who already hold USDC there.

## What this does not prove

- **The packet is issuer-signed, not Schwab-signed.** The chain proves which packet finalized and whether transactions obeyed it. It does not prove that the submitted figure matches Schwab's API at the cutoff.
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
