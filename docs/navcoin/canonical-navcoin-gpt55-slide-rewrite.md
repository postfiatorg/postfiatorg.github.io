# Slide Packet: USDC to a651 on Uniswap

## Global diagram language

- 16:9 technical diagrams only.
- Black background.
- Mint green = official source-of-truth state.
- Cyan = Ethereum / Uniswap side.
- Purple = Orchard privacy.
- Amber = gates, locks, handoffs.
- Red = reject, timeout, refund, failure.
- Keep image labels large and sparse. Put detailed explanation in slide copy, not inside the image.

---

## Slide 01 — Start with the user question

- **Slide number:** 01
- **Short title:** The question
- **Teaching goal:** Start from the user’s actual goal and define the key words needed for the route.
- **On-slide headline:** How do I turn USDC into a651 I can trade on Uniswap?
- **Body lines:**
  - a651 is the asset you want; the Uniswap pool is the public a651/USDC trading pair.
  - PFTL keeps the official a651 record; pfUSDC is USDC recorded on PFTL; Orchard is the private swap area.
  - Wrapped a651 is the Ethereum-side claim; atomic handoff means lock-and-release, or refund.
- **Visual specification:** Centered horizontal route with five large boxes: `USDC` → `PFTL record` → `Private swap` → `Ethereum-side a651` → `Uniswap pool`. Use mint for PFTL, purple for private swap, cyan for Ethereum/Uniswap, amber for the handoff arrow. Add one small footer label under PFTL: `official record here`.
- **gpt-image-2 prompt:**  
  > Create a precise technical process diagram, not a stylized crypto illustration. 16:9 black background. Show a simple left-to-right route with large labeled boxes: `USDC`, `PFTL record`, `Private swap`, `Ethereum-side a651`, `Uniswap pool`. Use mint green for PFTL, purple for private swap, cyan for Ethereum/Uniswap, amber for the handoff arrow. Add small label `official record here` under PFTL. Use sparse readable text, no logos, no decorative coins, no glow art.
- **Forbidden mistakes:**
  - Do not mention the retired model.
  - Do not imply Uniswap keeps the official a651 record.
  - Do not use logos or decorative token art.

---

## Slide 02 — NAV means accounting value

- **Slide number:** 02
- **Short title:** What NAV means
- **Teaching goal:** Define NAV before explaining NAVCoin and a651.
- **On-slide headline:** NAV is the accounting value behind a651.
- **Body lines:**
  - NAV means net asset value: reserve assets plus cash, minus liabilities.
  - NAV/unit means that value divided by valid units.
  - A NAVCoin follows those rules; a651 is the NAVCoin asset in this flow.
- **Visual specification:** Formula diagram. Left group: `assets` + `cash`; red subtraction box: `liabilities`; center amber gate: `accounting check`; right mint output: `NAV/unit`. Bottom small note: `market price is separate`.
- **gpt-image-2 prompt:**  
  > Create a precise technical formula diagram on a black background. Layout left to right: grouped boxes `assets` and `cash`, red subtraction box `liabilities`, amber box `accounting check`, mint green output box `NAV/unit`. Add a small separate footer label `market price is separate`. Use large sparse labels, clean arrows, no logos, no decorative graphics.
- **Forbidden mistakes:**
  - Do not call a651 a stablecoin.
  - Do not show Uniswap price as NAV.
  - Do not omit liabilities from the formula.

---

## Slide 03 — Proof of reserves is evidence

- **Slide number:** 03
- **Short title:** Checked reserves
- **Teaching goal:** Explain proof of reserves as the evidence packet behind NAV.
- **On-slide headline:** Proof of reserves checks what backs the coin.
- **Body lines:**
  - Proof of reserves is the evidence packet behind the NAV number.
  - It counts assets and cash, subtracts liabilities, and records time plus an evidence fingerprint.
  - It makes the process checkable; it does not make a dishonest data source honest.
- **Visual specification:** Left table group labeled `reserve evidence` with rows `assets`, `cash`, `liabilities`. Center amber box `math check`. Right mint packet labeled `proof packet` with four fields: `time`, `policy`, `fingerprint`, `net assets`. Bottom gray disclosure box: `gross notional: disclosure only`.
- **gpt-image-2 prompt:**  
  > Create a flat technical balance-sheet diagram. Black background. Left side: table group `reserve evidence` with rows `assets`, `cash`, `liabilities`. Center: amber gate `math check`. Right: mint green document box `proof packet` with fields `time`, `policy`, `fingerprint`, `net assets`. Bottom: gray box `gross notional: disclosure only`, not connected to NAV math. Large readable labels, sparse text, no vault art, no logos.
- **Forbidden mistakes:**
  - Do not add gross perp notional into NAV.
  - Do not hide the arithmetic in a vague “proof machine.”
  - Do not forget cash.

---

## Slide 04 — PFTL keeps the official record

- **Slide number:** 04
- **Short title:** Where truth lives
- **Teaching goal:** Explain PFTL in plain English and separate official recordkeeping from trading.
- **On-slide headline:** PFTL decides what a651 officially exists.
- **Body lines:**
  - PFTL means Post Fiat L1, the base blockchain that records official a651 state.
  - Uniswap is where people trade; PFTL is where the official a651 record is kept.
  - A receipt is a public record of a PFTL action, and Ethereum-side a651 must trace back to one.
