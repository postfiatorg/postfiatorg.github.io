# Model-Lift Boundary Adjudication

This packet adjudicates the 10 boundary disagreements from the prior model-lift comparator without inventing labels.

## Boundary

Adjudication from existing snapshot fields only. No ground-truth labels or human committee labels are invented.

## Inputs

- Source packet: `static/benchmarks/model-lift-baseline-20260601T154824Z`
- Source summary SHA-256: `c590167120b292491f672a061cf6206432cab924161769b7580f5d2910263219`
- Source comparison SHA-256: `a58aa0826f4430f7ef20ea82afd3b0955d0dda1a934cf95a6bd6899fc8896ea2`
- Prior top-20 overlap: 15/20
- Prior Jaccard: 0.6

## Result

- Boundary disagreements adjudicated: 10
- Model-only cases: 5
- Baseline-only cases: 5
- Model reasoning used only allowed saved fields: True
- Model-only average 30d agreement: 0.997724
- Baseline-only average 30d agreement: 0.99383
- Proven model advantage from existing rows: 0
- Proven baseline advantage from existing rows: 0
- Policy-tradeoff cases: 10

The prior benchmark exposed repeatable boundary disagreement, not model superiority. Existing fields show a clean tradeoff: model-only selections have stronger 30-day consensus and no domain accountability, while baseline-only selections have domain accountability and weaker long-window consensus. Operator independence, entity continuity, and concentration lift are undecidable from these rows because all 10 disagreement rows lack country/asn/operator-continuity fields.

## Disagreement Table

| Validator | Direction | Domain | 30d agreement | Model | Baseline | Adjudication |
|---|---|---|---:|---:|---:|---|
| `v009` | baseline-only | pft.g.money | 0.99367 | 81 | 75 | not_proven_without_external_label_or_policy_choice |
| `v012` | model-only | - | 0.99840 | 83 | 71 | not_proven_without_external_label_or_policy_choice |
| `v015` | baseline-only | pft.xbtseal.com | 0.99359 | 81 | 78 | not_proven_without_external_label_or_policy_choice |
| `v017` | model-only | - | 0.99758 | 82 | 71 | not_proven_without_external_label_or_policy_choice |
| `v022` | model-only | - | 0.99821 | 83 | 71 | not_proven_without_external_label_or_policy_choice |
| `v023` | model-only | - | 0.99824 | 83 | 71 | not_proven_without_external_label_or_policy_choice |
| `v026` | baseline-only | pft.akirax.xyz | 0.99407 | 81 | 75 | not_proven_without_external_label_or_policy_choice |
| `v028` | baseline-only | postfiat.nlh.xyz | 0.99165 | 81 | 74 | not_proven_without_external_label_or_policy_choice |
| `v029` | model-only | - | 0.99619 | 82 | 71 | not_proven_without_external_label_or_policy_choice |
| `v037` | baseline-only | pfthaploid.com | 0.99617 | 82 | 75 | not_proven_without_external_label_or_policy_choice |

## Whitepaper-Safe Claim

A defensible claim from this packet is limited to: the model-lift benchmark produced repeatable, auditable boundary disagreements, and adjudication shows those disagreements are policy tradeoffs under the current snapshot rather than proven model lift. The packet strengthens the case for auditable disagreement review and richer evidence schemas; it does not prove model superiority.
