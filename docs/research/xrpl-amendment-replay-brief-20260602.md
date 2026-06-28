# XRPL Amendment Replay Brief

Generated: 2026-06-02

## Executive Summary

The LLM governance replay idea is still viable, but the current blog post and
seed-13 artifacts mix three different targets: XRP-native validator votes,
source-code default votes, and researcher-defined governance triage routes. That
mix is the core credibility risk.

XRPL amendments do not work like a static list of "open" or "closed" blog rows.
An amendment is introduced in `rippled`, validators signal support in validation
messages, and the amendment activates only after more than 80% support from
trusted validators persists for the required two-week period. If support drops,
the timer restarts. Once enabled, the amendment is permanent unless a later
amendment changes or disables behavior. If source code is removed without the
amendment enabling, the network treats the amendment as vetoed/retired rather
than as a normal activation.

That means a credible replay must define the replay target before running the
model:

- historical XRP vote/outcome replay: compare `YES/NO` to terminal outcomes
  such as enabled, vetoed/retired, explicit validator no-vote advisories, or
  observed support withdrawal;
- point-in-time vote-state replay: compare to a dated support state such as
  below threshold, majority active, majority lost, or enabled;
- governance triage replay: compare `PROCEED/HOLD/DELAY/REJECT` to a declared
  safety-policy label, not to validator history;
- default-vote replay: compare to source-code default vote, and call it exactly
  that.

The current blog is mostly a governance-triage post, but parts of the experiment
were later interpreted as historical validator vote replay. That interpretation
is not safe. The required course of action is to freeze the current post as a
pilot, rebuild the corpus from live amendment lifecycle evidence, and rerun only
after each packet declares which target it is testing.

## How XRPL Amendments Work

XRPL amendments are protocol changes that affect transaction processing. Code
for an amendment is shipped in a `rippled` release. Validators then vote by
including supported amendment IDs in their validation messages. Validator
operators can explicitly configure votes; if they do not, the server uses a
source-code default vote, which can change between software releases.

The important mechanics for replay are:

- activation requires more than 80% support from trusted validators for the
  normal two-week period;
- support can rise, fall, and restart the timer any number of times before
  activation;
- enabled amendments are terminal historical `YES` outcomes for vote replay;
- currently supported but not enabled amendments are not terminal `NO` outcomes;
- default vote is a software/config baseline, not a historical validator result;
- advisory cases, such as bug disclosures telling validators to vote `No`, are
  valid historical decision surfaces if the advisory itself is part of the facts
  validators saw;
- post-launch incidents may not map to one vote unless the packet names the
  exact surface, for example "continue supporting unfixed feature" versus
  "support corrective fix amendment."

The static Known Amendments page is useful but insufficient. For state labels,
the corpus must cross-check live ledger state and a vote-history source. In the
seed-13 audit, `PermissionedDomains`, `TokenEscrow`, and `PermissionedDEX` were
listed as open/default-`No` in the local snapshot but were enabled on mainnet in
February 2026. Treating those as open/default-only made the split artifact wrong.

As of the live check on 2026-06-02:

| Amendment | Introduced | State | Enabled on / support |
|---|---:|---|---:|
| PermissionedDomains | 2.4.0 | enabled | 2026-02-04 |
| TokenEscrow | 2.5.0 | enabled | 2026-02-12 |
| PermissionedDEX | 2.5.0 | enabled | 2026-02-18 |
| LendingProtocol | 3.1.0 | supported, not enabled | 8/35, threshold 28 |
| SingleAssetVault | 3.1.0 | supported, not enabled | 9/35, threshold 28 |

## How Replay Can Be Useful

Replay is useful if it reduces private coordination while improving the public
work product. It should not be sold as "the model votes correctly."

A strong replay packet should contain:

- a dated decision surface;
- amendment ID and release context;
- source facts available at that date;
- explicit source receipts and hashes;
- held-out labels outside the model prompt;
- live or archived vote state when relevant;
- a deterministic baseline output;
- a model output with cited facts, missing evidence, and a validator work item;
- a clear mapping from the model output to the measured label.

The most credible benchmark structure is multi-lane:

1. Historical outcome lane: model must emit `YES/NO`; compare only against
   terminal XRP-native outcomes. Enabled means `YES`. Vetoed/disabled/advised-no
   means `NO` only when source-backed.
2. Point-in-time state lane: model predicts `ENABLED`, `MAJORITY_ACTIVE`,
   `NO_MAJORITY`, `MAJORITY_LOST`, `VETOED`, or `UNKNOWN` for a dated snapshot.
   This is useful for year-old open votes that have not enabled.
