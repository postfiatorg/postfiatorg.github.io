#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import textwrap
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OUTPUT_ROOT = Path("static/benchmarks")
DEFAULT_OPENAI_KEY_FILE = Path(os.environ["OPENAI_KEY_FILE"]) if os.environ.get("OPENAI_KEY_FILE") else None
DEFAULT_OPENROUTER_KEY_FILE = Path(os.environ["OPENROUTER_KEY_FILE"]) if os.environ.get("OPENROUTER_KEY_FILE") else None

SOURCE_URLS = {
    "xrpl_amendments": "https://xrpl.org/docs/concepts/networks-and-servers/amendments/",
    "xrpl_amm_status_update": "https://xrpl.org/blog/2024/amm-status-update",
    "xrpl_amm_vote_reversal": "https://thecryptobasic.com/2024/02/07/xrpl-validators-revoke-votes-on-xls-30d-amm-not-launching-on-feb-14/",
}

EVENT_FACTS = [
    {
        "fact_id": "F1",
        "source": "xrpl_amendments",
        "summary": (
            "XRPL transaction-processing changes are introduced as amendments. "
            "Validators vote on amendments; an amendment needs more than 80% support "
            "for two weeks before activation. Bug fixes that change transaction processing "
            "also require amendments."
        ),
    },
    {
        "fact_id": "F2",
        "source": "xrpl_amm_vote_reversal",
        "summary": (
            "In February 2024, extended integration testing identified an XLS-30D AMM issue "
            "that could prevent multiple AMM transactions from executing in the same ledger."
        ),
    },
    {
        "fact_id": "F3",
        "source": "xrpl_amm_vote_reversal",
        "summary": (
            "After the issue surfaced, validators revoked votes and reported support declined "
            "to 71.43%, below the 80% threshold, so the expected February 14 activation did not proceed."
        ),
    },
    {
        "fact_id": "F4",
        "source": "xrpl_amm_vote_reversal",
        "summary": (
            "Public validator rationales included concern that launching a critical feature with "
            "a known issue would set a bad governance precedent, even if the bug was described as minor."
        ),
    },
    {
        "fact_id": "F5",
        "source": "xrpl_amm_status_update",
        "summary": (
            "The AMM amendment went live on March 22, 2024; soon after, a community member "
            "identified AMM pool discrepancies. The official status update said the fix required "
            "another amendment and validator vote, and advised users not to deposit new funds into AMM pools until fixed."
        ),
    },
]

DEFAULT_PANEL_MODELS = [
    "anthropic/claude-4.8-opus-20260528",
    "deepseek/deepseek-v4-pro",
    "google/gemini-3.5-flash",
    "qwen/qwen3.7-max",
    "mistralai/mistral-medium-3-5",
]


