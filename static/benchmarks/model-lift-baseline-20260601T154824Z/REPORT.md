# Model-Lift Baseline Comparison

This packet compares saved Qwen3.6 scoring_v2 outputs against a deterministic rule baseline over the same frozen PFT testnet snapshot.

## Boundary

This is a comparator audit, not an accuracy benchmark. It invents no ground-truth labels. The deterministic baseline is an operator-authored heuristic derived from the public scoring_v2 dimensions. The prompt explicitly says the overall score is model judgment rather than a mechanical average, so the numeric baseline weights below are disclosed comparison rules, not protocol truth or hidden labels.

## Inputs

- Snapshot: `/home/postfiat/repos/dynamic-unl-scoring/data/testnet_snapshot.json`
- Scoring prompt: `/home/postfiat/repos/dynamic-unl-scoring/prompts/scoring_v2.txt`
- Model run directory: `/home/postfiat/repos/dynamic-unl-scoring/phase0/results/modal/qwen36-27b-fp8/2026-04-30_qwen36-27b-fp8_scoring-v2`
- Validators: 42
- Model runs: 5
- Cutoff/max size: 40/20
- Baseline weights: {"consensus": 0.42, "diversity": 0.13, "identity": 0.1, "reliability": 0.2, "software": 0.15}

## Results

- Model outputs identical across all saved runs: True
- Top-20 overlap: 15/20
- Top-k Jaccard: 0.6
- Model-only selections: 5
- Baseline-only selections: 5
- Pearson score correlation: 0.9362
- Spearman rank correlation: 0.8002
- Mean absolute score delta: 9.48

## Selection Disagreements

| Validator | Domain | Model | Baseline | Model rank | Baseline rank | Direction |
|---|---|---:|---:|---:|---:|---|
| `v009` | pft.g.money | 81 | 75 | 23 | 8 | baseline-only |
| `v012` | - | 83 | 71 | 7 | 22 | model-only |
| `v015` | pft.xbtseal.com | 81 | 78 | 27 | 6 | baseline-only |
| `v017` | - | 82 | 71 | 17 | 25 | model-only |
| `v022` | - | 83 | 71 | 10 | 26 | model-only |
| `v023` | - | 83 | 71 | 11 | 27 | model-only |
| `v026` | pft.akirax.xyz | 81 | 75 | 28 | 10 | baseline-only |
| `v028` | postfiat.nlh.xyz | 81 | 74 | 29 | 18 | baseline-only |
| `v029` | - | 82 | 71 | 19 | 28 | model-only |
| `v037` | pfthaploid.com | 82 | 75 | 22 | 13 | baseline-only |

## Integration Note

A defensible whitepaper sentence from this packet is limited to: the project ran a deterministic-rule comparator over the same frozen scoring_v2 snapshot and recorded overlap/disagreement metrics. It should not be phrased as proof that the model is correct or that the comparator is ground truth.
