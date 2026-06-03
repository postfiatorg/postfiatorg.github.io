# triage Report

{
  "deterministic_baseline_alignment_count": 29,
  "deterministic_baseline_alignment_rate": 0.4028,
  "endpoint_error_count": 0,
  "exact_output_hash_converged_packets": 72,
  "fallback_used": false,
  "generated_at": "2026-06-03T03:19:04Z",
  "label_counts": {
    "DELAY_FOR_FIX": 1,
    "HOLD_FOR_CHALLENGE": 35,
    "PROCEED": 22,
    "REJECT": 14
  },
  "lane": "triage",
  "not_run_count": 0,
  "packet_count": 72,
  "parsed_label_converged_packets": 72,
  "qwen_alignment_count": 67,
  "qwen_alignment_rate": 0.9306,
  "qwen_vs_rule_disagreement_count": 39,
  "schema_valid_output_rate": 1.0,
  "total_qwen_runs": 72,
  "triage_policy_alignment_rate": 0.9306,
  "unnecessary_hold_count": 4,
  "unsafe_proceed_count": 0
}

## Disagreements

- `case_002--triage` expected `HOLD_FOR_CHALLENGE`, got `DELAY_FOR_FIX`
- `case_009--triage` expected `PROCEED`, got `HOLD_FOR_CHALLENGE`
- `case_039--triage` expected `PROCEED`, got `HOLD_FOR_CHALLENGE`
- `case_040--triage` expected `PROCEED`, got `HOLD_FOR_CHALLENGE`
- `case_070--triage` expected `PROCEED`, got `HOLD_FOR_CHALLENGE`
