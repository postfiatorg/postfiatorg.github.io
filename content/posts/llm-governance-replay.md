---
title: "LLM Governance Replay"
date: 2026-06-01T00:00:00Z
summary: "A replay experiment on XRPL amendment history: public, reproducible governance triage without pretending a model governs the chain."
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

The cost is not only professional time. It is the coordination surface: the room,
the agenda keeper, the lawyers, the recurring reviewers, the implicit hierarchy
of who reads first, and the new place where validator pressure can accumulate
before validators vote.

Post Fiat's claim is narrower and more testable:

> Do not create a private committee unless the packet earns one. Make the first
> pass public, typed, cited, replayable, and overrideable.

That is the governance primitive tested here.

The experiment does **not** show that a language model should govern XRPL. It
shows that a public replay route can turn validator attention into an auditable
governance artifact: same packet, same model profile, same parser, same route
schema, same commit/reveal trail, and public override when humans disagree.

Replay-first governance does not eliminate expert judgment. It changes where
expert judgment enters the process: after a public work item exists, not before a
private committee has framed the agenda.

## 1. Accountable Triage, Not Automated Governance

This post is about accountable triage.

A validator vote is not just a preference. It is the end product of attention,
verification, and willingness to be publicly responsible for a position. That
puts replay governance closer to three older literatures than to ordinary
"AI governance" rhetoric.

First, collective-action theory treats participation and information acquisition
as costly. Second, group-decision research shows that committees do not
automatically pool distributed information well: private deliberation can
overweight already-shared facts, suppress minority information, and polarize a
group before the broader network sees the work product. Third, accountable-
algorithm work argues that transparency by itself is too weak. The better target
is procedural regularity: announce the procedure, bind inputs and outputs, and
make deviations visible afterward.

Replay governance is a concrete implementation of that idea. The model route is
not authority. It is a signed, inspectable work product. Operators still decide.
The difference is that agreement or disagreement attaches to the same packet,
the same model profile, the same parser, the same route schema, and the same
override record.

## 2. Why XRPL Is A Good Testbed

XRPL amendment voting is explicit, high-stakes, and observable.

The public rule is that an amendment must maintain more than 80% support from
trusted validators for the normal two-week period before activation. Servers
that do not understand newly enabled amendment code can become amendment-blocked
rather than silently interpreting ledger data under the wrong rules. That is the
right kind of seriousness for a settlement network, but it means every
contentious amendment creates a validator attention bill.

The testbed is therefore useful for exactly this question:

> Can a public replay primitive reduce private coordination and unpaid expert
> review without hiding the safety question?

The source universe starts with XRPL's Known Amendments inventory, amendment
process documentation, official XRPL blog posts, standards documents, and
external reporting where public vote reversal is part of the event record. The
labels are not model-generated. They are research labels anchored to public
evidence.

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

For a validator network, that answer is not neutral. A standing committee is not
only a review process. It is an institutional concentration device. It decides
who reads first, which facts become salient, which objections are treated as
serious, and which validators inherit a recommendation rather than doing primary
review.

That can be useful when expert deliberation is necessary. It is dangerous as the
default.

The problem is not that every committee is corrupt. The problem is that private
repeat review creates an agenda-setting surface before the wider validator set
sees a typed work product. Hidden-profile research warns that groups can fail to
surface information that is distributed across members. Informational-cascade
models explain how later actors can rationally copy early visible actions rather
than reveal their own private signals. Group-polarization work explains why
private deliberation can harden a position rather than merely average evidence.

Replay governance changes the order of operations:

```text
Private committee first:
  private deliberation -> committee summary -> validator deference or rebellion

Replay first:
  public packet -> pinned route function -> public default -> public override
```

The model is not the governor. It is a reproducible work product. Validators
remain responsible for their votes. The governance improvement is that the first
object of coordination is not a private room. It is a packet, a route, a hash,
and an override trail.

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
P_{\text{miss}}^{\text{replay}}
=
P(X\le 8)
=
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
independent detection has a tail. Correlated summaries do not.

This is the mathematical reason replay can be cheaper without simply doing less
governance. If per-validator detection clears the blocking fraction, independent
review compounds. Committee concentration does not.

### The Load-Bearing Caveat

The independence is not free.

