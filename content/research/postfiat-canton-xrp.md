---
title: "Post Fiat, Canton, and XRP: Three Bets on the Future of Settlement"
date: 2026-08-01T00:00:00Z
url: "/research/postfiat-canton-xrp/"
type: "blog"
breadcrumb_label: "Research"
breadcrumb_url: "/research/"
summary: "What Post Fiat is, explained by contrast: zero-issuance economics, protocol-state governance, and shielded settlement, set against the XRP Ledger and the Canton Network — and the economic bet behind each design."
description: "A Post Fiat position paper for investors and community members: the conceptual architecture of Post Fiat compared with XRP and Canton across economics, governance, privacy, and the NAVCoin settlement thesis."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Canton
  - XRP
  - Governance
  - Cobalt
  - NAVCoin
  - Privacy
  - CBDC
---

*Written for the Post Fiat community — investors, builders, and validators who want a clear picture of what Post Fiat is, where it is headed, and how it stands beside the two networks it is most often compared to.*

> **Scope and evidence status.** XRP and Canton descriptions below are linked to their primary documentation. Post Fiat claims distinguish design intent from behavior present in the public Rust reference implementation at commit [`2ee110b`](https://github.com/postfiatorg/postfiatl1v2/tree/2ee110b61265270f4c1317062eccaea701ac5f8a). Those source links verify what the code checks; they do **not** attest that an off-chain reserve exists, belongs to the issuer, is correctly valued, or will be legally available in a redemption.

> **Reproduction note (2 August 2026).** From a fresh public clone at that commit, `cargo test -p postfiat-execution nav_ --lib` ran 23 NAV-focused tests with 23 passing and none failing. The selected tests cover stale/deadman gating, multi-fetch attestations, bonded challenges, SP1 proof binding and tamper rejection, minting, pending redemption, and settlement deadlines. This is implementation evidence, not a production audit or reserve attestation.

## Three answers to the same question

Every settlement ledger is a set of answers to three old questions. Who keeps the books? Who pays the bookkeepers? And who gets to look?

The XRP Ledger, the Canton Network, and Post Fiat are three attempts to answer those questions for institutional finance. XRPL servers listen to validators selected through local Unique Node Lists; Canton's Global Synchronizer is operated by identified Super Validators; Post Fiat's current design also assumes an identified validator set. They answer differently — and each answer is an economic bet.

- **XRP** bets on radical simplicity: a transparent ledger, [validators with no direct protocol reward](https://xrpl.org/ja/blog/2020/running-an-xrp-ledger-validator), and a fixed initial supply whose transaction fees are [destroyed](https://xrpl.org/docs/concepts/transactions/transaction-cost).
- **Canton** bets on an identified institutional perimeter: Super Validators operate the Global Synchronizer, infrastructure and applications earn Canton Coin, and contract data is distributed on a [need-to-know basis](https://github.com/digital-asset/canton/blob/eaa9e7a4bf48793acb35aba270b85a970afe6006/docs-open/src/sphinx/participant/tutorials/getting_started.rst#L561-L566).
- **Post Fiat** bets on combining zero validator issuance, an Orchard-derived shielded lane, and protocol-state governance. The implementation can make some evidence *machine-checkable*; whether the evidence establishes a real-world fact remains profile- and attestor-dependent.

This piece lays the three side by side, so a reader can see precisely what Post Fiat is building and why.

## A shared ancestor, and where the family splits

More than a decade ago, the XRP Ledger demonstrated something quietly radical: a financial ledger can run without miners, stakers, or direct validator rewards. Each server reaches agreement by listening to validators on its [Unique Node List](https://xrpl.org/docs/concepts/consensus-protocol/unl); validated ledgers provide final results, although the safety model depends on sufficient UNL overlap. XRP began with [100 billion units](https://xrpl.org/docs/introduction/what-is-xrp), and transaction fees are burned rather than paid to validators. Behind the engineering sits a simple idea about who should secure a settlement system: parties who depend on settlement should have a natural reason to help operate it.

The [Post Fiat whitepaper](/whitepaper/) specifies the same broad category—known validators, certificate finality, fixed supply, and fee burn—while changing validator-set governance, disclosure, and authorization. Its post-quantum authorization and governance claims are design and implementation claims; they need public test vectors, compatibility evidence, and independent cryptographic review before they should be treated as deployed guarantees.

Canton takes a different road. Built by Digital Asset around Daml, it is a "network of networks" whose applications can use a [Global Synchronizer](https://docs.dev.sync.global/overview/overview.html) operated by Super Validators. The same primary documentation describes the Global Synchronizer Foundation, two-thirds BFT governance, and Canton Coin rewards for infrastructure, validators, and application providers. This is a stronger and narrower statement than treating every Canton deployment as one monolithic consortium ledger.

Three lineages, then: XRP the minimalist ancestor, Canton the institutional consortium, Post Fiat the cryptographic synthesis. The differences sharpen along three axes — economics, governance, and privacy — before converging on what Post Fiat builds with them.

## The economic bets

### XRP: "the best incentive is no incentive"

David Schwartz's "best incentive is no incentive" argument is the intellectual frame; XRPL's own validator guide states the narrower fact: the ledger provides [no direct economic reward for validation](https://xrpl.org/ja/blog/2020/running-an-xrp-ledger-validator) and aims to attract natural stakeholders. Whether this produces a sufficiently diverse and durable operator set is an empirical governance question, not something the incentive thesis proves by itself.

### Canton: pay for the bootstrap

Canton makes the opposite bet, deliberately. Its published schedule targets 100 billion Canton Coin minted over the first decade and 2.5 billion per year thereafter, allocated among application providers, validators, and Super Validators; fees are burned in a proposed burn-mint equilibrium. The figures and allocation phases are set out in the [Canton Coin MiCA whitepaper](https://www.canton.network/hubfs/Canton%20Network%20Files/whitepapers/Canton%20Coin%20%20-%20MiCA%20Whitepaper.pdf), while the live mechanism is described in the [Splice documentation](https://docs.dev.sync.global/overview/overview.html). This gives Canton a protocol-native bootstrap mechanism. It also couples network economics to the operator and governance structure, a tradeoff that should be evaluated from the live governance contracts rather than inferred from branding.

### Post Fiat: zero issuance, with the condition finally priced

Post Fiat keeps XRP's proposed economic answer—fixed supply, fee burn, and zero validator pay—and adds an explicit evidence predicate to the [governance design](/whitepaper/). Candidate evidence includes economic exposure, signed identity and revocation paths, operational reliability, attack surface, and correlation. The proposed selector treats shared control—such as a release manager, key-management vendor, or funding controller—as a reason to hold or reject admission. This is a policy claim until the live predicate, inputs, thresholds, and decisions are publicly replayable.

And, because pricing our own bet is the house style: zero issuance means zero protocol treasury. Ecosystem development is funded off-protocol, where it can be disclosed and vetted rather than minted. Canton has a machine for funding its bootstrap; XRP and Post Fiat pay for theirs some other way. Post Fiat chooses that trade with eyes open, because a subsidized validator class is exactly the constituency a settlement ledger should decline to create.

### The privacy-coin choice hiding inside this one

The great privacy systems took the other path. Zcash funded development through block-reward allocations, while Monero adopted tail emission. Post Fiat's design thesis is that zero-issuance economics can coexist with an Orchard-derived shielded lane. "Orchard-derived" matters: [ZIP 224](https://zips.z.cash/zip-0224) defines Orchard and its Halo 2 proof system; it does not certify Post Fiat's implementation. The implementation, test vectors, audits, and deployed parameters must carry that separate burden.

| | XRP Ledger | Canton Network | Post Fiat |
|---|---|---|---|
| Native issuance | None — 100B fixed at genesis | Scheduled minting curve (100B over decade one, 2.5B/yr thereafter), offset by fee burn | None — fixed supply at genesis |
| Fees | Burned | Burned (burn-mint equilibrium) | Burned — the only protocol-level economic flow |
| Validator compensation | None from the protocol | Super Validators, validators, and app providers mint CC for measured utility | None from the protocol |
| Who validates, and why | Natural stakeholders | Participants rewarded in the network's token | Natural stakeholders, admitted by a public evidence predicate |
| Ecosystem funding | Off-protocol | On-protocol, via emissions | Off-protocol, disclosed and vetted |
| Governance–economics coupling | Indirect, through UNL and amendment choices | Super Validators govern while operator/app classes receive emissions | Intended separation: no validator emissions; admission still creates political power |

## Governance: where does the validator list live?

Strip away the branding, and the deepest difference among the three networks is a single question: *where does the validator list live, and what does it take to change it?*

**XRP: on the operators' disks.** Each server trusts a Unique Node List, which determines whose validation votes it considers. XRPL's documentation says avoiding forks requires a high degree of overlap and notes that the default configuration consumes recommended lists published by the XRPL Foundation and Ripple; [anyone may publish a signed list](https://xrpl.org/docs/concepts/consensus-protocol/unl). The trade is explicit: choosing publishers and lists is outside ledger state, even though the downloaded lists are signed.

**Canton: in an on-chain governance application operated by the Super Validator collective.** The official Global Synchronizer documentation describes [two-thirds BFT ordering and governance voting](https://docs.dev.sync.global/overview/overview.html), with the Foundation coordinating and itself operating a Super Validator. For institutions that want identified operators and contractual recourse, that may be a feature. The concentration, independence, and upgrade risks must still be judged from the actual operator set and voting state.

**Post Fiat: intended to live in protocol state.** The design draws on Ethan MacBrough's [Cobalt paper](https://arxiv.org/abs/1802.07240), which studies atomic broadcast and governance under non-uniform trust. Cobalt supplies a research basis, not an audit of Post Fiat's transition checker or proof that every implementation-specific threshold is safe.

The core design principle fits in five words: **old rules judge new rules.** The intended genesis state commits the initial registry, trust graph, and rule-checker. A subsequent transition packet is evaluated under the previously active rules, including a proposal to replace the checker. That construction makes the trust handoff explicit; it does not eliminate the initial trusted launch or guarantee that incumbents will approve a necessary recovery.

The intended checker evaluates quorum arithmetic, old-to-new continuity, and connectivity, and rejects transitions that fail those predicates. Those are implementation claims that require test vectors, adversarial simulation, and independent review in addition to the Cobalt citation. "Fail closed" is safer against an invalid transition but can also preserve a captured or deadlocked incumbent registry; liveness and emergency recovery are part of the threat model, not footnotes.

Genesis remains a trusted act. The design calls for a signed launch certificate committing the initial state so that later auditors can identify the bootstrap assumption. Its value depends on publication, signer independence, reproducible genesis generation, and verification by shipped node software.

**Closing the last private room — without pretending the model is consensus.** The design proposes a pinned language model that converts public evidence into a typed, cited classification, followed by deterministic selector code. That split reduces authority only if the model artifact, prompt, retrieval corpus, evidence snapshot, and parser are all hash-bound and replayable. Evidence poisoning, model nondeterminism, unavailable model weights, and ambiguous outputs must resolve to abstention. "Deletion monotonicity" — removing the model can make the system no more permissive — is the target invariant; it still needs executable conformance tests.

A representative test case would submit a candidate with strong uptime but a release manager, monitoring endpoint, and funding source shared with an incumbent. The expected conservative result is *cosmetic diversity* and a held application, with citations to each shared-control field. Publishing that fixture and its deterministic expected output would turn the example from prose into evidence.

| | XRP Ledger | Canton Network | Post Fiat |
|---|---|---|---|
| Where the validator list lives | Operator configuration files | Foundation process | Protocol state |
| How it changes | Publishers post signed recommended lists; operators configure publishers | Two-thirds Super Validator governance | Intended transition packets validated under the prior rules |
| Who judges a change | Reputation and convention | The consortium itself | The old rules' checker: quorum intersection, continuity, connectivity — fail-closed |
| Qualitative questions | Operator/publisher discretion | Governance process | Proposed replayable classification; deterministic selector |
| A failed change | Resolved socially | Resolved procedurally | Previous registry remains in force, automatically |

## Privacy: three answers to who may see

The choice runs deeper than "privacy versus transparency." Each network picks a *perimeter* and an *enforcer*.

**XRP — transparent by default.** XRPL is a shared public ledger: validated transaction and state data can be inspected, subject to ordinary caveats about linking ledger addresses to real-world identities. That makes supply and on-ledger positions auditable but supplies no native transaction-content confidentiality.

**Canton — cryptography enforced around an organizational topology.** Canton participants receive transaction subtrees on a [need-to-know basis](https://github.com/digital-asset/canton/blob/eaa9e7a4bf48793acb35aba270b85a970afe6006/docs-open/src/sphinx/participant/tutorials/getting_started.rst#L561-L566), and payloads sent through a synchronizer are end-to-end encrypted. The synchronizer cannot decrypt payloads but [does see opaque-message metadata](https://github.com/digital-asset/canton/blob/eaa9e7a4bf48793acb35aba270b85a970afe6006/docs-open/src/sphinx/overview/explanations/canton/protocol.rst#L53-L64). Relevant participant nodes see the contract data needed to validate their part, while the Splice glossary states that [Canton Coin transactions are public](https://docs.dev.sync.global/glossary.html). The residual metadata and operator access surface therefore depend on topology, traffic analysis, endpoints, logging, and application design—not only Daml visibility rules.

**Post Fiat — cryptographic, with a public boundary.** The reference design adapts Orchard concepts to issued assets. Its current [privacy specification](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/docs/privacy/deposit-spend-withdraw.md#L11-L37) leaves the anchor, nullifier, output commitments, fee, policy hash, and disclosure hash public; deposit burns and withdrawal amounts are also public at the boundary. It intends to hide the asset ID, shielded value, owner key, memo, randomness, and Merkle path inside the proof. This does not hide timing, transaction size, network-layer identifiers, ingress/egress relationships, or information voluntarily disclosed by wallets, RPC providers, bridges, or counterparties. Two mechanisms adapt the model for institutional assets:

1. **The turnstile.** The [specified invariant](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/docs/privacy/deposit-spend-withdraw.md#L39-L65) is narrow: cumulative withdrawals for an asset cannot exceed cumulative deposits minus prior withdrawals, and a violation freezes that shielded action class. It bounds value leaving the shielded pool. It does **not** prove reserve quality, authenticate NAV, establish legal ownership of collateral, or guarantee that an issuer will honor redemption.
2. **Holder-controlled disclosure.** The target model uses viewing keys, scoped note openings, and auditor proofs so a holder can grant limited visibility. The privacy specification's public disclosure hash is evidence of a commitment point, not by itself proof that the full disclosure tooling, revocation model, and regulator workflow are complete.

Why the perimeter matters is best told through the FX benchmark cases. U.S. prosecutors said four banks agreed to plead guilty to conspiring to manipulate USD/EUR spot prices and pay [more than $2.5 billion in criminal fines](https://www.justice.gov/archives/opa/pr/five-major-banks-agree-parent-level-guilty-pleas); the CFTC separately imposed [more than $1.4 billion](https://www.cftc.gov/PressRoom/PressReleases/7056-14) over attempted manipulation of FX benchmark rates, and the European Commission later fined banks for [G10 spot-trading cartels](https://ec.europa.eu/commission/presscorner/api/files/document/print/cs/ip_21_6548/IP_21_6548_EN.pdf). Those actions support the narrower lesson that privileged order-flow information can be abused. They do not prove that confidentiality alone fixes benchmark governance, price formation, surveillance, or conflicts of interest.

| | XRP Ledger | Canton Network | Post Fiat |
|---|---|---|---|
| Model | Fully transparent ledger | Need-to-know data distribution | Shielded pool (zero-knowledge) |
| An outside observer sees | Public ledger addresses, state, and transactions | Only data in its participant scope; Canton Coin flows are public | Commitments, nullifiers, fees, policy hashes, timing, and boundary amounts |
| Operators and infrastructure see | Public ledger state | Relevant contract data; synchronizer sees encrypted-envelope metadata | Proof data plus public boundary metadata; endpoints may learn more |
| Trust basis | Public state plus UNL consensus | Cryptography, application authorization, and organizational topology | Proof system, implementation, parameters, keys, and endpoint hygiene |
| Selective disclosure | Addresses are pseudonymous but ledger data is public | Daml visibility rules, set per contract | Target: holder-granted viewing keys, proofs, and scoped openings |
| Supply auditability | Trivial | Per application | Per-asset public turnstile |

## The destination: NAVCoins and a hub for the internet of value

Machinery is only interesting for what it makes possible. Post Fiat's answer: *verified money, exchanged atomically, in private.*

**The trouble with stablecoins.** Many reserve-backed tokens still depend on issuer, custodian, accountant, and legal-entity representations that arrive outside consensus. A periodic report may be useful evidence, but a ledger cannot make that report true; it can only bind state transitions to authenticated inputs derived from it. The useful question is therefore not "attestation or code?" but: *who signs which fact, under what valuation policy, and what can the protocol safely do when that fact is late or disputed?*

**The NAVCoin.** Post Fiat's proposed instrument has a floating unit NAV rather than a fixed peg. In the current reference implementation, an authorized issuer or reserve operator submits a reserve packet; the code checks the packet's profile, epoch, uniqueness, and the arithmetic condition `verified_net_assets >= circulating_supply × nav_per_unit`, with explicit rounding and unit scaling ([submission path](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L1104-L1292), [collateralization arithmetic](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/types/src/market_nav_asset_types.rs#L897-L945)). Minting is capped against the finalized packet. That proves faithful execution of a configured policy—not the truth of an unproven input.

### What authenticates NAV and reserves?

The answer is profile-specific. These profiles cannot honestly be compressed into the phrase "machine-verified reserves."

- **Ledger-transparent profile:** consensus recomputes balances from named on-ledger reserve accounts and rejects a claimed total that does not match. This authenticates ledger state, not off-chain custody, asset quality, liens, or omitted liabilities.
- **SP1 Groth16 profile:** consensus verifies a proof against a registered program verification key and committed public values. Security then depends on the proved program, its data adapters and valuation policy, the verification key, proof-system assumptions, and the authenticity of data entering the circuit.
- **Multi-fetch quorum profile:** finalization requires a configured minimum of passing attestations. This is an attestor/oracle trust model: source authentication, independence, equivocation handling, and legal accountability remain external dependencies.
- **Legacy or unregistered profile:** authorization, hashes, freshness, and collateral arithmetic may be enforced without a consensus proof of the underlying real-world assets. The lifecycle test deliberately exercises such a packet with empty proof bytes ([test case](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/market_nav_execution_tests.rs#L296-L500)). It is evidence that the state machine works, not a reserve attestation.

The verifier dispatch implementing those distinctions is visible in the [reserve-submit branch](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L1175-L1267). Independent review still needs the registered profiles, verification keys, valuation programs, source adapters, attestor registry, key rotation, and production configuration—not merely this dispatcher.

### What happens when proof fails, disappears, or is disputed?

The code rejects undercollateralized or invalid submissions. A challenge can mark an eligible packet challenged and halt the asset; consensus-verified ledger-transparent and SP1 packets are not challengeable through that same branch ([challenge path](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L1295-L1404)). Finalization enforces the challenge window, snapshot age, and—where configured—the attestation threshold ([finalization path](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L1407-L1583)). Fraud discovered after finalization, a compromised registered verifier, and conflicting legally authoritative data still require explicit governance and recovery procedures.

The deadman switch is especially important. If the finalized packet exceeds its configured epoch gap, or the asset is halted, [`ensure_nav_asset_live_for_epoch`](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nav_vault_asset_execution.rs#L7615-L7660) rejects both minting **and redemption initiation**. That limits state changes under stale evidence, but it can also trap holders precisely during issuer or oracle distress. A production design needs a separately specified emergency exit—such as burn-to-claim under the last uncontested NAV, court- or trustee-directed wind-down, or another bounded mode—whose abuse and solvency consequences are analyzed before launch.

Finally, on-ledger redemption is not cash settlement. [`NavRedeemAtNav`](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L2085-L2180) debits the token and creates a pending redemption claim. A separate issuer/redemption-account action, [`NavRedeemSettle`](https://github.com/postfiatorg/postfiatl1v2/blob/2ee110b61265270f4c1317062eccaea701ac5f8a/crates/execution/src/nft_escrow_asset_execution.rs#L2252-L2315), marks that claim settled. The chain can record deadlines and status; it cannot by itself force a bank, custodian, transfer agent, or insolvency estate to deliver external assets.

**The hub primitive: the atomic shielded swap.** The target primitive exchanges two on-ledger shielded assets in one state transition, proving value conservation without revealing the note contents. Atomicity removes principal risk *between those two ledger legs*; it does not make either issuer solvent or guarantee external redemption.

```
Party A holds a USD-asset                 Party B holds a NOK-asset
        |                                         |
        v                                         v
+----------------------------------------------------------------+
|             ONE INDIVISIBLE SHIELDED TRANSACTION               |
|    value conservation proven; both legs settle, or neither     |
|    observers see: commitments, nullifiers, fee, boundary data  |
|    proof hides note contents; endpoints may reveal metadata    |
+----------------------------------------------------------------+
        |                                         |
        v                                         v
Party A holds the NOK-asset               Party B holds the USD-asset
```

Readers from the FX world will recognize the narrower risk this deletes. The Basel Committee defines FX principal risk as paying away one currency without receiving the other and recommends payment-versus-payment where practicable ([supervisory guidance](https://www.bis.org/publ/bcbs241.htm)). An atomic swap can provide PvP for assets within its settlement domain. Risks at reserve, bridge, issuer, wallet, and legal boundaries remain.

**Room for central banks.** In Post Fiat's FX thesis, each currency could be represented by a native ledger asset whose reserve and redemption regime is separately specified. [Project Mariana](https://www.bis.org/publ/othp75.htm) demonstrated a proof of concept for cross-border wholesale-CBDC exchange using AMMs, but the BIS explicitly calls it experimental and says it does not imply issuance or endorsement; its report also placed governance, privacy, performance, integration, and legal questions out of scope. Post Fiat's proposed addition is cryptographic transaction confidentiality with scoped disclosure. That is a research direction, not evidence of central-bank adoption or proof that viewing-key workflows satisfy supervisory requirements.

## The whole picture

| Dimension | XRP Ledger | Canton Network | Post Fiat |
|---|---|---|---|
| Category | Transparent authority-validated ledger | Synchronized network of sovereign Daml ledgers | Reference implementation of a shielded authority-validated settlement ledger |
| Finality | Deterministic, in seconds | BFT sequencing per synchronizer | Deterministic BFT with explicit two-phase commit |
| Issuance | Zero — 100B fixed | Scheduled minting, offset by burn | Zero — fixed supply, fee burn only |
| Validator pay | None | Minted rewards for measured utility | None |
| Validator list | Off-chain recommended lists | Foundation plus weighted Super Validator vote | Protocol state — old rules judge new rules |
| Qualitative judgment | Operator/publisher discretion | Super Validator governance process | Proposed replayable classification and deterministic selector |
| Privacy | Transparent | Organizational need-to-know | Zero-knowledge shielded pool |
| Disclosure | Everything public | Contract visibility rules | Holder-controlled viewing keys |
| Authorization | Classical signatures | Classical signatures | ML-DSA specified in the reference design; deployment assurance pending |
| Reserve-backed assets | Issuer-trusted IOUs | Tokenized assets under issuer and participant trust | NAVCoins — profile-bound reserve packets; mint cap; current stale-proof path blocks mint and redeem initiation |
| The bet | Simplicity and transparency endure | Regulated finance adopts the governed network | Profile-bound verification, privacy, and zero-issuance economics compose |

## Three bets, one field

Respect where it is due. XRP proved the category, and bets that its virtues — simplicity, transparency, a validator class that shows up because it must — are the ones that endure. Canton bets that regulated finance wants a governed club: identified members, contractual recourse, a foundation with famous names on the door, and a token that pays the builders. Both are serious positions held by serious people.

Post Fiat bets on the synthesis: governance predicates executed in protocol state, reserve claims bound to explicit verification profiles, and shielded settlement with scoped disclosure—without protocol issuance for validators. The bet succeeds only if the implementation, production parameters, data provenance, legal redemption stack, and emergency exits survive independent review. Code can narrow trust and make violations observable; it cannot abolish the institutions at the boundary.

That is what Post Fiat is building.

---

*Core Post Fiat design documents: the [Post Fiat whitepaper](/whitepaper/), [A Proposal for Better Private FX Settlement](/private-fx-settlement/), and [The NAVCoin Proposal](/blog/navcoin-proposal/). Claim-level links above point to the relevant external primary documentation and commit-pinned implementation paths. Source code is evidence of specified state-machine behavior, not attestation of deployed configuration or real-world reserves.*
