---
title: "The NAVCoin Proposal"
date: 2026-06-10T00:00:00Z
summary: "A NAVCoin is a token whose unit value tracks the machine-verified net asset value of a reserve portfolio — not a peg. The settlement rail already runs on the Post Fiat devnet; this post proposes the verification layer, the privacy model, and the cross-chain mechanics, and is published before implementation so the design can be attacked first."
categories:
  - PostFiat Research
tags:
  - NAVCoin
  - Proof of Reserves
  - TEE
  - RWA
  - PostFiat
---

This is a proposal, published deliberately before implementation. The settlement rail it builds on already runs on the Post Fiat devnet; the verification layer described here does not exist yet. We want the design criticized while changing it is still cheap. If you can break an assumption below, that is the contribution we are asking for.

## What a NAVCoin is, in plain terms

A NAVCoin is a token whose unit value tracks the marked net asset value of a reserve portfolio, where the marking is verified by machines on a fixed cadence rather than asserted by the issuer and sampled occasionally by accountants.

It is not a stablecoin and does not pretend to be one. If the reserves decline, the NAV declines. The promise is narrower and harder than "always worth a dollar": *the current backing, its liabilities, the valuation policy, and the redemption claim are explicit, hashed, machine-checked, fresh, and mechanically tied to the token's supply.* A NAV break is survivable by design. A false packet, a stale packet, or a blocked redemption is the real failure — so those are the things the protocol is built to prevent.

One limit belongs in the definition, not a footnote: machine verification proves what venues *reported*, not what is *true*. A lying broker or a quietly insolvent exchange passes every cryptographic check. The design treats that residual as a first-class problem — it is why the proposal has both a verification layer (below) and a commitment layer (after it), and why the limits section near the end is load-bearing rather than legal boilerplate.

## The economic gap it targets

Today's on-chain money sits at two unsatisfying poles.

| | Volatility | Yield to holder | Credit risk |
|---|---|---|---|
| Bitcoin (via IBIT) | 52% implied (30-day IV, 2026-06-05) | none | none (bearer) |
| Stablecoins | ~0% | structurally zero | uncapped, unobservable |
| Macro-portfolio NAV | 5.6% realized (2022–2026) | passes through | bounded by verification freshness |

The numbers are checkable, not vibes. Bitcoin's 30-day implied volatility via IBIT options was 52.3% on June 5, 2026 (AlphaQuery), and typically ranges 35–90%. The Barclay Global Macro Index — a public table of monthly hedge fund returns — shows an annualized standard deviation of 5.6% with a 9.0% compound annual return over January 2022 through May 2026 (53 monthly observations × √12; compute it yourself from the published table). Diversified macro money runs at roughly one-ninth the volatility of bitcoin while yielding like an asset.

Stablecoins solved volatility by introducing an issuer balance sheet you cannot see into. The interest on the float structurally accrues to the issuer, not the holder: Tether's reported profits (roughly $13B in 2024 — float interest plus mark-to-market gains on gold and bitcoin bought with retained earnings) belong entirely to the issuer, while the holder of the liability earns zero. And the credit risk is the worst kind: small in expectation, total in the tail, and unobservable while it forms.

A 5-to-6-vol instrument is a dramatically better medium of exchange than a 50-vol one — spreads quote tighter, mental accounting horizons stretch from minutes to weeks, merchants don't need instant conversion — and unlike a stablecoin it pays its holder for holding it. What has kept portfolio-backed tokens from filling this gap is not finance; it is verification. Nobody has had a way to hold a claim on a managed reserve portfolio without trusting the manager's self-reporting. That is the specific problem this proposal attacks.

## The status quo: even best practice is a PDF

**Tether** publishes quarterly attestations — point-in-time accountant reports, not audits. The historical record justifies skepticism about self-reported backing: in 2021 the CFTC fined Tether $41M for misstatements about its reserves during 2016–2018. Whatever its reserves are today, the verification regime is: trust, quarterly, in arrears.

**Paxos** is the honest benchmark, because it is roughly the best the current model can do: NYDFS-regulated trust structure, monthly third-party attestations, allocated gold in professional vaults for PAXG. And even this leaves the structural gaps untouched: the attestation is a point-in-time sample, published on human cadence; nothing connects it mechanically to the token contract — minting is constrained by the issuer's keys and the issuer's conscience, not by the attestation; and a holder cannot machine-verify anything. The exchange-style Merkle proof-of-reserves programs (Kraken, Binance) added user-side liability inclusion proofs, which is genuine progress on one axis, but remain point-in-time and silent on liability completeness.

