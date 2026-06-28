# XRPL Governance Corpus Expansion

Generated: 2026-06-02T01:52:53Z

## Result

- Official known-amendment detail sections parsed: 114
- Candidate universe after incident/release-response overlays: 122
- Selected real source-backed rows: 72
- Synthetic variant seeds: 360
- Variant seeds per real row: 5
- Original 13 named seed coverage: 13 / 13

The selected rows are real amendment, incident, or release-response events. The synthetic rows are only feeder seeds and have `independence_weight=0`.

## Top Real Rows

| rank | score | cluster | event | route hint | evidence |
|---:|---:|---|---|---|---|
| 1 | 23 | nft | fixEnforceNFTokenTrustlineV2 | PROCEED_AFTER_REVIEW | A |
| 2 | 22 | nft | fixRemoveNFTokenAutoTrustLine | PROCEED_AFTER_REVIEW | A |
| 3 | 21 | permissioned-access | PermissionDelegation vulnerability and validator no-vote response | REJECT | A |
| 4 | 20 | nft | fixNonFungibleTokensV1_2 | PROCEED_AFTER_REVIEW | A |
| 5 | 20 | nft | fixEnforceNFTokenTrustline | PROCEED_AFTER_REVIEW | A |
| 6 | 20 | amm | fixAMMv1_2 | PROCEED_AFTER_REVIEW | A |
| 7 | 20 | amm | fixAMMClawbackRounding | PROCEED_AFTER_REVIEW | A |
| 8 | 19 | nft | fixNFTokenNegOffer | REJECT | A |
| 9 | 19 | permissioned-access | fixCleanup3_1_3 | PROCEED_AFTER_REVIEW | A |
| 10 | 19 | amm | AMM / XLS-30 activation vote reversal | DELAY_FOR_FIX | B |
| 11 | 18 | amm | AMM post-launch pool discrepancy | DELAY_FOR_FIX | A |
| 12 | 18 | issuer-control | EnforceInvariants | HOLD_FOR_CHALLENGE | A |
| 13 | 18 | custody-timing | DepositAuth | PROCEED_AFTER_REVIEW | A |
| 14 | 17 | batch | Batch vulnerability and validator no-vote response | REJECT | A |
| 15 | 17 | mpt | fixTokenEscrowV1 | PROCEED_AFTER_REVIEW | A |
| 16 | 16 | nft | fixNFTokenPageLinks | PROCEED_AFTER_REVIEW | A |
| 17 | 16 | batch | fixBatchInnerSigs | REJECT | A |
| 18 | 15 | permissioned-access | rippled 2.6.1 disables PermissionDelegation | REJECT | A |
| 19 | 15 | nft | NonFungibleTokensV1_1 | PROCEED_AFTER_REVIEW | A |
| 20 | 15 | permissioned-access | fixInvalidTxFlags | PROCEED_AFTER_REVIEW | A |

## Cluster Counts

| cluster | real rows |
|---|---:|
| amm | 14 |
| auth-identity | 1 |
| batch | 4 |
| consensus-liveness | 4 |
| cross-chain | 1 |
| custody-timing | 5 |
| dex-offer-path | 5 |
| fee-reserve | 1 |
| issuer-control | 4 |
| mpt | 7 |
| nft | 10 |
| permissioned-access | 9 |
| protocol-cleanup | 5 |
| vault-lending | 2 |

## Safe Integration Sentence

A follow-on evidence packet expands the XRPL governance replay source universe from 13 seeded examples to 72 real source-backed amendment, incident, and release-response rows, plus 360 clustered synthetic variant seeds that are explicitly not counted as independent incidents.

## Claim This Packet Does Not Support

The synthetic rows are not additional real-world incidents; they are clustered derivatives for adversarial training and must be reported separately.

## Files

- `candidate_universe.csv`: all parsed and overlay candidate rows.
- `real_event_corpus.csv`: selected 60+ real source-backed rows.
- `real_event_corpus.json`: machine-readable selected corpus.
- `synthetic_variant_seeds.csv`: synthetic feeder seed table.
- `summary.json`: counts and safe/unsafe claims.
- `source_receipts.json`: source fetch status and hashes.
- `SOURCE_HASHES.json`: source body SHA-256s.
- `COMMANDS.txt`: reproduction commands.
- `SHA256SUMS.txt`: evidence packet hashes.
