---
title: "pfUSDC on Arc: one USDC, there and back, authorized by proofs of both chains' finality"
date: 2026-09-02T00:00:00Z
lastmod: 2026-09-04T00:00:00Z
url: "/research/pfusdc-on-arc-round-trip/"
type: "page"
layout: "pfusdc_arc_round_trip"
draft: false
summary: "On 2 September 2026 we deposited 1.000000 USDC into a vault on Arc testnet, proved Arc's validator quorum finalized it inside a Groth16 proof, minted pfUSDC on the PostFiat L1 against that proof, burned it, proved PostFiat finality of the burn under ML-DSA signatures in SP1, and released the USDC on Arc against that proof. Every hop is pinned to its hash and evidence file, 32 corrupted witnesses were rejected, and the one open finding (the SP1 gateway owner key) is stated up front with a reproducible PoC."
description: "Technical review packet: a USDC deposit on Arc testnet, proven into the PostFiat L1 with a zero-knowledge proof of Arc finality, burned, and released back on Arc against a proof of PostFiat finality. Every hop pinned to its hash."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - Arc
  - Circle
  - USDC
  - pfUSDC
  - SP1
  - Groth16
  - ML-DSA
  - Bridges
  - Post Fiat L1
robotsNoIndex: false
---

This research page is rendered as a self-contained technical review packet
prepared for independent audit. It traces a proof-verified USDC round trip
between Arc testnet and the PostFiat devnet hop by hop, lists the contracts
and program identities under review, states the trust model including one
open finding, and gives the commands to reproduce every check. Source and
evidence: [postfiatorg/postfiatl1v2 PR #37](https://github.com/postfiatorg/postfiatl1v2/pull/37).
