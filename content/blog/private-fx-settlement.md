---
title: "A Proposal for Better Private FX Settlement"
date: 2026-07-03T00:00:00Z
url: "/private-fx-settlement/"
aliases:
  - "/blog/private-fx-settlement/"
breadcrumb_label: "Blog"
breadcrumb_url: "/blog/"
summary: "Foreign exchange settles on rails that leak size and carry Herstatt risk on every uncovered leg. We rebuild the argument from theory — settlement finality, Kyle's model of information and impact, frequent batch auctions, dark-pool adverse selection — and propose a shielded frequent batch auction with atomic PvP over reserve-backed assets. New in this revision: a square-root law for internal netting, an information bound on what the externalized residual reveals, an equal-cost rule for batch length, and an unsentimental account of the two conditions the design still has to earn — a matcher nobody can see into, and a crowd."
description: "Market-design analysis of confidential FX settlement: settlement-risk theory (BIS 2025 Triennial, Herstatt), the microstructure of information leakage (Kyle 1985, Almgren-Chriss 2000), frequent batch auctions (Budish-Cramton-Shim 2015), dark-pool adverse selection (Zhu 2014), multi-CBDC bridges (Mariana, mBridge, Agorá), and original quantitative results: a square-root netting law, a mutual-information leakage bound, and a batch-length optimum."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - FX
  - Market Design
  - Privacy
  - CBDC
  - Settlement
  - Batch Auctions
---

## Two payments held together by nothing

Late in the afternoon of 26 June 1974, the German banking supervisor withdrew the licence of Bankhaus Herstatt, a mid-sized private bank in Cologne, and ordered it into liquidation. It was mid-morning in New York. Herstatt's foreign-exchange counterparties had paid Deutschmarks into Frankfurt hours earlier and were waiting on the dollars owed against them, due in New York that afternoon. The marks were trapped in the estate. The dollars never came. Banks that watched it happen began holding their own payments until they had seen the other side's arrive, and for a few weeks the plumbing of international finance ran backwards: everyone waiting, no one paying first.

The failure was small as bank failures go and enormous for what it exposed. A foreign-exchange trade is not one transaction. It is two payments, on two ledgers, in two jurisdictions, hours apart — held together by nothing except the expectation that your counterparty will still exist this afternoon. The exposure now carries the bank's name, which is the industry's way of admitting it never solved the problem, only named it.

Fifty-two years later the market that carries this risk turns over $9.6 trillion a day — the April 2025 figure from the BIS Triennial Survey, up 28% in three years. And for the first time, the 2025 survey measured settlement directly rather than inferring it: of average daily settlement, about $5.2 trillion — just over a third — settles payment-versus-payment, the only method that eliminates the risk outright. Roughly $7.6 trillion settles through methods that mitigate without eliminating — netting, intragroup books, timing controls. And $1.4 trillion a day settles gross and bilateral, exposed to the full Herstatt scenario, mostly because a counterparty, a currency, or a trade type falls outside the perimeter of any PvP system. Half a century of committee work, measured on the BIS's own comparable basis across its 2006 and 2025 settlement surveys: the PvP-protected share has crept from 54% to 56%, while currencies beyond the main PvP utility's reach have grown from 19% to 22% of global turnover.

This essay treats that state of affairs as a market-design problem rather than a plumbing problem, works through what the theory of settlement, information, and auctions jointly recommends, and proposes a mechanism. It also does something the previous version of this essay did not do carefully enough: it prices its own claims. Where a property is achieved, we say achieved; where it is a theorem about a system that does not yet exist, we say that instead, and we compute what the theorem is worth.

### Settlement risk is asynchrony risk

The response to Herstatt is best understood through one primitive. In 1996 the G10 central banks adopted a strategy (the Allsopp report) whose eventual product was CLS, live since 2002: a utility that settles both legs of a trade in an indivisible step, so that a member either receives what it is owed or keeps what it would have paid. **Payment-versus-payment** is the correct theoretical object — settlement risk is asynchrony risk, and PvP deletes the asynchrony.

