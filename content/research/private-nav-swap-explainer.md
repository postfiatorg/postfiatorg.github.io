---
title: "Private NAV Swaps, Explained From Zero: What the Product Is and How It Becomes Real"
date: 2026-07-10T00:00:00Z
draft: false
url: "/research/private-nav-swap-explainer/"
summary: "A ground-up explainer of the private NAV swap product: what wrapped pfUSDC actually is, how NAVCoins are priced on PFTL and represented on Uniswap, what a transparent and a private transaction look like step by step, how the counterfeit problem was found and fixed, why Orchard transactions need warm-ups, how RFQ quoting fits a wallet, how NAV and TVL move when money subscribes, and an honest ledger of what is and is not implemented."
description: "Plain-language architecture and product walkthrough for private NAV-based asset swaps on Post Fiat: pfUSDC, NAVCoins, Uniswap representation, privacy boundaries, counterfeit resistance, latency, RFQs, and fund accounting."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - pfUSDC
  - Privacy
  - Uniswap
  - PFTL
  - RFQ
  - Post Fiat
---

*Part of the NAVCoin series. This post is deliberately written from zero: if
you have lost the thread of what the product does, start here. It reflects
the system as it exists on 2026-07-10 — including what is proven, what is
built but not yet hardened, and what is still only a design.*

## The one-paragraph version

The product lets a user turn real USDC into a **NAVCoin** — a token whose
value tracks a machine-verified reserve portfolio — **swap it privately**
(nobody watching the chain learns the asset, amount, counterparty, or
price of the trade itself), and exit either by **redeeming at NAV** for
USDC or by **selling on a Uniswap pool**. Every boundary where value
enters or leaves the system is proven and countable; the trade in the
middle is shielded. That combination — private where privacy matters,
proven everywhere else — is the entire point.

There are two chains involved and one ledger of record:

| Layer | Where | What lives there |
| --- | --- | --- |
| Cash custody | Arbitrum One | Real USDC in a bridge vault |
| Ledger of record | PFTL (Post Fiat L1) | pfUSDC receipts, NAVCoin supply, NAV epochs, the shielded pool |
| Trading venue | Ethereum mainnet | Wrapped a651 ERC-20 + Uniswap v4 a651/USDC pool |

<figure><img src="/research/private-nav-swap/d1-system-map.svg" alt="System map: Arbitrum One holds real USDC in the ERC20BridgeVault; PFTL is the ledger of record holding pfUSDC receipts, NAV epochs, the Asset Orchard shielded pool, and the a651 supply ledger; Ethereum mainnet is the trading venue with the wrapped a651 ERC-20 and the Uniswap v4 pool banded around NAV."></figure>

---

## 1. Wrapped pfUSDC: how it works, and the Arbitrum logic

pfUSDC is **not** a generic wrapped dollar. It is a *cash receipt* on PFTL
that exists only when the chain can count the dollars behind it (see
[pfUSDC: Source-Labeled Cash Receipts](/blog/pfusdc/)).

**Deposit path (USDC → pfUSDC):**

1. A user deposits native USDC into the `ERC20BridgeVault` on Arbitrum One
   (deployed in the I-1 ceremony).
2. Deposit evidence is submitted to PFTL: source chain id (42161), vault
   address, token, depositor, amount, transaction hash, block hash, log
   index, and confirmation depth.
3. **Consensus admission verifies the claim, not just a signature.** Since
   the Stage-2 bridge-verification deploy, PFTL validators only admit the
   mint if registered observers confirm, under quorum rules, that the
   source transaction actually exists with receipt status 1. A deposit
   citing a block that does not exist is rejected in consensus.
4. pfUSDC is minted 1:1 against the counted deposit.

**Withdrawal path (pfUSDC → USDC):**

1. The user burns pfUSDC on PFTL, producing a redemption record.
2. A withdrawal verifier authorizes the Arbitrum vault to release USDC to
   the recipient. (Today this verifier is a 1-of-1 key — a known single
   point of failure with a threshold upgrade staged; see Section 9.)
