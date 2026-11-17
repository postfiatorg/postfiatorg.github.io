# Post Fiat Explorer: specification

**Status:** version 1 of this specification, 17 November 2026. It describes the explorer at
`postfiat.org/explorer/`, linked from the Task Node wallet.

## 1. What it is

The Post Fiat Explorer is the public window onto two networks:

1. **The devnet** (`postfiat-wan-devnet-2`), the new Post Fiat ledger. NAVCoins, PFUSDC,
   private swaps and the Ethereum bridge live here.
2. **The Task Node network** (the original `postfiatd` chain, network 2025). Task rewards,
   content pointers and profile NFTs live here.

A reader lands on a transaction and sees a sentence, then the evidence:

> **5,000 B24 created for 5,024.61 PFUSDC** at a NAV of $0.999922. Block 1,392, accepted,
> 5 of 6 validators voted for it.

Every page answers three questions in this order: what happened, was it accepted, and how
can I check it myself.

## 2. Who uses it

| Reader | Comes from | Wants |
| --- | --- | --- |
| Wallet user | A link in the Task Node wallet after a transaction | Proof that the deposit, swap or withdrawal went through, and where the funds are now |
| NAVCoin holder | A coin page | The history of NAV checks for the coin and the reserves behind it |
| Task Node contributor | A reward notice | The reward payment, the task it paid for, and the content pointer |
| Reviewer or auditor | A report or a tweet | Raw fields, hashes, validator signatures, and a way to recompute |
| Curious visitor | postfiat.org | A sense of what the network does, shown live |

## 3. What people do on these networks

The design follows measured use. Both tables come from a full read of each chain on
17 November 2026.

### 3.1 Devnet: 1,486 operations in 1,436 blocks, 73 addresses, 15 assets

| Lens | Operations on chain | Count |
| --- | --- | ---: |
| **Bridge** (USDC ↔ PFUSDC) | `vault_bridge_deposit_propose`, `_finalize`, `_claim`, `_attest`, `_fast_ingress_lifecycle`, `_burn_to_redeem`, `_redeem_settle`, `_nav_subscription_allocate`, `_bucket_impair` | 346 |
| **Payments** | `transparent_transfer` (PFT), `issued_payment` (assets), `trust_set` | 318 |
| **NAVCoin market** (create and cash in at NAV, Ethereum handoff) | `pftl_uniswap_order_reserve`, `_order_release`, `_primary_subscribe`, `_primary_subscribe_v2`, `_primary_redeem`, `_export_debit`, `_destination_consume`, `_return_import`, `_redemption_fund`, route `_init`, `_init_v2`, `_epoch_advance`, `_pause` | 285 |
| **Private** (shielded pool) | `asset_orchard_ingress_v2`, `shielded_swap_v1`, `asset_orchard_private_egress_v1`, `asset_orchard_private_primary_issue_v1`, `_private_primary_redeem_v1`, `asset_orchard_egress_v1` | 178 |
| **NAV checks** | `nav_profile_register`, `nav_asset_register`, `nav_attestor_register`, `nav_reserve_submit`, `nav_reserve_attest`, `nav_epoch_finalize`, `nav_mint_at_nav`, `nav_redeem_at_nav`, `nav_redeem_settle`, `nav_halt`, `asset_create`, `asset_burn` | 180 |
| **Swaps and orders** | `offer_create`, `offer_cancel`, atomic swaps, `fx_fix_register_v1`, `fx_fix_reservation_create_v1`, `market_ops_*` | 77 |
| **Fast lane** | owned deposits, committee control, anchor checkpoints | 60 |
| **Network** (governance) | amendments, bridge route profile activations, validator key rotations, authority transitions, storage activation | 42 |

Receipts: 1,391 accepted, 49 fast-lane deposits applied, 15 offers filled, the rest
rejections with a stated reason. A rejection is a first-class result and is shown as one.

