---
title: "Proposal: derive the UNL from Task Node identity and ratify it through Cobalt"
date: 2026-09-04T00:00:00Z
summary: "Validator lists on public ledgers are bought with grants and market-development fees. Post Fiat should instead derive its validator list deterministically from Task Node identity: a proven wallet, a replayable work history, and a public vouch graph. This proposal grounds that in the existing Admission Policy V1, the Task Node ledger replay, and the Cobalt ratification path, and evaluates World ID against a Task Node social graph for one-person-one-seat."
categories:
  - Post Fiat Research
tags:
  - UNL
  - Cobalt
  - Task Node
  - Validator Identity
  - Sybil Resistance
  - Post Fiat L1
robotsNoIndex: false
---

## The problem in one paragraph

A Unique Node List is the set of validators a node trusts. Every chain that
uses one has to answer the same question: who gets on it, and why. On the
ledgers with a public record, the money and the seats go to the same places:
grants, equity, "market development fees" and token distributions flow to
the institutions whose names then appear on the list, and nothing in the
protocol can tell an earned seat from a subsidised one. Post Fiat spent the
last two days measuring whether
an institution-prestige rubric could pick validators for us. It cannot. It
rewards exactly the kind of purchased legitimacy we want to avoid, and it
scores every operator who actually runs Post Fiat's network at zero. This
proposal replaces that idea with one that fits what Post Fiat already is: a
validator seat should be derived, deterministically and replayably, from a
Task Node identity, and the resulting list should be ratified through Cobalt
with no token incentive attached.

## Terms used below

- **UNL**: the list of validators a node trusts to agree on the next ledger.
- **Cobalt**: Post Fiat's protocol for ratifying changes to that list. It
  decides whether a proposed change is safe; it does not decide who deserves
  a seat.
- **PFT Ledger**: Post Fiat's existing XRPL-derived ledger, where Task Node
  activity is recorded.
- **Task Node**: the Foundation-run system where community members do
  verified work for the network and are paid for it. Its accounts are
  wallets.
- **`pf.ptr/v4` pointer**: a small memo transaction on the PFT Ledger that
  points at an encrypted file on IPFS; every step of a task is recorded as
  one.
- **Hive project / Team grant**: Task Node's multi-person work units.
- **Round 20**: the most recent weekly testnet round of the current
  validator-evaluation pipeline, used here as the baseline list.
- **`accountability_score`**: an existing admission input, 0–100, meant to
  measure whether an operator is a known and answerable party.
- **`rho_score`**: an existing admission input measuring how correlated a
  validator is with others already on the list; zero or below means no
  detected correlation.

## What the incumbents actually pay