3. Vault balance and PFTL issued supply must reconcile atom-for-atom; a
   standing report-only reserve watch records the conservation deltas.

The invariant to remember: **pfUSDC issued supply equals vault reserves,
and both sides of every crossing are independently checkable.**

---

## 2. NAVCoins: NAV calculation on PFTL, representation on Uniswap

A NAVCoin (the first is **a651**) is a floating-value token: one unit is
worth the net asset value of its reserve portfolio divided by units
outstanding. It is not a peg and there is no market maker promise — the
value claim is a *computation the chain performs* (see
[The NAVCoin Proposal](/blog/navcoin-proposal/)).

**NAV calculation on PFTL** runs on a reserve-packet lifecycle:

1. `nav_reserve_submit` — an attested packet reports the portfolio:
   holdings, valuation, epoch number, and a content hash.
2. Observation and challenge — the attestor registry and quorum rules
   (the same observation lane that was live-proven against a $275M
   Hyperliquid vault) validate the packet; challenges can block it.
3. `nav_epoch_finalize` — consensus records the finalized epoch:
   `(epoch, nav_per_unit, circulating_supply, reserve_packet_hash)`.
   This finalized `nav_per_unit` is **the** canonical price until the next
   epoch finalizes. `nav_halt` can freeze the asset if attestation fails.

Everything that prices "at NAV" — primary subscriptions, redemptions, and
(by default) private swaps — prices against a **finalized, non-stale
epoch**, referenced by hash. There is one canonical NAV, computed on PFTL,
no matter how many venues trade the token (see
[One Portfolio, Many Access Venues](/blog/navcoin-ethereum/)).

**Representation on Uniswap:** a651 also exists as a wrapped ERC-20 on
Ethereum mainnet (`0x1e55…b62e`), paired against USDC in a Uniswap v4 pool
(0.05% fee tier). The liquidity position is deliberately concentrated in a
**narrow tick band around NAV** — the pool is an *access venue*, not a
price oracle. Pool price can wander; NAV cannot. When they diverge, the
primary mint/redeem rail at NAV is the arbitrage anchor that pulls the
pool back. The pool was seeded against a recorded pricing epoch and
reserve packet hash, so even the venue's initial price is traceable to a
proven NAV.

Honest caveat: today, supply parity between PFTL-native a651 and the
mainnet wrapped float is issuer-attested (operator inventory seeded the
pool), not yet cryptographically proven end-to-end. The bridge
verification plan's later stages extend proof coverage there.

---

## 3. End-to-end: one transparent transaction, one private transaction

### The transparent version (proven end-to-end in June's OTC MVP)

**User story — Priya, transparent subscriber.** Priya wants NAV exposure
and does not care who sees it.

1. Priya sends 1,000 USDC to the Arbitrum vault. Observers confirm the
   deposit; PFTL mints her 1,000 pfUSDC. *(Public: her address, amount.)*
2. She submits a transparent NAVSwap: pfUSDC → a651 at the finalized epoch
   NAV. If NAV is 8.20, she receives ~121.95 a651 units. Supply and
   reserves update atomically in the same state transition.
3. Months later she redeems at the then-current NAV, burns her a651,
   receives pfUSDC, burns that, and the vault releases USDC on Arbitrum.

Every step is visible on the PFTL ledger. TVL rose by exactly her deposit
and fell by exactly her withdrawal — that arithmetic was the proven
centerpiece of the [OTC MVP](/blog/navcoin-otc-mvp-proven/).

### The private version (proven end-to-end in run R82, July 2026)

**User story — Bob, private swapper.** Bob is a fund that does not want
the market to see it building a position.

1. **Public funding:** USDC → pfUSDC, same as Priya. *(Entry boundary is
   visible: asset and amount.)*
2. **Shielded ingress:** Bob deposits pfUSDC into the Asset Orchard
   shielded pool, receiving private notes.
