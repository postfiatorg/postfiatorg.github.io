---
title: "LLM Governance Replay: Cheap Public Verification Before Private Committees"
date: 2026-06-02T00:00:00Z
summary: "A replay experiment on XRPL amendment history: deterministic LLM replay can make governance review cheaper by making first-pass claims public, typed, hash-bound, and contestable—not by replacing validator judgment."
aliases:
  - /llm-governance-replay/
  - /posts/llm-governance-replay/
categories:
  - PostFiat Research
tags:
  - PostFiat
  - Research
  - Governance
  - XRPL
  - Qwen
  - Replay
---

A governance committee is expensive before it protects anything.

The cost is not just professional time. It is the room, the agenda, the lawyers, the repeat reviewers, the private hierarchy of who reads first, and the pressure that can accumulate before the wider validator set sees the work.

The usual objection is simple: if governance gets cheaper, it must get less safe.

That objection is right only when the cost being removed is independent verification. It is wrong when the cost being removed is duplicate discovery, provenance confusion, private agenda-setting, and arguments over what the first-pass analysis even said.

This experiment tests a narrower claim:

> Start with a public, typed, cited, replayable, and overrideable first pass. Escalate to a private committee only when the packet earns one.

The experiment does **not** put a language model in charge of XRPL. Qwen does not vote. Qwen does not join a validator list. Qwen does not get a key. Operators still decide.

The question is whether replay can make the cheapest honest governance path also the most inspectable path.

## The Result In One Paragraph

The replay profile produced schema-valid, hash-addressed outputs on a source-backed XRPL amendment lifecycle corpus. It matched selected historical vote/outcome cases 60/60 and selected dated vote-state cases 70/70. On held-out cases, it matched dated vote state 47/47 and terminal XRP-native vote/outcome 44/46, with exact output-hash convergence across repeated deterministic runs on the historical claim lanes. The two terminal-outcome misses were conservative false negatives. The triage lane was weaker: selected triage matched 72/72, but held-out triage matched only 31/47 and included one unsafe `PROCEED` on `DepositPreauth`. That failure is important. It argues against automatic model-driven `PROCEED` votes, not against replay as a public work-item generator.

The most interesting single event was the Batch pre-disclosure replay. With the February 19, 2026 disclosure withheld, the deterministic rule floor could only hold for generic authorization risk. The H200/SGLang Qwen profile returned the same hold but, in 5/5 runs, named the signer-validation control-flow risk later disclosed publicly. That is the target behavior: not “Qwen decided,” but “Qwen named the thing validators should inspect.”

## Status And Claim Boundaries

This article is dated **June 2, 2026**. The 2026 artifact dates, the `Qwen/Qwen3.6-27B-FP8` model reference, the SGLang deterministic-inference runtime, the XRPL February 2026 Batch disclosure, and the CoinDesk February 2026 Batch article are public anchors for this post, not forward-dated fiction.

The empirical objects are also public benchmark artifacts:

| Artifact | What it supports |
|---|---|
| [selected lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/) | selected historical vote/outcome, dated state, and triage lanes |
| [held-out lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/) | held-out vote/outcome, dated state, and triage lanes |
| [selected H200 receipt](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/vast_lifecycle/machine_receipt.json) | sanitized machine receipt for the selected lifecycle run |
| [held-out H200 receipt](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json) | sanitized machine receipt for the held-out lifecycle run |
| [Batch pre-disclosure replay](/benchmarks/xrpl-batch-predisclosure-h200-replay-20260601T234631Z/) | the single-event challenge-lift example |

If a reader cannot reproduce or inspect those artifacts, the empirical claims should be treated as unverified. The post is intended to be checkable, not trusted.

The claims are deliberately split:

| Claim type | What is claimed | What is not claimed |
|---|---|---|
| Replay-addressability | A pinned packet/profile/parser/output tuple can be checked and disputed as a public object. | That deterministic output is independent judgment. |
| Historical replay | The selected and held-out `vote_state` and `vote_outcome` lanes mostly reproduce source-backed XRPL amendment history under the packet construction. | That this proves future safety or live validator independence. |
| Triage | The triage route is an operator-routing harness and work-item generator. | That held-out triage is ready to drive automatic `PROCEED` votes. |
| Cost | Replay can reduce duplicate attention and private coordination because the first-pass claim becomes public and hard to fake. | That any reduction in review time is automatically safe. |
| Probability math | The binomial model illustrates residual human detection after one common replay signal. | That the parameters are measured production safety rates. |
| Capture/collusion | Human committee capture and human override collusion remain relevant. | That an LLM copy is a private colluding committee member. It is not. |

The boundary that matters most is this:

> The LLM is one common signal. Validators are the accountable actors.

