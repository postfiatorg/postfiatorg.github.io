#!/usr/bin/env python3
"""Build reproducible funding evidence for the UltraShort research proposal.

The script reads settled hourly funding from Hyperliquid's public info endpoint,
writes a canonical CSV snapshot, and derives a JSON summary. Positive funding
means longs paid shorts under Hyperliquid's documented convention.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path


INFO_URL = "https://api.hyperliquid.xyz/info"
HOURS_PER_YEAR = 24 * 365


def _post_info(payload: dict[str, object]) -> list[dict[str, object]]:
    request = urllib.request.Request(
        INFO_URL,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.load(response)
    if not isinstance(value, list):
        raise RuntimeError("Hyperliquid returned a non-list funding response")
    return value


def fetch_funding(
    coin: str,
    *,
    start_ms: int,
    end_ms: int,
    max_pages: int = 20,
) -> list[dict[str, object]]:
    rows: dict[int, dict[str, object]] = {}
    cursor = start_ms
    for _ in range(max_pages):
        batch = _post_info(
            {
                "type": "fundingHistory",
                "coin": coin,
                "startTime": cursor,
                "endTime": end_ms,
            }
        )
        if not batch:
            break
        for raw in batch:
            time_ms = int(raw["time"])
            if time_ms > end_ms:
                continue
            rows[time_ms] = {
                "time_ms": time_ms,
                "time_utc": datetime.fromtimestamp(
                    time_ms / 1_000, tz=timezone.utc
                ).isoformat(timespec="milliseconds"),
                "coin": str(raw.get("coin") or coin),
                "funding_rate": float(raw["fundingRate"]),
                "premium": (
                    "" if raw.get("premium") is None else float(raw["premium"])
                ),
            }
        last = int(batch[-1]["time"])
        if last >= end_ms or last < cursor or len(batch) < 2:
            break
        cursor = last + 1
    result = [rows[key] for key in sorted(rows)]
    if not result:
        raise RuntimeError(f"no funding rows returned for {coin}")
    return result


def canonical_csv(rows: list[dict[str, object]]) -> bytes:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=["time_ms", "time_utc", "coin", "funding_rate", "premium"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _rolling_apr(rates: list[float], hours: int) -> list[float]:
    if len(rates) < hours:
        return []
    window: deque[float] = deque()
    running = 0.0
    values: list[float] = []
    for rate in rates:
        window.append(rate)
        running += rate
        if len(window) > hours:
            running -= window.popleft()
        if len(window) == hours:
            values.append((running / hours) * HOURS_PER_YEAR * 100)
    return values


def summarize(rows: list[dict[str, object]], *, csv_sha256: str) -> dict[str, object]:
    rates = [float(row["funding_rate"]) for row in rows]
    positive = [rate for rate in rates if rate > 0]
    negative = [rate for rate in rates if rate < 0]
    cumulative = 0.0
    high_water = 0.0
    maximum_drawdown = 0.0
    current_negative_streak = 0
    longest_negative_streak = 0
    monthly: dict[str, list[float]] = defaultdict(list)
    for row, rate in zip(rows, rates, strict=True):
        cumulative += rate
        high_water = max(high_water, cumulative)
        maximum_drawdown = min(maximum_drawdown, cumulative - high_water)
        current_negative_streak = current_negative_streak + 1 if rate < 0 else 0
        longest_negative_streak = max(
            longest_negative_streak, current_negative_streak
        )
        month = str(row["time_utc"])[:7]
        monthly[month].append(rate)

    monthly_rows = []
    for month, values in sorted(monthly.items()):
        monthly_rows.append(
            {
                "month": month,
                "observations": len(values),
                "positive_hours_pct": 100 * sum(v > 0 for v in values) / len(values),
                "simple_cumulative_funding_1x_pct": 100 * sum(values),
                "annualized_arithmetic_mean_1x_pct": (
                    statistics.mean(values) * HOURS_PER_YEAR * 100
                ),
            }
        )

    rolling_7d = _rolling_apr(rates, 24 * 7)
    rolling_30d = _rolling_apr(rates, 24 * 30)
    cumulative_1x_pct = sum(rates) * 100
    return {
        "schema": "postfiat-ultrashort-funding-evidence-v1",
        "methodology": {
            "source": "Hyperliquid public info endpoint fundingHistory",
            "source_url": INFO_URL,
            "funding_convention": (
                "positive funding is paid by longs to shorts; negative funding "
                "is paid by shorts to longs"
            ),
            "annualization": "arithmetic mean hourly rate * 24 * 365",
            "cumulative_funding": "simple sum of settled hourly rates",
            "constant_2x_example": (
                "2 * simple cumulative funding; holds notional at twice starting "
                "equity and excludes price P&L, rebalancing, fees, and compounding"
            ),
        },
        "coin": rows[0]["coin"],
        "observations": len(rows),
        "first_observation_utc": rows[0]["time_utc"],
        "last_observation_utc": rows[-1]["time_utc"],
        "csv_sha256": csv_sha256,
        "mean_hourly_rate": statistics.mean(rates),
        "median_hourly_rate": statistics.median(rates),
        "positive_hours_pct": 100 * len(positive) / len(rates),
        "negative_hours_pct": 100 * len(negative) / len(rates),
        "positive_contribution_1x_pct": 100 * sum(positive),
        "negative_contribution_1x_pct": 100 * sum(negative),
        "simple_cumulative_funding_1x_pct": cumulative_1x_pct,
        "constant_2x_funding_contribution_pct_of_starting_equity": (
            2 * cumulative_1x_pct
        ),
        "constant_2x_funding_dollars_per_1000_starting_equity": (
            20 * cumulative_1x_pct
        ),
        "annualized_arithmetic_mean_1x_pct": (
            statistics.mean(rates) * HOURS_PER_YEAR * 100
        ),
        "annualized_arithmetic_mean_2x_pct_of_equity": (
            statistics.mean(rates) * HOURS_PER_YEAR * 200
        ),
        "worst_cumulative_funding_drawdown_1x_pct": 100 * maximum_drawdown,
        "longest_consecutive_negative_hours": longest_negative_streak,
        "rolling_7d_apr_pct": {
            "minimum": min(rolling_7d),
            "median": statistics.median(rolling_7d),
            "maximum": max(rolling_7d),
        },
        "rolling_30d_apr_pct": {
            "minimum": min(rolling_30d),
            "median": statistics.median(rolling_30d),
            "maximum": max(rolling_30d),
        },
        "monthly": monthly_rows,
        "limitations": [
            "Historical funding is not a forecast.",
            "The calculation isolates funding and is not a token return backtest.",
            "Price P&L, changing notional, rebalancing, liquidation, fees, slippage, and compounding are excluded.",
            "The public API may not retain the full history indefinitely; the CSV is the immutable snapshot used here.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coin", default="xyz:SMSN")
    parser.add_argument("--start-ms", type=int, default=0)
    parser.add_argument("--end-ms", type=int, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    rows = fetch_funding(
        args.coin,
        start_ms=args.start_ms,
        end_ms=args.end_ms,
    )
    csv_bytes = canonical_csv(rows)
    csv_sha256 = hashlib.sha256(csv_bytes).hexdigest()
    summary = summarize(rows, csv_sha256=csv_sha256)

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.csv.write_bytes(csv_bytes)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
