# XRPL Amendment Replay Corpus Research Spec

## Purpose

Build the source-of-truth research package and public post for the question:

> If XRPL-style validators had a default setting `vote_replay_hash=1`, and that default caused them to run a pinned Qwen/SGLang governance packet before each amendment vote, what would the replay-default vote have recommended on real historical XRP Ledger amendment events?

This research does not try to prove that a model is wiser than human validators. It tests a narrower governance primitive:

> A public, replayable model process can convert raw amendment evidence into typed, cited work items, allowing validators to follow, verify, or explicitly override a default route without forming a standing private committee.

## Final Deliverable

The final deliverable is a public Post Fiat blog post:

```text
content/posts/llm-governance-replay.md
```

Title:

```text
LLM Governance Replay
```

This post is the source of truth for the public narrative. The benchmark packet,
research scripts, source receipts, and Qwen/SGLang run artifacts exist to support
and reproduce the post. If there is a conflict between a draft whitepaper section
and this post after publication, this post controls the public description of
the experiment.

The post must be written for a serious technical audience but should be readable
and enjoyable. It should explain:

- why standing human governance committees are expensive;
- why they create centralization, liability, and collusion surfaces;
- how deterministic Qwen/SGLang replay changes the governance primitive;
- how Vast H100/H200 GPU endpoints are provisioned and pinned for replay;
- how reproduction scripts rerun the packets;
- which 13 XRPL amendment events were selected and why;
- what happened historically in each event;
- how the deterministic baseline voted;
- how `vote_replay_hash=1` would have voted;
- where replay-default governance converged with or diverged from XRPL history;
- what the experiment proves and what it does not prove.

The final post must link to the benchmark packet and expose enough commands that
an external reviewer can reproduce the main tables.

## Core Hypothesis

A replay-default governance lane reduces private coordination and validator attention cost while preserving human override.

The benchmark should measure whether pinned Qwen triage:

- reaches a historically sane route on real XRPL amendment packets;
- avoids unsafe proceed recommendations on known-bug or high-uncertainty packets;
- produces useful cited work items beyond a deterministic alert;
- converges across repeated deterministic runs;
- lowers estimated all-validator review time;
- makes manual overrides explicit rather than hidden in private committee deliberation.

## Protocol Idea Under Test

Validators have two voting lanes.

### Manual lane

The validator operator explicitly votes `YES`, `NO`, `ABSTAIN`, or `HOLD`, with an optional reason.

### Replay-default lane

If the validator config contains:

```toml
[governance]
vote_replay_hash = true
model_profile = "qwen3.6-27b-fp8-sglang-v1"
manual_override = false
```

then the validator runs the published amendment packet through the pinned model profile and maps the parsed route to a default vote.

Example signed output:

```json
{
  "validator": "<validator public key>",
  "amendment_packet_hash": "<sha256>",
  "model_profile_hash": "<sha256>",
  "output_hash": "<sha256>",
  "route": "DELAY_FOR_FIX",
  "vote": "NO",
  "mode": "replay_default",
  "signature": "<validator signature>"
}
```

Manual override example:

```json
{
  "validator": "<validator public key>",
  "amendment_packet_hash": "<sha256>",
  "vote": "YES",
  "mode": "manual_override",
  "override_reason": "Operator reviewed the issue and believes the defect is non-critical.",
  "signature": "<validator signature>"
}
```

The resulting governance dashboard shows both:

- raw votes; and
- replay-default votes, split from manual overrides.

This makes a governance decision legible:

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

That split matters. It distinguishes reproducible process agreement from humans actively overriding the process.

## Research Question

For the last 13 controversial XRPL amendment events:

1. What route would pinned Qwen/SGLang recommend?
2. Would the replay-default route align with the eventual safe historical outcome?
3. Would the route have delayed, challenged, or rejected risky amendments before known defects surfaced?
4. How often would validators have needed manual override?
5. How many validator-hours are avoided versus standing committee review?
6. Does Qwen add useful typed structure beyond a deterministic rule alert?

## Corpus Selection

Do not hand-pick the 13 cases. Build the set by rule.

### Source universe

Start from the full public XRPL amendment universe, including:

- XRPL Known Amendments page;
- amendment objects or amendment IDs from XRPL public APIs where available;
- XRPL blog posts and release notes;
- `XRPLF/rippled` feature definitions and amendment PRs;
- public validator vote history where available;
- credible external reporting for vote reversals, bug-triggered delays, or public controversy.

### Controversy score

Each amendment candidate receives a controversy score. Select the 13 highest-scoring amendments among the most recent candidates, with recency as the tie-breaker.

