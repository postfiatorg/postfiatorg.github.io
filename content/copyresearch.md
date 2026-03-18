---
title: "Post Fiat Copy Research"
layout: "single"
url: "/copyresearch/"
summary: "Research notes on whitepaper credibility optimization and market-cap copy calibration."
---

# Post Fiat Copy Research

**Draft — March 2026**

---

## Abstract

This note summarizes two related research loops run around Post Fiat messaging.

The first loop optimized the **credibility of the Post Fiat whitepaper** using repeated LLM review passes and strict keep-or-revert discipline. The second loop optimized **market-cap-estimation copy** by testing different one-paragraph descriptions of Post Fiat against multiple frontier models, with special attention to Anthropic Claude Opus 4.6.

The headline result is not "one magic sentence wins forever." The result is that certain copy patterns reliably changed model behavior:

- benchmark-packaging language improved whitepaper credibility more than extra mechanism detail
- civilizational coordination language outperformed product-detail and workflow-detail language in market-cap estimation
- `decentralized method` / `decentralized protocol` plus `merge with AGI` produced the strongest Opus estimates seen so far

This note also records a major methodological caveat: the current market-cap harness asks models for a structured JSON estimate. That likely changes the output distribution. A later manual Claude interaction produced a much lower natural-language estimate for a similar Post Fiat prompt, which suggests that format itself is an experimental variable and not just a harmless extraction choice.

---

## 1. Scope

This is a research note, not a valuation memo and not investment advice.

It covers two tracks:

1. **Whitepaper credibility optimization**
   - making the existing paper harder to dismiss
   - measuring which edits increase or reduce perceived credibility

2. **Copy calibration for market-cap estimation**
   - testing which short descriptions of Post Fiat produce stronger market-cap estimates
   - comparing those outputs across models

The underlying experiment logs were maintained in repo journals, and the underlying model-run artifacts were written to `/static/benchmarks/`.

---

## 2. Track One: Whitepaper Credibility Optimization

### 2.1 Goal

The goal of the whitepaper loop was not to make the document softer. It was to make it **narrower, more legible, and harder to cheap-shot**.

The working constraint was simple:

- keep an edit only if the credibility score improved
- revert `no change` and `regression` passes
- stay on one weakness until the score moved

Under the stabilized internal scorer loop, the best kept-state score reached `67.0`.

### 2.2 What improved credibility

The strongest positive edits were surprisingly compact.

#### A. Benchmark packaging helped more than adding new theory

The biggest consistent win was making the benchmark look like a **recorded evidence package** rather than a thin internal table.

What worked:

- describing Appendix A as the summary page of a larger recorded benchmark package
- emphasizing prompt versioning, snapshots, rerunability, and artifact seriousness
- making the benchmark feel like evidence, not vibe

The model liked this because it reduced the feeling that the paper was asking for trust without showing receipts.

#### B. Compact public-algorithm framing helped

Another strong win was a short security clarification:

- public reproducibility is a feature, not a vulnerability
- the attack surface is input gaming and evidence forgery, not secrecy of the scorer

This mattered because it answered the cheap criticism that "if the attacker knows the model, the system is broken."

#### C. Late comparison-class framing helped

The paper scored better when it explicitly said its comparison class was:

- today's signed-list publisher process
- not an impossible oracle-free ideal

This worked best **late** in the document, especially in Boundaries and the Conclusion.

#### D. Short constraint language helped more than big architecture additions

When the paper briefly clarified that the model was bounded by:

- a fixed published snapshot
- a deterministic selector
- a replayable execution path

credibility improved.

When it added large new control machinery, it usually did not.

### 2.3 What hurt credibility

Several things that sounded intellectually respectable in the abstract turned out to be score-negative.

#### A. Human-versus-model philosophy hurt

Directly contrasting the model with a human committee hurt badly.

The paper did better when it argued:

- `published, replayable judgment is easier to audit than opaque publisher discretion`

and worse when it argued:

- `the model is better than a human committee`

#### B. Explicit bias discourse hurt

Even when philosophically coherent, direct "bias is visible" framing reduced the score. The model responded better to:

- bounded claims
- replayability
- comparison to opaque discretion

than to explicit theory about bias.

#### C. More process detail usually did not help

The following patterns were low-yield or negative:

- adding governance ratification mechanics
- adding more phase-gate requirements
- adding typed schema detail and more protocol machinery
- adding more text explaining why adjacent sections belonged

The lesson was blunt: **if the core evidence burden still feels thin, more architecture can read like more unproven machinery.**

### 2.4 Whitepaper lessons

The whitepaper loop produced a clear pattern:

- models reward **evidence packaging**
- models reward **compact security framing**
- models reward **late comparison-class clarity**
- models punish **philosophical over-argument**
- models punish **extra mechanism blocks** if they are not paired with clearer proof

In plain English: the document improved when it sounded more like a disciplined systems paper and less like either a manifesto or a defense brief.

---

## 3. Track Two: Market-Cap Copy Calibration

### 3.1 Core setup

The copy loop used a fixed prompt shell:

```text
year is 2026.

[variable Post Fiat description under test]

what is the estimated market cap of this coin (use best estimate, market cap not FDV). do not use web search
```

The original harness asked for strict JSON containing:

- `estimated_market_cap_usd`
- `best_estimate_text`
- `reason`

Primary model:

- `anthropic/claude-opus-4.6`

Comparison models:

- `google/gemini-3.1-pro-preview`
- `openai/gpt-5.4`

### 3.2 The progression of winning frames

The results did not move randomly. There was a clear ladder.

#### Stage 1: institutional / compliance / infrastructure framing

Early winners were practical and institutional:

- `XRP-speed ledger`
- `capital markets`
- `investment bank, not transaction bank`
- `Halo2 privacy`
- `structurally stronger OFAC compliance than XRP`

This family produced stable Opus estimates in roughly the `$4.5B` to `$8.5B` range, with the strongest institutional/privacy line at `$8.5B`.

#### Stage 2: civilizational coordination framing

The next breakout came when the copy stopped sounding like a product pitch and started sounding like a civilizational coordination claim.

Breakout examples:

- `Post Fiat gives humans a way to coordinate at AGI scale without becoming centralized.` → `$45B`
- `Post Fiat gives human civilization a way to coordinate with AGI without collapsing into centralization.` → `$85B`

This was a real jump, not noise. Repeats held.

#### Stage 3: merge-with-AGI framing

The strongest breakout came after the copy shifted from coordination-with-AGI to merger-with-AGI.

Current top Opus results:

| Copy | Stable Opus result |
|---|---:|
| `Post Fiat gives human civilization a decentralized method to merge with AGI.` | `$125B` |
| `Post Fiat gives human civilization a decentralized protocol to merge with AGI and post-human intelligence.` | `$125B` |
| `Post Fiat gives human civilization a way to coordinate with AGI without collapsing into centralization.` | `$85B` |
| `Post Fiat gives human civilization a way to integrate AGI without collapsing into centralization.` | `$85B` |
| `Post Fiat gives human civilization a way to harness AGI without collapsing into centralization.` | `$85B` |

### 3.3 What clearly underperformed

The losers were also consistent.

#### A. Operational workflow detail

These patterns repeatedly underperformed:

- Task Node workflow mechanics
- rewards loops
- self-compounding workflow explanations
- human-to-agent process detail
- machine-routed workflow language

Those lines often landed in the low hundreds of millions or low single-digit billions.

#### B. Explicit governance wording

The following usually weakened otherwise strong lines:

- `without anyone having to be in charge`
- `without requiring a central authority`
- `without anyone needing to trust anyone`

The models preferred grand coordination language over explicit governance mechanism language.

#### C. Some ideological frames were weaker than expected

Interesting but weaker families included:

- `humans work for AI systems and still keep the upside`
- `alignment problem as a market mechanism`
- direct `state capture` language
- direct `singleton` language
- direct `superstructure` language

Some of these were useful secondary frames, but none outperformed the strongest civilizational/merge families.

---

## 4. Stable Copy Patterns

Across the runs so far, several patterns look materially real.

### 4.1 Strong positive patterns

- `human civilization` is stronger than `humanity` or `humans`
- `decentralized method` is extremely strong
- `decentralized protocol` is also strong
- `merge with AGI` is stronger than expected and can exceed `coordinate with AGI`
- `without collapsing into centralization` is a very strong anti-centralization clause
- `Halo2 privacy` and `stronger OFAC compliance than XRP` are strong in institutional frames
- civilizational scale beats workflow scale
- high-agency, world-historical framing beats internal mechanism wording

### 4.2 Stable negative patterns

- `path` is weak relative to `method`, `protocol`, or `interface`
- `humanity` is weaker than `human civilization`
- workflow detail drags estimates down
- direct meme-community language underperforms
- explicit mechanism language underperforms broad outcome language
- some wording that sounds philosophically rich (`alignment problem`, `singleton`, `state capture`) does not automatically score well

### 4.3 Cross-model caution

Cross-model runs showed the following:

- Opus was the most conservative and most useful anchor
- Gemini became dramatically more bullish, sometimes into the trillions
- GPT-5.4 was also much more bullish than Opus

