# Origination Replay: Article and Experiment Plan

Status: working requirements document  
Companion artifacts:

- `static/benchmarks/xrpl-xls-provenance-20260603T230503Z/`
- `docs/research/the-system-is-what-it-does-requirements.md`

## 1. Core Thesis

Title:

> Origination Replay

Core line:

> The vote is visible. The whence is not.

The article is not about replacing validator governance. It is about the layer before validator governance: the off-chain process by which amendment-shaped options enter the menu.

The claim is:

> XRPL governance already has an off-chain origination layer. LLM replay is useful if it makes that layer public, replayable, and forkable.

The article should refuse the stronger and worse claim:

> The model should decide which amendments are good or which amendments should pass.

The intervention is narrower:

> Make upstream menu formation observable.

## 2. Status Quo Evidence

Use the provenance packet as the status quo section.

Current frozen packet:

```text
static/benchmarks/xrpl-xls-provenance-20260603T230503Z/
```

Source snapshot:

```text
XRPLF/XRPL-Standards
commit: 9ecf2b9db9cdc6597d9b4997b823dbf523d9b45b
source date: 2026-05-28T17:12:15+02:00
```

Article-safe numbers:

```text
78 XLS proposals parsed
46 amendment proposals parsed
31/46 amendment proposals are direct Ripple-authored
44/46 amendment proposals have strict source-backed XRP/XRPL author provenance
2/46 amendment proposals lack strict direct XRP-author evidence
```

Interpretation:

> The amendment menu is not random public emergence. It is overwhelmingly authored by Ripple or identifiable XRP/XRPL ecosystem insiders.

Important boundary:

> "Source-backed XRP/XRPL author provenance" does not mean Ripple endorsed the proposal, validators supported it, or the proposal was good. It means the listed author identity can be tied by source evidence to Ripple, XRPL Labs, or XRP Ledger ecosystem development.

## 3. Required Evidence Before Drafting

### EP-1: Provenance Packet

Already built.

Required use:

- Cite `31/46` direct Ripple-authored amendment proposals.
- Cite `44/46` strict source-backed XRP/XRPL author-provenance amendment proposals.
- Link to `REPORT.md`, `xls_provenance.csv`, `summary.json`, and `SHA256SUMS.txt`.

Do not use broad/recurring author support as a headline claim. Keep it in appendix or supporting notes.

### EP-2: Outcome and Status Reconciliation

Build a table for every amendment proposal with:

- XLS id
- title
- XLS status: `Final`, `Draft`, `Stagnant`, `Deprecated`, `Withdrawn`
- origin tier: Ripple / explicit XRPL org / external XRP ecosystem author / no direct support
- known XRPL amendment name, if any
- mainnet state: enabled / open for voting / not present / unknown
- source URL for status
- source URL for mainnet state

Reason:

> `Final` is not the same thing as mainnet-enabled.

This table is required before making any outcome-asymmetry claim.

### EP-3: Shadow Origination Demo

Run the replay harness on unresolved amendment proposals:

- `Withdrawn`
- `Draft`
- `Stagnant`
- `Deprecated`

Initial corpus from the provenance packet: 27 non-final amendment proposals.

The demo claim is:

> Here is a public, replayable first pass over the unresolved amendment backlog.

The demo must not claim:

> These amendments should pass.

## 4. Alternative Process

The proposed process is:

```text
public evidence packet
-> pinned replay function
-> typed work item
-> omission log
-> public hash receipt
-> forkable output
```

The process originates public agenda artifacts. It does not decide governance outcomes.

### Inputs

Each origination packet should contain:

- `packet_id`
- `schema_version`
- `amendment_identity`
- `question`
- `allowed_output_labels`
- `source_list`
- `source_excerpts`
- `known_status`
- `known_dependencies`
- `related_specs`
- `implementation_links`
- `open_discussion_links`
- `risk_surface_tags`
- `missing_evidence`
- `omission_log`
- `packet_compiler`
- `packet_hash`

### Outputs

The model emits a typed work item, not a vote recommendation.

Required output shape:

```json
{
  "work_item_label": "OPEN_RESEARCH_PACKET",
  "problem_statement": "...",
  "source_citations": ["source_id"],
  "missing_evidence": ["..."],
  "risks": ["..."],
  "fork_points": ["..."],
  "non_claims": [
    "This is not a validator vote recommendation.",
    "This does not decide whether the amendment should pass."
  ]
}
```

Allowed labels:

```text
OPEN_RESEARCH_PACKET
NEEDS_IMPLEMENTATION_OWNER
NEEDS_SECURITY_REVIEW
MERGE_WITH_RELATED_SPEC
WAIT_FOR_DEPENDENCY
PUBLIC_DISCUSSION_NEEDED
CLOSE_AS_SUPERSEDED
INSUFFICIENT_EVIDENCE
```

## 5. LLM Experiment Design

Use Qwen/SGLang for the replay artifact. API models can be used for editorial review, but not as the deterministic evidence base.

### Run Set

Corpus:

```text
27 non-final XRPL amendment proposals
```

Model/profile:

```text
Qwen profile used by the governance replay harness
SGLang deterministic inference
H200 primary run
```

Repetition:

```text
5 repeats per packet
27 packets
135 total runs
```

Minimum success bar:

```text
135/135 schema-valid outputs
exact parsed-output hash convergence per packet
raw output hashes recorded
no authority-boundary failures
no uncited factual claims in required fields
```

## 6. Determinism Tests

### Test 1: Packet Determinism

Same source snapshot should produce identical packet hashes.

Record:

- source repo commit
- source URLs
- packet JSON
- packet hash
- packet build script hash

Pass condition:

```text
same inputs -> same packet hash
```

### Test 2: Prompt/Profile Determinism

Record:

- model artifact hash
- tokenizer hash
- quantization/profile
- SGLang version/container
- launch flags
- prompt hash
- parser hash
- schema hash
- packet hash

Pass condition:

```text
same packet + same prompt/profile -> same parsed output hash
```

### Test 3: Same-Profile Replay

Run each packet five times on H200.

Pass condition:

```text
each packet has one stable parsed-output hash across all five repeats
```

Record both:

- raw output hash
- parsed output hash

The parsed output hash is the main replay artifact. Raw output hash drift is allowed only if parsed output is identical and the cause is documented as formatting-only.

### Test 4: Source-Grounding Check

Every factual claim in the required fields must cite a packet `source_id`.

Fail if:

- cited source does not exist
- output relies on an uncited factual claim
- output invents mainnet status
- output asserts author provenance not present in the packet

### Test 5: Authority-Boundary Check

Fail if output says or implies:

- validators should vote yes/no
- the amendment should be adopted
- the model decision is authoritative
- the output is governance legitimacy

Acceptable:

- "open a research packet"
- "needs security review"
- "missing evidence"
- "public discussion needed"
- "close as superseded"

### Test 6: Fork Test

Pick at least three packets and create explicit forks:

1. Remove implementation source.
2. Add contrary discussion/source.
3. Add missing mainnet-status source.

Pass condition:

- forked packet hash changes
- output hash changes or explicitly remains stable with explanation
- fork point is visible in the output

Claim:

> The process is forkable because packet differences are public and hash-bound.

### Test 7: Cross-Hardware Check

Optional but valuable.

Run a five-packet subset across:

- H200
- H100, if available

Pass condition:

- exact parsed-output hash match across hardware
- raw-output hash match only if achieved

Claim only what the data supports. If this is same-vendor Hopper only, call it same-profile or adjacent CUDA replay, not universal cross-hardware determinism.

## 7. Non-Final Amendment Corpus

Initial unresolved amendment corpus from the provenance packet:

```text
XLS-0008  Tickets                                  Withdrawn
XLS-0009  Blinded Tags                            Stagnant
XLS-0023  Lite Accounts                           Stagnant
XLS-0035  URITokens                               Draft
XLS-0049  Multiple Signer Lists                   Draft
XLS-0051  NFToken Escrows                         Stagnant
XLS-0054  NFTokenOffer Destination Tag            Stagnant
XLS-0060  Default AutoBridge                      Stagnant
XLS-0061  CrossCurrency NFTokenAcceptOffer        Stagnant
XLS-0062  Options                                 Stagnant
XLS-0064  Pseudo-Account                          Draft
XLS-0065  Single Asset Tokenized Vault            Draft
XLS-0066  Lending Protocol                        Draft
XLS-0067  Charge                                  Stagnant
XLS-0068  Sponsored Fees and Reserves             Draft
XLS-0071  Initial Owner Reserve Exemption         Stagnant
XLS-0073  AMMClawback                             Draft
XLS-0076  Min Incoming Amount                     Deprecated
XLS-0078  Subscriptions                           Draft
XLS-0082  MPT Integration into DEX                Draft
XLS-0086  Firewall                                Draft
XLS-0087  Token Pre-Authorization                 Stagnant
XLS-0094  Dynamic Multi-Purpose Tokens            Draft
XLS-0096  Confidential Transfers for MPT          Draft
XLS-0100  Smart Escrows                           Draft
XLS-0101  XRPL Smart Contracts                    Draft
XLS-0102  WASM VM                                 Draft
```

## 8. Article Structure

### 1. The Vote Is Visible

XRPL amendment votes are observable downstream.

Do not attack the vote as fake. The point is narrower:

> A visible vote can still be downstream of an opaque menu.

### 2. The Whence Is Not

Introduce origination:

> Governance begins before voting, when an amendment-shaped object enters the menu.

### 3. The Status Quo Menu

Use EP-1.

Main claims:

- amendment origination is concentrated
- concentration is source-backed, not asserted
- non-Ripple does not mean random outsider; most non-Ripple authors are still identifiable XRP/XRPL ecosystem authors

### 4. Why This Is Non-Ideal

Not:

> Ripple bad.

Instead:

> The public sees the vote more clearly than the upstream formation process.

Issues:

- agenda formation is hard to inspect
- failed/stagnant items are hard to compare
- omissions are not first-class artifacts
- forks are social rather than packetized

### 5. Origination Replay

Define the alternative process:

> public packet -> deterministic function -> typed work item -> omission log -> public receipt -> forkable output

### 6. Demonstration

Use EP-3.

Report:

- corpus size
- model/profile
- packet hashes
- schema validity
- parsed-output hash convergence
- authority-boundary failures, if any
- examples of useful work items
- examples of missing evidence
- fork test examples

### 7. Boundaries

State explicitly:

- the model does not decide what is good
- the model does not replace validators
- the output is not a vote recommendation
- packet construction can bias outputs
- objective frames are forkable and contestable
- decision quality is separate from replay fidelity

### 8. Conclusion

Close with:

> The answer to opaque off-chain governance is not pretending governance can be brought entirely on-chain. The practical intervention is to make the off-chain origination layer public enough to replay, audit, and fork.

## 9. Publication Claims Allowed

Allowed if the tests pass:

> We built a frozen provenance packet over the XRPL Standards corpus.

> We found that 31/46 amendment proposals were direct Ripple-authored, and 44/46 had strict source-backed XRP/XRPL author provenance.

> We ran a deterministic origination-replay harness over 27 unresolved amendment proposals.

> The harness produced schema-valid, source-cited, non-authoritative public work items.

> Each output is bound to packet, prompt, parser, model/profile, and output hashes.

> The packet can be forked and rerun, making agenda formation more inspectable.

## 10. Claims Forbidden

Do not claim:

- LLMs should govern XRPL.
- The model knows which amendments should pass.
- Replay proves decision quality.
- Determinism proves correctness.
- Final means enabled.
- Ripple authored all governance.
- Non-Ripple proposals are fake or bad.
- Cross-hardware determinism unless actually shown by hash.

## 11. Immediate Build To-Do

1. Build EP-2 outcome/status reconciliation.
2. Build packet schema for origination replay.
3. Generate 27 non-final amendment packets.
4. Add authority-boundary validator.
5. Add source-grounding validator.
6. Run H200 same-profile replay, five repeats per packet.
7. Produce `summary.json`, `outputs.jsonl`, `SHA256SUMS.txt`, and human-readable `REPORT.md`.
8. Run fork test on three packets.
9. Optionally run H100/H200 five-packet cross-hardware check.
10. Draft article only after the deterministic packet passes.
