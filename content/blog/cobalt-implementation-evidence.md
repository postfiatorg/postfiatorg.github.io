---
title: "Cobalt on the Devnet: Implementing the Road Not Taken"
date: 2026-06-09T00:00:00Z
draft: false
summary: "Post Fiat has implemented Cobalt — the 2018 trust-evolution protocol Ripple proposed and never shipped — on its devnet, with a public, replayable evidence bundle. Adoption is an open governance question. Here is the problem Cobalt solves, what we built, how to verify it, and what it would mean under a control-based regulatory test."
aliases:
  - /cobalt-implementation-evidence/
  - /posts/cobalt-implementation-evidence/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - L1
  - Cobalt
  - Governance
  - Consensus
  - Evidence
  - XRPL
---

## In One Page

Post Fiat has implemented **Cobalt** — the asynchronous BFT governance protocol Ripple published in 2018 and never deployed — end to end on our devnet, and published the evidence bundle so the question of whether to adopt it can be argued from artifacts rather than a whitepaper section.

Cobalt makes the validator list *protocol state*: who validates, and every change to who validates, becomes a typed object the protocol itself checks before it takes effect. In the XRP lineage that list has always been a signed file — and a file's transitions cannot be verified by anyone, however transparently the file is constructed.

| | |
|---|---|
| **What we claim** | Cobalt governance mechanics run on our devnet and pass release, replay, controlled-readiness, adversarial, transition-safety, and key-continuity gates — all published, hash-bound, and replayable. |
| **What we do not claim** | Adoption (an open governance question that today rests with the foundation, to be decided in public against this evidence). Decentralization (the devnet is seven foundation-operated logical validators on reused machines; a strict independent-topology gate exists and currently fails, by design). Testnet deployment (nothing on the testnet uses Cobalt; the testnet runs our published validator-list pipeline, where Phase 1 publication is live and the first Phase 2 shadow-convergence report is pending). |
| **Where the evidence is** | The [evidence bundle manifest](/benchmarks/cobalt-devnet-evidence-20260609/manifest.json) anchors every report cited below, with checksums. Appendix B maps each claim to its artifact. |

**How to verify this yourself.** Every gate report is a public JSON file. Start with the [controlled readiness gate](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-controlled-readiness-gate/amendment-replay-contract-clean-v1-20260519T150324Z/testnet-cobalt-controlled-readiness-gate.json): it composes the release and replay reports, checks their git revisions and schemas, and binds the 19-packet adversarial set by name and digest. Then open the [replay verifier](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-full-replay-verify/standalone-subreport-schema-clean-v0-20260519T1351Z/testnet-cobalt-full-replay-verify.json), which reopens the release packet and re-checks its subreports — the design principle is that no gate is a one-time screenshot. Checksums for every file are in the manifest. (A naming note: the gate families carry a `testnet-cobalt` prefix from earlier internal naming; all runs are controlled devnet runs.)

The rest of this post explains the problem (§1), the theory (§2), what we built and the boundary of it (§3–§4), the history of why Ripple never shipped Cobalt (§5), and a conditional note on what a control-based regulatory test would make of it (§6).

---

## 1. The Problem: Safety That Lives Outside the Protocol

The XRP Ledger replaced mining and staking with a simpler idea: every server declares a **Unique Node List (UNL)** — validators it trusts not to collude — and a transaction is final when a supermajority of that list agrees. No block rewards, no stake markets, deterministic finality in seconds. Post Fiat operates in the same category.

The weakness is not the trust assumption but *where it lives*. Safety depends on high **overlap** between servers' lists — with less than roughly 90% overlap, divergence is possible in the worst case (Chase–MacBrough, 2018; XRPL's consensus-protections documentation). Overlap stays high in practice because nearly everyone imports the same *recommended* list from a small number of publishers. So the live governance question — *if the list changes, does safety survive the change?* — is answered by reputation and file distribution. The protocol has no object representing the validator set, no object representing a change to it, and no way to check a change before it takes effect. The 2025 default-UNL migration, in which operators had to update both the list URL and publisher key before the old publisher shut down, showed that publication infrastructure *is* governance infrastructure.

