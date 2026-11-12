---
title: "How a Schwab-Backed NAVCoin Works"
date: 2026-11-12T00:00:00Z
draft: false
summary: "B23 is a native PFTL asset that trades to the net liquidation value of a Charles Schwab brokerage account. The account's value is committed on-chain every day, consensus only lets supply move against that figure, and holders can exit at NAV through an on-chain PFUSDC reserve."
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

B23 is a NAVCoin backed by a Charles Schwab brokerage account. It is a native asset on PFTL, the Post Fiat L1, and it trades to the account's net asset value (NAV).

Once a day, at a fixed cutoff, the account's value is committed on-chain exactly as Schwab reports it. Consensus then lets B23 be minted or burned only at that value, only on the current day's figure, and never beyond the supply that figure supports. Every signature on PFTL uses ML-DSA, a post-quantum signature scheme.

The result is a brokerage account that any PFTL wallet can hold a share of, trade, and exit at NAV. This post explains how the account value reaches the chain and how buyers and the issuer use B23 inside Task Node. It also compares B23 with the proof-of-reserves systems in use across the industry and sets out the safeguards around a centrally held account.

## The short version

- **One account is the reserve.** NAV per B23 is the account's net liquidation value divided by B23 supply.
- **A daily read becomes ledger state.** The value is read at a fixed cutoff and submitted to PFTL as a reserve packet. Finalizing the packet opens a NAV epoch.
- **Minting is capped by the packet.** The issuer mints B23 at NAV, and the chain rejects any mint past the supply the packet supports.
- **A PFUSDC reserve is the exit.** Any holder can burn B23 at NAV and receive PFUSDC, less a small fee that goes to a management wallet in the same transaction.
- **The market is separate.** B23 also trades on PFTL's native order book. A trade moves existing B23 between wallets and never changes supply.

## How the account becomes NAV

{{< b23-flow kind="mechanism" >}}

The reserve is a single Schwab brokerage account. Schwab computes a **net liquidation value** for it: what everything in the account is worth, minus what the account owes the broker. The margin loan and the value of short positions are already subtracted. B23 uses that number as Schwab reports it, with no adjustments.

**1. The daily read.** At the same cutoff time every day, a reader queries the account through Schwab's API. It records the net liquidation value, the balances and the positions. Because the cutoff is fixed, nobody picks the moment of the read.

**2. The reserve packet.** The issuer submits the read to PFTL as a signed reserve packet. The packet carries the account value, the cutoff time, a commitment to the account's identity, and hashes of the positions, cash and liabilities behind the figure. Once on-chain the packet is permanent. A later packet can follow it, but nothing can replace it.

**3. The NAV epoch.** Finalizing the packet opens a new NAV epoch. NAV per B23 is the account value divided by the supply in the packet. Each epoch number must be higher than the last, so the chain moves forward one day at a time.

**4. Mint at NAV.** Only the issuer can mint, and every mint must name the current epoch and its packet hash. Consensus rejects a mint against an older epoch, and it rejects any mint that would push supply past the packet's figure.

The opening mint is against the whole account balance. The 2,000 B23 minted earlier against one measured $2,000 wire are part of that opening supply, not an addition to it. That wire was already in the account, so it counts once. From the opening epoch on, every B23 tracks an equal share of the whole account, not a particular deposit.

### What anyone can check on PFTL

- Every reserve packet: its account value, cutoff time, account commitment and the hashes behind them.
- That each NAV epoch finalized, and in what order.
- That total B23 supply never exceeds what the current packet supports.
- That every mint and every burn at NAV used the current epoch and its packet.
- The PFUSDC in the reserve, the fee setting, and each payment out of the reserve, down to the atom.

## Three operations, three different effects

B23 moves in three ways, and they do different things:

- **Mint at NAV** (issuer only). New B23 is created against the account value in a finalized packet. Supply rises.
- **Burn at NAV** (any holder). B23 is destroyed and the holder is paid PFUSDC from the reserve. Supply and the reserve both fall.
- **Buy or sell on the market** (anyone). Existing B23 changes hands for PFUSDC at a price buyers and sellers agree on. Supply and the reserve do not change.

Task Node keeps these on separate screens with separate labels, so an order-book purchase is never shown as a mint.

## The PFUSDC reserve

The account holds stocks and cash at Schwab. A holder who wants out needs something liquid on PFTL. That is the job of the **PFUSDC reserve**: a standing pool of PFUSDC tied to B23 on-chain. PFUSDC is USDC brought onto PFTL by proof, described in Bob's journey below.

