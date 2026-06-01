# AI Governance Live Benchmark

This packet family exists to strengthen the empirical base for the whitepaper's
AI-governance claim without making the claim circular. No packet asks the model
to endorse PostFiat, Cobalt, Orchard, ML-DSA, or any other feature being sold by
the paper.

The benchmark tests whether a pinned model profile can classify live-effect
governance evidence across multiple packet families while preserving the
containment rule: the model has no positive authority and can only downgrade a
selector-admit into `hold`, `hold-for-challenge`, or `no-op`.

## Corpus

The v1 corpus contains six governance packet families:

- `validator-admission`
- `replay-profile`
- `attestor-conflict`
- `registry-transition`
- `omission-evidence`
- `privacy-assurance`

The default corpus has 240 packets: six families, five variants per family, and
eight deterministic copies per variant. The copies keep the route distribution
large enough for live-machine repeatability checks while preserving exact
auditable expected labels.

Packet set root for the final live run:
`8566a4a138fdf87013ecb29459aa216ff8f480a1557b9e03d0ba6cc4894e2fbc`.

## Build And Local Baseline

```bash
scripts/ai-governance-benchmark-build-corpus
scripts/ai-governance-rubric-baseline
scripts/ai-governance-benchmark-score \
  --rubric reports/ai-governance-live-benchmark/rubric/latest/rubric_outputs.json
```

## H100/H200 SGLang Run

Start or point to an OpenAI-compatible SGLang endpoint, then run:

```bash
scripts/ai-governance-qwen-benchmark \
  --base-url http://127.0.0.1:30000/v1 \
  --api-key EMPTY \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-label h200-a \
  --hardware-class H200 \
  --repeats 3 \
  --max-tokens 320 \
  --disable-thinking \
  --logprobs

scripts/ai-governance-benchmark-score \
  --rubric reports/ai-governance-live-benchmark/rubric/latest/rubric_outputs.json \
  --qwen reports/ai-governance-live-benchmark/qwen/latest/parsed_outputs.jsonl \
  --production-only \
  --require-production-pass
```

Run the same command on each admitted live machine, changing
`--machine-label`, `--hardware-class`, and `--provider-run-id`. The paper-grade
matrix should include at least one H100 and one H200 run under the same pinned
profile. Cross-profile MLX runs can support semantic convergence but should not
be presented as byte-identical logprob evidence.

After two or more machine runs exist, verify the matrix:

```bash
scripts/ai-governance-live-matrix-verify \
  reports/ai-governance-live-benchmark/qwen/<h100-run> \
  reports/ai-governance-live-benchmark/qwen/<h200-run>
```

## Final H100/H200 Evidence

Final clean run: 2026-05-29 UTC.

- Model: `Qwen/Qwen3.6-27B-FP8`
- Benchmark source hash:
  `scripts/ai-governance-qwen-benchmark`
  `45116ac277aa36491ace9d0353d511b75786da004b2f30beb19a5eebcf00b4be`
- H200 run:
  `reports/ai-governance-live-benchmark/qwen/20260529T155058Z-vast-h200-38417557-field-rules-citation-clean-v2`
- H100 run:
  `reports/ai-governance-live-benchmark/qwen/20260529T155058Z-vast-h100-38417559-field-rules-citation-clean-v2`
- Score reports:
  `reports/ai-governance-live-benchmark/score/20260529T160937Z` and
  `reports/ai-governance-live-benchmark/score/20260529T161225Z`
- Production-only score report:
  `reports/ai-governance-live-benchmark/production-score/20260530T010126Z`
- Production-only score report root:
  `e866b6a35499d4368d67ab02834e3e04a3561a224528c17f6dc15f6674a42b08`
- Matrix report:
  `reports/ai-governance-live-benchmark/matrix/20260529T161646Z`
- Matrix report root:
  `c19ba271b263838d490fb0244fefde6c72dd9d5ef84deb12a7fd0f0316837fa0`
- MVP matrix rerun:
  `reports/ai-governance-live-benchmark/matrix/20260530T010142Z`
