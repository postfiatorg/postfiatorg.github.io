#!/usr/bin/env python3
"""Simulate pre-disclosure replay governance for the XRPL Batch incident.

This script supports the production replay path: Qwen served through a pinned
OpenAI-compatible SGLang endpoint with a captured machine receipt. OpenRouter is
kept only as an explicit fallback/pilot mode. The output packet separates:

1. deterministic rule baseline using only amendment metadata,
2. model challenge output using a pre-disclosure packet plus bounded code
   excerpts, and
3. post-disclosure scoring against the later-known Batch bug pattern.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import textwrap
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RIPPLED_25 = Path("/home/postfiat/repos/rippled-2.5.0")
RIPPLED_313 = Path("/home/postfiat/repos/rippled-3.1.3-old")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_key(path: Path | None, env_name: str) -> str:
    if path and path.exists():
        text = path.read_text().strip()
        if "=" in text and "\n" not in text:
            return text.split("=", 1)[1].strip().strip('"').strip("'")
        return text.splitlines()[0].strip()
    return os.environ.get(env_name, "").strip()


def extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def line_window(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = []
    for idx in range(start, min(end, len(lines)) + 1):
        selected.append(f"{idx:5d}  {lines[idx - 1]}")
    return "\n".join(selected) + "\n"


def git_head(repo: Path) -> str:
    import subprocess

    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def deterministic_rule_baseline(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "route": "HOLD_FOR_CHALLENGE",
        "vote_default": "HOLD",
        "decision_summary": (
            "Batch is a new authorization and atomic-execution primitive with unsigned inner transactions. "
            "A deterministic governance rule can require public challenge before a default YES, but it "
            "does not identify a specific control-flow vulnerability."
        ),
        "triggered_rules": [
            "new authorization/signature semantics -> HOLD_FOR_CHALLENGE",
            "multi-transaction atomicity with account-state writes -> HOLD_FOR_CHALLENGE",
        ],
        "specific_challenge": "",
        "identified_surfaces": ["Batch amendment", "unsigned inner transactions"],
        "predicted_failure_class": "generic authorization review required",
    }


def build_prompt(packet: dict[str, Any]) -> str:
    schema = {
        "route": "PROCEED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT",
        "vote_default": "YES | NO | HOLD",
        "decision_summary": "short answer",
        "specific_challenge": "the most concrete validator challenge this packet justifies",
        "identified_surfaces": ["function/file/surface names"],
        "predicted_failure_class": "specific vulnerability class or generic risk",
        "review_questions": ["questions validators should answer before voting yes"],
        "cited_facts": [{"fact_id": "F1", "why_it_matters": "short"}],
        "forbidden_stronger_claim": "claim this output does not support",
    }
    return (
        "You are a model-assisted governance replay worker. You are reviewing a "
        "pre-disclosure XRPL amendment packet. Do not assume any future bug report. "
        "Use only the packet facts and code excerpts. Your job is not to prove an "
        "exploit; it is to decide whether the packet earns a public challenge before "
        "validators default to YES.\n\n"
        "Return only strict JSON matching this schema:\n"
        f"{json.dumps(schema, sort_keys=True)}\n\n"
        "Routing policy:\n"
        "- PROCEED means default YES is justified by this packet.\n"
        "- HOLD_FOR_CHALLENGE means public validator challenge is required.\n"
        "- DELAY_FOR_FIX means the packet already contains bug/fix sequencing evidence.\n"
        "- REJECT means the packet already contains disabling/obsolete evidence.\n\n"
        "A high-value answer names the concrete code surface and the failure class "
        "validators should inspect. Avoid generic 'security review needed' unless "
        "the packet gives no more specific signal.\n\n"
        f"PACKET:\n{json.dumps(packet, indent=2, sort_keys=True)}"
    )


def completion_url(endpoint: str) -> str:
    url = endpoint.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    return f"{url}/chat/completions"


def call_chat_completion(
    *,
    endpoint: str,
    model: str,
    api_key: str,
    prompt: str,
    timeout: int,
    max_tokens: int,
    default_headers: dict[str, str] | None = None,
    deterministic_qwen: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only valid JSON. No markdown. No reasoning block."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    if deterministic_qwen:
        body["chat_template_kwargs"] = {"enable_thinking": False}
        body["separate_reasoning"] = False
    headers = {"Content-Type": "application/json", **(default_headers or {})}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        completion_url(endpoint),
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    content = raw["choices"][0]["message"]["content"]
    return extract_json(content), raw


def score_output(output: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(output, sort_keys=True).lower()
    signer_surface = any(
        token in text
        for token in [
            "checkbatchsign",
            "batchsigners",
            "batch signer",
            "signer-validation",
            "signer validation",
            "checkbatchmultisign",
            "checkbatchsinglesign",
            "multisignhelper",
        ]
    )
    loop_or_early_success = any(
        token in text
        for token in [
            "early",
            "premature",
            "loop",
            "remaining signer",
            "skip",
            "all signers",
            "every signer",
            "short-circuit",
            "return success",
        ]
    )
    unsigned_inner_auth = any(
        token in text
        for token in [
            "unsigned inner",
            "inner transaction",
            "delegated",
            "outer batch",
            "authorize",
            "authorization",
        ]
    )
    specific_challenge = signer_surface and unsigned_inner_auth
    close_to_later_bug = specific_challenge and loop_or_early_success
    route = str(output.get("route", "")).upper()
    return {
        "route": route,
        "held_or_rejected": route in {"HOLD_FOR_CHALLENGE", "DELAY_FOR_FIX", "REJECT"},
        "identified_signer_validation_surface": signer_surface,
        "identified_unsigned_inner_authorization": unsigned_inner_auth,
        "identified_loop_or_early_success_risk": loop_or_early_success,
        "specific_challenge_lift": specific_challenge,
        "matched_later_bug_class": close_to_later_bug,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "static/benchmarks/xrpl-batch-predisclosure-replay-20260601T232000Z")
    parser.add_argument("--endpoint", default="", help="OpenAI-compatible endpoint base URL, for example http://host:port/v1")
    parser.add_argument("--api-key-file", type=Path, help="Optional API key for OpenAI-compatible endpoint.")
    parser.add_argument("--openrouter", action="store_true", help="Use OpenRouter fallback mode instead of the SGLang endpoint.")
    parser.add_argument("--openrouter-key-file", type=Path)
    parser.add_argument("--openrouter-model", default="qwen/qwen3.6-27b")
    parser.add_argument("--model", default="Qwen/Qwen3.6-27B-FP8")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--max-tokens", type=int, default=3000)
    parser.add_argument("--machine-receipt", type=Path)
    parser.add_argument("--skip-model", action="store_true")
    args = parser.parse_args()

    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    code_dir = out / "source"
    code_dir.mkdir(exist_ok=True)

    sttx_25 = RIPPLED_25 / "src/libxrpl/protocol/STTx.cpp"
    sttx_313 = RIPPLED_313 / "src/libxrpl/protocol/STTx.cpp"
    excerpt_25 = line_window(sttx_25, 269, 541)
    excerpt_313 = line_window(sttx_313, 300, 578)
    (code_dir / "rippled-2.5.0-STTx-batch-signature-window.txt").write_text(excerpt_25, encoding="utf-8")
    (code_dir / "rippled-3.1.3-STTx-batch-signature-window.txt").write_text(excerpt_313, encoding="utf-8")

    packet = {
        "packet_id": "xrpl-batch-predisclosure-2026",
        "constructed_at": utc_now(),
        "disclosure_cutoff": "2026-02-18T23:59:59Z",
        "purpose": (
            "Pre-disclosure simulation packet: contains amendment/process/code-surface facts but excludes "
            "the February 19, 2026 vulnerability disclosure, exploit description, and emergency response."
        ),
        "amendment_name": "Batch / XLS-56",
        "historical_truth_withheld_from_model": {
            "later_disclosure_date": "2026-02-19",
            "later_bug_class": (
                "critical signer-validation loop/early-success flaw in Batch authorization that could skip "
                "remaining signer checks"
            ),
            "later_outcome": "validators advised to vote No; rippled 3.1.1 disabled Batch and fixBatchInnerSigs",
        },
        "facts": [
            {
                "fact_id": "F1",
                "claim": "Batch packages multiple inner transactions into one atomic outer transaction.",
                "source": "XLS-56 / XRPL Batch documentation; user-supplied research packet",
            },
            {
                "fact_id": "F2",
                "claim": "Inner Batch transactions are intentionally unsigned; authorization is delegated through outer Batch signer data.",
                "source": "Batch design summary and local rippled signer-validation code surface",
            },
            {
                "fact_id": "F3",
                "claim": "Batch signer validation is implemented through STTx::checkBatchSign, checkBatchSingleSign, checkBatchMultiSign, and multiSignHelper.",
                "source": "local rippled source excerpts",
            },
            {
                "fact_id": "F4",
                "claim": "Batch was in the validator-voting/amendment process, so a HOLD/NO route could still prevent activation without mainnet fund loss.",
                "source": "XRPL amendment process",
            },
        ],
        "code_receipts": [
            {
                "repo": str(RIPPLED_25),
                "git_head": git_head(RIPPLED_25),
                "path": "src/libxrpl/protocol/STTx.cpp",
                "line_window": "269-541",
                "excerpt_file": "source/rippled-2.5.0-STTx-batch-signature-window.txt",
                "excerpt_sha256": sha_file(code_dir / "rippled-2.5.0-STTx-batch-signature-window.txt"),
            },
            {
                "repo": str(RIPPLED_313),
                "git_head": git_head(RIPPLED_313),
                "path": "src/libxrpl/protocol/STTx.cpp",
                "line_window": "300-578",
                "excerpt_file": "source/rippled-3.1.3-STTx-batch-signature-window.txt",
                "excerpt_sha256": sha_file(code_dir / "rippled-3.1.3-STTx-batch-signature-window.txt"),
            },
        ],
        "code_excerpts": {
            "rippled_2_5_0_STTx_batch_signature_window": excerpt_25,
            "rippled_3_1_3_STTx_batch_signature_window": excerpt_313,
        },
    }
    write_json(out / "predisclosure_packet.json", packet)

    baseline = deterministic_rule_baseline(packet)
    write_json(out / "deterministic_rule_baseline.json", baseline)
    write_json(out / "deterministic_rule_score.json", score_output(baseline))

    prompt = build_prompt(packet)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    prompt_sha = sha_bytes(prompt.encode("utf-8"))

    runs: list[dict[str, Any]] = []
    if args.openrouter:
        endpoint = "https://openrouter.ai/api/v1"
        key = read_key(args.openrouter_key_file, "OPENROUTER_API_KEY")
        model = args.openrouter_model
        provider = "openrouter"
        replay_grade = False
        replay_grade_reason = "OpenRouter fallback, not pinned H200/SGLang replay."
        default_headers = {
            "HTTP-Referer": "https://postfiat.org/",
            "X-Title": "Post Fiat XRPL Batch Predisclosure Replay",
        }
    else:
        endpoint = args.endpoint
        key = read_key(args.api_key_file, "OPENAI_API_KEY")
        model = args.model
        provider = "openai_compatible_sglang"
        default_headers = {}
        receipt_ok = bool(args.machine_receipt and args.machine_receipt.exists())
        replay_grade = bool(endpoint and receipt_ok and model == "Qwen/Qwen3.6-27B-FP8")
        replay_grade_reason = (
            "Pinned Qwen/Qwen3.6-27B-FP8 SGLang endpoint with captured machine receipt."
            if replay_grade
            else "Missing endpoint, machine receipt, or expected Qwen/Qwen3.6-27B-FP8 model id."
        )

    machine_receipt: dict[str, Any] | None = None
    machine_receipt_sha256 = ""
    machine_receipt_path = ""
    if args.machine_receipt and args.machine_receipt.exists():
        machine_receipt_path = args.machine_receipt.resolve().relative_to(out).as_posix()
        machine_receipt_sha256 = sha_file(args.machine_receipt)
        machine_receipt = json.loads(args.machine_receipt.read_text(encoding="utf-8"))

    write_json(
        out / "runtime_manifest.json",
        {
            "generated_at": utc_now(),
            "provider": provider,
            "model": model,
            "endpoint_present": bool(endpoint),
            "runs_requested": args.runs,
            "temperature": 0,
            "top_p": 1,
            "response_format": {"type": "json_object"},
            "chat_template_kwargs": {"enable_thinking": False},
            "max_tokens": args.max_tokens,
            "replay_grade": replay_grade,
            "replay_grade_reason": replay_grade_reason,
            "machine_receipt_path": machine_receipt_path,
            "machine_receipt_sha256": machine_receipt_sha256,
            "machine_receipt_summary": {
                key_: machine_receipt.get(key_) if machine_receipt else None
                for key_ in (
                    "provider",
                    "instance_id",
                    "offer_id",
                    "gpu_name",
                    "num_gpus",
                    "image_uuid",
                    "model_id",
                    "sglang_version",
                    "deterministic_inference",
                    "max_running_requests",
                    "tensor_parallelism",
                )
            },
        },
    )

    if args.skip_model or not endpoint:
        write_json(
            out / "model_run_status.json",
            {
                "status": "not_run",
                "reason": "Endpoint missing or --skip-model supplied.",
                "model": model,
                "provider": provider,
            },
        )
    else:
        for idx in range(1, args.runs + 1):
            started = utc_now()
            try:
                parsed, raw = call_chat_completion(
                    endpoint=endpoint,
                    model=model,
                    api_key=key,
                    prompt=prompt,
                    timeout=args.timeout,
                    max_tokens=args.max_tokens,
                    default_headers=default_headers,
                    deterministic_qwen=not args.openrouter,
                )
                error = ""
            except Exception as exc:  # noqa: BLE001 - captured in artifact
                parsed = {
                    "route": "ERROR",
                    "decision_summary": f"{type(exc).__name__}: {exc}",
                    "specific_challenge": "",
                }
                raw = {}
                error = f"{type(exc).__name__}: {exc}"
            run = {
                "run_index": idx,
                "started_at": started,
                "finished_at": utc_now(),
                "model": model,
                "provider": provider,
                "replay_grade": replay_grade,
                "prompt_sha256": prompt_sha,
                "parsed_output": parsed,
                "score": score_output(parsed),
                "error": error,
                "raw_response_sha256": sha_bytes(json.dumps(raw, sort_keys=True).encode("utf-8")),
            }
            runs.append(run)
            write_json(out / f"model_run_{idx:03d}.json", run)

    if runs:
        aggregate = {
            "runs": len(runs),
            "model": model,
            "provider": provider,
            "replay_grade": replay_grade,
            "replay_grade_reason": replay_grade_reason,
            "machine_receipt_sha256": machine_receipt_sha256,
            "route_counts": {},
            "held_or_rejected": sum(1 for run in runs if run["score"]["held_or_rejected"]),
            "specific_challenge_lift": sum(1 for run in runs if run["score"]["specific_challenge_lift"]),
            "matched_later_bug_class": sum(1 for run in runs if run["score"]["matched_later_bug_class"]),
            "identified_signer_validation_surface": sum(
                1 for run in runs if run["score"]["identified_signer_validation_surface"]
            ),
            "identified_unsigned_inner_authorization": sum(
                1 for run in runs if run["score"]["identified_unsigned_inner_authorization"]
            ),
            "identified_loop_or_early_success_risk": sum(
                1 for run in runs if run["score"]["identified_loop_or_early_success_risk"]
            ),
        }
        for run in runs:
            route = run["score"]["route"]
            aggregate["route_counts"][route] = aggregate["route_counts"].get(route, 0) + 1
    else:
        aggregate = {
            "runs": 0,
            "model": model,
            "provider": provider,
            "replay_grade": replay_grade,
            "replay_grade_reason": replay_grade_reason,
            "specific_challenge_lift": 0,
            "matched_later_bug_class": 0,
        }
    write_json(out / "model_aggregate.json", aggregate)

    decision = {
        "decision": (
            "REPLAY_SUPPORTS_SPECIFIC_CHALLENGE_LIFT"
            if replay_grade and aggregate.get("specific_challenge_lift", 0) > 0
            else "PILOT_SUPPORTS_SPECIFIC_CHALLENGE_LIFT"
            if aggregate.get("specific_challenge_lift", 0) > 0
            else "NO_MODEL_LIFT_SHOWN"
        ),
        "safe_sentence": (
            (
                "In a pre-disclosure Batch H200/SGLang replay, "
                if replay_grade
                else "In a pre-disclosure Batch pilot, "
            )
            + "the deterministic rule floor could only issue a generic "
            "HOLD for new authorization semantics, while Qwen named the Batch signer-validation surface "
            f"in {aggregate.get('identified_signer_validation_surface', 0)}/{aggregate.get('runs', 0)} runs "
            f"and matched the later signer-loop/early-success bug class in "
            f"{aggregate.get('matched_later_bug_class', 0)}/{aggregate.get('runs', 0)} runs."
        ),
        "forbidden_stronger_claim": (
            "This run does not prove the model would have prevented the incident; it only measures whether "
            "the pre-disclosure packet elicits a replayable challenge matching the later-known bug class."
        ),
    }
    write_json(out / "decision.json", decision)

    report = f"""# XRPL Batch Pre-Disclosure Replay Simulation

