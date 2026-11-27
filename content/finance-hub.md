---
title: "Post Fiat Finance Hub Access Guide"
layout: "single"
url: "/finance-hub/"
kicker: "Members Research Desk"
summary: "How to unlock Post Fiat Finance Hub via an active L1v2 validator or Top-30 Task Node standing: eligibility formulas, 7-day grace and rank-35 hysteresis, the daily Today desk, Goodbrief, GoodAlexander Library, Research API keys, and signed publishing."
description: "Canonical Post Fiat Finance Hub access guide: validator and Top-30 non-validator eligibility, 7-day grace / rank-35 buffer, Today desk, Goodbrief, Library/API keys, and signed publishing architecture."
keywords:
  - Post Fiat Finance Hub
  - GoodAlexander models
  - Goodbrief
  - Task Node Top 30
  - validator research API keys
  - signed publish API
copyMarkdownHref: "/agents/finance-hub.md"
copyMarkdownButton: "Copy Full Markdown"
copyMarkdownDescription: "Copy and paste into your terminal agent or runbook."
copyMarkdownStatus: "Full Finance Hub access guide copied."
copyMarkdownId: "pftFinanceHubCopyTool"
---

## What Finance Hub Is

**Finance Hub** is Post Fiat's members-only daily research desk inside [Task Node](https://tasknode.postfiat.org):

- **~60 GoodAlexander company & crypto models** — live valuation state, model changes, earnings takeaways, upcoming reporting calendars, and market movers.
- **The daily Today desk** — one unified morning landing page combining equities, crypto, and macro with search, starred watchlists, and cross-device *"New since your last visit"* markers.
- **Goodbrief** — the daily macro and markets roundup, published on its own independent pipeline so model build delays never hold up the morning brief.
- **GoodAlexander Library** — members-only research posts, reports, and media.
- **Information Hive Mind (Pillar 10) bridge** — every company page displays verified **Contributor insights** (with `< 1s` server-side MNPI takedown filtering) and an **Ask the agent** button launching a research chat scoped to that exact asset.

---

## Two Independent Ways to Qualify (`finance_hub` Tier)

Finance Hub access (`accountMeetsTier("finance_hub")`) is earned through contribution or infrastructure — never paid subscriptions — via **two independent paths**. Blacklisted or suspended accounts always fail closed.

### Path 1 — Active Post Fiat Validator

Run an active validator on `postfiatl1v2` and connect it to Task Node via `postfiat-node tasknode-bind` (see the [Run a Validator Guide](/run-a-validator/)).

- **Qualification:** Active in the on-chain validator registry and meeting the latency-fair uptime rule (**`>= 95%` mean participation across `25` of `30` completed height-days**, verified by 2-of-3 independent ML-DSA-65 observers via `postfiat-validator-uptime-v1`).
- **Day-0 Ramp-In:** Newly ratified validators unlock Finance Hub immediately on registry inclusion (exempt from the 25-day history check for their first 30 height-days while `>= 95%`).
- **14-Day Grace & Fast Recovery:** Dropping out of the registry or below 95% starts a **14-day grace window** while keeping Finance Hub and Research API keys active. Sustaining `>= 95%` for **3 consecutive completed height-days** restores `active` status immediately.
- **Stale-Feed Protection:** If the observer feed is stale (`> 1 hour`), existing validator access is preserved (only new grants and monthly credits pause).
- **Revocation:** When the 14-day grace window expires without recovery, Finance Hub access disables, **active Research API keys are invalidated immediately**, and the `$20/mo` credit pauses.
- **Migration note:** Legacy old-chain validator bindings remain valid until the `postfiatl1v2` public testnet migration sunset.

### Path 2 — Top 30 Task Node Contributor

Contribute high-signal work on Task Node to earn one of **30 non-validator seats** evaluated by a deterministic daily UTC snapshot (`finance-hub.top30-snapshot.v1`).

- **Scoring Formula (`directory-leaderboard.js` parity):**
  ```text
  score = round6(3 * network_tasks + 1 * personal_tasks + (rewards_pft / 25,000) + 1 * alignment_score)
  ```
