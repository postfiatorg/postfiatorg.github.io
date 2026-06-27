---
title: "How to Turn USDC Into a651 for Uniswap"
date: 2026-06-27T00:00:00Z
url: "/canonical-navcoin-transaction/"
aliases:
  - "/blog/canonical-navcoin-transaction/"
  - "/blog/canonical-navcoin-transaction-primer/"
summary: "A beginner-friendly visual walkthrough of the full route: USDC to pfUSDC on PFTL, private Orchard swap into a651, private egress, atomic handoff, wrapped a651, and the Uniswap a651/USDC pool."
description: "Slide deck explaining the full USDC to a651 route: PFTL proof of reserves, pfUSDC, Orchard private swap, private egress, atomic handoff, wrapped a651, and the Uniswap a651/USDC pool."
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

This is the beginner-friendly visual primer for the full route: USDC into PFTL, private a651 swap, atomic handoff, and Uniswap-side a651. The longer prose version has been moved to [research notes](/research/canonical-navcoin-transaction/).

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
<span class="deck-count" id="deckCount" data-deck-count>01 / 27</span>
</div>
<div class="deck-stage">
<section class="deck-slide is-active motion-source" data-slide="1">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-01-user-question-web.png" alt="Centered horizontal route with five large boxes: `USDC` → `PFTL record` → `Private swap` → `Ethereum-side a651` → `Uniswap pool`. Use mint for PFTL, purple for private swap,..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 01</p>
<h2>How do I turn USDC into a651 I can trade on Uniswap?</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">a651 is the asset you want; the Uniswap pool is the public a651/USDC trading pair.</li>
<li style="--i:2" data-step="2">PFTL keeps the official a651 record; pfUSDC is USDC recorded on PFTL; Orchard is the private swap area.</li>
<li style="--i:3" data-step="3">Wrapped a651 is the Ethereum-side claim; atomic handoff means lock-and-release, or refund.</li>
</ul>
<span class="deck-term">The question</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="2">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-02-nav-accounting-web.png" alt="Formula diagram. Left group: `assets` + `cash`; red subtraction box: `liabilities`; center amber gate: `accounting check`; right mint output: `NAV/unit`. Bottom small note:..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 02</p>
<h2>NAV is the accounting value behind a651.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">NAV means net asset value: reserve assets plus cash, minus liabilities.</li>
<li style="--i:2" data-step="2">NAV/unit means that value divided by valid units.</li>
<li style="--i:3" data-step="3">A NAVCoin follows those rules; a651 is the NAVCoin asset in this flow.</li>
</ul>
<span class="deck-term">What NAV means</span>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="3">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-03-proof-of-reserves-web.png" alt="Left table group labeled `reserve evidence` with rows `assets`, `cash`, `liabilities`. Center amber box `math check`. Right mint packet labeled `proof packet` with four fields:..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 03</p>
<h2>Proof of reserves checks what backs the coin.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Proof of reserves is the evidence packet behind the NAV number.</li>
<li style="--i:2" data-step="2">It counts assets and cash, subtracts liabilities, and records time plus an evidence fingerprint.</li>
<li style="--i:3" data-step="3">It makes the process checkable; it does not make a dishonest data source honest.</li>
</ul>
<span class="deck-term">Checked reserves</span>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="4">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-04-pftl-official-record-web.png" alt="Two-column relationship diagram. Left mint column: `PFTL official record` with box `a651 supply`. Right cyan column: `Ethereum / Uniswap trading side` with box `tradable a651..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 04</p>
<h2>PFTL decides what a651 officially exists.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">PFTL means Post Fiat L1, the base blockchain that records official a651 state.</li>
<li style="--i:2" data-step="2">Uniswap is where people trade; PFTL is where the official a651 record is kept.</li>
<li style="--i:3" data-step="3">A receipt is a public record of a PFTL action, and Ethereum-side a651 must trace back to one.</li>
</ul>
<span class="deck-term">Where truth lives</span>
</div>
</section>

<section class="deck-slide motion-private" data-slide="5">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-05-nav-epoch-web.png" alt="Left: `proof packet`. Center: validator checklist inside a ring of six small validator nodes; checklist items `math`, `fresh`, `policy`, `supply`. Right: mint block `NAV epoch`..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 05</p>
<h2>A NAV epoch is one accepted NAV snapshot.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">A NAV epoch is one finalized snapshot of NAV at a specific time.</li>
<li style="--i:2" data-step="2">Validators—the chain’s checkers—accept the proof only if the math and freshness pass.</li>
<li style="--i:3" data-step="3">No fresh epoch means no official a651 output.</li>
</ul>
<span class="deck-term">Fresh NAV snapshot</span>
</div>
</section>

<section class="deck-slide motion-source" data-slide="6">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-06-public-private-map-web.png" alt="Four horizontal sample lanes: `PFTL public state` in mint, `Orchard private notes` in purple with dashed boundary, `Ethereum / Uniswap public side` in cyan, `locks / rejects`..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 06</p>
<h2>Some steps are public; the middle swap is private.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Public means anyone can see the ledger event.</li>
<li style="--i:2" data-step="2">Private means the chain checks a proof while wallet details stay hidden.</li>
<li style="--i:3" data-step="3">Mint is PFTL, purple is Orchard, cyan is Ethereum/Uniswap, amber is locks, red is reject or refund.</li>
</ul>
<span class="deck-term">Read the map</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="7">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-07-usdc-start-web.png" alt="Left cyan box `USDC source`. Center box `your wallet`. Right faded mint box `next: PFTL record`. Use a public-lane label across the top: `public start`."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 07</p>
<h2>Step 1: you start with USDC.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Your starting asset is normal USDC in a wallet or exchange route.</li>
<li style="--i:2" data-step="2">At this moment, nothing private has happened.</li>
<li style="--i:3" data-step="3">Next, you create a PFTL-recorded USDC balance.</li>
</ul>
<span class="deck-term">Starting asset</span>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="8">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-08-pfusdc-bridge-in-web.png" alt="Two lanes. Top cyan lane `starting USDC`; bottom mint lane `PFTL`. Arrow from `USDC` to amber gate `bridge-in checks`, then down to mint box `pfUSDC balance`. Field chips near..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 08</p>
<h2>Step 2: USDC becomes pfUSDC on PFTL.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Bridge-in means a checked move from your starting USDC into a matching PFTL record.</li>
<li style="--i:2" data-step="2">pfUSDC means that PFTL record of USDC.</li>
<li style="--i:3" data-step="3">Public: asset, amount, recipient, and one-use id. Private: none yet.</li>
</ul>
<span class="deck-term">USDC on PFTL</span>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="9">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-09-shield-pfusdc-web.png" alt="Left mint public box `pfUSDC balance`. Center purple dashed boundary labeled `Orchard`. Amber/purple action box `shield`. Right purple wallet-side box `private note`. Below it,..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 09</p>
<h2>Step 3: put pfUSDC behind the privacy boundary.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Orchard is the private transaction area inside PFTL.</li>
<li style="--i:2" data-step="2">A private note is a sealed wallet record; the chain only sees a public fingerprint called a commitment.</li>
<li style="--i:3" data-step="3">Public: deposit and commitment. Private: owner, opening, and later route.</li>
</ul>
<span class="deck-term">Enter privacy</span>
</div>
</section>

<section class="deck-slide motion-private" data-slide="10">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-10-nullifier-web.png" alt="Purple `private note` flows into amber `spend proof`. Output public marker `nullifier`. A second attempted spend goes to red box `seen nullifier: reject`."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 10</p>
<h2>A nullifier lets privacy and accounting work together.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">A nullifier is a public spent marker created when a private note is used.</li>
<li style="--i:2" data-step="2">It lets validators reject the same note twice without learning which note it was.</li>
<li style="--i:3" data-step="3">Public: nullifier. Private: note opening and owner.</li>
</ul>
<span class="deck-term">Stop double spending</span>
</div>
</section>

<section class="deck-slide motion-source" data-slide="11">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-11-private-orchard-swap-web.png" alt="Purple block diagram. Left `pfUSDC note` enters center `Orchard swap`. Right outputs `a651 note` and optional `change note`. Bottom public lane shows `proof + nullifier` going..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 11</p>
<h2>Step 4: Orchard swaps pfUSDC into private a651.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Inside Orchard, your wallet spends a shielded pfUSDC note and creates a private a651 note.</li>
<li style="--i:2" data-step="2">Validators check proof validity and the one-use nullifier, not your wallet path.</li>
<li style="--i:3" data-step="3">Public: proof and nullifier. Private: input note, output note, route.</li>
</ul>
<span class="deck-term">Private swap</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="12">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-12-swap-proof-checks-web.png" alt="Center amber/purple gate `swap proof`. Checklist items: `real note`, `nullifier unused`, `exchange allowed`, `value balanced`. Green pass arrow to `new note accepted`; red fail..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 12</p>
<h2>The chain checks the rule, not your private route.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The proof says: a real note was spent once, the exchange is allowed under the current NAV epoch, and values balance.</li>
<li style="--i:2" data-step="2">Validators accept the proof without reading the sealed notes.</li>
<li style="--i:3" data-step="3">If any check fails, nothing changes.</li>
</ul>
<span class="deck-term">Proof checks</span>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="13">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-13-private-a651-note-web.png" alt="Purple Orchard zone with large sealed box `private a651 note`. Two arrows: loop arrow `stay private` and forward arrow `exit to public next`. Cyan Uniswap pool is visible far..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 13</p>
<h2>After the swap, a651 is still private.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">After the swap, your wallet owns a private a651 note.</li>
<li style="--i:2" data-step="2">Uniswap cannot trade that sealed note directly.</li>
<li style="--i:3" data-step="3">To reach Uniswap, you must exit to public PFTL a651.</li>
</ul>
<span class="deck-term">Private result</span>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="14">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-14-private-egress-web.png" alt="Left purple `private a651 note` behind dashed boundary. Center amber gate `egress proof`. Right mint boxes `public PFTL a651` and `exit receipt`. Four public field chips:..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 14</p>
<h2>Step 5: private egress creates public PFTL a651.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Private egress means leaving Orchard while revealing only the fields needed for public settlement.</li>
<li style="--i:2" data-step="2">Your wallet proves the private a651 note is valid and unspent.</li>
<li style="--i:3" data-step="3">Public: asset, amount, destination, receipt id. Private: old note details.</li>
</ul>
<span class="deck-term">Leave privacy</span>
</div>
</section>

<section class="deck-slide motion-private" data-slide="15">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-15-public-pftl-a651-web.png" alt="Mint ledger panel `PFTL public ledger` with `public a651 balance` and `exit receipt`. Arrow to amber box `ready to lock`. Cyan Ethereum-side box `waiting for verified receipt`..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 15</p>
<h2>Public PFTL a651 is what gets locked.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The public PFTL balance is the official a651 that can be locked for handoff.</li>
<li style="--i:2" data-step="2">This public step is intentional: the Ethereum release needs a visible source record.</li>
<li style="--i:3" data-step="3">Public: balance, exit receipt, and later lock.</li>
</ul>
<span class="deck-term">Official handoff input</span>
</div>
</section>

<section class="deck-slide motion-source" data-slide="16">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-16-atomic-handoff-overview-web.png" alt="Three horizontal lanes. Top mint lane `PFTL side`: `public a651` → amber `lock`. Middle cyan lane `Ethereum side`: `verify receipt` → `release a651`. Bottom red/amber lane..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 16</p>
<h2>Step 6: lock on PFTL, release on Ethereum, or refund.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Atomic handoff means lock on PFTL, verify on Ethereum, then release matching Ethereum-side a651.</li>
<li style="--i:2" data-step="2">If the verified release does not happen before timeout, the PFTL lock refunds.</li>
<li style="--i:3" data-step="3">The target design does not rely on a middle party paying from inventory.</li>
</ul>
<span class="deck-term">Atomic handoff</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="17">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-17-pftl-lock-fields-web.png" alt="Center amber lock document `PFTL lock receipt`. Field chips: `asset a651`, `amount`, `recipient`, `destination`, `deadline`, `swap id`. Green arrow `exact match`. Red reject..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 17</p>
<h2>The PFTL lock says exactly what can be released.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">The lock records the exact deal: asset, amount, recipient, destination, deadline, and swap id.</li>
<li style="--i:2" data-step="2">The swap id is the shared label that ties both sides to the same handoff.</li>
<li style="--i:3" data-step="3">Changed fields, expired locks, or reused ids must fail.</li>
</ul>
<span class="deck-term">Lock details</span>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="18">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-18-ethereum-verifier-web.png" alt="Left gray `relayer messenger` carrying `lock receipt`. Center cyan/amber `Ethereum verifier` with checklist `PFTL finalized`, `fields match`, `deadline ok`, `id unused`. Right..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 18</p>
<h2>Ethereum should verify the PFTL lock receipt.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">A relayer is just a messenger; it may carry the receipt but should not be trusted.</li>
<li style="--i:2" data-step="2">Finality means PFTL has settled this exact lock as chain state.</li>
<li style="--i:3" data-step="3">Ethereum verifies finality and fields before wrapped a651 can be released.</li>
</ul>
<span class="deck-term">Verify, don’t trust</span>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="19">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-19-wrapped-a651-web.png" alt="Left mint `PFTL locked a651`. Center `bridge accounting` with `used ids` and `outstanding wrapped`. Right cyan `wrapped a651 contract`. Tether line from contract back to PFTL..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 19</p>
<h2>Wrapped a651 is useful, but it is not the official ledger.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">A wrapped token is an Ethereum token that represents a PFTL-locked claim.</li>
<li style="--i:2" data-step="2">Wrapped a651 can move in Ethereum wallets and Uniswap, but it is not the official supply record.</li>
<li style="--i:3" data-step="3">Public: mint/release event on Ethereum. Source of truth: PFTL.</li>
</ul>
<span class="deck-term">Wrapped token</span>
</div>
</section>

<section class="deck-slide motion-private" data-slide="20">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-20-settle-or-refund-web.png" alt="State machine. `start` → `locked` → split. Green success path: `verified` → `released` → `settled`. Red/amber failure path: `timeout` → `refunded`. Red side boxes: `replay..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 20</p>
<h2>Atomic means both sides settle, or the lock refunds.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Success: lock → verified receipt → wrapped a651 released → lock consumed.</li>
<li style="--i:2" data-step="2">Failure: timeout → refund public PFTL a651.</li>
<li style="--i:3" data-step="3">A used receipt or expired lock must be rejected.</li>
</ul>
<span class="deck-term">Success or refund</span>
</div>
</section>

