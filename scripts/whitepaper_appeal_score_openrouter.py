#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import statistics
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODELS = ("anthropic/claude-opus-4.7", "openai/gpt-5.5")
DEFAULT_WHITEPAPER = "content/whitepaper.md"
DEFAULT_OUTPUT_DIR = "static/benchmarks"
DEFAULT_OUTPUT_PREFIX = "postfiat-whitepaper-appeal"
DEFAULT_TIMEOUT = 300.0
DEFAULT_MAX_TOKENS = 2200
DEFAULT_TEMPERATURE = 0.0
DEFAULT_RUNS_PER_MODEL = 3
DEFAULT_REFERER = "https://postfiat.org"
DEFAULT_TITLE = "postfiat-whitepaper-appeal-score"
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504, 520, 521, 522, 524}


@dataclass(frozen=True)
class ModelResult:
    requested_model: str
    run_index: int
    response_model: str
    score: int
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    highest_leverage_fixes: list[str]
    audience_appeal_notes: list[str]
    raw_response_text: str
    usage: dict[str, Any]
    latency_seconds: float
    response_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score the Post Fiat whitepaper's appeal using Opus 4.7 and GPT-5.5 over OpenRouter."
    )
    parser.add_argument("--whitepaper", default=DEFAULT_WHITEPAPER)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-prefix", default=DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument(
        "--runs-per-model",
        type=int,
        default=DEFAULT_RUNS_PER_MODEL,
        help="Number of independent judge calls to run for each model. Defaults to 3.",
    )
    parser.add_argument(
        "--allow-fallbacks",
        action="store_true",
        help="Allow OpenRouter provider fallback routing. Defaults to false for cleaner model attribution.",
    )
    parser.add_argument(
        "--keep-frontmatter",
        action="store_true",
        help="Include Jekyll front matter in the text shown to judges.",
    )
    return parser.parse_args()


def load_dotenv_file(file_path: Path) -> None:
    if not file_path.exists():
        return
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def bootstrap_env(script_path: Path) -> None:
    website_root = script_path.resolve().parents[1]
    repos_root = website_root.parent
    for candidate in (
        website_root / ".env",
        repos_root / "pftasks" / "api" / ".env",
        repos_root / "pftasks" / "worker" / ".env",
    ):
        load_dotenv_file(candidate)


def resolve_openrouter_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to the environment or one of the local .env files."
        )
    return api_key


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip()
    return text


def load_whitepaper(path: Path, keep_frontmatter: bool) -> str:
    text = path.read_text(encoding="utf-8")
    return text if keep_frontmatter else strip_frontmatter(text)


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
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part).strip()
    return ""


