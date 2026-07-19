---
title: "Proving on Apple Silicon: A Spec for a Metal Backend to SP1"
date: 2026-07-19T00:00:00Z
draft: true
url: "/proving-on-apple-silicon/"
aliases:
  - "/blog/proving-on-apple-silicon/"
breadcrumb_label: "Blog"
breadcrumb_url: "/blog/"
summary: "SP1's GPU prover is CUDA-only, so today a pfUSDC withdrawal proof (or any SP1 proof) needs an NVIDIA GPU — a rented box or a prover service. This spec scopes the alternative: accelerate SP1 proving on Apple Silicon with Metal, so a desktop wallet can generate its own proofs locally. It is written to be executed by an agent on a Mac: a phased plan that first measures the real M-series CPU baseline, profiles the hot kernels, surveys existing Metal/Plonky3 work, prototypes a Metal compute shader for the dominant kernel, and reports a go/no-go on a full backend — with a hard correctness bar (bit-identical proofs) throughout."
description: "Engineering spec for porting SP1 zkVM proof acceleration from CUDA to Apple Metal on Apple Silicon: pipeline background, the Plonky3 STARK backend and gnark wrap, a phased CPU-baseline → profile → Metal-kernel-prototype plan, correctness requirements, and the gnark-wrap caveat."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - SP1
  - Zero Knowledge
  - Apple Silicon
  - Metal
  - GPU
  - Proving
  - Spec
---

> **Status: internal engineering spec / R&D plan.** This is written to be handed to a coding agent
> running on an Apple Silicon Mac. It is not a result — it is the plan for producing one. Every
> phase ends in a measurement and a decision gate.

## Why this matters

Post Fiat's pfUSDC bridge, and every SP1 proof, currently depends on an **NVIDIA CUDA GPU** to
generate proofs in practical time. On CPU, a pfUSDC egress proof took ~2h43m; on a rented RTX 5090
it takes ~3 minutes. That is fine when a *prover service* (operator-run, or the Succinct prover
network) generates proofs on users' behalf — but it means the proof cannot be generated on the
device most users actually own.

The prize is **client-side proving on a Mac.** If an Apple Silicon machine can produce an SP1 proof
in an acceptable time, a desktop wallet can generate its own pfUSDC withdrawal proof with no rented
GPU, no operator prover in the trust or availability path, and no proving fee. "Who runs the GPU?"
becomes "you do, on the laptop you already have." That is a real UX and decentralization win, and —
because SP1 has no Metal backend today — a genuine open-source contribution beyond Post Fiat.

The constraint that forces this work: **SP1's GPU prover is CUDA-only. There is no Apple Metal
backend.** A Mac can only CPU-prove today. This spec scopes closing that gap.

## What SP1 actually does (so you accelerate the right thing)

SP1 is a RISC-V zkVM. A proof runs through a pipeline; know where the time goes before touching Metal:

1. **Execute** — run the guest program, record the trace. Cheap (seconds); CPU-bound; not the target.
2. **Core STARK prove** — prove the execution trace. This is the dominant cost and what the CUDA
   prover accelerates. SP1's STARK backend is **Plonky3**: arithmetic over a small prime field
   (BabyBear / KoalaBear depending on SP1 version), large **NTTs/FFTs**, **Poseidon2** Merkle
   hashing for the commitment/FRI layers, and MSM-free FRI. These kernels are massively parallel —
   the reason a GPU helps.
3. **Recursion / compress / shrink** — recursively prove the core proofs down to a single small
   STARK. Same kernel families as (2), also GPU-accelerated on CUDA.
4. **Wrap (STARK → SNARK)** — convert the final STARK to an on-chain-verifiable Groth16 or PLONK
   proof via **gnark** (a separate Go prover). In our runs this wrap is a **~132s fixed floor**,
   largely independent of program size. On CUDA it can use ICICLE-accelerated MSM; **on a Mac it
   will run on CPU** unless separately addressed. Do not ignore this — see the caveat below.

The CUDA path is Succinct's `sp1-gpu-server` ("moongate"), which offloads (2) and (3). A Metal port
means giving the Plonky3 backend a Metal implementation of its hot kernels.

## The Apple Silicon toolbox

- **Metal compute shaders** — the GPU. The target for parallel field arithmetic (NTT, Poseidon2,
  pointwise mul). Bind from Rust via the `metal` crate (`metal-rs`).
- **Unified memory** — Apple Silicon shares RAM between CPU and GPU. Big advantage: no PCIe host↔device
  copies, which are a real cost on discrete NVIDIA cards. Zero-copy buffer handoff is possible.
- **Accelerate / AMX** — Apple's CPU matrix/vector coprocessor. A cheaper intermediate win than a
  full GPU port for some kernels; reachable from the CPU prover without Metal.
- **What won't help:** the Neural Engine (not general-compute programmable for this).

## Baselines to beat (measured on an RTX 5090, SP1 CUDA + PLONK/Groth16)

| Stage | Program | Metric |
|---|---|---|
| Execute | pfUSDC egress (3-block segment) | ~2.5 s, ~74.8M cycles |
| Ingress proof | Groth16 | ~75 s (setup+prove) |
| Egress proof | PLONK, accel guest | ~187 s (~3.1 min) setup+prove; ~132s of that is the gnark wrap |

The Mac target is not "beat the 5090" — it is "acceptable for a desktop wallet" (single-digit
minutes, ideally). Establish the honest CPU baseline first; the gap to close may be smaller than
assumed, or the wrap may dominate.

## The plan (execute in order; each phase gates the next)

