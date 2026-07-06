---
title: "Introducing Post Fiat Terminal"
description: "A fork of Codex that runs Anthropic, GLM 5.2, and GPT models in one place — roughly 2–3× faster and 1.4–2.6× cheaper than Claude Code and Hermes on the same models, at identical accuracy. Provider-billed benchmarks, full evidence, and a reproduction script."
date: 2026-07-06
author: "goodalexander"
url: "/research/introducing-post-fiat-terminal/"
ShowToc: true
TocOpen: false
ShowReadingTime: true
ShowBreadCrumbs: false
_build:
  list: never
  render: always
---

I spend all day in Terminals. Codex. Claude Code. And sometimes Hermes.

I spend a lot of money on AI. It's my largest business expense. Increasingly my workflow is painful. A Claude Code pane running Fable managing one pane with a modded Claude Code running GLM 5.2 (across Baseten, Vercel, and Z.AI plans), sometimes a Hermes pane with some OpenRouter models, and two Codex panes.

Something about Claude Code's UX sent me off. It has cute little status updates I can't seem to turn off. It tells me to "go to bed" instead of just doing what it's told. A leaked source showed "pets" built within Claude Code. Hermes comes installed with countless plugins I don't want.

Codex, on the other hand, is a beautiful project. It renders fast. It's concise. It shows what it's doing. It's open source and held to high coding-quality standards. It doesn't opine on things it's not asked about or waste my tokens on things I didn't ask for.

Post Fiat Terminal is a fork of Codex designed to run Anthropic, GLM 5.2, and GPT models all in one place. It does so at a fraction of the cost and at an aggressively better speed than both Hermes and Claude Code. It's designed for my own workflows — crypto and trading — which means tight security practices like default use of vaults and provider keys built into the harness. It is open source, and free to use.

## The Benchmarks

What you're about to see is surprising. It surprised me. I did not realize the extent to which the excessive prompts and backend jobs were hurting the performance of the raw models.

The headline: running **the same models**, Post Fiat Terminal is roughly **2–3× faster** and **1.4–2.6× cheaper** than Claude Code and Hermes — at **identical accuracy** (100% task pass rate on both sides, every task). The gains are pure harness overhead. On Opus 4.8, Claude Code burned **2.5× more tokens** than Post Fiat Terminal to solve the exact same tasks.

| Comparison (identical model) | Speed | Cost | Accuracy | Paired runs |
| --- | :---: | :---: | :---: | :---: |
| **GLM-5.2-fast** — PfT vs Hermes | **1.8× faster** | **2.0× cheaper** | 100% = 100% | 100 |
| **Opus 4.8** — PfT vs Claude Code | **2.9× faster** | **2.6× cheaper** | 100% = 100% | 60 |
| **Fable 5** — PfT vs Claude Code | **1.9× faster** | **1.4× cheaper** | 100% = 100% | 60 |

*Speed is the paired median wall-clock ratio; cost is provider-billed dollars (see methodology). Every paired difference is statistically significant (p < 0.03; most p < 0.001).*

### GLM-5.2-fast — Post Fiat Terminal vs Hermes

Same model (`zai/glm-5.2-fast`) over Vercel, five Python tasks with hidden verifiers, 20 paired waves each (100 paired runs). Both sides passed 100%.

| Task | PfT time | Hermes time | Faster | PfT cost | Hermes cost | Cheaper |
| --- | ---: | ---: | :---: | ---: | ---: | :---: |
| eventforge | 68.5s | 90.8s | 1.4× | $0.461 | $0.579 | 1.3× |
| rategate | 30.2s | 43.8s | 1.6× | $0.158 | $0.218 | 1.4× |
| confclerk | 24.9s | 46.9s | 2.2× | $0.169 | $0.332 | 2.1× |
| queuecraft | 51.3s | 89.2s | 1.9× | $0.586 | $1.462 | 2.6× |
| pipeflow | 57.8s | 111.5s | 2.0× | $0.471 | $1.066 | 2.4× |
| **Overall** | **46.5s** | **76.5s** | **1.8×** | **$0.37** | **$0.73** | **2.0×** |

Provider-billed totals for the run: Post Fiat Terminal **$18.46**, Hermes **$36.58**.

### Opus 4.8 — Post Fiat Terminal vs Claude Code