### 3.2 Task Node network: 2,092 transactions in the last 6,000 ledgers (about 6.7 hours)

| Lens | Transaction | Count |
| --- | --- | ---: |
| **Payments** | `Payment` in PFT between accounts | 1,674 |
| **Profile NFTs** | `NFTokenMint` with an `ipfs://` URI, `NFTokenBurn` | 401 |
| **Task rewards** | `Payment` carrying a `pf.ptr` memo of kind REWARD: an IPFS content ID, a task ID and flags | 16 |
| **Network** | `UNLModify` (validator list changes) | 1 |

The `pf.ptr` memo (format `v4`) is the Task Node's on-chain pointer. It names an IPFS content
ID, a content kind (task, task update, submission, chat, context, reward, policy, identity,
asset, document, system), an optional task, thread or context ID, and flags (encrypted,
public, ephemeral, tombstone, multipart). The explorer decodes all of it.

## 4. Principles

1. **A sentence first.** Each operation has a plain-English summary built from its fields.
   The raw record is one click below, never hidden and never the first thing shown.
2. **Journeys, not rows.** A USDC deposit is three ledger operations and one Ethereum
   transaction. The explorer shows it as one journey with four steps.
3. **Private means visibly private.** A shielded action shows exactly what the public can
   see and names what is sealed. It never guesses an amount or a party.
4. **Checkable, and honest about how far.** Every figure carries its source: the block,
   the receipt, the validator votes, the Ethereum transaction. Each page states the
   evidence level it rests on (section 8) and gives the exact call that returns the same
   record from a validator.
5. **Calm.** Ivory paper, black ink, one accent. Motion only where something changed.

## 5. Pages

### 5.1 Home

- **Pulse:** current height, time since the last block, validators agreeing, operations in
  the last 24 hours.
- **What the network is doing:** the eight lenses of 3.1 as a ruled row of counts. Selecting
  one filters the stream below.
- **Stream:** the latest operations as sentences, newest first, updating live.
- **Latest blocks:** height, proposer, kind, operations, votes.
- **NAVCoins:** one line per coin with NAV, supply, last check and a sparkline of NAV.
- **Network switch:** Devnet or Task Node network. The choice is in the URL.

### 5.2 Block

Height, hash, parent, state root, kind (transparent, shielded, governance), proposer and
view. The certificate is drawn as six marks, one per validator: filled for a recorded accepting
vote, empty for none, with the signature scheme (ML-DSA-65), the quorum and the evidence
level. Below it, the
block's operations as sentences and its receipts.

### 5.3 Transaction

- The sentence, the result (accepted, filled, or rejected with the reason), the fee burned.
- **Parties** with roles (owner, issuer, subscriber, recipient), each linked to its account.
- **Journey panel** when the operation is a step of a journey (5.7, section 9).
- **Fields:** every field of the operation, labelled, with asset IDs resolved to names and
  amounts shown in units.
- **Raw:** the signed payload as JSON, with a copy button.
- **Check it yourself:** the evidence level, the block it is in, the receipt, and the read
  call, with the full ID, that returns the same data from a validator.

**Worked example.** Transaction `c833c343…fb9dc` on the devnet, as its page shows it:

| Part | Content |
| --- | --- |
| Sentence | **0.25 PFUSDC burned to withdraw 0.25 USDC** to `0xf77b…f7e1` on Ethereum |
| Result | Accepted at block 1,395. Fee burned: 23 atoms of PFT |
| Parties | Owner `pfab9b92…6353`; issuer `pf23d883…9ba8` |
| Fields | `operation` vault_bridge_burn_to_redeem; `asset_id` `02c46a36…5d7b` (PFUSDC); `amount_atoms` 250000 (0.25); `bucket_id` `a1dbe540…f090`; `epoch` 58; `destination_ref` `evm-erc20:1:0xf77b…f7e1`; `sequence` 326 |
| Signature | ML-DSA-65, public key 1,952 bytes, signature 3,309 bytes, both shown in Raw |
| Block | Hash `c0791cb4…`, state root `7fd3b2f0…`, proposer validator-3, votes from validators 0 to 4 (5 of 6, quorum 5) |
| Journey | USDC withdrawal: burn at 1,395 (done) → Ethereum payout `0x21bbaf84…718b` (confirmed, 0.25 USDC to the same address) |
| Evidence level | Cross-checked: two validators report the same block hash and state root |
| Check it yourself | `{"method":"tx","params":{"tx_id":"c833c343a8da52c5b472879558e55a420f925793f97aa0e4d0a4d600e37b9f9dd23bcc1198d675b05bece6fba21fb9dc"}}` sent to any validator returns the receipt, the block and its signed certificate. The payout is the vault's withdrawal log in Ethereum transaction `0x21bbaf84293965d73644a7700941ff3e9969862afc7e010f3b74f768a2bf718b` |

### 5.4 Account

Address, PFT balance and sequence, asset balances with value where a NAV exists, open
offers, and the account's operations as sentences. Known addresses carry a role label
(issuer of B24, bridge issuer, faucet, validator). On the Task Node network, public
contributor handles from the Task Node leaderboard label their wallets.

### 5.5 NAVCoin

One page per coin (B24, A666, BMNRC, B23).

- **Now:** NAV per unit, supply, reserve value, proven and attested shares, freshness
  against the coin's limit.
- **NAV checks:** every reading as a row on a timeline: epoch, NAV, verified net assets,
  supply, proof profile, the block that finalized it. A chart of NAV over epochs.
- **Market:** creations and cash-ins at NAV, with the fee and the price used.
- **Ethereum:** wrapped supply, the pool, exports and returns, each linked to Etherscan.
- **Holders:** balances by address.

### 5.6 Private

- A dial: the share of blocks that are shielded (160 of 1,436 today).
- The shielded actions as sealed cards. Each card states what is public and what is not:

| Action | Public | Sealed |
| --- | --- | --- |
| Deposit into the pool (`ingress`) | The burn, the asset, the amount, the output commitment | Who can spend the note |
| Private swap | That a swap happened, the proof system, the nullifiers | Assets, amounts, both parties |
| Private create or cash-in | The route, the NAV epoch priced at, the proof | The note and its owner inside the pool |
| Withdraw from the pool (`egress`) | The recipient, the asset, the amount, the nullifier | Which deposit funded it |

### 5.7 Journeys

| Journey | Steps joined | Key |
| --- | --- | --- |
| USDC deposit | Ethereum deposit → propose → finalize → claim | deposit ID |
| USDC withdrawal | burn → redeem settle → Ethereum payout | burn transaction |
| Create a NAVCoin | reserve → subscribe → (export) | reservation ID |
| Cash in a NAVCoin | redeem → settle | redemption ID |
| Bridge to Ethereum | export debit → Ethereum mint → destination consume | packet hash |
| Return from Ethereum | Ethereum burn → return import | packet hash |

A journey page draws its steps left to right with the height of each, shows which step is
pending, and states the amount at each step.

### 5.8 Market

Open offers by pair, fills, cancellations, atomic swaps and fixed-rate reservations.

### 5.9 Network

Validators with blocks proposed and votes cast; governance amendments in order with the
height each took effect; fast-lane committee events.

### 5.10 Task Node network

- **Rewards:** each reward payment as "2.70 PFT paid to @handle for task `task_097c…`",
  with the content ID and its flags. Encrypted content is labelled encrypted and is never
  fetched.
- **Pointers:** all `pf.ptr` memos by kind.
- **Profile NFTs:** mints and burns with the image when the URI resolves on the public
  gateway.
- **Payments** and **validator list changes**.
- Ledger and transaction pages with close time, result and fee.

### 5.11 Search

One box. It accepts a block height, a ledger index, a transaction ID, a `pf…` or `r…`
address, an asset ID or name (B24), a route ID, a deposit ID, an IPFS content ID, a task ID,
or an Ethereum transaction hash, and goes straight to the page.

