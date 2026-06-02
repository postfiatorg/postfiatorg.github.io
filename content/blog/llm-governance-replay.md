---
title: "LLM Governance Replay"
date: 2026-06-01T00:00:00Z
summary: "A replay experiment on XRPL amendment history: public, reproducible governance triage without pretending a model governs the chain."
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

A private governance committee is expensive before it makes a single decision.

The cost includes professional time and the coordination surface: the room, the
agenda keeper, the lawyers, the recurring reviewers, the implicit hierarchy of
who reads first, and the new place where validator pressure can accumulate before
validators vote.

Post Fiat's claim is narrower and more testable:

> Start with a public, typed, cited, replayable, and overrideable first pass.
> Escalate to a private committee only when the packet earns one.

That is the governance primitive tested here.

The experiment shows how a public replay route can turn validator attention into
an auditable governance artifact: same packet, same model profile, same parser,
same route schema, same commit/reveal trail, and public override when humans
disagree.

Replay-first governance preserves expert judgment while changing where it enters
the process: after a public work item exists, rather than after a private
committee has framed the agenda.

## 1. Accountable Triage Before Automated Governance

This post is about accountable triage.

A validator vote is more than a preference. It is the end product of attention,
verification, and willingness to be publicly responsible for a position. That
puts replay governance closer to three older literatures than to ordinary
"AI governance" rhetoric.

First, collective-action theory treats participation and information acquisition
as costly. Second, group-decision research shows that committees often fail to
pool distributed information well: private deliberation can overweight already-
shared facts, suppress minority information, and polarize a group before the
broader network sees the work product. Third, accountable-algorithm work argues
that transparency by itself is too weak. The better target is procedural
regularity: announce the procedure, bind inputs and outputs, and make deviations
visible afterward.

Replay governance is a concrete implementation of that idea. The model route is
a signed, inspectable work product. Operators still decide. The difference is
that agreement or disagreement attaches to the same packet, the same model
profile, the same parser, the same route schema, and the same override record.

## 2. Why XRPL Is A Good Testbed

XRPL amendment voting is explicit, high-stakes, and observable.

The public rule is that an amendment must maintain more than 80% support from
trusted validators for the normal two-week period before activation. Servers
that lack newly enabled amendment code can become amendment-blocked rather than
silently interpreting ledger data under the wrong rules. That is the right kind
of seriousness for a settlement network, but it means every contentious amendment
creates a validator attention bill.

The testbed is therefore useful for exactly this question:

> Can a public replay primitive reduce private coordination and unpaid expert
> review without hiding the safety question?

The source universe starts with XRPL's Known Amendments inventory, amendment
process documentation, official XRPL blog posts, standards documents, and
external reporting where public vote reversal is part of the event record. The
labels are research labels anchored to public evidence.

For example, XRPL's Known Amendments inventory lists `Batch` as obsolete and
warns that it was disabled in v3.1.1 due to a bug. It also lists
`PermissionDelegation` as obsolete and disabled in v2.6.1 due to a bug. The AMM
status update stated that a fix required an amendment and advised users to redeem
LP tokens and avoid new AMM deposits until the fix was enabled. The AMMClawback
transaction documentation describes issuer clawback behavior inside AMM pools.

Those are exactly the kinds of facts a replay packet should bind before a
validator sees a route.

## 3. The Committee Concentration Problem

The easy answer to "AI governance is risky" is "just make a committee."

For a validator network, that answer has a cost. A standing committee is both a
review process and an institutional concentration device. It decides who reads
first, which facts become salient, which objections are treated as serious, and
which validators inherit a recommendation rather than doing primary review.

That can be useful when expert deliberation is necessary. It is dangerous as the
default.

The problem is private repeat review: it creates an agenda-setting surface before
the wider validator set sees a typed work product. Hidden-profile research warns
that groups can fail to surface information that is distributed across members.
Informational-cascade models explain how later actors can rationally copy early
visible actions rather than reveal their own private signals. Group-polarization
work explains why private deliberation can harden a position rather than merely
average evidence.

Replay governance changes the order of operations:

```text
Private committee first:
  private deliberation -> committee summary -> validator deference or rebellion

Replay first:
  public packet -> pinned route function -> public default -> public override
```

