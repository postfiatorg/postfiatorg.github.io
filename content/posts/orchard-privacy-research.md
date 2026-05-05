---
title: "Orchard Privacy Research"
date: 2026-05-05T00:00:00Z
summary: "A Post Fiat privacy research note covering Orchard/Halo2 shielded payments, Railgun-style assurance, DID-bound providers, and why this material no longer belongs inside the validator-list whitepaper."
categories:
  - PostFiat Research
tags:
  - PostFiat
  - Orchard
  - Halo2
  - Privacy
  - Railgun
---

Appendix B does not belong in the Dynamic UNL whitepaper.

The validator-list paper should make one argument: Post Fiat can make validator-list publication auditable, replayable, and eventually independently recomputable. Orchard/Halo2 privacy and validator-consensus account exclusion are separate protocol questions. They are interesting enough to deserve their own research track, but keeping them inside the validator-list paper makes the whitepaper read like three papers stapled together.

This note moves that material out of the whitepaper and gives it a cleaner home.

## Bottom Line

Post Fiat's privacy branch is not a mixer, bridge, or external privacy token. The design direction is native Orchard-style privacy inside an XRPL-derived ledger, plus a Railgun-style assurance layer for counterparties that need privacy-preserving compliance evidence.

The current `halo2-devnet-integration` branch has working devnet coverage for:

- `t_to_z`: transparent funds entering the shielded pool;
- `z_to_z`: private shielded transfer;
- `z_to_t`: shielded funds returning to a transparent account;
- duplicate-nullifier rejection;
- wallet rescans from validated ledger history;
- checkpointed anchors and witnesses;
- root-backed assurance over accepted deposits;
- DID-backed assurance providers;
- Halo2 V1 admission proofs;
- Halo2 V1 assurance carry-forward through `z_to_z`;
- fail-closed wallet behavior when assurance or validated-ledger witness state is missing.

The important product idea is:

```text
PFT-native Orchard privacy
+ Railgun-style proof-of-innocence assurance
+ provider-pluralistic verification
+ no foundation viewing key
+ no separate privacy token
```

That gives Post Fiat a path toward Zcash-style native privacy while borrowing the useful compliance primitive from Railgun and Privacy Pools.

## Why This Is Separate From The Whitepaper

The Dynamic UNL whitepaper is about validator-list publication. Its thesis is narrow: the process that selects validators can be made more auditable and contestable if the inputs, prompts, model configuration, scoring artifacts, and list-construction rule are public and replayable.

Privacy does not prove that thesis. Account exclusion does not prove that thesis. Both belong in the broader Post Fiat roadmap, but neither belongs inside the whitepaper's core proof.

The split is therefore intentional:

- The whitepaper stays focused on validator-list publication.
- This post carries the privacy and compliance research.
- Future protocol docs can turn this research into formal amendment, wallet, and devnet specifications.

## Native Orchard Privacy

The `halo2-devnet-integration` branch ports Zcash's Orchard privacy model into a Post Fiat ledger rather than routing private value through a mixer or sidecar.

The branch adds an `OrchardPrivacy` amendment and a native `ttSHIELDED_PAYMENT` transaction family. The implementation uses a Rust `orchard-postfiat` crate built around Zcash's Orchard and `halo2_proofs` libraries, then connects that proof system to XRPL-style transaction validation in C++.

The core state model is familiar from Orchard:

- serialized shielded bundles;
- note commitments for new shielded outputs;
- anchors over the commitment tree;
- nullifiers for double-spend prevention;
- viewing-key-based note discovery;
- value-balance accounting for net flow between transparent balances and the shielded pool.

The same transaction family can support shielding, private transfer, and unshielding while preserving native ledger accounting. In the branch, proof-bearing bundles are parsed during transaction checks, Halo2 proof and anchor/nullifier constraints are enforced before application, and ledger effects debit or credit transparent balances only when value moves into or out of the shielded pool.

## Validated-Ledger Wallet Semantics

A major implementation issue was not whether Halo2 could prove something. It was whether the development wallet was preparing spends against the right ledger state.

An Orchard spend needs an anchor and a witness. The anchor is a Merkle root known to ledger history. The witness proves a note exists under that root. A wallet that prepares spends from provisional open-ledger state can build transactions that look valid locally but fail once validators close the ledger.

The current devnet behavior fails closed:

- unsafe wallet/prover RPCs are disabled by default on validators;
- local unsafe wallet RPCs require explicit configuration;
- wallet state is rebuilt from validated ledgers;
- spend witnesses and anchors come from checkpointed tree state;
- notes without checkpointed witnesses are not selected for spends;
- `orchard_prepare_payment` refuses to build a shielded spend while the open ledger already contains unvalidated shielded transactions.

Plain English: the dev wallet now refuses to pretend the open ledger is final.

## Railgun-Style Assurance

The compliance direction is not a foundation freeze key, not a global viewing backdoor, and not a separate privacy token.

The useful Railgun primitive is private proof of innocence: users keep shielded privacy while proving that funds are not associated with selected known-bad public sources. Post Fiat's version should be native to PFT and Orchard:

- assurance providers publish signed roots over accepted deposits or policy datasets;
- wallets derive deterministic deposit identifiers for decrypted notes;
- wallets import provider roots and mark matching notes as assured;
- `orchard_prepare_payment` can require assured-only shielded inputs;
- proof artifacts let counterparties verify assurance without seeing private Orchard addresses, balances, or transfer history.

This is provider-pluralistic. Different wallets, exchanges, and counterparties can choose different assurance providers or policies. The base chain does not need to hard-code one compliance oracle as the universal censor.

## DID-Bound Providers

Provider identity belongs at the provider layer, not the user layer.

Post Fiat's DID mapping uses a DID to identify the assurance provider, issuer, controller, or policy authority. The DID document resolves the assertion key that signs provider roots.

That means:

- `provider_id` can be the provider DID;
- `provider_did`, when supplied, must match `provider_id`;
- a provider DID document can resolve the signing key;
- provider root signatures can be checked against that DID;
- Orchard users, deposits, notes, recipients, nullifiers, and private credentials do not receive public DIDs.

The verifier's question becomes narrow: "Was this assurance root signed by a provider DID I trust?" It does not become: "Which shielded user is behind this transaction?"

## Halo2 V1 Assurance Proofs

The current branch includes first-cut Halo2 V1 assurance proofs.

Initial admission proves provider-root membership and emits the first assurance credential without publishing the deposit id, accepted set, amount, note commitment, credential secret, or private credential.

The `z_to_z` transition proof then carries assurance forward. It binds to:

- provider id;
- policy hash;
- provider root;
- validity ledger;
- transparent transaction digest;
- Orchard bundle commitment;
- Orchard input nullifier;
- fee;
- input assurance nullifier;
- assurance anchor;
- output assurance commitments.

The implemented V1 transition supports one assured input and up to two Orchard outputs. The public transition proof no longer exposes the original deposit id, source account, input note commitment, input assurance commitment, or private output credential payloads.

That is the key privacy/compliance primitive: assured value can move privately without forcing each later recipient or exchange to see the original deposit graph.

## Performance And Settlement

The branch's local performance tests measured successful private transaction flows in seconds on the development configuration:

| Flow | Observed mean send-to-close |
|---|---:|
| `t_to_z` | ~8.1 seconds |
| `z_to_z` | ~10.8 seconds |
| `z_to_t` | ~9.0 seconds |

This is not a mainnet benchmark. It is still meaningful because Post Fiat processes `ShieldedPayment` as a first-class ledger transaction. The design target is ledger-close finality on the Post Fiat network, not a second asynchronous privacy settlement system.

Compared with Zcash's 75-second block target, an XRPL-derived ledger with native Orchard verification has a plausible latency advantage if proof verification, validator resource limits, and wallet/prover separation are engineered correctly.

## Account Exclusion Is A Different Question

The old Appendix B also covered validator-consensus account exclusion. That material should stay out of the validator-list whitepaper and out of the core privacy thesis.

Account exclusion is a governance primitive. It differs from standard XRPL issuer freezes because it can reject generic transactions involving an excluded account, rather than only freezing an issuer-controlled IOU trust line. That makes it potentially relevant to sanctions-style compliance, but it also raises separate governance, due-process, decentralization, and market-structure questions.

The privacy direction above is cleaner as a first-class research path: preserve user privacy, avoid a universal viewing backdoor, and let counterparties require assurance from providers they trust.

## Current Release Boundary

This is still devnet-track research, not a public-mainnet claim.

The remaining release boundary is explicit:

- production wallet/prover separation;
- longer multi-validator devnet soaks;
- restart and reorg hardening;
- resource controls for proof verification;
- third-party provider operations;
- production recursive PPOI artifacts;
- deposit-private `z_to_t` exchange verification;
- external cryptographic and security review.

The near-term goal is not to claim production privacy before that work is done. The goal is to keep the design pointed in the right direction: native private PFT, privacy-preserving assurance, provider pluralism, and no centralized decryption or freeze backdoor.

## References

- Post Fiat whitepaper: [Auditable, Model-Assisted Validator-List Publication](/whitepaper/)
- Post Fiat implementation branch: `postfiatd` `halo2-devnet-integration`
- Zcash Orchard protocol context: [Zcash protocol specification](https://zips.z.cash/protocol/protocol.pdf)
- Railgun Private Proofs of Innocence: [Railgun docs](https://docs.railgun.org/wiki/assurance/private-proofs-of-innocence)
- Railgun Assurance Suite: [Railgun docs](https://docs.railgun.org/wiki/assurance/railgun-assurance-suite)
- XRPL freezes: [Common misconceptions about freezes](https://xrpl.org/docs/concepts/tokens/fungible-tokens/common-misconceptions-about-freezes)
- XRPL Deep Freeze: [Deep Freeze](https://xrpl.org/docs/concepts/tokens/fungible-tokens/deep-freeze)
- OFAC virtual currency guidance: [Sanctions Compliance Guidance for the Virtual Currency Industry](https://ofac.treasury.gov/system/files/126/virtual_currency_guidance_brochure.pdf)
