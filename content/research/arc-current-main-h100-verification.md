---
title: "Arc/current-main H100 replay: historical proof passes, current merge remains gated"
date: 2026-09-02T00:00:00Z
summary: "An H100 replay confirmed the archived Arc v1 Groth16 pipeline and reproduced its public values byte for byte, but the current v2 guest correctly rejects that old witness and Arc's public RPC cannot supply the authenticated registry proof needed to recapture it. PR 37 remains unmerged."
categories:
  - Post Fiat Research
tags:
  - Arc
  - H100
  - SP1
  - pfUSDC
  - Verification
  - Post Fiat L1
robotsNoIndex: true
---

## Decision

The Arc source can be transplanted onto current PostFiat L1: Git had one
textual conflict, the integrated tree compiles, Arc conformance passed 4/4,
and the current Arc guest passed 5/5 tests on an NVIDIA H100.

That is not enough to merge it as proof-qualified code. The paid H100 run found
a real evidence gap: the repository's archived ingress witness belongs to the
older v1 guest, while the current candidate contains the stricter v2 guest.
PR 37 remains unmerged until a proof-ready v2 witness exists and passes the
same H100 gate.

## What the current candidate proved

The machine ran candidate commit
`fba263ef59c5de89b1b00a6d2e5e0ffb19ec670c` on an NVIDIA H100 80GB HBM3
with driver 590.48.01 and compute capability 9.0.

| Check | Result |
| --- | --- |
| Arc conformance | 4 passed, 0 failed |
| Current Arc guest tests | 5 passed, 0 failed |
| Current Arc ELF SHA-256 | `830634e6bf67333315bda7874ed1155dfc45c7e3b1ebc5e97a1fd34f9af7f130` |
| Current Arc vkey | `0x00d8e761fd2e0034388813ad8febd38beb3b271a83575a05834168450ea814c5` |
| Archived witness under current guest | Rejected before proving: `ARC_INGRESS_BOUNDS` |

The rejection is correct. The archived JSON is a v1 witness. It has an empty
`next_validators` list and no `validator_registry_proof`. The v2 guest
requires an authenticated validator-registry proof even when the validator set
does not change. Weakening that requirement merely to make an old fixture pass
would undo the security improvement.

We then attempted to recapture the same archived deposit through Arc's public
testnet RPC. The endpoint returned JSON-RPC `-32601` for `eth_getProof`:
the method is not supported. Without that state proof, the public capture path
cannot construct the v2 witness required by the current guest.

## Historical control replay

To separate a broken GPU environment from a missing v2 input, the same H100
checked out the frozen v1 source commit
`3e2c9caa9159cd899664434f0377f05b27f31deb` and replayed the archived
witness under its matching guest.

| Measurement | Result |
| --- | --- |
| SP1 GPU server | 6.3.1, device 0 |
| Guest instructions | 2,376,633 |
| Execute time | 934 ms |
| Proof mode | Groth16 |
| Proof bytes | 356 |
| Program vkey | `0x00b218e0ab7d2582baacca0dfaa8a5b211f258880ee44898797e109ae6b55ee0` |
| Public values | 314 bytes |
| Public-values SHA-256 | `cd985257ccb45f8dd3c54c0dbdec8f63e3ab6ee14e8846485e3b5749032f074b` |
| Archive comparison | Byte-exact |
| Total wall time | 335 seconds, including compilation and the first circuit download |

The newly generated proof verified locally. Its proof serialization is not
treated as deterministic output; the stable comparisons are the program
identity and canonical public-value bytes.

## Merge consequence

This run distinguishes two claims that had been conflated:

1. **Historical replay works.** The archived v1 program, witness, and public
   values are internally consistent and replay on an H100.
2. **Current v2 release qualification is incomplete.** The repository does not
   contain a v2 ingress witness, and the default public Arc RPC cannot create
   one because it does not expose `eth_getProof`.

The code transplant is mechanically feasible, but the current merge remains
gated. The next acceptable evidence is one of:

- an archive-capable Arc endpoint producing the registry proof at the exact
  archived deposit block;
- a new deposit plus an authenticated registry proof at its exact block; or
- a reviewed protocol redesign that authenticates the next validator set
  without depending on `eth_getProof`.

After that input is frozen, the current v2 ELF and vkey must be rerun on H100
and its public values compared against a committed expected artifact. Only
then should PR 37 be merged.

## Cost and cleanup

The H100 cost approximately **$0.65** at **$2.2044/hour** for 1,054 seconds.
The provider confirmed the rental was absent after termination. No stopped or
billable GPU was left behind.

Machine-readable results:
[/research/arc-current-main-h100-20260902/summary.json](/research/arc-current-main-h100-20260902/summary.json).
