# XRPL Amendment Lifecycle Replay Report

Generated: 2026-06-03T03:19:04Z

## Claim Gate

Use lane-specific language only. `HOLD_FOR_CHALLENGE` is a triage/work-item label and is not an XRP validator vote.
`default_vote` is diagnostic only; it is not a historical replay claim because source defaults are not validator outcomes.

Safe article claim form:

> On source-backed XRPL amendment lifecycle packets, Qwen matched terminal XRP-native vote/outcome labels on X/Y eligible cases, matched dated vote-state labels on A/B cases, and matched conservative governance triage labels on E/F cases.

## Lane Summaries

### vote_outcome

- Packets: 60
- Qwen runs: 60
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.9
- Baseline alignment rate: 0.9667
- Qwen-vs-rule disagreements: 6

### vote_state

- Packets: 70
- Qwen runs: 70
- Schema-valid output rate: 1.0
- Qwen alignment rate: 1.0
- Baseline alignment rate: 1.0
- Qwen-vs-rule disagreements: 0

### default_vote

- Packets: 69
- Qwen runs: 69
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.1594
- Baseline alignment rate: 0.5072
- Qwen-vs-rule disagreements: 46

### triage

- Packets: 72
- Qwen runs: 72
- Schema-valid output rate: 1.0
- Qwen alignment rate: 0.9306
- Baseline alignment rate: 0.4028
- Qwen-vs-rule disagreements: 39

## Disagreements

- `vote_outcome` `case_005--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_006--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_013--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_014--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_049--vote_outcome` expected `YES`, Qwen `NO`, baseline `YES`
- `vote_outcome` `case_054--vote_outcome` expected `YES`, Qwen `NO`, baseline `NO`
- `triage` `case_002--triage` expected `HOLD_FOR_CHALLENGE`, Qwen `DELAY_FOR_FIX`, baseline `DELAY_FOR_FIX`
- `triage` `case_009--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_039--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_040--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `HOLD_FOR_CHALLENGE`
- `triage` `case_070--triage` expected `PROCEED`, Qwen `HOLD_FOR_CHALLENGE`, baseline `DELAY_FOR_FIX`

Diagnostic `default_vote` disagreements are excluded from this claim gate; see `default_vote_disagreements.csv`.
