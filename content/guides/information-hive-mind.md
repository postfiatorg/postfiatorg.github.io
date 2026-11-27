---
title: "Information Hive Mind Contributor, MNPI Firewall & Accelerated Alpha Guide"
url: "/docs/information-hive-mind/"
type: "page"
layout: "single"
kicker: "Pillar 10 · Information Hive Mind"
date: 2026-11-27
summary: "How eligible Task Node contributors match to Finance Hub coverage, run two-phase company agent interviews, pass the in-memory hash-only MNPI firewall, and earn accelerated alpha rewards."
---

The **Post Fiat Information Hive Mind** connects domain-verified Task Node contributors with the ~60 live company and protocol models in [Finance Hub](/finance-hub/). Dedicated AI company agents triangulate what each contributor directly observes, screen every message through an in-memory MNPI/NDA firewall before storage, pool corroborated claims for human model owners, and pay **accelerated rewards** when genuine, non-consensus alpha checks out against real-world outcomes.

## 1. Eligibility & Coverage Universe

### Who Can Participate

Matching is open automatically to any eligible Task Node user — **you do not need Finance Hub membership to contribute**:

- **Eligibility requirement:** Existing Task Node **Expert badge** (`>= 20` completed personal tasks with score `>= 80`) OR a verified capability profile in the matched domain.
- **Strict member vs. non-member data boundary:**
  - **Non-Finance-Hub contributors** interview strictly against a separate public index (`agent_brief_public.json` + build-checked public question list). Zero gated model targets, member open questions, or existing member pooled claims ever reach non-members.
  - **Finance Hub members** interview against `agent_brief_members.json` and may also be asked to corroborate or challenge anonymized pooled claims.

### Asset Classes in Scope

Every Finance Hub build exports `hub/coverage_manifest.json` limited strictly to two liquid asset classes:

1. **Covered crypto protocols and tokens**
2. **Liquid megacap equities that have perpetual futures (perps) in the Finance Hub coverage universe** (illiquid and non-perp equities are excluded; paid interviews on listed equities activate only after legal counsel sign-off on attestation wording and restricted-relationship rules)

### Privacy-Safe Matching

Task Node proposes knowledge areas and information types (`operator`, `builder`, `customer`, `trader`, `public-data analyst`) privately from your completed task profiles and badges:

- Nothing activates until you explicitly confirm or edit your knowledge areas.
- Match reasons are visible only to you.
- **Sanitized contributor brief:** Company agents receive **only** your confirmed areas/info types, declared relationship, and a user-approved summary. Raw Deep Memory, private chat, context documents, and task evidence **never** reach company agents, reviewers, or Finance Hub.
- You can also self-initiate an interview on any covered name (including via Finance Hub's **Ask the agent** button) under the exact same eligibility, attestation, and screening rules.

## 2. Two-Phase Triangulating Interviews

Every interview runs inside `finance_agent_threads` with bounded turns and token caps:

1. **Relationship & No-MNPI Attestation (Mandatory Gate):** Before Phase 1 starts, you declare your relationship to the covered company/protocol and attest that you will not share material non-public information (MNPI) or confidential/NDA-bound information.
2. **Phase 1 — Triangulation:** The company agent checks what you can directly observe in public or market-participant activity (for example, protocol validator operations, developer tooling adoption, customer pricing experience, supply-chain lead times, or public filings analysis).
3. **Phase 2 — Targeted Questions:** The agent asks focused questions tied to bounded open questions (public questions for non-members; open model blind spots for Finance Hub members) and structures concrete claims with stance (`confirms`, `refines`, or `challenges`), mechanism, evidence, and a dated public `check_event`.

## 3. In-Memory MNPI & Confidentiality Firewall

Post Fiat treats inside and confidential information as a hard zero-retention boundary:

- **Relationship exclusions:** Current employees and anyone bound by MNPI or NDA duties on a covered company are blocked from interviewing on that company. Public observers, customers, open-source builders, traders, and independent analysts may participate with explicit attestation.
- **Prompt & output guardrails:** System instructions and output filters prohibit company agents from asking about unreleased earnings, internal guidance, unannounced deals, internal orders/pricing, confidential product roadmaps, legal matters, or employer/client secrets.
- **In-memory pre-storage screening:** Every user message is screened **in RAM on the API handler BEFORE writing to `finance_agent_messages` or forwarding to any LLM** (using zero-data-retention model endpoints):
  - **`pass`:** Safe public/market observation; proceeds normally.
  - **`redact`:** Flagged spans stripped; user previews the remaining text before deciding whether to save.
  - **`refuse`:** Raw text is **discarded immediately in memory** — never written to Postgres, chat history, or logs. Only `(account, company, timestamp, reason_code, sha256)` is written to the hash-only compliance log.
- **Instant `< 1s` takedown:** If any published insight is later retracted for compliance reasons, Finance Hub serves `contributor_insights.json` through a server-side takedown overlay that removes the item in `< 1` second without waiting for a 15-minute model rebuild.

## 4. Claim Store, Reviewer Agent & Human Model-Owner Approval

### Signed Claims & Objective Alpha Baseline

When you submit a claim, your wallet signs the claim text at submission time (using your [Pillar 6 on-chain identity](/docs/onchain-identity/) or a pseudonymous key). Task Node atomically snapshots **`model_estimate_before`** and **`market_consensus_before`** at submission time so future alpha can be measured objectively against the exact baseline that existed when you spoke.

Accepted claims also emit encrypted [Pillar 2 `pf.msg.v1` packets](/docs/message-protocol/) (full interview transcripts remain private).

### Prompt-Injection Hardened Reviewer & Human Approval

1. Untrusted claim text is wrapped in strict quoted-data delimiters before entering the **Reviewer Agent**.
2. The Reviewer Agent clusters duplicate claims, flags corroboration vs. conflict, scores novelty, evidence quality, and checkability, and weights claims by contributors' historical domain accuracy.
3. Candidates queue into `finance_agent_proposals` for the **human model owner** (auto-escalating to the Finance Hub operator queue after 7 days; expiring to `unresolvable` after 30 days if unreviewed).
4. **Conflict-of-interest rule:** A model owner cannot approve or trigger payouts on their own submitted claims.
5. **Research-host bridge:** The research host pulls approved proposals via a read-only service token. When the human model owner merges a model edit and cites the contribution in the model `CHANGELOG`, the host posts a signed `proposal_applied` webhook (with commit/`CHANGELOG` reference) back to Task Node, publishing the insight to Finance Hub and unlocking citation payout.

### Attribution & Pseudonymity Rules

When submitting a claim, you choose one of three attribution modes:

- Your Task Node handle
- Your minted Pillar 6 on-chain identity
- **Verified pseudonym:** Displayed pseudonymously to Finance Hub readers while known to Task Node operators for Sybil review, compliance logging, and payout settlement (stated plainly in the UI).

## 5. Accelerated Alpha Rewards & Anti-Gaming Rules

Rewards execute through Task Node's verified-task payout pipeline (bounded by existing badge `max_payout_pft` caps and Sybil review):

| Payout Stage | Trigger | Range / Rule |
| --- | --- | --- |
| **Fast Citation Payout** | Cited in an applied model `CHANGELOG` via signed `proposal_applied` webhook | **`$10–$50` PFT equivalent** (split proportionally among corroborated duplicate claims in the same cluster) |
| **Accelerated Alpha Bonus** | Checkable claim verified by a dated public `check_event` (earnings, on-chain data, public release) | **`2x–5x` bonus multiplier** — highest for novel, non-consensus `challenges` that move model estimates closer to reality |
| **Uncheckable Claims** | Opinion/qualitative claims with no dated public `check_event` | Eligible **only** for citation payout if cited in an applied model update (blocks Sybil corroboration farming) |
| **Falsified Claims** | Contradicted by the dated public `check_event` | `$0` further payout and reduced contributor domain weight |

- **Anti-hedging rule:** Submitting contradictory stances on the same company and `check_event` is blocked.
- **Operator ROI tracking:** Task Node tracks total spend, acceptance rate, verification rate, cost per verified insight, and post-citation forecast accuracy delta on an internal ROI dashboard.
