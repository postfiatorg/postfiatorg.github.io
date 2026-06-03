#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export SGLANG_DISABLE_TORCH_COMPILE=0

nohup python3 -m http.server 8080 --directory /root >/root/http.log 2>&1 &

python3 -m sglang.launch_server \
  --model-path Qwen/Qwen3.6-27B-FP8 \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  --tp 1 \
  --context-length 32768 \
  --mem-fraction-static 0.75 \
  --enable-deterministic-inference \
  --max-running-requests 1 \
  --chunked-prefill-size 4096 \
  --attention-backend fa3 \
  --reasoning-parser qwen3 \
  >/root/sglang.log 2>&1
