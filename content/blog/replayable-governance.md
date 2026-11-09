---
title: "Replayable Governance"
date: 2026-11-09T00:00:00Z
draft: true
summary: "Post Fiat is running an experiment in algorithmic governance: the decisions that advance the network go to a pinned model, every exchange is published, and anyone can replay the answers byte for byte."
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Governance
  - Replay
  - DeepSeek
---

Post Fiat is running an experiment in algorithmic governance. The decisions that advance the network go to a pinned AI model in public: what to build next, how to use the treasury, when to launch the token. Every question, answer and challenge is logged, and anyone can replay the model's answers byte for byte.

## The problem

Every crypto network is governed by a committee, whether it admits it or keeps quiet about it. Bitcoin changes through the maintainers of Bitcoin Core, Ethereum through its core developers, and the XRP Ledger through validators following lists published by a handful of organizations.

The decisions that move a token's value usually sit one level higher, inside the companies and foundations around a chain. In 2025 Ripple agreed to acquire the prime broker Hidden Road for $1.25 billion. That decision carried heavy implications for XRP, and XRP holders had no visibility into it: no published reasoning, no record of the alternatives considered, and no way to contest it. Treasury sales, ecosystem funds and roadmap bets across the market follow the same pattern.

## The experiment

Post Fiat runs its strategic decisions through a public process:

1. The operator submits the question and the facts behind it.
2. A pinned model answers: DeepSeek V4.1 Flash, at a fixed revision, with fixed settings and a fixed seed.
3. The operator challenges the answer, and the model revises it.
4. Every submission, answer and challenge goes into a hash-chained log, published with the receipts needed to replay it.

Model inference usually varies from run to run. We run the model on [DeepInfer](https://github.com/deepseek-ai/DeepInfer), DeepSeek's open-source inference runtime, with batch-invariant kernels, so the same input produces the same output bytes on independent machines. A pair of four-GPU machines costs about $65 an hour and is ready in about 11 minutes.

[![How deterministic replay works across runs: ordinary inference drifts because batches change the order of arithmetic; Post Fiat pins the model, runtime, batch-invariant kernels, seed and prompt, so two machines and eight GPUs return identical bytes, published with receipts and a verifier.](/blog/replayable-governance-determinism.svg)](https://github.com/deepseek-ai/DeepInfer)

## Why it works

**Anyone can check the record.** A committee transcript records what people said, and nobody can re-run the people. A pinned model can be re-run. Stakeholders can feed the published inputs to the same configuration and get the same answer, instead of trusting the operator's account.

**Steering becomes visible.** Models sometimes produce bad answers, and someone has to correct them. Here every correction is part of the record. Stakeholders can read what the operator pushed on and what the model changed, and judge whether each change followed an argument or simple pressure. A committee lobbies in private; on Post Fiat the steering is the published artifact.

**The process creates a compliance loop.** The model recommends, and subsequent decisions and public evidence show whether the operator followed the recommendation. Community members, stakeholders and counterparties can judge over time whether the actors behave in good faith. Early runs say little on their own, but the evidence compounds, and every decision followed or departed from sharpens the picture.

**It improves on two axes.** Strong exchanges become precedent in a versioned constitution that future decisions must cite, and the models applying it get better every year. The models we use today are the weakest we will ever use.

## Decision correctness

Over time, this system posits that a transparent, iterative and replayable process will beat an opaque, human-driven one. Take a developer corporation choosing its business focus. The process forces management to state the reason for the initial decision and the iteration behind it, model output included. That shrinks the surface area for value destruction: a value-destroying decision is far easier to make in private than in public.

The process is more than AI judgment. It is a reproducible template for decision-making, and it improves as the models strengthen. The counterfactual matters most. Skipping the process leaves every decision just as consequential: decisions still shape protocols financially and technically, but they happen in darkness, beyond scrutiny. We think that base case carries negative expected value for token holders, for three reasons. Mistakes made in private go uncorrected for longer, because nobody outside the room sees them in time to object. Management can favor its own interests over the network's at low cost, because nobody can compare the decision with the reasoning behind it. And holders who carry the downside without seeing the reasoning have to price in that uncertainty. Concentrating consequential decisions in a closed room is also a centralization vector, whatever the network's validator count.

## The cherry-picking objection

A skeptic will ask whether the operator could run the model many times and publish the answer they like. Four points answer it.

1. **Determinism removes the reroll.** The same input always produces the same output. The operator can change the answer only by changing the question, and the question is published alongside the answer.
2. **A selected output still beats none.** Even a favorable answer puts reasoning on the record, where readers can examine and dispute it. An opaque process puts nothing on the record.
3. **The benchmark is the alternative.** Every system has flaws. The fair comparison is with what networks do today, where consequential decisions happen with no process and no record at all.
4. **Holders keep the final say.** Critics could say the founder might cherry-pick output to justify a specific decision. Any such cherry-picking would sit in plain view in the prompt chain. Economic actors who suspect an unfair process, or see it drifting, can sell their tokens, just as they could on any other network. The founder and the development company also have every incentive to run an effective process: the Layer 1 differentiates itself through better governance, and a visibly rigged or inept process would quickly destroy market value.

## The evidence so far

On November 8 two independent machines scored a 452-company equity index. Each generated 1,033,095 output tokens across 455 model calls, and both produced identical token sequences, identical scores and the same 29 holdings, for about $72 of compute.

On November 9 we put a real governance question to the same setup. goodalexander submitted Post Fiat's status and asked for the priorities that maximize the network's value over 1, 3, 5 and 10 years, then challenged the answer nine times. The model revised its advice under challenge, withdrawing a token-launch date that had no metrics behind it, and every answer came back byte-identical across eight GPUs on two machines. The [governance page](/governance/) publishes the full conversation, 88 per-GPU receipts and a verifier anyone can run.

## What remains open

This is an experiment, and its hardest questions are ahead: who may submit questions, how decisions become binding, how to show the log is complete, and how to defend the inputs against manipulation. Replay settles one question, whether the record is real. The next ones get answered in public, on the governance page, one decision at a time.
