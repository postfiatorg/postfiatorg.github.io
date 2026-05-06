# Whitepaper Score Lab Book

This lab book tracks whitepaper optimization experiments using the OpenRouter judge pair:

- `anthropic/claude-opus-4.7`
- `openai/gpt-5.5`

## Scoring Rule

Each candidate is scored with 3 independent calls per judge model, for 6 total judge calls per candidate. Calls run asynchronously through `scripts/whitepaper_appeal_score_openrouter.py`.

The comparison metric is `aggregate_model_mean_score`, which averages the per-model means. This keeps Opus and GPT-5.5 equally weighted even if a future run changes repeat counts.

Decision rule:

- Keep a whitepaper change only if `aggregate_model_mean_score` improves versus the current kept baseline.
- If the score is flat or lower, revert the candidate whitepaper change.
- Record the hypothesis, artifact path, score, cost, and keep/revert decision here.

## Current Kept Baseline

- Production source: `content/whitepaper.md`
- Draft farm: `docs/whitepaper_drafts/`
- Artifact: `static/benchmarks/postfiat-whitepaper-appeal-draft-v1_black_box_procedure-20260505T215343Z-summary.json`
- Aggregate model-mean score: `85.67`
- Opus 4.7 mean: `87.67` from scores `[87, 88, 88]`
- GPT-5.5 mean: `83.67` from scores `[84, 83, 84]`
- Known OpenRouter cost: `$0.612492`
- Decision: promoted from draft to production. New baseline for future drafts.

## Experiments

### 2026-05-05 Candidate 1 - Executive framing and model-layer rationale

- Hypothesis: the score should improve if the paper front-loads the practical stakes, makes the model-vs-rubric rationale more affirmative, and gives a clearer reason this belongs in Post Fiat rather than as an XRPL-side publisher plugin.
- Candidate artifact: `static/benchmarks/postfiat-whitepaper-appeal-20260505T212419Z-summary.json`
- Aggregate model-mean score: `85.5`
- Opus 4.7 mean: `87.0` from scores `[87, 87, 87]`
- GPT-5.5 mean: `84.0` from scores `[84, 84, 84]`
- Known OpenRouter cost: `$0.645735`
- Decision: kept. Improved versus prior kept baseline `84.5`.

### 2026-05-05 Candidate 2 - Network and PFT thesis tightening

- Hypothesis: the score should improve if Section 11.4 removes hedged value-language and gives concrete structural differences between an advisory XRPL plugin and a native Post Fiat governance surface.
- Candidate artifact: `static/benchmarks/postfiat-whitepaper-appeal-20260505T212544Z-summary.json`
- Aggregate model-mean score: `84.83`
- Opus 4.7 mean: `86.33` from scores `[86, 87, 86]`
- GPT-5.5 mean: `83.33` from scores `[84, 84, 82]`
- Known OpenRouter cost: `$0.532164`
- Decision: reverted. Failed versus kept baseline `85.5`.

### 2026-05-05 Candidate 3 - Comparative-procedure sentence in executive summary

- Hypothesis: the score should improve if the executive summary explicitly says the relevant comparison is published, replayable, challengeable judgment versus unpublished publisher discretion.
- Candidate artifact: `static/benchmarks/postfiat-whitepaper-appeal-20260505T214546Z-summary.json`
- Aggregate model-mean score: `85.33`
- Opus 4.7 mean: `87.33` from scores `[88, 87, 87]`
- GPT-5.5 mean: `83.33` from scores `[84, 82, 84]`
- Known OpenRouter cost: `$0.608222`
- Decision: reverted. Failed versus kept baseline `85.5`.

### 2026-05-05 Candidate 4 - Public-artifacts sentence in Section 2.5

- Hypothesis: the score should improve if Section 2.5 says qualitative judgment should be forced into public artifacts rather than left in publisher discretion.
- Candidate artifact: `static/benchmarks/postfiat-whitepaper-appeal-20260505T214704Z-summary.json`
- Aggregate model-mean score: `83.83`
- Opus 4.7 mean: `86.33` from scores `[86, 87, 86]`
- GPT-5.5 mean: `81.33` from scores `[83, 83, 78]`
- Known OpenRouter cost: `$0.600222`
- Decision: reverted. Failed versus kept baseline `85.5`.

### 2026-05-05 Candidate 5 - Baseline controls are not blockers

