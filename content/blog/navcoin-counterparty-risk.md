---
title: "Pricing Counterparty Risk into the NAVCoin"
date: 2026-06-11T00:00:00Z
summary: "A NAVCoin verifies what its venues report. Option markets price whether those venues survive. Multiply the two and every NAVCoin carries a live credit spread on-chain — turning the silent source of crypto yield into a number anyone can read."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - Credit Risk
  - Counterparty Risk
  - Options
  - Basis Trading
  - Post Fiat
---

*This article extends the NAVCoin design published by Post Fiat Research on June 10, 2026 ([postfiat.org/blog/navcoin-proposal](https://postfiat.org/blog/navcoin-proposal/)). It stands alone: Section 1 summarizes the NAVCoin in three paragraphs, and everything after is new.*

---

## 1. What a NAVCoin is

A NAVCoin is a token whose unit value tracks the net asset value of a reserve portfolio, where machines verify the marking on a fixed cadence instead of the issuer asserting it and accountants sampling it quarterly. It is not a stablecoin and does not pretend to be one: if the reserves decline, the NAV declines. The protocol enforces a hard arithmetic invariant — verified net assets must equal circulating supply times NAV per unit — so supply can grow only against reserves that actually verified. If the issuer stops proving, minting and redemption fail closed automatically.

Evidence comes from measured code running inside trusted execution environments against venue APIs, or from independent observers watching public sources. Disclosure happens in published, immutable tiers: full transparency (Tier 0); class-level aggregates such as "spot at qualified custodian; futures margin at exchange, 15% haircut" (Tier 1); a single attested coverage number (Tier 2). The market prices opacity instead of the protocol forbidding it.

The design names its own deepest limit. Machine verification proves what venues *reported*, not what is *true*. A reserve packet attesting "$500M of margin at venue V" is faithful testimony about V's API; it says nothing about whether V's database entries are backed, encumbered, or exceeded by liabilities elsewhere. A quietly insolvent exchange passes every cryptographic check. That residual — venue credit risk — is the subject of this article. Verification cannot eliminate it. The NAVCoin's own disclosure machinery, combined with option markets that already trade, can *price* it: continuously, on-chain, in a form anyone can recompute.

## 2. Counterparty risk is where the yield comes from

Crypto's signature "market-neutral" trade — long spot, short the perpetual, harvest the funding — carries little price risk and never has. Its yield is not alpha in the usual sense. It is rent on a scarce input, and the scarce input is willingness to hold an unsecured claim on an exchange: the short leg must be margined somewhere, and that somewhere can fail. There is a reason unlimited institutional capital does not pile into Binance basis until the spread compresses to Treasury bills. The trade's capacity is bounded by counterparty appetite, not by strategy. Ethena is the clearest acknowledgment in production: its off-exchange settlement architecture — collateral parked with custodians rather than on the venues it trades — exists because exchange credit is the binding constraint of the entire carry complex.

Finance keeps relearning the same lesson. Lehman's prime-brokerage clients discovered rehypothecation in 2008. MF Global's customers discovered where segregated funds had gone in 2011. Archegos blew through six prime brokers in 2021 because each saw only its own slice of a concentration no one could aggregate. Celsius and BlockFi sold deposit products that were unsecured loan books. FTX sold "market-neutral basis at 15%" that was an unsecured loan to the venue, relabeled as genius. In every case the position was fine and the intermediary was the risk — and in every case the exposure was invisible until it was total.

NAVCoins inherit this tension in sharpened form. Managers will not publish positions; strategy is the product, and the disclosure tiers exist precisely so they don't have to. But a holder evaluating a NAVCoin needs the one thing those tiers can conceal: a picture of counterparty exposure. A fund running CME bitcoin futures basis at a modest yield and a fund running HYPE perp basis at a rich one should not display identically — the second is being paid for a risk the first declined, and that difference belongs on the label. The resolution is a bubbled-up score: keep the portfolio private, publish the risk.

We propose the **venue credit spread (VCS)**: a per-epoch, on-chain field that multiplies a NAVCoin's attested venue-class exposures by market-implied distress probabilities for those venues, extracted from option markets that already trade. The claim has three parts. The theory connecting puts to credit is settled finance (Section 3), and exchange tokens extend it to venues without listed equity (Section 4). The construction is computable today from attested disclosures plus public quotes, with a defined fallback when quotes are missing (Section 5), and it would have read correctly through the canonical disaster (Section 6). And the result — counterparty risk as a first-class field on a portfolio token — makes the NAVCoin a better primitive for on-chain portfolio finance than anything the off-chain fund world reports (Section 7).

## 3. A put on equity is a credit instrument

The construction rests on one of the oldest results in modern finance. Merton (1974), building on Black and Scholes (1973), models a firm's equity as a call option on its assets struck at the face value of debt. Put–call parity on the balance sheet then yields the statement that matters here: **risky debt equals a risk-free bond minus a put on the firm's assets.** Holding credit exposure *is* being short a put. Credit and put options are not analogous instruments; they are the same instrument viewed from opposite sides of the balance sheet. First-passage and endogenous-default extensions (Black and Cox 1976; Leland 1994) refine the dynamics without disturbing the identity.

Three results carry the identity from theory to trading. Carr and Wu (2011) prove a model-free version: assume only that default knocks the stock below a low barrier `B` and keeps it there through expiry, and a vertical spread of two American puts struck below that barrier prices a pure default claim — `U = [P(K₂) − P(K₁)] / (K₂ − K₁)` equals the value of one dollar paid at default before expiry, for any `K₁ < K₂ ≤ B`, *regardless of the dynamics of the stock or its volatility*. Credit default swap spreads can be written directly in these unit recovery claims: deep out-of-the-money puts and credit protection are interchangeable, robustly rather than approximately. Culp, Nozawa, and Veronesi (2018) supply the empirical mirror. Their "pseudo-bonds" — Treasuries minus equity puts, the Merton replication run literally — carry credit spreads that match actual corporate bond spreads across rating classes: option markets and bond markets price the same default risk consistently. And the mapping is observable in the skew: Hull, Nelken, and White (2004) recover credit spreads from two points of the implied-volatility smirk, while Cremers, Driessen, and Maenhout (2008) show option-implied jump risk explains the level of corporate spreads.

Two technicalities matter for crypto. Listed crypto options are European where Carr–Wu assumes American; at a 90-day tenor the gap is the interest carry between default time and expiry — negligible, and signed conservative, since the European spread bounds the default claim from below. And when the reference claim recovers *nothing* in default, the extraction collapses to a single instrument: one deep put identifies the default probability outright, `Q(τ ≤ T) ≈ P(K) / (K · DF(T))` for `K ≤ B`. The next section explains why exchange tokens satisfy that zero-recovery condition almost exactly.

## 4. Exchange tokens are the junior claim on the venue

Listed venues are the easy case. Coinbase (COIN) and Interactive Brokers (IBKR) carry deep, OCC-cleared equity option markets, independent of crypto settlement infrastructure by construction, and the structural model applies as written. Most crypto venues have no listed equity. They have a token — and the token is, economically, the junior-most claim on the venue's going-concern value.

Consider what the token's value consists of. BNB began as a fee-discount claim and accreted utility: trading discounts, burns funded by venue revenue, gas on BNB Chain, collateral status. HYPE capitalizes Hyperliquid's fee flow through the Assistance Fund's continuous buybacks, plus gas and staking utility. Cong, Li, and Wang (2021) formalize the structure: a platform token's value derives from expected transactional benefits on the platform, so the token price capitalizes the platform's adoption and survival. Every term in that valuation is conditional on the venue operating. A fee discount buys nothing when there are no fees to discount. A burn funded by revenue stops when revenue stops. Gas on a dead chain meters nothing. The token is a strip of coupons clipped from a going concern, with no claim on the corpse.

That last clause makes the token a *cleaner* credit instrument than equity. Shareholders stand somewhere in the bankruptcy waterfall, and their recovery must be modeled; token holders generally stand nowhere — the token confers no claim on the estate, and any recovery is incidental. FTT is the type specimen: roughly $25 at the start of November 2022, under $4 ten days later, zero as a claim. Zero recovery is exactly the condition under which the single-put extraction of Section 3 holds, and the market grasped the structure intuitively in real time — FTT *was* the credit instrument, and shorting it was the only credit default swap on FTX anyone could buy.

Token prices also move on unlocks, burns, governance shocks, and broad crypto beta — none of it credit. Three filters separate signal from noise. Deep OTM put spreads price the jump-to-ruin state specifically and are robust to diffusion dynamics by construction; that is the content of the Carr–Wu result. Running the identical extraction on BTC and ETH deep puts yields the market-wide jump hazard, and the venue-idiosyncratic hazard is the floored excess. What remains — a regulatory shutdown reads like an insolvency — is tolerable for a credit display, because both events impair a claim parked at the venue. One entanglement earns its own schema field: when a venue holds its own token as treasury or collateral, the FTT pattern, the token's fall produces the failure it predicts. The signal leads by construction, and a **self-collateralization flag** makes that reflexivity a disclosed fact rather than a discovered one.

## 5. The construction

The spread is one line:

```
VCS  =  Σ_priced  w_i · λ_i · L_i   +   u · s_floor
```

`w_i` is the NAVCoin's attested Tier-1 weight in venue class `i`. `λ_i` is the market-implied hazard for that class's reference claim. `L_i` is a loss-given-default for the class. `u` is the **unpriced share** — weights with no eligible estimator, plus the entire NAV of issuers who decline to participate — and `s_floor` is a penalty rate. Every input is either already published each epoch by the NAVCoin protocol (the weights, attested by measured code) or computable from public market data (everything else). The subsections walk the pieces.

### 5.1 Reference claims and the independence rule

A methodology registry maps each venue class to the instrument whose options price that venue's distress — its **reference claim** — under one binding constraint: the market supplying the quotes must not depend, for settlement or collateral, on the venue being priced. Pricing Binance with options that clear on Binance is circular; in the crisis state, the quote source dies with its subject. The current landscape makes the rule bite immediately:

| Venue | Reference claim | Status (June 2026) | Grade |
|---|---|---|---|
| Coinbase | COIN equity options | Deep, OCC-cleared, fully independent | Primary |
| Interactive Brokers | IBKR equity options | Deep, OCC-cleared, fully independent | Primary |
| Hyperliquid | HYPE options on Derive | Live since Nov 2025; settles on Derive, but HYPE collateral bridges via a HyperEVM vault — quotes usable, partial dependency flagged | Primary, flagged |
| Binance | BNB options | Deribit listed BNB options, then delisted them in July 2025 for low activity; remaining liquid BNB options sit on Binance itself | Synthetic (§5.3) |
| No claim, illiquid spot | — | — | Floor (§5.4) |

The Binance row is the instructive one: the most systemically important venue in the asset class has no liquid, independent options market on its claim. The methodology must therefore define what happens in the gap — Section 5.3 — and every displayed number carries an **estimator tag**, so a reader knows whether a spread came from a quoted market, a model, or a penalty default. A venue the market cannot price is itself a fact a holder deserves to see.

Digital-asset treasury companies supply one more quote source, worth a paragraph and no more. Hyperliquid Strategies (Nasdaq: PURR) holds over $1.3B of HYPE against a similar market capitalization and carries listed, OCC-cleared options — quotes fully outside crypto settlement infrastructure, which no crypto-native venue can offer. The basis is the wrapper: a treasury-company equity is token NAV times a premium/discount ratio, so a deep PURR put pays on either HYPE collapse *or* premium compression. That contamination inflates the implied hazard — an upper bound, which is the direction the methodology is required to err. DAT quotes therefore enter as supplementary inputs at secondary grade, with the wrapper discount observable in real time because treasury wallets are disclosed on-chain. The largest BNB treasury, CEA Industries (Nasdaq: BNC), shows the failure mode: a micro-cap trading far below its token NAV amid a governance fight, with an options chain that exists on paper and not in depth. A ticker with a chain is not a usable credit signal; the eligibility gates below decide, not the listing.

### 5.2 Extracting hazard from quotes

For each venue with an eligible claim, the lane computes at a constant 90-day tenor, interpolated from listed expiries, as a time-weighted average of mid-quotes across the epoch and a trimmed median across quote venues. Claims with meaningful recovery — listed equities — use the Carr–Wu spread: `U = [P(K₂) − P(K₁)] / (K₂ − K₁)` for strikes below the registered barrier, `Q ≈ U / DF(T)`, hazard `λ = −ln(1 − Q) / T`. Zero-recovery tokens use the single-put identity, `Q ≈ P(K) / (K · DF(T))`, with the spread version as a cross-check where two strikes list. An optional netting step removes the systematic component: `λ_idio = max(λ − β · λ_mkt, 0)`, with `λ_mkt` extracted identically from BTC and ETH deep puts.

Eligibility gates quotes before they touch the estimator: minimum open interest and depth at the relevant strikes, a maximum bid-ask width, at least one strike at or below the barrier, and the independence test of 5.1. Quotes that fail demote the venue to synthetic grade for that epoch. A hollow book never produces a primary-grade number.

### 5.3 When no quotes exist: the synthetic put

A credit model that goes blind exactly when a token prints a −30% candle into an empty options book is mis-specified where it matters most. So where no eligible quoted market exists but the token's spot and perpetual markets remain liquid, the methodology constructs a **synthetic quote** — the price at which a competitive market maker would write and hedge the deep put — and runs the extraction of 5.2 on it unchanged. Two literatures make the synthetic principled rather than improvised.

First, implied volatility is forecast realized volatility plus a measurable premium. Christensen and Prabhala (1998) show implied volatility predicts subsequent realized volatility and subsumes the information in history; the wedge between the two is the variance risk premium, which Carr and Wu (2009) measure with synthesized variance swaps and Bollerslev, Tauchen, and Zhou (2009) show is systematic. The same structure holds one moment higher: implied skew tracks realized skew at a premium — Neuberger (2012) defines realized skewness so the comparison is well-posed, Kozhan, Neuberger, and Schneider (2013) measure the skew premium, and Bakshi, Kapadia, and Madan (2003) give the model-free risk-neutral skewness a surface must hit. A missing quote can therefore be rebuilt: forecast the realized inputs, then add the premia. Crypto helps with the first step, because 24/7 tick data makes realized measures cleaner than in equities (Andersen, Bollerslev, Diebold, and Labys 2003 for measurement; Corsi's 2009 HAR model for forecasting). The premia transfer from the basket where both sides trade: estimate the implied-to-realized variance and skew multipliers each epoch on BTC, ETH, SOL, and HYPE, and apply them to the unquoted token's forecasts. Every token that later lists options tests the transfer out-of-sample.

Second, the asymmetry — venue tokens drop fast and grind up — is the realized-side phenomenon the skew literature prices. The leverage effect (Black 1976; Glosten, Jagannathan, and Runkle 1993) says negative returns raise future volatility more than positive ones; Patton and Sheppard (2015) sharpen it, showing downside *signed jumps* specifically predict elevated volatility. Bipower variation (Barndorff-Nielsen and Shephard 2006) isolates the jump component from diffusion in near-real time, and realized semivariance (Barndorff-Nielsen, Kinnebrock, and Shephard 2010) isolates the downside half. A death candle therefore loads the jump-intensity and downside-semivariance estimators within the epoch it prints, steepening the synthetic skew and fattening the synthetic deep put: **realized distress raises displayed credit risk immediately, no options market required.** Where smirks do trade, steep ones predict subsequent crashes (Xing, Zhang, and Zhao 2010) — the implied and realized objects are two views of one distribution — and where a venue discloses leverage, a CreditGrades structural term (Finger et al. 2002) sets the default barrier.

Third, an option's price is its hedging cost, and the hedging cost is computable from the markets that stay liquid. Leland (1985) shows replication under proportional transaction costs is Black–Scholes at an adjusted volatility, `σ̂² = σ² · (1 + √(2/π) · k / (σ√Δt))`, with `k` the round-trip cost — observed directly as half-spread in the token's spot and perp books. Almgren and Chriss (2001) price the market impact of the hedger's rebalancing at observed depth, and Gârleanu, Pedersen, and Poteshman (2009) justify the residual inventory premium where hedging is imperfect, which deep strikes always are. The bid-offer the model consumes is measured, not assumed.

Every parameter lives in a content-addressed methodology object; synthetic numbers carry their tag and display one band coarser than quoted ones; and one test gates the lane: on the basket where real quotes exist, the synthetic deep put must rarely undercut the quoted ask. The estimator errs toward more displayed risk or it does not run. A quoted market, where eligible, always outranks the model — the synthetic exists so the display never goes blind, and it is never allowed to go first, because realized dynamics plus premia cannot anticipate untraded information the way a live quote can. Where even spot is illiquid, the floor applies.

### 5.4 Severity, and the price of opting out

The severity table `L_i` carries the instrument-class distinctions the Tier-1 schema already draws. Bearer and on-chain self-custody carry no venue credit term at all. Qualified-custodian classes carry low severity even when the custodian's equity hazard is elevated, because client assets sit segregated — COIN and IBKR puts price the holding company, and the table corrects that basis. Exchange-credited balances and derivative margin carry high severity, with one denomination nuance: the FTX estate ultimately repaid dollarized petition-date claims in full, while creditors absorbed the entire crypto-denominated and time-value loss. For an instrument marked at NAV in kind, in-kind severity is the relevant measure, and the record says it is severe.

The floor is the anti-Goodhart parameter. `s_floor` sits at or above the worst decile of all currently priced venue spreads, so that opting out of pricing — or migrating reserves to venues no market can price — never displays better than the worst priced alternative. A credit display that rewarded unpriceability would teach issuers to seek darkness, and would be worse than none.

### 5.5 Anonymity with a score

Class-level weights leak funding-venue choices, and some managers will refuse even that. The same enclave that attests the reserve packet resolves the conflict: holding the weight vector privately, it ingests the public hazard vector and severity table and attests the inner product — a single verified VCS — plus a venue-concentration index (a Herfindahl over the weights), so that a single-venue book cannot display like a diversified one with equal weighted hazard. The disclosure ladder descends in three rungs: publish Tier-1 weights, and anyone recomputes the spread; keep the weights private, and the enclave attests the spread and the concentration; decline both, and the floor applies to the full NAV. The trader's anonymity and the holder's credit visibility stop being a trade-off. The portfolio stays private; the risk statistic does not.

### 5.6 Where it runs

Nothing binds consensus to an options market. The NAVCoin protocol separates deterministic validity checks from observation of external state, which runs through a quorum of registered attestors with tolerance-band comparison — and option quotes are external state of exactly that kind. The VCS is produced in that lane: attestors independently pull eligible quotes, compute under the published methodology, and finalize a per-epoch credit packet, with tolerance applied to the computed hazards rather than the raw quotes. Because every input is public and the method is content-addressed, any third party can recompute the number without trusting anyone; the quorum publishes the figure, it does not make it true. One commitment holds throughout: no slashing condition, halt trigger, or validity rule ever binds to the VCS. Markets can be manipulated; validity rules must not be. The display is informational, which is also what keeps it cheap to defend (Section 8).

## 6. November 2022, replayed

Hold the machinery against the canonical counterparty catastrophe: a hypothetical NAVCoin running the era's signature trade — cash-and-carry with the short leg margined on FTX — with Tier-1 disclosure and the credit display live. Prices and dates are approximate but well documented.

| Date (2022) | Event | What the display reads |
|---|---|---|
| Since inception | — | Tier-1 weights show ~45% *derivative margin @ FTX*. The registry shows FTT has no independent options market, so the bucket carries the floor spread and an "unpriced" tag from day one — a standing, visible penalty in calm markets, before any news. |
| Nov 2 | CoinDesk publishes Alameda's balance sheet: ~$14.6B of assets dominated by FTT and SOL against ~$7.4B of loans | The leak is an involuntary disclosure of the counterparty's affiliate — the self-collateralization flag of Section 4, surfaced by journalism instead of schema. The synthetic estimator begins climbing as FTT's realized measures absorb the repricing. FTT ≈ $25. |
| Nov 6 | Binance announces it will liquidate ~$580M of FTT; Alameda's CEO publicly offers to buy it all at $22 | FTT −12% intraday. The candle loads the realized-jump and downside-semivariance inputs within the epoch; a public defense of a fixed level in the venue's own collateral token is the textbook distress signature. |
| Nov 7 | FTT pinned near $22; ~$5B of weekend withdrawals from FTX | The synthetic estimator reads a pinned price against swelling downside-jump intensity as rising, not falling, hazard. Deep amber, ~36 hours before the halt. |
| Nov 8 | $22 breaks; FTT collapses toward $4–5 intraday; FTX halts withdrawals that afternoon | The barrier breach sends the hazard vertical in the morning — hours before the halt — while redemption-at-NAV machinery is still live. |
| Nov 9–11 | Binance walks after diligence; Chapter 11 on Nov 11 | FTT ≈ $3–4, roughly −94% on the month: a zero-recovery claim pricing its default exactly as Section 4 predicts. |

Three things follow. The options-based signal degrades to the synthetic estimator in this case, because FTT had no independent options market — and the framework displays exactly that absence as a standing penalty, which is the deepest lesson of the episode: a claim the market cannot price is itself credit information. The market-implied lead time was short — days from the Binance announcement, hours from the barrier break — enough for epoch-cadence machinery and a live redemption window, far too short for a quarterly attestation to notice at all. And the lead time is not the main contribution. The display showed the exposure all year: a holder knew from inception that 45% of NAV sat as margin credit to an exchange whose claim no market would price, and could decompose the celebrated yield into a funding rate, a venue credit spread, and a residual. "Market-neutral basis at 15%" does not survive that panel. Verification cannot catch a lying venue; the display ensures nobody holds it unknowingly, or cheaply.

## 7. Why this is worth building

The economics of disclosure favor the design. Grossman (1981) and Milgrom (1981) prove the unraveling result: when disclosure is verifiable and cheap, buyers read silence as concealment of the worst type, so quality discloses to separate itself and non-disclosure pools at the bottom. The precondition that always failed in crypto is verifiability — anyone could *claim* low venue concentration, so claims were noise and silence was free. Attested packets supply the verifiability; the floor spread operationalizes the skeptical belief, pricing silence as the worst decile rather than merely suspecting it. Diamond and Verrecchia (1991) add the carrot: committed disclosure lowers information asymmetry and the cost of capital. A verified-low-VCS coin funds at a tighter discount to NAV and clears integrator gates an opaque competitor cannot.

The display also decomposes yield. With attested venue weights and market-implied hazards, a NAVCoin's return separates into a funding rate, a priced venue credit spread, and a residual that deserves the name alpha. The fund running CME bitcoin futures basis shows a thin spread; the fund running HYPE perp basis shows a thick one; capital chooses with the risk printed on the label, which is what a risk curve is for. The 2021-vintage pitch — venue credit booked as genius — becomes arithmetic anyone can check.

Most broadly, a portfolio token carrying a live, recomputable credit spread is collateral that prices itself. Lending desks can haircut by VCS instead of by reputation; structured products can gate on it; indices can weight by it; the protocol's own defense and integrator machinery can consume it as a sizing input. An off-chain fund reports counterparty exposure quarterly, in a PDF, to its own investors. An on-chain fund can report it every epoch, to everyone, attested — not the elimination of counterparty risk, which nothing achieves, but its conversion from a private fact into a market price. That conversion is what makes the NAVCoin a better primitive for on-chain portfolio finance.

One question stays open, and it is demand-side: whether a displayed floor spread costs an opaque issuer real flow, when the richest advertised yields will always come from whoever stays dark. The bet is that capital shown "verified 9%" beside "unpriced 15%" allocates differently after 2022 than it did before. If that bet fails, no disclosure architecture survives it.

## 8. Limits

The VCS is a risk-neutral, premium-laden quantity, not a physical default probability, and jump-to-default is the state options price worst in advance and reprice fastest in motion: the signal can sleep until it gaps. Deep books on venue tokens are thin, so manipulation is the first attack to consider; the defenses are the informational-only commitment (no hard payoff to manipulate toward), epoch-long TWAPs across trimmed multi-venue medians, the eligibility gates, and coarse display bands — and the analysis must be redone from scratch the moment any economic consequence is wired to the number. Reference claims carry basis: holding-company puts overstate custodial risk where client assets sit segregated and understate margin-account liquidation mechanics, while token puts conflate regulatory and insolvency jumps; the severity table and estimator tags carry the corrections, imperfectly. The synthetic lane trades manipulation risk for model risk — a painted book and a mis-specified surface fail differently and need different audits. Coverage is thinnest where it matters most (Binance) and partially entangled where it is best (HYPE options collateralized through the venue's own bridge). Reflexivity is disclosed, not removed: for self-collateralized venues the display participates in the run it predicts, and anyone wiring it into automated de-risking is building an accelerant. And a spread is not recourse. It prices the loss; identity registries, performance bonds, and courts recover it.

## 9. Build path

Two content-addressed objects and one packet, all reusing machinery the protocol already runs. The `credit_methodology` object holds the reference-claim registry with independence attestations and barriers, the synthetic parameter block (realized-measure windows, the premium-transfer basket, friction coefficients, conservatism thresholds), the eligibility gates, the severity table, the floor rule, and the display bands. The per-epoch `credit_packet` holds quote-snapshot commitments, per-class hazards with estimator tags, the VCS, the unpriced share, the concentration index, and the methodology hash. Phase A requires no protocol change: an open reference implementation over existing Tier-1 packets and public quotes, with a full replay of November 2022 against archived market data as the acceptance test. Phase B routes credit packets through the attestor lane. Phase C — whether gating, facility sizing, or collateral systems consume the number — waits on manipulation economics measured with Phase A data.

---

## References

Almgren, R., and N. Chriss. 2001. "Optimal Execution of Portfolio Transactions." *Journal of Risk* 3 (2): 5–39.

Andersen, T. G., T. Bollerslev, F. X. Diebold, and P. Labys. 2003. "Modeling and Forecasting Realized Volatility." *Econometrica* 71 (2): 579–625.

Bakshi, G., N. Kapadia, and D. Madan. 2003. "Stock Return Characteristics, Skew Laws, and the Differential Pricing of Individual Equity Options." *Review of Financial Studies* 16 (1): 101–143.

Barndorff-Nielsen, O. E., and N. Shephard. 2006. "Econometrics of Testing for Jumps in Financial Economics Using Bipower Variation." *Journal of Financial Econometrics* 4 (1): 1–30.

Barndorff-Nielsen, O. E., S. Kinnebrock, and N. Shephard. 2010. "Measuring Downside Risk: Realised Semivariance." In *Volatility and Time Series Econometrics: Essays in Honor of Robert F. Engle*, edited by T. Bollerslev, J. Russell, and M. Watson. Oxford: Oxford University Press.

Black, F. 1976. "Studies of Stock Price Volatility Changes." *Proceedings of the American Statistical Association, Business and Economic Statistics Section*: 177–181.

Black, F., and J. C. Cox. 1976. "Valuing Corporate Securities: Some Effects of Bond Indenture Provisions." *Journal of Finance* 31 (2): 351–367.

Black, F., and M. Scholes. 1973. "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy* 81 (3): 637–654.

Bollerslev, T., G. Tauchen, and H. Zhou. 2009. "Expected Stock Returns and Variance Risk Premia." *Review of Financial Studies* 22 (11): 4463–4492.

Carr, P., and L. Wu. 2009. "Variance Risk Premiums." *Review of Financial Studies* 22 (3): 1311–1341.

Carr, P., and L. Wu. 2011. "A Simple Robust Link Between American Puts and Credit Protection." *Review of Financial Studies* 24 (2): 473–505.

Christensen, B. J., and N. R. Prabhala. 1998. "The Relation between Implied and Realized Volatility." *Journal of Financial Economics* 50 (2): 125–150.

Cong, L. W., Y. Li, and N. Wang. 2021. "Tokenomics: Dynamic Adoption and Valuation." *Review of Financial Studies* 34 (3): 1105–1155.

Corsi, F. 2009. "A Simple Approximate Long-Memory Model of Realized Volatility." *Journal of Financial Econometrics* 7 (2): 174–196.

Cremers, M., J. Driessen, and P. Maenhout. 2008. "Explaining the Level of Credit Spreads: Option-Implied Jump Risk Premia in a Firm Value Model." *Review of Financial Studies* 21 (5): 2209–2242.

Culp, C. L., Y. Nozawa, and P. Veronesi. 2018. "Option-Based Credit Spreads." *American Economic Review* 108 (2): 454–488.

Diamond, D. W., and R. E. Verrecchia. 1991. "Disclosure, Liquidity, and the Cost of Capital." *Journal of Finance* 46 (4): 1325–1359.

Finger, C. C., V. Finkelstein, G. Pan, J.-P. Lardy, T. Ta, and J. Tierney. 2002. *CreditGrades Technical Document.* RiskMetrics Group.

Gârleanu, N., L. H. Pedersen, and A. M. Poteshman. 2009. "Demand-Based Option Pricing." *Review of Financial Studies* 22 (10): 4259–4299.

Glosten, L. R., R. Jagannathan, and D. E. Runkle. 1993. "On the Relation between the Expected Value and the Volatility of the Nominal Excess Return on Stocks." *Journal of Finance* 48 (5): 1779–1801.

Grossman, S. J. 1981. "The Informational Role of Warranties and Private Disclosure about Product Quality." *Journal of Law and Economics* 24 (3): 461–483.

Hull, J., I. Nelken, and A. White. 2004. "Merton's Model, Credit Risk, and Volatility Skews." *Journal of Credit Risk* 1 (1): 3–27.

Kozhan, R., A. Neuberger, and P. Schneider. 2013. "The Skew Risk Premium in the Equity Index Market." *Review of Financial Studies* 26 (9): 2174–2203.

Leland, H. E. 1985. "Option Pricing and Replication with Transactions Costs." *Journal of Finance* 40 (5): 1283–1301.

Leland, H. E. 1994. "Corporate Debt Value, Bond Covenants, and Optimal Capital Structure." *Journal of Finance* 49 (4): 1213–1252.

Merton, R. C. 1974. "On the Pricing of Corporate Debt: The Risk Structure of Interest Rates." *Journal of Finance* 29 (2): 449–470.

Milgrom, P. R. 1981. "Good News and Bad News: Representation Theorems and Applications." *Bell Journal of Economics* 12 (2): 380–391.

Neuberger, A. 2012. "Realized Skewness." *Review of Financial Studies* 25 (11): 3423–3455.

Patton, A. J., and K. Sheppard. 2015. "Good Volatility, Bad Volatility: Signed Jumps and the Persistence of Volatility." *Review of Economics and Statistics* 97 (3): 683–697.

Xing, Y., X. Zhang, and R. Zhao. 2010. "What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns?" *Journal of Financial and Quantitative Analysis* 45 (3): 641–662.

*Market-structure facts in §5.1 (Deribit's July 2025 delisting of BNB options; HYPE options on Derive since November 2025; PURR and BNC listings) reflect public announcements as of June 2026 and should be re-verified at implementation, as the reference-claim registry is designed to be updated.*