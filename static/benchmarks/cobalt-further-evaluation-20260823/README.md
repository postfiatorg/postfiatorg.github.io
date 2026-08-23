# Cobalt: Further Evaluation — public bundle

This directory supports the Post Fiat article published on 2026-08-23.

## Contents

- `matched-packet/`: canonical 80-case Cobalt/RippleD comparison built at Post Fiat L1 commit `3f00cb32a3f01c51beeed1661fffb6f9528fcfc7`.
- `handoff-packet/`: disposable Foundation-to-Cobalt handoff and forward-rollback rehearsal recorded at packet commit `d0af9c0f`.
- `readiness-packet/`: non-authorizing activation-readiness decision recorded at packet commit `21fa3fd3`.
- `source/`: exact source snapshots cited by the article.

Each packet retains its original `SHA256SUMS`. The cited source snapshots are covered by `SOURCE_SHA256SUMS.txt`.

## Packet roots

- Matched comparison: `7968a085033419255b52b844edd586346a1e85561394e52c69e6683b2561c50b`
- Handoff rehearsal: `b678b3f45eb2a14299b941101bd556d61795a1033f1f6e53557442b7e315807e`
- Activation readiness: `95c9a273272610b3d2622a47cefa184e67af035335c23854262c90f68461a8dd`

The matched packet is controlled simulator evidence. The live milestone is controlled-testnet evidence. Neither packet activates Cobalt authority.
