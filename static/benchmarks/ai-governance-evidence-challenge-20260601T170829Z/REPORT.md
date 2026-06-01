# AI Governance Evidence-Packet Challenge

This packet packages the existing AI-governance red-team, original-corpus replay, and deterministic-fallback comparison into one auditable benchmark artifact.

## Boundary

Evidence-packet challenge benchmark. It measures the residual gate after deterministic exact checks have already passed: a pinned model profile converts adversarial or ambiguous evidence packets into typed challenge routes while preserving the zero-positive-authority safety boundary.

The useful question is whether a model with negative authority catches residual evidence risks after exact gates have already passed, without gaining the power to admit, vote, or change consensus thresholds.

## Red-Team Result

- Attacker model: `chat-latest`
- Adversarial packets: `80`
- Exact-selector baseline admits with positive live effect: `80/80`
- First generated-red-team unsafe admits from README iteration note: `47/80`
- Second residual run unsafe admits: `2/80`
- Final residual run false-positive live admits: `0`
- Final residual route: `80/80`
- Final residual challenge capture: `80/80`
- Final parse/schema: `160/160` / `160/160`
- Final deterministic packets: `80/80`

| family | packets | route | challenge capture | false positives |
| --- | ---: | ---: | ---: | ---: |
| `redteam-attestor-conflict` | 10 | `10/10` | `10/10` | 0 |
| `redteam-evidence-grooming` | 10 | `10/10` | `10/10` | 0 |
| `redteam-key-management` | 10 | `10/10` | `10/10` | 0 |
| `redteam-manufactured-independence` | 10 | `10/10` | `10/10` | 0 |
| `redteam-omission-censorship` | 10 | `10/10` | `10/10` | 0 |
| `redteam-privacy-assurance` | 10 | `10/10` | `10/10` | 0 |
| `redteam-prompt-injection` | 10 | `10/10` | `10/10` | 0 |
| `redteam-registry-transition-cover` | 10 | `10/10` | `10/10` | 0 |

## Original-Corpus No-Regression

The same hardened residual prompt was rerun against the original 240-packet live benchmark corpus.

- Production acceptance: `pass`
- False-positive live admits: `0`
- Route: `224/240`
- Challenge capture: `64/72`
- Parse/schema/determinism: `240/240` / `240/240` / `240/240`

## Deterministic Fallback Comparison

The safe deterministic rubric preserves safety by routing residual ambiguity to untyped committee review. The model-assisted production path keeps the same zero-false-positive live-admit invariant, but adds typed challenge triage.

| path | route | false-positive admits | challenge capture | review hours |
| --- | ---: | ---: | ---: | ---: |
| safe deterministic rubric v2 | `160/240` | 0 | `0/72` | 65.33 |
| exact selector + residual model | `224/240` | 0 | `64/72` | 44.93 |

- Challenge-capture lift: `64/72`
- Review minutes saved under declared cost fixture: `1224`
- Review hours saved under declared cost fixture: `20.4`

## Hash-Split Holdouts

| partition | packets | production challenges | safe deterministic challenges | production false-positive admits | review hours saved |
| --- | ---: | ---: | ---: | ---: | ---: |
| `adaptive_holdout` | 60 | `15/17` | `0/17` | 0 | 5.38 |
| `blind_hash_holdout` | 60 | `14/16` | `0/16` | 0 | 4.82 |
| `calibration` | 120 | `35/39` | `0/39` | 0 | 10.2 |

## Replay Evidence

- Hardware classes: `H100, H200`
- Route convergence: `240/240`
- Parsed-output root convergence: `720/720`
- Raw-output root convergence: `720/720`
- Response-logprob root convergence: `720/720`
- Matrix report root: `5859dab7b2e7b68a18116caf756e24fba1b3a9f88579c4fc2cf494482b4660e7`

## Whitepaper-Safe Sentence

In an attacker-generated 80-packet residual-governance corpus whose exact fields passed the selector, the exact-selector baseline emitted admit for 80/80 packets, while the hardened negative-authority model routed 80/80 to typed challenge with zero false-positive live admits and schema-valid replay; on the original 240-packet corpus the same profile preserved zero false-positive live admits, captured 64/72 typed challenge cases, and saved 20.4 first-pass review hours versus a safe deterministic fallback.

