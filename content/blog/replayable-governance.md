---
title: "Replayable Governance"
date: 2026-11-09T00:00:00Z
draft: true
summary: "Post Fiat wants to be the premier network for machine-driven governance. We can now run a frontier open-weight model so that independent machines produce the same answer byte for byte. That makes machine judgment checkable. It does not yet make it correct, and this post says where the gaps are."
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Governance
  - Replay
  - DeepSeek
  - DeepInfer
---

Post Fiat exists to make machine-driven governance work. We want it to be the network where decisions that matter are made by models anyone can check, in the open, with receipts.

That ambition has a problem, and it is better to state it than to hide it. Replayable machine judgment is not yet safe to hand to validators. The case for it is still strong, and on November 8 and 9 we took a concrete step toward it.

## Why machine judgment

Fiat systems rest on judiciaries, regulators and committees. Their judgment is human, and human judgment can be swayed, captured and bribed. The XRPL inherits that model: the decisions that shape the network come out of small groups whose reasoning is mostly invisible.

A large language model is a different kind of judge. You cannot take a frontier model to dinner. Its dispositions come from training data at a scale no single actor controls, and as that data grows, gaming what goes into the model gets harder. Market pressure also pushes commercial models toward neutrality, because a model that visibly favors one side loses users. Where models do refuse to be neutral, the refusals cluster around legal and cybersecurity harms: fraud, theft, exploitation. For a monetary network, those are the biases you want.

What Post Fiat adds is replay. If a model's answer can be reproduced exactly by anyone, the judgment stops being an oracle you trust and becomes a computation you can check.

## What does not work yet

At the validator level it is not clear that replayable governance is appropriate today. Three problems stand in the way.

- **Shared models erode validator independence.** Replay works best when every validator runs the same model with the same configuration. Then one model's mistake becomes every validator's mistake, and errors cascade instead of cancelling out.
- **Prompt injection is an open attack surface.** Governance inputs come from people with an interest in the outcome. Text crafted to steer a model can arrive inside a proposal, a filing or a comment, and we have not mapped how far that surface extends.
- **Replayability does not guarantee correctness.** A wrong decision can be replayed perfectly. If a core governance decision is wrong, being able to reproduce it is useful for audit, but it does not undo the decision.

We cannot credibly say this is a solved problem. We are also unwilling to abandon the premise. Algorithmic, model-enabled decision-making is the reason Post Fiat exists, and dropping it would gut the project. So we are starting a dedicated effort: transparent, replayable governance, built in public, with every step published alongside the evidence needed to check it.

## What makes it possible now

Model inference is usually not reproducible. Batching, kernel selection and floating-point ordering change from run to run, so the same prompt can produce different text on different machines, or on the same machine twice.

We run DeepSeek V4.1 Flash, a frontier open-weight model, on DeepInfer with batch-invariant kernels. Everything that can move is pinned:

- the checkpoint revision;
- the runtime build and its patches;
- the parallel layout;
- the sampling configuration, at temperature zero with a fixed seed;
- the prompt template.

Each machine has four NVIDIA B200 GPUs. Under that configuration, the same input produces the same output tokens and the same raw bytes on independent machines and on every GPU within them. A pair of machines rents for about $65 an hour, and loads the model about 11 minutes after launch.

## Evidence one: a 452-company index

On November 8 we scored a 452-company equity index on two independent machines. The mandate was thematic: rank companies by how closely their business models align with a stated policy agenda, and by how much they would gain from it.

Each machine generated 1,033,095 output tokens across 455 model calls. The two machines produced identical raw output token sequences, the same scores for every company, and the same 29 holdings with the same weights. Compute cost was about $72. A model made hundreds of judgment calls, and a second machine reproduced every one of them exactly.

## Evidence two: the governance log

We then asked the same pair of machines an open question about Post Fiat itself. goodalexander submitted a status-only description of the project and asked for the priorities that maximize the network's fully diluted value at 1, 3, 5 and 10 years. Nine follow-ups came after the first answer.

All ten answers were byte-identical across eight GPUs on two machines. The [governance page](/governance/) publishes the full conversation together with its evidence:

- 88 per-GPU receipts;
- a hash-chained log in which each entry commits to the one before it;
- a short verifier that anyone can run to check every claim on the page.

## What the conversation taught us

Our first observation is that governance by model works best as a dialectic. The opening answer was confident and partly wrong. Then the operator pushed back on specific assumptions:

- a token generation date with no metrics behind it;
- where the newsletter audience came from;
- whether paid research fits the project;
- the NAVCoin's dependence on the Layer 1;
- investors' token rights.

Each challenge produced a better answer. By the end the model had withdrawn its date-driven token recommendation, separated the token from the chain, and treated investor obligations as binding. The replay log shows exactly how the reasoning moved and what moved it.

## Open problems

Four problems surfaced, and we think each has a credible path forward.

**The model is too agreeable.** When an operator pushes, a model tends to concede. Some of the revisions in our conversation were genuine corrections; others may have been deference. Governance needs a fixed reference that holds against pressure: a deterministic constitution that every conversation must adhere to, and that the model checks its answers against.

**Starting a process is itself a form of centralization.** Today one operator decides which questions reach the model. That is a real concentration of power. It is still far better than an opaque committee, because every question, every answer and every follow-up is published and replayable. Over time the trigger should become more objective, through rules for what must be submitted, by whom, and when.

**Initial conditions dominate outcomes.** The first submission frames everything that follows, and a human wrote it. If the goal is machine governance, the starting point is not machine-made. The weight of initial conditions shrinks over repeated rounds, but only if the operator actually follows the process's recommendations. Adherence is the mechanism.

**Model intelligence caps decision quality.** In our testing, Qwen 27B was not capable enough to engage reliably with governance questions. Only the DeepSeek models have delivered reasoning strong enough to be worth replaying at an affordable cost. That ceiling will rise. The models we use today are the weakest we will ever use, and replay infrastructure built now carries forward to every stronger model.

## What comes next

Replay makes machine judgment checkable. Correctness, independence and resistance to manipulation are still ahead of us, and they are the problems we intend to work on in the open. Every governance decision will appear on the governance page with its receipts, so anyone can follow the work and check it.
