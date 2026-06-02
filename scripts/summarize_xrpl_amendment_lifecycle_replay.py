#!/usr/bin/env python3
"""Summarize XRPL amendment lifecycle replay results."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import LANES, artifact_path, read_json, utc_now, write_json, write_sha256s


def load_runs(root: Path, lane: str, packet_id: str) -> list[dict[str, Any]]:
    run_dir = root / "qwen_runs" / lane / packet_id
    if not run_dir.exists():
        return []
    return [read_json(path) for path in sorted(run_dir.glob("run_*.json"))]


def majority_label(runs: list[dict[str, Any]]) -> str:
    labels = [run.get("parsed_label", "") for run in runs if run.get("schema_valid")]
    if not labels:
        return "NOT_RUN"
    return Counter(labels).most_common(1)[0][0]


def load_baseline(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "baseline" / "deterministic_baseline.json"
    if not path.exists():
        return {lane: {} for lane in LANES}
    return read_json(path)


def summarize_lane(root: Path, lane: str, baseline: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    labels = read_json(root / "labels" / f"{lane}_labels.json")
    rows = []
    total_runs = 0
    valid_runs = 0
    endpoint_errors = 0
    aligned = 0
    baseline_aligned = 0
    qwen_vs_rule = 0
    exact_hash_converged = 0
    parsed_label_converged = 0
    not_run = 0
    unsafe_proceed = 0
    unnecessary_hold = 0

    for packet_id, label_info in sorted(labels.items()):
        runs = load_runs(root, lane, packet_id)
        expected = label_info["expected_label"]
        pred = majority_label(runs)
        total_runs += len(runs)
        valid_runs += sum(1 for run in runs if run.get("schema_valid"))
        endpoint_errors += sum(1 for run in runs if run.get("error"))
        if not runs:
            not_run += 1
        hashes = [run.get("output_hash", "") for run in runs]
        labels_seen = [run.get("parsed_label", "") for run in runs if run.get("schema_valid")]
        if hashes and len(set(hashes)) == 1:
            exact_hash_converged += 1
        if labels_seen and len(set(labels_seen)) == 1:
            parsed_label_converged += 1
        if pred == expected:
            aligned += 1
        base = baseline.get(lane, {}).get(packet_id, {})
        base_pred = base.get("predicted_label", "")
        if base_pred == expected:
            baseline_aligned += 1
        if base_pred and pred != "NOT_RUN" and pred != base_pred:
            qwen_vs_rule += 1
        if lane == "triage":
            if pred == "PROCEED" and expected in {"HOLD_FOR_CHALLENGE", "DELAY_FOR_FIX", "REJECT"}:
                unsafe_proceed += 1
            if pred == "HOLD_FOR_CHALLENGE" and expected == "PROCEED":
                unnecessary_hold += 1
        rows.append(
            {
                "lane": lane,
                "packet_id": packet_id,
                "event_id": label_info["event_id"],
                "amendment_name": label_info["amendment_name"],
                "expected_label": expected,
                "qwen_majority_label": pred,
                "deterministic_baseline_label": base_pred,
                "aligned": pred == expected,
                "baseline_aligned": base_pred == expected,
                "qwen_vs_rule_disagreement": bool(base_pred and pred != "NOT_RUN" and pred != base_pred),
                "run_count": len(runs),
                "schema_valid_runs": sum(1 for run in runs if run.get("schema_valid")),
                "output_hashes": ",".join(hashes),
                "label_basis": label_info.get("label_basis", ""),
            }
        )

    packet_count = len(labels)
    summary = {
        "generated_at": utc_now(),
        "lane": lane,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "not_run_count": not_run,
        "schema_valid_output_rate": round(valid_runs / total_runs, 4) if total_runs else 0,
        "endpoint_error_count": endpoint_errors,
        "fallback_used": False,
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_label_converged_packets": parsed_label_converged,
        "qwen_alignment_count": aligned,
        "qwen_alignment_rate": round(aligned / packet_count, 4) if packet_count else 0,
        "deterministic_baseline_alignment_count": baseline_aligned,
        "deterministic_baseline_alignment_rate": round(baseline_aligned / packet_count, 4) if packet_count else 0,
        "qwen_vs_rule_disagreement_count": qwen_vs_rule,
        "label_counts": dict(Counter(item["expected_label"] for item in labels.values())),
    }
    if lane == "vote_outcome":
        summary["historical_vote_alignment_rate"] = summary["qwen_alignment_rate"]
    if lane == "vote_state":
        summary["vote_state_accuracy"] = summary["qwen_alignment_rate"]
        enabled_rows = [row for row in rows if row["expected_label"] == "ENABLED"]
        summary["enabled_state_accuracy"] = round(sum(1 for row in enabled_rows if row["aligned"]) / len(enabled_rows), 4) if enabled_rows else 0
    if lane == "default_vote":
        summary["source_default_vote_match_rate"] = summary["qwen_alignment_rate"]
        summary["claim_eligible"] = False
        summary["claim_note"] = "Diagnostic only: source default vote is not an XRP validator-history outcome."
    if lane == "triage":
        summary["triage_policy_alignment_rate"] = summary["qwen_alignment_rate"]
        summary["unsafe_proceed_count"] = unsafe_proceed
        summary["unnecessary_hold_count"] = unnecessary_hold
    return summary, rows


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(root: Path, summaries: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    claim_disagreements = [
        row for row in rows if row["lane"] != "default_vote" and row["qwen_majority_label"] != "NOT_RUN" and not row["aligned"]
    ]
    diagnostic_disagreements = [
        row for row in rows if row["lane"] == "default_vote" and row["qwen_majority_label"] != "NOT_RUN" and not row["aligned"]
    ]
    lines = [
        "# XRPL Amendment Lifecycle Replay Report",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Claim Gate",
        "",
        "Use lane-specific language only. `HOLD_FOR_CHALLENGE` is a triage/work-item label and is not an XRP validator vote.",
        "`default_vote` is diagnostic only; it is not a historical replay claim because source defaults are not validator outcomes.",
        "",
        "Safe article claim form:",
        "",
        "> On source-backed XRPL amendment lifecycle packets, Qwen matched terminal XRP-native vote/outcome labels on X/Y eligible cases, matched dated vote-state labels on A/B cases, and matched conservative governance triage labels on E/F cases.",
        "",
        "## Lane Summaries",
        "",
    ]
    for lane in LANES:
        summary = summaries[lane]
        lines.extend(
            [
                f"### {lane}",
                "",
                f"- Packets: {summary['packet_count']}",
                f"- Qwen runs: {summary['total_qwen_runs']}",
                f"- Schema-valid output rate: {summary['schema_valid_output_rate']}",
                f"- Qwen alignment rate: {summary['qwen_alignment_rate']}",
                f"- Baseline alignment rate: {summary['deterministic_baseline_alignment_rate']}",
                f"- Qwen-vs-rule disagreements: {summary['qwen_vs_rule_disagreement_count']}",
                "",
            ]
        )
    lines.extend(["## Disagreements", ""])
    if claim_disagreements:
        for row in claim_disagreements[:40]:
            lines.append(
                f"- `{row['lane']}` `{row['packet_id']}` expected `{row['expected_label']}`, Qwen `{row['qwen_majority_label']}`, baseline `{row['deterministic_baseline_label']}`"
            )
    else:
        lines.append("- No Qwen-vs-label disagreements among completed runs.")
    if diagnostic_disagreements:
        lines.extend(
            [
                "",
                "Diagnostic `default_vote` disagreements are excluded from this claim gate; see `default_vote_disagreements.csv`.",
            ]
        )
    (reports / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for lane in LANES:
        lane_rows = [row for row in rows if row["lane"] == lane]
        lane_lines = [f"# {lane} Report", "", json.dumps(summaries[lane], indent=2, sort_keys=True)]
        lane_lines.extend(["", "## Disagreements", ""])
        for row in lane_rows:
            if row["qwen_majority_label"] != "NOT_RUN" and not row["aligned"]:
                lane_lines.append(f"- `{row['packet_id']}` expected `{row['expected_label']}`, got `{row['qwen_majority_label']}`")
        (reports / f"{lane}_report.md").write_text("\n".join(lane_lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    root = artifact_path(args.artifact)
    summaries_dir = root / "summaries"
    reports_dir = root / "reports"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    baseline = load_baseline(root)
    summaries: dict[str, dict[str, Any]] = {}
    all_rows: list[dict[str, Any]] = []
    for lane in LANES:
        summary, rows = summarize_lane(root, lane, baseline)
        summaries[lane] = summary
        all_rows.extend(rows)
        write_json(summaries_dir / f"{lane}_summary.json", summary)
        write_rows(reports_dir / f"{lane}_results.csv", rows)
        write_rows(reports_dir / f"{lane}_disagreements.csv", [row for row in rows if row["qwen_majority_label"] != "NOT_RUN" and not row["aligned"]])

    combined = {
        "generated_at": utc_now(),
        "artifact": str(root),
        "lanes": summaries,
        "total_packets": sum(summary["packet_count"] for summary in summaries.values()),
        "total_qwen_runs": sum(summary["total_qwen_runs"] for summary in summaries.values()),
        "completed_lane_packets": sum(summary["packet_count"] - summary["not_run_count"] for summary in summaries.values()),
        "not_run_count": sum(summary["not_run_count"] for summary in summaries.values()),
    }
    write_json(summaries_dir / "combined_summary.json", combined)
    write_rows(reports_dir / "combined_results.csv", all_rows)
    write_rows(reports_dir / "combined_disagreements.csv", [row for row in all_rows if row["qwen_majority_label"] != "NOT_RUN" and not row["aligned"]])
    write_report(root, summaries, all_rows)
    sha = write_sha256s(root)
    combined["sha256s_hash"] = sha
    write_json(summaries_dir / "combined_summary.json", combined)
    print(json.dumps(combined, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