3. **Private swap:** Bob's pfUSDC notes and a counterparty's a651 notes
   are spent into one jointly-proven transaction. The zero-knowledge proof
   enforces conservation — nothing created, nothing destroyed — while
   revealing **no asset identifiers, no amounts, no owners, no price** as
   public action fields.
4. **Private egress:** Bob (or the counterparty) exits the shielded pool.
   The exit reveals a nullifier, an anchor, and a proof — not the history
   of the notes.
5. **Public exit:** two doors, on two different chains:
   - **Redeem at NAV:** burn a651 → pfUSDC → USDC released on
     **Arbitrum**. Fair value, slower, reveals exiting asset and amount.
   - **Uniswap exit:** bridge a651 out and sell into the mainnet pool at
     the venue price, bounded by a NAV band and slippage limit.

What the chain-watcher learns: something entered (asset, amount), and
something exited (asset, amount, destination). What they cannot learn:
what was swapped for what, at what price, between whom. We do **not**
claim amount anonymity at the public boundaries, and we do not claim
timing-correlation resistance — a watcher correlating entry and exit
timing can guess. The claim is a private *trade* between visible public
boundaries.

R82, the first fully verified private run, executed all five phases live:
21 PFTL transactions verified, the EVM router receipt verified, all six
validators finishing at the same height and state root, in 534.62 seconds.

<figure><img src="/research/private-nav-swap/d2-transparent-vs-private.svg" alt="Two lanes showing the same journey. Transparent lane: USDC deposit, pfUSDC mint, NAVSwap at epoch NAV, hold a651, redeem at NAV back to USDC, every step visible. Private lane: visible USDC deposit and pfUSDC mint, then a shielded region containing shielded ingress, private swap, and private egress where asset ids, amounts, owners, and price are not revealed, then two visible exits: redeem at NAV on Arbitrum or sell on Uniswap on mainnet."></figure>

---

## 4. The counterfeit problem: what it is, how it was solved

A NAV-based asset dies the moment anyone can create claims that are not
backed. Counterfeiting shows up at three layers here, and each has a
distinct defense:

**Layer 1 — counterfeit cash (the real incident).** During the W6 gate, a
test submitted **fabricated deposit evidence citing a nonexistent Arbitrum
block — and PFTL minted pfUSDC against it.** The admission path checked
that the evidence was *signed*, not that it was *true*. This was a genuine
money-integrity hole, and fixing it consumed a large share of the recent
engineering time — deliberately, because nothing else matters if this is
open. The fix, executed as a staged, gated plan:

- The fabricated receipt became a **permanent negative test vector**
  in-tree; the build fails if admission ever accepts it again.
- Stage 1 added deterministic admission hygiene (structural validity,
  chain-id and vault binding, pure-function checks in consensus).
- Stage 2 — the core fix — moved to **observer-quorum verification**:
  validators admit deposit credits only when registered observers confirm
  the source transaction exists with receipt status 1, under a minimum
  confirmation policy. This was deployed to the six-validator fleet with a
  pinned binary, activated at a governance-set height, and accepted by an
  independent audit gate.
- Crucially, the R82 private-swap proof ran **on top of** the hardened
  admission path — the end-to-end result already includes this fix.

**Layer 2 — counterfeit value inside the shielded pool.** In a private
pool you cannot see balances, so the circuit itself must make
counterfeiting impossible: conservation constraints prove that the value
spent equals the value created across every private action, and
nullifiers prevent the same note from being spent twice. This is a
validity rule, not a vote — an invalid proof is not a bad trade, it is an
unacceptable block.

**Layer 3 — counterfeit supply across the bridge.** The PFTL↔Ethereum
route carries per-route supply caps, per-packet notional caps, and a
replay-verifiable receipt chain: every transition receipt hashes into a
root that an external verifier can recompute. Remaining hardening
(receipt-inclusion proofs, bonded challenges, a reserve deadman, and a
threshold withdrawal verifier) is staged and tracked — see Section 9.

### External validation: Zcash's Orchard incident and the Ironwood turnstile

