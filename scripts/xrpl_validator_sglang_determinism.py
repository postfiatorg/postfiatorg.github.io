#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import re
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://agti--dynamic-unl-scoring-qwen36-scoringendpoint-serve.modal.run/v1"
DEFAULT_MODEL = "Qwen/Qwen3.6-27B-FP8"
DEFAULT_SOURCE_ARTIFACT = "static/benchmarks/full-xrpl-validator-credibility-20260317T000633Z.json"
DEFAULT_OUTPUT_DIR = "static/benchmarks"
DEFAULT_OUTPUT_PREFIX = "xrpl-validator-sglang-determinism"
DEFAULT_REPEATS_PER_BATCH = 50
DEFAULT_BATCHES = 2
DEFAULT_CONCURRENCY = 32
DEFAULT_TIMEOUT = 1800.0
DEFAULT_MAX_TOKENS = 128
DEFAULT_TEMPERATURE = 0.0

DEFAULT_PROMPT = (
    "score this validator's credibility on a scale from 0-100 where credibility is "
    "defined as useful institutional proof of a blockchain's legitimacy."
)
SYSTEM_PROMPT = (
    "You are scoring XRPL validators for a repeated-run benchmark.\n"
    "Credibility means whether the validator's operator provides useful institutional "
    "proof of a blockchain's legitimacy.\n"
    "Use a 0-100 integer scale.\n"
    "Return JSON only with a single key named score.\n"
    "score must be an integer from 0 to 100.\n"
    "Do not include markdown, prose, or any other keys."
)


@dataclass(frozen=True)
class ValidatorRecord:
    domain: str
    master_key: str
    unl_publishers: tuple[str, ...]
    verified: bool
    verification_message: str | None
    server_version: str | None
    last_seen: str | None


@dataclass(frozen=True)
class Job:
    batch: int
    repeat: int
    validator: ValidatorRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repeat the saved XRPL validator credibility prompt against a deterministic SGLang endpoint."
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--source-artifact", default=DEFAULT_SOURCE_ARTIFACT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-prefix", default=DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("--repeats-per-batch", type=int, default=DEFAULT_REPEATS_PER_BATCH)
    parser.add_argument("--batches", type=int, default=DEFAULT_BATCHES)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--domains", nargs="*", default=None)
    return parser.parse_args()


