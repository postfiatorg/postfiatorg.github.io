---
title: "Origination Replay: The System Is What It Does"
date: 2026-06-04T00:00:00Z
summary: "XRPL shows that protocol governance has an upstream origination layer. Post Fiat's proposal is to keep that reality explicit: publish the context, prompt, model choice, verdict, and replay trail behind institutional agenda formation."
aliases:
  - /origination-replay/
  - /posts/origination-replay/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - Governance
  - XRPL
  - Origination
  - Qwen
  - Replay
---

Governance decisions can be decentralized while governance origination remains institutional.

That distinction matters, but it is not automatically a scandal. Serious protocol ecosystems usually need someone to marshal people, capital, engineering focus, and a coherent story. Ripple did that for XRPL. It built around regulated payments, banking and enterprise counterparties, institutional liquidity, and a community capable of coordinating around a unified vision. If you are building an XRP/Ripple fork, you cannot pretend Ripple was incidental.

The question is what a fork does with that inheritance.

A validator vote can be real, public, and independently cast, while the menu being voted on is produced upstream by the entity with the deepest context, roadmap, and implementation capacity. In that world the vote is not fake. It is downstream of origination.

Post Fiat starts from that awareness. AGTI will have context. AGTI will have views about capital markets, AI governance, validator publication, and what the network should become. The answer is not to pretend the upstream actor disappears. The answer is to make the upstream judgment surface visible enough to replay.

The hard governance question is therefore not only:

```text
Who votes?
```

It is also:

```text
From whence did the vote object come?
```

## The XRPL Evidence

The full amendment surface is larger than the XLS standards repo.

We built a 10-year categorized amendment universe from three live sources: XRPL Known Amendments, XRPSCAN amendment rows, and the validated-ledger Amendments object:

[/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/](/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/)

The packet contains 114 official Known Amendment rows. The 10-year cut includes amendments enabled on or after June 4, 2016 plus current not-enabled known amendments:

| Measure | Count |
|---|---:|
| Official Known Amendments rows | 114 |
| Included 10-year/current rows | 113 |
| Enabled rows in cut | 91 |
| Current not-enabled rows in cut | 22 |
| Excluded enabled-before-cutoff rows | 1 |

The excluded pre-cutoff row is `FeeEscalation`, enabled on May 19, 2016.

The 10-year category split is:

| Category | Count |
|---|---:|
| Maintenance / bug fix | 51 |
| Compliance / authorization / identity | 13 |
| Payments / escrows / channels | 11 |
| Consensus safety / infrastructure | 7 |
| MPT / tokenization / RWA | 7 |
| DEX / AMM / liquidity | 6 |
| NFT | 6 |
| Account / transaction infrastructure | 4 |
| Fees / reserves | 3 |
| Programmability / batch / contracts | 2 |
| Cross-chain interop | 2 |
| Privacy / confidentiality | 1 |

That is the amendment universe. The relevant question is not whether XRPL has ecosystem contributors. It does. XRPL is nominally a protocol separate from Ripple Labs, and "XRPL ecosystem" is not the same category as "Ripple Labs."

So we use two narrower classifications.

First: direct Ripple Labs contribution or scope. An amendment counts only if the evidence ties its specification, implementation, author, reviewer, or defining scope to Ripple Labs. Evidence includes `@ripple.com` author emails, the same identity tied to Ripple evidence elsewhere in the corpus, public Ripple-role evidence at the relevant time, or an amendment scope plainly introduced by Ripple-authored XLS/spec work. Generic XRP-community involvement does not count.

Second: broader qualitative Ripple Labs relevance. This includes the direct-Ripple set plus amendment-gated maintenance of `rippled` and protocol surfaces materially related to Ripple's institutional payment, tokenization, compliance, custody, liquidity, bridge, or enterprise-adoption agenda. This is not an intent claim. It is a scope claim: what the amendment is about and whose operational surface it plausibly services.

The result:

| Classification | Count | Share | Warrant |
|---|---:|---:|---|
| Direct Ripple Labs contribution / definition | 91/113 | 80.5% | Source-backed Ripple author, Ripple email, Ripple-tied identity, or Ripple-defined amendment scope. |
| Broader qualitative Ripple Labs relevance | 104-108/113 | 92.0-95.6% | Direct Ripple rows plus `rippled` maintenance and institutional/compliance/payment/tokenization surfaces. |
| Not directly proven as Ripple Labs | 22/113 | 19.5% | External, community, unresolved, or only XRPL-ecosystem evidence. |
| Not qualitatively counted as Ripple-relevant | 5-9/113 | 4.4-8.0% | Rows where the relationship to Ripple Labs is weak, external, or unresolved. |

The second line is deliberately a range because qualitative scope is not the same kind of fact as an email address. The hard number is 91 of 113. The broader warrant is that most remaining rows are not independent agenda formation; they are amendment-gated repair and extension work on the live `rippled` system or on surfaces Ripple has clear institutional reasons to care about.

The bug-fix rows are not bugs in an abstract political process. They are mostly fixes to core XRPL server behavior: payment pathing, offer crossing, amount canonicalization, NFT page and link invariants, AMM rounding and accounting, MPT metadata, escrow/token behavior, bridge reward rounding, and amendment/validation mechanics. In other words: the maintenance backlog of the protocol implementation and feature surfaces through which the menu is built.

That is the first warrant for the article's claim. The validator vote may be decentralized, while the upstream proposal and maintenance surface remains heavily connected to Ripple Labs' engineering and product reality. That is not a dunk on Ripple. It is what effective institutional origination looks like in a protocol that has a real product direction.

The author-provenance surface is narrower if we only look at the XLS standards repo, because authorship evidence is cleanest where there is an XLS standards object. For that we built a frozen XLS provenance packet for `XRPLF/XRPL-Standards`:

[/benchmarks/xrpl-xls-provenance-20260603T230503Z/](/benchmarks/xrpl-xls-provenance-20260603T230503Z/)

The XLS packet snapshots commit `9ecf2b9db9cdc6597d9b4997b823dbf523d9b45b`, parses XLS front matter, and classifies author provenance using source-backed author evidence. The strict rule counts direct evidence tying a listed author identity to Ripple, an explicit XRPL organization, XRPL Labs, or XRP Ledger ecosystem development.

The standards-repo authorship result is blunt:

| Measure | Count |
|---|---:|
| XLS proposals parsed | 78 |
| Amendment proposals parsed | 46 |
| Direct Ripple-authored amendment proposals | 31/46 |
| Strict source-backed XRP/XRPL author-provenance amendment proposals | 44/46 |
| Amendment proposals without strict direct XRP-author evidence | 2/46 |

The enabled subset is also concentrated. In the status reconciliation packet, 15 XLS amendment rows map to amendments enabled in the validated ledger. All 15 have strict XRP/XRPL author support; 12 are direct Ripple-author rows and 3 are external XRP/XRPL-author rows.

The two amendment controls without strict direct XRP-author evidence are:

| XLS | Title | Status in frozen XLS snapshot | Listed author |
|---|---|---|---|
| `XLS-0054` | NFTokenOffer Destination Tag | Stagnant | Florent |
| `XLS-0076` | Min Incoming Amount | Deprecated | Kris Dangerfield |

That broader XLS packet is useful, but it is not the article's strongest claim because it intentionally counts XRPL ecosystem evidence. The stronger claim is the narrower one above: in the full 113-row amendment surface, roughly four-fifths have direct Ripple Labs contribution or definition evidence, and above nine-tenths are qualitatively tied to Ripple Labs' implementation or institutional agenda surface.

That is the system shape. The vote can still be decentralized. The menu can still be institutionally authored.

## Status Is A Separate Surface

We also built an XLS-to-mainnet status reconciliation packet:

[/benchmarks/xrpl-origination-status-20260604T011710Z/](/benchmarks/xrpl-origination-status-20260604T011710Z/)