Post Fiat's first answer — live on our testnet today — makes list *construction* auditable: published evidence, canonical snapshots, a pinned scoring stack, and a deterministic selector turn the publisher's discretion into a named, contestable artifact. But even a perfectly transparent, validator-converged list is still a *file* whose transitions nothing can validate. Closing that last gap is what Ethan MacBrough's **Cobalt** paper (2018) was written for: how can a network where participants legitimately hold *different* trust views safely agree on changes to the trust structure itself, with safety conditions that are local and checkable rather than assumed?

Three rungs, three systems:

| Rung | Question | System |
|---|---|---|
| Availability | Can quorum survive offline validators? | Negative UNL (XRPL, shipped 2021) |
| Construction transparency | Why is this validator on the list? | Post Fiat publication pipeline (testnet, live) |
| Transition safety | Is this *change* to the list provably safe? | Cobalt (Post Fiat devnet, implemented; adoption undecided) |

The Negative UNL deserves its row: it lets validators vote on-ledger to temporarily remove persistently offline validators from quorum *accounting* — capped, gradual, reversible, evidence-driven. It made the validator set's effective form a protocol object for the first time. But it never adds, admits, or permanently removes a validator; it is a circuit breaker on the existing list, not a governance mechanism for the list. List evolution stayed where it was: a publisher edits a file, and safety across the change is hoped for.

---

## 2. Cobalt's Theory, Cleanly

Strip Cobalt to four moves.

**Trust is declared, not assumed uniform.** Every validator publishes a **trust view**: the validators it relies on, organized into **essential subsets** — groups it considers sufficient to act on when they agree. The protocol's job becomes checking that *declared* views are mutually compatible, rather than assuming an overlap nobody verifies.

**Each subset must be locally sound.** For a subset \(S\) with size \(n_S\), fault budget \(t_S\), and quorum \(q_S\):

$$0 \le t_S, q_S \le n_S, \qquad t_S < 2 q_S - n_S, \qquad 2 t_S < q_S.$$

The second inequality guarantees any two quorums of \(S\) intersect in at least one *correct* validator under \(S\)'s own fault budget; the third keeps any quorum from being majority-Byzantine. These are checkable arithmetic facts about a declared object.

**Views must be linked.** Two trust views are **fully linked** when they share an essential subset whose active faults are within budget *and* which retains a full correct quorum. A validator's position is safe when every pair of views in its trust closure is fully linked — a graph of pairwise obligations, recomputable from the declared trust graph alone, replacing one global "~90% overlap" requirement that nobody checks. A proposer cannot assert linkedness; the checker recomputes it.

**Old rules validate new rules.** A transition from registry \(G_t\) to \(G_{t+1}\) is validated entirely by the rules active at \(t\) — a new registry, trust graph, or checker never participates in validating its own activation — and must satisfy a cross-registry condition: every old-rules quorum and every new-rules quorum intersect in strictly more than \(B\) validators, the transition's Byzantine budget.

The counterexample worth memorizing shows why local soundness isn't enough. Old registry \(\{A..G\}\), proposed registry \(\{A,B,H..L\}\), each a single subset with \(n_S=7\), \(q_S=5\), \(t_S=2\). **Both pass every local inequality.** But old quorum \(\{A,B,C,D,E\}\) and new quorum \(\{A,B,H,I,J\}\) intersect only in \(\{A,B\}\) — and with \(B=2\), that whole intersection can be Byzantine: the two quorums can certify conflicting histories with no correct validator forced to sign both. The old–new matrix catches it; the transition is rejected; the old registry stays active. **A published list cannot even express this failure class** — there is no protocol object on which to run the check. Make the list protocol state, and the check is a few lines of arithmetic over declared quorums.

{{< trust-state-transition-diagram >}}