Safety lives in the human verification, challenge, override, packet-forking, random-audit, and escalation layer. The scorecard below should be read through that boundary: the historical lanes are replay evidence; the triage lane is a policy-development lane.

## What Replay Means

A replay default is not a private expert recommendation. It is not a model vote. It is a bounded public claim:

```text
Given packet P,
under model/runtime profile M,
with parser S,
the route output was O,
and its hash was H.
```

Equivalently:

```text
P + M + S -> O -> H
```

That small claim is much harder to fake than a committee summary. A validator cannot later say, “the pinned replay told me X,” if the public packet, model profile, parser, and output hash deterministically reproduce Y. A packet author cannot quietly swap the prompt, omit the source map, or change the runtime without producing a different hash. A validator can still disagree, but the disagreement becomes an override rather than a forged replay claim.

The governance flow is therefore:

```text
source-backed amendment packet
  -> deterministic rule floor
  -> pinned model/runtime profile
  -> typed route schema
  -> parsed output
  -> output hash
  -> public commit/reveal
  -> follow, challenge, fork, or public override
```

The model route is an inspectable work product. The improvement is that agreement and disagreement attach to the same packet, model profile, parser, route schema, output hash, and override trail.

## Why XRPL Is A Useful Testbed

XRPL amendment voting is explicit, high-stakes, and observable.

The amendment rule is public: amendments must maintain support from more than 80% of trusted validators for the normal two-week period before activation. Servers that lack newly enabled amendment code can become amendment-blocked rather than silently interpreting ledger data under the wrong rules.

That is the right seriousness for a settlement network. It also creates a real attention bill. Every nontrivial amendment asks distributed operators to inspect code, read discussion, understand release context, and decide whether to support a change.

That makes XRPL a sharp testbed for the governance question:

> Can a public replay primitive reduce private coordination and unpaid expert review without hiding the safety question?

The source universe starts with XRPL's Known Amendments inventory, amendment process documentation, official XRPL blog posts, standards documents, and external reporting where public vote reversal is part of the event record. The labels are research labels anchored to public evidence.

For example, XRPL's Known Amendments inventory lists `Batch` as obsolete and warns that it was disabled in v3.1.1 due to a bug. It also lists `PermissionDelegation` as obsolete and disabled in v2.6.1 due to a bug. The February 2026 Batch disclosure says the Batch amendment was still in its voting phase, had not activated on mainnet, and was marked unsupported after a critical signature-validation flaw was reported. Those are exactly the kinds of facts a replay packet should bind before a validator sees a route.

## What Was Run

The replay target was an open-weight Qwen profile served through SGLang with deterministic inference enabled. The lifecycle runs were executed on a Vast H200 instance, with sanitized machine receipts included in the public artifacts:

[selected receipt](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/vast_lifecycle/machine_receipt.json) | [held-out receipt](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json)

| Field | Value |
|---|---|
| Provider run | Vast contract `39137704`, public endpoint redacted |
| GPU profile | H200, 143771 MiB VRAM |
| Model | `Qwen/Qwen3.6-27B-FP8` |
| Runtime | SGLang OpenAI-compatible server |
| SGLang image | `lmsysorg/sglang:nightly-dev-cu13-20260523-c112f762` |
| Determinism flag | `--enable-deterministic-inference` |
| Max running requests | `1` |
| Thinking mode | disabled via chat template kwargs |

Runtime details matter because “the model” is not enough information for governance replay. The replay profile must bind weights, quantization format, inference server, launch flags, prompt settings, packet hash, parser, and output hash. Otherwise a later validator cannot tell governance disagreement from runtime drift.

The public evidence artifacts use source-backed XRPL amendment lifecycle examples rather than a hand-sized demo corpus. The lifecycle packet has 119 examples: 72 in the selected evidence set and 47 held out. Those examples are expanded into lane-specific packets because terminal vote outcome, dated vote state, source default vote, and conservative triage are different claims.

The selected and held-out lifecycle artifacts together contain 458 lane packets and 644 Qwen/SGLang outputs. Their model profile hashes are:

```text
selected: 43cf85639efe8fbe37db0631fc90f0bef78a9b74fc952d7bd65641a4953aa755
held-out: ee303628f0a8b5cbc26df62a0b154d893c7cc19807f0ae611b0961c8e6bb2b7a
```

The model profile hash includes the machine receipt hash, launch profile, packet prompt settings, and replay parameters. That is replay addressability: a signer can show exactly which pinned machine/runtime/model profile produced the governance work item.

## Corpus And Lane Separation

The claim-bearing corpus is the XRPL amendment lifecycle corpus:

[expanded lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/)

It starts from a 114-amendment universe snapshot and builds 119 source-backed lifecycle examples.

