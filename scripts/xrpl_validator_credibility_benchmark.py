#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import os
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
XRPSCAN_VALIDATOR_REGISTRY_URL = "https://api.xrpscan.com/api/v1/validatorregistry?limit=500"
DEFAULT_REFERER = "https://postfiat.org"
DEFAULT_TITLE = "postfiat-whitepaper-benchmark"
DEFAULT_MODELS = (
    "minimax/minimax-m2.5",
    "deepseek/deepseek-v3.2",
    "moonshotai/kimi-k2.5",
)
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
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504, 520, 521, 522, 524}
DEFAULT_SUBSET_DOMAINS = (
    "shadow.haas.berkeley.edu",
    "ripple.com",
    "xrpscan.com",
    "xrpgoat.com",
)
MODEL_COMPLETION_TOKEN_DEFAULTS = {
    "deepseek/deepseek-v3.2": 128,
    "minimax/minimax-m2.5": 512,
    "moonshotai/kimi-k2.5": 1024,
}
MODEL_REASONING_DEFAULTS = {
    "minimax/minimax-m2.5": {"effort": "low", "exclude": True},
    "moonshotai/kimi-k2.5": {"effort": "low", "exclude": True},
}


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
class BenchmarkJob:
    model: str
    batch: int
    repeat: int
    validator: ValidatorRecord


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run repeated OpenRouter scoring on current XRPL UNL validators from XRPSCAN."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(DEFAULT_MODELS),
        help="OpenRouter model ids to query.",
    )
    parser.add_argument(
        "--repeats-per-batch",
        type=int,
        default=50,
        help="Number of repeated calls per model per validator in each batch.",
    )
    parser.add_argument(
        "--batches",
        type=int,
        default=2,
        help="Number of independent batches to run.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of UNL validators after filtering and sorting.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=None,
        help="Optional explicit validator domains to benchmark.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=18,
        help="Maximum number of concurrent OpenRouter requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Retries for retryable OpenRouter failures.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature passed to OpenRouter.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Optional override for max completion tokens across all models.",
    )
    parser.add_argument(
        "--output-dir",
        default="static/benchmarks",
        help="Directory for JSON and CSV outputs.",
    )
    parser.add_argument(
        "--output-prefix",
        default="xrpl-validator-credibility",
        help="Prefix for output artifact filenames.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="User-facing scoring prompt.",
    )
    parser.add_argument(
        "--shuffle-seed",
        type=int,
        default=7,
        help="Deterministic shuffle seed for request ordering.",
    )
    parser.add_argument(
        "--skip-model-catalog-check",
        action="store_true",
        help="Skip the OpenRouter /models preflight validation.",
    )
    return parser.parse_args(argv)


def load_dotenv_file(file_path: Path) -> None:
    if not file_path.exists():
        return
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


def bootstrap_env(script_path: Path) -> None:
    website_root = script_path.resolve().parents[1]
    repos_root = website_root.parent
    candidate_paths = [
        website_root / ".env",
        repos_root / "pftasks" / ".env",
        repos_root / "pftasks" / "api" / ".env",
        repos_root / "pftasks" / "worker" / ".env",
    ]
    for candidate in candidate_paths:
        load_dotenv_file(candidate)


def normalize_choice_content(body: dict[str, Any]) -> str:
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
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part).strip()
    return ""


def extract_score_and_rationale(raw_content: str) -> tuple[int | None, str | None, str | None]:
    text = str(raw_content or "").strip()
    if not text:
        return None, None, "empty_response"

    try:
        payload = json.loads(text)
        score = payload.get("score")
        if isinstance(score, bool):
            score = None
        if isinstance(score, (int, float)) and 0 <= int(score) <= 100:
            return int(score), None, None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            payload = json.loads(match.group(0))
            score = payload.get("score")
            if isinstance(score, (int, float)) and 0 <= int(score) <= 100:
                return int(score), None, None
        except json.JSONDecodeError:
            pass

    integer_match = re.search(r"(?<!\d)(100|[1-9]?\d)(?!\d)", text)
    if integer_match:
        return int(integer_match.group(1)), None, None

    return None, None, "score_not_found"