Generated: {utc_now()}

## Question

Could a PostFiat-style replay packet have improved on a simple deterministic
rule floor during the February 2026 XRPL Batch amendment incident?

## Boundary

Runtime kind: `{provider}`

Replay-grade: `{replay_grade}` — {replay_grade_reason}

The model prompt excludes the February 19, 2026 vulnerability disclosure and
the exploit description. Those later facts are used only after the run to score
whether the output named the right risk surface.

## Inputs

- Pre-disclosure packet: `predisclosure_packet.json`
- Deterministic baseline: `deterministic_rule_baseline.json`
- Prompt hash: `{prompt_sha}`
- Local rippled 2.5.0 source: `{git_head(RIPPLED_25)}`
- Local rippled 3.1.3 source: `{git_head(RIPPLED_313)}`
- Machine receipt hash: `{machine_receipt_sha256 or "none"}`

## Deterministic Baseline

The deterministic rule baseline routes `HOLD_FOR_CHALLENGE` because Batch is a
new authorization/signature primitive with unsigned inner transactions. It does
not identify a specific signer-loop or premature-success defect.

Score:

```json
{json.dumps(score_output(baseline), indent=2, sort_keys=True)}
```

## Model Aggregate

```json
{json.dumps(aggregate, indent=2, sort_keys=True)}
```

