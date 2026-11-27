---
title: "Post Fiat Finance Hub: A Daily Research Desk Earned by Validators and Top-30 Contributors"
date: 2026-11-27T00:00:00Z
draft: true
summary: "How Post Fiat Finance Hub pairs ~60 live company and crypto models, Goodbrief, and the GoodAlexander Library with active validator liveness and a daily Top-30 Task Node contributor tier."
author: "Post Fiat"
categories:
  - Research
tags:
  - Post Fiat
  - Finance Hub
  - Goodbrief
  - Validators
  - Task Node
---

<!-- Gate #4 Draft: ready for founder review & publish after Gate #2 UAT live tx hashes/screenshots are inserted -->

Good infrastructure incentives shouldn't rely on endless token emissions. **Post Fiat Finance Hub** is a daily research desk inside Task Node — ~60 live GoodAlexander company and crypto models, the **Goodbrief** macro roundup, and the **GoodAlexander Library** — unlocked strictly by running an active validator or earning a Top-30 contributor seat.

## Two Clean Ways In

Finance Hub access (`finance_hub` tier) is never sold via subscriptions. There are two independent ways to qualify:

1. **Active Post Fiat L1v2 Validator:** Stay active in the on-chain validator registry and meet the latency-fair uptime rule (`>= 95%` participation over `25` of `30` completed height-days, with Day-0 ramp-in, a 14-day grace window, and fast 3-day recovery). Active validators also keep **GoodAlexander Research API keys** (validators-only) and `$20/month` in Task Node USD credit.
2. **Top 30 Task Node Contributor:** Evaluated by a deterministic daily UTC snapshot of the existing Task Node leaderboard formula (`3 * network_tasks + personal_tasks + rewarded_pft / 25,000 + alignment`) across **all non-blacklisted accounts** (so private contributors still qualify without making their profile public). Active validators are excluded from the Top-30 pool so they never crowd out contributors. Reach rank `1–30` to enter, keep access down to rank `35` (zero 30/31 flicker), and get a 7-day grace window (with a 30-day anti-bounce cooldown) if you drop to rank `36+`.

## One "Today" Morning Desk

Old Equities / Crypto / Macro tabs are now filters on one unified **Today** landing page ordered for how you actually read markets in the morning:

1. **Goodbrief summary** (decoupled into its own independent signed publication so a model build error never delays the morning brief)
2. **Just reported** (results vs. consensus, model state, call takeaway)
3. **Model updates** (target and upside before -> after, plus why it moved)
4. **Reporting this week** (with options-implied moves)
5. **Live movers** (dated last session on non-trading days)
6. **Coverage changes** (exact added and dropped models)

Starred **watchlist** names float to the top of every section, ticker search works instantaneously, and **"New since your last visit"** markers stay synced across refreshes, browser tabs, and mobile until you click **Mark caught up**. Every company page also connects directly to [Pillar 10 (Information Hive Mind)](/docs/information-hive-mind/) via **Contributor insights** and an **Ask the agent** button.

## Hardened Isolation & Signed Publishing

We rebuilt the security boundary behind Finance Hub before opening it to Top-30 seats:

- **Isolated viewer origin (`hub-viewer.postfiat.org`):** The `ga-models` viewer runs off `tasknode.postfiat.org`, communicating via strict origin-checked `postMessage` and short-lived scoped tokens. Even a compromised publishing key can never execute script on Task Node's wallet origin.
- **Zero-exfiltration Goodbrief sandbox:** Full HTML Goodbrief renders inside `<iframe sandbox="allow-scripts">` via `srcdoc` with `connect-src 'none'`, blocking both Task Node session access and external data exfiltration.
- **Per-file auth & anti-leak controls:** Whole-archive `unlock` and `.../content` downloads are disabled; every file loads through per-file auth with per-account logging, rate limits, scrape alerts, subtle per-user watermarks, and appealable operator suspension.
- **Signed Publish API:** Unsigned `scp` and direct production DB writes are retired. Both `ga-models` and `goodbrief` publish through an authenticated, quota-limited, 2-key-rotatable signed Publish API with strict monotonic versioning (signed rollbacks publish a higher version pointing to a kept manifest hash).

## Live UAT Evidence

- **Today morning desk (laptop & mobile views):** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`
- **Active validator vs. Top-30 & grace countdown states:** `[INSERT LIVE UAT SCREENSHOT AFTER UAT]`
- **Signed Publish API bad-signature rejection & Goodbrief sandbox verification:** `[INSERT LIVE UAT LOG/VERIFICATION SUMMARY AFTER UAT]`

Read all eligibility formulas, grace rules, and perks in the [Finance Hub Access Guide](/finance-hub/).