It fetches the XRPL validated amendments object, XRPSCAN amendment API, and XRPL Known Amendments document on June 4, 2026. The captured validated ledger index is `104683568`.

The packet reports 46 amendment XLS rows:

| Mainnet state class | Count |
|---|---:|
| `ENABLED_IN_VALIDATED_LEDGER` | 15 |
| `IN_DEVELOPMENT_NOT_ENABLED` | 5 |
| `NOT_PRESENT_IN_KNOWN_AMENDMENTS` | 20 |
| `OBSOLETE_OR_RETIRED_NOT_ENABLED` | 3 |
| `OPEN_FOR_VOTING_NOT_ENABLED` | 3 |

This matters because `Final` in a standards repo is not the same thing as enabled on XRPL mainnet. A governance origin story has to keep those surfaces separate: proposal status, Known Amendments status, live validator support, and validated-ledger membership are different facts.

## From Whence In Practice

The public process is real, but uneven.

XRPL's own contribution guide describes a downstream path: start an XLS discussion before development, draft the standard, implement the amendment in `rippled`, submit a pull request, test through release candidates/Testnet/Mainnet nodes, then let validators vote. It also says bug fixes do not require an XLS, although they may still require an amendment. The newer [XLS-0001 process document](https://xls.xrpl.org/xls/XLS-0001-xls-process.html) is explicit that the earlier XLS process lacked clarity and consistency, and that formal Review / Last Call stages are not currently established.

That is the provenance shape: not invisible, not fully public either. The vote object eventually appears in public. The origin trail before that point depends heavily on who had the objective, staff, implementation capacity, and documentation venue to turn an idea into an amendment-shaped object.

