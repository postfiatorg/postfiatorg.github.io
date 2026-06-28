# LLM Governance Replay Head-To-Head

Generated: 2026-06-01T23:13:52+00:00

## Question

Does the Qwen replay route beat a simpler deterministic rule floor on the same
13 XRPL amendment packets?

## Answer

No route-choice lift was measured. Qwen and the deterministic rule floor selected
the same route on all 13 packets.

The measured advantage in this packet is process cost, not route discrimination:
the replay-default workflow is modeled at 75.83 review hours versus
399.75 hours for a deterministic alert that every validator
reviews, a 81.03% reduction. Against a standing
committee model, the reduction is 92.89%.

## Inputs

- Source packet: `static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z`
- Source packet SHA256SUMS hash: `b809a6b2b35d5dfccd8fbc3b5880ad14f8707886f88f84e11efe4e574b74f894`
- Contested method: Qwen/Qwen3.6-27B-FP8 deterministic SGLang replay-default route
- Simpler baseline: `xrpl-amendment-replay-baseline-v1`
- Packets: 13
- Qwen outputs: 39
- Runs per packet: 3
- Machine receipt SHA-256: `50ea43981c09fb7a83a663718e96ec7683a953b933ffaf5856244bec5d7c981d`

## Measurements

| Measurement | Value |
|---|---:|
| Qwen-vs-rule disagreements | 0 / 13 |
| Qwen wins versus rule, judged by distance to historical label | 0 |
| Rule wins versus Qwen, judged by distance to historical label | 0 |
| Exact ordinal route sequence match | true |
| Route distribution match | true |
| Unsafe `PROCEED` events | 0 |
| Standing committee review hours | 1066.00 |
| Deterministic alert review hours | 399.75 |
| Qwen replay-default review hours | 75.83 |
| Attention reduction vs deterministic alert | 81.03% |
| Attention reduction vs standing committee | 92.89% |

## Route Distributions

| Route | Historical | Deterministic baseline | Qwen replay |
|---|---:|---:|---:|
| PROCEED | 1 | 1 | 1 |
| HOLD_FOR_CHALLENGE | 8 | 8 | 8 |
| DELAY_FOR_FIX | 2 | 2 | 2 |
| REJECT | 2 | 2 | 2 |

## Safe Integration Sentence

On the 13-packet XRPL amendment replay corpus, Qwen added no route-choice lift over the deterministic rule floor (0/13 disagreements), while the replay-default process reduced modeled review hours by 81.03% versus a deterministic alert that every validator reviews.

## Claim This Packet Does Not Support

This packet does not show that Qwen is more accurate or more discriminating than the deterministic rule engine on route choice.

## Files

- `comparison.csv`: per-packet head-to-head comparison.
- `summary.json`: machine-readable metrics and source hashes.
- `decision.json`: integration decision and safe/unsafe claims.
- `SOURCE_HASHES.json`: hashes of the upstream packet files used.
- `COMMANDS.txt`: reproduction commands.
- `SHA256SUMS.txt`: hashes for this evidence packet.
