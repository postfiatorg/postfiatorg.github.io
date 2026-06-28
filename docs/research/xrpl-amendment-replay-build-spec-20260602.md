# XRPL Amendment Replay Build Spec

Generated: 2026-06-02

## Objective

Build a replay benchmark that can support meaningful statements about model
behavior on XRPL amendment governance. The benchmark must run 60+ source-backed
amendment/event rows through a pinned Qwen/SGLang profile on H200, while keeping
four different targets separate:

1. terminal XRP-native outcome replay;
2. point-in-time amendment vote-state replay;
3. source-code default-vote replay;
4. conservative governance-triage replay.

The output is a reproducible benchmark packet, not a blog edit.

## Non-Negotiable Boundaries

- Do not compare `HOLD_FOR_CHALLENGE` to XRP validator history. It is a triage
  policy label, not an XRPL vote.
- Do not treat source-code default vote as historical validator outcome.
- Do not treat "not enabled today" as terminal historical `NO`.
- Do not use stale Known Amendments status without cross-checking live ledger or
  vote-state data.
- Every row must declare which metrics it is eligible for.
- Every model prompt must exclude the label for the metric being scored.
- All source facts and state labels must be backed by archived receipts.

## Build Target

Create a new benchmark artifact:

```text
static/benchmarks/xrpl-amendment-lifecycle-replay-YYYYMMDDTHHMMSSZ/
  README.md
  COMMANDS.txt
  SHA256SUMS.txt
  corpus/
    amendment_universe.json
    amendment_universe.csv
    lifecycle_events.csv
    lifecycle_events.json
    corpus_selection.csv
    source_receipts.json
    state_receipts.json
  packets/
    vote_outcome/
      <packet_id>.json
    vote_state/
      <packet_id>.json
    default_vote/
      <packet_id>.json
    triage/
      <packet_id>.json
  labels/
    vote_outcome_labels.json
    vote_state_labels.json
    default_vote_labels.json
    triage_labels.json
  baseline/
    deterministic_baseline.json
    deterministic_baseline.csv
  qwen_runs/
    <lane>/<packet_id>/run_001.json
    <lane>/<packet_id>/run_002.json
    <lane>/<packet_id>/run_003.json
    <lane>/<packet_id>/commit_reveal_001.json
    ...
  summaries/
    vote_outcome_summary.json
    vote_state_summary.json
    default_vote_summary.json
    triage_summary.json
    combined_summary.json
  reports/
    REPORT.md
    vote_outcome_report.md
    vote_state_report.md
    default_vote_report.md
    triage_report.md
  vast_lifecycle/
    selected-offer.json
    create-instance-raw.json
    instances-ready.json
    machine_receipt.json
    sglang-models.json
    sglang-models-ready.json
    sglang-server-info.json
    sglang-smoke-chat.json
    sglang-log-tail-ready.txt
    sglang-log-tail-post-run.txt
    shutdown/
      destroy-instance-raw.json
      instances-after-destroy.json
```

The `shutdown/` artifacts are written only after the done condition in the H200
lifecycle section is met and the operator has accepted the run or explicitly
directed shutdown. They are not expected while the replay is still being built,
run, inspected, or corrected.

## Source Ingestion

Build `scripts/build_xrpl_amendment_lifecycle_corpus.py`.

Inputs:

- XRPSCAN amendments API:
  `https://api.xrpscan.com/api/v1/amendments`
- validated ledger `Amendments` object from a public XRPL server:
  `ledger_entry` for index
  `7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4`
- XRPL Known Amendments page and page-data JSON;
- XRPL release notes for introduced versions;
- XRPL vulnerability disclosures and AMM status posts;
- `XRPLF/rippled` source for amendment definitions/default votes where needed;
- optional public vote history sources for majority-start/loss events.

Required source receipt fields:

```json
{
  "source_id": "...",
  "url": "...",
  "source_type": "official_docs | official_blog | xrpl_rpc | xrpscan_api | github | news",
  "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ",
  "status_code": 200,
  "content_type": "...",
  "sha256": "...",
  "bytes": 0,
  "summary": "..."
}
```

## Amendment Universe

The universe row schema:

```json
{
  "amendment_id": "...",
  "name": "...",
  "introduced_version": "2.5.0",
  "introduced_release_date": "2025-06-24",
  "source_default_vote": "YES | NO | UNKNOWN",
  "current_enabled": true,
  "current_enabled_on": "2026-02-18T10:58:10Z",
  "current_enabled_in_ledger": 102328065,
  "current_support_count": 28,
  "current_validation_count": 34,
  "current_threshold": 27,
  "current_majority": "ACTIVE | NONE | UNKNOWN",
  "current_supported_by_code": true,
  "known_status_source": "xrpscan_api | ledger | known_amendments | source_code",
  "source_ids": ["..."]
}
```

Validation:

- if `current_enabled=true`, amendment ID must appear in validated ledger
  `Amendments`;
- if an amendment ID appears in validated ledger `Amendments`, its terminal
  outcome is `YES`;
- if `current_enabled=false`, it is not automatically terminal `NO`;
- if `source_default_vote=NO`, it is not automatically terminal `NO`;
- if Known Amendments status disagrees with validated ledger state, ledger state
  wins for enabled/not-enabled.

## Lifecycle Events

Rows are amendment lifecycle events, not just amendment names. This is how 60+
examples are obtained without inventing facts.

Event types:

- `introduced_open_for_voting`
- `enabled`
- `majority_active`
- `majority_lost`
- `vetoed_or_retired`
- `validator_no_advisory`
- `post_launch_bug`
- `follow_up_fix`
- `vote_reversal_or_support_withdrawal`

Lifecycle row schema:

```json
{
  "event_id": "...",
  "amendment_id": "...",
  "amendment_name": "...",
  "event_type": "...",
  "event_time": "YYYY-MM-DDTHH:MM:SSZ",
  "decision_surface": "...",
  "terminal_outcome": "YES | NO | NONE",
  "vote_state_label": "ENABLED | NO_MAJORITY | MAJORITY_ACTIVE | MAJORITY_LOST | VETOED | UNKNOWN",
  "source_default_vote": "YES | NO | UNKNOWN",
  "triage_policy_label": "PROCEED | HOLD_FOR_CHALLENGE | DELAY_FOR_FIX | REJECT | NONE",
  "eligible_metrics": [
    "vote_outcome",
    "vote_state",
    "default_vote",
    "triage"
  ],
  "label_basis": "...",
  "source_fact_ids": ["F1", "F2"],
  "held_out_fields": ["terminal_outcome", "vote_state_label"]
}
```

Minimum corpus composition:

- at least 60 lifecycle rows total;
- at least 40 terminal `YES` enabled rows;
- at least 5 terminal or advisory `NO` rows, if source-backed;
- at least 10 current vote-state rows that are not terminal outcomes;
- at least 10 governance-sensitive triage rows;
- include all seed-13 rows, corrected by lifecycle state.

If there are fewer than 5 source-backed terminal/advisory `NO` rows, do not
force balance. Report the class imbalance.

## Packet Lanes

### Lane 1: Vote Outcome

Purpose: historical XRP-native `YES/NO` outcome replay.

Allowed labels:

- `YES`: amendment enabled on mainnet, or specific decision surface resulted in
  support/activation;
- `NO`: source-backed veto, retired/obsolete without enablement, validator
  no-vote advisory, or observed support withdrawal for a named decision surface.

Prompt output schema:

```json
{
  "xrpl_vote_recommendation": "YES | NO",
  "vote_confidence": 0.0,
  "decision_summary": "...",
  "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
  "arguments_for_yes": ["..."],
  "arguments_for_no": ["..."],
  "missing_evidence": ["..."],
  "forbidden_stronger_claim": "..."
}
```

