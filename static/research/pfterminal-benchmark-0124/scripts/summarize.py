#!/usr/bin/env python3
"""Build machine-readable and Markdown summaries from cached campaign evidence."""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)

# Official GPT Image 2 output estimates captured in
# OPENAI_PRICING_SNAPSHOT.md. Prompt/input-token cost is additional, so these
# values are explicitly a lower-bound image-output estimate rather than
# authoritative account billing.
GPT_IMAGE_2_OUTPUT_USD = {
    ("low", "1024x1024"): 0.006,
    ("low", "1024x1536"): 0.005,
    ("low", "1536x1024"): 0.005,
    ("medium", "1024x1024"): 0.053,
    ("medium", "1024x1536"): 0.041,
    ("medium", "1536x1024"): 0.041,
    ("high", "1024x1024"): 0.211,
    ("high", "1024x1536"): 0.165,
    ("high", "1536x1024"): 0.165,
}
IMAGE_AUDIT_PATH = RUN_ROOT / "visual/image_generation_audit.json"
CONFORMANCE_AUDIT_PATH = RUN_ROOT / "visual/lane_conformance_audit.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 6) if values else None


def ratio(left: float | None, right: float | None) -> float | None:
    if left is None or right is None or left == 0:
        return None
    return round(right / left, 4)


