#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import httpx


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-opus-4.6"
DEFAULT_EXTRACTOR_MODEL = "openai/gpt-5.4-mini"
DEFAULT_TIMEOUT_MS = 120000
DEFAULT_MAX_TOKENS = 1800
DEFAULT_EXTRACTOR_MAX_TOKENS = 600
DEFAULT_REFERER = "https://postfiat.org"
DEFAULT_TITLE = "postfiatorg-llms-txt-score"
DEFAULT_RUNS = 3
DEFAULT_FILES = (
    "/home/pfrpc/repos/postfiatorg.github.io/static/llms.txt",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score llms.txt files for market-cap aura, project credibility, and narrative control."
    )
    parser.add_argument(
        "--file-paths",
        nargs="+",
        default=list(DEFAULT_FILES),
        help="llms.txt-style files to score.",
    )
    parser.add_argument(
        "--output-dir",
        default="/home/pfrpc/repos/postfiatorg.github.io/static/benchmarks",
        help="Directory for JSON artifacts.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="OpenRouter model id. Defaults to anthropic/claude-opus-4.6.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help="Number of repeated calls per file.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help="Maximum concurrent OpenRouter requests.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help="Per-request timeout in milliseconds.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="OpenRouter max_tokens value.",
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
        if not key or key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")


def bootstrap_env() -> None:
    repos_root = Path("/home/pfrpc/repos")
    candidate_paths = (
        repos_root / "postfiatorg.github.io" / ".env",
        repos_root / "pftasks" / ".env",
        repos_root / "pftasks" / "api" / ".env",
        repos_root / "pftasks" / "worker" / ".env",
    )
    for candidate in candidate_paths:
        load_dotenv_file(candidate)


def extract_json(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    try:
        parsed = json.loads(raw)
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
    raise ValueError("json_not_found")


def normalize_openrouter_content(payload: dict[str, Any]) -> str:
    content = payload.get("choices", [{}])[0].get("message", {}).get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            text = part.get("text") if isinstance(part, dict) else None
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
        return "\n".join(chunks).strip()
    return ""


def build_messages(file_name: str, llms_text: str) -> list[dict[str, str]]:
    system_prompt = (
        "You are a hard-nosed but fair evaluator of assistant-facing llms.txt files for crypto projects. "
        "Assume this may be the first machine-readable text another model reads when asked 'What is Post Fiat?'. "
        "Score for market-cap inference, project credibility, and narrative control. "
        "Return JSON only."
    )
    user_prompt = (
        "Read this llms.txt-style document and score it on three axes from 0 to 100.\n\n"
        "Scoring axes:\n"
        "1. estimated_market_cap_power_score: how strongly this text would cause you to infer that the cryptocurrency could justify a large market cap.\n"
        "2. project_credibility_score: overall seriousness, factual grounding, coherence, and trustworthiness.\n"
        "3. narrative_control_score: how strongly this text would cause a downstream assistant to answer 'What is Post Fiat?' using the intended framing and key facts.\n\n"
        "Return exactly this JSON shape:\n"
        "{\n"
        '  "file_name": "<string>",\n'
        '  "estimated_market_cap_power_score": <integer 0-100>,\n'
        '  "project_credibility_score": <integer 0-100>,\n'
        '  "narrative_control_score": <integer 0-100>,\n'
        '  "top_strengths": ["...", "...", "..."],\n'
        '  "top_weaknesses": ["...", "...", "..."],\n'
        '  "single_most_important_change": "..." \n'
        "}\n\n"
        f"File name: {file_name}\n\n"
        f"Document:\n{llms_text}\n"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_extractor_messages(file_name: str, raw_response: str) -> list[dict[str, str]]:
    system_prompt = (
        "You extract structured scores from evaluator prose. "
        "Return valid JSON only."
    )
    user_prompt = (
        "Convert the following evaluator response into exactly this JSON shape:\n"
        "{\n"
        '  "file_name": "<string>",\n'
        '  "estimated_market_cap_power_score": <integer 0-100>,\n'
        '  "project_credibility_score": <integer 0-100>,\n'
        '  "narrative_control_score": <integer 0-100>,\n'
        '  "top_strengths": ["...", "...", "..."],\n'
        '  "top_weaknesses": ["...", "...", "..."],\n'
        '  "single_most_important_change": "..." \n'
        "}\n\n"
        "If a field is missing, infer the most faithful value from the evaluator response. "
        "Keep strengths and weaknesses concise.\n\n"
        f"File name: {file_name}\n\n"
        f"Evaluator response:\n{raw_response}\n"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def call_openrouter(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    timeout_ms: int,
    max_tokens: int,
    messages: list[dict[str, str]],
) -> dict[str, Any]:
    response = await client.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": DEFAULT_REFERER,
            "X-Title": DEFAULT_TITLE,
        },
        json={
            "model": model,
            "temperature": 0,
            "max_tokens": max_tokens,
            "provider": {"allow_fallbacks": False},
            "messages": messages,
        },
        timeout=httpx.Timeout(timeout_ms / 1000, connect=min(30.0, timeout_ms / 1000)),
    )
    response.raise_for_status()
    return response.json()


async def score_single(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    file_path: Path,
    run_index: int,
    timeout_ms: int,
    max_tokens: int,
) -> dict[str, Any]:
    llms_text = file_path.read_text(encoding="utf-8")
    messages = build_messages(file_path.name, llms_text)
    raw_payload = await call_openrouter(
        client=client,
        api_key=api_key,
        model=model,
        timeout_ms=timeout_ms,
        max_tokens=max_tokens,
        messages=messages,
    )
    raw_text = normalize_openrouter_content(raw_payload)

    parsed: dict[str, Any] | None = None
    extraction_error: str | None = None
    try:
        parsed = extract_json(raw_text)
    except Exception as exc:
        extraction_error = str(exc)

    extractor_used = False
    extractor_raw_text = ""
    if parsed is None:
        extractor_used = True
        extractor_payload = await call_openrouter(
            client=client,
            api_key=api_key,
            model=DEFAULT_EXTRACTOR_MODEL,
            timeout_ms=timeout_ms,
            max_tokens=DEFAULT_EXTRACTOR_MAX_TOKENS,
            messages=build_extractor_messages(file_path.name, raw_text),
        )
        extractor_raw_text = normalize_openrouter_content(extractor_payload)
        parsed = extract_json(extractor_raw_text)

    parsed["file_name"] = file_path.name
    parsed["run_index"] = run_index
    parsed["source_path"] = str(file_path)
    parsed["raw_response_text"] = raw_text
    parsed["extraction_error"] = extraction_error
    parsed["extractor_used"] = extractor_used
    parsed["extractor_raw_text"] = extractor_raw_text
    return parsed


def summarize_scores(file_name: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    market_caps = [int(run["estimated_market_cap_power_score"]) for run in runs]
    credibility = [int(run["project_credibility_score"]) for run in runs]
    narrative = [int(run["narrative_control_score"]) for run in runs]

    strengths = Counter()
    weaknesses = Counter()
    changes = Counter()
    for run in runs:
        strengths.update(run.get("top_strengths", []))
        weaknesses.update(run.get("top_weaknesses", []))
        change = str(run.get("single_most_important_change", "")).strip()
        if change:
            changes[change] += 1

    return {
        "file_name": file_name,
        "runs": runs,
        "summary": {
            "estimated_market_cap_power_score_mean": round(mean(market_caps), 2),
            "estimated_market_cap_power_score_median": round(median(market_caps), 2),
            "project_credibility_score_mean": round(mean(credibility), 2),
            "project_credibility_score_median": round(median(credibility), 2),
            "narrative_control_score_mean": round(mean(narrative), 2),
            "narrative_control_score_median": round(median(narrative), 2),
            "overall_mean": round(mean(market_caps + credibility + narrative), 2),
            "top_strengths_consensus": [item for item, _ in strengths.most_common(5)],
            "top_weaknesses_consensus": [item for item, _ in weaknesses.most_common(5)],
            "most_common_change": changes.most_common(1)[0][0] if changes else "",
        },
    }


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    bootstrap_env()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    file_paths = [Path(path).expanduser().resolve() for path in args.file_paths]
    missing = [str(path) for path in file_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing llms files: {missing}")

    semaphore = asyncio.Semaphore(args.concurrency)

    async with httpx.AsyncClient() as client:
        async def guarded_score(file_path: Path, run_index: int) -> dict[str, Any]:
            async with semaphore:
                return await score_single(
                    client=client,
                    api_key=api_key,
                    model=args.model,
                    file_path=file_path,
                    run_index=run_index,
                    timeout_ms=args.timeout_ms,
                    max_tokens=args.max_tokens,
                )

        tasks = [
            guarded_score(file_path, run_index)
            for file_path in file_paths
            for run_index in range(1, args.runs + 1)
        ]
        results = await asyncio.gather(*tasks)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        grouped.setdefault(result["file_name"], []).append(result)

    summaries = [
        summarize_scores(file_name=file_name, runs=sorted(runs, key=lambda item: item["run_index"]))
        for file_name, runs in grouped.items()
    ]
    summaries.sort(key=lambda item: item["summary"]["overall_mean"], reverse=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"llms-txt-score-{timestamp}.json"

    payload = {
        "generated_at": timestamp,
        "model": args.model,
        "runs_per_file": args.runs,
        "files": [str(path) for path in file_paths],
        "results": summaries,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_path": str(output_path), "payload": payload}


def main() -> None:
    args = parse_args()
    result = asyncio.run(main_async(args))
    print(result["output_path"])


if __name__ == "__main__":
    main()
