---
title: "pfUSDC on Solana: A Proof-Verified Deposit Route at Minutes-Scale Latency"
date: 2026-11-19T00:00:00Z
draft: true
summary: "Post Fiat now credits pfUSDC against USDC deposited on Solana mainnet using a zero-knowledge proof of Solana finality in place of an operator attestation. A deposit locks USDC in a vault program, a prover shows that Solana's validators finalized the block and that the block created the deposit receipt, and Post Fiat validators verify a 356-byte proof before minting. Measured end to end on Solana mainnet: 174 to 201 seconds, against about 21 minutes for the proof-verified Ethereum route. This post specifies the route as implemented on 19 November 2026, gives the measurements, and lists what remains open."
categories:
  - Post Fiat Research
tags:
  - pfUSDC
  - Solana
  - Alpenglow
  - USDC
  - Vault Bridge
  - Zero-Knowledge Proofs
---

# pfUSDC on Solana: A Proof-Verified Deposit Route at Minutes-Scale Latency

**Status:** implemented and measured on Post Fiat's `postfiat-wan-devnet-2` network against Solana mainnet. The route was activated at ledger height 1678 on 19 November 2026. Deposits through the public wallet are paused while one parser fix described in section 7 is rolled out.

## 1. Why Solana

pfUSDC is Post Fiat's USDC-backed settlement asset. Each unit is minted against a counted deposit in a vault on an external chain. The vault domain sets three properties at once: how long a deposit takes, what it costs to verify, and who has to be trusted for the mint.

The existing proof-verified route runs through Ethereum. It needs no trusted operator, and it takes about 21 minutes, because a proof of Ethereum finality has to wait for Ethereum to finalize. A faster deposit through that route requires someone to advance funds before finality, which reintroduces a counterparty.

Solana changes the starting point. Under its Alpenglow consensus, validators sign a finality certificate for a block within about a second. A proof built on that certificate inherits Solana's finality time and adds only the time to prove. The Solana route therefore reaches minutes-scale latency with the same trust statement as the Ethereum route: the mint depends on a proof that Post Fiat validators check themselves.

## 2. What the route provides

**Credit by proof.** Post Fiat validators mint pfUSDC only after verifying a Groth16 proof whose public values name the Solana block, the vault program, the route binding, and each deposit receipt. The relay that carries the proof holds no authority over the mint.

**Replay protection.** Every deposit has a 32-byte nonce and a receipt account derived from it. The ledger records each credited deposit ID and rejects a second proof for the same deposit.

**Route binding.** The vault stores a 32-byte binding computed from the Post Fiat chain ID and genesis hash, the route ID, the Solana genesis hash, and the vault program ID. Every receipt carries it. A proof made for another vault or another chain fails the binding check.

**Source labelling.** Credits arrive as a pfUSDC source series tied to the Solana vault, so the ledger's backing statement counts Solana deposits separately from Ethereum deposits.

## 3. What was verified, and when

The following was observed on 19 November 2026.

- The vault program `GFkpeTibgdRAAAndgUMYsJnSTck91tUbrpuWBWan6z1G` is deployed on Solana mainnet and configured for Circle's USDC mint, with a cap of 25 USDC per deposit and 500 USDC in total.
- All six Post Fiat validators accepted the governed `solana-mainnet-usdc-v1` route at height 1678.
- Four USDC deposits made on Solana mainnet were credited as pfUSDC. Each credit has an accepted receipt and one state root across the six validators. The first, 0.1 USDC, was credited at height 1679.
- Three of those deposits were timed from the Solana send to the visible pfUSDC balance: 201, 174 and 190 seconds.
- On two private Alpenglow clusters, ten consecutive deposits had a median of 41.5 seconds end to end.
- The live ledger rejected three invalid submissions at admission: a replayed proof (`duplicate_solana_deposit`), a proof with one bit changed in its public values (`sp1_proof_invalid`), and a proof presented under a retired route revision (`solana_route_superseded`).
- An epoch handoff on a private cluster was proved and accepted, and deposits were credited on both sides of the boundary.

## 4. Specification

### Deposit flow

```
 Depositor (Solana)                         Post Fiat ledger
 ------------------                         ----------------
 vault.deposit(amount,
   pf_recipient, nonce)
        |
        | moves USDC to vault custody
        | creates receipt account:
        |   magic | route binding |
        |   recipient | amount |
        |   nonce | depositor
        v
 block finalized by Alpenglow
 certificate (about 1 s)
        |
        v
 Observer node saves:
   block shreds, certificate,
   old and new state of every
   account the block changed
        |
        v
 Prover (4 GPUs):                 --->   solana_bridge_proof_v1
   leaf proofs in parallel                 verify Groth16 proof
   aggregate proof                         check validator set, epoch,
   Groth16 wrap (356 bytes)                route binding, vault program
                                           reject credited deposit IDs
                                           mint pfUSDC to pf_recipient
```

### What the proof establishes

The proof program runs inside the SP1 zero-knowledge virtual machine. It takes the saved block data as private input and produces 391 public bytes. Each step commits to the next, so the receipt at the bottom is tied to the validator signatures at the top.

```
 Trusted validator set for the epoch  (held by the Post Fiat ledger)
        |
        |  BLS aggregate signature, stake threshold met
        v
 Finality certificate names   slot + block ID
        |
        |  block ID = Merkle root over the block's erasure sets
        v
 Block shreds  --->  block contents  --->  footer: bank hash
        |
        |  bank hash commits to the hash of all account state
        v
 Old state hash + changes in this block = new state hash
        |
        |  the changes include a NEW account owned by the vault
        v
 Deposit receipt: recipient, amount, nonce, route binding
```