- **Visual specification:** Two-column relationship diagram. Left mint column: `PFTL official record` with box `a651 supply`. Right cyan column: `Ethereum / Uniswap trading side` with box `tradable a651 claim`. Arrow from left to right labeled `verified PFTL receipt`. No arrow from right to left creating official supply.
- **gpt-image-2 prompt:**  
  > Create a precise two-column relationship diagram on a black background. Left mint green column labeled `PFTL official record` with box `a651 supply`. Right cyan column labeled `Ethereum / Uniswap trading side` with box `tradable a651 claim`. Draw one arrow from PFTL to Ethereum labeled `verified PFTL receipt`. Keep labels large and sparse. No logos, no decorative art, no retired-model comparison.
- **Forbidden mistakes:**
  - Do not write “Ethereum hosts the venue.”
  - Do not imply Ethereum decides official a651 supply.
  - Do not include the retired demo architecture.

---

## Slide 05 — A NAV epoch is a locked snapshot

- **Slide number:** 05
- **Short title:** Fresh NAV snapshot
- **Teaching goal:** Define a NAV epoch and show how reserve evidence becomes chain state.
- **On-slide headline:** A NAV epoch is one accepted NAV snapshot.
- **Body lines:**
  - A NAV epoch is one finalized snapshot of NAV at a specific time.
  - Validators—the chain’s checkers—accept the proof only if the math and freshness pass.
  - No fresh epoch means no official a651 output.
- **Visual specification:** Left: `proof packet`. Center: validator checklist inside a ring of six small validator nodes; checklist items `math`, `fresh`, `policy`, `supply`. Right: mint block `NAV epoch` with fields `epoch id`, `NAV/unit`, `time`, `proof fingerprint`.
- **gpt-image-2 prompt:**  
  > Create a consensus finalization diagram. Black background. Left document box `proof packet`. Center: six small validator nodes around an amber checklist with labels `math`, `fresh`, `policy`, `supply`. Right: mint green ledger block `NAV epoch` with fields `epoch id`, `NAV/unit`, `time`, `proof fingerprint`. Show arrow from proof packet to checklist to NAV epoch. Large readable labels, no tiny text, no sci-fi architecture.
- **Forbidden mistakes:**
  - Do not show one validator finalizing alone.
  - Do not use “approved” without showing what was checked.
  - Do not let a stale proof create a fresh epoch.

---

## Slide 06 — Public and private areas

- **Slide number:** 06
- **Short title:** Read the map
- **Teaching goal:** Teach the deck’s public/private color language before showing the transaction path.
- **On-slide headline:** Some steps are public; the middle swap is private.
- **Body lines:**
  - Public means anyone can see the ledger event.
  - Private means the chain checks a proof while wallet details stay hidden.
  - Mint is PFTL, purple is Orchard, cyan is Ethereum/Uniswap, amber is locks, red is reject or refund.
- **Visual specification:** Four horizontal sample lanes: `PFTL public state` in mint, `Orchard private notes` in purple with dashed boundary, `Ethereum / Uniswap public side` in cyan, `locks / rejects` in amber and red. Add tiny arrow examples inside each lane.
- **gpt-image-2 prompt:**  
  > Create a clean legend diagram on a black background. Four horizontal lanes with large labels: mint green `PFTL public state`, purple dashed `Orchard private notes`, cyan `Ethereum / Uniswap public side`, amber/red `locks / rejects`. Include one simple arrow example in each lane. Sparse readable labels only. No logos, no decorative crypto art.
- **Forbidden mistakes:**
  - Do not make everything look private.
  - Do not blend PFTL and Ethereum into one area.
  - Do not use unlabeled colors.

---

## Slide 07 — You start with USDC

- **Slide number:** 07
- **Short title:** Starting asset
- **Teaching goal:** Show the user’s initial state before any PFTL or privacy step.
- **On-slide headline:** Step 1: you start with USDC.
- **Body lines:**
  - Your starting asset is normal USDC in a wallet or exchange route.
  - At this moment, nothing private has happened.
  - Next, you create a PFTL-recorded USDC balance.
- **Visual specification:** Left cyan box `USDC source`. Center box `your wallet`. Right faded mint box `next: PFTL record`. Use a public-lane label across the top: `public start`.
- **gpt-image-2 prompt:**  
  > Create a simple starting-state diagram. Black background. Left cyan box `USDC source`, arrow to center box `your wallet`, arrow to faded mint green box `next: PFTL record`. Add top lane label `public start`. Keep text large and sparse. No privacy cloud, no Uniswap pool yet, no logos.
- **Forbidden mistakes:**
  - Do not show a651 already created.
  - Do not show Orchard privacy yet.
  - Do not imply USDC and a651 are the same asset.

---

## Slide 08 — USDC becomes pfUSDC on PFTL

- **Slide number:** 08
- **Short title:** USDC on PFTL
- **Teaching goal:** Define pfUSDC and the checked bridge-in step.
- **On-slide headline:** Step 2: USDC becomes pfUSDC on PFTL.
- **Body lines:**
  - Bridge-in means a checked move from your starting USDC into a matching PFTL record.
  - pfUSDC means that PFTL record of USDC.
  - Public: asset, amount, recipient, and one-use id. Private: none yet.
