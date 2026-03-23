#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


DEFAULT_SOURCE_URL = "https://vhs.testnet.postfiat.org/v1/network/validators/test"
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent / "static" / "benchmarks" / "live-testnet-validator-stats.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a compact live validator stats snapshot for the homepage fallback path."
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help=f"Validator registry URL. Defaults to {DEFAULT_SOURCE_URL}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output JSON path. Defaults to {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def fetch_payload(source_url: str) -> dict:
    response = requests.get(source_url, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("validators"), list):
        raise RuntimeError("Unexpected validator payload shape.")
    return payload


def mean_score(validators: list[dict], key: str) -> float:
    values: list[float] = []
    for validator in validators:
        raw_score = validator.get(key, {}).get("score")
        try:
            values.append(float(raw_score))
        except (TypeError, ValueError):
            continue
    if not values:
        return 0.0
    return sum(values) / len(values)


def threshold_count(validators: list[dict], key: str, threshold: float) -> int:
    count = 0
    for validator in validators:
        try:
            score = float(validator.get(key, {}).get("score"))
        except (TypeError, ValueError):
            continue
        if score >= threshold:
            count += 1
    return count


def build_snapshot(payload: dict, source_url: str) -> dict:
    validators = [validator for validator in payload["validators"] if not validator.get("revoked")]
    validator_count = len(validators)
    publishing_domain_count = sum(1 for validator in validators if str(validator.get("domain") or "").strip())
    verified_domain_count = sum(1 for validator in validators if bool(validator.get("domain_verified")))
    latest_ledger_index = max(
        (int(validator.get("current_index") or 0) for validator in validators),
        default=0,
    )

    strong_24h = threshold_count(validators, "agreement_24h", 0.999)
    strong_30day = threshold_count(validators, "agreement_30day", 0.99)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_name": "Live VHS snapshot",
        "source_url": source_url,
        "validator_count": validator_count,
        "publishing_domain_count": publishing_domain_count,
        "verified_domain_count": verified_domain_count,
        "latest_ledger_index": latest_ledger_index,
        "agreement_24h": {
            "threshold": 0.999,
            "threshold_label": "99.9%+",
            "count": strong_24h,
            "ratio": (strong_24h / validator_count) if validator_count else 0.0,
            "mean_score": mean_score(validators, "agreement_24h"),
        },
        "agreement_30day": {
            "threshold": 0.99,
            "threshold_label": "99%+",
            "count": strong_30day,
            "ratio": (strong_30day / validator_count) if validator_count else 0.0,
            "mean_score": mean_score(validators, "agreement_30day"),
        },
    }


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).resolve()
    payload = fetch_payload(args.source_url)
    snapshot = build_snapshot(payload, args.source_url)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