If every validator runs the same Qwen profile and blindly follows
`vote_replay_hash=1`, a model error becomes common-mode risk. The replay has
collapsed into a committee of one.

So the design has to protect the independence assumption:

- the deterministic rule floor catches obvious hard-stop cases;
- validators inspect the packet rather than merely copy the route;
- commit/reveal reduces ex-post copying from early visible votes;
- manual override remains public and easy to perform when the operator disagrees.

Replay governance is not "let the model vote." It is "make the public work item
cheap enough that independent validators can still do their job."

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

The accountability object is not the model answer by itself. It is the tuple:

\[
A_i = (P_i, M, H_o, R_i, V_i, O_i)
\]

where \(P_i\) is the amendment packet, \(M\) is the model/runtime profile,
\(H_o\) is the output hash, \(R_i\) is the parsed route, \(V_i\) is the
validator's vote, and \(O_i\) is either null or a public override reason.

Ordinary transparency is too weak. Publishing source code, a meeting note, or a
committee summary does not prove that the same procedure was applied to the same
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

Entropy does not decide governance. It tells the public what kind of
disagreement exists. A raw vote says who won. A replay dashboard says whether the
winning side followed the reproducible route or crossed it with public reasons.

## 6. Vast H200 Qwen/SGLang Replay

The replay target is an open-weight Qwen profile served through SGLang with
deterministic inference enabled. For this post, the run was executed on a Vast
H200 NVL instance and the machine receipt is included in the packet:

[machine receipt](/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/vast_lifecycle/machine_receipt.json)

| Field | Value |
|---|---|
| Provider run | `vast-39002186` |
| GPU profile | H200 NVL, 143771 MiB VRAM |
| Model | `Qwen/Qwen3.6-27B-FP8` |
| Runtime | SGLang OpenAI-compatible server |
| SGLang image | `lmsysorg/sglang:nightly-dev-cu13-20260523-c112f762` |
| Determinism flag | `--enable-deterministic-inference` |
| Max running requests | `1` |
| Thinking mode | disabled via chat template kwargs |

The public packet contains:

- 13 amendment packets;
- three Qwen/SGLang runs per packet;
- 41 simulated commit/reveal validators per run.

That produces 39 model outputs and 1,599 validator commit/reveal records, all
bound to the same model profile hash:

```text
a5b80f51a9cd02d11db357a115f0f22374319b8709787cc4a5b83694eef73c8f
```

The model profile hash includes the machine receipt hash, launch profile, packet
prompt settings, and replay parameters. The point is not that a remote GPU is
magic. The point is that a replay signer can show exactly which pinned
machine/runtime/model profile produced the governance work item.

Runtime details matter because "the model" is not a sufficient description of a
governance replay. The replay profile must bind weights, quantization format,
inference server, launch flags, prompt settings, packet hash, parser, and output
hash. Otherwise a later validator cannot tell whether a different output came
from a governance disagreement or a changed runtime.

The Qwen FP8 repository publishes quantized weights and configuration files, and
SGLang documents deterministic inference support and the
`--enable-deterministic-inference` flag. The claim is therefore not "this GPU is
trusted." The claim is "this governance artifact is replay-addressed."

## 7. Corpus Selection: 13 Controversial XRPL Amendments

The selection rule assigns points for public vote reversal, known bugs,
follow-up fixes, asset-control or compliance semantics, new financial primitives,
obsolete/disabled status, public debate, security/liveness implications, and
user-fund/accounting risk.

The resulting packet is here:

[benchmark packet](/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/)

The point of the corpus is not to create a popularity contest over historical
labels. It is to stress the replay route on governance-sensitive packets:
AMM-related fixes and reversals, obsolete bug-disabled amendments, issuer
control semantics, permissioned market access, vaults, lending, escrow, and new
token/accounting surfaces.