- **Any holder can burn B23 against the reserve** whenever a current NAV exists. The holder receives NAV minus *x* basis points in PFUSDC.
- **The fee is paid in the same transaction.** The *x* basis points go to a management wallet. One receipt shows both payments, and the two add up to the full NAV value of the B23 burned.
- **Each burn is capped by the reserve.** A request larger than the PFUSDC available is rejected whole. It never half-fills.
- **The issuer can top up the reserve at any time.** Adding PFUSDC mints no B23.
- **The issuer sets *x* and can change it at any time**, between 0 and 500 basis points, without redeploying anything. The new setting takes effect as a new route policy on-chain. A burn signed under the old setting is rejected once the new one is live.

## Bob: from MetaMask to B23

{{< b23-flow kind="bob" >}}

Bob holds USDC on Ethereum in MetaMask and wants B23. He does everything inside Task Node. MetaMask signs only the Ethereum side. His B23 lives in his Task Node wallet, whose ML-DSA keys are created in his browser and stored encrypted there.

**1. Connect MetaMask.** Bob opens his PFTL wallet in Task Node and connects MetaMask. Task Node shows his PFTL address as the recipient of the deposit.

**2. Convert USDC into PFUSDC.** Bob approves USDC and deposits it into the PFUSDC vault contract on Ethereum. The deposit names his PFTL address. Once Ethereum finalizes the block, a prover generates an SP1 zero-knowledge proof that the deposit sits in finalized Ethereum state. PFTL verifies the proof and credits Bob exactly the deposited amount as PFUSDC. No committee signs anything, and the same deposit cannot be claimed twice. The wallet shows each stage as it happens: deposit confirmed, Ethereum finality, state proof captured, proving, verification, credit.

**3. Buy B23 on the market.** Bob places an order to buy B23 with PFUSDC on PFTL's order book. When it meets Alice's sell offer, B23 moves to Bob and PFUSDC moves to Alice. No B23 is created and the reserve does not change.

Bob now holds B23. To leave, he can sell it on the market or burn it at NAV against the reserve.

## Alice: issuing B23

{{< b23-flow kind="alice" >}}

Alice is the issuer. She works entirely on PFTL inside Task Node and never needs MetaMask.

**1. Mint B23 against the Schwab account.** Alice submits the day's reserve packet, finalizes the NAV epoch and mints B23 at NAV, up to the supply the packet supports.

**2. Set up the reserve.** Alice adds PFUSDC to the B23 reserve and sets the fee *x*. From then on any holder can burn B23 at NAV minus *x* basis points, the management wallet receives the *x* basis points on every burn, and Alice can top up the reserve or change *x* whenever she chooses.

**3. Put up a market.** Alice posts a sell offer, B23 for PFUSDC, on PFTL's order book. She posts it from a holder account that is separate from the issuer account, because the protocol does not let an issuer account post offers in its own asset. That keeps issuing and trading apart on-chain. She can cancel any unfilled part of the offer.

## How B23 compares with industry proof of reserves

{{< b23-flow kind="proof-comparison" >}}

Every proof-of-reserves system answers the same questions: who looks at the reserves, what gets published, how often, whether what is owed is counted, and whether anything on-chain acts on the result.

**Ethena custodian attestations.** Ethena's USDe is backed by assets held off-exchange with institutional custodians. Each month Ethena publishes attestation reports from all of its integrated custodians. These reports confirm the existence, control and value of the backing assets. The custodians are the observers, and the reports are published on Ethena's website and Transparency dashboard. They cover assets held. Nothing on-chain acts on them.

**Ethena weekly proof of reserves.** Ethena also publishes a weekly proof. A program inside an AWS Nitro enclave pulls balances and derivatives positions from custodians, exchanges and the blockchain, and values spot assets with Pyth prices. It then answers fixed questions: does the backing exceed USDe supply, is the book delta-neutral, and are only approved assets used. The enclave signs its answers. Outside attestors check the signature, check that the enclave ran a build they reproduced from the code, and check the API credentials. The proof compares backing with USDe supply. Ethena does not describe any contract that uses the proof to gate minting.

**Chaos Labs proof of reserves.** Chaos Labs runs a proof-of-reserve oracle. It reads collateral held on-chain and turns custodian and exchange data into on-chain inputs. It tracks three things: locked reserves, issued supply across every supported chain, and a signal that says whether reserves meet or exceed that supply. Any contract can read the result in a single call. Whether anything acts on it is up to each integrator.

**Chainlink Proof of Reserve.** A Chainlink Proof of Reserve feed publishes a reserve figure on-chain through the same interface as a price feed. For reserves held off-chain, the number comes from an API: an auditor or accounting firm, the custodian, or the issuer's own server. Chainlink node operators carry that number on-chain. Chainlink warns that many of these feeds rely on a single data provider. It requires contracts that use them to add their own value bounds, caps, circuit breakers, freshness checks and pause controls. Comparing the reserve with token supply, and acting on it, is the consuming contract's job.