## 6. Design

The explorer uses the site's stylesheet (`assets/css/ink.css`) and adds nothing to its
palette.

| Element | Treatment |
| --- | --- |
| Page | Ivory paper `#f2eee5` with the site's grain; black ink `#10191d` |
| Headlines, sentences, large numbers | Instrument Serif |
| Body text | Newsreader |
| Hashes, addresses, labels, table headers | JetBrains Mono, small caps spacing for labels |
| Accent | Petrol teal `#057f82` for links, live marks and the current selection |
| The one warning colour | Oxblood `#7a1f1f`, for rejections only |
| Structure | Hairline rules and ledger tables; no cards with shadows, no rounded corners |
| Private | Night sections (`#0b0f10`) carry everything shielded, so privacy has its own look |
| Motion | A new row draws its rule left to right once; the live dot pulses; nothing else moves |
| Hashes | Shortened as `ab12cd34…ef56`, full value on hover and on copy |
| Time | Relative with the exact UTC time on hover |

The masthead and footer are the site's own partials. The page works at 360 px wide, with
tables collapsing to stacked rows as the site's ledger tables do. All state is in the URL,
so every view can be linked. The page meets WCAG AA contrast and is fully usable by
keyboard.

## 7. Architecture

```
postfiat.org/explorer/  (static page in the site repository)
        │  HTTPS, JSON, read-only
        ▼
Explorer API  /api/explorer/v1/…   (public, cached, no sign-in)
        │
Indexer service (loopback, beside the validators)
   ├── SQLite index: blocks, operations, receipts, journeys, accounts, NAV checks
   ├── tails the devnet through the validators' read RPC
   └── tails the Task Node network through its public RPC
```

**Why an index.** A read from a validator costs 3 to 5 seconds (measured) and returns at
most 512 records. Blocks carry 178 KB of signatures each. The explorer never reads a
validator on a page view. The indexer reads each new block once and serves everything else
from SQLite.

**Indexer.** One process. It backfills history from a one-time export, then polls the
chain tip every 5 seconds and reads only new blocks. For each block it stores a slim header
(no signature bytes, votes by validator), the batch payload, and the receipts. It derives
the lens, the sentence, the parties, the assets and the journey key for each operation. It
refreshes coin state (NAV, supply, routes) once per new block.

**Task Node network tail.** The indexer follows validated ledgers from
`rpc.testnet.postfiat.org`, stores transactions, decodes `pf.ptr` memos and NFT URIs, and
reads the public Task Node leaderboard hourly for handle labels.

**API.** Read-only GET endpoints returning JSON:

| Endpoint | Returns |
| --- | --- |
| `/summary` | Pulse, lens counts, coins |
| `/stream?lens=&before=` | Operations as sentences, paged |
| `/blocks?before=` and `/block/{height}` | Headers; one block with operations and receipts |
| `/tx/{id}` | One operation with fields, receipt, journey |
| `/account/{address}` | Balances and operations |
| `/coins` and `/coin/{slug}` | Coin state and NAV check history |
| `/journeys?kind=` and `/journey/{key}` | Journeys and their steps |
| `/private` | Shielded share and actions |
| `/network` | Validators, amendments |
| `/tasknode/summary`, `/tasknode/stream`, `/tasknode/tx/{hash}`, `/tasknode/account/{r}` | The Task Node network lens |
| `/search?q=` | The page a query resolves to |

Responses carry `Cache-Control: public, max-age=5` and the height they were built at.
Lists page by cursor. The API allows the `postfiat.org` origin.

**What is stored and what is fetched.** The index holds, for every block: the hash, parent,
state root, proposer, view, certificate ID, quorum, and each vote's validator and vote ID.
It does not hold the 3,309-byte signatures. When a reader opens "Check it yourself", the
API fetches the full signed block from a validator once, checks that its hash and
certificate ID equal the indexed ones, and caches it on disk. The validator registry and
its two key rotations (block 917) are indexed, so each vote is shown with the key in force
at that height.