The industry just ran this exact playbook at billion-dollar scale. In
May 2026, a researcher found a soundness flaw in Zcash's Orchard shielded
pool — an under-constrained scalar-multiplication gadget that could let a
malicious prover pass an invalid proof, meaning counterfeit notes could
in principle have been created invisibly inside the pool. The flaw had
shipped in 2022 and sat undetected for four years. Zcash's answer, the
Ironwood upgrade (NU6.3, activating late July 2026), is instructive: it
**seals the old pool** — no new deposits, no internal circulation — and
forces every exiting coin through a public **turnstile checkpoint**, so
that anyone running a node can verify circulating supply without seeing
any individual transaction. Any theoretical counterfeits are boxed in at
the boundary, because the turnstile refuses to let more value out than
legitimately went in.

Three lessons transfer directly:

1. **Boundary accounting is the containment mechanism.** Zcash is
   retrofitting what this product has by construction: every entry and
   exit of Asset Orchard is already a counted public event, so a circuit
   soundness bug is contained at the pool boundary rather than becoming
   systemic supply inflation.
2. **You cannot prove a negative inside a shielded pool.** Nobody can
   cryptographically confirm that counterfeiting *never* happened in a
   private pool — only bound the damage at the boundary. That is why the
   boundaries must be counted from day one, not added after an incident.
3. **Our circuits share the lineage — and were already patched.** The
   Asset Orchard circuits derive from the same Orchard/Halo2 code family.
   Our [June research note](/blog/orchard-halo2-vulnerability-response/)
   records the dependency-intersection finding and the remediation:
   the patched profile moved to `orchard 0.14.0` / `halo2_gadgets 0.5.0`,
   rejects legacy profile identifiers, and enforces strict proof-size
   reconstruction. The final Ironwood circuit revisions will be
   diff-checked when they ship.

Ironwood also raises the bar: it ships with independent audits and
near-complete **formal verification** of its circuits. That is now table
stakes for any shielded system holding real value, and an independent
audit plus scoped formal verification of the Asset Orchard conservation
and nullifier constraints is a named pre-mainnet requirement on this
product's roadmap.

---

## 5. Wallet warm-ups for Orchard transactions, and the latency work

Shielded transactions are computationally heavy: building and verifying
Halo2 proofs over real circuits (see
[Heavy ZK](/blog/heavy-zk-optimization/)). But the measured story is more
specific — and more fixable — than "ZK is slow":

| Measurement | Time |
| --- | ---: |
| Clean-run end-to-end baseline (Stage 4) | 851–873 s |
| R82 end-to-end | 534.62 s |
| — of which the private swap substep | 343.78 s |
| The same swap on a *warm* proof service | ~12.1–12.25 s |
| Post-warm-path projected end-to-end | ~203 s (inference, not benchmark) |
| Accepted target (median / p95) | ≤240 s / ≤300 s |

The dominant cost was **not** proof math. It was short-lived processes
regenerating and reloading verification keys — a fixed ~330–344 s setup
tax paid on the request path, independent of trade size. The fix, on the
warm-service branch:

- verification keys are **serialized, release-pinned artifacts** — never
  generated at request time;
- a long-lived Asset Orchard proof service **prewarms** both the
  private-swap and private-egress verifier paths before it ever reports
  ready;
- readiness is **fail-closed**: if the warm-up did not complete, the
  service refuses to accept work rather than silently paying the cold
  cost (or worse, appearing healthy while broken);
- warm keys are proven to change *performance only* — never proof
  acceptance, serialization, or state roots.

"Wallet warm-up" is the product-facing consequence: a wallet checks the
prover's readiness marker before letting a user commit to a swap, so the
user's confirmed action starts on a warm path with a predictable
~1–3 minute settlement instead of an unpredictable ~6–9 minute one.
Beyond that, the Heavy ZK roadmap (multicore proving, GPU markets) targets
sub-second proving — designed, not yet implemented.

---

## 6. RFQs: how quoting works, and how it fits in a wallet