| amendment_or_event | why it is governance-sensitive | historical_route | deterministic_route | qwen_replay_route | replay_default_vote |
|---|---|---:|---:|---:|---:|
| AMM post-launch pool discrepancy | known bug; follow-up fix; user-fund/accounting risk | `DELAY_FOR_FIX` | `DELAY_FOR_FIX` | `DELAY_FOR_FIX` | `NO` |
| AMM / XLS-30 activation vote reversal | public vote reversal; known bug; user-fund/accounting risk | `DELAY_FOR_FIX` | `DELAY_FOR_FIX` | `DELAY_FOR_FIX` | `NO` |
| AMMClawback | asset-control semantics inside AMM pools | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| Batch | obsolete after bug discovery | `REJECT` | `REJECT` | `REJECT` | `NO` |
| Clawback | issuer asset-control primitive | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| fixAMMOverflowOffer | narrow AMM fix after known issue | `PROCEED` | `PROCEED` | `PROCEED` | `YES` |
| LendingProtocol | new financial primitive; off-chain underwriting surface | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| MPTokensV1 | new token accounting surface | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| PermissionDelegation | obsolete after bug discovery; delegated authority | `REJECT` | `REJECT` | `REJECT` | `NO` |
| PermissionedDEX | compliance-gated market access | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| PermissionedDomains | compliance infrastructure for permissioned finance | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| SingleAssetVault | pooled custody/accounting primitive | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |
| TokenEscrow | issued-asset custody/timing primitive | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD_FOR_CHALLENGE` | `HOLD` |

## 8. Scoring The Replay

The replay is scored as a governance triage system, not as an oracle.

For each packet \(i\), define:

\[
G_i = (s_i, h_i, r_i, D_i, u_i)
\]

where:

- \(s_i=1\) if the output is schema-valid;
- \(h_i=1\) if repeated runs converge to the same output hash for the packet;
- \(r_i\) is the parsed replay route;
- \(D_i\) is route deviation from the research label;
- \(u_i=1\) if the replay recommends `PROCEED` where the packet's hard-stop
  evidence or research label calls for `HOLD_FOR_CHALLENGE`, `DELAY_FOR_FIX`, or
  `REJECT`.

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

## 9. Results: Conservative, Reproducible, And Not Overclaimed

The H200/SGLang result is conservative:

- 13 packets;
- 39 Qwen outputs;
- 100% schema-valid output rate;
- 13/13 exact output-hash convergence across the three runs for each packet;
- 13/13 parsed-route convergence;
- 13/13 historical route alignment under the research labels;
- 0 unsafe proceed recommendations;
- 0 Qwen-vs-rule route disagreements.

Under the metric definitions above:

\[
\bar{s}=39/39=1.00
\]

\[
\bar{h}=13/13=1.00
\]

\[
R_U=0/13=0
\]

\[
\frac{1}{13}\sum_i |D_i|=0.
\]

So the result is not "the model governed correctly." The result is narrower and
stronger:

> Under this packet construction and these research labels, the replay profile
> produced schema-valid, hash-convergent, route-convergent conservative triage
> with no observed unsafe proceed recommendations.

That last number matters, but it should be read with statistical humility. A
zero count in a small sample is evidence, not proof of a zero underlying rate.

Using the rule-of-three heuristic, zero unsafe-proceed events in 13 unique packet
scenarios gives an approximate 95% upper bound of:

\[
3/13\approx 23.1\%.
\]

The exact one-sided binomial upper bound is about 20.6%. If one instead counts
the 39 repeated model outputs as separate output-level trials, the rule-of-three
bound is \(3/39\approx 7.7\%\), but those outputs are not 39 independent
governance scenarios because repeated runs per packet were intentionally
convergent.

This is why broader testing matters. To push a zero-failure 95% upper bound
below 1%, the relevant unit needs roughly 300 clean independent trials.

## 10. Why Use Qwen If The Rule Engine Tied It?

In this run, Qwen did not beat the deterministic rule engine on route choice. It
tied it.

That is not an embarrassment. It is the design.

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
That is challenge lift, not vote authority: a concrete work item before a
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

## 11. Attention Cost Model

The cost model is deliberately plain:

- 41 validators;
- two hours of review per validator for a full private-committee style pass;
- $250/hour fully loaded professional time;
- 13 governance events.

That yields:

\[
41\cdot 2\cdot 13=1066
\]

validator-hours, or:

\[
1066\cdot 250=\$266{,}500.
\]

The benchmark replay-default model is cheaper because it asks fewer people to do
deep work by default:

- one packet verification pass per event;
- a five-minute skim by each validator;
- three deep reviewers per event;
- public override when an operator disagrees.

| Process | Hours | Cost |
|---|---:|---:|
| Standing committee review | 1,066.00 | $266,500.00 |
| Deterministic alert review | 399.75 | $99,937.50 |
| Qwen replay-default triage | 75.83 | $18,958.33 |

Under the declared model, replay-default triage reduces attention by:

\[
1-\frac{75.83}{1066}=92.89\%.
\]

Those are cost-model numbers, not proof of safety. Change validator count,
hourly rate, skim minutes, deep reviewers, or review minutes and the conclusion
should update.

The exact 92.89% figure is the base case, not the claim. If ordinary review
would only take 45 minutes per validator, and replay overhead rises to a
10-minute skim plus five deep reviewers and a 20-minute packet check, replay
still uses 158.17 hours versus 399.75 hours, a 60.44% reduction. If ordinary
review takes three hours per validator under the same replay overhead, the
reduction is 90.11%.

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

This is not a claim that every pair colludes. It is an exposure model: private
coordination opportunities scale quadratically with repeat reviewers.

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

This is a coordination-surface proxy, not a safety proof. The real claim is the
scaling law: private deliberation creates \(O(r^2)\) potential coordination
edges; replay-first triage creates \(O(n+k)\) public inspection and override
records.

### Override Burden

The system does not ban override. It makes override burden visible.

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

## 12. Reproduction Scripts

The packet can be rebuilt and checked with:

```bash
python3 scripts/build_xrpl_amendment_replay_corpus.py \
  --output static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z