def load_image_audits() -> dict[tuple[str, str, int], dict[str, Any]]:
    if not IMAGE_AUDIT_PATH.exists():
        return {}
    value = load(IMAGE_AUDIT_PATH)
    records = value.get("records")
    if not isinstance(records, list):
        raise RuntimeError(f"expected records array: {IMAGE_AUDIT_PATH}")
    audits: dict[tuple[str, str, int], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError(f"invalid image audit record: {record!r}")
        key = (
            str(record["cell"]),
            str(record["lane"]),
            int(record["wave"]),
        )
        if key in audits:
            raise RuntimeError(f"duplicate image audit record: {key}")
        audits[key] = record
    return audits


IMAGE_AUDITS = load_image_audits()


def load_conformance_audits() -> dict[tuple[str, str, int], dict[str, Any]]:
    if not CONFORMANCE_AUDIT_PATH.exists():
        return {}
    value = load(CONFORMANCE_AUDIT_PATH)
    records = value.get("records")
    if not isinstance(records, list):
        raise RuntimeError(f"expected records array: {CONFORMANCE_AUDIT_PATH}")
    audits: dict[tuple[str, str, int], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError(f"invalid conformance audit record: {record!r}")
        key = (
            str(record["cell"]),
            str(record["lane"]),
            int(record["wave"]),
        )
        if key in audits:
            raise RuntimeError(f"duplicate conformance audit record: {key}")
        audits[key] = record
    return audits


CONFORMANCE_AUDITS = load_conformance_audits()


def manifest_image_output_estimate(
    workspace: Path,
) -> tuple[int, int, float | None, str, int, float | None]:
    path = workspace / "image_manifest.json"
    if not path.exists():
        return 0, 0, None, "missing", 0, None
    value = json.loads(path.read_text(encoding="utf-8"))
    entries = value.get("images") if isinstance(value, dict) else value
    if not isinstance(entries, list):
        return 0, 0, None, "invalid_manifest", 0, None
    total = 0.0
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("model") != "gpt-image-2":
            return (
                len(entries),
                len(entries),
                None,
                "final_manifest_only",
                0,
                None,
            )
        key = (
            str(entry.get("quality", "")).lower(),
            str(entry.get("size", "")).lower().replace("×", "x"),
        )
        price = GPT_IMAGE_2_OUTPUT_USD.get(key)
        if price is None:
            return (
                len(entries),
                len(entries),
                None,
                "final_manifest_only",
                0,
                None,
            )
        total += price
    return (
        len(entries),
        len(entries),
        round(total, 6),
        "final_manifest_only",
        0,
        round(total, 6),
    )


def image_output_estimate(
    workspace: Path, cell: str, lane: str, wave: int
) -> tuple[int, int, float | None, str, int, float | None]:
    """Estimate every evidenced billed output, including discarded attempts."""
    record = IMAGE_AUDITS.get((cell, lane, wave))
    if record is None:
        return manifest_image_output_estimate(workspace)
    attempts = record.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise RuntimeError(
            f"image audit has no attempts: {(cell, lane, wave)}"
        )
    total_count = 0
    final_count = 0
    total_cost = 0.0
    uncertain_count = 0
    uncertain_cost = 0.0
    unsupported_pricing = False
    for attempt in attempts:
        if not isinstance(attempt, dict):
            raise RuntimeError(f"invalid image audit attempt: {attempt!r}")
        count = int(attempt.get("count") or 0)
        if count < 1:
            raise RuntimeError(f"invalid image audit count: {attempt!r}")
        model_supported = attempt.get("model") == "gpt-image-2"
        price_key = (
            str(attempt.get("quality", "")).lower(),
            str(attempt.get("size", "")).lower().replace("×", "x"),
        )
        price = (
            GPT_IMAGE_2_OUTPUT_USD.get(price_key)
            if model_supported
            else None
        )
        if price is None:
            unsupported_pricing = True
        if attempt.get("billing_status") == "response_unknown":
            uncertain_count += count
            if price is not None:
                uncertain_cost += count * price
            continue
        total_count += count
        if attempt.get("disposition") == "final":
            final_count += count
        if price is not None:
            total_cost += count * price
    manifest_count, _, _, _, _, _ = manifest_image_output_estimate(workspace)
    if manifest_count and final_count != manifest_count:
        raise RuntimeError(
            "image audit final count does not match manifest for "
            f"{(cell, lane, wave)}: {final_count} != {manifest_count}"
        )
    if unsupported_pricing:
        return (
            total_count,
            final_count,
            None,
            "attempt_audit_unsupported_route_or_price",
            uncertain_count,
            None,
        )
    return (
        total_count,
        final_count,
        round(total_cost, 6),
        "attempt_audit",
        uncertain_count,
        round(total_cost + uncertain_cost, 6),
    )


def pft_call_diagnostics(result_dir: Path) -> dict[str, Any] | None:
    path = result_dir / "pfterminal.stderr"
    if not path.exists():
        return None
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("tag") == "pfterminal_call_metrics":
            events.append(event)
    if not events:
        return None
    providers: dict[str, int] = defaultdict(int)
    finish_reasons: dict[str, int] = defaultdict(int)
    retry_attempts = 0
    for event in events:
        providers[str(event.get("provider") or "unknown")] += 1
        finish_reasons[str(event.get("finish_reason") or "unknown")] += 1
        retry_attempts += max(0, int(event.get("attempt_number") or 1) - 1)
    return {
        "calls": len(events),
        "retry_attempts": retry_attempts,
        "providers": dict(sorted(providers.items())),
        "finish_reasons": dict(sorted(finish_reasons.items())),
    }


def discover_visual() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cost_map_path = RUN_ROOT / "visual/opus/admin_costs.json"
    cost_map = load(cost_map_path) if cost_map_path.exists() else {}
    for path in sorted(
        (RUN_ROOT / "visual/results").glob("*/*/wave*/agent_run.json")
    ):
        record = load(path)
        cell = str(record["cell"])
        lane = str(record["lane"])
        wave = int(record["wave"])
        cost = (record.get("billing") or {}).get("cost_usd")
        if cost is None and cell == "opus":
            cost = (
                cost_map.get(f"wave{wave}", {}).get(lane)
                if isinstance(cost_map.get(f"wave{wave}"), dict)
                else None
            )
        workspace = Path(str(record["workspace"]))
        (
            image_count,
            final_image_count,
            image_cost,
            image_cost_evidence,
            uncertain_image_count,
            image_cost_upper_bound,
        ) = image_output_estimate(workspace, cell, lane, wave)
        call_diagnostics = (
            pft_call_diagnostics(path.parent) if lane == "pft" else None
        )
        conformance = CONFORMANCE_AUDITS.get((cell, lane, wave), {})
        conformance_valid = bool(conformance.get("valid", True))
        rows.append(
            {
                "workload": "visual_site",
                "cell": cell,
                "lane": lane,
                "wave": wave,
                "model": record.get("model"),
                "wall_seconds": record.get("wall_seconds"),
                "cost_usd": cost,
                "image_count": image_count,
                "final_image_count": final_image_count,
                "image_output_estimate_usd": image_cost,
                "image_output_estimate_upper_bound_usd": (
                    image_cost_upper_bound
                ),
                "image_cost_evidence": image_cost_evidence,
                "uncertain_image_count": uncertain_image_count,
                "contestant_plus_image_output_estimate_usd": (
                    round(float(cost) + image_cost, 6)
                    if isinstance(cost, (int, float)) and image_cost is not None
                    else None
                ),
                "contestant_plus_image_output_estimate_upper_bound_usd": (
                    round(float(cost) + image_cost_upper_bound, 6)
                    if isinstance(cost, (int, float))
                    and image_cost_upper_bound is not None
                    else None
                ),
                "pft_call_diagnostics": call_diagnostics,
                "conformance_valid": conformance_valid,
                "conformance_reasons": conformance.get("reasons") or [],
                "success": bool(
                    record.get("returncode") == 0
                    and (record.get("verification") or {}).get("ok")
                    and (record.get("route") or {}).get("route_verified")
                    and conformance_valid
                ),
                "returncode": record.get("returncode"),
                "timed_out": record.get("timed_out"),
                "artifact": str(path.relative_to(RUN_ROOT)),
            }
        )
    return rows


def deterministic_kind(path: Path) -> str:
    parts = path.relative_to(RUN_ROOT).parts
    return parts[1]


def deterministic_cell(path: Path) -> str:
    parts = path.relative_to(RUN_ROOT).parts
    cell = parts[2]
    if cell == "glm-vercel-current-hermes":
        return "glm-vercel"
    return cell


def invalidated_by_harness_marker(path: Path) -> bool:
    deterministic_root = RUN_ROOT / "deterministic"
    for parent in path.parents:
        if parent == deterministic_root:
            break
        if (parent / "INVALID_HARNESS.md").exists():
            return True
    return False


def discover_deterministic() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        (RUN_ROOT / "deterministic").glob(
            "*/*/wave*/*/results/*/wave*/agent_run.json"
        )
    ):
        if invalidated_by_harness_marker(path):
            continue
        record = load(path)
        verification = record.get("verification") or {}
        lane = record.get("lane")
        rows.append(
            {
                "workload": deterministic_kind(path),
                "cell": deterministic_cell(path),
                "lane": lane,
                "wave": int(record.get("wave")),
                "model": record.get("model"),
                "wall_seconds": record.get("wall_seconds"),
                "cost_usd": (record.get("billing") or {}).get("cost_usd"),
                "image_count": 0,
                "final_image_count": 0,
                "image_output_estimate_usd": None,
                "image_output_estimate_upper_bound_usd": None,
                "image_cost_evidence": None,
                "uncertain_image_count": 0,
                "contestant_plus_image_output_estimate_usd": None,
                "contestant_plus_image_output_estimate_upper_bound_usd": None,
                "pft_call_diagnostics": (
                    pft_call_diagnostics(path.parent)
                    if lane == "pft"
                    else None
                ),
                "conformance_valid": True,
                "conformance_reasons": [],
                "success": bool(
                    record.get("returncode") == 0 and verification.get("ok")
                ),
                "returncode": record.get("returncode"),
                "timed_out": record.get("timed_out"),
                "artifact": str(path.relative_to(RUN_ROOT)),
            }
        )
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["workload"], row["cell"], row["lane"])].append(row)
    output: list[dict[str, Any]] = []
    for (workload, cell, lane), items in sorted(groups.items()):
        walls = [
            float(item["wall_seconds"])
            for item in items
            if isinstance(item.get("wall_seconds"), (int, float))
        ]
        costs = [
            float(item["cost_usd"])
            for item in items
            if isinstance(item.get("cost_usd"), (int, float))
        ]
        image_costs = [
            float(item["image_output_estimate_usd"])
            for item in items
            if isinstance(item.get("image_output_estimate_usd"), (int, float))
        ]
        all_in_costs = [
            float(item["contestant_plus_image_output_estimate_usd"])
            for item in items
            if isinstance(
                item.get("contestant_plus_image_output_estimate_usd"),
                (int, float),
            )
        ]
        image_cost_upper_bounds = [
            float(item["image_output_estimate_upper_bound_usd"])
            for item in items
            if isinstance(
                item.get("image_output_estimate_upper_bound_usd"),
                (int, float),
            )
        ]
        all_in_upper_bounds = [
            float(item["contestant_plus_image_output_estimate_upper_bound_usd"])
            for item in items
            if isinstance(
                item.get(
                    "contestant_plus_image_output_estimate_upper_bound_usd"
                ),
                (int, float),
            )
        ]
        successes = sum(bool(item["success"]) for item in items)
        output.append(
            {
                "workload": workload,
                "cell": cell,
                "lane": lane,
                "runs": len(items),
                "successes": successes,
                "success_rate": round(successes / len(items), 4),
                "total_wall_seconds": round(sum(walls), 6) if walls else None,
                "median_wall_seconds": median(walls),
                "total_cost_usd": round(sum(costs), 6) if costs else None,
                "median_cost_usd": median(costs),
                "costed_runs": len(costs),
                "image_output_estimate_total_usd": (
                    round(sum(image_costs), 6)
                    if len(image_costs) == len(items)
                    else None
                ),
                "image_output_estimate_upper_bound_total_usd": (
                    round(sum(image_cost_upper_bounds), 6)
                    if len(image_cost_upper_bounds) == len(items)
                    else None
                ),
                "all_in_output_estimate_total_usd": (
                    round(sum(all_in_costs), 6)
                    if len(all_in_costs) == len(items)
                    else None
                ),
                "all_in_output_estimate_upper_bound_total_usd": (
                    round(sum(all_in_upper_bounds), 6)
                    if len(all_in_upper_bounds) == len(items)
                    else None
                ),
                "cost_per_success_usd": (
                    round(sum(costs) / successes, 6)
                    if costs and successes
                    else None
                ),
            }
        )
    return output