<section class="deck-slide motion-source" data-slide="21">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-21-uniswap-pool-web.png" alt="Cyan pool box `Uniswap a651/USDC pool` with two reserve boxes: `wrapped a651` and `USDC`. Arrows `buy` and `sell`. Separate mint side panel `PFTL NAV/unit` with no arrow into..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 21</p>
<h2>Step 7: trade wrapped a651 in the a651/USDC pool.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">A Uniswap pool is a public smart-contract market with two reserves.</li>
<li style="--i:2" data-step="2">The a651/USDC pool lets users swap between wrapped a651 and USDC.</li>
<li style="--i:3" data-step="3">Pool price is market price; PFTL NAV is the accounting value.</li>
</ul>
<span class="deck-term">The trading pool</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="22">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-22-complete-route-web.png" alt="Four horizontal lanes: `Public start`, `PFTL public`, `Orchard private`, `Ethereum / Uniswap`. Numbered boxes 1–10: `USDC`, `pfUSDC`, `shielded note`, `Orchard swap`, `private..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 22</p>
<h2>The complete path: USDC to Uniswap-side a651.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">USDC → PFTL/pfUSDC → shielded pfUSDC note → private Orchard swap → private a651 note.</li>
<li style="--i:2" data-step="2">Then: private egress → public PFTL a651 → atomic lock/handoff → Ethereum-side wrapped a651.</li>
<li style="--i:3" data-step="3">Finally: trade in the Uniswap a651/USDC pool.</li>
</ul>
<span class="deck-term">Complete route</span>
</div>
</section>

<section class="deck-slide motion-proof" data-slide="23">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-23-public-private-checklist-web.png" alt="Three-band diagram. Left and right bands labeled `public edges`; middle purple band labeled `private middle`. Place small stage chips: public bands contain `USDC`, `pfUSDC`,..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 23</p>
<h2>The edges are public; the middle route is private.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Public edges: bridge-in, egress, PFTL lock, Ethereum release, and Uniswap trade.</li>
<li style="--i:2" data-step="2">Private middle: shielded notes and the Orchard swap route.</li>
<li style="--i:3" data-step="3">The chain still checks proofs and nullifiers, so privacy does not remove accounting.</li>
</ul>
<span class="deck-term">Visibility checklist</span>
</div>
</section>

<section class="deck-slide motion-gate" data-slide="24">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-24-trust-model-web.png" alt="Maturity ladder from left to right. Left amber `staged: committee signs`. Middle amber/cyan `staged+: challenge window`. Right mint/cyan `final target: contract verifies PFTL..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 24</p>
<h2>Do not call it trustless unless the contract verifies the proof.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Trustless means contracts verify proof instead of trusting a messenger or committee.</li>
<li style="--i:2" data-step="2">Final target: direct PFTL verification or a compact proof; staged versions may use committee signatures or challenge windows.</li>
<li style="--i:3" data-step="3">Do not call a staged bridge production-trustless without deployment and verification evidence.</li>
</ul>
<span class="deck-term">What can be trusted</span>
</div>
</section>