The model is a reproducible work product. Validators remain responsible for their
votes. The governance improvement is that the first object of coordination is a
packet, a route, a hash, and an override trail.

## 4. The Missing Math: Independent Detection Versus Correlated Summaries

There is a clean probability model under the committee problem.

With 41 validators and a more-than-80% enable rule, an amendment needs at least
33 YES votes to pass. Equivalently, 9 NO votes block it:

\[
N=41,\qquad q_{\text{block}}=9,\qquad \theta=\frac{9}{41}\approx 0.2195.
\]

Now consider a subtly unsafe amendment whose replay default says `PROCEED`. Let
\(d\) be the probability that a validator who actually verifies the packet catches
the issue and votes NO.

In a private-summary model, the validator set can collapse into one correlated
signal. If the committee catches the issue with probability \(d_c\), the miss
probability is approximately:

\[
P_{\text{miss}}^{\text{committee}}\approx 1-d_c.
\]

In a replay-verification model, the detection events are at least closer to
independent because validators inspect the same public packet without waiting for
a private recommendation. The block count is:

\[
X \sim \mathrm{Bin}(41,d).
\]

The unsafe amendment slips through when eight or fewer validators catch it:

\[
P_{\text{miss}}^{\text{replay}} =
P(X\le 8) =
\sum_{k=0}^{8}\binom{41}{k}d^k(1-d)^{41-k}.
\]

For \(d=0.4\), the exact binomial miss probability is approximately:

\[
P(X\le 8)\approx 0.00446.
\]

That is about **0.45%**. At the same per-read competence, a single correlated
committee summary misses about **60%** of the time. Even a much stronger
committee with \(d_c=0.9\) still misses 10% of cases in this toy model.

A Chernoff-style relative-entropy bound makes the scaling visible:

\[
P_{\text{miss}}^{\text{replay}}
\le
\exp(-N D(\theta\|d)),
\]

where

\[
D(\theta\|d)=
\theta\ln\frac{\theta}{d}
+
(1-\theta)\ln\frac{1-\theta}{1-d}.
\]

At \(d=0.4\), \(D(\theta\|d)\approx 0.07354\), so the bound is:

\[
\exp(-41\cdot 0.07354)\approx 4.90\%.
\]

The exact number is smaller than the bound, but the lesson is the same:
independent detection has a tail. Correlated summaries collapse it.

This is the mathematical reason replay can be cheaper without simply doing less
governance. If per-validator detection clears the blocking fraction, independent
review compounds. Committee concentration flattens it.

### The Independence Requirement

The independence has a cost.

If every validator runs the same Qwen profile and blindly follows
`vote_replay_hash=1`, a model error becomes common-mode risk. The replay has
collapsed into a committee of one.

So the design has to protect the independence assumption:

- the deterministic rule floor catches obvious hard-stop cases;
- validators inspect the packet rather than merely copy the route;
- commit/reveal reduces ex-post copying from early visible votes;
- manual override remains public and easy to perform when the operator disagrees.

Replay governance means making the public work item cheap enough that independent
validators can still do their job.

## 5. The `vote_replay_hash=1` Default

A validator configuration could look like this:

```toml
[governance]
vote_replay_hash = true
model_profile = "qwen3.6-27b-fp8-sglang-v1"
manual_override = false
```

For each amendment packet, the validator computes:

```text
packet_hash
model_profile_hash
output_hash
parsed_route
default_vote
```

Then it commits and reveals:

```json
{
  "validator": "sim-validator-01",
  "packet_hash": "...",
  "model_profile_hash": "...",
  "output_hash": "...",
  "route": "DELAY_FOR_FIX",
  "vote": "NO",
  "mode": "replay_default"
}
```

If the operator disagrees, the vote becomes a manual override with a public
reason. The dashboard can then show the split:

```text
Raw vote:
  YES 24
  NO 17

Replay-default route:
  PROCEED 3
  HOLD/DELAY/REJECT 38

Manual overrides:
  YES 21
```

That split is the point. It separates outcome disagreement from process
disagreement.

The accountability object is the tuple:

\[
A_i = (P_i, M, H_o, R_i, V_i, O_i)
\]

where \(P_i\) is the amendment packet, \(M\) is the model/runtime profile,
\(H_o\) is the output hash, \(R_i\) is the parsed route, \(V_i\) is the
validator's vote, and \(O_i\) is either null or a public override reason.

Ordinary transparency is too weak. Publishing source code, a meeting note, or a
committee summary lacks proof that the same procedure was applied to the same
packet. A replay tuple is closer to procedural regularity: the input was fixed,
the machine profile was pinned, the parser was known, the output was hashed, and
deviations were recorded.

### Process Entropy

The dashboard can also report process entropy.

For a binary distribution \(p\), define Shannon entropy:

\[
H(X)=-\sum_x p(x)\log_2 p(x).
\]

For the example raw vote split, \(24/41\) YES and \(17/41\) NO:

\[
H(V)\approx 0.979 \text{ bits}.
\]

That is close to the maximum of 1 bit for a binary vote. The vote itself is
highly divided.

But the replay dashboard can expose a second distribution: how many validators
followed the replay default versus how many overrode it. If 20 follow and 21
override:

\[
H(M)\approx 1.000 \text{ bit}.
\]

Entropy characterizes governance disagreement. A raw vote says who won. A replay
dashboard says whether the winning side followed the reproducible route or
crossed it with public reasons.

## 6. Vast H200 Qwen/SGLang Replay

The replay target is an open-weight Qwen profile served through SGLang with
deterministic inference enabled. For this post, the lifecycle runs were executed
on a Vast H200 instance, with sanitized machine receipts included in the public
artifacts:

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

The public evidence artifacts use source-backed XRPL amendment lifecycle
examples rather than a hand-sized demo corpus. The current lifecycle packet has
119 examples: 72 in the selected evidence set and 47 held out. Those examples
are expanded into lane-specific packets because terminal vote outcome, dated
vote state, source default vote, and conservative triage are different claims.

The selected and held-out lifecycle artifacts together contain 458 lane packets
and 644 Qwen/SGLang outputs. Their model profile hashes are:

```text
selected: 43cf85639efe8fbe37db0631fc90f0bef78a9b74fc952d7bd65641a4953aa755
held-out: ee303628f0a8b5cbc26df62a0b154d893c7cc19807f0ae611b0961c8e6bb2b7a
```

The model profile hash includes the machine receipt hash, launch profile, packet
prompt settings, and replay parameters. The point is replay addressability: a
signer can show exactly which pinned machine/runtime/model profile produced the
governance work item.

Runtime details matter because "the model" is an incomplete description of a
governance replay. The replay profile must bind weights, quantization format,
inference server, launch flags, prompt settings, packet hash, parser, and output
hash. Otherwise a later validator loses the ability to distinguish governance
disagreement from runtime drift.

The Qwen FP8 repository publishes quantized weights and configuration files, and
SGLang documents deterministic inference support and the
`--enable-deterministic-inference` flag. The claim is therefore that the
governance artifact is replay-addressed.

## 7. Lifecycle Corpus

The claim-bearing corpus is the XRPL amendment lifecycle corpus:

[expanded lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/)

It starts from a 114-amendment universe snapshot and builds 119 source-backed
lifecycle examples. The split is deliberately explicit:

| Split | Lifecycle examples | Purpose |
|---|---:|---|
| selected evidence set | 72 | build the public evidence packet and claim gate |
| held-out set | 47 | test whether the claim survives cases not selected into the evidence set |

Each lifecycle example is converted into whichever lane packets are meaningful
for that example. An enabled amendment can support both a terminal outcome
question and a dated state question. A still-open or ambiguous item may support a
state or triage question without supporting a terminal historical outcome claim.
This is why the article reports lane counts rather than pretending every example
has the same label type.

The important separation is:

- `vote_outcome`: XRP-native historical yes/no outcome;
- `vote_state`: dated amendment state;
- `triage`: conservative operator-routing policy;
- `default_vote`: source/default diagnostic, not validator-history replay.

## 8. Scoring The Replay

The replay is scored lane by lane rather than as a single oracle score.

For each packet \(i\), define:

