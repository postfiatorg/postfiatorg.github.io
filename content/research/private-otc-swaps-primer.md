---
title: "Private OTC Swaps: Illustrated Primer"
date: 2026-06-25T00:00:00Z
url: "/research/private-otc-swaps/primer/"
summary: "A click-through visual primer for the shielding, private swap, certification, private egress, redemption, and transparent control steps behind the Private OTC Swaps post."
categories:
  - Post Fiat Research
tags:
  - NAVCoin
  - OTC
  - Privacy
  - Shielded
  - pfUSDC
  - PFTL
  - Orchard
---

This primer is the visual companion to [Private OTC Swaps](/research/private-otc-swaps/). It walks through the user-visible flow one step at a time: counted cash, shielded ingress, private swap, PFTL certification, private egress, public redemption, and the transparent control path.

<style>
.private-otc-deck {
  margin: 1.25rem 0 2.25rem;
  padding: 1rem;
  border: 1px solid var(--border, rgba(125, 125, 125, 0.24));
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(35, 197, 142, 0.12), rgba(71, 148, 255, 0.08)),
    var(--entry, rgba(255, 255, 255, 0.03));
}
.private-otc-deck input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}
.private-otc-deck h2 {
  margin: 0 0 0.25rem;
}
.private-otc-subtitle {
  margin: 0 0 1rem;
  color: var(--secondary, #6f7785);
}
.private-otc-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1rem;
}
.private-otc-tabs label {
  cursor: pointer;
  border: 1px solid var(--border, rgba(125, 125, 125, 0.28));
  border-radius: 999px;
  padding: 0.45rem 0.7rem;
  font-size: 0.82rem;
  line-height: 1;
  color: var(--secondary, #6f7785);
  background: var(--theme, rgba(255, 255, 255, 0.06));
}
.private-otc-slide {
  display: none;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
  gap: 1.1rem;
  align-items: center;
  min-height: 330px;
}
.private-otc-slide h3 {
  margin: 0.15rem 0 0.65rem;
  font-size: 1.45rem;
}
.private-otc-slide p {
  margin: 0 0 0.8rem;
}
.private-otc-kicker {
  display: inline-flex;
  margin: 0;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  background: rgba(35, 197, 142, 0.13);
  color: rgb(14, 116, 82);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.private-otc-panel {
  border: 1px solid var(--border, rgba(125, 125, 125, 0.24));
  border-radius: 14px;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.06);
}
.private-otc-flow {
  display: grid;
  gap: 0.55rem;
}
.private-otc-node {
  border: 1px solid rgba(54, 144, 255, 0.28);
  border-radius: 12px;
  padding: 0.7rem 0.8rem;
  background: rgba(54, 144, 255, 0.08);
}
.private-otc-node strong {
  display: block;
  margin-bottom: 0.18rem;
}
.private-otc-node span {
  color: var(--secondary, #6f7785);
  font-size: 0.86rem;
}
.private-otc-node.private {
  border-style: dashed;
  border-color: rgba(35, 197, 142, 0.48);
  background: rgba(35, 197, 142, 0.1);
}
.private-otc-arrow {
  text-align: center;
  color: var(--secondary, #6f7785);
  font-size: 0.9rem;
}
.private-otc-facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.8rem;
}
.private-otc-fact {
  border-radius: 10px;
  padding: 0.55rem;
  background: rgba(0, 0, 0, 0.04);
  font-size: 0.85rem;
}
.private-otc-fact strong {
  display: block;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--secondary, #6f7785);
}
#private-otc-slide-1:checked ~ .private-otc-tabs label[for="private-otc-slide-1"],
#private-otc-slide-2:checked ~ .private-otc-tabs label[for="private-otc-slide-2"],
#private-otc-slide-3:checked ~ .private-otc-tabs label[for="private-otc-slide-3"],
#private-otc-slide-4:checked ~ .private-otc-tabs label[for="private-otc-slide-4"],
#private-otc-slide-5:checked ~ .private-otc-tabs label[for="private-otc-slide-5"],
#private-otc-slide-6:checked ~ .private-otc-tabs label[for="private-otc-slide-6"],
#private-otc-slide-7:checked ~ .private-otc-tabs label[for="private-otc-slide-7"] {
  color: rgb(8, 83, 59);
  border-color: rgba(35, 197, 142, 0.62);
  background: rgba(35, 197, 142, 0.18);
}
#private-otc-slide-1:checked ~ .private-otc-slides .private-otc-slide:nth-child(1),
#private-otc-slide-2:checked ~ .private-otc-slides .private-otc-slide:nth-child(2),
#private-otc-slide-3:checked ~ .private-otc-slides .private-otc-slide:nth-child(3),
#private-otc-slide-4:checked ~ .private-otc-slides .private-otc-slide:nth-child(4),
#private-otc-slide-5:checked ~ .private-otc-slides .private-otc-slide:nth-child(5),
#private-otc-slide-6:checked ~ .private-otc-slides .private-otc-slide:nth-child(6),
#private-otc-slide-7:checked ~ .private-otc-slides .private-otc-slide:nth-child(7) {
  display: grid;
}
@media (max-width: 760px) {
  .private-otc-slide {
    grid-template-columns: 1fr;
  }
  .private-otc-facts {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="private-otc-deck">
  <h2>Click through the swap</h2>
  <p class="private-otc-subtitle">Seven panels, from counted cash to a private NAVCoin swap and back to a public exit.</p>

  <input id="private-otc-slide-1" name="private-otc-primer" type="radio" checked>
  <input id="private-otc-slide-2" name="private-otc-primer" type="radio">
  <input id="private-otc-slide-3" name="private-otc-primer" type="radio">
  <input id="private-otc-slide-4" name="private-otc-primer" type="radio">
  <input id="private-otc-slide-5" name="private-otc-primer" type="radio">
  <input id="private-otc-slide-6" name="private-otc-primer" type="radio">
  <input id="private-otc-slide-7" name="private-otc-primer" type="radio">

  <div class="private-otc-tabs" aria-label="Private OTC swap primer slides">
    <label for="private-otc-slide-1">1 Count cash</label>
    <label for="private-otc-slide-2">2 Shield</label>
    <label for="private-otc-slide-3">3 Swap</label>
    <label for="private-otc-slide-4">4 Certify</label>
    <label for="private-otc-slide-5">5 Egress</label>
    <label for="private-otc-slide-6">6 Redeem</label>
    <label for="private-otc-slide-7">7 Control path</label>
  </div>

  <div class="private-otc-slides">
    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Public accounting</p>
        <h3>Start with cash the chain can count.</h3>
        <p>The input is USDC, but Post Fiat does not treat every dollar-shaped token as the same asset. In the demo, USDC is bridged into PFTL as pfUSDC, a canonical stablecoin representation that can be counted by the NAV and settlement logic.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Public</strong>Source, amount, bridge receipt.</div>
          <div class="private-otc-fact"><strong>Why it matters</strong>The NAV system sees reserve-quality cash, not a vague wallet balance.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node"><strong>USDC</strong><span>Ethereum, Arbitrum, Base, or another source venue.</span></div>
          <div class="private-otc-arrow">bridge attestation</div>
          <div class="private-otc-node"><strong>pfUSDC on PFTL</strong><span>A chain-native receipt the swap circuit can consume.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Shielded ingress</p>
        <h3>Turn public pfUSDC into an Orchard note.</h3>
        <p>The wallet creates a private note commitment. The chain can verify that value entered the shielded pool, while the note opening and ownership stay wallet-side.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Public</strong>A valid shielded action and commitment.</div>
          <div class="private-otc-fact"><strong>Private</strong>Note opening, owner keys, and wallet path.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node"><strong>pfUSDC balance</strong><span>Visible before shielding.</span></div>
          <div class="private-otc-arrow">commit</div>
          <div class="private-otc-node private"><strong>pfUSDC Orchard note</strong><span>Private spendable input for the swap.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Private exchange</p>
        <h3>Swap pfUSDC into a651 inside the circuit.</h3>
        <p>The Asset-Orchard proof consumes a pfUSDC note and emits an a651 note. It enforces the permitted asset exchange and conservation rules without publishing the user's note details.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Input</strong>Private pfUSDC note.</div>
          <div class="private-otc-fact"><strong>Output</strong>Private a651 NAVCoin note.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node private"><strong>pfUSDC note</strong><span>Spent once; its nullifier prevents reuse.</span></div>
          <div class="private-otc-arrow">zk proof</div>
          <div class="private-otc-node private"><strong>a651 note</strong><span>NAVCoin output remains private until egress.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">PFTL finality</p>
        <h3>Validators certify the batch.</h3>
        <p>PFTL validators verify the proof, execute the state transition, and sign a block certificate. In the latest shielded execution, the swap certified with five validator votes at height 437.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Public</strong>Batch id, height, certificate, proof validity.</div>
          <div class="private-otc-fact"><strong>Measured</strong>Proof creation 6.06s; transport/certification 4.90s after prewarm.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node"><strong>Proposer</strong><span>Builds the shielded batch.</span></div>
          <div class="private-otc-arrow">verify and vote</div>
          <div class="private-otc-node"><strong>Certificate</strong><span>Consensus accepts the state transition.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Private egress</p>
        <h3>Exit the private note without revealing its opening.</h3>
        <p>When the user needs a public asset again, private egress proves the right to exit the a651 note and creates public exit fields. The egress is public; the internal note opening is not.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Public</strong>Exit artifact and verification result.</div>
          <div class="private-otc-fact"><strong>Private</strong>How the wallet owned and routed the note.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node private"><strong>a651 Orchard note</strong><span>Private asset ownership.</span></div>
          <div class="private-otc-arrow">private egress proof</div>
          <div class="private-otc-node"><strong>Public a651 exit</strong><span>Visible handoff for redemption.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Public exit</p>
        <h3>Redeem and withdraw on the visible rail.</h3>
        <p>After egress, the user is back in the public NAV and bridge-out world. The demo uses the public a651 exit to create the redemption path and settle the withdrawal.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Public</strong>Redemption artifact, withdrawal, final balances.</div>
          <div class="private-otc-fact"><strong>Boundary</strong>Privacy protects the shielded path, not the final public claim.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node"><strong>Public a651</strong><span>Exit artifact from the shielded pool.</span></div>
          <div class="private-otc-arrow">redeem and withdraw</div>
          <div class="private-otc-node"><strong>USDC claim</strong><span>Public settlement leg.</span></div>
        </div>
      </div>
    </section>

    <section class="private-otc-slide">
      <div>
        <p class="private-otc-kicker">Transparent control</p>
        <h3>Run the same NAV mechanics without Orchard.</h3>
        <p>The transparent demo is the control path: a651 trustline, primary mint, NAV money-in, NAV exit, and summary, all on PFTL without shielded notes. It proves the accounting path works before privacy is layered on.</p>
        <div class="private-otc-facts">
          <div class="private-otc-fact"><strong>Useful for</strong>Debugging, audit traces, and repeatable operator demos.</div>
          <div class="private-otc-fact"><strong>Not private</strong>It intentionally exposes the state transitions.</div>
        </div>
      </div>
      <div class="private-otc-panel">
        <div class="private-otc-flow">
          <div class="private-otc-node"><strong>Public pfUSDC</strong><span>Transparent input.</span></div>
          <div class="private-otc-arrow">primary mint and NAV exit</div>
          <div class="private-otc-node"><strong>Public summary</strong><span>Receipts, timing, and balances are visible.</span></div>
        </div>
      </div>
    </section>
  </div>
</div>

Return to [Private OTC Swaps](/research/private-otc-swaps/).
