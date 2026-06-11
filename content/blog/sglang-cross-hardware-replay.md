---
title: "Viability of SGLang Replay: Cross-Hardware"
date: 2026-06-03T00:00:00Z
summary: "An evidence note on SGLang replay across H200 and H100 NVL profiles: exact held-out packet replay, explicit prompt-drift quarantine, MLX capability control, machine receipts, comparison hashes, and shutdown receipts."
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - Governance
  - Replay
  - SGLang
  - Qwen
  - Hardware
---

The governance-replay article makes a narrow claim: a pinned Qwen/SGLang profile can produce public, typed, hash-addressed work items over XRPL amendment history. That is useful, but it is not enough.

The narrow next question is whether the replay object survives a second CUDA hardware profile.

> Can the same packet and prompt be replayed through another hardware profile, with enough determinism and enough drift reporting that validators can separate governance disagreement from runtime drift?

This draft records the first cross-hardware evidence packet for that question. In this packet, "cross-hardware" means adjacent same-vendor CUDA profiles: H200 and H100 NVL, both running the same SGLang container, model, and deterministic settings. The separate Apple/MLX GitHub Actions run is only a capability smoke control, not target-model replay evidence.

The result is strong on that narrower CUDA-profile claim:

```text
H200 held-out repeat:
  187 / 187 exact raw-and-parsed output matches
  0 route-label mismatches
  0 source-fact-set mismatches
  0 unsafe-PROCEED deltas

H100 NVL vs H200 held-out:
  187 / 187 exact raw-and-parsed output matches
  0 route-label mismatches
  0 source-fact-set mismatches
  0 unsafe-PROCEED deltas
```

That does not prove universal LLM determinism, independent-architecture portability, or validator independence. It proves a narrower operational fact: under this corpus, this model, this container, these SGLang flags, and these two NVIDIA profiles, the held-out replay object was byte-stable at the raw-output layer and therefore also stable at the parsed governance-object layer.

That distinction is load-bearing. H100 NVL and H200 are not independent governance minds, and they are not a substitute for human validator review. They are an operational replay check: can a second machine profile reproduce the same packet-bound work item exactly?

## The Boundary

"The model" is not a replay specification.

A replay claim has to bind at least:

```text
model weights
quantization format
tokenizer
runtime
container or package version
GPU or accelerator profile
launch flags
determinism flags
prompt hash
packet hash
parser version
raw output hash
parsed output hash
machine receipt
```

Without those fields, a validator cannot tell whether two artifacts differ because the model disagreed, the prompt changed, the packet changed, the parser changed, the runtime drifted, the hardware profile changed, or the operator produced a different work item.

The point of cross-hardware replay is not to pretend all machines are identical or independent. The point is to make differences visible.

## Evidence Packet

The public packet is:

[/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/](/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/)

It contains:

```text
profiles/h200_sglang_repeat_selected/
profiles/h200_sglang_repeat_heldout/
profiles/h100nvl_sglang_heldout/
profiles/mlx_github_actions_smoke/
comparisons/
gpu_shutdown/
README.md
SHA256SUMS.txt
```

The comparison script reports packet hashes, prompt hashes, strict profile/receipt hashes, raw output hashes, parsed output hashes, route labels, cited source facts, schema validity, and unsafe-PROCEED deltas.

The strict profile/receipt hashes are expected to differ across machines and even across fresh receipts. That is not a failure by itself. The comparison first asks whether the packet and prompt are identical. Only then does it interpret output drift.

## Runtime Profiles

Both CUDA runs used:

| Field | Value |
|---|---|
| Runtime | SGLang OpenAI-compatible server |
| Image | `lmsysorg/sglang:nightly-dev-cu13-20260523-c112f762` |
| Model | `Qwen/Qwen3.6-27B-FP8` |
| Determinism | `--enable-deterministic-inference` |
| Max running requests | `1` |
| Context length | `32768` |
| Static memory fraction | `0.75` |
| Attention backend | `fa3` |
| Reasoning parser | `qwen3` |
| Sampling | `temperature=0`, `top_p=1` |

The H200 profile ran on Vast instance `39137704`. The H100 profile ran on Vast instance `39230200`, an H100 NVL with 95,830 MB reported GPU RAM. Public network endpoints and provider secrets are redacted from the public receipts.

The H100 public port mapping did not expose the SGLang API cleanly, so the run used an SSH tunnel to the instance's internal port 8000. That is recorded as transport metadata. It is not a model or prompt difference.

## Scorecard

The clean comparison rows are the held-out rows. The earlier selected artifact had prompt-hash drift relative to the fresh selected rerun, so the selected comparison is quarantined as an invalid-input comparison rather than counted as repeatability evidence.