\[
G_i = (s_i, h_i, r_i, D_i, u_i)
\]

where:

- \(s_i=1\) if the output is schema-valid;
- \(h_i=1\) if repeated runs converge to the same output hash for the packet;
- \(r_i\) is the parsed replay label for the lane;
- \(D_i\) is label deviation from the lane label;
- \(u_i=1\) only in the triage lane, when the replay recommends `PROCEED` where
  the packet's hard-stop evidence or research label calls for a blocking route.

The unsafe-proceed metric is intentionally asymmetric:

\[
R_U=\frac{1}{m}\sum_{i=1}^{m}u_i.
\]

A false hold is annoying. A false proceed on a base-layer settlement network can
be catastrophic. The loss function should encode that:

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

Then compute:

\[
D_i=\sigma(r_i)-\sigma(r_i^{history}).
\]

A value of \(D_i=0\) means the replay route matched the historical research
label. A positive value means the replay was more conservative. A negative value
means it was less conservative.

## 9. Results: Conservative, Reproducible, And Bounded

The result is narrower and stronger than "the model governed correctly":

> Under this packet construction, the replay profile produced schema-valid
> lane-specific outputs, matched dated state across the selected and held-out
> historical state lanes, and mostly matched terminal historical outcomes with
> legible conservative false negatives.

The repeated-run evidence is used as a determinism check, not as a way to inflate
the sample size. Repeated outputs on the same packet share packet-level
clustering because the run is intentionally convergent.

This is why broader testing matters. To push a zero-failure 95% upper bound
below 1%, the relevant unit needs roughly 300 clean independent examples.

## 10. Expanded Lifecycle Replay

The claim-bearing packet is a lane-separated XRPL amendment lifecycle replay:

[expanded lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z/)

The important change is that the replay no longer mixes unlike labels.
`HOLD_FOR_CHALLENGE` is a triage work route, not an XRP validator vote.
`default_vote` is a diagnostic source-code field, not validator-history replay.
The claim gate therefore separates terminal outcomes, dated vote state, and
conservative triage policy.

On the selected evidence set, the historical lanes matched completely:

| Lane | Packets | Qwen runs | Claim status | Result |
|---|---:|---:|---|---:|
| terminal XRP-native vote/outcome | 60 | 60 | historical replay | 60/60 |
| dated vote state | 70 | 70 | historical replay | 70/70 |
| conservative governance triage | 72 | 72 | policy conformance | 72/72 |
| source default vote | 69 | 69 | diagnostic only | 15/69 |

The report's claim gate is explicit:

> `default_vote` is diagnostic only; it is not a historical replay claim because
> source defaults are not validator outcomes.

The expanded run produced 271 schema-valid Qwen outputs across all lanes. The
selected-run disagreement files for `vote_outcome`, `vote_state`, and `triage`
are empty. The diagnostic `default_vote` disagreement file is kept precisely
because it shows why source defaults should not be smuggled into a replay claim;
the held-out run below is the test that separates historical replay from the
experimental triage-policy lane.

A second run used the 47 cases that were present in the corpus but not selected
for that evidence set:

[held-out lifecycle replay](/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z/)

| Lane | Packets | Qwen runs | Claim status | Result |
|---|---:|---:|---|---:|
| terminal XRP-native vote/outcome | 46 | 138 | held-out historical replay | 44/46 |
| dated vote state | 47 | 141 | held-out historical replay | 47/47 |
| conservative governance triage | 47 | 47 | experimental policy lane | 31/47 |
| source default vote | 47 | 47 | diagnostic only | 16/47 |

The held-out result is the better stress test. Qwen matched dated amendment state
on every held-out case. It matched terminal XRP-native vote/outcome on 44 of 46
held-out cases, with three deterministic runs per packet on the historical
claim lanes and exact output-hash convergence for every packet in those lanes.

The two terminal-outcome misses were conservative false negatives:

| Case | Historical outcome | Qwen outcome | What changed the model's mind |
|---|---:|---:|---|
| `CryptoConditions` | `YES` | `NO` | the packet said the amendment has no effect because `SusPay` was replaced by `Escrow` |
| `FlowCross` | `YES` | `NO` | the packet described DEX offer-crossing changes involving rounding, ranking, and offer deletion |

