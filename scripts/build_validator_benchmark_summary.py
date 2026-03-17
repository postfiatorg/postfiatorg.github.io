#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODEL_LABELS = {
    "deepseek/deepseek-v3.2": "DeepSeek v3.2",
    "minimax/minimax-m2.5": "Minimax m2.5",
    "moonshotai/kimi-k2.5": "Kimi k2.5",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a compact summary JSON for the XRPL validator credibility benchmark page."
    )
    parser.add_argument("input_json", help="Path to the benchmark artifact JSON.")
    parser.add_argument("output_json", help="Path to write the compact summary JSON.")
    return parser.parse_args()


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or not xs:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def average_ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    output = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        next_index = index + 1
        while next_index < len(ordered) and ordered[next_index][1] == ordered[index][1]:
            next_index += 1
        average_rank = (index + 1 + next_index) / 2
        for offset in range(index, next_index):
            output[ordered[offset][0]] = average_rank
        index = next_index
    return output


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or not xs:
        return None
    return pearson(average_ranks(xs), average_ranks(ys))


def round_or_none(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def build_matrix(series: list[dict[str, Any]], domains: list[str], metric: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left in series:
        left_values = [float(left["values"][domain][metric]) for domain in domains]
        values: list[float | None] = []
        for right in series:
            right_values = [float(right["values"][domain][metric]) for domain in domains]
            if metric == "mode":
                corr = pearson(left_values, right_values)
            else:
                corr = spearman(left_values, right_values)
            values.append(round_or_none(corr))
        rows.append(
            {
                "key": left["key"],
                "label": left["label"],
                "values": values,
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).resolve()
    output_path = Path(args.output_json).resolve()

    artifact = json.loads(input_path.read_text(encoding="utf-8"))
    rankings = artifact["summary"]["rankings_by_run"]
    validator_meta = {entry["domain"]: entry for entry in artifact["validators"]}
    models = artifact["source"]["models"]
    batches = int(artifact["run_config"]["batches"])
    domains = sorted(validator_meta)

    by_series: dict[tuple[str, int], dict[str, Any]] = {}
    for row in rankings:
        key = (row["model"], int(row["batch"]))
        by_series.setdefault(
            key,
            {
                "key": f"{row['model']}::batch{row['batch']}",
                "label": f"{MODEL_LABELS.get(row['model'], row['model'])} Run {row['batch']}",
                "short_model": MODEL_LABELS.get(row["model"], row["model"]),
                "model": row["model"],
                "batch": int(row["batch"]),
                "values": {},
            },
        )
        by_series[key]["values"][row["domain"]] = {
            "mode": row["mode"],
            "rank": row["rank"],
            "mean": row["mean"],
            "n": row["n"],
            "errors": row["errors"],
            "parse_errors": row["parse_errors"],
        }

    ordered_series = [by_series[(model, batch)] for model in models for batch in range(1, batches + 1)]

    validators: list[dict[str, Any]] = []
    for domain in domains:
        meta = validator_meta[domain]
        cells: dict[str, Any] = {}
        for series in ordered_series:
            cells[series["key"]] = series["values"][domain]
        validators.append(
            {
                "domain": domain,
                "master_key": meta["master_key"],
                "unl_publishers": meta["unl_publishers"],
                "verified": meta["verified"],
                "verification_message": meta["verification_message"],
                "server_version": meta["server_version"],
                "last_seen": meta["last_seen"],
                "cells": cells,
            }
        )

    same_model_stability: list[dict[str, Any]] = []
    for model in models:
        run_1 = by_series[(model, 1)]
        run_2 = by_series[(model, 2)]
        run_1_modes = [float(run_1["values"][domain]["mode"]) for domain in domains]
        run_2_modes = [float(run_2["values"][domain]["mode"]) for domain in domains]
        run_1_ranks = [float(run_1["values"][domain]["rank"]) for domain in domains]
        run_2_ranks = [float(run_2["values"][domain]["rank"]) for domain in domains]
        same_model_stability.append(
            {
                "model": model,
                "label": MODEL_LABELS.get(model, model),
                "run_1_key": run_1["key"],
                "run_2_key": run_2["key"],
                "pearson_mode": round_or_none(pearson(run_1_modes, run_2_modes)),
                "spearman_rank": round_or_none(spearman(run_1_ranks, run_2_ranks)),
            }
        )

    validator_count = len(validators)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_generated_at": artifact["generated_at"],
        "artifact_path": f"/benchmarks/{input_path.name}",
        "artifact_supporting_paths": [
            f"/benchmarks/{input_path.stem}-by-batch.csv",
            f"/benchmarks/{input_path.stem}-overall.csv",
            f"/benchmarks/{input_path.stem}-rankings.csv",
            f"/benchmarks/{input_path.stem}-rank-changes.csv",
        ],
        "validator_count": validator_count,
        "requested_validator_note": (
            f"This recorded benchmark artifact contains {validator_count} validators. "
            "The page reflects the captured run exactly and does not synthesize scores "
            "for validators that were not present in the benchmark snapshot."
        ),
        "models": [{"id": model, "label": MODEL_LABELS.get(model, model)} for model in models],
        "series": [
            {
                "key": series["key"],
                "label": series["label"],
                "short_model": series["short_model"],
                "model": series["model"],
                "batch": series["batch"],
            }
            for series in ordered_series
        ],
        "validators": validators,
        "same_model_stability": same_model_stability,
        "pearson_mode_matrix": {
            "labels": [series["label"] for series in ordered_series],
            "rows": build_matrix(ordered_series, domains, "mode"),
        },
        "spearman_rank_matrix": {
            "labels": [series["label"] for series in ordered_series],
            "rows": build_matrix(ordered_series, domains, "rank"),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
