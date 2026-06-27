# Canonical NAVCoin Slide Diagram Spec

Working spec for replacing the current generated slide art with technical, informative process diagrams.
Do not regenerate images until this spec is reviewed.

## Global Diagram Rules

The slide images must explain the transaction mechanics. They should not be cinematic hero art, token glamour shots, abstract sci-fi architecture, dark decorative dashboards, or generic "cool crypto" scenes.

Use a clean technical diagram language:

- 16:9 landscape.
- Mostly flat process diagrams, swimlanes, state machines, tables, and relationship graphs.
- Use Post Fiat colors, but keep the visual priority on comprehension: black background, mint outlines, cyan data paths, amber gates, red rejection paths, gray retired/deprecated paths.
- Use large, sparse labels only. Prefer labels of 1 to 4 words inside the image. Exact longer text can remain in HTML below the slide.
- Each diagram must make clear what is public, private, canonical source state, venue state, proof artifact, or safety gate.
- Every arrow must have a semantic reason: state transition, proof verification, bridge message, mint/burn, or privacy boundary crossing.
- Avoid decorative coins unless they are clearly part of a process diagram.
- Avoid real brand logos. Use text labels like `Ethereum`, `Uniswap venue`, and `USDC`, but do not draw trademark-style logos.
- Avoid unlabeled icon clusters. If a shape appears, it needs a role.
- Leave a small margin around the whole diagram so it is not cropped in the web deck.

Recommended generation instruction prefix:

```text
Create a precise technical process diagram, not a stylized illustration.
Use flat infographic layout with labeled boxes, swimlanes, arrows, gates, receipts, proof artifacts, and boundary lines.
Use sparse large labels only. No decorative crypto city, no token glamour shot, no random symbols, no tiny unreadable text, no logos, no watermark.
```

## Slide 01 - PFTL Decides What Exists

Purpose: contrast the retired demo architecture with the canonical architecture.

Diagram type: two-lane comparison diagram.

Layout:

- Top lane, gray and muted, labeled `Retired demo`.
- Bottom lane, bright mint/cyan, labeled `Canonical path`.
- A vertical divider at the right labeled `Trading venue`.
- A left-side source box labeled `Truth source`.

Retired demo lane:

- Box 1: `ETH a651 token`.
- Arrow to Box 2: `ETH proof adapter`.
- Arrow to Box 3: `Uniswap pool`.
- Add a red warning badge over Box 1 or Box 2: `venue-adjacent truth`.
- Put a gray dashed label above the lane: `useful demo, not final source of truth`.

Canonical lane:

- Box 1: `PFTL reserve proof`.
- Arrow to Box 2: `PFTL supply ledger`.
- Arrow to Box 3: `PFTL bridge receipt`.
- Arrow crosses a boundary labeled `verified bridge`.
- Box 4: `wrapped ETH token`.
- Arrow to Box 5: `Uniswap venue`.
- Add a green check badge above Box 2: `official supply`.

Required relationship:

- The diagram must show that Ethereum is allowed to host a tradable representation, but PFTL owns existence.
- The retired lane should not look equally valid; it should be visibly de-emphasized.

Image labels to include:

- `Retired demo`
- `Canonical path`
- `PFTL supply ledger`
- `Bridge receipt`
- `Wrapped token`
- `Venue`
- `PFTL decides existence`

Do not include:

- Giant glowing tower as the main subject.
- A single token image with no process.
- Any implication that Uniswap validates NAV.

Animation intent:

- Reveal retired lane first in gray, then brighten canonical lane.
- Optional scan line should travel from `PFTL reserve proof` to `Uniswap venue`.

## Slide 02 - Whole Path Chain Of Custody

Purpose: show the entire transaction as a custody/proof chain, not a vague "flow".

Diagram type: horizontal swimlane flow.

Layout:

- Four horizontal swimlanes:
  - `Reserve evidence`
  - `PFTL canonical state`
  - `Ethereum venue`
  - `Orchard privacy`