Those disagreements are not random failures. They are cases where the model read
the packet and objected more conservatively than the validator history. The
right statement is therefore not that Qwen perfectly rediscovered XRPL history.
It is that the replay mostly matched history, and the held-out disagreements
were legible, conservative objections to amendments that later enabled.

The triage lane should be read differently. It is a workflow-policy lane, not
validator-history replay. The held-out triage result showed that the written
policy and the research labels were not yet the same object: most misses were
Qwen holding a `PROCEED`-labeled packet for challenge, and one miss was an unsafe
`PROCEED` on `DepositPreauth`. For that reason, the public historical replay
claim uses the vote/outcome and vote-state lanes. Triage remains an experimental
operator-routing harness until the policy is frozen and relabeled against
held-out cases.

## 11. Why Use Qwen If The Rule Engine Tied It?

When the route is already obvious, Qwen should tie the deterministic rule engine
on route choice.

That is the design.

The deterministic rule engine is the safety floor. It is good at refusing
obvious mistakes:

```text
known active bug      -> DELAY_FOR_FIX
obsolete/disabled    -> REJECT
new financial surface -> HOLD_FOR_CHALLENGE
narrow reviewed fix   -> PROCEED
```

A validator network should keep that floor.

The model adds value one layer above the floor. It converts a messy amendment
packet into a public review object: which facts matter, which evidence is
missing, what a validator should verify, and what a manual override has to
explain. That matters most before a pattern has hardened into a rule.

The Batch pre-disclosure replay isolates that layer. With the February 19, 2026
disclosure withheld, the deterministic rule floor could only hold for generic
authorization risk; the H200/SGLang Qwen profile returned the same hold but in
5/5 runs named the signer-validation control-flow risk later disclosed publicly.
That is challenge lift rather than vote authority: a concrete work item before a
validator defaults to yes. The packet is published at
[Batch pre-disclosure replay](/benchmarks/xrpl-batch-predisclosure-h200-replay-20260601T234631Z/).

A future amendment will arrive as release notes, pull requests, incident
reports, validator commentary, vote context, and prose-shaped risk. The replay
model can turn that material into a typed work item immediately. Repeated model
findings can then graduate into deterministic rules.

A useful graduation rule is information-theoretic:

\[
H(\text{route}\mid \text{features})\to 0.
\]

When the route becomes predictable from explicit features, the rule engine should
absorb it. When conditional entropy is still high, the model's job is to make
the packet legible enough for humans to challenge it.

The model's value is therefore option value:

\[
V_{\text{model}}
=
V_{\text{triage}}
+
V_{\text{pre-rule}}
+
V_{\text{audit}}
-
C_{\text{replay}}.
\]

The rule engine's value is:

\[
V_{\text{rule}}=V_{\text{triage}}-C_{\text{rule}}.
\]

The model earns its keep when:

\[
V_{\text{pre-rule}}+V_{\text{audit}}
>
C_{\text{replay}}-C_{\text{rule}}.
\]

If the model only repeats a mature rule, the rule should win. If it surfaces the
facts, questions, and override burden before a rule exists, it reduces the need
to assemble a private committee just to decide what everyone should read.

## 12. Attention Cost Model

The cost model is deliberately plain:

- 41 validators;
- two hours of review per validator for a full private-committee style pass;
- $250/hour fully loaded professional time.

That yields:

\[
41\cdot 2=82
\]

validator-hours per governance item, or:

\[
82\cdot 250=\$20{,}500.
\]

The benchmark replay-default model is cheaper because it asks fewer people to do
deep work by default:

- one packet verification pass per event;
- a five-minute skim by each validator;
- three deep reviewers per event;
- public override when an operator disagrees.

| Process | Hours per item | Cost per item |
|---|---:|---:|
| Standing committee review | 82.00 | $20,500.00 |
| Deterministic alert review | 30.75 | $7,687.50 |
| Qwen replay-default triage | 5.83 | $1,458.33 |

Under the declared model, replay-default triage reduces attention by:

\[
1-\frac{5.83}{82}=92.89\%.
\]

