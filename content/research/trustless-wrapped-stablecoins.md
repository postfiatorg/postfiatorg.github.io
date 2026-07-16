---
title: "Trustless Wrapped Stablecoins on PFTL"
date: 2026-07-16T00:00:00Z
url: "/research/trustless-wrapped-stablecoins/"
type: "blog"
breadcrumb_label: "Research"
breadcrumb_url: "/research/"
summary: "A primer and technical specification for wrapping external stablecoins onto PFTL under consensus-enforced verification: user-initiated deposits into an on-chain vault, an evidence ceremony every validator checks, quorum-observed credits, challenge-windowed exits, a per-tier threat model, and a staged ladder from observed verification to full finality proofs."
description: "Primer and technical spec for trustless wrapped stablecoins on PFTL, covering the ERC20BridgeVault, deposit evidence schema, observer-quorum validity rules, per-state redemption accounting, tiered threat model, and the roadmap to receipt-inclusion and finality-proof verification."
author: "Post Fiat"
categories:
  - Post Fiat Research
tags:
  - PFTL
  - Bridge
  - Stablecoins
  - pfUSDC
  - Proof of Reserves
  - Trust Minimization
draft: false
---

# Trustless Wrapped Stablecoins on PFTL

> **By:** Post Fiat  
> **Scope:** Primer and technical specification for bringing wrapped USDC and other external stablecoins onto PFTL, covering the protocol that exists today and the staged roadmap to full trustlessness

This document follows one terminology rule throughout:

> **“Trustless” is reserved for a tier where the destination chain verifies finalized source-chain facts through a permissionless verifier, directly or through a sound succinct proof.**

Threshold-signed systems are trust-based. Observer and optimistic systems are trust-minimized within their stated assumptions. Each deployment should claim exactly its enforced tier and nothing above it.

## 1. Executive summary

A wrapped stablecoin system must answer two questions:

1. What evidence permits PFTL to issue wrapped atoms after a source-chain deposit?
2. What evidence permits the source-chain vault to release underlying atoms after a PFTL burn?

PFTL answers the first question today with a consensus-enforced observer ceremony. A user deposits USDC into `ERC20BridgeVault`, choosing a PFTL recipient. Evidence for that deposit is proposed on PFTL, checked against exact observations from registered observers, finalized under a fail-closed quorum rule, and claimed by the named recipient.

At Tier 1, PFTL validators do **not** independently prove source-chain inclusion or finality. They validate that the submitted evidence is internally consistent and that enough registered observers reported matching source-chain facts. The system is therefore **independently observed**, not trustless.

The exit path is also interim: a PFTL burn produces a withdrawal packet that passes through source-chain challenge windows and a threshold-based verifier before the underlying is released. PFTL then records settlement using a withdrawal-observation quorum.

Control minimization is the design trajectory, not a completed Tier-1 property. Today’s authority surface includes:

- registered observers and the profile’s `min_attestations`;
- authorized role accounts, including `issuer`, `reserve_operator`, and `redemption_account`;
- profile and activation governance;
- a source-chain vault owner-held pause;
- a designated source-chain challenge authority; and
- an interim threshold verifier for exits.

The tier ladder retires these dependencies in stages: receipt proofs remove observers from entry safety, finality proofs remove governed checkpoints from entry safety, and succinct PFTL-finality proofs replace the threshold exit verifier. The target is a round trip whose cross-chain facts are verified permissionlessly in both directions.

### 1.1 Consensus validity rules versus application contracts

All destination-chain validators execute application contracts, so the important distinction is not simply “consensus versus contract” or where code is physically located. The meaningful differences are:

1. **Evidence requirements.** A signature-checking bridge accepts facts authorized by its committee or issuer. PFTL’s bridge transaction kinds require evidence under a state-committed verification profile. At Tier 1 that evidence is an observer quorum; at higher tiers it becomes receipt inclusion and source-chain finality proofs.
2. **Rule mutability and capture resistance.** PFTL bridge validity rules and profiles change through visible L1 governance and are committed to chain state. An application bridge may instead be governed through the application’s own admin keys or committee.
3. **Block validity.** A PFTL block containing a bridge operation that fails the active validity rules is invalid to PFTL validators. This does not make the source-chain assertion true by itself: at Tier 1, external truth still depends on the observer-honesty and source-chain-reorg assumptions described below.

The architecture therefore creates a stable verification locus while allowing the evidence standard to ratchet upward.

## 2. Primer: assets, evidence, and conservation

A wrapped stablecoin on PFTL is a native PFTL asset backed by an external stablecoin held in a source-chain vault. For USDC:

- asset code: `PFUSDC`;
- precision: 6 decimals;
- `VAULT_BRIDGE_UNIT = 1,000,000` atoms per whole token; and
- one pfUSDC atom represents one micro-USDC.

The bridge has two separate concerns:

- **authorization:** whether evidence satisfies the current verification tier; and
- **accounting:** whether deposits, issued atoms, burns, releases, and settlements conserve value through every lifecycle state.

### 2.1 Full lifecycle accounting model

A two-term equation such as “vault balance equals issued supply” is correct only when no deposit or redemption is in flight. The full model uses four state quantities:

- `V`: USDC atoms held by the source-chain vault;
- `S`: issued pfUSDC atoms on PFTL;
- `D`: atoms deposited into the vault but not yet credited on PFTL;
- `B`: atoms burned on PFTL whose redemption has not yet been settled on PFTL; and
- `R`: the subset of `B` already released by the source-chain vault but not yet settled on PFTL.

The conservation identity is:

```text
V = S + D + B - R
```

`R` is subtracted because a released-but-unsettled redemption remains open in PFTL’s lifecycle records but is no longer held by the vault.

For an exact amount `x`, the state transitions are:

| Lifecycle event | State transition | Identity after transition |
|---|---|---|
| Initial resting state | `D = 0`, `B = 0`, `R = 0` | `V = S` |
| Source-chain deposit | `V += x`, `D += x` | `V = S + D + B - R` |
| PFTL credit claim | `S += x`, `D -= x` | `V = S + D + B - R` |
| PFTL redemption burn | `S -= x`, `B += x` | `V = S + D + B - R` |
| Source-chain release | `V -= x`, `R += x` | `V = S + D + B - R` |
| PFTL settlement | `B -= x`, `R -= x` | `V = S + D + B - R` |

This explicitly covers the released-but-unsettled window. Immediately after source-chain release, vault balance and issued supply may again be equal, but the redemption remains operationally open until `vault_bridge_redeem_settle` removes both `B` and `R`.

### 2.2 Comparison by evidence and authority

| Design | Evidence accepted for a credit | Rule and upgrade authority | Source fact checked by destination |
|---|---|---|---|
| Guardian bridge, Wormhole class | Committee signatures | Application contract and its committee/admin surface | Committee assertion |
| Issuer attestation, CCTP class | Issuer signature | Application contract and issuer authority | Issuer assertion |
| Canonical rollup bridge | Protocol-recognized state or proofs | Protocol governance | Protocol-verified fact |
| **PFTL Tier 1** | **Exact evidence plus registered-observer quorum** | **PFTL validity rules and state-committed profiles under visible L1 governance** | **Observer reports, not direct inclusion proof** |
| **PFTL Tier 2** | **Receipt-inclusion proof against governed header anchor** | **Same validity-rule locus; proof verifier selected by profile** | **Receipt inclusion; checkpoint correctness remains governed** |
| **PFTL Tier 3–4** | **Permissionlessly verifiable entry and exit finality proofs** | **Visible L1 governance for validity-rule changes** | **Finalized cross-chain facts** |

A Tier-1 evidence record can be syntactically perfect and still be false. The observer quorum is what rejects that *well-formed lie*—unless enough observers collude or share a common failure. Tier 2 removes that observer-collusion path for receipt inclusion, while Tier 3 verifies the header’s finality rather than trusting a governed checkpoint.

## 3. Technical specification: what exists today

