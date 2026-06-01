# AI Governance Red-Team Comparison

Run id: `20260530T033500Z`
Packet set root: `8566a4a138fdf87013ecb29459aa216ff8f480a1557b9e03d0ba6cc4894e2fbc`
Report root: `676c34cd382db6d2f0f928d2bafcad2d3d94bbfabfe11cbfad6fadb9ee652230`

## Acceptance

- status: `pass`
- production false-positive live admits: `0`
- production challenge capture: `64/72`
- safe deterministic challenge capture: `0/72`
- review workload saved: `20.4 hours`
- H100/H200 route convergence: `240/240`
- H100/H200 parsed/raw/logprob convergence: `720/720`, `720/720`, `720/720`

## Path Comparison

| path | route | false-positive admits | challenge capture | clean admits | review hours |
| --- | ---: | ---: | ---: | ---: | ---: |
| `safe deterministic rubric v2` | `160/240` | `0` | `0/72` | `48/48` | `65.33` |
| `production exact-selector plus replayed model residual gate` | `224/240` | `0` | `64/72` | `48/48` | `44.93` |

## Marginal Value

The safe deterministic rubric preserves the zero-unsafe-admit invariant by routing residual ambiguity to untyped committee review. The production path keeps the same zero-unsafe-admit invariant, captures typed challenge routes for most residual cases, and reduces first-pass review workload under the declared cost fixture.

- challenge-capture lift: `64/72`
- review minutes saved: `1224`
- review hours saved: `20.4`

## Hash-Split Holdouts

Partition seed: `postfiat-ai-governance-redteam-partition-v1`

| partition | packets | production FP admits | production challenges | safe challenges | review hours saved |
| --- | ---: | ---: | ---: | ---: | ---: |
| `calibration` | `120` | `0` | `35/39` | `0/39` | `10.2` |
| `adaptive_holdout` | `60` | `0` | `15/17` | `0/17` | `5.38` |
| `blind_hash_holdout` | `60` | `0` | `14/16` | `0/16` | `4.82` |

## Cost Fixture

- `untyped_hold_minutes`: `25`
- `typed_challenge_minutes`: `8`
- `no_op_minutes`: `15`
- `admit_minutes`: `0`
- `reject_minutes`: `0`