| Surface | Public origin trail | Warrant |
|---|---|---|
| General process | [XRPL's contribution guide](https://xrpl.org/resources/contribute-code) sends `rippled` changes through XLS discussion, implementation PR, testing, release, and validator consensus; bug fixes may skip XLS while still using amendments. | Public ratification exists downstream, but not every upstream objective has a full public proposal trail. |
| AMM / `XLS-30` | [XLS-30](https://xls.xrpl.org/xls/XLS-0030-automated-market-maker.html) lists Aanchal Malhotra and David Schwartz as authors and points to GitHub discussion 78; XRPL's AMM launch post describes it as a two-year project beginning with a draft from Aanchal Malhotra and David Schwartz of Ripple. | This is a clean Ripple-authored public draft, then community feedback, implementation, and validator vote. |
| Clawback / `XLS-39` | [XLS-39](https://xls.xrpl.org/xls/XLS-0039-clawback.html) lists Nikolaos Bougalis and Shawn Xie, points to GitHub discussion 94, and frames the feature around issuer regulatory requirements. | The proposal surface is explicitly issuer/compliance-oriented; the warrant is scope, not bad intent. |
| MPT / `XLS-33` | [XLS-33](https://xls.xrpl.org/xls/XLS-0033-multi-purpose-tokens.html) lists David Fuelling, Nikolaos Bougalis, and Greg Weisbrod and motivates MPTs as an alternative to trust lines for token issuers, including stablecoins and CBDCs. | This is tokenization infrastructure in the institutional issuer surface. |
| Credentials and Permissioned DEX | [XLS-70 Credentials](https://xls.xrpl.org/xls/XLS-0070-credentials.html) and [XLS-81 Permissioned DEXes](https://xls.xrpl.org/xls/XLS-0081-permissioned-dex.html) are author-scoped standards for on-ledger credentials and permissioned trading; Ripple's own institutional DeFi post frames Credentials, Permissioned Domains, and Permissioned DEX as an identity/compliance stack for institutional use. | The public evidence directly connects these amendments to regulated institutional participation, KYC/AML, and tokenized RWA workflows. |
| Ripple prerelease venue | Ripple's [open-source docs site](https://opensource.ripple.com/docs) says it covers projects Ripple engineers are working on, including in-progress feature documentation; the same site lists prerelease pages such as [XLS-96 Confidential Transfers](https://opensource.ripple.com/docs/xls-96-confidential-transfers), [XLS-100 Smart Escrows](https://opensource.ripple.com/docs/xls-100-smart-escrows), and [XLS-82 MPT DEX Integration](https://opensource.ripple.com/docs/xls-82-mpt-dex). | Some current agenda formation is not only in the community standards repo; it is also housed on Ripple-controlled prerelease documentation. |
| Older and fix-era amendments | The second-pass provenance packet ties many older unknowns to implementation commits rather than modern XLS proposal threads. | These rows are public as code and release artifacts, but often not public as complete origination deliberation. |

The warrant is therefore not "Ripple controls XRPL" and not "XRPL is Ripple." XRPL is a protocol and validator network. Ripple Labs is a company that contributes heavily to it. The narrower claim is that when you ask where amendment-shaped objects come from, the public trail repeatedly points to Ripple-authored specs, Ripple-hosted prerelease docs, Ripple-maintained `rippled` implementation work, or feature surfaces that Ripple itself presents as institutional DeFi and payment infrastructure.

That is exactly the kind of off-chain origin surface an origination replay system would target. It would not replace validator voting. It would publish the pre-vote menu-making process in a form outsiders can inspect, replay, and fork.

## The Constructive Problem

The problem is not that Ripple has objectives. Every serious originator has objectives. Ripple's ability to hold a coherent institutional direction is part of why XRPL exists at all.

The problem is that the operative objective function is mostly private. Ripple can propose amendments for reasons that combine protocol maintenance, institutional adoption, customer needs, compliance posture, business strategy, developer ergonomics, and internal roadmap constraints. Some of those reasons may be excellent. Some may be irrelevant to independent validators. The public generally sees the proposal object after those priorities have already shaped it.

That is the agenda problem. By the time the amendment is a vote-shaped object, the originator has already decided what counts as important enough to propose.

Post Fiat has the same structural problem in a different domain. It is not trying to be Ripple's regulated cross-border payments company. It is a capital-markets and AI-governance project that values transparency, replayability, and intellectual honesty as part of the product. But AGTI is still an upstream actor. It will still see context before the public does. It will still frame questions before validators, tokenholders, contributors, or readers react.

So the proposed difference is not moral purity and not the absence of institutional power. It is a published interface for institutional origination.

## What AGTI Does Differently

AGTI should not ask the public to trust that its upstream agenda formation is neutral. It should publish the machinery.

The pattern is:

```text
AGTI context packet
  -> public decision prompt
  -> model-selection memo
  -> pinned judge profile
  -> typed nonbinding verdict
  -> replay receipts
  -> human decision or override
  -> public fork points
```

This is useful precisely because AGTI is opinionated. The packet does not hide that. It says: here is the context AGTI believes matters, here is the question we asked, here is the model we selected, here is why we selected it, here is the verdict, here is the exact output, and here is how to replay or contest it.

The first version can be nonbinding. For example:

```text
Given the disclosed AGTI/Post Fiat context packet, should Post Fiat enable
origination replay for this class of governance proposals?
```

The judge is not asked to govern the chain. It renders a typed verdict over a disclosed context packet. Humans still decide what to do. The improvement is that the origin step leaves a public trail before the decision hardens into policy.

## Packet Format

Each origination replay packet should have a stable packet hash and a stable response schema. The minimum packet is:

| Field | Purpose |
|---|---|
| `packet_id` | Stable identifier for the decision packet. |
| `schema_version` | Version of the packet and response schema. |
| `decision_question` | The exact question the judge must answer. |
| `proposal` | The proposed action, policy, feature, or governance process. |
| `originator` | The actor submitting the packet, such as AGTI. |
| `originator_role` | Why that actor has standing or context. |
| `existing_context_packet` | Hash or path to the current canonical Post Fiat context packet. |
| `context_components` | The parts of the context packet used: goals, constraints, stakeholders, risks, prior decisions, unresolved questions, metrics, budget, timeline, and dependencies. |
| `source_list` | Public sources, internal memos deliberately disclosed, prior blog posts, whitepaper sections, receipts, code links, and evidence files. |
| `source_excerpts` | Short cited excerpts or summaries mapped to source IDs. |
| `omission_log` | Known missing context, disputed facts, nonpublic context withheld, and why it is withheld. |
| `conflict_log` | Places where sources, incentives, or stakeholders disagree. |
| `model_candidates` | Models considered for judgment or playback. |
| `selected_model` | Primary model used for the verdict. |
| `model_selection_reasoning` | Why this model was selected: openness, determinism, cost, capability, reproducibility, hardware availability, context length, or independence from the originator. |
| `runtime_profile` | Inference server, weights, quantization, hardware, flags, temperature, seed, parser, and response mode. |
| `prompt` | Exact prompt given to the judge. |
| `allowed_verdicts` | Closed set of valid outputs. |
| `human_authority_boundary` | What the model may decide, what remains nonbinding, and who can override. |
| `packet_hash` | Hash of the normalized packet. |

The response should be typed, terse, and replayable:

```json
{
  "verdict": "APPROVE_FOR_NONBINDING_TRIAL",
  "confidence": "MEDIUM",
  "decision_summary": "The proposal is worth trying as a nonbinding transparency layer because the packet discloses the originator context and preserves human override.",
  "primary_reasons": [
    {
      "reason": "The process publishes AGTI context before the decision becomes policy.",
      "citations": ["context_packet:governance_objectives", "proposal:authority_boundary"]
    }
  ],
  "blocking_objections": [],
  "missing_context": [
    {
      "item": "External participant appeal process is not specified.",
      "severity": "MEDIUM"
    }
  ],
  "required_conditions": [
    "The first deployment remains nonbinding.",
    "The packet, prompt, selected model, raw output, parsed output, and human override must be published."
  ],
  "fork_points": [
    "Run the same packet through a second model.",
    "Replace AGTI-authored context with a critic-authored context packet."
  ],
  "non_claims": [
    "This verdict does not decide L1 governance.",
    "This verdict does not prove the proposal is optimal.",
    "This verdict does not remove AGTI as an originator."
  ]
}
```

Allowed first-pass verdicts should stay narrow:

| Verdict | Meaning |
|---|---|
| `APPROVE_FOR_NONBINDING_TRIAL` | Try the process as a public, nonbinding decision aid. |
| `REQUEST_MORE_CONTEXT` | Packet is plausible but materially underdisclosed. |
| `REJECT_AS_UNDERDISCLOSED` | The originator has not disclosed enough to justify a public verdict. |
| `ESCALATE_TO_HUMAN_REVIEW` | The question is too high-stakes, conflicted, or underspecified for first-pass model routing. |
| `SPLIT_PROPOSAL` | The packet combines multiple decisions that should be judged separately. |
| `RUN_MULTI_MODEL_PLAYBACK` | The packet is important enough to require several model families before publication. |

## Playback

A replay packet should not stop at one model output. It should make reconstruction cheap:

| Artifact | What it proves |
|---|---|
| `packet.normalized.json` | The exact context and proposal seen by the judge. |
| `prompt.txt` | The exact decision prompt. |
| `model_selection.md` | Why this judge was chosen and what alternatives were considered. |
| `runtime_manifest.json` | Weights, quantization, server, hardware, flags, parser, and deterministic settings. |
| `raw_output.txt` | The model's unedited answer. |
| `parsed_output.json` | The typed verdict accepted by the parser. |
| `hash_manifest.json` | Packet hash, prompt hash, raw-output hash, parsed-output hash, and runtime hash. |
| `human_decision.md` | What AGTI or Post Fiat actually did after seeing the verdict. |
| `override_receipt.md` | If humans overrode the verdict, why. |
| `forks/` | Alternative packets, critic packets, or multi-model playback outputs. |

Multi-model playback is not a vote and not a committee. It is a drift detector. If Qwen, GPT, Claude, DeepSeek, and a critic-authored packet all converge, that is evidence of procedural robustness. If they diverge, the divergence becomes the work product: a public map of what depends on model choice, prompt framing, or context selection.

That is the Schelling point Post Fiat can offer: not "AI is wise enough to govern," but "AI governance should be forced through public packets, public prompts, public model-selection reasoning, and public replay receipts."



## Evidence Links

| Artifact | Link |
|---|---|
| 10-year amendment universe packet | [/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/](/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/) |
| Ripple Labs scope methodology | [/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/ripple_labs_scope_methodology.md](/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/ripple_labs_scope_methodology.md) |
| Manual amendment review table | [/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/manual_review_table.md](/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/manual_review_table.md) |
| Unknowns provenance research | [/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/unknowns_provenance_research_20260604.md](/benchmarks/xrpl-amendments-10y-categorized-20260604T133927Z/unknowns_provenance_research_20260604.md) |
| AGTI origination replay spec packet | [/benchmarks/agti-origination-replay-spec-20260604/](/benchmarks/agti-origination-replay-spec-20260604/) |
| AGTI packet schema | [/benchmarks/agti-origination-replay-spec-20260604/transparent_origination_packet.schema.json](/benchmarks/agti-origination-replay-spec-20260604/transparent_origination_packet.schema.json) |
| AGTI judge response schema | [/benchmarks/agti-origination-replay-spec-20260604/judge_response.schema.json](/benchmarks/agti-origination-replay-spec-20260604/judge_response.schema.json) |
| XLS provenance packet | [/benchmarks/xrpl-xls-provenance-20260603T230503Z/](/benchmarks/xrpl-xls-provenance-20260603T230503Z/) |
| XLS provenance report | [/benchmarks/xrpl-xls-provenance-20260603T230503Z/REPORT.md](/benchmarks/xrpl-xls-provenance-20260603T230503Z/REPORT.md) |
| XLS provenance checksums | [/benchmarks/xrpl-xls-provenance-20260603T230503Z/SHA256SUMS.txt](/benchmarks/xrpl-xls-provenance-20260603T230503Z/SHA256SUMS.txt) |
| Status reconciliation packet | [/benchmarks/xrpl-origination-status-20260604T011710Z/](/benchmarks/xrpl-origination-status-20260604T011710Z/) |
| Status reconciliation report | [/benchmarks/xrpl-origination-status-20260604T011710Z/REPORT.md](/benchmarks/xrpl-origination-status-20260604T011710Z/REPORT.md) |
| Origination replay packet | [/benchmarks/xrpl-origination-replay-20260604T012024Z/](/benchmarks/xrpl-origination-replay-20260604T012024Z/) |
| Origination replay report | [/benchmarks/xrpl-origination-replay-20260604T012024Z/REPORT.md](/benchmarks/xrpl-origination-replay-20260604T012024Z/REPORT.md) |
| Replay summary JSON | [/benchmarks/xrpl-origination-replay-20260604T012024Z/summaries/origination_replay_summary.json](/benchmarks/xrpl-origination-replay-20260604T012024Z/summaries/origination_replay_summary.json) |
| Machine receipt | [/benchmarks/xrpl-origination-replay-20260604T012024Z/vast_lifecycle/machine_receipt.json](/benchmarks/xrpl-origination-replay-20260604T012024Z/vast_lifecycle/machine_receipt.json) |
| Shutdown receipt | [/benchmarks/xrpl-origination-replay-20260604T012024Z/vast_lifecycle/destroy-verification.json](/benchmarks/xrpl-origination-replay-20260604T012024Z/vast_lifecycle/destroy-verification.json) |
| Replay checksums | [/benchmarks/xrpl-origination-replay-20260604T012024Z/SHA256SUMS.txt](/benchmarks/xrpl-origination-replay-20260604T012024Z/SHA256SUMS.txt) |