The pattern across all of it: **the attestation is testimony about the system, never a component of it.** It can't halt a mint, can't cap supply, can't go stale in a way the token notices.

{{< navcoin-status-diagram >}}

## What already runs on the devnet

The reason this proposal lives here rather than on a whiteboard: Post Fiat's L1 already has a native NAV settlement rail, running on the devnet today. Seven native transaction types (`nav_asset_register`, `nav_reserve_submit`, `nav_reserve_challenge`, `nav_epoch_finalize`, `nav_mint_at_nav`, `nav_redeem_at_nav`, `nav_halt`) and three ledger objects implement the full lifecycle: register an asset, submit an epoch reserve packet, finalize it, mint only against the finalized supply cap, trade on the native order book, redeem at NAV with a deterministic on-chain claim. Consensus enforces the arithmetic invariant — verified net assets must equal circulating supply times NAV per unit, exactly — along with epoch monotonicity and halt behavior, and an end-to-end test demonstrates the whole sequence with all validators converging on identical state.

What the devnet rail does *not* yet do is the part that matters most: prove that the off-chain reserve inputs are true. The current proof profile is, by its own name, a placeholder. Everything below is the plan for replacing it.

## The verification layer

### Proof profiles are protocol objects, not labels

Each NAV asset registers against a **proof profile**: a governance-versioned ledger object specifying the verifier kind, the root of trust (e.g., a pinned TEE platform root certificate), the measurement policy identifying the exact fetcher code allowed to produce evidence, freshness bounds, the disclosure tier, and challenge parameters. "What counts as proof" becomes a protocol decision with an audit trail — not a string in a marketing deck.

### Evidence is produced by measured code

For reserves held at venues with authenticated APIs — a broker like IBKR, an exchange like Binance, a perp venue like Hyperliquid — a fetcher runs inside a trusted execution environment holding read-only API keys. It queries the venue, applies the registered valuation policy (marks, haircuts, margin and liability treatment), and emits a hardware attestation document binding three things together: the platform signature chain, the measurement of the exact code that ran, and the hash of the policy it enforced. The attestation travels with a published evidence bundle. For fully public sources — on-chain wallets, address-indexed venue state — no TEE is needed at all: validators can observe the source independently.

### Verification is a validity rule, not a vote

This is the design decision we expect the most pushback on, so here is the reasoning. Verifying an attestation document is deterministic cryptography: check the signature chain against the pinned root, check the measurement against the profile, check the policy binding, recompute the arithmetic, check freshness stamps. Every validator can run the identical check as part of transaction execution — so `nav_epoch_finalize` is simply **invalid** if the evidence fails. There is no oracle committee, no attestation quorum, no token-weighted truth. A vote layered on a deterministic check adds signatures, not security.

Voting survives in exactly two places, because physics requires it: observation of *external* state (consensus nodes cannot do live I/O, so public-source profiles use redundant independent fetches), and adjudication of bonded challenges, which is judgment by definition.

One subtlety keeps the determinism claim honest. Attestation verification has inputs that change over time — platform root certificates rotate, TCB security versions get revoked after vulnerabilities. If validators consulted vendor infrastructure live, two nodes checking seconds apart could disagree, and consensus would split. So revocation state, TCB minimums, and pinned roots are themselves **ledger state**, updated only through governance transactions: verification is a pure function of the transaction and the ledger, and never touches the outside world. The cost is honest too — a revocation takes effect at governance speed, not vendor speed, which is a parameter to tune, not an accident to discover.

### Freshness is enforced, with a deadman switch

Every packet carries snapshot timestamps checked against ledger time. If a NAV asset's finalized packet exceeds its profile's maximum age, mint and redeem fail closed automatically. An issuer who stops proving doesn't get a stale green light; the asset halts itself. Staleness becomes a protocol fact rather than an operator courtesy.

### Challenges are bonded and have teeth

