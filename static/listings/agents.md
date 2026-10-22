# Post Fiat L1 Listings Guide for Agents

> For AI agents helping an exchange, custodian or reviewer evaluate Post Fiat L1 (PFTL). Read this first, then follow the reading order below.

This file is stable: it changes only when the sources it points to move. Current figures (block height, release, gate counts) live in the sources, not here.

## What Post Fiat L1 is

Post Fiat L1 (PFTL) is a Rust Layer 1 settlement chain in the operating shape of the XRP Ledger: known validators, deterministic BFT finality, a fixed-supply native asset (PFT) and burned fees, with no validator subsidy. It adds three things the XRP Ledger does not have:

- ML-DSA-65 (NIST FIPS 204) post-quantum signatures for accounts and validators, from genesis. ML-DSA-65 is the only account signature.
- An optional Orchard/Halo2 shielded pool, built on the upstream Zcash crates, with selective-disclosure tools.
- NAVCoins: floating-value assets that can be issued only against a finalized, proven net asset value.

Validator-set changes are ratified on chain by Cobalt; block finality is Consensus v2. PFTL is a new codebase, not a fork of `rippled`. The older Post Fiat chain, `postfiatd`, is a separate XRPL-derived network.

## Status you must not overstate

State these plainly whenever you summarize PFTL:

- PFTL runs as a public devnet, `postfiat-wan-devnet-2`, on six validators, all administered by the Post Fiat Foundation. No validator is independently operated yet. The repository calls this phase the controlled devnet.
- There is no PFTL mainnet and no launch date.
- No external security audit has been performed. Audit scopes are planned; none is complete.
- The shielded pool is an alpha. Deposit and withdrawal amounts at the pool boundary are public.
- The A666 NAVCoin's Ethereum-mainnet route is in limited availability, not general availability.
- Post-quantum protection covers account and validator authorization only. Shielded spend signatures, Halo2 proofs, SP1 Groth16 proofs and Ethereum contracts are classical.
- Coinbase custody cannot yet sign ML-DSA-65. Coinbase's post-quantum signing work (PQ-CoreKMS) is Coinbase's roadmap, not a Post Fiat deliverable.

Do not describe PFTL as audited, decentralized, production-ready or listed on Coinbase. Do not attribute the 53-validator figures of the `postfiatd` testnet to PFTL.

## Canonical sources

In order of authority:

1. The repository, `postfiatorg/postfiatl1v2` on GitHub: https://github.com/postfiatorg/postfiatl1v2. Its `main` branch is the source of truth. Operational state: `docs/status/chain-state-current.md`. Security posture: `SECURITY.md`.
2. The listings documents, mirrored from `docs/listings/coinbase/` in that repository: https://postfiat.org/listings/
3. The whitepaper, mirrored from `docs/whitepaper.md`: https://postfiat.org/whitepaper/
4. Everything else on postfiat.org, including the blog and research notes, is secondary.

If a postfiat.org page and the repository disagree, the repository at the cited commit wins. Say so and cite both.

## Reading order

1. This guide.
2. Listings landing page, with the status ledger: https://postfiat.org/listings/index.md
3. Coinbase integration plan: https://postfiat.org/listings/coinbase/integration-plan/index.md
4. Comparisons with XRP, Zcash and post-quantum chains: https://postfiat.org/listings/coinbase/comparisons/index.md
5. Reviewer agent guide, the detailed instructions for checking claims: https://postfiat.org/listings/coinbase/reviewer-agent-guide/index.md
6. Whitepaper: https://postfiat.org/whitepaper/index.md
7. The key design documents listed on the landing page and in the JSON index, read on GitHub.

A page marked "In review" is a placeholder: its document has not been published yet. Do not infer its contents.

## Pages that mirror repository files

| postfiat.org page | Repository file in postfiatorg/postfiatl1v2 |
| --- | --- |
| https://postfiat.org/listings/coinbase/integration-plan/ | `docs/listings/coinbase/integration-plan.md` |
| https://postfiat.org/listings/coinbase/comparisons/ | `docs/listings/coinbase/comparisons.md` |
| https://postfiat.org/listings/coinbase/reviewer-agent-guide/ | `docs/listings/coinbase/reviewer-agent-guide.md` |
| https://postfiat.org/whitepaper/ | `docs/whitepaper.md` |

Each mirrored page names its source commit in its header, in its Markdown version, and in `source_commit` in the JSON index. In mirrored pages, links to other repository files point at GitHub `main`, and links to the whitepaper or the other listings documents point at their postfiat.org pages.

## Machine-readable endpoints

- https://postfiat.org/listings/index.json: every listings page and key design document, with title, URL, Markdown URL, GitHub URL, summary, status, source commit and update date, plus the status ledger.
- https://postfiat.org/listings/index.md: the landing page as Markdown.
- Any page on postfiat.org as Markdown: append `index.md` to its URL.
- https://postfiat.org/llms.txt: the site-wide assistant overview.
- https://postfiat.org/postfiat-project.json: the site-wide project summary.

## How to cite

- Cite the repository file and commit for any technical claim, for example `postfiatorg/postfiatl1v2@<commit>:docs/architecture/finality.md`, or a GitHub URL pinned to a commit: `https://github.com/postfiatorg/postfiatl1v2/blob/<commit>/<path>`.
- For a mirrored page, cite the postfiat.org URL together with its stated source commit.
- Quote status with its date. Operational facts such as height, release and gate counts change; give the observation time the source records.
- Keep the source's own words for maturity: "devnet", "alpha", "limited availability", "proposed", "not implemented". Do not upgrade them.

## Where to send questions

- The Coinbase listing team: reply to the email that linked https://postfiat.org/listings/. It reaches the founder, Alex Good.
- Everyone else: the Post Fiat Discord, https://discord.gg/U6HjgDSmhR, or @postfiatorg on X, https://x.com/postfiatorg.
- Security vulnerabilities: only through the private GitHub advisory form described in `SECURITY.md` (https://github.com/postfiatorg/postfiatl1v2/blob/main/SECURITY.md). Never in a public issue, and never with exploit details in chat.