Underneath, Cobalt is built from standard asynchronous components — reliable broadcast (RBC), binary and multi-valued Byzantine agreement (ABBA/MVBA), and democratic atomic broadcast (DABC) ordering accepted governance transitions on top. Safety is certificate arithmetic, never timing.

---

## 3. What We Built

One sentence describes the deployment posture:

> Post Fiat's devnet deploys Cobalt as a rooted, bounded, fail-closed validator-registry and trust-graph transition checker derived from MacBrough's construction, where the previous active rules validate proposed new rules; it is not a claim to the full open-network Cobalt result, and it is not an adoption decision.

Each narrowing buys a checkable property. **Rooted:** all trust views live in a hash-committed trust graph, so there is no undeclared trust for the checker to miss. **Bounded:** a profile fixes \(M_{cover}\), the maximum subsets one transition may involve, and cover enumeration is taken away from the proposer — an extractor walks the rooted graphs and emits a hash-bound report the safety witness must match exactly, so an unfavorable quorum cannot be pruned from the matrix. **Fail-closed:** missing, stale, conflicting, or oversized evidence produces a hold under the last valid rules; deadlock preserves the old registry; emergency recovery is limited to precommitted quorum-signed actions. The same conservative-failure principle our live pipeline already follows (missed round → last known-good list), one level deeper.

The implementation is not a demo crate. The `consensus_cobalt` crate implements the §2 machinery module-for-module (core types, admission policy, cover extractor, trust-graph governance, RBC/ABBA/MVBA, DABC registry, internal validation), and the node layer wires it into the operations a network would actually use to change its registry — ratifying validator sets and amendments, creating and applying registry updates, and replaying amendment bundles through Cobalt evidence checks. The [implementation-surface inventory](/benchmarks/cobalt-devnet-evidence-20260609/implementation-surface.json) lists the entry points.

The evidence is layered so each layer checks the one below it:

| Gate | What it establishes | Status | Artifact |
|---|---|---|---|
| Full release gate | End-to-end mechanics: non-uniform mode, 7 distinct trust views, RBC/ABBA/DABC drills, lifecycle transitions, post-change finality, unsafe-graph rejection | passed, zero blockers | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-full-release-gate/standalone-subreport-schema-clean-v0-20260519T1351Z/testnet-cobalt-full-release-gate.json) |
| Replay verifier | Reopens the release packet and re-checks the named subreports — the release cannot be a one-time screenshot | passed | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-full-replay-verify/standalone-subreport-schema-clean-v0-20260519T1351Z/testnet-cobalt-full-replay-verify.json) |
| Controlled readiness gate | Composes and verifies release + replay (revision and schema checks), binds remote-drill and topology evidence, binds the 19-packet adversarial set by name and digest | passed, zero blockers | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-controlled-readiness-gate/amendment-replay-contract-clean-v1-20260519T150324Z/testnet-cobalt-controlled-readiness-gate.json) |
| Adversarial harness | 11 scenarios including Byzantine RBC/ABBA behavior, equivocation detection, collusion, crash-restart idempotence; one packet among the 19 bound above | passed, scope `controlled-pre-testnet` | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-adversarial/adversarial-harness-v0-20260519T0228Z/testnet-cobalt-adversarial-harness.json) |
| Transition-safety proof | The §2 obligations as executable fixtures: a valid one-validator rotation passes; seven invalid fixtures fail for the right reasons (intersection failure, oversized cover, open challenge, missing old-checker validation…) | passed | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-transition-safety-proof/20260529T081141Z/cobalt-transition-safety-proof-report.json) |
| Key-continuity receipts | A key rotation cannot be smuggled through a registry transition: receipts bind old/new keys, operator, and registry roots, validated by the old checker, signed by both keys | passed, 8 negative fixtures | [report](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-key-continuity-receipt/20260529T083000Z/cobalt-key-continuity-receipt-report.json) |
| Cover sizing & extraction | The \(M_{cover}=64\) bound is usable: 35 validators in five groups → \(M=12\); 100 in ten groups → \(M=22\); extraction is proposer-independent | passed | [sizing](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-cover-sizing-v1-report.json), [extractor](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-cover-extractor-v1-report.json) |