Suggested scoring:

| Signal | Points |
|---|---:|
| Public vote reversal, delayed activation, or support below threshold after prior support | 5 |
| Known bug before activation or immediately after activation | 5 |
| Requires a follow-up fix amendment after launch | 4 |
| Changes asset control, issuer power, compliance, freeze, clawback, or custody semantics | 4 |
| Introduces a new financial primitive: AMM, lending, MPT, token escrow, permissioned DEX, vault | 3 |
| Obsolete, vetoed, disabled, or default-no status | 3 |
| Material validator/operator debate in public channels | 3 |
| Security/liveness/consensus-safety implication | 3 |
| User-fund, pool, reserve, or accounting risk | 3 |
| Routine cleanup with no observed controversy | 0 |

### Candidate classes to verify

These are not preselected results. They are likely search targets:

- XLS-30 AMM activation and the February 2024 vote reversal;
- AMM post-launch pool discrepancy and follow-up fix amendments;
- AMMClawback;
- Clawback;
- MPTokensV1;
- PermissionedDEX;
- PermissionedDomains;
- TokenEscrow;
- Batch;
- PermissionDelegation;
- LendingProtocol;
- SingleAssetVault;
- DID;
- NFT amendment/fix families where trustline, reserve, or freeze semantics changed;
- disallow-incoming or deposit-auth fix families;
- cleanup amendments that blocked or forced upgrades.

Final inclusion must be determined by the controversy score and documented in `corpus_selection.csv`.

## Amendment Packet Schema

Each packet is a frozen JSON document:

```json
{
  "packet_version": 1,
  "amendment_name": "AMM",
  "amendment_id": "<id if known>",
  "event_window": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  },
  "event_type": "activation | delay | revote | fix | controversy | obsolete",
  "short_description": "...",
  "technical_change": "...",
  "risk_class": [
    "new_financial_primitive",
    "known_bug",
    "asset_control",
    "consensus_safety"
  ],
  "historical_facts": [
    {
      "fact_id": "F1",
      "claim": "...",
      "source_id": "S1",
      "quote_or_summary": "...",
      "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ],
  "sources": [
    {
      "source_id": "S1",
      "url": "...",
      "source_type": "official_docs | official_blog | github | vote_tracker | news | forum",
      "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ",
      "sha256": "<retrieved body hash>",
      "status_code": 200
    }
  ],
  "vote_context": {
    "threshold": "80_percent_for_two_weeks",
    "known_support_percent": 71.43,
    "support_source_id": "S2"
  },
  "historical_outcome": {
    "route": "PROCEED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT | OBSOLETE",
    "outcome_summary": "...",
    "outcome_source_id": "S3"
  },
  "safe_route_label": {
    "label": "PROCEED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT",
    "label_basis": "historical_outcome | later_bug | explicit_validator_reversal | source_consensus",
    "labeler": "researcher",
    "notes": "..."
  }
}
```

## Qwen Triage Output Schema

Pinned Qwen/SGLang must output strict JSON:

```json
{
  "route": "PROCEED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT",
  "route_confidence": 0,
  "vote_default": "YES | NO | ABSTAIN | HOLD",
  "decision_summary": "...",
  "cited_facts": [
    {
      "fact_id": "F1",
      "why_it_matters": "..."
    }
  ],
  "arguments_for_proceeding": ["..."],
  "arguments_for_delay_or_challenge": ["..."],
  "missing_evidence": ["..."],
  "validator_work_item": {
    "title": "...",
    "recommended_validator_action": "...",
    "review_questions": ["..."],
    "override_questions": ["..."]
  },
  "private_standing_committee_required": false,
  "estimated_review_minutes": {
    "validator_skim": 0,
    "deep_review": 0,
    "packet_verification": 0
  },
  "forbidden_stronger_claim": "..."
}
```

## Vote Mapping

Use a conservative mapping:

| Qwen route | Replay-default vote |
|---|---|
| `PROCEED` | `YES` |
| `DELAY_FOR_FIX` | `NO` |
| `HOLD_FOR_CHALLENGE` | `ABSTAIN` or `HOLD` |
| `REJECT` | `NO` |

For safety analysis, `PROCEED` on a packet later labeled `DELAY_FOR_FIX`, `HOLD_FOR_CHALLENGE`, or `REJECT` is an unsafe proceed recommendation.

## Runtime Plan

### Production-like runner

Primary runner:

- model: `Qwen/Qwen3.6-27B-FP8`;
- serving: SGLang deterministic inference;
- provider: Vast H100/H200 or equivalent direct GPU provider with a captured
  machine receipt;