- **Visual specification:** Two lanes. Top cyan lane `starting USDC`; bottom mint lane `PFTL`. Arrow from `USDC` to amber gate `bridge-in checks`, then down to mint box `pfUSDC balance`. Field chips near gate: `asset`, `amount`, `recipient`, `one-use id`. Red reject branch: `bad or reused id`.
- **gpt-image-2 prompt:**  
  > Create a technical two-lane bridge-in diagram. Black background. Top cyan lane `starting USDC`; bottom mint green lane `PFTL`. Show `USDC` flowing to amber gate `bridge-in checks`, then to mint box `pfUSDC balance`. Add four field chips: `asset`, `amount`, `recipient`, `one-use id`. Add red reject branch `bad or reused id`. Large sparse labels, no logos, no decorative art.
- **Forbidden mistakes:**
  - Do not mint pfUSDC without checks.
  - Do not call this private.
  - Do not omit the one-use id.

---

## Slide 09 — Shield pfUSDC into Orchard

- **Slide number:** 09
- **Short title:** Enter privacy
- **Teaching goal:** Define Orchard and private note before the swap.
- **On-slide headline:** Step 3: put pfUSDC behind the privacy boundary.
- **Body lines:**
  - Orchard is the private transaction area inside PFTL.
  - A private note is a sealed wallet record; the chain only sees a public fingerprint called a commitment.
  - Public: deposit and commitment. Private: owner, opening, and later route.
- **Visual specification:** Left mint public box `pfUSDC balance`. Center purple dashed boundary labeled `Orchard`. Amber/purple action box `shield`. Right purple wallet-side box `private note`. Below it, small public tree labeled `commitment`.
- **gpt-image-2 prompt:**  
  > Create a boundary-crossing privacy diagram. Black background. Left mint green public box `pfUSDC balance`. Center purple dashed boundary labeled `Orchard` with action box `shield`. Right purple wallet-side box `private note`. Below, small public tree icon labeled `commitment`. Use large sparse labels. No privacy cloud, no hidden amount claim, no decorative art.
- **Forbidden mistakes:**
  - Do not show the private note contents publicly.
  - Do not imply the public deposit disappears from accounting.
  - Do not claim the deposit amount is hidden unless the implementation supports that.

---

## Slide 10 — Nullifier means spent-once marker

- **Slide number:** 10
- **Short title:** Stop double spending
- **Teaching goal:** Define nullifier and explain why private notes cannot be spent twice.
- **On-slide headline:** A nullifier lets privacy and accounting work together.
- **Body lines:**
  - A nullifier is a public spent marker created when a private note is used.
  - It lets validators reject the same note twice without learning which note it was.
  - Public: nullifier. Private: note opening and owner.
- **Visual specification:** Purple `private note` flows into amber `spend proof`. Output public marker `nullifier`. A second attempted spend goes to red box `seen nullifier: reject`.
- **gpt-image-2 prompt:**  
  > Create a simple nullifier diagram. Black background. Purple box `private note` arrows into amber box `spend proof`. Output a public marker labeled `nullifier`. Show a second dashed arrow to red reject box `seen nullifier: reject`. Keep labels large and sparse. Do not show identity, addresses, or note contents.
- **Forbidden mistakes:**
  - Do not make the nullifier look like a user identity.
  - Do not show the nullifier as created at deposit.
  - Do not allow the same note to spend twice.

---

## Slide 11 — Private swap pfUSDC for a651

- **Slide number:** 11
- **Short title:** Private swap
- **Teaching goal:** Show the private Orchard swap from shielded pfUSDC note to private a651 note.
- **On-slide headline:** Step 4: Orchard swaps pfUSDC into private a651.
- **Body lines:**
  - Inside Orchard, your wallet spends a shielded pfUSDC note and creates a private a651 note.
  - Validators check proof validity and the one-use nullifier, not your wallet path.
  - Public: proof and nullifier. Private: input note, output note, route.
- **Visual specification:** Purple block diagram. Left `pfUSDC note` enters center `Orchard swap`. Right outputs `a651 note` and optional `change note`. Bottom public lane shows `proof + nullifier` going to `validator check`.
- **gpt-image-2 prompt:**  
  > Create a zero-knowledge-style block diagram without jargon overload. Black background. Purple private lane: left box `pfUSDC note`, center box `Orchard swap`, right boxes `a651 note` and `change note`. Bottom public lane: `proof + nullifier` arrow to mint green `validator check`. Use sparse readable labels, no public account-transfer swap, no logos, no decorative crypto art.
- **Forbidden mistakes:**
  - Do not expose both notes as public balances.
  - Do not skip the nullifier.
  - Do not show Uniswap inside Orchard.

---

## Slide 12 — What the private swap proves

- **Slide number:** 12
- **Short title:** Proof checks
- **Teaching goal:** Explain what validators can verify without seeing the private notes.
- **On-slide headline:** The chain checks the rule, not your private route.
- **Body lines:**
  - The proof says: a real note was spent once, the exchange is allowed under the current NAV epoch, and values balance.
  - Validators accept the proof without reading the sealed notes.
  - If any check fails, nothing changes.
