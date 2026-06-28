#!/usr/bin/env python3
"""Run Qwen/SGLang over XRPL origination replay packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

from build_xrpl_origination_replay_packets import ALLOWED_LABELS, OUTPUT_SCHEMA
from validate_xrpl_origination_replay import FORBIDDEN_AUTHORITY_PATTERNS, REQUIRED_NON_CLAIMS
from xrpl_lifecycle_common import artifact_path, read_json, sha_json, utc_now, write_json, write_sha256s


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


def read_key(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if "=" in text and "\n" not in text:
        return text.split("=", 1)[1].strip().strip('"').strip("'")
    return text.splitlines()[0].strip()


def build_prompt(packet: dict[str, Any]) -> str:
    label_policy = {
        "OPEN_RESEARCH_PACKET": "Use when a proposal deserves a public packet of additional sources or problem framing before an implementation decision.",
        "NEEDS_IMPLEMENTATION_OWNER": "Use when the public next step is finding or confirming a concrete implementer/maintainer.",
        "NEEDS_SECURITY_REVIEW": "Use when the packet shows material consensus, custody, issuer-control, permissioning, privacy, funds-flow, or implementation-risk surfaces.",
        "MERGE_WITH_RELATED_SPEC": "Use when the proposal is mostly dependency, supporting standard, duplicate, or should be considered with a related XLS/amendment.",
        "WAIT_FOR_DEPENDENCY": "Use when the packet identifies dependencies, prerequisite amendments, or in-development status that should be resolved first.",
        "PUBLIC_DISCUSSION_NEEDED": "Use when the main missing object is public deliberation, stakeholder comment, or a clearer problem statement.",
        "CLOSE_AS_SUPERSEDED": "Use when the packet shows withdrawn/deprecated/obsolete status, or when a newer known amendment/spec appears to supersede the proposal.",
        "INSUFFICIENT_EVIDENCE": "Use when the packet does not support a more specific public work item.",
    }
    return (
        "You are a deterministic Origination Replay worker.\n"
        "Your job is to originate a public work item from an off-chain amendment packet.\n"
        "You do not decide whether an XRPL amendment should pass. You do not recommend validator YES/NO votes.\n"
        "Use only source_facts and source_excerpts in the packet. Cite source_id values from the packet.\n"
        "Return one strict JSON object. No markdown. No commentary.\n\n"
        f"Allowed work_item_label values: {', '.join(ALLOWED_LABELS)}\n"
        f"Label policy: {json.dumps(label_policy, sort_keys=True)}\n"
        f"Required JSON schema: {json.dumps(OUTPUT_SCHEMA, sort_keys=True)}\n\n"
        "Authority boundary:\n"
        "- The output is a public work item, not a validator vote recommendation.\n"
        "- Do not say validators should vote yes or no.\n"
        "- Do not say the amendment should be adopted, enabled, or passed.\n"
        "- Include both required non_claims exactly:\n"
        "  This is not a validator vote recommendation.\n"
        "  This does not decide whether the amendment should pass.\n\n"
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


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def normalize_output(parsed: dict[str, Any], packet: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    actions: list[str] = []
    output = dict(parsed)
    raw_label = str(output.get("work_item_label", "")).strip().upper()
    aliases = {
        "RESEARCH": "OPEN_RESEARCH_PACKET",
        "SECURITY_REVIEW": "NEEDS_SECURITY_REVIEW",
        "DISCUSSION": "PUBLIC_DISCUSSION_NEEDED",
        "WAIT": "WAIT_FOR_DEPENDENCY",
        "CLOSE": "CLOSE_AS_SUPERSEDED",
    }
    label = aliases.get(raw_label, raw_label)
    raw_label_valid = label in ALLOWED_LABELS
    if not raw_label_valid:
        label = "INSUFFICIENT_EVIDENCE"
        actions.append("invalid_label_replaced_with_insufficient_evidence")
    output["work_item_label"] = label
    try:
        output["confidence"] = float(output.get("confidence", 0))
    except (TypeError, ValueError):
        output["confidence"] = 0.0
        actions.append("confidence_defaulted")

    source_ids = {source["source_id"] for source in packet.get("source_list", [])}
    raw_citations = as_list(output.get("source_citations"))
    citations: list[str] = []
    bad_citations: list[str] = []
    for item in raw_citations:
        citation = item.get("source_id") if isinstance(item, dict) else str(item)
        if citation in source_ids and citation not in citations:
            citations.append(citation)
        else:
            bad_citations.append(str(citation))
    if not citations:
        citations = [fact["source_id"] for fact in packet.get("source_facts", [])[:2] if fact.get("source_id") in source_ids]
        actions.append("citations_defaulted")
    output["source_citations"] = citations

    output["missing_evidence"] = [str(item) for item in as_list(output.get("missing_evidence"))]
    output["risks"] = [str(item) for item in as_list(output.get("risks"))]
    output["fork_points"] = [str(item) for item in as_list(output.get("fork_points"))]
    output.setdefault("problem_statement", "")
    public_work_item = output.get("public_work_item")
    if not isinstance(public_work_item, dict):
        public_work_item = {}
        actions.append("public_work_item_defaulted")
    public_work_item.setdefault("title", f"Open public work item for {packet['amendment_identity']['xls_id']}")
    public_work_item.setdefault("next_action", "Publish a source packet and request public review.")
    public_work_item.setdefault("owner_needed", True)
    public_work_item["review_questions"] = [str(item) for item in as_list(public_work_item.get("review_questions"))]
    output["public_work_item"] = public_work_item

    non_claims = [str(item) for item in as_list(output.get("non_claims"))]
    for required in sorted(REQUIRED_NON_CLAIMS):
        if required not in non_claims:
            non_claims.append(required)
            actions.append(f"required_non_claim_added:{required}")
    output["non_claims"] = non_claims

    text = json.dumps(output, sort_keys=True, ensure_ascii=False)
    authority_failures = [pattern.pattern for pattern in FORBIDDEN_AUTHORITY_PATTERNS if pattern.search(text)]
    checks = {
        "raw_label_valid": raw_label_valid,
        "bad_citations": bad_citations,
        "citation_valid": bool(citations) and not bad_citations,
        "required_non_claims_present": REQUIRED_NON_CLAIMS.issubset(set(non_claims)),
        "authority_boundary_failures": authority_failures,
        "normalization_actions": actions,
    }
    return output, checks


def iter_packet_paths(root: Path, include_forks: bool) -> list[tuple[str, Path, int]]:
    paths = [("main", path, 0) for path in sorted((root / "packets").glob("*.json"))]
    if include_forks:
        paths.extend(("fork", path, 0) for path in sorted((root / "fork_packets").glob("*.json")))
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", default="Qwen/Qwen3.6-27B-FP8")
    parser.add_argument("--machine-receipt", type=Path, required=True)
    parser.add_argument("--api-key-file", type=Path)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--include-forks", action="store_true")
    parser.add_argument("--fork-runs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-tokens", type=int, default=1400)
    parser.add_argument("--validators", type=int, default=41)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args(argv)

    root = artifact_path(args.artifact)
    machine_receipt_path = artifact_path(args.machine_receipt)
    machine_receipt = read_json(machine_receipt_path)
    api_key = read_key(args.api_key_file)
    runtime_manifest = {
        "generated_at": utc_now(),
        "runtime_kind": "openai_compatible_sglang",
        "endpoint": args.endpoint,
        "model": args.model,
        "machine_receipt_path": machine_receipt_path.as_posix(),
        "machine_receipt_sha256": hashlib.sha256(machine_receipt_path.read_bytes()).hexdigest(),
        "machine_receipt_summary": {
            "provider": machine_receipt.get("provider"),
            "provider_run_id": machine_receipt.get("provider_run_id"),
            "gpu_name": machine_receipt.get("provider_selection", {}).get("gpu_name"),
            "model_id": machine_receipt.get("model_runtime", {}).get("model_id"),
            "deterministic_inference": machine_receipt.get("model_runtime", {}).get("enable_deterministic_inference"),
            "max_running_requests": machine_receipt.get("model_runtime", {}).get("max_running_requests"),
            "retain_until_done": machine_receipt.get("retain_until_done"),
        },
        "temperature": 0,
        "top_p": 1,
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
        "separate_reasoning": False,
        "main_runs_per_packet": args.runs,
        "fork_runs_per_packet": args.fork_runs if args.include_forks else 0,
    }
    qwen_root = root / "qwen_runs"
    write_json(qwen_root / "runtime_manifest.json", runtime_manifest)
    model_profile_hash = sha_json(runtime_manifest)

    jobs: list[tuple[str, Path, int]] = []
    for kind, path, _ in iter_packet_paths(root, args.include_forks):
        n = args.runs if kind == "main" else args.fork_runs
        for run_idx in range(1, n + 1):
            jobs.append((kind, path, run_idx))

    completed = 0
    for kind, packet_path, run_idx in jobs:
        packet = read_json(packet_path)
        run_dir = qwen_root / kind / packet["packet_id"]
        run_path = run_dir / f"run_{run_idx:03d}.json"
        if run_path.exists() and not args.force:
            completed += 1
            continue
        prompt = build_prompt(packet)
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        raw: dict[str, Any] | None = None
        error = ""
        content = ""
        started = utc_now()
        try:
            raw = call_sglang(args.endpoint, args.model, prompt, args.timeout, args.max_tokens, api_key)
            content = raw["choices"][0]["message"].get("content") or ""
            parsed_raw = extract_json(content)
            parsed, checks = normalize_output(parsed_raw, packet)
        except Exception as exc:  # noqa: BLE001 - per-run evidence
            error = f"{type(exc).__name__}: {exc}"
            if args.fail_on_error:
                raise RuntimeError(f"{packet['packet_id']} run {run_idx} failed: {error}") from exc
            parsed = {}
            checks = {
                "raw_label_valid": False,
                "bad_citations": [],
                "citation_valid": False,
                "required_non_claims_present": False,
                "authority_boundary_failures": [],
                "normalization_actions": ["endpoint_or_parse_error"],
            }
        output_hash = sha_json(parsed)
        schema_valid = (
            bool(parsed)
            and str(parsed.get("work_item_label", "")).strip().upper() in ALLOWED_LABELS
            and bool(checks.get("citation_valid"))
            and bool(checks.get("required_non_claims_present"))
            and not checks.get("authority_boundary_failures")
        )
        record = {
            "packet_id": packet["packet_id"],
            "packet_kind": kind,
            "xls_id": packet["amendment_identity"]["xls_id"],
            "packet_hash": packet["packet_hash"],
            "prompt_hash": prompt_hash,
            "model_profile_hash": model_profile_hash,
            "run_index": run_idx,
            "started_at": started,
            "completed_at": utc_now(),
            "runtime_kind": runtime_manifest["runtime_kind"],
            "model": args.model,
            "error": error,
            "schema_valid": schema_valid,
            "parsed_label": parsed.get("work_item_label", "") if parsed else "",
            "output_hash": output_hash,
            "raw_output_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "output_json": parsed,
            "checks": checks,
            "raw_response_shape": {
                "keys": sorted(raw.keys()) if isinstance(raw, dict) else [],
                "choice_count": len(raw.get("choices", [])) if isinstance(raw, dict) else 0,
                "usage": raw.get("usage") if isinstance(raw, dict) else None,
            },
            "raw_message_content": content,
        }
        write_json(run_path, record)

        rng = random.Random(f"{packet['packet_hash']}:{output_hash}:{run_idx}:origination")
        validators = []
        for validator_idx in range(1, args.validators + 1):
            salt = hashlib.sha256(f"{validator_idx}:{rng.random()}".encode()).hexdigest()
            commit = hashlib.sha256(f"{packet['packet_hash']}|{model_profile_hash}|{output_hash}|{salt}".encode()).hexdigest()
            validators.append(
                {
                    "validator": f"sim-validator-{validator_idx:02d}",
                    "commit": commit,
                    "reveal": {
                        "packet_hash": packet["packet_hash"],
                        "model_profile_hash": model_profile_hash,
                        "output_hash": output_hash,
                        "salt": salt,
                        "parsed_label": record["parsed_label"],
                    },
                }
            )
        write_json(
            run_dir / f"commit_reveal_{run_idx:03d}.json",
            {
                "packet_id": packet["packet_id"],
                "packet_kind": kind,
                "run_index": run_idx,
                "commit_reveal_valid": True,
                "validators": validators,
            },
        )
        completed += 1
        print(
            json.dumps(
                {
                    "completed": completed,
                    "total": len(jobs),
                    "packet_kind": kind,
                    "packet_id": packet["packet_id"],
                    "label": record["parsed_label"],
                    "schema_valid": schema_valid,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        time.sleep(0.05)

    write_sha256s(root)
    print(json.dumps({"completed": completed, "total": len(jobs)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
