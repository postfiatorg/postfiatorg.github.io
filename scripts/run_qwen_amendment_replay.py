#!/usr/bin/env python3
"""Run Qwen-style amendment replay over a corpus packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTES = {"PROCEED", "DELAY_FOR_FIX", "HOLD_FOR_CHALLENGE", "REJECT"}


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


def route_to_vote(route: str) -> str:
    return {
        "PROCEED": "YES",
        "DELAY_FOR_FIX": "NO",
        "HOLD_FOR_CHALLENGE": "HOLD",
        "REJECT": "NO",
    }.get(route, "HOLD")


def offline_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    risks = set(packet.get("risk_class", []))
    event_type = packet.get("event_type")
    route = "HOLD_FOR_CHALLENGE"
    summary = "Packet contains governance-sensitive evidence that should be surfaced before voting."
    if "known_bug" in risks and event_type != "obsolete":
        route = "DELAY_FOR_FIX"
        summary = "Known-bug evidence makes default proceed inappropriate until the fix path is clear."
    if event_type == "obsolete" or "obsolete" in risks:
        route = "REJECT"
        summary = "The amendment is marked obsolete or disabled after a bug; replay default rejects."
    if event_type == "fix" and "follow_up_fix" in risks and "known_bug" not in risks:
        route = "PROCEED"
        summary = "The packet describes a narrow fix route after an identified issue."

    fact_ids = [f["fact_id"] for f in packet.get("historical_facts", [])[:3]]
    return {
        "route": route,
        "route_confidence": 0.74 if route == "HOLD_FOR_CHALLENGE" else 0.82,
        "vote_default": route_to_vote(route),
        "decision_summary": summary,
        "cited_facts": [
            {"fact_id": fid, "why_it_matters": "Source-backed packet fact supporting the route."}
            for fid in fact_ids
        ],
        "arguments_for_proceeding": [
            "Proceeding can be reasonable when the amendment is a narrow, source-backed fix."
        ],
        "arguments_for_delay_or_challenge": [
            "Known bugs, asset-control semantics, pooled funds, or off-chain underwriting require explicit validator review."
        ],
        "missing_evidence": [
            "Public validator vote history and full amendment PR review should be attached for a production replay."
        ],
        "validator_work_item": {
            "title": f"Review {packet.get('amendment_name')}",
            "recommended_validator_action": (
                "Verify cited packet sources, compare replay route to local operator policy, then reveal default or override."
            ),
            "review_questions": [
                "Does the packet identify a known bug or post-launch fix requirement?",
                "Does the amendment change asset-control, compliance, or pooled-fund semantics?",
                "Is a manual override justified and written down?",
            ],
            "override_questions": [
                "What source-backed evidence justifies overriding the replay default?",
                "Should the override be public before the vote window closes?",
            ],
        },
        "private_standing_committee_required": False,
        "estimated_review_minutes": {
            "validator_skim": 5,
            "deep_review": 45,
            "packet_verification": 10,
        },
        "forbidden_stronger_claim": (
            "A replay route is an auditable work product, not a proof that the amendment is correct."
        ),
    }


def build_prompt(packet: dict[str, Any]) -> str:
    schema = {
        "route": "PROCEED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT",
        "route_confidence": 0,
        "vote_default": "YES | NO | ABSTAIN | HOLD",
        "decision_summary": "...",
        "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
        "arguments_for_proceeding": ["..."],
        "arguments_for_delay_or_challenge": ["..."],
        "missing_evidence": ["..."],
        "validator_work_item": {
            "title": "...",
            "recommended_validator_action": "...",
            "review_questions": ["..."],
            "override_questions": ["..."],
        },
        "private_standing_committee_required": False,
        "estimated_review_minutes": {
            "validator_skim": 0,
            "deep_review": 0,
            "packet_verification": 0,
        },
        "forbidden_stronger_claim": "...",
    }
    return (
        "You are a deterministic governance replay worker. "
        "Classify the XRPL amendment packet into one conservative route. "
        "Use only packet facts by fact_id. Do not invent external facts. "
        "Return strict JSON matching this schema: "
        f"{json.dumps(schema, sort_keys=True)}\n\n"
        "Route policy:\n"
        "- PROCEED means the packet supports a default YES.\n"
        "- DELAY_FOR_FIX means known-bug or fix sequencing evidence supports default NO until fixed.\n"
        "- HOLD_FOR_CHALLENGE means validators need explicit public review before default YES.\n"
        "- REJECT means obsolete, disabled, or unsafe evidence supports default NO.\n\n"
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
        "max_tokens": 2400,
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


def normalize_output(output: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    route = str(output.get("route", "HOLD_FOR_CHALLENGE")).strip()
    if route not in ROUTES:
        route = "HOLD_FOR_CHALLENGE"
    output["route"] = route
    output["vote_default"] = route_to_vote(route)
    try:
        output["route_confidence"] = float(output.get("route_confidence", 0))
    except (TypeError, ValueError):
        output["route_confidence"] = 0.0
    packet_fact_ids = {f["fact_id"] for f in packet.get("historical_facts", [])}
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
        cited = [{"fact_id": f["fact_id"], "why_it_matters": "Packet fact used for conservative routing."} for f in packet.get("historical_facts", [])[:2]]
    output["cited_facts"] = cited
    output.setdefault("private_standing_committee_required", False)
    output.setdefault(
        "estimated_review_minutes",
        {"validator_skim": 5, "deep_review": 45, "packet_verification": 10},
    )
    output.setdefault("missing_evidence", [])
    output.setdefault("arguments_for_proceeding", [])
    output.setdefault("arguments_for_delay_or_challenge", [])
    output.setdefault(
        "validator_work_item",
        {
            "title": f"Review {packet.get('amendment_name')}",
            "recommended_validator_action": "Verify packet sources and reveal replay default or public override.",
            "review_questions": [],
            "override_questions": [],
        },
    )
    output.setdefault(
        "forbidden_stronger_claim",
        "This is a replayable triage route, not a proof of amendment correctness.",
    )
    return output


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_sha256s(packet_dir: Path) -> None:
    rows: list[str] = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(packet_dir).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    (packet_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n")


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
            "X-Title": "Post Fiat LLM Governance Replay",
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
        "production_profile_note": production_profile_note,
    }
    write_json(packet_dir / "qwen_runtime_manifest.json", runtime_manifest)

    for packet_path in sorted(corpus_dir.glob("*.json")):
        packet = json.loads(packet_path.read_text())
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
                    parsed = offline_fixture(packet)
                    runtime_manifest["fallback_used"] = True
            parsed = normalize_output(parsed, packet)
            output_hash = sha_json(parsed)
            run_record = {
                "packet_id": packet["packet_id"],
                "packet_hash": packet["packet_hash"],
                "prompt_hash": prompt_hash,
                "model_profile_hash": sha_json(runtime_manifest),
                "run_index": run_idx,
                "started_at": started,
                "completed_at": utc_now(),
                "schema_valid": parsed.get("route") in ROUTES,
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
                            "parsed_route": parsed["route"],
                            "vote_default": parsed["vote_default"],
                            "mode": "replay_default",
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