- **Visual specification:** Center amber/purple gate `swap proof`. Checklist items: `real note`, `nullifier unused`, `exchange allowed`, `value balanced`. Green pass arrow to `new note accepted`; red fail arrow to `reject`.
- **gpt-image-2 prompt:**  
  > Create a proof-check gate diagram. Black background. Center amber/purple gate labeled `swap proof`. Add four large checklist items: `real note`, `nullifier unused`, `exchange allowed`, `value balanced`. Green arrow to `new note accepted`; red arrow to `reject`. Keep labels sparse and readable. No magic black box with no checks.
- **Forbidden mistakes:**
  - Do not make the proof a vague “privacy cloud.”
  - Do not imply value can be created from nothing.
  - Do not show failed proofs changing state.

---

## Slide 13 — You now hold private a651

- **Slide number:** 13
- **Short title:** Private result
- **Teaching goal:** Show the user’s state after the private swap and before public exit.
- **On-slide headline:** After the swap, a651 is still private.
- **Body lines:**
  - After the swap, your wallet owns a private a651 note.
  - Uniswap cannot trade that sealed note directly.
  - To reach Uniswap, you must exit to public PFTL a651.
- **Visual specification:** Purple Orchard zone with large sealed box `private a651 note`. Two arrows: loop arrow `stay private` and forward arrow `exit to public next`. Cyan Uniswap pool is visible far right but disconnected.
- **gpt-image-2 prompt:**  
  > Create a state diagram on a black background. Purple dashed Orchard zone contains large sealed box `private a651 note`. Add one loop arrow labeled `stay private` and one forward arrow labeled `exit to public next`. Far right, show cyan `Uniswap pool` grayed out and disconnected. Large sparse labels, no decorative coins.
- **Forbidden mistakes:**
  - Do not show Uniswap trading the private note.
  - Do not show public PFTL a651 before egress.
  - Do not skip the exit step.

---

## Slide 14 — Private egress to public PFTL a651

- **Slide number:** 14
- **Short title:** Leave privacy
- **Teaching goal:** Define private egress and show the private-to-public transition.
- **On-slide headline:** Step 5: private egress creates public PFTL a651.
- **Body lines:**
  - Private egress means leaving Orchard while revealing only the fields needed for public settlement.
  - Your wallet proves the private a651 note is valid and unspent.
  - Public: asset, amount, destination, receipt id. Private: old note details.
- **Visual specification:** Left purple `private a651 note` behind dashed boundary. Center amber gate `egress proof`. Right mint boxes `public PFTL a651` and `exit receipt`. Four public field chips: `asset`, `amount`, `destination`, `receipt id`.
- **gpt-image-2 prompt:**  
  > Create a selective-disclosure egress diagram. Black background. Left purple dashed privacy boundary with box `private a651 note`. Center amber gate `egress proof`. Right mint green boxes `public PFTL a651` and `exit receipt`. Add field chips `asset`, `amount`, `destination`, `receipt id`. Keep note details hidden. Large sparse labels, no decorative art.
- **Forbidden mistakes:**
  - Do not show the private note opening in the public receipt.
  - Do not make egress look like a second mint from nowhere.
  - Do not omit the public exit fields.

---

## Slide 15 — Public PFTL a651 is the handoff input

- **Slide number:** 15
- **Short title:** Official handoff input
- **Teaching goal:** Make clear that the atomic handoff starts from public PFTL a651.
- **On-slide headline:** Public PFTL a651 is what gets locked.
- **Body lines:**
  - The public PFTL balance is the official a651 that can be locked for handoff.
  - This public step is intentional: the Ethereum release needs a visible source record.
  - Public: balance, exit receipt, and later lock.
- **Visual specification:** Mint ledger panel `PFTL public ledger` with `public a651 balance` and `exit receipt`. Arrow to amber box `ready to lock`. Cyan Ethereum-side box `waiting for verified receipt` sits to the right.
- **gpt-image-2 prompt:**  
  > Create a public-ledger readiness diagram. Black background. Mint green panel `PFTL public ledger` contains boxes `public a651 balance` and `exit receipt`. Arrow to amber box `ready to lock`. On the right, cyan box `waiting for verified receipt`. Use large sparse labels, no Uniswap trade yet, no Ethereum mint before lock.
- **Forbidden mistakes:**
  - Do not release Ethereum-side a651 before the PFTL lock.
  - Do not make this stage private.
  - Do not imply Uniswap can verify a private note.

---

## Slide 16 — Atomic handoff means lock-and-release

- **Slide number:** 16
- **Short title:** Atomic handoff
- **Teaching goal:** Define atomic handoff in plain English.
- **On-slide headline:** Step 6: lock on PFTL, release on Ethereum, or refund.
- **Body lines:**
  - Atomic handoff means lock on PFTL, verify on Ethereum, then release matching Ethereum-side a651.
  - If the verified release does not happen before timeout, the PFTL lock refunds.
  - The target design does not rely on a middle party paying from inventory.