3. Triage lane: model emits `PROCEED`, `HOLD_FOR_CHALLENGE`, `DELAY_FOR_FIX`,
   or `REJECT`; compare to a declared conservative policy label and report it as
   policy alignment, not validator-history alignment.
4. Work-item quality lane: model is scored on citations, missing evidence,
   risk framing, and override questions. This is where Qwen may add value even
   when deterministic rules tie route choice.

The old route table can survive only in lane 3. For example, calling
`PermissionedDEX` a `HOLD_FOR_CHALLENGE` case may be a defensible conservative
policy label because it changes compliance-gated market access. It is not a
historical `NO`, because it enabled on mainnet.

## Blog Assessment

The current post has a strong thesis: a public, deterministic replay object can
make validator governance cheaper and more inspectable than a standing private
committee. The math around independent detection versus correlated summaries is
directionally useful. The runtime receipt and convergence claims are also useful
operational evidence.

The unsafe parts are:

- the "13/13 historical route alignment" claim depends on researcher route
  labels, not XRP-native validator outcomes;
- `HOLD_FOR_CHALLENGE` is not an XRPL vote option and must not be presented as
  historical replay of validator votes;
- source default vote was treated too close to historical vote outcome in later
  analysis;
- the source snapshot was stale for several amendments that are now enabled;
- the AMM post-launch pool-discrepancy packet is ambiguous unless split into a
  named unfixed-state surface and a named corrective-fix surface;
- the blog does not separate "Qwen tied the deterministic rule engine" from
  "Qwen added useful work-item quality."

The post should not cite the old 13/13 result as historical validator replay.
It can cite it, after caveating, as a pilot showing deterministic execution and
route-schema convergence under a conservative policy label set.

## Required Course Of Action

1. Mark the current blog/post artifacts as a pilot or pull the results section
   until corrected. Do not cite `13/13 historical route alignment` without
   saying "under researcher-defined conservative triage labels."

2. Rebuild the source-of-truth corpus from authoritative amendment lifecycle
   data:
   - official XRPL amendment process docs;
   - official release notes introducing each amendment;
   - live validated `Amendments` ledger object;
   - XRPSCAN amendment API for enabled dates, support counts, thresholds, and
     introduced versions;
   - official vulnerability disclosures and release notes for no-vote cases;
   - archived source receipts for every page/API response.

3. Change the schema so each packet has separate fields:
   - `source_default_vote`;
   - `current_vote_state`;
   - `terminal_outcome`;
   - `historical_vote_label`;
   - `triage_policy_label`;
   - `label_basis`;
   - `eligible_metrics`.

4. Correct the seed-13 split:
   - historical lane should include the original 7 plus `PermissionedDomains`,
     `TokenEscrow`, and `PermissionedDEX` as enabled `YES` outcomes;
   - `LendingProtocol` and `SingleAssetVault` should be current-state cases,
     not terminal historical `NO`;
   - AMM post-launch pool discrepancy should remain excluded until split into
     specific vote surfaces.

5. Expand to 60+ examples by extracting amendment lifecycle events, not by
   stretching the original 13:
   - all enabled amendments with introduced version and enabled date;
   - all vetoed/obsolete/removed amendments;
   - majority-start and majority-loss events where vote history is available;
   - advisory no-vote events;
   - post-launch bug and follow-up fix pairs;
   - governance-sensitive primitives such as AMM, MPT, lending, vaults,
     permissioned domains/DEX, clawback, escrow, credentials, NFTs, and DIDs.

6. Rerun H200 only after the corpus validator passes. The validator must fail if
   a historical prompt leaks held-out outcome, if default vote is used as a
   terminal label, or if a non-XRPL route label is included in a vote-only
   comparison.

7. Rewrite the blog around the corrected claim:

   > In a source-backed replay of XRPL amendment lifecycle events, the model
   > produced deterministic, cited governance work items. Historical vote
   > alignment is measured only on terminal XRP-native outcomes; open vote-state
   > and conservative triage are reported separately.

This course preserves the valuable idea while removing the thing that would
damage credibility: pretending one metric measures three different governance
objects.

## Key Sources

- XRPL amendment process: https://xrpl.org/docs/concepts/networks-and-servers/amendments/
- XRPL known amendments: https://xrpl.org/resources/known-amendments
- `rippled` 2.4.0 release: https://xrpl.org/blog/2025/rippled-2.4.0
- `rippled` 2.5.0 release: https://xrpl.org/blog/2025/rippled-2.5.0
- `rippled` 3.1.0 release: https://xrpl.org/blog/2026/rippled-3.1.0
- XRPSCAN amendments API docs: https://docs.xrpscan.com/api-documentation/amendment/amendments
- XRPSCAN amendments API: https://api.xrpscan.com/api/v1/amendments