**B23 on PFTL.** The issuer's reader takes Schwab's net liquidation value at a fixed daily cutoff. That figure already subtracts the margin loan and short positions. It is committed as a reserve packet signed with ML-DSA. The packet is not a report about B23 that a contract may choose to read. It is the ledger state that B23's supply is tied to. The chain does not mint against a packet that has not finalized, mint past its figure, or price a mint or burn on anything but the current epoch. The exit is part of the same rules: the reserve pays at NAV under consensus, and the fee split appears in the same receipt.

That is the step B23 adds to the industry pattern. In the systems above, the proof is evidence that sits next to the asset. For B23, the proof is a precondition for supply to move.

## Safeguards

Reading a centrally held account has four weak points. The moment of the read can be chosen, the number can be edited before it is committed, the account can change after the read, and a holder can find no liquidity on the way out. B23's design answers each one.

### In B23's rules today

- **A fixed cutoff and Schwab's own figure.** The read happens at the same time every day and uses Schwab's reported net liquidation value without adjustment. Nobody picks a favorable moment or a favorable method.
- **Permanent, committed packets.** Each packet commits to the account's identity, the cutoff, the value, and hashes of the positions, cash and liabilities behind it. History cannot be rewritten, and any later statement for that day can be checked against the hashes.
- **Supply bounded by the packet.** No mint can take supply past the figure in the current packet.
- **Current epoch only.** Mints and burns must name the current epoch and its packet. Burns through the reserve also carry a maximum NAV age set in the route policy. Past it, they stop until a new epoch finalizes. A missed update is visible to everyone at once.
- **An exit enforced by consensus.** The reserve is on-chain and visible. Each burn fills whole or not at all, and the fee split is atomic. The issuer can add to the reserve without minting.
- **A separate market.** Order-book prices never change supply or NAV.

### The next layers

- **Independent readers.** Several operators read the same account, each with its own session, servers and code. A packet finalizes only when every registered reader agrees.
- **Reads that give the same answer every time.** The value is rebuilt as of the cutoff, and every flow in and out of the account is matched against on-chain events. A read taken at any hour then returns the same number.
- **A nonce in the money.** The chain publishes an unpredictable number, and a small cash transfer makes the account balance end in those cents. A read showing that balance proves the account was live and under control after the number existed.
- **Withdrawal drills.** On a schedule, a small amount travels the whole path from the Schwab account back to PFUSDC, visible on-chain. The drill shows that money comes out, not only that it is there.
- **Origin proofs.** A TLS transcript proof shows that the bytes of the read came from Schwab's servers.
- **Withdrawal limits.** Money leaving the account is restricted to pre-agreed destinations, and the restriction itself can be checked.

## Two routes for USDC: Ethereum and Arc

Bob's USDC enters from Ethereum mainnet because that is where his USDC is. PFTL also has an ingress route from Arc, Circle's EVM chain. The two differ at the source; both end in PFUSDC on PFTL.

- **Finality.** Ethereum finalizes in minutes. Arc finalizes each block in under a second using Tendermint-style BFT consensus among a permissioned set of validators.
- **What the proof checks.** On the Ethereum route, the SP1 proof checks Ethereum's own finality and the deposit. On the Arc route, it checks the Arc validator signatures and the deposit receipt against a validator set pinned by PFTL governance.
- **Steps for an Ethereum user.** The Ethereum route is approve, deposit, wait for PFUSDC. The Arc route adds a hop first: moving USDC from Ethereum to Arc through Circle's CCTP, which Circle lists at roughly 15 to 19 minutes for a standard transfer or about 20 seconds for a fast one.
- **Effect on B23.** None. Either route produces PFUSDC. Neither changes the account, the NAV, the reserve or the market.

The Ethereum route serves Bob directly. Arc is the natural second route for users who already hold USDC on Arc.

## What this does not prove

- The account value is an operator read of Schwab's API. Schwab does not sign it. From the chain alone, a reader can confirm that each packet is final and that supply and every burn obey it. A reader cannot confirm that the figure matches what Schwab showed at the cutoff.
- A packet records the account at the cutoff. It does not stop money leaving the account after the read.
- Four items can post to the account after a read: cash legs of unsettled trades, accrued margin interest, dividends owed on short positions, and fees. Any of them can move the next day's figure.
- NAV uses Schwab's own prices. No second pricing source checks them.
- Burns at NAV are limited to the PFUSDC in the reserve. Beyond that, holders sell on the market at the market price.
- There is one reader today. The next layers listed above are not yet live.
- PFTL's Arc route has run end to end on Arc testnet. B23's entry route is Ethereum.

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