- **Visual specification:** Three horizontal lanes. Top mint lane `PFTL side`: `public a651` → amber `lock`. Middle cyan lane `Ethereum side`: `verify receipt` → `release a651`. Bottom red/amber lane `timeout safety`: `timeout` → `refund`. Shared label between lanes: `same swap id`.
- **gpt-image-2 prompt:**  
  > Create a three-lane atomic handoff diagram. Black background. Top mint green lane `PFTL side`: `public a651` arrow to amber `lock`. Middle cyan lane `Ethereum side`: `verify receipt` arrow to `release a651`. Bottom red/amber lane `timeout safety`: `timeout` arrow to `refund`. Add shared label `same swap id` connecting lock and release. Large sparse labels, no custodian inventory box, no vague bridge arrow.
- **Forbidden mistakes:**
  - Do not show a custodian inventory pool.
  - Do not make the handoff one-way with no refund.
  - Do not release Ethereum-side a651 without verification.

---

## Slide 17 — The lock binds the exact deal

- **Slide number:** 17
- **Short title:** Lock details
- **Teaching goal:** Show which fields must be locked so the handoff cannot be rewritten.
- **On-slide headline:** The PFTL lock says exactly what can be released.
- **Body lines:**
  - The lock records the exact deal: asset, amount, recipient, destination, deadline, and swap id.
  - The swap id is the shared label that ties both sides to the same handoff.
  - Changed fields, expired locks, or reused ids must fail.
- **Visual specification:** Center amber lock document `PFTL lock receipt`. Field chips: `asset a651`, `amount`, `recipient`, `destination`, `deadline`, `swap id`. Green arrow `exact match`. Red reject branches: `changed field`, `expired`, `used id`.
- **gpt-image-2 prompt:**  
  > Create a lock-receipt diagram. Black background. Center amber document labeled `PFTL lock receipt`. Add large field chips: `asset a651`, `amount`, `recipient`, `destination`, `deadline`, `swap id`. Green arrow labeled `exact match`. Red reject branches labeled `changed field`, `expired`, `used id`. Sparse readable text, no decorative locks beyond simple diagram icon.
- **Forbidden mistakes:**
  - Do not omit recipient or amount.
  - Do not let changed fields pass.
  - Do not forget timeout/deadline.

---

## Slide 18 — Ethereum verifies the PFTL receipt

- **Slide number:** 18
- **Short title:** Verify, don’t trust
- **Teaching goal:** Explain that the messenger is not the source of truth.
- **On-slide headline:** Ethereum should verify the PFTL lock receipt.
- **Body lines:**
  - A relayer is just a messenger; it may carry the receipt but should not be trusted.
  - Finality means PFTL has settled this exact lock as chain state.
  - Ethereum verifies finality and fields before wrapped a651 can be released.
- **Visual specification:** Left gray `relayer messenger` carrying `lock receipt`. Center cyan/amber `Ethereum verifier` with checklist `PFTL finalized`, `fields match`, `deadline ok`, `id unused`. Right green `release allowed`; red branches `bad receipt` and `replay`.
- **gpt-image-2 prompt:**  
  > Create a verifier pipeline diagram. Black background. Left gray box `relayer messenger` carrying document `lock receipt`. Center cyan/amber box `Ethereum verifier` with checklist labels `PFTL finalized`, `fields match`, `deadline ok`, `id unused`. Right green output `release allowed`. Add red reject branches `bad receipt` and `replay`. Large sparse labels, no relayer as authority, no logos.
- **Forbidden mistakes:**
  - Do not make the relayer a trusted approver.
  - Do not accept changed packets.
  - Do not allow the same receipt twice.

---

## Slide 19 — Wrapped a651 is an Ethereum-side claim

- **Slide number:** 19
- **Short title:** Wrapped token
- **Teaching goal:** Define wrapped token and its relationship to PFTL.
- **On-slide headline:** Wrapped a651 is useful, but it is not the official ledger.
- **Body lines:**
  - A wrapped token is an Ethereum token that represents a PFTL-locked claim.
  - Wrapped a651 can move in Ethereum wallets and Uniswap, but it is not the official supply record.
  - Public: mint/release event on Ethereum. Source of truth: PFTL.
- **Visual specification:** Left mint `PFTL locked a651`. Center `bridge accounting` with `used ids` and `outstanding wrapped`. Right cyan `wrapped a651 contract`. Tether line from contract back to PFTL labeled `must trace back`. Invariant footer: `wrapped ≤ locked`.
- **gpt-image-2 prompt:**  
  > Create a wrapped-token relationship diagram. Black background. Left mint green box `PFTL locked a651`. Center accounting box `bridge accounting` with labels `used ids` and `outstanding wrapped`. Right cyan box `wrapped a651 contract`. Draw a tether line back to PFTL labeled `must trace back`. Footer invariant `wrapped ≤ locked`. Large sparse labels, no standalone token glamour art, no logos.
- **Forbidden mistakes:**
  - Do not show wrapped a651 as the official supply ledger.
  - Do not show minting without a verified PFTL lock.
  - Do not draw a huge decorative token with no accounting.

---

## Slide 20 — Atomic outcomes: settle or refund

- **Slide number:** 20
- **Short title:** Success or refund
- **Teaching goal:** Show the state machine for the handoff result.
- **On-slide headline:** Atomic means both sides settle, or the lock refunds.
- **Body lines:**
  - Success: lock → verified receipt → wrapped a651 released → lock consumed.
  - Failure: timeout → refund public PFTL a651.
  - A used receipt or expired lock must be rejected.