- decoding: greedy / temperature 0;
- thinking mode: disabled unless explicitly tested as a separate profile;
- output schema: JSON object;
- runtime manifest includes model repo, image hash, launch args, GPU type,
  driver/CUDA surface, parser version, prompt hash, packet hash, and the
  machine receipt hash.

The benchmark packet must include:

- a sanitized provider machine receipt;
- the SGLang served-model response;
- a final SGLang log tail;
- the replay runtime manifest;
- per-run model profile hashes;
- per-run output hashes;
- commit/reveal files for the simulated validators;
- `SHA256SUMS.txt` binding the packet.

### Simulated validator count

Run at least:

- `N=41` replay-default validators for the main counterfactual;
- repeated runs per packet sufficient to test convergence;
- if compute budget allows, multiple hardware profiles: H100, H200, Apple/MLX or a non-NVIDIA control.

### Commit/reveal simulation

For each simulated validator:

```text
commit = H(packet_hash || model_profile_hash || output_hash || salt)
reveal = {
  packet_hash,
  model_profile_hash,
  output_hash,
  output_json,
  salt,
  parsed_route,
  vote_default
}
```

Measure:

- commit/reveal validity;
- output hash convergence;
- parsed route convergence;
- vote convergence;
- schema validity;
- citation validity.

## Baselines

### Deterministic rule baseline

A simple rule engine should run on the same packet:

```text
known bug + feature launch -> DELAY_FOR_FIX
support below threshold -> HOLD_FOR_CHALLENGE
security fix with clear source -> PROCEED or EXPEDITE
missing source evidence -> HOLD_FOR_CHALLENGE
asset-control/compliance expansion -> HOLD_FOR_CHALLENGE unless low-risk evidence is strong
obsolete/vetoed status -> REJECT or HOLD
```

Output schema:

```json
{
  "route": "...",
  "vote_default": "...",
  "triggered_rules": ["..."],
  "cited_facts": ["F1", "F2"],
  "limitations": ["..."]
}
```

### Standing committee baseline

Cost model only, unless real human labels are collected.

Default assumptions:

- 41 validators;
- 120 minutes per validator for full review;
- $250/hour fully loaded professional time;
- private coordination surfaces: chat/call, agenda control, recurring reviewer roles, discoverable deliberation, validator-to-validator coordination nexus.

### Synthetic judge panel

Optional but useful:

- Use external models blind to which output came from Qwen or deterministic rules.
- Ask them which output is more actionable, source-faithful, historically aligned, and committee-reducing.
- Do not call this human validation.

## Metrics

### Safety and historical alignment

- `historically_aligned_route_rate`
- `unsafe_proceed_count`
- `unnecessary_hold_count`
- `known_bug_delay_capture_rate`
- `post_launch_fix_prediction_rate`
- `route_confidence_calibration`

### Usefulness over deterministic baseline

- Qwen-vs-rule disagreement count;
- Qwen wins / rule wins / ties under synthetic or human adjudication;
- cases where Qwen identifies missing evidence not captured by rules;
- cases where rules outperform Qwen;
- citation validity;
- hallucinated fact count.

### Replay and convergence

- exact output hash convergence;
- parsed route convergence;
- vote convergence;
- schema-valid output rate;
- commit/reveal validity;
- cross-hardware drift if tested.

### Attention compression

Compute:

```text
standing_committee_hours =
  validator_count * full_review_minutes / 60

deterministic_alert_hours =
  validator_count * deterministic_review_minutes / 60

qwen_triage_hours =
  packet_verification_minutes / 60
  + validator_count * skim_minutes / 60
  + deep_reviewers * deep_review_minutes / 60

attention_reduction_vs_committee =
  1 - qwen_triage_hours / standing_committee_hours

attention_reduction_vs_deterministic =
  1 - qwen_triage_hours / deterministic_alert_hours
```

## Pass / Fail Gates

The corpus supports a strong whitepaper claim only if:

- at least 13 packets are source-backed and hash-bound;
- all packet source receipts are retrievable or archived;
- Qwen output schema validity is at least 98%;
- parsed route convergence is at least 95% within the pinned profile;
- unsafe proceed count is zero on known-bug / later-fix packets;
- historically aligned route rate is materially above deterministic baseline, or Qwen produces clear attention/actionability lift without worse safety;
- attention reduction versus standing committee exceeds 70%;
- the report explicitly identifies cases where Qwen loses or ties.

If Qwen only ties deterministic rules on route safety, the claim is still useful only if Qwen materially improves:

- validator work item quality;
- cited rationale;
- missing-evidence identification;
- private committee avoidance;
- review-time compression.

## Source Of Truth And Outputs

The public source of truth is:

```text
content/posts/llm-governance-replay.md
```

The supporting reproducibility packet is:

```text
static/benchmarks/xrpl-amendment-governance-replay-YYYYMMDDTHHMMSSZ/
  README.md
  REPORT.md
  corpus_selection.csv
  amendment_packets/
    <amendment>.json
  source_receipts.json
  deterministic_baseline.json
  qwen_runs/
    <packet_id>/
      run_<n>.json
      commit_reveal_<n>.json
  convergence_summary.json
  vote_replay_hash_counterfactual.csv
  attention_cost_model.json
  judge_panel.json
  summary.json
  COMMANDS.txt
  SHA256SUMS.txt
```

The post must include these sections:

```text
1. The Governance Cost Problem
2. The Committee Collusion Problem
3. Deterministic Qwen/SGLang Replay
4. The `vote_replay_hash=1` Default
5. Corpus Selection: 13 Controversial XRPL Amendments
6. Reproduction Scripts
7. Results: Convergence, Divergence, And Unsafe Proceed Checks
8. Attention Cost Model
9. What This Proves
10. What This Does Not Prove
```

The 13-amendment table in the post must include:

| Column | Meaning |
|---|---|
| `amendment_or_event` | Amendment name or event label |
| `controversy_reason` | Why it entered the corpus |
| `what_happened` | Plain-English historical summary |
| `historical_route` | `PROCEED`, `DELAY_FOR_FIX`, `HOLD_FOR_CHALLENGE`, `REJECT`, or `OBSOLETE` |
| `deterministic_route` | Route from the baseline rule engine |
| `qwen_replay_route` | Route from pinned Qwen/SGLang replay |
| `replay_default_vote` | `YES`, `NO`, `ABSTAIN`, or `HOLD` |
| `converged_with_history` | Boolean |
| `notes` | One sentence on divergence or caveat |

The reproduction section must show commands similar to:

```bash
python3 scripts/build_xrpl_amendment_replay_corpus.py \
  --output static/benchmarks/xrpl-amendment-governance-replay-<timestamp>

python3 scripts/run_qwen_amendment_replay.py \
  --corpus static/benchmarks/xrpl-amendment-governance-replay-<timestamp>/amendment_packets \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-governance-replay-<timestamp>/vast_lifecycle/machine_receipt.json \
  --runs 3 \
  --validators 41

python3 scripts/summarize_xrpl_amendment_replay.py \
  --packet static/benchmarks/xrpl-amendment-governance-replay-<timestamp>

sha256sum -c static/benchmarks/xrpl-amendment-governance-replay-<timestamp>/SHA256SUMS.txt
```

## Blog-Safe Claims

Allowed if results pass:

> In a 13-event replay of controversial XRPL amendment governance, simulated validators running the pinned Qwen/SGLang replay-default process converged on the historically safe route in X/Y packets, produced zero unsafe proceed recommendations in known-bug cases, and reduced estimated validator attention by Z% versus standing committee review under the declared cost model.

Allowed if Qwen ties deterministic route safety but improves work item quality:

> The replay does not show model superiority over deterministic rules on route selection. It does show that model-generated typed work items compress validator attention and make manual override explicit without creating a standing private committee.

Forbidden:

> Qwen proves the correct governance answer.

Forbidden:

> AI replaces validator judgment.

Forbidden:

> Synthetic model judges are human committee validation.

## Implementation Phases

### Phase 1: Corpus build

- Fetch amendment universe.
- Score controversy.
- Select 13 packets.
- Write packet JSON and source receipts.

### Phase 2: Deterministic baseline

- Implement rule baseline.
- Run on all packets.
- Save route/vote outputs.

### Phase 3: Qwen replay

- Run pinned Qwen/SGLang on each packet.
- Save runtime manifests, outputs, parsed routes, and commit/reveal objects.
- Repeat enough times to measure convergence.

### Phase 4: Judgment and cost model

- Run synthetic judge panel or collect human labels.
- Compute attention compression.
- Compare Qwen, deterministic baseline, and historical outcome.

### Phase 5: Report and whitepaper integration

- Publish the static benchmark packet.
- Write `content/posts/llm-governance-replay.md`.
- The blog post is the public source of truth for this experiment.
- Run the site locally and verify the post renders.
- Only after the blog post exists and the benchmark packet validates should any whitepaper section cite it.
