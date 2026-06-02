# XRPL Batch Pre-Disclosure Replay Simulation

Generated: 2026-06-01T23:54:57+00:00

## Question

Could a PostFiat-style replay packet have improved on a simple deterministic
rule floor during the February 2026 XRPL Batch amendment incident?

## Boundary

Runtime kind: `openai_compatible_sglang`

Replay-grade: `True` — Pinned Qwen/Qwen3.6-27B-FP8 SGLang endpoint with captured machine receipt.

The model prompt excludes the February 19, 2026 vulnerability disclosure and
the exploit description. Those later facts are used only after the run to score
whether the output named the right risk surface.

## Inputs

- Pre-disclosure packet: `predisclosure_packet.json`
- Deterministic baseline: `deterministic_rule_baseline.json`
- Prompt hash: `63d13f7bd4dc64a6a143c77e184b3b4fa7bd919b365f475f0c2ee5c7e99bda49`
- Local rippled 2.5.0 source: `1e01cd34f7a216092ed779f291b43324c167167a`
- Local rippled 3.1.3 source: `46b241ace8b30d9c9775d60ffba7d24b21903896`
- Machine receipt hash: `6a91e2bfced980cb6bbcf3f2ff62a47dcfe8f8f9c6f9a216bfd32b32688f8114`

## Deterministic Baseline

The deterministic rule baseline routes `HOLD_FOR_CHALLENGE` because Batch is a
new authorization/signature primitive with unsigned inner transactions. It does
not identify a specific signer-validation loop or premature-success defect.

Score:

```json
{
  "held_or_rejected": true,
  "identified_loop_or_early_success_risk": false,
  "identified_signer_validation_surface": false,
  "identified_unsigned_inner_authorization": true,
  "matched_later_bug_class": false,
  "route": "HOLD_FOR_CHALLENGE",
  "specific_challenge_lift": false
}
```

## Model Aggregate

```json
{
  "held_or_rejected": 5,
  "identified_loop_or_early_success_risk": 5,
  "identified_signer_validation_surface": 5,
  "identified_unsigned_inner_authorization": 5,
  "machine_receipt_sha256": "6a91e2bfced980cb6bbcf3f2ff62a47dcfe8f8f9c6f9a216bfd32b32688f8114",
  "matched_later_bug_class": 5,
  "model": "Qwen/Qwen3.6-27B-FP8",
  "provider": "openai_compatible_sglang",
  "replay_grade": true,
  "replay_grade_reason": "Pinned Qwen/Qwen3.6-27B-FP8 SGLang endpoint with captured machine receipt.",
  "route_counts": {
    "HOLD_FOR_CHALLENGE": 5
  },
  "runs": 5,
  "specific_challenge_lift": 5
}
```

## Result

In a pre-disclosure Batch H200/SGLang replay, the deterministic rule floor could only issue a generic HOLD for new authorization semantics, while Qwen named the Batch signer-validation surface in 5/5 runs and matched the later signer-loop/early-success bug class in 5/5 runs.

## What This Does Not Prove

This run does not prove the model would have prevented the incident; it only measures whether the pre-disclosure packet elicits a replayable challenge matching the later-known bug class.

## Files

- `predisclosure_packet.json`: facts and bounded code excerpts available to the model.
- `deterministic_rule_baseline.json`: simple rule-floor output.
- `model_run_*.json`: per-run Qwen outputs and scoring.
- `model_aggregate.json`: aggregate route and challenge metrics.
- `runtime_manifest.json`: provider, endpoint class, and replay-grade metadata.
- `decision.json`: safe and forbidden integration claims.
- `SHA256SUMS.txt`: artifact hashes.