The private swap is bilateral — two parties spend notes into one proof —
so someone must set the price. The mechanism is a **request-for-quote**
(RFQ), the standard OTC pattern:

1. **Bob posts a quote.** "I will sell 500 a651 at 8.25, valid 120
   seconds." The quote object binds: the pair, size, price, **the NAV
   epoch it references**, an expiry, and Bob's signature. (The primary
   subscription rail already uses exactly this shape on-chain — epoch,
   reserve-packet hash, rounding rule — the RFQ mirrors it.)
2. **Alice receives it and fills it.** Her wallet shows the quote *versus
   the canonical NAV*: "8.25 vs NAV 8.20 (+0.61%), expires in 90 s,
   settlement ~2 min." She confirms **once, before execution** — there is
   no second confirmation mid-flight, because a multi-minute rail with
   re-confirmation prompts is both bad UX and a griefing vector.
3. **Price locks at acceptance.** The locked quote and its NAV epoch go
   into the run's immutable state record. Two clocks then govern: the
   quote expiry and the NAV staleness bound. If either runs out before
   submission, the workflow fails closed — nothing moves.
4. **The joint proof settles it.** Both sides' notes are committed, the
   proof is built on the warm service, submitted, certified by the
   validator fleet, and each party ends holding new private notes.
5. **If the other side vanishes** after one party commits, the committed
   notes unlock at a deadline and the run records a typed failure —
   the same deadline-and-refund pattern the bridge already uses for
   cross-chain packets.

**Default pricing is at NAV.** The default band is zero; a quote away from
NAV is an explicit, disclosed choice (`at_nav` → `at_nav_with_band` →
`negotiated`), and validator policy can reject settlements outside the
allowed band. The negotiation itself (who asked, who quoted, what was
discussed) never touches the chain — only the settled, proven result does.
In the first release the counterparty is the operator's own quoting desk,
which means privacy holds *against the chain*, not against your
counterparty — the same as any brokered OTC trade, and stated honestly.

In the wallet this appears as: a quotes inbox, a single confirm screen
with NAV comparison and expiry countdown, a progress view driven by the
crash-safe state machine (prepared → submitted → certified → applied →
verified), and an exit screen that compares "redeem at NAV (Arbitrum,
~5 min)" against "sell at pool (mainnet, ~2 min)" **net of bridging and
gas** — because the two doors pay out on different chains.

<figure><img src="/research/private-nav-swap/d3-rfq-sequence.svg" alt="RFQ sequence diagram with three lanes: Bob the maker, the protocol and chain, and Alice the taker. Bob posts a signed quote off-chain with pair, size, price, NAV epoch reference, and expiry. Alice confirms once, ex ante, seeing the quote versus NAV. Price locks at acceptance with two clocks: quote expiry and NAV staleness, failing closed if either runs out. Both sides' notes are committed into one joint shielded proof built on the warm prover, then certified by all six validators. If a side vanishes, the deadline passes, notes unlock, and a typed failure is recorded."></figure>

### The cost advantage: why swap OTC when the asset trades on Uniswap?

Because the OTC rail delivers **the same mainnet asset** while bypassing
every cost that scales with the pool:

| Cost | Buy in the pool | OTC at NAV, bridge out |
| --- | --- | --- |
| LP fee (0.05% here) | paid on full notional | **not paid** — the pool is never touched |
| Price impact | grows with size ÷ pool depth | **none** — NAV pricing is depth-independent |
| MEV / sandwich | exposed in the public mempool | **none** — the trade is a shielded bilateral settlement |
| Trade visibility | fully public | private between visible boundaries |
| What you pay instead | — | desk spread (the NAV band), bridge + gas for the exit |

The decisive line is price impact. Today's pool holds roughly $2k of
banded liquidity — a $1M buy through it is not expensive, it is
*impossible* at any sane price. Through the OTC rail, the same $1M
executes at NAV ± the quoted band regardless of pool depth, and the
buyer still walks away holding the identical wrapped a651 ERC-20 the
pool trades, because the supply-conserving bridge — not the pool — is
what puts the asset on mainnet. The pool is an access and price-discovery
venue for small size; the OTC rail is how size moves. The two stay
honest with each other through arbitrage against the primary
mint/redeem-at-NAV rail.