| Comparison | Rows | Packet mismatches | Prompt mismatches | Exact raw+parsed matches | Route mismatches | Source-fact mismatches | Unsafe-PROCEED deltas | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| H200 selected source vs H200 selected repeat | 271 | 0 | 271 | 0 | 28 | 87 | 0 | Invalid for repeatability; prompt changed. |
| H200 held-out source vs H200 held-out repeat | 187 | 0 | 0 | 187 | 0 | 0 | 0 | Clean same-input H200 repeat. |
| H200 held-out repeat vs H100 NVL held-out | 187 | 0 | 0 | 187 | 0 | 0 | 0 | Clean H200/H100 NVL cross-profile replay. |

The important number is not the combined total, because the selected comparison is intentionally invalid. The useful result is:

```text
clean held-out comparison rows: 374
exact raw-and-parsed matches: 374
governance-relevant route drift: 0
unsafe-PROCEED deltas: 0
```

## What Stayed Stable

The H200 held-out repeat and H100 NVL held-out run produced the same lane summaries:

| Lane | Packets | Schema valid | Exact output convergence | Alignment result |
|---|---:|---:|---:|---|
| `vote_outcome` | 46 | 100% | 46/46 | 44/46 historical vote alignment |
| `vote_state` | 47 | 100% | 47/47 | 47/47 state alignment |
| `default_vote` | 47 | 100% | 47/47 | Diagnostic only, 16/47 source default-vote match |
| `triage` | 47 | 100% | 47/47 | 31/47 policy alignment, 1 unsafe proceed |

The triage weakness did not disappear on H100, and that is the correct outcome for this experiment. Cross-hardware replay should preserve failures, not hide them. The H100 profile reproduced the same held-out triage behavior, including the same one unsafe-PROCEED result already identified as a policy/harness problem in the governance replay work.

That is not decision-quality evidence. Replay fidelity and decision quality are independent: a profile can exactly reproduce a bad route. Perfectly replaying a 31/47 held-out triage lane with one unsafe proceed is not a foundation for autonomous governance; it is evidence that the public work item is stable enough for humans, validators, and competing packet authors to inspect the same object and challenge the same failure.

This matters because the experiment is not asking whether Qwen is perfect. It is asking whether validators can replay the same work item and get the same object back without turning runtime drift into governance disagreement.

## What Did Not Count

The selected-set comparison did not count as repeatability evidence.

The packet hashes matched, but all 271 prompt hashes differed between the older selected source and the fresh selected repeat. Once the prompt hash differs, the comparison is no longer a replay of the same input. The comparison script therefore classifies every selected row as:

```text
invalid_input_mismatch
```

That is the right failure mode. A replay harness should refuse flattering numbers when the prompt changed.

The fresh selected rerun is still useful as a current H200 run summary: 271 packets completed, no endpoint fallback, 100% schema-valid outputs, 70/70 vote-state alignment, 54/60 vote-outcome alignment, and 67/72 triage-policy alignment with zero unsafe proceeds. But it is not evidence that the older selected artifact was exactly reproduced.

## MLX Control

The Apple/MLX control is deliberately modest.

GitHub Actions run `26860227368` completed successfully on `macos-15-xlarge` at commit `06e110f`. The log records an Apple arm64 runner, imports `mlx.core`, installs `mlx==0.31.2` and `mlx-lm==0.31.3`, and runs a small MLX compute smoke test.

That proves the repository can dispatch and capture a public MLX execution receipt through GitHub Actions. It does not prove that `Qwen/Qwen3.6-27B-FP8` replayed under MLX, and it does not prove byte-equivalence between MLX and SGLang. A real MLX replay packet should be its own profile, with its own model artifact, prompt hashes, parsed-output hashes, and drift table.

The MLX control belongs in this packet because it establishes the non-NVIDIA evidence path. It should not be oversold.

## V2 Follow-Up

A second evidence packet records the completed follow-up expansion:

[/benchmarks/sglang-cross-hardware-replay-v2-20260603T131318Z/](/benchmarks/sglang-cross-hardware-replay-v2-20260603T131318Z/)

It closes the missing table from the first packet without changing the claim boundary.

CUDA result:

```text
H100 NVL selected same-profile repeat: 271/271 exact raw-and-parsed matches
H100 NVL held-out same-profile repeat: 187/187 exact raw-and-parsed matches
H100 NVL vs H100 SXM held-out replay: 187/187 exact raw-and-parsed matches
combined_rows: 645
route_label_mismatches: 0
schema_invalid_rows: 0
unsafe_proceed_deltas: 0
active_target_instance_count_after_destroy: 0
```

MLX subset control:

```text
model: mlx-community/Qwen3-0.6B-4bit
runner: macos-15-xlarge
run: 26887497536
packet_count: 4
run_count: 8
schema_valid_count: 8
same_packet_repeat_raw_matches: 4
same_packet_repeat_parsed_matches: 4
label_matches: 4
```