- **Deterministic Tie-Breaking:** `score DESC`, then `network_tasks DESC`, then `rewards_pft DESC`, then `account_id ASC`.
- **All Non-Blacklisted Accounts Ranked (Private Profiles Included):** You do **not** have to list your profile publicly to qualify (`include_private_accounts = true`).
- **30 Non-Validator Seats:** Active validators are excluded from the Top-30 pool (`exclude_active_validators = true`) so validators never crowd out top contributors.
- **Keep-Until Rank 35 Hysteresis (Zero Flicker):**
  - **Enter (`seated_top30`):** Reach non-validator rank **`1–30`** to unlock Finance Hub (`basis = "top30"`).
  - **Stay (`retained_hysteresis_31_35`):** Once entitled, you **keep** access all the way down to rank **`35`**. (Accounts reaching rank `31–35` without prior `top30` entitlement do not enter until they reach `<= 30`.)
- **7-Day Grace Window & 30-Day Cooldown:**
  - Dropping to rank **`>= 36`** enters a **7-day grace window** (`basis = "grace"`), with the exact expiry date displayed inside Finance Hub.
  - **Anti-bounce cooldown:** Each account has a **30-day grace cooldown** (`grace_cooldown_until = grace_started_at + 30 days`) so bouncing between rank 35 and 36 cannot generate infinite grace windows.
- **Fail-Safe Snapshot Retention:** If a daily UTC snapshot job ever fails, Task Node retains the last good snapshot and alerts operators rather than revoking Top-30 seats.

---

## Perks & Access Parity Matrix

| Feature / Entitlement | Active Validator (`basis = validator`) | Top-30 Contributor (`basis = top30`) | Grace Window (`basis = grace`) | Standard Member |
| --- | --- | --- | --- | --- |
| **Today desk & ~60 company/crypto models (`ga-models`)** | Unlocked | Unlocked | Unlocked (until `graceEndsAt`) | Locked (shows rank/validator path) |
| **Goodbrief daily macro roundup (`goodbrief`)** | Unlocked | Unlocked | Unlocked (until `graceEndsAt`) | Locked |
| **GoodAlexander Library posts & reports** | Unlocked | Unlocked | Unlocked (until `graceEndsAt`) | Locked |
| **Member Agent Briefs & Ask the Agent (Pillar 10)** | Full member brief + insights | Full member brief + insights | Full member brief + insights | Public-safe brief only (`finance-hub-public`) |
| **GoodAlexander Research API Keys** | **Active** (Validators-only) | Not included | Active for validator grace only | Not included |
| **$20/month Task Node USD Credit (Deep Research)** | **Eligible** (1 per operator) | Not included | Paused during grace | Not included |

Every publication and Library item carries an `allowed_bases` metadata list checked on every request (`["validator", "top30", "grace"]`), allowing per-publication tier adjustments without a code deploy.

---

## Inside the Daily "Today" Desk

Finance Hub opens on one unified **Today** landing page across equities, crypto, and macro (legacy category tabs act as instant filters), ordered by morning priority:

1. **Goodbrief Summary** — pulled from the independent `goodbrief` publication under its own `allowed_bases` check, with one-click full brief view.
2. **Just Reported** — latest earnings results vs. consensus, updated model state, and call takeaway.
3. **Model Updates** — target price / upside **before → after** plus a concise explanation of what changed.
4. **Reporting This Week** — upcoming calendar with options-implied moves.
5. **Live Movers** — intraday movers (dated to the last completed session on weekends and holidays).
6. **Coverage Changes** — diff from `hub/coverage_changes.json` listing newly added or dropped models.

### Watchlist, Search, Notifications & Mac App

- **Search & Starred Watchlist:** Instant ticker/name search plus a per-account starred watchlist that automatically floats your tracked names to the top of every Today section.
- **Cross-Device *"New Since Last Visit"* Markers:** Task Node tracks `visit_baseline_at` and `last_active_at` per account, updating the baseline only after an idle gap so page refreshes, multiple tabs, and mobile hand-offs keep *"New"* badges intact until you click **Mark caught up**.
- **Notifications:** Opt-in **in-app + Hive DM** alert when a new Goodbrief lands (no third-party email sender in v1).
- **Local Mac App:** The native Task Node Mac app links directly to the hosted web view and **never stores protected research bundles on local disk**.