def build_messages(prompt: str, validator: ValidatorRecord) -> list[dict[str, str]]:
    user_prompt = (
        f"{prompt}\n\n"
        f"validator: {validator.domain}\n\n"
        'Return JSON only: {"score": <0-100 integer>}.'
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def model_completion_tokens(model: str, override: int | None) -> int:
    if isinstance(override, int) and override > 0:
        return override
    return MODEL_COMPLETION_TOKEN_DEFAULTS.get(model, 256)


def model_reasoning_config(model: str) -> dict[str, Any] | None:
    config = MODEL_REASONING_DEFAULTS.get(model)
    if not config:
        return None
    return dict(config)


async def fetch_validator_registry(client: httpx.AsyncClient) -> list[ValidatorRecord]:
    response = await client.get(XRPSCAN_VALIDATOR_REGISTRY_URL)
    response.raise_for_status()
    payload = response.json()
    validators: list[ValidatorRecord] = []
    for entry in payload:
        unl_publishers = tuple(entry.get("unl") or ())
        domain = str(entry.get("domain") or "").strip().lower()
        if not unl_publishers or not domain:
            continue
        meta = entry.get("meta") or {}
        server_version = entry.get("server_version") or {}
        validators.append(
            ValidatorRecord(
                domain=domain,
                master_key=str(entry.get("master_key") or "").strip(),
                unl_publishers=tuple(sorted(unl_publishers)),
                verified=bool(meta.get("verified")),
                verification_message=str(meta.get("verification_message") or "").strip() or None,
                server_version=str(server_version.get("version_full") or server_version.get("version") or "").strip() or None,
                last_seen=str(entry.get("last_seen") or "").strip() or None,
            )
        )
    validators.sort(key=lambda item: item.domain)
    return validators


async def validate_models_exist(client: httpx.AsyncClient, api_key: str, models: list[str]) -> None:
    response = await client.get(
        f"{OPENROUTER_BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    response.raise_for_status()
    payload = response.json()
    available = {entry.get("id") for entry in payload.get("data", []) if entry.get("id")}
    missing = [model for model in models if model not in available]
    if missing:
        raise RuntimeError(f"OpenRouter models not found: {', '.join(missing)}")


async def run_job(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    api_key: str,
    prompt: str,
    job: BenchmarkJob,
    temperature: float,
    max_tokens: int,
    timeout: float,
    max_retries: int,
) -> dict[str, Any]:
    queued_at = time.perf_counter()
    completion_token_budget = model_completion_tokens(job.model, max_tokens)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": DEFAULT_REFERER,
        "X-Title": DEFAULT_TITLE,
    }
    payload = {
        "model": job.model,
        "messages": build_messages(prompt, job.validator),
        "temperature": temperature,
        "max_completion_tokens": completion_token_budget,
    }
    reasoning = model_reasoning_config(job.model)
    if reasoning:
        payload["reasoning"] = reasoning

    last_error: str | None = None
    for attempt in range(max_retries + 1):
        try:
            async with semaphore:
                request_started_at = time.perf_counter()
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
                request_latency_ms = round((time.perf_counter() - request_started_at) * 1000, 2)
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < max_retries:
                last_error = f"http_{response.status_code}"
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            response.raise_for_status()
            body = response.json()
            content = normalize_choice_content(body)
            score, rationale, parse_error = extract_score_and_rationale(content)
            finish_reason = (body.get("choices") or [{}])[0].get("finish_reason")
            if score is None and finish_reason == "length" and attempt < max_retries:
                completion_token_budget = min(int(math.ceil(completion_token_budget * 1.5)), 2048)
                payload["max_completion_tokens"] = completion_token_budget
                await asyncio.sleep(0.25 * (attempt + 1))
                continue
            return {
                "model": job.model,
                "batch": job.batch,
                "repeat": job.repeat,
                "validator": asdict(job.validator),
                "score": score,
                "rationale": rationale,
                "parse_error": parse_error,
                "error": None,
                "request_latency_ms": request_latency_ms,
                "elapsed_ms": round((time.perf_counter() - queued_at) * 1000, 2),
                "usage": body.get("usage"),
                "response_id": body.get("id"),
                "response_model": body.get("model"),
                "finish_reason": finish_reason,
                "raw_content": content,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            return {
                "model": job.model,
                "batch": job.batch,
                "repeat": job.repeat,
                "validator": asdict(job.validator),
                "score": None,
                "rationale": None,
                "parse_error": None,
                "error": last_error,
                "request_latency_ms": None,
                "elapsed_ms": round((time.perf_counter() - queued_at) * 1000, 2),
                "usage": None,
                "response_id": None,
                "response_model": None,
                "finish_reason": None,
                "raw_content": None,
            }
    raise RuntimeError(f"unreachable: {last_error}")


def compute_mode(values: list[int]) -> int | None:
    if not values:
        return None
    modes = statistics.multimode(values)
    if not modes:
        return None
    counts = Counter(values)
    modes.sort(key=lambda item: (-counts[item], item))
    return modes[0]


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    total_cost = 0.0
    total_completion_tokens = 0.0
    total_reasoning_tokens = 0.0
    by_model_batch: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    by_model_batch_meta: dict[tuple[str, str, int], dict[str, Any]] = defaultdict(
        lambda: {
            "successes": 0,
            "errors": 0,
            "parse_errors": 0,
            "request_latencies_ms": [],
            "elapsed_ms": [],
            "completion_costs": [],
            "completion_tokens": [],
            "reasoning_tokens": [],
        }
    )
    by_model_domain: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for result in results:
        domain = result["validator"]["domain"]
        model = result["model"]
        batch = int(result["batch"])
        key = (domain, model, batch)
        meta = by_model_batch_meta[key]
        if isinstance(result.get("request_latency_ms"), (int, float)):
            meta["request_latencies_ms"].append(result.get("request_latency_ms"))
        if isinstance(result.get("elapsed_ms"), (int, float)):
            meta["elapsed_ms"].append(result.get("elapsed_ms"))
        usage = result.get("usage") or {}
        cost = usage.get("cost")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
            meta["completion_costs"].append(float(cost))
        completion_tokens = usage.get("completion_tokens")
        if isinstance(completion_tokens, (int, float)):
            total_completion_tokens += float(completion_tokens)
            meta["completion_tokens"].append(float(completion_tokens))
        reasoning_tokens = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
        if isinstance(reasoning_tokens, (int, float)):
            total_reasoning_tokens += float(reasoning_tokens)
            meta["reasoning_tokens"].append(float(reasoning_tokens))
        if result.get("error"):
            meta["errors"] += 1
        elif result.get("score") is None:
            meta["parse_errors"] += 1
        else:
            meta["successes"] += 1
            by_model_batch[key].append(int(result["score"]))
        by_model_domain[(domain, model)].append(result)

    batch_rows: list[dict[str, Any]] = []
    overall_rows: list[dict[str, Any]] = []

    for key in sorted(by_model_batch_meta):
        domain, model, batch = key
        scores = by_model_batch.get(key, [])
        meta = by_model_batch_meta[key]
        batch_rows.append(
            {
                "domain": domain,
                "model": model,
                "batch": batch,
                "n": len(scores),
                "errors": meta["errors"],
                "parse_errors": meta["parse_errors"],
                "mode": compute_mode(scores),
                "mean": round(statistics.fmean(scores), 4) if scores else None,
                "stdev": round(statistics.pstdev(scores), 4) if len(scores) > 1 else 0.0 if scores else None,
                "min": min(scores) if scores else None,
                "max": max(scores) if scores else None,
                "cost_sum": round(sum(meta["completion_costs"]), 6) if meta["completion_costs"] else 0.0,
                "completion_tokens_mean": round(statistics.fmean(meta["completion_tokens"]), 2)
                if meta["completion_tokens"]
                else None,
                "reasoning_tokens_mean": round(statistics.fmean(meta["reasoning_tokens"]), 2)
                if meta["reasoning_tokens"]
                else None,
                "request_latency_ms_mean": round(
                    statistics.fmean(value for value in meta["request_latencies_ms"] if isinstance(value, (int, float))),
                    2,
                )
                if meta["request_latencies_ms"]
                else None,
                "elapsed_ms_mean": round(
                    statistics.fmean(value for value in meta["elapsed_ms"] if isinstance(value, (int, float))),
                    2,
                )
                if meta["elapsed_ms"]
                else None,
            }
        )

    for key in sorted(by_model_domain):
        domain, model = key
        per_batch: dict[int, list[int]] = defaultdict(list)
        errors = 0
        parse_errors = 0
        request_latencies: list[float] = []
        elapsed_values: list[float] = []
        costs: list[float] = []
        completion_tokens_values: list[float] = []
        reasoning_tokens_values: list[float] = []
        for result in by_model_domain[key]:
            if isinstance(result.get("request_latency_ms"), (int, float)):
                request_latencies.append(result["request_latency_ms"])
            if isinstance(result.get("elapsed_ms"), (int, float)):
                elapsed_values.append(result["elapsed_ms"])
            usage = result.get("usage") or {}
            if isinstance(usage.get("cost"), (int, float)):
                costs.append(float(usage["cost"]))
            if isinstance(usage.get("completion_tokens"), (int, float)):
                completion_tokens_values.append(float(usage["completion_tokens"]))
            reasoning_tokens = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
            if isinstance(reasoning_tokens, (int, float)):
                reasoning_tokens_values.append(float(reasoning_tokens))
            if result.get("error"):
                errors += 1
                continue
            if result.get("score") is None:
                parse_errors += 1
                continue
            per_batch[int(result["batch"])].append(int(result["score"]))
        all_scores = [score for batch_scores in per_batch.values() for score in batch_scores]
        overall_rows.append(
            {
                "domain": domain,
                "model": model,
                "n": len(all_scores),
                "errors": errors,
                "parse_errors": parse_errors,
                "overall_mode": compute_mode(all_scores),
                "overall_mean": round(statistics.fmean(all_scores), 4) if all_scores else None,
                "overall_stdev": round(statistics.pstdev(all_scores), 4) if len(all_scores) > 1 else 0.0 if all_scores else None,
                "batch_1_mode": compute_mode(per_batch.get(1, [])),
                "batch_2_mode": compute_mode(per_batch.get(2, [])),
                "cost_sum": round(sum(costs), 6) if costs else 0.0,
                "completion_tokens_mean": round(statistics.fmean(completion_tokens_values), 2)
                if completion_tokens_values
                else None,
                "reasoning_tokens_mean": round(statistics.fmean(reasoning_tokens_values), 2)
                if reasoning_tokens_values
                else None,
                "request_latency_ms_mean": round(statistics.fmean(request_latencies), 2) if request_latencies else None,
                "elapsed_ms_mean": round(statistics.fmean(elapsed_values), 2) if elapsed_values else None,
            }
        )

    return {
        "totals": {
            "request_count": len(results),
            "cost_sum": round(total_cost, 6),
            "completion_tokens_sum": round(total_completion_tokens, 2),
            "reasoning_tokens_sum": round(total_reasoning_tokens, 2),
        },
        "by_batch": batch_rows,
        "overall": overall_rows,
    }


def write_summary_csv(output_path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def filter_validators(validators: list[ValidatorRecord], args: argparse.Namespace) -> list[ValidatorRecord]:
    if args.domains:
        wanted = [domain.strip().lower() for domain in args.domains if domain.strip()]
        wanted_set = set(wanted)
        selected = [validator for validator in validators if validator.domain in wanted_set]
        missing = [domain for domain in wanted if domain not in {validator.domain for validator in selected}]
        if missing:
            raise RuntimeError(f"Requested validator domains not found in current XRPSCAN UNL set: {', '.join(missing)}")
        by_domain = {validator.domain: validator for validator in selected}
        return [by_domain[domain] for domain in wanted]
    if args.limit:
        return validators[: args.limit]
    return validators


def build_jobs(validators: list[ValidatorRecord], args: argparse.Namespace) -> list[BenchmarkJob]:
    jobs = [
        BenchmarkJob(model=model, batch=batch, repeat=repeat, validator=validator)
        for model in args.models
        for batch in range(1, args.batches + 1)
        for repeat in range(1, args.repeats_per_batch + 1)
        for validator in validators
    ]
    random.Random(args.shuffle_seed).shuffle(jobs)
    return jobs


async def run_async(args: argparse.Namespace, script_path: Path) -> int:
    bootstrap_env(script_path)
    api_key = str(os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY missing after env bootstrap.")

    timeout = httpx.Timeout(args.timeout, connect=min(args.timeout, 20.0))
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        if not args.skip_model_catalog_check:
            await validate_models_exist(client, api_key, args.models)

        validators = await fetch_validator_registry(client)
        validators = filter_validators(validators, args)
        jobs = build_jobs(validators, args)
        semaphore = asyncio.Semaphore(args.concurrency)

        print(
            json.dumps(
                {
                    "validators": len(validators),
                    "domains": [validator.domain for validator in validators],
                    "models": args.models,
                    "batches": args.batches,
                    "repeats_per_batch": args.repeats_per_batch,
                    "total_requests": len(jobs),
                    "concurrency": args.concurrency,
                },
                indent=2,
            )
        )

        tasks = [
            asyncio.create_task(
                run_job(
                    client=client,
                    semaphore=semaphore,
                    api_key=api_key,
                    prompt=args.prompt,
                    job=job,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                )
            )
            for job in jobs
        ]

        results: list[dict[str, Any]] = []
        completed = 0
        total = len(tasks)
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            completed += 1
            if completed == total or completed % max(1, math.ceil(total / 10)) == 0:
                print(f"progress {completed}/{total}", file=sys.stderr)

    summary = build_summary(results)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = (script_path.resolve().parents[1] / args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / f"{args.output_prefix}-{timestamp}.json"
    batch_csv_path = output_root / f"{args.output_prefix}-{timestamp}-by-batch.csv"
    overall_csv_path = output_root / f"{args.output_prefix}-{timestamp}-overall.csv"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "validator_registry": XRPSCAN_VALIDATOR_REGISTRY_URL,
            "models": args.models,
            "prompt": args.prompt,
            "system_prompt": SYSTEM_PROMPT,
            "model_completion_token_defaults": MODEL_COMPLETION_TOKEN_DEFAULTS,
            "model_reasoning_defaults": MODEL_REASONING_DEFAULTS,
        },
        "run_config": {
            "batches": args.batches,
            "repeats_per_batch": args.repeats_per_batch,
            "concurrency": args.concurrency,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
            "max_retries": args.max_retries,
        },
        "validators": [asdict(validator) for validator in validators],
        "summary": summary,
        "results": results,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_summary_csv(batch_csv_path, summary["by_batch"])
    write_summary_csv(overall_csv_path, summary["overall"])

    print(f"wrote {json_path}")
    print(f"wrote {batch_csv_path}")
    print(f"wrote {overall_csv_path}")
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        return asyncio.run(run_async(args, Path(__file__)))
    except KeyboardInterrupt:
        print("aborted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