def extract_json(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    cleaned = raw
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()
    for candidate in (raw, cleaned):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        parsed = json.loads(raw[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError(f"No JSON object found in model response: {raw[:500]}")


def clamp_score(value: Any) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def string_list(value: Any, limit: int = 6) -> list[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, str) and value.strip():
        items = [value]
    else:
        items = []
    return [str(item).strip() for item in items if str(item).strip()][:limit]


def build_messages(whitepaper_markdown: str) -> list[dict[str, str]]:
    system = (
        "You are a skeptical frontier-model evaluator reviewing a crypto/network whitepaper. "
        "Judge the paper as written for serious reader appeal. Do not rewrite it. "
        "Return valid JSON only."
    )
    user = (
        "Score the following Post Fiat whitepaper on a 0-100 scale for appeal.\n\n"
        "Definition of appeal:\n"
        "- The paper makes the project feel important, credible, differentiated, and worth continued attention.\n"
        "- It appeals to sophisticated technical readers, crypto infrastructure people, validators, investors, and builders.\n"
        "- It has a clear thesis, strong evidence, good structure, useful caveats, and a compelling sense of why this matters now.\n"
        "- It avoids sounding generic, evasive, overclaimed, internally confused, legally awkward, or padded.\n\n"
        "Scoring calibration:\n"
        "- 95-100: category-defining, exceptionally persuasive, and almost publication-perfect.\n"
        "- 90-94: excellent and clearly compelling, with only minor weaknesses.\n"
        "- 80-89: strong but meaningfully improvable.\n"
        "- 70-79: credible but not yet compelling enough for elite readers.\n"
        "- 60-69: has substance but major appeal/positioning/clarity problems.\n"
        "- 0-59: weak, confusing, unserious, or not publication-ready.\n\n"
        "Return exactly this JSON object:\n"
        "{\n"
        '  "score": 0,\n'
        '  "summary": "one concise paragraph explaining the score",\n'
        '  "strengths": ["3-5 bullets"],\n'
        '  "weaknesses": ["3-5 bullets"],\n'
        '  "highest_leverage_fixes": ["3-5 concrete edits that would most improve appeal"],\n'
        '  "audience_appeal_notes": ["3-5 bullets naming which audiences are or are not persuaded"]\n'
        "}\n\n"
        "Whitepaper markdown:\n\n"
        f"{whitepaper_markdown}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def call_openrouter(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    request_body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "provider": {"allow_fallbacks": bool(args.allow_fallbacks)},
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": DEFAULT_REFERER,
        "X-Title": DEFAULT_TITLE,
    }
    last_error: Exception | None = None
    for attempt in range(3):
        request = urllib.request.Request(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            data=json.dumps(request_body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                response_body = response.read().decode("utf-8")
            return json.loads(response_body)
        except urllib.error.HTTPError as exc:
            last_error = exc
            status_code = exc.code
            if status_code not in RETRYABLE_STATUS_CODES or attempt == 2:
                error_body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenRouter HTTP {status_code} for {model}: {error_body}") from exc
        except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 2:
                raise
        time.sleep((2**attempt) + random.random())
    assert last_error is not None
    raise last_error


async def score_model(
    *,
    api_key: str,
    requested_model: str,
    run_index: int,
    messages: list[dict[str, str]],
    args: argparse.Namespace,
) -> ModelResult:
    started = time.perf_counter()
    body = await asyncio.to_thread(
        call_openrouter,
        api_key=api_key,
        model=requested_model,
        messages=messages,
        args=args,
    )
    latency_seconds = round(time.perf_counter() - started, 3)
    raw_text = normalize_choice_content(body)
    parsed = extract_json(raw_text)
    return ModelResult(
        requested_model=requested_model,
        run_index=run_index,
        response_model=str(body.get("model") or requested_model),
        score=clamp_score(parsed.get("score")),
        summary=str(parsed.get("summary", "")).strip(),
        strengths=string_list(parsed.get("strengths")),
        weaknesses=string_list(parsed.get("weaknesses")),
        highest_leverage_fixes=string_list(parsed.get("highest_leverage_fixes")),
        audience_appeal_notes=string_list(parsed.get("audience_appeal_notes")),
        raw_response_text=raw_text,
        usage=body.get("usage") if isinstance(body.get("usage"), dict) else {},
        latency_seconds=latency_seconds,
        response_id=str(body.get("id", "")),
    )


def usage_total_cost(usage: dict[str, Any]) -> float | None:
    value = usage.get("cost")
    if value is None:
        value = usage.get("total_cost")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_summary(
    *,
    whitepaper_path: Path,
    results: list[ModelResult],
    generated_at: str,
    elapsed_seconds: float,
    output_base: str,
) -> dict[str, Any]:
    scores = [result.score for result in results]
    costs = [usage_total_cost(result.usage) for result in results]
    known_costs = [cost for cost in costs if cost is not None]
    model_score_summary: list[dict[str, Any]] = []
    for model in dict.fromkeys(result.requested_model for result in results):
        model_results = [result for result in results if result.requested_model == model]
        model_scores = [result.score for result in model_results]
        model_costs = [usage_total_cost(result.usage) for result in model_results]
        model_known_costs = [cost for cost in model_costs if cost is not None]
        model_latencies = [result.latency_seconds for result in model_results]
        model_score_summary.append(
            {
                "requested_model": model,
                "runs": len(model_results),
                "scores": model_scores,
                "mean_score": round(statistics.mean(model_scores), 2) if model_scores else 0.0,
                "score_stdev": round(statistics.stdev(model_scores), 2) if len(model_scores) > 1 else 0.0,
                "min_score": min(model_scores) if model_scores else None,
                "max_score": max(model_scores) if model_scores else None,
                "mean_latency_seconds": round(statistics.mean(model_latencies), 3) if model_latencies else 0.0,
                "known_total_cost_usd": round(sum(model_known_costs), 6) if model_known_costs else None,
            }
        )
    model_means = [item["mean_score"] for item in model_score_summary]
    return {
        "generated_at": generated_at,
        "whitepaper_path": str(whitepaper_path),
        "models": list(dict.fromkeys(result.requested_model for result in results)),
        "runs_per_model": max((item["runs"] for item in model_score_summary), default=0),
        "aggregate_score": round(statistics.mean(scores), 2) if scores else 0.0,
        "aggregate_model_mean_score": round(statistics.mean(model_means), 2) if model_means else 0.0,
        "score_count": len(scores),
        "score_stdev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "known_total_cost_usd": round(sum(known_costs), 6) if known_costs else None,
        "output_base": output_base,
        "model_score_summary": model_score_summary,
        "model_results": [
            {
                "requested_model": result.requested_model,
                "run_index": result.run_index,
                "response_model": result.response_model,
                "score": result.score,
                "summary": result.summary,
                "strengths": result.strengths,
                "weaknesses": result.weaknesses,
                "highest_leverage_fixes": result.highest_leverage_fixes,
                "audience_appeal_notes": result.audience_appeal_notes,
                "latency_seconds": result.latency_seconds,
                "usage": result.usage,
                "response_id": result.response_id,
            }
            for result in results
        ],
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Post Fiat Whitepaper Appeal Score",
        "",
        f"Generated: {summary['generated_at']}",
        f"Whitepaper: `{summary['whitepaper_path']}`",
        "",
        f"Aggregate score: **{summary['aggregate_score']} / 100**",
        f"Aggregate model-mean score: **{summary['aggregate_model_mean_score']} / 100**",
        f"Runs per model: `{summary['runs_per_model']}`",
        f"Score stdev: `{summary['score_stdev']}`",
        f"Elapsed: `{summary['elapsed_seconds']}s`",
    ]
    if summary.get("known_total_cost_usd") is not None:
        lines.append(f"Known OpenRouter cost: `${summary['known_total_cost_usd']}`")
    lines.append("")

    for item in summary.get("model_score_summary", []):
        lines.extend(
            [
                f"## {item['requested_model']} Mean - {item['mean_score']} / 100",
                "",
                f"Scores: `{item['scores']}`",
                f"Score stdev: `{item['score_stdev']}`",
                f"Mean latency: `{item['mean_latency_seconds']}s`",
            ]
        )
        if item.get("known_total_cost_usd") is not None:
            lines.append(f"Known OpenRouter cost: `${item['known_total_cost_usd']}`")
        lines.append("")

    for result in summary["model_results"]:
        lines.extend(
            [
                f"## {result['requested_model']} Run {result['run_index']} - {result['score']} / 100",
                "",
                result["summary"],
                "",
                "### Strengths",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in result["strengths"])
        lines.extend(["", "### Weaknesses", ""])
        lines.extend(f"- {item}" for item in result["weaknesses"])
        lines.extend(["", "### Highest-Leverage Fixes", ""])
        lines.extend(f"- {item}" for item in result["highest_leverage_fixes"])
        lines.extend(["", "### Audience Appeal Notes", ""])
        lines.extend(f"- {item}" for item in result["audience_appeal_notes"])
        lines.extend(
            [
                "",
                f"Latency: `{result['latency_seconds']}s`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


async def amain() -> None:
    script_path = Path(__file__).resolve()
    bootstrap_env(script_path)
    args = parse_args()
    if args.runs_per_model < 1:
        raise ValueError("--runs-per-model must be at least 1")
    root = script_path.parents[1]
    whitepaper_path = Path(args.whitepaper)
    if not whitepaper_path.is_absolute():
        whitepaper_path = root / whitepaper_path
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    api_key = resolve_openrouter_api_key()
    whitepaper = load_whitepaper(whitepaper_path, keep_frontmatter=args.keep_frontmatter)
    messages = build_messages(whitepaper)
    started = time.perf_counter()
    results = await asyncio.gather(
        *[
            score_model(
                api_key=api_key,
                requested_model=model,
                run_index=run_index,
                messages=messages,
                args=args,
            )
            for model in args.models
            for run_index in range(1, args.runs_per_model + 1)
        ]
    )
    elapsed_seconds = time.perf_counter() - started
    generated_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_base = f"{args.output_prefix}-{generated_at}"
    summary = build_summary(
        whitepaper_path=whitepaper_path,
        results=results,
        generated_at=generated_at,
        elapsed_seconds=elapsed_seconds,
        output_base=output_base,
    )

    raw_payload = {
        "generated_at": generated_at,
        "whitepaper_path": str(whitepaper_path),
        "models": list(args.models),
        "runs_per_model": args.runs_per_model,
        "model_results": [
            {
                **result.__dict__,
            }
            for result in results
        ],
    }
    raw_path = output_dir / f"{output_base}-raw.json"
    summary_path = output_dir / f"{output_base}-summary.json"
    markdown_path = output_dir / f"{output_base}-summary.md"
    latest_summary_path = output_dir / f"latest-{args.output_prefix}-summary.json"
    latest_markdown_path = output_dir / f"latest-{args.output_prefix}-summary.md"
    raw_path.write_text(json.dumps(raw_payload, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    markdown = render_markdown(summary)
    markdown_path.write_text(markdown, encoding="utf-8")
    latest_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    latest_markdown_path.write_text(markdown, encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
