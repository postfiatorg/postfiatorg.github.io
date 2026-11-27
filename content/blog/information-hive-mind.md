---
title: "The Post Fiat Information Hive Mind: Triangulated Expertise and Accelerated Alpha"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How Task Node matches domain-verified contributors to Finance Hub's crypto and perp-backed equity models, enforces an in-memory hash-only MNPI firewall, and pays accelerated rewards for verified alpha."
author: "Post Fiat"
categories:
  - Collective Intelligence
tags:
  - Post Fiat
  - Information Hive Mind
  - Finance Hub
  - Alpha
  - Task Node
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Task Node already knows what its contributors are genuinely good at from the work they complete. Finance Hub maintains ~60 live research models across crypto protocols and liquid megacap equities with perpetual futures.

The **Post Fiat Information Hive Mind** connects the two — turning distributed, verifiable domain expertise into sharper research models and paying real alpha fast.

## Open Automatic Matching Without Leaking Gated Models

You do **not** need Finance Hub membership to contribute. Any Task Node user with an **Expert badge** (`>= 20` completed personal tasks, score `>= 80`) or a verified capability profile can confirm suggested knowledge areas and match automatically to covered names in `hub/coverage_manifest.json` (crypto protocols/tokens plus liquid megacap equities with perps; paid listed-equity interviews activate after legal counsel sign-off on attestation wording).

Two hard privacy boundaries stay enforced at every step:

1. **Your private Task Node data stays private:** Raw Deep Memory, private chat, context docs, and task evidence never reach company agents, reviewers, or Finance Hub. Agents receive only your confirmed knowledge areas, declared relationship, and a user-approved summary.
2. **Finance Hub models stay gated:** Non-Finance-Hub contributors interview strictly against a separate public-safe index (`agent_brief_public.json` + build-checked public questions). Zero gated model targets, member open questions, or member pooled claims ever cross into a non-member interview.

## Triangulate First, Then Probe Real Blind Spots

Every covered company or protocol gets a two-phase AI research agent:

- **Phase 1 (Triangulation):** Establishes what you directly observe in public or market-participant life (operator, builder, customer, trader, or public-data analyst).
- **Phase 2 (Targeted Questions):** Probes bounded open questions and structures concrete claims (`confirms`, `refines`, or `challenges`) signed by your wallet at submission time alongside an automatic snapshot of `model_estimate_before` and `market_consensus_before` plus a dated public `check_event`.

## Hard In-Memory MNPI Firewall (Zero Retention)

Before Phase 1 starts, you declare your relationship to the company and attest that you will not share material non-public information (MNPI) or NDA-bound secrets. Current employees and anyone under MNPI/NDA duties on a company are blocked from interviewing on that name.

Every message is screened **in RAM on the API handler BEFORE writing to the database or forwarding to any LLM** (using zero-data-retention endpoints):

- **`pass`:** Proceeds normally.
- **`redact`:** Strips flagged spans and lets you review before saving.
- **`refuse`:** Discards raw text immediately in memory — never written to Postgres or chat history. Only `(account, company, timestamp, reason_code, sha256)` enters the compliance log.

Any published insight can also be removed from Finance Hub in `< 1` second via a server-side takedown overlay without waiting for a model rebuild.

## Human Approval & Accelerated Alpha Rewards

A prompt-injection-hardened Reviewer Agent clusters duplicate claims, flags corroboration vs. conflict, and queues proposals for the **human model owner** (who cannot approve their own claims). When the model owner merges an edit and cites your contribution in the model `CHANGELOG`, a signed webhook unlocks rewards through Task Node's badge-capped payout pipeline:

- **Fast citation payout:** `$10–$50` PFT equivalent immediately on `CHANGELOG` citation (split across corroborated duplicates in the same cluster).
- **Accelerated alpha bonus (`2x–5x`):** Triggered when your dated public `check_event` proves out — weighted highest for well-argued contrarian `challenges` that pull model estimates closer to reported reality.
- **Anti-gaming:** Uncheckable claims earn only if cited in an applied model edit; hedging contradictory stances on the same company and check event is blocked; falsified claims pay zero bonus and lower domain weight.

## Live UAT Evidence

- **Encrypted Pillar 2 accepted claim packet (`postfiatl1v2`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **Accelerated alpha reward payout (`order_hash`):** `[INSERT LIVE DEVNET/MAINNET TX HASH AFTER UAT]`
- **MNPI hash-only refusal verification & `CHANGELOG` citation screenshot:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`

Read the full rules on matching, MNPI screening, attribution, and alpha multipliers in the [Information Hive Mind Guide](/docs/information-hive-mind/).
