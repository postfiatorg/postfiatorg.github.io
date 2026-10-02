---
title: "About Post Fiat"
layout: "single"
url: "/about/"
summary: "XRP 2.0: the private, quantum-resistant internet of value for on-chain capital markets."
description: "Post Fiat is XRP 2.0: a private, quantum-resistant Layer 1 for on-chain capital markets. This page is the canonical plain-language summary of what exists today, what is live, and how the project is different from XRP."
keywords:
  - Post Fiat
  - XRP
  - PFT
  - Task Node
  - validator benchmark
  - capital markets
---

# About Post Fiat

Post Fiat is XRP 2.0: a private, quantum-resistant Layer 1 for on-chain capital markets. Machine intelligence will compound capital on chain. Post Fiat is the chain where that will happen.

It is built so that you can privately swap any asset on chain at low cost and hold market-neutral portfolios as NAVCoins whose net asset value is proven on chain, on a fixed-supply native asset, with Task Node as its network of pseudonymous contributors.

## What it does

1. **Represents portfolios trustlessly.** A NAVCoin is a floating-value unit issued only against a finalized, proven NAV.
2. **Swaps into them privately.** Asset-Orchard settles both legs of an exchange in one atomic, shielded transition.
3. **Maintains a fixed supply.** Native PFT is fixed at genesis; every fee burns; there is no validator reward.
4. **Runs an information network.** Task Node assigns, verifies and rewards useful work by pseudonymous contributors and their agents.

## How it differs from XRP

It keeps XRP's settlement design (known validators, deterministic finality, fixed supply, fee burn, no validator subsidy) and changes three things. Validator-trust changes become protocol state ratified by **Cobalt**. Accounts and validators sign with post-quantum **ML-DSA** from genesis. Settlement can run privately through **Asset-Orchard**. Its first market is buy-side capital markets.

## Networks

| Network | What runs there |
|---|---|
| Post Fiat L1 (postfiatl1v2) | NAVCoins, private swaps, the pfUSDC bridge and Cobalt governance. A666 has opened at NAV $1.000000 and completed a 20-minute Ethereum mainnet round trip. |
| Post Fiat validator network (postfiatd) | 53 validators across 42 publishing domains, with model-assisted validator-list publication. |

## The validator network, in figures

<div class="stats" style="margin:1.6em 0 .6em">
  <div><div class="v">53</div><div class="k">Validators</div></div>
  <div><div class="v">39</div><div class="k">Verified domains</div></div>
  <div><div class="v">52<small style="font-size:.4em"> / 53</small></div><div class="k">24h agreement ≥ 99.9%</div></div>
  <div><div class="v">46<small style="font-size:.4em"> / 53</small></div><div class="k">30d agreement ≥ 99%</div></div>
</div>

<p class="muted" style="font-size:15px">Snapshot of September 21, 2026 from the <a href="https://vhs.testnet.postfiat.org/v1/network/validators/test">validator history service</a>, also shown in the <a href="https://explorer.testnet.postfiat.org/network/validators">testnet explorer</a>. 42 publishing domains.</p>

## Where to go next

- [Whitepaper](/whitepaper/): the design, and a claim-by-claim map to proof and source.
- [Research](/blog/): experiments, published with their evidence.
- [Task Node](https://tasknode.postfiat.org/): take work, show evidence, earn PFT. [Connect your agent](/agents/).
- [postfiatl1v2](https://github.com/postfiatorg/postfiatl1v2): the L1 source.
- [Validator setup](/validator-setup/) and [benchmark](/validator-benchmark/): run a validator.
- [Legacy governance whitepaper](/whitepaper/legacy-governance/): the original validator-list design.
- For assistants: [llms.txt](/llms.txt) and the [JSON summary](/postfiat-project.json).

## Founder

Post Fiat was founded by Alex Good ([@goodalexander](https://x.com/goodalexander)), whose background spans Citi FX, Palantir, Balyasny (TMT) and Perpetua. Post Fiat is venture backed by Hypersphere Capital Management.

## FAQ

### What is a NAVCoin?

A floating-value unit whose reserve valuation, supply, methodology, custody perimeter and settlement representation can each be inspected. The ledger creates and retires units only against a finalized, proven NAV. NAV floats with the reserves.

### What is the Task Node?

The community intelligence layer: contributors and their AI agents request tasks, submit evidence, are verified and earn PFT. It is the main way to take part in the network today.

### What is PFT used for?

PFT is the fixed-supply native asset. It pays for ordering and proof verification, every fee burns, and it rewards verified Task Node work.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "AboutPage",
      "@id": "https://postfiat.org/about/#page",
      "url": "https://postfiat.org/about/",
      "name": "About Post Fiat",
      "description": "What Post Fiat is, what exists today, and how it differs from XRP."
    },
    {
      "@type": "Organization",
      "@id": "https://postfiat.org/#organization",
      "name": "Post Fiat",
      "url": "https://postfiat.org/",
      "description": "Post Fiat is XRP 2.0: a private, quantum-resistant Layer 1 for on-chain capital markets.",
      "founder": {
        "@type": "Person",
        "name": "Alex Good"
      },
      "sameAs": [
        "https://www.twitter.com/postfiatorg",
        "https://www.github.com/postfiatorg",
        "https://postfiat.org/community/"
      ]
    },
    {
      "@type": "FAQPage",
      "@id": "https://postfiat.org/about/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is Post Fiat?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Post Fiat is XRP 2.0: a private, quantum-resistant Layer 1 for on-chain capital markets. It represents portfolios as NAVCoins issued against proven net asset value, swaps into them privately through Asset-Orchard, keeps a fixed native supply with fee burn and no validator subsidy, and runs Task Node, a network of pseudonymous contributors."
          }
        },
        {
          "@type": "Question",
          "name": "How is Post Fiat different from XRP?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "It keeps XRP's settlement design (known validators, deterministic finality, fixed supply, fee burn, no validator subsidy) and changes three things: validator-trust changes become protocol state ratified by Cobalt, accounts and validators sign with post-quantum ML-DSA from genesis, and settlement can run privately through Asset-Orchard."
          }
        },
        {
          "@type": "Question",
          "name": "What exists today?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "The current and legacy whitepapers, the postfiatl1v2 source, the new L1 with NAVCoins and private swaps, a 53-validator network with validator history and explorer, the validator benchmark, and Task Node."
          }
        },
        {
          "@type": "Question",
          "name": "What is PFT used for?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "PFT is the fixed-supply native asset. It pays for ordering and proof verification, every fee burns, and it rewards verified Task Node work."
          }
        }
      ]
    }
  ]
}
</script>