The implementation is in [`postfiatorg/postfiatl1v2`](https://github.com/postfiatorg/postfiatl1v2).

Normative and implementation references include:

- `docs/vault-bridge-deposit-evidence-spec.md`;
- `crates/execution/src/nav_vault_asset_execution.rs`;
- `crates/types/src/core_chain.rs`; and
- `crates/ethereum-contracts/src/`.

### 3.1 Source-chain vault

`ERC20BridgeVault` holds the external stablecoin on source chain id `42161`, Arbitrum One, for native USDC. Its deposit interface is permissionless:

```solidity
function deposit(uint256 amount, string calldata pftl_recipient, bytes32 nonce)
    external nonReentrant returns (bytes32 deposit_id)
```

The vault derives:

```text
deposit_id = keccak256(abi.encode(
    "postfiat.erc20_bridge.deposit.v1",
    block.chainid, vault, token, depositor,
    amount, keccak256(pftl_recipient), nonce))
```

This binds the source chain, vault, token, depositor, amount, recipient hash, and nonce. Evidence naming another recipient fails recomputation.

The current administrative surface includes an owner-held pause and a designated challenge authority. These remain Tier-1 trust and liveness dependencies. The target posture retires administrative control in favor of an immutable, unpausable vault and permissionless bonded challenges.

### 3.2 Deposit evidence

A deposit becomes a twelve-field `VaultBridgeDepositEvidence` record containing:

- source chain id;
- vault and token addresses;
- depositor;
- PFTL recipient and recipient hash;
- amount in atoms;
- nonce;
- deposit id;
- block hash;
- transaction hash; and
- log index.

`deposit_id` and `pftl_recipient_hash` are re-derived during validation. They are not trusted as free-standing assertions.

The node CLI operation `vault-bridge-deposit-relay-rpc-bundle` builds evidence from a live source-chain receipt. The relay transports evidence but does not make it valid.

### 3.3 Four-operation credit ceremony

#### 1. `vault_bridge_deposit_propose`

Admission requires:

- a registered asset using a `vault_bridge:<source_domain>` proof profile;
- a matching source policy and policy hash;
- an unexpired proposal;
- an evidence root that recomputes from the submitted fields; and
- no existing `(asset_id, evidence_root)` pair.

Duplicate evidence roots are therefore rejected structurally.

#### 2. `vault_bridge_deposit_attest`

Each attestor must be a registered, identity-bearing observer. Its observation must match the evidence exactly:

- the transaction exists;
- receipt status is success;
- source chain id matches;
- vault matches;
- token matches;
- depositor matches;
- amount matches;
- deposit id matches;
- block hash matches;
- transaction hash matches;
- log index matches; and
- confirmation depth satisfies `bridge_observer_min_confirmations`.

These are discrete EVM facts, so `tolerance_bp` does not apply. The rule is exact equality.

Distinct observer identities do not by themselves prove operational independence. Shared RPCs, infrastructure, or control can create common-mode failures even when registrations are distinct.

#### 3. `vault_bridge_deposit_finalize`

Finalization requires:

```text
pass_count >= min_attestations
fail_count == 0
```

A single recorded failure blocks finalization. The operation also enforces challenge-window and snapshot-age rules.

#### 4. `vault_bridge_deposit_claim`

The claimant and amount must match the evidence. Issued supply uses checked addition and cannot exceed `max_supply`.

A `vault_bridge_deposit_challenge` can contest a proposal during its window and is bonded by `min_challenge_bond`.

The development-network profile uses a quorum of 3 observers and a minimum confirmation depth of 6. These are profile parameters, not universal security constants. Six confirmations do not eliminate the possibility of a deeper source-chain reorganization.

Activation is governed through `ratify-bridge-verification-activation-height`. Observer registration, quorum sizes, source bindings, and confirmation requirements are visible in state rather than controlled through a relayer toggle.

### 3.4 Redemption lifecycle

Redemption has three accounting stages and five source-chain verifier/vault operations.

#### Stage 1: burn on PFTL

The user submits:

```text
vault_bridge_burn_to_redeem
```

The operation burns wrapped atoms, names a source-chain recipient in the form:

```text
evm-erc20:42161:<address>
```

and produces a redemption id.

Accounting transition:

```text
S -= x
B += x
```

#### Stage 2: verify and release on the source chain

A withdrawal packet is digest-bound to the redemption and proceeds through:

```text
submitProof
→ finalizeProof
→ submitWithdrawal
→ finalizeWithdrawal
→ claimWithdrawal
```

The packet clears a challenge window at the verifier and another at the vault before release.

When the vault releases `x` atoms:

```text
V -= x
R += x
```

At this point the user has received the source asset, but PFTL has not yet closed the redemption. `B` remains outstanding and `R` records that the outstanding redemption has already been released.

The source-chain verifier currently uses an interim threshold posture. Compromise of the required threshold can affect exit safety; unavailability of the threshold can halt exits.

#### Stage 3: settle on PFTL

`vault_bridge_redeem_settle` requires a quorum of withdrawal observations. Each observation must match the withdrawal packet exactly and carry a valid observer signature.

Settlement applies:

```text
B -= x
R -= x
```

The redemption is then closed on both sides of the accounting model.

### 3.5 Reserve and NAV integration

Four additional consensus kinds consume wrapped stablecoin receipts as verified reserve capacity for NAV assets:

- `vault_bridge_receipt_submit`;
- `vault_bridge_receipt_count`;
- `vault_bridge_mint_from_receipts`; and
- `vault_bridge_nav_subscription_allocate`.

The associated profile fields include `valuation_unit`, `valuation_policy_hash`, and `tolerance_bp`. `valuation_policy_hash` binds the selected valuation policy, while `tolerance_bp` supplies valuation tolerance for NAV processing. It is unused when validating discrete EVM deposit facts, which require exact equality.

`vault_bridge_bucket_impair` marks impaired backing buckets.

### 3.6 Guarantees and their conditions

#### Enforced unconditionally by the active PFTL rules

The following properties hold for blocks accepted under the active rules and profile:

- submitted recipient hashes and deposit ids must recompute;
- duplicate evidence roots are rejected;
- observation fields must match evidence exactly;
- finalization requires `pass_count >= min_attestations` and `fail_count == 0`;
- claims must use the evidence recipient and amount;
- checked arithmetic and `max_supply` constrain issuance; and
- rule and profile changes are visible through PFTL state and governance.

These properties establish internal consistency. They do not independently prove that a Tier-1 source-chain report is true.

#### Conditional Tier-1 safety guarantees

Tier-1 entry safety additionally requires:

- fewer than `min_attestations` registered observers collude to report a false event;
- observers do not suffer a quorum-wide common-mode data failure;
- the accepted source-chain history does not undergo a reorganization deeper than the profile’s confirmation assumption; and
- profile or activation governance is not captured and used to weaken or redirect the verification policy.

Tier-1 exit safety additionally requires:

- the threshold exit verifier is not compromised;
- the source-chain vault and challenge authority operate within their disclosed powers;
- withdrawal observers do not provide a false settlement quorum; and
- source-chain release facts remain canonical.

The statement “faults degrade liveness, never safety” is therefore valid only under these honesty, governance, verifier, and source-chain-history assumptions. Outside them, observer-quorum collusion, profile-governance capture, deep source-chain reorganizations, checkpoint-governance capture at Tier 2, and threshold-verifier compromise can violate safety.

### 3.7 Failure and recovery behavior

| Event | Immediate result | Safety or liveness effect |
|---|---|---|
| Insufficient observer attestations | Proposal cannot finalize and may expire | Liveness |
| Any recorded failed observation | Finalization blocked | Liveness under honest reporting; colluding observers remain a safety threat |
| Stale proposal or snapshot | Rejected under freshness rules | Liveness |
| Duplicate evidence root | Rejected | Replay safety |
| Relay unavailable or censoring | Another party can submit the bundle | Liveness |
| Common RPC failure across observers | Quorum may repeat the same bad view | Safety if it produces a false accepted fact |
| Deep reorganization after accepted confirmations | Previously observed fact may leave canonical history | Safety |
| Vault pause | Deposits or withdrawals may stop | Liveness |
| Challenge-authority misuse or capture | Withdrawal processing may be obstructed or improperly influenced within that authority surface | Safety or liveness, depending on action |
| Observer-quorum collusion | False Tier-1 evidence may satisfy quorum | Safety |
| Profile-governance capture | Source bindings, quorum, or verification parameters may be changed | Safety |
| Governed-checkpoint capture at Tier 2 | Proof may be anchored to an invalid header | Safety |
| Threshold exit-verifier compromise | Invalid withdrawal authorization may be accepted | Safety |
| Threshold exit-verifier unavailability | Withdrawals cannot advance | Liveness |

Permissionless relay reduces transport censorship but does not guarantee that observers, governance, the vault, or the threshold verifier remain available.

### 3.8 Tier-by-tier threat model

| Tier | Trusted parties and assumptions | Collusion or compromise sufficient to affect safety | Liveness powers | Governance and upgrade authority | Retirement at higher tiers |
|---|---|---|---|---|---|
| **Tier 1: independently observed** | Registered observers; profile and activation governance; vault owner pause; designated challenge authority; authorized role accounts; threshold exit verifier; source history after `bridge_observer_min_confirmations` | `min_attestations` observers can satisfy a false positive quorum if no failing observation is recorded; development-network value is 3. Exact governance and exit-verifier thresholds: **[TBD: maintainers]** | Observers can withhold attestations; owner can pause; challenge and role accounts can delay their gated operations; exit threshold can withhold authorization | Visible PFTL governance controls activation and state-committed profiles. Source-vault upgradeability details: **[TBD: maintainers]** | Receipt proofs retire observers from entry safety; later tiers retire checkpoint and exit-threshold trust |
| **Tier 2: receipt-proven** | Governed `EthereumFinalizedCheckpointV1` correctness; proof-system soundness; Tier-1 exit authorities remain | Checkpoint-governance capture or proof unsoundness can affect entry safety; exit threshold compromise remains sufficient for exit safety | Checkpoint updates, proof production, and existing exit actors can delay progress | PFTL governance selects the active `verifier_kind` and checkpoint policy | Tier 3 replaces governed header correctness with verified source finality |
| **Tier 3: finality-verified entry** | Sound light-client or succinct-proof pipeline; source-chain consensus; Tier-1 exit threshold remains | No observer or checkpoint collusion is sufficient for entry; proof-system failure or visible validity-rule governance capture can affect entry safety. Exit threshold compromise still affects exits | Proof production can delay entry; exit actors can delay withdrawal | Validity-rule changes remain subject to visible L1 governance | Tier 4 retires the threshold exit verifier |
| **Tier 4: proof-verified exit** | Sound entry and PFTL-finality proof systems | No observer, checkpoint, or threshold-signer collusion is sufficient for cross-chain fact verification; proof-system failure or visible validity-rule governance capture remains relevant | Proof generation or relay can delay either direction | Visible L1 governance governs validity-rule changes | Establishes the trustless round trip defined by this document |
| **Tier 5: canonical alignment** | Tier-4 proof assumptions plus Bridged USDC Standard alignment | Same bridge-verification safety posture as Tier 4 | Same proof and relay liveness dependencies | Visible L1 governance plus the canonical-alignment process | Allows the bridged representation to be superseded by native USDC issuance on PFTL |

The bridge is “trustless” only for the directions whose finalized cross-chain facts are permissionlessly verified. Tier 3 earns that term for entry. Tier 4 earns it for the round trip.

## 4. Operational guide

### 4.1 Wrap sequence

```text
 user              vault (source chain)         relay              PFTL validators/observers
  |                       |                       |                            |
  |-- approve ----------->|                       |                            |
  |-- deposit ----------->|                       |                            |
  |                       |-- Deposit event ----->|                            |
  |                       |                       |-- evidence proposal ------>|
  |                       |<~~~~ observers read source-chain receipt ~~~~~~~~~|
  |                       |                       |-- attestations ----------->|
  |                       |                       |-- finalize --------------->|
  |                       |                       |-- claim ------------------>|
  |<========== PFUSDC credited to deposit-bound recipient ====================|
```

### 4.2 Wrap procedure: USDC to pfUSDC

1. The user holds native USDC on source chain id `42161`.
2. The user calls `approve`.
3. The user calls `deposit(amount, pftl_recipient, nonce)`.
4. The vault transfers the tokens and returns a `deposit_id` binding the chosen recipient.
5. Any party runs `vault-bridge-deposit-relay-rpc-bundle` against a source-chain RPC.
6. PFTL processes `propose`, observer `attest` operations, `finalize`, and `claim`.
7. The exact atom amount is credited. A deposit of 250 USDC corresponds to 250,000,000 pfUSDC atoms.
8. The integrator checks the full conservation equation, including deposits still awaiting claim.

### 4.3 Unwrap sequence

```text
 user                    PFTL               source verifier             vault              PFTL
  |                        |                       |                      |                   |
  |-- burn_to_redeem ----->|                       |                      |                   |
  |                        |-- withdrawal packet ->|                      |                   |
  |                        |                       |-- submitProof ------>|                   |
  |                        |                       |-- finalizeProof ---->|                   |
  |                        |                       |-- submitWithdrawal ->|                   |
  |                        |                       |-- finalizeWithdrawal>|                   |
  |-- claimWithdrawal -------------------------------------------------->|                   |
  |<========================== source USDC released =====================|                   |
  |                        |<~~~~ withdrawal observers read release fact ~~~~~~~~~~~~~~~~~~~~|
  |                        |------------------------------------------------ redeem_settle -->|
  |<============================= redemption closed ========================================|
```

### 4.4 Unwrap procedure: pfUSDC to USDC

1. The user submits `vault_bridge_burn_to_redeem` and names their source-chain address.
2. The burn reduces `S` and increases `B`.
3. The digest-bound packet advances through `submitProof`, `finalizeProof`, `submitWithdrawal`, `finalizeWithdrawal`, and `claimWithdrawal`.
4. Release reduces `V` and increases `R`; the redemption is now released but unsettled.
5. Withdrawal observers attest to the exact packet and release.
6. `vault_bridge_redeem_settle` reduces both `B` and `R`, closing the lifecycle.

### 4.5 Integrator requirements

- Read all profile parameters from chain state. Do not hardcode quorum size, confirmation depth, challenge windows, deadlines, source bindings, or `verifier_kind`.
- Treat relays as untrusted transport. Verify accepted PFTL operations rather than a relayer’s report.
- Track the full accounting identity:

  ```text
  V = S + D + B - R
  ```

- Distinguish “burned but not released” from “released but not settled.” The latter has already left vault custody.
- Treat any unexplained conservation mismatch as a halt condition.
- Support self-relay where practical.
- Display the active verification tier in wallet and application UX.
- Describe Tier-1 credits as **independently observed**, not “proven” or “trustless.”
- Monitor governance changes to profiles, activation state, observer registration, source bindings, and verifier selection.
- Treat the current exit threshold as an explicit authorization dependency.

## 5. Roadmap: from observation to trustless verification

Each tier upgrades the evidence accepted by the bridge rules. Governance activation must precede any stronger public claim.

### Tier 1 — Independently observed

The current development-network system uses:

- registered observers;
- exact fact matching;
- `min_attestations`;
- `fail_count == 0`;
- source-chain confirmation minimums;
- challenge windows;
- bonded deposit challenges; and
- state-committed profiles.

The development-network profile uses 3 observers for quorum and a minimum confirmation depth of 6.

Tier-1 safety depends on preventing a quorum from colluding or sharing a false source view. Distinct registrations, infrastructure, or RPC providers can reduce common-mode risk but do not cryptographically enforce independence.

**Permitted claim:** independently observed deposits.

### Tier 2 — Receipt-proven

The entry rule upgrades to a Merkle-Patricia receipt-inclusion proof against a block’s receipts root. `verifier_kind` is the profile seam for moving from `multi_fetch` to `sp1-groth16`.

The header anchor uses the governed `EthereumFinalizedCheckpointV1` machinery. A valid inclusion proof prevents an observer quorum from inventing a receipt, but governed checkpoint correctness remains a safety assumption.

**Permitted claim:** receipt-proven deposits.

### Tier 3 — Finality-verified entry

A light-client or succinct-proof pipeline verifies source-chain finality, including Ethereum consensus and Arbitrum settlement into it, rather than accepting a governed checkpoint as authoritative.

Entry then satisfies this document’s definition of trustless verification: finalized source-chain facts are verified through a permissionless verifier.

**Permitted claim:** trustless entry.

### Tier 4 — Proof-verified exit

The source-chain verifier replaces its threshold signature check with verification of succinct proofs of PFTL consensus finality.

PFTL uses post-quantum ML-DSA signatures, which are impractical to verify directly in the EVM. The design path proves PFTL finality through the SP1/Groth16 lane and verifies a constant-size proof on the source chain. PFTL’s Halo2 private-swap stack provides the existing succinct-proof competence referenced by this roadmap.

Until this tier is activated, the threshold signer set remains the exit trust boundary.

**Permitted claim:** trustless round trip.

### Tier 5 — Canonical alignment

For USDC, the asset conforms to Circle’s Bridged USDC Standard and preserves the path for the bridged representation to be superseded by native USDC issuance on PFTL.

This tier changes canonical asset alignment rather than weakening the Tier-4 proof requirement.

**Permitted claim:** canonical-aligned USDC with a trustless bridge round trip, where Tier 4 remains enforced.

## 6. Control-minimization checklist

### Entry and evidence

- [ ] `deposit()` is permissionless
- [ ] The depositor chooses the PFTL recipient
- [ ] The recipient hash is bound into `deposit_id`
- [ ] `deposit_id` and `pftl_recipient_hash` are re-derived during validation
- [ ] Duplicate `(asset_id, evidence_root)` pairs are rejected
- [ ] Tier-1 observations match evidence exactly
- [ ] Finalization requires `pass_count >= min_attestations`
- [ ] Finalization requires `fail_count == 0`
- [ ] Tier-2 claims are not used until receipt proofs are enforced
- [ ] Trustless-entry claims are not used until source finality is permissionlessly verified

### Supply and redemption accounting

- [ ] Issuance uses checked arithmetic
- [ ] Issued supply cannot exceed `max_supply`
- [ ] Operators track `V`, `S`, `D`, `B`, and `R`
- [ ] The monitored identity is `V = S + D + B - R`
- [ ] Released-but-unsettled redemptions are recorded separately from unreleased burns
- [ ] `vault_bridge_redeem_settle` requires matching withdrawal observations
- [ ] Any unexplained accounting divergence is a halt condition

### Authority and governance

- [ ] Registered observer identities and active quorum are visible
- [ ] Operational independence is assessed separately from observer identity
- [ ] `issuer`, `reserve_operator`, and `redemption_account` are enumerated
- [ ] Vault owner pause authority is disclosed
- [ ] Source-chain challenge authority is disclosed
- [ ] Vault upgradeability is disclosed
- [ ] Exit-verifier signers and threshold are disclosed
- [ ] Profile and activation governance thresholds are disclosed
- [ ] Governance changes are visible on-chain
- [ ] Administrative authorities have explicit retirement conditions on the tier ladder
- [ ] The threshold exit verifier is not described as trustless

### Operations and public claims

- [ ] Relayers hold no verification authority
- [ ] Users can self-relay
- [ ] Integrators read profiles from state
- [ ] Confirmation depth is not described as absolute source-chain finality
- [ ] Tier 1 is labeled “independently observed”
- [ ] Tier 2 is labeled “receipt-proven”
- [ ] Tier 3 uses “trustless” only for entry
- [ ] “Trustless round trip” is used only after Tier 4 activation
- [ ] Bridged USDC Standard alignment is tracked separately from proof-verification status

## 7. Scope and limitations

This document describes the PFTL development-network protocol and its design-committed roadmap. Tier 1 is active under a governance-activated height; Tiers 2–5 are not the currently enforced evidence standard. Development-network parameters must be read from chain state.

This is a public research primer, not an audit or mainnet deployment announcement. Exact deployed contract addresses, activation heights, pinned source commit hashes, observer-set composition, observer compensation or slashing arrangements, bond-sizing rationale, governance thresholds, exit-verifier signers and threshold, and source-vault upgradeability are **[TBD: maintainers]**. No quantified economic claim about the cost of observer collusion follows from `min_challenge_bond`, `min_attestations`, or `max_supply` alone.

The current profile’s confirmation depth of 6 is an acceptance parameter, not a proof of Arbitrum or Ethereum finality. Tier 1 remains exposed to deeper source-chain reorganizations and observer common-mode failures. Tier 2 remains exposed to governed-checkpoint correctness. The exit remains threshold-authorized until Tier 4.

This document is not legal, regulatory, or investment advice.

---

## Appendix A — Deposit evidence schema

`VaultBridgeDepositEvidence` is specified in `docs/vault-bridge-deposit-evidence-spec.md`.

| Field | Type | Validation binding |
|---|---|---|
| `source_chain_id` | u64 | Must equal the profile’s registered source chain |
| `vault` | EVM address | Must equal the profile’s registered vault |
| `token` | EVM address | Must equal the profile’s registered token |
| `depositor` | EVM address | Bound into `deposit_id` |
| `pftl_recipient` | PFTL address text | Chosen by the depositor |
| `pftl_recipient_hash` | bytes32 | Re-derived as `keccak256(pftl_recipient)` |
| `amount_atoms` | u64 | Claim amount must equal this value |
| `nonce` | bytes32 | Depositor-chosen replay salt |
| `deposit_id` | bytes32 | Re-derived from the domain-separated tuple |
| `block_hash` | bytes32 | Observed at Tier 1; proven at Tier 2+ |
| `tx_hash` | bytes32 | Must exist with receipt status 1 |
| `log_index` | u64 | Deposit-event position |

Tier-1 observations require exact equality on:

```text
source_chain_id
vault
token
depositor
amount_atoms
deposit_id
block_hash
tx_hash
log_index
```

They additionally require:

```text
tx_exists
receipt_status == 1
confirmation_depth >= bridge_observer_min_confirmations
```

No tolerance band applies to these facts.

### Deposit identifier

```text
deposit_id = keccak256(abi.encode(
    "postfiat.erc20_bridge.deposit.v1",
    block.chainid,
    vault,
    token,
    depositor,
    amount,
    keccak256(pftl_recipient),
    nonce
))
```

## Appendix B — Transaction kind reference

The twelve `vault_bridge_*` consensus kinds are defined in `crates/types/src/core_chain.rs`.

### Credit ceremony

- `vault_bridge_deposit_propose`
- `vault_bridge_deposit_attest`
- `vault_bridge_deposit_finalize`
- `vault_bridge_deposit_claim`
- `vault_bridge_deposit_challenge`

### Redemption

- `vault_bridge_burn_to_redeem`
- `vault_bridge_redeem_settle`

### Reserve and NAV integration

- `vault_bridge_receipt_submit`
- `vault_bridge_receipt_count`
- `vault_bridge_mint_from_receipts`
- `vault_bridge_nav_subscription_allocate`

### Impairment

- `vault_bridge_bucket_impair`

## Appendix C — Parameter reference

Per-asset profiles use `VaultBridgeBootstrapBundleOptions` and are committed to PFTL state.

| Parameter | Role |
|---|---|
| `source_chain_id` | Registered source chain |
| `vault_address` | Registered source-chain vault |
| `token_address` | Registered source token |
| `issuer` | Authorized role account |
| `reserve_operator` | Authorized reserve role account |
| `redemption_account` | Authorized redemption role account |
| `asset_code` | Asset identifier; pfUSDC uses `PFUSDC` |
| `asset_version` | Asset version |
| `asset_precision` | Atom precision; pfUSDC uses 6 |
| `max_supply` | Hard issuance cap |
| `verifier_kind` | Evidence standard: `multi_fetch` today; `sp1-groth16` proof seam |
| `min_attestations` | Required Tier-1 observer quorum |
| `bridge_observer_min_confirmations` | Minimum observed confirmation depth |
| `challenge_window_blocks` | Challenge window |
| `min_challenge_bond` | Required challenge bond |
| `max_snapshot_age_blocks` | Snapshot freshness limit |
| `max_epoch_gap_blocks` | Maximum epoch gap |
| `settle_deadline_blocks` | Settlement deadline |
| `tolerance_bp` | NAV valuation tolerance; unused for discrete EVM facts |
| `valuation_unit` | NAV valuation unit |
| `valuation_policy_hash` | Binding to the NAV valuation policy |

Chain constant:

```text
VAULT_BRIDGE_UNIT = 1,000,000
```

Governance and registry operations include:

- `ratify-bridge-verification-activation-height`; and
- observer registration through the on-chain attestor registry.

## Appendix D — Trust-model comparison matrix

| Property | Guardian bridge | Issuer attestation | Canonical rollup bridge | PFTL Tier 1 | PFTL Tier 2 | PFTL Tier 3–4 |
|---|---|---|---|---|---|---|
| Accepted evidence | Committee signatures | Issuer signature | Protocol-recognized proof/state | Observer quorum | Receipt proof plus governed checkpoint | Finality proofs |
| Validator action | Executes signature-checking contract | Executes issuer-verification contract | Enforces protocol rules | Enforces evidence and quorum rules | Enforces receipt proof | Enforces finality proof |
| External truth authority | Committee | Issuer | Protocol | Registered observers | Checkpoint governance for header correctness | Permissionless verifier |
| Well-formed lie possible? | If committee colludes | If issuer signs it | No under protocol assumptions | If `min_attestations` observers collude | Not for receipt inclusion; invalid checkpoint remains possible | Not under proof soundness and verified finality |
| Entry permissionless? | Yes | Yes | Yes | Deposit yes; credit ceremony-gated | Yes, subject to proof availability | Yes |
| Exit trust | Committee | Issuer | Protocol proof | Threshold verifier and challenge windows | Threshold verifier and challenge windows | Tier 3: threshold verifier; Tier 4: PFTL-finality proof |
| Rule authority | App admin/committee | Issuer/app authority | Protocol governance | Visible PFTL governance | Visible PFTL governance | Visible PFTL governance |
| Replay protection | Per design | Per design | Structural | Evidence-root deduplication and domain-separated ids | Same | Same |
| Profile visibility | Per design | Per design | Protocol state | State-committed | State-committed | State-committed |
| Accurate claim | Committee-authorized | Issuer-attested | Protocol-verified | Independently observed | Receipt-proven | Trustless entry at Tier 3; trustless round trip at Tier 4 |

## Appendix E — Integrator quick reference

### Read from chain state

- `source_chain_id`
- `vault_address`
- `token_address`
- `verifier_kind`
- `min_attestations`
- `bridge_observer_min_confirmations`
- `challenge_window_blocks`
- `min_challenge_bond`
- `max_snapshot_age_blocks`
- `max_epoch_gap_blocks`
- `settle_deadline_blocks`
- `max_supply`
- role accounts
- observer registry
- activation state

### Verify the lifecycle

```text
Deposit:   V += x, D += x
Claim:     S += x, D -= x
Burn:      S -= x, B += x
Release:   V -= x, R += x
Settlement B -= x, R -= x
```

At every lifecycle state:

```text
V = S + D + B - R
```

### Use precise public language

| Active tier | Public description |
|---|---|
| Tier 1 | Independently observed deposits |
| Tier 2 | Receipt-proven deposits |
| Tier 3 | Trustless entry |
| Tier 4 | Trustless round trip |
| Tier 5 | Canonical-aligned USDC with Tier-4 verification retained |

### Operational alerts

Treat each of the following as an investigation or halt condition:

- unexplained conservation mismatch;
- unexpected profile or source-binding change;
- unexpected observer-registry change;
- quorum or confirmation-depth reduction;
- vault pause;
- stale or repeatedly expiring ceremonies;
- source-chain reorganization affecting accepted evidence;
- release without timely PFTL settlement;
- threshold exit-verifier unavailability; or
- public claims exceeding the active `verifier_kind` and tier.