Those are cost-model numbers, short of proof of safety. Change validator count,
hourly rate, skim minutes, deep reviewers, or review minutes and the conclusion
should update.

The exact 92.89% figure is the base case. The claim is directional. If ordinary
review would only take 45 minutes per validator, and replay overhead rises to a
10-minute skim plus five deep reviewers and a 20-minute packet check, replay
still uses materially fewer public validator-hours. If ordinary review takes
three hours per validator under the same replay overhead, the reduction is
larger.

The point is the direction of the trade: less private coordination, less unpaid
expert labor, and a public override trail when validators disagree.

### Coordination-Surface Compression

The cost model measures validator-hours. The governance problem also has a
coordination dimension.

If \(r\) reviewers deliberate privately before the wider validator set sees a
work product, the potential pairwise private coordination surface is:

\[
E_{\text{private}}(r)=\binom{r}{2}=\frac{r(r-1)}{2}.
\]

This is an exposure model: private coordination opportunities scale quadratically
with repeat reviewers.

Replay governance changes the scaling. Each validator can inspect the same
public packet and either follow or override the default. A simple public-process
proxy is:

\[
E_{\text{replay}}(n,k)=n+k,
\]

where \(n\) is the number of validators that inspect the packet and \(k\) is the
number of manual overrides requiring public explanation.

For the 41-validator base case:

\[
E_{\text{private}}(41)=820.
\]

If 41 validators inspect the packet and 5 override publicly:

\[
E_{\text{replay}}(41,5)=46.
\]

\[
1-\frac{46}{820}=94.39\%.
\]

This is a coordination-surface proxy rather than a safety proof. The real claim
is the scaling law: private deliberation creates \(O(r^2)\) potential
coordination edges; replay-first triage creates \(O(n+k)\) public inspection and
override records.

### Override Burden

The system keeps override available and makes its burden visible.

Define:

\[
B_o=\frac{\text{manual overrides against replay default}}{\text{validators}}.
\]

A severity-weighted version is:

\[
S_o=B_o\cdot w_r.
\]

| Replay route | Suggested severity weight |
|---|---:|
| `PROCEED` | 1 |
| `HOLD_FOR_CHALLENGE` | 2 |
| `DELAY_FOR_FIX` | 3 |
| `REJECT` | 4 |

A validator may still vote against the replay default. The dashboard should
distinguish "followed a reproducible default" from "overrode a reproducible
default on a high-severity packet."

### Linking Cost To Safety

The current benchmark declares review effort. A production system should choose
review effort from a safety target.

Let \(m\) be validator review minutes and let:

\[
d(m)=1-e^{-\lambda m}
\]

be a simple calibrated detection curve: more review time raises the probability
of catching a subtle issue, with diminishing returns.

Then review policy can be stated as an optimization problem:

\[
\min_m \; N\cdot m\cdot w\cdot E
\]

subject to:

\[
P(\mathrm{Bin}(N,d(m))\ge 9)\ge 1-\varepsilon.
\]

The target \(\varepsilon\) is the tolerated probability that an unsafe amendment
escapes blocking review. This converts "how much review should validators do?"
from a vibes question into a policy parameter.

Replay is cheaper only if it preserves enough independent detection to hit the
same safety target with less total attention. If validators merely copy the
default, the cost model wins and the safety model loses. The whole design exists
to avoid that trade.

## 13. Reproduction Scripts

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

## 14. What This Proves

This proves that the replay-default pattern is operationally coherent on a
production-like H200/SGLang path.

For a real governance event, validators can receive the same packet, run the
same route function, commit to an output hash, reveal the output, and preserve a
public trail of whether they followed or overrode the default. The process
directly attacks two costs that ordinary governance hand-waves away: attention
cost and private coordination cost.

It also shows that positive model authority is unnecessary. The strongest
held-out lifecycle result was historical: exact dated-state replay and high
terminal-outcome alignment, with conservative objections where the model
disagreed.

The strongest claim is institutional rather than magical:

> A public replay primitive can make the cheapest governance path also the most
> inspectable path.

## 15. Boundaries

These results establish operational coherence rather than model superiority over
the rule engine. In the expanded lifecycle run, the rule engine remained the
safety floor, while the claim gate separated historical vote/outcome replay,
dated state replay, and triage-policy experiments.

