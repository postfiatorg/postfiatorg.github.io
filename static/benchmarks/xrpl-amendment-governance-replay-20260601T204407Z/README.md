# XRPL Amendment Governance Replay Packet

Generated: 2026-06-01T20:44:07Z

This packet supports the Post Fiat post `LLM Governance Replay`.

It contains 13 source-backed amendment/event packets selected by a
declared controversy-score rule, source receipts, and a deterministic rule
baseline. Run Qwen replay and summarization with:

```bash
python3 scripts/run_qwen_amendment_replay.py \
  --corpus static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/amendment_packets \
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \
  --model Qwen/Qwen3.6-27B-FP8 \
  --machine-receipt static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z/vast_lifecycle/machine_receipt.json \
  --runs 3 \
  --validators 41

python3 scripts/summarize_xrpl_amendment_replay.py \
  --packet static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z
```