CLS also demonstrates, at industrial scale, a second idea this essay will lean on: multilateral netting is astonishingly efficient. In 2025 CLS settled an average of $8.1 trillion a day and, on its record day that December, $22.9 trillion — funded with about $100 billion of actual pay-ins, half a percent of the gross. Opposite obligations, pooled, mostly annihilate each other. Hold that number; it returns later as the engine of something other than liquidity.

CLS's limitation is not the primitive but its perimeter: eighteen eligible currencies, a membership of settlement banks, one daily cycle anchored to a few hours when European and American payment systems overlap. Everything outside the perimeter — the growing emerging-market share of turnover, the counterparties who find membership uneconomic, the trades that miss the window — falls back onto the 1974 arrangement. The CPMI's 2023 push to widen PvP adoption and the 2025 revision of the FX Global Code, with its new hierarchy of settlement-risk mitigation, are candid official acknowledgments that the perimeter, not the principle, is the problem.

### Execution cost is information cost

The second inefficiency has nothing to do with settlement and everything to do with being seen.

Kyle's 1985 model is short enough to carry in a pocket. A trader knows something about value; uninformed flow of standard deviation σᵤ churns alongside; a market maker observes only the combined order flow and sets the price against it, p = p₀ + λ·(order flow). In equilibrium the impact coefficient is

```
        λ  =  √Σ₀ / (2 σᵤ)
```