- The flow moves left to right.
- Each major artifact is a box; each state transition is an arrow.

Required boxes:

1. `reserve legs`
2. `proof packet`
3. `NAV epoch`
4. `native NAVCoin`
5. `bridge packet`
6. `wrapped NAVCoin`
7. `USDC pool trade`
8. `shielded note`
9. `private egress`
10. `public exit`

Required boundaries:

- A bold vertical line between `PFTL canonical state` and `Ethereum venue`, labeled `bridge verification`.
- A dashed privacy boundary around `shielded note` and `private egress`, labeled `private wallet-side details`.

Required relationship:

- Every downstream claim must trace back to the NAV epoch or bridge packet.
- The diagram should visually answer: "What artifact proves this step is legitimate?"

Image labels to include:

- `Proof`
- `Epoch`
- `Native supply`
- `Bridge receipt`
- `Wrapped venue token`
- `Private notes`
- `Exit`

Do not include:

- Circular abstract map with unlabeled decorative stations.
- Tiny labels in empty callout boxes.

Animation intent:

- Step highlight moves left to right across the custody chain.

## Slide 03 - Proof Of Reserves Balance Sheet

Purpose: explain verified net assets and prevent the old cash-omission bug from recurring conceptually.

Diagram type: balance sheet plus formula.

Layout:

- Left side: `Reserve assets` table.
- Middle: `Arithmetic gate`.
- Right side: `Proof packet`.
- Bottom: `Not NAV` disclosure strip.

Reserve asset rows:

- `EVM spot`
- `NEAR`
- `Solana`
- `XMR`
- `Aave collateral`
- `Hyperliquid spot`
- `Hyperliquid cash`
- `uPnL`

Liability rows:

- `Aave borrow`
- `Other liabilities`

Formula in center:

- `verified net assets = spot + cash - liabilities`

Important distinction:

- Add a separate bottom box labeled `gross perp notional`.
- Connect it to `disclosure only`, not to the NAV formula.
- The visual must not add gross notional into NAV.

Proof packet fields:

- `timestamp`
- `proof hash`
- `policy version`
- `leg totals`
- `verified NAV`

Required relationship:

- Cash is included.
- Liabilities subtract.
- Gross perp notional is not a reserve asset by itself.

Do not include:

- Generic vault art without a leg table.
- A proof machine that hides the arithmetic.

Animation intent:

- Highlight asset rows, then cash rows, then liability subtraction, then output packet.

## Slide 04 - PFTL Finalizes A NAV Epoch

Purpose: show how reserve proof becomes PFTL protocol state.

Diagram type: consensus finalization sequence.

Layout:

- Left: `Reserve packet`.
- Center: six validator boxes around a verification checklist.
- Right: `Finalized NAV epoch`.

Required steps:

1. `submit reserve packet`
2. `verify proof hash`
3. `check arithmetic`
4. `check freshness`
5. `validator votes`
6. `epoch finalized`

Finalized epoch fields:

- `epoch id`
- `asset id`
- `verified net assets`
- `supply denominator`
- `NAV/unit`
- `timestamp`
- `freshness deadline`
- `proof hash`

Consensus detail:

- Show a quorum certificate as a ring or certificate box labeled `quorum certificate`.
- Do not imply one validator can finalize alone.

Required relationship:

- Before finalization: proof packet is evidence.
- After finalization: NAV epoch is chain state.

Do not include:

- Validator pillars with no checklist.
- A vague "approved" stamp without fields.

Animation intent:

- Checklist lights up, then quorum certificate closes, then epoch box becomes active.

## Slide 05 - Native NAVCoin Comes Before Wrapping

Purpose: explain native mint/release under PFTL policy.

Diagram type: policy gate flow.

Layout:

- Left: `User input`.
- Center: `NAV policy gate`.
- Right: `PFTL native balance`.

Required user input boxes:

- `pfUSDC`
- `user PFTL account`
- `amount`

Policy gate checks:

- `fresh NAV epoch`
- `supply available`
- `input counted`
- `liabilities unchanged`
- `receipt produced`