Same model (`claude-opus-4-8`) direct to Anthropic, three tasks, 20 paired waves each. Both sides passed 100%.

| Task | PfT time | Claude Code time | Faster | PfT cost | Claude Code cost | Cheaper |
| --- | ---: | ---: | :---: | ---: | ---: | :---: |
| queuecraft | 50.2s | 298.6s | 6.0× | $0.409 | $1.586 | 3.9× |
| textwright | 65.3s | 176.5s | 2.8× | $0.525 | $1.101 | 2.2× |
| queryforge | 154.7s | 381.8s | 2.5× | $0.553 | $1.145 | 2.1× |
| **Overall** | **90.1s** | **285.6s** | **2.9×** (median) | **$0.50** | **$1.27** | **2.6×** |

This is the result that surprised me most. It's the *same* Opus 4.8 through the *same* Anthropic API — the only difference is the harness wrapped around it. On the hardest task, Claude Code took six times as long. Provider-billed totals: Post Fiat Terminal **$20.41**, Claude Code **$53.54**.

### Fable 5 — Post Fiat Terminal vs Claude Code

Same model (`claude-fable-5`), three tasks, 20 paired waves each. Both sides passed 100%.

| Task | PfT time | Claude Code time | Faster | PfT cost | Claude Code cost | Cheaper |
| --- | ---: | ---: | :---: | ---: | ---: | :---: |
| queuecraft | 85.8s | 176.0s | 2.1× | $0.969 | $1.615 | 1.7× |
| textwright | 73.6s | 138.7s | 1.9× | $0.857 | $1.159 | 1.4× |
| queryforge | 150.3s | 223.1s | 1.6× | $1.074 | $1.391 | 1.3× |
| **Overall** | **103.2s** | **179.3s** | **1.9×** | **$0.97** | **$1.39** | **1.4×** |

### How we measured cost — and why you can trust it

Internal token counters lie. So we don't use them. **Every dollar figure above is the provider's own billed amount:**

- **GLM (Vercel):** we snapshot Vercel's `/v1/report` billing endpoint, grouped by API key, before and after each run, and take the delta.
- **Opus & Fable (Anthropic):** we use the Anthropic Admin Usage API, billed by API key and model.
- **Isolation:** each side of every comparison ran on its own dedicated API key, so the two never mix — even when they run concurrently.
- **Integrity check:** on the clean lanes, the billed dollars *exactly* equal the model's published per-token price applied to the API-reported token counts. Opus reconciled to **0.000%** on both sides. That equality is the proof there's no hidden accounting trick.