— the ratio of how much there is to know (Σ₀, the variance of the trader's information) to how much cover there is to hide in (σᵤ). Size moves price not because size consumes liquidity but because size *is information*, and the market reads it. Almgren and Chriss (2000) formalized what every execution desk does about this: split the order, slow it down, spend calendar time to shrink the observable footprint. Their apparatus is the management of a symptom. Read literally, the theory's prescription is more radical than anything a scheduler can deliver: the optimal observable quantity of an order is zero.

No production rail delivers it, and the market has run the controlled experiment that shows what happens in its absence. For a few minutes each afternoon, foreign exchange already operates a batch auction — the London 4pm fix, where funds and corporates pool orders to cross at a single benchmark print, precisely because one coordinated price is easier to hold a portfolio to than a thousand fills. Between roughly 2008 and 2013, dealers at several of the largest banks shared their sight of pending fix orders in private chat rooms and positioned ahead of the flow. The rigging settlements ran to roughly ten billion dollars; a global head of FX trading went to prison for front-running a single client's $3.5 billion order. The scandal is usually filed under conduct. File it under mechanism design instead: the fix is *batching without confidentiality* — the orders pooled, and the intermediaries saw the pool. A batch auction whose book is visible to the people executing it is a machine for manufacturing exactly the anticipatory trading it was built to suppress.

So the status quo leaves two structural residues. Trillions a day settle with no protection against the oldest failure mode in the book, and the participants who move real size pay a tax denominated in information — to dealers, to venues, to anyone positioned to observe quantity before it is final. Neither is misbehaviour bolted onto a sound design. Both are the predictable output of a market whose settlement and execution were designed separately, by different people, in different decades, for different problems.

## The design space

Five families of mechanism address parts of this. Laying them side by side shows what each solves and — more usefully — where each one leaks.

```
                        Atomic   Hidden from  Hidden from   Finality       Settlement          Status
  Mechanism              PvP     the market   the operator                 asset
  ─────────────────────────────────────────────────────────────────────────────────────────────────────
  CLS + correspondent    yes¹    no           —             daily cycle    central-bank        live, 2002
                                                                           money, 18 ccys
  CCP (ForexClear etc.)  yes     no           —             daily cycles   via RTGS            live; deliverable
                                                                                               FX never mandated
  Multi-CBDC AMM bridge  yes     no           —             continuous     wholesale CBDC      pilots ended or
  (Mariana, mBridge)                                                                           handed over²
  Transparent on-chain   yes     no — worst   —             continuous     stablecoins         live; MEV-taxed
  AMM / CLOB                     case
  Trusted dark pool      no³     partly       NO            n/a            inherits bilateral  live; the operator
                                                                           settlement          is the leak
  ─────────────────────────────────────────────────────────────────────────────────────────────────────
  This proposal          yes     yes          no⁴ (v1)      swap: instant  reserve-backed →    proposed; swap
                                              open problem  batch: per-τ   CBDC (a spectrum)   prototyped
  ─────────────────────────────────────────────────────────────────────────────────────────────────────
  ¹ inside the settlement window, for eligible currency pairs and members
  ² Mariana concluded as an experiment in 2023; the BIS handed mBridge to its member
    central banks in late 2024 — see below, because the manner of that exit is itself data
  ³ dark pools are execution venues; settlement remains bilateral, with all that entails
  ⁴ the v1 batch constructor sees the committed book for one interval in order to cross it;
    on this axis v1 occupies the same cell as the dark pool — Open Problems, item two
```

The table is drawn to keep us honest, and the fourth footnote is the place to stand while reading it. In its first version, this design's matcher must see orders in order to cross them. Hidden from the market, hidden from every counterparty — not hidden from the operator. That is the cell the dark pool lives in, and the dark pool's history is why the cell is set in capitals. The differences are real and worth stating precisely: the operator's sight lasts one batch interval rather than a resting book's lifetime; the clearing is a single uniform price that the operator must *prove* was computed correctly from the committed inputs, so a misallocated fill is detectable after the fact in a way no dark-pool client ever enjoyed; and settlement is atomic rather than a promise. But briefly-trusted-and-auditable-afterwards is not blind, and we decline to typeset it as if it were. Making the matcher blind is this design's central open problem — a research program, named and scheduled below, not a footnote to be skimmed.

Row by row, the rest of the field: CLS solves PvP inside its perimeter and offers nothing on information. Central clearing brings genuine capital efficiency through novation and netting, but deliverable FX was carved out of the clearing mandates, and the lit central limit order book that typically feeds a CCP is the most information-revealing venue that can be built — a public ledger of the Kyle numerator. The multi-CBDC bridges are the most serious prior art and the direction we adopt for the settlement asset: Project Mariana (BIS with the Bank of France, MAS, and the Swiss National Bank) settled cross-border FX between wholesale CBDCs through an automated market maker; Project Agorá extends tokenized central-bank and commercial-bank money to a seven-central-bank, forty-institution testbed. But every one of them is transparent by construction — an on-chain AMM publishes its pool and its trades, which is superb for auditability and disqualifying for size; it re-imports the leakage the whole exercise should remove. Transparent public chains generalize that flaw and add MEV, a professionalized industry of being seen first. And the dark pool, TradFi's honest answer to Kyle, concentrates the entire information problem into one party — the operator — whose incentives the historical record has already graded.

No production mechanism occupies the row we want. The question is what it costs to occupy it, and in which currency.

## Three requirements, and a condition

The survey compresses into three requirements the mechanism must satisfy at once:

1. **Atomic PvP.** Both legs settle in one indivisible step, or neither does. *Settlement-finality theory; the principle CLS realizes and the 2025 survey shows two-thirds of settlement still lacks.*
2. **Confidential execution.** No market participant — and, when the open problem falls, no one at all — learns size, direction, price, or identity before a trade is final. *Kyle; Almgren–Chriss; the fix scandal as the natural experiment.*
3. **Incentive-compatible matching.** Opposite flows cross without a latency race and without an order-revelation channel. *Budish, Cramton and Shim (2015): discrete time, uniform price.*

And one condition that is not a requirement but a law this design lives under: **depth**. In a venue whose privacy comes from crossing, privacy is not a cryptographic constant. It is an equilibrium quantity. The anonymity literature learned this before finance did — Dingledine and Mathewson's phrase was that *anonymity loves company*: a hiding place is exactly as good as the crowd inside it. In a shielded batch your counterparties are your camouflage, and the arithmetic of the next sections makes the slogan exact — per-order leakage falls like 1/n in batch depth, and a batch of one conceals nothing. Every admiring property claimed below should be read with this condition attached, which is why it appears here, before the mechanism, and again at the top of the open problems, where it ranks first.

## The mechanism

### Settlement asset: reserve-backed native assets

Each currency is a native ledger asset whose reserves are proven on-chain — a dollar asset referencing a dollar reserve, a krone asset referencing a krone reserve. Native assets against attested reserves; not fund shares, not wrapped derivatives. The *quality* of the settlement asset — commercial reserve, tokenized deposit, wholesale central-bank money — is a separate axis, treated in its own section below, that upgrades without touching the mechanism.

### Execution: a shielded pool

Exchange happens inside a shielded pool in the confidential-transaction lineage — Pedersen commitments (1991), Zerocash (Ben-Sasson et al., 2014), the Halo2 proving system of Zcash's Orchard. A swap is proven correct — value conserved, input notes spent, output notes created — while the public ledger records only commitments. This is requirement (2) realized at the ledger layer: the execution footprint is zero observable quantity.

A single confidential swap is atomic PvP by construction:

```
  Atomic confidential swap                      (requirements 1 + 2)

   Party A (holds private USD notes)                 Shielded pool
   ─────────────────────────────────                 ─────────────
   1. request quote  ─────────────────────────────▶  bind {rate, policy, expiry}
   2. build swap locally, prove:                     ◀── bound quote
        spend(USD notes) ∧ create(NOK notes)
        ∧ value conserved  ── zk proof ───────────▶
   3.                      certified in one round ── both legs, or neither
   ─────────────────────────────────
   On the wire: commitments only. No amount, no rate, no direction, no identity.
```

There is no second ledger, no settlement window, no correspondent chain, and no instant at which one leg stands settled and the other does not. Herstatt's afternoon cannot be reconstructed here; there is no first payment to trap.

### Matching: a shielded frequent batch auction

A lone swap is not enough for size — a large order still moves the pool's reserve aggregate, and there may be no resting counter-flow. Here the market-design literature is decisive. Budish, Cramton and Shim showed that discretizing time and clearing each interval at one uniform price removes the value of speed and the mechanical front-running a continuous book invites. We take their auction and seal it: orders enter a batch as commitments, the interval clears at a uniform price, and opposite flows cross *inside* the batch, invisibly.

```
  Shielded frequent batch auction               (requirement 3)

   Party A: sell USD → buy NOK  ┐                        ┌─ A filled in NOK
   Party B: sell NOK → buy USD  ┼─▶  one certified  ─────┼─ B filled in USD
   Party C: sell USD → buy NOK  ┘    batch, uniform      └─ C filled in NOK
                                     clearing price

     internal cross:   A+C's USD  ⇄  B's NOK        netted, never externalized
     residual only:    (A+C − B) USD ── settle ──▶  market maker (hedges on lit venues)

   • uniform price   → nothing to gain from racing or outbidding within the batch
   • commitments     → no order visible to any counterparty before clearing
   • internal cross  → the crossing IS the liquidity; net, not gross, meets the world
```

Two properties follow immediately, and the previous version of this essay left both as assertions. The remedy for assertion is arithmetic.

## The arithmetic of hiding

Nothing in this section is deep. To our knowledge it has not been written down for this setting, and writing it down is what keeps the design honest — including where the numbers refuse to flatter it.

### A square-root law of camouflage

Let a batch collect n orders with sizes drawn independently around mean μ with coefficient of variation cv, each a buy or a sell of the base currency with equal probability. Gross flow G = Σqᵢ grows like n. The net N = Σ±qᵢ has mean zero and standard deviation μ·√(n(1+cv²)) — it grows like √n. The fraction of the batch's business the outside world ever sees is therefore

```
   f(n)  ≡  E|N| / E[G]  ≈  √( 2(1+cv²) / (π n) )
```

and with cv = 1 (order sizes as dispersed as they are large):

```
   depth n         10      25      50     100     400    1000
   externalized   36%     23%     16%     11%    5.6%    3.6%
```

Doubling depth cuts the externalized footprint by √2. Read once as liquidity: at n = 100 the venue internalizes 89% of gross, and the residual that must be hedged in lit markets is a ninth of the business done. This is not a speculative property of exotic infrastructure — it is the same annihilation CLS performs every day when it settles trillions against half a percent of funding. The batch simply moves the netting from the settlement layer, where it saves liquidity, to the execution layer, where it also does something stranger.

The stranger thing appears on the second reading, as privacy: the √n is the crowd each order hides inside. And the law has a floor worth respecting. If flow runs persistently 55/45 in one direction, f(n) converges to |2p−1| = 10% however deep the batch — with n = 100 it is about 14%, at n = 1000 it sits on the floor. Netting conceals *composition*, never *direction*. A sustained aggregate imbalance will surface, as it must: prices still have to discover which way the world is leaning, or the lit reference this venue prices against stops meaning anything. What the market permanently loses is the ability to tell one motivated buyer from forty routine ones — which, in Kyle's accounting, is most of what it was charging for.

### What the residual confesses

Honesty means running the microstructure argument against our own mechanism. The batch externalizes N to a market maker. N is observable. Observable quantities, by the entire logic of this essay, are information. So: precisely what does N give away?

```
   batch t−2        batch t−1        batch t
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ ▓▓▓▓▓░░ │      │ ▓▓▓▓▓▓░ │      │ ▓▓▓▓▓░░ │      ▓ crossed inside (never seen)
   └────┬────┘      └────┬────┘      └────┬────┘      ░ residual (externalized)
        ▼                ▼                ▼
      N_{t−2}          N_{t−1}          N_t    ──▶   the only time series the market ever gets
```

Under the model above, N is a sufficient statistic for the batch's imbalance and for nothing else. Measured in the correct currency — mutual information — what one participant's signed order sᵢ leaks through the published residual is

```
   I(sᵢ ; N)  =  ½ · ln( 1 + 1/(n−1) )  ≈  1/(2(n−1))   nats
```

At n = 51, about a hundredth of a nat per batch: the market learns, about you, almost exactly nothing. This is the quantitative content of *anonymity loves company*. It is also the warning label, because the bound is exactly as strong as its assumptions, and two failure modes deserve to be stated at full volume rather than discovered by a counterparty:

**A whale in a thin batch is naked.** For an order of size Q against typical counterflow, leakage is ½·ln(1 + Q²/((n−1)·E[q²])). Let Q be twenty times the r.m.s. order in a batch of fifty and the residual leaks over a nat and a half — sign and rough scale, effectively published. The discipline this imposes is familiar: optimal execution does not die inside the venue, it coarsens. Slice the parent across batches so each slice stays inside the crowd — Q of order √n times the typical order per batch holds leakage at the 1/n floor. Almgren–Chriss survives as an allocation across auctions rather than a race across milliseconds, and the venue should enforce the hygiene it depends on, with per-batch size norms tied to expected depth.

**Residuals form a time series.** A parent worked across k consecutive batches leaves a drift in N₁ … N_k, and the residual's market maker will read that drift the way market makers read everything. The venue conceals identity, composition, and gross; it does not conceal, and should not pretend to conceal, a sustained lean. Call it conservation of information: what can be hidden is *who* and *how much more is coming* — not, in the limit, *which way*.

With the confession filed, the positive claim can be stated at the precision it deserves. The mechanism does not eliminate the Kyle channel; it attenuates per-order leakage at rate 1/n and coarsens the market's observable to net-of-batch. In Kyle's own notation: from the perspective of anyone pricing the residual, every other participant's crossed flow has become your σᵤ — impact falls like 1/√n because the venue converts other people's business into your noise. The dark pool promised this and priced it in trust; the lit book refuses it on principle; the shielded batch delivers it to exactly the degree that the crowd shows up, and not one order further.

### How long is a batch?

Budish, Cramton and Shim, writing against the continuous book in equities, proposed intervals around a tenth of a second — long enough to kill the speed race, short enough that no human notices. Our interval exists for a different reason. A sealed batch has no speed race to kill; the interval is there to *accumulate camouflage*, and so it trades two costs. Wait longer and the batch deepens — n = Λτ at arrival rate Λ — so the externalized fraction c₀/√(Λτ) falls (c₀ = √(2(1+cv²)/π)). Wait longer and the clearing price goes stale against a moving market, a risk priced at roughly κσ√τ. Per unit traded:

```
   cost(τ)  ≈  κσ·√τ   +   γ·c₀/√(Λτ)
              staleness     residual impact

   τ*  =  γc₀ / (κσ·√Λ)        — and at τ*, the two terms are exactly equal.
```

An equal-cost rule: the batch should be exactly long enough that the marginal price of waiting meets the marginal value of company. The comparative statics behave the way design intuitions should. Volatile days want shorter batches (σ up, τ* down). Busier venues run faster *and* deeper — τ* falls like 1/√Λ while depth-at-optimum n* = Λτ* grows like √Λ, so scale buys both speed and cover at once. Markets where impact bites harder should wait longer for camouflage.

Numbers, offered for texture, on the napkin where they belong. An institutional major pair: Λ ≈ 100 parent orders an hour, staleness priced near 1bp per √minute, full-size lit impact γ ≈ 8bp, cv = 1. Then τ* ≈ 7 minutes, n* ≈ 12 orders a batch, a third of gross externalized, all-in cost around 5.3bp against 8-plus lit. Double the venue's flow and τ* drops under five minutes while the externalized share falls toward a quarter. And note what the same arithmetic says about the fashionable interval: at a BCS-style 250 milliseconds this venue would usually hold one order or none — f = 100%, confidentiality by batching at equity cadence is, for institutional FX arrival rates, a contradiction in terms. The design space is bracketed by two existing artifacts — the microsecond book and the once-a-day fix — and the mathematics of hiding lands deliberately between them, at minutes. Frequent, not continuous; the optimum is interior, which was the batch-auction literature's general lesson, here restated with a privacy term in the objective.

The cryptography fits inside those minutes with room to spare. Orchard-class proofs are built to be generated on ordinary client hardware in seconds and verified in milliseconds, with verification batching well; and proving sits off the critical path in any case, since a client proves against its notes and binds to a batch by commitment — the venue's true throughput constraint is verification and state update, comfortably faster than any economically sensible τ. The binding constraints on this design are economic and institutional. They are next.

## The settlement-asset spectrum, and who must act

Settlement *quality* is orthogonal to the mechanism:

```
  weaker finality ◀───────────────────────────────────────────▶ stronger finality

  commercial           tokenized bank          wholesale CBDC leg      two wholesale
  reserve-backed   →   deposit / regulated  →  + tokenized other   →   CBDC legs
  asset (today)        tokenized liability     (one central bank)      (both)

  issuer credit risk        reduced               one pristine leg      no issuer risk
```

The mechanism is invariant along this axis; only the credit behind the settlement asset changes. An earlier draft of this essay claimed that a single central bank could reach the third stage "without any counterpart central bank acting," and as a statement about the mechanism it is true — only one leg must be central-bank money for that leg to be pristine. As a statement about the world it was glib, and the gap between the two statements is where this design will actually be decided.

A wholesale CBDC leg does not wander into a privately operated confidential venue. It is issued into a *designated system*: settlement-finality statutes — the EU's Settlement Finality Directive and its analogues elsewhere — attach legal finality to systems that authorities have designated; designation drags the venue inside the oversight perimeter of the PFMI; and no overseer will bless a system it cannot see into. So the pristine leg has a price, and the price is sight.

The design can pay it, because selective disclosure is native to this cryptographic lineage rather than bolted on. Viewing keys expose a participant's flows, or a note's full history, to a named authority while exposing nothing to the market. The venue that results is dark to the market and legible to the supervisor — confidential in exactly one direction. It is worth sitting with how strange an object that is. The same construction that denies a dealer the sight of your order can grant a central bank, holding the right key, a cleaner record of settled FX than any reporting regime has ever assembled. The technology of hiding, held the other way round, is a technology of seeing; whoever custodies the keys custodies the sight; and the question of who that should be is a constitutional question arriving dressed as an engineering parameter. This essay flags it rather than resolves it. A version that did not flag it would be selling something.

Sequencing follows from the same realism. The entry configuration is regulated tokenized liabilities — deposit tokens, supervised e-money — with supervisory viewing keys and designated-system status as the milestones that actually gate progress. The wholesale-CBDC leg is then a policy decision taken *about* a functioning, overseen venue, not a deployment step inside one. Two-CBDC settlement — the direction of Project Agorá, whose seven central banks and forty-odd private institutions are due to report findings in the first half of this year — remains the destination rather than the entry point.

And the recent history of the CBDC pilots is the case study in why the institutional layer, not the technical one, is decisive. Project Mariana proved the wholesale-CBDC FX concept and concluded, as experiments do. Project mBridge reached minimum viable product in mid-2024 — and within months the BIS had, in its general manager's phrase, graduated out of its own flagship, shortly after a sanctioned head of state publicly floated the platform's architecture as a route around the correspondent-banking system that sanctions travel through; subsequent reporting describes a platform carried on by its remaining members, its volumes settling overwhelmingly in renminbi. Whatever one concludes about the exit, the lesson for any settlement design is the same: the mechanism survived contact with production, and the *sponsorship* did not survive contact with politics. Mechanisms are portable. Sponsors are not. A design that needs one central bank rather than a concert of them is easier to sponsor — that much of the original claim stands — but the one it needs must designate, supervise, and hold keys to a venue whose entire purpose is opacity. The technical statement was always true. The institutional statement is the hard one, and it is the honest form of the claim.

## Open problems, in order of severity

Three problems remain genuinely open. They are ordered by what kills the design first, and the first one is not cryptographic at all.

**1. Depth. The condition the whole construction leans on.** Every property claimed above — the netting, the leakage bound, the impact dilution — is a function of n, and n is a function of whether institutional FX will pool in a venue it cannot see into. Zhu (2014) supplies the sharpest form of the worry: when a dark venue sits beside a lit one, informed flow — which clusters on one side and therefore fails to cross — tends to sort itself toward the exchange, and the dark venue skims the uninformed. Uniform-price batch clearing blunts the mechanics Zhu studied, and the sorting itself is not unwelcome here — a venue whose imbalanced flow pays its own impact through the residual is a venue that structurally discourages toxicity. But no mechanism conjures the second side of a market, and the cold-start designs must be named rather than waved at: dealers committed to two-sided flow each batch in exchange for the residual franchise, which is the specialist's ancient bargain re-struck; scheduled deep batches at hours where flow already pools, because the 4pm fix is the standing proof that FX will coordinate at a point in time when benchmarking rewards it — this venue is, in one sentence, what the fix should have been; and per-batch size norms so that early whales do not vaporize the crowd they need. If institutional flow will not pool without pre-trade sight, this design fails, and it fails here first. That sentence belongs this early in the section because the previous version of this essay buried it, and burying the binding constraint is a way of lying with structure.

**2. Blinding the matcher.** Version one's batch constructor sees the committed book for one interval in order to clear it — the cell it shares with the dark pool, marked in the table and repeated here on purpose. Removing the operator's sight means computing the uniform clearing price and the fills over encrypted orders, so that no party, the venue included, ever holds the book in the clear. The encouraging precedent is old and agricultural: in January 2008, some twelve hundred Danish farmers cleared a nationwide double auction for sugar-beet production contracts under multi-party computation — the first production MPC market; a price was discovered and no one, operator included, ever saw a bid (Bogetoft et al., 2009). Sugar beets clear once a season and we need minutes, and that gap is the research program. Threshold decryption of a committed book — a t-of-m committee jointly opens each batch, no smaller coalition can — looks likelier to reach our τ than general-purpose MPC; trusted hardware enclaves are the tempting interim, and we distrust them for the standard side-channel reasons and say so now to avoid quietly relying on them later. Until one of these lands, the honest description of v1 is the one the table gives.

**3. Reference prices, and the parasite's bound.** A confidential venue does not discover price; it *imports* one, and both directions of that dependency need engineering. Inbound: the reference must be manipulation-resistant — a median or time-weighted read over multiple signed feeds, not a single print someone can paint in the seconds before a batch — and the staleness term κσ√τ in the batch-length rule is also, read differently, the budget an attacker must beat. Outbound, the subtler problem: this venue free-rides on the lit market's price discovery while siphoning off the uninformed flow that funds it. Grossman and Stiglitz taught the general form — someone must be paid to make prices informative — and it puts a ceiling on market share: succeed too completely and the reference degrades under you. An interior equilibrium, not total victory, is the design target, and pretending otherwise would be another flattering cell in the table. Alongside both sits legal finality: statutes are only beginning to say what a court should treat as final when settlement is a proof, and until they say it clearly, cryptographic finality and legal finality are different words that happen to rhyme.

What would change our minds, stated so that it can be checked: flow declining to pool at coordinated batch times without pre-trade transparency; threshold opening failing to clear realistic books inside single-digit minutes; overseers rejecting every viewing-key custody arrangement offered; or residual time-series leakage proving materially richer in practice than the imbalance floor the model sets. Any of these, demonstrated, moves this proposal from the table's last row back onto the pile.

## Related work

Settlement risk and PvP: the CPSS/Allsopp strategy (1996); CLS (2002–); Glowka and Nilsson, *FX settlement risk: an unsettled issue*, BIS Quarterly Review (2022); *Uncovering FX settlement risk: new measures from the 2025 BIS Triennial Survey*, BIS Quarterly Review (2026); CPMI, *Facilitating increased adoption of PvP* (2023); the FX Global Code as revised January 2025. Microstructure of information and execution: Kyle, *Continuous Auctions and Insider Trading* (1985); Almgren and Chriss, *Optimal Execution of Portfolio Transactions* (2000). Market design of batching: Budish, Cramton and Shim, *The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response*, QJE (2015). Dark-pool sorting and adverse selection: Zhu, *Do Dark Pools Harm Price Discovery?*, RFS (2014). The economics of informative prices: Grossman and Stiglitz (1980). Anonymity as a network good: Dingledine and Mathewson, *Anonymity Loves Company* (2006). Confidential transactions and zero knowledge: Pedersen (1991); Ben-Sasson et al., *Zerocash* (2014); the Halo2 proof system (Zcash Orchard). Production MPC auctions: Bogetoft et al., *Secure Multiparty Computation Goes Live* (2009). Multi-CBDC and tokenized settlement: BIS Innovation Hub Projects mBridge, Mariana, and Agorá.

## Implementation note

A prototype of the confidential swap and the reserve-backed settlement asset exists and is documented separately. The batch-auction matching layer and, above it, operator-blind matching are the open frontier. Every number in this essay's models is a model's number — the netting table, the leakage bound, the seven-minute τ* are consequences of stated assumptions, offered so that a reader can attack the assumptions rather than the arithmetic. This post is the mechanism and the theory that recommends it; it is not a claim that the mechanism is running.

## The empty row

The table has a row no production system fills: atomic, dark to the market, continuous, in good money. This essay has tried to earn a precise claim about that row — that settlement theory, microstructure, and market design, consulted jointly, specify one mechanism rather than a menu — while typesetting what occupying it still requires: a matcher nobody can see into, and a crowd. In principle, the shielded frequent batch auction over reserve-backed assets satisfies all three requirements at once; in practice it satisfies them conditional on those two problems, one cryptographic and one as old as market-making, and the essay that hides its conditions in a bullet list has already failed the standard it proposes for markets.

There is precedent for patience here. CLS was six years of committee work between the strategy paper and the first settled trade; the primitive was obvious in 1996 and the institution was the hard part, and it will be the hard part again. What is not conditional is the direction of the argument. The theory of settlement says the two legs should be one event. The theory of information says quantity should be nobody's to observe. The theory of auctions says matching should be discrete and uniform-priced. The cryptography that finally permits all three at once arrives with a clause of its own, and it is the clause to end on rather than bury: a market that can hide from everyone is also a market that chooses exactly whom it is visible to. Someone will hold that choice. The mechanism can be specified, and this essay has specified it; the keys are politics, and politics does not batch.