Anyone may challenge a packet by posting a bond. A challenge escalates disclosure to a designated verifier set under the profile's rules, whose verdict is public even when the underlying data is not. Frivolous challenges forfeit the bond; upheld challenges halt the asset and pay the challenger. (The devnet's current challenge path is unauthenticated and unbonded — a known defect this proposal fixes.)

## Privacy: publish the computation, not the portfolio

No serious manager will dox positions, so position-level disclosure is optional by design. The TEE inverts the problem: the measured code saw the full detail, applied the public policy, and attested to the aggregate — verifiers check *what code computed the number*, not the underlying rows.

Disclosure is a per-asset, published, immutable tier, so the market prices opacity instead of the protocol forbidding it:

- **Tier 0 — transparent.** Full evidence bundle public.
- **Tier 1 — class-level.** Post-haircut aggregates by instrument and venue class: "spot metals; futures exposure net of margin, 15% haircut." The required minimum for anything marketed as *backed* — because a futures position is not a vault bar, and a standard that let those look identical would be worse than no standard.
- **Tier 2 — aggregate-only.** One number, the policy hash, and the attestation. Appropriate for NAV-tracked funds whose strategy is the product.
- **Tier 3 — attestor-disclosed.** Full detail revealed only to named attestors; their signatures are public, the data never is.

One refinement: a backed-1:1 product never needed to publish its reserve level, only the inequality. So coverage can be attested as a **banded ratio** ("≥ 1.00") computed inside the enclave — solvency without a P&L feed. A floating NAV product necessarily publishes NAV per unit, because that *is* its price.

## Interoperation: liquidity where it lives, truth where it's enforced

Realistically, NAVCoins will trade where liquidity already is — Uniswap, Jupiter — and the proposal embraces that rather than fighting it. The issuer mints natively on multiple chains under a **declared supply perimeter**: every contract, chain, and bridge enumerated in the registry. Cross-chain movement is burn-here-mint-there under issuer keys (the model Circle proved with CCTP — no wrapped assets, no third-party bridge custody, no new trust class). The verification layer observes supply across the entire perimeter via host-chain light-client proofs, and coverage is computed against the *global* total. Supply observed outside the declared perimeter is a challengeable, status-degrading event.

The Post Fiat instance occupies a specific role in this topology: it is the **reference instance** — the only copy whose mint is unconditionally consensus-gated by fresh verified reserves and which halts itself on staleness. Convenience forms trade on the big venues; the fail-closed form lives here. Two venue properties follow. First, redemption at NAV is native protocol machinery on Post Fiat, so arbitrage tethers the local price to NAV the way ETF primary markets discipline secondary prices — the venue where you can redeem is the venue where price discovery snaps to truth. Second, the internal order book can host direct NAV-to-NAV crosses (a gold-NAV against a silver-NAV) with both legs verified under the same standard and live premium/discount-to-NAV display — a pair structure that two-hop AMM routing through USDC does not replicate.

## The commitment layer: pricing the risks verification can't reach

Verification proves reserves existed at a venue at a time. It cannot prove the venue is solvent, that the issuer won't abscond, or that anyone will defend the token's price. Those are behavioral risks, and the answer to behavioral risk is not more cryptography — it is commitment devices whose breach is machine-detectable. Three of them, each consuming the deterministic facts the verification layer already emits:

**Verifiable legal identity.** Issuers register a verifiable legal-entity credential (GLEIF's vLEI standard exists for precisely this), verified domains — the same mechanism this network's validators already use — and hashes of the governing legal documents: trust indenture, custody agreements, redemption terms. None of this prevents fraud. What it does is convert "who do I sue, in which jurisdiction, under which terms" from a research project into a registry lookup, and make any quiet amendment of legal terms a visible hash change. A deterrent layer that operates at jurisdiction speed, labeled as such.

**An issuer performance bond.** The issuer locks first-loss capital in contracts on the chains where the asset trades, slashed by facts the registry already produces: an upheld fraud challenge, a redemption default past its deadline, staleness beyond the profile's tolerance. The slashing oracle is the same threshold-signed status feed integrators consume — no new trust machinery. Sized honestly, a bond is a deductible, not insurance: it cannot cover total loss on a large asset, but it prices the issuer's own confidence, bounds small failures, and makes absconding strictly negative-sum up to the bond. It is also the one reserve class that needs no TEE at all — on-chain, tier-0 transparent by construction.

**A standing NAV-defense facility.** When a backed token trades below its verified NAV, buying it back is not a peg defense — it is profitable arbitrage by construction: units retired at a discount raise NAV per remaining unit. Closed-end funds carry persistent discounts because NAV is unverifiable, redemption is gated, and buybacks are discretionary; this design has verified NAV and native redemption, so it can make the buyback *mandatory*. The facility is disclosed dry powder with a published mandate: a deviation beyond a threshold for a sustained window — measured by the same external-observation lane that watches supply — emits an on-chain margin call; the facility must demonstrate deployment by a deadline, and deployment is itself verifiable because the fills execute on public venues. Failure to deploy is an on-chain fact that degrades the asset's status and slashes the bond. The industry already knows the discretionary version of this play, at both ends of the quality spectrum. Ethena bought its own token off an exchange wick when USDe traded far below a dollar — effective, but a voluntary act nobody could have compelled. And Tether has, for years, recycled float profits into hard assets — gold and bitcoin, some of it on-chain — that function as an informal, entity-owned buffer that *could* defend the peg if it broke. Both are the right instinct expressed as managerial discretion. The proposal's contribution is making the buffer explicit, pre-committed, observable, and obligatory, with defense depth published as a gateable metric alongside coverage ratio — the difference between "the issuer probably has dry powder somewhere" and a mandate with a deadline and a slashing condition.

None of these eliminate the tail. A venue can still be insolvent; a determined fraud still costs someone money. The commitment layer re-prices the tail: identity makes pursuit cheap, the bond makes small defection unprofitable, the facility makes discounts self-closing — and every breach becomes a machine-detectable event in the registry rather than a discovery in bankruptcy court.

## Economics: who gets paid, and who doesn't

Post Fiat inherits the XRPL position that validation is never compensated, and this proposal keeps it intact: the consensus-native verification checks are validation, and the fees on NAV transactions burn like every other fee. No payment attaches to consensus power — that line is what prevents proof-of-reserves from becoming a validator rent market.

What is paid is **extra-consensus service work**: operating TEE fetchers for issuers, performing independent observations for public-source profiles, adjudicating bonded challenges, serving evidence bundles. These are opt-in, per-actor, measurable services open to anyone — payment attaches to verifiable service delivery, never to validation. Validators are well-positioned to compete for this work precisely because the network already publishes scored evidence of their independence and reliability, which is what an issuer shopping for verification infrastructure wants to buy. The chain's own benefit is fee burn on every epoch, mint, redemption, and cross-NAV trade.

## What this does not solve

Stated plainly, because a verification proposal that oversells verification refutes itself:

- **Source honesty.** If a broker's API lies, or a venue misreports internally-credited balances, machine verification faithfully confirms a false world. TEEs bound *fetcher and transport* honesty, not *venue* honesty. The mitigation is source diversity and instrument-class visibility, not cryptography.
- **Completeness.** No system can prove the absence of undisclosed liabilities held elsewhere. The perimeter, the policy, and tier-3 attestors manage this; nothing eliminates it.
- **Platform trust.** TEE attestation roots trust in the hardware vendor, and TEE side-channel attacks are an active research area. Profiles pin specific platforms and TCB minimums so this exposure is explicit and revocable rather than silent.
- **Instruments are not bars.** Futures-backed exposure carries basis, roll, and liquidation risk that allocated custody does not. The schema's job is to keep that difference visible, not to flatten it.
- **Legal claim.** An on-chain redemption claim is not a court judgment. The redemption-settlement loop (receipts, deadlines, auto-halt on default) narrows but does not close the gap between cryptographic and legal recourse.

## Poke holes

The build sequence is: verification interface and lifecycle fixes against devnet-native reserves first; one public-source profile (validator multi-fetch) second; the TEE lane for authenticated venues third; host-chain supply observation and the external-asset registry after that. Each phase ships with replayable evidence, in the same format as our prior devnet work.

Before any of that starts, this document is the attack surface. The assumptions we most want stress-tested: that epoch-cadence verification is fresh enough to matter; that banded coverage attestation leaks little enough for real managers; that the bonded-challenge game is stable (neither griefable nor capturable); and that demand-side enforcement — integrators gating on coverage status — is strong enough discipline for instances on chains we don't control. If one of those fails, better it fails in review.