The clearest public record is Ripple's. Its
[University Blockchain Research Initiative](https://ripple.com/university-blockchain-research-initiative/)
has committed more than $80 million to over sixty universities since 2018, and
several grants explicitly fund the operation of XRP Ledger validators. Yonsei,
the University of South Florida and the University of Nicosia all appear on
the default UNL and all received UBRI money. On the commercial side, MoneyGram
received a $50 million equity investment plus roughly $61.5 million in
"market development fees" across 2019 and 2020 for using Ripple's products,
and disclosed in its
[SEC filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001273931&type=10-K)
that it sold the XRP it received immediately. PNC and goLance were named as
receiving incentives, and the
[SEC's complaint](https://www.sec.gov/litigation/complaints/2020/comp-pr2020-338.pdf)
alleged that billions of XRP were distributed to counterparties in exchange
for labour and market-making rather than sold at market.

Three honest notes. First, we searched for a documented Barclays incentive and
found none; Barclays has been described as an early experimenter with Ripple's
technology, but there is no public record of a payment tied to validation or
adoption, so we do not claim one. Second, none of this is illegal or even
unusual. It is simply what it costs to make a list look independent when the
underlying network has no native notion of who anyone is. Third, none of it
is proof that any particular seat was sold. It is proof that the money and
the seats flow to the same places, and that nothing in the protocol can tell
the difference.

Our own numbers say the same thing from the other side. When we replayed a
prestige-based identity rubric across 55 validator profiles on pinned
hardware (192 of 192 judgments byte-identical across two separately owned
H200s; packet set `8051f392…`, aggregate `9d6935e2…`, results in
`docs/governance/institution-reputation-packets-h200-results-20260904.md` on
the `integrate/arc-tier4-current-v2-20260901` branch at `59f60713`), the
highest scorers on the XRPL side were Ripple itself and grant-funded
universities. All twenty Post Fiat validators scored zero, because a prestige
rubric has nothing to say about a community operator with a year of clean
uptime and a long record of verified work. The rubric was measuring what
money can buy.

## What Post Fiat already has

Post Fiat is unusual in that it already has a working definition of identity
that is neither a passport nor a brand name. It is a Task Node account.

A Task Node account is a wallet whose control has been proven to the server
with a signed challenge (the wallet signs, the server never sees the seed),
attached to a history of tasks that were proposed, accepted, submitted,
verified by an AI reviewer and rewarded. That lifecycle is not just rows in a
database. Each step is written to the PFT Ledger as a `pf.ptr/v4` memo pointer
to an encrypted IPFS payload, and the Task Node database is designed to be
rebuilt from those pointers rather than the other way round. Verified
eligibility is stored as badges, which gate which network tasks a user can be
routed. A daily airdrop worker scores rewarded work. Every account also gets a
Nostr identity derived from its wallet, with a NIP-05 handle at the Task Node
domain and private messaging over NIP-17.

On the L1 side, the pieces for a rule-driven validator list already exist and
are documented:

- Admission Policy V1 is a pure selector in `postfiat-consensus-cobalt`. Its
  controlled-testnet floors are uptime of at least 9,950 basis points over the
  window, `accountability_score >= 70`, `rho_score <= 0`, no shared operator,
  release-manager, key-management or funding-source group, a signed operator
  manifest with a proved key-domain binding, and `cobalt.linkedness_safe`.
  Missing evidence holds; a clean pass emits an `add` registry-delta
  candidate, which is decision support and only changes registry state after
  old-rule authorization.
- The evidence field registry forbids specific inputs to any rule:
  social-media reputation, private KYC status, private messages, uncollected
  web search, unbounded browsing, raw IP geolocation as proof of jurisdiction,
  and any human label not present in the packet.
- The dynamic UNL evidence pipeline already freezes a packet, pins it to IPFS,
  anchors it with a memo transaction on the PFT Ledger, replays the judgment,
  and converges by commit-reveal. It has run for more than twenty weekly
  testnet rounds. It already defines `DynamicUnlValidatorBindingV1`, which
  maps one PFT Ledger secp256k1 master key to exactly one L1 validator ID and
  ML-DSA-65 hot key, and applies safe-churn limits so a proposal can never
  replace more of the list than the trust graph can absorb in one round. The
  L1 is designed as a ratifier, not an evaluator.
- Cobalt is bounded to registry and trust-graph ratification. Finality is
  consensus v2. The independent-operator proposal path spec states plainly
  that the Foundation currently controls every proposer and signer and that
  an independent path is the mandatory follow-on.

What is missing is the join. Nothing today connects a validator's master key
to a Task Node account, and nothing turns a Task Node work history into the
`accountability_score` and `rho_score` fields that Admission Policy V1 already
consumes. That join is the proposal.

## The proposal

### 1. Bind the validator key to a Task Node wallet

A Task Node wallet is a PFT Ledger wallet, so this is an extension of
`DynamicUnlValidatorBindingV1` rather than a new mechanism. An operator runs a
CLI command that signs a challenge with the validator master key. The
operator's Task Node wallet countersigns the same challenge. The pair is
submitted as a memo transaction on the PFT Ledger from the Task Node wallet,
so the binding is public, timestamped and replayable without trusting the
Task Node server. New evidence fields under
`validator.identity.tasknode_binding.*` carry the wallet address, the
transaction hash, the challenge digest and both signatures.

Rotation and compromise: a binding is superseded by a later binding memo
signed by the same wallet, and revoked by a memo signed by either key. If the
validator key is rotated through the normal L1 path, the new key must be
re-bound within one evaluation window or the validator holds. If the wallet
is compromised, the operator revokes from the validator side and the
work-history attached to that wallet is frozen at the revocation ledger index;
it can be re-attached to a new wallet only by a vouch from two accounts that
held co-work edges with the old one. One wallet may bind at most one
validator; a second binding attempt is itself evidence of shared control and
places both validators in the same control group.

### 2. Derive `accountability_score` from replayed work history

The score is computed by a deterministic function of the account's task
events as replayed from ledger pointers, never from the live database. No
part of this step involves a language model.

Because task payloads on IPFS are encrypted, the packet does not contain them.
Instead Task Node publishes, per account and per evaluation window, a signed
work digest: the list of `pf.ptr/v4` pointer hashes it counted, the outcome
it recorded for each, and the resulting inputs below. The digest is signed by
the Task Node publishing key and anchored on the PFT Ledger. Anyone can check
that every pointer in the digest exists on the ledger and was emitted by the
bound wallet; the operator can additionally disclose payloads to a reviewer
in a dispute. Nothing private enters the packet, and a digest that does not
reconcile with the ledger holds.

Indicative formula, over a rolling 180-day window, all terms clamped to
[0, 1]:

| Term | Definition | Weight |
| --- | --- | --- |
| `work` | accepted network tasks (not personal tasks) ÷ 40 | 35 |
| `tenure` | days since first rewarded task ÷ 365 | 25 |
| `quality` | verification pass rate over the window | 20 |
| `standing` | 1 minus (open disputes ÷ 3) | 10 |
| `badge` | 1 if a verified operator badge is current, else 0 | 10 |

`accountability_score` is the weighted sum, so the existing floor of 70 is
reachable, for example, by an operator with roughly a year of tenure, twenty
accepted network tasks, a 90 percent pass rate, no open disputes and a
current badge. The numbers are proposals for the shadow phase and are meant
to be tuned against the published diff, but they are stated so that the first
shadow run has something concrete to be wrong about.

### 3. Derive independence from the graph, not from a form

`rho_score` and the control-group gates are populated from three
deterministic sources: the one-wallet-one-validator rule above, the
funding-source graph of the bound wallet on the PFT Ledger, and profile
correlation across operator manifests. Our existing correlation tool already
does the last part and correctly identifies the one real cluster on the
current list, the three Foundation-run validators.

Funding edges are deliberately narrow so that ordinary use does not look like
collusion. Two wallets share a funding edge only if one was the first funder
of the other, or if more than half of either wallet's inbound value over the
window came from the other. Exchange and Foundation distribution addresses
are on a published exclusion list. A funding edge places two validators in
the same funding-source control group, which the existing selector already
treats as a hold for the second one, not as a rejection of both.

Where a qualitative judgment is genuinely required, for example whether two
named entities are the same organisation, it is made by a pinned model over a
frozen packet with the answer replayed byte for byte, and it can only ever
hold, never admit.

### 4. Keep the selector, change the inputs

Admission Policy V1 does not change shape. It receives the same fields it
already expects, now populated from Task Node evidence, and emits the same
registry-delta candidates. Those pass through old-rule authorization and
Cobalt ratification unchanged. The first run is shadow-only: derive the list,
publish the diff against the round-20 testnet list, and explain every
difference in public before anything is ratified.

Liveness and overlap are not the identity layer's job, but the identity layer
must not be able to break them. The derived list is a candidate set, not a
replacement list. The existing safe-churn limit bounds how many additions and
removals a single round may propose, so the ratified list changes by at most
that budget per round regardless of how many new accounts qualify. Removals
for identity reasons (a revoked binding, a newly detected control group) are
proposed as holds first and only become removals after a full evaluation
window.

Worked example on the current list, measuring overlap as the intersection
of two nodes' views divided by their union. With twenty validators, a round
that both removes one and adds one leaves a node one round behind sharing 19
of 21 with a current node, about 90.5 percent, which only just meets XRPL's
documented 90 percent worst-case fork-safety overlap and fails it for a node
two rounds behind (18 of 22, about 82 percent). A swap round does not reach
95 percent until the list has 39 validators. So the rule this proposal adds
is one change per round, either an addition or a removal, until the list
reaches 39. On twenty validators that gives 19 of 20 or 20 of 21 for a node
one round behind, 95 percent either way, and no worse than 18 of 20 (90
percent) for a node two rounds behind. Deltas must also be built on a
registry root no older than one round, which the registry's existing
stale-root check enforces. Every emitted delta is checked against the trust
graph's transition budget before it reaches Cobalt.

Appeals: an account whose packet holds can see exactly which field held it,
because every hold names the field and the replayed value. The operator fixes
the evidence (re-binds a key, resolves a dispute, publishes a manifest) and
the next window re-evaluates. There is no discretionary override path, and
that is intentional; the remedy for a wrong rule is a public rule change.

### 5. Make the AI reviewer auditable rather than trusted

Task Node's verification is done by a model. That is acceptable for a
validator list only if the judgment can be reproduced. The pattern is the one
we have already proven: freeze the evidence, pin the model and weights, run on
pinned hardware, and require byte-identical output across independent
machines before the result is anchored. The 192 of 192 replay on two
separately owned H200s is the existence proof. Judgments that do not replay
are discarded, not averaged.

## One person, one seat

A work history proves that someone did work. It does not prove that the
"someone" behind ten validators is ten people. Two approaches were evaluated.

### World ID

World ID (Worldcoin) issues a proof of unique personhood after iris enrolment
at an Orb. It has genuine strengths: the uniqueness check is strong, the
proof is zero-knowledge so the validator packet would carry a nullifier rather
than a biometric, and it is already used by other protocols for exactly this
purpose.

The problems are decisive for a required check. Enrolment needs physical
hardware, concentrated in a handful of countries, and the project has been
banned, suspended or ordered to stop processing biometrics in Kenya, Spain,
Portugal, Hong Kong, Germany, Brazil, Indonesia, South Korea and Colombia,
which would exclude community operators by geography. Verification
is centralised on Tools for Humanity and is not replayable from public data,
which conflicts directly with the evidence pipeline's requirement that every
rule input be reconstructible. Biometric enrolment is permanent, so a
compromise cannot be rotated like a key. And in practice a World ID proves
that a human enrolled, not who operates the validator; verified IDs are
already rented on secondary markets.

Verdict: World ID can be accepted as an optional, additive attestation that
raises confidence in an operator's independence. It must never be a
requirement, and it must never be the only evidence of uniqueness.

### A Task Node social graph

The better answer is already half-built. Task Node accounts have wallets,
public Nostr identities, and shared work. That is a graph, and Sybil
resistance on graphs is a well-studied problem.

Edges come from three public, replayable sources:

- explicit vouches: a signed statement from one account that it knows the
  operator of another, published as a PFT Ledger memo or a public Nostr event
  (never a NIP-17 private message, which the field registry already forbids);
- co-work: two accounts that completed the same Hive project or shared a Team
  grant, as replayed from task pointers;
- funding: the first-funder and repeated-settlement edges from step 3.

Ranking uses a web-of-trust walk in the style of
[EigenTrust](https://nlp.stanford.edu/pubs/eigentrust.pdf) and
[SybilRank](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final73.pdf).
The seed set is not chosen by the Foundation. It is the currently ratified
validator list at the start of the window, with Foundation-bound validators
removed, and each seed carries equal weight. On today's list that is
seventeen seeds. That makes the seeds a public, already-ratified fact rather
than a lever, and it means the Foundation's own validators receive trust only
through edges from other operators.

Proposed parameters, all published constants: edge weights of 1 for a vouch,
1 per shared Hive project or Team grant capped at 3, and 2 for a funding
edge; rows normalised to sum to 1; power iteration for 20 steps with damping
0.85 back to the uniform seed vector; clusters cut where conductance falls
below 0.1. That is enough to recompute the walk from the ledger alone.

The walk does two things and they should be kept apart. It assigns every
account to a cluster, so the seat cap can be enforced. And it produces a
connectivity requirement: to hold a seat, an account must carry at least
1/(2N) of the walk's stationary mass, where N is the list size, which in
practice means at least two vouch or co-work edges from accounts in two
different existing clusters. An account with no path to the seeds is not
admissible, however good its work history, because without that requirement
an attacker could farm many unconnected accounts and have each treated as
its own cluster. Vouches are accountable: a vouch is public, and if two
accounts an operator vouched for later collapse into the same cluster, that
operator's outgoing vouch weight is halved for the next window.

Two things keep this from becoming incumbency. The connectivity requirement
is met by edges from any seed-connected account, not from seeds themselves,
so any two established members in different clusters can bring in a
newcomer; the seeds define where trust starts, not who may sponsor. And the
seed set can only change by the churn budget each round, so capturing it
means winning many public rounds in a row, each with a published diff.

The property that matters is that a cluster of fake accounts can only attach
to the honest graph through the few edges its creator can actually earn, so
its aggregate trust is bounded no matter how many accounts it contains. No
cluster may hold more than two validator seats or ten percent of the list,
whichever is larger; on a twenty-validator list that is two seats, and the
cap grows only as the list does. Tenure helps because buying old accounts is
the only way to parallelise it, and bought accounts drag their funding and
vouch edges with them into the buyer's cluster.

Cost of the obvious attacks, assuming the parameters above:

| Attack | What it costs | What stops it |
| --- | --- | --- |
| Vouch ring | N accounts vouching for each other | Ring has no inbound edges from seeds; walk assigns it near-zero trust; cluster cap limits it to two seats regardless |
| Buying aged accounts | Market price of accounts with ≥1 year tenure and ≥20 accepted tasks | Transfer of control changes funding pattern; bought accounts inherit the buyer's first-funder and settlement edges and collapse into one cluster |
| Farming work with parallel identities | Real reviewer-verified work per identity, over 180 days, per seat, plus two sponsors from different clusters per identity | Cost scales linearly with seats; the connectivity requirement means the farmer needs outside sponsors for every identity, and sponsors whose vouchees cluster together lose vouch weight |
| First-funder manipulation (funding a rival to taint them) | One transaction | Edge requires first-funder *or* majority-of-inflow; a one-off transfer to an already-funded wallet creates no edge |
| Foundation choosing who wins | Nothing today | Seeds are the ratified non-Foundation list; every input is on-ledger; SHADOW_ONLY until an independent ratifier signs |

None of this makes a seat impossible to buy. It makes the price of a seat the
price of a year of genuine, publicly verifiable participation in the network,
paid per seat, which is exactly the cost we want it to have.

For comparison: BrightID uses social-graph verification parties and is closest
in spirit but adds its own centralised app; Proof of Humanity uses video
submissions and deposits with adversarial challenges, which is strong but slow
and expensive per person; Gitcoin Passport aggregates many weak stamps, which
is flexible but easy to farm. The Task Node graph has an advantage none of
them do, which is that the edges are a by-product of paid, verified work
rather than a ceremony performed to obtain an identity.

## Centralisation, stated plainly

The Foundation operates Task Node, the AI reviewer, and today every Cobalt
proposer and signer. Deriving the UNL from Task Node therefore does not
decentralise control on day one.

The specific gap is task outcomes. Because payloads are encrypted, an outside
observer can verify that a pointer exists, that the bound wallet emitted it,
and that Task Node signed a digest counting it. They cannot, from public data
alone, verify that the reviewer's verdict inside the payload was what the
digest says, or that no eligible task was left out. Until that changes, the
`work`, `quality` and `standing` terms of the accountability score are a
Foundation attestation, and this document says so rather than hiding it
behind the word "replayable".

Three things narrow that gap. The reviewer model, weights and prompt are
pinned and their hashes published, so a verdict can be re-run by anyone the
operator discloses the payload to. The digest carries the hash of each
verdict, so a disclosed payload either matches the digest or proves it wrong.
And the exit criterion for Phase 3 includes an independent ratifier
re-running the pinned reviewer over a random five percent of disclosed
payloads from the window and matching every verdict hash; any mismatch is
published and blocks promotion. Omission (leaving an eligible task out of a
digest) is detectable by the operator, who sees their own pointers on the
ledger, and is grounds for a public dispute against the digest.

What the proposal does on day one is make the exercise of Foundation control
legible: every input a rule can see is on the PFT Ledger or IPFS, every model
judgment is fixed and re-runnable, and every registry change carries the
packet it was derived from. The independent-proposer path is the mechanism
that turns legibility into decentralisation, and this proposal should remain
SHADOW_ONLY until at least one non-Foundation operator can propose and ratify.

On money: this proposal says nothing about how operators are compensated for
running a validator. It removes payment for the seat itself.

## Rollout

- Phase 0: publish the scoring function and weights above as constants in
  `postfiat-consensus-cobalt`; implement the key-to-wallet binding CLI, the
  Task Node signed work digest, and the
  `validator.identity.tasknode_binding.*` fields; existing operators bind
  voluntarily.
- Phase 1: shadow-derive the list from bound accounts each week alongside the
  current testnet rounds; publish the diff and reasons.
- Phase 2: add vouch and co-work edges, run the trust walk, publish cluster
  assignments; still shadow. Exit criterion: three consecutive weekly rounds
  in which the shadow list and the ratified list differ only by additions the
  Foundation did not propose.
- Phase 3: after the independent-proposer path is live and a non-Foundation
  ratifier has signed a shadow round and completed the five-percent reviewer
  replay above with zero mismatches, promote the derived list to the ratified
  registry.

At no phase is any token paid for a seat. An operator's cost of entry is time
and verified work, and both are visible to everyone.

## What this does not claim

It does not claim to identify legal persons. It does not claim that a Task
Node account cannot be sold, only that a sold account is expensive and drags
its graph with it. It does not claim the AI reviewer is unbiased or correct;
byte-identical replay proves the judgment is fixed and therefore
contestable, not that it is right. It does not claim the Foundation is out
of the loop; it claims the loop is public. It does not claim the weights
above are final; they are the first thing the shadow diff should argue with.
And it does not claim institutions are unwelcome. An exchange or a university
that wants a seat is welcome to earn it the same way everyone else does: bind
a wallet, do the work, get vouched for by people who know you.

## Sources

- `docs/governance/validator-registry.md` (Admission Policy V1 gates)
- `docs/governance/validator-evidence-field-registry.md` (forbidden rule inputs)
- `docs/governance/cobalt-independent-operator-proposal-path-research-spec.md`
- `docs/governance/dynamic-unl-l1-evidence-source-note.md`
- `docs/governance/institution-reputation-packets-h200-results-20260904.md`
- Task Node: `auth-wallet-boundary.md`, `pftl-live-task-replay.md`,
  `badge-based-network-task-routing.md`, `daily-airdrop-worker.md`, `nostr.md`
- Ripple UBRI public announcements; MoneyGram 10-K and 10-Q disclosures
  2019–2020; SEC v. Ripple Labs complaint (December 2020)
- EigenTrust (Kamvar et al., 2003); SybilRank (Cao et al., 2012)