Outputs:

- `native NAVCoin balance`
- `state receipt`
- `updated supply`

Required relationship:

- Native NAVCoin is minted or released on PFTL before any wrapped token exists.
- Ethereum is absent from this slide except maybe a gray note: `venue mint not allowed here`.

Do not include:

- ETH token minting as the main action.
- A bridge before native supply exists.

Animation intent:

- Flow from user input through gate to native balance, with each gate check appearing in order.

## Slide 06 - Wrapping Is A Receipt

Purpose: show bridge wrapping as a receipt-verified representation, not a second source of supply.

Diagram type: two-chain bridge sequence.

Layout:

- Left swimlane: `PFTL`.
- Center swimlane: `Bridge proof`.
- Right swimlane: `Ethereum`.

PFTL lane:

- `native NAVCoin`
- arrow to `debit or lock`
- arrow to `finalized receipt`

Bridge proof lane:

- `packet fields`
- `finality proof`
- `nonce`
- `destination chain`

Ethereum lane:

- `bridge verifier`
- `mint wNAV`
- `mark nonce used`

Required packet fields:

- `source chain`
- `destination chain`
- `asset id`
- `amount`
- `recipient`
- `nonce`
- `expiry`

Required invariant:

- `wrapped supply <= PFTL locked/debited supply`

Do not include:

- A relayer as a trusted authority.
- A bridge that looks like it mints because it received a message without verification.

Animation intent:

- Receipt moves from PFTL to verifier; mint arrow only appears after verifier pass.

## Slide 07 - Bridge Verifies Finality

Purpose: teach what the Ethereum verifier checks.

Diagram type: verifier decision tree.

Layout:

- Left: `incoming packet`.
- Center: stacked verification pipeline.
- Right: two branches, `accept` and `reject`.

Verification pipeline:

1. `domain check`
2. `receipt root`
3. `validator certificate`
4. `field match`
5. `freshness/expiry`
6. `nonce unused`

Accept branch:

- `mint/release allowed`

Reject branches:

- `wrong chain`
- `changed amount`
- `changed recipient`
- `expired`
- `nonce replay`
- `bad certificate`

Required relationship:

- The same finalized packet must be verified exactly.
- Any mutation or replay fails.

Do not include:

- A generic shield icon with no checks.
- A green accepted path without red rejected examples.

Animation intent:

- Packet enters top of checklist; failed examples branch red; exact packet exits green.

## Slide 08 - Wrapped Token Is A Claim Ticket

Purpose: explain the relationship between wrapped NAVCoin and native PFTL state.

Diagram type: relationship/invariant diagram.

Layout:

- Left: `PFTL native supply`.
- Center: `bridge accounting`.
- Right: `Ethereum wNAV contract`.
- Bottom: `redemption path`.

PFTL native supply:

- `native NAVCoin`
- `locked/debited amount`
- `bridge receipt`

Bridge accounting:

- `used nonces`
- `outstanding wrapped supply`
- `burn receipts`

Ethereum wNAV contract:

- `mint only verifier`
- `burn for return`
- `transfer/trade`

Redemption path:

- `burn wNAV`
- `prove burn`
- `release native NAVCoin`

Required invariant:

- `outstanding wNAV = verified PFTL bridge-out receipts - verified burns`

Required relationship:

- wNAV is useful because wallets and venues can trade it.
- wNAV is not the official supply ledger.

Do not include:

- A huge standalone token with no tether or accounting.

Animation intent:

- Tether line pulses from wNAV contract back to PFTL bridge accounting.

## Slide 09 - Uniswap Is A Venue, Not The Oracle

Purpose: separate market price from canonical NAV.

Diagram type: dual-panel market/NAV comparison.

Layout:

- Left panel: `Uniswap venue`.
- Right panel: `PFTL NAV epoch`.
- Center: `interface display`.

Uniswap venue panel:

- `wNAV reserve`
- `USDC reserve`
- `AMM curve`
- `market price`
- `slippage`