def repo_root(script_path: Path) -> Path:
    return script_path.resolve().parents[1]


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def load_validators(path: Path, limit: int | None, domains: list[str] | None) -> list[ValidatorRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_validators = payload.get("validators")
    if not isinstance(raw_validators, list) or not raw_validators:
        raise ValueError(f"No validators found in {path}")
    validators: list[ValidatorRecord] = []
    for raw in raw_validators:
        validators.append(
            ValidatorRecord(
                domain=str(raw.get("domain") or "").strip().lower(),
                master_key=str(raw.get("master_key") or "").strip(),
                unl_publishers=tuple(raw.get("unl_publishers") or ()),
                verified=bool(raw.get("verified")),
                verification_message=str(raw.get("verification_message") or "").strip() or None,
                server_version=str(raw.get("server_version") or "").strip() or None,
                last_seen=str(raw.get("last_seen") or "").strip() or None,
            )
        )
    validators = [validator for validator in validators if validator.domain]
    if domains:
        wanted = [domain.strip().lower() for domain in domains if domain.strip()]
        by_domain = {validator.domain: validator for validator in validators}
        missing = [domain for domain in wanted if domain not in by_domain]
        if missing:
            raise ValueError(f"Requested domains are not in source artifact: {missing}")
        validators = [by_domain[domain] for domain in wanted]
    if limit:
        validators = validators[:limit]
    return validators


def build_messages(validator: ValidatorRecord) -> list[dict[str, str]]:
    user_prompt = (
        f"{DEFAULT_PROMPT}\n\n"
        f"validator: {validator.domain}\n\n"
        'Return JSON only: {"score": <0-100 integer>}.'
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def extract_content(body: dict[str, Any]) -> str:
    choice = ((body.get("choices") or [None])[0]) or {}
    message = choice.get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(part.strip() for part in parts if part).strip()
    return ""


def extract_score(text: str) -> tuple[int | None, str | None]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty_response"
    try:
        parsed = json.loads(raw)
        score = parsed.get("score") if isinstance(parsed, dict) else None
        if isinstance(score, bool):
            return None, "score_is_bool"
        if isinstance(score, (int, float)) and 0 <= int(score) <= 100:
            return int(score), None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            score = parsed.get("score") if isinstance(parsed, dict) else None
            if isinstance(score, (int, float)) and 0 <= int(score) <= 100:
                return int(score), None
        except json.JSONDecodeError:
            pass
    integer_match = re.search(r"(?<!\d)(100|[1-9]?\d)(?!\d)", raw)
    if integer_match:
        return int(integer_match.group(1)), None
    return None, "score_not_found"


def run_job(endpoint: str, model: str, args: argparse.Namespace, job: Job) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": build_messages(job.validator),
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_body = response.read().decode("utf-8")
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        parsed_body = json.loads(response_body)
        raw_content = extract_content(parsed_body)
        score, parse_error = extract_score(raw_content)
        choice = ((parsed_body.get("choices") or [None])[0]) or {}
        return {
            "batch": job.batch,
            "repeat": job.repeat,
            "validator": job.validator.__dict__,
            "score": score,
            "parse_error": parse_error,
            "error": None,
            "raw_content": raw_content,
            "raw_content_sha256": hashlib.sha256(raw_content.encode("utf-8")).hexdigest(),
            "finish_reason": choice.get("finish_reason"),
            "response_model": parsed_body.get("model"),
            "usage": parsed_body.get("usage"),
            "latency_ms": latency_ms,
        }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return error_result(job, f"HTTP {exc.code}: {error_body}", started)
    except Exception as exc:  # noqa: BLE001
        return error_result(job, f"{type(exc).__name__}: {exc}", started)


def error_result(job: Job, error: str, started: float) -> dict[str, Any]:
    return {
        "batch": job.batch,
        "repeat": job.repeat,
        "validator": job.validator.__dict__,
        "score": None,
        "parse_error": None,
        "error": error,
        "raw_content": None,
        "raw_content_sha256": None,
        "finish_reason": None,
        "response_model": None,
        "usage": None,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def score_map_hash(items: list[dict[str, Any]]) -> str:
    score_map = {
        item["validator"]["domain"]: item["score"]
        for item in sorted(items, key=lambda row: row["validator"]["domain"])
    }
    return hashlib.sha256(json.dumps(score_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [result for result in results if result.get("score") is not None and not result.get("error")]
    errors = [result for result in results if result.get("error")]
    parse_errors = [result for result in results if result.get("parse_error")]
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_round: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_domain[result["validator"]["domain"]].append(result)
        by_round[(int(result["batch"]), int(result["repeat"]))].append(result)

    domain_rows: list[dict[str, Any]] = []
    for domain, rows in sorted(by_domain.items()):
        scores = [int(row["score"]) for row in rows if row.get("score") is not None]
        content_hashes = sorted({row.get("raw_content_sha256") for row in rows if row.get("raw_content_sha256")})
        finish_reasons = sorted({str(row.get("finish_reason")) for row in rows if row.get("finish_reason")})
        latencies = [float(row["latency_ms"]) for row in rows if isinstance(row.get("latency_ms"), (int, float))]
        domain_rows.append(
            {
                "domain": domain,
                "n": len(scores),
                "errors": sum(1 for row in rows if row.get("error")),
                "parse_errors": sum(1 for row in rows if row.get("parse_error")),
                "unique_scores": len(set(scores)),
                "score": scores[0] if scores else None,
                "min": min(scores) if scores else None,
                "max": max(scores) if scores else None,
                "stdev": round(statistics.pstdev(scores), 6) if len(scores) > 1 else 0.0 if scores else None,
                "unique_raw_outputs": len(content_hashes),
                "finish_reasons": finish_reasons,
                "latency_ms_mean": round(statistics.fmean(latencies), 2) if latencies else None,
            }
        )

    round_hashes: list[dict[str, Any]] = []
    expected_domain_count = len(by_domain)
    for (batch, repeat), rows in sorted(by_round.items()):
        complete = len([row for row in rows if row.get("score") is not None]) == expected_domain_count
        round_hashes.append(
            {
                "batch": batch,
                "repeat": repeat,
                "complete": complete,
                "score_map_sha256": score_map_hash(rows) if complete else None,
            }
        )
    unique_score_map_hashes = sorted(
        {row["score_map_sha256"] for row in round_hashes if row.get("score_map_sha256")}
    )
    usage_rows = [row.get("usage") for row in results if isinstance(row.get("usage"), dict)]
    total_tokens = [usage.get("total_tokens") for usage in usage_rows if isinstance(usage.get("total_tokens"), (int, float))]
    completion_tokens = [
        usage.get("completion_tokens") for usage in usage_rows if isinstance(usage.get("completion_tokens"), (int, float))
    ]
    reasoning_tokens = [
        usage.get("reasoning_tokens") for usage in usage_rows if isinstance(usage.get("reasoning_tokens"), (int, float))
    ]
    latencies = [float(row["latency_ms"]) for row in results if isinstance(row.get("latency_ms"), (int, float))]
    return {
        "request_count": len(results),
        "success_count": len(successful),
        "error_count": len(errors),
        "parse_error_count": len(parse_errors),
        "validator_count": len(by_domain),
        "round_count": len(by_round),
        "complete_round_count": sum(1 for row in round_hashes if row["complete"]),
        "unique_score_map_hash_count": len(unique_score_map_hashes),
        "unique_score_map_hashes": unique_score_map_hashes,
        "domains_with_score_variance": [
            row["domain"] for row in domain_rows if isinstance(row.get("unique_scores"), int) and row["unique_scores"] > 1
        ],
        "domains_with_raw_output_variance": [
            row["domain"]
            for row in domain_rows
            if isinstance(row.get("unique_raw_outputs"), int) and row["unique_raw_outputs"] > 1
        ],
        "all_scores_perfectly_deterministic": all(row.get("unique_scores") == 1 for row in domain_rows),
        "all_raw_outputs_perfectly_deterministic": all(row.get("unique_raw_outputs") == 1 for row in domain_rows),
        "all_score_maps_perfectly_deterministic": len(unique_score_map_hashes) == 1 and all(
            row["complete"] for row in round_hashes
        ),
        "latency_ms_mean": round(statistics.fmean(latencies), 2) if latencies else None,
        "latency_ms_p95": percentile(latencies, 95) if latencies else None,
        "total_tokens_sum": int(sum(total_tokens)) if total_tokens else None,
        "completion_tokens_sum": int(sum(completion_tokens)) if completion_tokens else None,
        "reasoning_tokens_sum": int(sum(reasoning_tokens)) if reasoning_tokens else None,
        "by_domain": domain_rows,
        "round_hashes": round_hashes,
    }


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = math.ceil((pct / 100.0) * len(ordered)) - 1
    return round(ordered[max(0, min(index, len(ordered) - 1))], 2)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    script_path = Path(__file__).resolve()
    root = repo_root(script_path)
    args = parse_args()
    source_path = resolve_path(root, args.source_artifact)
    output_dir = resolve_path(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    validators = load_validators(source_path, args.limit, args.domains)
    jobs = [
        Job(batch=batch, repeat=repeat, validator=validator)
        for batch in range(1, args.batches + 1)
        for repeat in range(1, args.repeats_per_batch + 1)
        for validator in validators
    ]
    generated_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_base = f"{args.output_prefix}-{generated_at}"
    print(
        json.dumps(
            {
                "endpoint": args.endpoint,
                "model": args.model,
                "validators": len(validators),
                "batches": args.batches,
                "repeats_per_batch": args.repeats_per_batch,
                "requests": len(jobs),
                "concurrency": args.concurrency,
                "source_artifact": str(source_path),
                "output_base": output_base,
            },
            indent=2,
        )
    )

    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        future_to_job = {
            executor.submit(run_job, args.endpoint, args.model, args, job): job for job in jobs
        }
        for completed, future in enumerate(concurrent.futures.as_completed(future_to_job), start=1):
            results.append(future.result())
            if completed == len(jobs) or completed % max(1, math.ceil(len(jobs) / 20)) == 0:
                elapsed = time.perf_counter() - started
                rate = completed / elapsed if elapsed > 0 else 0.0
                print(f"progress {completed}/{len(jobs)} elapsed={elapsed:.1f}s rate={rate:.2f}/s", flush=True)

    summary = summarize(results)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(source_path),
        "endpoint": args.endpoint,
        "model": args.model,
        "prompt": DEFAULT_PROMPT,
        "system_prompt": SYSTEM_PROMPT,
        "request_config": {
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "response_format": {"type": "json_object"},
            "chat_template_kwargs": {"enable_thinking": False},
        },
        "run_config": {
            "batches": args.batches,
            "repeats_per_batch": args.repeats_per_batch,
            "concurrency": args.concurrency,
            "timeout": args.timeout,
        },
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "validators": [validator.__dict__ for validator in validators],
        "summary": summary,
        "results": sorted(results, key=lambda row: (row["batch"], row["repeat"], row["validator"]["domain"])),
    }
    raw_path = output_dir / f"{output_base}.json"
    summary_path = output_dir / f"{output_base}-summary.json"
    domains_csv_path = output_dir / f"{output_base}-domains.csv"
    latest_summary_path = output_dir / f"latest-{args.output_prefix}-summary.json"
    raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps({k: v for k, v in payload.items() if k != "results"}, indent=2), encoding="utf-8")
    latest_summary_path.write_text(summary_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_csv(domains_csv_path, summary["by_domain"])
    print(f"wrote {raw_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {domains_csv_path}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