| Split | Lifecycle examples | Purpose |
|---|---:|---|
| selected evidence set | 72 | build the public evidence packet and claim gate |
| held-out set | 47 | test whether the claim survives cases not selected into the evidence set |

Each lifecycle example becomes whichever lane packets are meaningful for that example. An enabled amendment can support both a terminal outcome question and a dated state question. A still-open or ambiguous item may support a state or triage question without supporting a terminal historical outcome claim. That is why this post reports lane counts rather than pretending every example has the same label type.

The lanes are separate because they make different claims:

| Lane | Meaning | Claim status |
|---|---|---|
| `vote_outcome` | XRP-native historical yes/no outcome | Historical replay |
| `vote_state` | Dated amendment state | Historical replay |
| `triage` | Conservative operator-routing policy | Experimental work-item lane |
| `default_vote` | Source/default diagnostic | Not validator-history replay |

This separation prevents the easy mistake of using a weak or experimental triage lane to inflate a historical replay claim, or using a strong historical state lane to pretend triage is solved.

## Scoring: The Metric Penalizes Unsafe `PROCEED`

The replay is scored lane by lane rather than as one oracle score.

For each packet `i`, define:

\[
G_i=(s_i,h_i,r_i,D_i,u_i),
\]

where:

- `s_i=1` if the output is schema-valid;
- `h_i=1` if repeated runs converge to the same output hash for the packet;
- `r_i` is the parsed replay label for the lane;
- `D_i` is label deviation from the lane label;
- `u_i=1` only in the triage lane, when the replay recommends `PROCEED` where hard-stop evidence or the research label calls for a blocking route.

The unsafe-proceed metric is intentionally asymmetric:

\[
R_U=\frac{1}{m}\sum_{i=1}^{m}u_i.
\]

A false hold is annoying. A false proceed on a base-layer settlement network can be catastrophic. The loss function should encode that:

\[
L=\lambda_U U+\lambda_D D+\lambda_H H,
\qquad
\lambda_U\gg \lambda_D>\lambda_H.
\]

The exact weights are policy choices. The ordering is the claim.

To compare route conservatism, assign an ordinal severity score:

\[
\sigma(\text{PROCEED})=0,\quad
\sigma(\text{HOLD\_FOR\_CHALLENGE})=1,\quad
\sigma(\text{DELAY\_FOR\_FIX})=2,\quad
\sigma(\text{REJECT})=3.
\]

A positive deviation means the replay was more conservative than history. A negative deviation means it was less conservative.

## Results: Reproducible, Useful, And Bounded

The result is narrower and stronger than “the model governed correctly”:

> Under this packet construction, the replay profile produced schema-valid, hash-addressed lane outputs, matched dated state across the selected and held-out historical state lanes, and mostly matched terminal historical outcomes with legible conservative false negatives.

Repeated-run evidence is used as a determinism check, not as a way to inflate sample size. Repeated outputs on the same packet share packet-level clustering because the run is intentionally convergent.

On the selected evidence set, the historical lanes matched completely:

| Lane | Packets | Qwen runs | Claim status | Result |
|---|---:|---:|---|---:|
| terminal XRP-native vote/outcome | 60 | 60 | historical replay | 60/60 |
| dated vote state | 70 | 70 | historical replay | 70/70 |
| conservative governance triage | 72 | 72 | policy conformance | 72/72 |
| source default vote | 69 | 69 | diagnostic only | 15/69 |

A second run used the 47 cases present in the corpus but not selected for that evidence set:

[held-out lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/)

| Lane | Packets | Qwen runs | Claim status | Result |
|---|---:|---:|---|---:|
| terminal XRP-native vote/outcome | 46 | 138 | held-out historical replay | 44/46 |
| dated vote state | 47 | 141 | held-out historical replay | 47/47 |
| conservative governance triage | 47 | 47 | experimental policy lane | 31/47 |
| source default vote | 47 | 47 | diagnostic only | 16/47 |

Qwen matched dated amendment state on every held-out case. It matched terminal XRP-native vote/outcome on 44 of 46 held-out cases, with three deterministic runs per packet on the historical claim lanes and exact output-hash convergence for every packet in those lanes.

The two terminal-outcome misses were conservative false negatives:

| Case | Historical outcome | Qwen outcome | What changed the model's mind |
|---|---:|---:|---|
| `CryptoConditions` | `YES` | `NO` | the packet said the amendment has no effect because `SusPay` was replaced by `Escrow` |
| `FlowCross` | `YES` | `NO` | the packet described DEX offer-crossing changes involving rounding, ranking, and offer deletion |

Those disagreements do not prove the model is wiser than history. They show that the replay read the packet and produced legible conservative objections.

The triage lane must be read differently. It is a workflow-policy lane, not validator-history replay. The held-out triage result showed that the written policy and the research labels were not yet the same object:

| Triage delta | Meaning |
|---|---|
| most misses | Qwen held a `PROCEED`-labeled packet for challenge, which is conservative but not label-matching |
| `DepositPreauth` | Qwen produced an unsafe `PROCEED` on an authorization/permission-surface amendment |

That `DepositPreauth` miss is the useful failure. It says the policy cannot let a clean-looking model `PROCEED` bypass structural review when the packet touches authorization, delegation, signature validation, fund movement, reserves, AMMs/DEX, or consensus semantics. Those surfaces need mandatory deep review even when the route is green.

For that reason, the public historical replay claim uses the vote/outcome and vote-state lanes. Triage remains an experimental operator-routing harness until the policy is frozen, relabeled, and re-tested against held-out cases. The triage failure is evidence against autonomous `PROCEED`; it is not evidence against replay-addressed public review.

## The Batch Replay Shows The Use Case

When the route is already obvious, Qwen should tie the deterministic rule engine on route choice. That is the design.

The deterministic rule engine is the safety floor. It is good at refusing obvious mistakes:

```text
known active bug       -> DELAY_FOR_FIX
obsolete/disabled     -> REJECT
new financial surface -> HOLD_FOR_CHALLENGE
narrow reviewed fix   -> PROCEED
```

A validator network should keep that floor.

The model adds value one layer above it. It converts a messy amendment packet into a public review object: which facts matter, which evidence is missing, what a validator should verify, and what a manual override has to explain. That matters most before a pattern has hardened into a rule.

The Batch pre-disclosure replay isolates that layer. With the February 19, 2026 disclosure withheld, the deterministic rule floor could only hold for generic authorization risk. The H200/SGLang Qwen profile returned the same hold but in 5/5 runs named the signer-validation control-flow risk later disclosed publicly.

The packet is published at:

[Batch pre-disclosure replay](/benchmarks/xrpl-batch-predisclosure-h200-replay-20260601T234631Z/)

This is one event, not a theorem. It is still the most interesting evidence in the post because it shows the target behavior: not “Qwen decided,” but “Qwen named the thing validators should inspect.”

A future amendment will arrive as release notes, pull requests, incident reports, validator commentary, vote context, and prose-shaped risk. The replay model can turn that material into a typed work item immediately. Repeated model findings can then graduate into deterministic rules.

A useful graduation rule is simple: when the route becomes predictable from explicit features, the rule engine should absorb it. When the route still depends on messy context, the model's job is to make the packet legible enough for humans to challenge it.

## Cost, Common-Mode Risk, And Residual Verification

The strongest criticism of replay-first governance is real: cheapness and independence can pull in opposite directions. If validators simply enable `vote_replay_hash=1` and stop thinking, replay becomes a committee of one.

The answer is to be precise about what kind of risk lives at each layer:

| Layer | Main risk | What replay changes |
|---|---|---|
| model output | common-mode error | the output is hash-bound and reproducible, but not independent |
| packet construction | agenda-setting | source maps, omission logs, and packet forks make the agenda public |
| validator behavior | deference or laziness | verification receipts distinguish checked follows from unchecked follows |
| human coordination | capture or collusion | overrides and packet-hash splits become visible process evidence |

A private committee is made of agents. Members can bargain, selectively disclose, suppress minority views, leak pressure, and change recommendations after private conversation. A pinned deterministic LLM profile is not that kind of participant. If the same open-weight model profile is run on the same packet under the same runtime and parser, the result is one common signal. The copies do not form a caucus. They do not privately pressure validators. They produce an output that can be hashed and compared.

That distinction does not make the model safe. It makes the failure mode different. The model layer has common-mode risk, not collusion risk. The human layer still has collusion risk. Packet construction still has agenda-setting risk. Validators still have deference risk. Collapsing all of those into “everyone used the same model” misses the mechanism-design question.

The review-budget claim is therefore conditional:

> Replay should reduce duplicate coordination and provenance work, not residual verification.

High cost is not a safety property. High cost is often why validators outsource judgment to a small committee in the first place. A public packet can increase practical independence if it lets more validators perform a bounded check instead of inheriting a committee's private framing.

A replay-default vote should never mean:

```text
I clicked yes because Qwen said yes.
```

It should mean:

```text
I saw packet_hash P,
model_profile_hash M,
output_hash H,
route R,
and I either verified the relevant checklist or accepted the public challenge
window with no unresolved blockers.
```

The dashboard should distinguish three modes:

```text
replay_default_unchecked       -> visible weak signal
replay_default_verified        -> bounded verification receipt attached
manual_override                -> public reason required
```

That receipt does not prove the validator is right. It changes the default from private deference to public accountability. A validator who follows every replay route unchecked becomes legibly different from a validator who follows after sampling sources, checking the risk surface, and reviewing open challenges.