PFTL NAV panel:

- `latest epoch`
- `NAV/unit`
- `proof timestamp`
- `fresh/stale`

Interface display:

- two large side-by-side readouts:
  - `Market price`
  - `Canonical NAV/unit`
- small derived readout:
  - `premium/discount`

Required relationship:

- Market price is produced by pool reserves.
- Canonical NAV/unit is produced by PFTL proof state.
- The pool is not an oracle and cannot validate reserve truth.

Do not include:

- Uniswap logo.
- One gauge that blends NAV and market price.

Animation intent:

- Market panel and NAV panel animate independently, then interface shows both.

## Slide 10 - Shielding Turns Public Balance Into Private Note

Purpose: explain public-to-private ingress into Orchard.

Diagram type: boundary-crossing diagram.

Layout:

- Left public zone: `transparent account`.
- Center boundary: `shield action`.
- Right private zone: `Orchard pool`.

Public zone:

- `public NAV balance`
- `deposit tx`
- `asset id`
- `amount`

Shield action:

- `create note commitment`
- `update commitment tree`
- `public receipt`

Private zone:

- `note`
- `owner secret`
- `randomness`
- `wallet view key`

Nullifier explanation:

- Show `nullifier` as a future spend artifact, not as the deposit itself.
- Label: `created on spend`.

Required relationship:

- Deposit is visible.
- Note ownership and note opening are private.
- Commitment is public, but not the owner.

Do not include:

- A generic privacy cloud with no note tree.
- A diagram that implies amount is hidden at deposit if the design makes deposit amount public.

Animation intent:

- Public balance enters boundary; commitment appears in tree; private note appears only wallet-side.

## Slide 11 - Private Swap Inside Orchard

Purpose: show how private swap proof enforces correctness without revealing wallet details.

Diagram type: zero-knowledge circuit block diagram.

Layout:

- Left private inputs.
- Center `Orchard swap circuit`.
- Right private outputs.
- Bottom public verification.

Private inputs:

- `pfUSDC note`
- `spend key`
- `opening`
- `anchor`

Circuit constraints:

- `note ownership`
- `nullifier unique`
- `asset exchange allowed`
- `value conserved`
- `output commitments valid`

Private outputs:

- `NAVCoin note`
- `change note` if applicable.

Public verification:

- `proof`
- `nullifier`
- `anchor/root`
- `validator verifies`

Required relationship:

- Validators learn proof validity and nullifier uniqueness.
- Validators do not learn the user's note opening or full private path.

Do not include:

- A magic black box with no constraints.
- A public swap path that exposes both assets as account transfers.

Animation intent:

- Inputs go into circuit, constraints light up, public proof exits downward, private notes exit right.

## Slide 12 - Private Egress Reveals Only Exit Fields

Purpose: explain private-to-public exit without revealing the note opening.

Diagram type: selective disclosure diagram.

Layout:

- Left: `private Orchard note`.
- Center: `egress proof`.
- Right: `public exit artifact`.
- Far right: `bridge-out / redemption`.

Private side:

- `note owner`
- `note opening`
- `wallet secret`
- `hidden path`

Egress proof checks:

- `valid note`
- `unspent nullifier`
- `authorized owner`
- `amount/asset matches`
- `destination allowed`

Public exit fields:

- `asset id`
- `amount`
- `destination`
- `nullifier`
- `proof hash`
- `receipt id`

Bridge-out path:

- `public NAV exit`
- `burn/redeem`
- `withdraw USDC` if that is the chosen product path.

Required relationship:

- The exit is public, but the private note opening remains hidden.
- Egress is not a second mint; it is a disclosure of a valid private claim.

Do not include:

- A full hidden note shown in the public artifact.
- A public receipt with no proof gate.

Animation intent:

- Private side remains behind a dashed boundary; only allowed fields cross to public artifact.

## Slide 13 - Every Dangerous Shortcut Gets A Gate

Purpose: show the system's fail-closed rules.

