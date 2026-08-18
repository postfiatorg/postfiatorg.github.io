#!/usr/bin/env python3
"""Compare short funding across fixed Hyperliquid perp universes.

The output deliberately separates Hyperliquid's core crypto perps from HIP-3
``xyz:`` markets. Positive funding means longs paid shorts. Each market is
measured over the same trailing window within its cohort, with minimum coverage
and freshness rules fixed on the command line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pandas as pd


HOURS_PER_YEAR = 24 * 365


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xyz_manifest(files: list[Path]) -> tuple[str, list[dict[str, object]]]:
    entries = [
        {
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(files, key=lambda item: item.name)
    ]
    canonical = json.dumps(entries, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(canonical).hexdigest(), entries


def normalize_cutoff(value: str) -> pd.Timestamp:
    cutoff = pd.Timestamp(value)
    if cutoff.tzinfo is None:
        cutoff = cutoff.tz_localize("UTC")
    return cutoff.tz_convert("UTC")


def summarize_market(
    cohort: str,
    coin: str,
    rates: pd.Series,
    *,
    cutoff: pd.Timestamp,
    expected_hours: int,
) -> dict[str, object]:
    rates = rates.dropna().sort_index()
    simple_sum_pct = float(rates.sum() * 100)
    return {
        "cohort": cohort,
        "coin": coin,
        "observations": int(rates.size),
        "coverage_pct": float(100 * rates.size / expected_hours),
        "first_observation_utc": rates.index.min().isoformat(),
        "last_observation_utc": rates.index.max().isoformat(),
        "hours_stale_at_cutoff": float(
            (cutoff - rates.index.max()).total_seconds() / 3600
        ),
        "positive_hours_pct": float(100 * (rates > 0).mean()),
        "negative_hours_pct": float(100 * (rates < 0).mean()),
        "simple_cumulative_funding_1x_pct": simple_sum_pct,
        "constant_2x_funding_pct_of_starting_equity": 2 * simple_sum_pct,
        "annualized_arithmetic_mean_1x_pct": float(
            rates.mean() * HOURS_PER_YEAR * 100
        ),
    }


def eligible_market_rows(
    cohort: str,
    market_rates: dict[str, pd.Series],
    *,
    cutoff: pd.Timestamp,
    window_days: int,
    min_coverage: float,
    freshness_hours: float,
) -> tuple[list[dict[str, object]], int]:
    expected_hours = window_days * 24
    minimum_observations = math.ceil(expected_hours * min_coverage)
    window_start = cutoff - pd.Timedelta(days=window_days)
    rows: list[dict[str, object]] = []
    for coin, complete_rates in sorted(market_rates.items()):
        rates = complete_rates[
            (complete_rates.index > window_start) & (complete_rates.index <= cutoff)
        ]
        if rates.empty or rates.size < minimum_observations:
            continue
        staleness = (cutoff - rates.index.max()).total_seconds() / 3600
        if staleness > freshness_hours:
            continue
        rows.append(
            summarize_market(
                cohort,
                coin,
                rates,
                cutoff=cutoff,
                expected_hours=expected_hours,
            )
        )
    return rows, len(market_rates)


def load_core_rates(panel_path: Path) -> dict[str, pd.Series]:
    panel = pd.read_parquet(panel_path)
    if not isinstance(panel.columns, pd.MultiIndex):
        raise RuntimeError("core panel must have MultiIndex (coin, field) columns")
    coins = sorted(set(panel.columns.get_level_values("coin")))
    return {
        str(coin): panel[(coin, "funding")].dropna().sort_index()
        for coin in coins
        if (coin, "funding") in panel.columns
    }


def load_xyz_rates(files: list[Path]) -> dict[str, pd.Series]:
    frames = []
    for path in files:
        frame = pd.read_parquet(
            path, columns=["time_ms", "coin", "funding_rate"]
        ).copy()
        frames.append(frame)
    if not frames:
        raise RuntimeError("no xyz funding parquet files found")
    funding = pd.concat(frames, ignore_index=True)
    funding["hour"] = pd.to_datetime(funding["time_ms"], unit="ms", utc=True).dt.floor(
        "h"
    )
    # Multiple archive files may overlap. One settled rate per coin-hour is the
    # unit of analysis; retain the latest captured row for that hour.
    funding = funding.sort_values("time_ms").drop_duplicates(
        subset=["coin", "hour"], keep="last"
    )
    return {
        str(coin): group.set_index("hour")["funding_rate"].dropna().sort_index()
        for coin, group in funding.groupby("coin", sort=True)
    }


def distribution(series: pd.Series) -> dict[str, float]:
    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "q25": float(series.quantile(0.25)),
        "q75": float(series.quantile(0.75)),
        "minimum": float(series.min()),
        "maximum": float(series.max()),
    }


def summarize_cohort(
    cohort: str,
    rows: list[dict[str, object]],
    *,
    universe_markets: int,
    cutoff: pd.Timestamp,
    window_days: int,
) -> dict[str, object]:
    frame = pd.DataFrame(rows)
    cumulative = frame["simple_cumulative_funding_1x_pct"]
    observations = frame["observations"]
    positive_hours = (
        frame["positive_hours_pct"] * observations / 100
    ).sum()
    # Each row's cumulative rate is already the sum of its hourly observations.
    pooled_mean_hourly = (cumulative.sum() / 100) / observations.sum()
    return {
        "cohort": cohort,
        "cutoff_utc": cutoff.isoformat(),
        "window_start_exclusive_utc": (
            cutoff - pd.Timedelta(days=window_days)
        ).isoformat(),
        "universe_markets": universe_markets,
        "eligible_markets": int(frame.shape[0]),
        "eligible_market_hours": int(observations.sum()),
        "markets_with_positive_cumulative_funding": int((cumulative > 0).sum()),
        "markets_with_positive_cumulative_funding_pct": float(
            100 * (cumulative > 0).mean()
        ),
        "pooled_positive_market_hours_pct": float(
            100 * positive_hours / observations.sum()
        ),
        "pooled_annualized_arithmetic_mean_1x_pct": float(
            pooled_mean_hourly * HOURS_PER_YEAR * 100
        ),
        "equal_market_simple_cumulative_funding_1x_pct": distribution(cumulative),
        "equal_market_constant_2x_funding_pct_of_starting_equity": distribution(
            cumulative * 2
        ),
        "equal_market_positive_hours_pct": distribution(
            frame["positive_hours_pct"]
        ),
        "equal_market_annualized_arithmetic_mean_1x_pct": distribution(
            frame["annualized_arithmetic_mean_1x_pct"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-panel", type=Path, required=True)
    parser.add_argument("--xyz-dir", type=Path, required=True)
    parser.add_argument("--core-cutoff", required=True)
    parser.add_argument("--xyz-cutoff", required=True)
    parser.add_argument("--window-days", type=int, default=90)
    parser.add_argument("--min-coverage", type=float, default=0.90)
    parser.add_argument("--freshness-hours", type=float, default=6)
    parser.add_argument("--markets-csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    core_cutoff = normalize_cutoff(args.core_cutoff)
    xyz_cutoff = normalize_cutoff(args.xyz_cutoff)
    xyz_files = sorted(args.xyz_dir.glob("xyz_*.parquet"))
    core_rates = load_core_rates(args.core_panel)
    xyz_rates = load_xyz_rates(xyz_files)
    core_rows, core_universe = eligible_market_rows(
        "core_crypto",
        core_rates,
        cutoff=core_cutoff,
        window_days=args.window_days,
        min_coverage=args.min_coverage,
        freshness_hours=args.freshness_hours,
    )
    xyz_rows, xyz_universe = eligible_market_rows(
        "hip3_xyz",
        xyz_rates,
        cutoff=xyz_cutoff,
        window_days=args.window_days,
        min_coverage=args.min_coverage,
        freshness_hours=args.freshness_hours,
    )
    rows = core_rows + xyz_rows
    if not core_rows or not xyz_rows:
        raise RuntimeError("both cohorts must have at least one eligible market")

    args.markets_csv.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows).sort_values(["cohort", "coin"])
    frame.to_csv(args.markets_csv, index=False, float_format="%.10f")
    markets_csv_sha256 = sha256_file(args.markets_csv)
    xyz_manifest_sha256, xyz_entries = xyz_manifest(xyz_files)
    summary = {
        "schema": "postfiat-ultrashort-funding-universe-v1",
        "methodology": {
            "funding_convention": (
                "positive funding is paid by longs to shorts; negative funding "
                "is paid by shorts to longs"
            ),
            "window_days": args.window_days,
            "minimum_coverage_pct": args.min_coverage * 100,
            "maximum_staleness_hours": args.freshness_hours,
            "market_weighting": (
                "distribution statistics give each eligible market equal weight; "
                "pooled statistics give each observed market-hour equal weight"
            ),
            "cumulative_funding": "simple sum of settled hourly funding rates",
            "constant_2x_example": (
                "twice the 1x simple funding sum; excludes price P&L, changing "
                "notional, rebalancing, fees, liquidation, and compounding"
            ),
        },
        "sources": {
            "core_panel": {
                "file": args.core_panel.name,
                "bytes": args.core_panel.stat().st_size,
                "sha256": sha256_file(args.core_panel),
            },
            "xyz_archive": {
                "files": len(xyz_entries),
                "manifest_sha256": xyz_manifest_sha256,
            },
            "markets_csv_sha256": markets_csv_sha256,
        },
        "cohorts": {
            "core_crypto": summarize_cohort(
                "core_crypto",
                core_rows,
                universe_markets=core_universe,
                cutoff=core_cutoff,
                window_days=args.window_days,
            ),
            "hip3_xyz": summarize_cohort(
                "hip3_xyz",
                xyz_rows,
                universe_markets=xyz_universe,
                cutoff=xyz_cutoff,
                window_days=args.window_days,
            ),
        },
        "combined_inventory": {
            "eligible_markets": len(rows),
            "eligible_market_hours": int(frame["observations"].sum()),
            "note": (
                "Cohorts have different cutoffs and market structures; use their "
                "separate distributions for economic inference."
            ),
        },
        "limitations": [
            "Historical funding is not a forecast and can reverse sign.",
            "This is a funding decomposition, not a token or short-strategy return backtest.",
            "Price P&L, changing notional, rebalancing, liquidation, fees, slippage, and compounding are excluded.",
            "Survivorship remains possible because the test requires a market to be active and sufficiently complete at the cohort cutoff.",
            "Core crypto and HIP-3 xyz markets are reported separately because their assets, operators, and funding regimes differ.",
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
