# XRPL Amendments Manual Review Table

Snapshot context: current XRPL known-amendments universe reviewed on 2026-06-04, limited to amendments enabled or present after 2016-06-04. `FeeEscalation` is excluded because it enabled on 2016-05-19.

Method note: this table does not infer authorship from amendment names. Where the reviewed packet had XLS provenance, the named authors are shown and classified by direct Ripple evidence or XRP-ecosystem evidence. Where the packet did not contain reviewed XLS author provenance, the author field is marked unknown.

| Amendment | Reviewed author / Ripple status | What it does |
|---|---|---|
| MultiSign | Unknown: no reviewed XLS author in packet. | Adds multi-signing and SignerList support. |
| TrustSetAuth | Unknown: no reviewed XLS author in packet. | Lets issuers pre-authorize trust lines under authorized-trustline regimes. |
| Flow | Unknown: no reviewed XLS author in packet. | Replaces the payment processing engine. |
| CryptoConditions | Unknown: no reviewed XLS author in packet. | Adds crypto-condition support, but has no practical effect without suspended payments. |
| TickSize | Unknown: no reviewed XLS author in packet. | Lets issuers control offer precision by setting tick size. |
| Escrow | Unknown: no reviewed XLS author in packet. | Adds suspended XRP payments through escrow. |
| PayChan | Unknown: no reviewed XLS author in packet. | Adds XRP payment channels. |
| fix1368 | Unknown: no reviewed XLS author in packet. | Fixes a payment rounding issue that could cause valid payments to fail. |
| fix1373 | Unknown: no reviewed XLS author in packet. | Fixes payment path-preparation failures. |
| EnforceInvariants | Unknown: no reviewed XLS author in packet. | Adds invariant checks to transaction processing. |
| SortedDirectories | Unknown: no reviewed XLS author in packet. | Sorts directory entries and fixes a directory deletion edge case. |
| fix1201 | Unknown: no reviewed XLS author in packet. | Caps transfer fees at 100 percent. |
| fix1512 | Unknown: no reviewed XLS author in packet. | Corrects PaymentChannelClaim error-code behavior. |
| fix1523 | Unknown: no reviewed XLS author in packet. | Tracks escrows by destination. |
| fix1528 | Unknown: no reviewed XLS author in packet. | Fixes validator divergence caused by timestamp handling. |
| DepositAuth | Unknown: no reviewed XLS author in packet. | Lets accounts reject unsolicited incoming funds. |
| fix1513 | Unknown: no reviewed XLS author in packet. | Applies corrected amount calculation when FeeEscalation is enabled. |
| fix1571 | Unknown: no reviewed XLS author in packet. | Tightens EscrowCreate fields and escrow behavior. |
| fix1623 | Unknown: no reviewed XLS author in packet. | Adds delivered-amount metadata for flexible CheckCash behavior. |
| fix1543 | Unknown: no reviewed XLS author in packet. | Enforces reserved transaction flag ranges. |
| DepositPreauth | Unknown: no reviewed XLS author in packet. | Lets deposit-authorized accounts preauthorize specific senders. |
| fix1515 | Unknown: no reviewed XLS author in packet. | Aligns Payment and OfferCreate liquidity consumption. |
| fix1578 | Unknown: no reviewed XLS author in packet. | Fixes OfferCreate result codes for FillOrKill offers. |
| fixTakerDryOfferRemoval | Unknown: no reviewed XLS author in packet. | Removes dry offers left behind by autobridging. |
| MultiSignReserve | Unknown: no reviewed XLS author in packet. | Lowers reserve requirements for signer lists. |
| fixMasterKeyAsRegularKey | Unknown: no reviewed XLS author in packet. | Prevents using the master key as the regular key in a way that can trap an account. |
| fixCheckThreading | Unknown: no reviewed XLS author in packet. | Adds Checks to receiver account-history metadata. |
| fixPayChanRecipientOwnerDir | Unknown: no reviewed XLS author in packet. | Adds payment channels to the recipient owner directory. |
| DeletableAccounts | Ripple / XRP ecosystem: Scott Schurr, Ripple email; Nik Bougalis, XRP ecosystem evidence. | Adds account deletion. |
| Checks | Unknown: no reviewed XLS author in packet. | Adds check-style deferred payments. |
| RequireFullyCanonicalSig | Unknown: no reviewed XLS author in packet. | Requires fully canonical transaction signatures. |
| fixQualityUpperBound | Unknown: no reviewed XLS author in packet. | Fixes unused quality-estimation code in cross-currency payment steps. |
| FlowCross | Unknown: no reviewed XLS author in packet. | Rewrites offer crossing logic using the Flow engine. |
| HardenedValidations | Unknown: no reviewed XLS author in packet. | Adds a validation attestation field for stronger consensus validation signaling. |
| fix1781 | Unknown: no reviewed XLS author in packet. | Fixes circular XRP payment path detection. |
| fixAmendmentMajorityCalc | Unknown: no reviewed XLS author in packet. | Fixes 80 percent amendment-majority rounding. |
| fixSTAmountCanonicalize | Unknown: no reviewed XLS author in packet. | Fixes an STAmount deserialization overflow edge case. |
| FlowSortStrands | Unknown: no reviewed XLS author in packet. | Improves payment-engine strand and path sorting. |
| fixRmSmallIncreasedQOffers | Unknown: no reviewed XLS author in packet. | Fixes reduced offers with distorted exchange rates. |
| TicketBatch | XRP ecosystem, not direct Ripple in packet: Nik Bougalis. | Adds tickets for out-of-sequence transaction submission. |
| NegativeUNL | Unknown: no reviewed XLS author in packet. | Tracks temporarily offline validators for quorum calculations. |
| ExpandedSignerList | Unknown: no reviewed XLS author in packet. | Expands signer lists and adds optional signer data. |
| fixRemoveNFTokenAutoTrustLine | Unknown: no reviewed XLS author in packet. | Removes an NFT trust-line flag to prevent issuer denial-of-service behavior. |
| NonFungibleTokensV1_1 | Ripple / XRP ecosystem: David Schwartz and Aanchal Malhotra, Ripple emails; Nikolaos Bougalis, XRP ecosystem evidence. | Adds native NFT support with fixes over the earlier NFT amendment. |
| CheckCashMakesTrustLine | Unknown: no reviewed XLS author in packet. | Lets CheckCash create a trust line when needed. |
| DisallowIncoming | Unknown: no reviewed XLS author in packet. | Lets accounts block incoming checks, payment channels, NFT offers, and trust lines. |
| ImmediateOfferKilled | Unknown: no reviewed XLS author in packet. | Makes immediately killed offers return tecKILLED when they do not fill. |
| fixNonFungibleTokensV1_2 | Ripple / XRP ecosystem: David Schwartz and Aanchal Malhotra, Ripple emails; Nikolaos Bougalis, XRP ecosystem evidence. | Fixes NFT edge cases including unburnable NFTs and offer behavior. |
| fixTrustLinesToSelf | Unknown: no reviewed XLS author in packet. | Deletes two historical self-trustline ledger artifacts. |
| fixUniversalNumber | Unknown: no reviewed XLS author in packet. | Unifies decimal floating-point number handling. |
| fixReducedOffersV1 | Unknown: no reviewed XLS author in packet. | Fixes rounding-reduced offers that could block order books. |
| fixNFTokenRemint | Unknown: no reviewed XLS author in packet. | Prevents duplicate NFT sequence-number collisions on remint. |
| Clawback | Ripple / XRP ecosystem: Shawn Xie, Ripple email; Nikolaos Bougalis, XRP ecosystem evidence. | Lets issuers claw back issued tokens. |
| AMM | Ripple: Aanchal Malhotra and David Schwartz, Ripple emails. | Adds a native automated market maker integrated with the XRPL DEX. |
| XRPFees | Unknown: no reviewed XLS author in packet. | Converts fee accounting units to drops of XRP. |
| fixInnerObjTemplate | Unknown: no reviewed XLS author in packet. | Fixes AMM inner-object field-template handling. |
| fixAMMOverflowOffer | Unknown: no reviewed XLS author in packet. | Fixes handling of very large synthetic AMM offers. |
| fixDisallowIncomingV1 | Unknown: no reviewed XLS author in packet. | Fixes trust-line approval behavior after disallow-incoming flags. |
| fixFillOrKill | Unknown: no reviewed XLS author in packet. | Fixes a FlowCross FillOrKill exact-rate bug. |
| fixNFTokenReserve | Unknown: no reviewed XLS author in packet. | Adds a reserve check after NFTokenAcceptOffer owner-count changes. |
| fixAMMv1_1 | Unknown: no reviewed XLS author in packet. | Fixes AMM rounding and low-quality order-book blocking behavior. |
| fixEmptyDID | Unknown: no reviewed XLS author in packet. | Prevents empty DID ledger entries. |
| fixPreviousTxnID | Unknown: no reviewed XLS author in packet. | Adds previous-transaction fields to ledger entries that lacked them. |
| DID | Ripple: Aanchal Malhotra, Ripple email. | Adds decentralized identifier ledger objects and transactions. |
| PriceOracle | Ripple: Gregory Tsipenyuk, Ripple email. | Adds on-ledger price oracle objects. |
| AMMClawback | Ripple: Shawn Xie and Yinyi Qian, Ripple emails. | Allows clawback-enabled tokens in AMMs and adds AMMClawback behavior. |
| fixEnforceNFTokenTrustline | Unknown: no reviewed XLS author in packet. | Fixes NFT transfer-fee and trustline checks. |
| fixInnerObjTemplate2 | Unknown: no reviewed XLS author in packet. | Generalizes inner-object template enforcement. |
| fixNFTokenPageLinks | Unknown: no reviewed XLS author in packet. | Fixes missing NFT directory links and adds repair or invariant checks. |
| fixAMMv1_2 | Unknown: no reviewed XLS author in packet. | Fixes AMMWithdraw reserve behavior and payment-engine AMM usage. |
| fixReducedOffersV2 | Unknown: no reviewed XLS author in packet. | Adds another reduced-offer rounding fix. |
| NFTokenMintOffer | XRP ecosystem, not direct Ripple in packet: tequ. | Allows minting an NFT and creating a sell offer in one transaction. |
| DeepFreeze | Ripple: Shawn Xie, Ripple email. | Lets issuers deep-freeze trust lines. |
| fixFrozenLPTokenTransfer | Unknown: no reviewed XLS author in packet. | Blocks blacklisted transfer of frozen LP tokens. |
| fixInvalidTxFlags | Unknown: no reviewed XLS author in packet. | Adds invalid-flag checks for credential and signer transactions. |
| DynamicNFT | Ripple-affiliated by packet evidence: Mayukha Vadari; XRP ecosystem: Vet and TeQu. | Lets authorized accounts update NFT URI data. |
| fixAMMv1_3 | Unknown: no reviewed XLS author in packet. | Adds further AMM invariant and rounding fixes. |
| fixEnforceNFTokenTrustlineV2 | Unknown: no reviewed XLS author in packet. | Prevents NFT transfer fees from bypassing token-receive restrictions. |
| fixPayChanCancelAfter | Unknown: no reviewed XLS author in packet. | Rejects payment channels whose CancelAfter time is already in the past. |
| Credentials | Ripple: Mayukha Vadari, Ripple email. | Adds on-ledger credentials for authorization and compliance use cases. |
| MPTokensV1 | Ripple / XRP ecosystem: David Fuelling and Greg Weisbrod, Ripple emails; Nikolaos Bougalis, XRP ecosystem evidence. | Adds Multi-Purpose Tokens. |
| fixDirectoryLimit | Unknown: no reviewed XLS author in packet. | Removes the directory page limit. |
| fixAMMClawbackRounding | Unknown: no reviewed XLS author in packet. | Fixes AMMClawback LP-token accounting rounding. |
| fixIncludeKeyletFields | Unknown: no reviewed XLS author in packet. | Adds identifying fields to ledger entries. |
| fixMPTDeliveredAmount | Unknown: no reviewed XLS author in packet. | Adds delivered-amount metadata for direct MPT payments. |
| fixPriceOracleOrder | Unknown: no reviewed XLS author in packet. | Canonicalizes price-oracle asset-pair order. |
| fixTokenEscrowV1 | Unknown: no reviewed XLS author in packet. | Fixes MPT escrow transfer-fee accounting. |
| PermissionedDomains | Ripple: Mayukha Vadari, Ripple email. | Adds permissioned domains for access-controlled ledger features. |
| TokenEscrow | XRP ecosystem, not direct Ripple in packet: Denis Angell. | Extends escrow to issued tokens and Multi-Purpose Tokens. |
| PermissionedDEX | Ripple: Mayukha Vadari and Shawn Xie, Ripple emails. | Adds permissioned DEX environments controlled by domains. |
| fixCleanup3_1_3 | Unknown: no reviewed XLS author in packet. | Bundles fixes for NFTs, Permissioned Domains, vaults, and lending. |
| Batch | Ripple: Mayukha Vadari, Ripple email. | Bundles multiple transactions atomically; disabled after a bug and slated for replacement. |
| ConfidentialTransfer | Ripple: Murat Cenk, Aanchal Malhotra, Ayo Akinyele, Peter Chen, Shawn Xie, and Yinyi Qian, Ripple emails. | Adds institutional-grade private Multi-Purpose Token transfers using cryptographic privacy tooling. |
| CryptoConditionsSuite | Unknown: no reviewed XLS author in packet. | Intended to add more crypto-condition suites for escrow; obsolete or incomplete. |
| DynamicMPT | Ripple: Yinyi Qian, Ripple email. | Lets issuers define mutable Multi-Purpose Token properties. |
| FlowV2 | Unknown: no reviewed XLS author in packet. | Earlier Flow version that was rejected due to a bug. |
| InvariantsV1_1 | Unknown: no reviewed XLS author in packet. | Adds additional invariant checks. |
| LendingProtocol | Ripple: Vytautas Vito Tumas and Aanchal Malhotra, Ripple emails. | Adds on-chain fixed-term uncollateralized lending using vaults and off-chain underwriting. |
| MPTokensV2 | Ripple: Gregory Tsipenyuk, Ripple email. | Extends the DEX to support Multi-Purpose Token trading. |
| NonFungibleTokensV1 | Ripple / XRP ecosystem: David Schwartz and Aanchal Malhotra, Ripple emails; Nikolaos Bougalis, XRP ecosystem evidence. | Earlier native NFT support, superseded by the later NFT amendment. |
| OwnerPaysFee | Unknown: no reviewed XLS author in packet. | Fixes transfer-fee payer inconsistency between OfferCreate and Payment. |
| PermissionDelegation | Ripple: Mayukha Vadari, Yinyi Qian, and Ed Hennis, Ripple emails. | Lets accounts delegate specific permissions; disabled after a bug and slated for replacement. |
| SHAMapV2 | Unknown: no reviewed XLS author in packet. | Changes the ledger hash tree structure; obsolete. |
| SingleAssetVault | Ripple: Vytautas Vito Tumas and Aanchal Malhotra, Ripple emails. | Adds single-asset vaults for pooled assets and lending flows. |
| SmartEscrow | Ripple-affiliated by packet evidence: Mayukha Vadari and David Fuelling. | Adds a WASM-based programmable escrow condition layer. |
| Sponsor | Ripple-affiliated by packet evidence: Mayukha Vadari. | Lets entities subsidize fees and reserves for users. |
| SusPay | Unknown: no reviewed XLS author in packet. | Adds suspended payments; replaced by Escrow. |
| Tickets | Ripple / XRP ecosystem: Scott Schurr, Ripple email; Nik Bougalis, XRP ecosystem evidence. | Earlier ticket implementation for out-of-sequence transaction submission. |
| XChainBridge | Ripple: Mayukha Vadari and Scott Determan, Ripple emails. | Adds cross-chain bridge transaction support. |
| fixBatchInnerSigs | Unknown: no reviewed XLS author in packet. | Fixes Batch inner-signature validity issues; tied to the disabled Batch amendment. |
| fixNFTokenDirV1 | Unknown: no reviewed XLS author in packet. | Fixes NFT page off-by-one and invariant issues. |
| fixNFTokenNegOffer | Unknown: no reviewed XLS author in packet. | Fixes an NFT negative-price offer bug. |
| fixXChainRewardRounding | Unknown: no reviewed XLS author in packet. | Rounds XChainBridge reward shares down. |
