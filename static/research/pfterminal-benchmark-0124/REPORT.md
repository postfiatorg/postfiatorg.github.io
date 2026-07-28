# PFTerminal 0.1.24 comprehensive benchmark

Cached paid agent spend currently attributed: **$60.7347**.
Observed GPT Image 2 output-cost lower-bound currently attributed: **$11.3300** (prompt input additional).
Neutral GPT-5.6-Sol judge overhead currently attributed: **$6.1174** across 18 passes.
Total currently attributable lower bound: **$78.1821** plus GPT Image 2 prompt input.

## Harness comparisons

| workload | cell | opponent | solves | speed ratio | agent cost ratio | agent savings | all-in* ratio | all-in* savings | consistency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| eventforge | glm-openrouter | hermes | 3/3 vs 3/3 | 1.466x | 2.918x | 65.73% | — | — | consistent_pft |
| eventforge | kimi-openrouter | hermes | 3/3 vs 2/3 | 1.140x | 1.408x | 29.00% | — | — | mixed_or_incomplete |
| queuecraft | glm-openrouter | hermes | 3/3 vs 3/3 | 1.111x | 1.060x | 5.71% | — | — | mixed_or_incomplete |
| queuecraft | glm-vercel | hermes | 3/3 vs 3/3 | 1.657x | 1.660x | 39.77% | — | — | consistent_pft |
| queuecraft | kimi-openrouter | hermes | 3/3 vs 3/3 | 4.232x | 5.247x | 80.94% | — | — | consistent_pft |
| visual_site | glm-openrouter | hermes | 3/3 vs 1/3 | 1.178x | 2.400x | 58.33% | — | — | mixed_or_incomplete |
| visual_site | kimi-openrouter | hermes | 3/3 vs 3/3 | 1.266x | 1.443x | 30.68% | 1.434x | 30.25% | mixed_or_incomplete |
| visual_site | opus | cc | 3/3 vs 2/3 | 1.743x | 2.318x | 56.86% | 2.101x | 52.40% | mixed_or_incomplete |

Ratios above 1.0 favor PFTerminal: opponent total divided by PFTerminal total. Failures remain in solve denominators and spend.
`all-in*` adds the official GPT Image 2 output estimate for every confirmed-output generation—including discarded attempts—to agent billing. Timed-out in-flight calls are retained as a separate upper bound; prompt input and neutral-judge overhead remain separate.

## Per-lane aggregates

| workload | cell | lane | solves | wall total | wall median | agent cost | image output est. | all-in* | cost / solve |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| eventforge | glm-openrouter | hermes | 3/3 | 1730.516 | 516.232 | $0.4397 | — | — | $0.1466 |
| eventforge | glm-openrouter | pft | 3/3 | 1180.345 | 265.688 | $0.1507 | — | — | $0.0502 |
| eventforge | kimi-openrouter | hermes | 2/3 | 1792.318 | 314.765 | $1.6060 | — | — | $0.8030 |
| eventforge | kimi-openrouter | pft | 3/3 | 1571.644 | 582.386 | $1.1403 | — | — | $0.3801 |
| queuecraft | glm-openrouter | hermes | 3/3 | 1063.555 | 288.692 | $1.0234 | — | — | $0.3411 |
| queuecraft | glm-openrouter | pft | 3/3 | 957.643 | 377.436 | $0.9650 | — | — | $0.3217 |
| queuecraft | glm-vercel | hermes | 3/3 | 790.371 | 304.641 | $1.7399 | — | — | $0.5800 |
| queuecraft | glm-vercel | pft | 3/3 | 476.914 | 158.720 | $1.0480 | — | — | $0.3493 |
| queuecraft | kimi-openrouter | hermes | 3/3 | 1844.472 | 705.385 | $4.8031 | — | — | $1.6010 |
| queuecraft | kimi-openrouter | pft | 3/3 | 435.786 | 143.329 | $0.9153 | — | — | $0.3051 |
| visual_site | glm-openrouter | hermes | 1/3 | 5366.347 | 1456.798 | $3.7412 | — | — | $3.7412 |
| visual_site | glm-openrouter | pft | 3/3 | 4554.221 | 1497.890 | $1.5591 | $2.6710 | $4.2301 | $0.5197 |
| visual_site | kimi-openrouter | hermes | 3/3 | 5622.937 | 1840.704 | $7.5700 | $1.9800 | $9.5500 | $2.5233 |
| visual_site | kimi-openrouter | pft | 3/3 | 4439.645 | 1546.911 | $5.2472 | $1.4140 | $6.6612 | $1.7491 |
| visual_site | opus | cc | 2/3 | 5337.666 | 1689.070 | $20.1103 | $1.6230 | $21.7333 | $10.0552 |
| visual_site | opus | pft | 3/3 | 3061.889 | 988.026 | $8.6756 | $1.6690 | $10.3446 | $2.8919 |

## Blind visual judgments

| cell | wave | model | verdict |
| --- | ---: | --- | --- |
| glm-openrouter | 1 | gpt-5.6-sol | pft |
| glm-openrouter | 2 | gpt-5.6-sol | tie_inconclusive_order_sensitive |
| glm-openrouter | 3 | gpt-5.6-sol | pft |
| kimi-openrouter | 1 | gpt-5.6-sol | pft |
| kimi-openrouter | 2 | gpt-5.6-sol | pft |
| kimi-openrouter | 3 | gpt-5.6-sol | pft |
| opus | 1 | gpt-5.6-sol | cc |
| opus | 2 | gpt-5.6-sol | pft |
| opus | 3 | gpt-5.6-sol | tie_inconclusive_order_sensitive |

Balanced-order wave tally:

| cell | opponent | PFT wins | opponent wins | inconclusive |
| --- | --- | ---: | ---: | ---: |
| glm-openrouter | hermes | 2 | 0 | 1 |
| kimi-openrouter | hermes | 3 | 0 | 0 |
| opus | cc | 1 | 1 | 1 |

## Conformance exclusions

The following runs remain in elapsed-time and spend totals but do not count as successful matched-route runs:
- `visual_site/glm-openrouter/hermes/wave2`: Hermes terminal isolation removed the supplied OPENAI_API_KEY. The agent generated final assets through the ChatGPT Codex OAuth backend using gpt-image-2-codex rather than the required OpenAI Image API gpt-image-2 route. Evidence: `visual/results/glm-openrouter/hermes/wave2/agent_run.json`.
- `visual_site/glm-openrouter/hermes/wave3`: Hermes terminal isolation removed the supplied OPENAI_API_KEY. The agent generated final assets through a discovered Vercel AI Gateway credential rather than the matched direct OpenAI Image API route. Evidence: `visual/results/glm-openrouter/hermes/wave3/agent_run.json`.

## Interpretation guardrails

- Three waves establish replication, not statistical significance.
- `consistent` requires the same directional speed result in all three waves.
- Provider billing deltas are primary; token-price reconstructions are diagnostic.
- Image attempt audits override final manifests when traces prove additional billed generations; otherwise the final manifest is a documented lower bound.
- An image request whose client timed out without a response is not asserted as free or billed: its possible output cost appears only in the upper bound.
- Website quality is a winner only when balanced A/B orders agree.