### Phase 0 — Environment
- Record the machine: chip (`sysctl -n machdep.cpu.brand_string`), core counts, GPU, and RAM
  (`sysctl hw.memsize`). Metal proving is memory-hungry; note the ceiling.
- Install Rust and the SP1 toolchain (`sp1up`); confirm `cargo prove --version`.
- Build a representative workload from source: the pfUSDC egress guest + `tools/pfusdc-tier4-prover`
  from `github.com/postfiatorg/postfiatl1v2`, plus a tiny SP1 program (e.g., fibonacci) for fast
  iteration. Note the pinned SP1 version — pin all work to it.
- **Deliverable:** an environment report and a reproducible build.

### Phase 1 — CPU baseline (the first real number)
- Prove the tiny program, then the real pfUSDC egress short-segment witness, on the M-series **CPU**
  prover. Use `/usr/bin/time -l` for wall-time and peak RSS.
- Record the **per-phase split**: execute vs core-prove vs recursion vs gnark wrap. (SP1 exposes
  timing; if not granular enough, wrap each stage.)
- **Decision gate:** if the CPU proof is already acceptable for a desktop wallet (say ≤ a few
  minutes), the whole Metal effort may be unnecessary — report that and stop. If it is tens of
  minutes, continue.
- **Deliverable:** honest Mac CPU latency + memory, per phase.

### Phase 2 — Profile the hot kernels
- Profile the CPU core-prove with Instruments (Time Profiler) or `cargo flamegraph`.
- Quantify the share of: **Poseidon2 hashing**, **NTT/FFT**, **field multiply/pointwise**, and the
  **gnark wrap**. Rank them. The top one or two kernels are the Metal targets.
- **Deliverable:** a ranked kernel profile with % of total proof time.

### Phase 3 — Feasibility survey
- Survey existing work before writing shaders: any Metal backend for Plonky3; Metal NTT/Poseidon2
  libraries; ICICLE's Metal support; `mopro`, `zkmopro`, and mobile-proving projects; any community
  SP1-on-Metal effort.
- Identify the exact **Plonky3 trait boundary** where a Metal implementation plugs in (the field /
  FFT / hasher abstractions), so a backend can be added without forking the whole prover.
- **Deliverable:** a build-vs-reuse verdict and the integration seam.

### Phase 4 — Prototype the dominant kernel on Metal
- Implement a Metal compute shader for the **single hottest kernel** from Phase 2 (most likely the
  field NTT or Poseidon2 permutation), bound via `metal-rs`, exploiting unified memory (zero-copy).
- Integrate behind a **feature flag** with a **CPU fallback**; never replace the reference path.
- **Deliverable:** a working Metal kernel with a microbenchmark vs its CPU equivalent.

### Phase 5 — Measure, verify, extrapolate
- End-to-end: prove the pfUSDC egress witness with the Metal kernel enabled; measure speedup.
- **Correctness (non-negotiable):** the resulting proof and program **vkey must be bit-identical**
  to the CPU/CUDA reference, and the proof must verify on-chain. A wrong kernel is a soundness break,
  not a bug. Run FIPS/SP1 test vectors and equivalence-vs-reference on every kernel; keep the CPU
  path as the oracle.
- Extrapolate: given the kernel speedup and its profile share (Amdahl), estimate full-proof time if
  the remaining kernels were also ported.
- **Deliverable:** measured speedup, a proof of correctness, and a **go/no-go** on a full Metal
  backend.

## The gnark-wrap caveat (read before promising a full local proof)

Even a perfect Metal STARK backend does not, by itself, deliver a fast Mac proof. The **gnark wrap
(~132s) runs on CPU on a Mac** and may then *dominate* total time. Before committing to a full
backend, this sub-question must be answered:

- Measure the gnark wrap in isolation on the Mac CPU. Is it tolerable?
- Is a **Groth16** wrap faster than PLONK for this circuit on CPU? (Smaller proof; possibly cheaper.)
- Can the wrap's MSM be Metal-accelerated, or is the wrap best left to a small remote/one-shot step?
- Worst case, a viable product is "Metal STARK locally + the tiny final wrap done remotely or via
  the SP1 network" — still removes the heavy per-proof GPU dependency.

## Success criteria

1. A published, honest **Mac CPU baseline** (Phase 1) — useful on its own.
2. A **ranked kernel profile** (Phase 2).
3. A **feasibility verdict** with the integration seam (Phase 3).
4. A **correct, benchmarked Metal kernel prototype** (Phases 4–5), bit-identical to reference.
5. A defensible **full-proof time estimate** and go/no-go, including the wrap.

## Risks and honest unknowns

- A full Metal SP1 backend is a substantial undertaking; it may not beat a cents-per-proof rented
  CUDA box or the SP1 prover network on pure economics — the case for it is UX, privacy, and
  decentralization (local proving), not raw cost.
- The gnark wrap may cap the achievable local latency regardless of STARK acceleration.
- SP1/Plonky3 internals move; pin versions and keep the Metal path behind a flag.
- Correctness risk is severe: an incorrect accelerated kernel silently breaks soundness. The
  bit-identical-vs-reference bar is the guardrail and is not optional.

## Handoff notes

- Source of the real workload: `github.com/postfiatorg/postfiatl1v2` (`tools/pfusdc-tier4-prover`,
  `programs/pfusdc-egress`). Pin to the repo's SP1 version.
- Reach the Mac for remote agent work via Tailscale SSH (enable Remote Login + `tailscale up --ssh`
  on the Mac).
- Report each phase's deliverable back before proceeding to the next; correctness gates override
  speed at every step.