- **Visual specification:** State machine. `start` → `locked` → split. Green success path: `verified` → `released` → `settled`. Red/amber failure path: `timeout` → `refunded`. Red side boxes: `replay reject`, `expired reject`.
- **gpt-image-2 prompt:**  
  > Create a small state machine diagram. Black background. Boxes: `start` → `locked`, then split to green path `verified` → `released` → `settled`, and red/amber path `timeout` → `refunded`. Add red side boxes `replay reject` and `expired reject`. Use large readable labels and clean arrows. No custodian inventory, no dead-end pending state.
- **Forbidden mistakes:**
  - Do not leave funds stuck with no refund path.
  - Do not allow replay.
  - Do not call a failed handoff successful.

---

## Slide 21 — Trade in the Uniswap a651/USDC pool

- **Slide number:** 21
- **Short title:** The trading pool
- **Teaching goal:** Define Uniswap pool and separate market price from NAV.
- **On-slide headline:** Step 7: trade wrapped a651 in the a651/USDC pool.
- **Body lines:**
  - A Uniswap pool is a public smart-contract market with two reserves.
  - The a651/USDC pool lets users swap between wrapped a651 and USDC.
  - Pool price is market price; PFTL NAV is the accounting value.
- **Visual specification:** Cyan pool box `Uniswap a651/USDC pool` with two reserve boxes: `wrapped a651` and `USDC`. Arrows `buy` and `sell`. Separate mint side panel `PFTL NAV/unit` with no arrow into pool math except a display line labeled `show separately`.
- **gpt-image-2 prompt:**  
  > Create a clear pool diagram. Black background. Cyan box `Uniswap a651/USDC pool` containing two reserve boxes `wrapped a651` and `USDC`. Add arrows `buy` and `sell`. Separate mint green side panel `PFTL NAV/unit` with display line `show separately`. Large sparse labels, no Uniswap logo, no blended NAV/market gauge.
- **Forbidden mistakes:**
  - Do not use the Uniswap logo.
  - Do not show pool price as official NAV.
  - Do not say Uniswap validates reserves.

---

## Slide 22 — The full path in one line

- **Slide number:** 22
- **Short title:** Complete route
- **Teaching goal:** Show the required user path explicitly from USDC to tradable a651.
- **On-slide headline:** The complete path: USDC to Uniswap-side a651.
- **Body lines:**
  - USDC → PFTL/pfUSDC → shielded pfUSDC note → private Orchard swap → private a651 note.
  - Then: private egress → public PFTL a651 → atomic lock/handoff → Ethereum-side wrapped a651.
  - Finally: trade in the Uniswap a651/USDC pool.
- **Visual specification:** Four horizontal lanes: `Public start`, `PFTL public`, `Orchard private`, `Ethereum / Uniswap`. Numbered boxes 1–10: `USDC`, `pfUSDC`, `shielded note`, `Orchard swap`, `private a651 note`, `private egress`, `public PFTL a651`, `atomic lock`, `wrapped a651`, `a651/USDC pool`. Use arrows crossing lanes in order.
- **gpt-image-2 prompt:**  
  > Create a full swimlane user-path map. Black background. Four horizontal lanes labeled `Public start`, `PFTL public`, `Orchard private`, `Ethereum / Uniswap`. Add numbered boxes in order: `1 USDC`, `2 pfUSDC`, `3 shielded note`, `4 Orchard swap`, `5 private a651 note`, `6 private egress`, `7 public PFTL a651`, `8 atomic lock`, `9 wrapped a651`, `10 a651/USDC pool`. Use mint for PFTL, purple for Orchard, cyan for Ethereum/Uniswap, amber for lock. Large sparse labels, no logos.
- **Forbidden mistakes:**
  - Do not skip pfUSDC.
  - Do not skip private egress.
  - Do not release wrapped a651 before the atomic lock.

---

## Slide 23 — What is public and what is private

- **Slide number:** 23
- **Short title:** Visibility checklist
- **Teaching goal:** Make the public/private status clear for every stage.
- **On-slide headline:** The edges are public; the middle route is private.
- **Body lines:**
  - Public edges: bridge-in, egress, PFTL lock, Ethereum release, and Uniswap trade.
  - Private middle: shielded notes and the Orchard swap route.
  - The chain still checks proofs and nullifiers, so privacy does not remove accounting.
- **Visual specification:** Three-band diagram. Left and right bands labeled `public edges`; middle purple band labeled `private middle`. Place small stage chips: public bands contain `USDC`, `pfUSDC`, `egress`, `lock`, `wrapped a651`, `pool trade`; private band contains `pfUSDC note`, `swap route`, `a651 note`. Bottom check strip: `proofs`, `nullifiers`, `one-use ids`.
- **gpt-image-2 prompt:**  
  > Create a visibility checklist diagram. Black background. Three horizontal bands: left mint/cyan `public edge`, middle purple dashed `private middle`, right mint/cyan `public edge`. Public chips: `USDC`, `pfUSDC`, `egress`, `lock`, `wrapped a651`, `pool trade`. Private chips: `pfUSDC note`, `swap route`, `a651 note`. Bottom amber strip `proofs • nullifiers • one-use ids`. Large sparse labels, no tiny table.
