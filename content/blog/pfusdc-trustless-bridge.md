---
title: "pfUSDC: A Stablecoin Bridge Secured by Proofs, Not Committees"
date: 2026-07-19T00:00:00Z
url: "/pfusdc-trustless-bridge/"
aliases:
  - "/blog/pfusdc-trustless-bridge/"
breadcrumb_label: "Blog"
breadcrumb_url: "/blog/"
summary: "Most stablecoin bridges are guarded by a validator committee that signs an attestation a contract mints against — the exact layer that has lost most of the value stolen in DeFi since 2022. pfUSDC replaces it: both directions of the bridge are authorized by succinct cryptographic finality proofs, not signatures. USDC deposits on Arbitrum mint pfUSDC on the Post Fiat L1 against a proof of finalized Ethereum/Arbitrum state; pfUSDC burns are redeemed against a proof of finalized PFTL consensus — including the validators' post-quantum ML-DSA signatures verified inside a zkVM. We ran a complete round trip end to end on a controlled testnet: a real deposit minted, burned, and withdrawn as exactly 1.000000 USDC, conservation to the atom, both legs proof-verified on-chain with replay protection. Checkpoint-pinning keeps each withdrawal proof to a three-block segment and a custom ML-DSA lattice accelerator trims the dominant cost, bringing a trustless withdrawal proof to roughly three minutes of GPU time."
description: "A trust-minimized stablecoin bridge where both directions are authorized by zero-knowledge finality proofs rather than a signing committee: USDC on Arbitrum and pfUSDC on the Post Fiat L1, with post-quantum ML-DSA consensus verified inside an SP1 zkVM, demonstrated end to end on testnet with exact conservation and on-chain replay protection. Open source at github.com/postfiatorg/postfiatl1v2."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - pfUSDC
  - Stablecoins
  - Bridges
  - Zero Knowledge
  - Post-Quantum
  - SP1
  - USDC
---

Most stablecoin bridges are guarded by a committee. A set of validators watches one chain, signs
an attestation, and a contract on the other chain mints against that signature. It is a
well-trodden failure surface: since 2022, by widely-cited industry tallies, bridge exploits account
for much of the value stolen in DeFi — on the order of $2.8B — and the root cause is almost always
the same: a signature or attestation an attacker learned to forge or bypass. The verification layer
*is* the bridge, and when it fails the rest just automates the loss.

{{< bridge-flow mode="status-quo" >}}

Proof-based bridges — zk light clients like Polyhedra and Succinct's work — answer this by
replacing the committee's attestation with a succinct proof of the source chain's consensus.
pfUSDC belongs to that class and pushes it further: both directions are proof-verified, the two
chains are sovereign, and one of them runs post-quantum consensus that the bridge verifies
*inside a zkVM*.

This does not abolish trust; it relocates it. You still rely on Ethereum's finality and on PFTL's
own consensus being sound — but you no longer rely on an extra multisig or attestation layer
stacked on top of them, which is exactly the layer that has failed elsewhere. A relayer can carry
a proof; it cannot forge one or redirect funds, because every proof is bound to the exact deposit
or withdrawal it authorizes, and there is no fallback path to a signer.

## How a dollar moves

{{< bridge-flow mode="pfusdc" >}}

**In (USDC → pfUSDC).** You deposit USDC into a vault contract on Arbitrum. A zero-knowledge
proof (generated with SP1, a RISC-V zkVM) demonstrates that your exact deposit is included in a
confirmed Arbitrum assertion settled under finalized Ethereum state. PFTL verifies that proof
on-chain against a pinned checkpoint and mints exactly the deposited amount of pfUSDC. No observer
attests to your deposit; the proof is the authorization.

**Out (pfUSDC → USDC).** You burn pfUSDC on PFTL. A second proof demonstrates that the burn was
accepted in a finalized PFTL consensus block — including the validator signatures and the block's
ancestry back to a checkpoint the Arbitrum vault already trusts. The vault verifies that proof and
releases exactly your USDC. No threshold committee signs the withdrawal; the proof does.

Underneath, two stateful light clients keep the system honest. PFTL holds a checkpoint of
Ethereum/Arbitrum finality; the Arbitrum vault holds a checkpoint of PFTL consensus and its
validator set. Each checkpoint is established once, at deployment, from a genuinely finalized
block of the other chain — a public, auditable anchor — and from then on advances **only** by
verifying a proof, never by an operator setting a value and never by trusting an RPC. Validator-set
rotations on PFTL are proven as part of the chain segment, so the vault follows PostFiat's
validators cryptographically rather than being told who they are.

## What you trust, and what you don't