Scored metric:

- `historical_vote_alignment_rate`

### Lane 2: Vote State

Purpose: dated amendment state replay.

Allowed labels:

- `ENABLED`
- `NO_MAJORITY`
- `MAJORITY_ACTIVE`
- `MAJORITY_LOST`
- `VETOED_OR_RETIRED`
- `UNKNOWN`

Prompt output schema:

```json
{
  "vote_state": "ENABLED | NO_MAJORITY | MAJORITY_ACTIVE | MAJORITY_LOST | VETOED_OR_RETIRED | UNKNOWN",
  "state_confidence": 0.0,
  "decision_summary": "...",
  "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
  "missing_evidence": ["..."]
}
```

Scored metrics:

- `vote_state_accuracy`
- `enabled_vs_not_enabled_accuracy`
- `majority_state_accuracy`

### Lane 3: Default Vote

Purpose: source-code default-vote replay.

Allowed labels:

- `YES`
- `NO`
- `UNKNOWN`

Scored metric:

- `source_default_vote_match_rate`

This metric must never be described as validator history.

### Lane 4: Governance Triage

Purpose: conservative policy/work-item replay.

Allowed labels:

- `PROCEED`
- `HOLD_FOR_CHALLENGE`
- `DELAY_FOR_FIX`
- `REJECT`

Prompt output schema:

```json
{
  "route": "PROCEED | HOLD_FOR_CHALLENGE | DELAY_FOR_FIX | REJECT",
  "route_confidence": 0.0,
  "decision_summary": "...",
  "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
  "arguments_for_proceeding": ["..."],
  "arguments_for_delay_or_challenge": ["..."],
  "missing_evidence": ["..."],
  "validator_work_item": {
    "title": "...",
    "recommended_validator_action": "...",
    "review_questions": ["..."],
    "override_questions": ["..."]
  },
  "estimated_review_minutes": {
    "validator_skim": 0,
    "deep_review": 0,
    "packet_verification": 0
  },
  "forbidden_stronger_claim": "..."
}
```

Scored metrics:

- `triage_policy_alignment_rate`
- `unsafe_proceed_count`
- `unnecessary_hold_count`
- `qwen_vs_rule_disagreement_count`
- `work_item_schema_valid_rate`

## Corpus Validator

Build `scripts/validate_xrpl_amendment_lifecycle_corpus.py`.

Hard failures:

- packet prompt contains held-out scored label;
- vote-outcome packet contains `HOLD_FOR_CHALLENGE`;
- default vote used as terminal outcome without independent basis;
- Known Amendments status contradicts validated ledger and ledger was ignored;
- enabled amendment absent from terminal `YES` label;
- non-enabled amendment labeled terminal `NO` only because it is below threshold;
- source URL/title leak contains the held-out answer where the prompt is meant
  to be blind;
- fewer than 60 lifecycle rows;
- missing source receipt hash;
- H200 runtime manifest missing machine receipt.

## Deterministic Baseline

Build `scripts/run_xrpl_amendment_lifecycle_baseline.py`.

Baseline rules:

```text
official no-vote advisory -> NO / REJECT
enabled on validated ledger -> YES / PROCEED_OR_REVIEWED
vetoed_or_retired -> NO / REJECT
post-launch bug with unfixed state -> NO / DELAY_FOR_FIX
follow-up fix with clear official fix basis -> YES / PROCEED
new financial primitive + no terminal outcome -> NO_MAJORITY or HOLD_FOR_CHALLENGE
asset-control/compliance primitive + no terminal outcome -> HOLD_FOR_CHALLENGE
insufficient evidence -> UNKNOWN or HOLD_FOR_CHALLENGE
```

The rule output must include triggered rules and cited fact IDs.

## H200 / SGLang Spec

Build `scripts/run_h200_xrpl_amendment_lifecycle_replay.py` or a Make target
that wraps the existing Vast workflow.

Vast selection:

- GPU: single H200;
- GPU RAM: approximately 143 GB;
- one GPU only, tensor parallelism 1;
- reliability > 0.98;
- verified/rentable;
- driver compatible with CUDA 13 image, prefer 570+ and avoid known-bad offers;
- label:
  `postfiat-xrpl-amendment-lifecycle-h200-<timestamp>`.

SGLang launch:

```bash
python3 -m sglang.launch_server \
  --model-path Qwen/Qwen3.6-27B-FP8 \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  --tp 1 \
  --context-length 32768 \
  --mem-fraction-static 0.75 \
  --enable-deterministic-inference \
  --max-running-requests 1 \
  --chunked-prefill-size 4096 \
  --attention-backend fa3 \
  --reasoning-parser qwen3
```

Generation settings:

```json
{
  "temperature": 0,
  "top_p": 1,
  "response_format": {"type": "json_object"},
  "chat_template_kwargs": {"enable_thinking": false},
  "separate_reasoning": false,
  "max_tokens": 1800
}
```

Machine receipt fields:

```json
{
  "provider": "vastai",
  "provider_run_id": 0,
  "offer_id": 0,
  "machine_id": 0,
  "host_id": 0,
  "gpu_name": "H200",
  "gpu_ram": 0,
  "driver_version": "...",
  "image_uuid": "lmsysorg/sglang:nightly-dev-cu13-20260523-c112f762",
  "model_id": "Qwen/Qwen3.6-27B-FP8",
  "endpoint_url": "...",
  "log_url": "...",
  "deterministic_inference": true,
  "max_running_requests": 1,
  "context_length": 32768,
  "chunked_prefill_size": 4096,
  "attention_backend": "fa3",
  "reasoning_parser": "qwen3",
  "temperature": 0,
  "top_p": 1,
  "models_response": {},
  "server_info": {},
  "smoke_chat": {},
  "lifecycle_artifact_sha256": {},
  "retain_until_done": true,
  "shutdown_condition": "corpus built; corpus validator passed; baseline generated; selected H200 replay lanes completed without fallback; summaries generated; disagreements inspected; checksums verified; operator accepted run or explicitly directed shutdown"
}
```

Lifecycle requirements:

- create output must be sanitized to remove `instance_api_key`;
- capture `/v1/models`;
- capture server info;
- run smoke chat;
- run all lanes;
- capture final log tail;
- keep the H200 running until the run is thoroughly done, where "done" means:
  corpus built, corpus validator passed, baseline generated, all selected H200
  replay lanes completed without fallback, summaries generated, disagreements
  inspected, checksums verified, and the operator has either accepted the run or
  explicitly directed shutdown;
- do not destroy the H200 merely because one intermediate run completed;
- only after the done condition is met, destroy the H200, verify the created
  instance ID is absent from `vastai show instances`, and write
  `instances-after-destroy.json`.

## Qwen Runner

Build `scripts/run_qwen_xrpl_amendment_lifecycle_replay.py`.

Arguments:

```bash
--packet-root <artifact>
--lane vote_outcome|vote_state|default_vote|triage|all
--endpoint <openai-compatible-url>
--model Qwen/Qwen3.6-27B-FP8
--machine-receipt <path>
--runs 3
--validators 41
--fail-on-error
```

Runner behavior:

- prompts are built per lane;
- each packet gets 3 independent calls;
- every run writes raw response shape, parsed output, schema validity,
  packet hash, prompt hash, model profile hash, output hash;
- commit/reveal is generated for 41 simulated validators per run;
- no offline fallback when `--fail-on-error` is set;
- a runtime manifest is written per lane.

## Summarizers

Build `scripts/summarize_xrpl_amendment_lifecycle_replay.py`.

It must emit separate lane summaries plus combined report.

Required metrics:

```json
{
  "packet_count": 0,
  "total_qwen_runs": 0,
  "schema_valid_output_rate": 0.0,
  "endpoint_error_count": 0,
  "fallback_used": false,
  "exact_output_hash_converged_packets": 0,
  "parsed_label_converged_packets": 0,
  "historical_vote_alignment_rate": 0.0,
  "vote_state_accuracy": 0.0,
  "source_default_vote_match_rate": 0.0,
  "triage_policy_alignment_rate": 0.0,
  "unsafe_proceed_count": 0,
  "qwen_vs_rule_disagreement_count": 0,
  "label_basis_counts": {},
  "class_distribution": {},
  "runtime_manifest": {}
}
```

Combined report must include:

- lane counts;
- class balance;
- all disagreements;
- all unsafe proceeds;
- all cases where Qwen and deterministic baseline differ;
- all cases where a row is excluded from a metric;
- H200 receipt hash;
- root checksum hash.

## 60+ Event Construction

The first pass should not hand-select 60. It should build all lifecycle rows it
can source, then filter/report.

Initial construction:

1. Pull every XRPSCAN amendment row.
2. Cross-check enabled IDs against validated ledger `Amendments`.
3. Join release notes by introduced version.
4. Join source default vote from Known Amendments/source definitions.
5. Add official vulnerability/advisory event rows.
6. Add AMM vote reversal and post-launch bug/fix event rows.
7. Score governance sensitivity.
8. Select:
   - all terminal `NO`/advisory rows;
   - all post-launch bug/fix rows;
   - all governance-sensitive enabled rows;
   - enough routine enabled rows to exceed 60 and provide denominator stability.

Expected first corpus:

- approximately 90+ enabled amendment outcome rows;
- 2 current non-enabled lending/vault rows;
- several obsolete/veto/advisory rows;
- AMM incident/fix rows;
- seed-13 corrected rows.

If the enabled row count is high, report both:

- full corpus metrics;
- governance-sensitive subset metrics.

## Meaningful Statements Enabled

Allowed after this build:

- "On N terminal amendment outcome rows, the model matched XRP-native terminal
  YES/NO outcomes at rate X."
- "On N current vote-state rows, the model identified enabled vs not-enabled
  state at rate X."
- "On N default-vote rows, the model matched source-code default vote at rate X."
- "On N triage-policy rows, the model matched the conservative policy label at
  rate X and produced Y unsafe proceeds."
- "Across N packets, exact output hash convergence was X/Y under the captured
  H200/SGLang profile."

Forbidden:

- "HOLD matched validator history."
- "Default No means historical No."
- "Not enabled by June 2026 means rejected."
- "Qwen governed correctly."
- "60+ repeated runs are 60+ independent events" if they are repeats over the
  same packet.

## Acceptance Gates

The benchmark is usable only if:

- corpus has at least 60 source-backed lifecycle rows;
- every row has source receipts;
- corpus validator passes with zero hard failures;
- H200 receipt is present and sanitized;
- schema-valid rate is at least 0.98;
- parsed-label convergence is at least 0.95 per lane;
- exact output-hash convergence is reported, not assumed;
- unsafe proceed count is zero for known-bug/advisory/fix-required rows;
- all disagreements are listed;
- H200 created for the run is destroyed and verified absent;
- `sha256sum -c SHA256SUMS.txt` passes.

## Build Order

1. `build_xrpl_amendment_lifecycle_corpus.py`
2. `validate_xrpl_amendment_lifecycle_corpus.py`
3. `run_xrpl_amendment_lifecycle_baseline.py`
4. `build_xrpl_amendment_lifecycle_packets.py`
5. `run_h200_xrpl_amendment_lifecycle_replay.py`
6. `run_qwen_xrpl_amendment_lifecycle_replay.py`
7. `summarize_xrpl_amendment_lifecycle_replay.py`
8. checksum and H200 shutdown verification

This is the missing implementation spec. The next engineering task is to build
steps 1-4 locally, validate the 60+ corpus without GPU time, then rent H200 only
for the final replay pass.
