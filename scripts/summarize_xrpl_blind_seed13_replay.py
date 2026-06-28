#!/usr/bin/env python3
"""Summarize a blind XRPL seed-13 governance replay."""

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


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256s(packet_dir: Path) -> str:
    rows = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rows.append(f"{sha_file(path)}  {path.relative_to(packet_dir).as_posix()}\n")
    sums = "".join(rows)
    (packet_dir / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    return hashlib.sha256(sums.encode("utf-8")).hexdigest()


def route_to_vote(route: str) -> str:
    return {
        "PROCEED": "YES",
        "DELAY_FOR_FIX": "NO",
        "HOLD_FOR_CHALLENGE": "HOLD",
        "REJECT": "NO",
    }.get(route, "HOLD")


def load_runs(packet_dir: Path, packet_id: str) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((packet_dir / "qwen_runs" / packet_id).glob("run_*.json"))
    ]


def unsafe_proceed(expected_route: str, qwen_route: str) -> bool:
    return qwen_route == "PROCEED" and expected_route in {
        "DELAY_FOR_FIX",
        "HOLD_FOR_CHALLENGE",
        "REJECT",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)

    packet_dir = args.packet.resolve()
    generated_at = utc_now()
    labels_doc = json.loads((packet_dir / "blind_eval_labels.json").read_text(encoding="utf-8"))
    labels = labels_doc["labels"]
    runtime_manifest = {}
    manifest_path = packet_dir / "qwen_runtime_manifest.json"
    if manifest_path.exists():
        runtime_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    total_runs = 0
    schema_valid = 0
    exact_hash_converged = 0
    parsed_route_converged = 0
    aligned = 0
    unsafe = 0
    qwen_route_counts: Counter[str] = Counter()
    error_count = 0

    for packet_id, label in sorted(labels.items()):
        packet = json.loads((packet_dir / "amendment_packets" / f"{packet_id}.json").read_text(encoding="utf-8"))
        source_status = packet.get("source_reported_status", "")
        if not source_status and isinstance(packet.get("source_status_context"), dict):
            source_status = packet["source_status_context"].get("status", "")
        source_default_vote = packet.get("source_reported_default_vote", "")
        if not source_default_vote and isinstance(packet.get("source_default_vote_context"), dict):
            source_default_vote = packet["source_default_vote_context"].get("default_vote", "")
        runs = load_runs(packet_dir, packet_id)
        total_runs += len(runs)
        schema_valid += sum(1 for run in runs if run.get("schema_valid"))
        error_count += sum(1 for run in runs if run.get("error"))
        output_hashes = [run.get("output_hash") for run in runs]
        routes = [run.get("output_json", {}).get("route", "NOT_RUN") for run in runs]
        if output_hashes and len(set(output_hashes)) == 1:
            exact_hash_converged += 1
        if routes and len(set(routes)) == 1:
            parsed_route_converged += 1
        qwen_route = Counter(routes).most_common(1)[0][0] if routes else "NOT_RUN"
        qwen_route_counts[qwen_route] += 1
        expected_route = label["expected_route"]
        is_aligned = qwen_route == expected_route
        is_unsafe = unsafe_proceed(expected_route, qwen_route)
        aligned += int(is_aligned)
        unsafe += int(is_unsafe)
        rows.append(
            {
                "packet_id": packet_id,
                "event_name": packet["amendment_or_event_name"],
                "source_reported_status": source_status,
                "source_reported_default_vote": source_default_vote,
                "expected_route_held_out": expected_route,
                "qwen_replay_route": qwen_route,
                "qwen_replay_vote": route_to_vote(qwen_route),
                "aligned_with_held_out_label": str(is_aligned).lower(),
                "unsafe_proceed": str(is_unsafe).lower(),
                "exact_output_hash_converged": str(bool(output_hashes and len(set(output_hashes)) == 1)).lower(),
                "parsed_route_converged": str(bool(routes and len(set(routes)) == 1)).lower(),
                "run_count": len(runs),
                "first_source_fact": packet["source_facts"][0]["quote_or_summary"],
            }
        )

    with (packet_dir / "blind_vote_replay.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    packet_count = len(labels)
    summary = {
        "generated_at": generated_at,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "schema_valid_output_rate": round(schema_valid / total_runs, 4) if total_runs else 0,
        "endpoint_error_count": error_count,
        "fallback_used": bool(runtime_manifest.get("fallback_used")),
        "held_out_alignment_rate": round(aligned / packet_count, 4) if packet_count else 0,
        "unsafe_proceed_count": unsafe,
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_route_converged_packets": parsed_route_converged,
        "qwen_route_counts": dict(sorted(qwen_route_counts.items())),
        "runtime_manifest": runtime_manifest,
        "eval_boundary": labels_doc["eval_boundary"],
        "selection_policy": labels_doc["selection_policy"],
    }
    write_json(packet_dir / "blind_replay_summary.json", summary)
    write_json(packet_dir / "summary.json", summary)

    report_lines = [
        "# XRPL Blind Seed-13 Governance Replay Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        f"- Packets: {packet_count}",
        f"- Qwen runs: {total_runs}",
        f"- Schema-valid output rate: {summary['schema_valid_output_rate']}",
        f"- Endpoint errors: {error_count}",
        f"- Offline fallback used: {summary['fallback_used']}",
        f"- Exact-output-hash converged packets: {exact_hash_converged}",
        f"- Parsed-route converged packets: {parsed_route_converged}",
        f"- Held-out label alignment rate: {summary['held_out_alignment_rate']}",
        f"- Unsafe proceed count: {unsafe}",
        f"- Runtime kind: {runtime_manifest.get('runtime_kind', 'missing')}",
        f"- Model: {runtime_manifest.get('model', 'missing')}",
        f"- Machine receipt: {runtime_manifest.get('machine_receipt_path', '')}",
        f"- Machine receipt SHA-256: {runtime_manifest.get('machine_receipt_sha256', '')}",
        "",
        "## Boundary",
        "",
        "Prompt packets retain source-backed facts, source-reported statuses, default votes, and official validator advisories.",
        "Prompt packets exclude corpus route labels, risk tags, controversy signals, safe-route labels, and generated route-hint facts.",
        "",
        "## Results",
        "",
        "| Event | Source Status | Source Default Vote | Held-Out Route | Qwen Route | Vote | Aligned | Unsafe Proceed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['event_name']} | {row['source_reported_status']} | "
            f"{row['source_reported_default_vote']} | {row['expected_route_held_out']} | "
            f"{row['qwen_replay_route']} | {row['qwen_replay_vote']} | "
            f"{row['aligned_with_held_out_label']} | {row['unsafe_proceed']} |"
        )
    (packet_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    packet_root = write_sha256s(packet_dir)
    print(json.dumps({"packet": packet_dir.relative_to(REPO_ROOT).as_posix(), "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