With 41 validators and a more-than-80% enable rule, an amendment needs at least 33 YES votes to pass. Equivalently, 9 NO votes block it. If a common replay signal misses a subtle issue, the independent events are not 41 Qwen runs. The independent events are the residual human checks after the common signal.

For illustration only, if each validator performing the bounded check has a 0.4 chance of catching the issue, the chance that eight or fewer of 41 catch it is about 0.45%. That number is not a measured safety rate. It is a reminder that the tail benefit comes from residual human detection, not from pretending identical model outputs are independent witnesses.

This is the proper comparison with committee-first review. A committee-first process can collapse many validators into one framed signal before the public packet exists. Replay-first review makes the common signal public first, then lets validators check, challenge, fork, and override it in public. If 21 validators manually override the same replay route, the dashboard shows it. If 41 validators follow the route without verification receipts, the dashboard shows that too.

Replay does not abolish human collusion. It narrows the collusion target and makes the process evidence harder to fake.

## Packet Construction Is The Remaining Agenda-Setting Risk

The strongest packet-level criticism is correct: whoever constructs the packet can influence the route.

The answer is not to pretend otherwise. The answer is to make packet construction less committee-like than the alternative.

A committee summary is usually a single narrative. A replay packet should be a forkable source map.

A good packet has:

```text
amendment identity
source list
source excerpts or stable references
known status facts
risk-surface tags
omission log
conflicting evidence field
packet compiler identity
packet hash
schema version
```

The omission log matters. A packet should not only say what it included. It should say what it failed to resolve:

```json
{
  "missing_evidence": [
    "No independent code review found for signer-list edge case",
    "No public validator rationale for late vote reversal found"
  ],
  "conflicting_evidence": [
    "release note says default yes; known-amendments status now obsolete"
  ]
}
```

Most importantly, packets must be forkable. If a validator believes a packet weights the wrong facts, the validator should publish a competing packet hash and run the same route function on it. The dashboard should show disagreement at the packet layer, not hide it as an ordinary vote split:

```text
Amendment X
  packet_hash A: 24 validators, route PROCEED
  packet_hash B: 11 validators, route HOLD_FOR_CHALLENGE
  packet_hash C: 6 validators, route DELAY_FOR_FIX
```

This turns agenda-setting into a public object. It does not eliminate bias. It makes bias addressable.

If packet construction were monopolized by one private actor, replay would become a new committee. The design must reject that. Anyone should be able to file a packet fork, and votes should disclose which packet hash they relied on.

## Committees Need Triggers, Not Vibes

“Escalate when the packet earns one” cannot mean “escalate when people feel nervous.” It needs public triggers.

A replay-first process should escalate to deeper review, rotating deep reviewers, or a private committee when any of the following are true:

| Trigger | Default action | Reason |
|---|---|---|
| Deterministic hard-stop rule fires | `DELAY_FOR_FIX` or `REJECT` | Known bug, obsolete amendment, unsupported code path, or source conflict should not be negotiated away by a model. |
| Route is not `PROCEED` | Human review before support | A hold/delay/reject route is a work item, not an automatic vote. |
| `PROCEED` touches high-consequence surfaces | Mandatory rotating deep review | Signature validation, authorization, fund movement, ledger invariants, AMMs/DEX, permissions/delegation, reserves, and consensus semantics deserve review even if the first-pass route is clean. |
| Packet has missing or conflicting sources | Hold for packet repair | Source incompleteness is an agenda-setting risk. |
| Model and rule floor disagree | Hold for challenge | A disagreement between deterministic rules and model route is information. |
| Model profiles drift | Hold for profile comparison | Runtime drift is not governance disagreement. |
| A competing packet is filed | Show packet-hash split and delay if material | Packet construction must be forkable. |
| Manual overrides exceed a public threshold | Escalate | Override clusters are evidence of disagreement, pressure, or missing context. |
| Random audit seed selects the packet | Deep review regardless of route | Random audits keep low-friction defaults from becoming unexamined defaults. |

This directly answers the “subtle unsafe packet that looks clean” problem. The system should not rely only on the model route to trigger review. It should use structural risk triggers that fire even when the route says `PROCEED`.

The committee is therefore not abolished. It is moved to the second step, behind a public packet and public trigger logic.

## What A Validator Default Could Look Like

A validator configuration could look like this:

```toml
[governance]
vote_replay_hash = true
model_profile = "qwen3.6-27b-fp8-sglang-v1"
manual_override = false
verification_receipts = true
challenge_window_required = true
```

For each amendment packet, the validator computes:

```text
packet_hash
model_profile_hash
parser_hash
output_hash
parsed_route
default_vote
verification_receipt_hash
```

Then it commits and reveals:

```json
{
  "validator": "sim-validator-01",
  "packet_hash": "...",
  "model_profile_hash": "...",
  "parser_hash": "...",
  "output_hash": "...",
  "route": "DELAY_FOR_FIX",
  "vote": "NO",
  "mode": "replay_default_verified",
  "verification_receipt_hash": "..."
}
```

If the operator disagrees, the vote becomes a manual override with a public reason:

```json
{
  "validator": "sim-validator-12",
  "packet_hash": "...",
  "output_hash": "...",
  "route": "HOLD_FOR_CHALLENGE",
  "vote": "YES",
  "mode": "manual_override",
  "override_reason_hash": "..."
}
```

The dashboard can then show the split:

```text
Raw vote:
  YES 24
  NO 17

Replay route:
  PROCEED 3
  HOLD/DELAY/REJECT 38

Mode:
  replay_default_verified 16
  replay_default_unchecked 4
  manual_override 21

Packet-hash split:
  packet A 35
  packet B 6
```

That split is the point. It separates outcome disagreement from process disagreement. A raw vote says who won. A replay dashboard says whether the winning side followed the reproducible route, checked it, overrode it, or relied on a different packet.

The accountability object is:

\[
A_i=(P_i,M,S,H_o,R_i,V_i,C_i,O_i),
\]

where `P_i` is the packet, `M` is the model/runtime profile, `S` is the parser, `H_o` is the output hash, `R_i` is the route, `V_i` is the vote, `C_i` is the verification receipt, and `O_i` is either null or a public override reason.

Ordinary transparency is too weak. Publishing source code, a meeting note, or a committee summary lacks proof that the same procedure was applied to the same packet. A replay tuple is procedural regularity: the input was fixed, the machine profile was pinned, the parser was known, the output was hashed, and deviations were recorded.

## Attention Cost And Coordination Surface

The base cost model is deliberately plain: 41 validators, two hours of review per validator for a full private-committee-style pass, and $250/hour fully loaded professional time. That is 82 validator-hours, or $20,500 per governance item.

The replay-default model is cheaper only if it removes duplicate discovery and private coordination while preserving targeted verification:

- one packet verification pass per event;
- a bounded source/provenance/checklist review by each validator;
- rotating deep reviewers selected per event;
- public challenge window;
- public override when an operator disagrees.

One illustrative base case is:

| Process | Hours per item | Cost per item |
|---|---:|---:|
| Standing committee-style full review | 82.00 | $20,500.00 |
| Deterministic alert review | 30.75 | $7,687.50 |
| Replay-default public verification | 5.83 | $1,458.33 |

Under that declared model, replay-default public verification reduces attention by 92.89%. That is not a measured production savings number. It is arithmetic from declared assumptions.

The real claim is not the second decimal. It is that a public, typed, hash-bound, source-backed, forkable, and overrideable governance claim should require fewer private human-hours to reach the same or better level of accountable verification.

The same point applies to coordination. Private deliberation creates hidden agenda-setting opportunities before most validators see a work product. Replay-first governance does not make every private conversation bad; it makes private conversation an escalation path instead of the default object of governance. The public objects become packet hashes, output hashes, verification receipts, packet forks, challenge records, and override reasons.

There is still a hard boundary. If replay becomes blind following, the cost model is just a cheaper common-mode failure. The cost claim only survives with verification receipts, challenge windows, packet forks, random audits, and escalation triggers.

## Attack Model

A replay-first system should be judged by concrete attacks.

| Attack | What the attacker wants | Replay-first defense | Remaining risk |
|---|---|---|---|
| Fake model output | Claim the pinned model said `PROCEED` when it did not | Packet/profile/parser/output hashes and public reproduction | Reproduction infra must remain available |
| Runtime drift | Use a different runtime or launch profile | Model profile hash binds runtime, launch flags, prompt settings, and receipt | Hardware/software reproducibility remains hard |
| Packet omission | Exclude a source that would change the route | Source map, omission log, packet forks, challenge window | Packet readers must actually inspect omissions |
| Packet monopoly | Turn packet compiler into new committee | Anyone can publish competing packet hashes | Social attention could still concentrate |
| Blind following | Validators leave replay on and stop checking | Verification receipt modes, random audits, dashboards showing unchecked follows | Culture and incentives matter |
| Human override cartel | Validators manually override the route together | Public override reasons, packet-hash split, commit/reveal trail | Humans can still collude publicly or off-channel |
| Subtle clean-looking bug | `PROCEED` route hides a non-obvious failure | Structural escalation triggers for high-consequence surfaces and random audits | No process eliminates all subtle bugs |

This table is the safety argument. Not “the model is right.” Not “hashes solve governance.” The argument is that replay narrows each attack into a specific public object: packet, profile, parser, output, receipt, fork, or override.

