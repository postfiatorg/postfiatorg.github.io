# SGLang Cross-Hardware Replay Evidence

Generated: 2026-06-03T15:26:11Z

This packet compares profile-addressed replay outputs. It separates machine/profile acceptance hashes, packet/prompt hashes, raw output hashes, parsed output hashes, route labels, cited source facts, and unsafe-proceed deltas.

## Comparisons

### h100nvl_selected_clean_repeat

- Profile A: `h100nvl_selected_a`
- Profile B: `h100nvl_selected_b`
- Rows: 271
- Profile acceptance hash match: `True`
- Packet hash mismatches: 0
- Prompt hash mismatches: 0
- Schema-invalid rows: 0
- Route-label mismatches: 0
- Source-fact-set mismatches: 0
- Unsafe-proceed deltas: 0
- Drift classes: `{"exact_raw_and_parsed_match": 271}`

### h100nvl_heldout_clean_repeat

- Profile A: `h100nvl_heldout_a`
- Profile B: `h100nvl_heldout_b`
- Rows: 187
- Profile acceptance hash match: `True`
- Packet hash mismatches: 0
- Prompt hash mismatches: 0
- Schema-invalid rows: 0
- Route-label mismatches: 0
- Source-fact-set mismatches: 0
- Unsafe-proceed deltas: 0
- Drift classes: `{"exact_raw_and_parsed_match": 187}`

### h100nvl_vs_second_cuda_heldout

- Profile A: `h100nvl_heldout_a`
- Profile B: `second_cuda_heldout`
- Rows: 187
- Profile acceptance hash match: `False`
- Packet hash mismatches: 0
- Prompt hash mismatches: 0
- Schema-invalid rows: 0
- Route-label mismatches: 0
- Source-fact-set mismatches: 0
- Unsafe-proceed deltas: 0
- Drift classes: `{"exact_raw_and_parsed_match": 187}`

## Combined Result

```text
combined_rows: 645
exact_raw_and_parsed_match: 645
combined_route_label_mismatches: 0
combined_unsafe_proceed_deltas: 0
schema_invalid_rows: 0 across all comparison rows
```

The CUDA run used two rented Vast instances:

- `h100nvl_base`: H100 NVL, instance `39300325`, offer `39293263`, host `531902`.
- `h100sxm_second`: H100 SXM, instance `39300330`, offer `36371403`, host `404057`.

Both instances were destroyed after evidence capture. `gpu_lifecycle/instances-after-destroy.json` records `active_target_instance_count: 0`.

## MLX Control

The same packet also includes a real Apple/MLX subset control:

```text
model: mlx-community/Qwen3-0.6B-4bit
runner: macos-15-xlarge
run: 26887497536
prompt_profile: mlx_no_think_suffix
packet_count: 4
run_count: 8
schema_valid_count: 8
same_packet_repeat_raw_matches: 4
same_packet_repeat_parsed_matches: 4
label_matches: 4
```

This MLX evidence is an independent-profile subset control. It is not Qwen/Qwen3.6-27B-FP8 SGLang equivalence.
