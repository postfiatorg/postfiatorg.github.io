# NAVCoin Proof-of-Reserves Devnet Evidence — 2026-06-10

Artifacts backing the implementation-status section of
[The NAVCoin Proposal](/blog/navcoin-proposal/). All runs executed on
controlled multi-validator devnets of the Post Fiat L1.

| File | What it shows |
|---|---|
| `navcoin-current-infra-report.json` | Phase 0 lifecycle end-to-end: NAV asset registration, reserve packet submit/finalize, supply-capped mint, DEX swap, redemption claim, state-root convergence across 4 validators. |
| `hyperliquid-drift-20260610T183316Z.json` | Snapshot-skew tolerance study: 10 live observations of a ~$275M Hyperliquid vault. Equity span drift 0.0005 bp; zero bit-identical observation roots — the empirical basis for verdict-based tolerance over exact matching. |
| `navcoin-multifetch-report.json` | Phase 1 end-to-end with live data: three bonded, registered observers independently fetch live Hyperliquid state for a declared reserve account, attest with three distinct observation roots under an on-chain 100 bp tolerance profile, and the reserve packet finalizes on quorum with full validator convergence. |

Verification mechanics, schemas, and the full design rationale are in
the blog post and its linked plan. Checksums:

```
a879aee1f3f699bfe467f8377ca418b53e2382d66aa8f93069b4fbfe5a79506b  hyperliquid-drift-20260610T183316Z.json
287a8137a877ab99415f9c0c788319a4b0f008fcd8f060a2fa06caf30e2dc21f  navcoin-current-infra-report.json
253ac7e8cbb3407fcb9201339f18020a8bac38a65e5520a4a22b0621566dc199  navcoin-multifetch-report.json
```