python3 scripts/run_qwen_amendment_replay.py \
  --corpus static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/amendment_packets \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/vast_lifecycle/machine_receipt.json \
  --runs 3 \
  --validators 41

python3 scripts/summarize_xrpl_amendment_replay.py \
  --packet static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z

cd static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z
sha256sum -c SHA256SUMS.txt
```

The actual post run used a local SSH tunnel into the Vast container:

```bash
ssh -N \
  -L 18000:127.0.0.1:8000 \
  -p <vast_ssh_port> root@<vast_ssh_host>
```

The packet records the sanitized Vast machine receipt, served model response,
and SGLang log tail under `vast_lifecycle/`.

Packet root:

```text
b809a6b2b35d5dfccd8fbc3b5880ad14f8707886f88f84e11efe4e574b74f894
```

## 13. What This Proves

This proves that the replay-default pattern is operationally coherent on a
production-like H200/SGLang path.

For a real governance event, validators can receive the same packet, run the
same route function, commit to an output hash, reveal the output, and preserve a
public trail of whether they followed or overrode the default. The process
directly attacks two costs that ordinary governance hand-waves away: attention
cost and private coordination cost.

It also shows that the model does not need positive authority. In this replay,
the useful outputs are conservative routes: delay for known-bug AMM packets,
reject obsolete bug-disabled packets, hold governance-sensitive financial
primitives for challenge, and proceed on a narrow AMM fix.

The strongest claim is institutional, not magical:

> A public replay primitive can make the cheapest governance path also the most
> inspectable path.

## 14. What This Does Not Prove

This does not prove that Qwen is smarter than the rule engine on route choice.
It tied the rule engine in this run.

It does not prove that the 13 research labels are the only valid labels for
these events.

It does not prove that any future amendment should be accepted because a model
says `PROCEED`.

It does not prove the true unsafe-proceed rate is zero. The sample is too small
for that. The zero-event result is a useful negative finding and a reason to run
broader tests, not a safety theorem.

It also does not remove the committee option. Some packets will earn a committee.
The claim is only that committee formation should be the second move, not the
first. Start with a public replay object. Escalate when the packet actually
requires concentrated expert deliberation.

The stronger claim still requires broader profile evidence: H100/H200 repeated
checks under the same corpus, cross-profile drift reporting, Apple/MLX or other
non-NVIDIA controls where practical, packet hashes, prompt hashes,
parsed-output hashes, and public replay scripts.

That is the right end state: not AI as governor, and not a private committee as
governor. Public replay primitive first; human override second; private committee
only when the packet earns one.

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

This appendix is illustrative, not empirical. The independence assumption is
strong, \(p\) is not estimated here, and real influence is correlated. The useful
point is the threshold structure: replay-first governance moves disagreement
from a small private recommendation threshold to a public mass-override
threshold.

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
