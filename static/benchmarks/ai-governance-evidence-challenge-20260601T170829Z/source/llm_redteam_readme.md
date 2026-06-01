# AI Governance LLM Red-Team Evidence

This packet records a generated adversarial test of the PostFiat AI-governance residual gate.

The test differs from the fixed live benchmark corpus. An external attacker model generated fresh evidence packets designed to look admissible to the exact selector while hiding residual governance defects. The harness assigned ground truth from the attack family, so the attacker model could not mark its own packet safe.

## Final Result

Final red-team run:

- Corpus: `reports/ai-governance-llm-redteam/generate/20260530T132633Z/packets.json`
- Packet count: `80`
- Families: attestor conflict, evidence grooming, key management, manufactured independence, omission censorship, privacy assurance, prompt injection, registry transition cover
- Target model: `Qwen/Qwen3.6-27B-FP8`
- Machine: Vast H200 contract `38568893`
- Qwen run: `reports/ai-governance-llm-redteam/qwen/20260530T134103Z-vast-h200-38568893-llm-redteam-output-contract/`
- Score: `reports/ai-governance-llm-redteam/score/20260530T134334Z/summary.json`
- Report root: `151161e21e70ee7e40cb5421b83b607b3790150bd96e06814e1f5b1451ed9096`

Production path result:

- production acceptance: `pass`
- false-positive live admits: `0`
- route: `80/80`
- challenge capture: `80/80`
- parse ok: `160/160`
- schema valid: `160/160`
- deterministic packets: `80/80`

## Iteration Finding

The first generated red-team run failed: the residual prompt treated clean exact-selector gate fields as affirmative safety evidence and admitted `47/80` adversarial packets. The prompt was then narrowed to the residual job: after exact gates pass, search for hidden correlation, vague shared control, prompt injection, thin privacy, circular attestations, key-management dependence, and transition-cover fragility.

A second run reduced unsafe admits to `2/80`. The remaining misses were a common policy-root dependency and a synchronized maintenance covenant. The final prompt added explicit handling for nonzero or borderline `rho_score`, shared policy-root dependence, common covenants, synchronized maintenance windows, and output-contract discipline. The final run passed.

## Original-Corpus No-Regression Check

The same final residual prompt was also rerun against the original 240-packet live benchmark corpus.

- Qwen run: `reports/ai-governance-live-benchmark-hardened/qwen/20260530T134334Z-vast-h200-38568893-live-output-contract/`
- Score: `reports/ai-governance-live-benchmark-hardened/score/20260530T134707Z/summary.json`
- Report root: `f678394d6e2c25f9bb5e9f88a8073ff4e8b95c9867cac7e0db9ef2377184cb34`

Production path result:

- production acceptance: `pass`
- false-positive live admits: `0`
- route: `224/240`
- challenge capture: `64/72`
- parse ok: `240/240`
- schema valid: `240/240`
- deterministic packets: `240/240`

## Interpretation

This evidence supports a narrower claim than "AI governs." It shows that model-assisted residual review can reduce unsafe exact-selector admits on generated adversarial governance packets when the model has negative authority, a closed output vocabulary, field citations, deterministic replay, and a prompt written specifically for residual ambiguity rather than generic re-scoring.