We hold ourselves to full disclosure. During the Fable run, the Claude Code baseline key picked up some interrupted-and-resumed attempts outside the counted set (about 16% of that key's tokens). Rather than let that inflate the number, we priced only the counted runs from their own API-reported tokens at Anthropic's published rate — a method we'd already validated to **0.005%** against real billing on the Opus lanes. The raw, un-cleaned Fable number would have looked *better* for us (1.66× vs the 1.43× we report). We report the clean one.

Why is the same model faster and cheaper under Post Fiat Terminal? It sends leaner prompts and takes fewer round-trips to reach the same passing solution. It is not doing less — both sides pass the identical hidden verifier, and the produced code is comparable in size. It's simply less overhead per token of real work.

Full per-run data, billing artifacts, and a reproduction script are in the [appendix](#appendix-evidence--reproduction).

## Coordination, Panes and Vaults

Post Fiat Terminal adds four core features.

**`/panes`** — lets you have multiple panes open in one tmux screen running different models and settings. You can create panes with either Codex (standard, performance-optimized) or a Claude wrapper. We plan on adding Cursor support soon.

**`/vault`** — an easy way to store credentials without revealing them, which agents natively know how to interact with, without ever exposing keys.

**`/providers`** — a place to manage all your API keys and have them seamlessly stored in the vault.

**`/tasknode`** — a place to interact with Post Fiat's other core product, the [Task Node](/task-node/). This is a personal productivity system that I use every day, along with our community, that natively integrates with Post Fiat Terminal.

**`/spawn`** is the orchestration layer. It's entirely optional, and fairly early. The cost benefits you get from Post Fiat Terminal work fine without it. In Post Fiat's core product — the Task Node — we ran into a problem where it was hard to tell AI agents apart from humans. Codex solved this by giving Greek names to their agent spawns. Post Fiat Terminal uses Mordor-themed terminology: **Nazgûls** are the powerful entities (like CTOs), **Trolls** are managers (like VP Eng/Product), and **Orcs** are individual contributors.

`/spawn` means you can use Post Fiat Terminal out of the box with the popular orchestration method you see on X — Fable managing Codex.

The results can be fairly powerful. Here are some screenshots of an isometric video game built via `/spawn`.

<!-- IMAGE PLACEHOLDER: Raw Codex (2 hours) — drop screenshot(s) here -->
> **Raw Codex (2 hours)** — *screenshot to be added*

<!-- IMAGE PLACEHOLDER: Orchestration (2 hours) — drop screenshot(s) here -->
> **Orchestration via `/spawn` (2 hours)** — *screenshot to be added*

## Getting started

Post Fiat Terminal is open source and free. Install it with:

```sh
curl -fsSL https://github.com/agtico/PfTerminal/releases/latest/download/install.sh | sh
```

Works on Linux, macOS, and Windows. Source and docs: [github.com/agtico/PfTerminal](https://github.com/agtico/PfTerminal).

---

## Appendix: Evidence & Reproduction

Every number in this post is backed by raw, downloadable data. Nothing here is a token estimate.

**Test conditions.** Shipped binary `pfterminal 0.1.8`. Ten Python coding tasks with hidden, held-out verifiers; a task "passes" only if its verifier passes. Runs are *paired* (Post Fiat Terminal and the baseline run the same task in the same wave, same day) because provider conditions swing enough day-to-day that only same-day pairs compare fairly. Speed is wall-clock time to a verifier-passing solution. Significance is a paired test (Wilcoxon / paired-t) per task.

**Full evidence report** (methodology, every lane total, all per-task tables, CIs, p-values, and the billing reconciliation):

- [phase1-evidence-report.md](/research/pfterminal-benchmark/phase1-evidence-report.md)

**Raw data:**

- [raw-waves.csv](/research/pfterminal-benchmark/raw-waves.csv) — one row per run: task, agent, wave, pass/fail, tests passed, wall-clock seconds, billed cost, cost source, route verification.

**Provider billing artifacts (the cost ground truth):**

- [vercel-report-settle.json](/research/pfterminal-benchmark/vercel-report-settle.json) — Vercel `/v1/report` before/after billing by API key (GLM).
- [frontier-token-reconciliation.json](/research/pfterminal-benchmark/frontier-token-reconciliation.json) — Anthropic Admin Usage tokens vs counted-run tokens, per key (Opus & Fable).
- [frontier-row-priced-cost-recovery.json](/research/pfterminal-benchmark/frontier-row-priced-cost-recovery.json) — the clean Fable cost derivation and the 0.005% Opus validation.
- [frontier-fairness-controls.json](/research/pfterminal-benchmark/frontier-fairness-controls.json) — same-model fairness checks (matched effort disclosure, equivalent-output proxy, cost-vs-token-ratio gate).
- [key-scan.json](/research/pfterminal-benchmark/key-scan.json) — automated secret scan of all evidence artifacts (0 hits).

**Reproduce it yourself:**

- [reproduce/README.md](/research/pfterminal-benchmark/reproduce/README.md) — exact commands.
- [reproduce/runner.py](/research/pfterminal-benchmark/reproduce/runner.py) — the config-driven, stdlib-only benchmark harness (multi-provider, provider-billed cost, route verification, secret scanning, and a no-spend `validate-stored` path that re-checks the published rows without spending a cent).
- [reproduce/config.example.json](/research/pfterminal-benchmark/reproduce/config.example.json) — a sanitized config template (key files and paths are placeholders).

```sh
# no-spend: re-derive and validate the published numbers from the stored raw artifacts
python3 runner.py --config config.example.json validate-stored

# dry-run plan (no spend):
python3 runner.py --config config.example.json plan

# scan all artifacts for accidentally-committed secrets:
python3 runner.py scan-keys

# live run (spends real provider credits; keys are read from files/vault, never inline):
python3 runner.py --config config.example.json run
```

*Cost figures were validated against provider billing, not internal token counters. Where a billing window contained non-benchmark traffic, it is disclosed above and excluded by a method independently validated against real billing.*