def comparisons(aggregates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in aggregates:
        grouped[(item["workload"], item["cell"])][item["lane"]] = item
    output: list[dict[str, Any]] = []
    for (workload, cell), lanes in sorted(grouped.items()):
        pft = lanes.get("pft")
        opponent_name = "cc" if "cc" in lanes else "hermes"
        opponent = lanes.get(opponent_name)
        if pft is None or opponent is None:
            continue
        wave_rows = [
            row
            for row in RAW_ROWS
            if row["workload"] == workload and row["cell"] == cell
        ]
        directions: list[bool] = []
        for wave in sorted({int(row["wave"]) for row in wave_rows}):
            by_lane = {
                row["lane"]: row
                for row in wave_rows
                if int(row["wave"]) == wave
            }
            left, right = by_lane.get("pft"), by_lane.get(opponent_name)
            if (
                left
                and right
                and left["success"]
                and right["success"]
                and isinstance(left.get("wall_seconds"), (int, float))
                and isinstance(right.get("wall_seconds"), (int, float))
            ):
                directions.append(left["wall_seconds"] < right["wall_seconds"])
        output.append(
            {
                "workload": workload,
                "cell": cell,
                "opponent": opponent_name,
                "pft_successes": pft["successes"],
                "opponent_successes": opponent["successes"],
                "pft_speedup_x_total": ratio(
                    pft["total_wall_seconds"], opponent["total_wall_seconds"]
                ),
                "pft_cost_advantage_x_total": ratio(
                    pft["total_cost_usd"], opponent["total_cost_usd"]
                ),
                "pft_cost_savings_percent": (
                    round(
                        100
                        * (
                            1
                            - float(pft["total_cost_usd"])
                            / float(opponent["total_cost_usd"])
                        ),
                        2,
                    )
                    if pft["total_cost_usd"] is not None
                    and opponent["total_cost_usd"]
                    else None
                ),
                "pft_all_in_output_estimate_advantage_x_total": ratio(
                    pft["all_in_output_estimate_total_usd"],
                    opponent["all_in_output_estimate_total_usd"],
                ),
                "pft_all_in_output_estimate_savings_percent": (
                    round(
                        100
                        * (
                            1
                            - float(pft["all_in_output_estimate_total_usd"])
                            / float(
                                opponent["all_in_output_estimate_total_usd"]
                            )
                        ),
                        2,
                    )
                    if pft["all_in_output_estimate_total_usd"] is not None
                    and opponent["all_in_output_estimate_total_usd"]
                    else None
                ),
                "directional_speed_waves": directions,
                "speed_result": (
                    "consistent_pft"
                    if len(directions) == 3 and all(directions)
                    else "consistent_opponent"
                    if len(directions) == 3 and not any(directions)
                    else "mixed_or_incomplete"
                ),
            }
        )
    return output


def judgment_rows() -> list[dict[str, Any]]:
    path = RUN_ROOT / "visual/blind/campaign_summary.json"
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def visual_verdict_summary(
    judgments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, int]] = defaultdict(
        lambda: {"pft": 0, "opponent": 0, "inconclusive": 0}
    )
    opponent_by_cell: dict[str, str] = {}
    for judgment in judgments:
        cell = str(judgment["cell"])
        opponent_by_cell[cell] = "cc" if cell == "opus" else "hermes"
        verdict = str(judgment.get("verdict") or "")
        if verdict == "pft":
            grouped[cell]["pft"] += 1
        elif verdict in {"cc", "hermes"}:
            grouped[cell]["opponent"] += 1
        else:
            grouped[cell]["inconclusive"] += 1
    return [
        {
            "cell": cell,
            "opponent": opponent_by_cell[cell],
            "pft_wins": counts["pft"],
            "opponent_wins": counts["opponent"],
            "inconclusive": counts["inconclusive"],
            "waves": sum(counts.values()),
        }
        for cell, counts in sorted(grouped.items())
    ]