- **Forbidden mistakes:**
  - Do not imply the whole route is private.
  - Do not imply privacy removes supply checks.
  - Do not hide the public lock or Uniswap trade.

---

## Slide 24 — Trust model and rollout status

- **Slide number:** 24
- **Short title:** What can be trusted
- **Teaching goal:** Separate final-target trustless design from staged or not-yet-production versions.
- **On-slide headline:** Do not call it trustless unless the contract verifies the proof.
- **Body lines:**
  - Trustless means contracts verify proof instead of trusting a messenger or committee.
  - Final target: direct PFTL verification or a compact proof; staged versions may use committee signatures or challenge windows.
  - Do not call a staged bridge production-trustless without deployment and verification evidence.
- **Visual specification:** Maturity ladder from left to right. Left amber `staged: committee signs`. Middle amber/cyan `staged+: challenge window`. Right mint/cyan `final target: contract verifies PFTL proof`. Red footer label: `no evidence = no production claim`.
- **gpt-image-2 prompt:**  
  > Create a trust-model maturity ladder. Black background. Three columns left to right: amber `staged: committee signs`, amber/cyan `staged+: challenge window`, mint/cyan `final target: contract verifies PFTL proof`. Add red footer `no evidence = no production claim`. Large readable labels, no claim of live deployment, no decorative crypto art.
- **Forbidden mistakes:**
  - Do not claim the final bridge is deployed.
  - Do not call committee signatures fully trustless.
  - Do not hide staged status.

---

## Slide 25 — Safety gates keep supply honest

- **Slide number:** 25
- **Short title:** Fail closed
- **Teaching goal:** Summarize the gates that block unsafe state changes.
- **On-slide headline:** Every dangerous shortcut gets a gate.
- **Body lines:**
  - Fresh proof, supply rules, finality, one-use ids, nullifiers, and egress proofs all must pass.
  - Good UX should explain which gate failed.
  - Fail closed: no proof, no mint; reused id, no release; bad nullifier, no spend.
- **Visual specification:** 2x4 gate matrix. Tiles: `fresh NAV`, `reserve math`, `supply policy`, `PFTL finality`, `one-use id`, `nullifier`, `egress proof`, `market labels`. Each tile has a small pass check and red reject mark. One tile, `one-use id`, is visibly red with label `replay blocked`.
- **gpt-image-2 prompt:**  
  > Create a gate matrix diagram. Black background. 2x4 grid of amber gate tiles labeled `fresh NAV`, `reserve math`, `supply policy`, `PFTL finality`, `one-use id`, `nullifier`, `egress proof`, `market labels`. Add small green pass checks and red reject marks. Make `one-use id` tile red with label `replay blocked`. Large sparse labels, no generic dashboard gauges.
- **Forbidden mistakes:**
  - Do not show gates as decorative icons with no meaning.
  - Do not let replay pass.
  - Do not combine market price and NAV into one label.

---

## Slide 26 — Final summary

- **Slide number:** 26
- **Short title:** The answer
- **Teaching goal:** Recap the route in plain English.
- **On-slide headline:** One route, one official record, one trading pool.
- **Body lines:**
  - You turn USDC into pfUSDC on PFTL, privately swap it into a651, then egress to public PFTL a651.
  - PFTL keeps the official record; Ethereum-side wrapped a651 exists only after a verified lock/handoff.
  - Uniswap is where wrapped a651 trades against USDC; it is not where official supply is decided.
- **Visual specification:** Three large panels. Panel 1 mint: `enter PFTL: USDC → pfUSDC`. Panel 2 purple: `swap privately: pfUSDC note → a651 note`. Panel 3 cyan/amber: `handoff + trade: lock → wrapped a651 → pool`. Footer: `official record: PFTL`.
- **gpt-image-2 prompt:**  
  > Create a final summary diagram. Black background. Three large panels left to right: mint green `enter PFTL: USDC → pfUSDC`, purple `swap privately: pfUSDC note → a651 note`, cyan/amber `handoff + trade: lock → wrapped a651 → pool`. Add footer `official record: PFTL`. Large sparse labels, clean arrows, no logos, no decorative art.
- **Forbidden mistakes:**
  - Do not introduce a new concept.
  - Do not omit PFTL as the official record.
  - Do not say Uniswap decides supply.

---

## Slide 27 — Appendix: evidence and claim boundary

- **Slide number:** 27
- **Short title:** Evidence boundary
- **Teaching goal:** Prevent overclaiming about deployment or trustlessness.
- **On-slide headline:** This explains the design path; production claims need evidence.
- **Body lines:**
  - This packet explains the official design path; it does not prove the final bridge is live.
  - Production evidence should include deployed contract addresses, verifier method, pool address, proof freshness source, and replay/nullifier checks.
  - If any step is manual or committee-signed, label it staged.
- **Visual specification:** Three-column appendix checklist. Green column `design claim`: `PFTL source`, `private middle`, `atomic target`. Amber column `needs evidence`: `contracts`, `verifier`, `pool`, `freshness`. Red column `do not claim`: `production bridge`, `NAV = pool price`, `committee = trustless`.
- **gpt-image-2 prompt:**  
  > Create an appendix claim-boundary checklist. Black background. Three columns: green `design claim` with chips `PFTL source`, `private middle`, `atomic target`; amber `needs evidence` with chips `contracts`, `verifier`, `pool`, `freshness`; red `do not claim` with chips `production bridge`, `NAV = pool price`, `committee = trustless`. Large readable labels, no retired-model history, no logos.
