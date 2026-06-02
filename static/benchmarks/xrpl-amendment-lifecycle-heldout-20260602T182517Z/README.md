# XRPL Amendment Lifecycle Held-Out Replay

Generated: 2026-06-02T18:26:12Z

Source artifact: `/home/postfiat/repos/postfiatorg.github.io/static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z`

This artifact contains lifecycle rows where `selected == false` in the source artifact.
It is a held-out validation set for the existing packet format and lane prompts.

## Counts

- Held-out lifecycle rows: 47
- Terminal outcome labels: {'YES': 46, 'NONE': 1}
- Triage labels: {'PROCEED': 36, 'HOLD_FOR_CHALLENGE': 11}
- Lane packet counts: {'vote_outcome': 46, 'vote_state': 47, 'default_vote': 47, 'triage': 47}

## Claim Boundary

`default_vote` is diagnostic only. `triage` is policy conformance. The clean historical lanes are `vote_outcome` and `vote_state`.