**Two sources agree or the page says so.** The indexer reads each new block from one
validator and its hash and state root from a second. If they differ, the block is stored as
disputed, the Home page shows an oxblood notice, and no sentence is published for it until
they agree.

**History.** The first 1,436 blocks were loaded from a one-time export of one validator's
store and checked against the validators: every block hash chains to its parent, and the
tip's state root equals the root all six validators report. From there the indexer only
appends.

**Front end.** One HTML page from a Hugo layout and one JavaScript file, no framework and
no build step, matching how the site's other live pages are made. It polls `/summary` every
5 seconds and fetches only what the current view needs.

**Hosting.** The page ships with the site. The API runs beside the validators and is
published through the Task Node's existing relay path as
`tasknode.postfiat.org/api/explorer/v1`.

## 8. Trust and evidence levels

The explorer is a reader of the network, and it says what it has and has not checked. Every
block, operation and journey step carries one of three levels, shown as a small label next
to the result:

| Level | What the explorer did | Wording on the page |
| --- | --- | --- |
| **Reported** | Read the record from one validator | "Reported by validator-N" |
| **Cross-checked** | Read the block hash and state root from a second validator and found them equal; checked that the block's parent hash equals the previous block's hash | "Cross-checked with validator-M" |
| **Verified** | Checked every vote's ML-DSA-65 signature against the registry key in force at that height, and that the accepting votes reach the quorum | "Signatures verified" |

Version 1 reaches Cross-checked for every block. It never uses the word "verified" for a
devnet record: the Verified level is reserved for the build step in which the indexer runs
the node's own certificate verifier over each block, and until then no page claims it. The
words "signed", "proof" and "verified" appear only where the explorer has checked a
signature or a proof itself. A vote the explorer has only read is called a recorded vote.

Cross-checking detects a validator that answers differently from another. It does not
establish that a certificate is valid or that the state is correct, and the "Check it
yourself" panel says so in one line.

## 9. Ethereum evidence and journey states

A journey step on Ethereum is shown as done only when the explorer has read it from
Ethereum itself. A matching ID on the devnet is a correlation and is never presented as an
Ethereum fact.

**What is read.** The indexer follows Ethereum mainnet through one configured RPC provider
and reads logs from four contracts:

| Contract | Address | Events used |
| --- | --- | --- |
| USDC vault | `0xE7A432a28b20621A70E845C7F202004Cf98e7A2C` | deposit (deposit ID, depositor, amount, recipient), withdrawal (burn ID, recipient, amount) |
| Handoff controller | `0x2C7DB4C2fF8514334F62e6630226E95e72Fa6056` | receipt accepted, mint, return burn (packet hash, amount) |
| wB24 token | `0x540FDa223a2198690d31920a921A0b9DfF335dbF` | transfers to and from the zero address (wrapped supply) |
| Receipt verifier | `0x01d3A6032dF5f892dFa8a1Fc11F04f1c123C985F` | checkpoint advanced (height) |

Other coins add their own rows from the route registry on the devnet, which names each
route's contracts.

**Finality.** An Ethereum log counts once its block is at or below Ethereum's `finalized`
block. Until then the step shows as "seen, not final". A log that disappears before
finality is removed and the step returns to pending.

**Step states.** Every journey step is in exactly one of seven states:

| State | Meaning | Shown as |
| --- | --- | --- |
| Done | On the devnet: an accepted receipt. On Ethereum: a finalized log whose ID, amount and recipient equal the devnet step | Filled mark, height or Ethereum block |
| Seen, not final | Ethereum log found, block not yet finalized | Half mark with "awaiting Ethereum finality" |
| Pending | The step before it is done and this one has not appeared | Empty mark with how long the journey has waited |
| Not started | An earlier step is not yet done | Faint empty mark, no timer |
| Mismatched | The step exists but its ID, amount or recipient differs from the step it should complete | Oxblood mark with both values |
| Rejected | A devnet receipt that was not accepted | Oxblood mark with the reason |
| Unknown | The explorer cannot read the source (provider down, history not indexed) | Dashed mark with "not checked", never "pending" |