def conformance_exclusions(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "workload": row["workload"],
            "cell": row["cell"],
            "lane": row["lane"],
            "wave": row["wave"],
            "reasons": row.get("conformance_reasons") or [],
            "artifact": row["artifact"],
        }
        for row in rows
        if not bool(row.get("conformance_valid", True))
    ]


def judge_overhead(judgments: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "passes": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_tokens": 0,
        "output_tokens": 0,
    }
    for judgment in judgments:
        for judge_pass in judgment.get("passes") or []:
            usage = judge_pass.get("usage") or {}
            details = usage.get("input_tokens_details") or {}
            totals["passes"] += 1
            totals["input_tokens"] += int(usage.get("input_tokens") or 0)
            totals["cached_input_tokens"] += int(
                details.get("cached_tokens") or 0
            )
            totals["cache_write_tokens"] += int(
                details.get("cache_write_tokens") or 0
            )
            totals["output_tokens"] += int(usage.get("output_tokens") or 0)
    noncached = max(
        0,
        totals["input_tokens"]
        - totals["cached_input_tokens"]
        - totals["cache_write_tokens"],
    )
    # GPT-5.6-Sol standard short-context rates captured in
    # OPENAI_PRICING_SNAPSHOT.md. This is usage reconstruction and remains
    # experiment overhead; it is never assigned to either contestant.
    totals["estimated_cost_usd"] = round(
        (
            noncached * 5.00
            + totals["cached_input_tokens"] * 0.50
            + totals["cache_write_tokens"] * 6.25
            + totals["output_tokens"] * 30.00
        )
        / 1_000_000,
        6,
    )
    totals["source"] = (
        "GPT-5.6-Sol response usage reconstructed with official standard "
        "short-context prices"
    )
    return totals


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def fmt_ratio(value: Any, suffix: str = "x", digits: int = 3) -> str:
    return "—" if value is None else f"{fmt(value, digits)}{suffix}"


