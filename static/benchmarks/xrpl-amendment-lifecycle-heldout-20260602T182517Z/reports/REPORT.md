# XRPL Amendment Lifecycle Replay Report

Generated: 2026-06-02T21:04:03Z

## Claim Gate

Use lane-specific language only. `HOLD_FOR_CHALLENGE` is a triage/work-item label and is not an XRP validator vote.
`default_vote` is diagnostic only; it is not a historical replay claim because source defaults are not validator outcomes.

Safe article claim form:

> On source-backed XRPL amendment lifecycle packets, Qwen matched terminal XRP-native vote/outcome labels on X/Y eligible cases, matched dated vote-state labels on A/B cases, and matched conservative governance triage labels on E/F cases.

## Lane Summaries

### vote_outcome

- Packets: 46
- Qwen runs: 138
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.9565
- Baseline alignment rate: 0.913
- Qwen-vs-rule disagreements: 6

### vote_state

- Packets: 47
- Qwen runs: 141
- Schema-valid output rate: 1.0
- Qwen alignment rate: 1.0
- Baseline alignment rate: 1.0
- Qwen-vs-rule disagreements: 0

### default_vote

- Packets: 47
- Qwen runs: 47
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.3404
- Baseline alignment rate: 0.5106
- Qwen-vs-rule disagreements: 19

### triage

- Packets: 47
- Qwen runs: 47
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.6596
- Baseline alignment rate: 0.5106
- Qwen-vs-rule disagreements: 33

## Disagreements

- `vote_outcome` `case_003--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_034--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `triage` `case_002--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_003--triage` expected `HOLD_FOR_CHALLENGE`, Qwen `REJECT`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_004--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_006--triage` expected `HOLD_FOR_CHALLENGE`, Qwen `PROCEED`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_015--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `DELAY_FOR_FIX`
- `triage` `case_019--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_020--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_033--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_034--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_035--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_036--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_039--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_041--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_043--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `DELAY_FOR_FIX`
- `triage` `case_045--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`
- `triage` `case_047--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `PROCEED`

Diagnostic `default_vote` disagreements are excluded from this claim gate; see `default_vote_disagreements.csv`.