---

## Security, Isolation & Anti-Leak Controls

Finance Hub is engineered so untrusted HTML or leaked credentials can never compromise your Task Node wallet or session, and protected research cannot be bulk-scraped:

- **Dedicated Isolated Viewer Origin:** The `ga-models` viewer runs on an **isolated origin** (`hub-viewer.postfiat.org` — never `tasknode.postfiat.org`) communicating with the Task Node shell via strict origin-checked `postMessage` and short-lived scoped viewer tokens. Even a compromised publish key can never execute scripts on `tasknode.postfiat.org` or access user wallets.
- **Zero-Exfiltration Goodbrief Sandbox:** Goodbrief HTML is fetched server-side through the authenticated per-file route, local approved styles are inlined, and the document renders inside `<iframe sandbox="allow-scripts">` via `srcdoc` with strict CSP:
  ```text
  default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; form-action 'none'
  ```
  This blocks both Task Node session access and external network exfiltration.
- **Per-File Auth (No Whole-Bundle Downloads):** Every file is served individually through per-file auth checks; legacy whole-bundle `unlock` and `.../content` archive download paths are disabled for `finance_hub` indices.
- **Anti-Leak Hygiene:** Per-account access logging, rate limits, unusual-scrape operator alerts, subtle per-user watermarks, escaped LLM/contributor text (no raw HTML), and operator suspension (appealable via the Task Node reinstatement board).

---

## Signed Publishing & Rollback Overview (Operators)

Finance Hub publishing uses an authenticated, quota-limited **Signed Publish API** (`POST /api/research/publish`, schema `finance-hub.publish-payload.v1`), completely replacing legacy unsigned `scp` / direct Postgres writes and retiring the `pfrpc` database credential.

### Three Decoupled Indices

| `index_id` | Tier | `allowed_bases` | Purpose & Isolation |
| --- | --- | --- | --- |
| `ga-models` | `finance_hub` | Subset of `["validator", "top30", "grace"]` | Company & crypto models, `hub/*.json`, `agent_brief_members.json` |
| `goodbrief` | `finance_hub` | Subset of `["validator", "top30", "grace"]` | Independent daily Goodbrief publication (decoupled from model builds) |
| `finance-hub-public` | `public_safe` | `["public"]` | Public-safe `hub/coverage_manifest.json` (`crypto_protocol` + `perp_megacap_equity` with verified perp venues and counsel-gated paid equity interviews) and `public/briefs/<model_id>.json` (`agent_brief_public.v1`, build-scanned for zero price targets, model estimates, member claims, or secrets) |

### Cryptographic Verification & Monotonic Rollback Rules

- **Canonical Signing Envelope (`canonical-json-v1`):** The publisher signs:
  ```text
  postfiat.finance-hub.publish.v1\n<index_id>\n<version>\n<nonce>\n<payload_sha256>
  ```
  using either **`ed25519`** or **`hmac-sha256`** (constant-time verification). Every file's content is bound via per-file SHA-256 and `manifest_sha256`.
- **2-Key Rotation Per Index:** Each `index_id` maintains up to two active keys (`primary` and `next`). A key scoped to `goodbrief` is strictly rejected for `ga-models` or `finance-hub-public`.
- **Replay & Freshness Protection:**
  - `version` MUST be strictly monotonic (`version > current_version`; otherwise `409 version_not_monotonic`).
  - `issued_at` must be within `±300s` of server UTC time; `expires_at <= issued_at + 600s`.
  - Single-use `nonce` persisted per `(index_id, nonce)` for `>= 900s` (duplicates rejected `409 nonce_replayed`).
  - Payload bounds: `<= 64 MiB` total, `<= 5,000` files, safe relative POSIX paths only, and mandatory `render_gate.passed = true` + `render_gate.shrink_guard_passed = true` (plus `public_leak_scan_passed = true` for `finance-hub-public`).
- **Signed Monotonic Rollbacks:** Rollbacks **never** decrement `version`. To revert a bad release, the publisher submits `operation = "rollback"` with a **new monotonically higher `version`**, `rollback_target_version < version`, and `rollback_of_manifest_sha256` pointing to a retained content-addressed historical manifest hash — restoring atomically while preserving full replay protection.
