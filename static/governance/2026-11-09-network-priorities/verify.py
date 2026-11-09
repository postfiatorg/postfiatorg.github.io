#!/usr/bin/env python3
"""Verify the Post Fiat governance entries of 9 November 2026. Standard library only.

    python3 verify.py                      # checks receipts, prompts, agreement and the log chain
    python3 verify.py --tokenizer tokenizer.json   # also re-decodes every output token (pip install tokenizers)

Run from the directory that holds log-entries.jsonl and receipts/.
"""
import base64
import glob
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM = "You are a helpful assistant."
EFFORT = "Reasoning Effort: 75 (range 1-100, the higher the value, the more thorough the reasoning)\n\n"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def render(question):
    # The pinned DeepSeek V4.1 chat rendering used by the worker (system + one user turn, thinking on).
    return "<｜begin▁of▁sentence｜><｜System｜>" + EFFORT + SYSTEM + "<｜User｜>" + question + "<｜Assistant｜><think>"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


tok = None
if "--tokenizer" in sys.argv:
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(sys.argv[sys.argv.index("--tokenizer") + 1])

failures = 0


def check(ok, label):
    global failures
    print(("PASS " if ok else "FAIL ") + label)
    failures += 0 if ok else 1


entries = [json.loads(x) for x in (ROOT / "log-entries.jsonl").read_text().splitlines() if x.strip()]
for i, e in enumerate(entries):
    print(f"\nEntry #{e['seq']}  round {e['round']}")
    body = {k: v for k, v in e.items() if k != "entry_sha256"}
    check(sha(canon(body)) == e["entry_sha256"], f"entry hash {e['entry_sha256'][:16]}... recomputes")
    if i:
        check(e["prev_entry_sha256"] == entries[i - 1]["entry_sha256"], "entry links to the previous entry")
    files = sorted(glob.glob(str(ROOT / "receipts" / f"entry-{e['seq']}" / "*.json")))
    rs = [json.loads(Path(f).read_text()) for f in files]
    check(len(rs) == 8, f"{len(rs)} receipts (4 GPU ranks x 2 machines)")
    machines = {r["execution"]["host"]["machine_id"] for r in rs}
    gpus = [g for r in rs[::4] for g in r["execution"]["host"]["gpu_uuids"]]
    check(len(machines) == 2 and len(set(gpus)) == 8, f"two distinct machines {sorted(machines)}, eight distinct GPUs")
    check(all(r["question"] == e["question"] for r in rs), "every receipt carries the logged question")
    prompt = render(e["question"]).encode()
    check(all(r["rendered_prompt_sha256"] == sha(prompt) for r in rs), "rendered prompt recomputes from the question")
    check(len({json.dumps(r["input_token_ids"]) for r in rs}) == 1, "identical input token IDs on all 8 ranks")
    check(len({json.dumps(r["output_token_ids"]) for r in rs}) == 1, f"identical output token IDs on all 8 ranks ({len(rs[0]['output_token_ids'])} tokens)")
    raws = [base64.b64decode(r["raw_output_base64"]) for r in rs]
    check(all(sha(b) == r["raw_sha256"] for b, r in zip(raws, rs)), "raw output bytes match each receipt's SHA-256")
    check(len({sha(b) for b in raws}) == 1, f"identical raw output bytes on all 8 ranks (sha256 {sha(raws[0])[:16]}...)")
    check(sha(raws[0]) == e["raw_output_sha256"], "raw output hash matches the log entry")
    check(rs[0]["content"] == e["answer"], "published answer equals the receipt's answer channel")
    check(all(r["effective_sampling"] == rs[0]["effective_sampling"] for r in rs) and rs[0]["effective_sampling"]["seq_seed"] == 438916795,
          "identical pinned sampling (temperature 1e-5, seed 438916795)")
    if tok:
        check(tok.encode(prompt.decode(), add_special_tokens=False).ids == rs[0]["input_token_ids"], "tokenizer reproduces the input token IDs")

print("\nALL CHECKS PASSED" if not failures else f"\n{failures} CHECK(S) FAILED")
sys.exit(1 if failures else 0)