Solana commits to its account state as one aggregate hash, with no per-account tree. The proof therefore accounts for every account the block changed, about 1,500 on mainnet, and shows that the old state plus those changes gives the new state the validators signed. A receipt that the block did not create cannot appear in that set.

### Parallel proving

Hashing 1,500 account changes dominates the work. The prover splits them across four GPUs. Each leaf proof covers a contiguous range of account changes and commits to its bytes and its contribution to the state hash. The aggregate proof verifies the four leaves, checks that their ranges cover the block exactly once and in order, verifies the certificate and the block, and emits the public values. A final wrap produces the Groth16 proof the ledger verifies in about a third of a second.

### Following Solana's validator set

Solana's validator set changes every epoch, about two days. A recorder program on Solana writes each epoch's validator keys and stakes into accounts. A handoff proof shows that a block finalized by the current set contains the next set, and that validators holding at least two thirds of the current stake signed it. The ledger then replaces its stored set.

```
 epoch E set (in ledger)  --signs-->  block containing recorder table for E+1
                                              |
                                      handoff proof
                                              v
                                   ledger stores epoch E+1 set
```

The first set for a route is installed by a validator-signed governance transaction. Every later set follows by proof.

## 5. Latency

Measured on the first mainnet deposit, in seconds after the Solana send:

```
 0        Solana transaction sent
 7.1      finalized, seen by the relay
 18.4     block data exported from the observer node
 21.9     witness built
 89.0     four leaf proofs done            (67 s)
 164.1    aggregate and Groth16 proof done (75 s)
 166.5    submitted to Post Fiat
 195.0    finalized on Post Fiat
 200.9    pfUSDC balance visible
```

Proving accounts for about 142 of the 201 seconds. The next two timed deposits finished in 174 and 190 seconds, with proofs of 91 to 142 seconds depending on the size of the block.

| Route | Trust for the mint | Deposit to credit |
| --- | --- | --- |
| Ethereum, proof-verified | proof | about 21 minutes |
| Solana mainnet, proof-verified | proof | 174 to 201 seconds |
| Private Alpenglow cluster, proof-verified | proof | 41.5 seconds median |

The private-cluster figure shows where the floor is when blocks are small: Solana finality took 0.36 seconds, proving took 32 seconds, and the Post Fiat side took the rest. On mainnet the block is larger and proving is the dominant cost.

## 6. Integration constraints

- **Deposit caps.** The mainnet vault accepts at most 25 USDC per deposit and 500 USDC in total. The caps are set at initialization.
- **Depositor costs.** The depositor pays Solana's transaction fee and the storage deposit for the 132-byte receipt account, about 0.003 SOL together.
- **Token program.** The vault accepts the classic SPL Token program and a six-decimal mint.
- **Proof size.** The ledger accepts proof bodies up to 4,096 bytes, which fits the Groth16 proof and excludes the larger intermediate proofs.
- **Observer node.** The prover needs the state of every changed account before and after the block. That requires a node that executes Solana blocks; the node is untrusted, since a wrong input produces no valid proof.

## 7. Open items

1. **Padded block markers.** Some Solana block producers pad the end-of-block marker with trailing zeros. Solana's validator accepts this; the first version of the proof program did not, so deposits landing in those blocks, roughly one in four in the sample examined, could not be proved. The corrected parser and rebuilt proof programs are being installed, and the route moves to the new program key by a governed revision.
2. **Epoch handoff on mainnet.** Handoffs are proved automatically on the private clusters. The mainnet relay does not yet run them.
3. **Program upgrade authority.** The Solana programs are still upgradeable by the deployer key. Custody becomes independent of that key when the authority is removed.
4. **Withdrawals to Solana.** The ledger selects one exit route per asset, and for pfUSDC that route is Ethereum. A per-route exit selector is required before pfUSDC credited from Solana can leave through Solana.
5. **Recorder storage.** Each epoch's validator table locks about 0.65 SOL of storage deposit. The recorder needs a close instruction that returns it once the epoch has ended.
6. **Proving time.** Proving is about 70% of mainnet latency. The proof program's account hashing and the final wrap are the two places to cut.
7. **Observer hosting.** The observer runs on rented hardware. It needs a dedicated host and a second instance.

## Disclaimer

This document describes software running on a Post Fiat development network against Solana mainnet, with deposit caps of 25 USDC per deposit and 500 USDC in total. It has had no external audit. Measurements are from 19 November 2026 and from a small number of deposits. pfUSDC is a claim on USDC held in a vault program and depends on Circle, Solana, and the open items above. Nothing here is investment advice or an offer of any asset.

## Sources

- Post Fiat, `postfiatl1v2` branch `sol/live`: `programs/pfusdc-sol-ingress` (proof programs), `solana/pfusdc-vault` and `solana/pfusdc-recorder` (Solana programs), `tools/pfusdc-sol-relay` (relay), `docs/review/solana-live-route-analytics.md` (private-cluster timings).
- Post Fiat, `docs/specs/pfusdc-solana-trustless-bridge-spec-20261118.md`: route specification.
- Post Fiat, `docs/review/solana-live-rejections.md`: live rejection evidence.
- Anza, Agave validator source at commit `141da0c3`: shred, block-component, certificate and bank-hash formats.
- Succinct, SP1 6.3.1: zero-knowledge virtual machine and Groth16 verifier.
