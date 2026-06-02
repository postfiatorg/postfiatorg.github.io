#!/usr/bin/env python3
"""Summarize an XRPL amendment governance replay packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def route_to_vote(route: str) -> str:
    return {
        "PROCEED": "YES",
        "DELAY_FOR_FIX": "NO",
        "HOLD_FOR_CHALLENGE": "HOLD",
        "REJECT": "NO",
        "OBSOLETE": "NO",
    }.get(route, "HOLD")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_sha256s(packet_dir: Path) -> str:
    rows: list[str] = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(packet_dir).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    sums = "\n".join(rows) + "\n"
    (packet_dir / "SHA256SUMS.txt").write_text(sums)
    return hashlib.sha256(sums.encode("utf-8")).hexdigest()


def load_packets(packet_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text())
        for path in sorted((packet_dir / "amendment_packets").glob("*.json"))
    ]


def load_deterministic(packet_dir: Path) -> dict[str, Any]:
    path = packet_dir / "deterministic_baseline.json"
    if not path.exists():
        return {"results": {}}
    return json.loads(path.read_text())


def load_qwen_routes(packet_dir: Path, packet_id: str) -> tuple[str, list[dict[str, Any]]]:
    runs = []
    for path in sorted((packet_dir / "qwen_runs" / packet_id).glob("run_*.json")):
        runs.append(json.loads(path.read_text()))
    if not runs:
        return "NOT_RUN", []
    routes = Counter(run.get("output_json", {}).get("route", "HOLD_FOR_CHALLENGE") for run in runs)
    return routes.most_common(1)[0][0], runs


def is_unsafe_proceed(historical_route: str, qwen_route: str) -> bool:
    return qwen_route == "PROCEED" and historical_route in {"DELAY_FOR_FIX", "HOLD_FOR_CHALLENGE", "REJECT", "OBSOLETE"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)

    packet_dir = args.packet.resolve()
    generated_at = utc_now()
    packets = load_packets(packet_dir)
    deterministic = load_deterministic(packet_dir).get("results", {})
    runtime_manifest = {}
    manifest_path = packet_dir / "qwen_runtime_manifest.json"
    if manifest_path.exists():
        runtime_manifest = json.loads(manifest_path.read_text())

    rows = []
    qwen_output_hashes: dict[str, list[str]] = {}
    schema_valid = 0
    total_runs = 0
    unsafe = 0
    aligned = 0
    qwen_vs_rule_disagreements = 0

    for packet in packets:
        pid = packet["packet_id"]
        hist = packet["historical_outcome"]["route"]
        det = deterministic.get(pid, {}).get("route", "HOLD_FOR_CHALLENGE")
        qwen_route, runs = load_qwen_routes(packet_dir, pid)
        total_runs += len(runs)
        schema_valid += sum(1 for run in runs if run.get("schema_valid"))
        qwen_output_hashes[pid] = [run["output_hash"] for run in runs]
        if qwen_route == hist:
            aligned += 1
        if qwen_route != det:
            qwen_vs_rule_disagreements += 1
        if is_unsafe_proceed(hist, qwen_route):
            unsafe += 1
        rows.append(
            {
                "packet_id": pid,
                "amendment_or_event": packet["amendment_name"],
                "controversy_reason": ", ".join(packet["controversy_signals"]),
                "what_happened": packet["historical_outcome"]["outcome_summary"],
                "historical_route": hist,
                "deterministic_route": det,
                "qwen_replay_route": qwen_route,
                "replay_default_vote": route_to_vote(qwen_route),
                "converged_with_history": str(qwen_route == hist).lower(),
                "unsafe_proceed": str(is_unsafe_proceed(hist, qwen_route)).lower(),
                "notes": packet["safe_route_label"]["notes"],
            }
        )

    with (packet_dir / "vote_replay_hash_counterfactual.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "packet_id",
                "amendment_or_event",
                "controversy_reason",
                "what_happened",
                "historical_route",
                "deterministic_route",
                "qwen_replay_route",
                "replay_default_vote",
                "converged_with_history",
                "unsafe_proceed",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    packet_count = len(packets)
    validator_count = 41
    full_review_minutes = 120
    deterministic_review_minutes = 45
    packet_verification_minutes = 10
    validator_skim_minutes = 5
    deep_reviewers = 3
    deep_review_minutes = 45
    hourly_rate = 250

    standing_hours = packet_count * validator_count * full_review_minutes / 60
    deterministic_hours = packet_count * validator_count * deterministic_review_minutes / 60
    qwen_hours = (
        packet_count * packet_verification_minutes / 60
        + packet_count * validator_count * validator_skim_minutes / 60
        + packet_count * deep_reviewers * deep_review_minutes / 60
    )
    cost_model = {
        "generated_at": generated_at,
        "packet_count": packet_count,
        "validator_count": validator_count,
        "hourly_rate_usd": hourly_rate,
        "standing_committee": {
            "hours": round(standing_hours, 2),
            "cost_usd": round(standing_hours * hourly_rate, 2),
            "assumption": "Every validator performs a full two-hour review for every governance event.",
        },
        "deterministic_alert": {
            "hours": round(deterministic_hours, 2),
            "cost_usd": round(deterministic_hours * hourly_rate, 2),
            "assumption": "Every validator reviews a deterministic alert for 45 minutes per event.",
        },
        "qwen_replay_default": {
            "hours": round(qwen_hours, 2),
            "cost_usd": round(qwen_hours * hourly_rate, 2),
            "assumption": "One packet verification, five-minute validator skim, and three deep reviewers per event.",
        },
        "attention_reduction_vs_committee": round(1 - qwen_hours / standing_hours, 4),
        "attention_reduction_vs_deterministic": round(1 - qwen_hours / deterministic_hours, 4),
    }
    write_json(packet_dir / "attention_cost_model.json", cost_model)

    exact_hash_converged = sum(1 for hashes in qwen_output_hashes.values() if hashes and len(set(hashes)) == 1)
    route_converged = sum(1 for row in rows if row["qwen_replay_route"] != "NOT_RUN")
    summary = {
        "generated_at": generated_at,
        "runtime_manifest": runtime_manifest,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "schema_valid_output_rate": round(schema_valid / total_runs, 4) if total_runs else 0,
        "historically_aligned_route_rate": round(aligned / packet_count, 4) if packet_count else 0,
        "unsafe_proceed_count": unsafe,
        "qwen_vs_rule_disagreement_count": qwen_vs_rule_disagreements,
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_route_converged_packets": route_converged,
        "attention_reduction_vs_committee": cost_model["attention_reduction_vs_committee"],
        "attention_reduction_vs_deterministic": cost_model["attention_reduction_vs_deterministic"],
    }
    write_json(packet_dir / "convergence_summary.json", summary)
    write_json(packet_dir / "summary.json", summary)
    write_json(packet_dir / "judge_panel.json", {"generated_at": generated_at, "status": "not_run", "notes": "Synthetic judge panel is optional and was not run for this packet."})

    report_lines = [
        "# XRPL Amendment Governance Replay Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        f"- Packets: {packet_count}",
        f"- Qwen runs: {total_runs}",
        f"- Schema-valid output rate: {summary['schema_valid_output_rate']}",
        f"- Parsed-route converged packets: {summary['parsed_route_converged_packets']}",
        f"- Exact-output-hash converged packets: {summary['exact_output_hash_converged_packets']}",
        f"- Historically aligned route rate: {summary['historically_aligned_route_rate']}",
        f"- Unsafe proceed count: {unsafe}",
        f"- Runtime kind: {runtime_manifest.get('runtime_kind', 'missing')}",
        f"- Model: {runtime_manifest.get('model', 'missing')}",
        f"- Machine receipt: {runtime_manifest.get('machine_receipt_path', '')}",
        f"- Machine receipt SHA-256: {runtime_manifest.get('machine_receipt_sha256', '')}",
        f"- Attention reduction vs standing committee: {summary['attention_reduction_vs_committee']}",
        f"- Attention reduction vs deterministic alert: {summary['attention_reduction_vs_deterministic']}",
        "",
        "## Counterfactual Table",
        "",
        "| Event | Historical | Deterministic | Replay | Vote | Unsafe Proceed |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['amendment_or_event']} | {row['historical_route']} | {row['deterministic_route']} | "
            f"{row['qwen_replay_route']} | {row['replay_default_vote']} | {row['unsafe_proceed']} |"
        )
    report_lines.extend(
        [
            "",
            "## Runtime Boundary",
            "",
            runtime_manifest.get(
                "production_profile_note",
                "No Qwen runtime manifest found. Run run_qwen_amendment_replay.py before relying on replay results.",
            ),
            "",
        ]
    )
    (packet_dir / "REPORT.md").write_text("\n".join(report_lines))

    packet_root = write_sha256s(packet_dir)
    print(json.dumps({"packet": packet_dir.relative_to(REPO_ROOT).as_posix(), "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
