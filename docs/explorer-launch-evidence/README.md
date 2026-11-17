# Devnet explorer launch: evidence packet

Checked 2026-11-17T17:53:49Z. Everything here resolves without sign-in or private-network access.

## 1. Live site

| Check | URL | Result |
| --- | --- | --- |
| Explorer page | https://postfiat.org/explorer/ | HTTP 200 |
| Public data address | https://postfiatfoundationv2.taila4ec45.ts.net:10000/api/explorer/v1/summary | `ok: true`, index height 1436, chain height 1436 |
| One operation, as a page | https://postfiat.org/explorer/#/tx/1392-0 | "5,000 B24 created for 5,024.61 PFUSDC at a NAV of $0.999922" |

## 2. Ledger totals, counted through the public data address

| Total | Stated | Counted | How |
| --- | ---: | ---: | --- |
| Blocks | 1,436 | 1,436 | every page of `/blocks` (36 pages) |
| Operations | 1,486 | 1,486 | every page of `/stream` (38 pages) |
| Receipts | 1,482 | 1,482 | distinct transaction IDs across `/stream`; each receipt belongs to one transaction ID |

`/summary` reports the same: 1,436 blocks, 1,486 operations. By kind of block: {'governance': 43, 'shielded': 160, 'transparent': 1233}.
Operations by lens: bridge 344, payments 318, navmarket 285, private 178, navchecks 180, market 77, fastlane 60, network 44.

## 3. Source

- Pull request: https://github.com/postfiatorg/postfiatorg.github.io/pull/36 (merged 2026-11-17T17:45:32Z)
- Merge commit: https://github.com/postfiatorg/postfiatorg.github.io/commit/1f9d3c0ac52365ce87a8024f26657c2045fdb735
- Specification: https://github.com/postfiatorg/postfiatorg.github.io/blob/main/docs/explorer-spec.md
- Page and script: `content/explorer.md`, `layouts/page/explorer.html`, `static/explorer/explorer.js`, `static/explorer/explorer.css`

## 4. Raw responses

- Summary: [api-summary.json](api-summary.json), fetched from `https://postfiatfoundationv2.taila4ec45.ts.net:10000/api/explorer/v1/summary`
- One transaction: [api-tx-1392-0.json](api-tx-1392-0.json), fetched from `https://postfiatfoundationv2.taila4ec45.ts.net:10000/api/explorer/v1/tx/1392-0`

The transaction response and its explorer page agree:

| Field | API response | Explorer page https://postfiat.org/explorer/#/tx/1392-0 |
| --- | --- | --- |
| Sentence | 5,000 B24 created for 5,024.61 PFUSDC at a NAV of $0.999922 | Headline of the page |
| Transaction ID | `0e40d925c1888f79ea4595ee22714f90fbe09423b9f821726dbe18f3ebe7ca7091958c8b3f9ffd0dbd9f34992bced72d` | "Transaction" row, shortened, with copy |
| Result | accepted `True`, code `accepted`, fee 23 atoms | "Accepted", "fee 23 atoms of PFT" |
| Block | 1392, proposer validator-0, 5 of 6 votes, quorum 5 | "Block 1,392", vote marks, "5 of 6, proposed by validator-0" |
| Evidence level | `cross-checked` | "Cross-checked" |
| Journey | create: Creation reserved (done, block 1391), NAVCoin created at NAV (done, block 1392) | "NAVCoin creation" panel with both steps done |

Screenshots of the live site taken with a headless browser resolving the data address as a public visitor does:
[overview](live-home.png), [transaction](live-tx.png), [B24 coin page](live-coin.png), [private page on a phone](live-m.png).

## 5. Design review by vision models

Exact prompt, sent with ten screenshots (eight at 1440 px wide, two at 390 px wide):

> score the block explorer aesthetically with a strong understanding of UX from 0-100, provide your reasoning

| Round | Model (through OpenRouter) | Score | Note |
| --- | --- | ---: | --- |
| 1 | google/gemini-4-argon | 92 | first build |
| 1 | anthropic/claude-opus-5.5 | 77 | same screenshots; harsher, so used from here on |
| 2 | anthropic/claude-opus-5.5 | 74 | a change of ours broke the private page layout |
| 3 | anthropic/claude-opus-5.5 | 84 | private page fixed, times and clickable addresses added |
| 4 | anthropic/claude-opus-5.5 | 83 | labels, numbers, transaction header, unlisted assets |
| 5 | anthropic/claude-opus-5.5 | 84 | one mark system, legends, quieter journeys table |
| 6 | anthropic/claude-opus-5.5 | 84 | last scored state; two small fixes went in afterwards and are unscored |

## 6. Known limits

1. **Ethereum is not read.** Journey steps on Ethereum show "not checked". A journey reads "done here" at most; the explorer never shows an Ethereum step as done.
2. **Validator signatures are recorded, not verified.** The explorer reads each block's votes and cross-checks the block hash and state root between two validators. It does not check the ML-DSA signatures itself and says so on every block and transaction page.
3. **Chrome on our private network is blocked from the data.** The data address is a Tailscale funnel. For a visitor on the same tailnet it resolves to a private address, and Chrome refuses a public page reading a private address. Visitors outside the tailnet are not affected. The fix is to serve the data from the Task Node domain: https://github.com/postfiatorg/tasknode/pull/410, which is **open and not merged**. Its checks fail on `npm audit` because of advisory GHSA-fc5q-39xc-vjpf against `picomatch`, a build-time dependency of Vite with no patched release; the production dependency audit is clean. The pull request is held until that gate is resolved.

Also: block times before the explorer started come from one validator's vote records, and task rewards and profile NFTs are not on this chain yet, so they do not appear.
