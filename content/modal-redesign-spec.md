---
title: "Modal-Inspired Homepage Redesign Spec"
layout: "single"
url: "/modal-redesign-spec/"
summary: "Spec for the alternate Post Fiat homepage redesign."
---

# Modal-Inspired Homepage Redesign Spec

## Goal

Create an alternate Post Fiat homepage that keeps the current rough page copy and product claims, but makes the site feel more like high-performance AI infrastructure: dark, precise, visual, fast, and developer-literate.

The current homepage remains unchanged. The redesign lives at `/modal-redesign/`.

## Design Direction

- Black-first canvas with pale green and electric green accents.
- Pill navigation, compact buttons, restrained borders, and strong spacing.
- Large centered hero with a live animated infrastructure canvas behind it.
- Section rhythm alternates between dark technical bands and pale green evidence bands.
- Repeated cards are used only for product/use-case items, not as wrappers around whole page sections.
- Copy stays close to the current homepage: AGI coordination, XRP-speed settlement, validator selection, privacy, Task Node participation, PFT utility, validator operation, and capital-markets use cases.

## Page Structure

1. Hero
   - Headline: "A Decentralized Method to Merge with AGI"
   - Current rough positioning paragraph retained.
   - Primary CTAs: whitepaper, Task Node, validator setup, community.
   - Animated canvas visualizes a green infrastructure plane, validator nodes, and moving signal paths.

2. Proof Strip
   - Compact bordered strip for the core proof points: live testnet, validator domains, public benchmark, Task Node, whitepaper, explorer.

3. Task Node Feed
   - Lower-page operating evidence section titled "The Hive Mind in Action."
   - Shows recent Task Node activity with category, timestamp, semi-anonymous node id, ticker tags, and PFTL proof links.
   - Uses a smooth horizontal carousel: centered active card, visible adjacent cards, arrow controls, progress dots, and automatic rotation.
   - Ships with static fallback cards, tries the public activity endpoint, and falls back to the public AGTI feed page if browser CORS blocks the API.

4. How It Works
   - Four technical rows:
   - XRP is the right primitive.
   - Post Fiat fixes what XRP does not.
   - Built for capital markets, not generic payment theater.
   - Task Node turns community into collective intelligence.
   - Sticky side rail highlights the active row during scroll.
   - Active rows brighten, animate code/metric panels, and run a signal sweep across the visual.

5. Public Artifacts
   - Pale green band with five repeated artifact cards:
   - Whitepaper, Task Node, Validator Benchmark, Validator Setup, Community.

6. Use Cases
   - Horizontal scroller/card row:
   - ETFs and indexing, compliance and private coordination, buy-side expert networks, validator governance.
   - Cards use distinct animated art instead of generic illustration: index matrix, privacy lock, expert network, and validator topology.

7. Security and Governance
   - Accordion-style list for live testnet, validator scoring, privacy, and PFT coordination.
   - Visual system stack beside the accordion.

8. Founder and Market Credibility
   - Keeps existing rough proof points around Alex Good, background, and capital/market credibility.

9. Final CTA
   - "Join before the coordination layer hardens."
   - CTAs repeat the practical next steps.

## Interaction Requirements

- Hero canvas animates subtly and degrades gracefully if JavaScript is disabled.
- Mobile menu opens from the pill header without changing the current homepage.
- Header and footer include canonical Post Fiat links for GitHub, X, and Discord.
- Task Node Feed tries `https://pftasks-api.fly.dev/activity/public-feed?limit=24` and falls back to `https://agtico.github.io/task-node-feed/`.
- Task Node Feed automatically rotates cards, pauses on hover/focus/touch interaction, and respects `prefers-reduced-motion`.
- How It Works keeps the sticky rail, copy, and side art synchronized while scrolling.
- Governance section uses accessible buttons with `aria-expanded`.
- Use-case strip can be horizontally scrolled on mobile and desktop.
- Respect `prefers-reduced-motion` by lowering canvas frame rate and disabling large transforms.

## Implementation Notes

- New Hugo content file: `content/modal-redesign.md`.
- New Hugo layout: `layouts/page/modal_redesign.html`.
- This spec is published through `content/modal-redesign-spec.md`.
- No current homepage file is deleted or replaced.
- The current homepage still uses `layouts/index.html` and `layouts/page/oai_redesign.html`.
