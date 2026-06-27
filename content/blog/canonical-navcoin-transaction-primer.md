---
title: "Canonical NAVCoin Transaction: Illustrated Primer"
date: 2026-06-27T00:00:00Z
url: "/blog/canonical-navcoin-transaction-primer/"
summary: "A click-through visual primer for the correct NAVCoin architecture: PFTL reserve proofs, canonical supply, Ethereum wrapping, Uniswap trading, Orchard shielding, bridge finality, and safety gates."
description: "Visual primer explaining the canonical NAVCoin transaction, including proof of reserves, PFTL, wrapped venue tokens, Uniswap, Orchard notes, bridge packets, and protocol gates."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - PFTL
  - Uniswap
  - Bridge
  - Orchard
  - Proof of Reserves
draft: false
---

This primer is the visual companion to [Canonical NAVCoin Transaction](/blog/canonical-navcoin-transaction/). It explains the target architecture, not the retired demo pool: PFTL is the source of truth, Ethereum is a trading venue, and every external token must be backed by a verified PFTL state transition.

<style>
.canon-deck {
  margin: 1.25rem 0 2.4rem;
  padding: 1rem;
  border: 1px solid rgba(221, 255, 220, 0.18);
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(127, 238, 100, 0.08), rgba(66, 153, 225, 0.06)),
    rgba(8, 12, 8, 0.78);
}
.canon-deck input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}
.canon-deck h2 {
  margin: 0 0 0.25rem;
}
.canon-subtitle {
  margin: 0 0 1rem;
  color: var(--muted, #83917f);
}
.canon-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.42rem;
  margin: 0 0 1.05rem;
}
.canon-tabs label {
  cursor: pointer;
  border: 1px solid rgba(221, 255, 220, 0.16);
  border-radius: 999px;
  padding: 0.42rem 0.66rem;
  color: var(--pale-2, #bad8b6);
  background: rgba(221, 255, 220, 0.04);
  font-size: 0.78rem;
  line-height: 1;
}
.canon-slide {
  display: none;
  grid-template-columns: minmax(0, 0.98fr) minmax(300px, 1.02fr);
  gap: 1.05rem;
  align-items: stretch;
  min-height: 375px;
}
.canon-slide h3 {
  margin: 0.15rem 0 0.65rem;
  color: var(--pale, #ddffdc);
  font-size: 1.45rem;
  line-height: 1.14;
}
.canon-slide p {
  margin: 0 0 0.85rem;
}
.canon-kicker {
  display: inline-flex;
  margin: 0;
  padding: 0.22rem 0.5rem;
  border-radius: 999px;
  background: rgba(127, 238, 100, 0.13);
  color: var(--green, #7fee64);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.canon-panel {
  display: grid;
  align-content: center;
  border: 1px solid rgba(221, 255, 220, 0.15);
  border-radius: 12px;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.22);
}
.canon-flow {
  display: grid;
  gap: 0.54rem;
}
.canon-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}
.canon-node {
  border: 1px solid rgba(127, 238, 100, 0.24);
  border-radius: 10px;
  padding: 0.68rem 0.72rem;
  background: rgba(127, 238, 100, 0.075);
  min-height: 78px;
}
.canon-node strong {
  display: block;
  margin-bottom: 0.18rem;
  color: var(--pale, #ddffdc);
  font-size: 0.94rem;
}
.canon-node span {
  display: block;
  color: var(--pale-2, #bad8b6);
  font-size: 0.82rem;
  line-height: 1.34;
}
.canon-node.public {
  border-color: rgba(66, 153, 225, 0.35);
  background: rgba(66, 153, 225, 0.08);
}
.canon-node.private {
  border-style: dashed;
  border-color: rgba(127, 238, 100, 0.5);
  background: rgba(127, 238, 100, 0.1);
}
.canon-node.gate {
  border-color: rgba(255, 214, 102, 0.45);
  background: rgba(255, 214, 102, 0.1);
}
.canon-node.danger {
  border-color: rgba(255, 113, 113, 0.45);
  background: rgba(255, 113, 113, 0.08);
}
.canon-arrow {
  color: var(--muted, #83917f);
  text-align: center;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.78rem;
}
.canon-lane {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.55rem;
  align-items: center;
}
.canon-badge-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.85rem;
}
.canon-badge {
  border-radius: 9px;
  padding: 0.55rem;
  background: rgba(221, 255, 220, 0.045);
  color: var(--pale-2, #bad8b6);
  font-size: 0.84rem;
}
.canon-badge strong {
  display: block;
  margin-bottom: 0.15rem;
  color: var(--green, #7fee64);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
#canon-slide-1:checked ~ .canon-tabs label[for="canon-slide-1"],
#canon-slide-2:checked ~ .canon-tabs label[for="canon-slide-2"],
#canon-slide-3:checked ~ .canon-tabs label[for="canon-slide-3"],
#canon-slide-4:checked ~ .canon-tabs label[for="canon-slide-4"],
#canon-slide-5:checked ~ .canon-tabs label[for="canon-slide-5"],
#canon-slide-6:checked ~ .canon-tabs label[for="canon-slide-6"],
#canon-slide-7:checked ~ .canon-tabs label[for="canon-slide-7"],
#canon-slide-8:checked ~ .canon-tabs label[for="canon-slide-8"],
#canon-slide-9:checked ~ .canon-tabs label[for="canon-slide-9"],
#canon-slide-10:checked ~ .canon-tabs label[for="canon-slide-10"],
#canon-slide-11:checked ~ .canon-tabs label[for="canon-slide-11"],
#canon-slide-12:checked ~ .canon-tabs label[for="canon-slide-12"],
#canon-slide-13:checked ~ .canon-tabs label[for="canon-slide-13"],
#canon-slide-14:checked ~ .canon-tabs label[for="canon-slide-14"] {
  border-color: rgba(127, 238, 100, 0.66);
  background: rgba(127, 238, 100, 0.16);
  color: var(--green, #7fee64);
}
#canon-slide-1:checked ~ .canon-slides .canon-slide:nth-child(1),
#canon-slide-2:checked ~ .canon-slides .canon-slide:nth-child(2),
#canon-slide-3:checked ~ .canon-slides .canon-slide:nth-child(3),
#canon-slide-4:checked ~ .canon-slides .canon-slide:nth-child(4),
#canon-slide-5:checked ~ .canon-slides .canon-slide:nth-child(5),
#canon-slide-6:checked ~ .canon-slides .canon-slide:nth-child(6),
#canon-slide-7:checked ~ .canon-slides .canon-slide:nth-child(7),
#canon-slide-8:checked ~ .canon-slides .canon-slide:nth-child(8),
#canon-slide-9:checked ~ .canon-slides .canon-slide:nth-child(9),
#canon-slide-10:checked ~ .canon-slides .canon-slide:nth-child(10),
#canon-slide-11:checked ~ .canon-slides .canon-slide:nth-child(11),
#canon-slide-12:checked ~ .canon-slides .canon-slide:nth-child(12),
#canon-slide-13:checked ~ .canon-slides .canon-slide:nth-child(13),
#canon-slide-14:checked ~ .canon-slides .canon-slide:nth-child(14) {
  display: grid;
}
@media (max-width: 800px) {
  .canon-slide,
  .canon-lane,
  .canon-row {
    grid-template-columns: 1fr;
  }
  .canon-badge-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="canon-deck">
<h2>Click through the canonical transaction</h2>
<p class="canon-subtitle">Fourteen slides: old demo, correct model, reserve proof, bridge, wrapper, Uniswap, Orchard, egress, and gates.</p>
<input id="canon-slide-1" name="canon-primer" type="radio" checked>
<input id="canon-slide-2" name="canon-primer" type="radio">
<input id="canon-slide-3" name="canon-primer" type="radio">
<input id="canon-slide-4" name="canon-primer" type="radio">
<input id="canon-slide-5" name="canon-primer" type="radio">
<input id="canon-slide-6" name="canon-primer" type="radio">
<input id="canon-slide-7" name="canon-primer" type="radio">
<input id="canon-slide-8" name="canon-primer" type="radio">
<input id="canon-slide-9" name="canon-primer" type="radio">
<input id="canon-slide-10" name="canon-primer" type="radio">
<input id="canon-slide-11" name="canon-primer" type="radio">
<input id="canon-slide-12" name="canon-primer" type="radio">
<input id="canon-slide-13" name="canon-primer" type="radio">
<input id="canon-slide-14" name="canon-primer" type="radio">
<div class="canon-tabs" aria-label="Canonical NAVCoin primer slides">
<label for="canon-slide-1">1 Old demo</label>
<label for="canon-slide-2">2 Correct model</label>
<label for="canon-slide-3">3 Reserve proof</label>
<label for="canon-slide-4">4 NAV epoch</label>
<label for="canon-slide-5">5 Native mint</label>
<label for="canon-slide-6">6 Bridge packet</label>
<label for="canon-slide-7">7 Finality proof</label>
<label for="canon-slide-8">8 Wrapped token</label>
<label for="canon-slide-9">9 Uniswap</label>
<label for="canon-slide-10">10 Shield</label>
<label for="canon-slide-11">11 Orchard swap</label>
<label for="canon-slide-12">12 Egress</label>
<label for="canon-slide-13">13 Gates</label>
<label for="canon-slide-14">14 Whole path</label>
</div>
<div class="canon-slides">
<section class="canon-slide">
<div>
<p class="canon-kicker">Before</p>
<h3>The old demo put the token on Ethereum first.</h3>
<p>The retired a651 pool was useful because it proved we could deploy a NAVCoin-like token and trade it against USDC. But the Ethereum token and its proof adapter were acting like the main truth surface.</p>
<p>The correct system cannot depend on an Ethereum mirror being fresh. Ethereum should be a venue. PFTL should be the ledger that says what exists.</p>
<div class="canon-badge-grid">
<div class="canon-badge"><strong>Good for</strong>Demo liquidity, smoke swaps, early UX.</div>
<div class="canon-badge"><strong>Not good for</strong>Canonical supply, trustless bridge accounting.</div>
</div>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node danger"><strong>Ethereum a651</strong><span>Standalone token and pool.</span></div>
<div class="canon-arrow">reads</div>
<div class="canon-node danger"><strong>Ethereum proof adapter</strong><span>A secondary surface that can become stale.</span></div>
<div class="canon-arrow">trades on</div>
<div class="canon-node public"><strong>Uniswap</strong><span>Useful market, not the source of truth.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Target model</p>
<h3>PFTL owns truth. Ethereum owns venue access.</h3>
<p>In the canonical model, PFTL tracks NAV proof, supply, reserve epochs, mint rights, burn rights, and bridge packets. Ethereum receives a wrapped representation only when it can verify that PFTL authorized it.</p>
<p>If you remember one line, remember this: <strong>the wrapper can trade anywhere, but the thing being wrapped is a PFTL claim.</strong></p>
</div>
<div class="canon-panel">
<div class="canon-lane">
<div class="canon-node gate"><strong>PFTL</strong><span>Canonical reserve proof and supply ledger.</span></div>
<div class="canon-arrow">verified bridge</div>
<div class="canon-node public"><strong>Ethereum</strong><span>Wrapped token and Uniswap venue.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Proof of reserves</p>
<h3>First prove what backs the coin.</h3>
<p>A NAVCoin is not "trust me, there is money somewhere." A proof run reads reserve legs, liabilities, cash, and venue positions, then computes verified net assets under a published policy.</p>
<p>Proofs do not make dishonest venues honest. They make the reported reserve packet checkable, fresh, and bound to supply rules.</p>
</div>
<div class="canon-panel">
<div class="canon-row">
<div class="canon-node public"><strong>Reserve legs</strong><span>On-chain wallets, venue balances, cash, collateral.</span></div>
<div class="canon-node public"><strong>Liabilities</strong><span>Borrowing, claims, offsets.</span></div>
<div class="canon-node gate"><strong>Policy</strong><span>What counts, haircuts, stale windows.</span></div>
</div>
<div class="canon-arrow">verified net assets = reserves + cash - liabilities</div>
<div class="canon-node gate"><strong>Reserve packet</strong><span>Hash-bound evidence, timestamp, NAV/unit, proof status.</span></div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">PFTL epoch</p>
<h3>The proof becomes a finalized NAV epoch.</h3>
<p>PFTL validators check the proof and the arithmetic. If it passes, the epoch finalizes. If the proof is stale, malformed, inconsistent, or outside policy, the epoch should not become usable.</p>
<p>This is where NAV stops being a website number and becomes protocol state.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node public"><strong>nav_reserve_submit</strong><span>Submit the reserve packet and proof.</span></div>
<div class="canon-arrow">validators verify</div>
<div class="canon-node gate"><strong>nav_epoch_finalize</strong><span>Finalize only if proof and supply rules pass.</span></div>
<div class="canon-arrow">outputs</div>
<div class="canon-node public"><strong>Canonical NAV</strong><span>Epoch, timestamp, verified NAV, NAV/unit.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Native mint</p>
<h3>Native NAVCoin supply starts on PFTL.</h3>
<p>A buyer can enter with counted cash, such as pfUSDC. PFTL mints or releases native NAVCoin only under the finalized NAV policy. That keeps the supply denominator tied to a proof epoch.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node public"><strong>pfUSDC in</strong><span>Cash representation PFTL can count.</span></div>
<div class="canon-arrow">NAV policy gate</div>
<div class="canon-node gate"><strong>native NAVCoin</strong><span>PFTL a651-like asset with canonical supply accounting.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Bridge packet</p>
<h3>To trade on Ethereum, PFTL creates an export packet.</h3>
<p>The packet says: burn or lock this many native NAVCoins on PFTL, then mint the matching wrapped amount on Ethereum for this recipient. It includes chain ids, asset ids, amount, nonce, recipient, expiry, and receipt root binding.</p>
<p>A relayer can carry the packet, but the relayer is not trusted to decide whether it is true.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node gate"><strong>PFTL debit</strong><span>Native supply is burned or locked.</span></div>
<div class="canon-arrow">creates</div>
<div class="canon-node public"><strong>Export packet</strong><span>Amount, recipient, nonce, route, expiry, receipt proof.</span></div>
<div class="canon-arrow">carried by any relayer</div>
<div class="canon-node public"><strong>Ethereum bridge</strong><span>Verifies before minting.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Finality verifier</p>
<h3>Ethereum must verify that PFTL really finalized the packet.</h3>
<p>This is the hard part. The Ethereum bridge needs a PFTL finality verifier or a succinct proof of PFTL finality. It should not trust a screenshot, an API server, or a single operator signature.</p>
<p>Until this exists, the bridge is trust-based or trust-minimized, not fully trustless.</p>
</div>
<div class="canon-panel">
<div class="canon-row">
<div class="canon-node gate"><strong>Header</strong><span>Finalized PFTL block state.</span></div>
<div class="canon-node gate"><strong>Certificate</strong><span>Quorum proof from validators.</span></div>
<div class="canon-node gate"><strong>Receipt inclusion</strong><span>Packet is inside the finalized receipt root.</span></div>
</div>
<div class="canon-arrow">if all pass</div>
<div class="canon-node public"><strong>Mint wrapped token</strong><span>Ethereum token supply increases exactly once.</span></div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Wrapped token</p>
<h3>The Ethereum token is a wrapper, not a new NAV source.</h3>
<p>The wrapped ERC-20 can be held in normal wallets and traded in normal Ethereum apps. But it should only mint from verified PFTL packets and only burn into verified return packets.</p>
<p>That is what makes it different from the retired standalone a651 demo token.</p>
</div>
<div class="canon-panel">
<div class="canon-lane">
<div class="canon-node gate"><strong>Bridge controller</strong><span>Consumes packet nonce, verifies proof, mints once.</span></div>
<div class="canon-arrow">controls</div>
<div class="canon-node public"><strong>wNAVCoin ERC-20</strong><span>Venue representation of the PFTL asset.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Uniswap venue</p>
<h3>Uniswap gives execution, not truth.</h3>
<p>Once wrapped NAVCoin exists on Ethereum, it can trade against USDC in a new Uniswap pool. The pool discovers a market price. It does not know whether NAV is fresh. Dashboards and front ends should show both: market price and canonical NAV.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node public"><strong>wNAVCoin</strong><span>Wrapped PFTL claim.</span></div>
<div class="canon-arrow">trades with</div>
<div class="canon-node public"><strong>USDC pool</strong><span>Market price, liquidity, slippage.</span></div>
<div class="canon-arrow">display beside</div>
<div class="canon-node gate"><strong>PFTL NAV</strong><span>Verified NAV/unit and proof freshness.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Shielding</p>
<h3>Orchard is the privacy envelope.</h3>
<p>Orchard is a shielded note system. Instead of publishing "Alice spent this exact coin to Bob," the wallet creates private notes and proves the transition is valid. The chain sees commitments, nullifiers, and proofs; it does not see the note opening.</p>
<p>A nullifier is the public "this note has been spent" marker. It prevents double spending without revealing which private note was yours.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node public"><strong>Public pfUSDC</strong><span>Visible balance.</span></div>
<div class="canon-arrow">shielded ingress</div>
<div class="canon-node private"><strong>Orchard note</strong><span>Private owner, private opening, public commitment.</span></div>
<div class="canon-arrow">spend publishes</div>
<div class="canon-node private"><strong>Nullifier</strong><span>Prevents reuse without exposing the note.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Private swap</p>
<h3>A private NAVCoin swap changes notes, not public balances.</h3>
<p>Inside the shielded path, a pfUSDC note can be consumed and a NAVCoin note can be created. The proof enforces allowed assets, conservation, nullifier rules, and policy checks. The public chain sees proof validity, not the user's exact private path.</p>
</div>
<div class="canon-panel">
<div class="canon-lane">
<div class="canon-node private"><strong>pfUSDC note</strong><span>Private input.</span></div>
<div class="canon-arrow">Halo2 proof</div>
<div class="canon-node private"><strong>NAVCoin note</strong><span>Private output.</span></div>
</div>
<div class="canon-arrow">validators verify proof and nullifiers</div>
<div class="canon-node gate"><strong>PFTL certificate</strong><span>Certified shielded batch.</span></div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Egress</p>
<h3>Leaving privacy means making a public claim again.</h3>
<p>To bridge out or redeem, the user must create a public exit artifact. The private note opening stays hidden, but the output needed for public settlement becomes visible.</p>
<p>This is why privacy and bridges need careful gates: the private middle hides routing, while the edges are public accounting surfaces.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node private"><strong>Private NAVCoin note</strong><span>Wallet-side ownership.</span></div>
<div class="canon-arrow">private egress proof</div>
<div class="canon-node public"><strong>Public NAV exit</strong><span>Visible recipient, amount, asset, receipt.</span></div>
<div class="canon-arrow">then</div>
<div class="canon-node public"><strong>Bridge or redeem</strong><span>Return to Ethereum, USDC, or another public venue.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Safety gates</p>
<h3>Every step has a stop sign.</h3>
<p>The correct system should fail closed. If the proof is stale, minting stops. If the bridge packet is replayed, minting stops. If a nullifier already exists, spending stops. If finality cannot be verified, wrapping stops.</p>
</div>
<div class="canon-panel">
<div class="canon-row">
<div class="canon-node gate"><strong>Proof gate</strong><span>Fresh NAV epoch required.</span></div>
<div class="canon-node gate"><strong>Supply gate</strong><span>No mint beyond authorized supply.</span></div>
<div class="canon-node gate"><strong>Replay gate</strong><span>Nonce/packet consumed once.</span></div>
</div>
<div class="canon-row">
<div class="canon-node gate"><strong>Nullifier gate</strong><span>Private note cannot be spent twice.</span></div>
<div class="canon-node gate"><strong>Finality gate</strong><span>Destination verifies source finality.</span></div>
<div class="canon-node gate"><strong>Stale gate</strong><span>Old NAV data cannot silently pass.</span></div>
</div>
</div>
</section>
<section class="canon-slide">
<div>
<p class="canon-kicker">Whole path</p>
<h3>The canonical transaction is a chain of checked claims.</h3>
<p>The user experience can feel simple: buy, shield, swap, bridge, redeem. Underneath, every hop should be backed by a proof, packet, nullifier, receipt, or finalized epoch.</p>
<p>That is the difference between a token that happens to trade on Uniswap and a NAVCoin whose external venue supply is tied back to PFTL.</p>
</div>
<div class="canon-panel">
<div class="canon-flow">
<div class="canon-node gate"><strong>Proof of reserves</strong><span>Backed NAV epoch on PFTL.</span></div>
<div class="canon-arrow">authorizes</div>
<div class="canon-node gate"><strong>Native supply</strong><span>PFTL canonical NAVCoin.</span></div>
<div class="canon-arrow">verified packet</div>
<div class="canon-node public"><strong>Wrapped venue token</strong><span>Ethereum representation.</span></div>
<div class="canon-arrow">optional paths</div>
<div class="canon-row">
<div class="canon-node public"><strong>Uniswap</strong><span>Public market execution.</span></div>
<div class="canon-node private"><strong>Orchard</strong><span>Private note movement.</span></div>
<div class="canon-node public"><strong>Redeem</strong><span>Public exit and settlement.</span></div>
</div>
</div>
</div>
</section>
</div>
</div>
## Short glossary

| Term | Meaning |
|---|---|
| PFTL | Post Fiat L1, the canonical ledger in this design. |
| NAVCoin | A token whose unit value is tied to a verified net asset value process. |
| pfUSDC | A PFTL-recognized stablecoin representation used as counted cash. |
| Wrapped token | A venue token on another chain that represents a PFTL claim. |
| Bridge packet | A source-chain instruction that can be verified on the destination chain. |
| Orchard | A shielded note system for private ownership and transfers. |
| Note commitment | A public commitment to a private note. |
| Nullifier | A public marker proving a private note was spent once, without revealing which note it was. |
| Gate | A rule that stops the transaction if a proof, packet, nonce, supply limit, or freshness check fails. |

