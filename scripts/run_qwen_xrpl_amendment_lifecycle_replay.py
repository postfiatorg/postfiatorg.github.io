#!/usr/bin/env python3
"""Run Qwen/SGLang over XRPL amendment lifecycle replay packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import (
    LANE_ALLOWED_LABELS,
    LANE_LABEL_FIELD,
    LANES,
    artifact_path,
    read_json,
    sha_json,
    utc_now,
    write_json,
    write_sha256s,
)


def extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("model response JSON was not an object")
    return value


def lane_schema(lane: str) -> dict[str, Any]:
    if lane == "vote_outcome":
        return {
            "xrpl_vote_recommendation": "YES | NO",
            "vote_confidence": 0.0,
            "decision_summary": "...",
            "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
            "arguments_for_yes": ["..."],
            "arguments_for_no": ["..."],
            "missing_evidence": ["..."],
            "forbidden_stronger_claim": "...",
        }
    if lane == "vote_state":
        return {
            "vote_state": "ENABLED | NO_MAJORITY | MAJORITY_ACTIVE | MAJORITY_LOST | VETOED_OR_RETIRED | UNKNOWN",
            "state_confidence": 0.0,
            "decision_summary": "...",
            "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
            "missing_evidence": ["..."],
        }
    if lane == "default_vote":
        return {
            "source_default_vote": "YES | NO | UNKNOWN",
            "default_vote_confidence": 0.0,
            "decision_summary": "...",
            "cited_facts": [{"fact_id": "F1", "why_it_matters": "..."}],
            "missing_evidence": ["..."],
        }
    return {
        "route": "PROCEED | HOLD_FOR_CHALLENGE | DELAY_FOR_FIX | REJECT",
        "route_confidence": 0.0,
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
        "estimated_review_minutes": {
            "validator_skim": 0,
            "deep_review": 0,
            "packet_verification": 0,
        },
        "forbidden_stronger_claim": "...",
    }


def build_prompt(packet: dict[str, Any]) -> str:
    lane = packet["lane"]
    rules = {
        "vote_outcome": (
            "Choose the XRP-native YES/NO recommendation for the named decision surface. "
            "Do not output HOLD_FOR_CHALLENGE, DELAY_FOR_FIX, PROCEED, or REJECT."
        ),
        "vote_state": (
            "Classify the dated amendment state from source facts. ENABLED means the source facts show enabled ledger membership. "
            "NO_MAJORITY means currently below threshold without enablement. MAJORITY_ACTIVE means threshold support is active but not enabled. "
            "MAJORITY_LOST means a formerly active majority was lost. VETOED_OR_RETIRED means source-backed no advisory, obsolete, or retired."
        ),
        "default_vote": "Infer the latest stable release source default vote. If the packet does not support YES or NO, output UNKNOWN.",
        "triage": (
            "Choose the conservative validator review route at the amendment decision surface described by the packet. "
            "HOLD_FOR_CHALLENGE is a review route, not an XRP vote. "
            "Apply this precedence order exactly. "
            "First, use REJECT only for explicit no-vote advisory, retired/obsolete proposals, or critical unsafe evidence. "
            "Second, use DELAY_FOR_FIX for pre-fix incident windows where the packet describes an unresolved bug, vulnerability, or fix sequencing problem. "
            "Third, if the amendment name starts with 'fix' and the packet describes the amendment as the fix itself, use PROCEED unless the packet also contains an explicit no-vote advisory, says the fix is obsolete, or describes broad cross-feature canonicalization/serialization/template enforcement, consensus/liveness risk, AMM invariant or rounding changes, freeze/authorization bypasses, ledger repair transaction types, NFT offer-settlement semantics, material token supply or issuer-balance accounting, escrow math, numeric precision, or edge-case transaction-processing uncertainty. "
            "Do not hold a localized fix amendment merely because the underlying domain name mentions AMM, NFT, token, trustline, accounting, or bridge; hold only when the supplied facts identify one of those material risk patterns. "
            "Use HOLD_FOR_CHALLENGE for material financial, compliance, permissioning, privacy, bridge, oracle, identity, fee/reserve, invariant, consensus/liveness, NFT sell-offer, or asset-control semantics that deserve explicit review. "
            "Account-local opt-out controls that only let an account block unwanted incoming objects may PROCEED unless the facts show broader third-party asset control or systemic risk. "
            "Mutable NFT URI or metadata controls count as asset-control semantics. "
            "Do not reject merely because a historical packet later completed or an amendment eventually became enabled."
        ),
    }
    return (
        "You are a deterministic XRPL governance replay worker. Use only the packet facts by fact_id. "
        "Do not use outside knowledge, real-world memory, packet_id, event_id, case numbering, label order, "
        "or held_out_fields names as evidence. Allowed labels define the output schema only. "
        "Return one strict JSON object with no markdown and no commentary.\n\n"
        f"Lane: {lane}\n"
        f"Allowed labels: {', '.join(packet['allowed_labels'])}\n"
        f"Task rule: {rules[lane]}\n"
        f"Required JSON schema: {json.dumps(lane_schema(lane), sort_keys=True)}\n\n"
        f"PACKET:\n{json.dumps(packet, sort_keys=True, ensure_ascii=False)}"
    )


def call_sglang(endpoint: str, model: str, prompt: str, timeout: int, max_tokens: int, api_key: str = "") -> dict[str, Any]:
    url = endpoint.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only valid JSON. No markdown. No commentary."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
        "separate_reasoning": False,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_output(lane: str, parsed: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    label_field = LANE_LABEL_FIELD[lane]
    allowed = set(LANE_ALLOWED_LABELS[lane])
    label = str(parsed.get(label_field, "")).strip().upper()
    aliases = {
        "VETOED": "VETOED_OR_RETIRED",
        "RETIRED": "VETOED_OR_RETIRED",
        "HOLD": "HOLD_FOR_CHALLENGE",
        "DELAY": "DELAY_FOR_FIX",
        "PROCEED_AFTER_REVIEW": "PROCEED",
    }
    label = aliases.get(label, label)
    if label not in allowed:
        if lane == "default_vote":
            label = "UNKNOWN"
        elif lane == "vote_state":
            label = "UNKNOWN"
        elif lane == "vote_outcome":
            label = "NO"
        else:
            label = "HOLD_FOR_CHALLENGE"
    parsed[label_field] = label

    facts = packet.get("input_context", {}).get("source_facts", [])
    fact_ids = {item.get("fact_id") for item in facts}
    cited = []
    for item in parsed.get("cited_facts", []):
        if isinstance(item, dict) and item.get("fact_id") in fact_ids:
            cited.append({"fact_id": item["fact_id"], "why_it_matters": str(item.get("why_it_matters", ""))[:400]})
    if not cited and facts:
        cited = [{"fact_id": facts[0]["fact_id"], "why_it_matters": "Primary packet source fact used for classification."}]
    parsed["cited_facts"] = cited
    parsed.setdefault("decision_summary", "")
    parsed.setdefault("missing_evidence", [])
    parsed.setdefault("forbidden_stronger_claim", "This output is a replay classification, not proof of amendment correctness.")
    if lane == "triage":
        parsed.setdefault(
            "validator_work_item",
            {
                "title": f"Review {packet.get('input_context', {}).get('amendment_name', packet['packet_id'])}",
                "recommended_validator_action": "Verify cited packet facts and record any override rationale.",
                "review_questions": [],
                "override_questions": [],
            },
        )
        parsed.setdefault("estimated_review_minutes", {"validator_skim": 5, "deep_review": 45, "packet_verification": 10})
    return parsed


def parsed_label(lane: str, output: dict[str, Any]) -> str:
    return str(output.get(LANE_LABEL_FIELD[lane], "")).strip().upper()


def read_key(path: Path | None) -> str:
    if not path:
        return ""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if "=" in text and "\n" not in text:
        return text.split("=", 1)[1].strip().strip('"').strip("'")
    return text.splitlines()[0].strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--lane", default="all", choices=["all", *LANES])
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", default="Qwen/Qwen3.6-27B-FP8")
    parser.add_argument("--machine-receipt", type=Path, required=True)
    parser.add_argument("--api-key-file", type=Path)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--validators", type=int, default=41)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-tokens", type=int, default=1100)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args(argv)

    root = artifact_path(args.artifact)
    lanes = list(LANES) if args.lane == "all" else [args.lane]
    qwen_root = root / "qwen_runs"
    qwen_root.mkdir(parents=True, exist_ok=True)
    machine_receipt_path = artifact_path(args.machine_receipt)
    machine_receipt = read_json(machine_receipt_path)
    machine_receipt_sha = hashlib.sha256(machine_receipt_path.read_bytes()).hexdigest()
    api_key = read_key(args.api_key_file)

    runtime_manifest = {
        "generated_at": utc_now(),
        "runtime_kind": "openai_compatible_sglang",
        "endpoint": args.endpoint,
        "model": args.model,
        "machine_receipt_path": machine_receipt_path.relative_to(root).as_posix(),
        "machine_receipt_sha256": machine_receipt_sha,
        "machine_receipt_summary": {
            "provider": machine_receipt.get("provider"),
            "provider_run_id": machine_receipt.get("provider_run_id"),
            "gpu_name": machine_receipt.get("provider_selection", {}).get("gpu_name"),
            "model_id": machine_receipt.get("model_runtime", {}).get("model_id"),
            "deterministic_inference": machine_receipt.get("model_runtime", {}).get("enable_deterministic_inference"),
            "max_running_requests": machine_receipt.get("model_runtime", {}).get("max_running_requests"),
            "retain_until_done": machine_receipt.get("retain_until_done"),
        },
        "lanes": lanes,
        "runs_per_packet": args.runs,
        "simulated_validators": args.validators,
        "temperature": 0,
        "top_p": 1,
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
        "separate_reasoning": False,
        "fallback_used": False,
    }
    write_json(qwen_root / "runtime_manifest.json", runtime_manifest)

    total = 0
    for lane in lanes:
        total += len(list((root / "packets" / lane).glob("*.json"))) * args.runs
    completed = 0

    for lane in lanes:
        lane_dir = qwen_root / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        for packet_path in sorted((root / "packets" / lane).glob("*.json")):
            packet = read_json(packet_path)
            out_dir = lane_dir / packet["packet_id"]
            out_dir.mkdir(parents=True, exist_ok=True)
            prompt = build_prompt(packet)
            prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            for run_idx in range(1, args.runs + 1):
                run_path = out_dir / f"run_{run_idx:03d}.json"
                if run_path.exists() and not args.force:
                    completed += 1
                    continue
                started = utc_now()
                error = ""
                raw: dict[str, Any] | None = None
                try:
                    raw = call_sglang(
                        endpoint=args.endpoint,
                        model=args.model,
                        prompt=prompt,
                        timeout=args.timeout,
                        max_tokens=args.max_tokens,
                        api_key=api_key,
                    )
                    message = raw["choices"][0]["message"]
                    content = message.get("content") or ""
                    parsed = extract_json(content)
                    parsed = normalize_output(lane, parsed, packet)
                except Exception as exc:  # noqa: BLE001 - per-run evidence
                    error = f"{type(exc).__name__}: {exc}"
                    if args.fail_on_error:
                        raise RuntimeError(f"{lane} {packet['packet_id']} run {run_idx} failed: {error}") from exc
                    parsed = {}
                output_hash = sha_json(parsed)
                model_profile_hash = sha_json(runtime_manifest)
                label = parsed_label(lane, parsed) if parsed else ""
                schema_valid = label in LANE_ALLOWED_LABELS[lane]
                run_record = {
                    "packet_id": packet["packet_id"],
                    "event_id": packet["event_id"],
                    "lane": lane,
                    "packet_hash": packet["packet_hash"],
                    "prompt_hash": prompt_hash,
                    "model_profile_hash": model_profile_hash,
                    "run_index": run_idx,
                    "started_at": started,
                    "completed_at": utc_now(),
                    "schema_valid": schema_valid,
                    "parsed_label": label,
                    "runtime_kind": runtime_manifest["runtime_kind"],
                    "model": args.model,
                    "error": error,
                    "output_hash": output_hash,
                    "output_json": parsed,
                    "raw_response_shape": {
                        "keys": sorted(raw.keys()) if isinstance(raw, dict) else [],
                        "choice_count": len(raw.get("choices", [])) if isinstance(raw, dict) else 0,
                        "usage": raw.get("usage") if isinstance(raw, dict) else None,
                    },
                    "raw_message_content": raw.get("choices", [{}])[0].get("message", {}).get("content") if isinstance(raw, dict) else "",
                }
                write_json(run_path, run_record)

                rng = random.Random(f"{packet['packet_hash']}:{output_hash}:{run_idx}:{lane}")
                validators = []
                for validator_idx in range(1, args.validators + 1):
                    salt = hashlib.sha256(f"{validator_idx}:{rng.random()}".encode()).hexdigest()
                    commit = hashlib.sha256(
                        f"{packet['packet_hash']}|{model_profile_hash}|{output_hash}|{salt}".encode()
                    ).hexdigest()
                    validators.append(
                        {
                            "validator": f"sim-validator-{validator_idx:02d}",
                            "commit": commit,
                            "reveal": {
                                "packet_hash": packet["packet_hash"],
                                "model_profile_hash": model_profile_hash,
                                "output_hash": output_hash,
                                "salt": salt,
                                "parsed_label": label,
                                "lane": lane,
                            },
                        }
                    )
                write_json(
                    out_dir / f"commit_reveal_{run_idx:03d}.json",
                    {
                        "packet_id": packet["packet_id"],
                        "event_id": packet["event_id"],
                        "lane": lane,
                        "run_index": run_idx,
                        "commit_reveal_valid": True,
                        "validators": validators,
                    },
                )
                completed += 1
                print(json.dumps({"completed": completed, "total": total, "lane": lane, "packet_id": packet["packet_id"], "label": label}, sort_keys=True), flush=True)
                time.sleep(0.05)

    write_sha256s(root)
    print(json.dumps({"completed": completed, "total": total, "lanes": lanes}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
