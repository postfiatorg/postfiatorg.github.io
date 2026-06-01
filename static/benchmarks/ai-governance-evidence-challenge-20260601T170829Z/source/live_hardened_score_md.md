# AI Governance Live Benchmark Score

Run id: `20260530T134707Z`
Packet set: `ai-governance-live-machine-corpus-v1`
Packet set root: `8566a4a138fdf87013ecb29459aa216ff8f480a1557b9e03d0ba6cc4894e2fbc`

## Production Acceptance

- status: `PASS`
- live path: `exact selector plus qwen residual router`
- false-positive live admits: `0`
- route: `224/240`
- challenge capture: `64/72`
- parser/schema/determinism: `True`
- diagnostic ablations: `no live authority`

## exact selector plus qwen residual router (production path)

- route: `224/240`
- false-positive live effects: `0`
- challenge capture: `64/72`
- parse ok: `240/240`
- schema valid: `240/240`
- deterministic packets: `240/240`

| family | route | false positive | challenge capture |
| --- | --- | ---: | --- |
| `attestor-conflict` | `40/40` | `0` | `24/24` |
| `omission-evidence` | `40/40` | `0` | `8/8` |
| `privacy-assurance` | `40/40` | `0` | `16/16` |
| `registry-transition` | `40/40` | `0` | `0/0` |
| `replay-profile` | `32/40` | `0` | `0/8` |
| `validator-admission` | `32/40` | `0` | `16/16` |