The expanded triage labels remain research labels for these events. The held-out
triage result shows that this policy lane is not yet ready to carry the main
claim. The historical outcome and state lanes are source-backed replay labels,
but they are still only as good as the cited packet construction.

Future `PROCEED` outputs still require normal validator review.

The true unsafe-proceed rate remains unknown. The sample is still too small to
settle that value. The zero-event result is a useful negative finding and a
reason to run broader held-out tests rather than a safety theorem.

Committees remain available. Some packets will earn one. The claim is that
committee formation should be the second move. Start with a public replay object.
Escalate when the packet actually requires concentrated expert deliberation.

The stronger claim still requires broader profile evidence: H100/H200 repeated
checks under the same corpus, cross-profile drift reporting, Apple/MLX or other
non-NVIDIA controls where practical, packet hashes, prompt hashes,
parsed-output hashes, and public replay scripts.

That is the right end state: public replay primitive first; human override
second; private committee only when the packet earns one.

## Appendix: Toy Capture-Threshold Model

A private committee concentrates agenda-setting power into a smaller threshold.
If \(c\) committee members frame the recommendation, and \(q\) influenced members
are enough to control that recommendation, a simple independent-risk model is:

\[
P_{\text{committee}}=
\sum_{j=q}^{c}
\binom{c}{j}p^j(1-p)^{c-j},
\]

where \(p\) is the probability that a given reviewer is conflicted, exhausted,
captured, or otherwise predictably influenceable.

For a five-person committee where three members can frame the recommendation,
with \(p=0.15\):

\[
P_{\text{committee}}\approx 2.66\%.
\]

A public override threshold has a different shape. If 21 of 41 validators must
override a replay default to reverse the outcome, then:

\[
P_{\text{mass override}}=
\sum_{j=21}^{41}
\binom{41}{j}p^j(1-p)^{41-j}.
\]

At \(p=0.15\), this is approximately:

\[
6.18\times 10^{-8}.
\]

This appendix is illustrative rather than empirical. The independence assumption
is strong, \(p\) remains unestimated here, and real influence is correlated. The
useful point is the threshold structure: replay-first governance moves
disagreement from a small private recommendation threshold to a public
mass-override threshold.

## References

- XRPL amendment process documentation: <https://xrpl.org/docs/concepts/networks-and-servers/amendments/>
- XRPL Known Amendments inventory: <https://xrpl.org/resources/known-amendments>
- XRPL AMM status update: <https://xrpl.org/blog/2024/amm-status-update>
- XRPL AMMClawback transaction documentation: <https://xrpl.org/docs/references/protocol/transactions/types/ammclawback>
- Qwen/Qwen3.6-27B-FP8 model card: <https://huggingface.co/Qwen/Qwen3.6-27B-FP8>
- SGLang deterministic inference documentation: <https://sgl-project.github.io/advanced_features/deterministic_inference.html>
- Joshua A. Kroll et al., "Accountable Algorithms," University of Pennsylvania Law Review 165(3), 2017: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2765268>
- Garold Stasser and William Titus, "Pooling of Unshared Information in Group Decision Making," Journal of Personality and Social Psychology, 1985: <https://www.uni-muenster.de/imperia/md/content/psyifp/aeechterhoff/vorlesungkommunikation/stasser_titus_unsharedinfogroupdisc_jpsp1985.pdf>
- Cass R. Sunstein, "The Law of Group Polarization," 1999: <https://chicagounbound.uchicago.edu/law_and_economics/542/>
- Sushil Bikhchandani, David Hirshleifer, and Ivo Welch, "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades," Journal of Political Economy, 1992: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1286306>
- David M. Estlund, "Opinion Leaders, Independence, and Condorcet's Jury Theorem," 1994: <https://philarchive.org/archive/ESTOLI>
- Claude E. Shannon, "A Mathematical Theory of Communication," 1948: <https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf>
- J. A. Hanley and A. Lippman-Hand, "If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators," JAMA, 1983: <https://jhanley.biostat.mcgill.ca/c607/ch08/zero_numerator.pdf>
