# Whitepaper Provenance Packet

Generated: `20260601T175048Z`

Source whitepaper: `content/whitepaper.md`

Whitepaper SHA-256: `dceec07dbbb9f2f82e72adbbe96d95303e109b9ead7f4a37732a2b937b06a677`

## Finding

The current date/provenance criticism is mostly addressable as a metadata and citation-surface problem, not as an absence of evidence. The packet found `22` present local artifacts and `3` successful public receipts. The strongest public checks are:

- `https://postfiat.org/testnet_vl.json` is reachable and decodes to validator-list sequence `5`, `20` validators, effective `2026-05-26T17:50:23Z`.
- `https://scoring-testnet.postfiat.org/api/scoring/config` is reachable and returns `{"cadence_hours": 168.0, "unl_max_size": 20, "unl_min_score_gap": 5, "unl_score_cutoff": 40}`.
- Git history records scoring-service publication commits for rounds 4 through 7 and VL sequences 2 through 5.

## What Should Change In The Whitepaper

The paper can safely cite this packet for the date/provenance surface. Two wording changes are supported:

1. Treat `Originally published to production: 2026-03-23 02:07:45 UTC` as production metadata, with the nearest repository commit at `2026-03-23T02:08:10Z`.
2. Mark references `[16]` and `[17]` as local repository evidence unless those dynamic-unl-scoring files are separately published.

## What This Does Not Prove

This packet does not prove model-scoring correctness or authority-transfer readiness. It only verifies that the paper's May 2026/testnet/provenance claims have checkable supporting receipts and identifies which citation surfaces remain local rather than public.

## Files

- `date_inventory.csv` — every date/provenance-sensitive whitepaper line found by the inventory.
- `artifact_inventory.csv` — local artifact presence, SHA-256, and relevant git history.
- `public_receipts.csv` — public URL reachability and hashes.
- `decoded_testnet_vl.json` — decoded public signed-list summary.
- `git_history.json` — relevant git history excerpts.
- `summary.json` — machine-readable summary.
- `COMMANDS.txt` — command transcript.
- `SHA256SUMS.txt` — artifact hashes.