- **Forbidden mistakes:**
  - Do not claim production deployment without proof.
  - Do not claim NAV equals Uniswap price.
  - Do not turn this appendix into a retired-model history lesson.

---

# Implementation Notes For Codex

1. **Replace the current deck from scratch.** Do not patch the existing 15-slide structure. Delete the current slide sections, current image references, and current retired-model lead.
2. **Use this exact 27-slide order.** The deck must start with the user question and must not begin with historical contrast.
3. **Update front matter:**
   - `title: "How to Turn USDC Into a651 for Uniswap"`
   - `summary: "A beginner-friendly visual walkthrough of the full route: USDC to pfUSDC on PFTL, private Orchard swap into a651, private egress, atomic handoff, wrapped a651, and the Uniswap a651/USDC pool."`
   - Keep existing canonical URL unless product routing requires a new one.
4. **Generate new images with gpt-image-2 only.** Do not reuse old deck images. Save generated images using these paths:
   - `/navcoin/canonical-transaction/slide-01-user-question-web.png`
   - `/navcoin/canonical-transaction/slide-02-nav-accounting-web.png`
   - `/navcoin/canonical-transaction/slide-03-proof-of-reserves-web.png`
   - `/navcoin/canonical-transaction/slide-04-pftl-official-record-web.png`
   - `/navcoin/canonical-transaction/slide-05-nav-epoch-web.png`
   - `/navcoin/canonical-transaction/slide-06-public-private-map-web.png`
   - `/navcoin/canonical-transaction/slide-07-usdc-start-web.png`
   - `/navcoin/canonical-transaction/slide-08-pfusdc-bridge-in-web.png`
   - `/navcoin/canonical-transaction/slide-09-shield-pfusdc-web.png`
   - `/navcoin/canonical-transaction/slide-10-nullifier-web.png`
   - `/navcoin/canonical-transaction/slide-11-private-orchard-swap-web.png`
   - `/navcoin/canonical-transaction/slide-12-swap-proof-checks-web.png`
   - `/navcoin/canonical-transaction/slide-13-private-a651-note-web.png`
   - `/navcoin/canonical-transaction/slide-14-private-egress-web.png`
   - `/navcoin/canonical-transaction/slide-15-public-pftl-a651-web.png`
   - `/navcoin/canonical-transaction/slide-16-atomic-handoff-overview-web.png`
   - `/navcoin/canonical-transaction/slide-17-pftl-lock-fields-web.png`
   - `/navcoin/canonical-transaction/slide-18-ethereum-verifier-web.png`
   - `/navcoin/canonical-transaction/slide-19-wrapped-a651-web.png`
   - `/navcoin/canonical-transaction/slide-20-settle-or-refund-web.png`
   - `/navcoin/canonical-transaction/slide-21-uniswap-pool-web.png`
   - `/navcoin/canonical-transaction/slide-22-complete-route-web.png`
   - `/navcoin/canonical-transaction/slide-23-public-private-checklist-web.png`
   - `/navcoin/canonical-transaction/slide-24-trust-model-web.png`
   - `/navcoin/canonical-transaction/slide-25-safety-gates-web.png`
   - `/navcoin/canonical-transaction/slide-26-final-summary-web.png`
   - `/navcoin/canonical-transaction/slide-27-evidence-boundary-web.png`
5. **Use the slide copy exactly as written unless there is a verified protocol correction.** Keep each slide to one headline and 1–3 short body lines.
6. **Update navigation from 15 to 27 slides.** If tabs are hard-coded, create buttons `01` through `27`. If possible, generate tabs from the slide count.
7. **Update deck count display to `01 / 27` initially.** Ensure JavaScript still reads the actual number of `.deck-slide` elements.
8. **Set image alt text per slide.** Use a one-sentence description of the diagram, not generic text.
9. **Remove visible “slide instructions” accordions from the published deck.** The implementation should show the teaching deck, not production notes.
10. **Do not include the retired model in the main deck.** If historical contrast is ever added later, place it after the appendix and label it clearly as history.
11. **Never use vague phrasing like “Ethereum hosts the venue.”** Use direct wording: “Uniswap is where people trade; PFTL is where the official a651 record is kept.”
12. **Include the status boundary.** Slide 24 and Slide 27 must remain, so the deck does not imply a production trustless bridge unless deployment evidence exists.
13. **Keep all diagrams informational.** No cinematic scenes, glowy hero art, token glamour shots, brand logos, or unlabeled icon clusters.
14. **Check first-use definitions before publishing.** The deck must define NAV, proof of reserves, PFTL, pfUSDC, a651, Orchard, private note, nullifier, private egress, atomic handoff, wrapped token, and Uniswap pool before relying on them.
15. **Verify the full route appears exactly on Slide 22:**  
    `USDC -> PFTL/pfUSDC -> shielded pfUSDC note -> private Orchard swap -> private a651 note -> private egress -> public PFTL a651 -> atomic lock/handoff -> Ethereum-side wrapped a651 -> Uniswap a651/USDC pool`.