Field-level details, digests, and revision identifiers for every report are in Appendix B and in the JSON itself.

---

## 4. The Boundary, With Numbers

A strict public-launch gate exists and **currently fails — by design.** It demands seven distinct host fingerprints, seven operator groups, seven operator-host groups. The devnet runs seven *logical* validators on reused-machine topology, which the controlled gates permit and the strict gate refuses. Placement preflight quantifies the gap: the minimum no-single-group-can-block-quorum profile needs four independent groups and is short by one; the strict one-validator-per-independent-host profile needs seven and is short by four independent groups and four credential slots ([expected-fail](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-controlled-launch-gate/strict-expected-fail-standard-check-v0-20260519T0613Z/testnet-cobalt-strict-launch-expected-fail.json), [preflight](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-placement-preflight/preflight-v0-20260518T233339Z/testnet-cobalt-placement-preflight.json), [topology](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-topology-diversity/topology-independent-v0-20260518T2307Z/testnet-cobalt-topology-diversity-gate.json)).

The gap is informational today — no adoption decision has been made, so there is no launch to gate. It is published anyway, so that if adoption is ever decided, the topology requirements and the distance to them are already on the record. The gates exist to make compressing "devnet mechanics passed" into "decentralized launch achieved" mechanically impossible.

Why build before deciding? Because the decision deserves better inputs than a paper. Our pipeline's own endgame poses the question — later phases transfer list-content authority to validator-converged output and decentralize publication, but even a fully decentralized publication of a *file* leaves transitions uncheckable (§2). If that last gap is ever to close, Cobalt-style registry-as-protocol-state is the candidate mechanism, and the honest way to evaluate a candidate is to implement it, attack it, gate it, and publish the results. If adopted, Cobalt would *validate and activate* membership changes; the transparency pipeline would remain the process that *proposes* them; availability suspension (our Negative UNL analog) would keep handling temporary outages separately from membership; and PFT would continue to play no role in consensus or governance — validator-based, not token-voting, with no validator rewards.

---

## 5. Why Ripple Never Shipped It: An Interpretation

