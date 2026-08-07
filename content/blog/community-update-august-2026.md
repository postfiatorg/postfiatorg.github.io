---
title: "Post Fiat Community Update — August 2026"
date: 2026-08-06T21:30:00Z
draft: false
summary: "Layer 1 V2 on controlled testnet, the rebuilt Task Node board system, PF Terminal benchmarks, NAVCoin architecture, and the on-chain finance content push — with links to code and evidence throughout."
aliases:
  - /posts/community-update-august-2026/
categories:
  - Post Fiat Updates
tags:
  - Community Update
  - Task Node
  - PF Terminal
  - NAVCoin
  - Layer 1
description: "What is live, what runs on the controlled testnet, and what ships next across Post Fiat L1 V2, Task Node, PF Terminal, NAVCoin, and the on-chain finance content push."
---

Post Fiat runs five connected workstreams: Layer 1 V2, Task Node, PF Terminal, NAVCoin, and content distribution. This update states what is live, what has been validated on the controlled testnet, and what ships next — with links to the code, benchmarks, and dashboards throughout.

## How It Fits Together

<img src="/images/how-it-fits-together.svg" alt="How it fits together: Task Node and PF Terminal produce code, data, and research; content distributes it; hardened products convert attention into participation; NAVCoin converts participation into swaps and fees, which fund more building. PF Terminal powers every stage, and Post Fiat L1 V2 is the foundation." style="width:100%;max-width:760px;display:block;margin:8px auto 24px;" />

## TL;DR