<section class="deck-slide motion-private" data-slide="25">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-25-safety-gates-web.png" alt="2x4 gate matrix. Tiles: `fresh NAV`, `reserve math`, `supply policy`, `PFTL finality`, `one-use id`, `nullifier`, `egress proof`, `market labels`. Each tile has a small pass..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 25</p>
<h2>Every dangerous shortcut gets a gate.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">Fresh proof, supply rules, finality, one-use ids, nullifiers, and egress proofs all must pass.</li>
<li style="--i:2" data-step="2">Good UX should explain which gate failed.</li>
<li style="--i:3" data-step="3">Fail closed: no proof, no mint; reused id, no release; bad nullifier, no spend.</li>
</ul>
<span class="deck-term">Fail closed</span>
</div>
</section>

<section class="deck-slide motion-source" data-slide="26">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-26-final-summary-web.png" alt="Three large panels. Panel 1 mint: `enter PFTL: USDC → pfUSDC`. Panel 2 purple: `swap privately: pfUSDC note → a651 note`. Panel 3 cyan/amber: `handoff + trade: lock → wrapped..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 26</p>
<h2>One route, one official record, one trading pool.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">You turn USDC into pfUSDC on PFTL, privately swap it into a651, then egress to public PFTL a651.</li>
<li style="--i:2" data-step="2">PFTL keeps the official record; Ethereum-side wrapped a651 exists only after a verified lock/handoff.</li>
<li style="--i:3" data-step="3">Uniswap is where wrapped a651 trades against USDC; it is not where official supply is decided.</li>
</ul>
<span class="deck-term">The answer</span>
</div>
</section>

<section class="deck-slide motion-map" data-slide="27">
<figure class="deck-art"><img src="/navcoin/canonical-transaction/slide-27-evidence-boundary-web.png" alt="Three-column appendix checklist. Green column `design claim`: `PFTL source`, `private middle`, `atomic target`. Amber column `needs evidence`: `contracts`, `verifier`, `pool`,..."></figure>
<div class="deck-copy">
<p class="deck-kicker">Slide 27</p>
<h2>This explains the design path; production claims need evidence.</h2>
<ul class="deck-beats">
<li style="--i:1" data-step="1">This packet explains the official design path; it does not prove the final bridge is live.</li>
<li style="--i:2" data-step="2">Production evidence should include deployed contract addresses, verifier method, pool address, proof freshness source, and replay/nullifier checks.</li>
<li style="--i:3" data-step="3">If any step is manual or committee-signed, label it staged.</li>
</ul>
<span class="deck-term">Evidence boundary</span>
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
<button class="deck-tab" type="button" data-goto="15" aria-label="Slide 15">15</button>
<button class="deck-tab" type="button" data-goto="16" aria-label="Slide 16">16</button>
<button class="deck-tab" type="button" data-goto="17" aria-label="Slide 17">17</button>
<button class="deck-tab" type="button" data-goto="18" aria-label="Slide 18">18</button>
<button class="deck-tab" type="button" data-goto="19" aria-label="Slide 19">19</button>
<button class="deck-tab" type="button" data-goto="20" aria-label="Slide 20">20</button>
<button class="deck-tab" type="button" data-goto="21" aria-label="Slide 21">21</button>
<button class="deck-tab" type="button" data-goto="22" aria-label="Slide 22">22</button>
<button class="deck-tab" type="button" data-goto="23" aria-label="Slide 23">23</button>
<button class="deck-tab" type="button" data-goto="24" aria-label="Slide 24">24</button>
<button class="deck-tab" type="button" data-goto="25" aria-label="Slide 25">25</button>
<button class="deck-tab" type="button" data-goto="26" aria-label="Slide 26">26</button>
<button class="deck-tab" type="button" data-goto="27" aria-label="Slide 27">27</button>
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