def fmt_money(value: Any, digits: int = 4) -> str:
    return "—" if value is None else f"${fmt(value, digits)}"


def write_report(
    rows: list[dict[str, Any]],
    aggregates: list[dict[str, Any]],
    comparisons_data: list[dict[str, Any]],
    judgments: list[dict[str, Any]],
    verdict_summary: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
    judge_cost: dict[str, Any],
) -> None:
    spend = sum(
        float(row["cost_usd"])
        for row in rows
        if isinstance(row.get("cost_usd"), (int, float))
    )
    image_output_estimate = sum(
        float(row["image_output_estimate_usd"])
        for row in rows
        if isinstance(row.get("image_output_estimate_usd"), (int, float))
    )
    attributable_lower_bound = (
        spend
        + image_output_estimate
        + float(judge_cost["estimated_cost_usd"])
    )
    lines = [
        "# PFTerminal 0.1.24 comprehensive benchmark",
        "",
        f"Cached paid agent spend currently attributed: **${spend:.4f}**.",
        f"Observed GPT Image 2 output-cost lower-bound currently attributed: "
        f"**${image_output_estimate:.4f}** (prompt input additional).",
        f"Neutral GPT-5.6-Sol judge overhead currently attributed: "
        f"**${float(judge_cost['estimated_cost_usd']):.4f}** across "
        f"{judge_cost['passes']} passes.",
        f"Total currently attributable lower bound: "
        f"**${attributable_lower_bound:.4f}** plus GPT Image 2 prompt input.",
        "",
        "## Harness comparisons",
        "",
        "| workload | cell | opponent | solves | speed ratio | agent cost ratio | agent savings | all-in* ratio | all-in* savings | consistency |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in comparisons_data:
        lines.append(
            "| {workload} | {cell} | {opponent} | {pft_successes}/3 vs "
            "{opponent_successes}/3 | {speed} | {cost} | {savings} | "
            "{all_in} | {all_in_savings} | {result} |".format(
                **item,
                speed=fmt_ratio(item["pft_speedup_x_total"]),
                cost=fmt_ratio(item["pft_cost_advantage_x_total"]),
                savings=fmt_ratio(
                    item["pft_cost_savings_percent"], "%", 2
                ),
                all_in=fmt_ratio(
                    item["pft_all_in_output_estimate_advantage_x_total"]
                ),
                all_in_savings=fmt_ratio(
                    item["pft_all_in_output_estimate_savings_percent"],
                    "%",
                    2,
                ),
                result=item["speed_result"],
            )
        )
    lines.extend(
        [
            "",
            "Ratios above 1.0 favor PFTerminal: opponent total divided by "
            "PFTerminal total. Failures remain in solve denominators and spend.",
            "`all-in*` adds the official GPT Image 2 output estimate for every "
            "confirmed-output generation—including discarded attempts—to agent "
            "billing. Timed-out in-flight calls are retained as a separate "
            "upper bound; prompt input and neutral-judge overhead remain separate.",
            "",
            "## Per-lane aggregates",
            "",
            "| workload | cell | lane | solves | wall total | wall median | agent cost | image output est. | all-in* | cost / solve |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in aggregates:
        lines.append(
            "| {workload} | {cell} | {lane} | {successes}/{runs} | {wall} | "
            "{median} | {cost} | {image_cost} | {all_in} | "
            "{cost_success} |".format(
                **item,
                wall=fmt(item["total_wall_seconds"]),
                median=fmt(item["median_wall_seconds"]),
                cost=fmt_money(item["total_cost_usd"]),
                image_cost=fmt_money(
                    item["image_output_estimate_total_usd"]
                ),
                all_in=fmt_money(item["all_in_output_estimate_total_usd"]),
                cost_success=fmt_money(item["cost_per_success_usd"]),
            )
        )
    lines.extend(["", "## Blind visual judgments", ""])
    if judgments:
        lines.extend(
            [
                "| cell | wave | model | verdict |",
                "| --- | ---: | --- | --- |",
            ]
        )
        for item in judgments:
            lines.append(
                f"| {item['cell']} | {item['wave']} | {item['model']} | "
                f"{item['verdict']} |"
            )
    else:
        lines.append("Pending.")
    if verdict_summary:
        lines.extend(
            [
                "",
                "Balanced-order wave tally:",
                "",
                "| cell | opponent | PFT wins | opponent wins | inconclusive |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for item in verdict_summary:
            lines.append(
                f"| {item['cell']} | {item['opponent']} | "
                f"{item['pft_wins']} | {item['opponent_wins']} | "
                f"{item['inconclusive']} |"
            )
    lines.extend(["", "## Conformance exclusions", ""])
    if exclusions:
        lines.append(
            "The following runs remain in elapsed-time and spend totals but do "
            "not count as successful matched-route runs:"
        )
        for item in exclusions:
            reasons = " ".join(str(reason) for reason in item["reasons"])
            lines.append(
                f"- `{item['workload']}/{item['cell']}/{item['lane']}/"
                f"wave{item['wave']}`: {reasons} Evidence: "
                f"`{item['artifact']}`."
            )
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- Three waves establish replication, not statistical significance.",
            "- `consistent` requires the same directional speed result in all three waves.",
            "- Provider billing deltas are primary; token-price reconstructions are diagnostic.",
            "- Image attempt audits override final manifests when traces prove "
            "additional billed generations; otherwise the final manifest is a "
            "documented lower bound.",
            "- An image request whose client timed out without a response is "
            "not asserted as free or billed: its possible output cost appears "
            "only in the upper bound.",
            "- Website quality is a winner only when balanced A/B orders agree.",
            "",
        ]
    )
    (RUN_ROOT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


RAW_ROWS = discover_visual() + discover_deterministic()


def main() -> int:
    aggregates = aggregate(RAW_ROWS)
    comparisons_data = comparisons(aggregates)
    judgments = judgment_rows()
    verdict_summary = visual_verdict_summary(judgments)
    exclusions = conformance_exclusions(RAW_ROWS)
    judge_cost = judge_overhead(judgments)
    payload = {
        "raw_runs": RAW_ROWS,
        "aggregates": aggregates,
        "comparisons": comparisons_data,
        "visual_judgments": judgments,
        "visual_verdict_summary": verdict_summary,
        "conformance_exclusions": exclusions,
        "judge_overhead": judge_cost,
    }
    (RUN_ROOT / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (RUN_ROOT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RAW_ROWS[0]) if RAW_ROWS else [
            "workload", "cell", "lane", "wave", "model", "wall_seconds",
            "cost_usd", "success", "returncode", "timed_out", "artifact"
        ])
        writer.writeheader()
        writer.writerows(RAW_ROWS)
    write_report(
        RAW_ROWS,
        aggregates,
        comparisons_data,
        judgments,
        verdict_summary,
        exclusions,
        judge_cost,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
