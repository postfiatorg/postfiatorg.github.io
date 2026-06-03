# SGLang Cross-Hardware Replay Evidence

Generated: 2026-06-03T03:47:50Z

This packet compares profile-addressed replay outputs. It separates machine/profile acceptance hashes, packet/prompt hashes, raw output hashes, parsed output hashes, route labels, cited source facts, and unsafe-proceed deltas.

## Comparisons

### h200_repeatability_selected

- Profile A: `h200_sglang_initial_selected`
- Profile B: `h200_sglang_repeat_selected`
- Rows: 271
- Profile acceptance hash match: `False`
- Packet hash mismatches: 0
- Prompt hash mismatches: 271
- Schema-invalid rows: 0
- Route-label mismatches: 28
- Source-fact-set mismatches: 87
- Unsafe-proceed deltas: 0
- Drift classes: `{"invalid_input_mismatch": 271}`

### h200_repeatability_heldout

- Profile A: `h200_sglang_initial_heldout`
- Profile B: `h200_sglang_repeat_heldout`
- Rows: 187
- Profile acceptance hash match: `False`
- Packet hash mismatches: 0
- Prompt hash mismatches: 0
- Schema-invalid rows: 0
- Route-label mismatches: 0
- Source-fact-set mismatches: 0
- Unsafe-proceed deltas: 0
- Drift classes: `{"exact_raw_and_parsed_match": 187}`

### h200_repeat_vs_h100nvl_heldout

- Profile A: `h200_sglang_repeat_heldout`
- Profile B: `h100nvl_sglang_heldout`
- Rows: 187
- Profile acceptance hash match: `False`
- Packet hash mismatches: 0
- Prompt hash mismatches: 0
- Schema-invalid rows: 0
- Route-label mismatches: 0
- Source-fact-set mismatches: 0
- Unsafe-proceed deltas: 0
- Drift classes: `{"exact_raw_and_parsed_match": 187}`