| Priority | Workstream | Current status | Next |
| --- | --- | --- | --- |
| **1 — Distribution** | **Content / [Doom Index](https://goodalexander.com/doom-thesis/)** | Live, with published methodology, full history, and open JSON | Pivot [goodalexander.com](https://goodalexander.com) to on-chain finance |
| **2a — Hardening** | **[Post Fiat L1 V2](https://github.com/postfiatorg/postfiatl1v2)** | On controlled testnet: wallets, RPCs, Python libraries, validators, privacy, governance primitives | Governance-replay port; PF Terminal integration; public mainnet |
| **2b — Hardening** | **Task Node** | Rebuilt board system live; agents route and review tasks continuously | Private inference through Ambient; free chat |
| **3 — Monetization** | **[NAVCoin](https://github.com/postfiatorg/postfiatl1v2/tree/main/docs/navcoins)** | Connector layer and provable-NAV architecture built; chain primitives on the controlled testnet | Total-return perp and staking fixes; swap infrastructure; CBDC bridge research |
| **All stages** | **[PF Terminal](https://github.com/agtico/PfTerminal)** | Shipping, with live multi-provider model orchestration | Crypto-paid plans; native L1 V2 integration |

Hardening is one stage with two products, 2a and 2b; PF Terminal powers every stage. The sequence: content creates distribution, reliable products convert that attention into participation, and NAVCoin turns participation and portfolio activity into fees. Task Node and PF Terminal produce the data, research, code, and agent capabilities that feed all of it.

## Priorities

1. **Distribution:** the on-chain finance content push starts immediately.
2. **Hardening:** L1 V2 and Task Node get the reliability work required for dependable daily use.
3. **Monetization:** NAVCoin swap infrastructure connects portfolio activity to operating revenue.

PF Terminal supports all three stages. It deploys validators, powers coding agents, routes inference, and gives agents a crypto-native operating interface.

## 1. Post Fiat L1 V2

### Current status: controlled testnet

**[Post Fiat L1 V2](https://github.com/postfiatorg/postfiatl1v2)** is a Rust Layer 1 in its controlled-testnet phase — a network our team operates end to end. The repository holds 19 crates spanning consensus (`consensus_cobalt`, `ordering_fast`), privacy (`privacy_orchard`, `proofs`), execution, mempool, RPC, SDKs, and a WASM wallet. Wallets, RPCs, and Python libraries operate inside that controlled testnet, and operators can join it today using the published validator setup guide.

`STATUS.md` records the current measurements:

- Submit-to-finality at p50 (median) 1.56s on a 5-validator local cluster.
- A p50 1.03s certified round over WAN — validators separated by real internet distance.
- Working transparent transfers.
- Orchard/Halo2 shielded deposits, spends, and withdrawals — Halo2 is Orchard's zero-knowledge proving system — with nullifier sets providing double-spend protection for shielded notes.
- Cobalt validator-registry transitions with safety-witness verification.
- ML-DSA signatures from genesis.
- NAVCoin OTC-swap and proof-of-reserve primitives.

Every number above was measured on hardware we control, published now so the public network has a baseline to beat. The controlled-testnet target remains ~1.5s submit-to-finality. Public mainnet follows two gates already on the board: the governance-replay port and native PF Terminal integration.

### Why we rebuilt it

Post Fiat began as an XRP fork built around one problem: XRPL governance is opaque and unreplayable. Domagoj developed a multi-phase governance-replay process using SGX-verified inference — secure hardware attests to model outputs, so participants can verify a replay ran honestly. The process includes selection of the UNL (Unique Node List: the set of validators a node trusts), and many current validators have been through it.

For evidence on the governance problem, we read the XRPL amendment record end to end and attributed each decision to its originating organization. Roughly 80% traces to Ripple, and much of that agenda diverges from what a buy-side chain — one built for asset owners and portfolio managers — requires. The same review surfaced bugs, which we wrote up and disclosed to the affected parties. The full governance thesis appears in the May 2026 revision of the **[Post Fiat Whitepaper](https://postfiat.org/whitepaper/)**.

Three requirements drove the rebuild:

1. **Quantum resistance.** ML-DSA is the NIST post-quantum signature standard. Post Fiat requires it from genesis.
2. **Private settlement.** Orchard — the shielded-pool design pioneered in Zcash — enables shielded transactions for buy-side workflows. The design, including exclusion of validator-consensus accounts, is covered in the **[Orchard Privacy Research](https://postfiat.org/posts/orchard-privacy-research/)**.
3. **Replayable governance.** Cobalt lets each validator declare and update its UNL on-chain. Ripple designed and published the approach; Post Fiat implemented it.

ML-DSA and Orchard live in Rust ecosystems, so since May the Layer 1 has been rebuilt in Rust with vendored Orchard/Halo2 dependencies, private swaps, Cobalt-governed validator evolution, and HotStuff-style finality — the consensus family behind modern Byzantine fault-tolerant chains.

Next: the governance-replay port and native PF Terminal integration. The **[Validator Setup guide](https://postfiat.org/validator-setup/)** covers installation, configuration, domain attestation, and verification. The **[Validator Benchmark](https://postfiat.org/validator-benchmark/)** publishes mode scores, ranks, and correlation tables from validator credibility runs.

## 2. Task Node: the Hive rebuilt

### Current status: live

The old Hive board failed — its manager generated tasks blind to the codebase, judged submissions without checking whether a pull request improved the project, and let duplicate-account farming erode reward credibility. The rebuilt system is live, and community members are receiving network tasks today:

- **One continuous agent per board.** Kimi K3 and GLM 5.2 class models stay grounded in the repositories each board covers.
- **Code-aware task generation.** Agents create tasks from actual repository state and review the code that comes back.
- **Deterministic reward caps.** Every reward decision passes through fixed limits.
- **Public decisions.** The **[Hive Brain](https://tasknode.postfiat.org)** publishes each agent's activity feed with a plain-English account of its reasoning.

The live app contains tasks, wallet functions, chat, six network boards with live routing, and the Hive Brain. Two model developments made this architecture practical: frontier models of the GPT Terra class for judgment, and cheap open-source models such as DeepSeek Flash that run continuously at viable cost. The Task Node remains the center of daily participation and protocol differentiation. New members can start with the **[Task Node overview](https://postfiat.org/task-node/)**.

### Private inference and free chat

Confidentiality is the most consistent product request: users want plans and code kept away from third-party readers. Post Fiat closed a compute deal with Ambient for private Task Node inference. Ambient's merger moved its centralized inference business to a dedicated provider — a transition that interrupted compute sourcing for a stretch and ended in a stronger agreement. The same agreement supplies the compute path for free Task Node chat and crypto-paid PF Terminal plans. Both ship next.

## 3. PF Terminal

### Current status: shipping and benchmarked

PF Terminal began as a Codex fork with Task Node integration and grew into a multi-provider coding terminal with model-aware agent orchestration. The product rationale is in **[Introducing Post Fiat Terminal](https://postfiat.org/research/introducing-post-fiat-terminal/)**.

Our published benchmark measures PF Terminal at roughly 2–3× faster and 1.4–2.6× cheaper than Claude Code and Hermes on the same Anthropic and GLM models at identical accuracy. We ran those tests ourselves, priced them at provider-billed costs, and published a reproduction script so anyone can rerun them — methodology and results are in **[Introducing Post Fiat Terminal](https://postfiat.org/research/introducing-post-fiat-terminal/)**. Inside OpenAI's own ecosystem, performance is at par.

The gain came from replacing an OpenAI-specific assumption inside Codex. OpenAI models emit file edits through ApplyPatch, an editing format wired into their training and harness; PF Terminal rebuilt that layer for multiple providers. Its orchestrator now routes sub-agents on three signals: cost, tokens per second, and benchmark performance.

The open-source **[PF Terminal repository](https://github.com/agtico/PfTerminal)** supports OpenAI, Anthropic, Kimi, GLM, Grok, and additional models through direct providers, gateways, prepaid plans, and local inference. It ships with encrypted credentials, Telegram control, and a local Solana wallet for SOL, USDC, and inference plans.

PF Terminal plays two direct roles in the Layer 1 strategy. First, community analytics showed validators being deployed by pasting agentic instructions into Codex and Claude Code; a terminal-native Linux installation path makes that deployment repeatable and verifiable. Second, an agent that earns money needs a coding harness, USDC funding, and accessible compute — PF Terminal puts all three in one interface. Next: crypto-paid inference plans, Ambient compute, and native L1 V2 integration.

## 4. NAVCoin

### Current status: public architecture, controlled-testnet primitives

October 10, 2025 — "10/10" — exposed a basic weakness in crypto balance sheets. During that day's liquidation cascade through Binance's USD markets, USDe traded to 67 cents while holders had zero independent way to verify whether the balance sheet behind it was whole. Attested balances run on trust in an accountant's letter, and the same structure holds for Tether, the largest fee generator in crypto at a ~$300B secondary-market cap.

NAVCoin's approach:

> Wrap a market-neutral portfolio, prove its net asset value with zero-knowledge proofs, and make that provable NAV swappable.

The market-neutral and basis-trading strategies AGTI has run for years operate at 7–8 realized vol — below G10 currencies — while carrying real drawdowns and an upward drift over time. Wrapping such a portfolio as a fixed dollar creates a liability mismatch. Presenting its changing NAV directly creates a distinct, honest asset.

NAVCoin lives inside the Layer 1 repository: the **[NAVCoin documentation](https://github.com/postfiatorg/postfiatl1v2/tree/main/docs/navcoins)** covers reserve primitives, supported assets and venues, the Uniswap pool design, and PFTL tooling, while the chain-side OTC-swap and proof-of-reserve primitives run in the L1 V2 controlled testnet. The connector set covers staked NEAR, staked SOL, staked ETH, Hyperliquid perpetuals, and collateral plus its yield. The full architecture appears in the **[Post Fiat Whitepaper](https://postfiat.org/whitepaper/)**.

Provable NAV unlocks a concrete sequence: private OTC portfolio swaps, then Uniswap pools for exit liquidity, then trustless redemption at NAV on the Post Fiat L1. Bob bridges USDC and swaps into Alice's NAVCoin; he can exit through the pool or redeem privately at NAV.

### Near-term fee line: indices and fixes

Perpetuals routinely trade at several multiples of spot volume, yet crypto still lacks a total-return BTC-perp series with a London-style fix — the daily reference print convention that gold and FX markets settle against — including collateral yield, often 10% a year. A trustless fix for staked assets and perpetuals creates a standard reference value; a standard reference supports larger swaps, and swaps generate fees.

### Research directions

Two directions sit in research today.

**CBDCs.** Norges Bank operates a CBDC sandbox with an active repository. Once fiat assets become chain-representable, the research path connects CBDC liquidity to market-neutral NAVCoin exposure — an FX-to-portfolio bridge outside the dollar.

**Agent NAVCoins.** AI agent tokens sell a story about an agent's future output. A NAVCoin wrapping a PF Terminal agent sells a defined asset: the agent's NAV, proven over time. Think VendingBench — the benchmark testing whether an agent can run a small business over long horizons — applied to real capital, with performance anyone can verify on-chain.

### Economics: studying the Chainlink Reserve model

NAVCoin swaps, index fixes, and PF Terminal inference are fee-generating services operated by the project. The open design question is how fee-generating services should relate to a protocol's economics, and the model we study most closely is the Chainlink Reserve.

Chainlink's approach has three properties worth learning from. Revenue from real services — enterprise integrations, data feeds — flows into an on-chain reserve with public, verifiable accounting. The structure was developed in the open, through years of iteration alongside U.S. regulators, rather than announced first and defended later. And it sequences conservatively: services earn first, the reserve accounts publicly, and structural claims follow the record instead of preceding it.

That sequencing matches how Post Fiat operates: build the services, publish the accounting, let structure follow evidence. Which services fit such a model, in which jurisdictions, under what structure — those are live research questions. Decisions will be announced through official channels after full legal review.

## 5. Content: the Doom Index and on-chain finance

### Current status: live distribution asset

Technology needs distribution to produce attention, liquidity, and market growth, and the immediate content focus is agentic and on-chain finance — including the rise of on-chain stocks. Robinhood Chain's direct on-chain stock initiative expands the audience for chain-represented portfolios, indices, swaps, and market-neutral products, and that audience maps straight onto the NAVCoin model.

The **[goodalexander site](https://goodalexander.com)** is pivoting to on-chain finance. Its anchor is the **[Doom Index](https://goodalexander.com/doom-thesis/)**, a live dashboard measuring federal debt and unfunded obligations against household income and public-company earnings — methodology, score, full history, and open JSON, all published.

The content plan: publish differentiated datasets and trade research, turn Task Node and PF Terminal output into usable analysis, build an audience around on-chain stocks, agentic finance, and market structure, and route that audience toward Post Fiat products and NAVCoin liquidity.

For Task Node members, the direct benefits: free access to AGTI datasets, the underlying reports, trade ideas, content generation, PF Terminal coding accounts, and free Task Node chat under the new inference agreement.

## The Post Fiat flywheel

Task Node and PF Terminal produce code, datasets, research, and agent capability. Content packages that edge and pulls new users into the ecosystem. A hardened L1 and Task Node convert their attention into daily participation. NAVCoin converts portfolio activity into TVL, swaps, and fee-generating services — and those services fund more building. Underneath the loop sits a Rust Layer 1 with ML-DSA signatures, Orchard privacy, published finality evidence, and governance any participant can replay and verify.

Distribution first. Hardening second. Monetization third. PF Terminal powering every layer.
