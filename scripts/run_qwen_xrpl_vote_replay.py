#!/usr/bin/env python3
"""Run Qwen vote-only XRPL amendment replay over a packet corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VOTES = {"YES", "NO"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_json(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def read_key(path: Path | None, env_name: str) -> str:
    if path and path.exists():
        text = path.read_text().strip()
        if "=" in text and "\n" not in text:
            return text.split("=", 1)[1].strip().strip('"').strip("'")
        return text.splitlines()[0].strip()
    return os.environ.get(env_name, "").strip()


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def offline_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(packet, sort_keys=True).lower()
    vote = "NO"
    if "default_vote" in text and '"yes"' in text:
        vote = "YES"
    if "advised" in text and "vote no" in text:
        vote = "NO"
    return {
        "xrpl_vote_recommendation": vote,
        "vote_confidence": 0.75,
        "decision_summary": "Offline fixture used; not valid replay evidence.",
        "cited_facts": [
            {
                "fact_id": fact["fact_id"],
                "why_it_matters": "Packet fact used for XRP-native vote replay.",
            }
            for fact in packet.get("historical_facts", [])[:2]
        ],
        "arguments_for_yes": [],
        "arguments_for_no": [],
        "missing_evidence": [],
        "unscored_review_flags": {
            "needs_public_review": False,
            "bug_or_fix_sequence": False,
            "asset_control_or_compliance": False,
            "source_default_vote_used": False,
        },
        "forbidden_stronger_claim": "A YES/NO replay recommendation is not proof that the amendment is correct.",
    }


def build_prompt(packet: dict[str, Any]) -> str:
    schema = {
        "xrpl_vote_recommendation": "YES | NO",
        "vote_confidence": 0,
        "decision_summary": "...",
        "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
        "arguments_for_yes": ["..."],
        "arguments_for_no": ["..."],
        "missing_evidence": ["..."],
        "unscored_review_flags": {
            "needs_public_review": False,
            "bug_or_fix_sequence": False,
            "asset_control_or_compliance": False,
            "source_default_vote_used": False,
        },
        "forbidden_stronger_claim": "...",
    }
    return (
        "You are a deterministic XRPL amendment vote replay worker. "
        "Use only packet facts by fact_id. Do not invent external facts. "
        "Return strict JSON matching this schema: "
        f"{json.dumps(schema, sort_keys=True)}\n\n"
        "Scored vote policy:\n"
        "- The only scored field is xrpl_vote_recommendation.\n"
        "- The only allowed scored values are YES and NO.\n"
        "- YES means support, approve, or enable the amendment/change at the relevant XRPL vote surface.\n"
        "- NO means oppose, veto, or do not support enabling the amendment/change at the relevant XRPL vote surface.\n"
        "- Any third option or internal workflow state is not an XRPL vote output; do not emit one in the scored field.\n"
        "- Review concerns may be placed only in unscored_review_flags and rationale fields.\n\n"
        f"PACKET:\n{json.dumps(packet, indent=2, sort_keys=True)}"
    )


def call_chat_completion(
    endpoint: str,
    model: str,
    api_key: str,
    prompt: str,
    default_headers: dict[str, str],
    timeout: int,
    deterministic_qwen: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    url = endpoint.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return only valid JSON. No markdown. No commentary.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 1800,
        "response_format": {"type": "json_object"},
    }
    if deterministic_qwen:
        body["chat_template_kwargs"] = {"enable_thinking": False}
        body["separate_reasoning"] = False
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        **default_headers,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    content = raw["choices"][0]["message"]["content"]
    return extract_json(content), raw


def normalize_output(output: dict[str, Any], packet: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    raw_vote = str(output.get("xrpl_vote_recommendation", "")).strip().upper()
    schema_valid = raw_vote in VOTES
    vote = raw_vote if schema_valid else "NO"
    output["xrpl_vote_recommendation"] = vote
    try:
        output["vote_confidence"] = float(output.get("vote_confidence", 0))
    except (TypeError, ValueError):
        output["vote_confidence"] = 0.0

    packet_fact_ids = {fact["fact_id"] for fact in packet.get("historical_facts", [])}
    cited = []
    for item in output.get("cited_facts", []):
        if isinstance(item, dict) and item.get("fact_id") in packet_fact_ids:
            cited.append(
                {
                    "fact_id": item["fact_id"],
                    "why_it_matters": str(item.get("why_it_matters", ""))[:500],
                }
            )
    if not cited:
        cited = [
            {
                "fact_id": fact["fact_id"],
                "why_it_matters": "Packet fact used for XRP-native vote replay.",
            }
            for fact in packet.get("historical_facts", [])[:2]
        ]
    output["cited_facts"] = cited
    output.setdefault("decision_summary", "")
    output.setdefault("arguments_for_yes", [])
    output.setdefault("arguments_for_no", [])
    output.setdefault("missing_evidence", [])
    flags = output.get("unscored_review_flags")
    if not isinstance(flags, dict):
        flags = {}
    output["unscored_review_flags"] = {
        "needs_public_review": bool(flags.get("needs_public_review", False)),
        "bug_or_fix_sequence": bool(flags.get("bug_or_fix_sequence", False)),
        "asset_control_or_compliance": bool(flags.get("asset_control_or_compliance", False)),
        "source_default_vote_used": bool(flags.get("source_default_vote_used", False)),
    }
    output.setdefault(
        "forbidden_stronger_claim",
        "A YES/NO replay recommendation is not proof that the amendment is correct.",
    )
    return output, schema_valid


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256s(packet_dir: Path) -> None:
    rows: list[str] = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(packet_dir).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    (packet_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--model", default="Qwen/Qwen3.6-27B-FP8")
    parser.add_argument("--api-key-file", type=Path)
    parser.add_argument("--openrouter-key-file", type=Path)
    parser.add_argument("--openrouter", action="store_true")
    parser.add_argument("--openrouter-model", default="qwen/qwen3.6-27b")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--validators", type=int, default=41)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--machine-receipt", type=Path)
    parser.add_argument("--offline-fixture", action="store_true")
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Abort instead of substituting the offline fixture when an endpoint call fails.",
    )
    args = parser.parse_args(argv)

    corpus_dir = args.corpus.resolve()
    packet_dir = corpus_dir.parent
    qwen_dir = packet_dir / "qwen_runs"
    qwen_dir.mkdir(exist_ok=True)

    if args.openrouter:
        endpoint = "https://openrouter.ai/api/v1"
        api_key = read_key(args.openrouter_key_file, "OPENROUTER_API_KEY")
        model = args.openrouter_model
        runtime_kind = "openrouter_qwen_pilot_not_deterministic_sglang"
        default_headers = {
            "HTTP-Referer": "https://postfiat.org/",
            "X-Title": "Post Fiat XRPL Vote Replay",
        }
    else:
        endpoint = args.endpoint
        api_key = read_key(args.api_key_file, "OPENAI_API_KEY")
        model = args.model
        runtime_kind = "openai_compatible_sglang"
        default_headers = {}
        if os.environ.get("MODAL_KEY") and os.environ.get("MODAL_SECRET"):
            default_headers["Modal-Key"] = os.environ["MODAL_KEY"]
            default_headers["Modal-Secret"] = os.environ["MODAL_SECRET"]

    machine_receipt: dict[str, Any] | None = None
    machine_receipt_sha256 = ""
    machine_receipt_path = ""
    if args.machine_receipt:
        machine_receipt_path = args.machine_receipt.resolve().relative_to(packet_dir).as_posix()
        machine_receipt_bytes = args.machine_receipt.read_bytes()
        machine_receipt_sha256 = hashlib.sha256(machine_receipt_bytes).hexdigest()
        machine_receipt = json.loads(machine_receipt_bytes.decode("utf-8"))

    production_profile_note = (
        "Production replay uses Qwen/Qwen3.6-27B-FP8 on deterministic SGLang with a captured machine receipt."
    )
    if args.openrouter:
        production_profile_note = (
            "This is an OpenRouter pilot run. It is not bit-exact replay evidence and should not be used "
            "as the production governance replay profile."
        )

    runtime_manifest = {
        "generated_at": utc_now(),
        "runtime_kind": "offline_fixture" if args.offline_fixture else runtime_kind,
        "endpoint_present": bool(endpoint),
        "model": model,
        "machine_receipt_path": machine_receipt_path,
        "machine_receipt_sha256": machine_receipt_sha256,
        "machine_receipt_summary": {
            key: machine_receipt.get(key)
            for key in (
                "provider",
                "provider_run_id",
                "gpu_name",
                "gpu_ram",
                "image_uuid",
                "model_id",
                "deterministic_inference",
                "max_running_requests",
            )
        } if machine_receipt else {},
        "runs_per_packet": args.runs,
        "simulated_validators": args.validators,
        "temperature": 0,
        "top_p": 1,
        "scored_output_field": "xrpl_vote_recommendation",
        "allowed_scored_values": sorted(VOTES),
        "production_profile_note": production_profile_note,
        "fallback_used": False,
    }
    write_json(packet_dir / "qwen_runtime_manifest.json", runtime_manifest)

    for packet_path in sorted(corpus_dir.glob("*.json")):
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        out_dir = qwen_dir / packet["packet_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        prompt = build_prompt(packet)
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        for run_idx in range(1, args.runs + 1):
            started = utc_now()
            raw_response: dict[str, Any] | None = None
            error = ""
            if args.offline_fixture:
                parsed = offline_fixture(packet)
            else:
                try:
                    parsed, raw_response = call_chat_completion(
                        endpoint=endpoint,
                        model=model,
                        api_key=api_key,
                        prompt=prompt,
                        default_headers=default_headers,
                        timeout=args.timeout,
                        deterministic_qwen=(not args.openrouter),
                    )
                except Exception as exc:  # noqa: BLE001 - recorded per run
                    error = f"{type(exc).__name__}: {exc}"
                    if args.fail_on_error:
                        raise RuntimeError(
                            f"Endpoint call failed for {packet['packet_id']} run {run_idx}: {error}"
                        ) from exc
                    parsed = offline_fixture(packet)
                    runtime_manifest["fallback_used"] = True
                    write_json(packet_dir / "qwen_runtime_manifest.json", runtime_manifest)
            parsed, schema_valid = normalize_output(parsed, packet)
            output_hash = sha_json(parsed)
            run_record = {
                "packet_id": packet["packet_id"],
                "packet_hash": packet["packet_hash"],
                "prompt_hash": prompt_hash,
                "model_profile_hash": sha_json(runtime_manifest),
                "run_index": run_idx,
                "started_at": started,
                "completed_at": utc_now(),
                "schema_valid": schema_valid,
                "runtime_kind": runtime_manifest["runtime_kind"],
                "model": model,
                "error": error,
                "output_hash": output_hash,
                "output_json": parsed,
                "raw_response_shape": {
                    "keys": sorted(raw_response.keys()) if isinstance(raw_response, dict) else [],
                    "choice_count": len(raw_response.get("choices", [])) if isinstance(raw_response, dict) else 0,
                },
            }
            write_json(out_dir / f"run_{run_idx:03d}.json", run_record)

            validators = []
            rng = random.Random(f"{packet['packet_hash']}:{output_hash}:{run_idx}")
            for validator_idx in range(1, args.validators + 1):
                salt = hashlib.sha256(f"{validator_idx}:{rng.random()}".encode()).hexdigest()
                commit = hashlib.sha256(
                    f"{packet['packet_hash']}|{run_record['model_profile_hash']}|{output_hash}|{salt}".encode()
                ).hexdigest()
                validators.append(
                    {
                        "validator": f"sim-validator-{validator_idx:02d}",
                        "commit": commit,
                        "reveal": {
                            "packet_hash": packet["packet_hash"],
                            "model_profile_hash": run_record["model_profile_hash"],
                            "output_hash": output_hash,
                            "salt": salt,
                            "parsed_xrpl_vote_recommendation": parsed["xrpl_vote_recommendation"],
                            "mode": "vote_only_replay",
                        },
                    }
                )
            write_json(
                out_dir / f"commit_reveal_{run_idx:03d}.json",
                {
                    "packet_id": packet["packet_id"],
                    "run_index": run_idx,
                    "commit_reveal_valid": True,
                    "validators": validators,
                },
            )
            time.sleep(0.2)

    write_sha256s(packet_dir)
    print(packet_dir.relative_to(REPO_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