Cobalt is one of XRP lore's genuine mysteries — announced by Ripple itself as decentralization momentum, then never mentioned again. The documented record, briefly: Ripple's February 2018 post framed Cobalt as enabling "more diverse UNLs" — diversity, not speed ([Ripple Insights](https://ripple.com/insights/continued-decentralization-xrp-ledger-consensus-protocol/)). Three months later its author, Ethan MacBrough, left Ripple research for Coil, the Ripple-backed startup founded by ex-Ripple CTO Stefan Thomas; by October 2018 he said publicly there was no release date; a 2019 testnet reset sparked Cobalt speculation that Ripple's C++ lead promptly disputed; what shipped instead was the Negative UNL; MacBrough returned to Ripple in 2023 as a performance engineer, not a consensus researcher; and XRPL's documentation today still files Cobalt under consensus research, with no Cobalt amendment on the Known Amendments page.

Our reading — labeled interpretation, not insider knowledge — is that five ordinary forces sufficed, no villain required. Replacing the consensus core of a live, never-forked settlement network is the riskiest act available, and Chase–MacBrough's proof that the deployed protocol is safe *given high overlap* was a sedative. The recommended-list equilibrium then destroyed Cobalt's customer: when everyone imports the same file, the non-uniform trust Cobalt handles never manifests, so its costs are paid now for benefits in a future the dUNL forecloses. The pain operators actually felt was liveness, and the Negative UNL fixed exactly that. The philosophy of XRPL's chief architect ran opposite to Cobalt's premise — David Schwartz has argued that expanding validator power "would weaken an essential limitation" and that the amendment process should remain "a mere coordination mechanism and not... a primary governance mechanism" ([reported remarks](https://u.today/ripple-cto-reacts-to-speculation-around-xrp-ledger-upgrade-ahead-of-2026)), while Cobalt is definitionally a governance mechanism; and in the enforcement era there was a regulatory logic to owning nothing a court could compel ([Schwartz on control](https://beincrypto.com/xrp-ledger-centralization-debate-justin-bons-david-schwartz/)). And the construction's champion left the building three months after publication. A maximally risky migration with no felt pain, philosophical headwinds, and no champion doesn't need to be killed; it dies of natural causes.

The lesson is that Cobalt lost a cost-benefit calculation on a live network, not a technical argument — and every term in that calculation is environment-specific. A greenfield devnet has nothing live to migrate, no incumbent list equilibrium to defend, both failure classes designed for before launch, and a governance philosophy chosen rather than inherited. That is why a Cobalt deployment in this lineage was always more likely to come from a new network. It is also a warning we apply to ourselves: the seductiveness of a working stopgap, and the temptation to let a foundation-published list quietly become permanent, are forces that act on us too. Our defense is not immunity; it is that our version of the decision must be made in public, against this evidence bundle.

---

## 6. If a Control-Based Test Becomes Law: A Conditional Note

*Technical and regulatory analysis by the research team, not legal advice. The legislation discussed is pending and its text may change.*

The Digital Asset Market Clarity Act (H.R. 3633) passed the House in July 2025 and was advanced out of the Senate Banking Committee by a 15–9 vote in May 2026; it is not law, and floor timing and final text remain open. What has been stable across drafts is the structural direction: classification by *control facts* rather than enforcement narrative. The House text defines a **mature blockchain system** as one "not controlled by any person or group of persons under common control," lets an issuer certify maturity to the SEC against named criteria, and creates a graduation path toward commodity treatment (H.R. 3633 §205; [CRS overview, Sept. 30, 2025](https://doa.mt.gov/_docs/Blockchain_Task_Force/Meetings/2026-02-11-Meeting/Overview-of-Clarity-Act-09-30-25.pdf)).

If something like that test becomes law, the relevant observation about Cobalt is narrow. Take the central criterion as a worked example: no entity may hold "unilateral authority to control or materially alter the functionality, operation, or rules" of the system (H.R. 3633 §205). A recommended-list publisher is, functionally, a party with practical authority to alter who validates — they edit a file and the validator set follows — and a network in that position must *argue* that influence is not control. A correctly implemented Cobalt registry inverts the burden: after genesis no one holds an override path, every rule change is validated by the previously active rules, and any deviation from the accepted process is a hash mismatch rather than a contestable story. The difference is evidentiary, not rhetorical: **a list architecture argues about influence; a registry architecture submits hashes.**

The remaining criteria map the same way, compressed:

| H.R. 3633 §205 criterion (House text) | Cobalt-architecture counterpart |
|---|---|
| Rules "encoded directly within the source code" | The validator registry, trust graph, and transition checker become protocol state — the one governance surface this lineage historically leaves un-encoded |
| No "unique permission or privilege" for any person or common-control group | Genesis ratifier set frozen and post-genesis powerless; key-continuity receipts; recovery limited to precommitted quorum-signed actions |
| No control by a "group of persons under common control" | The topology gates and the admission predicate's correlation veto (shared release manager, key vendor, funding controller → reject) detect and measure common-control clusters in auditable units |
| Issuer certification against named criteria | Hash-bound packets, replay verifiers, and signed gate reports are the documentary form a certification reviews; the strict gate's published shortfall ("short by N groups") documents distance and bona fide intent |

Two limits keep this from being marketing. First, **maturity would be assessed on the system as operated, not as designed**: seven foundation validators on reused machines would not pass a control test — our gates crisply document failing one — so any classification benefit is earned only if and when strict gates pass with genuinely independent operators. Until then the benefit is of the documentation-of-intent kind. Second, the bill is not enacted and its text is moving; we rely on the direction, not the details.

The direction is enough to close a loop with §5, though. The deepest force that shelved Cobalt at Ripple was, in our reading, a philosophy fitted to the enforcement era: build no formal control surface, keep the list off-chain, own nothing a court could compel. In that era informal influence was deniable and formal governance was attackable. A certification regime would invert the incentive — the test becomes "demonstrate the absence of control," under which informal influence is the liability and legible, provable governance the asset. Cobalt did not change. The question being asked of it may be about to.

---

## 7. The Claim

> Post Fiat has implemented Cobalt governance mechanics in code on its devnet, wired them into node governance operations, and published passing controlled-readiness, release, replay, adversarial, transition-safety, and key-continuity evidence packets. This is decision evidence for an open governance question — not an adoption announcement, and not a decentralization claim. The live testnet remains on the published validator-list pipeline; the first Phase 2 shadow-convergence report is pending.

Or in one line: **Cobalt is implemented on the devnet; whether Post Fiat adopts it is the next governance question, and the evidence to argue it with is public.** Stronger than "we have a design." Narrower than "we are decentralized." It is the claim the artifacts can defend.

---

## Appendix A: Glossary

- **UNL.** XRPL's Unique Node List: validators a server trusts not to collude; safety requires high overlap between lists.
- **Negative UNL.** XRPL amendment for temporarily removing persistently offline validators from quorum accounting. Liveness only; never membership.
- **Trust view / essential subset.** A validator's declared trust structure; a declared group with size \(n_S\), fault budget \(t_S\), quorum \(q_S\) subject to the local inequalities.
- **Linked / fully linked.** Views sharing an essential subset within fault budget / additionally retaining a correct quorum — the pairwise replacement for global overlap.
- **Cover / \(M_{cover}\).** The complete set of old and new essential subsets in a transition, enumerated proposer-independently, bounded by profile.
- **RBC / ABBA / MVBA / DABC.** Reliable broadcast; asynchronous binary and multi-valued Byzantine agreement; democratic atomic broadcast ordering accepted governance transitions.
- **Controlled readiness.** Full Cobalt mechanics passing on seven logical devnet validators, reused topology permitted. What this post claims.
- **Strict launch.** The fail-closed gate requiring independent host/operator placement. Not claimed; informational until adoption is decided.
- **Mature blockchain system.** H.R. 3633's term for a system not controlled by any person or common-control group, assessed via issuer certification. Pending legislation; see §6.

## Appendix B: Evidence Register

All anchors live under the [bundle manifest](/benchmarks/cobalt-devnet-evidence-20260609/manifest.json), which records checksums and sizes for every file. Key identifying fields, so readers can confirm they are looking at the cited artifacts:

| Artifact | Key fields |
|---|---|
| [Release gate](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-full-release-gate/standalone-subreport-schema-clean-v0-20260519T1351Z/testnet-cobalt-full-release-gate.json) | `passed`; generated `2026-05-19T13:51:54Z`; git `9d648c24…`, dirty `false`; mode `non_uniform`; 7 distinct trust views; blockers `[]` |
| [Replay verify](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-full-replay-verify/standalone-subreport-schema-clean-v0-20260519T1351Z/testnet-cobalt-full-replay-verify.json) | `passed`; same timestamp/revision; `full_cobalt_replay_verify_ok=true` |
| [Controlled readiness gate](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-controlled-readiness-gate/amendment-replay-contract-clean-v1-20260519T150324Z/testnet-cobalt-controlled-readiness-gate.json) | `passed`; generated `2026-05-19T15:04:03Z`; git `2080c174…` (a later build that verifies the `9d648c24…` artifacts); 19-packet set exact in release and replay; packet-name digest `9a4a85f9…da573` |
| [Adversarial harness](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-adversarial/adversarial-harness-v0-20260519T0228Z/testnet-cobalt-adversarial-harness.json) | `passed`; scope `controlled-pre-testnet`; `validator_count=7`; `scenario_count=11` (one packet of the 19); `outside_operators_required=false` |
| [Transition-safety proof](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-transition-safety-proof/20260529T081141Z/cobalt-transition-safety-proof-report.json) | `passed`; valid rotation → `accept-transition`; 7 negative fixtures route to named rejections |
| [Key-continuity receipt](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-key-continuity-receipt/20260529T083000Z/cobalt-key-continuity-receipt-report.json) | `passed`; valid receipts for validators A–G; 8 negative fixtures; conflicting child rejected |
| [Cover sizing](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-cover-sizing-v1-report.json) / [extractor](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/cobalt-cover-extractor-v1-report.json) | `passed`; `max_cover_subsets=64`; M=12 (35 validators) and M=22 (100 validators); `cover_is_derived_from_graphs=true`, `proposer_supplied_cover_pruning=false` |
| [Strict expected-fail](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-controlled-launch-gate/strict-expected-fail-standard-check-v0-20260519T0613Z/testnet-cobalt-strict-launch-expected-fail.json) / [placement preflight](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-placement-preflight/preflight-v0-20260518T233339Z/testnet-cobalt-placement-preflight.json) / [topology diversity](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/testnet-cobalt-topology-diversity/topology-independent-v0-20260518T2307Z/testnet-cobalt-topology-diversity-gate.json) | strict gate fails as expected; preflight `blocked`, short by 1 group (minimum profile) and 4 groups + 4 credential slots (strict profile) |
| [Implementation surface](/benchmarks/cobalt-devnet-evidence-20260609/implementation-surface.json) | `consensus_cobalt` modules and the nine node-governance entry points |
| [MLX](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/qwen-mlx-profile-portability/20260528T155652Z/machine_report.json) / [SGLang](/benchmarks/cobalt-devnet-evidence-20260609/postfiatl1v2/reports/qwen-sglang-profile-portability/20260528T162243Z/machine_report.json) constitutional-packet portability | Replay-machinery convergence across two runtime families (300/300 and 100/100 parseable; identical parsed-output and decision roots). Method evidence for our replayable-classification research; not a governance outcome and carries no authority |
| Live testnet VL | `https://postfiat.org/testnet_vl.json` — checked `2026-06-09`: sequence `7`, `20` validators, effective `2026-06-09T18:13:16Z` |
| [List-publication whitepaper](https://postfiat.org/whitepaper/) | The production architecture this post repeatedly contrasts with (May 2026 revision) |

## References

- Schwartz, Youngs, Britto. "The Ripple Protocol Consensus Algorithm." 2014.
- Chase, MacBrough. "Analysis of the XRP Ledger Consensus Protocol." arXiv:1802.07242, 2018.
- MacBrough. "Cobalt: BFT Governance in Open Networks." arXiv:1802.07240, 2018.
- Amores-Sesar, Cachin, Mićić. "Security Analysis of Ripple Consensus." OPODIS 2020.
- Ripple Insights. ["Continued Decentralization & the XRP Ledger Consensus Protocol."](https://ripple.com/insights/continued-decentralization-xrp-ledger-consensus-protocol/) February 2018.
- XRPL documentation: [UNL](https://xrpl.org/docs/concepts/consensus-protocol/unl); [Consensus Protections](https://xrpl.org/docs/concepts/consensus-protocol/consensus-protections); [Consensus Research](https://xrpl.org/docs/concepts/consensus-protocol/consensus-research); [Negative UNL](https://xrpl.org/docs/concepts/consensus-protocol/negative-unl); [Known Amendments](https://xrpl.org/resources/known-amendments); [Default UNL Migration](https://xrpl.org/blog/2025/default-unl-migration).
- H.R. 3633, Digital Asset Market Clarity Act, 119th Congress (House-passed July 17, 2025); [CRS overview (Sept. 30, 2025)](https://doa.mt.gov/_docs/Blockchain_Task_Force/Meetings/2026-02-11-Meeting/Overview-of-Clarity-Act-09-30-25.pdf); [Senate Banking Committee advancement, May 2026](https://www.banking.senate.gov/newsroom/majority/chairman-scott-senate-banking-committee-advance-clarity-act-in-historic-bipartisan-vote).
- Post Fiat, ["Auditable, Model-Assisted Validator-List Publication for XRPL-Derived Networks,"](https://postfiat.org/whitepaper/) May 2026 revision.