The same logic runs in reverse on exit: selling size into the pool pays
fee plus impact; redeeming at NAV pays neither. That is why the wallet's
exit screen compares both doors net of all costs.

<figure><img src="/research/private-nav-swap/d4-otc-cost-advantage.svg" alt="Two routes from holding one million USDC to holding mainnet a651. Route A buys in the Uniswap pool: LP fee of five basis points, price impact scaling with size divided by depth, roughly two thousand dollars of current pool depth making a one million dollar trade impossible at any sane price, MEV exposure, and a fully public trade. Route B goes OTC: USDC to pfUSDC counted cash, private swap at NAV plus or minus a band with no pool touched, then bridge out to the same wrapped ERC-20 the pool trades. Costs are the desk spread and bridge plus gas, independent of size and pool depth."></figure>

---

## 7. Fund math: $100k fund, $1M subscription — what moves, and when

Start: a fund holds **$100,000 of assets** with **100,000 units**
outstanding. NAV = $100,000 / 100,000 = **$1.00**.

A subscriber commits **$1,000,000 at NAV**. The mint executes at the
finalized epoch NAV of $1.00, so they receive **1,000,000 units**. In the
same atomic state transition:

| | Before | After |
| --- | ---: | ---: |
| Reserves (TVL) | $100,000 | $1,100,000 |
| Units outstanding | 100,000 | 1,100,000 |
| NAV per unit | $1.00 | **$1.00** |

**Subscriptions and redemptions at NAV never move NAV.** They scale TVL
and supply together, by construction: the cash entering reserves is
exactly the units minted times the price. NAV changes only when the
*portfolio* changes value (or fees accrue). This is the arithmetic the
OTC MVP proved on-chain: TVL rises by exactly the deposit, falls by
exactly the withdrawal, atom-for-atom.

**How it is represented on PFTL:** the mint consumes counted pfUSDC into
the reserve allocation and increments `circulating_supply` immediately —
ledger accounting is consistent the instant the transaction applies.
`nav_per_unit`, however, is an **epoch value**: it stays at the last
finalized number until the next reserve packet (which must now report the
new $1.1M, or it fails reconciliation against the supply ledger and the
reserve watch) is submitted, survives its challenge window, and finalizes.

**How soon must things update?**

- *Ledger supply and reserves:* instantly, atomically, at the mint.
- *NAV:* at the next epoch finalize. Between epochs, everyone prices at
  the last finalized NAV — which is correct *if the portfolio hasn't
  moved*.
- *The stale-price window is the real risk:* if the portfolio gains 5%
  after the epoch finalized and before your $1M mint, you bought at
  yesterday's price and diluted existing holders — the classic mutual-fund
  timing problem. The defenses are: short epochs, a staleness bound
  (mints refuse to execute against an epoch older than the profile
  allows), tolerance rules that halt on out-of-band moves, and `nav_halt`
  as the hard stop. Epoch cadence is therefore a *product parameter*, not
  an implementation detail: the required cadence is set by portfolio
  volatility, not by engineering convenience.
- *The Uniswap pool:* updates by arbitrage, not by decree. A subscription
  that doubles supply does not touch the pool price directly (the pool
  prices its own float); what disciplines the pool is traders arbitraging
  venue price against the primary at-NAV rail. This is why primary-rail
  latency and availability are the true price-quality mechanism —
  slow or gated minting means wide, lazy venue spreads.

---

## 8. What else you should be thinking about (things this plan was neglecting)

- **Fees.** Management fees, spread capture on the quoting desk, bridge
  and gas costs — none are yet specified as product economics. NAV must
  state whether it is net-of-fees per epoch.
- **Liquidity reality.** The mainnet pool was seeded with roughly $2k of
  USDC in a narrow band — a proof-of-mechanics venue, not product depth.
  Real size exits either need real LP depth or will route via NAV
  redemption.