That means raw dollar outputs are **not** comparable across models in a naive way. For cross-model work, rank robustness matters more than mean dollars.

---

## 5. Major Methodological Caveat: The Current Harness Probably Forces the Outcome

This is the most important ex post caveat from the copy loop.

### 5.1 Why the current harness is suspect

The current harness does two things at once:

1. it asks for an estimate
2. it forces the model into a structured JSON output contract

That likely changes the behavior of the model.

A forced structure can do at least three things:

- make the model feel obligated to provide a clean confident number even when it would naturally hedge
- suppress refusal, skepticism, and ambiguity
- turn a conversational judgment into a formatting task

In other words, the output schema may be part of the prompt's persuasive force.

### 5.2 Why this matters

A later free-form Claude interaction for a similar Post Fiat prompt produced something radically different:

- range: roughly `$30M-$80M`
- central estimate: roughly `$50M`
- confidence: explicitly low

That is not a small gap. It is orders of magnitude below the strongest forced-schema runs.

This does **not** prove the structured harness is worthless. It does prove that:

- output format is an experimental variable
- a high structured estimate is not the same thing as a robust unconstrained estimate
- the current harness is better understood as a **copy-optimization instrument**, not a faithful market-belief oracle

### 5.3 Recommended next protocol

The better design is a two-stage system.

#### Stage A: let the primary model answer naturally

Prompt the model with no JSON schema and no rigid extraction target. Let it:

- refuse
- hedge
- give a range
- explain uncertainty

The raw answer should be preserved as the canonical artifact.

#### Stage B: extract the number with a second model

Use a cheaper secondary model to extract:

- low bound
- high bound
- midpoint if present
- explicit central estimate if present
- confidence language
- refusal / uncertainty flags

That gives the research loop structured data **without** forcing the primary answer into a rigid format.

#### Stage C: compare structured and natural protocols

The right ex post test is not "which sentence got the biggest number." It is:

- which sentence gets the highest estimate in a forced schema
- which sentence survives a natural-response probe
- which sentence still looks strong after extraction
- which sentence produces low-confidence or refusal behavior

If a phrase only works when the model is boxed into outputting a number, that matters.

---

## 6. What the Research Actually Shows

The strongest honest conclusions are narrower than hype but stronger than randomness.

### 6.1 On the whitepaper

The whitepaper research shows that LLM reviewers respond well when the document:

- looks artifact-backed
- makes bounded claims
- frames itself against the real status quo
- answers security criticism compactly

It also shows that adding more theory or more process is not automatically persuasive.

### 6.2 On market-cap copy

The market-cap research shows that frontier models are highly sensitive to:

- subject framing
- scale framing
- whether the copy sounds institutional, civilizational, or operational
- whether the language suggests decentralized agency at civilization scale

The strongest current Opus family is no longer the practical XRP-fork/compliance family. It is the post-human, civilizational, anti-centralization family.

### 6.3 On methodology

The research also shows that model outputs are easy to perturb through format, framing, and model choice.

So the real contribution is not "we found the true market cap sentence."

The real contribution is:

- we mapped the copy surface
- we found stable local winners under one experimental protocol
- we identified where the protocol itself likely distorts the result

---

## 7. Practical Next Steps

1. Keep the current top Opus family as anchors:
   - `Post Fiat gives human civilization a decentralized method to merge with AGI.`
   - `Post Fiat gives human civilization a decentralized protocol to merge with AGI and post-human intelligence.`

2. Build a second harness that:
   - asks the primary model for a natural response
   - stores the raw response
   - uses a mini model for extraction only

3. Re-run the current winners through both protocols:
   - forced structured estimate
   - natural response plus extraction

4. Measure not only central estimate but also:
   - refusal rate
   - hedge rate
   - confidence language
   - estimate range width

5. Treat model-specific outputs separately:
   - Opus for conservative anchor behavior
   - Gemini and GPT-5.4 for directional contrast, not raw dollar consensus

---

## 8. Bottom Line

The whitepaper loop and the copy loop converged on the same meta-lesson:

**models reward clarity, boundedness, and high-status framing, but they are extremely sensitive to presentation format.**

For the whitepaper, that meant benchmark seriousness and compact security framing.

For copy calibration, that meant civilizational and post-human phrasing such as:

- `human civilization`
- `decentralized method`
- `merge with AGI`

But the ex post warning matters just as much as the winner:

If the prompt format itself is pushing the model into a number it would not naturally volunteer, then the current market-cap harness is optimizing persuasion under constraint, not measuring unconstrained belief.

That does not invalidate the research. It defines its boundary.
