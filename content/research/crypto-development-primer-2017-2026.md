---
title: "Crypto, 2017 to 2026: A Primer on What Was Built and What Was Decided"
date: 2026-09-30T00:00:00Z
url: "/research/crypto-primer-2017-2026/"
summary: "A year-by-year primer on the technologies and political decisions that shaped crypto, from the ICO boom to tokenized stocks."
categories:
  - Post Fiat Research
tags:
  - Primer
  - History
  - Stablecoins
  - Privacy
  - Zero Knowledge
  - Regulation
---

<style>
.pfp-fig{margin:1.7rem 0 2.1rem;padding:1.15rem 1.15rem .95rem;border:1px solid var(--border);border-radius:14px;background:var(--entry);font-size:.86rem;line-height:1.38;color:var(--primary)}
.pfp-title{font-weight:700;font-size:.74rem;letter-spacing:.07em;text-transform:uppercase;color:var(--secondary);margin:0 0 .85rem}
.pfp-sub{font-weight:700;font-size:.8rem;margin:1rem 0 .5rem;color:var(--primary)}
.pfp-cap{font-size:.76rem;color:var(--secondary);margin-top:.8rem}
.pfp-row{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.pfp-node{padding:.45rem .7rem;border-radius:9px;border:1px solid var(--border);background:var(--theme);min-width:0}
.pfp-node b{display:block;font-size:.83rem;line-height:1.25}
.pfp-node small{display:block;color:var(--secondary);font-size:.73rem;line-height:1.3;margin-top:.1rem}
.pfp-arr{color:var(--secondary);font-size:1rem;padding:0 .1rem;flex:0 0 auto}
.pfp-flow{flex-wrap:nowrap;align-items:stretch}
.pfp-flow>.pfp-node{flex:1 1 0}
.pfp-flow>.pfp-arr{align-self:center}
.pfp-api{font-size:.74rem;color:var(--secondary);flex:0 0 auto;align-self:center}
.pfp-down{text-align:center;color:var(--secondary);font-size:1rem;line-height:1;margin:.35rem 0}
.pfp-grid2{display:grid;grid-template-columns:1fr 1fr;gap:.7rem}
.pfp-grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.6rem}
.pfp-grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem}
@media (max-width:640px){.pfp-flow{flex-direction:column}.pfp-flow>.pfp-arr{transform:rotate(90deg);text-align:center}.pfp-grid2,.pfp-grid3{grid-template-columns:1fr}.pfp-grid4{grid-template-columns:1fr 1fr}.pfp-layer{grid-template-columns:1fr!important}.pfp-nowrap{flex-wrap:wrap!important}}
.pfp-chip{display:inline-block;padding:.16rem .55rem;border-radius:99px;font-size:.74rem;margin:.12rem .08rem;border:1px solid var(--border);background:var(--theme);white-space:nowrap}
.pfp-layer{display:grid;grid-template-columns:6.6rem 1fr;gap:.6rem;align-items:center;padding:.5rem 0;border-top:1px dashed var(--border)}
.pfp-layer:first-of-type{border-top:0}
.pfp-lab{font-weight:700;font-size:.7rem;letter-spacing:.07em;text-transform:uppercase}
.pfp-g{border-color:rgba(35,197,142,.55)!important;background:rgba(35,197,142,.11)!important}
.pfp-b{border-color:rgba(71,148,255,.55)!important;background:rgba(71,148,255,.11)!important}
.pfp-a{border-color:rgba(245,165,36,.6)!important;background:rgba(245,165,36,.12)!important}
.pfp-r{border-color:rgba(239,93,93,.6)!important;background:rgba(239,93,93,.12)!important}
.pfp-p{border-color:rgba(163,124,240,.6)!important;background:rgba(163,124,240,.12)!important}
.pfp-tg{color:#23c58e}.pfp-tb{color:#4794ff}.pfp-ta{color:#f5a524}.pfp-tr{color:#ef5d5d}.pfp-tp{color:#a37cf0}.pfp-ts{color:var(--secondary)}
.pfp-dash{border-style:dashed!important}
.pfp-box{border:1px solid var(--border);border-radius:11px;padding:.7rem .8rem;background:var(--theme)}
.pfp-box>b{display:block;margin-bottom:.45rem}
.pfp-box .pfp-node{background:var(--entry)}
.pfp-tl{position:relative;margin-left:.4rem;padding-left:1.1rem;border-left:2px solid rgba(127,127,127,.35)}
.pfp-tli{position:relative;display:grid;grid-template-columns:2.9rem 1fr;gap:.4rem;align-items:baseline;padding:.3rem 0}
.pfp-tli .pfp-chip{margin-left:.35rem;white-space:normal}
.pfp-tli:before{content:"";position:absolute;left:-1.5rem;top:.66rem;width:.62rem;height:.62rem;border-radius:50%;background:var(--secondary)}
.pfp-tli.pfp-hot:before{background:#23c58e}
.pfp-yr{font-weight:700;font-variant-numeric:tabular-nums;min-width:2.6rem}
.pfp-step{display:grid;grid-template-columns:1.6rem 1fr;gap:.5rem;align-items:start;padding:.3rem 0}
.pfp-num{width:1.45rem;height:1.45rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;background:rgba(71,148,255,.18);color:#4794ff}
.pfp-seg{display:flex;border-radius:8px;overflow:hidden;border:1px solid var(--border)}
.pfp-seg>div{padding:.4rem .55rem;font-size:.76rem;text-align:center;border-right:1px solid var(--border)}
.pfp-seg>div:last-child{border-right:0}
.pfp-bar{display:grid;grid-template-columns:5.6rem 1fr 4.4rem;gap:.55rem;align-items:center;padding:.3rem 0}
.pfp-track{height:.95rem;border-radius:99px;background:var(--theme);border:1px solid var(--border);overflow:hidden}
.pfp-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#4794ff,#23c58e)}
.pfp-val{font-variant-numeric:tabular-nums;text-align:right;font-weight:700}
.pfp-link{flex:1;min-width:4.5rem;text-align:center;font-size:.72rem;color:var(--secondary);border-bottom:2px solid rgba(245,165,36,.75);padding-bottom:.15rem;margin:0 .15rem}
.pfp-note{font-size:.76rem;color:var(--secondary)}
.pfp-svg{width:100%;height:auto;display:block}
.pfp-scroll{overflow-x:auto}
.pfp-scroll .pfp-svg{min-width:540px}
.pfp-svg text{fill:var(--primary);font-family:inherit}
.pfp-svg .m{fill:var(--secondary)}
.pfp-svg .ln{stroke:var(--secondary);fill:none}
.pfp-svg .bx{fill:var(--theme);stroke:var(--border)}
</style>

In 2017 crypto's two largest networks were a payment system that cleared about seven transactions a second and a smart-contract chain used mostly to sell tokens. In 2026, dollar stablecoins move trillions of dollars a month. The depository that settles American equities runs a tokenization service on a blockchain. A decentralized exchange lists perpetual futures on the S&P 500. The US Treasury holds a Strategic Bitcoin Reserve.

It is written for a technical reader who knows distributed systems and data infrastructure but has watched crypto only from the outside. Each year has five parts: what was **built**, what was **decided** (law, courts, regulators, politics), a **diagram**, the **status** of those technologies as of September 2026, and **reading**. Coverage follows market value and design significance: a development gets space if it moved a top-50 asset, created a new category, or changed the law, so a few mid-cap networks (Zcash, NEAR, Bittensor, World) get room because they are the clearest examples of a technology. The publisher, Post Fiat Foundation, runs a network in the XRP family; see the disclosure at the end. Topics that span several years are explained once, in the year they mattered most, and the explanation carries forward to today.

### The map

<div class="pfp-fig"><div class="pfp-title">The map: what got built, 2017 → 2026</div><div class="pfp-layer"><div class="pfp-lab pfp-tp">Politics</div><div><span class="pfp-chip pfp-p">DAO Report</span><span class="pfp-chip pfp-p">Libra backlash</span><span class="pfp-chip pfp-p">Tornado sanctions</span><span class="pfp-chip pfp-p">Spot ETFs</span><span class="pfp-chip pfp-p">MiCA</span><span class="pfp-chip pfp-p">GENIUS Act</span><span class="pfp-chip pfp-p">SEC–CFTC split</span><span class="pfp-chip pfp-p">CLARITY stall</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-ta">Markets</div><div><span class="pfp-chip pfp-a">ICOs</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-a">AMMs / DeFi</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-a">Perp DEXs</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-a">Tokenized stocks</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-tg">Money</div><div><span class="pfp-chip pfp-g">Tether</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-g">USDC</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-g">Terra (failed)</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-g">Regulated dollars</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-tb">Privacy</div><div><span class="pfp-chip pfp-b">Sapling</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Orchard</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Ironwood</span> <span class="pfp-chip pfp-b">Mixers</span><span class="pfp-chip pfp-b">TEEs</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-tb">Proofs</div><div><span class="pfp-chip pfp-b">SNARKs</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Rollups</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">zkVMs</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Real-time proving</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-ts">Settlement</div><div><span class="pfp-chip ">Bitcoin (PoW)</span><span class="pfp-chip ">Ethereum (PoS)</span><span class="pfp-chip ">Solana</span><span class="pfp-chip ">Avalanche</span><span class="pfp-chip ">BNB</span><span class="pfp-chip ">XRPL</span><span class="pfp-chip ">Tron</span><span class="pfp-chip ">Hyperliquid</span><span class="pfp-chip ">NEAR</span><span class="pfp-chip ">Canton</span></div></div><div class="pfp-layer"><div class="pfp-lab pfp-ts">Support</div><div><span class="pfp-chip ">Oracles</span><span class="pfp-chip ">Storage (Arweave, Filecoin)</span><span class="pfp-chip ">Identity (World)</span><span class="pfp-chip ">AI markets (Bittensor)</span><span class="pfp-chip ">Restaking</span></div></div><div class="pfp-cap">Each layer depends on the ones below it; politics shaped all of them.</div></div>

### The scoreboard, 30 September 2026

Selected assets, with market values from CoinMarketCap. The total crypto market is $2.87 trillion, and bitcoin's share is 58.7%.

| Asset | Market cap | What it is |
|---|---|---|
| BTC | $1,683B | Proof-of-work money; the reserve asset |
| ETH | $327B | Proof-of-stake smart-contract platform |
| USDT | $184B | Largest dollar stablecoin (Tether) |
| BNB | $102B | Binance's exchange and chain token |
| XRP | $94.5B | XRP Ledger, validator-list consensus |
| USDC | $74B | Regulated dollar stablecoin (Circle) |
| SOL | $70B | High-throughput monolithic L1 |
| TRX | $32B | Tron, the main USDT payments rail |
| ZEC | $24.2B | Zcash, shielded proof-of-work money |
| HYPE | $21.5B | Hyperliquid, on-chain order-book exchange |
| DOGE | $14.8B | Dogecoin, the original memecoin |
| LINK | $10.6B | Chainlink, oracle network |
| XMR | $10.2B | Monero, private-by-default money |
| ADA | $9.0B | Cardano, proof-of-stake L1 |
| NEAR | $6.9B | Sharded L1; cross-chain intents |
| AVAX | $4.8B | Avalanche, network of sovereign L1s |
| TAO | $3.5B | Bittensor, markets for machine learning |
| WLD | $2.1B | World, proof of personhood |

Stablecoins total $285 billion by CoinMarketCap's count and about $300 billion or more by other trackers.

### If you read only this

1. **Settlement became provable.** Ethereum moved to proof of stake (2022) and pushed execution onto rollups (2021–24). Proving costs then fell far enough (2025) that validators may eventually check a proof instead of re-running each block; that shift is still a proposal.
2. **The dollar became the killer app.** Stablecoins grew from a trading chip into a payments rail. Each failure (Libra, Terra, SVB, FTX) produced a rule, ending in the GENIUS Act (2025).
3. **Washington changed sides.** The period started with enforcement (2017–24) and ended with sponsorship (2025–26). Congress passed a stablecoin law but stalled on market structure, so the SEC and CFTC are writing the rulebook themselves.
4. **Exchanges moved on-chain.** AMMs (2020) came first, then order-book perp DEXs such as Hyperliquid and Lighter (2024–25), then tokenized stocks and the DTCC (2025–26).
5. **Privacy survived, under stress.** Zcash's pools moved from trusted setups to formally verified circuits after a live bug. Treasury sanctioned Tornado Cash and then lost in court. TEEs now offer a faster, weaker alternative.
6. **Bitcoin changes slowly, on purpose.** SegWit and Taproot shipped. Covenants are stuck, and quantum migration is the hardest open problem in the industry.

### Terms used throughout

| Term | Meaning |
|---|---|
| Slashing | Destroying part of a validator's stake as a penalty for provable misbehavior |
| MEV | Profit a block producer can extract by ordering, inserting or censoring transactions |
| Sequencer | The operator that orders transactions for a rollup before they reach Ethereum |
| Nullifier | A one-time tag that marks a private note or credential as used, without revealing which one |
| Perp | A perpetual future: a leveraged contract with no expiry, kept near spot by periodic funding payments |
| DCM | Designated contract market, a CFTC-registered derivatives exchange |
| TEE | Trusted execution environment, a hardware enclave that hides computation from the machine's operator |

Dates for 2026 come from regulator releases and company announcements. Where something is proposed, scheduled or on testnet, the text says so.

---

## 2017: The token sale and the block-size war

**Built.** ERC-20, a standard interface for tokens on Ethereum, meant a new asset took about fifty lines of code. The result was the initial coin offering. Projects raised roughly $6 billion that year by selling tokens directly to the public: Filecoin raised $257 million, Tezos $232 million, and EOS ran a year-long sale that ended near $4 billion. Cardano and Tron, both funded in this period, are still top-20 assets. In November, CryptoKitties congested Ethereum and helped popularize ERC-721, the standard later used for NFTs.

Bitcoin had its constitutional crisis the same year. Miners and large companies wanted bigger blocks. Node operators and developers wanted to keep blocks small and scale in layers. Segregated Witness (SegWit) was the compromise. It moves signatures out of the data that defines a transaction's ID. That fixed transaction malleability, where a third party could change a transaction's ID before it confirmed, and raised effective capacity through a new "block weight" limit. Miners stalled. Users answered with a user-activated soft fork (BIP 148), under which their nodes would reject blocks that failed to signal for SegWit. SegWit activated on 24 August 2017. The bigger-block faction had already forked away on 1 August as Bitcoin Cash. The outcome set a precedent: in Bitcoin, the economic nodes that accept payments define the rules, and hashpower follows them. 

**Decided.**
- In July the SEC's **DAO Report** said tokens can be securities under the Howey test. That set the terms of US enforcement for eight years.
- In September China banned ICOs and closed its domestic exchanges.
- In December CBOE and CME listed cash-settled bitcoin futures. This was the first regulated US bitcoin derivative, and it later anchored the argument for spot ETFs. Bitcoin peaked near $19,800 that month.

<div class="pfp-fig"><div class="pfp-title">SegWit: signatures leave the transaction ID</div><div class="pfp-grid2"><div class="pfp-box"><b>Legacy transaction</b><div class="pfp-seg"><div style="flex:1">inputs</div><div class="pfp-r" style="flex:1.3">signatures</div><div style="flex:1">outputs</div></div><div class="pfp-note" style="margin-top:.45rem">All three are hashed into the txid, so a third party can tweak a signature and change the ID before it confirms.</div></div><div class="pfp-box"><b>SegWit transaction</b><div class="pfp-seg"><div style="flex:1">inputs</div><div style="flex:1">outputs</div></div><div class="pfp-seg pfp-g" style="margin-top:.35rem"><div style="flex:1">witness: signatures · counted at ¼ weight</div></div><div class="pfp-note" style="margin-top:.45rem">The txid is fixed, and the discount leaves more room per block.</div></div></div><div class="pfp-sub">Who followed which rules</div><div class="pfp-scroll"><svg class="pfp-svg" viewBox="0 0 680 120" role="img" aria-label="Bitcoin fork tree">
<path class="ln" stroke-width="2.5" d="M10 42 H150"/>
<path stroke="#23c58e" stroke-width="2.5" fill="none" d="M150 42 H660"/>
<path stroke="#f5a524" stroke-width="2.5" fill="none" d="M150 42 C175 42 175 88 200 88 H540"/>
<circle cx="150" cy="42" r="6" fill="#4794ff"/>
<text x="10" y="30" font-size="13" font-weight="700">BTC</text>
<text x="140" y="68" font-size="12" class="m" text-anchor="end">1 Aug 2017</text>
<circle cx="265" cy="42" r="5" fill="#23c58e"/><text x="225" y="30" font-size="12.5">SegWit · 24 Aug 2017</text>
<circle cx="455" cy="42" r="5" fill="#23c58e"/><text x="420" y="30" font-size="12.5">Taproot · 2021</text>
<text x="612" y="30" font-size="12.5" font-weight="700">today</text>
<text x="205" y="112" font-size="12.5">BCH · 8 MB blocks</text>
<circle cx="430" cy="88" r="5" fill="#f5a524"/><text x="395" y="112" font-size="12.5">BSV split · 2018</text>
</svg></div><div class="pfp-cap">Economic nodes enforced SegWit; the big-block faction left as Bitcoin Cash.</div></div>

**Status.** Most Bitcoin transactions now use SegWit or Taproot outputs. Bitcoin Cash is worth $6.1 billion against bitcoin's $1.68 trillion.

**Reading.** [SEC, *Report of Investigation: The DAO* (2017)](https://www.sec.gov/litigation/investreport/34-81207.pdf). [BIP 141, *Segregated Witness*](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki). Jonathan Bier, *The Blocksize War* (2021).

---

## 2018: Winter, and the layers underneath

**Built.** Prices fell more than 80%, and the useful work moved to lower layers.

- **Lightning.** Lightning's mainnet beta shipped in March 2018. It uses payment channels: two parties lock funds in a 2-of-2 output and exchange signed balance updates off-chain. Payments route across chains of channels using hash time-locked contracts (HTLCs), so that each hop pays only on proof of the same secret. SegWit's malleability fix made this safe.
- **Zcash Sapling.** Sapling activated in October. It cut shielded-transaction proving from about 40 seconds and 3 GB of memory to a few seconds and about 40 MB, which made private payments possible on phones. Its Groth16 proofs still needed a multi-party "trusted setup" ceremony. If every participant in that ceremony had colluded, they could have forged coins undetectably, and removing that assumption drove the next four years of Zcash work.
- **Stablecoins.** USDC launched in September, from Circle and Coinbase, with monthly attestations. It was the first large stablecoin designed to satisfy US regulators. MakerDAO's Dai, a dollar backed by crypto collateral, had launched in December 2017.

**Decided.**
- **Hinman speech.** In June, SEC official William Hinman said ether had become "sufficiently decentralized" to fall outside securities law. The speech gave the industry its working theory of how a token stops being a security. It was later a central exhibit in the Ripple case.
- **ICO settlements.** In November the SEC settled with Airfox and Paragon, which had to register their tokens and offer refunds.

<div class="pfp-fig"><div class="pfp-title">Lightning: pay across a channel graph, touch the chain rarely</div><div class="pfp-row pfp-nowrap" style="flex-wrap:nowrap"><div class="pfp-node pfp-b"><b>Alice</b><small>payer</small></div><div class="pfp-link">channel · 0.5 BTC</div><div class="pfp-node "><b>Bob</b><small>routing node</small></div><div class="pfp-link">channel · 1.0 BTC</div><div class="pfp-node pfp-g"><b>Carol</b><small>payee</small></div></div><div class="pfp-sub">Alice pays Carol 0.01 BTC through Bob</div><div class="pfp-step"><div class="pfp-num">1</div><div>Carol picks a secret R and gives Alice its hash H.</div></div><div class="pfp-step"><div class="pfp-num">2</div><div>Alice → Bob: 0.0101 BTC, claimable with R before block t+40. Bob keeps 0.0001 as a fee.</div></div><div class="pfp-step"><div class="pfp-num">3</div><div>Bob → Carol: 0.0100 BTC, claimable with R before block t+20.</div></div><div class="pfp-step"><div class="pfp-num">4</div><div>Carol reveals R to get paid; Bob uses the same R to collect from Alice.</div></div><div class="pfp-cap">On-chain transactions happen only when channels open, close or are disputed.</div></div>

**Status.** Public Lightning capacity is a few thousand BTC, and most retail use runs through custodial wallets such as Cash App and Strike. For dollar payments, stablecoins won that market. Sapling's proof system still secures older Zcash notes, while newer ones live in Orchard and Ironwood (see 2022 and 2026).

**Reading.** [Poon and Dryja, *The Bitcoin Lightning Network* (2016)](https://lightning.network/lightning-network-paper.pdf). [Zcash Protocol Specification](https://zips.z.cash/protocol/protocol.pdf), Sapling sections. [W. Hinman, *When Howey Met Gary (Plastic)* (2018)](https://www.sec.gov/news/speech/speech-hinman-061418).

---

## 2019: Libra, and the birth of stablecoin politics

**Built.** In June, Facebook announced **Libra**. It was a stablecoin backed by a basket of currencies, governed by an association of 28 companies, and aimed at more than two billion users. Within four months PayPal, Visa and Mastercard had left the project. It shrank to a single-dollar coin called Diem and was sold for parts in January 2022. Finance ministers called private global money a threat to monetary sovereignty. Congress held hearings. Xi Jinping gave a speech in October endorsing blockchain and accelerating China's e-CNY, and the ECB began work on a digital euro. Every stablecoin law since then is partly a response to Libra.

Tether moved onto **Tron**, whose cheap transfers made it the main rail for dollar payments in emerging markets, which is why TRX is worth $32 billion today. Chainlink's oracle network went live in May and became the standard way to bring prices on-chain. MakerDAO launched multi-collateral Dai in November.

**Decided.**
- **Travel rule.** In June, FATF extended its "travel rule" to crypto service providers, requiring them to pass sender and recipient identity along with transfers. Compliance vendors have built around it ever since.
- **Tether.** The New York Attorney General sued Bitfinex and Tether in April over an $850 million hole that had been covered with Tether reserves. The case settled in 2021 for $18.5 million plus mandatory reserve disclosures. This began the proof-of-reserves thread, which runs through 2022 and ends in a Big Four audit in 2026.
- **Telegram.** The SEC won an order halting Telegram's $1.7 billion TON token. The community relaunched the chain without Telegram.

<div class="pfp-fig"><div class="pfp-title">The stablecoin lineage: each shock wrote a rule</div><div class="pfp-tl"><div class="pfp-tli"><span class="pfp-yr">2014</span><span>Tether launches the first dollar token</span></div><div class="pfp-tli"><span class="pfp-yr">2018</span><span>USDC launches with monthly attestations</span></div><div class="pfp-tli"><span class="pfp-yr">2019</span><span>Libra announced; finance ministers push back<span class="pfp-chip pfp-g">a sovereignty question</span></span></div><div class="pfp-tli"><span class="pfp-yr">2021</span><span>President's Working Group report<span class="pfp-chip pfp-g">issuers should be supervised like banks</span></span></div><div class="pfp-tli"><span class="pfp-yr">2022</span><span>Terra's algorithmic dollar collapses<span class="pfp-chip pfp-g">algorithmic designs barred</span></span></div><div class="pfp-tli"><span class="pfp-yr">2023</span><span>SVB fails; USDC trades at $0.87<span class="pfp-chip pfp-g">reserve quality and custody rules</span></span></div><div class="pfp-tli pfp-hot"><span class="pfp-yr">2024</span><span>MiCA stablecoin rules apply in the EU</span></div><div class="pfp-tli pfp-hot"><span class="pfp-yr">2025</span><span>GENIUS Act signed in the US</span></div><div class="pfp-tli pfp-hot"><span class="pfp-yr">2026</span><span>GENIUS rulemaking; Tether's first full audit</span></div></div></div>

**Status.** Libra's premise, a dollar token used worldwide, came true through Tether, Circle and Tron rather than Facebook.

**Reading.** Libra Association, *Libra White Paper* (2019). [FATF, virtual asset guidance](https://www.fatf-gafi.org/en/topics/virtual-assets.html) (2019, updated 2021). NYAG, settlement with Bitfinex and Tether (Feb 2021).

---

## 2020: DeFi summer, new chains, and a proof-of-stake beacon

**Built.**

**Automated market makers.** Uniswap v2 (May) replaced the order book with a formula. A pool holds reserves *x* and *y* and trades along *x·y = k*, so price is the ratio of reserves and anyone can supply liquidity. In June, Compound began paying its COMP governance token to users, a practice called "liquidity mining." Capital poured into Compound, Aave, Curve and Uniswap. Uniswap's airdrop of 400 UNI to every past user in September became the template for token distribution. The failure mode arrived early. On "Black Thursday" (12 March), Ethereum congestion let keepers buy MakerDAO collateral for zero bids.

**New layer ones.**
- **Solana** (mainnet beta, March) runs a single global state machine. Proof of History acts as a verifiable clock that orders transactions before consensus. Sealevel executes transactions in parallel when their account lists do not overlap. Blocks come every ~400 ms.
- **Avalanche** (September) introduced Snow consensus. Each validator repeatedly asks small random samples of peers for their preference until the network converges, which gives finality in about a second without an all-to-all vote.
- **Binance Smart Chain** (September), an Ethereum fork with 21 validators, delivered cheap fees and made BNB a $100 billion asset.

**Ethereum's Beacon Chain** launched on 1 December. It was a proof-of-stake chain running alongside proof-of-work Ethereum, waiting for the 2022 merge.

**Decentralized storage.** Filecoin's mainnet launched in October. It runs a storage market in which providers post collateral, prove they hold a unique copy (proof of replication), and keep proving it over time (proof of spacetime). **Arweave** (mainnet 2018) sells permanence instead. A user pays once, and the fee goes into an endowment sized to fund 200 years of storage under conservative assumptions about falling storage costs. Its mining (SPoRA, from 2021) requires miners to read random old chunks from local disk, which pays them to keep the whole archive.

**Decided.**
- **OCC letters.** Between July 2020 and January 2021, the Office of the Comptroller of the Currency said national banks may custody crypto, hold stablecoin reserves, and use blockchains for payments. In November 2021 the OCC added a condition (Interpretive Letter 1179): banks needed their supervisor's written non-objection before doing any of it. That condition was lifted in March 2025.
- **Ripple.** In December the SEC sued Ripple over XRP sales.
- **Treasuries.** MicroStrategy bought $250 million of bitcoin in August and invented the corporate bitcoin treasury.
- **Halving.** The May halving cut the bitcoin block reward to 6.25 BTC.

<div class="pfp-fig"><div class="pfp-title">Uniswap v2: a price curve instead of an order book</div><div class="pfp-grid2"><div><svg class="pfp-svg" viewBox="0 0 400 250" role="img" aria-label="Constant product curve">
<path class="ln" stroke-width="1.2" d="M30 12 V215 H385"/>
<path stroke="#4794ff" stroke-width="3" fill="none" d="M30.0 20.0 L35.5 51.7 L41.0 74.3 L46.5 91.2 L52.0 104.4 L57.5 115.0 L63.0 123.6 L68.5 130.8 L74.0 136.9 L79.5 142.1 L85.0 146.7 L90.5 150.6 L96.0 154.1 L101.5 157.2 L107.0 160.0 L112.5 162.5 L118.0 164.8 L123.5 166.8 L129.0 168.7 L134.5 170.4 L140.0 172.0 L145.5 173.5 L151.0 174.8 L156.5 176.1 L162.0 177.2 L167.5 178.3 L173.0 179.4 L178.5 180.3 L184.0 181.2 L189.5 182.1 L195.0 182.9 L200.5 183.6 L206.0 184.3 L211.5 185.0 L217.0 185.6 L222.5 186.2 L228.0 186.8 L233.5 187.4 L239.0 187.9 L244.5 188.4 L250.0 188.9 L255.5 189.3 L261.0 189.8 L266.5 190.2 L272.0 190.6 L277.5 191.0 L283.0 191.4 L288.5 191.7 L294.0 192.1 L299.5 192.4 L305.0 192.7 L310.5 193.0 L316.0 193.3 L321.5 193.6 L327.0 193.9 L332.5 194.2 L338.0 194.4 L343.5 194.7 L349.0 194.9 L354.5 195.2 L360.0 195.4"/>
<path stroke="#f5a524" stroke-width="2" stroke-dasharray="4 4" fill="none" d="M57.5 115.0 V162.5 H112.5"/>
<circle cx="57.5" cy="115.0" r="6" fill="#23c58e"/><circle cx="112.5" cy="162.5" r="6" fill="#f5a524"/>
<text x="67.5" y="119.0" font-size="12">pool before</text>
<text x="122.5" y="152.5" font-size="12">after a big trade</text>
<text x="290" y="190" font-size="14" font-weight="700">x · y = k</text>
<text x="372" y="234" font-size="12" class="m">x</text><text x="14" y="22" font-size="12" class="m">y</text>
</svg></div><div style="display:flex;flex-direction:column;gap:.5rem;justify-content:center"><div class="pfp-node "><b>Price = y ÷ x</b><small>the ratio of the pool's two reserves</small></div><div class="pfp-node "><b>Buy X</b><small>the pool gains Y, loses X, and moves along the curve</small></div><div class="pfp-node pfp-a"><b>Bigger trade, more slippage</b><small>the curve bends harder the further you go</small></div></div></div><div class="pfp-sub">Two ways to pay for decentralized storage</div><div class="pfp-grid2"><div class="pfp-box pfp-g"><b>Arweave: pay once</b><span class="pfp-chip pfp-g">Upfront fee</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-g">Endowment</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-g">Miners paid as needed</span></div><div class="pfp-box pfp-b"><b>Filecoin: rent storage</b><span class="pfp-chip pfp-b">Deal + collateral</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Proof of replication</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b">Proof of spacetime, ongoing</span></div></div></div>

**Status.** AMMs remain the core of on-chain spot trading, and Uniswap (UNI, $5.5 billion) is still the reference design. Solana, BNB Chain and Avalanche all survive, with different results (see 2025–26). Arweave stores about 347 TiB and launched AO, a parallel compute layer, in February 2025. Filecoin launched Onchain Cloud, a paid hot-storage service, in January 2026. Its committed capacity is far larger than the storage users actually pay for.

**Reading.** [Adams et al., *Uniswap v2 Core* (2020)](https://uniswap.org/whitepaper.pdf). [Yakovenko, *Solana: A new architecture* (2017)](https://solana.com/solana-whitepaper.pdf). [Team Rocket, *Scalable and Probabilistic Leaderless BFT* (2019)](https://arxiv.org/abs/1906.08936). [Arweave, *Yellow Paper*](https://www.arweave.org/yellow-paper.pdf). [Filecoin Specification](https://spec.filecoin.io/).

---

## 2021: Mania, rollups, Taproot, and China leaves

**Built.**

**Ethereum fees and rollups.** In August, Ethereum's London upgrade shipped EIP-1559. A protocol-set base fee is burned, which ties ETH supply to usage. Congestion still pushed fees above $50, so scaling moved to **rollups**. A rollup executes transactions off-chain and posts the transaction data plus a state commitment to Ethereum.
- *Optimistic* rollups (Arbitrum One, August; Optimism) assume the posted state is correct and allow a challenge window of about seven days for fraud proofs.
- *ZK* rollups (zkSync, StarkNet, Scroll, Linea, from 2022 onward) post a validity proof, and Ethereum verifies it in milliseconds.

The rollup design made Ethereum's roadmap "rollup-centric," and the next four years of Ethereum upgrades served it.

**Bitcoin's Taproot** activated in November. It has three parts:
- Schnorr signatures allow key aggregation, so a multisig can look like a single signature.
- MAST commits to a tree of spending scripts and reveals only the branch actually used.
- Tapscript makes future opcodes easier to add.

Taproot also removed the old limit on script size. Two years later that enabled Ordinals.

**Other activity.**
- **NFTs.** Beeple sold an NFT for $69 million in March. Bored Apes and Axie Infinity followed, and Axie's Ronin sidechain later became the site of the largest hack of 2022.
- **Dogecoin.** Retail mania made it a top-10 asset.
- **Solana.** Solana ran from $1 to $260. On 14 September a flood of bot transactions stopped it for 17 hours, the first of several outages that shaped its later engineering.
- **Newcomers.** Bittensor launched its first network. Worldcoin announced itself.

**Decided.**
- **China.** Beijing banned mining in May–June and all crypto trading in September. Bitcoin's hashrate fell by half, then rebuilt in Texas, Kazakhstan and Russia. The United States became the largest mining country within a year.
- **El Salvador** made bitcoin legal tender in September. An IMF program reversed mandatory acceptance in 2025.
- **Wall Street.** Coinbase listed directly on Nasdaq in April. The first US bitcoin futures ETF (BITO) launched in October.
- **Tax reporting.** The Infrastructure Act in November defined crypto "brokers" for tax reporting; Congress repealed the DeFi part in 2025.
- **Stablecoin report.** The President's Working Group reported in November that stablecoin issuers should be insured banks. The GENIUS Act kept the federal-supervision core of that idea and added a regulated nonbank path.

Bitcoin peaked at $69,000 in November, with the whole market near $3 trillion.

<div class="pfp-fig"><div class="pfp-title">Rollups: execute elsewhere, settle on Ethereum</div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Users</b></div><span class="pfp-arr">→</span><div class="pfp-node pfp-b"><b>Sequencer</b><small>orders transactions</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Batch</b></div></div><div class="pfp-down">↓</div><div class="pfp-grid2"><div class="pfp-node "><b>Transaction data</b><small>calldata, later blobs</small></div><div class="pfp-node "><b>New state root</b><small>commitment to the result</small></div></div><div class="pfp-down">↓</div><div class="pfp-box pfp-g"><b>Ethereum L1: stores the data, holds the bridge, checks correctness</b><div class="pfp-grid2"><div class="pfp-node pfp-a"><b>Optimistic rollups</b><small>assume valid; anyone can submit a fraud proof within ~7 days</small></div><div class="pfp-node pfp-b"><b>ZK rollups</b><small>validity proof verified on arrival</small></div></div></div></div>

**Status.** Most Ethereum user activity now happens on rollups. Base (Coinbase), Arbitrum and Optimism lead. Most major rollups have reached "stage 1" decentralization, meaning working fraud or validity proofs with a security council able to override them. Taproot adoption is broad, and Taproot is the foundation for most current Bitcoin proposals.

**Reading.** [Vitalik Buterin, *An Incomplete Guide to Rollups* (2021)](https://vitalik.eth.limo/general/2021/01/05/rollup.html). [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559). [BIP 341, Taproot](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki). [President's Working Group, *Report on Stablecoins* (Nov 2021)](https://home.treasury.gov/system/files/136/StableCoinReport_Nov1_508.pdf). [L2BEAT](https://l2beat.com).

---

## 2022: Collapse, the Merge, and the privacy line

**Built.**

**The Merge** (15 September) moved Ethereum from proof of work to proof of stake without stopping the chain. How it works:
- **Validators.** Each validator stakes ETH (32 at minimum). Time runs in 12-second *slots* grouped into 32-slot *epochs*. Each slot, a randomly chosen proposer builds a block, and committees attest to it.
- **Fork choice.** LMD-GHOST picks the head of the chain.
- **Finality.** Casper FFG finalizes checkpoints after about two epochs (~13 minutes). Reverting a finalized block would require destroying at least a third of all stake through slashing.
- **Energy.** Energy use fell about 99.95%.

A market for block building grew around the protocol. With MEV-Boost, specialized builders assemble blocks and validators pick the highest bid. This "proposer-builder separation" still runs outside the protocol, through trusted relays; Glamsterdam would move it inside (see 2026).

**Zcash NU5** (31 May) introduced the **Orchard** pool, built on Halo 2. Halo 2 uses recursive proof composition over the Pallas/Vesta curve cycle and needs no trusted setup, which removed the assumption Sapling had carried. Unified addresses hid the pool choice from users.

**Proof of reserves** came out of the disasters below. The standard design is a *Merkle sum tree* over customer balances. The exchange publishes the root and proves on-chain control of assets at least equal to the total. Each customer can check that their balance is included. The limits are important. The method shows assets at one moment but cannot show all liabilities, since an exchange can leave accounts out. It also ignores off-chain debts, and the assets could be borrowed for the snapshot. Binance published zk-SNARK versions in 2023 that prove no balance is negative.

**Collapsed.**
- **Terra.** Its UST stablecoin held its peg by letting holders redeem $1 of UST for $1 of newly minted LUNA. The Anchor protocol paid 19.5% on UST deposits. When deposits ran in May, redemptions minted LUNA faster than buyers absorbed it, and about $40 billion was lost in a week.
- **Contagion.** It spread to lenders and funds: Three Arrows Capital, Celsius, Voyager and BlockFi.
- **FTX** failed in November after customer deposits were found at its affiliate Alameda, leaving an $8 billion hole.
- **Bridge hacks.** North Korea's Lazarus Group took $625 million from Axie's Ronin bridge. Wormhole lost $325 million and Nomad $190 million.

**Decided.**
- **Tornado Cash.** On 8 August, OFAC sanctioned Tornado Cash, an immutable Ethereum mixer. It was the first time the US sanctioned software rather than a person. A Dutch court later convicted developer Alexey Pertsev. In November 2024 the Fifth Circuit held that immutable smart contracts are not "property" that OFAC can block, and Treasury delisted Tornado in March 2025.
- **Executive order.** In March, Executive Order 14067 ordered a whole-of-government study, including a central bank digital currency (CBDC).
- **MiCA.** The EU reached political agreement on MiCA in June.

<div class="pfp-fig"><div class="pfp-title">Ethereum proof of stake after the Merge</div><div class="pfp-scroll"><svg class="pfp-svg" viewBox="0 0 680 110" role="img" aria-label="Slots and epochs">
<text x="10" y="20" font-size="12.5" font-weight="700">Epoch N</text><text x="342" y="20" font-size="12.5" font-weight="700">Epoch N+1</text>
<rect x="10" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.95"/><rect x="20" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="30" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="40" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="50" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="60" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="70" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="80" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="90" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.95"/><rect x="100" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="110" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="120" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="130" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="140" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="150" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="160" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="170" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.95"/><rect x="180" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="190" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="200" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="210" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="220" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="230" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="240" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="250" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.95"/><rect x="260" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="270" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="280" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="290" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="300" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="310" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="320" y="30" width="8" height="26" rx="2" fill="#4794ff" opacity="0.55"/><rect x="342" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.95"/><rect x="352" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="362" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="372" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="382" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="392" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="402" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="412" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="422" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.95"/><rect x="432" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="442" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="452" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="462" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="472" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="482" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="492" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="502" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.95"/><rect x="512" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="522" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="532" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="542" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="552" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="562" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="572" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="582" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.95"/><rect x="592" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="602" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="612" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="622" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="632" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="642" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/><rect x="652" y="30" width="8" height="26" rx="2" fill="#23c58e" opacity="0.55"/>
<path class="ln" stroke-width="1.5" d="M10 68 V76 H668 V68"/>
<text x="10" y="98" font-size="12" class="m">1 slot = 12 s · 1 epoch = 32 slots = 6.4 min</text>
<text x="668" y="98" font-size="12" text-anchor="end">finality ≈ 2 epochs (~13 min)</text>
</svg></div><div class="pfp-sub">Two clients, one node</div><div class="pfp-row pfp-flow"><div class="pfp-node pfp-b"><b>Execution client</b><small>EVM, transactions, state</small></div><span class="pfp-api">⇄ Engine API ⇄</span><div class="pfp-node pfp-g"><b>Consensus client</b><small>validators, attestations, fork choice</small></div></div><div class="pfp-sub">Block building today (MEV-Boost, outside the protocol)</div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Builders</b><small>assemble blocks and bid</small></div><span class="pfp-arr">→</span><div class="pfp-node pfp-a"><b>Relay</b><small>trusted middleman</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Proposer</b><small>picks the highest bid</small></div></div><div class="pfp-cap">Reverting a finalized block would require destroying at least a third of all stake.</div></div>

<div class="pfp-fig"><div class="pfp-title">Proof of reserves: a Merkle sum tree</div><div class="pfp-scroll"><svg class="pfp-svg" viewBox="0 0 640 230" role="img" aria-label="Merkle sum tree">
<path class="ln" stroke-width="1.5" d="M320 54 L170 108 M320 54 L470 108 M170 138 L90 188 M170 138 L250 188 M470 138 L390 188 M470 138 L550 188"/>
<path stroke="#23c58e" stroke-width="3" fill="none" d="M320 54 L170 108 M170 138 L90 188"/>
<rect x="205" y="12" width="230" height="42" rx="9" fill="rgba(71,148,255,.16)" stroke="#4794ff"/>
<text x="320" y="30" font-size="12.5" text-anchor="middle" font-weight="700">root · sum 1,000 BTC</text>
<text x="320" y="46" font-size="11" text-anchor="middle" class="m">published; on-chain assets ≥ 1,000?</text>
<rect x="115" y="108" width="110" height="30" rx="8" class="bx"/><text x="170" y="128" font-size="12.5" text-anchor="middle">sum 600</text>
<rect x="415" y="108" width="110" height="30" rx="8" class="bx"/><text x="470" y="128" font-size="12.5" text-anchor="middle">sum 400</text>
<rect x="45" y="188" width="90" height="30" rx="8" fill="rgba(35,197,142,.18)" stroke="#23c58e"/><text x="90" y="208" font-size="12.5" text-anchor="middle" font-weight="700">you · 50</text>
<rect x="205" y="188" width="90" height="30" rx="8" class="bx"/><text x="250" y="208" font-size="12.5" text-anchor="middle">u2 · 550</text>
<rect x="345" y="188" width="90" height="30" rx="8" class="bx"/><text x="390" y="208" font-size="12.5" text-anchor="middle">u3 · 100</text>
<rect x="505" y="188" width="90" height="30" rx="8" class="bx"/><text x="550" y="208" font-size="12.5" text-anchor="middle">u4 · 300</text>
</svg></div><div class="pfp-cap">You check the green path from your balance to the published root. The proof cannot show liabilities left out of the tree, or assets borrowed for the snapshot.</div></div>

**Status.** Close to 30% of all ETH is staked. Liquid-staking tokens (Lido's stETH, Coinbase's cbETH) are standard collateral. Terra's failure is written into the GENIUS Act's ban on algorithmic stablecoins. Proof of reserves is now routine at large exchanges, and in 2026 Tether moved beyond it to a full audit.

**Reading.** [ethereum.org, *The Merge*](https://ethereum.org/en/roadmap/merge/). [Buterin, *Having a Safe CEX: Proof of Solvency* (2022)](https://vitalik.eth.limo/general/2022/11/19/proof_of_solvency.html). [*The halo2 Book*](https://zcash.github.io/halo2/). [US Treasury, Tornado Cash designation (2022)](https://home.treasury.gov/news/press-releases/jy0916). *Van Loon v. Treasury* (5th Cir. 2024).

---

## 2023: Rebuilding: restaking, inscriptions, identity, and the courts

**Built.**

**Shapella** (April) enabled staking withdrawals, which made staked ETH liquid. **ERC-4337** (March) brought "account abstraction," meaning smart-contract wallets with recovery, batching and sponsored gas. Coinbase launched **Base** (August), a rollup that became the largest by user activity. Sui, a high-throughput chain built on the Move language, launched in May.

**Restaking (EigenLayer, mainnet June).** A validator's staked ETH already carries slashing risk for Ethereum. Restaking lets the same stake also secure other services, called *actively validated services* (AVSs). Examples are data-availability layers, oracles, bridges and coprocessors. Operators run each AVS's software, and each AVS defines conditions under which a misbehaving operator's stake is slashed. The pitch is shared security: a new service rents Ethereum's economic security instead of bootstrapping its own. The risk is leverage. The same ETH backs several promises, and liquid restaking tokens stacked further yield on top.

**Ordinals** (January) numbered individual satoshis and stored arbitrary data ("inscriptions") in Taproot witnesses. That turned Bitcoin blocks into an NFT and token (BRC-20, later Runes) market, and miners earned record fees. It also started a culture war over what block space is for, which reached Bitcoin Core's own policy in 2025.

**World** (then Worldcoin, launched July) targeted "proof of personhood": showing that an account belongs to one unique human without revealing who. An "Orb" camera scans the iris and computes an iris code. The code is split into secret shares held by several parties, which check uniqueness together without any one party seeing it. The user then holds a World ID and can prove "I am a verified, unique human" to an app with a zero-knowledge proof. The proof uses an app-specific nullifier, so the same person cannot be linked across apps. Regulators in Kenya, Spain, Portugal, Hong Kong and elsewhere suspended scanning.

**The XRP Ledger**, whose token the Ripple case (below) concerned, dates to 2012 and uses neither mining nor staking. Each validator trusts a published list of validators, its Unique Node List, and a ledger closes every few seconds once about 80% of that list agrees. Default lists are published by the XRPL Foundation and Ripple, so security rests on the independence of the validators on them.

**Decided.**
- **Banks.** Silvergate, Silicon Valley Bank and Signature failed in March. Circle had $3.3 billion at SVB, and USDC fell to $0.87 until the FDIC backstopped depositors. The industry called the loss of banking access "Operation Choke Point 2.0."
- **Ripple.** On 13 July, Judge Torres ruled in *SEC v. Ripple* that Ripple's direct sales of XRP to institutions were investment contracts, while its programmatic sales on exchanges, where buyers could not know they were buying from Ripple, were not. The ruling was limited to those facts, and weeks later another judge in the same court rejected its reasoning in the Terraform case. It still became the industry's main legal argument that a traded token is not itself a security.
- **Grayscale.** In August the D.C. Circuit held that the SEC's refusal to convert Grayscale's bitcoin trust into an ETF was "arbitrary and capricious," which opened the ETF door.
- **Exchanges.** The SEC sued Binance and Coinbase in June. In November, Binance pleaded guilty to US money-laundering and sanctions charges and paid $4.3 billion, and CZ stepped down. Sam Bankman-Fried was convicted.
- **Tornado Cash.** Its developers were indicted in August.
- **MiCA** became EU law in June.

<div class="pfp-fig"><div class="pfp-title">Restaking: one stake, several promises</div><div class="pfp-node pfp-b"><b>ETH stake</b><small>native, or a liquid staking token</small></div><div class="pfp-down">↓</div><div class="pfp-node pfp-p"><b>EigenLayer contracts</b><small>allocate a slice of stake to each service</small></div><div class="pfp-down">↓</div><div class="pfp-node "><b>Operators</b><small>run each service's software</small></div><div class="pfp-down">↓</div><div class="pfp-grid4"><div class="pfp-node pfp-a"><b>EigenDA</b><small>own slashing rule</small></div><div class="pfp-node pfp-a"><b>Oracle</b><small>own slashing rule</small></div><div class="pfp-node pfp-a"><b>Bridge</b><small>own slashing rule</small></div><div class="pfp-node pfp-a"><b>AI coprocessor</b><small>own slashing rule</small></div></div></div>

<div class="pfp-fig"><div class="pfp-title">World ID: prove “unique human,” reveal nothing else</div><div class="pfp-sub" style="margin-top:0">Enrollment</div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Orb</b><small>iris scan</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Iris code</b></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Secret shares</b><small>split across parties</small></div><span class="pfp-arr">→</span><div class="pfp-node pfp-g"><b>Unique?</b><small>checked jointly; no party sees the code</small></div></div><div class="pfp-sub">Use</div><div class="pfp-row pfp-flow"><div class="pfp-node pfp-b"><b>Phone holds World ID</b></div><span class="pfp-arr">→</span><div class="pfp-node "><b>ZK proof + per-app nullifier</b></div><span class="pfp-arr">→</span><div class="pfp-node "><b>App</b><small>learns only: verified, unique, first time here</small></div></div></div>

**Status.**
- **Restaking.** EigenLayer added slashing in April 2025 and "redistributable" slashing in July 2025, and rebranded as EigenCloud around verifiable compute and AI. Restaked value peaked around $15–20 billion and sits near $5 billion. Competitor Symbiotic holds roughly $1–1.5 billion. No major slashing event has occurred, so the model's central promise remains largely untested.
- **World** reports nearly 18 million Orb-verified people in about 160 countries. It launched in the US in May 2025, added passport-based credentials and a smaller Orb, and integrated with Tinder, Zoom, Docusign and Razer.

**Reading.** EigenLayer, *EigenLayer: The Restaking Collective* (2023). [World whitepaper](https://whitepaper.world.org/). *SEC v. Ripple Labs*, Opinion and Order (S.D.N.Y. 2023). *Grayscale v. SEC* (D.C. Cir. 2023). [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337).

---

## 2024: Wall Street arrives, and blobs make rollups cheap

**Built.**

**Dencun** (13 March, EIP-4844) gave Ethereum a second data lane, "blobs." Blobs are large data packets that rollups post, which validators keep for about 18 days and then delete. Rollups only need the data long enough for anyone to reconstruct state or raise a challenge. Blobs are priced in their own fee market, and rollup fees fell by about 90% overnight.

**Bitcoin.**
- **Halving.** The April halving cut the block reward to 3.125 BTC.
- **Babylon** (August) let BTC holders stake to secure proof-of-stake chains without bridging. Coins sit in a self-custodied timelock script. A validator that double-signs leaks a key through "extractable one-time signatures," which lets anyone slash the locked BTC.
- **BitVM.** The BitVM line of research (from late 2023) showed how to verify arbitrary computation on Bitcoin optimistically, through a challenge game. BitVM2 bridges went live on Citrea in January 2026.

**New dollar designs.**
- **Ethena** (February) launched **USDe**, a synthetic dollar built from staked ETH plus an equal short perpetual futures position. Its yield comes from funding rates.
- **Tokenized Treasuries.** BlackRock's **BUIDL** (March) made tokenized Treasury funds institutional.
- **Stripe** agreed to buy stablecoin infrastructure company Bridge for $1.1 billion in October.

**Solana and Hyperliquid.**
- **Pump.fun** (January) let anyone launch a token on a bonding curve in seconds. The resulting memecoin boom pushed Solana's DEX volume past Ethereum's for long stretches.
- **Hyperliquid**, a perpetual futures exchange on its own chain, airdropped about 31% of its HYPE supply to users in November, with no venture allocation. HYPE is now worth $21.5 billion.

**Avalanche9000** (December) turned Avalanche's "subnets" into sovereign L1s. They pay a continuous fee (about 1.33 AVAX a month per validator) instead of posting 2,000 AVAX of stake, which cut launch cost by roughly 99%. Cardano's Chang hard fork (September) moved it to on-chain governance.

**Decided.**
- **ETFs.** The SEC approved **spot bitcoin ETFs** on 10 January. BlackRock's IBIT became the fastest-growing ETF on record, and US spot ETFs held more than a million BTC within the year. Spot **ether ETFs** began trading on 23 July.
- **Politics.** The **Fairshake** super PAC and its affiliates spent about $130 million in the 2024 cycle, and crypto became an organized voting bloc. Donald Trump promised in July to make America "the crypto capital of the planet," and won in November. Bitcoin crossed $100,000 on 5 December.
- **MiCA.** Stablecoin rules took effect in June, and the full regime in December. Tether chose to stay unauthorized, and EU exchanges delisted USDT for European users in early 2025.
- **Privacy prosecutions.** The Samourai Wallet founders were arrested in April and later sentenced to prison. The Fifth Circuit ruled for Tornado Cash users in November.

<div class="pfp-fig"><div class="pfp-title">EIP-4844: blobs, a cheap and temporary data lane</div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Rollup batch</b></div><span class="pfp-arr">→</span><div class="pfp-node pfp-b"><b>Blob</b><small>~128 KB, priced in its own fee market</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Beacon block</b></div></div><div class="pfp-down">↓</div><div class="pfp-grid2"><div class="pfp-node pfp-g"><b>KZG commitment</b><small>kept forever</small></div><div class="pfp-node pfp-a"><b>Blob data</b><small>pruned after ~18 days</small></div></div><div class="pfp-sub">Capacity</div><div class="pfp-tl"><div class="pfp-tli"><span class="pfp-yr">2024</span><span>Dencun: 3 target / 6 max blobs per block</span></div><div class="pfp-tli pfp-hot"><span class="pfp-yr">2025</span><span>Fusaka: PeerDAS, where nodes sample slices instead of downloading every blob; limits keep rising</span></div></div></div>

**Status.**
- **ETFs** hold a large share of all bitcoin and are now a core channel for institutional ownership. Staking inside US ETFs arrived in late 2025.
- **USDe** grew to about $14 billion, then shrank to $4.9 billion after the October 2025 crash (see below).
- **Avalanche's** L1 model has drawn institutional deployments: fund tokenization on Spruce with T. Rowe Price and WisdomTree, and Japan's Progmat moving about $2 billion of assets from Corda. AVAX itself trades at $4.8 billion, far below its peak.

**Reading.** [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844). Babylon, *Bitcoin Staking* litepaper. [Robin Linus, *BitVM* (2023)](https://bitvm.org). Ethena documentation. SEC, spot bitcoin ETP approval order (Jan 2024).

---

## 2025 (I): Washington changes sides

**Decided.** Within about six months, US policy moved from enforcement toward open sponsorship.

- **Presidential.** Days before the inauguration, the Trump family launched the $TRUMP memecoin. Its World Liberty Financial venture later issued **USD1**, a stablecoin used in a $2 billion investment by Abu Dhabi's MGX into Binance. The family's crypto income became the main political obstacle to market-structure law. Executive Order 14178 (23 January) created a crypto working group and prohibited federal work on a CBDC. The **Strategic Bitcoin Reserve** order (6 March) moved forfeited bitcoin into a permanent reserve and allowed only budget-neutral additions.
- **SEC.**
  - The SEC rescinded SAB 121, the accounting rule that had kept banks out of custody. It set up a Crypto Task Force under Commissioner Peirce.
  - It dismissed the Coinbase, Kraken, Consensys and Binance cases. The Ripple appeals ended in August, leaving the 2023 ruling in place.
  - Staff statements declared that memecoins, proof-of-work mining, protocol staking and fully reserved "covered stablecoins" fall outside securities law.
  - "Generic listing standards" in September let exchanges list ETFs on other large assets without separate approval, and Solana and XRP ETFs followed.
- **Banks.** Regulators withdrew their anti-crypto guidance and removed "reputation risk" from exams. In December, several crypto firms, Circle and Ripple among them, received conditional OCC national trust charters.
- **Justice.** A Deputy Attorney General memo ended "regulation by prosecution." A presidential pardon freed CZ in October. Roman Storm of Tornado Cash was convicted in August of conspiracy to run an unlicensed money transmitter. The jury hung on the laundering and sanctions counts, and DOJ is pursuing a retrial on those.
- **Circle** went public in June.
- **Bitcoin treasury companies.** "Digital asset treasury" companies copied MicroStrategy (now Strategy), which by late 2025 held more than 3% of all bitcoin. The boom ended with the October crash, and many of these companies now trade below the value of their holdings.
- **Security.** In February, Lazarus stole $1.5 billion from Bybit by compromising the Safe multisig web interface its signers used. It was the largest theft in the industry's history.

**The GENIUS Act** (signed 18 July 2025) is the first US federal statute for a crypto asset class. It regulates "payment stablecoins," tokens redeemable at a fixed dollar value:
- **Reserves.** Backing must be one-to-one in cash, bank deposits, Treasury bills of 93 days or less, overnight repos and government money funds. Reserves cannot be rehypothecated except for narrow liquidity needs.
- **Disclosure.** Issuers publish reserves monthly, examined by a registered accounting firm and certified by the CEO and CFO. Issuers above $50 billion need annual audited financial statements.
- **Licensing.** Issuers can be bank subsidiaries, OCC-licensed nonbanks, or state-qualified issuers under $10 billion.
- **Foreign issuers.** They need a comparable home regime and the technical ability to freeze tokens on lawful order. Tether answered with **USAT**, a US-regulated token issued through Anchorage.
- **Algorithmic stablecoins** of the Terra type are barred as payment stablecoins.
- **Holder protection.** Holders get priority in an issuer's insolvency.
- **Compliance.** Issuers are financial institutions under the Bank Secrecy Act.
- **Interest.** Issuers cannot pay interest to holders. Whether exchanges and affiliates may pay "rewards" became the fight that stalled the next bill.
- **Securities status.** Payment stablecoins are neither securities nor commodities.

<div class="pfp-fig"><div class="pfp-title">GENIUS Act: who may issue a US payment stablecoin</div><div class="pfp-grid3"><div class="pfp-node pfp-b"><b>Bank subsidiary</b><small>an insured bank's stablecoin arm</small></div><div class="pfp-node pfp-b"><b>OCC-licensed nonbank</b><small>federal charter</small></div><div class="pfp-node pfp-b"><b>State-qualified issuer</b><small>under $10B outstanding</small></div></div><div class="pfp-down">↓</div><div class="pfp-grid2"><div class="pfp-node pfp-g"><b>Reserves 1:1</b><small>cash · deposits · T-bills ≤93 days · repo · government money funds</small></div><div class="pfp-node pfp-g"><b>Monthly reserve report</b><small>accountant-examined, CEO/CFO certified</small></div><div class="pfp-node "><b>Over $50B outstanding</b><small>annual audited financial statements</small></div><div class="pfp-node "><b>BSA/AML + freeze capability</b><small>issuers are financial institutions</small></div><div class="pfp-node pfp-a"><b>No interest to holders</b><small>rewards paid by exchanges: the CLARITY fight</small></div><div class="pfp-node "><b>Holders first in insolvency</b><small>priority claim on reserves</small></div><div class="pfp-node pfp-r"><b>Algorithmic stablecoins</b><small>barred as payment stablecoins</small></div><div class="pfp-node pfp-a"><b>Foreign issuers</b><small>comparable regime + Treasury finding</small></div></div><div class="pfp-cap">Effective by 18 January 2027 at the latest; final rules are still pending.</div></div>

**Status.** Rulemaking is late. [The 18 July 2026 deadline for final rules passed](https://crypto.news/the-genius-act-turned-one-by-missing-its-own-deadline/) with ten proposals and no final rules, four of the proposals from Treasury and two from the OCC. The OCC says it will finalize in November 2026. Treasury had yet to issue, as of August, the foreign-regime finding that USDT itself needs to keep serving US businesses. The act takes effect on the earlier of 18 January 2027 or 120 days after final rules. The stablecoin market is about $285–315 billion. USDT has roughly 60–65% of it, but USDC moved more on-chain volume in 2025.

**Reading.** [GENIUS Act, S. 1582](https://www.congress.gov/bill/119th-congress/senate-bill/1582). Executive Order 14178 (Jan 2025). SEC staff statements on memecoins, mining, staking and stablecoins (2025). DOJ, *Ending Regulation by Prosecution* (Apr 2025).

---

## 2025 (II): Exchanges move on-chain, then break on 10 October

**Built.**

**Hyperliquid** is the clearest proof that a fully on-chain order book can compete with centralized exchanges.
- **Architecture.** Its L1 runs HyperBFT consensus. HyperCore is the exchange engine, where every order, cancel, fill and liquidation is a state transition. HyperEVM (February 2025) is a smart-contract environment with direct access to HyperCore's books. Exchange fees fund continuous HYPE buybacks.
- **Criticism.** In March 2025, during the JELLY incident, the validator set delisted a manipulated market and settled it at a chosen price. That exposed how much discretion a small validator set holds.
- **HIP-3** (13 October 2025) lets anyone who stakes 500,000 HYPE deploy their own perpetual market. Trade.xyz used it to list stock and index perps: single US stocks, the XYZ100 index and, under a license signed in March 2026, the S&P 500. It holds more than 90% of HIP-3 open interest.
- **HIP-4** (May 2026) added outcome contracts.
- **Scale.** Hyperliquid runs roughly $170–245 billion of perp volume a month with about $9 billion of open interest.

**Lighter** made the opposite design choice.
- **Design.** It is an Ethereum ZK rollup specialized for trading. Order matching and liquidations run inside circuits, so every fill carries a validity proof. Retail trading carries zero fees.
- **Launches.** Mainnet came in October 2025 and the LIT token at year end. US stock perps followed in January 2026 and Korean stock perps in February.
- **Robinhood.** Since 1 July 2026 [a dedicated Lighter instance on Robinhood Chain](https://www.theblock.co/news/business/2026-07-01-robinhood-chain-goes-live-mainnet-alongside-24-7-tokenized-stocks-lighter-perps-planned-crypto-agentic-trading-406918) has been the perps venue inside Robinhood Wallet, for users outside the US and other restricted jurisdictions.

**Tokenized stocks** took three forms:
1. **Wrapped shares.** Backed's xStocks on Solana (June 2025; Backed was acquired by Kraken in December) and Ondo Global Markets (September 2025) say they hold real shares at a broker and issue one token per share.
2. **Brokerage tokens.** Robinhood issues stock tokens to EU customers on Arbitrum.
3. **Synthetic perps.** Venues such as trade.xyz and Lighter offer perpetual futures on stocks.

Tokenized stocks grew from tens of millions of dollars in early 2025 to [about $3.1 billion in early September 2026, by Token Terminal's count](https://cryptobriefing.com/tokenized-stocks-hit-3b-market-cap-etfs-644m/). Ondo leads with about 31%, ahead of xStocks and Binance's bStocks.

**The crash.** On 10 October 2025, President Trump announced 100% tariffs on China. Crypto markets liquidated about $19 billion of leveraged positions in a day, a record.
- **Hyperliquid.** Open interest fell from $14 billion to $6 billion. Its auto-deleveraging engine closed profitable positions to cover bankrupt ones, which broke the hedges of traders who thought they were market-neutral.
- **USDe.** On Binance, USDe printed $0.65 because Binance priced it from its own thin order book rather than from redemption value. Liquidations cascaded from that price.

The lessons: oracle design matters more than matching speed, auto-deleveraging is a real risk for hedged books, and synthetic dollars carry funding risk that fiat-backed ones avoid.

SOL fell from $228 to about $104 by February 2026.

<div class="pfp-fig"><div class="pfp-title">Two ways to put an exchange on-chain</div><div class="pfp-grid2"><div class="pfp-box pfp-g"><b>Hyperliquid · its own L1</b><div class="pfp-node "><b>HyperBFT validators</b></div><div class="pfp-down">↓</div><div class="pfp-node "><b>HyperCore</b><small>order books, margin, liquidations as state</small></div><div class="pfp-down">↓</div><div class="pfp-node "><b>HyperEVM</b><small>contracts read the books</small></div><div class="pfp-down">↓</div><div class="pfp-node "><b>HIP-3</b><small>staked builders list stocks, indexes, anything</small></div><div class="pfp-note" style="margin-top:.55rem">Trust: the validator set</div></div><div class="pfp-box pfp-b"><b>Lighter · Ethereum ZK rollup</b><div class="pfp-node "><b>Sequencer</b><small>matches orders</small></div><div class="pfp-down">↓</div><div class="pfp-node "><b>Circuit</b><small>proves matching, liquidations, balances</small></div><div class="pfp-down">↓</div><div class="pfp-node "><b>Proof verified on Ethereum</b></div><div class="pfp-down">↓</div><div class="pfp-node "><b>Exit hatch</b><small>withdraw via L1 if the operator stalls</small></div><div class="pfp-note" style="margin-top:.55rem">Trust: circuits, contracts, upgrade keys, Ethereum</div></div></div><div class="pfp-sub">Three routes to a tokenized stock</div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Real share at a broker</b></div><span class="pfp-arr">→</span><div class="pfp-node pfp-g"><b>1:1 token</b><small>Ondo, xStocks · spot, custodial</small></div></div><div style="height:.4rem"></div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>Broker's own ledger</b></div><span class="pfp-arr">→</span><div class="pfp-node pfp-b"><b>Stock token</b><small>Robinhood EU · spot, platform</small></div></div><div style="height:.4rem"></div><div class="pfp-row pfp-flow"><div class="pfp-node "><b>No share at all</b></div><span class="pfp-arr">→</span><div class="pfp-node pfp-a"><b>Perp on the price</b><small>trade.xyz, Lighter · derivative</small></div></div></div>

**Status.** HIP-3 open interest peaked around $3.2 billion in June 2026 and sat near $1.9 billion in late September. Perp DEXs now take a meaningful share of global crypto derivatives. Stock perps trade on weekends while the underlying is closed; that gap is both the product and the risk.

**Reading.** [Hyperliquid documentation](https://hyperliquid.gitbook.io/hyperliquid-docs) (HyperCore, HIP-3). [Lighter documentation](https://docs.lighter.xyz). Ondo Global Markets disclosures. [Token Terminal](https://tokenterminal.com), tokenized-asset dashboards.

---

## 2025 (III): Real-time proofs, AI markets, and faster clients

**Built.**

**ZK proving became cheap and fast.** In May 2025, Succinct's SP1 Hypercube proved Ethereum blocks in under 12 seconds, the block time, on about 200 consumer GPUs. Months later, 16 RTX 5090s did it for 99.7% of blocks. Pico Prism averaged 6.9 seconds on 64 GPUs, ZKsync's Airbender proves on a single GPU, and ZisK claims 9.6 seconds at p99 on four. Ethproofs, which tracks cost, shows proving an Ethereum block falling from $1.69 in January 2025 to under half a cent in September 2026. Five things drove it:

1. **Small fields.** Older SNARKs did arithmetic over 254-bit elliptic-curve fields. Modern STARK-family systems work over 31- or 64-bit fields (BabyBear, Mersenne-31, Goldilocks) that fit in machine words. That is roughly an order-of-magnitude gain per operation.
2. **Better proof systems.** Sumcheck and multilinear techniques (as in Jolt and Binius) and lookup arguments replace expensive constraint work with table lookups and linear-time proving.
3. **zkVMs on RISC-V.** Developers write ordinary Rust, compile it to RISC-V, and prove the execution trace. Hand-written precompiles handle the hot paths (Keccak, secp256k1). Competition is now an engineering race over one shared target.
4. **GPUs.** The core kernels (hashing, number-theoretic transforms, multi-scalar multiplication) are massively parallel.
5. **Recursion.** Traces are split into shards, proved in parallel, then folded into one proof. This descends from the recursion Halo 2 made practical for Zcash.

The same forces cut client-side proving for private payments from minutes to seconds on a phone. In December 2025, the Ethereum Foundation shifted its emphasis from speed to *security*: a 128-bit provable-security target and caution about unproven "proximity gap" conjectures. EIP-8025 lets clients accept optional execution proofs, the first step toward validators checking a proof instead of re-running every block.

**Bittensor** is a market for machine-learning work. Its structure:
- **Subnets.** The chain hosts 128 subnets. Each defines a task, such as inference, pretraining, protein folding or data scraping, and a scoring rule.
- **Scoring.** Miners do the work. Validators score them and submit weight vectors. Yuma Consensus clips outlier validators and turns the weights into emissions.
- **Split.** Emissions go 41% to miners, 41% to validators and 18% to the subnet owner.
- **dTAO** (February 2025) gave each subnet its own "alpha" token with a TAO liquidity pool. Emissions now follow where stakers put capital, instead of a small committee's votes.

TAO has a 21 million cap and bitcoin-style halvings. The first, in December 2025, cut issuance from 7,200 to 3,600 TAO a day.

**Base layers.**
- **Ethereum's Pectra** (May 2025) shipped EIP-7702, which lets ordinary accounts act as smart wallets. It also raised the maximum validator balance to 2,048 ETH so large stakers can consolidate. **Fusaka** (December 2025) shipped PeerDAS, where nodes sample slices of blob data instead of downloading all of it, and raised the gas limit to 60 million.
- **Solana.** Firedancer, Jump's independent validator client written from scratch in C, reached mainnet in December 2025. Solana validators voted in September 2025 to adopt **Alpenglow**, which replaces Proof of History and TowerBFT with a new voting protocol (Votor) and targets finality around 150 ms instead of about 12.8 seconds.
- **NEAR** halved its inflation to 2.5%.

<div class="pfp-fig"><div class="pfp-title">Cost to prove one Ethereum block (Ethproofs, log scale)</div><div class="pfp-bar"><span>Jan 2025</span><div class="pfp-track"><div class="pfp-fill" style="width:97%"></div></div><span class="pfp-val">$1.69</span></div><div class="pfp-bar"><span>Dec 2025</span><div class="pfp-track"><div class="pfp-fill" style="width:39%"></div></div><span class="pfp-val">$0.04</span></div><div class="pfp-bar"><span>Sep 2026</span><div class="pfp-track"><div class="pfp-fill" style="width:7%"></div></div><span class="pfp-val"><$0.005</span></div><div class="pfp-sub">Why it fell</div><span class="pfp-chip pfp-b">Small 31/64-bit fields</span><span class="pfp-chip pfp-b">Sumcheck + lookups</span><span class="pfp-chip pfp-b">RISC-V zkVMs</span><span class="pfp-chip pfp-b">GPUs</span><span class="pfp-chip pfp-b">Recursion</span><div class="pfp-cap">Roughly a 99.7% fall in 20 months; real-time proving (under 12 s) arrived in May 2025.</div></div>

<div class="pfp-fig"><div class="pfp-title">Bittensor's subnet loop</div><div class="pfp-row pfp-flow"><div class="pfp-node pfp-p"><b>Subnet task</b><small>inference, training, data</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Miners</b><small>do the work</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Validators</b><small>score miners</small></div><span class="pfp-arr">→</span><div class="pfp-node "><b>Yuma Consensus</b><small>clips outliers, sets weights</small></div><span class="pfp-arr">→</span><div class="pfp-node pfp-g"><b>Emissions</b><small>41% miners · 41% validators · 18% owner</small></div></div><div class="pfp-note" style="margin-top:.55rem">↺ Stakers route TAO into each subnet's alpha pool, which sets how much that subnet earns next.</div></div>

**Status.**
- **Bittensor.** Subnet revenue from outside customers reached about $43 million in Q1 2026. That is real revenue, though small against a $3.5 billion token. In April 2026 [Covenant AI left](https://www.falconx.io/newsroom/state-of-bittensor-subnet-adoption-trends-network-mechanics-and-covenants-departure). It ran three top subnets, including Templar, which had just trained a 72-billion-parameter model across the open internet. It called the governance "decentralization theatre" and sold about 37,000 TAO on the way out. Bittensor answered in May with "Conviction," which locks subnet owners' emissions.
- **Firedancer** runs about 14% of Solana stake, plus about 26% on "Frankendancer," a hybrid.
- **Alpenglow** reached public testnet in September 2026, with mainnet still ahead.

**Reading.** [Ethproofs](https://ethproofs.org). [Justin Thaler, *Proofs, Arguments, and Zero-Knowledge*](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html). Succinct, *SP1 Hypercube* (2025). [Bittensor documentation](https://docs.learnbittensor.org) (Yuma Consensus, dTAO). [Solana SIMDs](https://github.com/solana-foundation/solana-improvement-documents) (SIMD-0326, Alpenglow). [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702).

---

## 2026 (I): Plumbing: agencies act, Congress stalls, stocks tokenize

**Decided.** The **CLARITY Act** (H.R. 3633) is the market-structure bill meant to finish what GENIUS started:
- It splits jurisdiction: the CFTC gets spot "digital commodities," and the SEC keeps fundraising and securities.
- It gives tokens a path to "mature blockchain" status.
- It protects DeFi developers and non-custodial software (§604).
- It addresses stablecoin yield (§404).

It passed the House 294–134 in July 2025. On 15 September 2026, [a Senate cloture vote](https://www.coindesk.com/policy/2026/09/15/crypto-clarity-act-flames-out-in-failed-u-s-senate-vote) on the motion to proceed failed 49–50, eleven short of the 60 required. No Democrat voted yes, and four Republicans voted no. The main dispute was ethics language on officials' crypto holdings; developer liability and stablecoin rewards were the other two. The lead sponsor called the bill over for 2026.

The agencies moved without it:
- **Joint framework.** SEC Chair Atkins and CFTC Chair Selig made "Project Crypto" a joint program in January. The agencies signed a memorandum of understanding in March. On 17 March they issued a [**joint interpretation**](https://www.paulweiss.com/insights/client-memos/sec-and-cftc-release-interpretation-on-application-of-federal-securities-laws-to-crypto-assets), binding on both agencies, that sorts crypto assets into five categories: digital commodities, digital collectibles, digital tools, stablecoins and digital securities. It names ether as a digital commodity. It also treats protocol mining, protocol staking, wrapping and airdrops of non-security tokens as outside securities law.
- **Tokenized stocks.**
  - The SEC [approved Nasdaq's trading of **tokenized securities**](https://www.coindesk.com/policy/2026/03/18/sec-approves-nasdaq-s-move-to-allow-tokenized-securities-trading) (18 March). Tokenized Russell 1000 stocks and index ETFs trade on the same order book as ordinary shares, and DTC settles them.
  - It proposed rules for transfer agents that keep ownership records on blockchains (1 September).
  - On 17 September, two days after the Senate vote, it issued the five-year [**Innovation Exemption**](https://www.sec.gov/newsroom/press-releases/2026-90-sec-issues-innovation-exemption-facilitate-trading-tokenized-nms-stock-request-comment). The exemption lets "tokenized securities venues" trade tokenized versions of listed US stocks through permissioned AMM pools without registering as exchanges. It excludes synthetic tokens that give no ownership of the shares.
  - The proposed **Regulation Crypto Assets**, which covers token offerings, is open for comment until 20 October.
- **CFTC staff letters.** These are the "disclaimers" people cite. Their common logic is that software which only routes users to regulated venues is not a broker:
  - **26-05** (February) lets digital assets serve as margin.
  - **26-09** (March) gave that routing logic to one firm, Phantom's self-custodial wallet.
  - **26-25** ([17 September](https://www.cftc.gov/PressRoom/PressReleases/9300-26)) extends it to any "passive software provider." To qualify, the software must hold no customer assets, give no trading signals and use no routing discretion, and the provider must meet ten conditions, including joint liability with the venues it connects to. That covers wallets and apps that send users to registered exchanges and prediction markets such as Kalshi.
  - **FAQs** (updated 24 September) cover tokenized collateral and blockchain recordkeeping.

  Staff letters bind only CFTC staff, not DOJ or the states, and can be withdrawn. For now they are the working rulebook.
- **Listed spot.** Listed spot crypto has traded on CFTC-registered exchanges since December 2025, and the first bitcoin perpetual on a registered exchange launched in May 2026.
- **Tether audit.** On 13 August, [Tether announced](https://www.coindesk.com/business/2026/08/13/tether-says-it-completed-long-promised-big-four-audit-of-finances-behind-usd180-billion-usdt-stablecoin) that KPMG had given an unqualified opinion on its 2025 financial statements, which showed reserves exceeding token liabilities by $6.81 billion at year end. That completed the move from snapshot attestations to a full audit. Later quarterly attestations sit outside the audit opinion and move with Tether's gold and bitcoin holdings.

**Built.**
- **DTCC.** DTCC received SEC no-action relief in December 2025. On 15 July 2026, [more than 30 firms took part](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality) in live trades of DTC-custodied stocks, ETFs and Treasuries, settled on DTCC's private Besu network and on **Canton**. The full DTCC Tokenization Service is scheduled for October.
- **Canton**, built by Digital Asset, is a network of permissioned participants. It gives *sub-transaction privacy*: each party sees only the parts of a transaction it is party to. A "Global Synchronizer" orders transactions across institutions. Its token, CC, is worth $5 billion.
- **Robinhood Chain** mainnet launched on 1 July.
- **Exchange stakes.** ICE invested in OKX at a $25 billion valuation, and Nasdaq put $100 million into Kraken.
- **Scale.** Tokenized real-world assets total about $46 billion.

<div class="pfp-fig"><div class="pfp-title">US crypto oversight, September 2026</div><div class="pfp-box pfp-p"><b>Congress</b><div class="pfp-grid2"><div class="pfp-node pfp-g"><b>GENIUS Act</b><small>law since July 2025; final rules pending</small></div><div class="pfp-node pfp-r"><b>CLARITY Act</b><small>House 294–134; Senate cloture failed 49–50</small></div></div></div><div class="pfp-down">↓</div><div class="pfp-grid3"><div class="pfp-box"><b>Bank regulators</b><div class="pfp-note">OCC · Fed · FDIC · NCUA · Treasury</div><div style="margin-top:.4rem"><span class="pfp-chip ">Stablecoin issuers</span><span class="pfp-chip ">Trust charters</span></div></div><div class="pfp-box pfp-b"><b>SEC</b><div><span class="pfp-chip ">5-category token taxonomy</span><span class="pfp-chip ">Innovation Exemption</span><span class="pfp-chip ">Nasdaq tokenized trading</span><span class="pfp-chip ">DLT transfer agents (proposed)</span><span class="pfp-chip ">Reg Crypto Assets (proposed)</span></div></div><div class="pfp-box pfp-g"><b>CFTC</b><div><span class="pfp-chip ">Listed spot + perps on DCMs</span><span class="pfp-chip ">Letters 26-05 · 26-09 · 26-25</span><span class="pfp-chip ">Passive-software relief</span></div></div></div><div class="pfp-note" style="text-align:center;margin-top:.45rem">SEC ⇄ CFTC: MOU + binding joint interpretation (March 2026)</div><div class="pfp-sub">Tokenized equity rails</div><span class="pfp-chip pfp-a">DTCC → Besu + Canton</span><span class="pfp-chip pfp-a">Nasdaq → same order book</span><span class="pfp-chip pfp-a">Ondo / xStocks → Ethereum, Solana, BNB</span><span class="pfp-chip pfp-a">Robinhood → own chain</span></div>

**Status.** The US now has a working split between the SEC and the CFTC, built from binding interpretations, exemptive orders and staff letters rather than statute. A future administration could change all of it. Tokenized stocks are small next to US equity markets (about $3 billion against about $60 trillion), but incumbents are building the settlement infrastructure. That is the difference from 2017, when every token was an outsider.

**Reading.** [CLARITY Act, H.R. 3633](https://www.congress.gov/bill/119th-congress/house-bill/3633). [CoinDesk on the 49–50 vote](https://www.coindesk.com/policy/2026/09/15/crypto-clarity-act-flames-out-in-failed-u-s-senate-vote). [SEC Innovation Exemption, release 2026-90](https://www.sec.gov/newsroom/press-releases/2026-90-sec-issues-innovation-exemption-facilitate-trading-tokenized-nms-stock-request-comment). SEC–CFTC joint interpretation, 91 Fed. Reg. 13714 (2026). [CFTC release on Letter 26-25](https://www.cftc.gov/PressRoom/PressReleases/9300-26). [DTCC, tokenized trades](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality). [Tether, KPMG audit](https://tether.io/news/tether-completes-the-largest-inaugural-financial-audit-in-history/).

---

## 2026 (II): Privacy under stress: Zcash's bug, Ironwood, and TEEs

**Zcash.** Each Zcash shielded pool carries a different proof system and trust assumption:

| Pool | Year | Proof system | Setup |
|---|---|---|---|
| Sprout | 2016 | BCTV14 | trusted |
| Sapling | 2018 | Groth16 | trusted (MPC) |
| Orchard | 2022 | Halo 2 | none |
| Ironwood | 2026 | Halo 2 (patched Orchard), formally verified | none |

On 29 May 2026, [Shielded Labs](https://shieldedlabs.net/ironwood/) researcher Taylor Hornby found an under-constrained elliptic-curve multiplication in Orchard's circuit. The flaw had existed since Orchard's launch in 2022 and could in principle have let an attacker mint counterfeit ZEC inside the pool with no public trace. The response came in three steps:
1. An emergency soft fork disabled Orchard.
2. The NU6.2 hard fork (3 June) corrected the circuit and restored the pool.
3. **Ironwood** activated with NU6.3 on 28 July at block 3,428,143. It is a new pool that reuses the patched Orchard design with fresh note trees and nullifier sets, formal verification and quantum-recoverable notes. Orchard became withdrawal-only.

The **turnstile** limits the damage. Zcash tracks every pool's total balance publicly, and no pool can pay out more than went into it. The turnstile cannot prove that no counterfeit was ever minted inside Orchard, but it traps any that was. Fake ZEC would compete with real ZEC for Orchard's capped balance, and the last holders to leave would bear the loss, which is why the migration was pushed hard. Developers found no evidence of exploitation. By 10 September, 88% of Orchard's ZEC had moved to Ironwood.

**Status.**
- About 4.9 million ZEC, 29% of supply, is shielded.
- The **NU7** coinholder vote [closed on 14 September](https://crypto.news/zcash-holders-back-25-second-blocks-in-nu7-vote/). Only Ironwood balances counted, and ballots were encrypted. About 2.4 million of 3.6 million eligible ZEC voted: 99.9% for 25-second blocks (from 75), 98.9% for keeping bitcoin-style halvings. Features unfinished by 30 September drop out. No activation height is set.
- The legacy zcashd node has been retired in favor of the Zebra-based stack.
- ZEC fell by about half after the disclosure, then recovered. At $24.2 billion it is the ninth-largest crypto asset.
- **Monero** ($10.2 billion) is private by default using ring signatures. It is preparing a major upgrade (FCMP++) that enlarges each transaction's anonymity set to the whole chain. In August 2025 it survived a hashrate-majority stunt by the Qubic project that reorganized six blocks.

**NEAR Intents and TEEs.**
- **Intents.** With an intent, a user signs an *outcome* ("give me 10 ZEC for at most 5,000 USDC, on Zcash"), not a transaction. Solvers compete to fill it, and a verifier contract on NEAR settles atomically.
- **Chain Signatures** is a multi-party computation (MPC) network in which NEAR validators jointly sign transactions on Bitcoin, Ethereum, Zcash and other chains, so NEAR can hold and move native assets elsewhere.
- **Confidential Intents** (launched 25 February 2026, open to all developers from 8 July 2026) moves that settlement onto a private shard with permissioned validators and a [bridge running in trusted execution environments](https://www.near.org/blog/confidential-intents). Balances and fills are hidden from the public.

The trade-off is explicit. A TEE is fast and general-purpose, but the user trusts the chip vendor, the attestation chain and the operator set, and physical-access attacks on server TEEs were published in 2025. A zero-knowledge system like Zcash's asks the user to trust mathematics and audited code, and as May showed, that code can have bugs too. More than $1.5 billion of ZEC volume has flowed through NEAR Intents, which makes it a main on-ramp to shielded ZEC.

**The law of privacy** moved from sanctions toward nuance:
- Treasury delisted Tornado Cash (March 2025).
- [Treasury's March 2026 report to Congress](https://www.coindesk.com/policy/2026/03/09/u-s-treasury-signals-shift-on-crypto-mixers-acknowledges-legitimate-privacy-uses) said mixers have lawful privacy uses and recommended no new limits on non-custodial ones.
- DOJ ended regulation by prosecution.

Developer liability is still unsettled. The Storm retrial is pending, and CLARITY's §604 protection stalled with the bill.

<div class="pfp-fig"><div class="pfp-title">Zcash turnstile: counterfeit stays trapped in its pool</div><div style="display:flex;justify-content:center"><div class="pfp-node "><b>Transparent ZEC</b><small>public balances</small></div></div><div class="pfp-down">↕ &nbsp;&nbsp; ↕ &nbsp;&nbsp; ↕</div><div class="pfp-grid3"><div class="pfp-node "><b>Sapling</b><small>2018 · balance tracked publicly</small></div><div class="pfp-node pfp-a"><b>Orchard</b><small>2022 · withdraw-only since July 2026</small></div><div class="pfp-node pfp-g"><b>Ironwood</b><small>2026 · active pool, formally verified</small></div></div><div class="pfp-box pfp-b" style="margin-top:.6rem;text-align:center"><b style="margin:0">Rule: withdrawals from a pool ≤ deposits into it</b></div><div class="pfp-cap">The turnstile cannot prove no fake ZEC was minted inside Orchard, but any that was cannot leave the pool.</div></div>

<div class="pfp-fig"><div class="pfp-title">NEAR Confidential Intents</div><div class="pfp-row pfp-flow"><div class="pfp-node pfp-b"><b>User signs an intent</b><small>“10 ZEC for ≤ 5,000 USDC”</small></div><span class="pfp-arr">→</span><div class="pfp-node pfp-p"><b>Private shard</b><small>permissioned validators; solvers quote; best fill settles; state hidden</small></div><span class="pfp-arr">→</span><div class="pfp-node pfp-g"><b>Native BTC / ETH / ZEC</b><small>via Chain Signatures (MPC) + TEE bridge</small></div></div><div class="pfp-note" style="margin-top:.55rem">Trust: chip vendor + attestation + operator set · no client-side zero-knowledge proof</div></div>

**Reading.** [Shielded Labs, *Ironwood*](https://shieldedlabs.net/ironwood/). [Crypto Briefing, Ironwood activation](https://cryptobriefing.com/zcash-activates-ironwood-upgrade-after-orchard-security-flaw/). [Zcash ZIPs](https://zips.z.cash). [NEAR, *Confidential Intents*](https://www.near.org/blog/confidential-intents). US Treasury, illicit-finance risk assessment (2026). Monero FCMP++ research.

---

## 2026 (III): Base layers: Ethereum's next fork, Solana's new consensus, Bitcoin's quantum problem

**Ethereum.** **Glamsterdam** is [scheduled for its first public testnet, Sepolia, on 6 October](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement). Hoodi and mainnet dates are unset; developers target Q4 2026, and a large private devnet was still failing to finalize in September. It has two headline changes:
- **Enshrined proposer-builder separation** (ePBS, EIP-7732) moves the MEV-Boost builder market into the protocol, removing trusted relays.
- **Block-level access lists** (EIP-7928) declare in advance which state each block touches, so clients can execute and fetch data in parallel. That opens a path to much higher gas limits.

The next fork, **Hegotá**, centers on FOCIL (EIP-7805), fork-choice-enforced inclusion lists that let many validators force transactions into blocks. That limits a single builder's power to censor. Real-time proving (see 2025) is the longer arc, toward validators verifying a proof instead of re-executing every block.

**Solana.** Alpenglow [moved onto Solana's public testnet in late September](https://coinpaprika.com/news/solana-chases-150-millisecond-finality/), then devnet. No mainnet date is set, and Firedancer does not yet support it. SOL ETFs trade in the US.

**Bitcoin** is working through three debates at once.
- **Covenants.** Covenants would let an output restrict how it can be spent later, for vaults, channel factories and cheaper Layer 2s.
  - An independent [CTV (BIP 119) activation client](https://delvingbitcoin.org/t/bip-119-ctv-activation-client/2242) opened a signaling window from 30 March 2026 to 30 March 2027 that needs 90% of miners. Miner support has been minimal.
  - OP_CAT (BIP 347) has a finished specification and no activation path.
  - Meanwhile BitVM2 bridges run without any soft fork.
- **Data.** Bitcoin Core v30 (October 2025) loosened its default policy on OP_RETURN data. Node software Knots rejected the change. BIP-110, which would cap data at the consensus level, has minimal miner support. This is the Ordinals culture war reaching node policy.
- **Quantum.** A [Google Quantum AI paper](https://research.google/blog/safeguarding-cryptocurrency-by-disclosing-quantum-vulnerabilities-responsibly/) (March 2026, with Ethereum Foundation and Stanford co-authors) estimated that fewer than 500,000 physical qubits could break Bitcoin's elliptic-curve signatures in minutes, roughly 20 times fewer than earlier estimates. No machine near that size exists. By the paper's count about 6.9 million BTC, roughly a third of supply, sits in outputs whose public keys are already exposed, including early coins and reused addresses. [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki) (P2MR) was merged into the BIP repository in February 2026. It protects only coins whose keys stay hidden until spent; full protection needs post-quantum signatures, and no migration has been scheduled. Every major chain faces the same problem, and the ones that adopt lattice signatures such as ML-DSA early will avoid a forced migration later.

<div class="pfp-fig"><div class="pfp-title">Quantum exposure on Bitcoin (simplified)</div><div class="pfp-seg" style="margin-bottom:.4rem"><div class="pfp-r" style="flex:6.9">exposed now · ~6.9M BTC</div><div class="pfp-a" style="flex:13">key hidden until spent · ~13M BTC</div></div><div class="pfp-note">Of ~19.9M BTC mined. Exposure count from the Google Quantum AI paper (March 2026).</div><div class="pfp-grid3" style="margin-top:.6rem"><div class="pfp-node pfp-r"><b>Exposed now</b><small>early pay-to-pubkey coins, reused addresses, Taproot key path</small></div><div class="pfp-node pfp-a"><b>Exposed when spent</b><small>hashed-key outputs, vulnerable in the mempool window</small></div><div class="pfp-node pfp-g"><b>Proposed: BIP-360 P2MR</b><small>hides keys; post-quantum signatures come later</small></div></div><div class="pfp-sub">Ethereum forks</div><div><span class="pfp-chip ">Merge · 2022</span> <span class="pfp-arr">→</span> <span class="pfp-chip ">Shapella · 2023</span> <span class="pfp-arr">→</span> <span class="pfp-chip ">Dencun · 2024</span> <span class="pfp-arr">→</span> <span class="pfp-chip ">Pectra · 2025</span> <span class="pfp-arr">→</span> <span class="pfp-chip ">Fusaka · Dec 2025</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-b pfp-dash">Glamsterdam · ePBS + BALs · Sepolia 6 Oct</span> <span class="pfp-arr">→</span> <span class="pfp-chip pfp-dash">Hegotá · FOCIL · next</span></div></div>

**Status.** Ethereum's gas limit is rising and Glamsterdam is entering public testing. Solana's two biggest changes, Firedancer and Alpenglow, are partly shipped. Bitcoin is changing slowly, as designed, which makes quantum migration its hardest open problem.

**Reading.** [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732), [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928), [EIP-7805](https://eips.ethereum.org/EIPS/eip-7805). [BIP 119](https://github.com/bitcoin/bips/blob/master/bip-0119.mediawiki), [BIP 347](https://github.com/bitcoin/bips/blob/master/bip-0347.mediawiki), [BIP 360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki). Google Quantum AI, resource estimate for breaking elliptic-curve cryptography (2026). [ethereum.org roadmap](https://ethereum.org/en/roadmap/).

---

## Where the stack stands

| Topic | Covered in | Status, Sep 2026 |
|---|---|---|
| Bitcoin upgrades | 2017, 2018, 2021, 2024, 2026 | SegWit/Taproot live; covenants stalled; quantum open |
| Ethereum proof of stake | 2020, 2022, 2025, 2026 | Live since 2022; Glamsterdam Sepolia 6 Oct |
| Rollups and data availability | 2021, 2024 | Majority of activity; blobs + PeerDAS live |
| ZK proving speed | 2025 | Real-time; under half a cent per block |
| Zcash pools | 2018, 2022, 2026 | Orchard bug fixed; 88% moved to Ironwood |
| Other privacy | 2022, 2025, 2026 | Tornado delisted; Monero FCMP++ pending |
| TEE privacy (NEAR) | 2026 | Confidential Intents GA; hardware trust |
| Proof of reserves | 2019, 2022, 2026 | Routine; Tether KPMG audit |
| Stablecoins | 2018–2026 | ~$285–315B; USDT ~60–65% |
| GENIUS Act | 2025 | Law; rules pending; effective by Jan 2027 |
| CLARITY / SEC–CFTC | 2026 | Senate 49–50; joint taxonomy; Innovation Exemption |
| CFTC staff relief | 2026 | 26-05, 26-09, 26-25; FAQs |
| Perp DEXs | 2024, 2025 | Hyperliquid ~$9B OI; Lighter in Robinhood |
| Tokenized stocks | 2025, 2026 | ~$3B; DTCC live trades; Innovation Exemption |
| Restaking | 2023 | ~$5B; slashing live, untested |
| Bittensor | 2025 | 128 subnets; post-halving; governance fights |
| Storage | 2020 | Arweave AO; Filecoin Onchain Cloud |
| Proof of personhood | 2023 | ~18M Orb-verified; US live |
| Solana | 2020, 2021, 2025, 2026 | Firedancer live; Alpenglow testnet |
| Avalanche | 2020, 2024 | L1 network; institutional pilots |

---

## Disclaimer

This primer is for education and historical reference only. It is not investment, legal or tax advice. Market values are CoinMarketCap figures from 30 September 2026 and will change. Figures for 2026 events come from public announcements, regulators' releases and industry trackers. Some are early counts that later reporting may revise. Post Fiat Foundation contributors may hold digital assets discussed here, including assets whose design this primer describes.

## Data

Market values: [CoinMarketCap](https://coinmarketcap.com), 30 September 2026. Proving costs: [Ethproofs](https://ethproofs.org). Rollup status: [L2BEAT](https://l2beat.com). Tokenized assets: Token Terminal. Primary sources for each period are listed under **Reading** in its section.

## About the publisher

Post Fiat Foundation publishes this primer. Post Fiat is a settlement network in the XRP family; its [whitepaper](https://postfiat.org/whitepaper/) sets out which parts are live and which are targets.