- **Key custody is the current weakest link.** A 1-of-1 withdrawal
  verifier guards the entire USDC reserve; the Uniswap LP position sits
  on an operator EOA; validator signing material had campaign-era custody
  gaps. All are known P0s with staged fixes — but they gate any real
  money.
- **Operational maturity.** The recent campaign exposed (and fixed, in
  as-yet-unmerged branches) real gaps: certified blocks could skip a
  lagging validator, services didn't survive reboots, workflows weren't
  crash-resumable. The fixes exist with tests; the fleet-level acceptance
  evidence does not yet.
- **Timing and amount privacy limits.** Boundaries reveal amounts;
  timing correlation is possible. Serious counterparties will ask; the
  answer should be printed, not improvised.
- **Two-chain UX.** Cash settles on Arbitrum, the venue is on mainnet.
  Every user-facing comparison must be net of the hop, or users will be
  systematically surprised.
- **Who may quote.** V1 is operator-as-desk. Opening RFQ to third-party
  makers requires the griefing protections (quote bonds or reputation,
  note-lock expiries) to be real, not designed.
- **Governance and authority.** Who can halt an asset, rotate an
  attestor, sign a deployment manifest, authorize a live-money run. The
  campaign ran on written GO discipline; the product needs the same
  discipline encoded, not remembered.

---

## 9. The NAVCoin series: what each post claimed, and what is not yet real

| Post | Claim | Production status (2026-07-10) |
| --- | --- | --- |
| [The NAVCoin Proposal](/blog/navcoin-proposal/) | Verified-NAV assets, challenge windows, deadman | NAV observation lane live-proven (incl. against a $275M external vault); bonded challenges and deadman **not deployed** |
| [Pricing Counterparty Risk](/blog/navcoin-counterparty-risk/) | Live exchange credit spread priced into NAV | **Not implemented.** No venue-risk spread exists in any NAV computation today |
| [One Portfolio, Many Venues](/blog/navcoin-ethereum/) | One canonical NAV, many access venues, policy-bound market ops | One venue exists (single Uniswap v4 pool); market-ops envelope types exist in code; **hooks and bounded market operations not deployed** |
| [Collateralization Without Spot Redemption](/blog/navcoin-collateralization/) | Floating NAV without standing redemption rights, envelope-enforced | Design only; note the current demo rail *does* redeem at NAV — the two models need explicit reconciliation |
| [pfUSDC](/blog/pfusdc/) | Source-labeled counted cash | Implemented on devnet with observer-verified admission (Stage 2 deployed and audited); source-label haircut policy partial |
| [OTC MVP Proven](/blog/navcoin-otc-mvp-proven/) | Transparent round trip with real value | **Proven live** (Arbitrum + WAN devnet), including cross-NAVCoin swaps |
| [Canonical Transaction Walkthrough](/blog/canonical-navcoin-transaction/) | The full USDC→a651→Uniswap route, visually | The route R82 later proved privately |
| [Heavy ZK](/blog/heavy-zk-optimization/) | Sub-second proving via multicore/GPU | **Not implemented.** Current state: warm-service keys (~12 s swap step), targets 240/300 s end-to-end |
| [Anatomy of a Proven Swap](/research/proven-private-swap/) (draft) | The full private transaction, end to end | Proven once, live (R82), on the hardened admission path; **not yet a crash-safe, wallet-wired product** — that is the current engineering program |

And the honest bottom line on "how this is actually going to be a thing":
the cryptography, the counterfeit defenses, and the end-to-end rail are
**proven** — each exactly once, under campaign conditions, on a devnet.
Between here and a product stand four named, bounded pieces of work:
finish and merge the reliability fixes (durable delivery, resumable
workflows, supervised services), retire placeholder NAV inputs for the
finalized-epoch feed everywhere, wire the RFQ + state machine into the
wallet with the at-NAV default, and close the custody P0s. None of these
requires new research. All of them require the same evidence-gated
execution discipline that fixed the counterfeit hole.