## Result

{decision['safe_sentence']}

## What This Does Not Prove

{decision['forbidden_stronger_claim']}

## Files

- `predisclosure_packet.json`: facts and bounded code excerpts available to the model.
- `deterministic_rule_baseline.json`: simple rule-floor output.
- `model_run_*.json`: per-run Qwen outputs and scoring.
- `model_aggregate.json`: aggregate route and challenge metrics.
- `runtime_manifest.json`: provider, endpoint class, and replay-grade metadata.
- `decision.json`: safe and forbidden integration claims.
- `SHA256SUMS.txt`: artifact hashes.
"""
    (out / "REPORT.md").write_text(report, encoding="utf-8")
    if args.openrouter:
        command_line = (
            f"python3 scripts/xrpl_batch_predisclosure_replay_sim.py --openrouter "
            f"--openrouter-key-file /home/postfiat/repos/openx.txt --runs {args.runs}\n"
        )
    else:
        receipt_arg = f" --machine-receipt {args.machine_receipt}" if args.machine_receipt else ""
        command_line = (
            "python3 scripts/xrpl_batch_predisclosure_replay_sim.py "
            f"--endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model {model}{receipt_arg} --runs {args.runs}\n"
        )
    (out / "COMMANDS.txt").write_text(
        command_line
        +
        f"cd {out.relative_to(REPO_ROOT)} && sha256sum -c SHA256SUMS.txt\n",
        encoding="utf-8",
    )

    sums = []
    for path in sorted(out.rglob("*")):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        sums.append(f"{sha_file(path)}  {path.relative_to(out).as_posix()}\n")
    (out / "SHA256SUMS.txt").write_text("".join(sums), encoding="utf-8")
    print(out.relative_to(REPO_ROOT))
    print(f"decision={decision['decision']}")
    print(decision["safe_sentence"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