The CUDA row is the stronger result: same model, same SGLang profile, same packets, exact outputs across same-profile repeats and a second CUDA host. The MLX row is a narrower control: it proves the repository can dispatch and capture a real Apple/MLX Qwen-family replay, not that MLX is byte-equivalent to the 27B FP8 SGLang profile.

## Why This Matters For Governance Replay

The governance article's strongest infrastructure claim is replay-addressability:

```text
packet hash
prompt hash
model/runtime profile hash
machine receipt
raw output hash
parsed output hash
public comparison row
```

Cross-hardware replay tests whether that object is a one-machine anecdote or an auditable artifact that survives another machine profile.

On the clean held-out packet set, the answer was favorable. H200 repeat and H100 NVL replay were exact at the raw-output layer. That means the parsed governance object, route label, cited source facts, and unsafe-proceed flag were also exact.

This strengthens the governance article in one specific way: validators do not have to treat the H200 result as a private runtime anecdote. For the held-out packet set, another NVIDIA CUDA profile under the same SGLang image and deterministic settings reproduced the exact same outputs.

It does not solve independence by itself. If every validator blindly accepts one replay hash, the social process can still collapse into common-mode reliance. The benefit here is different: the replay object is inspectable, reproducible across at least one adjacent CUDA hardware profile, and strict enough to reject changed prompts.

## Failure Rules

The safety rule is:

> Runtime drift is not governance disagreement.

A useful replay packet must classify failures instead of smoothing them over:

| Failure | Meaning | Response |
|---|---|---|
| Packet hash mismatch | Different evidence input. | Reject the comparison. |
| Prompt hash mismatch | Different task input. | Reject the comparison. |
| Raw text differs, parsed output matches | Runtime text drift exists, governance object stable. | Report raw drift; make only parsed-output claims. |
| Parsed output differs, route matches | Governance object drift exists below the label layer. | Report parsed drift; do not claim exact replay. |
| Route label differs | Governance-relevant drift. | Escalate for manual review. |
| Unsafe `PROCEED` appears in one profile only | Profile-specific safety regression. | Fail the profile on that packet. |
| Profile cannot run | Practical limitation. | Record fail-closed; do not invent equivalence. |

The selected-set prompt mismatch is an example of this discipline working. The H100 NVL held-out exact match is the positive case.

## Reproduction Sketch

The evidence packet was built from the existing lifecycle artifacts and replayed through live SGLang endpoints:

```bash
python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/profiles/h200_sglang_repeat_heldout \
  --lane all \
  --endpoint <H200_SGLANG_ENDPOINT>/v1 \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/profiles/h200_sglang_repeat_heldout/vast_lifecycle/machine_receipt.json \
  --runs 1 \
  --fail-on-error \
  --force

python3 scripts/run_qwen_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/profiles/h100nvl_sglang_heldout \
  --lane all \
  --endpoint http://127.0.0.1:18000/v1 \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/profiles/h100nvl_sglang_heldout/vast_lifecycle/machine_receipt.json \
  --runs 1 \
  --fail-on-error \
  --force

python3 scripts/summarize_xrpl_amendment_lifecycle_replay.py \
  --artifact static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z/profiles/h100nvl_sglang_heldout

python3 scripts/compare_sglang_cross_hardware_replay.py \
  --artifact static/benchmarks/sglang-cross-hardware-replay-20260603T023942Z
```

The H100 endpoint was local because it used SSH tunneling. The public artifact records the tunnel as transport metadata and redacts public provider endpoint details.

## Shutdown Receipt

The GPUs used for this packet were shut down after evidence capture:

```text
H200 Vast instance:      39137704
H100 NVL Vast instance:  39230200
after-destroy target instance count: 0
shutdown receipt hashes: /benchmarks/sglang-cross-hardware-replay-20260603T023942Z/gpu_shutdown/SHA256SUMS.txt
```

The shutdown receipt is part of the evidence packet because rented GPU work should have an operational closeout. A public replay experiment should not leave expensive infrastructure ambiguous.

## Conclusion

This packet supports a narrow but useful conclusion:

> SGLang replay is viable across the tested H200 and H100 NVL profiles for the XRPL lifecycle held-out packet set, under the pinned Qwen 27B FP8 model, pinned container, deterministic SGLang settings, identical packet hashes, and identical prompt hashes.

The result does not prove all GPUs, all SGLang versions, all Qwen profiles, or all future governance packets will behave this way. It does show that the replay primitive is not merely a one-machine anecdote, and that the harness can reject invalid comparisons when the prompt changes.

That is the right bar for a governance artifact: not "trust the model," but "publish the packet, bind the profile, replay the output, compare the hashes, and make drift visible."