A journey is complete only when every step is Done. One Rejected, Mismatched or Unknown
step makes the whole journey show that state in its summary line.

## 10. Staleness and failure

- Every response carries the height and the time it was built. The page shows
  "index at 1,436 · chain at 1,436" in the pulse; when they differ by more than two blocks
  or one minute, it says the index is behind and by how much.
- If the API cannot be reached, the page keeps the last data, greys the live mark and says
  so. It never shows an empty network.
- If the validators cannot be read, the indexer keeps serving what it has and marks coin
  state with the height it was read at.
- A rejected operation has its own page with the receipt code and message, and appears in
  the stream as a rejection.

## 11. Time

The devnet ledger records no clock time. The explorer shows three kinds of time and labels
each:

- **Observed:** when the indexer first saw a block. Exact for every block from the day the
  indexer starts.
- **Ethereum:** for bridge and handoff steps, the timestamp of the finalized Ethereum block.
- **Order:** for older blocks, the height alone.

The Task Node network has ledger close times, and they are used as they are.

## 12. Acceptance

The explorer is correct when all of these hold:

1. **Counts reconcile.** The lens counts on Home equal the table in 3.1 at the same height:
   1,486 operations in 1,436 blocks.
2. **Every block is complete.** For each height, the receipts shown equal the block's
   receipt count.
3. **Spot checks match the validators.** Twenty transactions chosen at random are fetched
   from a validator and equal the explorer's fields.
4. **Coin figures match the coin pages.** NAV and supply for each coin equal the Task Node
   coin page at the same height.
5. **Journeys close.** The 5,025 USDC deposit of 16 November
   (`0x009c8320…2f85`) shows propose, finalize and claim; the 0.25 USDC withdrawal at
   height 1,395 shows its burn and its Ethereum payout `0x21bbaf84…718b`, read from
   Ethereum at a finalized block, with the same amount (0.25 USDC) and recipient as the burn.
6. **Privacy holds.** No page shows an amount, asset or party that the chain does not
   publish for a shielded action.
7. **Rewards decode.** A reward on the Task Node network shows its content ID, task ID and
   flags exactly as the memo carries them.
8. **States are honest.** With the Ethereum provider switched off, Ethereum steps show
   "not checked" and no journey shows as complete.
9. **Disagreement is visible.** In a test where the second validator's answer is altered,
   the block is shown as disputed and produces no sentence.
10. **No overclaim.** No devnet page contains the words "verified" or "proof checked" in
    version 1, and every result shows its evidence level.
11. **Speed.** Home paints in under one second on a laptop; a new block appears within ten
   seconds of the validators agreeing on it.

## 13. Build order

1. Indexer with the full devnet history, the summary, stream, block, transaction and
   account endpoints.
2. The page: Home, Block, Transaction, Account, Search.
3. NAVCoin pages and NAV check history.
4. Journeys for the bridge and the NAVCoin market.
5. Private page.
6. Task Node network lens.
7. Market and Network pages.
8. Publication behind the relay and the link from the Task Node wallet.
9. Signature verification of every certificate with the node's verifier, which unlocks the
   Verified level.

## 14. Limits of version 1

- Devnet block times before the indexer's first day are unknown; those blocks show height
  only.
- The public Task Node RPC keeps about 80,000 ledgers (roughly four days). Older history
  needs the archive node.
- Ethereum reading arrives in build step 4. Until then every Ethereum step shows "not
  checked".
- Encrypted pointer content is never opened. The explorer shows that it exists and where.
- Balances come from the validators at the current height; historical balances are not
  reconstructed.
