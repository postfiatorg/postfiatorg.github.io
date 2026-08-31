---
title: "Runbook: Deterministic Qwen 3.8 Inference for Replayable Index Scoring"
date: 2026-08-31T00:00:00Z
summary: "The locked serving profile that makes Qwen 3.8 27B FP8 produce byte-identical output across independent H200 hosts: exact model pin, runtime image digest, SGLang launch flags, fixed-batch request discipline, and the two-host replay gate that verifies every raw response byte for byte."
categories:
  - Post Fiat Research
tags:
  - Determinism
  - Qwen
  - SGLang
  - Replay
  - Index
---

## Purpose

Corbanu index runs treat the scoring model as a deterministic function: the
same request bytes must yield the same response bytes on any admitted host.
Every published index artifact carries a replay proof in which two independent
H200 machines scored the full 1,000-company universe and every raw response
matched byte for byte (1,000 of 1,000 comparisons byte-identical in the
published live-sample artifact). This runbook records the exact profile that
achieves that, and the hazards that break it.

## Locked model and runtime pin

Every element below is pinned by identifier or digest. A run that deviates on
any row is rejected by the operator before scoring starts.

| Element | Locked value |
| --- | --- |
| Model | `Qwen/Qwen3.8-27B-FP8` |
| Model revision | `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a` |
| Runtime image | `lmsysorg/sglang:nightly-dev-cu13-20260817-d91c3682@sha256:fa8774dd128600a09fd6d46670b06fb69a55dac8a3881e50ccf0916a45eb39af` |
| Hardware | NVIDIA H200, single GPU |
| Tensor parallelism | 1 |
| Attention backends | triton (attention and linear attention) |
| Radix cache | off |
| CUDA graphs | off (prefill and decode) |
| Overlap schedule | off |
| Deterministic inference | on |
| Random seed | `438916795` |
| Context length | 32,768 |
| Max running requests | 32 |
| Execution profile id | `qwen3.8-27b-fp8-h200-sglang-strict-fixed32-schema-v2` |

## Server launch

The host bootstrap downloads the pinned revision through
`huggingface_hub.snapshot_download`, records GPU identity, driver, and Python
version into the run directory, then launches SGLang bound to localhost:

```bash
python3 -m sglang.launch_server \
  --model-path "$model_path" \
  --served-model-name Qwen/Qwen3.8-27B-FP8 \
  --host 127.0.0.1 \
  --port 8000 \
  --trust-remote-code \
  --tp 1 \
  --context-length 32768 \
  --mem-fraction-static 0.75 \
  --chunked-prefill-size 4096 \
  --max-running-requests 32 \
  --reasoning-parser qwen3 \
  --enable-deterministic-inference \
  --disable-radix-cache \
  --random-seed 438916795 \
  --enable-metrics
```

The server is reachable only through a narrow HTTPS tunnel; it is bound to
localhost and exposed to a single local operator process.

## Request discipline

- `temperature: 0`, `top_p: 1`, thinking disabled per request.
- Companies are scored in fixed 32-request batches per host. The batch
  schedule is part of the profile: floating-point reduction order inside a
  batch depends on which requests share it, so the batch composition itself
  must replay.
- The mandate compiler and every company score use strict JSON response
  schemas; a response that fails to parse fails the run rather than being
  repaired.
- Requests are content-addressed: each request's SHA-256 is recorded and must
  match across hosts before response bytes are even compared.

## Two-host replay gate

A run executes on two independent H200 machines, primary and replay:

1. The compiled mandate rubric is generated on both hosts concurrently; the
   run aborts unless the raw rubric bytes are identical.
2. All 1,000 companies are scored on both hosts in the same fixed batch
   order. Both hosts run to completion so a failure on one never alters the
   other's batch schedule.
3. For every company, `request_sha256` must match, then the raw response
   bytes must match exactly.
4. Any batch-sensitive mismatch triggers strict replay recovery: the exact
   request is recomputed alone on otherwise idle machines on both hosts, and
   only a byte-identical strict pair is admitted.
5. The published artifact carries the per-company primary and replay content
   hashes plus an aggregate comparison SHA-256, so the replay claim can be
   inspected company by company from the artifact alone.

Published evidence: the live-sample artifact at
[/benchmarks/agentic-index-live-samples-20260827.json](/benchmarks/agentic-index-live-samples-20260827.json)
embeds the full `model_profile` and a `replay_proof` block with
`byte_identical_count: 1000` of `comparison_count: 1000`, alongside a
representative raw replay with matching content hashes.

## Determinism hazards

Each of these produced or would produce drift, and each is closed by the
profile above.

| Hazard | Why it breaks byte-level replay | Mitigation |
| --- | --- | --- |
| Radix / prefix cache | Cache hits change kernel execution paths between otherwise identical requests | `--disable-radix-cache` |
| Dynamic batching | Reduction order varies with co-scheduled requests | Fixed 32-request batches; batch schedule locked in the profile |
| CUDA graphs and overlap scheduling | Capture and replay reorder work relative to eager execution | Both disabled |
| Tensor parallelism | Cross-GPU reductions have no fixed summation order | Single GPU, `--tp 1` |
| Model or tokenizer drift | A silently updated repo changes weights or prompt bytes | Revision pin `017b9c7a…` verified at load |
| Runtime drift | Kernel changes across SGLang builds change numerics | Image pinned by sha256 digest |
| Sampling | Any stochastic decode path defeats replay | Greedy decode: temperature 0, top_p 1, fixed seed, thinking off |
| Hardware class drift | Different GPU generations produce different numerics | Admitted hardware locked to H200 |

## Profile history

- `qwen3.8-27b-fp8-h200-sglang-deterministic-noradix-schema-v1`: first
  deterministic profile; established the pinned runtime, greedy decode, and
  radix-cache-off baseline used for the published live samples.
- `qwen3.8-27b-fp8-h200-sglang-strict-fixed32-schema-v2`: current admitted
  profile; adds the fixed 32-request batch contract
  (`request_batch_size_per_host: 32`), strict replay recovery, and the
  batch-byte-identical count in the published proof. The public index
  contract test rejects artifacts from superseded profiles.

## Scope

This profile makes one pinned model, one pinned runtime, and one hardware
class replayable at the byte level. It is a serving discipline, and it is
sufficient for two-host replay gating of index runs. Cross-vendor or
cross-generation portability requires the separate consensus-executor line of
work and is out of scope here.