- Hypothesis: the score should improve if Section 2.5 says deterministic and human baselines are future controls, not objections to publishing model-assisted judgment now.
- Candidate artifact: `static/benchmarks/postfiat-whitepaper-appeal-20260505T214845Z-summary.json`
- Aggregate model-mean score: `84.66`
- Opus 4.7 mean: `86.33` from scores `[86, 86, 87]`
- GPT-5.5 mean: `83.0` from scores `[83, 84, 82]`
- Known OpenRouter cost: `$0.595032`
- Decision: reverted. Failed versus kept baseline `85.5`.

### 2026-05-05 Draft Farm Batch 1 - Five uncorrelated drafts

- Process change: production remained at `content/whitepaper.md`; five isolated candidates were generated under `docs/whitepaper_drafts/` and scored as draft inputs. Only the winning draft was promoted.
- Production score to beat: `85.5`.

| Draft | Hypothesis | Score | Opus mean | GPT-5.5 mean | Decision |
|---|---|---:|---:|---:|---|
| `v1_black_box_procedure.md` | Steelman "one black box to another" and answer with decomposable public procedure | `85.67` | `87.67` | `83.67` | Promoted |
| `v2_baseline_control_not_blocker.md` | Reframe deterministic baselines as future controls rather than blockers | `85.34` | `87.0` | `83.67` | Rejected |
| `v3_high_stakes_trust_boundary.md` | Add high-stakes trust-boundary language to executive summary | `84.66` | `87.0` | `82.33` | Rejected |
| `v4_governance_controls.md` | Add governance controls section | `84.66` | `86.0` | `83.33` | Rejected |
| `v5_judicial_clerk.md` | Frame model as judicial clerk, not sovereign | `85.0` | `86.67` | `83.33` | Rejected |

- Winning artifact: `static/benchmarks/postfiat-whitepaper-appeal-draft-v1_black_box_procedure-20260505T215343Z-summary.json`
- Promoted production edit: one paragraph in Section 2.3 explicitly acknowledges black-box substitution risk and answers procedurally.

## Hypothesis Backlog

### H1 - Copy-Only Reframing of the Deterministic-Baseline Objection

- Source: Claude feedback after Appendix B removal.
- Constraint: do not claim a deterministic baseline has been run.
- Hypothesis: copy can improve if the paper reframes the missing deterministic-rubric baseline as the correct future falsification test while emphasizing that the present claim is narrower: published, replayable, challengeable qualitative judgment is already a procedural improvement over opaque publisher discretion.
- Testable edit: one or two sentences in Section 2.5 or the executive summary. Do not add tables, benchmark claims, or invented results.
- Expected scoring effect: high. This directly answers the repeated "why a model" objection from both Opus and GPT-5.5.
- Required work before edit: none, but any candidate must be scored and reverted unless it beats `85.5`.

### H2 - Add a Borderline Validator Case Study

- Source: repeated judge feedback plus Claude's deterministic-baseline objection.
- Hypothesis: one concrete disagreement case near the inclusion cutoff will make the model layer feel earned rather than decorative.
- Testable edit: show raw evidence, deterministic-rubric output, model rationale, selector output, and why the final decision is more contestable than closed human judgment.
- Expected scoring effect: medium-high. This may work even before a full deterministic-baseline benchmark if the example is real and tied to existing snapshot data.
- Required work before edit: identify an actual validator where simple metrics and model judgment diverge.

### H3 - Clarify Copying vs. Reproducibility

- Source: Claude feedback on Sections 8.2 and 9.2.
- Hypothesis: a short sentence acknowledging that perfect determinism makes "I reran it" and "I copied the canonical output" indistinguishable after publication will improve technical trust.
- Testable edit: update the commit-reveal section to say commit-reveal proves temporal independence before the canonical output is visible, but does not prove local execution after reveal.
- Expected scoring effect: low-medium. This is polish, but it addresses a real cryptographic/governance nuance.
- Required work before edit: none.

### H4 - Split Internal Artifact References

- Source: Claude feedback on reference density.
- Hypothesis: splitting broad internal implementation references into narrower citations will improve auditability optics and reduce "self-referential artifact" criticism.
- Testable edit: separate deployment scripts, scoring prompt/config, replay artifacts, and benchmark result references.
- Expected scoring effect: low-medium. Useful for formal polish, unlikely to beat H1.
- Required work before edit: inventory public paths and ensure every cited artifact is actually inspectable.

### H5 - Do Not Spend More Score Budget on Stale Smoke-Test Feedback

- Source: Claude feedback appears partly stale relative to the current whitepaper.
- Current status: the current conclusion says "two layers," not "three layers"; `smoke`, `6,960`, and the old multi-model suite are not present in the current whitepaper. Section 7.1 already says Qwen3.6 is active and Qwen3-Next is historical.
- Decision: do not run an edit on this unless those terms reappear in the source.
