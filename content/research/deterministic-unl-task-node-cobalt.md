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
uses one has to answer the same question: who gets on it, and why. The honest
answer on most ledgers is that seats are paid for. Grants, equity, "market
development fees" and token distributions buy the appearance of independent,
institutional validation. Post Fiat spent the last two days measuring whether
an institution-prestige rubric could pick validators for us. It cannot. It
rewards exactly the kind of purchased legitimacy we want to avoid, and it
scores every operator who actually runs Post Fiat's network at zero. This
proposal replaces that idea with one that fits what Post Fiat already is: a
validator seat should be derived, deterministically and replayably, from a
Task Node identity, and the resulting list should be ratified through Cobalt
with no token incentive attached.

## What the incumbents actually pay

The clearest public record is Ripple's. Its University Blockchain Research
Initiative has committed more than $80 million to over sixty universities
since 2018, and several grants explicitly fund the operation of XRP Ledger
validators. Yonsei, the University of South Florida and the University of
Nicosia all appear on the default UNL and all received UBRI money. On the
commercial side, MoneyGram received a $50 million equity investment plus
roughly $61.5 million in "market development fees" across 2019 and 2020 for
using Ripple's products, and disclosed that it sold the XRP it received
immediately. PNC and goLance were named as receiving incentives, and the SEC's
complaint alleged that billions of XRP were distributed to counterparties in
exchange for labour and market-making rather than sold at market.

Two honest notes. First, we searched for a documented Barclays incentive and
found none; Barclays has been described as an early experimenter with Ripple's
technology, but there is no public record of a payment tied to validation or
adoption, so we do not claim one. Second, none of this is illegal or even
unusual. It is simply what it costs to make a list look independent when the
underlying network has no native notion of who anyone is.

Our own numbers say the same thing from the other side. When we replayed a
prestige-based identity rubric across 55 validator profiles on pinned
hardware (192 of 192 judgments byte-identical across two H200s), the highest
scorers on the XRPL side were Ripple itself and grant-funded universities. All
twenty Post Fiat validators scored zero, because a prestige rubric has nothing
to say about a community operator with a year of clean uptime and a long
record of verified work. The rubric was measuring what money can buy.

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
  testnet rounds. The L1 is designed as a ratifier, not an evaluator.
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

An operator runs a CLI command that signs a challenge with the validator
master key. The operator's Task Node wallet countersigns the same challenge.
The pair is submitted as a memo transaction on the PFT Ledger from the Task
Node wallet, so the binding is public, timestamped and replayable without
trusting the Task Node server. New evidence fields under
`validator.identity.tasknode_binding.*` carry the wallet address, the
transaction hash, the challenge digest and both signatures. A binding can be
revoked the same way. One wallet may bind at most one validator; a second
binding attempt is itself evidence of shared control.

### 2. Derive `accountability_score` from replayed work history

The score is computed by a deterministic function of the account's task
events as replayed from ledger pointers, never from the live database. Inputs
are: count of accepted network tasks (not personal tasks), tenure measured
from the first rewarded task, verification pass rate, open and resolved
disputes, and current badge state. Weights are published constants. Because
task payloads on IPFS are encrypted, the operator discloses the relevant
payload keys into the evidence packet at binding time; a packet that cannot
be decrypted and replayed holds, exactly as missing evidence holds today. No
part of this step involves a language model.

### 3. Derive independence from the graph, not from a form

`rho_score` and the control-group gates are populated from three
deterministic sources: the one-wallet-one-validator rule above, the
funding-source graph of the bound wallet on the PFT Ledger (who first funded
it, who it repeatedly settles with), and profile correlation across operator
manifests. Our existing correlation tool already does the last part and
correctly identifies the one real cluster on the current list, the three
Foundation-run validators. Where a qualitative judgment is genuinely required,
for example whether two named entities are the same organisation, it is made
by a pinned model over a frozen packet with the answer replayed byte for byte,
and it can only ever hold, never admit.

### 4. Keep the selector, change the inputs

Admission Policy V1 does not change shape. It receives the same fields it
already expects, now populated from Task Node evidence, and emits the same
registry-delta candidates. Those pass through old-rule authorization and
Cobalt ratification unchanged. The first run is shadow-only: derive the list,
publish the diff against the round-20 testnet list, and explain every
difference in public before anything is ratified.

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
banned or suspended in Kenya, Spain, Portugal, Hong Kong, the Philippines and
Thailand, which would exclude community operators by geography. Verification
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

Ranking uses a web-of-trust walk from several seeds (EigenTrust and SybilRank
are the reference designs), not from the Foundation alone. The property that
matters is that a cluster of fake accounts can only attach to the honest graph
through the few edges its creator can actually earn, so its aggregate trust is
bounded no matter how many accounts it contains. Combined with tenure, which
cannot be parallelised, and a hard cap on validator seats per detected
cluster, this gives a uniqueness signal that is entirely public, entirely
replayable, and produced by the same activity the network already rewards.

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
decentralise control on day one. What it does is make the exercise of that
control legible: every input a rule can see is on the PFT Ledger or IPFS,
every model judgment is replayable, and every registry change carries the
packet it was derived from. The independent-proposer path is the mechanism
that turns legibility into decentralisation, and this proposal should remain
SHADOW_ONLY until at least one non-Foundation operator can propose and ratify.

## Rollout

- Phase 0: publish the scoring function and weights; implement the
  key-to-wallet binding CLI and the `validator.identity.tasknode_binding.*`
  fields; existing operators bind voluntarily.
- Phase 1: shadow-derive the list from bound accounts each week alongside the
  current testnet rounds; publish the diff and reasons.
- Phase 2: add vouch and co-work edges, run the trust walk, publish cluster
  assignments; still shadow.
- Phase 3: after the independent-proposer path is live and a non-Foundation
  ratifier has signed a shadow round, promote the derived list to the ratified
  registry.

At no phase is any token paid for a seat. An operator's cost of entry is time
and verified work, and both are visible to everyone.

## What this does not claim

It does not claim to identify legal persons. It does not claim that a Task
Node account cannot be sold. It does not claim the AI reviewer is unbiased,
only that its bias is fixed, replayable and therefore contestable. It does not
claim the Foundation is out of the loop; it claims the loop is public. And it
does not claim institutions are unwelcome. An exchange or a university that
wants a seat is welcome to earn it the same way everyone else does: bind a
wallet, do the work, get vouched for by people who know you.

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
