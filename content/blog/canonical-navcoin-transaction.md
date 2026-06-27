---
title: "Canonical NAVCoin Transaction"
date: 2026-06-27T00:00:00Z
url: "/canonical-navcoin-transaction/"
aliases:
  - "/blog/canonical-navcoin-transaction/"
  - "/blog/canonical-navcoin-transaction-primer/"
summary: "A click-through slide deck explaining the correct NAVCoin transaction: proof of reserves, PFTL supply, Ethereum wrapping, Uniswap trading, Orchard privacy, private egress, and the gates that keep supply honest."
description: "Slide deck explaining canonical NAVCoin transactions, including PFTL proof of reserves, wrapped Ethereum venue tokens, Uniswap, Orchard notes, bridge packets, and safety gates."
author: "Post Fiat"
breadcrumb_label: "Slide Deck"
breadcrumb_url: "/canonical-navcoin-transaction/"
hide_from_blog: true
show_toc: false
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

This is the visual primer. The longer prose version has been moved to [research notes](/research/canonical-navcoin-transaction/).

<style>
.navcoin-deck {
  --deck-bg: #030604;
  --deck-panel: rgba(6, 14, 9, 0.74);
  --deck-line: rgba(221, 255, 220, 0.18);
  --deck-bright: #ddffdc;
  --deck-soft: #bad8b6;
  --deck-muted: #83917f;
  --deck-green: #7fee64;
  --deck-cyan: #4fc3ff;
  --deck-amber: #ffd166;
  position: relative;
  left: 50%;
  width: min(1280px, calc(100vw - 24px));
  margin: 1.4rem 0 3rem;
  transform: translateX(-50%);
  color: var(--deck-bright);
}
.deck-shell {
  border: 1px solid var(--deck-line);
  border-radius: 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 22% 12%, rgba(127, 238, 100, 0.16), transparent 34%),
    radial-gradient(circle at 82% 4%, rgba(79, 195, 255, 0.12), transparent 30%),
    linear-gradient(180deg, rgba(12, 22, 15, 0.95), rgba(0, 0, 0, 0.96));
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.45);
}
.deck-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-bottom: 1px solid rgba(221, 255, 220, 0.12);
  background: rgba(0, 0, 0, 0.34);
}
.deck-eyebrow,
.deck-count {
  color: var(--deck-green);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.deck-count {
  color: var(--deck-soft);
}
.deck-stage {
  position: relative;
  min-height: 0;
  overflow: visible;
}
.deck-slide {
  position: relative;
  display: none;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  gap: 0;
  pointer-events: none;
}
.deck-slide.is-active {
  display: grid;
  pointer-events: auto;
}
.deck-art {
  position: relative;
  min-height: 0;
  aspect-ratio: 16 / 9;
  background: #020402;
  overflow: hidden;
}
.deck-art img {
  width: 100%;
  height: 100%;
  min-height: 0;
  aspect-ratio: 16 / 9;
  object-fit: contain;
  display: block;
  filter: saturate(1.04) contrast(1.04);
}
.deck-slide.is-active.motion-source .deck-art img { animation: deck-pan-right 8800ms ease-out both; }
.deck-slide.is-active.motion-map .deck-art img { animation: deck-breathe 9000ms ease-in-out both; }
.deck-slide.is-active.motion-proof .deck-art img { animation: deck-pan-left 8200ms ease-out both; }
.deck-slide.is-active.motion-gate .deck-art img { animation: deck-gate-pulse 7600ms ease-in-out both; }
.deck-slide.is-active.motion-private .deck-art img { animation: deck-private-drift 8600ms ease-out both; }
.deck-art::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.04), transparent 28%, rgba(0, 0, 0, 0.18)),
    radial-gradient(circle at 50% 120%, rgba(127, 238, 100, 0.12), transparent 38%);
}
.deck-slide.is-active .deck-art::before {
  content: "";
  position: absolute;
  inset: -20%;
  z-index: 1;
  pointer-events: none;
  background: linear-gradient(100deg, transparent 20%, rgba(127, 238, 100, 0.13), transparent 48%);
  transform: translateX(-72%);
  animation: deck-scan 2400ms ease-out 260ms both;
}
.deck-copy {
  position: relative;
  z-index: 2;
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: clamp(1.15rem, 2.4vw, 1.9rem);
  border-top: 1px solid rgba(221, 255, 220, 0.14);
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.24), rgba(0, 0, 0, 0.62)),
    rgba(4, 8, 5, 0.86);
}
.deck-slide.is-active .deck-copy {
  animation: deck-copy-in 420ms ease-out both;
}
.deck-kicker {
  margin: 0;
  color: var(--deck-green);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.deck-copy h2 {
  margin: 0;
  border: 0;
  padding: 0;
  color: var(--deck-bright);
  font-size: clamp(1.7rem, 3.35vw, 3.35rem);
  line-height: 1;
  font-weight: 650;
  letter-spacing: 0;
}
.deck-copy p {
  margin: 0;
  color: var(--deck-soft);
  font-size: clamp(1rem, 1.4vw, 1.16rem);
  line-height: 1.55;
}
.deck-beats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
  margin: 0;
  padding: 0;
  list-style: none;
}
.deck-beats li {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.62rem;
  align-items: start;
  min-height: 48px;
  padding: 0.72rem 0.82rem;
  border: 1px solid rgba(221, 255, 220, 0.13);
  border-radius: 10px;
  background: rgba(221, 255, 220, 0.045);
  color: var(--deck-soft);
  opacity: 0;
  transform: translateY(10px);
}
.deck-beats li::before {
  content: attr(data-step);
  display: grid;
  place-items: center;
  width: 1.45rem;
  height: 1.45rem;
  border-radius: 50%;
  background: rgba(127, 238, 100, 0.14);
  color: var(--deck-green);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.72rem;
  font-weight: 700;
}
.deck-slide.is-active .deck-beats li {
  animation: deck-beat-in 360ms ease-out both;
  animation-delay: calc(var(--i) * 105ms + 250ms);
}
.deck-term {
  display: inline-flex;
  width: fit-content;
  margin-top: 0.1rem;
  padding: 0.28rem 0.52rem;
  border: 1px solid rgba(127, 238, 100, 0.24);
  border-radius: 999px;
  color: var(--deck-green);
  background: rgba(127, 238, 100, 0.08);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.74rem;
}
.slide-notes {
  margin-top: 0.25rem;
  border: 1px solid rgba(221, 255, 220, 0.11);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.22);
  overflow: hidden;
}
.slide-notes summary {
  padding: 0.62rem 0.75rem;
  color: var(--deck-muted);
  cursor: pointer;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.slide-notes div {
  display: grid;
  gap: 0.45rem;
  padding: 0 0.75rem 0.75rem;
  color: var(--deck-soft);
  font-size: 0.88rem;
  line-height: 1.5;
}
.deck-controls {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.7rem;
  align-items: center;
  padding: 0.9rem 1rem 1rem;
  border-top: 1px solid rgba(221, 255, 220, 0.12);
  background: rgba(0, 0, 0, 0.42);
}
.deck-button {
  min-height: 42px;
  border: 1px solid rgba(127, 238, 100, 0.35);
  border-radius: 999px;
  padding: 0.55rem 0.9rem;
  background: rgba(127, 238, 100, 0.08);
  color: var(--deck-green);
  cursor: pointer;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}
.deck-button:hover,
.deck-button:focus-visible {
  border-color: rgba(127, 238, 100, 0.78);
  color: var(--deck-bright);
}
.deck-tabs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.38rem;
}
.deck-tab {
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border: 1px solid rgba(221, 255, 220, 0.13);
  border-radius: 50%;
  background: rgba(221, 255, 220, 0.04);
  color: var(--deck-soft);
  cursor: pointer;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.72rem;
}
.deck-tab.is-active {
  border-color: rgba(127, 238, 100, 0.75);
  background: rgba(127, 238, 100, 0.17);
  color: var(--deck-green);
  box-shadow: 0 0 22px rgba(127, 238, 100, 0.18);
}
@keyframes deck-pan-right { from { filter: saturate(1.02) contrast(1.02) brightness(0.96); } to { filter: saturate(1.08) contrast(1.05) brightness(1.04); } }
@keyframes deck-pan-left { from { filter: saturate(1.08) contrast(1.04) brightness(1.03); } to { filter: saturate(1.02) contrast(1.02) brightness(0.98); } }
@keyframes deck-breathe { 0% { filter: saturate(1.02) brightness(0.98); } 55% { filter: saturate(1.1) brightness(1.06); } 100% { filter: saturate(1.04) brightness(1); } }
@keyframes deck-gate-pulse { 0% { filter: saturate(1) brightness(1); } 50% { filter: saturate(1.12) brightness(1.08); } 100% { filter: saturate(1.04) brightness(1); } }
@keyframes deck-private-drift { from { filter: saturate(1.02) brightness(0.98); } to { filter: saturate(1.09) brightness(1.05); } }
@keyframes deck-scan { from { transform: translateX(-72%); opacity: 0; } 25% { opacity: 1; } to { transform: translateX(72%); opacity: 0; } }
@keyframes deck-copy-in { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes deck-beat-in { to { opacity: 1; transform: translateY(0); } }
@media (max-width: 920px) {
  .deck-slide {
    display: none;
    grid-template-columns: 1fr;
    min-height: 0;
  }
  .deck-slide.is-active { display: grid; }
  .deck-art img { min-height: 0; aspect-ratio: 16 / 9; }
  .deck-beats { grid-template-columns: 1fr; }
  .deck-controls {
    grid-template-columns: 1fr;
  }
  .deck-button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  .deck-slide,
  .deck-slide.is-active .deck-art img,
  .deck-slide.is-active .deck-art::before,
  .deck-slide.is-active .deck-copy,
  .deck-slide.is-active .deck-beats li {
    animation: none !important;
    transition: none !important;
  }
  .deck-beats li { opacity: 1; transform: none; }
}
</style>

<div class="navcoin-deck" id="navcoinDeck">
<div class="deck-shell">
<div class="deck-topbar">
<span class="deck-eyebrow">Canonical NAVCoin Transaction</span>
<span class="deck-count" id="deckCount" data-deck-count>01 / 14</span>
</div>
<div class="deck-stage">
<section class="deck-slide is-active motion-source" data-slide="1">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-01-source-of-truth-web.png" alt="PFTL official ledger path replacing the retired Ethereum-first demo path."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 01</p>
<h2>PFTL decides what exists.</h2>
<p>The old demo proved market mechanics. The canonical design moves truth back to PostFiat L1, then lets venues trade verified claims.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The retired path treated the Ethereum token too much like the source of truth.</li>
<li style="--i:2" data-step="2">The correct path starts with PFTL proof state and native supply.</li>
<li style="--i:3" data-step="3">Ethereum receives a wrapped claim only after PFTL finality.</li>
</ul>
<span class="deck-term">Rule: source chain first, venue second.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> show a muted retired Ethereum-first path in the background and a bright PFTL-authorized path in the foreground. <strong>Animation:</strong> slow rightward push, scan beam, bullets reveal as the corrected path becomes primary.</div></details>
</div>
</section>

<section class="deck-slide motion-map" data-slide="2">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-02-map-web.png" alt="End-to-end NAVCoin path from reserves to PFTL, wrapping, venue trading, privacy, and exit."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 02</p>
<h2>The whole path is one chain of custody.</h2>
<p>A canonical transaction is not just a swap. It is a proof, an epoch, a supply change, a bridge receipt, a venue trade, and optional privacy.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Proof of reserves establishes verified net assets.</li>
<li style="--i:2" data-step="2">PFTL finalizes the epoch and controls supply.</li>
<li style="--i:3" data-step="3">Bridge and privacy steps are receipts over that source state.</li>
</ul>
<span class="deck-term">Think: official ledger -> trading venues -> private settlement.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> seven stations connected by clean rails: proof, PFTL, bridge, wrapped token, market venue, Orchard, exit. <strong>Animation:</strong> gentle breathing zoom, bullets reveal in transaction order.</div></details>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="3">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-03-proof-of-reserves-web.png" alt="Reserve sources feeding a cryptographic evidence packet."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 03</p>
<h2>First, prove the balance sheet.</h2>
<p>NAVCoin starts with reserve evidence. The proof counts assets, cash, and liabilities, then binds the output to a timestamp and proof hash.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Assets and cash are reserve value.</li>
<li style="--i:2" data-step="2">Liabilities reduce that value.</li>
<li style="--i:3" data-step="3">The result is verified net assets, not a marketing number.</li>
</ul>
<span class="deck-term">Formula: spot + cash - liabilities.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> reserve legs fan into a proof engine and sealed packet. <strong>Animation:</strong> leftward pan and scan line, reinforcing inputs being checked before output.</div></details>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="4">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-04-nav-epoch-web.png" alt="Validators finalizing a NAV epoch around a ledger block."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 04</p>
<h2>PFTL finalizes a NAV epoch.</h2>
<p>The proof is not useful until it becomes protocol state. Validators finalize an epoch that says which NAV number is current and fresh.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Validators verify the proof packet.</li>
<li style="--i:2" data-step="2">The chain records NAV per unit, timestamp, and freshness.</li>
<li style="--i:3" data-step="3">No fresh finalized epoch means no canonical mint.</li>
</ul>
<span class="deck-term">Gate: fresh epoch required.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> validator pillars closing a quorum ring around a finalized NAV block. <strong>Animation:</strong> pulse zoom to make the epoch feel like a confirmed checkpoint.</div></details>
</div>
</section>

<section class="deck-slide motion-map" data-slide="5">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-05-native-mint-web.png" alt="pfUSDC entering a policy gate and producing native NAVCoin on PFTL."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 05</p>
<h2>Native NAVCoin comes before wrapping.</h2>
<p>A user brings counted value into PFTL. The NAV policy then mints or releases native NAVCoin under the current epoch.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The input is counted value, such as pfUSDC.</li>
<li style="--i:2" data-step="2">The policy gate checks the epoch and supply rules.</li>
<li style="--i:3" data-step="3">Native NAVCoin is the official unit.</li>
</ul>
<span class="deck-term">Do not let a venue mint reality.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> simple user-facing flow: stable value -> policy gate -> official ledger -> native units. <strong>Animation:</strong> breathing zoom, bullets reveal like a mint checklist.</div></details>
</div>
</section>

<section class="deck-slide motion-source" data-slide="6">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-06-bridge-wrap-web.png" alt="PFTL bridge receipt minting wrapped NAVCoin on Ethereum."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 06</p>
<h2>Wrapping is a receipt, not a second coin.</h2>
<p>To trade on Ethereum, PFTL debits or locks native NAVCoin, finalizes a receipt, and the Ethereum bridge mints the matching wrapped amount.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Debit or lock on PFTL.</li>
<li style="--i:2" data-step="2">Finalize a bridge packet with amount, asset, recipient, nonce, and destination.</li>
<li style="--i:3" data-step="3">Mint wrapped NAVCoin only from the verified packet.</li>
</ul>
<span class="deck-term">Gate: no verified packet, no wrapped token.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> two chain islands with a guarded receipt packet and replay seals. <strong>Animation:</strong> rightward push, making the receipt feel like it crosses from source to venue.</div></details>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="7">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-07-finality-proof-web.png" alt="Verifier accepting an exact finalized packet and rejecting altered packets."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 07</p>
<h2>The bridge verifies finality.</h2>
<p>The messenger is not trusted. Ethereum needs proof that PFTL actually finalized this exact receipt.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Source chain, destination chain, asset id, amount, recipient, nonce, and expiry are bound.</li>
<li style="--i:2" data-step="2">Changed packets fail.</li>
<li style="--i:3" data-step="3">Used nonces cannot mint twice.</li>
</ul>
<span class="deck-term">Replay protection is part of the asset.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> verifier gate with green accepted packet and red rejected branch. <strong>Animation:</strong> leftward pan and scan line to suggest proof checking.</div></details>
</div>
</section>

<section class="deck-slide motion-source" data-slide="8">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-08-wrapped-token-web.png" alt="Wrapped NAVCoin tethered back to official PFTL ledger state."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 08</p>
<h2>The wrapped token is a claim ticket.</h2>
<p>The Ethereum token can be familiar to wallets and markets, but it is only valid because it traces back to a PFTL receipt.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">It is convenient for Ethereum users.</li>
<li style="--i:2" data-step="2">It is not the official supply ledger.</li>
<li style="--i:3" data-step="3">Its redemption path points back to PFTL.</li>
</ul>
<span class="deck-term">Analogy: resale ticket, not ticket office.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> wrapped token in a transparent shell tethered to official PFTL ledger state. <strong>Animation:</strong> rightward push, emphasizing the tether to source truth.</div></details>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="9">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-09-uniswap-venue-web.png" alt="Market pool with separate canonical NAV and market price gauges."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 09</p>
<h2>Uniswap is a venue, not the oracle.</h2>
<p>The pool gives public liquidity and market price. The canonical NAV per unit still comes from PFTL.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Market price can differ from NAV.</li>
<li style="--i:2" data-step="2">The interface should show both numbers.</li>
<li style="--i:3" data-step="3">The pool cannot mint canonical supply by itself.</li>
</ul>
<span class="deck-term">Show NAV/unit beside market price.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> generic AMM pool with two separate gauges. <strong>Animation:</strong> gate pulse, because the key idea is separation between venue math and canonical proof math.</div></details>
</div>
</section>

<section class="deck-slide motion-private" data-slide="10">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-10-shielding-web.png" alt="Public NAVCoin entering an Orchard shielded note commitment tree."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 10</p>
<h2>Shielding turns a public balance into a private note.</h2>
<p>Orchard is the shielded pool. Instead of a public account balance, the wallet owns private notes and later spends them with proofs.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Public deposit creates a note commitment.</li>
<li style="--i:2" data-step="2">The owner stays wallet-side.</li>
<li style="--i:3" data-step="3">Nullifiers prevent double spend without revealing the note.</li>
</ul>
<span class="deck-term">Orchard = notes + commitments + nullifiers.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> public side passing through a privacy gate into a commitment tree. <strong>Animation:</strong> private drift and scan, suggesting a veil rather than a public ledger entry.</div></details>
</div>
</section>

<section class="deck-slide motion-private" data-slide="11">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-11-orchard-swap-web.png" alt="Zero-knowledge circuit consuming a pfUSDC note and emitting a NAVCoin note."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 11</p>
<h2>The private swap happens inside Orchard.</h2>
<p>The wallet proves that it consumed the right input note and created the right output note without exposing the note details publicly.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Input: private pfUSDC note.</li>
<li style="--i:2" data-step="2">Circuit enforces conservation and allowed exchange.</li>
<li style="--i:3" data-step="3">Output: private NAVCoin note.</li>
</ul>
<span class="deck-term">Validators see proof validity, not wallet path.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> sealed notes entering and leaving a zero-knowledge circuit with a proof check below. <strong>Animation:</strong> private drift, making the note path feel hidden behind the proof.</div></details>
</div>
</section>

<section class="deck-slide motion-private" data-slide="12">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-12-private-egress-web.png" alt="Private Orchard note producing a public exit artifact without revealing note opening."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 12</p>
<h2>Private egress reveals only what the exit needs.</h2>
<p>To return to a public bridge-out flow, the wallet proves it can open a valid note while disclosing only the public exit fields.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The note opening stays private.</li>
<li style="--i:2" data-step="2">The exit artifact is public and verifiable.</li>
<li style="--i:3" data-step="3">Bridge-out and redemption can proceed from that public artifact.</li>
</ul>
<span class="deck-term">Privacy ends only at the chosen public exit.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> hidden note behind veil, proof gate, public receipt and bridge-out path. <strong>Animation:</strong> private drift with reveal bullets, distinguishing hidden ownership from visible exit fields.</div></details>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="13">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-13-gates-web.png" alt="Safety gate dashboard for freshness, arithmetic, supply, replay, privacy proof, and market display."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 13</p>
<h2>Every dangerous shortcut gets a gate.</h2>
<p>The system should fail closed when proof, supply, bridge, or privacy rules do not match.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Stale reserve proofs cannot power fresh minting.</li>
<li style="--i:2" data-step="2">Bridge packets cannot be replayed or rewritten.</li>
<li style="--i:3" data-step="3">Privacy proofs must verify before state changes.</li>
</ul>
<span class="deck-term">Good UX says which gate failed.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> six safety gates in a control-room grid with one closed stale gate. <strong>Animation:</strong> pulsing gate zoom and staged bullet reveal.</div></details>
</div>
</section>

<section class="deck-slide motion-map" data-slide="14">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-14-complete-path-web.png" alt="Complete canonical NAVCoin transaction map from reserve proof through PFTL, bridge, venue, Orchard, and exit."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 14</p>
<h2>The transaction is canonical because every claim points home.</h2>
<p>The final design can use Uniswap and private settlement without asking either one to be the official truth source.</p>
<ul class="deck-beats">
<li style="--i:1" data-step="1">PFTL owns proof state and native supply.</li>
<li style="--i:2" data-step="2">Ethereum trades a verified wrapper.</li>
<li style="--i:3" data-step="3">Orchard hides wallet movement while preserving proof validity.</li>
</ul>
<span class="deck-term">Canonical does not mean single venue. It means single source of truth.</span>
<details class="slide-notes"><summary>Slide instructions</summary><div><strong>Image:</strong> complete circular transaction map with all stations visible and empty callout positions. <strong>Animation:</strong> gentle breathing zoom, final bullets summarize source, venue, and privacy roles.</div></details>
</div>
</section>
</div>

<div class="deck-controls" aria-label="Slide controls">
<button class="deck-button" type="button" data-prev="true">Previous</button>
<div class="deck-tabs" role="tablist" aria-label="Slides">
<button class="deck-tab is-active" type="button" data-goto="1" aria-label="Slide 1">01</button>
<button class="deck-tab" type="button" data-goto="2" aria-label="Slide 2">02</button>
<button class="deck-tab" type="button" data-goto="3" aria-label="Slide 3">03</button>
<button class="deck-tab" type="button" data-goto="4" aria-label="Slide 4">04</button>
<button class="deck-tab" type="button" data-goto="5" aria-label="Slide 5">05</button>
<button class="deck-tab" type="button" data-goto="6" aria-label="Slide 6">06</button>
<button class="deck-tab" type="button" data-goto="7" aria-label="Slide 7">07</button>
<button class="deck-tab" type="button" data-goto="8" aria-label="Slide 8">08</button>
<button class="deck-tab" type="button" data-goto="9" aria-label="Slide 9">09</button>
<button class="deck-tab" type="button" data-goto="10" aria-label="Slide 10">10</button>
<button class="deck-tab" type="button" data-goto="11" aria-label="Slide 11">11</button>
<button class="deck-tab" type="button" data-goto="12" aria-label="Slide 12">12</button>
<button class="deck-tab" type="button" data-goto="13" aria-label="Slide 13">13</button>
<button class="deck-tab" type="button" data-goto="14" aria-label="Slide 14">14</button>
</div>
<button class="deck-button" type="button" data-next="true">Next</button>
</div>
</div>
</div>

<script>
(function () {
const deck = document.getElementById("navcoinDeck");
if (!deck) return;
const slides = Array.from(deck.querySelectorAll(".deck-slide"));
const tabs = Array.from(deck.querySelectorAll(".deck-tab"));
const count = deck.querySelector("[data-deck-count]");
let active = 1;
const total = slides.length;

function show(index) {
active = ((index - 1 + total) % total) + 1;
slides.forEach((slide) => {
const selected = Number(slide.dataset.slide) === active;
slide.classList.toggle("is-active", selected);
slide.setAttribute("aria-hidden", selected ? "false" : "true");
});
tabs.forEach((tab) => {
const selected = Number(tab.dataset.goto) === active;
tab.classList.toggle("is-active", selected);
tab.setAttribute("aria-selected", selected ? "true" : "false");
});
if (count) count.textContent = String(active).padStart(2, "0") + " / " + String(total).padStart(2, "0");
}

deck.querySelector("[data-prev='true']")?.addEventListener("click", () => show(active - 1));
deck.querySelector("[data-next='true']")?.addEventListener("click", () => show(active + 1));
tabs.forEach((tab) => tab.addEventListener("click", () => show(Number(tab.dataset.goto))));
document.addEventListener("keydown", (event) => {
const tag = String(event.target?.tagName || "").toLowerCase();
if (tag === "input" || tag === "textarea" || event.target?.isContentEditable) return;
if (event.key === "ArrowLeft") show(active - 1);
if (event.key === "ArrowRight") show(active + 1);
});
show(active);
})();
</script>