Diagram type: gate matrix with inputs, checks, and failure labels.

Layout:

- 2 x 4 grid of gates.
- Each gate tile has:
  - input artifact
  - check
  - pass output
  - failure label

Gate tiles:

1. `proof freshness`
   - input: `NAV epoch`
   - check: `timestamp <= deadline`
   - failure: `stale proof`
2. `reserve arithmetic`
   - input: `leg totals`
   - check: `spot + cash - liabilities`
   - failure: `net mismatch`
3. `supply`
   - input: `mint request`
   - check: `supply cap / policy`
   - failure: `supply violation`
4. `bridge finality`
   - input: `packet`
   - check: `certificate/root`
   - failure: `bad finality`
5. `replay`
   - input: `nonce`
   - check: `unused`
   - failure: `nonce replay`
6. `privacy proof`
   - input: `zk proof`
   - check: `verify`
   - failure: `invalid proof`
7. `nullifier`
   - input: `spend`
   - check: `not seen`
   - failure: `double spend`
8. `market display`
   - input: `pool price + NAV`
   - check: `separate labels`
   - failure: `oracle confusion`

Required relationship:

- Every gate should be understandable as "input -> check -> result".
- Include at least one visibly closed gate for stale proof or replay.

Do not include:

- Generic dashboard gauges without exact gates.

Animation intent:

- Gates light up sequentially; failed gate stays red and blocks the downstream arrow.

## Slide 14 - Complete User Path

Purpose: show the user-level flow that was missing from the earlier deck: USDC enters PFTL, the user swaps privately into a651, then atomically hands off public a651 into the Uniswap-side representation.

Diagram type: full swimlane user-path map.

Layout:

- Four horizontal lanes:
  - `Reserve proof`
  - `PFTL public state`
  - `Orchard privacy`
  - `Ethereum / Uniswap venue`
- Keep labels sparse and large.

Required path:

1. `fresh NAV`
2. `bridge USDC`
3. `shield`
4. `private swap`
5. `private egress`
6. `lock a651`
7. `verify lock`
8. `release wA651`
9. `Uniswap pool`

Required relationships:

- The path must read as: `USDC -> PFTL -> private a651 -> atomic handoff -> Uniswap-side a651`.
- The private swap happens inside Orchard before the public atomic handoff.
- The Ethereum/Uniswap-side release depends on verified PFTL lock/finality.

Do not include:

- Circular map with empty callout boxes.
- Pretty icons without the numbered path.
- Any implication that the Ethereum venue can mint without a PFTL receipt.

Animation intent:

- Animate the path in user-action order.
- Use lane highlighting rather than zooming the whole image.

## Slide 15 - Atomic Handoff To Uniswap

Purpose: explain the atomic swap/handoff primitive explicitly. This is the step that turns public PFTL a651, produced after private egress, into the Uniswap-side representation without using an inventory IOU.

Diagram type: two-chain atomic handoff / hashlock escrow diagram.

Layout:

- Three horizontal lanes:
  - `PFTL side`
  - `Ethereum side`
  - `timeout / safety`
- The PFTL lane shows the asset lock.
- The Ethereum lane shows receipt verification and wrapped-token release.
- The safety lane shows both the success and refund outcomes.

Required boxes:

1. `public a651`
2. `hashlock escrow`
3. `PFTL receipt`
4. `secret reveal`
5. `verify receipt`
6. `release wA651`
7. `both settle`
8. `or refund`

Required relationships:

- The PFTL lock binds asset, amount, recipient, and swap id.
- Ethereum verifies the finalized PFTL receipt before releasing the Uniswap-side claim.
- A secret or matching swap id links both sides.
- Timeout produces refund rather than relying on relayer inventory.

Do not include:

- A custodian inventory box.
- A vague bridge arrow without lock, receipt, and refund mechanics.
- Any text suggesting this is already production deployed unless the deployment exists.

Animation intent:

- Highlight the lock, receipt, verification, release path.
- Keep the timeout/refund path visible as the safety fallback.
