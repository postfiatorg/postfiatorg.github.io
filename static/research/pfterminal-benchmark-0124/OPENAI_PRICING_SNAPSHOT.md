# OpenAI pricing snapshot

Captured: 2026-07-28 UTC

Official sources:

- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/docs/guides/image-generation

## GPT Image 2

Standard token prices per million:

| Modality | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| Image | $8.00 | $2.00 | $30.00 |
| Text | $5.00 | $1.25 | — |

Official example output-cost estimates:

| Quality | 1024×1024 | 1024×1536 | 1536×1024 |
| --- | ---: | ---: | ---: |
| Low | $0.006 | $0.005 | $0.005 |
| Medium | $0.053 | $0.041 | $0.041 |
| High | $0.211 | $0.165 | $0.165 |

These examples cover image output. Text prompt input tokens are additional.
The benchmark reports image generation separately from the contestant coding
model and from neutral-judge overhead.

## GPT-5.6-Sol judge

Standard short-context prices per million:

| Input | Cached input | Cache write | Output |
| ---: | ---: | ---: | ---: |
| $5.00 | $0.50 | $6.25 | $30.00 |

Judge cost is experiment overhead and is never assigned to either contestant.
