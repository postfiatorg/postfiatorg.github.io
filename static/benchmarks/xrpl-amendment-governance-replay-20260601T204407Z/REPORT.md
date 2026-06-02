# XRPL Amendment Governance Replay Report

Generated: 2026-06-01T21:30:12Z

## Summary

- Packets: 13
- Qwen runs: 39
- Schema-valid output rate: 1.0
- Parsed-route converged packets: 13
- Exact-output-hash converged packets: 13
- Historically aligned route rate: 1.0
- Unsafe proceed count: 0
- Runtime kind: openai_compatible_sglang
- Model: Qwen/Qwen3.6-27B-FP8
- Machine receipt: vast_lifecycle/machine_receipt.json
- Machine receipt SHA-256: 50ea43981c09fb7a83a663718e96ec7683a953b933ffaf5856244bec5d7c981d
- Attention reduction vs standing committee: 0.9289
- Attention reduction vs deterministic alert: 0.8103

## Counterfactual Table

| Event | Historical | Deterministic | Replay | Vote | Unsafe Proceed |
|---|---:|---:|---:|---:|---:|
| AMM post-launch pool discrepancy | DELAY_FOR_FIX | DELAY_FOR_FIX | DELAY_FOR_FIX | NO | false |
| AMM / XLS-30 activation vote reversal | DELAY_FOR_FIX | DELAY_FOR_FIX | DELAY_FOR_FIX | NO | false |
| AMMClawback | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| Batch | REJECT | REJECT | REJECT | NO | false |
| Clawback | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| fixAMMOverflowOffer | PROCEED | PROCEED | PROCEED | YES | false |
| LendingProtocol | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| MPTokensV1 | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| PermissionDelegation | REJECT | REJECT | REJECT | NO | false |
| PermissionedDEX | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| PermissionedDomains | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| SingleAssetVault | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |
| TokenEscrow | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD_FOR_CHALLENGE | HOLD | false |

## Runtime Boundary

Production replay uses Qwen/Qwen3.6-27B-FP8 on deterministic SGLang with a captured machine receipt.