The precise trust model is the point, so here it is plainly.

**You trust:** that Ethereum reaches finality; that PFTL's own consensus is sound (an honest
validator majority); that the cryptography is correct — SP1's proof system and the ML-DSA
signature scheme; and that the deployed contracts and zkVM programs faithfully implement the rules
described here. That last assumption is exactly what independent audits exist to check: a proof is
only ever as sound as the program it proves.

**You do not trust:** any bridge multisig or attestation committee (there is none); any relayer
(it can only carry proofs); any operator to set checkpoints or balances by hand (checkpoints move
only by proof); or any RPC endpoint's honesty (every claim is checked against finalized state, not
taken on faith). The one privileged control the deployment retains is a pause switch — an operator
can halt the bridge, but the contracts give no one the power to move, mint, or redirect locked
funds — and there is no downgrade path back to a signer once a route is live.

That second list is where bridges normally lose money. pfUSDC removes it, and narrows the first
list to assumptions you can independently audit.

## What's different here

Two things make this bridge unusual. First, it is **fully bidirectional between two sovereign
chains** — the USDC vault lives on Arbitrum (settling to Ethereum L1), and PFTL is a separate
sovereign chain with its own consensus. Most trust-minimized bridges are one-way header relays, or
an L2 proving into its own settlement layer — not two chains each proving finality to the other.

Second, PFTL runs **post-quantum consensus**: its validators sign with ML-DSA (FIPS-204
Dilithium), and the withdrawal proof verifies those lattice signatures *inside the zkVM*. The
mathematics that makes PostFiat quantum-resistant is the same mathematics the Arbitrum contract
checks with a single succinct proof. We know of no other bridge that proves post-quantum consensus
in zero knowledge.

That verification is heavy, and making it practical was the engineering. Proving runs on GPUs
(SP1's CUDA prover), which turns a multi-hour CPU proof into minutes. Withdrawal proofs are kept
short by advancing the on-chain checkpoint close to the chain head, so each exit proves only a
handful of blocks of ancestry — a three-block segment in our runs — rather than the entire
history. And a custom accelerator for the ML-DSA lattice arithmetic (the part generic zkVM
precompiles don't touch) trims the dominant remaining cost. Together these bring a withdrawal
proof to roughly three minutes of GPU time — now bounded by the fixed cost of the final SNARK
wrap rather than by how long the chain is.

## We ran it end to end

This is not a whiteboard design. We executed a complete round trip on a controlled testnet against
Arbitrum Sepolia and verified every step on-chain: a genuine on-chain deposit of testnet USDC,
minted as pfUSDC, then burned and withdrawn, with cryptographic proofs accepted on both chains.
The withdrawal released **exactly 1.000000 USDC** back out — conservation to the atom — its
on-chain receipt succeeded, and the proof's nullifier was consumed so the same proof can never be
replayed. Ingress and egress each verified against their pinned, honestly-established finality
checkpoints; neither leg touched an observer or a signer. The exit is publicly checkable — the
withdrawal settled on Arbitrum Sepolia in transaction `0x664b2897…e702c1f9` with an accepted
receipt — and the withdrawal proof behind it was a three-block segment the GPU prover produced in
about three minutes. None of this is a black box: the vault and verifier contracts, the SP1
programs that generate and check the proofs, and the acceptance gate that validated this exact
round trip are open source at
[github.com/postfiatorg/postfiatl1v2](https://github.com/postfiatorg/postfiatl1v2) — the same code
described here, available to read and audit.

## What it means for holders

pfUSDC is a native asset on PFTL whose backing is verifiable, not asserted. Every pfUSDC in
circulation corresponds to USDC locked in a vault whose balance is auditable on-chain, and the
mint and burn that move value across the boundary are each backed by a proof anyone can check. You
do not have to trust Post Fiat's operators, a separate bridge multisig, or a relayer to get your
dollar back — the reliance narrows to the two things underneath any honest bridge: that Ethereum
is final and that PFTL's own consensus is sound.

## Honest boundaries

What we have is a testnet prototype that demonstrates the full Tier-4 mechanism end to end — both
directions proof-verified, no downgrade path — not yet a production mainnet deployment. The
remaining work is chiefly productionization and independent review: a hardened prover service so
users never touch proving infrastructure, custody hardening on the exit side, a measured
cost-and-latency budget under continuous load, and third-party audits of the contracts and the
zkVM programs — which the whole trust model rests on and which could still surface issues to fix —
before mainnet. The trust model is proof-based and demonstrated on-chain today; the engineering to
make it cheap, fast, and operable at scale, and the review to earn confidence in the code, are
what come next. We will keep claiming only the rung we can prove.