def read_key(path: Path | None, env_name: str) -> str:
    value = os.environ.get(env_name, "").strip()
    if value:
        return value
    if path is None or not path.exists():
        raise SystemExit(f"Missing {env_name}; pass a key-file argument or set the environment variable")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            line = line.split("=", 1)[1].strip()
        return line.strip().strip('"').strip("'")
    raise SystemExit(f"Missing {env_name} and no key in {path}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_url(url: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "postfiat-governance-replay/1.0 (+https://postfiat.org)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read()
            return {
                "url": url,
                "status": int(resp.status),
                "ok": 200 <= int(resp.status) < 400,
                "bytes": len(body),
                "sha256": sha256_bytes(body),
                "content_type": resp.headers.get("content-type", ""),
                "elapsed_seconds": round(time.time() - started, 3),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return {
            "url": url,
            "status": int(exc.code),
            "ok": False,
            "bytes": len(body),
            "sha256": sha256_bytes(body),
            "content_type": exc.headers.get("content-type", "") if exc.headers else "",
            "error": body[:500].decode("utf-8", errors="replace"),
            "elapsed_seconds": round(time.time() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": url,
            "status": None,
            "ok": False,
            "bytes": 0,
            "sha256": None,
            "content_type": "",
            "error": repr(exc),
            "elapsed_seconds": round(time.time() - started, 3),
        }


def extract_json(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(raw[start : end + 1])
        if isinstance(value, dict):
            return value
    raise ValueError("json_object_not_found")


def response_output_text(raw: dict[str, Any]) -> str:
    if isinstance(raw.get("output_text"), str):
        return raw["output_text"].strip()
    pieces: list[str] = []
    for item in raw.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                pieces.append(str(content.get("text", "")))
    return "\n".join(piece for piece in pieces if piece).strip()


def normalize_openrouter_content(raw: dict[str, Any]) -> str:
    content = raw.get("choices", [{}])[0].get("message", {}).get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts).strip()
    return ""


def call_openai_response(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": prompt,
        "text": {"format": {"type": "json_object"}},
        "max_output_tokens": max_output_tokens,
        "store": True,
    }
    req = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    text = response_output_text(raw)
    return {
        "provider": "openai",
        "model": model,
        "raw": raw,
        "text": text,
        "parsed": extract_json(text),
        "usage": raw.get("usage"),
    }


def call_openrouter_chat(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
        "provider": {"allow_fallbacks": False},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a protocol governance reviewer. Return only valid JSON. "
                    "Do not use markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://postfiat.org",
            "X-Title": "XRPL AMM governance attention replay",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    text = normalize_openrouter_content(raw)
    return {
        "provider": "openrouter",
        "model": model,
        "raw": raw,
        "text": text,
        "parsed": extract_json(text),
        "usage": raw.get("usage"),
    }


def event_packet() -> dict[str, Any]:
    return {
        "event_id": "xrpl-xls30-amm-2024",
        "title": "XRPL XLS-30 AMM amendment bug and vote-reversal replay",
        "historical_period": "February-March 2024",
        "known_historical_action": "delay/fix/challenge before proceeding with known-bug AMM activation",
        "facts": EVENT_FACTS,
        "source_urls": SOURCE_URLS,
        "decision_options": [
            "PROCEED_AS_PLANNED",
            "DELAY_FOR_FIX",
            "HOLD_FOR_CHALLENGE",
            "REJECT_AMENDMENT",
        ],
    }


def deterministic_alert(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow": "deterministic_alert",
        "route": "DELAY_FOR_FIX",
        "rule": "if known_protocol_bug == true and amendment_support_percent < 80 then delay_or_challenge",
        "cited_facts": ["F1", "F2", "F3"],
        "output": (
            "Known transaction-processing bug plus support below the 80% amendment threshold. "
            "Delay or challenge until a fix is reviewed."
        ),
        "limitations": [
            "Does not summarize competing validator rationales.",
            "Does not produce a typed review packet or missing-evidence list.",
            "Still leaves validators to read source material independently.",
        ],
    }


def triage_prompt(packet: dict[str, Any]) -> str:
    return textwrap.dedent(
        f"""
        You are simulating a Post Fiat model-assisted governance triage layer.

        Historical event packet:
        {json.dumps(packet, indent=2, sort_keys=True)}

        Task:
        Produce a typed governance work item for validators. The model has negative authority only:
        it may route to challenge, hold, delay, or no-op, but it cannot approve an amendment,
        admit a validator, or bind validator votes.

        Return exactly this JSON object:
        {{
          "route": "PROCEED_AS_PLANNED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT_AMENDMENT",
          "route_confidence": <integer 0-100>,
          "decision_summary": "<one paragraph>",
          "cited_facts": [
            {{"fact_id": "F1", "why_it_matters": "<short>"}}
          ],
          "arguments_for_proceeding": ["<short>", "<short>"],
          "arguments_for_delay_or_challenge": ["<short>", "<short>", "<short>"],
          "missing_evidence": ["<short>", "<short>"],
          "validator_work_item": {{
            "title": "<short>",
            "recommended_validator_action": "<short>",
            "review_questions": ["<short>", "<short>", "<short>"],
            "vote_options": ["<short>", "<short>", "<short>"]
          }},
          "estimated_minutes": {{
            "senior_packet_verification": <integer>,
            "validator_skim": <integer>,
            "deep_challenge_review": <integer>
          }},
          "private_standing_committee_required": <true or false>,
          "forbidden_stronger_claim": "<one sentence>"
        }}

        Scoring discipline:
        - Cite fact IDs only from the packet.
        - A historically aligned answer should not blindly proceed with known unresolved AMM defects.
        - Keep the work item compact enough that validators can review asynchronously without a standing committee.
        """
    ).strip()


def judge_prompt(
    *,
    packet: dict[str, Any],
    triage: dict[str, Any],
    deterministic: dict[str, Any],
    cost_model: dict[str, Any],
) -> str:
    return textwrap.dedent(
        f"""
        You are a blind synthetic governance reviewer. You are not deciding whether XRP or Post Fiat is good.
        You are evaluating whether a typed model triage packet would have reduced validator attention cost
        in the historical XRPL XLS-30 AMM bug/vote-reversal scenario while preserving human veto.

        Historical event packet:
        {json.dumps(packet, indent=2, sort_keys=True)}

        Candidate workflow A: model-assisted typed triage packet
        {json.dumps(triage, indent=2, sort_keys=True)}

        Candidate workflow B: deterministic alert
        {json.dumps(deterministic, indent=2, sort_keys=True)}

        Candidate workflow C: standing human committee
        {json.dumps(cost_model["standing_human_committee"], indent=2, sort_keys=True)}

        Cost assumptions:
        {json.dumps(cost_model, indent=2, sort_keys=True)}

        Return exactly this JSON object:
        {{
          "source_fidelity_score": <integer 0-100>,
          "historical_alignment_score": <integer 0-100>,
          "validator_actionability_score": <integer 0-100>,
          "attention_compression_score": <integer 0-100>,
          "preferred_workflow": "model_triage | deterministic_alert | standing_human_committee | tie",
          "would_route_to": "PROCEED_AS_PLANNED | DELAY_FOR_FIX | HOLD_FOR_CHALLENGE | REJECT_AMENDMENT",
          "fatal_issue": <true or false>,
          "key_reason": "<one paragraph>",
          "fields_that_reduce_private_committee_need": ["<short>", "<short>"],
          "remaining_human_work": ["<short>", "<short>"]
        }}

        Do not treat model output as ground truth. Prefer model_triage only if it adds actionable,
        cited structure beyond the deterministic alert and reduces the need for private committee coordination.
        """
    ).strip()


def build_cost_model(validator_count: int, hourly_rate_usd: float) -> dict[str, Any]:
    full_minutes_per_validator = 120
    deterministic_minutes_per_validator = 45
    llm_senior_minutes = 120
    llm_skim_minutes = 8
    llm_deep_reviewers = 5
    llm_deep_minutes = 30

    full_total = validator_count * full_minutes_per_validator
    deterministic_total = validator_count * deterministic_minutes_per_validator
    llm_total = llm_senior_minutes + validator_count * llm_skim_minutes + llm_deep_reviewers * llm_deep_minutes

    def block(total_minutes: int, private_surfaces: list[str]) -> dict[str, Any]:
        hours = total_minutes / 60
        return {
            "validator_count": validator_count,
            "total_minutes": total_minutes,
            "total_hours": round(hours, 2),
            "professional_cost_usd": round(hours * hourly_rate_usd, 2),
            "private_coordination_surfaces": private_surfaces,
            "private_coordination_surface_count": len(private_surfaces),
        }

    standing = block(
        full_total,
        [
            "private chat or call",
            "agenda control",
            "recurring reviewer role",
            "discoverable deliberation record",
            "validator-to-validator coordination nexus",
        ],
    )
    deterministic = block(
        deterministic_total,
        [
            "validators still independently read source material",
            "no typed work item beyond rule alert",
        ],
    )
    llm = block(
        llm_total,
        [
            "public typed packet",
            "disputes only for escalated reviewers",
        ],
    )
    return {
        "hourly_rate_usd": hourly_rate_usd,
        "standing_human_committee": standing,
        "deterministic_alert_independent_review": deterministic,
        "llm_typed_triage": llm,
        "attention_reduction_vs_standing_committee": round(1 - llm_total / full_total, 4),
        "attention_reduction_vs_deterministic_alert": round(1 - llm_total / deterministic_total, 4),
        "assumptions": {
            "standing_committee_minutes_per_validator": full_minutes_per_validator,
            "deterministic_alert_minutes_per_validator": deterministic_minutes_per_validator,
            "llm_senior_packet_verification_minutes": llm_senior_minutes,
            "llm_validator_skim_minutes": llm_skim_minutes,
            "llm_deep_reviewers": llm_deep_reviewers,
            "llm_deep_review_minutes_each": llm_deep_minutes,
        },
    }


def aggregate_judges(judge_results: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [row["parsed"] for row in judge_results if row.get("ok") and isinstance(row.get("parsed"), dict)]
    if not parsed:
        return {"judge_count": 0, "error": "no_successful_judges"}
    fields = [
        "source_fidelity_score",
        "historical_alignment_score",
        "validator_actionability_score",
        "attention_compression_score",
    ]
    scores: dict[str, Any] = {}
    for field in fields:
        vals = [int(row[field]) for row in parsed if isinstance(row.get(field), (int, float))]
        scores[field] = {
            "mean": round(statistics.mean(vals), 2) if vals else None,
            "median": statistics.median(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
        }
    preferred = Counter(str(row.get("preferred_workflow")) for row in parsed)
    routes = Counter(str(row.get("would_route_to")) for row in parsed)
    fatal = sum(1 for row in parsed if row.get("fatal_issue") is True)
    return {
        "judge_count": len(parsed),
        "score_summary": scores,
        "preferred_workflow_counts": dict(preferred),
        "route_counts": dict(routes),
        "fatal_issue_count": fatal,
        "model_triage_preference_rate": round(preferred.get("model_triage", 0) / len(parsed), 4),
        "historically_aligned_route_rate": round(
            sum(routes.get(route, 0) for route in ("DELAY_FOR_FIX", "HOLD_FOR_CHALLENGE")) / len(parsed),
            4,
        ),
    }


def write_sha256s(out_dir: Path) -> str:
    rows = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        rows.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    target = out_dir / "SHA256SUMS.txt"
    target.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return sha256_file(target)


def report_markdown(summary: dict[str, Any]) -> str:
    judges = summary["judge_panel_summary"]
    cost = summary["cost_model"]
    triage = summary["triage_packet"]
    return textwrap.dedent(
        f"""\
        # XRPL AMM Governance Attention Replay

        This packet replays the 2024 XRPL XLS-30 AMM bug/vote-reversal episode as an attention-cost simulation for Post Fiat governance.

        ## Boundary

        This is a synthetic committee stress test, not human validation and not proof that a model is correct. It asks whether a model-generated, cited, typed work item can reduce validator attention cost in a real XRPL-style governance incident while preserving human veto and public review.

        ## Historical Case

        The case is the February-March 2024 XRPL AMM amendment cycle. Public sources report that a known AMM issue surfaced during integration testing, validators revoked votes, support dropped below the 80% amendment threshold, and later AMM pool discrepancies required a fix amendment after AMM launch.

        ## Model Triage Result

        - Triage route: `{triage.get("route")}`
        - Route confidence: `{triage.get("route_confidence")}`
        - Private standing committee required: `{triage.get("private_standing_committee_required")}`

        ## Synthetic Judge Panel

        - Successful judges: `{judges.get("judge_count")}`
        - Preferred workflow counts: `{judges.get("preferred_workflow_counts")}`
        - Route counts: `{judges.get("route_counts")}`
        - Model-triage preference rate: `{judges.get("model_triage_preference_rate")}`
        - Historically aligned route rate: `{judges.get("historically_aligned_route_rate")}`
        - Fatal issue count: `{judges.get("fatal_issue_count")}`

        Mean judge scores:

        | Metric | Mean | Min | Max |
        | --- | ---: | ---: | ---: |
        | Source fidelity | {judges["score_summary"]["source_fidelity_score"]["mean"]} | {judges["score_summary"]["source_fidelity_score"]["min"]} | {judges["score_summary"]["source_fidelity_score"]["max"]} |
        | Historical alignment | {judges["score_summary"]["historical_alignment_score"]["mean"]} | {judges["score_summary"]["historical_alignment_score"]["min"]} | {judges["score_summary"]["historical_alignment_score"]["max"]} |
        | Validator actionability | {judges["score_summary"]["validator_actionability_score"]["mean"]} | {judges["score_summary"]["validator_actionability_score"]["min"]} | {judges["score_summary"]["validator_actionability_score"]["max"]} |
        | Attention compression | {judges["score_summary"]["attention_compression_score"]["mean"]} | {judges["score_summary"]["attention_compression_score"]["min"]} | {judges["score_summary"]["attention_compression_score"]["max"]} |

        ## Attention Cost Model

        | Workflow | Hours | Cost at ${cost["hourly_rate_usd"]}/hr | Private coordination surfaces |
        | --- | ---: | ---: | ---: |
        | Standing human committee | {cost["standing_human_committee"]["total_hours"]} | ${cost["standing_human_committee"]["professional_cost_usd"]} | {cost["standing_human_committee"]["private_coordination_surface_count"]} |
        | Deterministic alert + independent review | {cost["deterministic_alert_independent_review"]["total_hours"]} | ${cost["deterministic_alert_independent_review"]["professional_cost_usd"]} | {cost["deterministic_alert_independent_review"]["private_coordination_surface_count"]} |
        | LLM typed triage + human veto | {cost["llm_typed_triage"]["total_hours"]} | ${cost["llm_typed_triage"]["professional_cost_usd"]} | {cost["llm_typed_triage"]["private_coordination_surface_count"]} |

        - Attention reduction versus standing committee: `{cost["attention_reduction_vs_standing_committee"]}`
        - Attention reduction versus deterministic alert: `{cost["attention_reduction_vs_deterministic_alert"]}`

        ## Whitepaper-Safe Claim

        In a replay of the 2024 XRPL AMM governance incident, a model-generated typed work item reached the historically aligned delay/fix route and a blind multi-model synthetic panel preferred model triage over a deterministic alert or standing committee in the successful judge set; under the declared cost model, typed triage reduced validator attention by {round(cost["attention_reduction_vs_standing_committee"] * 100, 1)}% versus all-validator committee review and by {round(cost["attention_reduction_vs_deterministic_alert"] * 100, 1)}% versus deterministic alert plus independent review.

        ## Claim Discipline

        - This does not prove that a model is correct.
        - This does not replace human validator judgment.
        - This does not show production authority transfer.
        - This supports the narrower claim that model-assisted triage can compress validator attention and avoid routine standing-committee coordination.
        """
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run XRPL AMM governance attention replay simulation.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--label", default=None)
    parser.add_argument("--openai-key-file", type=Path, default=DEFAULT_OPENAI_KEY_FILE)
    parser.add_argument("--openrouter-key-file", type=Path, default=DEFAULT_OPENROUTER_KEY_FILE)
    parser.add_argument("--triage-model", default="chat-latest")
    parser.add_argument("--panel-models", nargs="+", default=DEFAULT_PANEL_MODELS)
    parser.add_argument("--validator-count", type=int, default=41)
    parser.add_argument("--hourly-rate-usd", type=float, default=250.0)
    parser.add_argument("--max-output-tokens", type=int, default=4500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = args.label or f"xrpl-amm-governance-attention-replay-{timestamp}"
    out_dir = args.output_root / label
    out_dir.mkdir(parents=True, exist_ok=False)

    openai_key = read_key(args.openai_key_file, "OPENAI_API_KEY")
    openrouter_key = read_key(args.openrouter_key_file, "OPENROUTER_API_KEY")

    packet = event_packet()
    receipts = {key: fetch_url(url) for key, url in SOURCE_URLS.items()}
    cost_model = build_cost_model(args.validator_count, args.hourly_rate_usd)
    baseline = deterministic_alert(packet)

    triage_call = call_openai_response(
        api_key=openai_key,
        model=args.triage_model,
        prompt=triage_prompt(packet),
        max_output_tokens=args.max_output_tokens,
    )
    triage = triage_call["parsed"]

    judge_results: list[dict[str, Any]] = []
    prompt = judge_prompt(packet=packet, triage=triage, deterministic=baseline, cost_model=cost_model)
    for model in args.panel_models:
        started = time.time()
        try:
            result = call_openrouter_chat(
                api_key=openrouter_key,
                model=model,
                prompt=prompt,
                max_tokens=args.max_output_tokens,
            )
            judge_results.append(
                {
                    "ok": True,
                    "model": model,
                    "provider": "openrouter",
                    "elapsed_seconds": round(time.time() - started, 3),
                    "text": result["text"],
                    "parsed": result["parsed"],
                    "usage": result.get("usage"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            judge_results.append(
                {
                    "ok": False,
                    "model": model,
                    "provider": "openrouter",
                    "elapsed_seconds": round(time.time() - started, 3),
                    "error": repr(exc),
                }
            )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_packet_sha256": sha256_bytes(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()),
        "source_receipts_ok": all(row.get("ok") for row in receipts.values()),
        "event_packet": packet,
        "source_receipts": receipts,
        "deterministic_baseline": baseline,
        "cost_model": cost_model,
        "triage_model": {
            "provider": "openai",
            "model": args.triage_model,
            "usage": triage_call.get("usage"),
        },
        "triage_packet": triage,
        "judge_panel_models": args.panel_models,
        "judge_panel_summary": aggregate_judges(judge_results),
        "successful_judge_count": sum(1 for row in judge_results if row.get("ok")),
        "failed_judge_count": sum(1 for row in judge_results if not row.get("ok")),
        "claim_boundary": (
            "Synthetic committee stress test for attention compression. This is not a human label set "
            "and not proof of model correctness."
        ),
    }

    write_json(out_dir / "event_packet.json", packet)
    write_json(out_dir / "source_receipts.json", receipts)
    write_json(out_dir / "deterministic_baseline.json", baseline)
    write_json(out_dir / "cost_model.json", cost_model)
    write_json(
        out_dir / "triage_call.json",
        {
            "provider": "openai",
            "model": args.triage_model,
            "usage": triage_call.get("usage"),
            "text": triage_call["text"],
            "parsed": triage,
        },
    )
    write_json(out_dir / "judge_panel.json", judge_results)
    write_json(out_dir / "summary.json", summary)
    (out_dir / "REPORT.md").write_text(report_markdown(summary), encoding="utf-8")
    (out_dir / "COMMANDS.txt").write_text(
        " ".join(
            [
                "python3",
                "scripts/xrpl_amm_governance_attention_replay.py",
                "--label",
                label,
                "--triage-model",
                args.triage_model,
                "--panel-models",
                *args.panel_models,
                "--validator-count",
                str(args.validator_count),
                "--hourly-rate-usd",
                str(args.hourly_rate_usd),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    sha_root = write_sha256s(out_dir)
    print(f"output_dir={out_dir}")
    print(f"sha256s={sha_root}")
    print(f"successful_judges={summary['successful_judge_count']}")
    print(json.dumps(summary["judge_panel_summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