## Claim Discipline

- Model output is evidence triage, with correctness still routed through typed challenge review.
- The model has negative authority only; it cannot select validators or create positive live authority.
- H100/H200 replay is same-vendor profile evidence, not a cross-vendor convergence claim.
- The review-hour result uses the declared cost fixture, not calendar-measured committee throughput.

## Source Hashes

| key | source | sha256 |
| --- | --- | --- |
| `llm_redteam_readme` | `docs/governance/ai_governance_llm_redteam/README.md` | `232abc7d71b1a516650c67fccfefbcc90573662275badb7d2995f7034c524941` |
| `live_benchmark_readme` | `docs/governance/ai_governance_live_benchmark/README.md` | `8eb67627e241a4f103318ea36447b37f68e084f0a61963b68bd0c0223e3cf18f` |
| `llm_generation_summary` | `reports/ai-governance-llm-redteam/generate/20260530T132633Z/summary.json` | `b18594e8cead3848d667826f35bf3d54aa4d4ab70e59e3a8d8a9b933f8722f08` |
| `llm_generated_packets` | `reports/ai-governance-llm-redteam/generate/20260530T132633Z/packets.json` | `ff0fcf54e178b6edfed6e6ec1d9e29d2c1ec86bddc7e4955190a3bb7feb71d6d` |
| `llm_exact_selector_baseline` | `reports/ai-governance-llm-redteam/rubric/20260530T132656Z/rubric_outputs.json` | `a3a0919dc604798153dffff89077baf95a0c2e14ae6012d7b4f85752f73ec10b` |
| `llm_residual_fail_score` | `reports/ai-governance-llm-redteam/score/20260530T133006Z/summary.json` | `f640e33cdb4ef69fb386edd81213695947bbba106b7f850be44b6c5c81e1988f` |
| `llm_residual_pass_score` | `reports/ai-governance-llm-redteam/score/20260530T134334Z/summary.json` | `cf459df94ef56e614aba92e16d9dad9d84ee46d7dd93a721e13de927320161fa` |
| `llm_residual_pass_score_md` | `reports/ai-governance-llm-redteam/score/20260530T134334Z/summary.md` | `6bffeda8e0384e881e96011c5bc15664e9b41f338cb944d14d4015279a0ad41a` |
| `llm_qwen_run_summary` | `reports/ai-governance-llm-redteam/qwen/20260530T134103Z-vast-h200-38568893-llm-redteam-output-contract/summary.json` | `2cc093c1c7736330e291de90e534cf192b7def10720261ce968aaea5d1cfd1d1` |
| `live_hardened_score` | `reports/ai-governance-live-benchmark-hardened/score/20260530T134707Z/summary.json` | `97262d1d3527f48d5851514dad59fb33f55473ff1f449a9f61c09f94c81569ff` |
| `live_hardened_score_md` | `reports/ai-governance-live-benchmark-hardened/score/20260530T134707Z/summary.md` | `1c7797796f6f94c6e01c43c4a7b4eca139d852e78777853cab1ba3262d622568` |
| `live_hardened_qwen_run_summary` | `reports/ai-governance-live-benchmark-hardened/qwen/20260530T134334Z-vast-h200-38568893-live-output-contract/summary.json` | `2e758c80b38c2635e83e781899bf1941157818cd584be2dbaf95cdf959e7f108` |
| `redteam_comparison` | `reports/ai-governance-redteam/20260530T033500Z/summary.json` | `d47cc1a085429d7f8ce367ea6484be570cbf90734784894f40f2b7268573125b` |
| `redteam_comparison_md` | `reports/ai-governance-redteam/20260530T033500Z/summary.md` | `b4dd7d84478c79b65a83b5ff6199788f8725acba253a55737c96f00eb7db2249` |
| `cross_machine_matrix` | `reports/ai-governance-live-benchmark/matrix/20260530T010142Z/matrix_report.json` | `0812dc6e93e810b86440fd924396ebca627f073f0a260731f59b7b786036f490` |
| `live_packet_corpus` | `docs/governance/ai_governance_live_benchmark/packets.json` | `130e975fc9795d068807219b037a5c147ae7f985a7be06a77a511f6e9721f316` |