A private committee can also handle these risks, but it handles them through a smaller trusted group. Replay handles them by making the first-pass object public and moving expert concentration to the cases that earn it.

## What This Proves

This proves that the replay-default pattern is operationally coherent on a production-like H200/SGLang path.

For a real governance event, validators can receive the same packet, run the same route function, commit to an output hash, reveal the output, and preserve a public trail of whether they followed, verified, challenged, forked, or overrode the default.

The strongest claim is institutional rather than magical:

> A public replay primitive can make the cheapest honest governance path also the most falsifiable path.

That is different from saying the model governs. It is also stronger than saying a model can summarize a packet. The governance value is the public tuple and the process record around it.

Replay is useful because it makes four things harder:

```text
harder to fake what the first pass said,
harder to hide packet agenda-setting,
harder to collapse disagreement into a private summary,
harder to follow or override without leaving a public trace.
```

If those four claims hold, dropping cost is not a concession. It is the point.

## Boundaries

These results establish operational coherence rather than model superiority over the rule engine. In the expanded lifecycle run, the rule engine remained the safety floor, while the claim gate separated historical vote/outcome replay, dated state replay, and triage-policy experiments.

The expanded triage labels remain research labels. The held-out triage result shows that this policy lane is not yet ready to carry the main claim. The historical outcome and state lanes are source-backed replay labels, but they are still only as good as the cited packet construction.

Future `PROCEED` outputs still require normal validator review, and high-consequence `PROCEED` outputs should receive mandatory rotating deep review whether or not the model looks confident.

The common replay signal remains a common-mode risk. Hashes prevent equivocation; they do not make identical model outputs independent. The network-level safety claim requires public residual verification, manual override, packet forking, challenge windows, random audits, and measurement of how often validators merely follow the replay default.

The true unsafe-proceed rate remains unknown. The sample is still too small to settle that value. The zero-event result is a useful negative finding and a reason to run broader held-out tests rather than a safety theorem. To push a zero-failure 95% upper bound below 1%, the relevant unit needs roughly 300 clean independent examples.

Committees remain available. Some packets will earn one. The claim is that committee formation should be the second move. Start with a public replay object. Escalate when public triggers, packet forks, risk surfaces, or unresolved challenges require concentrated expert deliberation.

The stronger claim still requires broader profile evidence: H100/H200 repeated checks under the same corpus, cross-profile drift reporting, Apple/MLX or other non-NVIDIA controls where practical, packet hashes, prompt hashes, parsed-output hashes, verification receipts, and public replay scripts.

That is the right end state: public replay primitive first; human verification, challenge, and override second; private committee only when the packet earns one.

## Appendix A: Current-Date Public Anchors

These anchors are included so a reader does not need to trust stale model memory about 2026 artifacts.

| Anchor | Public fact checked for this post | URL |
|---|---|---|
| Qwen model card | `Qwen/Qwen3.6-27B-FP8` is a Hugging Face repository containing FP8-quantized model weights and configuration files, with compatibility notes for SGLang and other runtimes. | https://huggingface.co/Qwen/Qwen3.6-27B-FP8 |
| SGLang deterministic inference | SGLang documents deterministic inference and the `--enable-deterministic-inference` launch flag. | https://github.com/sgl-project/sgl-project.github.io/blob/main/_sources/advanced_features/deterministic_inference.md |
| XRPL amendment process | XRPL documentation says amendments must maintain support from more than 80% of trusted validators for two weeks to be enabled, and describes amendment-blocked servers. | https://xrpl.org/docs/concepts/networks-and-servers/amendments/ |
| XRPL Known Amendments | The Known Amendments page lists `Batch` as obsolete and disabled in v3.1.1 due to a bug; it also lists `PermissionDelegation` as obsolete and disabled in v2.6.1 due to a bug. | https://xrpl.org/resources/known-amendments |
| XRPL Batch disclosure | XRPL's February 26, 2026 vulnerability disclosure says the Batch bug was reported February 19, 2026, affected rippled 3.1.0 with Batch enabled, had not activated on mainnet, and led validators to be advised to vote No. | https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-feb2026 |
| External Batch reporting | CoinDesk reported on February 27, 2026 that the Batch bug involved signature validation, was found during voting, and did not reach mainnet. | https://www.coindesk.com/tech/2026/02/27/ai-tool-catches-critical-xrp-ledger-bug-that-could-have-drained-wallets |

The local benchmark artifacts are the checkable evidence for the replay claim:

| Artifact | URL |
|---|---|
| selected lifecycle artifact | [/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/) |
| selected artifact hashes | [/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/SHA256SUMS.txt](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/SHA256SUMS.txt) |
| selected H200 receipt | [/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/vast_lifecycle/machine_receipt.json](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/vast_lifecycle/machine_receipt.json) |
| held-out lifecycle artifact | [/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/) |
| held-out artifact hashes | [/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/SHA256SUMS.txt](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/SHA256SUMS.txt) |
| held-out H200 receipt | [/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json) |
| Batch pre-disclosure artifact | [/benchmarks/xrpl-batch-predisclosure-h200-replay-20260601T234631Z/](/benchmarks/xrpl-batch-predisclosure-h200-replay-20260601T234631Z/) |

## Appendix B: Assumption Ledger For Headline Numbers

| Number | What it means | Driving assumptions | Status |
|---|---|---|---|
| 0.45% | `P(Bin(41,0.4)<=8)`, the residual miss probability if the common replay signal misses and each validator who verifies catches the issue with probability 0.4. | `N=41`, 9 NO votes block, `d=0.4`, independent residual human detection. | Toy model, not measured. |
| 60% | Miss rate of a single correlated summary with detection probability 0.4. | One committee/framed-summary signal with `d_c=0.4`. | Toy contrast, not measured. |
| 92.89% | Attention reduction from 82 hours to 5.83 hours. | 41 validators, two-hour full review baseline, declared replay review process. | Cost model, not production measurement. |
| ~300 clean examples | Approximate zero-failure sample size needed for a 95% upper bound below 1%. | Rule-of-three style zero-numerator reasoning. | Statistical calibration target. |

The numbers are useful only when read with their assumptions. The real claim is not that toy parameters prove safety. The real claim is that replay-first governance changes the object of trust from private summary to public, hash-bound, challengeable process state.

## Appendix C: Reproduction Scripts

The expanded lifecycle packet can be rebuilt and checked with:

```bash
python3 scripts/build_xrpl_amendment_lifecycle_corpus.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z \
  --target-count 72

python3 scripts/validate_xrpl_amendment_lifecycle_corpus.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z

python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z \
  --lane all \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/vast_lifecycle/machine_receipt.json \
  --runs 1 \
  --validators 41

python3 scripts/summarize_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z
```

The held-out lifecycle packet is derived from the same corpus split:

```bash
python3 scripts/build_xrpl_amendment_lifecycle_heldout.py \
  --source-artifact static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z

python3 scripts/validate_xrpl_amendment_lifecycle_corpus.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z \
  --min-selected 47 \
  --min-terminal-yes 46 \
  --min-nonterminal-state 1 \
  --min-sensitive-triage 11

python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z \
  --lane all \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json \
  --runs 1

python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z \
  --lane vote_outcome \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json \
  --runs 3

python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z \
  --lane vote_state \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/vast_lifecycle/machine_receipt.json \
  --runs 3

python3 scripts/summarize_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z
```

## References

- XRPL amendment process documentation: <https://xrpl.org/docs/concepts/networks-and-servers/amendments/>
- XRPL Known Amendments inventory: <https://xrpl.org/resources/known-amendments>
- XRPL Batch vulnerability disclosure: <https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-feb2026>
- CoinDesk, "AI tool catches critical XRP Ledger bug that could have drained wallets," February 27, 2026: <https://www.coindesk.com/tech/2026/02/27/ai-tool-catches-critical-xrp-ledger-bug-that-could-have-drained-wallets>
- Qwen/Qwen3.6-27B-FP8 model card: <https://huggingface.co/Qwen/Qwen3.6-27B-FP8>
- SGLang deterministic inference documentation: <https://github.com/sgl-project/sgl-project.github.io/blob/main/_sources/advanced_features/deterministic_inference.md>
- Joshua A. Kroll et al., "Accountable Algorithms," University of Pennsylvania Law Review 165(3), 2017: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2765268>
- Garold Stasser and William Titus, "Pooling of Unshared Information in Group Decision Making," Journal of Personality and Social Psychology, 1985: <https://www.uni-muenster.de/imperia/md/content/psyifp/aeechterhoff/vorlesungkommunikation/stasser_titus_unsharedinfogroupdisc_jpsp1985.pdf>
- Cass R. Sunstein, "The Law of Group Polarization," 1999: <https://chicagounbound.uchicago.edu/law_and_economics/542/>
- Sushil Bikhchandani, David Hirshleifer, and Ivo Welch, "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades," Journal of Political Economy, 1992: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1286306>
- David M. Estlund, "Opinion Leaders, Independence, and Condorcet's Jury Theorem," 1994: <https://philarchive.org/archive/ESTOLI>
- Claude E. Shannon, "A Mathematical Theory of Communication," 1948: <https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf>
- J. A. Hanley and A. Lippman-Hand, "If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators," JAMA, 1983: <https://jhanley.biostat.mcgill.ca/c607/ch08/zero_numerator.pdf>