- MVP matrix report root:
  `5859dab7b2e7b68a18116caf756e24fba1b3a9f88579c4fc2cf494482b4660e7`
- Parsed-output root, both machines:
  `c1e1cb47fffa6e523803774698d67e40b8eaca64d9044d2afd7c70a0f2bf3a7c`
- Route convergence: `240/240`
- Raw-output root convergence: `720/720`
- Response-logprob root convergence: `720/720`
- Per-machine schema validity: `720/720`
- Per-machine deterministic packet fraction: `240/240`

Promoted production score against the committee route baseline:

| path | route | false-positive live admits | challenge capture |
| --- | ---: | ---: | ---: |
| exact selector + Qwen residual router | `224/240` | `0` | `64/72` |

The exact-selector-only and Qwen-only paths are diagnostic ablations. They have
no live authority and are not promotable evidence for the whitepaper. They exist
to verify that the production route is an ensemble with one-sided model
authority: exact rejects, holds, and no-ops dominate; the model can only
downgrade an exact admit into `hold`, `hold-for-challenge`, or `no-op`.

## Red-Team Marginal-Value Comparison

The red-team comparison asks the scorer's central question: what does the model
add over a safe deterministic fallback?

Report:

```text
reports/ai-governance-redteam/20260530T031144Z
```

Report root:

```text
6508aa27ef24cbf576e722814978876d36c100c9c434ef3145ad782f088c79c4
```

The comparison uses the same 240-packet corpus, production parsed outputs, and
H100/H200 matrix. The safe deterministic rubric preserves safety by admitting
only clean packets and routing residual ambiguity to untyped committee review.
The production path keeps the same zero-unsafe-admit invariant and adds typed
challenge triage.

| path | route | false-positive admits | challenge capture | clean admits | review hours |
| --- | ---: | ---: | ---: | ---: | ---: |
| safe deterministic rubric v2 | `160/240` | `0` | `0/72` | `48/48` | `65.33` |
| exact selector + Qwen residual router | `224/240` | `0` | `64/72` | `48/48` | `44.93` |

Under the declared cost fixture, the model-assisted path saves `20.4` first-pass
review hours while preserving zero false-positive live admits.

The follow-up comparison adds a deterministic hash split over the same corpus:

```text
reports/ai-governance-redteam/20260530T033500Z
```

Report root:

```text
676c34cd382db6d2f0f928d2bafcad2d3d94bbfabfe11cbfad6fadb9ee652230
```

| partition | packets | production challenges | safe deterministic challenges | production false-positive admits | review hours saved |
| --- | ---: | ---: | ---: | ---: | ---: |
| calibration | 120 | `35/39` | `0/39` | `0` | `10.2` |
| adaptive holdout | 60 | `15/17` | `0/17` | `0` | `5.38` |
| blind hash holdout | 60 | `14/16` | `0/16` | `0` | `4.82` |

Generate the promotable production-only score report with:

```bash
scripts/ai-governance-benchmark-score \
  --rubric reports/ai-governance-live-benchmark/rubric/latest/rubric_outputs.json \
  --qwen reports/ai-governance-live-benchmark/qwen/20260529T155058Z-vast-h200-38417557-field-rules-citation-clean-v2/parsed_outputs.jsonl \
  --production-only \
  --require-production-pass \
  --out-root reports/ai-governance-live-benchmark/production-score
```

The first live passes are intentionally retained as local reports because they
showed two implementation issues: token-budget clipping under a loose citation
prompt, and a same-second run-directory collision. The promoted run above uses
short citations, explicit typed field rules, and machine-qualified run ids.

## Acceptance Bar

The evidence should not be promoted into the whitepaper as broad production
evidence unless the live-machine matrix satisfies:

- zero parser/schema escapes;
- zero false-positive live-effect admits in the combined selector-plus-model
  path;
- all stale, split, drifted, or unresolved replay cases fail closed;
- same-profile H100/H200 runs converge on parsed roots and logprob roots where
  the endpoint exposes logprobs;
- the report states results as fractions, not decimal precision.
